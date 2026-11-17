"""
Invoice History Page: Lịch sử giao dịch & in lại hóa đơn (1:1 with Desktop/Views/InvoiceHistoryPage.xaml).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from styles.color_tokens import (
    TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, LAYER_BG, 
    BORDER_SUBTLE, ACCENT_PRIMARY, STATUS_SUCCESS
)
from mock_data import INVOICES

class InvoiceHistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        lbl_title = QLabel("LỊCH SỬ & IN HÓA ĐƠN GIAO DỊCH")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        
        lbl_desc = QLabel("Tra cứu lịch sử thu ngân, xuất biên lai và xử lý hoàn trả hóa đơn")
        lbl_desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_desc)
        header.addLayout(title_box)
        main_layout.addLayout(header)
        
        # Search & Filter
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Tìm kiếm theo Mã hóa đơn, Tên hội viên hoặc Thu ngân...")
        self.txt_search.textChanged.connect(self.filter_table)
        main_layout.addWidget(self.txt_search)
        
        # Invoices Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Mã Hóa Đơn", "Hội Viên", "Gói Dịch Vụ", "Số Tiền", "Phương Thức", "Thời Gian", "Thao Tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table)
        
        self.render_table(INVOICES)
        
    def render_table(self, inv_list):
        self.table.setRowCount(len(inv_list))
        for row, inv in enumerate(inv_list):
            self.table.setItem(row, 0, QTableWidgetItem(inv["code"]))
            self.table.setItem(row, 1, QTableWidgetItem(inv["member_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(inv["package_name"]))
            
            amt_item = QTableWidgetItem(f"{inv['amount']:,.0f} đ")
            amt_item.setForeground(Qt.GlobalColor.cyan)
            self.table.setItem(row, 3, amt_item)
            
            self.table.setItem(row, 4, QTableWidgetItem(inv["payment_method"]))
            self.table.setItem(row, 5, QTableWidgetItem(inv["date"]))
            
            btn_print = QPushButton("In Biên Lai")
            btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_print.setStyleSheet("font-size: 11px; padding: 4px 8px;")
            btn_print.clicked.connect(lambda ch, item=inv: QMessageBox.information(self, "In Biên Lai", f"Đang gửi lệnh in hóa đơn {item['code']} ra máy in nhiệt bill!"))
            self.table.setCellWidget(row, 6, btn_print)
            
    def filter_table(self):
        q = self.txt_search.text().lower()
        filtered = [inv for inv in INVOICES if q in inv["code"].lower() or q in inv["member_name"].lower()]
        self.render_table(filtered)
