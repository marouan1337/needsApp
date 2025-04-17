from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QCalendarWidget, 
                            QTableWidget, QTableWidgetItem, QLabel)
from PyQt6.QtCore import Qt, QDate, QTimer
from database import Database, Need
from datetime import datetime, timedelta

class CalendarView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.setup_notifications()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Calendar Widget
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.date_selected)
        layout.addWidget(self.calendar)
        
        # Date Label
        self.date_label = QLabel("Select a date to view needs")
        layout.addWidget(self.date_label)
        
        # Needs Table
        self.needs_table = QTableWidget()
        self.needs_table.setColumnCount(4)
        self.needs_table.setHorizontalHeaderLabels(["Customer", "Product", "Status", "Time"])
        layout.addWidget(self.needs_table)
        
        # Update calendar highlights
        self.update_calendar_highlights()

    def setup_notifications(self):
        # Check for pending needs every 5 minutes
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.check_pending_needs)
        self.notification_timer.start(300000)  # 5 minutes

    def date_selected(self, date):
        self.date_label.setText(f"Needs for {date.toString('yyyy-MM-dd')}")
        self.update_needs_table(date)

    def update_needs_table(self, date):
        start_date = datetime(date.year(), date.month(), date.day())
        end_date = start_date + timedelta(days=1)
        
        needs = self.db.session.query(Need).filter(
            Need.created_at >= start_date,
            Need.created_at < end_date
        ).all()
        
        self.needs_table.setRowCount(len(needs))
        for i, need in enumerate(needs):
            self.needs_table.setItem(i, 0, QTableWidgetItem(need.customer.name))
            self.needs_table.setItem(i, 1, QTableWidgetItem(need.product.name))
            status = "Fulfilled" if need.is_fulfilled else "Pending"
            self.needs_table.setItem(i, 2, QTableWidgetItem(status))
            time = need.created_at.strftime("%H:%M")
            self.needs_table.setItem(i, 3, QTableWidgetItem(time))

    def update_calendar_highlights(self):
        # Get all needs dates
        needs = self.db.session.query(Need).all()
        dates_with_needs = set(need.created_at.date() for need in needs)
        
        # Format dates for calendar
        self.calendar.setDateTextFormat(QDate(), self.calendar.dateTextFormat(QDate()))
        for date in dates_with_needs:
            qdate = QDate(date.year, date.month, date.day)
            format = self.calendar.dateTextFormat(qdate)
            format.setBackground(Qt.GlobalColor.yellow)
            self.calendar.setDateTextFormat(qdate, format)

    def check_pending_needs(self):
        # Get needs that are more than 24 hours old and still pending
        old_date = datetime.now() - timedelta(days=1)
        pending_needs = self.db.session.query(Need).filter(
            Need.created_at <= old_date,
            Need.is_fulfilled == False
        ).all()
        
        if pending_needs:
            # Here you would implement your notification system
            # For example, you could show a QMessageBox or use a system notification
            print(f"Warning: {len(pending_needs)} needs are pending for more than 24 hours")
            
            # You could also update the calendar highlights
            self.update_calendar_highlights() 