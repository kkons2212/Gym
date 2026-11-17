"""Domain Entity Invoice mapped to database table Invoice."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from constants import InvoiceStatus, PaymentMethod, TransactionType
from exceptions import ValidationException
from models.base_model import BaseModel


@dataclass
class Invoice(BaseModel):
    """Thực thể Hóa đơn thanh toán giao dịch phòng tập.

    Thuộc tính:
        invoice_id: Khóa chính (HD001...).
        invoice_code: Mã hóa đơn duy nhất hiển thị cho khách (INV-20261117-XXXX).
        transaction_type: Loại giao dịch (NEW_REGISTRATION, RENEWAL).
        subtotal_amount: Tiền trước giảm/thuế.
        total_amount: Tổng tiền thực thu (VNĐ).
        payment_method: Phương thức (CASH hoặc VIETQR).
        status: Trạng thái (PAID, REFUNDED, CANCELLED).
        refund_amount: Số tiền hoàn lại nếu có.
        refund_reason: Lý do hoàn tiền.
        paid_at: Ngày thanh toán.
        username: Mã hội viên (FK -> User).
        subscription_id: Mã gói thẻ tạo ra (FK -> MemberSubscription).
        created_by_admin_id: Nhân viên lễ tân lập hóa đơn.
        check_in_log_id: Mã log phạt nếu là hóa đơn quá giờ.
    """

    invoice_id: str
    username: str
    subscription_id: str
    invoice_code: Optional[str] = None
    transaction_type: str = TransactionType.NEW_REGISTRATION.value
    subtotal_amount: float = 0.0
    total_amount: float = 0.0
    payment_method: str = PaymentMethod.VIETQR.value
    status: str = InvoiceStatus.PAID.value
    refund_amount: float = 0.0
    refund_reason: Optional[str] = None
    paid_at: Optional[date] = None
    created_by_admin_id: Optional[str] = None
    check_in_log_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Kiểm tra tính hợp lệ của phương thức thanh toán (Zero POS rule)."""
        allowed = {PaymentMethod.CASH.value, PaymentMethod.VIETQR.value}
        if self.payment_method not in allowed:
            raise ValidationException(
                f"Phương thức thanh toán '{self.payment_method}' không được hỗ trợ. Chỉ chấp nhận CASH hoặc VIETQR.",
                "payment_method",
            )
