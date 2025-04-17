import pandas as pd
from datetime import datetime
from database import Database, Customer, Product, Need

class DataManager:
    def __init__(self, db):
        self.db = db

    def export_customers_to_csv(self, filename):
        customers = self.db.get_all_customers()
        data = []
        for customer in customers:
            needs = self.db.get_customer_needs(customer.id)
            needs_text = ", ".join([f"{need.product.name} ({'Fulfilled' if need.is_fulfilled else 'Pending'})" 
                                  for need in needs])
            data.append({
                'Name': customer.name,
                'Phone': customer.phone,
                'Created At': customer.created_at,
                'Needs': needs_text
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return True

    def export_products_to_csv(self, filename):
        products = self.db.get_all_products()
        data = []
        for product in products:
            needs = self.db.session.query(Need).filter_by(product_id=product.id).all()
            pending_count = sum(1 for need in needs if not need.is_fulfilled)
            fulfilled_count = sum(1 for need in needs if need.is_fulfilled)
            
            data.append({
                'Product Name': product.name,
                'Created At': product.created_at,
                'Total Requests': len(needs),
                'Pending Requests': pending_count,
                'Fulfilled Requests': fulfilled_count
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return True

    def export_needs_to_csv(self, filename):
        needs = self.db.session.query(Need).all()
        data = []
        for need in needs:
            data.append({
                'Customer Name': need.customer.name,
                'Customer Phone': need.customer.phone,
                'Product': need.product.name,
                'Status': 'Fulfilled' if need.is_fulfilled else 'Pending',
                'Created At': need.created_at,
                'Fulfilled At': need.fulfilled_at if need.is_fulfilled else ''
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return True

    def import_customers_from_csv(self, filename):
        df = pd.read_csv(filename)
        for _, row in df.iterrows():
            try:
                self.db.add_customer(row['Name'], row['Phone'])
            except Exception as e:
                print(f"Error importing customer {row['Name']}: {str(e)}")
        return True

    def import_products_from_csv(self, filename):
        df = pd.read_csv(filename)
        for _, row in df.iterrows():
            try:
                self.db.add_product(row['Product Name'])
            except Exception as e:
                print(f"Error importing product {row['Product Name']}: {str(e)}")
        return True

    def get_statistics_dataframe(self):
        stats = self.db.get_statistics()
        return pd.DataFrame([stats])

    def get_recent_activity_dataframe(self, limit=10):
        needs = self.db.session.query(Need).order_by(Need.created_at.desc()).limit(limit).all()
        data = []
        for need in needs:
            data.append({
                'Customer': need.customer.name,
                'Product': need.product.name,
                'Status': 'Fulfilled' if need.is_fulfilled else 'Pending',
                'Date': need.fulfilled_at if need.is_fulfilled else need.created_at
            })
        return pd.DataFrame(data) 