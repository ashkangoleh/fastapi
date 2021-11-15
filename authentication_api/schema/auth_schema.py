from pydantic import BaseModel
from typing import Any, Optional, Dict
from werkzeug.security import generate_password_hash, check_password_hash


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

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


def verify_password(plain_password, hashed_password):
    return check_password_hash(plain_password, hashed_password)


def get_password_hash(password):
    return generate_password_hash(password)
