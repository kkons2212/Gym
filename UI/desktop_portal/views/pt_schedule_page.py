"""PT Schedule Page: Điều phối lịch huấn luyện viên.

Matches 1:1 with Desktop/Views/PtSchedulePage.xaml.
"""

from typing import Any, Dict, List

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from mock_data import MEMBERS, SCHEDULE_SLOTS, TRAINERS
from styles.color_tokens import (
    ACCENT_PRIMARY,
    STATUS_SUCCESS,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class PtSchedulePage(QWidget):
    """PT schedule coordinator, booking, and weekly calendar view."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # =============================================================
        # LEFT COLUMN (380px): PT Selector & Booking Guardrail
        # =============================================================
        filter_card = QFrame()
        filter_card.setObjectName("cardFrame")
        filter_card.setFixedWidth(380)
        f_layout = QVBoxLayout(filter_card)
        f_layout.setContentsMargins(20, 20, 20, 20)
        f_layout.setSpacing(12)

        lbl_title = QLabel("ĐIỀU PHỐI LỊCH HUẤN LUYỆN VIÊN")
        lbl_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        f_layout.addWidget(lbl_title)

        # 1. Huấn luyện viên phụ trách
        lbl_pt = QLabel("Huấn luyện viên phụ trách (*):")
        lbl_pt.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        f_layout.addWidget(lbl_pt)

        self.cbo_pt = QComboBox()
        self.cbo_pt.setFixedHeight(38)
        for pt in TRAINERS:
            self.cbo_pt.addItem(pt["name"], pt)
        self.cbo_pt.currentIndexChanged.connect(self.update_schedule)
        f_layout.addWidget(self.cbo_pt)

        # 2. Ngày dạy
        lbl_date = QLabel("Ngày dạy (*):")
        lbl_date.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        f_layout.addWidget(lbl_date)

        self.date_picker = QDateEdit()
        self.date_picker.setFixedHeight(38)
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        f_layout.addWidget(self.date_picker)

        # 3. Hội viên đặt ca
        lbl_member = QLabel("Hội viên đặt ca (*):")
        lbl_member.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        f_layout.addWidget(lbl_member)

        self.cbo_member = QComboBox()
        self.cbo_member.setFixedHeight(38)
        for m in MEMBERS:
            left_sessions = m.get("sessions_left", 0)
            self.cbo_member.addItem(
                f"{m['name']} • Còn {left_sessions} buổi", m
            )
        f_layout.addWidget(self.cbo_member)

        # 4. Khung giờ bắt đầu & kết thúc
        time_layout = QHBoxLayout()
        time_layout.setSpacing(12)

        start_col = QVBoxLayout()
        start_col.setSpacing(4)
        lbl_start = QLabel("Giờ bắt đầu:")
        lbl_start.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        start_col.addWidget(lbl_start)

        self.cbo_start_time = QComboBox()
        self.cbo_start_time.setFixedHeight(38)
        time_slots_start = [
            "06:00", "07:00", "08:00", "09:00", "10:00",
            "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
        ]
        self.cbo_start_time.addItems(time_slots_start)
        self.cbo_start_time.setCurrentText("07:00")
        start_col.addWidget(self.cbo_start_time)
        time_layout.addLayout(start_col)

        end_col = QVBoxLayout()
        end_col.setSpacing(4)
        lbl_end = QLabel("Giờ kết thúc:")
        lbl_end.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        end_col.addWidget(lbl_end)

        self.cbo_end_time = QComboBox()
        self.cbo_end_time.setFixedHeight(38)
        time_slots_end = [
            "07:00", "08:00", "09:00", "10:00", "11:00",
            "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00",
        ]
        self.cbo_end_time.addItems(time_slots_end)
        self.cbo_end_time.setCurrentText("08:00")
        end_col.addWidget(self.cbo_end_time)
        time_layout.addLayout(end_col)

        f_layout.addLayout(time_layout)
        f_layout.addStretch()

        btn_assign = QPushButton("Xếp Lịch HLV")
        btn_assign.setFixedHeight(44)
        btn_assign.setProperty("primary", True)
        btn_assign.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_assign.clicked.connect(self.book_schedule_slot)
        f_layout.addWidget(btn_assign)

        main_layout.addWidget(filter_card)

        # =============================================================
        # RIGHT COLUMN (Flex): Scheduled Slots List in cardFrame
        # =============================================================
        right_card = QFrame()
        right_card.setObjectName("cardFrame")
        r_layout = QVBoxLayout(right_card)
        r_layout.setContentsMargins(20, 20, 20, 20)
        r_layout.setSpacing(14)

        # Header Row
        right_header = QHBoxLayout()
        right_header.setSpacing(12)

        right_title_box = QVBoxLayout()
        right_title_box.setSpacing(4)
        lbl_table_title = QLabel("LỊCH TRÌNH DẠY THEO TUẦN")
        lbl_table_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        lbl_table_sub = QLabel(
            "Các ca tập đã xếp của HLV trong khung giờ 06:00 - 22:00"
        )
        lbl_table_sub.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px;"
        )
        right_title_box.addWidget(lbl_table_title)
        right_title_box.addWidget(lbl_table_sub)
        right_header.addLayout(right_title_box)
        right_header.addStretch()

        btn_trainers = QPushButton("Danh Sách HLV")
        btn_trainers.setFixedHeight(36)
        btn_trainers.setProperty("primary", True)
        btn_trainers.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_trainers.clicked.connect(self.open_trainer_list)
        right_header.addWidget(btn_trainers)

        btn_refresh = QPushButton("Tải Lại Lịch")
        btn_refresh.setFixedHeight(36)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.clicked.connect(self.update_schedule)
        right_header.addWidget(btn_refresh)
        r_layout.addLayout(right_header)

        # Timetable Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Khung Giờ", "Hội Viên Kèm", "Trạng Thái Ca", "Thao Tác"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(3, 170)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        r_layout.addWidget(self.table)

        main_layout.addWidget(right_card, 1)
        self.update_schedule()

    def update_schedule(self) -> None:
        pt_data = self.cbo_pt.currentData()
        if not pt_data:
            return

        filtered_slots = [
            s for s in SCHEDULE_SLOTS if s.get("pt") == pt_data["name"]
        ]
        self.table.setRowCount(len(filtered_slots))
        for row, slot in enumerate(filtered_slots):
            time_item = QTableWidgetItem(slot["time"])
            time_item.setForeground(QColor(ACCENT_PRIMARY))
            self.table.setItem(row, 0, time_item)

            member_name = (
                slot.get("member") or "(Trống - Sẵn sàng nhận học viên)"
            )
            self.table.setItem(row, 1, QTableWidgetItem(member_name))

            st_item = QTableWidgetItem(slot["status"])
            if slot["status"] == "Đã xác nhận":
                st_item.setForeground(QColor(STATUS_SUCCESS))
            else:
                st_item.setForeground(QColor(ACCENT_PRIMARY))
            self.table.setItem(row, 2, st_item)

            # Action Buttons: Chi Tiết & Xác Nhận
            btn_detail = QPushButton("Chi Tiết")
            btn_detail.setProperty("tableAction", True)
            btn_detail.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_detail.clicked.connect(
                lambda ch, s=slot: self.show_slot_detail(s)
            )

            btn_confirm = QPushButton("Xác Nhận")
            btn_confirm.setProperty("tableAction", True)
            btn_confirm.setProperty("actionVariant", "success")
            btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_confirm.clicked.connect(
                lambda ch, s=slot: self.confirm_slot(s)
            )

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            action_layout.addWidget(btn_detail)
            action_layout.addWidget(btn_confirm)
            self.table.setCellWidget(row, 3, action_widget)

    def book_schedule_slot(self) -> None:
        pt_data = self.cbo_pt.currentData()
        member_data = self.cbo_member.currentData()
        start = self.cbo_start_time.currentText()
        end = self.cbo_end_time.currentText()
        slot_date = self.date_picker.date().toString("dd/MM/yyyy")

        if not pt_data or not member_data:
            QMessageBox.warning(
                self, "Thiếu Dữ Liệu", "Vui lòng chọn HLV và hội viên!"
            )
            return

        time_range = f"{start} - {end}"
        SCHEDULE_SLOTS.append({
            "pt": pt_data["name"],
            "time": time_range,
            "member": member_data["name"],
            "status": "Đã xác nhận",
            "date": slot_date,
        })
        self.update_schedule()
        QMessageBox.information(
            self,
            "Xếp Lịch Thành Công",
            f"Đã xếp lịch dạy cho HLV {pt_data['name']}:\n"
            f"• Hội viên: {member_data['name']}\n"
            f"• Ngày: {slot_date}\n"
            f"• Khung giờ: {time_range}",
        )

    def confirm_slot(self, slot: Dict[str, Any]) -> None:
        slot["status"] = "Đã xác nhận"
        self.update_schedule()
        member_name = slot.get('member') or 'HLV'
        QMessageBox.information(
            self,
            "Xác Nhận Ca Tập",
            f"Đã xác nhận ca tập {slot['time']} của {member_name}!",
        )

    def show_slot_detail(self, slot: Dict[str, Any]) -> None:
        pt_name = slot.get("pt", "HLV")
        member = slot.get("member") or "Chưa có hội viên"
        QMessageBox.information(
            self,
            "Chi Tiết Buổi Tập",
            f"Khung giờ: {slot['time']}\n"
            f"Huấn luyện viên: {pt_name}\n"
            f"Hội viên: {member}\n"
            f"Trạng thái: {slot['status']}",
        )

    def open_trainer_list(self) -> None:
        info_lines: List[str] = []
        for t in TRAINERS:
            info_lines.append(
                f"• {t['name']} - Chuyên môn: {t['specialty']} ({t['rating']} ⭐)"
            )
        msg_content = (
            "Danh sách HLV phụ trách tại trung tâm:\n\n"
            + "\n".join(info_lines)
        )
        QMessageBox.information(
            self,
            "Danh Sách Huấn Luyện Viên",
            msg_content,
        )
