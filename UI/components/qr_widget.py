"""QR widget for member tokens and VietQR payment images."""

import base64
import binascii
import io

import qrcode
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout

from styles.color_tokens import (
    BORDER_SUBTLE,
    CARD_BG,
    QR_BACKGROUND,
    TEXT_SECONDARY,
)


class QRWidget(QFrame):
    def __init__(
        self,
        data: str = "GYM-DEMO",
        size: int = 180,
        caption: str = "",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.setStyleSheet(
            f"""
            QFrame#cardFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 12px;
                padding: 12px;
            }}
            """
        )

        self.size = size
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.qr_label = QLabel()
        self.qr_label.setFixedSize(size, size)
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setStyleSheet(
            f"background-color: {QR_BACKGROUND}; "
            "border-radius: 8px; padding: 4px;"
        )
        layout.addWidget(self.qr_label)

        self.caption_label = None
        if caption:
            self.caption_label = QLabel(caption)
            self.caption_label.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: 11px; margin-top: 6px;"
            )
            self.caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.caption_label)

        self.set_data(data)

    def set_data(self, data: str) -> None:
        self.data = data
        if data.startswith("data:image/"):
            header, separator, encoded = data.partition(",")
            if not separator or ";base64" not in header:
                raise ValueError(
                    "QR ảnh phải có DataURL mã hóa Base64 hợp lệ."
                )
            try:
                image_data = base64.b64decode(encoded, validate=True)
            except binascii.Error as err:
                raise ValueError(
                    "Dữ liệu QR ảnh không phải Base64 hợp lệ."
                ) from err
            image = QImage.fromData(image_data)
            if image.isNull():
                raise ValueError("Không thể đọc ảnh QR từ DataURL.")
        else:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            buffer = io.BytesIO()
            qr.make_image(fill_color="black", back_color="white").save(
                buffer, format="PNG"
            )
            image = QImage.fromData(buffer.getvalue())

        pixmap = QPixmap.fromImage(image).scaled(
            self.size - 8,
            self.size - 8,
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self.qr_label.setPixmap(pixmap)
