from dataclasses import dataclass
from datetime import date
from typing import List

@dataclass
class Product:
    product_id: str
    name: str
    category: str
    price: float

@dataclass
class Coupon:
    coupon_code: str
    description: str
    discount_type: str
    discount_value: float
    min_cart_value: float
    applicable_categories: List[str]
    max_discount_amount: float
    start_date: date
    end_date: date
    is_active: bool
