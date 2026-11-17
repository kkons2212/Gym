"""
StatCard Component: Modern KPI card matching Desktop/Views/DashboardPage.xaml
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from styles.color_tokens import CARD_BG, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_PRIMARY, STATUS_SUCCESS

class StatCard(QFrame):
    def __init__(self, title: str, value: str, subtext: str = "", badge_text: str = "", badge_positive: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 12px;
                padding: 14px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)
        
        # Header row (Title & Badge)
        header_layout = QHBoxLayout()
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        if badge_text:
            badge_color = "#10B981" if badge_positive else "#EF4444"
            badge_bg = "rgba(16, 185, 129, 0.15)" if badge_positive else "rgba(239, 68, 68, 0.15)"
            badge_lbl = QLabel(badge_text)
            badge_lbl.setStyleSheet(f"""
                color: {badge_color};
                background-color: {badge_bg};
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: bold;
            """)
            header_layout.addWidget(badge_lbl)
            
        layout.addLayout(header_layout)
        
        # Main Value
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 22px; font-weight: bold;")
        layout.addWidget(val_lbl)
        
        # Subtext / caption
        if subtext:
            sub_lbl = QLabel(subtext)
            sub_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
            layout.addWidget(sub_lbl)
