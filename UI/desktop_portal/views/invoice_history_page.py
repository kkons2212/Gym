"""Invoice History Page: Lịch sử giao dịch & in lại hóa đơn.

Matches 1:1 with Desktop/Views/InvoiceHistoryPage.xaml.
"""

from typing import Any, Dict, List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
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

from mock_data import INVOICES
from styles.color_tokens import (
    ACCENT_PRIMARY,
    STATUS_DANGER,
    STATUS_SUCCESS,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class InvoiceHistoryPage(QWidget):
    """Invoice history lookup, receipt reprint, and status filtering page."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        lbl_title = QLabel("LỊCH SỬ HÓA ĐƠN & IN PHIẾU THU")
        lbl_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;"
        )

        lbl_desc = QLabel(
            "Tra cứu lịch sử giao dịch, in lại phiếu thu nhiệt K80 "
            "và xử lý yêu cầu hoàn tiền"
        )
        lbl_desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")

        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_desc)
        header.addLayout(title_box)
        main_layout.addLayout(header)

        # Filter & Search Toolbar (1:1 with InvoiceHistoryPage.xaml)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(40)
        self.txt_search.setFixedWidth(360)
        self.txt_search.setPlaceholderText(
            "Tìm theo mã hóa đơn hoặc tên hội viên…"
        )
        self.txt_search.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.txt_search)

        # Status Segmented Filter Buttons
        self._filter_tag = "ALL"
        self._filter_buttons: Dict[str, QPushButton] = {}
        filters_box = QHBoxLayout()
        filters_box.setSpacing(8)

        filter_configs = [
            ("ALL", "Tất cả", TEXT_PRIMARY),
            ("PAID", "Đã thanh toán", STATUS_SUCCESS),
            ("REFUNDED", "Đã hoàn tiền", STATUS_DANGER),
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

        toolbar.addLayout(filters_box)
        toolbar.addStretch()

        btn_refresh = QPushButton("Làm mới")
        btn_refresh.setFixedHeight(40)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(lambda: self.render_table(INVOICES))
        toolbar.addWidget(btn_refresh)

        main_layout.addLayout(toolbar)

        # Invoices Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "MÃ HÓA ĐƠN",
            "THỜI GIAN",
            "HỘI VIÊN",
            "GÓI DỊCH VỤ",
            "SỐ TIỀN",
            "PHƯƠNG THỨC",
            "TRẠNG THÁI",
            "THAO TÁC",
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            7, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(7, 190)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        main_layout.addWidget(self.table)

        self.render_table(INVOICES)

    def _set_filter(self, tag: str) -> None:
        self._filter_tag = tag
        for btn_tag, btn in self._filter_buttons.items():
            is_active = (btn_tag == tag)
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.filter_table()

    def render_table(self, inv_list: List[Dict[str, Any]]) -> None:
        self.table.setRowCount(len(inv_list))
        for row, inv in enumerate(inv_list):
            code_item = QTableWidgetItem(inv["code"])
            code_item.setForeground(QColor(ACCENT_PRIMARY))
            self.table.setItem(row, 0, code_item)

            self.table.setItem(row, 1, QTableWidgetItem(inv["date"]))
            self.table.setItem(row, 2, QTableWidgetItem(inv["member_name"]))
            self.table.setItem(row, 3, QTableWidgetItem(inv["package_name"]))

            amt_item = QTableWidgetItem(f"{inv['amount']:,.0f} đ")
            amt_item.setForeground(QColor(STATUS_SUCCESS))
            self.table.setItem(row, 4, amt_item)

            self.table.setItem(row, 5, QTableWidgetItem(inv["payment_method"]))

            status_text = inv.get("status", "Đã thanh toán")
            is_paid = status_text in ("Đã thanh toán", "PAID")
            st_item = QTableWidgetItem(
                "Đã thanh toán" if is_paid else "Đã hoàn tiền"
            )
            st_item.setForeground(
                QColor(STATUS_SUCCESS if is_paid else STATUS_DANGER)
            )
            self.table.setItem(row, 6, st_item)

            btn_print = QPushButton("In K80")
            btn_print.setProperty("tableAction", True)
            btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_print.clicked.connect(
                lambda ch, item=inv: QMessageBox.information(
                    self,
                    "In Hóa Đơn K80",
                    f"Đang gửi lệnh in hóa đơn {item['code']} ra máy in K80!",
                )
            )

            btn_refund = QPushButton("Hoàn Tiền")
            btn_refund.setProperty("tableAction", True)
            btn_refund.setProperty("actionVariant", "warning")
            btn_refund.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_refund.setEnabled(is_paid)
            btn_refund.clicked.connect(
                lambda ch, item=inv: self.open_refund_dialog(item)
            )

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            action_layout.addWidget(btn_print)
            action_layout.addWidget(btn_refund)
            self.table.setCellWidget(row, 7, action_widget)

    def open_refund_dialog(self, invoice: Dict[str, Any]) -> None:
        reply = QMessageBox.question(
            self,
            "Xử Lý Hoàn Tiền Hóa Đơn",
            f"Bạn có muốn lập phiếu hoàn tiền cho hóa đơn {invoice['code']}?\n"
            f"Hội viên: {invoice['member_name']}\n"
            f"Gói dịch vụ: {invoice['package_name']}\n"
            f"Số tiền hoàn: {invoice['amount']:,.0f} đ\n\n"
            "Thao tác này sẽ chuyển trạng thái hóa đơn sang 'Đã hoàn tiền' "
            "và thu hồi quyền lợi gói tập tương ứng.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            invoice["status"] = "Đã hoàn tiền"
            self.filter_table()
            QMessageBox.information(
                self,
                "Hoàn Tiền Thành Công",
                f"Đã xử lý hoàn tiền cho hóa đơn {invoice['code']}!",
            )

    def filter_table(self) -> None:
        q = self.txt_search.text().lower()
        filtered = []
        for inv in INVOICES:
            status_text = inv.get("status", "Đã thanh toán")
            is_paid = status_text in ("Đã thanh toán", "PAID")

            if self._filter_tag == "PAID" and not is_paid:
                continue
            if self._filter_tag == "REFUNDED" and is_paid:
                continue

            matches_query = (
                q in inv["code"].lower()
                or q in inv["member_name"].lower()
                or q in inv.get("package_name", "").lower()
            )
            if matches_query:
                filtered.append(inv)

        self.render_table(filtered)
