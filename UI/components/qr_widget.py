"""
QR Widget Component: Generates and displays QR codes (VietQR, Member Check-in QR)
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
import io
import qrcode
from styles.color_tokens import CARD_BG, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY

class QRWidget(QFrame):
    def __init__(self, data: str = "GYM-DEMO", size: int = 180, caption: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        
        self.size = size
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(size, size)
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setStyleSheet("background-color: #FFFFFF; border-radius: 8px; padding: 4px;")
        self.layout.addWidget(self.qr_label)
        
        self.caption_label = None
        if caption:
            self.caption_label = QLabel(caption)
            self.caption_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; margin-top: 6px;")
            self.caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.caption_label)
            
        self.set_data(data)
        
    def set_data(self, data: str):
        self.data = data
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert PIL image to QPixmap
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qimg = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimg).scaled(self.size - 8, self.size - 8, Qt.AspectRatioMode.KeepAspectRatio)
            self.qr_label.setPixmap(pixmap)
        except Exception:
            self.qr_label.setText("QR CODE")
            self.qr_label.setStyleSheet("background-color: #1E293B; color: #94A3B8; font-weight: bold;")
