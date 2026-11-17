"""
VietQR Payment Dialog: Displays dynamic QR code, bank info, and transfer content.
Matches Desktop/Dialogs/VietQrPaymentDialog.xaml.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from styles.color_tokens import (
    DIALOG_BG, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, 
    ACCENT_PRIMARY, STATUS_SUCCESS
)
from components.qr_widget import QRWidget

class VietQrPaymentDialog(QDialog):
    def __init__(self, amount: int, order_code: str, package_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thanh Toán Chuyển Khoản VietQR")
        self.setFixedSize(450, 540)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {DIALOG_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 16px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        
        # Header
        lbl_title = QLabel("QUÉT MÃ ĐỂ THANH TOÁN (VIETQR)")
        lbl_title.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 14px; font-weight: bold;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        lbl_amount = QLabel(f"{amount:,.0f} VNĐ")
        lbl_amount.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 26px; font-weight: bold;")
        lbl_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_amount)
        
        # QR Code Display
        qr_payload = f"00020101021238540010A00000072701240006970422011409876543215303704540{amount}5802VN62150811{order_code}6304"
        self.qr_widget = QRWidget(data=qr_payload, size=210, caption="Mở App Ngân Hàng hoặc Ví Điện Tử để quét mã")
        layout.addWidget(self.qr_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Details Card
        info_card = QFrame()
        info_card.setObjectName("cardFrame")
        info_card.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 10px;")
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(6)
        
        info_rows = [
            ("Ngân hàng nhận:", "MB Bank (Ngân hàng Quân Đội)"),
            ("Số tài khoản:", "0987654321"),
            ("Chủ tài khoản:", "HE THONG PHONG TAP GYM"),
            ("Nội dung chuyển khoản:", order_code),
            ("Gói dịch vụ:", package_name)
        ]
        
        for k, v in info_rows:
            r = QHBoxLayout()
            lk = QLabel(k)
            lk.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
            lv = QLabel(v)
            lv.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 11px; font-weight: bold;")
            r.addWidget(lk)
            r.addStretch()
            r.addWidget(lv)
            info_layout.addLayout(r)
            
        layout.addWidget(info_card)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Hủy Bỏ")
        btn_cancel.clicked.connect(self.reject)
        
        btn_confirm = QPushButton("✓ Đã Nhận Tiền Thành Công")
        btn_confirm.setProperty("success", True)
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)
        layout.addLayout(btn_layout)
