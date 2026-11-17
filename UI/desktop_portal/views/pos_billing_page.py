"""
POS Billing Page: Bán gói dịch vụ & thanh toán POS (1:1 with Desktop/Views/PosBillingPage.xaml).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QFrame, QScrollArea, QComboBox, QMessageBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from datetime import datetime
from styles.color_tokens import (
    TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, LAYER_BG, 
    BORDER_SUBTLE, ACCENT_PRIMARY, STATUS_SUCCESS
)
from mock_data import PACKAGES, MEMBERS, INVOICES
from desktop_portal.dialogs.vietqr_dialog import VietQrPaymentDialog

class PosBillingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_package = None
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # LEFT COLUMN (60%): Package Catalog
        left_col = QVBoxLayout()
        left_col.setSpacing(14)
        
        # Title & Search
        lbl_title = QLabel("DANH MỤC GÓI TẬP NIÊM YẾT")
        lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold;")
        
        lbl_desc = QLabel("Bấm chọn gói tập để nạp vào hóa đơn thanh toán (F2)")
        lbl_desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("Tìm kiếm gói tập theo tên hoặc từ khóa...")
        self.txt_filter.textChanged.connect(self.filter_packages)
        
        left_col.addWidget(lbl_title)
        left_col.addWidget(lbl_desc)
        left_col.addWidget(self.txt_filter)
        
        # Scrollable Packages List
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.pkg_container = QWidget()
        self.pkg_layout = QVBoxLayout(self.pkg_container)
        self.pkg_layout.setSpacing(12)
        self.pkg_layout.setContentsMargins(0, 0, 0, 0)
        
        self.render_packages(PACKAGES)
        scroll.setWidget(self.pkg_container)
        left_col.addWidget(scroll)
        
        main_layout.addLayout(left_col, 6)
        
        # RIGHT COLUMN (40%): Checkout Panel & Invoice Details
        right_col = QVBoxLayout()
        right_col.setSpacing(16)
        
        checkout_card = QFrame()
        checkout_card.setObjectName("cardFrame")
        c_layout = QVBoxLayout(checkout_card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(14)
        
        c_title = QLabel("HÓA ĐƠN THANH TOÁN")
        c_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        c_layout.addWidget(c_title)
        
        # Member Selection
        lbl_mem_sel = QLabel("Hội Viên Thanh Toán:")
        lbl_mem_sel.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        c_layout.addWidget(lbl_mem_sel)
        
        self.cbo_member = QComboBox()
        self.cbo_member.addItem("-- Khách Hàng Mới / Vãng Lai --")
        for m in MEMBERS:
            self.cbo_member.addItem(f"{m['name']} ({m['code']})", m)
        c_layout.addWidget(self.cbo_member)
        
        # Selected Package Summary
        self.summary_box = QFrame()
        self.summary_box.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 12px;")
        sum_layout = QVBoxLayout(self.summary_box)
        sum_layout.setSpacing(6)
        
        self.lbl_sum_pkg = QLabel("Chưa chọn gói tập nào")
        self.lbl_sum_pkg.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold;")
        
        self.lbl_sum_price = QLabel("Tổng tiền: 0 VNĐ")
        self.lbl_sum_price.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 18px; font-weight: bold;")
        
        sum_layout.addWidget(self.lbl_sum_pkg)
        sum_layout.addWidget(self.lbl_sum_price)
        c_layout.addWidget(self.summary_box)
        
        # Payment Method Options
        lbl_method = QLabel("Phương Thức Thanh Toán:")
        lbl_method.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")
        c_layout.addWidget(lbl_method)
        
        self.method_group = QButtonGroup(self)
        self.rb_vietqr = QRadioButton("Mã QR Ngân Hàng (VietQR)")
        self.rb_vietqr.setChecked(True)
        self.rb_cash = QRadioButton("Tiền mặt tại quầy (Cash)")
        self.rb_card = QRadioButton("Quẹt thẻ ngân hàng (POS)")
        
        self.method_group.addButton(self.rb_vietqr)
        self.method_group.addButton(self.rb_cash)
        self.method_group.addButton(self.rb_card)
        
        c_layout.addWidget(self.rb_vietqr)
        c_layout.addWidget(self.rb_cash)
        c_layout.addWidget(self.rb_card)
        
        c_layout.addStretch()
        
        # Checkout Button
        self.btn_pay = QPushButton("Xác Nhận & Thanh Toán (F9)")
        self.btn_pay.setFixedHeight(44)
        self.btn_pay.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pay.setProperty("primary", True)
        self.btn_pay.clicked.connect(self.process_payment)
        c_layout.addWidget(self.btn_pay)
        
        right_col.addWidget(checkout_card)
        main_layout.addLayout(right_col, 4)
        
    def render_packages(self, pkg_list):
        # Clear layout
        while self.pkg_layout.count():
            item = self.pkg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for pkg in pkg_list:
            card = QFrame()
            card.setObjectName("cardFrame")
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.setStyleSheet(f"""
                QFrame#cardFrame {{
                    background-color: {CARD_BG};
                    border: 1px solid {BORDER_SUBTLE};
                    border-radius: 12px;
                    padding: 14px;
                }}
                QFrame#cardFrame:hover {{
                    border-color: {ACCENT_PRIMARY};
                    background-color: #27354A;
                }}
            """)
            
            c_layout = QVBoxLayout(card)
            c_layout.setSpacing(6)
            
            top_row = QHBoxLayout()
            lbl_name = QLabel(pkg["name"])
            lbl_name.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
            
            lbl_badge = QLabel(pkg["badge"])
            lbl_badge.setStyleSheet("color: #38BDF8; background-color: rgba(14, 165, 233, 0.15); border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: bold;")
            
            top_row.addWidget(lbl_name)
            top_row.addStretch()
            top_row.addWidget(lbl_badge)
            c_layout.addLayout(top_row)
            
            lbl_desc = QLabel(pkg["benefits"])
            lbl_desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
            lbl_desc.setWordWrap(True)
            c_layout.addWidget(lbl_desc)
            
            bottom_row = QHBoxLayout()
            lbl_dur = QLabel(f"Thời hạn: {pkg['duration_days']} ngày")
            lbl_dur.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
            
            lbl_price = QLabel(f"{pkg['price']:,.0f} đ")
            lbl_price.setStyleSheet(f"color: {ACCENT_PRIMARY}; font-size: 16px; font-weight: bold;")
            
            bottom_row.addWidget(lbl_dur)
            bottom_row.addStretch()
            bottom_row.addWidget(lbl_price)
            c_layout.addLayout(bottom_row)
            
            # Make card clickable
            card.mousePressEvent = lambda e, p=pkg: self.select_package(p)
            self.pkg_layout.addWidget(card)
            
        self.pkg_layout.addStretch()

    def filter_packages(self, text):
        filtered = [p for p in PACKAGES if text.lower() in p["name"].lower() or text.lower() in p["benefits"].lower()]
        self.render_packages(filtered)

    def select_package(self, pkg):
        self.selected_package = pkg
        self.lbl_sum_pkg.setText(f"Gói chọn: {pkg['name']}")
        self.lbl_sum_price.setText(f"Tổng tiền: {pkg['price']:,.0f} VNĐ")

    def process_payment(self):
        if not self.selected_package:
            QMessageBox.warning(self, "Chưa Chọn Gói", "Vui lòng chọn 1 gói tập từ danh mục bên trái!")
            return
            
        order_code = f"HD-{datetime.now().strftime('%Y%m%d%H%M')}"
        mem_idx = self.cbo_member.currentIndex()
        mem_name = self.cbo_member.currentText() if mem_idx > 0 else "Khách Vãng Lai"
        
        if self.rb_vietqr.isChecked():
            dialog = VietQrPaymentDialog(self.selected_package["price"], order_code, self.selected_package["name"], self)
            if dialog.exec():
                self.record_invoice(order_code, mem_name, "VietQR Chuyển khoản")
        else:
            method = "Tiền mặt" if self.rb_cash.isChecked() else "Quẹt thẻ POS"
            self.record_invoice(order_code, mem_name, method)
            
    def record_invoice(self, order_code, mem_name, method):
        INVOICES.insert(0, {
            "code": order_code,
            "member_name": mem_name,
            "package_name": self.selected_package["name"],
            "amount": self.selected_package["price"],
            "payment_method": method,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "Đã thanh toán",
            "cashier": "Admin Lễ Tân"
        })
        QMessageBox.information(self, "Thành Công", f"Đã xuất hóa đơn {order_code} và kích hoạt gói tập thành công!")
