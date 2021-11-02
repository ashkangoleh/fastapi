from pydantic import BaseModel
from typing import Any, Optional, Dict

from sqlalchemy import orm


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_status: Optional[str] = "PENDING"
    order_sizes: Optional[str] = "SMALL"
    user_id: Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "quantity": 2,
                "order_size": "LARGE"
            }
        }
