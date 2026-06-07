# Email Pipeline Design
**Date:** 2026-06-07  
**Status:** Approved

## Overview

A Python script that reads a leads CSV (exported from the existing lead generator), filters and tiers leads, maps template variables using if/else logic, and uploads each lead to the appropriate Instantly.ai campaign via the REST API. Instantly handles warmup, scheduling, and delivery. A local `sent_log.json` prevents duplicate sends across runs.

---

## Architecture & Data Flow

```
leads.csv
    │
    ▼
pipeline.py
    ├── 1. Load CSV
    ├── 2. Filter & tier leads (skip IDs already in sent_log.json)
    │       Tier 1: worth_reaching_out=1 + has email
    │       Tier 2: has_website=0 + has email  (not tier 1)
    │       Tier 3: has_website=1 + has email  (not tier 1 or 2)
    ├── 3. Build lead payload per entry
    │       business_name    → CSV business_name field
    │       business_type    → CSV category field
    │       cta_type         → if/else lookup on category (see CTA_MAP)
    │       campaign_id      → Template A (tiers 1+3) or Template B (tier 2)
    ├── 4. Upload each lead to Instantly via POST /api/v1/lead/add
    └── 5. Append sent lead metadata to sent_log.json
```

---

## Components

### `pipeline.py`
Single entry point. Usage:
```
python pipeline.py --csv leads.csv
```
Orchestrates loading, filtering, variable mapping, API upload, and logging.

### `config.py`
Holds the CTA_MAP dict and reads secrets from `.env`. No hardcoded credentials.

```python
CTA_MAP = {
    "coffee shops":           "order",
    "barber shops":           "booking",
    "med spas":               "booking",
    "workout yoga studios":   "booking",
    "photographers":          "booking",
    "moving companies":       "booking",
    "lawn services":          "booking",
    "landscapers":            "booking",
    "freelancers":            "contact",
    "real estate agents":     "contact",
    "bike repair shops":      "contact",
    "watch repair shops":     "contact",
    "roofing companies":      "contact",
    "construction contractors": "contact",
    "plumbing companies":     "contact",
}
```

Unknown categories fall back to `"contact"` with a logged warning.

### `.env`
```
INSTANTLY_API_KEY=your_key_here
INSTANTLY_CAMPAIGN_HAS_WEBSITE=campaign_id_for_template_A
INSTANTLY_CAMPAIGN_NO_WEBSITE=campaign_id_for_template_B
```

### `sent_log.json`
Append-only. Each entry:
```json
{"id": 105, "email": "info@example.com", "business_name": "OU Beauty", "tier": 1, "sent_at": "2026-06-07T14:32:00"}
```

### `.gitignore`
Covers: `.env`, `sent_log.json`, `ex.csv`, `*.csv`

---

## Email Templates

Both templates live in Instantly's campaign editor. The script supplies variables; Instantly performs substitution.

**Template A — has website (Tiers 1 & 3):**
```
Hi {{business_name}},

I'm a Cornell student who builds websites for local businesses, and I came
across you guys while looking at {{business_type}}s in the area. I saw you
have great reviews and a strong local reputation, but I thought your
website/online presence could show that off a little better.

I put together a quick refreshed concept with cleaner visuals, reviews, and
a simple {{cta_type}} section — free of charge.

Would you be open to taking a look?

If you're not interested, just reply "no thanks" and I won't follow up.

Best,
William
```

**Template B — no website (Tier 2):**
```
Hi {{business_name}},

I'm a Cornell student who builds websites for local businesses, and I came
across you guys while looking at {{business_type}}s in the area. I saw you
have great reviews and a strong local reputation, but no website.

I put together a quick refreshed concept with cleaner visuals, reviews, and
a simple {{cta_type}} section — free of charge.

Would you be open to taking a look?

If you're not interested, just reply "no thanks" and I won't follow up.

Best,
William
```

---

## Instantly Campaign Settings

- **Send window:** 9am–5pm PST (hardcoded — does not follow operator timezone)
- **Daily limit:** 30–40 emails/day to start; increase to 50 after one more week
- **Delay between emails:** 120–180 seconds (randomized by Instantly)
- **From address:** will@williamdamato.com
- **Two campaigns required:** one per template variant

---

## Error Handling

| Situation | Behavior |
|---|---|
| Lead has no email | Skipped silently before upload |
| Lead ID already in sent_log.json | Skipped, no API call made |
| Category not in CTA_MAP | Log warning, use `"contact"` as fallback |
| Instantly API error (network, rate limit, bad key) | Print error, halt run cleanly — lead NOT written to sent_log.json so it retries next run |

---

## What Instantly Handles (not the script's responsibility)

- Email warmup
- Rate limiting and send scheduling
- Open/reply tracking
- Spam avoidance (delays, randomization, warmup reputation)
