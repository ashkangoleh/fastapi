from pydantic import BaseModel
from typing import Any, Optional, Dict


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


class LoginModel(BaseModel):
    username: str
    password: str
