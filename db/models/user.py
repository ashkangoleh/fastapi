from sqlalchemy.orm import relationship
from db.database import Base
from sqlalchemy import (
    Boolean,
    String,
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
    JSON,
)
from sqlalchemy_utils import ChoiceType, URLType
import datetime


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(25), unique=True)
    email = Column(String(80), unique=True)
    phone_number = Column(String(11), unique=True, nullable=True, default=None)
    password = Column(Text, nullable=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    # relation order to user
    # string name as obj in relationship is Class name
    orders = relationship('Order', back_populates="user")
    verification_code = relationship('CodeVerification', back_populates="user")
    users_log = relationship('UserLog', back_populates="user")
    user_profile = relationship('UserProfile', back_populates="user")

    def __repr__(self):
        return f"<user {self.username}>"


class CodeVerification(Base):
    __tablename__ = "verification_code"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), nullable=False)
    validation = Column(Boolean, nullable=True, default=True)
    expiration_time = Column(DateTime, default=datetime.datetime.now())
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates='verification_code')

    def __repr__(self):
        return f"<code for {self.id}>"

    @staticmethod
    def old_code_remover(db):
        old = datetime.datetime.now() - datetime.timedelta(days=1)
        old_code = db.query(CodeVerification).filter(
            CodeVerification.expiration_time < old).all()
        for olds in old_code:
            db.delete(olds)


class UserLog(Base):
    __tablename__ = "users_log"
    id = Column(Integer, primary_key=True, index=True)
    user_log = Column(JSON)
    login_datetime = Column(DateTime, default=datetime.datetime.now())
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates='users_log')

    def __repr__(self):
        return f"<code for {self.id}>"


class UserProfile(Base):
    TYPE = (
        ("guest", "guest"),
        ("normal", "normal"),
        ("vip", "vip"),
        ("pro", "pro"),
    )
    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    address = Column(Text)
    image = Column(
        URLType, default="/media/profile_image/simple.png", nullable=False)
    postal_code = Column(String(25))
    national_code = Column(String(10))
    type = Column(ChoiceType(TYPE), default="guest")
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship('User', back_populates="user_profile")

    def __repr__(self):
        return f"<code for {self.id}"
