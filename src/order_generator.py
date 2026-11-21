"""Day 10: deterministic orders, line items and payment attempts.

All amounts are Decimal values quantized to cents. No real customer data is used.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
import random

CENTS = Decimal("0.01")
FIELDS = {
    "orders": ["order_id", "customer_id", "placed_at", "status"],
    "order_items": ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_amount"],
    "payments": ["payment_id", "order_id", "attempted_at", "amount", "status"],
}

def money(value):
    return Decimal(value).quantize(CENTS, rounding=ROUND_HALF_UP)

def timestamp(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_transactions(base, config):
    """Return three deterministic, FK-consistent tables for the supplied catalog."""
    rng = random.Random(f"{config['seed']}:401")
    statuses = config["order_status_weights"]
    lines = config["order_line_count_weights"]
    start = datetime.fromisoformat(config["observation_start"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(config["observation_end"].replace("Z", "+00:00"))
    # Reserve at least 4 minutes for all payment attempts inside the observation window.
    latest = end - timedelta(minutes=4)
    customers = base["customers"]
    products = base["products"]
    by_id = {p["product_id"]: p for p in products}
    customer_created = {
        c["customer_id"]: datetime.fromisoformat(c["created_at"].replace("Z", "+00:00"))
        for c in customers
    }
    orders, items, payments = [], [], []
    item_id = payment_id = 0
    for order_id in range(1, config["counts"]["orders"] + 1):
        customer = rng.choice(customers)
        customer_id = customer["customer_id"]
        earliest = max(start, customer_created[customer_id])
        if earliest > latest:
            # Customers created near year end can be excluded from this order's buyer pool.
            customer_id = customers[0]["customer_id"]
            earliest = max(start, customer_created[customer_id])
        if earliest > latest:
            raise ValueError("No eligible customer exists before the order cutoff")
        span = int((latest - earliest).total_seconds())
        placed = earliest + timedelta(seconds=rng.randint(0, span))
        status = rng.choices(list(statuses), weights=list(statuses.values()))[0]
        orders.append({"order_id": order_id, "customer_id": customer_id,
                       "placed_at": timestamp(placed), "status": status})
        count = int(rng.choices(list(lines), weights=list(lines.values()))[0])
        chosen = rng.sample(products, k=min(count, len(products)))
        total = Decimal("0.00")
        for product in chosen:
            item_id += 1
            quantity = rng.randint(1, 4)
            price = money(product["list_price"])
            gross = price * quantity
            discount = Decimal("0.00")
            if rng.random() < config["discount_probability"]:
                rate = Decimal(str(rng.uniform(config["discount_min_rate"], config["discount_max_rate"])))
                discount = min(gross, money(gross * rate))
            total += gross - discount
            items.append({"order_item_id": item_id, "order_id": order_id,
                          "product_id": product["product_id"], "quantity": quantity,
                          "unit_price": f"{price:.2f}", "discount_amount": f"{discount:.2f}"})
        # A zero-priced basket cannot be captured because the SQL schema requires amount > 0.
        # Config defaults have positive product prices and discounts below 100%.
        if total <= 0:
            raise ValueError("Order total must be positive")
        # Non-completed orders can have a failed or pending attempt but never a capture.
        if status == "completed":
            for _ in range(rng.choices([0, 1, 2], weights=[0.75, 0.20, 0.05])[0]):
                payment_id += 1
                payments.append({"payment_id": payment_id, "order_id": order_id,
                                 "attempted_at": timestamp(placed + timedelta(seconds=payment_id % 45 + 1)),
                                 "amount": f"{total:.2f}", "status": "failed"})
            payment_id += 1
            payments.append({"payment_id": payment_id, "order_id": order_id,
                             "attempted_at": timestamp(placed + timedelta(minutes=3)),
                             "amount": f"{total:.2f}", "status": "captured"})
        elif rng.random() < 0.35:
            payment_id += 1
            payments.append({"payment_id": payment_id, "order_id": order_id,
                             "attempted_at": timestamp(placed + timedelta(minutes=1)),
                             "amount": f"{total:.2f}",
                             "status": "failed" if status in ("cancelled", "expired") else "pending"})
    return {"orders": orders, "order_items": items, "payments": payments}

def validate_transactions(base, transactions, config):
    customer_created = {c["customer_id"]: c["created_at"] for c in base["customers"]}
    product_ids = {p["product_id"] for p in base["products"]}
    orders = transactions["orders"]
    if len(orders) != config["counts"]["orders"]:
        raise ValueError("Order count mismatch")
    order_map = {o["order_id"]: o for o in orders}
    if len(order_map) != len(orders):
        raise ValueError("Duplicate order ID")
    totals = {}
    line_counts = {}
    for item in transactions["order_items"]:
        if item["order_id"] not in order_map or item["product_id"] not in product_ids:
            raise ValueError("Invalid item FK")
        gross = money(item["unit_price"]) * item["quantity"]
        discount = money(item["discount_amount"])
        if item["quantity"] <= 0 or gross < 0 or not 0 <= discount <= gross:
            raise ValueError("Invalid item amount")
        oid = item["order_id"]
        totals[oid] = totals.get(oid, Decimal("0.00")) + gross - discount
        line_counts[oid] = line_counts.get(oid, 0) + 1
    captures = {}
    for payment in transactions["payments"]:
        oid = payment["order_id"]
        if oid not in order_map:
            raise ValueError("Invalid payment FK")
        if payment["status"] not in ("pending", "failed", "captured") or money(payment["amount"]) <= 0:
            raise ValueError("Invalid payment")
        if payment["attempted_at"] < order_map[oid]["placed_at"]:
            raise ValueError("Payment before order")
        if payment["status"] == "captured":
            captures.setdefault(oid, []).append(money(payment["amount"]))
    for order in orders:
        oid = order["order_id"]
        if order["customer_id"] not in customer_created:
            raise ValueError("Invalid customer FK")
        if order["placed_at"] < customer_created[order["customer_id"]]:
            raise ValueError("Order before customer creation")
        if order["status"] not in ("placed", "completed", "cancelled", "expired"):
            raise ValueError("Invalid order status")
        if not line_counts.get(oid):
            raise ValueError("Order missing items")
        if order["status"] == "completed":
            if captures.get(oid) != [totals[oid]]:
                raise ValueError("Completed order not reconciled")
        elif oid in captures:
            raise ValueError("Non-completed order has capture")
    for table, field in (("order_items", "order_item_id"), ("payments", "payment_id")):
        ids = [r[field] for r in transactions[table]]
        if len(ids) != len(set(ids)) or ids != list(range(1, len(ids) + 1)):
            raise ValueError("Invalid sequential IDs: " + table)
    return {"orders": len(orders), "order_items": len(transactions["order_items"]),
            "payments": len(transactions["payments"]),
            "completed_orders": sum(o["status"] == "completed" for o in orders)}
