"""
Desktop Portal Main Window (1:1 with Desktop/MainWindow.xaml & MainPage.xaml).
Hosts the Navigation Sidebar and Stacked Pages for Admin/Receptionist operations.
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import pyqtSignal
from components.sidebar import Sidebar
from desktop_portal.views.checkin_counter_page import CheckInCounterPage
from desktop_portal.views.pos_billing_page import PosBillingPage
from desktop_portal.views.invoice_history_page import InvoiceHistoryPage
from desktop_portal.views.members_page import MembersPage
from desktop_portal.views.pt_schedule_page import PtSchedulePage
from desktop_portal.views.dashboard_page import DashboardPage
from desktop_portal.views.package_plans_page import PackagePlansPage
from desktop_portal.views.settings_page import SettingsPage

class DesktopMainWindow(QMainWindow):
    switch_portal_requested = pyqtSignal()
    
    def __init__(self, current_user="Admin Hệ Thống", role="ADMIN", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hệ Thống Quản Lý Phòng Tập Thể Thao • Gym Management System (Desktop Portal)")
        self.resize(1300, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Left Sidebar
        self.sidebar = Sidebar(current_user=current_user, role=role, parent=self)
        self.sidebar.page_changed.connect(self.switch_page)
        self.sidebar.logout_requested.connect(self.switch_portal_requested.emit)
        main_layout.addWidget(self.sidebar)
        
        # 2. Right Stacked Widget
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Page mappings
        self.pages = {
            "checkin": CheckInCounterPage(),
            "pos": PosBillingPage(),
            "invoices": InvoiceHistoryPage(),
            "members": MembersPage(),
            "schedule": PtSchedulePage(),
            "dashboard": DashboardPage(),
            "packages": PackagePlansPage(),
            "staff": SettingsPage(),
        }
        
        for key, page in self.pages.items():
            self.stack.addWidget(page)
            
        # Default active page
        self.sidebar.select_item("checkin")
        self.switch_page("checkin")
        
    def switch_page(self, key: str):
        if key in self.pages:
            self.stack.setCurrentWidget(self.pages[key])
