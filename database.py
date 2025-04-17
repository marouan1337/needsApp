from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import re

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    needs = relationship("Need", back_populates="customer")
    created_at = Column(DateTime, default=datetime.now)

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    needs = relationship("Need", back_populates="product")
    created_at = Column(DateTime, default=datetime.now)

class Need(Base):
    __tablename__ = 'needs'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    is_fulfilled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    fulfilled_at = Column(DateTime, nullable=True)
    
    customer = relationship("Customer", back_populates="needs")
    product = relationship("Product", back_populates="needs")

class Database:
    def __init__(self):
        self.engine = create_engine('sqlite:///needs.db')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def validate_phone(self, phone):
        # Basic phone number validation
        return bool(re.match(r'^\+?1?\d{9,15}$', phone))

    def add_customer(self, name, phone):
        if not self.validate_phone(phone):
            raise ValueError("Invalid phone number format")
        customer = Customer(name=name, phone=phone)
        self.session.add(customer)
        self.session.commit()
        return customer

    def add_product(self, name):
        product = Product(name=name)
        self.session.add(product)
        self.session.commit()
        return product

    def add_need(self, customer_id, product_id):
        need = Need(customer_id=customer_id, product_id=product_id)
        self.session.add(need)
        self.session.commit()
        return need

    def get_customers_needing_product(self, product_name):
        return self.session.query(Customer).join(Need).join(Product).filter(
            Product.name == product_name,
            Need.is_fulfilled == False
        ).all()

    def mark_need_fulfilled(self, customer_id, product_id):
        need = self.session.query(Need).filter_by(
            customer_id=customer_id,
            product_id=product_id,
            is_fulfilled=False
        ).first()
        if need:
            need.is_fulfilled = True
            need.fulfilled_at = datetime.now()
            self.session.commit()
            return True
        return False

    def get_all_products(self):
        return self.session.query(Product).all()

    def get_all_customers(self):
        return self.session.query(Customer).all()

    def get_customer_needs(self, customer_id):
        return self.session.query(Need).filter_by(customer_id=customer_id).all()

    def search_customers(self, query):
        return self.session.query(Customer).filter(
            (Customer.name.ilike(f'%{query}%')) |
            (Customer.phone.ilike(f'%{query}%'))
        ).all()

    def delete_customer(self, customer_id):
        customer = self.session.query(Customer).get(customer_id)
        if customer:
            self.session.delete(customer)
            self.session.commit()
            return True
        return False

    def delete_product(self, product_id):
        product = self.session.query(Product).get(product_id)
        if product:
            self.session.delete(product)
            self.session.commit()
            return True
        return False

    def get_statistics(self):
        total_customers = self.session.query(Customer).count()
        total_products = self.session.query(Product).count()
        total_needs = self.session.query(Need).count()
        fulfilled_needs = self.session.query(Need).filter_by(is_fulfilled=True).count()
        pending_needs = total_needs - fulfilled_needs
        
        return {
            'total_customers': total_customers,
            'total_products': total_products,
            'total_needs': total_needs,
            'fulfilled_needs': fulfilled_needs,
            'pending_needs': pending_needs
        } 