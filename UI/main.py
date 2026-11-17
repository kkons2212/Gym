"""
Main Application Entry Point for Gym Management System.
Brings together Desktop Portal and Web Portals (Member & PT) in Python (PyQt6).
"""
import sys
import os
import argparse

# Add UI folder to sys.path so modules can import styles, components, etc.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from desktop_portal.views.login_page import LoginDialog
from desktop_portal.main_window import DesktopMainWindow
from web_portal.member_portal_window import MemberPortalWindow
from web_portal.pt_portal_window import PtPortalWindow

class GymAppManager:
    def __init__(self, app: QApplication, initial_role: str = None):
        self.app = app
        self.current_window = None
        self.initial_role = initial_role
        
    def start(self):
        if self.initial_role:
            self.launch_portal(self.initial_role.upper())
        else:
            self.show_login()
            
    def show_login(self):
        if self.current_window:
            self.current_window.close()
            self.current_window = None
            
        dlg = LoginDialog()
        if dlg.exec():
            role = dlg.selected_role or "ADMIN"
            self.launch_portal(role)
        else:
            sys.exit(0)
            
    def launch_portal(self, role: str):
        if self.current_window:
            self.current_window.close()
            
        if role == "ADMIN":
            self.current_window = DesktopMainWindow()
        elif role == "MEMBER":
            self.current_window = MemberPortalWindow()
        elif role == "PT":
            self.current_window = PtPortalWindow()
        else:
            self.current_window = DesktopMainWindow()
            
        self.current_window.switch_portal_requested.connect(self.show_login)
        self.current_window.show()

def main():
    parser = argparse.ArgumentParser(description="Gym Management Python UI Launcher")
    parser.add_argument("--role", choices=["admin", "member", "pt"], help="Launch directly into a specific portal")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("GymManagementSystem")
    app.setStyle("Fusion")
    
    # Load stylesheet
    qss_path = os.path.join(current_dir, "styles", "dark_theme.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
            
    manager = GymAppManager(app, initial_role=args.role)
    manager.start()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
