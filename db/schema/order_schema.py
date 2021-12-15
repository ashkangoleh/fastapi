from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
ORDER_SIZES = (
    ("SMALL", "small"),
    ("MEDIUM", "medium"),
    ("LARGE", "large"),
    ("EXTRA-LARGE", "extra-large"),
)


class status(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in-transit"
    DELIVERED = "delivered"


class sizes(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA = "extra-large"


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_status: Optional[str] = Field(None, alias="Status")
    order_sizes: Optional[str] = Field(None, alias="Sizes")
    user_id: Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "quantity": 2,
                "order_size": "LARGE"
            }
        }


class OrderStatusModel(BaseModel):
    order_status: Optional[str] = "PENDING"

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "order_status": "PENDING"
            }
        }


class OrderTest(BaseModel):
    customer_name: str
    order_quantity: int
