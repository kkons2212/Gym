"""Dialog displaying a VietQR payment request."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from components.qr_widget import QRWidget
from config.settings import settings
from styles.color_tokens import ACCENT_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY


class VietQrPaymentDialog(QDialog):
    """Show the transfer QR and allow staff to confirm receipt."""

    def __init__(
        self,
        amount: int,
        order_code: str,
        package_name: str,
        parent=None,
        qr_data_url: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Thanh Toán Chuyển Khoản VietQR")
        self.setFixedSize(450, 540)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("QUÉT MÃ ĐỂ THANH TOÁN (VIETQR)")
        title.setStyleSheet(
            f"color: {ACCENT_PRIMARY}; font-size: 14px; font-weight: bold;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        amount_label = QLabel(f"{amount:,.0f}\u00a0đ")
        amount_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 26px; font-weight: bold;"
        )
        amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(amount_label)

        qr_data = qr_data_url or self._legacy_qr_payload(amount, order_code)
        layout.addWidget(
            QRWidget(
                data=qr_data,
                size=210,
                caption="Mở ứng dụng ngân hàng để quét mã",
            ),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        info_card = QFrame()
        info_card.setObjectName("cardFrame")
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(6)
        info_rows = (
            ("Mã ngân hàng:", settings.vietqr_bank_bin),
            ("Số tài khoản:", settings.vietqr_account_no),
            ("Chủ tài khoản:", settings.vietqr_account_name),
            ("Nội dung chuyển khoản:", order_code),
            ("Gói dịch vụ:", package_name),
        )
        for label_text, value_text in info_rows:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
            value = QLabel(value_text)
            value.setStyleSheet(
                f"color: {TEXT_PRIMARY}; font-size: 11px; font-weight: bold;"
            )
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            info_layout.addLayout(row)
        layout.addWidget(info_card)

        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Hủy Bỏ")
        cancel_button.setFixedHeight(40)
        cancel_button.clicked.connect(self.reject)
        confirm_button = QPushButton("✓ Đã Nhận Tiền Thành Công")
        confirm_button.setFixedHeight(40)
        confirm_button.setProperty("success", True)
        confirm_button.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(confirm_button)
        layout.addLayout(button_layout)

    @staticmethod
    def _legacy_qr_payload(amount: int, order_code: str) -> str:
        """Preserve non-desktop callers during VietQrService migration."""
        account_no = settings.vietqr_account_no.replace(" ", "")
        bank_bin = settings.vietqr_bank_bin
        amount_text = str(int(amount))
        memo = order_code[:25].replace(" ", "_")
        return (
            f"00020101021238540010A00000072701240006{bank_bin}"
            f"01{len(account_no):02d}{account_no}530370454"
            f"{len(amount_text):02d}{amount_text}5802VN62"
            f"{len(memo) + 4:02d}08{len(memo):02d}{memo}"
            "6304"
        )
