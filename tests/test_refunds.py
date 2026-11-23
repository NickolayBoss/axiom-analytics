"""Day 12 regression tests: refund invariants and quality reporting."""
from decimal import Decimal
from pathlib import Path
import unittest

from src.generator import generate, parse_config, validate
from src.refund_quality import validate_refunds, quality_report

CONFIG = Path(__file__).resolve().parents[1] / "config" / "synthetic_data.json"

class RefundQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, _ = parse_config(CONFIG)
        cls.rows = generate(cls.config)

    def clone(self):
        return {name: [dict(row) for row in records] for name, records in self.rows.items()}

    def test_ten_tables(self):
        self.assertEqual(len(self.rows), 10)
        self.assertEqual(quality_report(self.rows, self.config)["status"], "passed")

    def test_settled_refund_cap(self):
        payments = {p["payment_id"]: p for p in self.rows["payments"]}
        settled = {}
        for refund in self.rows["refunds"]:
            self.assertEqual(payments[refund["payment_id"]]["status"], "captured")
            if refund["status"] == "settled":
                pid = refund["payment_id"]
                settled[pid] = settled.get(pid, Decimal("0")) + Decimal(refund["amount"])
        for pid, total in settled.items():
            self.assertLessEqual(total, Decimal(payments[pid]["amount"]))

    def test_invalid_refund_payment(self):
        rows = self.clone()
        if not rows["refunds"]:
            self.skipTest("No refunds generated with this seed")
        rows["refunds"][0]["payment_id"] = -1
        with self.assertRaisesRegex(ValueError, "captured payment"):
            validate_refunds(rows, self.config)

    def test_excessive_refund(self):
        rows = self.clone()
        if not rows["refunds"]:
            self.skipTest("No refunds generated with this seed")
        refund = rows["refunds"][0]
        payment = next(p for p in rows["payments"] if p["payment_id"] == refund["payment_id"])
        refund["status"] = "settled"
        refund["refunded_at"] = refund["requested_at"]
        refund["amount"] = f"{Decimal(payment['amount']) + Decimal('0.01'):.2f}"
        with self.assertRaisesRegex(ValueError, "exceeds"):
            validate_refunds(rows, self.config)

    def test_invalid_settlement_timestamp(self):
        rows = self.clone()
        if not rows["refunds"]:
            self.skipTest("No refunds generated with this seed")
        refund = rows["refunds"][0]
        refund["status"] = "pending"
        refund["refunded_at"] = refund["requested_at"]
        with self.assertRaisesRegex(ValueError, "Unsettled"):
            validate_refunds(rows, self.config)

    def test_full_validation(self):
        validate(self.rows, self.config)
