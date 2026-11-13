"""Request and response shapes of the orders API. The contract in contracts/ is built from them."""
from enum import Enum

from pydantic import BaseModel, Field


class Status(str, Enum):
    draft = "draft"
    placed = "placed"
    paid = "paid"
    cancelled = "cancelled"


class Item(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(gt=0, le=10_000)
    unit_price_minor: int = Field(ge=0, le=100_000_000, description="Price of one unit, in the minor unit of the currency")


class NewOrder(BaseModel):
    customer_id: str = Field(min_length=1, max_length=64)
    currency: str = Field(pattern=r"^[A-Z]{3}$", description="ISO 4217 code")
    items: list[Item] = Field(min_length=1, max_length=200)
    discount_code: str | None = Field(default=None, max_length=32)


class Order(BaseModel):
    id: str
    customer_id: str
    currency: str
    status: Status
    items: list[Item]
    discount_code: str | None
    subtotal_minor: int
    discount_minor: int
    total_minor: int
    created_at: str = Field(description="UTC, ISO 8601")


class Problem(BaseModel):
    detail: str
