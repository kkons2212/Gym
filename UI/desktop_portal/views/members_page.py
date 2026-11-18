"""Live member lookup and registration page."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from exceptions import DatabaseTransactionException
from repositories.subscription_repository import SubscriptionRepository
from desktop_portal.dialogs.member_detail_dialog import MemberDetailDialog
from desktop_portal.dialogs.register_member_dialog import RegisterMemberDialog
from styles.color_tokens import (
    STATUS_DANGER,
    STATUS_SUCCESS,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class MembersPage(QWidget):
    """Search members and view their persisted membership details."""

    def __init__(
        self,
        parent=None,
        subscription_repo: Optional[SubscriptionRepository] = None,
    ) -> None:
        super().__init__(parent)
        self.subscription_repo = subscription_repo or SubscriptionRepository()
        self._members: List[Dict[str, Any]] = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = QLabel("QUẢN LÝ HỘI VIÊN & GÓI TẬP")
        title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;"
        )
        description = QLabel(
            "Tra cứu thông tin, gia hạn và bảo lưu gói tập (F3)"
        )
        description.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        title_box.addWidget(title)
        title_box.addWidget(description)
        header.addLayout(title_box)
        header.addStretch()

        add_button = QPushButton("  + Đăng Ký Hội Viên Mới  ")
        add_button.setFixedHeight(40)
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.setProperty("primary", True)
        add_button.clicked.connect(self.open_register_dialog)
        header.addWidget(add_button)
        main_layout.addLayout(header)

        # Search Bar & Status Segmented Filters (1:1 with MembersPage.xaml)
        filter_row = QHBoxLayout()
        filter_row.setSpacing(16)

        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(40)
        self.txt_search.setPlaceholderText(
            "Tìm kiếm theo Họ tên, SĐT, hoặc Mã hội viên..."
        )
        self.txt_search.textChanged.connect(self.filter_table)
        filter_row.addWidget(self.txt_search, 1)

        # Status filter buttons
        self._filter_tag = "ALL"
        self._filter_buttons: Dict[str, QPushButton] = {}
        filters_box = QHBoxLayout()
        filters_box.setSpacing(8)

        filter_configs = [
            ("ALL", "Tất cả", TEXT_PRIMARY),
            ("ACTIVE", "Đang Hoạt Động", STATUS_SUCCESS),
            ("FROZEN", "Đang bảo lưu", "#FBBF24"),
            ("EXPIRED", "Đã hết hạn", STATUS_DANGER),
        ]

        for tag, label_text, color in filter_configs:
            btn = QPushButton(label_text)
            btn.setFixedHeight(40)
            btn.setProperty("filterButton", True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if tag == "ALL":
                btn.setProperty("active", True)
            if color != TEXT_PRIMARY:
                btn.setStyleSheet(f"color: {color};")
            btn.clicked.connect(lambda ch, t=tag: self._set_filter(t))
            self._filter_buttons[tag] = btn
            filters_box.addWidget(btn)

        filter_row.addLayout(filters_box)
        main_layout.addLayout(filter_row)

        # Compatibility proxy for cbo_status if referenced externally
        self.cbo_status = QComboBox()
        self.cbo_status.addItems([
            "Tất cả trạng thái", "Đang hoạt động", "Hết hạn", "Hết lượt",
            "Đang bảo lưu", "Đã hủy", "Chưa đăng ký", "Tạm khóa"
        ])
        self.cbo_status.hide()

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        main_layout.addWidget(self.status_label)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Mã HV",
                "Họ tên",
                "Số điện thoại",
                "Gói tập hiện tại",
                "Hạn sử dụng",
                "Trạng thái",
                "Thao tác",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            6, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(6, 220)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        main_layout.addWidget(self.table)
        self._displayed_members: List[Dict[str, Any]] = []
        self._load_members()

    def _set_filter(self, tag: str) -> None:
        self._filter_tag = tag
        for btn_tag, btn in self._filter_buttons.items():
            is_active = (btn_tag == tag)
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.filter_table()

    @staticmethod
    def _format_date(value: Any) -> str:
        if isinstance(value, (date, datetime)):
            return value.strftime("%Y-%m-%d")
        return str(value) if value else "—"

    @classmethod
    def _to_member_view(cls, row: Dict[str, Any]) -> Dict[str, Any]:
        today = date.today()
        user_status = row.get("user_status")
        subscription_status = row.get("subscription_status")
        end_date = row.get("end_date")
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        elif isinstance(end_date, str):
            end_date = date.fromisoformat(end_date[:10])

        if user_status != "ACTIVE":
            status = "Tạm khóa"
        elif not row.get("subscription_id"):
            status = "Chưa đăng ký"
        elif subscription_status == "FROZEN":
            status = "Đang bảo lưu"
        elif subscription_status == "CANCELLED":
            status = "Đã hủy"
        elif (
            subscription_status == "ACTIVE"
            and row.get("remaining_check_in_sessions") is not None
            and row.get("remaining_check_in_sessions") <= 0
        ):
            status = "Hết lượt"
        elif (
            subscription_status == "ACTIVE"
            and (not end_date or end_date >= today)
            and (
                row.get("remaining_check_in_sessions") is None
                or row.get("remaining_check_in_sessions") > 0
            )
        ):
            status = "Đang hoạt động"
        else:
            status = "Hết hạn"

        return {
            "code": row.get("username") or "—",
            "name": row.get("full_name") or "—",
            "phone": row.get("phone") or "—",
            "email": row.get("email") or "",
            "package_name": row.get("plan_name") or "Chưa đăng ký",
            "start_date": cls._format_date(row.get("start_date")),
            "expiry_date": cls._format_date(end_date),
            "status": status,
            "sessions_left": row.get("remaining_pt_sessions"),
            "check_ins_left": row.get("remaining_check_in_sessions"),
            "pt_assigned": row.get("assigned_pt_id"),
            "qr_code": row.get("qr_code"),
            "weight": None,
            "height": None,
            "body_fat": None,
            "muscle_mass": None,
        }

    def _load_members(self) -> None:
        try:
            rows = self.subscription_repo.get_member_summaries()
        except DatabaseTransactionException as err:
            self.status_label.setText(str(err))
            self.status_label.show()
            return

        self._members = [self._to_member_view(row) for row in rows]
        self.status_label.clear()
        self.status_label.hide()
        self.filter_table()

    def render_table(self, members: List[Dict[str, Any]]) -> None:
        self._displayed_members = members
        self.table.setRowCount(len(members))
        for row_index, member in enumerate(members):
            values = (
                member["code"],
                member["name"],
                member["phone"],
                member["package_name"],
                member["expiry_date"],
                member["status"],
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column == 5:
                    color = (
                        STATUS_SUCCESS
                        if member["status"] == "Đang hoạt động"
                        else STATUS_DANGER
                    )
                    item.setForeground(QColor(color))
                self.table.setItem(row_index, column, item)

            btn_edit = QPushButton("Sửa")
            btn_edit.setProperty("tableAction", True)
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.clicked.connect(
                lambda ch, m=member: self.open_edit_dialog(m)
            )

            btn_freeze = QPushButton("Bảo lưu")
            btn_freeze.setProperty("tableAction", True)
            btn_freeze.setProperty("actionVariant", "warning")
            btn_freeze.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_freeze.clicked.connect(
                lambda ch, m=member: self.open_freeze_dialog(m)
            )

            btn_cancel = QPushButton("Hủy gói")
            btn_cancel.setProperty("tableAction", True)
            btn_cancel.setProperty("actionVariant", "danger")
            btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_cancel.clicked.connect(
                lambda ch, m=member: self.open_cancel_dialog(m)
            )

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_freeze)
            action_layout.addWidget(btn_cancel)
            self.table.setCellWidget(row_index, 6, action_widget)

    def _on_cell_double_clicked(self, row: int, _col: int) -> None:
        if 0 <= row < len(self._displayed_members):
            self.open_detail_dialog(self._displayed_members[row])

    def filter_table(self) -> None:
        query = self.txt_search.text().strip().casefold()
        tag_status_map = {
            "ALL": None,
            "ACTIVE": "Đang hoạt động",
            "FROZEN": "Đang bảo lưu",
            "EXPIRED": "Hết hạn",
        }
        target_status = tag_status_map.get(self._filter_tag)

        filtered = [
            member
            for member in self._members
            if (
                target_status is None
                or member["status"] == target_status
            )
            and any(
                query in str(member[key]).casefold()
                for key in ("name", "code", "phone")
            )
        ]
        self.render_table(filtered)

    def open_register_dialog(self) -> None:
        dialog = RegisterMemberDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_members()

    def open_detail_dialog(self, member: Dict[str, Any]) -> None:
        MemberDetailDialog(member, self).exec()

    def open_edit_dialog(self, member: Dict[str, Any]) -> None:
        QMessageBox.information(
            self,
            "Sửa Thông Tin Hội Viên",
            f"Chỉnh sửa thông tin: {member['name']} ({member['code']})\n"
            f"Số điện thoại: {member['phone']}\n"
            "Chức năng chỉnh sửa thông tin hồ sơ đang được kết nối.",
        )

    def open_freeze_dialog(self, member: Dict[str, Any]) -> None:
        QMessageBox.information(
            self,
            "Bảo Lưu Gói Tập",
            f"Yêu cầu bảo lưu gói tập cho hội viên: {member['name']}\n"
            f"Gói hiện tại: {member['package_name']}\n"
            f"Hạn sử dụng hiện tại: {member['expiry_date']}\n"
            "Hệ thống sẽ cập nhật trạng thái khi được phê duyệt.",
        )

    def open_cancel_dialog(self, member: Dict[str, Any]) -> None:
        warn_msg = (
            f"CẢNH BÁO: Bạn có muốn hủy gói của hội viên {member['name']}?\n"
            f"Gói tập: {member['package_name']}\n"
            "Thao tác này sẽ chấm dứt quyền sử dụng phòng tập của hội viên."
        )
        reply = QMessageBox.warning(
            self,
            "Xác Nhận Hủy Gói Tập",
            warn_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self,
                "Hủy Gói Tập",
                f"Đã ghi nhận yêu cầu hủy gói của {member['name']}.",
            )
