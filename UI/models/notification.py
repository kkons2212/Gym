"""Domain Entity Notification mapped to database table Notification."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from models.base_model import BaseModel


@dataclass
class Notification(BaseModel):
    """Thực thể Thông báo gửi tới hội viên.

    Thuộc tính:
        notification_id: Khóa chính (NOTI001...).
        title: Tiêu đề thông báo.
        message: Nội dung chi tiết.
        is_read: 0 nếu chưa đọc, 1 nếu đã đọc.
        created_at: Thời điểm gửi thông báo.
        username: Mã hội viên nhận thông báo (FK -> User).
    """

    notification_id: str
    username: str
    title: str
    message: str
    is_read: int = 0
    created_at: Optional[datetime] = None
