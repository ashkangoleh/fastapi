from pydantic import BaseModel, EmailStr, ValidationError, validator
from typing import Any, Optional, Dict
from utils import AuthHandler

import re


class Authorization:
    Auth: str = AuthHandler.Token_requirement

    @classmethod
    def authorize(cls):
        return cls.Auth



class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: EmailStr
    phone_number: Optional[str]
    password: str
    password2: Optional[str]

    def hashed_password(self):
        self.password = AuthHandler.get_password_hash(self.password)
        self.password2 = AuthHandler.get_password_hash(self.password)
        return self.password

    @validator('phone_number')
    def phone_number_must_have_10_digits(cls, v):
        match = re.match(r"0\d{10}", v)
        if (match is None) or (len(v) != 11):
            raise ValueError('Phone number must have 10 digits')
        return v

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                "username": "admin",
                "email": "admin@example.com",
                "password": "password",
                "is_staff": False,
                "is_active": True,
            }
        }


class ResetPassword(BaseModel):
    code: str
    username: str
    # email: EmailStr
    new_password: str
    new_password2: Optional[str]

    def hashed_password(self):
        self.new_password = AuthHandler.get_password_hash(self.new_password)
        self.new_password2 = AuthHandler.get_password_hash(self.new_password)
        return self.new_password

    @validator('new_password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('new_password do not match')
        return v


class Settings(BaseModel):
    authjwt_secret_key: str = 'f00cc46cca11ba7fb31010c7435b8593267d8e973cf55e85d905083452246b20'
    authjwt_access_token: int = 300
    authjwt_refresh_token: int = 300  # 5min
    # authjwt_token_location: set = {"cookies"}
    # authjwt_cookie_csrf_protect: bool = False


class LoginModel(BaseModel):
    username: str
    password: str
