"""Deterministic refunds and cross-table data-quality checks for Day 12."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import random

FIELDS = ["refund_id", "payment_id", "requested_at", "refunded_at", "amount", "status", "reason"]
CENT = Decimal("0.01")

def date(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def iso(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_refunds(tables, config):
    """Only captured payments are refundable; settled totals never exceed capture."""
    rng = random.Random(f"{config['seed']}:809")
    end = date(config["observation_end"])
    captured = [p for p in tables["payments"] if p["status"] == "captured"]
    refunds = []
    for payment in captured:
        if rng.random() >= config["refund_incidence_rate"]:
            continue
        amount = Decimal(payment["amount"])
        # Need enough time after capture for request and settlement.
        captured_at = date(payment["attempted_at"])
        if captured_at + timedelta(days=2) > end:
            continue
        # Refund a portion or all of the captured amount.
        fraction = Decimal(str(rng.choice((0.25, 0.5, 0.75, 1.0))))
        value = (amount * fraction).quantize(CENT)
        value = max(CENT, min(amount, value))
        requested = captured_at + timedelta(hours=rng.randint(1, 24))
        status = rng.choices(("settled", "pending", "failed"), weights=(0.82, 0.12, 0.06))[0]
        settled = requested + timedelta(hours=rng.randint(1, 12)) if status == "settled" else None
        refunds.append({
            "refund_id": len(refunds) + 1,
            "payment_id": payment["payment_id"],
            "requested_at": iso(requested),
            "refunded_at": iso(settled) if settled else "",
            "amount": f"{value:.2f}",
            "status": status,
            "reason": rng.choice(("customer_request", "damaged_item", "delivery_issue", "other")),
        })
    return refunds

def validate_refunds(tables, config):
    payments = {p["payment_id"]: p for p in tables["payments"]}
    seen = set()
    settled_by_payment = {}
    end = config["observation_end"]
    for refund in tables["refunds"]:
        rid = refund["refund_id"]
        if rid in seen:
            raise ValueError("Duplicate refund ID")
        seen.add(rid)
        payment = payments.get(refund["payment_id"])
        if not payment or payment["status"] != "captured":
            raise ValueError("Refund must reference a captured payment")
        value = Decimal(refund["amount"])
        if value <= 0 or not refund["reason"].strip():
            raise ValueError("Invalid refund amount or reason")
        if refund["requested_at"] < payment["attempted_at"] or refund["requested_at"] > end:
            raise ValueError("Refund request outside valid window")
        if refund["status"] == "settled":
            if not refund["refunded_at"] or not refund["requested_at"] <= refund["refunded_at"] <= end:
                raise ValueError("Invalid settlement timestamp")
            pid = refund["payment_id"]
            settled_by_payment[pid] = settled_by_payment.get(pid, Decimal("0.00")) + value
            if settled_by_payment[pid] > Decimal(payment["amount"]):
                raise ValueError("Refund exceeds captured payment")
        elif refund["status"] in ("pending", "failed"):
            if refund["refunded_at"]:
                raise ValueError("Unsettled refund has settlement timestamp")
        else:
            raise ValueError("Invalid refund status")
    return {"refunds": len(tables["refunds"]),
            "settled_refunds": sum(r["status"] == "settled" for r in tables["refunds"])}

def quality_report(tables, config):
    """Fail closed on invalid data; report counts and core finance consistency."""
    from src.order_generator import validate_transactions
    from src.marketing_generator import validate_marketing
    transactions = validate_transactions(tables, tables, config)
    marketing = validate_marketing(tables, tables, config)
    refunds = validate_refunds(tables, config)
    captured = sum(Decimal(p["amount"]) for p in tables["payments"] if p["status"] == "captured")
    settled = sum(Decimal(r["amount"]) for r in tables["refunds"] if r["status"] == "settled")
    if settled > captured:
        raise ValueError("Refund total exceeds captures")
    return {"status": "passed", "tables": len(tables),
            "row_counts": {name: len(rows) for name, rows in tables.items()},
            "captured_cu": f"{captured:.2f}",
            "settled_refunds_cu": f"{settled:.2f}",
            **transactions, **marketing, **refunds}
