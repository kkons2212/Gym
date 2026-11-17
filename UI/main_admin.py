"""
Standalone Admin Application for Gym Management System.
Dedicated exclusively for Management & Receptionists (Desktop Portal).
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt6.QtWidgets import QApplication
from components.login_window import LoginWindow
from desktop_portal.main_window import DesktopMainWindow

class AdminApp:
    def __init__(self):
        self.login_win = None
        self.main_win = None
        
    def start(self):
        self.show_login()
        
    def show_login(self):
        if self.main_win:
            self.main_win.close()
            self.main_win = None
            
        self.login_win = LoginWindow(role="ADMIN")
        self.login_win.login_success.connect(self.show_main)
        self.login_win.show()
        
    def show_main(self, user_data):
        self.main_win = DesktopMainWindow(current_user=user_data.get("username", "Admin Hệ Thống"), role="ADMIN")
        self.main_win.switch_portal_requested.connect(self.show_login)
        self.main_win.show()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GymAdminManagement")
    app.setStyle("Fusion")
    
    qss_path = os.path.join(current_dir, "styles", "dark_theme.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
            
    runner = AdminApp()
    runner.start()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
