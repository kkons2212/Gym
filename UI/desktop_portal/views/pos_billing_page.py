"""POS Billing and Live Package Plans Catalog matching Desktop/Views/PosBillingPage.xaml."""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from exceptions import DatabaseTransactionException
from models.package_plan import PackagePlan
from repositories.package_plan_repository import PackagePlanRepository
from desktop_portal.dialogs.register_member_dialog import RegisterMemberDialog
from styles.color_tokens import (
    ACCENT_PRIMARY,
    ACCENT_SUBTLE,
    BORDER_SUBTLE,
    CARD_BG,
    INPUT_BG,
    LAYER_BG,
    STATUS_PT,
    STATUS_SUCCESS,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_TERTIARY,
)


class PosBillingPage(QWidget):
    """
    Split-pane POS billing screen matching Desktop/Views/PosBillingPage.xaml.
    - Left column (60%): Live Package Plans Catalog
    - Right column (40%): POS Billing Invoice & Quick Checkout Cart
    """

    def __init__(
        self,
        parent=None,
        package_repo: Optional[PackagePlanRepository] = None,
    ) -> None:
        super().__init__(parent)
        self.package_repo = package_repo or PackagePlanRepository()
        self._plans: List[PackagePlan] = []
        self.selected_plan: Optional[PackagePlan] = None
        self._cards: List[QFrame] = []

        # Main 2-column layout (Split-pane: Left 60%, Right 40%)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # =========================================================================
        # 1. LEFT COLUMN: Package Plans Catalog (Width: 6*)
        # =========================================================================
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(14)

        # Header: Search & Title
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = QLabel("DANH MỤC GÓI TẬP NIÊM YẾT")
        title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;"
        )
        subtitle = QLabel("Bấm chọn gói tập để nạp vào hóa đơn thanh toán (F2)")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        left_layout.addLayout(title_box)

        # Filter Input
        self.txt_filter = QLineEdit()
        self.txt_filter.setFixedHeight(38)
        self.txt_filter.setPlaceholderText("Tìm gói tập theo tên hoặc mô tả...")
        self.txt_filter.setStyleSheet(f"""
            QLineEdit {{
                background-color: {INPUT_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                padding-left: 12px;
                color: {TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {ACCENT_PRIMARY};
            }}
        """)
        self.txt_filter.textChanged.connect(self.filter_packages)
        left_layout.addWidget(self.txt_filter)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        left_layout.addWidget(self.status_label)

        # Packages ListView / ScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.pkg_container = QWidget()
        self.pkg_container.setStyleSheet("background: transparent;")
        self.pkg_layout = QVBoxLayout(self.pkg_container)
        self.pkg_layout.setSpacing(12)
        self.pkg_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.pkg_container)
        left_layout.addWidget(scroll)

        main_layout.addWidget(left_container, 6)

        # =========================================================================
        # 2. RIGHT COLUMN: Cart & Billing Checkout (Width: 4*)
        # =========================================================================
        right_frame = QFrame()
        right_frame.setObjectName("posBillingCard")
        right_frame.setStyleSheet(f"""
            QFrame#posBillingCard {{
                background-color: {LAYER_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 16px;
            }}
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(16)

        # Section Title
        lbl_cart_title = QLabel("HÓA ĐƠN BÁN HÀNG POS")
        lbl_cart_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;"
        )
        right_layout.addWidget(lbl_cart_title)

        # Member Selection
        member_box = QVBoxLayout()
        member_box.setSpacing(6)
        lbl_member = QLabel("Hội viên thanh toán:")
        lbl_member.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: 600;"
        )
        member_box.addWidget(lbl_member)

        member_row = QHBoxLayout()
        member_row.setSpacing(8)
        self.cb_members = QComboBox()
        self.cb_members.setFixedHeight(36)
        self.cb_members.setStyleSheet(f"""
            QComboBox {{
                background-color: {INPUT_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                padding: 4px 10px;
                color: {TEXT_PRIMARY};
                font-size: 13px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                selection-background-color: {ACCENT_PRIMARY};
                selection-color: #FFFFFF;
                border: 1px solid {BORDER_SUBTLE};
            }}
        """)
        self._load_members()
        member_row.addWidget(self.cb_members, stretch=1)

        self.btn_new_member = QPushButton("+ Khách mới")
        self.btn_new_member.setFixedHeight(36)
        self.btn_new_member.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_member.setStyleSheet(f"""
            QPushButton {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                color: {ACCENT_PRIMARY};
                font-size: 12px;
                font-weight: bold;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_SUBTLE};
                border-color: {ACCENT_PRIMARY};
            }}
        """)
        self.btn_new_member.clicked.connect(
            lambda: self.open_registration(
                self.selected_plan.plan_id if self.selected_plan else None
            )
        )
        member_row.addWidget(self.btn_new_member)
        member_box.addLayout(member_row)

        # Transaction Type Selector
        type_row = QHBoxLayout()
        type_row.setSpacing(16)
        self.rb_purchase = QRadioButton("Mua mới")
        self.rb_purchase.setChecked(True)
        self.rb_purchase.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px;")
        self.rb_renew = QRadioButton("Gia hạn gói")
        self.rb_renew.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")

        self.tx_group = QButtonGroup(self)
        self.tx_group.addButton(self.rb_purchase)
        self.tx_group.addButton(self.rb_renew)
        type_row.addWidget(self.rb_purchase)
        type_row.addWidget(self.rb_renew)
        type_row.addStretch()
        member_box.addLayout(type_row)
        right_layout.addLayout(member_box)

        # Invoice Breakdown Line Items
        breakdown_box = QFrame()
        breakdown_box.setStyleSheet(f"""
            QFrame {{
                background-color: #0F172A;
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        breakdown_layout = QVBoxLayout(breakdown_box)
        breakdown_layout.setSpacing(8)

        lbl_item_header = QLabel("Chi tiết gói tập:")
        lbl_item_header.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;"
        )
        breakdown_layout.addWidget(lbl_item_header)

        self.lbl_selected_name = QLabel("Chưa chọn gói tập")
        self.lbl_selected_name.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: bold;"
        )
        breakdown_layout.addWidget(self.lbl_selected_name)

        self.lbl_selected_desc = QLabel(
            "Vui lòng bấm chọn một gói tập từ danh mục bên trái"
        )
        self.lbl_selected_desc.setWordWrap(True)
        self.lbl_selected_desc.setStyleSheet(
            f"color: {TEXT_TERTIARY}; font-size: 11px;"
        )
        breakdown_layout.addWidget(self.lbl_selected_desc)

        # Divider line
        div1 = QFrame()
        div1.setFixedHeight(1)
        div1.setStyleSheet(f"background-color: {BORDER_SUBTLE}; border: none;")
        breakdown_layout.addWidget(div1)

        # Duration row
        row_dur = QHBoxLayout()
        lbl_dur_title = QLabel("Thời hạn sử dụng:")
        lbl_dur_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.lbl_dur_val = QLabel("--")
        self.lbl_dur_val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px;")
        row_dur.addWidget(lbl_dur_title)
        row_dur.addStretch()
        row_dur.addWidget(self.lbl_dur_val)
        breakdown_layout.addLayout(row_dur)

        # Gym sessions row
        row_gym = QHBoxLayout()
        lbl_gym_title = QLabel("Số buổi Gym:")
        lbl_gym_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.lbl_gym_val = QLabel("--")
        self.lbl_gym_val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px;")
        row_gym.addWidget(lbl_gym_title)
        row_gym.addStretch()
        row_gym.addWidget(self.lbl_gym_val)
        breakdown_layout.addLayout(row_gym)

        # PT sessions row
        row_pt = QHBoxLayout()
        lbl_pt_title = QLabel("Buổi PT kèm:")
        lbl_pt_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.lbl_pt_val = QLabel("--")
        self.lbl_pt_val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px;")
        row_pt.addWidget(lbl_pt_title)
        row_pt.addStretch()
        row_pt.addWidget(self.lbl_pt_val)
        breakdown_layout.addLayout(row_pt)

        # Divider line
        div2 = QFrame()
        div2.setFixedHeight(1)
        div2.setStyleSheet(f"background-color: {BORDER_SUBTLE}; border: none;")
        breakdown_layout.addWidget(div2)

        # Subtotal row
        row_sub = QHBoxLayout()
        lbl_sub_title = QLabel("Tạm tính (Subtotal):")
        lbl_sub_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.lbl_sub_val = QLabel("0 đ")
        self.lbl_sub_val.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: 600;"
        )
        row_sub.addWidget(lbl_sub_title)
        row_sub.addStretch()
        row_sub.addWidget(self.lbl_sub_val)
        breakdown_layout.addLayout(row_sub)

        # Total row (Green prominent)
        row_total = QHBoxLayout()
        lbl_total_title = QLabel("TỔNG THANH TOÁN:")
        lbl_total_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold;"
        )
        self.lbl_total_val = QLabel("0 đ")
        self.lbl_total_val.setStyleSheet(
            f"color: {STATUS_SUCCESS}; font-size: 18px; font-weight: bold;"
        )
        row_total.addWidget(lbl_total_title)
        row_total.addStretch()
        row_total.addWidget(self.lbl_total_val)
        breakdown_layout.addLayout(row_total)

        right_layout.addWidget(breakdown_box)

        # Payment Methods
        pay_box = QVBoxLayout()
        pay_box.setSpacing(8)
        lbl_pay = QLabel("Phương thức thanh toán:")
        lbl_pay.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: 600;"
        )
        pay_box.addWidget(lbl_pay)

        pay_row = QHBoxLayout()
        pay_row.setSpacing(8)

        self.btn_cash = QPushButton("💵 Tiền Mặt")
        self.btn_cash.setCheckable(True)
        self.btn_cash.setChecked(True)
        self.btn_cash.setFixedHeight(38)
        self.btn_cash.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cash.setStyleSheet(f"""
            QPushButton {{
                background-color: {INPUT_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                color: {TEXT_PRIMARY};
                font-weight: 600;
            }}
            QPushButton:checked {{
                background-color: {CARD_BG};
                border-color: {ACCENT_PRIMARY};
                color: #FFFFFF;
            }}
        """)

        self.btn_vietqr = QPushButton("📱 VietQR")
        self.btn_vietqr.setCheckable(True)
        self.btn_vietqr.setFixedHeight(38)
        self.btn_vietqr.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_vietqr.setStyleSheet(f"""
            QPushButton {{
                background-color: {INPUT_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
                color: {TEXT_PRIMARY};
                font-weight: 600;
            }}
            QPushButton:checked {{
                background-color: {ACCENT_PRIMARY};
                border-color: {ACCENT_PRIMARY};
                color: #FFFFFF;
            }}
        """)

        self.pay_group = QButtonGroup(self)
        self.pay_group.addButton(self.btn_cash)
        self.pay_group.addButton(self.btn_vietqr)
        pay_row.addWidget(self.btn_cash)
        pay_row.addWidget(self.btn_vietqr)
        pay_box.addLayout(pay_row)
        right_layout.addLayout(pay_box)

        right_layout.addStretch()

        # Checkout Action Button
        self.btn_checkout = QPushButton("Thanh Toán và Xuất Hóa Đơn (Enter)")
        self.btn_checkout.setFixedHeight(46)
        self.btn_checkout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_checkout.setStyleSheet(f"""
            QPushButton {{
                background-color: #16A34A;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #15803D;
            }}
            QPushButton:pressed {{
                background-color: #166534;
            }}
        """)
        self.btn_checkout.clicked.connect(self._process_checkout)
        right_layout.addWidget(self.btn_checkout)

        main_layout.addWidget(right_frame, 4)

        # Initial Load
        self._load_packages()

    def _load_members(self) -> None:
        """Load registered members into the combobox safely."""
        self.cb_members.clear()
        self.cb_members.addItem("-- Khách vãng lai / Đăng ký mới --", None)
        try:
            from repositories.user_repository import UserRepository
            user_repo = UserRepository()
            members = user_repo.get_all_members()
            for m in members:
                display = f"{m.full_name} • {m.phone or m.username}"
                self.cb_members.addItem(display, m.username)
        except Exception:
            # Fallback if DB is disconnected in mock or unit test environments
            pass

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
        self._cards.clear()

    def filter_packages(self, text: str) -> None:
        query = text.strip().casefold()
        plans = [
            plan
            for plan in self._plans
            if query in plan.name.casefold()
            or query in (plan.description or "").casefold()
        ]
        self.render_packages(plans)

    def select_plan(self, plan: PackagePlan) -> None:
        """Update selected package in the right-hand checkout panel."""
        self.selected_plan = plan
        session_limit = (
            f"{plan.max_check_in_sessions} buổi"
            if plan.max_check_in_sessions
            else "Không giới hạn"
        )
        pt_limit = (
            f"{plan.total_pt_sessions} buổi"
            if plan.total_pt_sessions
            else "Không kèm PT"
        )

        self.lbl_selected_name.setText(plan.name)
        self.lbl_selected_desc.setText(plan.description or "Gói tập niêm yết")
        self.lbl_dur_val.setText(f"{plan.duration_days} ngày")
        self.lbl_gym_val.setText(session_limit)
        self.lbl_pt_val.setText(pt_limit)
        self.lbl_sub_val.setText(f"{plan.price:,.0f} đ")
        self.lbl_total_val.setText(f"{plan.price:,.0f} đ")

        # Visual indicator update on cards
        for card in self._cards:
            is_this_card = getattr(card, "_plan_id", None) == plan.plan_id
            border_color = ACCENT_PRIMARY if is_this_card else BORDER_SUBTLE
            bg_color = ACCENT_SUBTLE if is_this_card else CARD_BG
            card.setStyleSheet(f"""
                QFrame#packageCard {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 12px;
                }}
                QFrame#packageCard:hover {{
                    border-color: {ACCENT_PRIMARY};
                }}
            """)

    def render_packages(self, plans: List[PackagePlan]) -> None:
        self._clear_cards()
        for plan in plans:
            session_limit = (
                f"{plan.max_check_in_sessions} buổi Gym"
                if plan.max_check_in_sessions
                else "Gym không giới hạn"
            )
            card = QFrame()
            card.setObjectName("packageCard")
            card._plan_id = plan.plan_id
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.setStyleSheet(f"""
                QFrame#packageCard {{
                    background-color: {CARD_BG};
                    border: 1px solid {BORDER_SUBTLE};
                    border-radius: 12px;
                }}
                QFrame#packageCard:hover {{
                    border-color: {ACCENT_PRIMARY};
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 14)
            card_layout.setSpacing(8)

            # Top Row: Name & Price
            title_row = QHBoxLayout()
            name = QLabel(plan.name)
            name.setStyleSheet(
                f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: bold;"
            )
            price = QLabel(f"{plan.price:,.0f} đ")
            price.setStyleSheet(
                f"color: {STATUS_SUCCESS}; font-size: 16px; font-weight: bold;"
            )
            title_row.addWidget(name)
            title_row.addStretch()
            title_row.addWidget(price)
            card_layout.addLayout(title_row)

            # Benefit Details
            detail = QLabel(plan.description or "Gói tập niêm yết phòng gym")
            detail.setWordWrap(True)
            detail.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
            card_layout.addWidget(detail)

            # Chips Row
            chips_row = QHBoxLayout()
            chips_row.setSpacing(6)

            dur_chip = QLabel(f"⏱ {plan.duration_days} ngày")
            dur_chip.setStyleSheet(f"""
                color: {ACCENT_PRIMARY};
                background-color: #0F172A;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
                padding: 3px 8px;
            """)
            chips_row.addWidget(dur_chip)

            sess_chip = QLabel(f"⚡ {session_limit}")
            sess_chip.setStyleSheet(f"""
                color: {STATUS_SUCCESS};
                background-color: #0F172A;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
                padding: 3px 8px;
            """)
            chips_row.addWidget(sess_chip)

            if getattr(plan, "total_pt_sessions", None):
                pt_chip = QLabel(f"🏋️ {plan.total_pt_sessions} buổi PT")
                pt_chip.setStyleSheet(f"""
                    color: {STATUS_PT};
                    background-color: #0F172A;
                    font-size: 11px;
                    font-weight: bold;
                    border-radius: 4px;
                    padding: 3px 8px;
                """)
                chips_row.addWidget(pt_chip)

            chips_row.addStretch()

            btn_select = QPushButton("Chọn nạp hóa đơn ➔")
            btn_select.setFixedHeight(30)
            btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_select.setStyleSheet(f"""
                QPushButton {{
                    background-color: {INPUT_BG};
                    border: 1px solid {BORDER_SUBTLE};
                    border-radius: 6px;
                    color: {ACCENT_PRIMARY};
                    font-size: 11px;
                    font-weight: bold;
                    padding: 0 10px;
                }}
                QPushButton:hover {{
                    background-color: {ACCENT_PRIMARY};
                    color: #FFFFFF;
                }}
            """)
            btn_select.clicked.connect(lambda _, p=plan: self.select_plan(p))
            chips_row.addWidget(btn_select)

            card_layout.addLayout(chips_row)

            # Clicking card also selects it
            card.mousePressEvent = lambda e, p=plan: self.select_plan(p)

            self.pkg_layout.addWidget(card)
            self._cards.append(card)

        if not plans:
            empty = QLabel("Không có gói tập nào khớp với tìm kiếm.")
            empty.setStyleSheet(f"color: {TEXT_SECONDARY};")
            self.pkg_layout.addWidget(empty)
        self.pkg_layout.addStretch()

        # Auto-select the first plan if none selected
        if plans and (self.selected_plan is None or self.selected_plan not in plans):
            self.select_plan(plans[0])

    def _process_checkout(self) -> None:
        """Route checkout to member registration or confirmation."""
        if not self.selected_plan:
            self.status_label.setText("Vui lòng chọn một gói tập trước khi thanh toán.")
            self.status_label.show()
            return
        self.open_registration(self.selected_plan.plan_id)

    def open_registration(self, plan_id: Optional[str] = None) -> None:
        target_id = plan_id or (self.selected_plan.plan_id if self.selected_plan else None)
        dialog = RegisterMemberDialog(self, preferred_plan_id=target_id)
        if dialog.exec():
            self._load_packages()
            self._load_members()
