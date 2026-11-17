"""
CheckIn Counter Page: Quầy điểm danh hội viên (1:1 with Desktop/Views/CheckInCounterPage.xaml).
Features: Webcam scanner preview / simulation, manual code lookup, member card preview, check-in history table.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFrame, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2
from datetime import datetime
from styles.color_tokens import (
    TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, LAYER_BG, 
    BORDER_SUBTLE, ACCENT_PRIMARY, STATUS_SUCCESS, STATUS_DANGER
)
from mock_data import MEMBERS, CHECKIN_LOGS

class CheckInCounterPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.is_camera_on = False
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # LEFT COLUMN (40%): Camera Scanner & Manual Input
        left_col = QVBoxLayout()
        left_col.setSpacing(16)
        
        # Camera Card
        cam_card = QFrame()
        cam_card.setObjectName("cardFrame")
        cam_layout = QVBoxLayout(cam_card)
        cam_layout.setContentsMargins(16, 16, 16, 16)
        cam_layout.setSpacing(12)
        
        cam_header = QHBoxLayout()
        lbl_cam_title = QLabel("📷  WEBCAM QUÉT MÃ QR")
        lbl_cam_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold;")
        
        self.btn_toggle_cam = QPushButton("Bật Camera")
        self.btn_toggle_cam.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_cam.setStyleSheet(f"background-color: {ACCENT_PRIMARY}; color: white; padding: 4px 12px;")
        self.btn_toggle_cam.clicked.connect(self.toggle_camera)
        
        cam_header.addWidget(lbl_cam_title)
        cam_header.addStretch()
        cam_header.addWidget(self.btn_toggle_cam)
        cam_layout.addLayout(cam_header)
        
        # Video Display Viewport
        self.video_label = QLabel("Camera đang tắt\nBấm 'Bật Camera' để quét QR thẻ hội viên")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setFixedHeight(240)
        self.video_label.setStyleSheet(f"""
            background-color: #0F172A;
            border: 2px dashed {BORDER_SUBTLE};
            border-radius: 8px;
            color: {TEXT_SECONDARY};
            font-size: 12px;
        """)
        cam_layout.addWidget(self.video_label)
        
        # Manual Code Lookup Card
        lookup_card = QFrame()
        lookup_card.setObjectName("cardFrame")
        lookup_layout = QVBoxLayout(lookup_card)
        lookup_layout.setContentsMargins(16, 16, 16, 16)
        lookup_layout.setSpacing(10)
        
        lbl_manual = QLabel("TRA CỨU THỦ CÔNG (SĐT / MÃ HV)")
        lbl_manual.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: bold;")
        lookup_layout.addWidget(lbl_manual)
        
        input_row = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Nhập SĐT hoặc Mã HV (vd: 0987654321, HV-1001)...")
        self.txt_search.returnPressed.connect(self.do_checkin)
        
        btn_checkin = QPushButton("Điểm Danh (Enter)")
        btn_checkin.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_checkin.setProperty("primary", True)
        btn_checkin.clicked.connect(self.do_checkin)
        
        input_row.addWidget(self.txt_search)
        input_row.addWidget(btn_checkin)
        lookup_layout.addLayout(input_row)
        
        left_col.addWidget(cam_card)
        left_col.addWidget(lookup_card)
        left_col.addStretch()
        
        main_layout.addLayout(left_col, 4)
        
        # RIGHT COLUMN (60%): Member Card Preview & Today Logs
        right_col = QVBoxLayout()
        right_col.setSpacing(16)
        
        # Member Preview Card
        self.preview_card = QFrame()
        self.preview_card.setObjectName("cardFrame")
        prev_layout = QVBoxLayout(self.preview_card)
        prev_layout.setContentsMargins(20, 20, 20, 20)
        prev_layout.setSpacing(12)
        
        prev_header = QHBoxLayout()
        self.lbl_member_name = QLabel("Nguyễn Hoàng Nam")
        self.lbl_member_name.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        
        self.badge_status = QLabel("  ĐANG HOẠT ĐỘNG  ")
        self.badge_status.setStyleSheet("color: #4ADE80; background-color: #064E3B; border-radius: 4px; font-size: 11px; font-weight: bold; padding: 4px;")
        
        prev_header.addWidget(self.lbl_member_name)
        prev_header.addStretch()
        prev_header.addWidget(self.badge_status)
        prev_layout.addLayout(prev_header)
        
        # Details grid
        details_layout = QHBoxLayout()
        self.lbl_code = QLabel("Mã HV: HV-1001")
        self.lbl_code.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        self.lbl_pkg = QLabel("Gói: VIP Platinum 12 Tháng")
        self.lbl_pkg.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 12px; font-weight: bold;")
        
        self.lbl_expiry = QLabel("Hạn: 15/01/2027")
        self.lbl_expiry.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        details_layout.addWidget(self.lbl_code)
        details_layout.addWidget(self.lbl_pkg)
        details_layout.addWidget(self.lbl_expiry)
        details_layout.addStretch()
        prev_layout.addLayout(details_layout)
        
        right_col.addWidget(self.preview_card)
        
        # Today's Logs Table
        lbl_log_title = QLabel("NHẬT KÝ ĐIỂM DANH HÔM NAY")
        lbl_log_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold;")
        right_col.addWidget(lbl_log_title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Thời Gian", "Mã HV", "Họ Tên Hội Viên", "Phương Thức", "Trạng Thái"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.populate_logs()
        right_col.addWidget(self.table)
        
        main_layout.addLayout(right_col, 6)
        
    def populate_logs(self):
        self.table.setRowCount(len(CHECKIN_LOGS))
        for row, item in enumerate(CHECKIN_LOGS):
            self.table.setItem(row, 0, QTableWidgetItem(item["time"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["code"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["name"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["method"]))
            
            status_item = QTableWidgetItem(item["status"])
            if item["status"] == "Hợp Lệ":
                status_item.setForeground(Qt.GlobalColor.green)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 4, status_item)
            
    def do_checkin(self):
        text = self.txt_search.text().strip()
        if not text:
            QMessageBox.warning(self, "Lỗi Nhập Liệu", "Vui lòng nhập Mã hội viên hoặc Số điện thoại!")
            return
            
        found = None
        for m in MEMBERS:
            if text.lower() in m["code"].lower() or text in m["phone"]:
                found = m
                break
                
        if found:
            self.lbl_member_name.setText(found["name"])
            self.lbl_code.setText(f"Mã HV: {found['code']}")
            self.lbl_pkg.setText(f"Gói: {found['package_name']}")
            self.lbl_expiry.setText(f"Hạn: {found['expiry_date']}")
            
            is_valid = found["status"] == "Đang hoạt động"
            self.badge_status.setText(f"  {found['status'].upper()}  ")
            if is_valid:
                self.badge_status.setStyleSheet("color: #4ADE80; background-color: #064E3B; border-radius: 4px; font-size: 11px; font-weight: bold; padding: 4px;")
            else:
                self.badge_status.setStyleSheet("color: #F87171; background-color: #7F1D1D; border-radius: 4px; font-size: 11px; font-weight: bold; padding: 4px;")
                
            # Prepend to log table
            now_str = datetime.now().strftime("%H:%M:%S")
            CHECKIN_LOGS.insert(0, {
                "time": now_str, 
                "code": found["code"], 
                "name": found["name"], 
                "method": "Nhập Mã", 
                "status": "Hợp Lệ" if is_valid else found["status"]
            })
            self.populate_logs()
            self.txt_search.clear()
        else:
            QMessageBox.critical(self, "Không Tìm Thấy", f"Không tìm thấy hội viên nào khớp với '{text}'!")

    def toggle_camera(self):
        if not self.is_camera_on:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                QMessageBox.warning(self, "Camera", "Không tìm thấy webcam kết nối! Đang chạy chế độ mô phỏng.")
                self.video_label.setText("Mô phỏng máy quét QR tự động kích hoạt")
                return
            self.is_camera_on = True
            self.btn_toggle_cam.setText("Tắt Camera")
            self.btn_toggle_cam.setStyleSheet("background-color: #DC2626; color: white;")
            self.timer.start(30)
        else:
            self.is_camera_on = False
            self.timer.stop()
            if self.camera:
                self.camera.release()
                self.camera = None
            self.btn_toggle_cam.setText("Bật Camera")
            self.btn_toggle_cam.setStyleSheet(f"background-color: {ACCENT_PRIMARY}; color: white;")
            self.video_label.setText("Camera đã dừng")

    def update_frame(self):
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(q_img).scaled(
                    self.video_label.width(), self.video_label.height(), Qt.AspectRatioMode.KeepAspectRatio
                ))
