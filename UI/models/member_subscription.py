"""Domain Entity MemberSubscription mapped to database table MemberSubscription."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple

from constants import DenialReason, SubscriptionStatus
from models.base_model import BaseModel


@dataclass
class MemberSubscription(BaseModel):
    """Thực thể Thẻ hội viên / Gói đăng ký của hội viên.

    Thuộc tính:
        subscription_id: Mã số định danh thẻ tập (PK).
        qr_code: Chuỗi mã token QR định danh duy nhất (Unique).
        start_date: Ngày kích hoạt gói tập.
        end_date: Ngày hết hạn của gói tập.
        remaining_check_in_sessions: Số lượt điểm danh còn lại (None = không giới hạn).
        remaining_pt_sessions: Số buổi PT còn lại.
        freeze_start_date: Ngày bắt đầu bảo lưu (nếu có).
        freeze_end_date: Ngày kết thúc bảo lưu (nếu có).
        status: Trạng thái (ACTIVE, EXPIRED, FROZEN, CANCELLED).
        created_at: Thời điểm tạo bản ghi.
        username: Tên đăng nhập / mã hội viên (FK -> User).
        assigned_pt_id: Mã HLV phụ trách nếu có (FK -> User).
        plan_id: Mã gói tập đã mua (FK -> PackagePlan).
        pt_session_id: Khóa ngoại buổi tập nếu có.
    """

    subscription_id: str
    username: str
    plan_id: str
    qr_code: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    remaining_check_in_sessions: Optional[int] = None
    remaining_pt_sessions: Optional[int] = None
    freeze_start_date: Optional[date] = None
    freeze_end_date: Optional[date] = None
    status: str = SubscriptionStatus.ACTIVE.value
    created_at: Optional[date] = None
    assigned_pt_id: Optional[str] = None
    pt_session_id: Optional[str] = None

    def is_eligible_for_checkin(
        self, target_date: Optional[date] = None
    ) -> Tuple[bool, str]:
        """Kiểm tra điều kiện hợp lệ để hội viên được check-in vào phòng tập.

        Áp dụng Guard Clauses theo UC03.1 & UC03.2.

        Args:
            target_date: Ngày cần kiểm tra (mặc định: ngày hiện tại).

        Returns:
            Tuple[bool, str]: (Đủ điều kiện: True/False, Thông điệp/Lý do từ chối).
        """
        check_date = target_date or date.today()

        # 1. Guard clause: Trạng thái thẻ phải là ACTIVE
        if self.status != SubscriptionStatus.ACTIVE.value:
            if self.status == SubscriptionStatus.FROZEN.value:
                return False, "Thẻ hội viên đang trong thời gian bảo lưu."
            if self.status == SubscriptionStatus.CANCELLED.value:
                return False, "Thẻ hội viên đã bị hủy bỏ."
            return False, DenialReason.NOT_ACTIVE.value

        # 2. Guard clause: Kiểm tra thời hạn kết thúc
        if self.end_date and self.end_date < check_date:
            return False, DenialReason.EXPIRED.value

        # 3. Guard clause: Kiểm tra số buổi còn lại nếu gói có giới hạn
        if self.remaining_check_in_sessions is not None:
            if self.remaining_check_in_sessions <= 0:
                return False, DenialReason.OUT_OF_SESSIONS.value

        return True, "Hợp lệ"
