"""Centralized Enums & Business Constants for Gym Management System.

Eliminates magic strings/numbers across domain models, repositories, and UI.
Strictly mapped to physical schema from doc/GymManagement_Physical_Model.sql.
"""

from enum import Enum


class RoleID(str, Enum):
    """System User Roles mapped to table Role (RoleID)."""
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    PT = "PT"


class SubscriptionStatus(str, Enum):
    """Lifecycle status of a MemberSubscription."""
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    FROZEN = "FROZEN"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    """Allowed payment methods for Invoice (Rule: No POS card swipe)."""
    CASH = "CASH"
    VIETQR = "VIETQR"


class InvoiceStatus(str, Enum):
    """Invoice payment lifecycle status."""
    PAID = "PAID"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class TransactionType(str, Enum):
    """Type of transaction represented by an Invoice."""
    NEW_REGISTRATION = "NEW_REGISTRATION"
    RENEWAL = "RENEWAL"


class CheckInStatus(str, Enum):
    """Status recorded in CheckInLog for each entry attempt."""
    SUCCESS = "SUCCESS"
    DENIED = "DENIED"


class CheckInMethod(str, Enum):
    """Method used by member to check in at front counter."""
    QR_SCAN = "QR_SCAN"
    MANUAL = "MANUAL"


class DenialReason(str, Enum):
    """Standardized reasons for denying a check-in attempt."""
    EXPIRED = "Gói tập đã hết hạn sử dụng"
    OUT_OF_SESSIONS = "Đã sử dụng hết số lượt tập của gói"
    NOT_ACTIVE = "Thẻ hội viên không ở trạng thái hoạt động"
    SUBSCRIPTION_NOT_FOUND = "Không tìm thấy thẻ hoặc gói tập hợp lệ"
    USER_LOCKED = "Tài khoản hội viên đang bị tạm khóa"
    INVALID_QR = "Mã QR check-in không hợp lệ hoặc đã bị thay đổi"


class UserStatus(str, Enum):
    """Status of user account in table User."""
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    INACTIVE = "INACTIVE"
