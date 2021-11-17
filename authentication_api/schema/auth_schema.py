from re import match
from pydantic import BaseModel,EmailStr,ValidationError,validator
from typing import Any, Optional, Dict
from pydantic.class_validators import root_validator
from werkzeug.security import generate_password_hash, check_password_hash
import re

def verify_password(plain_password, hashed_password):
    return check_password_hash(plain_password, hashed_password)


def get_password_hash(password):
    return generate_password_hash(password)

class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: EmailStr
    phone_number : Optional[str]
    password: str
    password2: Optional[str]
    is_staff: Optional[bool]
    is_active: Optional[bool]
    
    def hashed_password(self):
        self.password = get_password_hash(self.password)
        self.password2 = get_password_hash(self.password)
        return self.password
    
    @validator('phone_number')
    def phone_number_must_have_10_digits(cls,v):
        match = re.match(r"0\d{9}",v)
        if (match is None) or (len(v) != 10):
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


class Settings(BaseModel):
    authjwt_secret_key: str = 'f00cc46cca11ba7fb31010c7435b8593267d8e973cf55e85d905083452246b20'
    authjwt_access_token:int =300
    authjwt_refresh_token:int =300 # 5min
    # authjwt_token_location: set = {"cookies"}
    # authjwt_cookie_csrf_protect: bool = False


class LoginModel(BaseModel):
    username: str
    password: str


