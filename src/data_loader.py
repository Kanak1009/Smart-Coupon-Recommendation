import csv
from datetime import datetime
from typing import Dict, List

from .models import Product, Coupon

DATE_FORMAT = "%Y-%m-%d"

def parse_date(date_str: str):
    return datetime.strptime(date_str, DATE_FORMAT).date()

def parse_bool(value: str) -> bool:
    return value.strip().upper() == "TRUE"

def parse_categories(categories_str: str) -> List[str]:
    categories_str = categories_str.strip()
    if categories_str.upper() == "ALL":
        return ["ALL"]
    return [cat.strip().upper() for cat in categories_str.split(";") if cat.strip()]

def load_products(csv_path: str) -> Dict[str, Product]:
    products: Dict[str, Product] = {}
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not row.get("product_id"):
                continue
            product = Product(
                product_id=row["product_id"].strip().upper(),
                name=row["name"].strip(),
                category=row["category"].strip().upper(),
                price=float(row["price"]),
            )
            products[product.product_id] = product
    return products

def load_coupons(csv_path: str) -> List[Coupon]:
    coupons: List[Coupon] = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not row.get("coupon_code"):
                continue
            coupon = Coupon(
                coupon_code=row["coupon_code"].strip().upper(),
                description=row["description"].strip(),
                discount_type=row["discount_type"].strip().upper(),
                discount_value=float(row["discount_value"]),
                min_cart_value=float(row["min_cart_value"]),
                applicable_categories=parse_categories(row["applicable_categories"]),
                max_discount_amount=float(row["max_discount_amount"]),
                start_date=parse_date(row["start_date"]),
                end_date=parse_date(row["end_date"]),
                is_active=parse_bool(row["is_active"]),
            )
            coupons.append(coupon)
    return coupons
