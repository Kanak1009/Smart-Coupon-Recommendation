from datetime import date
from typing import Dict, List, Tuple, Any

from .models import Product, Coupon

def calculate_cart(products: Dict[str, Product], cart_items: Dict[str, int]) -> Tuple[float, Dict[str, float], List[Dict[str, Any]]]:
    category_totals: Dict[str, float] = {}
    line_items: List[Dict[str, Any]] = []
    cart_total = 0.0

    for pid, qty in cart_items.items():
        if pid not in products:
            raise KeyError(f"Product id '{pid}' not found in product catalog.")
        product = products[pid]
        qty = int(qty)
        subtotal = float(product.price) * qty
        cart_total += subtotal
        cat = product.category.upper()
        category_totals[cat] = category_totals.get(cat, 0.0) + subtotal
        line_items.append({
            "product_id": pid,
            "name": product.name,
            "category": cat,
            "unit_price": float(product.price),
            "qty": qty,
            "subtotal": round(subtotal, 2)
        })

    cart_total = round(cart_total, 2)
    for k in list(category_totals.keys()):
        category_totals[k] = round(category_totals[k], 2)

    return cart_total, category_totals, line_items

def _coupon_date_and_active_ok(coupon: Coupon, today: date) -> Tuple[bool, str]:
    if not coupon.is_active:
        return False, "Coupon is not active."
    if coupon.start_date and today < coupon.start_date:
        return False, f"Coupon not started (starts {coupon.start_date})."
    if coupon.end_date and today > coupon.end_date:
        return False, f"Coupon expired on {coupon.end_date}."
    return True, "Date & active checks passed."

def _compute_applicable_amount_for_coupon(coupon: Coupon, cart_total: float, category_totals: Dict[str, float]) -> float:
    cats = coupon.applicable_categories
    if len(cats) == 1 and cats[0].upper() == "ALL":
        return round(cart_total, 2)
    applicable_amount = 0.0
    for c in cats:
        applicable_amount += float(category_totals.get(c.upper(), 0.0))
    return round(applicable_amount, 2)

def is_coupon_eligible(coupon: Coupon, cart_total: float, category_totals: Dict[str, float], today: date) -> Tuple[bool, List[str], float]:
    reasons: List[str] = []
    ok, msg = _coupon_date_and_active_ok(coupon, today)
    if not ok:
        reasons.append(msg)
        return False, reasons, 0.0
    reasons.append(msg)
    applicable_amount = _compute_applicable_amount_for_coupon(coupon, cart_total, category_totals)
    reasons.append(f"Applicable amount for coupon (by category): {applicable_amount:.2f}")
    if cart_total < float(coupon.min_cart_value):
        reasons.append(f"Cart total {cart_total:.2f} is less than coupon's min required {coupon.min_cart_value:.2f}.")
        return False, reasons, applicable_amount
    reasons.append(f"Cart total {cart_total:.2f} satisfies min cart value {coupon.min_cart_value:.2f}.")
    if applicable_amount <= 0.0:
        reasons.append("No items from coupon's applicable categories are present in the cart.")
        return False, reasons, applicable_amount
    reasons.append("Coupon eligible based on rules.")
    return True, reasons, applicable_amount

def compute_coupon_savings(coupon: Coupon, cart_total: float, applicable_amount: float) -> float:
    if coupon.discount_type.upper() == "PERCENT":
        percent = float(coupon.discount_value) / 100.0
        raw_discount = applicable_amount * percent
        cap = float(coupon.max_discount_amount)
        savings = min(raw_discount, cap)
    elif coupon.discount_type.upper() == "FLAT":
        intended = float(coupon.discount_value)
        cap = float(coupon.max_discount_amount)
        savings = min(intended, cap)
    else:
        savings = 0.0
    savings = min(savings, cart_total)
    return round(savings, 2)

def evaluate_coupons_for_cart(coupons: List[Coupon], products: Dict[str, Product], cart_items: Dict[str, int], today: date = date.today()) -> List[Dict[str, Any]]:
    cart_total, category_totals, line_items = calculate_cart(products, cart_items)
    results: List[Dict[str, Any]] = []
    for coupon in coupons:
        eligible, reasons, applicable_amount = is_coupon_eligible(coupon, cart_total, category_totals, today)
        savings = 0.0
        final_total = cart_total
        if eligible:
            savings = compute_coupon_savings(coupon, cart_total, applicable_amount)
            final_total = round(cart_total - savings, 2)
        results.append({
            "coupon_code": coupon.coupon_code,
            "description": coupon.description,
            "eligible": eligible,
            "reasons": reasons,
            "applicable_amount": round(applicable_amount, 2),
            "savings": round(savings, 2),
            "final_total": round(final_total, 2),
            "coupon_obj": coupon
        })
    results.sort(key=lambda x: (-x["savings"], x["final_total"]))
    return results

def recommend_best_coupon(evaluated_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    for r in evaluated_results:
        if r["eligible"] and r["savings"] > 0:
            return r
    return {}
