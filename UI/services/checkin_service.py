"""Check-In Service for Member Access Control (UC03.1 & UC03.2).

Validates membership status, verifies expiration dates, deducts session quotas,
and logs entry audits in compliance with physical database rules.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from constants import CheckInMethod, CheckInStatus, DenialReason
from database.db_connection import db
from exceptions import CheckInDeniedException
from models.check_in_log import CheckInLog
from models.member_subscription import MemberSubscription
from models.user import User
from repositories.check_in_repository import CheckInRepository
from repositories.package_plan_repository import PackagePlanRepository
from repositories.subscription_repository import SubscriptionRepository
from repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class CheckInService:
    """Service kiểm soát điểm danh ra vào phòng tập cho hội viên."""

    def __init__(
        self,
        sub_repo: Optional[SubscriptionRepository] = None,
        user_repo: Optional[UserRepository] = None,
        check_in_repo: Optional[CheckInRepository] = None,
        plan_repo: Optional[PackagePlanRepository] = None,
    ) -> None:
        self.sub_repo = sub_repo or SubscriptionRepository()
        self.user_repo = user_repo or UserRepository()
        self.check_in_repo = check_in_repo or CheckInRepository()
        self.plan_repo = plan_repo or PackagePlanRepository()
        self.db = db

    def process_checkin(
        self,
        key: str,
        method: str = CheckInMethod.QR_SCAN.value,
        admin_id: Optional[str] = "ADMIN",
        check_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Xử lý quy trình kiểm tra và điểm danh hội viên vào phòng tập.

        Hỗ trợ cả 2 phương thức:
        - UC03.1: Quét mã QR token từ webcam camera.
        - UC03.2: Nhập tay số điện thoại hoặc mã hội viên (Username).

        Args:
            key: Chuỗi mã QR token, hoặc Số điện thoại / Mã hội viên.
            method: QR_SCAN hoặc MANUAL.
            admin_id: Quản trị viên trực quầy xác nhận.
            check_date: Ngày điểm danh (mặc định: ngày hiện tại).

        Returns:
            Dict[str, Any]: Thông tin lượt điểm danh để UI hiển thị.

        Raises:
            CheckInDeniedException: Thẻ không đủ điều kiện điểm danh.
        """
        target_date = check_date or date.today()
        key = key.strip() if key else ""

        if not key:
            raise CheckInDeniedException(
                "Mã QR hoặc thông tin tra cứu không được để trống."
            )

        subscription: Optional[MemberSubscription] = None
        user: Optional[User] = None

        # 1. Nhận diện và tra cứu thông tin hội viên & gói tập
        if method == CheckInMethod.QR_SCAN.value:
            subscription = self.sub_repo.find_by_qrcode(key)
            if subscription:
                user = self.user_repo.find_by_username(subscription.username)
        else:
            # Tra cứu thủ công qua SĐT hoặc Username
            user = self.user_repo.find_by_phone_or_username(key)
            if user:
                subscription = self.sub_repo.find_active_by_username(
                    user.username
                )

        # 2. Xử lý trường hợp không tìm thấy thẻ hoặc hội viên
        if not subscription or not user:
            logger.warning(
                "Từ chối điểm danh: Không tìm thấy thẻ hoặc hội viên "
                "khớp với key='%s' (method=%s)",
                key,
                method,
            )
            raise CheckInDeniedException(
                DenialReason.SUBSCRIPTION_NOT_FOUND.value,
                username=user.username if user else key,
            )

        # 3. Kiểm tra tính hợp lệ của tài khoản người dùng
        if not user.is_active():
            check_in_id = self._record_denial_log(
                subscription=subscription,
                user=user,
                reason=DenialReason.USER_LOCKED.value,
                admin_id=admin_id,
            )
            raise CheckInDeniedException(
                DenialReason.USER_LOCKED.value,
                username=user.username,
                check_in_id=check_in_id,
            )

        # 4. Kiểm tra Guard Clauses của thẻ hội viên (is_eligible_for_checkin)
        is_eligible, reason = subscription.is_eligible_for_checkin(target_date)
        if not is_eligible:
            check_in_id = self._record_denial_log(
                subscription=subscription,
                user=user,
                reason=reason,
                admin_id=admin_id,
            )
            raise CheckInDeniedException(
                reason, username=user.username, check_in_id=check_in_id
            )

        # 5. Ghi log thành công cùng transaction với việc giảm lượt.
        now_dt = datetime.now()
        check_in_id = f"CK{uuid4().hex[:6].upper()}"
        success_log = CheckInLog(
            check_in_id=check_in_id,
            username=user.username,
            check_in_at=now_dt,
            status=CheckInStatus.SUCCESS.value,
            denial_reason=None,
            subscription_id=subscription.subscription_id,
            verified_by_admin_id=admin_id,
        )
        decremented = False
        has_limited_sessions = (
            subscription.remaining_check_in_sessions is not None
            and subscription.remaining_check_in_sessions > 0
        )
        with self.db.transaction(dictionary=False) as cursor:
            if has_limited_sessions:
                decremented = self.sub_repo.decrement_sessions_with_cursor(
                    cursor, subscription.subscription_id
                )
            else:
                decremented = True

            if decremented:
                self.check_in_repo.create_with_cursor(cursor, success_log)

        if not decremented:
            reason = DenialReason.OUT_OF_SESSIONS.value
            denied_check_in_id = self._record_denial_log(
                subscription=subscription,
                user=user,
                reason=reason,
                admin_id=admin_id,
            )
            raise CheckInDeniedException(
                reason,
                username=user.username,
                check_in_id=denied_check_in_id,
            )

        if has_limited_sessions:
            subscription.remaining_check_in_sessions -= 1

        # 6. Lấy tên gói tập để hiển thị lên thẻ Preview
        plan = self.plan_repo.get_by_id(subscription.plan_id)
        plan_name = plan.name if plan else subscription.plan_id

        logger.info(
            "Điểm danh thành công: user=%s, name=%s, plan=%s, remaining=%s",
            user.username,
            user.full_name,
            plan_name,
            subscription.remaining_check_in_sessions,
        )

        return {
            "success": True,
            "check_in_id": check_in_id,
            "check_in_at": now_dt,
            "username": user.username,
            "full_name": user.full_name or user.username,
            "phone": user.phone or "",
            "plan_name": plan_name,
            "end_date": subscription.end_date,
            "remaining_sessions": subscription.remaining_check_in_sessions,
            "status": subscription.status,
        }

    def _record_denial_log(
        self,
        subscription: MemberSubscription,
        user: User,
        reason: str,
        admin_id: Optional[str] = None,
    ) -> str:
        """Ghi nhận lịch sử từ chối điểm danh vào bảng CheckInLog."""
        check_in_id = f"CK{uuid4().hex[:6].upper()}"
        denial_log = CheckInLog(
            check_in_id=check_in_id,
            username=user.username,
            check_in_at=datetime.now(),
            status=CheckInStatus.DENIED.value,
            denial_reason=reason,
            subscription_id=subscription.subscription_id,
            verified_by_admin_id=admin_id,
        )
        with self.db.transaction(dictionary=False) as cursor:
            self.check_in_repo.create_with_cursor(cursor, denial_log)
        return check_in_id
