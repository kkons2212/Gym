"""
Trainer (PT) Portal Window: Cổng dịch vụ huấn luyện viên cá nhân (1:1 with Web/Components/Pages/PT/*.razor).
Features:
- Weekly Schedule & Session Dispatching (PtWeeklySchedule.razor)
- Availability Grid & Shift Registration (PtAvailabilityGrid.razor)
- Student Management & Progress (PtStudentsList.razor)
- Trainer Profile & Rating Summary (PtProfileSummaryWidget.razor)
- InBody Measurement Entry Modal (InBodyEntryModal.razor)
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QDialog, QLineEdit, QDoubleSpinBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from styles.color_tokens import (
    TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, LAYER_BG, 
    BORDER_SUBTLE, ACCENT_PRIMARY, STATUS_SUCCESS
)
from mock_data import TRAINERS, SCHEDULE_SLOTS, MEMBERS

class InBodyEntryDialog(QDialog):
    def __init__(self, student_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Nhập Chỉ Số InBody • Học Viên: {student_name}")
        self.setFixedSize(420, 380)
        self.setStyleSheet("background-color: #162032; border: 1px solid #334155; border-radius: 12px;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        lbl_title = QLabel("NHẬP KẾT QUẢ ĐO INBODY")
        lbl_title.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        layout.addWidget(QLabel("Cân nặng (kg):"))
        self.spn_weight = QDoubleSpinBox()
        self.spn_weight.setRange(30, 200)
        self.spn_weight.setValue(72.5)
        layout.addWidget(self.spn_weight)
        
        layout.addWidget(QLabel("Tỷ lệ mỡ Body Fat (%):"))
        self.spn_fat = QDoubleSpinBox()
        self.spn_fat.setRange(3, 60)
        self.spn_fat.setValue(16.5)
        layout.addWidget(self.spn_fat)
        
        layout.addWidget(QLabel("Khối lượng cơ Skeletal Muscle (kg):"))
        self.spn_muscle = QDoubleSpinBox()
        self.spn_muscle.setRange(10, 100)
        self.spn_muscle.setValue(35.2)
        layout.addWidget(self.spn_muscle)
        
        layout.addStretch()
        
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("✓ Lưu Chỉ Số InBody")
        btn_save.setProperty("primary", True)
        btn_save.clicked.connect(self.save_data)
        
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)
        
    def save_data(self):
        QMessageBox.information(self, "Thành Công", "Đã cập nhật chỉ số InBody mới cho học viên!")
        self.accept()

class PtPortalWindow(QMainWindow):
    switch_portal_requested = pyqtSignal()
    
    def __init__(self, current_pt=None, parent=None):
        super().__init__(parent)
        self.pt = current_pt or TRAINERS[0]
        self.setWindowTitle(f"Cổng Huấn Luyện Viên (PT) • Gym Trainer Portal ({self.pt['name']})")
        self.resize(1180, 780)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # 1. Navbar
        nav = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        
        lbl_brand = QLabel("GYM TRAINER PORTAL")
        lbl_brand.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        lbl_name = QLabel(f"Huấn Luyện Viên: {self.pt['name']} ⭐ {self.pt['rating']}")
        lbl_name.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;")
        
        title_box.addWidget(lbl_brand)
        title_box.addWidget(lbl_name)
        nav.addLayout(title_box)
        nav.addStretch()
        
        btn_logout = QPushButton("🚪 Đăng Xuất")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self.switch_portal_requested.emit)
        nav.addWidget(btn_logout)
        main_layout.addLayout(nav)
        
        # 2. Main Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_schedule_tab(), "📅 Lịch Dạy & Buổi Hẹn")
        self.tabs.addTab(self.create_students_tab(), "👥 Danh Sách Học Viên")
        self.tabs.addTab(self.create_availability_tab(), "⏱ Đăng Ký Ca Rảnh")
        self.tabs.addTab(self.create_profile_tab(), "👤 Hồ Sơ & Đánh Giá")
        
        main_layout.addWidget(self.tabs)
        
    def create_schedule_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        lbl = QLabel("LỊCH TRÌNH BUỔI DẠY TRONG TUẦN")
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Khung Giờ", "Học Viên", "Nội Dung Buổi Tập", "Thao Tác"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table.verticalHeader().setVisible(False)
        
        slots = [s for s in SCHEDULE_SLOTS if s["pt"] == self.pt["name"]]
        table.setRowCount(len(slots))
        for row, s in enumerate(slots):
            table.setItem(row, 0, QTableWidgetItem(s["time"]))
            table.setItem(row, 1, QTableWidgetItem(s["member"] or "(Ca Trống)"))
            table.setItem(row, 2, QTableWidgetItem("Tăng cơ ngực & tay sau" if s["member"] else "Sẵn sàng nhận học viên"))
            
            btn_complete = QPushButton("Hoàn Tất Buổi")
            btn_complete.setEnabled(bool(s["member"]))
            btn_complete.clicked.connect(lambda ch, mem=s["member"]: QMessageBox.information(self, "Xác Nhận", f"Đã ghi nhận hoàn tất buổi dạy cho học viên {mem}!"))
            table.setCellWidget(row, 3, btn_complete)
            
        layout.addWidget(table)
        return tab

    def create_students_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        lbl = QLabel("QUẢN LÝ HỌC VIÊN ĐANG THEO KÈM")
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Mã HV", "Họ Tên Học Viên", "SĐT", "Số Buổi Còn Lại", "Nhập InBody"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.verticalHeader().setVisible(False)
        
        table.setRowCount(len(MEMBERS))
        for row, m in enumerate(MEMBERS):
            table.setItem(row, 0, QTableWidgetItem(m["code"]))
            table.setItem(row, 1, QTableWidgetItem(m["name"]))
            table.setItem(row, 2, QTableWidgetItem(m["phone"]))
            table.setItem(row, 3, QTableWidgetItem(f"{m['sessions_left']} buổi"))
            
            btn_inbody = QPushButton("📊 Nhập InBody")
            btn_inbody.setProperty("primary", True)
            btn_inbody.clicked.connect(lambda ch, s=m["name"]: InBodyEntryDialog(s, self).exec())
            table.setCellWidget(row, 4, btn_inbody)
            
        layout.addWidget(table)
        return tab

    def create_availability_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        
        lbl = QLabel("THIẾT LẬP CA RẢNH HÀNG TUẦN (STUDENTS CAN BOOK)")
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl)
        
        card = QFrame()
        card.setObjectName("cardFrame")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(12)
        
        shifts = [
            ("Ca Sáng 1: 06:00 - 08:00", True),
            ("Ca Sáng 2: 08:00 - 10:00", True),
            ("Ca Trưa: 11:30 - 13:30", False),
            ("Ca Chiều: 15:00 - 17:00", True),
            ("Ca Tối (Giờ Vàng): 17:30 - 20:30", True),
        ]
        
        for name, active in shifts:
            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            row.addStretch()
            btn_toggle = QPushButton("Đang Mở Nhận Ca" if active else "Đang Tắt")
            if active:
                btn_toggle.setProperty("success", True)
            row.addWidget(btn_toggle)
            c_layout.addLayout(row)
            
        c_layout.addStretch()
        btn_save = QPushButton("Lưu Cấu Hình Ca Rảnh")
        btn_save.setProperty("primary", True)
        btn_save.clicked.connect(lambda: QMessageBox.information(self, "Lưu Thành Công", "Đã cập nhật lịch khả dụng trên hệ thống đặt lịch hội viên!"))
        c_layout.addWidget(btn_save)
        
        layout.addWidget(card)
        return tab

    def create_profile_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        
        card = QFrame()
        card.setObjectName("cardFrame")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(12)
        
        c_layout.addWidget(QLabel(f"HỒ SƠ HUẤN LUYỆN VIÊN: {self.pt['name'].upper()}"))
        
        rows = [
            ("Chuyên môn:", self.pt["specialty"]),
            ("Kinh nghiệm & Bằng cấp:", self.pt["experience"]),
            ("Đánh giá sao trung bình:", f"{self.pt['rating']} / 5.0 ⭐⭐⭐⭐⭐"),
            ("Tổng số học viên đã kèm:", f"{self.pt['active_students']} học viên"),
            ("Số điện thoại liên hệ:", self.pt["phone"]),
        ]
        for k, v in rows:
            r = QHBoxLayout()
            r.addWidget(QLabel(k))
            r.addStretch()
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
            r.addWidget(lbl_v)
            c_layout.addLayout(r)
            
        c_layout.addStretch()
        layout.addWidget(card)
        return tab
