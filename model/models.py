from sqlalchemy.orm import relationship
from db.database import Base
from sqlalchemy import (
    Boolean,
    String,
    Column,
    Integer,
    Text,
    ForeignKey,DateTime
)
from sqlalchemy_utils import ChoiceType
import datetime

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(80), unique=True)
    phone_number = Column(String(10), unique=True, nullable=True, default=None)
    password = Column(Text, nullable=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    # relation order to user
    # string name as obj in relationship is Class name
    orders = relationship('Order', back_populates="user")
    verification_code = relationship('CodeVerification', back_populates="user")

    def __repr__(self):
        return f"<user {self.username}>"


class Order(Base):
    ORDER_STATUSES = (
        ("PENDING", "pending"),
        ("IN-TRANSIT", "in-transit"),
        ("DELIVERED", "delivered"),
    )
    ORDER_SIZES = (
        ("SMALL", "small"),
        ("MEDIUM", "medium"),
        ("LARGE", "large"),
        ("EXTRA-LARGE", "extra-large"),
    )
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(ChoiceType(
        choices=ORDER_STATUSES), default="PENDING")
    order_sizes = Column(ChoiceType(choices=ORDER_SIZES), default="SMALL")
    # relation user to order
    # string name as obj in relationship is Class name
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates='orders')

    def __repr__(self):
        return f"<Order {self.id}>"


class CodeVerification(Base):
    __tablename__ = "verification_code"
    id = Column(Integer, primary_key=True)
    code = Column(String(6), nullable=False)
    validation = Column(Boolean,nullable=True,default=True)
    expiration_time = Column(DateTime,default=datetime.datetime.now())
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates='verification_code')
    
    def __repr__(self):
        return f"<code for {self.id}>"

