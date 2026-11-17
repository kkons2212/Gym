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
        title = QLabel("QUẢN LÝ HỘI VIÊN & GÓI TẬP")
        title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;"
        )
        description = QLabel("Tra cứu hồ sơ và trạng thái gói tập")
        description.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        title_box.addWidget(title)
        title_box.addWidget(description)
        header.addLayout(title_box)
        header.addStretch()

        add_button = QPushButton("  + Đăng ký hội viên mới  ")
        add_button.setFixedHeight(40)
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.setProperty("primary", True)
        add_button.clicked.connect(self.open_register_dialog)
        header.addWidget(add_button)
        main_layout.addLayout(header)

        filter_row = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText(
            "Tìm theo họ tên, mã hội viên hoặc số điện thoại..."
        )
        self.txt_search.textChanged.connect(self.filter_table)
        filter_row.addWidget(self.txt_search, 7)

        self.cbo_status = QComboBox()
        self.cbo_status.addItems(
            [
                "Tất cả trạng thái",
                "Đang hoạt động",
                "Hết hạn",
                "Hết lượt",
                "Đang bảo lưu",
                "Đã hủy",
                "Chưa đăng ký",
                "Tạm khóa",
            ]
        )
        self.cbo_status.currentIndexChanged.connect(self.filter_table)
        filter_row.addWidget(self.cbo_status, 3)
        main_layout.addLayout(filter_row)

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
            6, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table)
        self._load_members()

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

            view_button = QPushButton("Xem chi tiết")
            view_button.clicked.connect(
                lambda: self.open_detail_dialog(member)
            )
            self.table.setCellWidget(row_index, 6, view_button)

    def filter_table(self) -> None:
        query = self.txt_search.text().strip().casefold()
        status_filter = self.cbo_status.currentText()
        filtered = [
            member
            for member in self._members
            if (
                status_filter == "Tất cả trạng thái"
                or member["status"] == status_filter
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
