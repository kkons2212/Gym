"""Member Registration and Subscription Service (UC02.1 & UC05.1).

Coordinates atomic multi-table business transactions across User, MemberSubscription,
Invoice, and Notification entities under strict ACID compliance.
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional
from uuid import uuid4

from constants import InvoiceStatus, PaymentMethod, RoleID, SubscriptionStatus, TransactionType, UserStatus
from database.db_connection import db
from exceptions import (
    DuplicateUserException,
    PackageNotFoundException,
    ValidationException,
)
from models.invoice import Invoice
from models.member_subscription import MemberSubscription
from models.notification import Notification
from models.user import User
from repositories.invoice_repository import InvoiceRepository
from repositories.notification_repository import NotificationRepository
from repositories.package_plan_repository import PackagePlanRepository
from repositories.subscription_repository import SubscriptionRepository
from repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class MemberService:
    """Dịch vụ nghiệp vụ quản lý vòng đời Hội viên và Gói đăng ký."""

    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        plan_repo: Optional[PackagePlanRepository] = None,
        sub_repo: Optional[SubscriptionRepository] = None,
        invoice_repo: Optional[InvoiceRepository] = None,
        noti_repo: Optional[NotificationRepository] = None,
    ) -> None:
        self.user_repo = user_repo or UserRepository()
        self.plan_repo = plan_repo or PackagePlanRepository()
        self.sub_repo = sub_repo or SubscriptionRepository()
        self.invoice_repo = invoice_repo or InvoiceRepository()
        self.noti_repo = noti_repo or NotificationRepository()
        self.db = db

    def register_member_with_package(
        self,
        full_name: str,
        phone: str,
        plan_id: str,
        payment_method: str = PaymentMethod.VIETQR.value,
        email: Optional[str] = None,
        admin_id: Optional[str] = "ADMIN",
        assigned_pt_id: Optional[str] = None,
        gender: Optional[int] = 1,
    ) -> Dict[str, Any]:
        """Thực hiện quy trình đăng ký hội viên mới kèm gói tập và hóa đơn.

        Quy trình được thực thi nguyên tử trong một Transaction (All-or-Nothing).
        Nếu phát sinh bất kỳ lỗi nào, toàn bộ dữ liệu 4 bảng sẽ được rollback.

        Args:
            full_name: Họ tên hội viên.
            phone: Số điện thoại (chuẩn 10 số).
            plan_id: Mã gói tập lựa chọn.
            payment_method: CASH hoặc VIETQR (nghiêm cấm quẹt thẻ POS).
            email: Địa chỉ email (tùy chọn).
            admin_id: Mã nhân viên lễ tân trực quầy thực hiện giao dịch.
            assigned_pt_id: Mã HLV phụ trách nếu gói có PT.
            gender: Giới tính (1: Nam, 0: Nữ).

        Returns:
            Dict[str, Any]: Kết quả chi tiết gồm thông tin User, Subscription, Invoice, Notification.

        Raises:
            ValidationException: Khi thông tin nhập liệu không hợp lệ.
            DuplicateUserException: Khi số điện thoại đã tồn tại trong hệ thống.
            PackageNotFoundException: Khi mã gói tập không tồn tại hoặc đã ngừng bán.
        """
        # 1. Fail-Fast Validation
        full_name = full_name.strip() if full_name else ""
        if not full_name:
            raise ValidationException("Họ và tên hội viên không được để trống.", "full_name")

        phone = phone.strip() if phone else ""
        if not phone:
            raise ValidationException("Số điện thoại không được để trống.", "phone")

        clean_phone = re.sub(r"[\s\-\.]", "", phone)
        if clean_phone.startswith("+84"):
            clean_phone = "0" + clean_phone[3:]
        if not re.match(r"^0\d{9}$", clean_phone):
            raise ValidationException(
                f"Số điện thoại '{phone}' không hợp lệ. Bắt buộc phải là 10 chữ số tại Việt Nam.",
                "phone",
            )

        if email:
            email = email.strip()
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                raise ValidationException(f"Địa chỉ email '{email}' không đúng định dạng.", "email")

        payment_method = payment_method.upper().strip()
        if payment_method not in {PaymentMethod.CASH.value, PaymentMethod.VIETQR.value}:
            raise ValidationException(
                f"Phương thức thanh toán '{payment_method}' không hợp lệ. Chỉ chấp nhận CASH hoặc VIETQR.",
                "payment_method",
            )

        # 2. Kiểm tra trùng lặp số điện thoại
        existing_phone = self.user_repo.find_by_phone(clean_phone)
        if existing_phone:
            raise DuplicateUserException("Số điện thoại", clean_phone)

        # 3. Tra cứu gói tập niêm yết
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan or not plan.is_available():
            raise PackageNotFoundException(plan_id)

        # 4. Tính toán thời hạn và số buổi
        today = date.today()
        end_date = today + timedelta(days=plan.duration_days)
        remaining_checkins = plan.max_check_in_sessions
        remaining_pts = plan.total_pt_sessions if plan.is_pt_included else 0

        # 5. Sinh các khóa chính phù hợp kích thước VARCHAR(10) trong Schema
        username = f"HV{uuid4().hex[:6].upper()}"
        sub_id = f"SUB{uuid4().hex[:6].upper()}"
        inv_id = f"INV{uuid4().hex[:6].upper()}"
        noti_id = f"NOT{uuid4().hex[:6].upper()}"
        qr_token = f"GYM-QR-{username}-{uuid4().hex[:8].upper()}"
        inv_code = f"HD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:4].upper()}"

        # 6. Tạo các thực thể Entity
        new_user = User(
            username=username,
            role_id=RoleID.MEMBER.value,
            full_name=full_name,
            phone=clean_phone,
            email=email or f"{clean_phone}@gym.vn",
            password_hash=None,
            gender=gender,
            status=UserStatus.ACTIVE.value,
            created_at=today,
        )

        new_sub = MemberSubscription(
            subscription_id=sub_id,
            username=username,
            plan_id=plan.plan_id,
            qr_code=qr_token,
            start_date=today,
            end_date=end_date,
            remaining_check_in_sessions=remaining_checkins,
            remaining_pt_sessions=remaining_pts,
            status=SubscriptionStatus.ACTIVE.value,
            created_at=today,
            assigned_pt_id=assigned_pt_id,
        )

        new_invoice = Invoice(
            invoice_id=inv_id,
            invoice_code=inv_code,
            transaction_type=TransactionType.NEW_REGISTRATION.value,
            subtotal_amount=float(plan.price),
            total_amount=float(plan.price),
            payment_method=payment_method,
            status=InvoiceStatus.PAID.value,
            paid_at=today,
            username=username,
            subscription_id=sub_id,
            created_by_admin_id=admin_id,
        )

        new_noti = Notification(
            notification_id=noti_id,
            username=username,
            title="Chào mừng hội viên mới!",
            message=f"Chúc mừng bạn đã kích hoạt thành công gói tập '{plan.name}'. Mã QR thẻ tập của bạn: {qr_token}",
            created_at=datetime.now(),
        )

        # 7. Mở Transaction nguyên tử ghi vào 4 bảng CSDL
        with self.db.transaction() as cursor:
            self.user_repo.create_with_cursor(cursor, new_user)
            self.sub_repo.create_with_cursor(cursor, new_sub)
            self.invoice_repo.create_with_cursor(cursor, new_invoice)
            self.noti_repo.create_with_cursor(cursor, new_noti)

        logger.info(
            "Đăng ký hội viên thành công: username=%s, phone=%s, plan=%s, invoice=%s",
            username,
            clean_phone,
            plan.name,
            inv_code,
        )

        return {
            "success": True,
            "user": new_user,
            "subscription": new_sub,
            "invoice": new_invoice,
            "notification": new_noti,
            "qr_code": qr_token,
        }
