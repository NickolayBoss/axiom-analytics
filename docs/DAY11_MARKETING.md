# Day 11 — Campaigns, Sessions and Funnel Events

**Implementation:** Nine synthetic CSV tables; refunds are deferred to Day 12.

## Generated entities

- **campaigns:** 24 fictional campaigns, channel, start/end dates and one whole-campaign spend value (CU). Campaign IDs and RNG are stable.
- **sessions:** 100,000 sessions, 1–90 minutes, anonymous sessions and optional campaign references. Known customers must exist before session start. Campaign assignment requires the campaign to be active at session start.
- **events:** session_start, product_view, add_to_cart, checkout_start, purchase, with strictly increasing timestamps inside each session. Each session follows a prefix of the canonical funnel; non-purchasing sessions drop off at a sampled stage.
- **purchase linkage:** up to 10% of sessions are assigned a distinct eligible completed order. Each linked session has the same customer as the order, and purchase occurs at/after placement. The remaining completed orders are legitimate financially but have no linked session purchase.

## Modeling caveats

- Sessions without campaigns are **unattributed**, not organic by default.
- Attribution is single-session descriptive only; there is no cross-device or multi-touch claim.
- Campaign spend is whole-campaign. Daily ROAS cannot be computed without allocation assumptions.
- Events are synthetic and not evidence of real customer behavior.
- The generator does not yet create refunds. Full ten-table import and SQL quality-gate verification are future acceptance checks.
- Campaign dates are created within the configured observation year; the baseline assumes a full calendar year.

## Run

```bash
python -m unittest discover -s tests -v
python -m src.generator --validate-only
python -m src.generator --output data/generated
```

The output contains nine CSVs and a manifest of actual counts and SHA-256 hashes. RNG streams for campaigns, sessions and events are independent of product and order streams. `tests/test_marketing.py` covers referential integrity, ordered funnels, matching purchase customers, and invalid attribution/product references.

## CI and verification

The existing Python workflow is **manual-only** to avoid one notification per commit: [Run workflow](../.github/workflows/day09-generator.yml). The new Day 11 source has been published, but a successful Actions run is **not yet confirmed**. Do not mark Issue #10 complete until the current revision is verified.

## Next

Day 12: refunds, comprehensive data-quality suite, and a clean PostgreSQL import/quality-gate test.
