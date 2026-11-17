"""
Members Page: Quản lý hội viên & gói tập (1:1 with Desktop/Views/MembersPage.xaml).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from styles.color_tokens import (
    TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, LAYER_BG, 
    BORDER_SUBTLE, ACCENT_PRIMARY, STATUS_SUCCESS, STATUS_DANGER
)
from mock_data import MEMBERS
from desktop_portal.dialogs.register_member_dialog import RegisterMemberDialog
from desktop_portal.dialogs.member_detail_dialog import MemberDetailDialog

class MembersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        lbl_title = QLabel("QUẢN LÝ HỘI VIÊN & GÓI TẬP")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        
        lbl_desc = QLabel("Tra cứu thông tin, gia hạn và bảo lưu gói tập (F3)")
        lbl_desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_desc)
        header.addLayout(title_box)
        header.addStretch()
        
        btn_add = QPushButton("  + Đăng Ký Hội Viên Mới  ")
        btn_add.setFixedHeight(40)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setProperty("primary", True)
        btn_add.clicked.connect(self.open_register_dialog)
        header.addWidget(btn_add)
        main_layout.addLayout(header)
        
        # Filter Bar
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Tìm kiếm theo Họ tên, Mã HV hoặc Số điện thoại...")
        self.txt_search.textChanged.connect(self.filter_table)
        filter_row.addWidget(self.txt_search, 7)
        
        self.cbo_status = QComboBox()
        self.cbo_status.addItems(["Tất cả trạng thái", "Đang hoạt động", "Hết hạn", "Đang bảo lưu"])
        self.cbo_status.currentIndexChanged.connect(self.filter_table)
        filter_row.addWidget(self.cbo_status, 3)
        
        main_layout.addLayout(filter_row)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Mã HV", "Họ Tên", "Số Điện Thoại", "Gói Tập Hiện Tại", "Hạn Sử Dụng", "Trạng Thái", "Thao Tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table)
        
        self.render_table(MEMBERS)
        
    def render_table(self, member_list):
        self.table.setRowCount(len(member_list))
        for row, m in enumerate(member_list):
            self.table.setItem(row, 0, QTableWidgetItem(m["code"]))
            self.table.setItem(row, 1, QTableWidgetItem(m["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(m["phone"]))
            self.table.setItem(row, 3, QTableWidgetItem(m["package_name"]))
            self.table.setItem(row, 4, QTableWidgetItem(m["expiry_date"]))
            
            st_item = QTableWidgetItem(m["status"])
            if m["status"] == "Đang hoạt động":
                st_item.setForeground(Qt.GlobalColor.green)
            else:
                st_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 5, st_item)
            
            # Action button
            btn_view = QPushButton("Xem Chi Tiết")
            btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_view.setStyleSheet("font-size: 11px; padding: 4px 8px;")
            btn_view.clicked.connect(lambda ch, mem=m: self.open_detail_dialog(mem))
            self.table.setCellWidget(row, 6, btn_view)
            
    def filter_table(self):
        query = self.txt_search.text().lower()
        st_filter = self.cbo_status.currentText()
        
        filtered = []
        for m in MEMBERS:
            matches_q = (query in m["name"].lower() or query in m["code"].lower() or query in m["phone"])
            matches_st = (st_filter == "Tất cả trạng thái" or m["status"] == st_filter)
            if matches_q and matches_st:
                filtered.append(m)
        self.render_table(filtered)
        
    def open_register_dialog(self):
        dlg = RegisterMemberDialog(self)
        if dlg.exec():
            self.filter_table()
            
    def open_detail_dialog(self, member):
        dlg = MemberDetailDialog(member, self)
        dlg.exec()
