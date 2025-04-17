import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QLineEdit, QPushButton,
                            QTableWidget, QTableWidgetItem, QMessageBox,
                            QTabWidget, QFormLayout, QGroupBox, QGridLayout,
                            QDialog, QFileDialog, QMenuBar, QMenu, QStatusBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from database import Database, Product, Customer, Need
from auth import AuthManager, User
from data_manager import DataManager
from calendar_view import CalendarView
from charts import ChartsView
from datetime import datetime
import os

class LoginDialog(QDialog):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Login")
        layout = QFormLayout(self)
        
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addRow("Username:", self.username)
        layout.addRow("Password:", self.password)
        
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        layout.addRow(login_button)

    def login(self):
        username = self.username.text()
        password = self.password.text()
        
        user = self.auth_manager.authenticate(username, password)
        if user:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

class NeedsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.auth_manager = AuthManager(self.db.session)
        self.data_manager = DataManager(self.db)
        
        # Create admin user if not exists
        self.create_admin_user()
        
        # Show login dialog
        if not self.show_login():
            sys.exit()
        
        self.setup_ui()

    def create_admin_user(self):
        if not self.db.session.query(User).first():
            try:
                self.auth_manager.create_user("admin", "admin", True)
            except:
                pass

    def show_login(self):
        dialog = LoginDialog(self.auth_manager)
        return dialog.exec() == QDialog.DialogCode.Accepted

    def setup_ui(self):
        self.setWindowTitle("Needs Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Add tabs
        self.setup_dashboard_tab()
        self.setup_add_customer_tab()
        self.setup_search_tab()
        self.setup_products_tab()
        self.setup_customers_tab()
        self.setup_calendar_tab()
        self.setup_charts_tab()

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        export_action = QAction("Export Data", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        import_action = QAction("Import Data", self)
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_dashboard_tab(self):
        dashboard_tab = QWidget()
        self.tabs.addTab(dashboard_tab, "Dashboard")
        
        layout = QVBoxLayout(dashboard_tab)
        
        # Statistics Group
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout()
        
        self.total_customers_label = QLabel("Total Customers: 0")
        self.total_products_label = QLabel("Total Products: 0")
        self.total_needs_label = QLabel("Total Needs: 0")
        self.fulfilled_needs_label = QLabel("Fulfilled Needs: 0")
        self.pending_needs_label = QLabel("Pending Needs: 0")
        
        stats_layout.addWidget(self.total_customers_label, 0, 0)
        stats_layout.addWidget(self.total_products_label, 0, 1)
        stats_layout.addWidget(self.total_needs_label, 1, 0)
        stats_layout.addWidget(self.fulfilled_needs_label, 1, 1)
        stats_layout.addWidget(self.pending_needs_label, 2, 0)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Recent Activity Group
        recent_group = QGroupBox("Recent Activity")
        recent_layout = QVBoxLayout()
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["Customer", "Product", "Status", "Date"])
        recent_layout.addWidget(self.recent_table)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        self.update_dashboard()

    def setup_add_customer_tab(self):
        add_customer_tab = QWidget()
        self.tabs.addTab(add_customer_tab, "Add Customer Need")
        
        customer_form = QFormLayout()
        self.customer_name = QLineEdit()
        self.customer_phone = QLineEdit()
        self.product_name = QLineEdit()
        
        customer_form.addRow("Customer Name:", self.customer_name)
        customer_form.addRow("Phone Number:", self.customer_phone)
        customer_form.addRow("Product Needed:", self.product_name)
        
        add_button = QPushButton("Add Need")
        add_button.clicked.connect(self.add_customer_need)
        customer_form.addRow(add_button)
        
        add_customer_tab.setLayout(customer_form)

    def setup_search_tab(self):
        search_tab = QWidget()
        self.tabs.addTab(search_tab, "Search")
        
        search_layout = QVBoxLayout()
        
        # Search by Product
        product_group = QGroupBox("Search by Product")
        product_layout = QVBoxLayout()
        self.search_product = QLineEdit()
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_product_needs)
        
        product_layout.addWidget(QLabel("Product Name:"))
        product_layout.addWidget(self.search_product)
        product_layout.addWidget(search_button)
        product_group.setLayout(product_layout)
        
        # Search by Customer
        customer_group = QGroupBox("Search by Customer")
        customer_layout = QVBoxLayout()
        self.search_customer = QLineEdit()
        customer_search_button = QPushButton("Search")
        customer_search_button.clicked.connect(self.search_customer_needs)
        
        customer_layout.addWidget(QLabel("Customer Name/Phone:"))
        customer_layout.addWidget(self.search_customer)
        customer_layout.addWidget(customer_search_button)
        customer_group.setLayout(customer_layout)
        
        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Customer Name", "Phone", "Product", "Fulfill"])
        
        search_layout.addWidget(product_group)
        search_layout.addWidget(customer_group)
        search_layout.addWidget(self.results_table)
        
        search_tab.setLayout(search_layout)

    def setup_products_tab(self):
        products_tab = QWidget()
        self.tabs.addTab(products_tab, "Products")
        
        layout = QVBoxLayout()
        
        # Add Product
        add_product_layout = QHBoxLayout()
        self.new_product = QLineEdit()
        add_product_button = QPushButton("Add Product")
        add_product_button.clicked.connect(self.add_product)
        
        add_product_layout.addWidget(QLabel("New Product:"))
        add_product_layout.addWidget(self.new_product)
        add_product_layout.addWidget(add_product_button)
        
        # Products Table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(2)
        self.products_table.setHorizontalHeaderLabels(["Product Name", "Delete"])
        
        layout.addLayout(add_product_layout)
        layout.addWidget(self.products_table)
        
        products_tab.setLayout(layout)
        self.update_products_table()

    def setup_customers_tab(self):
        customers_tab = QWidget()
        self.tabs.addTab(customers_tab, "Customers")
        
        layout = QVBoxLayout()
        
        # Customers Table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(4)
        self.customers_table.setHorizontalHeaderLabels(["Name", "Phone", "Needs", "Delete"])
        
        layout.addWidget(self.customers_table)
        
        customers_tab.setLayout(layout)
        self.update_customers_table()

    def setup_calendar_tab(self):
        calendar_tab = CalendarView(self.db)
        self.tabs.addTab(calendar_tab, "Calendar")

    def setup_charts_tab(self):
        charts_tab = ChartsView(self.db)
        self.tabs.addTab(charts_tab, "Charts")

    def export_data(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "CSV Files (*.csv)")
        
        if file_name:
            try:
                if "customers" in file_name.lower():
                    self.data_manager.export_customers_to_csv(file_name)
                elif "products" in file_name.lower():
                    self.data_manager.export_products_to_csv(file_name)
                else:
                    self.data_manager.export_needs_to_csv(file_name)
                QMessageBox.information(self, "Success", "Data exported successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export data: {str(e)}")

    def import_data(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Import Data", "", "CSV Files (*.csv)")
        
        if file_name:
            try:
                if "customers" in file_name.lower():
                    self.data_manager.import_customers_from_csv(file_name)
                elif "products" in file_name.lower():
                    self.data_manager.import_products_from_csv(file_name)
                QMessageBox.information(self, "Success", "Data imported successfully")
                self.update_all_tabs()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import data: {str(e)}")

    def show_settings(self):
        # Implement settings dialog
        pass

    def show_about(self):
        QMessageBox.about(self, "About",
                         "Needs Management System\n\n"
                         "Version 1.0\n"
                         "A comprehensive system for managing customer needs and product tracking.")

    def update_all_tabs(self):
        self.update_dashboard()
        self.update_products_table()
        self.update_customers_table()
        self.tabs.widget(5).update_data()  # Update charts
        self.tabs.widget(4).update_calendar_highlights()  # Update calendar

    def update_dashboard(self):
        stats = self.db.get_statistics()
        self.total_customers_label.setText(f"Total Customers: {stats['total_customers']}")
        self.total_products_label.setText(f"Total Products: {stats['total_products']}")
        self.total_needs_label.setText(f"Total Needs: {stats['total_needs']}")
        self.fulfilled_needs_label.setText(f"Fulfilled Needs: {stats['fulfilled_needs']}")
        self.pending_needs_label.setText(f"Pending Needs: {stats['pending_needs']}")
        
        # Update recent activity
        recent_needs = self.db.session.query(Need).order_by(Need.created_at.desc()).limit(10).all()
        self.recent_table.setRowCount(len(recent_needs))
        
        for i, need in enumerate(recent_needs):
            self.recent_table.setItem(i, 0, QTableWidgetItem(need.customer.name))
            self.recent_table.setItem(i, 1, QTableWidgetItem(need.product.name))
            status = "Fulfilled" if need.is_fulfilled else "Pending"
            self.recent_table.setItem(i, 2, QTableWidgetItem(status))
            date = need.fulfilled_at if need.is_fulfilled else need.created_at
            self.recent_table.setItem(i, 3, QTableWidgetItem(date.strftime("%Y-%m-%d %H:%M")))

    def add_customer_need(self):
        try:
            name = self.customer_name.text()
            phone = self.customer_phone.text()
            product = self.product_name.text()
            
            if not all([name, phone, product]):
                QMessageBox.warning(self, "Error", "Please fill in all fields")
                return
            
            # Add customer
            customer = self.db.add_customer(name, phone)
            
            # Add product if it doesn't exist
            product_obj = self.db.session.query(Product).filter_by(name=product).first()
            if not product_obj:
                product_obj = self.db.add_product(product)
            
            # Add need
            self.db.add_need(customer.id, product_obj.id)
            
            QMessageBox.information(self, "Success", "Customer need added successfully")
            self.customer_name.clear()
            self.customer_phone.clear()
            self.product_name.clear()
            self.update_products_table()
            self.update_customers_table()
            self.update_dashboard()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def search_product_needs(self):
        product_name = self.search_product.text()
        if not product_name:
            QMessageBox.warning(self, "Error", "Please enter a product name")
            return
        
        customers = self.db.get_customers_needing_product(product_name)
        self.update_results_table(customers, product_name)

    def search_customer_needs(self):
        query = self.search_customer.text()
        if not query:
            QMessageBox.warning(self, "Error", "Please enter a search query")
            return
        
        customers = self.db.search_customers(query)
        self.update_results_table(customers)

    def update_results_table(self, customers, product_name=None):
        self.results_table.setRowCount(len(customers))
        
        for i, customer in enumerate(customers):
            self.results_table.setItem(i, 0, QTableWidgetItem(customer.name))
            self.results_table.setItem(i, 1, QTableWidgetItem(customer.phone))
            
            if product_name:
                self.results_table.setItem(i, 2, QTableWidgetItem(product_name))
                fulfill_button = QPushButton("Mark as Fulfilled")
                fulfill_button.clicked.connect(lambda checked, c=customer: self.mark_fulfilled(c.id, product_name))
                self.results_table.setCellWidget(i, 3, fulfill_button)
            else:
                needs = self.db.get_customer_needs(customer.id)
                needs_text = ", ".join([need.product.name for need in needs if not need.is_fulfilled])
                self.results_table.setItem(i, 2, QTableWidgetItem(needs_text))
                self.results_table.setItem(i, 3, QTableWidgetItem(""))

    def mark_fulfilled(self, customer_id, product_name):
        product = self.db.session.query(Product).filter_by(name=product_name).first()
        if product:
            if self.db.mark_need_fulfilled(customer_id, product.id):
                QMessageBox.information(self, "Success", "Need marked as fulfilled")
                self.search_product_needs()
                self.update_dashboard()
            else:
                QMessageBox.warning(self, "Error", "Could not mark need as fulfilled")

    def update_products_table(self):
        products = self.db.get_all_products()
        self.products_table.setRowCount(len(products))
        for i, product in enumerate(products):
            self.products_table.setItem(i, 0, QTableWidgetItem(product.name))
            
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, p=product: self.delete_product(p.id))
            self.products_table.setCellWidget(i, 1, delete_button)

    def update_customers_table(self):
        customers = self.db.get_all_customers()
        self.customers_table.setRowCount(len(customers))
        for i, customer in enumerate(customers):
            self.customers_table.setItem(i, 0, QTableWidgetItem(customer.name))
            self.customers_table.setItem(i, 1, QTableWidgetItem(customer.phone))
            
            needs = self.db.get_customer_needs(customer.id)
            needs_text = ", ".join([need.product.name for need in needs if not need.is_fulfilled])
            self.customers_table.setItem(i, 2, QTableWidgetItem(needs_text))
            
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, c=customer: self.delete_customer(c.id))
            self.customers_table.setCellWidget(i, 3, delete_button)

    def add_product(self):
        product_name = self.new_product.text()
        if not product_name:
            QMessageBox.warning(self, "Error", "Please enter a product name")
            return
        
        try:
            self.db.add_product(product_name)
            self.new_product.clear()
            self.update_products_table()
            self.update_dashboard()
            QMessageBox.information(self, "Success", "Product added successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def delete_product(self, product_id):
        reply = QMessageBox.question(self, 'Confirm Delete',
                                   'Are you sure you want to delete this product?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_product(product_id):
                self.update_products_table()
                self.update_dashboard()
                QMessageBox.information(self, "Success", "Product deleted successfully")
            else:
                QMessageBox.warning(self, "Error", "Could not delete product")

    def delete_customer(self, customer_id):
        reply = QMessageBox.question(self, 'Confirm Delete',
                                   'Are you sure you want to delete this customer?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_customer(customer_id):
                self.update_customers_table()
                self.update_dashboard()
                QMessageBox.information(self, "Success", "Customer deleted successfully")
            else:
                QMessageBox.warning(self, "Error", "Could not delete customer")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NeedsApp()
    window.show()
    sys.exit(app.exec()) 