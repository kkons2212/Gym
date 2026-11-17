"""Domain Entity User mapped to database table User."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Optional

from constants import RoleID, UserStatus
from exceptions import ValidationException
from models.base_model import BaseModel


@dataclass
class User(BaseModel):
    """Thực thể Người dùng / Hội viên / Nhân viên phòng tập.

    Thuộc tính:
        username: Khóa chính (CCCD, mã định danh, hoặc username duy nhất).
        role_id: Khóa ngoại trỏ tới Role (ADMIN, MEMBER, PT).
        full_name: Họ và tên đầy đủ.
        phone: Số điện thoại liên hệ (Unique).
        email: Địa chỉ hòm thư điện tử.
        password_hash: Chuỗi hash mật khẩu bảo mật.
        gender: Giới tính (1: Nam, 0: Nữ, None: Khác).
        status: Trạng thái tài khoản (ACTIVE, LOCKED, INACTIVE).
        created_at: Ngày tạo hồ sơ.
    """

    username: str
    role_id: str = RoleID.MEMBER.value
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    gender: Optional[int] = 1
    status: str = UserStatus.ACTIVE.value
    created_at: Optional[date] = None

    def is_active(self) -> bool:
        """Kiểm tra tài khoản có đang ở trạng thái hoạt động hay không."""
        return self.status == UserStatus.ACTIVE.value

    def validate_phone(self) -> str:
        """Chuẩn hóa và kiểm tra tính hợp lệ của số điện thoại Việt Nam."""
        if not self.phone:
            raise ValidationException("Số điện thoại không được để trống.", "phone")

        clean_phone = re.sub(r"[\s\-\.]", "", self.phone)
        if clean_phone.startswith("+84"):
            clean_phone = "0" + clean_phone[3:]

        if not re.match(r"^0\d{9}$", clean_phone):
            raise ValidationException(
                f"Số điện thoại '{self.phone}' không đúng định dạng chuẩn 10 chữ số tại Việt Nam.",
                "phone",
            )
        self.phone = clean_phone
        return clean_phone
