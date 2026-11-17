"""
Register Member Wizard Dialog: Multi-step registration.
Matches Desktop/Dialogs/RegisterMemberWizard.xaml.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFrame, QMessageBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from styles.color_tokens import (
    DIALOG_BG, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, 
    ACCENT_PRIMARY, STATUS_SUCCESS
)
from mock_data import PACKAGES, MEMBERS
from datetime import datetime, timedelta

class RegisterMemberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Đăng Ký Hội Viên Mới • Gym Management")
        self.setFixedSize(540, 520)
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
        
        lbl_title = QLabel("ĐĂNG KÝ HỘI VIÊN MỚI")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        # Form Fields
        form_frame = QFrame()
        form_frame.setObjectName("cardFrame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)
        
        # 1. Full name
        form_layout.addWidget(QLabel("Họ và Tên Hội Viên (*):"))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Ví dụ: Nguyễn Văn An...")
        form_layout.addWidget(self.txt_name)
        
        # 2. Phone
        form_layout.addWidget(QLabel("Số Điện Thoại (*):"))
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("Ví dụ: 0988112233...")
        form_layout.addWidget(self.txt_phone)
        
        # 3. Email
        form_layout.addWidget(QLabel("Email Liên Hệ:"))
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Ví dụ: an.nguyen@gmail.com...")
        form_layout.addWidget(self.txt_email)
        
        # 4. Package selection
        form_layout.addWidget(QLabel("Gói Dịch Vụ Đăng Ký (*):"))
        self.cbo_package = QComboBox()
        for p in PACKAGES:
            self.cbo_package.addItem(f"{p['name']} - {p['price']:,.0f} đ", p)
        form_layout.addWidget(self.cbo_package)
        
        layout.addWidget(form_frame)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Hủy Bỏ")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("✓ Hoàn Tất Đăng Ký")
        btn_save.setProperty("primary", True)
        btn_save.clicked.connect(self.save_member)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
    def save_member(self):
        name = self.txt_name.text().strip()
        phone = self.txt_phone.text().strip()
        email = self.txt_email.text().strip()
        
        if not name or not phone:
            QMessageBox.warning(self, "Thiếu Thông Tin", "Vui lòng nhập Họ tên và Số điện thoại!")
            return
            
        pkg = self.cbo_package.currentData()
        new_code = f"HV-{1001 + len(MEMBERS)}"
        start_dt = datetime.now()
        exp_dt = start_dt + timedelta(days=pkg["duration_days"])
        
        new_member = {
            "code": new_code,
            "name": name,
            "phone": phone,
            "email": email or f"{phone}@gym.vn",
            "package_name": pkg["name"],
            "package_id": pkg["id"],
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "expiry_date": exp_dt.strftime("%Y-%m-%d"),
            "status": "Đang hoạt động",
            "sessions_left": pkg["pt_sessions"],
            "pt_assigned": "Nguyễn Văn Hưng" if pkg["has_pt"] else "Chưa có",
            "avatar": "",
            "weight": 65.0,
            "height": 170,
            "body_fat": 18.0,
            "muscle_mass": 32.0,
            "bmi": 22.5
        }
        MEMBERS.insert(0, new_member)
        QMessageBox.information(self, "Thành Công", f"Đã đăng ký thành công hội viên {name} với Mã HV: {new_code}")
        self.accept()
