"""Day 10 transactional integrity tests."""
import copy
from decimal import Decimal
from pathlib import Path
import unittest

from src.generator import generate, parse_config, validate
from src.order_generator import validate_transactions

CONFIG = Path(__file__).resolve().parents[1] / "config" / "synthetic_data.json"

class TransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, _ = parse_config(CONFIG)
        cls.rows = generate(cls.config)

    def test_reconciliation(self):
        summary = validate_transactions(self.rows, self.rows, self.config)
        self.assertEqual(summary["orders"], 40000)
        self.assertGreater(summary["completed_orders"], 0)

    def test_unique_captured_payment(self):
        captures = [p["order_id"] for p in self.rows["payments"] if p["status"] == "captured"]
        self.assertEqual(len(captures), len(set(captures)))

    def test_payment_amount_matches_items(self):
        totals = {}
        for item in self.rows["order_items"]:
            oid = item["order_id"]
            totals[oid] = totals.get(oid, Decimal("0.00")) + (
                Decimal(item["unit_price"]) * item["quantity"] - Decimal(item["discount_amount"])
            )
        for payment in self.rows["payments"]:
            if payment["status"] == "captured":
                self.assertEqual(Decimal(payment["amount"]), totals[payment["order_id"]])

    def test_bad_capture_rejected(self):
        rows = {key: [dict(row) for row in value] for key, value in self.rows.items()}
        capture = next(p for p in rows["payments"] if p["status"] == "captured")
        capture["amount"] = "0.01"
        with self.assertRaisesRegex(ValueError, "reconciled"):
            validate_transactions(rows, rows, self.config)

    def test_capture_for_cancelled_order_rejected(self):
        rows = {key: [dict(row) for row in value] for key, value in self.rows.items()}
        capture = next(p for p in rows["payments"] if p["status"] == "captured")
        next(o for o in rows["orders"] if o["order_id"] == capture["order_id"])["status"] = "cancelled"
        with self.assertRaisesRegex(ValueError, "Non-completed"):
            validate_transactions(rows, rows, self.config)

    def test_invalid_product_fk_rejected(self):
        rows = {key: [dict(row) for row in value] for key, value in self.rows.items()}
        rows["order_items"][0]["product_id"] = -1
        with self.assertRaisesRegex(ValueError, "item FK"):
            validate_transactions(rows, rows, self.config)

    def test_determinism(self):
        self.assertEqual(self.rows, generate(self.config))

    def test_end_to_end_validation(self):
        validate(self.rows, self.config)
