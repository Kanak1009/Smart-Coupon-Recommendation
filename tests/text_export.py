import json
import os
from datetime import date

from src.data_loader import load_products, load_coupons
from src.engine import evaluate_coupons_for_cart, recommend_best_coupon
from src.utils import build_receipt_payload, export_receipt_json


def test_export_receipt_json(tmp_path):
    """
    Ensure exporting a receipt generates a valid JSON file
    with correct structure.
    """
    # Load data
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    products = load_products(os.path.join(data_dir, "products.csv"))
    coupons = load_coupons(os.path.join(data_dir, "coupons.csv"))

    # Sample cart for testing
    cart = {"P001": 1, "P003": 1}

    # Run evaluation
    evaluated = evaluate_coupons_for_cart(
        coupons, products, cart, today=date(2025, 5, 1)
    )
    best = recommend_best_coupon(evaluated)

    # Build payload
    payload = build_receipt_payload(cart, products, best, evaluated)

    # Export into temporary directory
    exports_dir = tmp_path
    outpath = export_receipt_json(payload, exports_dir=exports_dir)

    # File should exist
    assert os.path.exists(outpath)

    # Load JSON content
    with open(outpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check required keys
    assert "generated_at_utc" in data
    assert "cart_total" in data
    assert "items" in data
    assert "recommended_coupon" in data
    assert "evaluations" in data

    # Basic content checks
    assert data["cart_total"] == 1798.00
    assert data["recommended_coupon"]["coupon_code"] == "WELCOME10"
    assert data["recommended_coupon"]["savings"] == 179.8
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 2
