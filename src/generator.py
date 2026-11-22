"""AXIOM Day 09: deterministic customer and catalog CSV generator."""
import argparse
import csv
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import random

from src.order_generator import FIELDS as TRANSACTION_FIELDS, generate_transactions, validate_transactions
from src.marketing_generator import FIELDS as MARKETING_FIELDS, generate_marketing, validate_marketing

VERSION = "0.3.0"
FIELDS = {
    "categories": ["category_id", "category_name"],
    "products": ["product_id", "category_id", "product_name", "list_price", "active"],
    "customers": ["customer_id", "created_at", "region", "acquisition_source"],
    **TRANSACTION_FIELDS,
    **MARKETING_FIELDS,
}
CONFIG_KEYS = {"schema_version","seed","currency","timezone","observation_start","observation_end","counts","targets_approximate","customer_region_weights","acquisition_source_weights","order_status_weights","order_line_count_weights","discount_probability","discount_min_rate","discount_max_rate","refund_incidence_rate","anonymous_session_rate","campaign_session_rate","session_duration_minutes","product_price_cu","notes"}

def parse_config(path):
    raw = Path(path).read_bytes()
    config = json.loads(raw)
    if set(config) - CONFIG_KEYS:
        raise ValueError("Unknown configuration keys")
    if (config["schema_version"], config["currency"], config["timezone"]) != ("1.0", "CU", "UTC"):
        raise ValueError("Unsupported configuration")
    if type(config["seed"]) is not int or config["seed"] < 0:
        raise ValueError("Invalid seed")
    for name in ("categories", "products", "customers", "orders", "campaigns", "sessions"):
        if type(config["counts"][name]) is not int or config["counts"][name] <= 0:
            raise ValueError("Invalid count: " + name)
    if config["counts"]["products"] < config["counts"]["categories"]:
        raise ValueError("Products must cover categories")
    for name in ("customer_region_weights", "acquisition_source_weights"):
        weights = config[name]
        if not weights or any(type(x) not in (float, int) or not 0 <= x <= 1 for x in weights.values()) or abs(sum(weights.values()) - 1) > 1e-9:
            raise ValueError("Invalid probabilities: " + name)
    if not 0 < config["product_price_cu"]["min"] <= config["product_price_cu"]["max"] <= 999999:
        raise ValueError("Invalid price range")
    start = datetime.fromisoformat(config["observation_start"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(config["observation_end"].replace("Z", "+00:00"))
    if not start.tzinfo or not end.tzinfo or start >= end:
        raise ValueError("Invalid observation window")
    return config, raw

def generate(config):
    seed = config["seed"]
    product_rng = random.Random(f"{seed}:211")
    customer_rng = random.Random(f"{seed}:307")
    nc, np, nu = (config["counts"][name] for name in ("categories", "products", "customers"))
    categories = [{"category_id": i, "category_name": f"Category {i:02d}"} for i in range(1, nc + 1)]
    products = []
    lo, hi = config["product_price_cu"]["min"], config["product_price_cu"]["max"]
    for i in range(1, np + 1):
        price = Decimal(str(lo * (hi / lo) ** product_rng.random())).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        products.append({"product_id": i, "category_id": (i - 1) % nc + 1, "product_name": f"Product {i:04d}", "list_price": f"{price:.2f}", "active": "true" if product_rng.random() < 0.94 else "false"})
    start = datetime.fromisoformat(config["observation_start"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(config["observation_end"].replace("Z", "+00:00"))
    seconds = int((end - start).total_seconds())
    region = config["customer_region_weights"]
    source = config["acquisition_source_weights"]
    customers = []
    for i in range(1, nu + 1):
        timestamp = (start + timedelta(seconds=customer_rng.randint(0, seconds))).strftime("%Y-%m-%dT%H:%M:%SZ")
        customers.append({"customer_id": i, "created_at": timestamp, "region": customer_rng.choices(list(region), weights=list(region.values()))[0], "acquisition_source": customer_rng.choices(list(source), weights=list(source.values()))[0]})
    base = {"categories": categories, "products": products, "customers": customers}
    transactions = generate_transactions(base, config)
    combined = {**base, **transactions}
    return {**combined, **generate_marketing(combined, config)}

def validate(rows, config):
    for table, fields in FIELDS.items():
        records = rows[table]
        if table in config["counts"] and len(records) != config["counts"][table]:
            raise ValueError("Unexpected count: " + table)
        pk = {"categories": "category_id", "products": "product_id", "customers": "customer_id", "orders": "order_id", "order_items": "order_item_id", "payments": "payment_id", "campaigns": "campaign_id", "sessions": "session_id", "events": "event_id"}[table]
        if len({r[pk] for r in records}) != len(records) or any(set(r) != set(fields) for r in records):
            raise ValueError("Invalid keys/columns: " + table)
    category_ids = {r["category_id"] for r in rows["categories"]}
    if len({r["category_name"] for r in rows["categories"]}) != len(category_ids):
        raise ValueError("Duplicate category name")
    for r in rows["products"]:
        if r["category_id"] not in category_ids or Decimal(r["list_price"]) < 0 or r["active"] not in ("true", "false"):
            raise ValueError("Invalid product")
    for r in rows["customers"]:
        if r["region"] not in config["customer_region_weights"] or r["acquisition_source"] not in config["acquisition_source_weights"] or not config["observation_start"] <= r["created_at"] <= config["observation_end"]:
            raise ValueError("Invalid customer")
    transaction_summary = validate_transactions(rows, rows, config)
    marketing_summary = validate_marketing(rows, rows, config)
    return {**transaction_summary, **marketing_summary}

def publish(rows, config, raw, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"generator_version": VERSION, "phase": "day-11-marketing-sessions-events", "seed": config["seed"], "currency": config["currency"], "observation_start": config["observation_start"], "observation_end": config["observation_end"], "config_sha256": hashlib.sha256(raw).hexdigest(), "files": {}, "validation": {"status": "passed", "scope": "nine tables (excluding refunds); PostgreSQL import not checked"}}
    for table, records in rows.items():
        path = output / (table + ".csv")
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS[table], lineterminator="\n")
            writer.writeheader()
            writer.writerows(records)
        manifest["files"][path.name] = {"rows": len(records), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    (output / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return manifest

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/synthetic_data.json"))
    parser.add_argument("--output", type=Path, default=Path("data/generated"))
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    config, raw = parse_config(args.config)
    rows = generate(config)
    validate(rows, config)
    if args.validate_only:
        print("PASS: Day 11 records validated in memory")
    else:
        print(json.dumps(publish(rows, config, raw, args.output), sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
