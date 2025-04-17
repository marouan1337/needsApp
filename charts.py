from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
from database import Database, Need, Customer, Product
from datetime import datetime, timedelta

class ChartsView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create figure and canvas
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Create subplots
        self.ax1 = self.figure.add_subplot(221)  # Top left
        self.ax2 = self.figure.add_subplot(222)  # Top right
        self.ax3 = self.figure.add_subplot(212)  # Bottom
        
        # Update charts
        self.update_charts()

    def update_charts(self):
        # Clear the figure
        self.figure.clear()
        
        # Get data from database
        needs = self.db.session.query(Need).all()
        
        if not needs:
            # If no data, show a message
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            self.canvas.draw()
            return
            
        # Create subplots
        ax1 = self.figure.add_subplot(221)  # Status pie chart
        ax2 = self.figure.add_subplot(222)  # Top products bar chart
        ax3 = self.figure.add_subplot(212)  # Needs over time line chart
        
        # 1. Status pie chart
        fulfilled = sum(1 for need in needs if need.is_fulfilled)
        pending = len(needs) - fulfilled
        ax1.pie([fulfilled, pending], labels=['Fulfilled', 'Pending'], autopct='%1.1f%%')
        ax1.set_title('Needs Status')
        
        # 2. Top products bar chart
        product_counts = {}
        for need in needs:
            product_name = need.product.name
            product_counts[product_name] = product_counts.get(product_name, 0) + 1
        
        products = list(product_counts.keys())
        counts = list(product_counts.values())
        
        if products and counts:
            ax2.bar(products, counts)
            ax2.set_title('Top Products')
            ax2.tick_params(axis='x', rotation=45)
        
        # 3. Needs over time line chart
        dates = [need.created_at for need in needs]
        date_counts = {}
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            date_counts[date_str] = date_counts.get(date_str, 0) + 1
        
        if date_counts:
            sorted_dates = sorted(date_counts.items())
            dates = [item[0] for item in sorted_dates]
            counts = [item[1] for item in sorted_dates]
            
            ax3.plot(dates, counts, marker='o')
            ax3.set_title('Needs Over Time')
            ax3.tick_params(axis='x', rotation=45)
        
        # Adjust layout and draw
        self.figure.tight_layout()
        self.canvas.draw()

    def update_data(self):
        self.update_charts() 