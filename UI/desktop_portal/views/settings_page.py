"""Settings Page: Quản lý tài khoản nhân sự & cài đặt hệ thống.

Matches 1:1 with Desktop/Views/SettingsPage.xaml.
"""

from typing import Any, Dict, List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from styles.color_tokens import (
    ACCENT_PRIMARY,
    BORDER_SUBTLE,
    STATUS_DANGER,
    STATUS_SUCCESS,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

STAFF_LIST: List[Dict[str, Any]] = [
    {
        "username": "admin",
        "name": "Nguyễn Quản Trị",
        "email": "admin@gymsystem.vn",
        "phone": "0900000001",
        "role": "ADMIN",
        "status": "Hoạt động",
    },
    {
        "username": "admin02",
        "name": "Lê Thị Thu Ngân",
        "email": "ngan.le@gymsystem.vn",
        "phone": "0901234567",
        "role": "STAFF",
        "status": "Hoạt động",
    },
    {
        "username": "pt_hung",
        "name": "Nguyễn Văn Hưng",
        "email": "hung.pt@gymsystem.vn",
        "phone": "0900000002",
        "role": "PT",
        "status": "Hoạt động",
    },
    {
        "username": "pt_mai",
        "name": "Trần Thị Mai",
        "email": "mai.pt@gymsystem.vn",
        "phone": "0903344556",
        "role": "PT",
        "status": "Hoạt động",
    },
]


class SettingsPage(QWidget):
    """User account management and role-based access control page."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # LEFT COLUMN (380px): Add Staff Form
        left_card = QFrame()
        left_card.setObjectName("cardFrame")
        left_card.setFixedWidth(380)
        l_layout = QVBoxLayout(left_card)
        l_layout.setContentsMargins(20, 20, 20, 20)
        l_layout.setSpacing(12)

        lbl_title = QLabel("QUẢN LÝ TÀI KHOẢN HỆ THỐNG")
        lbl_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        l_layout.addWidget(lbl_title)

        # Current admin badge (1:1 with SettingsPage.xaml)
        admin_badge = QFrame()
        admin_badge.setObjectName("adminBadgeFrame")
        admin_badge.setStyleSheet(f"""
            QFrame#adminBadgeFrame {{
                background-color: #0F172A;
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
            }}
        """)
        ab_layout = QVBoxLayout(admin_badge)
        ab_layout.setContentsMargins(14, 12, 14, 12)
        ab_layout.setSpacing(4)

        lbl_admin_sub = QLabel("Đang đăng nhập với vai trò:")
        lbl_admin_sub.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 11px; "
            "border: none; background: transparent;"
        )
        lbl_admin_name = QLabel("Quản trị viên hệ thống (admin)")
        lbl_admin_name.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold; "
            "border: none; background: transparent;"
        )

        badge_role = QLabel("ADMIN")
        badge_role.setStyleSheet(
            "background-color: #16A34A; color: #FFFFFF; font-size: 10px; "
            "font-weight: bold; border-radius: 4px; padding: 2px 8px; "
            "border: none;"
        )
        badge_role.setFixedHeight(20)

        ab_layout.addWidget(lbl_admin_sub)
        ab_layout.addWidget(lbl_admin_name)
        ab_layout.addWidget(badge_role, alignment=Qt.AlignmentFlag.AlignLeft)
        l_layout.addWidget(admin_badge)

        lbl_add_sub = QLabel("Thêm tài khoản nhân viên / HLV:")
        lbl_add_sub.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: 600;"
        )
        l_layout.addWidget(lbl_add_sub)

        # Form Inputs (Each explicitly 38px height)
        l_layout.addWidget(QLabel("Tên đăng nhập (*):"))
        self.txt_username = QLineEdit()
        self.txt_username.setFixedHeight(38)
        self.txt_username.setPlaceholderText("tên_đăng_nhập")
        l_layout.addWidget(self.txt_username)

        l_layout.addWidget(QLabel("Họ và tên (*):"))
        self.txt_fullname = QLineEdit()
        self.txt_fullname.setFixedHeight(38)
        self.txt_fullname.setPlaceholderText("Nhập họ và tên...")
        l_layout.addWidget(self.txt_fullname)

        l_layout.addWidget(QLabel("Email (*):"))
        self.txt_email = QLineEdit()
        self.txt_email.setFixedHeight(38)
        self.txt_email.setPlaceholderText("email@gymsystem.vn")
        l_layout.addWidget(self.txt_email)

        l_layout.addWidget(QLabel("Số điện thoại (*):"))
        self.txt_phone = QLineEdit()
        self.txt_phone.setFixedHeight(38)
        self.txt_phone.setPlaceholderText("0901234567")
        l_layout.addWidget(self.txt_phone)

        l_layout.addWidget(QLabel("Mật khẩu (*):"))
        self.txt_password = QLineEdit()
        self.txt_password.setFixedHeight(38)
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText(
            "Nhập mật khẩu (tối thiểu 6 ký tự)..."
        )
        l_layout.addWidget(self.txt_password)

        l_layout.addWidget(QLabel("Vai trò (Role):"))
        self.cbo_role = QComboBox()
        self.cbo_role.setFixedHeight(38)
        self.cbo_role.addItems([
            "Huấn luyện viên cá nhân (PT)",
            "Quản trị viên (ADMIN)",
        ])
        l_layout.addWidget(self.cbo_role)

        l_layout.addStretch()

        btn_create = QPushButton("Tạo Tài Khoản")
        btn_create.setFixedHeight(44)
        btn_create.setProperty("primary", True)
        btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_create.clicked.connect(self.add_staff)
        l_layout.addWidget(btn_create)

        main_layout.addWidget(left_card)

        # RIGHT COLUMN: Staff Table
        right_card = QFrame()
        right_card.setObjectName("cardFrame")
        r_layout = QVBoxLayout(right_card)
        r_layout.setContentsMargins(20, 20, 20, 20)
        r_layout.setSpacing(14)

        # Header Row (Title on left, Refresh Button on right)
        right_header = QHBoxLayout()
        right_header.setSpacing(12)

        right_title_box = QVBoxLayout()
        right_title_box.setSpacing(4)
        lbl_right_title = QLabel("DANH SÁCH TÀI KHOẢN VẬN HÀNH")
        lbl_right_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        lbl_right_sub = QLabel(
            "Danh sách người dùng có quyền truy cập hệ thống (Admin & PT)"
        )
        lbl_right_sub.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px;"
        )
        right_title_box.addWidget(lbl_right_title)
        right_title_box.addWidget(lbl_right_sub)
        right_header.addLayout(right_title_box)
        right_header.addStretch()

        btn_refresh = QPushButton("Tải Lại")
        btn_refresh.setFixedHeight(36)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self.render_table)
        right_header.addWidget(btn_refresh)
        r_layout.addLayout(right_header)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Tên Đăng Nhập",
            "Họ Tên",
            "Email & SĐT",
            "Vai Trò",
            "Trạng Thái",
            "Thao Tác",
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(5, 180)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        r_layout.addWidget(self.table)

        main_layout.addWidget(right_card, 1)
        self.render_table()

    def render_table(self) -> None:
        self.table.setRowCount(len(STAFF_LIST))
        for row, s in enumerate(STAFF_LIST):
            self.table.setItem(row, 0, QTableWidgetItem(s["username"]))
            self.table.setItem(row, 1, QTableWidgetItem(s["name"]))

            email_phone = f"{s.get('email', '')} • {s.get('phone', '')}"
            contact_text = email_phone.strip(" •")
            self.table.setItem(row, 2, QTableWidgetItem(contact_text))

            role_item = QTableWidgetItem(s["role"])
            role_item.setForeground(QColor(ACCENT_PRIMARY))
            self.table.setItem(row, 3, role_item)

            is_active = s["status"] == "Hoạt động"
            st_item = QTableWidgetItem(s["status"])
            st_item.setForeground(
                QColor(STATUS_SUCCESS if is_active else STATUS_DANGER)
            )
            self.table.setItem(row, 4, st_item)

            # Action buttons in cell container (prevents layout clipping)
            btn_edit = QPushButton("Sửa")
            btn_edit.setProperty("tableAction", True)
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.clicked.connect(
                lambda ch, idx=row: self.open_edit_user(idx)
            )

            btn_lock = QPushButton("Khóa TK" if is_active else "Mở Khóa")
            btn_lock.setProperty("tableAction", True)
            btn_lock.setProperty(
                "actionVariant", "danger" if is_active else "success"
            )
            btn_lock.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_lock.clicked.connect(
                lambda ch, idx=row: self._toggle_status(idx)
            )

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_lock)
            self.table.setCellWidget(row, 5, action_widget)

    def open_edit_user(self, idx: int) -> None:
        staff = STAFF_LIST[idx]
        user_name = staff['username']
        QMessageBox.information(
            self,
            "Sửa Thông Tin Tài Khoản",
            f"Chỉnh sửa nhân sự: {staff['name']} (@{user_name})\n"
            f"Vai trò: {staff['role']} | Email: {staff.get('email', '—')}\n"
            "Form cập nhật hồ sơ và phân quyền đang sẵn sàng kết nối.",
        )

    def _toggle_status(self, idx: int) -> None:
        staff = STAFF_LIST[idx]
        new_st = "Tạm khóa" if staff["status"] == "Hoạt động" else "Hoạt động"
        staff["status"] = new_st
        self.render_table()
        QMessageBox.information(
            self,
            "Trạng Thái",
            f"Đã cập nhật trạng thái của {staff['username']} "
            f"thành '{new_st}'!",
        )

    def add_staff(self) -> None:
        u = self.txt_username.text().strip()
        n = self.txt_fullname.text().strip()
        e = self.txt_email.text().strip()
        p = self.txt_phone.text().strip()
        _pwd = self.txt_password.text().strip()
        r_text = self.cbo_role.currentText()
        r = (
            "PT" if "PT" in r_text
            else ("ADMIN" if "ADMIN" in r_text else "STAFF")
        )

        if not u or not n:
            QMessageBox.warning(
                self,
                "Thiếu Thông Tin",
                "Vui lòng nhập tên đăng nhập và họ tên!",
            )
            return

        STAFF_LIST.append({
            "username": u,
            "name": n,
            "email": e or f"{u}@gymsystem.vn",
            "phone": p or "—",
            "password": _pwd or "staff123",
            "role": r,
            "status": "Hoạt động",
        })
        self.render_table()
        self.txt_username.clear()
        self.txt_fullname.clear()
        self.txt_email.clear()
        self.txt_phone.clear()
        self.txt_password.clear()
        QMessageBox.information(
            self, "Thành Công", f"Đã thêm tài khoản nhân sự {u} thành công!"
        )
