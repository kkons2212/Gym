"""
Package Plans Page: Quản lý danh mục gói dịch vụ (1:1 with Desktop/Views/PackagePlansPage.xaml).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt
from styles.color_tokens import (
    TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, LAYER_BG, 
    BORDER_SUBTLE, ACCENT_PRIMARY, STATUS_SUCCESS
)
from mock_data import PACKAGES

class PackagePlansPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        lbl_title = QLabel("DANH MỤC GÓI TẬP & DỊCH VỤ")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        
        lbl_desc = QLabel("Cấu hình chính sách giá, thời hạn sử dụng và quyền lợi đi kèm gói tập")
        lbl_desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_desc)
        header.addLayout(title_box)
        header.addStretch()
        
        btn_add = QPushButton("  + Thêm Gói Dịch Vụ Mới  ")
        btn_add.setFixedHeight(40)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setProperty("primary", True)
        btn_add.clicked.connect(lambda: QMessageBox.information(self, "Thêm Gói Mới", "Mở hộp thoại tạo gói tập và dịch vụ mới!"))
        header.addWidget(btn_add)
        main_layout.addLayout(header)
        
        # Grid of Packages
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(16)
        
        for idx, pkg in enumerate(PACKAGES):
            card = QFrame()
            card.setObjectName("cardFrame")
            card.setStyleSheet(f"""
                QFrame#cardFrame {{
                    background-color: {CARD_BG};
                    border: 1px solid {BORDER_SUBTLE};
                    border-radius: 12px;
                    padding: 16px;
                }}
            """)
            c_layout = QVBoxLayout(card)
            c_layout.setSpacing(10)
            
            top_row = QHBoxLayout()
            lbl_name = QLabel(pkg["name"])
            lbl_name.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
            
            lbl_badge = QLabel(pkg["badge"])
            lbl_badge.setStyleSheet("color: #38BDF8; background-color: rgba(14, 165, 233, 0.15); border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: bold;")
            
            top_row.addWidget(lbl_name)
            top_row.addStretch()
            top_row.addWidget(lbl_badge)
            c_layout.addLayout(top_row)
            
            lbl_price = QLabel(f"{pkg['price']:,.0f} VNĐ")
            lbl_price.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 20px; font-weight: bold;")
            c_layout.addWidget(lbl_price)
            
            lbl_dur = QLabel(f"⏱ Thời hạn: {pkg['duration_days']} ngày | Buổi PT: {pkg['pt_sessions']} buổi")
            lbl_dur.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
            c_layout.addWidget(lbl_dur)
            
            lbl_desc = QLabel(pkg["benefits"])
            lbl_desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
            lbl_desc.setWordWrap(True)
            c_layout.addWidget(lbl_desc)
            
            c_layout.addStretch()
            
            btn_row = QHBoxLayout()
            btn_edit = QPushButton("Chỉnh Sửa")
            btn_edit.clicked.connect(lambda ch, p=pkg: QMessageBox.information(self, "Chỉnh Sửa", f"Chỉnh sửa thông tin gói: {p['name']}"))
            btn_row.addWidget(btn_edit)
            
            c_layout.addLayout(btn_row)
            
            row = idx // 2
            col = idx % 2
            grid.addWidget(card, row, col)
            
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
