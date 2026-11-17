"""
Dashboard Page: Báo cáo & Thống kê doanh thu (1:1 with Desktop/Views/DashboardPage.xaml).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from styles.color_tokens import (
    TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, LAYER_BG, 
    BORDER_SUBTLE, ACCENT_PRIMARY
)
from components.stat_card import StatCard
from components.chart_widget import ChartWidget

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Header Row
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        lbl_title = QLabel("BÁO CÁO & THỐNG KÊ DOANH THU")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        
        lbl_desc = QLabel("Tổng quan chỉ số kinh doanh, tỷ trọng gói tập và lưu lượng check-in theo giờ")
        lbl_desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_desc)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        
        # Action Buttons (Export Excel & PDF)
        btn_excel = QPushButton("  📊  Xuất Excel (.xlsx)")
        btn_excel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_excel.setFixedHeight(38)
        btn_excel.clicked.connect(lambda: QMessageBox.information(self, "Xuất Báo Cáo", "Đã xuất dữ liệu báo cáo ra file Excel thành công!"))
        
        btn_pdf = QPushButton("  📄  Xuất PDF (.pdf)")
        btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pdf.setFixedHeight(38)
        btn_pdf.clicked.connect(lambda: QMessageBox.information(self, "Xuất Báo Cáo", "Đã xuất báo cáo tổng hợp ra file PDF thành công!"))
        
        header_layout.addWidget(btn_excel)
        header_layout.addWidget(btn_pdf)
        main_layout.addLayout(header_layout)
        
        # Scroll Area for Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. 4 KPI Stat Cards
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(16)
        
        card_rev = StatCard("Doanh Thu Tháng Này", "184,500,000 đ", "Tăng 18.2% so với tháng trước", "+18.2%", True)
        card_mem = StatCard("Hội Viên Đang Hoạt Động", "1,248", "64 hội viên đăng ký mới tuần này", "+5.4%", True)
        card_pt = StatCard("Buổi PT Hoàn Tất", "382 buổi", "Tỷ lệ tham gia đúng hẹn 98.4%", "+3.1%", True)
        card_in = StatCard("Lượt Check-in Hôm Nay", "142 lượt", "Đạt 85% công suất tối đa phòng tập", "Ổn định", True)
        
        kpi_grid.addWidget(card_rev, 0, 0)
        kpi_grid.addWidget(card_mem, 0, 1)
        kpi_grid.addWidget(card_pt, 0, 2)
        kpi_grid.addWidget(card_in, 0, 3)
        content_layout.addLayout(kpi_grid)
        
        # 2. Charts Row (Peak Hours & Revenue Distribution)
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)
        
        # Peak Hours Chart
        self.chart_peak = ChartWidget(width=6, height=3.5)
        hours = [f"{h:02d}h" for h in range(6, 22)]
        checkins = [12, 28, 45, 30, 18, 15, 20, 22, 35, 58, 82, 95, 70, 48, 25, 10]
        self.chart_peak.plot_peak_hours(hours, checkins)
        charts_row.addWidget(self.chart_peak, 6)
        
        # Revenue Breakdown Pie Chart
        self.chart_pie = ChartWidget(width=4, height=3.5)
        pkgs = ["VIP Platinum", "PT 1-1", "Standard 3M", "Standard 1M", "Khác"]
        shares = [42, 28, 16, 10, 4]
        self.chart_pie.plot_revenue_breakdown(pkgs, shares)
        charts_row.addWidget(self.chart_pie, 4)
        
        content_layout.addLayout(charts_row)
        
        # 3. Quick Summary Table Card
        summary_card = QFrame()
        summary_card.setObjectName("cardFrame")
        sum_layout = QVBoxLayout(summary_card)
        sum_layout.setContentsMargins(16, 16, 16, 16)
        sum_layout.setSpacing(10)
        
        sum_title = QLabel("TỔNG KẾT VẬN HÀNH THÁNG HIỆN TẠI")
        sum_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px; font-weight: bold;")
        sum_layout.addWidget(sum_title)
        
        metrics = [
            ("Tổng số hóa đơn giao dịch:", "342 hóa đơn"),
            ("Giá trị đơn hàng trung bình (AOV):", "1,850,000 đ"),
            ("Tỷ lệ gia hạn hợp đồng (Renewal rate):", "78.6%"),
            ("Đánh giá trung bình từ học viên PT:", "4.92 / 5.0 ⭐ (186 lượt đánh giá)"),
        ]
        
        for k, v in metrics:
            row = QHBoxLayout()
            lbl_k = QLabel(k)
            lbl_k.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: bold;")
            row.addWidget(lbl_k)
            row.addStretch()
            row.addWidget(lbl_v)
            sum_layout.addLayout(row)
            
        content_layout.addWidget(summary_card)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
