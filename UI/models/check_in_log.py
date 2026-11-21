"""Domain Entity CheckInLog mapped to database table CheckInLog."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from constants import CheckInStatus
from models.base_model import BaseModel


@dataclass
class CheckInLog(BaseModel):
    """Thực thể Nhật ký điểm danh của hội viên vào phòng tập.

    Thuộc tính:
        check_in_id: Khóa chính (CK001...).
        check_in_at: Thời điểm quẹt thẻ/nhập mã.
        status: SUCCESS hoặc DENIED.
        denial_reason: Lý do từ chối nếu status = DENIED.
        subscription_id: Thẻ tập được sử dụng (FK -> MemberSubscription).
        verified_by_admin_id: Quản trị viên trực quầy xác nhận.
        username: Mã hội viên (FK -> User).
    """

    check_in_id: str
    username: str
    check_in_at: Optional[datetime] = None
    status: str = CheckInStatus.SUCCESS.value
    denial_reason: Optional[str] = None
    subscription_id: Optional[str] = None
    verified_by_admin_id: Optional[str] = None

    def is_success(self) -> bool:
        """Kiểm tra lượt điểm danh có thành công hay không."""
        return self.status == CheckInStatus.SUCCESS.value
