"""
Member Portal Window: Cổng dịch vụ hội viên (1:1 with Web/Components/Member).
Tabs:
- Thẻ Điện Tử & Hồ Sơ (/member/dashboard - DigitalSubscriptionWidget.razor)
- Đặt Lịch Huấn Luyện Viên (/member/booking - PtBooking.razor)
- Chỉ Số Cơ Thể InBody (/member/inbody - InBody.razor)
- Nhật Ký Tập Luyện & Vào Cửa (/member/history - WorkoutHistoryTimeline.razor)
"""

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from components.chart_widget import ChartWidget
from components.qr_widget import QRWidget
from mock_data import MEMBERS, TRAINERS
from styles.color_tokens import (
    ACCENT_PRIMARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class MemberPortalWindow(QMainWindow):
    switch_portal_requested = pyqtSignal()

    def __init__(self, current_member=None, parent=None):
        super().__init__(parent)
        self.member = current_member or MEMBERS[0]
        self.setWindowTitle(
            f"Cổng Hội Viên Thể Thao • Gym Member Portal "
            f"({self.member['name']})"
        )
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
        lbl_brand.setStyleSheet(
            f"color: {ACCENT_PRIMARY}; font-size: 11px; "
            "font-weight: bold; letter-spacing: 1px;"
        )

        lbl_welcome = QLabel(f"Xin chào, {self.member['name']} 👋")
        lbl_welcome.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;"
        )
        logo_box.addWidget(lbl_brand)
        logo_box.addWidget(lbl_welcome)
        nav_header.addLayout(logo_box)
        nav_header.addStretch()

        btn_logout = QPushButton("🚪 Đăng Xuất")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self.switch_portal_requested.emit)
        nav_header.addWidget(btn_logout)
        main_layout.addLayout(nav_header)

        # 2. Main Tabs (4 tabs matching NavMenu.razor 1:1)
        self.tabs = QTabWidget()
        self.tabs.addTab(
            self.create_dashboard_tab(), "💳 Thẻ Điện Tử & Hồ Sơ"
        )
        self.tabs.addTab(
            self.create_pt_booking_tab(), "📅 Đặt Lịch Huấn Luyện Viên"
        )
        self.tabs.addTab(
            self.create_inbody_tab(), "📈 Chỉ Số Cơ Thể InBody"
        )
        self.tabs.addTab(
            self.create_history_tab(), "🕒 Nhật Ký Tập Luyện"
        )

        main_layout.addWidget(self.tabs)

    def create_dashboard_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        # Left: Digital Membership Card with QR
        card_frame = QFrame()
        card_frame.setObjectName("cardFrame")
        card_frame.setStyleSheet("""
            QFrame#cardFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1E3A5F, stop:1 #0F172A
                );
                border: 1px solid #38BDF8;
                border-radius: 16px;
                padding: 16px;
            }
        """)
        c_layout = QVBoxLayout(card_frame)
        c_layout.setSpacing(12)

        lbl_card_title = QLabel("THẺ HỘI VIÊN ĐIỆN TỬ")
        lbl_card_title.setStyleSheet(
            "color: #38BDF8; font-size: 13px; font-weight: bold; "
            "letter-spacing: 1px;"
        )
        c_layout.addWidget(
            lbl_card_title, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.qr_code = QRWidget(
            data=self.member["code"],
            size=160,
            caption="Đưa mã này trước máy quét quầy lễ tân để check-in",
        )
        c_layout.addWidget(
            self.qr_code, alignment=Qt.AlignmentFlag.AlignCenter
        )

        lbl_code = QLabel(f"MÃ SỐ: {self.member['code']}")
        lbl_code.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        lbl_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(lbl_code)

        badge_status = QLabel(f"  {self.member['status'].upper()}  ")
        badge_status.setStyleSheet(
            "color: #4ADE80; background-color: #064E3B; border-radius: 4px; "
            "font-size: 11px; font-weight: bold; padding: 4px;"
        )
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
        lbl_info_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        r_layout.addWidget(lbl_info_title)

        info_list = [
            ("Gói tập hiện tại:", self.member["package_name"]),
            ("Ngày bắt đầu:", self.member["start_date"]),
            ("Ngày hết hạn:", self.member["expiry_date"]),
            (
                "Số buổi kèm PT còn lại:",
                f"{self.member['sessions_left']} buổi",
            ),
            (
                "Huấn luyện viên phụ trách:",
                self.member.get("pt_assigned", "Chưa phân công"),
            ),
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
        btn_update.clicked.connect(
            lambda: QMessageBox.information(
                self,
                "Cập Nhật Hồ Sơ",
                "Lưu thay đổi thông tin liên lạc thành công!",
            )
        )
        r_layout.addWidget(btn_update)

        layout.addWidget(right_frame, 6)
        return tab

    def create_pt_booking_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        lbl_title = QLabel("ĐẶT LỊCH HẸN VỚI HUẤN LUYỆN VIÊN (PT 1-1)")
        lbl_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(lbl_title)

        form_card = QFrame()
        form_card.setObjectName("cardFrame")
        f_layout = QVBoxLayout(form_card)
        f_layout.setContentsMargins(20, 20, 20, 20)
        f_layout.setSpacing(12)

        f_layout.addWidget(QLabel("1. Chọn Huấn Luyện Viên:"))
        self.cbo_booking_pt = QComboBox()
        for pt in TRAINERS:
            self.cbo_booking_pt.addItem(
                f"{pt['name']} ({pt['specialty'][:30]}...)", pt
            )
        f_layout.addWidget(self.cbo_booking_pt)

        f_layout.addWidget(QLabel("2. Chọn Ngày Tập:"))
        self.dt_booking = QDateEdit()
        self.dt_booking.setDate(QDate.currentDate().addDays(1))
        self.dt_booking.setCalendarPopup(True)
        f_layout.addWidget(self.dt_booking)

        f_layout.addWidget(QLabel("3. Chọn Khung Giờ Ca Rảnh:"))
        self.cbo_booking_slot = QComboBox()
        self.cbo_booking_slot.addItems([
            "07:00 - 08:00 (Sáng sớm)",
            "09:00 - 10:00 (Sáng)",
            "15:00 - 16:00 (Chiều)",
            "18:00 - 19:00 (Giờ vàng)",
        ])
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
        QMessageBox.information(
            self,
            "Đặt Lịch Thành Công",
            f"Đã gửi lịch hẹn tới HLV {pt_name} vào ngày {date_str} "
            f"lúc {slot_str}!",
        )

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
        c_title.setStyleSheet(
            f"color: {ACCENT_PRIMARY}; font-size: 14px; font-weight: bold;"
        )
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
        curr = [
            self.member["weight"],
            self.member["muscle_mass"],
            self.member["body_fat"],
        ]
        targ = [70.0, 38.0, 14.0]
        chart.plot_inbody_radar(labels, curr, targ)
        layout.addWidget(chart, 6)

        return tab

    def create_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Header Title & Subtitle (1:1 with Web/Pages/Member/History.razor)
        header_box = QVBoxLayout()
        header_box.setSpacing(4)
        lbl_title = QLabel("NHẬT KÝ TẬP LUYỆN & VÀO CỬA")
        lbl_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        lbl_sub = QLabel(
            "Toàn bộ lịch sử quét mã qua cổng kiểm soát "
            "và các ca tập với huấn luyện viên"
        )
        lbl_sub.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        header_box.addWidget(lbl_title)
        header_box.addWidget(lbl_sub)
        layout.addLayout(header_box)

        # Filter buttons bar (1:1 with WorkoutHistoryTimeline.razor)
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        self.btn_filter_all = QPushButton("Tất Cả Hoạt Động")
        self.btn_filter_checkin = QPushButton("Vào Cửa Phòng Tập")
        self.btn_filter_pt = QPushButton("Tập Với HLV (PT)")

        for btn in (
            self.btn_filter_all,
            self.btn_filter_checkin,
            self.btn_filter_pt,
        ):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(34)
            filter_layout.addWidget(btn)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Table Widget
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "Thời Gian",
            "Loại Hoạt Động",
            "Nội Dung Hoạt Động",
            "Chi Tiết / Ghi Chú",
        ])
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.history_table.setColumnWidth(0, 150)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.history_table.setColumnWidth(1, 170)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.history_table.setColumnWidth(2, 270)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.history_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self.history_table)

        # Events data (Checkin & PT sessions for current member)
        pt_name = self.member.get("pt_assigned", "Nguyễn Văn Hưng")
        self.workout_events = [
            {
                "time": "18/11/2026 08:15",
                "type": "CHECKIN",
                "badge": "Vào Cửa Phòng Tập",
                "title": "Điểm danh vào cổng phòng gym",
                "detail": (
                    "Phương thức: Quét mã QR tại cổng kiểm soát - Hợp lệ"
                ),
            },
            {
                "time": "17/11/2026 17:30",
                "type": "PT",
                "badge": "Tập Luyện PT 1-1",
                "title": f"Buổi tập cùng HLV {pt_name}",
                "detail": (
                    "Trạng thái: Hoàn tất (60 phút) • Nhóm cơ ngực & tay sau"
                ),
            },
            {
                "time": "16/11/2026 09:00",
                "type": "CHECKIN",
                "badge": "Vào Cửa Phòng Tập",
                "title": "Điểm danh vào cổng phòng gym",
                "detail": (
                    "Phương thức: Quét mã QR tại quầy lễ tân - Hợp lệ"
                ),
            },
            {
                "time": "15/11/2026 18:00",
                "type": "PT",
                "badge": "Tập Luyện PT 1-1",
                "title": f"Buổi tập cùng HLV {pt_name}",
                "detail": (
                    "Trạng thái: Hoàn tất (60 phút) • Cardio HIIT & Thể lực"
                ),
            },
            {
                "time": "14/11/2026 08:45",
                "type": "CHECKIN",
                "badge": "Vào Cửa Phòng Tập",
                "title": "Điểm danh vào cổng phòng gym",
                "detail": (
                    "Phương thức: Quét mã QR tại cổng kiểm soát - Hợp lệ"
                ),
            },
            {
                "time": "12/11/2026 17:00",
                "type": "PT",
                "badge": "Tập Luyện PT 1-1",
                "title": f"Buổi tập cùng HLV {pt_name}",
                "detail": (
                    "Trạng thái: Hoàn tất (60 phút) • Chân đùi & Squat form"
                ),
            },
            {
                "time": "10/11/2026 07:30",
                "type": "CHECKIN",
                "badge": "Vào Cửa Phòng Tập",
                "title": "Điểm danh vào cổng phòng gym",
                "detail": (
                    "Phương thức: Quét mã QR tại cổng kiểm soát - Hợp lệ"
                ),
            },
            {
                "time": "08/11/2026 08:00",
                "type": "CHECKIN",
                "badge": "Vào Cửa Phòng Tập",
                "title": "Điểm danh vào cổng phòng gym",
                "detail": (
                    "Phương thức: Quét mã QR tại cổng kiểm soát - Hợp lệ"
                ),
            },
        ]

        self.btn_filter_all.clicked.connect(
            lambda: self.apply_history_filter("ALL")
        )
        self.btn_filter_checkin.clicked.connect(
            lambda: self.apply_history_filter("CHECKIN")
        )
        self.btn_filter_pt.clicked.connect(
            lambda: self.apply_history_filter("PT")
        )

        self.apply_history_filter("ALL")
        return tab

    def apply_history_filter(self, filter_type: str) -> None:
        active_style = (
            "background-color: #38BDF8; color: #0F172A; font-weight: bold; "
            "border-radius: 6px; padding: 6px 14px; border: none;"
        )
        inactive_style = (
            "background-color: #1E293B; color: #94A3B8; font-weight: 500; "
            "border-radius: 6px; padding: 6px 14px; border: 1px solid #334155;"
        )

        self.btn_filter_all.setStyleSheet(
            active_style if filter_type == "ALL" else inactive_style
        )
        self.btn_filter_checkin.setStyleSheet(
            active_style if filter_type == "CHECKIN" else inactive_style
        )
        self.btn_filter_pt.setStyleSheet(
            active_style if filter_type == "PT" else inactive_style
        )

        if filter_type == "CHECKIN":
            filtered = [
                ev for ev in self.workout_events if ev["type"] == "CHECKIN"
            ]
        elif filter_type == "PT":
            filtered = [
                ev for ev in self.workout_events if ev["type"] == "PT"
            ]
        else:
            filtered = self.workout_events

        self.history_table.setRowCount(len(filtered))
        for row_idx, ev in enumerate(filtered):
            self.history_table.setRowHeight(row_idx, 38)

            # Col 0: Thời Gian
            item_time = QTableWidgetItem(ev["time"])
            item_time.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_time.setForeground(QColor("#94A3B8"))
            self.history_table.setItem(row_idx, 0, item_time)

            # Col 1: Loại Hoạt Động
            item_type = QTableWidgetItem(f" ● {ev['badge']}")
            item_type.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            if ev["type"] == "PT":
                item_type.setForeground(QColor("#38BDF8"))
            else:
                item_type.setForeground(QColor("#34D399"))
            self.history_table.setItem(row_idx, 1, item_type)

            # Col 2: Nội Dung Hoạt Động
            item_title = QTableWidgetItem(ev["title"])
            item_title.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_title.setForeground(QColor("#F8FAFC"))
            self.history_table.setItem(row_idx, 2, item_title)

            # Col 3: Chi Tiết / Ghi Chú
            item_detail = QTableWidgetItem(ev["detail"])
            item_detail.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_detail.setForeground(QColor("#94A3B8"))
            self.history_table.setItem(row_idx, 3, item_detail)
