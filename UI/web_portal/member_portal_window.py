"""
Member Portal Window: Cổng dịch vụ hội viên (1:1 with Web/Components/Pages/Member/*.razor).
Features:
- Digital Subscription Card & QR Check-in (DigitalSubscriptionWidget.razor)
- Package Catalog & VietQR Checkout (Packages.razor)
- PT Booking Wizard (PtBooking.razor)
- Workout & Check-in History (History.razor)
- InBody Dashboard & Progress Chart (InBody.razor)
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QFrame, QScrollArea, QComboBox, QLineEdit, QGridLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from datetime import datetime
from styles.color_tokens import (
    TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, LAYER_BG, 
    BORDER_SUBTLE, ACCENT_PRIMARY, STATUS_SUCCESS
)
from components.qr_widget import QRWidget
from components.chart_widget import ChartWidget
from mock_data import MEMBERS, PACKAGES, TRAINERS, INVOICES, SCHEDULE_SLOTS
from desktop_portal.dialogs.vietqr_dialog import VietQrPaymentDialog

class MemberPortalWindow(QMainWindow):
    switch_portal_requested = pyqtSignal()
    
    def __init__(self, current_member=None, parent=None):
        super().__init__(parent)
        self.member = current_member or MEMBERS[0]
        self.setWindowTitle(f"Cổng Hội Viên Thể Thao • Gym Member Portal ({self.member['name']})")
        self.resize(1180, 780)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # 1. Top Navbar
        nav_header = QHBoxLayout()
        logo_box = QVBoxLayout()
        logo_box.setSpacing(2)
        lbl_brand = QLabel("GYM MEMBER PORTAL")
        lbl_brand.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        lbl_welcome = QLabel(f"Xin chào, {self.member['name']} 👋")
        lbl_welcome.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;")
        logo_box.addWidget(lbl_brand)
        logo_box.addWidget(lbl_welcome)
        nav_header.addLayout(logo_box)
        nav_header.addStretch()
        
        btn_logout = QPushButton("🚪 Đăng Xuất")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self.switch_portal_requested.emit)
        nav_header.addWidget(btn_logout)
        main_layout.addLayout(nav_header)
        
        # 2. Main Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_dashboard_tab(), "💳 Thẻ Điện Tử & Hồ Sơ")
        self.tabs.addTab(self.create_packages_tab(), "📦 Mua Gói Tập (VietQR)")
        self.tabs.addTab(self.create_pt_booking_tab(), "📅 Đặt Lịch Huấn Luyện Viên")
        self.tabs.addTab(self.create_inbody_tab(), "📈 Chỉ Số Cơ Thể InBody")
        self.tabs.addTab(self.create_history_tab(), "📜 Lịch Sử & Hóa Đơn")
        
        main_layout.addWidget(self.tabs)
        
    def create_dashboard_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # Left: Digital Membership Card with QR
        card_frame = QFrame()
        card_frame.setObjectName("cardFrame")
        card_frame.setStyleSheet(f"""
            QFrame#cardFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E3A5F, stop:1 #0F172A);
                border: 1px solid #38BDF8;
                border-radius: 16px;
                padding: 16px;
            }}
        """)
        c_layout = QVBoxLayout(card_frame)
        c_layout.setSpacing(12)
        
        lbl_card_title = QLabel("THẺ HỘI VIÊN ĐIỆN TỬ")
        lbl_card_title.setStyleSheet("color: #38BDF8; font-size: 13px; font-weight: bold; letter-spacing: 1px;")
        c_layout.addWidget(lbl_card_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.qr_code = QRWidget(data=self.member["code"], size=160, caption="Đưa mã này trước máy quét quầy lễ tân để check-in")
        c_layout.addWidget(self.qr_code, alignment=Qt.AlignmentFlag.AlignCenter)
        
        lbl_code = QLabel(f"MÃ SỐ: {self.member['code']}")
        lbl_code.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        lbl_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(lbl_code)
        
        badge_status = QLabel(f"  {self.member['status'].upper()}  ")
        badge_status.setStyleSheet("color: #4ADE80; background-color: #064E3B; border-radius: 4px; font-size: 11px; font-weight: bold; padding: 4px;")
        badge_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(badge_status)
        
        layout.addWidget(card_frame, 4)
        
        # Right: Subscription details & Profile update form
        right_frame = QFrame()
        right_frame.setObjectName("cardFrame")
        r_layout = QVBoxLayout(right_frame)
        r_layout.setContentsMargins(20, 20, 20, 20)
        r_layout.setSpacing(12)
        
        lbl_info_title = QLabel("THÔNG TIN DỊCH VỤ & TÀI KHOẢN")
        lbl_info_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        r_layout.addWidget(lbl_info_title)
        
        info_list = [
            ("Gói tập hiện tại:", self.member["package_name"]),
            ("Ngày bắt đầu:", self.member["start_date"]),
            ("Ngày hết hạn:", self.member["expiry_date"]),
            ("Số buổi kèm PT còn lại:", f"{self.member['sessions_left']} buổi"),
            ("Huấn luyện viên phụ trách:", self.member["pt_assigned"]),
            ("Số điện thoại:", self.member["phone"]),
            ("Email:", self.member["email"]),
        ]
        
        for k, v in info_list:
            row = QHBoxLayout()
            row.addWidget(QLabel(k))
            row.addStretch()
            val_lbl = QLabel(v)
            val_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
            row.addWidget(val_lbl)
            r_layout.addLayout(row)
            
        r_layout.addStretch()
        
        btn_update = QPushButton("Chỉnh Sửa Thông Tin Cá Nhân")
        btn_update.clicked.connect(lambda: QMessageBox.information(self, "Cập Nhật Hồ Sơ", "Lưu thay đổi thông tin liên lạc thành công!"))
        r_layout.addWidget(btn_update)
        
        layout.addWidget(right_frame, 6)
        return tab

    def create_packages_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        
        lbl_title = QLabel("DANH MỤC GÓI TẬP DÀNH CHO BẠN")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(14)
        
        for idx, pkg in enumerate(PACKAGES):
            card = QFrame()
            card.setObjectName("cardFrame")
            card.setStyleSheet(f"background-color: {CARD_BG}; border: 1px solid {BORDER_SUBTLE}; border-radius: 12px; padding: 14px;")
            c_layout = QVBoxLayout(card)
            c_layout.setSpacing(8)
            
            top_row = QHBoxLayout()
            lbl_name = QLabel(pkg["name"])
            lbl_name.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold;")
            top_row.addWidget(lbl_name)
            top_row.addStretch()
            c_layout.addLayout(top_row)
            
            lbl_price = QLabel(f"{pkg['price']:,.0f} đ")
            lbl_price.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 18px; font-weight: bold;")
            c_layout.addWidget(lbl_price)
            
            lbl_desc = QLabel(pkg["benefits"])
            lbl_desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
            lbl_desc.setWordWrap(True)
            c_layout.addWidget(lbl_desc)
            
            c_layout.addStretch()
            
            btn_buy = QPushButton("Đăng Ký & Quét VietQR")
            btn_buy.setProperty("primary", True)
            btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_buy.clicked.connect(lambda ch, p=pkg: self.buy_package(p))
            c_layout.addWidget(btn_buy)
            
            grid.addWidget(card, idx // 2, idx % 2)
            
        scroll.setWidget(container)
        layout.addWidget(scroll)
        return tab

    def buy_package(self, pkg):
        order_code = f"WEB-{datetime.now().strftime('%m%d%H%M')}"
        dlg = VietQrPaymentDialog(pkg["price"], order_code, pkg["name"], self)
        if dlg.exec():
            QMessageBox.information(self, "Đăng Ký Thành Công", f"Chúc mừng bạn đã gia hạn/mua thành công gói {pkg['name']}!")

    def create_pt_booking_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        
        lbl_title = QLabel("ĐẶT LỊCH HẸN VỚI HUẤN LUYỆN VIÊN (PT 1-1)")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        form_card = QFrame()
        form_card.setObjectName("cardFrame")
        f_layout = QVBoxLayout(form_card)
        f_layout.setContentsMargins(20, 20, 20, 20)
        f_layout.setSpacing(12)
        
        f_layout.addWidget(QLabel("1. Chọn Huấn Luyện Viên:"))
        self.cbo_booking_pt = QComboBox()
        for pt in TRAINERS:
            self.cbo_booking_pt.addItem(f"{pt['name']} ({pt['specialty'][:30]}...)", pt)
        f_layout.addWidget(self.cbo_booking_pt)
        
        f_layout.addWidget(QLabel("2. Chọn Ngày Tập:"))
        self.dt_booking = QDateEdit()
        self.dt_booking.setDate(QDate.currentDate().addDays(1))
        self.dt_booking.setCalendarPopup(True)
        f_layout.addWidget(self.dt_booking)
        
        f_layout.addWidget(QLabel("3. Chọn Khung Giờ Ca Rảnh:"))
        self.cbo_booking_slot = QComboBox()
        self.cbo_booking_slot.addItems(["07:00 - 08:00 (Sáng sớm)", "09:00 - 10:00 (Sáng)", "15:00 - 16:00 (Chiều)", "18:00 - 19:00 (Giờ vàng)"])
        f_layout.addWidget(self.cbo_booking_slot)
        
        f_layout.addStretch()
        
        btn_confirm = QPushButton("✓ Xác Nhận Đặt Lịch Hẹn")
        btn_confirm.setFixedHeight(42)
        btn_confirm.setProperty("primary", True)
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.clicked.connect(self.confirm_booking)
        f_layout.addWidget(btn_confirm)
        
        layout.addWidget(form_card)
        return tab

    def confirm_booking(self):
        pt_name = self.cbo_booking_pt.currentText().split("(")[0].strip()
        date_str = self.dt_booking.date().toString("dd/MM/yyyy")
        slot_str = self.cbo_booking_slot.currentText().split("(")[0].strip()
        QMessageBox.information(self, "Đặt Lịch Thành Công", f"Đã gửi lịch hẹn tới HLV {pt_name} vào ngày {date_str} lúc {slot_str}!")

    def create_inbody_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # Stats List
        card = QFrame()
        card.setObjectName("cardFrame")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(16, 16, 16, 16)
        c_layout.setSpacing(12)
        
        c_title = QLabel("CHỈ SỐ THỂ TRẠNG INBODY")
        c_title.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 14px; font-weight: bold;")
        c_layout.addWidget(c_title)
        
        stats = [
            ("Cân nặng hiện tại:", f"{self.member['weight']} kg"),
            ("Chiều cao:", f"{self.member['height']} cm"),
            ("Tỷ lệ mỡ cơ thể (Body Fat):", f"{self.member['body_fat']} %"),
            ("Khối lượng cơ (Muscle):", f"{self.member['muscle_mass']} kg"),
            ("Chỉ số BMI:", f"{self.member['bmi']} (Bình thường)"),
            ("Tỷ lệ chuyển hóa cơ bản (BMR):", "1,640 kcal/ngày"),
        ]
        
        for k, v in stats:
            r = QHBoxLayout()
            r.addWidget(QLabel(k))
            r.addStretch()
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
            r.addWidget(lbl_v)
            c_layout.addLayout(r)
            
        c_layout.addStretch()
        layout.addWidget(card, 4)
        
        # Matplotlib Chart
        chart = ChartWidget(width=6, height=4)
        labels = ["Cân Nặng", "Khối Lượng Cơ", "Tỷ Lệ Mỡ"]
        curr = [self.member["weight"], self.member["muscle_mass"], self.member["body_fat"]]
        targ = [70.0, 38.0, 14.0]
        chart.plot_inbody_radar(labels, curr, targ)
        layout.addWidget(chart, 6)
        
        return tab

    def create_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        lbl_title = QLabel("LỊCH SỬ TẬP LUYỆN & HÓA ĐƠN")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Ngày", "Hoạt Động / Gói", "Chi Tiết / Số Tiền", "Trạng Thái"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        
        table.setRowCount(4)
        logs = [
            ("17/11/2026 08:15", "Điểm danh phòng tập", "Quẹt mã QR tại quầy", "Thành công"),
            ("16/11/2026 17:30", "Buổi tập PT 1-1", "HLV Nguyễn Văn Hưng", "Hoàn tất"),
            ("15/11/2026 08:30", "Điểm danh phòng tập", "Quẹt mã QR tại quầy", "Thành công"),
            ("15/01/2026 08:30", "Đăng ký VIP Platinum 12 Tháng", "4,500,000 đ (VietQR)", "Đã thanh toán"),
        ]
        for row, (d, act, det, st) in enumerate(logs):
            table.setItem(row, 0, QTableWidgetItem(d))
            table.setItem(row, 1, QTableWidgetItem(act))
            table.setItem(row, 2, QTableWidgetItem(det))
            st_item = QTableWidgetItem(st)
            st_item.setForeground(Qt.GlobalColor.green)
            table.setItem(row, 3, st_item)
            
        layout.addWidget(table)
        return tab
