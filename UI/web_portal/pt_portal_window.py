"""
Trainer (PT) Portal Window: Cổng dịch vụ huấn luyện viên cá nhân.
1:1 with Web/Components/Pages/PT/*.razor:
- Weekly Schedule & Session Dispatching (PtWeeklySchedule.razor)
- Availability Grid & Shift Registration (PtAvailabilityGrid.razor)
- Student Management & Progress (PtStudentsList.razor)
- Trainer Profile & Rating Summary (PtProfileSummaryWidget.razor)
- InBody Measurement Entry Modal (InBodyEntryModal.razor)
"""

from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from mock_data import MEMBERS, TRAINERS
from styles.color_tokens import (
    ACCENT_PRIMARY,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class InBodyEntryDialog(QDialog):
    def __init__(self, student_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            f"Nhập Chỉ Số InBody • Học Viên: {student_name}"
        )
        self.setFixedSize(420, 380)
        self.setStyleSheet(
            "background-color: #162032; border: 1px solid #334155; "
            "border-radius: 12px;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_title = QLabel("NHẬP KẾT QUẢ ĐO INBODY")
        lbl_title.setStyleSheet(
            f"color: {ACCENT_PRIMARY}; font-size: 14px; font-weight: bold;"
        )
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
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("✓ Lưu Chỉ Số InBody")
        btn_save.setProperty("primary", True)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.save_data)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def save_data(self):
        QMessageBox.information(
            self,
            "Thành Công",
            "Đã cập nhật chỉ số InBody mới cho học viên!",
        )
        self.accept()


class PtPortalWindow(QMainWindow):
    switch_portal_requested = pyqtSignal()

    def __init__(self, current_pt=None, parent=None):
        super().__init__(parent)
        self.pt = current_pt or TRAINERS[0]
        self.setWindowTitle(
            f"Cổng Huấn Luyện Viên (PT) • Gym Trainer Portal "
            f"({self.pt['name']})"
        )
        self.resize(1180, 780)

        # Calculate standard week days (Monday to Sunday)
        self.today = datetime.today().date()
        self.monday = self.today - timedelta(days=self.today.weekday())
        self.week_days = [
            self.monday + timedelta(days=i) for i in range(7)
        ]

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
        lbl_brand.setStyleSheet(
            f"color: {ACCENT_PRIMARY}; font-size: 11px; font-weight: bold; "
            "letter-spacing: 1px;"
        )

        lbl_name = QLabel(
            f"Huấn Luyện Viên: {self.pt['name']} ⭐ {self.pt['rating']}"
        )
        lbl_name.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;"
        )

        title_box.addWidget(lbl_brand)
        title_box.addWidget(lbl_name)
        nav.addLayout(title_box)
        nav.addStretch()

        btn_logout = QPushButton("🚪 Đăng Xuất")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self.switch_portal_requested.emit)
        nav.addWidget(btn_logout)
        main_layout.addLayout(nav)

        # Initialize mock schedule data with explicit dates
        self.schedule_sessions = [
            {
                "date": self.week_days[0],
                "time": "08:00 - 09:00",
                "member": "Trần Thị Thu Thảo",
                "topic": "Khởi động & Cardio sức bền",
                "status": "Đã hoàn thành",
            },
            {
                "date": self.week_days[1],
                "time": "09:00 - 10:00",
                "member": "Lê Anh Tuấn",
                "topic": "Tăng cơ lưng xô & tay trước",
                "status": "Đã hoàn thành",
            },
            {
                "date": self.week_days[2],
                "time": "07:00 - 08:00",
                "member": "Nguyễn Hoàng Nam",
                "topic": "Tăng cơ ngực & tay sau",
                "status": "Đã xác nhận",
            },
            {
                "date": self.week_days[2],
                "time": "09:00 - 10:00",
                "member": "Hoàng Văn Đạt",
                "topic": "Cardio HIIT & giảm mỡ",
                "status": "Đã xác nhận",
            },
            {
                "date": self.week_days[2],
                "time": "15:00 - 16:00",
                "member": "",
                "topic": "Sẵn sàng nhận học viên",
                "status": "Còn trống",
            },
            {
                "date": self.week_days[2],
                "time": "18:00 - 19:00",
                "member": "Lê Quốc Thịnh",
                "topic": "Chân đùi & Squat chuyên sâu",
                "status": "Đã xác nhận",
            },
            {
                "date": self.week_days[3],
                "time": "08:00 - 09:00",
                "member": "Vũ Mai Phương",
                "topic": "Giáo án mông đùi nữ",
                "status": "Đã xác nhận",
            },
            {
                "date": self.week_days[3],
                "time": "17:30 - 18:30",
                "member": "Đỗ Bích Ngọc",
                "topic": "Thể lực & Core bụng",
                "status": "Đã xác nhận",
            },
            {
                "date": self.week_days[4],
                "time": "07:00 - 08:00",
                "member": "Phạm Quốc Dũng",
                "topic": "Phục hồi chức năng cơ",
                "status": "Đã xác nhận",
            },
            {
                "date": self.week_days[4],
                "time": "18:00 - 19:00",
                "member": "Nguyễn Hoàng Nam",
                "topic": "Kiểm tra form Deadlift",
                "status": "Đã xác nhận",
            },
            {
                "date": self.week_days[5],
                "time": "09:00 - 10:00",
                "member": "Hoàng Văn Đạt",
                "topic": "Tổng hợp toàn thân",
                "status": "Đã xác nhận",
            },
            {
                "date": self.week_days[6],
                "time": "15:00 - 16:00",
                "member": "",
                "topic": "Ca trống cuối tuần",
                "status": "Còn trống",
            },
        ]

        # 2. Main Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(
            self.create_schedule_tab(), "📅 Lịch Dạy & Buổi Hẹn"
        )
        self.tabs.addTab(
            self.create_students_tab(), "👥 Danh Sách Học Viên"
        )
        self.tabs.addTab(
            self.create_availability_tab(), "⏱ Đăng Ký Ca Rảnh"
        )
        self.tabs.addTab(
            self.create_profile_tab(), "👤 Hồ Sơ & Đánh Giá"
        )

        main_layout.addWidget(self.tabs)

    # =========================================================================
    # TAB 1: LỊCH DẠY & BUỔI HẸN (PtWeeklySchedule.razor)
    # =========================================================================
    def create_schedule_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header Title & Reload
        header_row = QHBoxLayout()
        h_box = QVBoxLayout()
        h_box.setSpacing(2)
        lbl = QLabel("LỊCH TRÌNH BUỔI DẠY TRONG TUẦN")
        lbl.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        lbl_sub = QLabel(
            "Theo dõi các ca tập 1-1 theo ngày và xác nhận hoàn thành buổi tập"
        )
        lbl_sub.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        h_box.addWidget(lbl)
        h_box.addWidget(lbl_sub)
        header_row.addLayout(h_box)
        header_row.addStretch()

        btn_reload = QPushButton("↻ Làm mới")
        btn_reload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reload.clicked.connect(self.reload_schedule_tab)
        header_row.addWidget(btn_reload)
        layout.addLayout(header_row)

        # Day Carousel for the week (Thứ 2 to Chủ Nhật)
        lbl_day_select = QLabel("Chọn ngày huấn luyện:")
        lbl_day_select.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: 600;"
        )
        layout.addWidget(lbl_day_select)

        self.schedule_day_buttons_layout = QHBoxLayout()
        self.schedule_day_buttons_layout.setSpacing(8)
        self.schedule_day_buttons = []
        self.selected_schedule_date = self.today

        day_names = [
            "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"
        ]

        # Button for "Tất Cả Tuần"
        self.btn_sched_all = QPushButton("Tất Cả\nTuần Này")
        self.btn_sched_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sched_all.setFixedHeight(50)
        self.btn_sched_all.setFixedWidth(96)
        self.btn_sched_all.clicked.connect(
            lambda: self.select_schedule_date(None)
        )
        self.schedule_day_buttons_layout.addWidget(self.btn_sched_all)

        for idx, d in enumerate(self.week_days):
            btn_d = QPushButton()
            btn_d.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_d.setFixedHeight(50)
            btn_d.setFixedWidth(96)
            btn_d.setText(f"{day_names[idx]}\n{d.strftime('%d/%m')}")
            btn_d.clicked.connect(
                lambda ch, date_val=d: self.select_schedule_date(date_val)
            )
            self.schedule_day_buttons.append(btn_d)
            self.schedule_day_buttons_layout.addWidget(btn_d)

        self.schedule_day_buttons_layout.addStretch()
        layout.addLayout(self.schedule_day_buttons_layout)

        # Schedule Table with explicit NGÀY column
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels([
            "Ngày",
            "Khung Giờ",
            "Học Viên",
            "Nội Dung Buổi Tập",
            "Trạng Thái",
            "Thao Tác",
        ])
        header = self.schedule_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.schedule_table.setColumnWidth(0, 110)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.schedule_table.setColumnWidth(1, 130)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.schedule_table.setColumnWidth(2, 180)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.schedule_table.setColumnWidth(4, 130)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.schedule_table.setColumnWidth(5, 150)
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setAlternatingRowColors(True)

        layout.addWidget(self.schedule_table)
        self.select_schedule_date(self.today)
        return tab

    def select_schedule_date(self, date_val):
        self.selected_schedule_date = date_val

        # Update button styles
        if date_val is None:
            self.btn_sched_all.setStyleSheet(
                "background-color: #0284C7; color: #FFFFFF; "
                "font-weight: bold; border-radius: 8px; border: none; "
                "padding: 4px; font-size: 12px;"
            )
        else:
            self.btn_sched_all.setStyleSheet(
                "background-color: #1E293B; color: #94A3B8; "
                "border-radius: 8px; border: 1px solid #334155; "
                "padding: 4px; font-size: 12px;"
            )

        for idx, d in enumerate(self.week_days):
            btn = self.schedule_day_buttons[idx]
            if d == date_val:
                btn.setStyleSheet(
                    "background-color: #0284C7; color: #FFFFFF; "
                    "font-weight: bold; border-radius: 8px; border: none; "
                    "padding: 4px; font-size: 12px;"
                )
            elif d < self.today:
                # Past days: grayed out
                btn.setStyleSheet(
                    "background-color: #0F172A; color: #64748B; "
                    "border-radius: 8px; border: 1px solid #1E293B; "
                    "padding: 4px; font-size: 12px;"
                )
            else:
                # Upcoming days: standard dark
                btn.setStyleSheet(
                    "background-color: #1E293B; color: #F8FAFC; "
                    "border-radius: 8px; border: 1px solid #334155; "
                    "padding: 4px; font-size: 12px;"
                )

        self.render_schedule_table()

    def render_schedule_table(self):
        if self.selected_schedule_date is None:
            slots = self.schedule_sessions
        else:
            slots = [
                s for s in self.schedule_sessions
                if s["date"] == self.selected_schedule_date
            ]

        self.schedule_table.setRowCount(len(slots))
        for row, s in enumerate(slots):
            self.schedule_table.setRowHeight(row, 44)

            # Col 0: Ngày
            d_str = s["date"].strftime("%d/%m/%Y")
            item_date = QTableWidgetItem(d_str)
            item_date.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            color_date = (
                QColor("#64748B") if s["date"] < self.today
                else QColor("#38BDF8")
            )
            item_date.setForeground(color_date)
            self.schedule_table.setItem(row, 0, item_date)

            # Col 1: Khung Giờ
            item_time = QTableWidgetItem(s["time"])
            item_time.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_time.setForeground(QColor("#94A3B8"))
            self.schedule_table.setItem(row, 1, item_time)

            # Col 2: Học Viên
            item_mem = QTableWidgetItem(s["member"] or "(Ca Trống)")
            item_mem.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_mem.setForeground(
                QColor("#F8FAFC") if s["member"] else QColor("#64748B")
            )
            self.schedule_table.setItem(row, 2, item_mem)

            # Col 3: Nội Dung Buổi Tập
            item_desc = QTableWidgetItem(s["topic"])
            item_desc.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_desc.setForeground(
                QColor("#CBD5E1") if s["member"] else QColor("#64748B")
            )
            self.schedule_table.setItem(row, 3, item_desc)

            # Col 4: Trạng Thái
            st = s["status"]
            item_st = QTableWidgetItem(st)
            item_st.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            if st == "Đã hoàn thành":
                item_st.setForeground(QColor("#34D399"))
            elif st == "Đã xác nhận":
                item_st.setForeground(QColor("#38BDF8"))
            else:
                item_st.setForeground(QColor("#64748B"))
            self.schedule_table.setItem(row, 4, item_st)

            # Col 5: Thao Tác (Compact button with tableAction property)
            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(4, 2, 4, 2)
            a_layout.setSpacing(0)

            btn_complete = QPushButton("Hoàn Tất Buổi")
            btn_complete.setProperty("tableAction", True)
            btn_complete.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_complete.setEnabled(
                bool(s["member"]) and s["status"] != "Đã hoàn thành"
            )
            if s["status"] == "Đã hoàn thành":
                btn_complete.setText("✓ Đã Xong")
                btn_complete.setEnabled(False)
            elif s["member"]:
                btn_complete.setProperty("actionVariant", "primary")
                btn_complete.clicked.connect(
                    lambda ch, item=s: self.complete_session(item)
                )

            a_layout.addWidget(btn_complete)
            self.schedule_table.setCellWidget(row, 5, action_widget)

    def complete_session(self, slot_item):
        slot_item["status"] = "Đã hoàn thành"
        self.render_schedule_table()
        QMessageBox.information(
            self,
            "Xác Nhận",
            f"Đã ghi nhận hoàn tất buổi dạy cho học viên "
            f"{slot_item['member']}!",
        )

    def reload_schedule_tab(self):
        self.render_schedule_table()
        QMessageBox.information(
            self, "Làm Mới", "Đã đồng bộ lại lịch dạy từ hệ thống!"
        )

    # =========================================================================
    # TAB 2: DANH SÁCH HỌC VIÊN (PtStudentsList.razor)
    # =========================================================================
    def create_students_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        h_box = QVBoxLayout()
        h_box.setSpacing(2)
        lbl = QLabel("QUẢN LÝ HỌC VIÊN ĐANG THEO KÈM")
        lbl.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        lbl_sub = QLabel(
            "Danh sách học viên đăng ký gói kèm PT cá nhân 1-1"
        )
        lbl_sub.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        h_box.addWidget(lbl)
        h_box.addWidget(lbl_sub)
        layout.addLayout(h_box)

        # Search Bar
        self.txt_student_search = QLineEdit()
        self.txt_student_search.setPlaceholderText(
            "🔍 Tìm kiếm theo tên học viên, số điện thoại, mã số…"
        )
        self.txt_student_search.textChanged.connect(self.filter_students)
        layout.addWidget(self.txt_student_search)

        self.students_table = QTableWidget()
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels([
            "Mã HV",
            "Họ Tên Học Viên",
            "SĐT",
            "Số Buổi Còn Lại",
            "Nhập InBody",
        ])
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.students_table.setColumnWidth(0, 110)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.students_table.setColumnWidth(1, 200)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.students_table.setColumnWidth(2, 140)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.students_table.setColumnWidth(4, 160)
        self.students_table.verticalHeader().setVisible(False)
        self.students_table.setAlternatingRowColors(True)

        layout.addWidget(self.students_table)
        self.render_students(MEMBERS)
        return tab

    def filter_students(self, keyword: str):
        kw = keyword.strip().lower()
        if not kw:
            self.render_students(MEMBERS)
            return
        matched = [
            m for m in MEMBERS
            if kw in m["name"].lower()
            or kw in m["phone"]
            or kw in m["code"].lower()
        ]
        self.render_students(matched)

    def render_students(self, members):
        self.students_table.setRowCount(len(members))
        for row, m in enumerate(members):
            self.students_table.setRowHeight(row, 44)

            # Col 0: Mã HV
            item_code = QTableWidgetItem(m["code"])
            item_code.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_code.setForeground(QColor("#94A3B8"))
            self.students_table.setItem(row, 0, item_code)

            # Col 1: Họ Tên
            item_name = QTableWidgetItem(m["name"])
            item_name.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_name.setForeground(QColor("#F8FAFC"))
            self.students_table.setItem(row, 1, item_name)

            # Col 2: SĐT
            item_phone = QTableWidgetItem(m["phone"])
            item_phone.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_phone.setForeground(QColor("#94A3B8"))
            self.students_table.setItem(row, 2, item_phone)

            # Col 3: Số Buổi Còn Lại
            item_left = QTableWidgetItem(f"{m['sessions_left']} buổi")
            item_left.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_left.setForeground(QColor("#38BDF8"))
            self.students_table.setItem(row, 3, item_left)

            # Col 4: Thao Tác (Compact button with tableAction property)
            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(4, 2, 4, 2)
            a_layout.setSpacing(0)

            btn_inbody = QPushButton("📊 Nhập InBody")
            btn_inbody.setProperty("tableAction", True)
            btn_inbody.setProperty("actionVariant", "primary")
            btn_inbody.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_inbody.clicked.connect(
                lambda ch, s=m["name"]: InBodyEntryDialog(s, self).exec()
            )
            a_layout.addWidget(btn_inbody)
            self.students_table.setCellWidget(row, 4, action_widget)

    # =========================================================================
    # TAB 3: ĐĂNG KÝ CA RẢNH (PtAvailabilityGrid.razor)
    # =========================================================================
    def create_availability_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Header Title & Subtitle
        header_row = QHBoxLayout()
        h_box = QVBoxLayout()
        h_box.setSpacing(2)
        lbl_title = QLabel("ĐĂNG KÝ KHUNG GIỜ RẢNH DẠY KÈM")
        lbl_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        lbl_sub = QLabel(
            "Mở các khung giờ trong tuần để học viên có thể chủ động đặt lịch"
        )
        lbl_sub.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        h_box.addWidget(lbl_title)
        h_box.addWidget(lbl_sub)
        header_row.addLayout(h_box)
        header_row.addStretch()

        btn_reload = QPushButton("↻ Làm mới")
        btn_reload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reload.clicked.connect(self.reload_availability_data)
        header_row.addWidget(btn_reload)
        layout.addLayout(header_row)

        # 1. Day Selector (Standard Week: Thứ 2 -> Chủ Nhật)
        lbl_day = QLabel("Chọn ngày thiết lập:")
        lbl_day.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: 600;"
        )
        layout.addWidget(lbl_day)

        self.day_buttons_layout = QHBoxLayout()
        self.day_buttons_layout.setSpacing(8)
        self.day_buttons = []
        self.selected_avail_date = self.today

        day_names = [
            "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"
        ]

        for idx, d in enumerate(self.week_days):
            btn_d = QPushButton()
            btn_d.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_d.setFixedHeight(50)
            btn_d.setFixedWidth(96)
            btn_d.setText(f"{day_names[idx]}\n{d.strftime('%d/%m')}")
            btn_d.clicked.connect(
                lambda ch, date_val=d: self.select_avail_date(date_val)
            )
            self.day_buttons.append(btn_d)
            self.day_buttons_layout.addWidget(btn_d)

        self.day_buttons_layout.addStretch()
        layout.addLayout(self.day_buttons_layout)

        # 2. Time Range Selector Card
        time_card = QFrame()
        time_card.setObjectName("cardFrame")
        t_layout = QVBoxLayout(time_card)
        t_layout.setContentsMargins(16, 12, 16, 12)
        t_layout.setSpacing(8)

        self.lbl_time_target = QLabel()
        self.lbl_time_target.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600;"
        )
        t_layout.addWidget(self.lbl_time_target)

        # Past-date warning banner
        self.lbl_past_warning = QLabel(
            "⚠️ Ngày này đã qua trong quá khứ. "
            "Không thể đăng ký thêm khung giờ rảnh mới."
        )
        self.lbl_past_warning.setStyleSheet(
            "color: #F87171; font-size: 12px; font-weight: 600; "
            "background-color: rgba(239, 68, 68, 0.15); "
            "border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; "
            "padding: 6px 10px;"
        )
        self.lbl_past_warning.setVisible(False)
        t_layout.addWidget(self.lbl_past_warning)

        # Inputs row: labels, combo boxes, and add button in a single row
        inputs_row = QHBoxLayout()
        inputs_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        inputs_row.setSpacing(10)

        lbl_s = QLabel("Giờ bắt đầu:")
        lbl_s.setStyleSheet("color: #94A3B8; font-size: 13px;")
        inputs_row.addWidget(lbl_s)

        self.cbo_start_time = QComboBox()
        self.cbo_start_time.setFixedHeight(36)
        self.cbo_start_time.addItems([
            "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
            "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"
        ])
        self.cbo_start_time.setCurrentText("08:00")
        inputs_row.addWidget(self.cbo_start_time)

        lbl_e = QLabel("Giờ kết thúc:")
        lbl_e.setStyleSheet("color: #94A3B8; font-size: 13px;")
        inputs_row.addWidget(lbl_e)

        self.cbo_end_time = QComboBox()
        self.cbo_end_time.setFixedHeight(36)
        self.cbo_end_time.addItems([
            "07:00", "08:00", "09:00", "10:00", "11:00", "12:00",
            "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"
        ])
        self.cbo_end_time.setCurrentText("09:00")
        inputs_row.addWidget(self.cbo_end_time)

        inputs_row.addStretch()

        self.btn_add_slot = QPushButton("+ Mở Khung Giờ Này")
        self.btn_add_slot.setFixedHeight(36)
        self.btn_add_slot.setProperty("primary", True)
        self.btn_add_slot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_slot.clicked.connect(self.add_avail_slot)
        inputs_row.addWidget(self.btn_add_slot)
        t_layout.addLayout(inputs_row)

        layout.addWidget(time_card)

        # 3. Slots Table
        self.lbl_slots_count = QLabel()
        self.lbl_slots_count.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: 600;"
        )
        layout.addWidget(self.lbl_slots_count)

        self.avail_table = QTableWidget()
        self.avail_table.setColumnCount(4)
        self.avail_table.setHorizontalHeaderLabels([
            "Khung Giờ",
            "Trạng Thái",
            "Chi Tiết / Học Viên Đặt",
            "Thao Tác",
        ])
        header = self.avail_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.avail_table.setColumnWidth(0, 150)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.avail_table.setColumnWidth(1, 180)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.avail_table.setColumnWidth(3, 140)
        self.avail_table.verticalHeader().setVisible(False)
        self.avail_table.setAlternatingRowColors(True)
        layout.addWidget(self.avail_table)

        # Initial Mock Data for availability slots across the week
        self.availability_slots = [
            {
                "date": self.week_days[0],
                "time": "08:00 - 09:00",
                "status": "BOOKED",
                "member": "Trần Thị Thu Thảo",
            },
            {
                "date": self.week_days[1],
                "time": "09:00 - 10:00",
                "status": "BOOKED",
                "member": "Lê Anh Tuấn",
            },
            {
                "date": self.week_days[2],
                "time": "07:00 - 08:00",
                "status": "BOOKED",
                "member": "Nguyễn Hoàng Nam",
            },
            {
                "date": self.week_days[2],
                "time": "09:00 - 10:00",
                "status": "BOOKED",
                "member": "Hoàng Văn Đạt",
            },
            {
                "date": self.week_days[2],
                "time": "15:00 - 16:00",
                "status": "OPEN",
                "member": "",
            },
            {
                "date": self.week_days[2],
                "time": "18:00 - 19:00",
                "status": "BOOKED",
                "member": "Lê Quốc Thịnh",
            },
            {
                "date": self.week_days[3],
                "time": "08:00 - 09:00",
                "status": "BOOKED",
                "member": "Vũ Mai Phương",
            },
            {
                "date": self.week_days[3],
                "time": "16:00 - 17:00",
                "status": "OPEN",
                "member": "",
            },
            {
                "date": self.week_days[4],
                "time": "07:00 - 08:00",
                "status": "OPEN",
                "member": "",
            },
            {
                "date": self.week_days[4],
                "time": "17:30 - 18:30",
                "status": "OPEN",
                "member": "",
            },
            {
                "date": self.week_days[5],
                "time": "09:00 - 10:00",
                "status": "OPEN",
                "member": "",
            },
            {
                "date": self.week_days[6],
                "time": "15:00 - 16:00",
                "status": "OPEN",
                "member": "",
            },
        ]

        # 4. Save Button
        btn_save = QPushButton("✓ Lưu Thay Đổi Lịch Rảnh")
        btn_save.setFixedHeight(42)
        btn_save.setProperty("primary", True)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.save_availability_changes)
        layout.addWidget(btn_save)

        self.select_avail_date(self.today)
        return tab

    def select_avail_date(self, date_val):
        self.selected_avail_date = date_val
        is_past = date_val < self.today

        # Update warning banner & button state
        self.lbl_past_warning.setVisible(is_past)
        self.btn_add_slot.setEnabled(not is_past)

        for idx, d in enumerate(self.week_days):
            btn = self.day_buttons[idx]
            if d == date_val:
                # Sáng hôm được chọn (active)
                btn.setStyleSheet(
                    "background-color: #0284C7; color: #FFFFFF; "
                    "font-weight: bold; border-radius: 8px; border: none; "
                    "padding: 4px; font-size: 12px;"
                )
            elif d < self.today:
                # Ngày đã qua: màu xám
                btn.setStyleSheet(
                    "background-color: #0F172A; color: #64748B; "
                    "border-radius: 8px; border: 1px solid #1E293B; "
                    "padding: 4px; font-size: 12px;"
                )
            else:
                # Ngày sắp tới (bình thường)
                btn.setStyleSheet(
                    "background-color: #1E293B; color: #F8FAFC; "
                    "border-radius: 8px; border: 1px solid #334155; "
                    "padding: 4px; font-size: 12px;"
                )

        d_str = date_val.strftime("%d/%m/%Y")
        self.lbl_time_target.setText(f"Thiết lập khung giờ: {d_str}")
        self.render_day_slots()

    def render_day_slots(self):
        d_str = self.selected_avail_date.strftime("%d/%m/%Y")
        day_slots = [
            s for s in self.availability_slots
            if s["date"] == self.selected_avail_date
        ]
        self.lbl_slots_count.setText(
            f"Các khung giờ ngày {d_str}: ({len(day_slots)} khung giờ)"
        )

        self.avail_table.setRowCount(len(day_slots))
        for row, s in enumerate(day_slots):
            self.avail_table.setRowHeight(row, 44)

            # Col 0: Khung Giờ
            item_time = QTableWidgetItem(s["time"])
            item_time.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_time.setForeground(QColor("#F8FAFC"))
            self.avail_table.setItem(row, 0, item_time)

            # Col 1: Trạng Thái Badge
            if s["status"] == "BOOKED":
                status_text = "🔒 Đã có học viên đặt"
                status_color = QColor("#FBBF24")
            else:
                status_text = "✓ Đang mở nhận lịch"
                status_color = QColor("#38BDF8")

            item_status = QTableWidgetItem(status_text)
            item_status.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_status.setForeground(status_color)
            self.avail_table.setItem(row, 1, item_status)

            # Col 2: Chi Tiết / Học Viên
            detail_text = (
                f"Học viên: {s['member']}"
                if s["member"]
                else "Sẵn sàng nhận học viên đặt lịch mới"
            )
            item_det = QTableWidgetItem(detail_text)
            item_det.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item_det.setForeground(QColor("#94A3B8"))
            self.avail_table.setItem(row, 2, item_det)

            # Col 3: Thao Tác (Button "✕ Hủy Mở")
            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(4, 2, 4, 2)
            a_layout.setSpacing(0)

            btn_del = QPushButton("✕ Hủy Mở")
            btn_del.setProperty("tableAction", True)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            if s["status"] == "BOOKED" or s["date"] < self.today:
                btn_del.setEnabled(False)
            else:
                btn_del.setProperty("actionVariant", "danger")
                btn_del.clicked.connect(
                    lambda ch, slot=s: self.remove_avail_slot(slot)
                )

            a_layout.addWidget(btn_del)
            self.avail_table.setCellWidget(row, 3, action_widget)

    def add_avail_slot(self):
        if self.selected_avail_date < self.today:
            QMessageBox.warning(
                self,
                "Không Hợp Lệ",
                "Không thể mở khung giờ cho ngày đã qua trong quá khứ!",
            )
            return

        start_t = self.cbo_start_time.currentText()
        end_t = self.cbo_end_time.currentText()

        # Validate start < end
        start_h = int(start_t.split(":")[0])
        end_h = int(end_t.split(":")[0])
        if end_h <= start_h:
            QMessageBox.warning(
                self,
                "Cảnh Báo",
                "Giờ kết thúc phải lớn hơn giờ bắt đầu (tối thiểu 60 phút)!",
            )
            return

        slot_str = f"{start_t} - {end_t}"
        # Check collision
        collision = any(
            s["date"] == self.selected_avail_date and s["time"] == slot_str
            for s in self.availability_slots
        )
        if collision:
            QMessageBox.warning(
                self,
                "Khung Giờ Trùng",
                f"Khung giờ {slot_str} đã tồn tại trong ngày này!",
            )
            return

        self.availability_slots.append({
            "date": self.selected_avail_date,
            "time": slot_str,
            "status": "OPEN",
            "member": "",
        })
        self.render_day_slots()
        # Suggest next slot
        idx = self.cbo_end_time.currentIndex()
        if idx < self.cbo_start_time.count() - 1:
            self.cbo_start_time.setCurrentIndex(idx)
            self.cbo_end_time.setCurrentIndex(
                min(idx + 1, self.cbo_end_time.count() - 1)
            )

    def remove_avail_slot(self, slot):
        if slot in self.availability_slots:
            self.availability_slots.remove(slot)
            self.render_day_slots()

    def reload_availability_data(self):
        self.render_day_slots()
        QMessageBox.information(
            self, "Làm Mới", "Đã cập nhật lại lịch khả dụng từ máy chủ!"
        )

    def save_availability_changes(self):
        d_str = self.selected_avail_date.strftime("%d/%m/%Y")
        QMessageBox.information(
            self,
            "Lưu Thành Công",
            f"Đã lưu thành công cấu hình ca rảnh ngày {d_str} "
            "lên hệ thống đặt lịch hội viên!",
        )

    # =========================================================================
    # TAB 4: HỒ SƠ & ĐÁNH GIÁ (PtProfileSummaryWidget.razor)
    # =========================================================================
    def create_profile_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. Summary Card
        summary_card = QFrame()
        summary_card.setObjectName("cardFrame")
        s_layout = QVBoxLayout(summary_card)
        s_layout.setContentsMargins(20, 20, 20, 20)
        s_layout.setSpacing(16)

        header_row = QHBoxLayout()
        header_row.setSpacing(14)

        avatar_badge = QLabel("PT")
        avatar_badge.setFixedSize(48, 48)
        avatar_badge.setStyleSheet(
            "QLabel { background-color: rgba(192, 132, 252, 0.2); "
            "border: 1.5px solid #A855F7; border-radius: 24px; "
            "color: #C084FC; font-size: 16px; font-weight: bold; }"
        )
        avatar_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_row.addWidget(avatar_badge)

        name_box = QVBoxLayout()
        name_box.setSpacing(2)
        lbl_pt_title = QLabel(self.pt["name"])
        lbl_pt_title.setStyleSheet(
            "QLabel { color: #F8FAFC; font-size: 18px; font-weight: bold; "
            "background: transparent; border: none; }"
        )
        lbl_pt_code = QLabel("Mã HLV: PT-101 • Huấn luyện viên trưởng")
        lbl_pt_code.setStyleSheet(
            f"QLabel {{ color: {ACCENT_PRIMARY}; font-size: 12px; "
            "font-weight: 600; background: transparent; border: none; }"
        )
        name_box.addWidget(lbl_pt_title)
        name_box.addWidget(lbl_pt_code)
        header_row.addLayout(name_box)
        header_row.addStretch()

        badge_active = QLabel("  ● Đang hoạt động  ")
        badge_active.setFixedHeight(28)
        badge_active.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_active.setStyleSheet(
            "QLabel { background-color: rgba(6, 78, 59, 0.7); "
            "border: 1px solid #059669; border-radius: 14px; "
            "color: #34D399; font-size: 12px; font-weight: bold; "
            "padding: 0 12px; }"
        )
        header_row.addWidget(badge_active)
        s_layout.addLayout(header_row)

        # 4 DB metric cards in 2x2 grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(12)

        metrics = [
            (
                "👥 Học Viên Phụ Trách",
                f"{self.pt.get('active_students', 0)} người",
                "#38BDF8",
            ),
            (
                "⭐ Đánh Giá HLV",
                f"{self.pt['rating']} ★ (28 đánh giá)",
                "#FBBF24",
            ),
            ("🏋️ Đã Hoàn Thành", "142 ca", "#34D399"),
            ("📅 Ca Sắp Tới", "8 ca", "#C084FC"),
        ]

        for idx, (title, val, col) in enumerate(metrics):
            m_card = QFrame()
            m_card.setStyleSheet(
                "QFrame { background-color: #0F172A; border-radius: 8px; "
                "border: 1px solid #334155; }"
            )
            m_lay = QVBoxLayout(m_card)
            m_lay.setContentsMargins(14, 10, 14, 10)
            m_lay.setSpacing(4)

            lbl_m_t = QLabel(title)
            lbl_m_t.setStyleSheet(
                "QLabel { color: #94A3B8; font-size: 11px; "
                "background: transparent; border: none; }"
            )
            lbl_m_v = QLabel(val)
            lbl_m_v.setStyleSheet(
                f"QLabel {{ color: {col}; font-size: 18px; font-weight: bold; "
                "background: transparent; border: none; }"
            )
            m_lay.addWidget(lbl_m_t)
            m_lay.addWidget(lbl_m_v)
            metrics_grid.addWidget(m_card, idx // 2, idx % 2)

        s_layout.addLayout(metrics_grid)
        layout.addWidget(summary_card)

        # 2. Detailed Info Card
        detail_card = QFrame()
        detail_card.setObjectName("cardFrame")
        d_layout = QVBoxLayout(detail_card)
        d_layout.setContentsMargins(20, 20, 20, 20)
        d_layout.setSpacing(14)

        lbl_info_title = QLabel("THÔNG TIN HỒ SƠ CHI TIẾT")
        lbl_info_title.setStyleSheet(
            "QLabel { color: #F8FAFC; font-size: 14px; font-weight: bold; "
            "background: transparent; border: none; }"
        )
        d_layout.addWidget(lbl_info_title)

        rows = [
            ("Chuyên môn huấn luyện:", self.pt.get("specialty", "Huấn luyện viên cá nhân")),
            ("Kinh nghiệm & Bằng cấp:", self.pt.get("experience", "Đang cập nhật")),
            ("Số điện thoại liên hệ:", self.pt.get("phone", "Chưa cập nhật")),
            (
                "Địa chỉ email cá nhân:",
                self.pt.get("email", "pt.hung@gympro.vn"),
            ),
        ]
        for k, v in rows:
            r = QHBoxLayout()
            lbl_k = QLabel(k)
            lbl_k.setStyleSheet(
                "QLabel { color: #94A3B8; font-size: 13px; "
                "background: transparent; border: none; }"
            )
            r.addWidget(lbl_k)
            r.addStretch()

            lbl_v = QLabel(v)
            lbl_v.setStyleSheet(
                "QLabel { color: #F8FAFC; font-weight: 600; font-size: 13px; "
                "background: transparent; border: none; }"
            )
            r.addWidget(lbl_v)
            d_layout.addLayout(r)

        d_layout.addStretch()
        layout.addWidget(detail_card)

        return tab
