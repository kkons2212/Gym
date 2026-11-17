"""
Chart Widget: Matplotlib Canvas for Revenue Trends, Peak Hours, and InBody Charts.
Integrated with Dark Theme (#0A0F1D, #1E293B, #0EA5E9).
"""
import os
import tempfile

# Suppress Matplotlib cache path warning on Windows
if 'MPLCONFIGDIR' not in os.environ:
    os.environ['MPLCONFIGDIR'] = os.path.join(tempfile.gettempdir(), 'matplotlib')

from PyQt6.QtWidgets import QFrame, QVBoxLayout
import matplotlib
matplotlib.use('QtAgg')
matplotlib.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']
matplotlib.rcParams['font.family'] = 'sans-serif'

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from styles.color_tokens import CARD_BG, BORDER_SUBTLE

class ChartWidget(QFrame):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        super().__init__(parent)
        self.setObjectName("cardFrame")
        self.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 12px;
            }}
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor='#1E293B')
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.layout.addWidget(self.canvas)
        
    def plot_peak_hours(self, hours, checkins):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#1E293B')
        
        bars = ax.bar(hours, checkins, color='#0EA5E9', width=0.6, edgecolor='#38BDF8', alpha=0.9)
        ax.set_title("LƯU LƯỢNG CHECK-IN THEO GIỜ TRONG NGÀY", color='#F8FAFC', fontsize=10, fontweight='bold', pad=10)
        ax.set_xlabel("Khung Giờ (24h)", color='#94A3B8', fontsize=8)
        ax.set_ylabel("Lượt khách", color='#94A3B8', fontsize=8)
        
        ax.tick_params(colors='#94A3B8', labelsize=8)
        ax.grid(True, linestyle='--', alpha=0.15, color='#F8FAFC')
        
        for spine in ax.spines.values():
            spine.set_color('#334155')
            
        self.figure.tight_layout()
        self.canvas.draw()
        
    def plot_revenue_breakdown(self, categories, values):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#1E293B')
        
        colors = ['#0EA5E9', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']
        res = ax.pie(
            values, 
            labels=categories, 
            autopct='%1.1f%%',
            startangle=140,
            colors=colors[:len(categories)],
            textprops=dict(color='#F8FAFC', fontsize=8),
            wedgeprops=dict(width=0.45, edgecolor='#1E293B')
        )
        if len(res) == 3:
            _, _, autotexts = res
            for autotext in autotexts:
                autotext.set_color('#FFFFFF')
                autotext.set_fontsize(8)
                autotext.set_weight('bold')
            
        ax.set_title("TỶ TRỌNG DOANH THU THEO GÓI DỊCH VỤ", color='#F8FAFC', fontsize=10, fontweight='bold', pad=10)
        self.figure.tight_layout()
        self.canvas.draw()
        
    def plot_inbody_radar(self, labels, values, targets):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#1E293B')
        
        x = range(len(labels))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], values, width, label='Hiện tại', color='#0EA5E9')
        ax.bar([i + width/2 for i in x], targets, width, label='Mục tiêu', color='#10B981', alpha=0.7)
        
        ax.set_xticks(x)
        ax.set_xticklabels(labels, color='#F8FAFC', fontsize=9)
        ax.tick_params(colors='#94A3B8', labelsize=8)
        ax.legend(facecolor='#111827', edgecolor='#334155', labelcolor='#F8FAFC', fontsize=8)
        ax.set_title("CHỈ SỐ THỂ CHẤT SO VỚI MỤC TIÊU", color='#F8FAFC', fontsize=10, fontweight='bold', pad=10)
        
        ax.grid(True, linestyle='--', alpha=0.15, color='#F8FAFC')
        for spine in ax.spines.values():
            spine.set_color('#334155')
            
        self.figure.tight_layout()
        self.canvas.draw()
