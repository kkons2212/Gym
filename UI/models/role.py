"""Domain Entity Role mapped to database table Role."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.base_model import BaseModel


@dataclass
class Role(BaseModel):
    """Thực thể vai trò người dùng trong hệ thống (ADMIN, MEMBER, PT)."""

    role_id: str
    role_name: Optional[str] = None
