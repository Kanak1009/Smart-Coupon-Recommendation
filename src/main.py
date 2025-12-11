import os
import sys
from datetime import date
from typing import Dict

from .data_loader import load_products, load_coupons
from .engine import evaluate_coupons_for_cart, recommend_best_coupon

def parse_cart_input(text: str) -> Dict[str, int]:
    cart: Dict[str, int] = {}
    if not text.strip():
        return cart
    parts = text.split(",")
    for raw in parts:
        item = raw.strip()
        if not item:
            continue
        if ":" not in item:
            raise ValueError(f"Invalid item '{item}'. Use PRODUCT_ID:QTY format.")
        pid, qty_str = item.split(":", 1)
        pid = pid.strip().upper()
        try:
            qty = int(qty_str.strip())
        except Exception:
            raise ValueError(f"Invalid quantity for '{pid}': '{qty_str}'")
        if qty <= 0:
            raise ValueError(f"Quantity must be positive for '{pid}'.")
        cart[pid] = cart.get(pid, 0) + qty
    return cart

def pretty_print_cart(products: Dict[str, any], cart: Dict[str, int]):
    print("\nYour cart:")
    print("-" * 50)
    total = 0.0
    for pid, qty in cart.items():
        prod = products.get(pid)
        if not prod:
            print(f"{pid}: <UNKNOWN PRODUCT> x {qty}")
            continue
        subtotal = qty * prod.price
        total += subtotal
        print(f"{pid:6} {prod.name:30} x{qty:<3} ₹{subtotal:8.2f}")
    print("-" * 50)
    print(f"Cart total: ₹{total:.2f}\n")

def pretty_print_recommendations(evaluated_results):
    if not evaluated_results:
        print("No coupons available.")
        return
    print("\nTop coupon recommendations (sorted by savings):")
    print("-" * 70)
    print(f"{'CODE':12} {'ELIG':6} {'SAVINGS':10} {'FINAL_TOTAL':12}  {'NOTE'}")
    print("-" * 70)
    for r in evaluated_results[:10]:
        code = r["coupon_code"]
        elig = "YES" if r["eligible"] else "NO"
        print(f"{code:12} {elig:6} ₹{r['savings']:8.2f}    ₹{r['final_total']:10.2f}   {('eligible' if r['eligible'] else 'not eligible')}")
    print("-" * 70)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    products_path = os.path.join(data_dir, "products.csv")
    coupons_path = os.path.join(data_dir, "coupons.csv")

    products = load_products(products_path)
    coupons = load_coupons(coupons_path)

    print("Smart Coupon Recommendation System — Comma-separated CLI")
    print("Enter cart items in this format: P001:2, P003:1, P007:3")
    print("Type 'exit' or press Enter on an empty line to quit.\n")

    while True:
        try:
            user = input("Enter cart: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            sys.exit(0)

        if user.lower() == "exit" or user == "":
            print("Goodbye.")
            break

        try:
            cart = parse_cart_input(user)
        except ValueError as e:
            print(f"Input error: {e}")
            continue

        unknowns = [pid for pid in cart.keys() if pid not in products]
        if unknowns:
            print(f"Unknown product IDs found: {', '.join(unknowns)}")
            print("Please check product IDs or update your input.")
            continue

        pretty_print_cart(products, cart)

        evaluated = evaluate_coupons_for_cart(coupons, products, cart, today=date.today())

        pretty_print_recommendations(evaluated)

        best = recommend_best_coupon(evaluated)
        if best:
            print(f"\nRecommended coupon -> {best['coupon_code']}  (saves ₹{best['savings']:.2f})")
            see_reasons = input("See detailed reasons for this coupon? (y/N): ").strip().lower()
            if see_reasons == "y":
                print("\nReasons / checks:")
                for line in best["reasons"]:
                    print(" -", line)
                print(f"\nApplicable amount: ₹{best['applicable_amount']:.2f}")
                print(f"Savings: ₹{best['savings']:.2f}")
                print(f"Final total: ₹{best['final_total']:.2f}")
        else:
            print("\nNo eligible coupon found for this cart.")

        print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
