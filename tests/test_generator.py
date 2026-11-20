"""Day 09 generator checks. Run: python -m unittest discover -s tests -v."""
import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from src.generator import FIELDS, generate, parse_config, publish, validate

CONFIG = Path(__file__).resolve().parents[1] / "config" / "synthetic_data.json"

class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.raw = parse_config(CONFIG)
        cls.rows = generate(cls.config)

    def test_counts(self):
        for table in FIELDS:
            self.assertEqual(len(self.rows[table]), self.config["counts"][table])

    def test_validation(self):
        validate(self.rows, self.config)

    def test_determinism(self):
        self.assertEqual(self.rows, generate(self.config))

    def test_seed_changes_data(self):
        config = copy.deepcopy(self.config)
        config["seed"] += 1
        self.assertNotEqual(self.rows["customers"], generate(config)["customers"])

    def test_unique_sequential_ids(self):
        for table, key in (("categories","category_id"),("products","product_id"),("customers","customer_id")):
            self.assertEqual([r[key] for r in self.rows[table]], list(range(1, len(self.rows[table]) + 1)))

    def test_products(self):
        category_ids = {r["category_id"] for r in self.rows["categories"]}
        for row in self.rows["products"]:
            self.assertIn(row["category_id"], category_ids)
            self.assertGreaterEqual(Decimal(row["list_price"]), Decimal("5"))
            self.assertLessEqual(Decimal(row["list_price"]), Decimal("1500"))

    def test_repeatable_files(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            m1 = publish(self.rows, self.config, self.raw, Path(a))
            m2 = publish(self.rows, self.config, self.raw, Path(b))
            self.assertEqual(m1, m2)
            for name, info in m1["files"].items():
                content = (Path(a) / name).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), info["sha256"])
                self.assertEqual(content, (Path(b) / name).read_bytes())
                self.assertEqual(content.count(b"\n"), info["rows"] + 1)
            self.assertEqual((Path(a) / "manifest.json").read_bytes(), (Path(b) / "manifest.json").read_bytes())

    def test_bad_probabilities(self):
        with tempfile.TemporaryDirectory() as d:
            config = copy.deepcopy(self.config)
            config["customer_region_weights"]["North"] = 0.7
            path = Path(d) / "bad.json"
            path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, "probabilities"):
                parse_config(path)

    def test_unknown_key(self):
        with tempfile.TemporaryDirectory() as d:
            config = copy.deepcopy(self.config)
            config["unknown"] = 1
            path = Path(d) / "bad.json"
            path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, "Unknown"):
                parse_config(path)

    def test_duplicate_pk(self):
        rows = {k: [dict(r) for r in v] for k, v in self.rows.items()}
        rows["categories"][1]["category_id"] = 1
        with self.assertRaisesRegex(ValueError, "Invalid keys"):
            validate(rows, self.config)
