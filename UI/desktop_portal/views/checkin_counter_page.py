"""Live QR/manual check-in counter with camera and database-backed history."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional

import cv2
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from constants import CheckInMethod, CheckInStatus
from exceptions import CheckInDeniedException, DatabaseTransactionException
from repositories.check_in_repository import CheckInRepository
from services.checkin_service import CheckInService
from styles.color_tokens import (
    BORDER_SUBTLE,
    INPUT_BG,
    STATUS_DANGER,
    STATUS_DANGER_BG,
    STATUS_SUCCESS,
    STATUS_SUCCESS_BG,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class CheckInCounterPage(QWidget):
    """Run member check-ins and show persisted outcomes."""

    def __init__(
        self,
        parent=None,
        checkin_service: Optional[CheckInService] = None,
        check_in_repo: Optional[CheckInRepository] = None,
        camera_factory: Optional[Callable[[], Any]] = None,
        qr_detector: Optional[Any] = None,
    ) -> None:
        super().__init__(parent)
        self.checkin_service = checkin_service or CheckInService()
        self.check_in_repo = check_in_repo or CheckInRepository()
        self.camera_factory = camera_factory or (lambda: cv2.VideoCapture(0))
        self.qr_detector = qr_detector or cv2.QRCodeDetector()
        self.camera = None
        self.is_camera_on = False
        self._last_scan_key = ""
        self._last_scan_at = 0.0
        self._display_methods: Dict[str, str] = {}

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        left_column = QVBoxLayout()
        left_column.setSpacing(16)

        camera_card = QFrame()
        camera_card.setObjectName("cardFrame")
        camera_layout = QVBoxLayout(camera_card)
        camera_header = QHBoxLayout()
        camera_title = QLabel("WEBCAM QUÉT MÃ QR")
        camera_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold;"
        )
        self.btn_toggle_cam = QPushButton("Bật camera")
        self.btn_toggle_cam.setProperty("primary", True)
        self.btn_toggle_cam.clicked.connect(self.toggle_camera)
        camera_header.addWidget(camera_title)
        camera_header.addStretch()
        camera_header.addWidget(self.btn_toggle_cam)
        camera_layout.addLayout(camera_header)

        self.video_label = QLabel("Camera đang tắt")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setFixedHeight(240)
        self.video_label.setStyleSheet(
            f"background-color: {INPUT_BG}; "
            f"border: 2px dashed {BORDER_SUBTLE}; "
            "border-radius: 8px;"
        )
        camera_layout.addWidget(self.video_label)
        left_column.addWidget(camera_card)

        lookup_card = QFrame()
        lookup_card.setObjectName("cardFrame")
        lookup_layout = QVBoxLayout(lookup_card)
        lookup_layout.addWidget(
            QLabel("TRA CỨU THỦ CÔNG (SĐT / MÃ HV)")
        )
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        self.txt_search = QLineEdit()
        self.txt_search.setFixedHeight(38)
        self.txt_search.setPlaceholderText(
            "Nhập mã hội viên hoặc SĐT (USR001 / 0901234567)"
        )
        self.txt_search.returnPressed.connect(self.do_checkin)
        self.btn_checkin = QPushButton("Điểm Danh")
        self.btn_checkin.setFixedHeight(38)
        self.btn_checkin.setProperty("primary", True)
        self.btn_checkin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_checkin.clicked.connect(self.do_checkin)
        input_row.addWidget(self.txt_search, 1)
        input_row.addWidget(self.btn_checkin)
        lookup_layout.addLayout(input_row)
        left_column.addWidget(lookup_card)
        left_column.addStretch()
        main_layout.addLayout(left_column, 4)

        right_column = QVBoxLayout()
        right_column.setSpacing(16)

        self.status_card = QFrame()
        self.status_card.setObjectName("cardFrame")
        self.status_card.setProperty("checkinStatus", "neutral")
        status_layout = QVBoxLayout(self.status_card)
        self.status_title = QLabel("SẴN SÀNG ĐIỂM DANH")
        self.status_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;"
        )
        self.status_message = QLabel(
            "Quét mã QR hoặc nhập thông tin hội viên."
        )
        self.status_message.setWordWrap(True)
        self.status_message.setStyleSheet(f"color: {TEXT_SECONDARY};")
        status_layout.addWidget(self.status_title)
        status_layout.addWidget(self.status_message)
        right_column.addWidget(self.status_card)

        self.preview_card = QFrame()
        self.preview_card.setObjectName("cardFrame")
        preview_layout = QVBoxLayout(self.preview_card)
        header = QHBoxLayout()
        self.lbl_member_name = QLabel("—")
        self.lbl_member_name.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;"
        )
        self.badge_status = QLabel("—")
        header.addWidget(self.lbl_member_name)
        header.addStretch()
        header.addWidget(self.badge_status)
        preview_layout.addLayout(header)

        details = QHBoxLayout()
        self.lbl_code = QLabel("Mã HV: —")
        self.lbl_pkg = QLabel("Gói: —")
        self.lbl_expiry = QLabel("Hạn: —")
        for label in (self.lbl_code, self.lbl_pkg, self.lbl_expiry):
            label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
            details.addWidget(label)
        details.addStretch()
        preview_layout.addLayout(details)
        right_column.addWidget(self.preview_card)

        log_title = QLabel("NHẬT KÝ ĐIỂM DANH HÔM NAY")
        log_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold;"
        )
        right_column.addWidget(log_title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            [
                "Thời gian",
                "Mã HV",
                "Họ tên hội viên",
                "Phương thức",
                "Trạng thái",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeaderItem(3).setToolTip(
            "Phương thức không được lưu trong CheckInLog; chỉ lượt hiện tại "
            "còn thông tin từ thao tác quầy."
        )
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        right_column.addWidget(self.table)
        main_layout.addLayout(right_column, 6)
        self._load_today_logs()

    def _set_status(
        self, title: str, message: str, success: Optional[bool]
    ) -> None:
        self.status_title.setText(title)
        self.status_message.setText(message)
        if success is True:
            status = "success"
        elif success is False:
            status = "denied"
        else:
            status = "neutral"
        self.status_card.setProperty("checkinStatus", status)
        self.status_card.style().unpolish(self.status_card)
        self.status_card.style().polish(self.status_card)

        if success is True:
            badge_text = "HỢP LỆ"
            badge_color = STATUS_SUCCESS
            badge_background = STATUS_SUCCESS_BG
        elif success is False:
            badge_text = "TỪ CHỐI"
            badge_color = STATUS_DANGER
            badge_background = STATUS_DANGER_BG
        else:
            badge_text = ""
            badge_color = TEXT_SECONDARY
            badge_background = "transparent"
        self.badge_status.setText(badge_text)
        self.badge_status.setStyleSheet(
            f"color: {badge_color}; background-color: {badge_background}; "
            "border-radius: 4px; font-size: 11px; "
            "font-weight: bold; padding: 4px;"
        )
        self.status_title.setStyleSheet(
            f"color: {badge_color}; font-size: 16px; font-weight: bold;"
        )
        self.status_message.setStyleSheet(f"color: {badge_color};")

    def _set_member_preview(self, result: Dict[str, Any]) -> None:
        self.lbl_member_name.setText(result.get("full_name") or "—")
        self.lbl_code.setText(f"Mã HV: {result.get('username') or '—'}")
        self.lbl_pkg.setText(f"Gói: {result.get('plan_name') or '—'}")
        end_date = result.get("end_date")
        expiry = (
            end_date.strftime("%Y-%m-%d")
            if hasattr(end_date, "strftime")
            else str(end_date or "—")
        )
        self.lbl_expiry.setText(f"Hạn: {expiry}")

    def _clear_member_preview(self) -> None:
        self.lbl_member_name.setText("—")
        self.lbl_code.setText("Mã HV: —")
        self.lbl_pkg.setText("Gói: —")
        self.lbl_expiry.setText("Hạn: —")
        self.badge_status.clear()
        self.badge_status.setStyleSheet("")

    def do_checkin(self) -> None:
        key = self.txt_search.text().strip()
        if not key:
            self._set_status(
                "THIẾU THÔNG TIN",
                "Vui lòng nhập mã hội viên hoặc số điện thoại.",
                None,
            )
            self.txt_search.setFocus()
            return
        if self._process_checkin(key, CheckInMethod.MANUAL.value):
            self.txt_search.clear()

    def _process_checkin(self, key: str, method: str) -> bool:
        try:
            result = self.checkin_service.process_checkin(key, method=method)
        except CheckInDeniedException as err:
            self._clear_member_preview()
            if err.username:
                self.lbl_code.setText(f"Mã HV / tra cứu: {err.username}")
            self._set_status(
                "ĐIỂM DANH BỊ TỪ CHỐI", err.reason, False
            )
            if err.check_in_id:
                self._display_methods[err.check_in_id] = (
                    "Nhập mã" if method == CheckInMethod.MANUAL.value else "QR"
                )
                self._load_today_logs()
            return True
        except DatabaseTransactionException as err:
            self._set_status(
                "LỖI CƠ SỞ DỮ LIỆU", str(err), None
            )
            return False
        else:
            self._set_member_preview(result)
            remaining = result.get("remaining_sessions")
            remaining_text = (
                str(remaining) if remaining is not None else "không giới hạn"
            )
            self._set_status(
                "ĐIỂM DANH THÀNH CÔNG",
                f"Chào {result.get('full_name') or result.get('username')}! "
                f"Còn {remaining_text} lượt.",
                True,
            )
            self._display_methods[result["check_in_id"]] = (
                "Nhập mã" if method == CheckInMethod.MANUAL.value else "QR"
            )
            self._load_today_logs()
            return True

    def _load_today_logs(self) -> None:
        try:
            logs = self.check_in_repo.get_today_logs()
        except DatabaseTransactionException as err:
            self._set_status(
                "KHÔNG TẢI ĐƯỢC NHẬT KÝ", str(err), None
            )
            return

        self.table.setRowCount(len(logs))
        for row_index, record in enumerate(logs):
            timestamp = record.get("check_in_at")
            time_text = (
                timestamp.strftime("%H:%M:%S")
                if hasattr(timestamp, "strftime")
                else str(timestamp or "—")
            )
            status = record.get("status")
            status_text = (
                "Hợp lệ"
                if status == CheckInStatus.SUCCESS.value
                else "Từ chối"
            )
            values = (
                time_text,
                record.get("username") or "—",
                record.get("full_name") or record.get("username") or "—",
                self._display_methods.get(record.get("check_in_id"), "—"),
                status_text,
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column == 4:
                    item.setForeground(
                        QColor(STATUS_SUCCESS)
                        if status == CheckInStatus.SUCCESS.value
                        else QColor(STATUS_DANGER)
                    )
                self.table.setItem(row_index, column, item)

    def toggle_camera(self) -> None:
        if self.is_camera_on:
            self._stop_camera()
            self.video_label.setText("Camera đã dừng")
            return

        camera = self.camera_factory()
        if camera is None or not camera.isOpened():
            if camera is not None:
                camera.release()
            self._set_status(
                "KHÔNG MỞ ĐƯỢC CAMERA",
                "Kiểm tra webcam hoặc tiếp tục bằng cách nhập mã thủ công.",
                None,
            )
            return

        self.camera = camera
        self.is_camera_on = True
        self.btn_toggle_cam.setText("Tắt camera")
        self.btn_toggle_cam.setProperty("primary", False)
        self.btn_toggle_cam.setProperty("danger", True)
        self.btn_toggle_cam.style().unpolish(self.btn_toggle_cam)
        self.btn_toggle_cam.style().polish(self.btn_toggle_cam)
        self.timer.start(30)

    def _stop_camera(self) -> None:
        self.timer.stop()
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.is_camera_on = False
        self.btn_toggle_cam.setText("Bật camera")
        self.btn_toggle_cam.setProperty("danger", False)
        self.btn_toggle_cam.setProperty("primary", True)
        self.btn_toggle_cam.style().unpolish(self.btn_toggle_cam)
        self.btn_toggle_cam.style().polish(self.btn_toggle_cam)

    def update_frame(self) -> None:
        if self.camera is None or not self.camera.isOpened():
            return
        success, frame = self.camera.read()
        if not success:
            self.video_label.setText("Không đọc được hình ảnh từ camera")
            return

        try:
            decoded, _, _ = self.qr_detector.detectAndDecode(frame)
        except cv2.error as err:
            self._set_status("LỖI QUÉT QR", str(err), None)
            return
        if decoded:
            now = time.monotonic()
            is_new_scan = decoded != self._last_scan_key
            debounce_elapsed = now - self._last_scan_at >= 2.0
            if is_new_scan or debounce_elapsed:
                self._last_scan_key = decoded
                self._last_scan_at = now
                self._process_checkin(decoded, CheckInMethod.QR_SCAN.value)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_frame.shape
        image = QImage(
            rgb_frame.data,
            width,
            height,
            channels * width,
            QImage.Format.Format_RGB888,
        ).copy()
        self.video_label.setPixmap(
            QPixmap.fromImage(image).scaled(
                self.video_label.width(),
                self.video_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
        )

    def closeEvent(self, event) -> None:
        self._stop_camera()
        super().closeEvent(event)
