"""Base Model for Domain Entities in Gym Management System.

Provides bidirectional serialization between OOP entity attributes (snake_case)
and physical database column names (PascalCase/case-insensitive).
"""

from __future__ import annotations

from abc import ABC
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Type, TypeVar

T = TypeVar("T", bound="BaseModel")


class BaseModel(ABC):
    """Abstract Base Class for all domain entities."""

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thực thể thành dictionary Python."""
        if is_dataclass(self):
            return asdict(self)
        return {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        }

    @classmethod
    def from_row(cls: Type[T], row: Dict[str, Any]) -> T:
        """Tạo đối tượng Entity từ kết quả truy vấn CSDL (dictionary cursor).

        Tự động chuẩn hóa tên cột để hỗ trợ cả PascalCase và snake_case.

        Args:
            row: Dòng dữ liệu từ MySQL dictionary cursor.

        Returns:
            Đối tượng Entity thuộc lớp con kế thừa.
        """
        if not row:
            raise ValueError(f"Không thể khởi tạo {cls.__name__} từ dữ liệu rỗng.")

        # Tạo map chuẩn hóa lowercase_key -> raw_value
        normalized = {k.lower().replace("_", ""): v for k, v in row.items()}

        kwargs: Dict[str, Any] = {}
        # Lấy danh sách field/init params của class
        init_annotations = getattr(cls, "__annotations__", {})

        for field_name in init_annotations:
            norm_field = field_name.lower().replace("_", "")
            if norm_field in normalized:
                kwargs[field_name] = normalized[norm_field]

        return cls(**kwargs)
