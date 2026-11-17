"""Live package catalog; registrations use the member registration flow."""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from exceptions import DatabaseTransactionException
from models.package_plan import PackagePlan
from repositories.package_plan_repository import PackagePlanRepository
from desktop_portal.dialogs.register_member_dialog import RegisterMemberDialog
from styles.color_tokens import ACCENT_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY


class PosBillingPage(QWidget):
    """Display active packages and route purchases to member registration."""

    def __init__(
        self,
        parent=None,
        package_repo: Optional[PackagePlanRepository] = None,
    ) -> None:
        super().__init__(parent)
        self.package_repo = package_repo or PackagePlanRepository()
        self._plans: List[PackagePlan] = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(14)

        title = QLabel("DANH MỤC GÓI TẬP")
        title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;"
        )
        description = QLabel(
            "Chọn gói để đăng ký hội viên; không hỗ trợ thanh toán POS."
        )
        description.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText(
            "Tìm gói tập theo tên hoặc mô tả..."
        )
        self.txt_filter.textChanged.connect(self.filter_packages)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.hide()

        main_layout.addWidget(title)
        main_layout.addWidget(description)
        main_layout.addWidget(self.txt_filter)
        main_layout.addWidget(self.status_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.pkg_container = QWidget()
        self.pkg_layout = QVBoxLayout(self.pkg_container)
        self.pkg_layout.setSpacing(12)
        self.pkg_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.pkg_container)
        main_layout.addWidget(scroll)
        self._load_packages()

    def _load_packages(self) -> None:
        try:
            self._plans = self.package_repo.get_active_plans()
        except DatabaseTransactionException as err:
            self.status_label.setText(str(err))
            self.status_label.show()
            return
        self.status_label.clear()
        self.status_label.hide()
        self.filter_packages(self.txt_filter.text())

    def _clear_cards(self) -> None:
        while self.pkg_layout.count():
            item = self.pkg_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def filter_packages(self, text: str) -> None:
        query = text.strip().casefold()
        plans = [
            plan
            for plan in self._plans
            if query in plan.name.casefold()
            or query in (plan.description or "").casefold()
        ]
        self.render_packages(plans)

    def render_packages(self, plans: List[PackagePlan]) -> None:
        self._clear_cards()
        for plan in plans:
            session_limit = (
                plan.max_check_in_sessions
                if plan.max_check_in_sessions
                else "Không giới hạn"
            )
            card = QFrame()
            card.setObjectName("cardFrame")
            card_layout = QVBoxLayout(card)

            title_row = QHBoxLayout()
            name = QLabel(plan.name)
            name.setStyleSheet(
                f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: bold;"
            )
            price = QLabel(f"{plan.price:,.0f} đ")
            price.setStyleSheet(
                f"color: {ACCENT_PRIMARY}; font-size: 16px; font-weight: bold;"
            )
            title_row.addWidget(name)
            title_row.addStretch()
            title_row.addWidget(price)
            card_layout.addLayout(title_row)

            detail = QLabel(
                f"{plan.description or 'Gói tập niêm yết'}\n"
                f"Thời hạn: {plan.duration_days} ngày  •  "
                f"Lượt check-in: {session_limit}"
            )
            detail.setWordWrap(True)
            detail.setStyleSheet(f"color: {TEXT_SECONDARY};")
            card_layout.addWidget(detail)

            register_button = QPushButton("Đăng ký hội viên với gói này")
            register_button.setProperty("primary", True)
            register_button.clicked.connect(
                lambda: self.open_registration(plan.plan_id)
            )
            card_layout.addWidget(register_button)
            self.pkg_layout.addWidget(card)

        if not plans:
            empty = QLabel("Không có gói tập nào khớp với tìm kiếm.")
            empty.setStyleSheet(f"color: {TEXT_SECONDARY};")
            self.pkg_layout.addWidget(empty)
        self.pkg_layout.addStretch()

    def open_registration(self, plan_id: str) -> None:
        dialog = RegisterMemberDialog(self, preferred_plan_id=plan_id)
        if dialog.exec():
            self._load_packages()
