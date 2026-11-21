"""
Reusable Login Window for Gym Management System.
Faithfully styled per Desktop/Views/LoginPage.xaml and Web/Components/Pages/Login.razor.
Dedicated for each independent role (Admin, Member, PT) without cross-portal jumping.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QCheckBox, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from styles.color_tokens import (
    DIALOG_BG, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, 
    ACCENT_PRIMARY
)
from mock_data import MEMBERS, TRAINERS

ROLE_CONFIGS = {
    "ADMIN": {
        "title": "CỔNG QUẢN TRỊ VIÊN",
        "subtitle": "Đăng nhập để điều hành vận hành phòng tập",
        "tag": "ADMINISTRATION PORTAL",
        "color": ACCENT_PRIMARY,
    },
    "MEMBER": {
        "title": "CỔNG HỘI VIÊN THỂ THAO",
        "subtitle": "Đăng nhập để xem thẻ số, InBody và đặt lịch tập",
        "tag": "MEMBER SERVICES PORTAL",
        "color": "#10B981",
    },
    "PT": {
        "title": "CỔNG HUẤN LUYỆN VIÊN (PT)",
        "subtitle": "Đăng nhập để xem lịch dạy, học viên và chấm công",
        "tag": "TRAINER SERVICES PORTAL",
        "color": "#F59E0B",
    }
}

class LoginWindow(QMainWindow):
    login_success = pyqtSignal(dict)
    
    def __init__(self, role: str = "ADMIN", parent=None):
        super().__init__(parent)
        self.role = role.upper()
        self.cfg = ROLE_CONFIGS.get(self.role, ROLE_CONFIGS["ADMIN"])
        
        self.setWindowTitle(f"{self.cfg['title']} • Gym Management")
        self.setFixedSize(460, 500)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card = QFrame()
        card.setObjectName("cardFrame")
        card.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: {DIALOG_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 16px;
                padding: 24px;
            }}
        """)
        
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(16)
        
        # Header / Brand
        tag_lbl = QLabel(self.cfg["tag"])
        tag_lbl.setStyleSheet(f"color: {self.cfg['color']}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        tag_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(tag_lbl)
        
        title_lbl = QLabel(self.cfg["title"])
        title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(title_lbl)
        
        sub_lbl = QLabel(self.cfg["subtitle"])
        sub_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setWordWrap(True)
        c_layout.addWidget(sub_lbl)
        
        # Inputs Form
        c_layout.addSpacing(10)
        
        c_layout.addWidget(QLabel("Tên đăng nhập / Số điện thoại / Email:"))
        self.txt_username = QLineEdit()
        self.txt_username.setFixedHeight(40)
        self.txt_username.setPlaceholderText("Nhập thông tin tài khoản...")
        c_layout.addWidget(self.txt_username)
        
        c_layout.addWidget(QLabel("Mật khẩu truy cập:"))
        self.txt_password = QLineEdit()
        self.txt_password.setFixedHeight(40)
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Nhập mật khẩu...")
        self.txt_password.returnPressed.connect(self.handle_login)
        c_layout.addWidget(self.txt_password)
        
        # Remember me
        self.chk_remember = QCheckBox("Ghi nhớ tài khoản trên thiết bị này")
        self.chk_remember.setChecked(True)
        c_layout.addWidget(self.chk_remember)
        
        # Login Button
        self.btn_login = QPushButton("ĐĂNG NHẬP")
        self.btn_login.setFixedHeight(42)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.cfg['color']};
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """)
        self.btn_login.clicked.connect(self.handle_login)
        c_layout.addWidget(self.btn_login)
        
        layout.addWidget(card)
        
    def handle_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Lỗi Nhập Liệu", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
            return
            
        user_data = {"username": username, "role": self.role}
        
        if self.role == "MEMBER":
            found = next((m for m in MEMBERS if username.lower() in m["code"].lower() or username in m["phone"] or username.lower() in m["email"].lower()), None)
            user_data["member"] = found or MEMBERS[0]
        elif self.role == "PT":
            found = next((pt for pt in TRAINERS if username.lower() in pt["name"].lower() or username.lower() in pt["id"].lower()), None)
            user_data["pt"] = found or TRAINERS[0]
            
        self.login_success.emit(user_data)
        self.close()
