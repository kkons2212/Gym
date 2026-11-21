"""
Sidebar Navigation Component matching Desktop/MainPage.xaml.
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup
from PyQt6.QtCore import pyqtSignal, Qt
from styles.color_tokens import LAYER_BG, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_PRIMARY, ACCENT_SUBTLE

NAV_ITEMS = [
    ("checkin", "Quầy Điểm Danh", "⚡"),
    ("pos", "Bán Gói và Thanh Toán", "🛒"),
    ("invoices", "Lịch Sử và In Hóa Đơn", "🧾"),
    ("members", "Quản Lý Hội Viên", "👥"),
    ("schedule", "Lịch Biểu HLV (PT)", "📅"),
    ("dashboard", "Báo Cáo và Doanh Thu", "📊"),
    ("packages", "Danh Mục Gói Tập", "📦"),
    ("staff", "Quản Lý Nhân Sự", "⚙️"),
]

class Sidebar(QFrame):
    page_changed = pyqtSignal(str)
    logout_requested = pyqtSignal()
    
    def __init__(self, current_user="Admin Hệ Thống", role="ADMIN", parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarFrame")
        self.setFixedWidth(260)
        self.setStyleSheet(f"""
            QFrame#sidebarFrame {{
                background-color: {LAYER_BG};
                border-right: 1px solid {BORDER_SUBTLE};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)
        
        # Header / Brand
        brand_frame = QFrame()
        brand_layout = QVBoxLayout(brand_frame)
        brand_layout.setContentsMargins(8, 0, 8, 12)
        brand_layout.setSpacing(2)
        
        lbl_subtitle = QLabel("GYM MANAGEMENT")
        lbl_subtitle.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        lbl_title = QLabel("Cổng Quản Trị Viên")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        
        brand_layout.addWidget(lbl_subtitle)
        brand_layout.addWidget(lbl_title)
        layout.addWidget(brand_frame)
        
        # Menu items
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.buttons = {}
        
        for key, label, icon in NAV_ITEMS:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(42)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding-left: 14px;
                    border: none;
                    border-radius: 8px;
                    background-color: transparent;
                    color: {TEXT_SECONDARY};
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #1E293B;
                    color: {TEXT_PRIMARY};
                }}
                QPushButton:checked {{
                    background-color: {ACCENT_SUBTLE};
                    color: {ACCENT_PRIMARY};
                    font-weight: bold;
                    border-left: 3px solid {ACCENT_PRIMARY};
                }}
            """)
            btn.clicked.connect(lambda checked, k=key: self.page_changed.emit(k))
            self.btn_group.addButton(btn)
            layout.addWidget(btn)
            self.buttons[key] = btn
            
        layout.addStretch()
        
        # Footer: Admin Info và Logout
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_frame.setStyleSheet(f"""
            QFrame#footerFrame {{
                border: none;
                border-top: 1px solid {BORDER_SUBTLE};
                background-color: transparent;
            }}
        """)
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(4, 12, 4, 4)
        footer_layout.setSpacing(8)
        
        user_info = QVBoxLayout()
        user_info.setContentsMargins(0, 0, 0, 0)
        user_info.setSpacing(3)
        
        user_lbl = QLabel(current_user)
        user_lbl.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 600;
                border: none;
                background: transparent;
            }}
        """)
        
        role_badge = QLabel(role)
        role_badge.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background-color: #16A34A;
                font-size: 9px;
                font-weight: bold;
                border-radius: 4px;
                padding: 2px 8px;
                border: none;
            }
        """)
        role_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        user_info.addWidget(user_lbl)
        user_info.addWidget(role_badge, alignment=Qt.AlignmentFlag.AlignLeft)
        footer_layout.addLayout(user_info, stretch=1)
        
        btn_logout = QPushButton("🚪")
        btn_logout.setToolTip("Đăng xuất")
        btn_logout.setFixedSize(36, 36)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background-color: #1E293B;
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                font-size: 16px;
                padding: 0px;
                margin: 0px;
            }}
            QPushButton:hover {{
                background-color: #7F1D1D;
                border-color: #DC2626;
            }}
        """)
        btn_logout.clicked.connect(self.logout_requested.emit)
        footer_layout.addWidget(btn_logout, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        layout.addWidget(footer_frame)
        
    def select_item(self, key: str):
        if key in self.buttons:
            self.buttons[key].setChecked(True)
