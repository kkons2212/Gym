"""
Login & Portal Selector Dialog: Đăng nhập & Lựa chọn cổng truy cập.
Matches Desktop/Views/LoginPage.xaml & Web/Components/Pages/Login.razor.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QFrame, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from styles.color_tokens import (
    DIALOG_BG, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, 
    ACCENT_PRIMARY
)

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_role = None
        self.setWindowTitle("Đăng Nhập Hệ Thống Gym • Chọn Cổng Truy Cập")
        self.setFixedSize(480, 560)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {DIALOG_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 16px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
        
        # Logo / Title Box
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_brand = QLabel("GYM MANAGEMENT SYSTEM")
        lbl_brand.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        lbl_brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_main = QLabel("Cổng Dịch Vụ Thể Thao")
        lbl_main.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 22px; font-weight: bold;")
        lbl_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_desc = QLabel("Chọn vai trò hoặc đăng nhập để điều hành & sử dụng hệ thống")
        lbl_desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_box.addWidget(lbl_brand)
        title_box.addWidget(lbl_main)
        title_box.addWidget(lbl_desc)
        layout.addLayout(title_box)
        
        # Fast Role Selector Buttons
        role_frame = QFrame()
        role_frame.setObjectName("cardFrame")
        role_frame.setStyleSheet(f"background-color: #0F172A; border: 1px solid {BORDER_SUBTLE}; border-radius: 12px; padding: 12px;")
        rf_layout = QVBoxLayout(role_frame)
        rf_layout.setSpacing(10)
        
        lbl_rf = QLabel("TRUY CẬP NHANH THEO VAI TRÒ (QUICK ACCESS):")
        lbl_rf.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        rf_layout.addWidget(lbl_rf)
        
        btn_admin = QPushButton("🖥️  1. Cổng Quản Trị Viên / Lễ Tân (Desktop)")
        btn_admin.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_admin.setFixedHeight(40)
        btn_admin.setStyleSheet(f"background-color: #1E293B; border: 1px solid {ACCENT_PRIMARY}; color: {TEXT_PRIMARY}; font-weight: bold; text-align: left; padding-left: 14px;")
        btn_admin.clicked.connect(lambda: self.pick_role("ADMIN"))
        rf_layout.addWidget(btn_admin)
        
        btn_member = QPushButton("📱  2. Cổng Hội Viên Thể Thao (Member Web)")
        btn_member.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_member.setFixedHeight(40)
        btn_member.setStyleSheet(f"background-color: #1E293B; border: 1px solid #10B981; color: {TEXT_PRIMARY}; font-weight: bold; text-align: left; padding-left: 14px;")
        btn_member.clicked.connect(lambda: self.pick_role("MEMBER"))
        rf_layout.addWidget(btn_member)
        
        btn_pt = QPushButton("🏋️  3. Cổng Huấn Luyện Viên PT (Trainer Web)")
        btn_pt.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pt.setFixedHeight(40)
        btn_pt.setStyleSheet(f"background-color: #1E293B; border: 1px solid #F59E0B; color: {TEXT_PRIMARY}; font-weight: bold; text-align: left; padding-left: 14px;")
        btn_pt.clicked.connect(lambda: self.pick_role("PT"))
        rf_layout.addWidget(btn_pt)
        
        layout.addWidget(role_frame)
        
        # Standard Credential Form
        layout.addWidget(QLabel("Hoặc đăng nhập bằng tài khoản:"))
        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("Tên đăng nhập hoặc Email...")
        self.txt_user.setText("admin")
        layout.addWidget(self.txt_user)
        
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setPlaceholderText("Mật khẩu...")
        self.txt_pass.setText("••••••••")
        layout.addWidget(self.txt_pass)
        
        btn_login = QPushButton("Đăng Nhập")
        btn_login.setFixedHeight(38)
        btn_login.setProperty("primary", True)
        btn_login.clicked.connect(self.submit_login)
        layout.addWidget(btn_login)
        
    def pick_role(self, role: str):
        self.selected_role = role
        self.accept()
        
    def submit_login(self):
        u = self.txt_user.text().strip().lower()
        if "admin" in u or "letan" in u:
            self.selected_role = "ADMIN"
        elif "pt" in u or "hung" in u or "mai" in u:
            self.selected_role = "PT"
        else:
            self.selected_role = "MEMBER"
        self.accept()
