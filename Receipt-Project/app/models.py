from pydantic import BaseModel, validator
from typing import List
import re
from datetime import datetime

class Item(BaseModel):
    shortDescription: str  # Use str instead of constr
    price: str

    @validator("shortDescription")
    def validate_short_description(cls, v):
        if not v.strip():
            raise ValueError("Short description cannot be empty")
        return v.strip()

    @validator("price")
    def validate_price(cls, v):
        if not re.match(r"^\d+\.\d{2}$", v):
            raise ValueError("Invalid price format")
        return v

class Receipt(BaseModel):
    retailer: str  # Use str instead of constr
    purchaseDate: str
    purchaseTime: str
    items: List[Item]
    total: str

    @validator("retailer")
    def validate_retailer(cls, v):
        if not re.match(r"^[\w\s\-&]+$", v):
            raise ValueError("Invalid retailer name")
        return v

    @validator("purchaseDate")
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid purchase date")
        return v

    @validator("purchaseTime")
    def validate_time(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Invalid purchase time")
        return v

    @validator("total")
    def validate_total(cls, v):
        if not re.match(r"^\d+\.\d{2}$", v):
            raise ValueError("Invalid total format")
        return v