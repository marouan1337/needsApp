from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import bcrypt
from database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class AuthManager:
    def __init__(self, session):
        self.session = session

    def create_user(self, username, password, is_admin=False):
        if self.session.query(User).filter_by(username=username).first():
            raise ValueError("Username already exists")
        
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        user = User(
            username=username,
            password_hash=password_hash.decode('utf-8'),
            is_admin=is_admin
        )
        
        self.session.add(user)
        self.session.commit()
        return user

    def authenticate(self, username, password):
        user = self.session.query(User).filter_by(username=username).first()
        if not user:
            return None
        
        password_bytes = password.encode('utf-8')
        stored_hash = user.password_hash.encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, stored_hash):
            return user
        return None

    def change_password(self, username, old_password, new_password):
        user = self.authenticate(username, old_password)
        if not user:
            return False
        
        password_bytes = new_password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        user.password_hash = password_hash.decode('utf-8')
        self.session.commit()
        return True 