# src/utils.py
import json
import os
from datetime import datetime
from typing import Dict, Any, List

def ensure_exports_dir(path: str = None) -> str:
    """
    Ensure an 'exports' directory exists at repo root (or at provided path).
    Returns the directory path.
    """
    if path is None:
        # parent of src/ is project root; compute relative to this file
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exports_dir = os.path.join(base, "exports")
    else:
        exports_dir = path
    os.makedirs(exports_dir, exist_ok=True)
    return exports_dir


def build_receipt_payload(cart: Dict[str, int],
                          products: Dict[str, Any],
                          best: Dict[str, Any],
                          evaluated: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a structured payload summarizing the cart, products, recommended coupon and all evaluations.
    """
    items = []
    cart_total = 0.0
    for pid, qty in cart.items():
        prod = products.get(pid)
        if not prod:
            continue
        subtotal = round(prod.price * qty, 2)
        cart_total += subtotal
        items.append({
            "product_id": pid,
            "name": prod.name,
            "category": prod.category,
            "unit_price": prod.price,
            "quantity": qty,
            "subtotal": subtotal
        })

    payload = {
        "generated_at_utc": datetime.utcnow().isoformat(),
        "cart_total": round(cart_total, 2),
        "items": items,
        "recommended_coupon": {
            "coupon_code": best.get("coupon_code") if best else None,
            "savings": best.get("savings") if best else 0.0,
            "final_total": best.get("final_total") if best else cart_total
        },
        "evaluations": [
            {
                "coupon_code": r["coupon_code"],
                "eligible": r["eligible"],
                "applicable_amount": r["applicable_amount"],
                "savings": r["savings"],
                "final_total": r["final_total"]
            } for r in evaluated
        ]
    }
    return payload


def export_receipt_json(payload: Dict[str, Any], exports_dir: str = None, prefix: str = "receipt") -> str:
    """
    Write payload to a JSON file in the exports folder. Returns the written file path.
    """
    exports_dir = ensure_exports_dir(exports_dir)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{prefix}_{ts}.json"
    filepath = os.path.join(exports_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return filepath
