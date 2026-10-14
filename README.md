# Email Pipeline: Convert Leads

The outreach stage of an automated lead-generation system for a web design agency. It takes a CSV of local businesses produced by an upstream lead generator (Google Maps data + lead scoring), sorts them into priority tiers, personalizes the pitch variables for each business, and uploads them to the right [Instantly.ai](https://instantly.ai) campaign. Instantly then handles inbox warmup, scheduling, and delivery.

## How it works

```
leads.csv
    │
    ▼
pipeline.py
    ├── 1. Load CSV
    ├── 2. Filter & tier leads (skip anything already in sent_log.json)
    │       Tier 1: worth_reaching_out=1 + has email
    │       Tier 2: has_website=0 + has email
    │       Tier 3: has_website=1 + has email
    ├── 3. Build a payload per lead
    │       business_type → from the CSV category
    │       cta_type      → "order" / "booking" / "contact", looked up from category
    │       campaign      → "has website" or "no website" campaign
    ├── 4. Upload to Instantly (POST /api/v1/lead/add)
    └── 5. Append the lead to sent_log.json
```

- **Tiering:** leads flagged as worth reaching out go first, then businesses with no website (the strongest pitch), then everyone else with an email.
- **Personalization:** each lead carries `business_name`, `business_type`, and `cta_type` as Instantly custom variables, so one template reads naturally for a coffee shop ("order online") or a barber ("book online").
- **Two campaigns:** businesses without a website get a different pitch than those that already have one.
- **Idempotent runs:** every upload is appended to `sent_log.json` (JSON Lines), and Instantly is told to skip leads already in the workspace, so re-running on an overlapping CSV never double-sends.
- **Failure isolation:** one bad lead is logged and skipped without stopping the batch. Uploads are lightly rate-limited.

## Project layout

| File | Purpose |
|---|---|
| `pipeline.py` | CLI entry point; orchestrates load → tier → upload → log |
| `filter.py` | Splits leads into the three tiers |
| `template.py` | Builds each lead's payload (CTA type, campaign) |
| `instantly.py` | Instantly REST API client |
| `tracker.py` | Reads and appends the `sent_log.json` dedup log |
| `config.py` | Loads secrets from `.env`; holds the category → CTA map |
| `tests/` | pytest suite covering each module |

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:

```
INSTANTLY_API_KEY=your_api_key
INSTANTLY_CAMPAIGN_HAS_WEBSITE=campaign_id_for_businesses_with_a_site
INSTANTLY_CAMPAIGN_NO_WEBSITE=campaign_id_for_businesses_without_a_site
```

## Usage

Preview what would be sent without calling the API:

```bash
python pipeline.py --csv leads.csv --dry-run
```

Upload for real:

```bash
python pipeline.py --csv leads.csv
```

### Input CSV

| Column | Description |
|---|---|
| `id` | Unique lead ID, used for deduplication |
| `business_name` | Business name |
| `email` | Contact email; rows without one are skipped |
| `category` | Business type, e.g. `coffee shops`, `barber shops` |
| `has_website` | `1` or `0` |
| `worth_reaching_out` | `1` for high-priority leads |

Categories not in `CTA_MAP` (in `config.py`) default to a `contact` CTA and log a warning. Add new verticals there.

## Tests

```bash
python -m pytest
```
