"""Custom Exception Hierarchy for Gym Management System.

Provides high-semantic error tracking, clear error codes, and fail-fast guarantees.
All exceptions inherit from GymBaseException.
"""

from typing import Any, Optional


class GymBaseException(Exception):
    """Base exception for all domain and operational errors in Gym Management."""

    def __init__(self, message: str, error_code: str = "GYM_GENERAL_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class DuplicateUserException(GymBaseException):
    """Raised when registering a user with an already existing phone, email, or username."""

    def __init__(self, field_name: str, value: str) -> None:
        super().__init__(
            message=f"Hội viên hoặc tài khoản với {field_name}='{value}' đã tồn tại trong hệ thống.",
            error_code="USER_DUPLICATE_ERROR",
        )
        self.field_name = field_name
        self.value = value


class PackageNotFoundException(GymBaseException):
    """Raised when a referenced PackagePlan cannot be found or is inactive."""

    def __init__(self, plan_id: str) -> None:
        super().__init__(
            message=f"Gói dịch vụ có mã '{plan_id}' không tồn tại hoặc đã ngừng kinh doanh.",
            error_code="PACKAGE_NOT_FOUND",
        )
        self.plan_id = plan_id


class SubscriptionExpiredException(GymBaseException):
    """Raised when an operation is requested on an expired subscription."""

    def __init__(self, message: str, end_date: Any = None) -> None:
        super().__init__(
            message=message,
            error_code="SUBSCRIPTION_EXPIRED",
        )
        self.end_date = end_date


class CheckInDeniedException(GymBaseException):
    """Raised when a check-in attempt fails validation guardrails."""

    def __init__(self, reason: str, username: Optional[str] = None) -> None:
        super().__init__(
            message=f"Từ chối điểm danh hội viên {username or ''}: {reason}".strip(),
            error_code="CHECKIN_DENIED",
        )
        self.reason = reason
        self.username = username


class DatabaseTransactionException(GymBaseException):
    """Raised when a database query or transaction fails and is safely rolled back."""

    def __init__(self, original_error: Any) -> None:
        super().__init__(
            message=f"Lỗi giao dịch cơ sở dữ liệu: {original_error}",
            error_code="DB_TRANSACTION_ERROR",
        )
        self.original_error = original_error


class ValidationException(GymBaseException):
    """Raised when business input validation fails."""

    def __init__(self, message: str, field_name: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
        )
        self.field_name = field_name
