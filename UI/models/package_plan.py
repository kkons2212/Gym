"""Domain Entity PackagePlan mapped to database table PackagePlan."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.base_model import BaseModel


@dataclass
class PackagePlan(BaseModel):
    """Thực thể Gói tập niêm yết trong hệ thống phòng tập.

    Thuộc tính:
        plan_id: Mã gói tập (PK).
        name: Tên gói tập (Standard 1M, VIP Platinum...).
        description: Mô tả quyền lợi.
        duration_days: Số ngày có hiệu lực.
        price: Đơn giá niêm yết (VNĐ).
        max_check_in_sessions: Số lượt check-in tối đa (None hoặc 0 = không giới hạn).
        is_pt_included: 1 nếu có kèm HLV, 0 nếu không.
        total_pt_sessions: Số buổi kèm PT nếu có.
        is_active: 1 nếu đang mở bán, 0 nếu tạm ngừng.
    """

    plan_id: str
    name: str
    description: Optional[str] = None
    duration_days: int = 30
    price: float = 0.0
    max_check_in_sessions: Optional[int] = None
    is_pt_included: int = 0
    total_pt_sessions: int = 0
    is_active: int = 1

    def is_available(self) -> bool:
        """Kiểm tra gói tập có đang được kinh doanh mở bán hay không."""
        return bool(self.is_active)
