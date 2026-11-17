"""
Member Detail Dialog: Displays full profile, current membership, and InBody stats.
Matches Desktop/Dialogs/MemberDetailDialog.xaml.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from styles.color_tokens import (
    DIALOG_BG, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, 
    ACCENT_PRIMARY, STATUS_SUCCESS, STATUS_WARNING, STATUS_DANGER
)
from components.qr_widget import QRWidget

class MemberDetailDialog(QDialog):
    def __init__(self, member: dict, parent=None):
        super().__init__(parent)
        self.member = member
        self.setWindowTitle(f"Hồ Sơ Hội Viên • {member['name']}")
        self.setFixedSize(580, 560)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {DIALOG_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 16px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header Row
        header = QHBoxLayout()
        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 36px; background-color: #1E293B; border-radius: 24px; padding: 6px;")
        
        name_box = QVBoxLayout()
        lbl_name = QLabel(member["name"])
        lbl_name.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        
        lbl_code = QLabel(f"Mã HV: {member['code']} • SĐT: {member['phone']}")
        lbl_code.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        name_box.addWidget(lbl_name)
        name_box.addWidget(lbl_code)
        
        header.addWidget(avatar)
        header.addLayout(name_box)
        header.addStretch()
        
        # Status Badge
        badge = QLabel(f"  {member['status'].upper()}  ")
        if member["status"] == "Đang hoạt động":
            badge.setStyleSheet("color: #4ADE80; background-color: #064E3B; border-radius: 4px; font-size: 11px; font-weight: bold; padding: 4px;")
        else:
            badge.setStyleSheet("color: #F87171; background-color: #7F1D1D; border-radius: 4px; font-size: 11px; font-weight: bold; padding: 4px;")
        header.addWidget(badge)
        layout.addLayout(header)
        
        # Content Grid (Membership info + QR)
        content_row = QHBoxLayout()
        content_row.setSpacing(16)
        
        # Membership details card
        card = QFrame()
        card.setObjectName("cardFrame")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(8)
        
        c_title = QLabel("THÔNG TIN GÓI TẬP HIỆN TẠI")
        c_title.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 12px; font-weight: bold;")
        c_layout.addWidget(c_title)
        
        rows = [
            ("Gói dịch vụ:", member["package_name"]),
            ("Ngày bắt đầu:", member["start_date"]),
            ("Ngày hết hạn:", member["expiry_date"]),
            ("Số buổi PT còn:", f"{member['sessions_left']} buổi"),
            ("HLV phụ trách:", member["pt_assigned"]),
            ("Email:", member["email"]),
        ]
        
        for k, v in rows:
            r = QHBoxLayout()
            r.addWidget(QLabel(k))
            r.addStretch()
            val = QLabel(v)
            val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
            r.addWidget(val)
            c_layout.addLayout(r)
            
        content_row.addWidget(card, 6)
        
        # Digital QR Card
        qr = QRWidget(data=member["code"], size=150, caption="Mã QR Check-in Cá Nhân")
        content_row.addWidget(qr, 4)
        layout.addLayout(content_row)
        
        # InBody stats card
        inbody_card = QFrame()
        inbody_card.setObjectName("cardFrame")
        ib_layout = QGridLayout(inbody_card)
        ib_layout.setSpacing(12)
        
        ib_layout.addWidget(QLabel("Cân nặng:"), 0, 0)
        ib_layout.addWidget(QLabel(f"{member['weight']} kg"), 0, 1)
        ib_layout.addWidget(QLabel("Chiều cao:"), 0, 2)
        ib_layout.addWidget(QLabel(f"{member['height']} cm"), 0, 3)
        
        ib_layout.addWidget(QLabel("Khối lượng cơ:"), 1, 0)
        ib_layout.addWidget(QLabel(f"{member['muscle_mass']} kg"), 1, 1)
        ib_layout.addWidget(QLabel("Tỷ lệ mỡ:"), 1, 2)
        ib_layout.addWidget(QLabel(f"{member['body_fat']} %"), 1, 3)
        
        layout.addWidget(inbody_card)
        
        # Buttons
        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
