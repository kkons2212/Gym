"""
Standalone Trainer (PT) Application for Gym Management System.
Dedicated exclusively for Personal Trainers (Trainer Web Portal).
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt6.QtWidgets import QApplication
from components.login_window import LoginWindow
from web_portal.pt_portal_window import PtPortalWindow

class PtApp:
    def __init__(self):
        self.login_win = None
        self.main_win = None
        
    def start(self):
        self.show_login()
        
    def show_login(self):
        if self.main_win:
            self.main_win.close()
            self.main_win = None
            
        self.login_win = LoginWindow(role="PT")
        self.login_win.login_success.connect(self.show_main)
        self.login_win.show()
        
    def show_main(self, user_data):
        pt_obj = user_data.get("pt")
        self.main_win = PtPortalWindow(current_pt=pt_obj)
        self.main_win.switch_portal_requested.connect(self.show_login)
        self.main_win.show()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GymTrainerPortal")
    app.setStyle("Fusion")
    
    qss_path = os.path.join(current_dir, "styles", "dark_theme.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
            
    runner = PtApp()
    runner.start()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
