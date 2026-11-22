"""Day 11 marketing and funnel invariants."""
import copy
from pathlib import Path
import unittest

from src.generator import generate, parse_config, validate
from src.marketing_generator import STAGES, validate_marketing

CONFIG = Path(__file__).resolve().parents[1] / "config" / "synthetic_data.json"

class MarketingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, _ = parse_config(CONFIG)
        cls.rows = generate(cls.config)

    def test_counts_and_integrity(self):
        result = validate_marketing(self.rows, self.rows, self.config)
        self.assertEqual(result["campaigns"], 24)
        self.assertEqual(result["sessions"], 100000)
        self.assertGreater(result["linked_purchases"], 0)
        self.assertGreater(result["events"], 100000)

    def test_session_funnel(self):
        by_session = {}
        for event in self.rows["events"]:
            by_session.setdefault(event["session_id"], []).append(event)
        for events in by_session.values():
            self.assertEqual([e["event_type"] for e in events],
                             list(STAGES[:len(events)]))
            self.assertEqual(len({e["occurred_at"] for e in events}), len(events))

    def test_purchase_customer_and_time(self):
        sessions = {s["session_id"]: s for s in self.rows["sessions"]}
        orders = {o["order_id"]: o for o in self.rows["orders"]}
        for event in self.rows["events"]:
            if event["event_type"] == "purchase":
                order = orders[event["order_id"]]
                self.assertEqual(order["status"], "completed")
                self.assertEqual(sessions[event["session_id"]]["customer_id"], order["customer_id"])
                self.assertGreaterEqual(event["occurred_at"], order["placed_at"])

    def test_orphan_product_rejected(self):
        rows = {k: [dict(r) for r in v] for k, v in self.rows.items()}
        view = next(e for e in rows["events"] if e["event_type"] == "product_view")
        view["product_id"] = -1
        with self.assertRaisesRegex(ValueError, "product reference"):
            validate_marketing(rows, rows, self.config)

    def test_invalid_campaign_rejected(self):
        rows = {k: [dict(r) for r in v] for k, v in self.rows.items()}
        linked = next(s for s in rows["sessions"] if s["campaign_id"] != "")
        linked["campaign_id"] = -1
        with self.assertRaisesRegex(ValueError, "campaign attribution"):
            validate_marketing(rows, rows, self.config)

    def test_validation(self):
        validate(self.rows, self.config)
