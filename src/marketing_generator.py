"""Day 11: deterministic campaigns, sessions and ordered funnel events."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import calendar
import random

FIELDS = {
    "campaigns": ["campaign_id", "campaign_name", "channel", "start_date", "end_date", "spend"],
    "sessions": ["session_id", "customer_id", "campaign_id", "started_at", "ended_at"],
    "events": ["event_id", "session_id", "occurred_at", "event_type", "order_id", "product_id"],
}
STAGES = ("session_start", "product_view", "add_to_cart", "checkout_start", "purchase")

def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def generate_marketing(base, config):
    """Produce FK-valid rows, with purchase events only for eligible matching customers."""
    rng_campaign = random.Random(f"{config['seed']}:503")
    rng_session = random.Random(f"{config['seed']}:601")
    rng_event = random.Random(f"{config['seed']}:701")
    start, end = dt(config["observation_start"]), dt(config["observation_end"])
    campaigns = []
    channels = ("paid_search", "social", "display", "affiliate")
    count = config["counts"]["campaigns"]
    for i in range(1, count + 1):
        month = (i - 1) % 12 + 1
        year = start.year
        first = datetime(year, month, 1, tzinfo=timezone.utc)
        last = datetime(year, month, calendar.monthrange(year, month)[1], tzinfo=timezone.utc)
        first, last = max(first, start), min(last, end)
        if first > last:
            raise ValueError("Campaign observation period must cover all twelve months")
        campaigns.append({"campaign_id": i, "campaign_name": f"Campaign {i:03d}",
                          "channel": channels[(i - 1) % len(channels)],
                          "start_date": first.date().isoformat(), "end_date": last.date().isoformat(),
                          "spend": f"{Decimal(rng_campaign.randint(10000, 1500000)) / 100:.2f}"})
    customers = base["customers"]
    customer_created = {c["customer_id"]: dt(c["created_at"]) for c in customers}
    # For every purchase, the linked session must have the same customer and precede checkout.
    # Reserve a small sample of completed orders with enough time for the full funnel.
    eligible = [o for o in base["orders"] if o["status"] == "completed"
                and dt(o["placed_at"]) - customer_created[o["customer_id"]] >= timedelta(minutes=20)
                and dt(o["placed_at"]) >= start + timedelta(minutes=20)]
    eligible.sort(key=lambda o: o["order_id"])
    reserved = min(len(eligible), max(1, config["counts"]["sessions"] // 10))
    linked = eligible[:reserved]
    sessions, events = [], []
    event_id = 0
    def add_event(sid, when, kind, order="", product=""):
        nonlocal event_id
        event_id += 1
        events.append({"event_id": event_id, "session_id": sid, "occurred_at": iso(when),
                       "event_type": kind, "order_id": order, "product_id": product})
    product_ids = [p["product_id"] for p in base["products"]]
    for sid in range(1, config["counts"]["sessions"] + 1):
        linked_order = linked[sid - 1] if sid <= len(linked) else None
        if linked_order:
            customer_id = linked_order["customer_id"]
            placed = dt(linked_order["placed_at"])
            began = placed - timedelta(minutes=10)
            duration = 16
        else:
            customer_id = "" if rng_session.random() < config["anonymous_session_rate"] else rng_session.choice(customers)["customer_id"]
            duration = rng_session.randint(config["session_duration_minutes"]["min"],
                                           config["session_duration_minutes"]["max"])
            earliest = start if customer_id == "" else max(start, customer_created[customer_id])
            latest = end - timedelta(minutes=duration)
            if earliest > latest:
                # Use an anonymous session rather than backdating a known customer's registration.
                customer_id = ""
                earliest = start
            began = earliest + timedelta(seconds=rng_session.randint(0, int((latest - earliest).total_seconds())))
        finished = began + timedelta(minutes=duration)
        campaign_id = ""
        if rng_session.random() < config["campaign_session_rate"]:
            choices = [c for c in campaigns if c["start_date"] <= began.date().isoformat() <= c["end_date"]]
            if choices:
                campaign_id = rng_session.choice(choices)["campaign_id"]
        sessions.append({"session_id": sid, "customer_id": customer_id, "campaign_id": campaign_id,
                         "started_at": iso(began), "ended_at": iso(finished)})
        add_event(sid, began, "session_start")
        # Non-purchasing sessions drop off at a sampled stage.
        reached = 5 if linked_order else rng_event.choices([1, 2, 3, 4], weights=[0.24, 0.37, 0.26, 0.13])[0]
        product = rng_event.choice(product_ids)
        for step, kind in enumerate(STAGES[1:reached], 1):
            occurred = (began + timedelta(minutes=10) if kind == "purchase" else
                        began + timedelta(seconds=max(1, int(duration * 60 * step / (reached + 1)))))
            add_event(sid, occurred, kind,
                      linked_order["order_id"] if kind == "purchase" else "",
                      product if kind in ("product_view", "add_to_cart") else "")
    return {"campaigns": campaigns, "sessions": sessions, "events": events}

def validate_marketing(base, tables, config):
    campaigns = tables["campaigns"]
    sessions = tables["sessions"]
    events = tables["events"]
    if len(campaigns) != config["counts"]["campaigns"] or len(sessions) != config["counts"]["sessions"]:
        raise ValueError("Marketing count mismatch")
    customers = {c["customer_id"]: c["created_at"] for c in base["customers"]}
    products = {p["product_id"] for p in base["products"]}
    orders = {o["order_id"]: o for o in base["orders"]}
    campaign_map = {c["campaign_id"]: c for c in campaigns}
    session_map = {s["session_id"]: s for s in sessions}
    if len(campaign_map) != len(campaigns) or len(session_map) != len(sessions):
        raise ValueError("Duplicate campaign/session key")
    for c in campaigns:
        if c["start_date"] > c["end_date"] or Decimal(c["spend"]) < 0:
            raise ValueError("Invalid campaign")
    for s in sessions:
        if s["started_at"] >= s["ended_at"] or s["started_at"] < config["observation_start"] or s["ended_at"] > config["observation_end"]:
            raise ValueError("Invalid session bounds")
        if s["customer_id"] != "" and (s["customer_id"] not in customers or s["started_at"] < customers[s["customer_id"]]):
            raise ValueError("Invalid session customer")
        if s["campaign_id"] != "":
            c = campaign_map.get(s["campaign_id"])
            if not c or not c["start_date"] <= s["started_at"][:10] <= c["end_date"]:
                raise ValueError("Invalid campaign attribution")
    by_session = {}
    seen_ids = set()
    purchase_orders = set()
    for e in events:
        if e["event_id"] in seen_ids or e["session_id"] not in session_map:
            raise ValueError("Duplicate event ID or orphan session")
        seen_ids.add(e["event_id"])
        s = session_map[e["session_id"]]
        if not s["started_at"] <= e["occurred_at"] <= s["ended_at"] or e["event_type"] not in STAGES:
            raise ValueError("Invalid event bounds/type")
        if e["event_type"] in ("product_view", "add_to_cart"):
            if e["product_id"] not in products:
                raise ValueError("Missing product reference")
        elif e["product_id"] != "":
            raise ValueError("Unexpected product reference")
        if e["event_type"] == "purchase":
            o = orders.get(e["order_id"])
            if not o or o["status"] != "completed" or s["customer_id"] != o["customer_id"]:
                raise ValueError("Invalid purchase order/customer")
            if e["occurred_at"] < o["placed_at"] or e["order_id"] in purchase_orders:
                raise ValueError("Invalid purchase time/duplicate order")
            purchase_orders.add(e["order_id"])
        elif e["order_id"] != "":
            raise ValueError("Unexpected order reference")
        by_session.setdefault(e["session_id"], []).append(e)
    for sid, stream in by_session.items():
        if not stream or stream[0]["event_type"] != "session_start":
            raise ValueError("Missing session start")
        if len([e for e in stream if e["event_type"] == "purchase"]) > 1:
            raise ValueError("Multiple purchases in session")
        last = ""
        previous_stage = -1
        for e in stream:
            stage = STAGES.index(e["event_type"])
            if stage != previous_stage + 1 or (last and e["occurred_at"] <= last):
                raise ValueError("Invalid funnel ordering")
            previous_stage, last = stage, e["occurred_at"]
    if len(by_session) != len(sessions):
        raise ValueError("Session missing events")
    return {"campaigns": len(campaigns), "sessions": len(sessions),
            "events": len(events), "linked_purchases": len(purchase_orders)}
