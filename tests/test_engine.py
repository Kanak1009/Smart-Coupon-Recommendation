import os
from datetime import date

from src.data_loader import load_products, load_coupons
from src.engine import (
    calculate_cart,
    is_coupon_eligible,
    compute_coupon_savings,
    evaluate_coupons_for_cart,
    recommend_best_coupon,
)

def get_paths():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base, "data")
    return (
        os.path.join(data_dir, "products.csv"),
        os.path.join(data_dir, "coupons.csv")
    )

def test_calculate_cart():
    products_path, _ = get_paths()
    products = load_products(products_path)
    cart = {"P001": 1, "P003": 1}
    total, category_totals, line_items = calculate_cart(products, cart)
    assert total == 1798.00
    assert category_totals["ELECTRONICS"] == 1798.00
    assert len(line_items) == 2

def test_coupon_eligibility_percent_coupon():
    products_path, coupons_path = get_paths()
    products = load_products(products_path)
    coupons = load_coupons(coupons_path)
    welcome = next(c for c in coupons if c.coupon_code == "WELCOME10")
    cart = {"P001": 1, "P003": 1}
    total, category_totals, _ = calculate_cart(products, cart)
    eligible, reasons, applicable = is_coupon_eligible(
        welcome, total, category_totals, today=date(2025, 5, 1)
    )
    assert eligible is True
    assert applicable == total

def test_coupon_savings_percent():
    savings = compute_coupon_savings(
        coupon=type("Fake", (), {
            "discount_type": "PERCENT",
            "discount_value": 10,
            "max_discount_amount": 250
        }),
        cart_total=1798,
        applicable_amount=1798
    )
    assert savings == 179.80

def test_coupon_savings_flat():
    savings = compute_coupon_savings(
        coupon=type("Fake", (), {
            "discount_type": "FLAT",
            "discount_value": 150,
            "max_discount_amount": 150
        }),
        cart_total=1798,
        applicable_amount=1798
    )
    assert savings == 150.00

def test_evaluate_coupons_best_choice():
    products_path, coupons_path = get_paths()
    products = load_products(products_path)
    coupons = load_coupons(coupons_path)
    cart = {"P001": 1, "P003": 1}
    results = evaluate_coupons_for_cart(coupons, products, cart, today=date(2025, 5, 1))
    best = recommend_best_coupon(results)
    assert best["coupon_code"] == "WELCOME10"
    assert best["savings"] == 179.80
    assert best["final_total"] == 1618.20
