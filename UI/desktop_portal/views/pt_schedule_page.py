"""
PT Schedule Page: Điều phối lịch huấn luyện viên (1:1 with Desktop/Views/PtSchedulePage.xaml).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from styles.color_tokens import (
    TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, LAYER_BG, 
    BORDER_SUBTLE, ACCENT_PRIMARY, STATUS_SUCCESS
)
from mock_data import TRAINERS, SCHEDULE_SLOTS, MEMBERS

class PtSchedulePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # LEFT COLUMN (35%): Trainer Info & Filter Card
        left_col = QVBoxLayout()
        left_col.setSpacing(16)
        
        filter_card = QFrame()
        filter_card.setObjectName("cardFrame")
        f_layout = QVBoxLayout(filter_card)
        f_layout.setContentsMargins(20, 20, 20, 20)
        f_layout.setSpacing(14)
        
        lbl_title = QLabel("ĐIỀU PHỐI LỊCH HUẤN LUYỆN VIÊN")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        f_layout.addWidget(lbl_title)
        
        f_layout.addWidget(QLabel("Chọn Huấn Luyện Viên:"))
        self.cbo_pt = QComboBox()
        for pt in TRAINERS:
            self.cbo_pt.addItem(f"{pt['name']} - {pt['specialty'][:25]}...", pt)
        self.cbo_pt.currentIndexChanged.connect(self.update_schedule)
        f_layout.addWidget(self.cbo_pt)
        
        # PT Profile snippet
        self.pt_snippet = QFrame()
        self.pt_snippet.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 12px;")
        snip_layout = QVBoxLayout(self.pt_snippet)
        snip_layout.setSpacing(6)
        
        self.lbl_snip_name = QLabel("HLV: Nguyễn Văn Hưng")
        self.lbl_snip_name.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold; font-size: 13px;")
        
        self.lbl_snip_rating = QLabel("Đánh giá: 4.9 ⭐ • Học viên kèm: 14")
        self.lbl_snip_rating.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 11px;")
        
        self.lbl_snip_exp = QLabel("6 năm kinh nghiệm, Chứng chỉ Quốc tế NASM CPT")
        self.lbl_snip_exp.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        self.lbl_snip_exp.setWordWrap(True)
        
        snip_layout.addWidget(self.lbl_snip_name)
        snip_layout.addWidget(self.lbl_snip_rating)
        snip_layout.addWidget(self.lbl_snip_exp)
        f_layout.addWidget(self.pt_snippet)
        
        f_layout.addStretch()
        
        btn_assign = QPushButton("+ Xếp Lịch Kèm Mới")
        btn_assign.setFixedHeight(40)
        btn_assign.setProperty("primary", True)
        btn_assign.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_assign.clicked.connect(lambda: QMessageBox.information(self, "Xếp Lịch PT", "Chức năng xếp ca hẹn mới cho hội viên & HLV!"))
        f_layout.addWidget(btn_assign)
        
        left_col.addWidget(filter_card)
        main_layout.addLayout(left_col, 4)
        
        # RIGHT COLUMN (65%): Weekly Timetable Table
        right_col = QVBoxLayout()
        right_col.setSpacing(14)
        
        lbl_table_title = QLabel("LỊCH TRÌNH BUỔI HẸN TRONG TUẦN")
        lbl_table_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        right_col.addWidget(lbl_table_title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Khung Giờ", "Hội Viên Kèm", "Trạng Thái Ca", "Thao Tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        right_col.addWidget(self.table)
        
        main_layout.addLayout(right_col, 6)
        self.update_schedule()
        
    def update_schedule(self):
        pt_data = self.cbo_pt.currentData()
        if not pt_data:
            return
            
        self.lbl_snip_name.setText(f"HLV: {pt_data['name']}")
        self.lbl_snip_rating.setText(f"Đánh giá: {pt_data['rating']} ⭐ • Học viên kèm: {pt_data['active_students']}")
        self.lbl_snip_exp.setText(pt_data["experience"])
        
        filtered_slots = [s for s in SCHEDULE_SLOTS if s["pt"] == pt_data["name"]]
        self.table.setRowCount(len(filtered_slots))
        for row, slot in enumerate(filtered_slots):
            self.table.setItem(row, 0, QTableWidgetItem(slot["time"]))
            self.table.setItem(row, 1, QTableWidgetItem(slot["member"] or "(Trống - Sẵn sàng nhận học viên)"))
            
            st_item = QTableWidgetItem(slot["status"])
            if slot["status"] == "Đã xác nhận":
                st_item.setForeground(Qt.GlobalColor.green)
            else:
                st_item.setForeground(Qt.GlobalColor.cyan)
            self.table.setItem(row, 2, st_item)
            
            btn_action = QPushButton("Chi Tiết")
            btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_action.setStyleSheet("font-size: 11px; padding: 4px 8px;")
            btn_action.clicked.connect(lambda ch, s=slot: QMessageBox.information(self, "Buổi Tập", f"Khung giờ: {s['time']}\nHọc viên: {s['member'] or 'Chưa có'}\nTrạng thái: {s['status']}"))
            self.table.setCellWidget(row, 3, btn_action)
