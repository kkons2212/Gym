"""
Settings Page: Quản lý tài khoản nhân sự & cài đặt hệ thống (1:1 with Desktop/Views/SettingsPage.xaml).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from styles.color_tokens import (
    TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, LAYER_BG, 
    BORDER_SUBTLE, ACCENT_PRIMARY, STATUS_SUCCESS
)

STAFF_LIST = [
    {"username": "admin", "name": "Nguyễn Quản Trị", "role": "ADMIN", "status": "Hoạt động"},
    {"username": "letan01", "name": "Lê Thị Thu Ngân", "role": "STAFF", "status": "Hoạt động"},
    {"username": "pt_hung", "name": "Nguyễn Văn Hưng", "role": "PT", "status": "Hoạt động"},
    {"username": "pt_mai", "name": "Trần Thị Mai", "role": "PT", "status": "Hoạt động"},
]

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # LEFT COLUMN (380px): Add Staff Form
        left_card = QFrame()
        left_card.setObjectName("cardFrame")
        left_card.setFixedWidth(360)
        l_layout = QVBoxLayout(left_card)
        l_layout.setContentsMargins(20, 20, 20, 20)
        l_layout.setSpacing(14)
        
        lbl_title = QLabel("QUẢN LÝ NHÂN SỰ HỆ THỐNG")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        l_layout.addWidget(lbl_title)
        
        # Current admin badge
        admin_badge = QFrame()
        admin_badge.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 10px;")
        ab_layout = QVBoxLayout(admin_badge)
        ab_layout.setSpacing(4)
        ab_layout.addWidget(QLabel("Đang đăng nhập với vai trò: Quản Trị Viên (Admin)"))
        ab_layout.addWidget(QLabel("Tài khoản: admin@gym.vn"))
        l_layout.addWidget(admin_badge)
        
        l_layout.addWidget(QLabel("Tên đăng nhập:"))
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("vd: letan02...")
        l_layout.addWidget(self.txt_username)
        
        l_layout.addWidget(QLabel("Họ và Tên:"))
        self.txt_fullname = QLineEdit()
        self.txt_fullname.setPlaceholderText("vd: Trần Văn Bình...")
        l_layout.addWidget(self.txt_fullname)
        
        l_layout.addWidget(QLabel("Vai trò phân quyền:"))
        self.cbo_role = QComboBox()
        self.cbo_role.addItems(["Nhân Viên Lễ Tân (STAFF)", "Huấn Luyện Viên (PT)", "Quản Trị Viên (ADMIN)"])
        l_layout.addWidget(self.cbo_role)
        
        l_layout.addStretch()
        
        btn_create = QPushButton("+ Thêm Tài Khoản Mới")
        btn_create.setFixedHeight(40)
        btn_create.setProperty("primary", True)
        btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_create.clicked.connect(self.add_staff)
        l_layout.addWidget(btn_create)
        
        main_layout.addWidget(left_card)
        
        # RIGHT COLUMN: Staff Table
        right_col = QVBoxLayout()
        right_col.setSpacing(14)
        
        lbl_right_title = QLabel("DANH SÁCH TÀI KHOẢN VẬN HÀNH")
        lbl_right_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        right_col.addWidget(lbl_right_title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tên Đăng Nhập", "Họ Tên", "Vai Trò", "Trạng Thái", "Thao Tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        right_col.addWidget(self.table)
        
        main_layout.addLayout(right_col)
        self.render_table()
        
    def render_table(self):
        self.table.setRowCount(len(STAFF_LIST))
        for row, s in enumerate(STAFF_LIST):
            self.table.setItem(row, 0, QTableWidgetItem(s["username"]))
            self.table.setItem(row, 1, QTableWidgetItem(s["name"]))
            
            role_item = QTableWidgetItem(s["role"])
            role_item.setForeground(Qt.GlobalColor.cyan)
            self.table.setItem(row, 2, role_item)
            
            st_item = QTableWidgetItem(s["status"])
            st_item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row, 3, st_item)
            
            btn_lock = QPushButton("Khóa / Đổi MK")
            btn_lock.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_lock.setStyleSheet("font-size: 11px; padding: 4px 8px;")
            btn_lock.clicked.connect(lambda ch, u=s: QMessageBox.information(self, "Tài Khoản", f"Quản lý mật khẩu hoặc trạng thái của {u['username']}"))
            self.table.setCellWidget(row, 4, btn_lock)

    def add_staff(self):
        u = self.txt_username.text().strip()
        n = self.txt_fullname.text().strip()
        r = self.cbo_role.currentText().split("(")[1].replace(")", "")
        if not u or not n:
            QMessageBox.warning(self, "Thiếu Thông Tin", "Vui lòng nhập tên đăng nhập và họ tên!")
            return
        STAFF_LIST.append({"username": u, "name": n, "role": r, "status": "Hoạt động"})
        self.render_table()
        self.txt_username.clear()
        self.txt_fullname.clear()
        QMessageBox.information(self, "Thành Công", f"Đã thêm tài khoản nhân viên {u} thành công!")
