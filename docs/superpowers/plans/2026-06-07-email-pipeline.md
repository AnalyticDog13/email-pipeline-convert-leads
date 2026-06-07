# Email Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI that reads a leads CSV, tiers leads by quality, maps template variables, and uploads each lead to the correct Instantly.ai campaign via API — tracking sent leads locally to prevent duplicates.

**Architecture:** A single `pipeline.py` entry point orchestrates five focused modules: `config` (CTA map + env), `filter` (tiering), `template` (variable mapping), `tracker` (sent log), and `instantly` (API client). No API calls are made for template substitution — all variable mapping is pure if/else logic.

**Tech Stack:** Python 3.10+, `requests`, `python-dotenv`, `pytest`

---

## File Map

| File | Responsibility |
|---|---|
| `pipeline.py` | Entry point — orchestrates load → filter → map → upload → log |
| `config.py` | CTA_MAP dict + loads `.env` into constants |
| `filter.py` | Reads CSV, returns leads sorted into tiers 1/2/3 |
| `template.py` | Maps one CSV row → `{business_name, business_type, cta_type, campaign_id}` |
| `tracker.py` | Reads/writes `sent_log.json` |
| `instantly.py` | Wraps Instantly REST API — single `upload_lead()` function |
| `tests/test_filter.py` | Unit tests for tiering logic |
| `tests/test_template.py` | Unit tests for variable mapping |
| `tests/test_tracker.py` | Unit tests for sent log read/write |
| `tests/test_instantly.py` | Unit tests for API client (mocked HTTP) |
| `requirements.txt` | `requests`, `python-dotenv`, `pytest` |
| `.env.example` | Template — lists required env vars with blank values |
| `.gitignore` | Covers `.env`, `sent_log.json`, `*.csv` |

---

## Task 1: Project Scaffolding

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create `.gitignore`**

```
.env
sent_log.json
*.csv
__pycache__/
.pytest_cache/
*.pyc
```

- [ ] **Step 2: Create `requirements.txt`**

```
requests==2.31.0
python-dotenv==1.0.1
pytest==8.2.0
```

- [ ] **Step 3: Create `.env.example`**

```
INSTANTLY_API_KEY=
INSTANTLY_CAMPAIGN_HAS_WEBSITE=
INSTANTLY_CAMPAIGN_NO_WEBSITE=
```

- [ ] **Step 4: Create `tests/__init__.py`**

Empty file — makes `tests/` a package.

```python
```

- [ ] **Step 5: Install dependencies**

```
pip install -r requirements.txt
```

Expected: packages install without errors.

- [ ] **Step 6: Commit**

```bash
git add .gitignore requirements.txt .env.example tests/__init__.py
git commit -m "feat: project scaffolding"
```

---

## Task 2: `config.py` — CTA Map + Environment

**Files:**
- Create: `config.py`

- [ ] **Step 1: Create `config.py`**

```python
import os
from dotenv import load_dotenv

load_dotenv()

INSTANTLY_API_KEY = os.getenv("INSTANTLY_API_KEY")
INSTANTLY_CAMPAIGN_HAS_WEBSITE = os.getenv("INSTANTLY_CAMPAIGN_HAS_WEBSITE")
INSTANTLY_CAMPAIGN_NO_WEBSITE = os.getenv("INSTANTLY_CAMPAIGN_NO_WEBSITE")

CTA_MAP = {
    "coffee shops":             "order",
    "barber shops":             "booking",
    "med spas":                 "booking",
    "workout yoga studios":     "booking",
    "photographers":            "booking",
    "moving companies":         "booking",
    "lawn services":            "booking",
    "landscapers":              "booking",
    "freelancers":              "contact",
    "real estate agents":       "contact",
    "bike repair shops":        "contact",
    "watch repair shops":       "contact",
    "roofing companies":        "contact",
    "construction contractors": "contact",
    "plumbing companies":       "contact",
}
```

- [ ] **Step 2: Verify it loads cleanly**

```
python -c "import config; print(config.CTA_MAP['coffee shops'])"
```

Expected output: `order`

- [ ] **Step 3: Commit**

```bash
git add config.py
git commit -m "feat: add config with CTA map and env loading"
```

---

## Task 3: `filter.py` + Tests — Lead Tiering

**Files:**
- Create: `filter.py`
- Create: `tests/test_filter.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_filter.py
import pytest
from filter import tier_leads

def _row(email="e@x.com", has_website="0", worth_reaching_out="0"):
    return {
        "id": "1",
        "business_name": "Test Biz",
        "category": "barber shops",
        "email": email,
        "has_website": has_website,
        "worth_reaching_out": worth_reaching_out,
    }

def test_tier1_worth_reaching_out_with_email():
    leads = [_row(has_website="1", worth_reaching_out="1")]
    t1, t2, t3 = tier_leads(leads, sent_ids=set())
    assert len(t1) == 1
    assert t2 == []
    assert t3 == []

def test_tier2_no_website_with_email():
    leads = [_row(has_website="0", worth_reaching_out="0")]
    t1, t2, t3 = tier_leads(leads, sent_ids=set())
    assert t1 == []
    assert len(t2) == 1
    assert t3 == []

def test_tier3_has_website_not_flagged():
    leads = [_row(has_website="1", worth_reaching_out="0")]
    t1, t2, t3 = tier_leads(leads, sent_ids=set())
    assert t1 == []
    assert t2 == []
    assert len(t3) == 1

def test_no_email_excluded_from_all_tiers():
    leads = [_row(email="", has_website="1", worth_reaching_out="1")]
    t1, t2, t3 = tier_leads(leads, sent_ids=set())
    assert t1 == t2 == t3 == []

def test_already_sent_excluded():
    leads = [_row(has_website="1", worth_reaching_out="1")]
    t1, t2, t3 = tier_leads(leads, sent_ids={"1"})
    assert t1 == t2 == t3 == []

def test_tier1_beats_tier2_when_no_website_but_flagged():
    # worth_reaching_out=1 overrides has_website=0 — goes to tier 1
    leads = [_row(has_website="0", worth_reaching_out="1")]
    t1, t2, t3 = tier_leads(leads, sent_ids=set())
    assert len(t1) == 1
    assert t2 == []
```

- [ ] **Step 2: Run tests to confirm they fail**

```
pytest tests/test_filter.py -v
```

Expected: `ImportError` — `filter` module not found.

- [ ] **Step 3: Implement `filter.py`**

```python
def tier_leads(leads, sent_ids):
    tier1, tier2, tier3 = [], [], []
    for row in leads:
        if not row.get("email", "").strip():
            continue
        if row["id"] in sent_ids:
            continue
        if row.get("worth_reaching_out") == "1":
            tier1.append(row)
        elif row.get("has_website") == "0":
            tier2.append(row)
        else:
            tier3.append(row)
    return tier1, tier2, tier3
```

- [ ] **Step 4: Run tests to confirm they pass**

```
pytest tests/test_filter.py -v
```

Expected: 6 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add filter.py tests/test_filter.py
git commit -m "feat: add lead tiering logic"
```

---

## Task 4: `template.py` + Tests — Variable Mapping

**Files:**
- Create: `template.py`
- Create: `tests/test_template.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_template.py
import pytest
from unittest.mock import patch
from template import build_payload

FAKE_CAMPAIGN_HAS_WEBSITE = "campaign-abc"
FAKE_CAMPAIGN_NO_WEBSITE = "campaign-xyz"

def _row(category="barber shops", has_website="1", worth_reaching_out="1"):
    return {
        "id": "5",
        "business_name": "Tony's Cuts",
        "category": category,
        "email": "tony@cuts.com",
        "has_website": has_website,
        "worth_reaching_out": worth_reaching_out,
    }

@patch("template.INSTANTLY_CAMPAIGN_HAS_WEBSITE", FAKE_CAMPAIGN_HAS_WEBSITE)
@patch("template.INSTANTLY_CAMPAIGN_NO_WEBSITE", FAKE_CAMPAIGN_NO_WEBSITE)
def test_known_category_maps_cta():
    payload = build_payload(_row(category="barber shops", has_website="1"))
    assert payload["cta_type"] == "booking"

@patch("template.INSTANTLY_CAMPAIGN_HAS_WEBSITE", FAKE_CAMPAIGN_HAS_WEBSITE)
@patch("template.INSTANTLY_CAMPAIGN_NO_WEBSITE", FAKE_CAMPAIGN_NO_WEBSITE)
def test_coffee_shop_maps_order():
    payload = build_payload(_row(category="coffee shops", has_website="1"))
    assert payload["cta_type"] == "order"

@patch("template.INSTANTLY_CAMPAIGN_HAS_WEBSITE", FAKE_CAMPAIGN_HAS_WEBSITE)
@patch("template.INSTANTLY_CAMPAIGN_NO_WEBSITE", FAKE_CAMPAIGN_NO_WEBSITE)
def test_unknown_category_falls_back_to_contact(caplog):
    import logging
    with caplog.at_level(logging.WARNING):
        payload = build_payload(_row(category="pet groomers", has_website="1"))
    assert payload["cta_type"] == "contact"
    assert "pet groomers" in caplog.text

@patch("template.INSTANTLY_CAMPAIGN_HAS_WEBSITE", FAKE_CAMPAIGN_HAS_WEBSITE)
@patch("template.INSTANTLY_CAMPAIGN_NO_WEBSITE", FAKE_CAMPAIGN_NO_WEBSITE)
def test_has_website_uses_has_website_campaign():
    payload = build_payload(_row(has_website="1"))
    assert payload["campaign_id"] == FAKE_CAMPAIGN_HAS_WEBSITE

@patch("template.INSTANTLY_CAMPAIGN_HAS_WEBSITE", FAKE_CAMPAIGN_HAS_WEBSITE)
@patch("template.INSTANTLY_CAMPAIGN_NO_WEBSITE", FAKE_CAMPAIGN_NO_WEBSITE)
def test_no_website_uses_no_website_campaign():
    payload = build_payload(_row(has_website="0", worth_reaching_out="0"))
    assert payload["campaign_id"] == FAKE_CAMPAIGN_NO_WEBSITE

@patch("template.INSTANTLY_CAMPAIGN_HAS_WEBSITE", FAKE_CAMPAIGN_HAS_WEBSITE)
@patch("template.INSTANTLY_CAMPAIGN_NO_WEBSITE", FAKE_CAMPAIGN_NO_WEBSITE)
def test_payload_contains_required_fields():
    payload = build_payload(_row())
    assert "email" in payload
    assert "business_name" in payload
    assert "business_type" in payload
    assert "cta_type" in payload
    assert "campaign_id" in payload
```

- [ ] **Step 2: Run tests to confirm they fail**

```
pytest tests/test_template.py -v
```

Expected: `ImportError` — `template` module not found.

- [ ] **Step 3: Implement `template.py`**

```python
import logging
from config import CTA_MAP, INSTANTLY_CAMPAIGN_HAS_WEBSITE, INSTANTLY_CAMPAIGN_NO_WEBSITE

logger = logging.getLogger(__name__)


def build_payload(row):
    category = row.get("category", "").strip().lower()
    if category not in CTA_MAP:
        logger.warning("Unknown category '%s' — defaulting cta_type to 'contact'", category)
    cta_type = CTA_MAP.get(category, "contact")

    has_website = row.get("has_website", "0") == "1"
    campaign_id = INSTANTLY_CAMPAIGN_HAS_WEBSITE if has_website else INSTANTLY_CAMPAIGN_NO_WEBSITE

    return {
        "email": row["email"].strip(),
        "business_name": row["business_name"].strip(),
        "business_type": category,
        "cta_type": cta_type,
        "campaign_id": campaign_id,
    }
```

- [ ] **Step 4: Run tests to confirm they pass**

```
pytest tests/test_template.py -v
```

Expected: 6 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add template.py tests/test_template.py
git commit -m "feat: add template variable mapping"
```

---

## Task 5: `tracker.py` + Tests — Sent Log

**Files:**
- Create: `tracker.py`
- Create: `tests/test_tracker.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_tracker.py
import json
import pytest
from tracker import load_sent_ids, record_sent

def test_load_sent_ids_returns_empty_set_when_file_missing(tmp_path):
    path = tmp_path / "sent_log.json"
    result = load_sent_ids(str(path))
    assert result == set()

def test_load_sent_ids_returns_ids_from_existing_file(tmp_path):
    path = tmp_path / "sent_log.json"
    path.write_text(json.dumps([
        {"id": "1"}, {"id": "42"}
    ]))
    result = load_sent_ids(str(path))
    assert result == {"1", "42"}

def test_record_sent_appends_to_file(tmp_path):
    path = tmp_path / "sent_log.json"
    record_sent(str(path), lead_id="7", email="a@b.com", business_name="Biz", tier=1)
    entries = json.loads(path.read_text())
    assert len(entries) == 1
    assert entries[0]["id"] == "7"
    assert entries[0]["email"] == "a@b.com"
    assert entries[0]["tier"] == 1
    assert "sent_at" in entries[0]

def test_record_sent_appends_to_existing_file(tmp_path):
    path = tmp_path / "sent_log.json"
    record_sent(str(path), lead_id="1", email="a@b.com", business_name="A", tier=1)
    record_sent(str(path), lead_id="2", email="c@d.com", business_name="B", tier=2)
    entries = json.loads(path.read_text())
    assert len(entries) == 2
```

- [ ] **Step 2: Run tests to confirm they fail**

```
pytest tests/test_tracker.py -v
```

Expected: `ImportError` — `tracker` module not found.

- [ ] **Step 3: Implement `tracker.py`**

```python
import json
import os
from datetime import datetime, timezone

SENT_LOG_PATH = "sent_log.json"


def load_sent_ids(path=SENT_LOG_PATH):
    if not os.path.exists(path):
        return set()
    with open(path, "r") as f:
        entries = json.load(f)
    return {str(e["id"]) for e in entries}


def record_sent(path=SENT_LOG_PATH, *, lead_id, email, business_name, tier):
    entries = []
    if os.path.exists(path):
        with open(path, "r") as f:
            entries = json.load(f)
    entries.append({
        "id": str(lead_id),
        "email": email,
        "business_name": business_name,
        "tier": tier,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    })
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)
```

- [ ] **Step 4: Run tests to confirm they pass**

```
pytest tests/test_tracker.py -v
```

Expected: 4 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add tracker.py tests/test_tracker.py
git commit -m "feat: add sent log tracker"
```

---

## Task 6: `instantly.py` + Tests — API Client

**Files:**
- Create: `instantly.py`
- Create: `tests/test_instantly.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_instantly.py
import pytest
from unittest.mock import patch, MagicMock
from instantly import upload_lead

def _mock_response(status_code=200, json_body=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_body or {"status": "success"}
    mock.raise_for_status = MagicMock()
    return mock

@patch("instantly.requests.post")
def test_upload_lead_calls_correct_endpoint(mock_post):
    mock_post.return_value = _mock_response()
    upload_lead(
        api_key="key123",
        campaign_id="camp456",
        email="test@biz.com",
        business_name="Test Biz",
        business_type="barber shops",
        cta_type="booking",
    )
    call_args = mock_post.call_args
    assert "https://api.instantly.ai/api/v1/lead/add" in call_args[0][0]

@patch("instantly.requests.post")
def test_upload_lead_sends_correct_payload(mock_post):
    mock_post.return_value = _mock_response()
    upload_lead(
        api_key="key123",
        campaign_id="camp456",
        email="test@biz.com",
        business_name="Test Biz",
        business_type="barber shops",
        cta_type="booking",
    )
    payload = mock_post.call_args[1]["json"]
    assert payload["api_key"] == "key123"
    assert payload["campaign_id"] == "camp456"
    assert payload["leads"][0]["email"] == "test@biz.com"
    assert payload["leads"][0]["custom_variables"]["business_name"] == "Test Biz"
    assert payload["leads"][0]["custom_variables"]["cta_type"] == "booking"
    assert payload["skip_if_in_workspace"] is True

@patch("instantly.requests.post")
def test_upload_lead_raises_on_http_error(mock_post):
    mock = _mock_response(status_code=401)
    mock.raise_for_status.side_effect = Exception("401 Unauthorized")
    mock_post.return_value = mock
    with pytest.raises(Exception, match="401"):
        upload_lead(
            api_key="bad_key",
            campaign_id="camp456",
            email="test@biz.com",
            business_name="Test Biz",
            business_type="barber shops",
            cta_type="booking",
        )
```

- [ ] **Step 2: Run tests to confirm they fail**

```
pytest tests/test_instantly.py -v
```

Expected: `ImportError` — `instantly` module not found.

- [ ] **Step 3: Implement `instantly.py`**

```python
import requests

INSTANTLY_BASE_URL = "https://api.instantly.ai/api/v1"


def upload_lead(*, api_key, campaign_id, email, business_name, business_type, cta_type):
    payload = {
        "api_key": api_key,
        "campaign_id": campaign_id,
        "skip_if_in_workspace": True,
        "leads": [
            {
                "email": email,
                "company_name": business_name,
                "custom_variables": {
                    "business_name": business_name,
                    "business_type": business_type,
                    "cta_type": cta_type,
                },
            }
        ],
    }
    response = requests.post(f"{INSTANTLY_BASE_URL}/lead/add", json=payload)
    response.raise_for_status()
    return response.json()
```

- [ ] **Step 4: Run tests to confirm they pass**

```
pytest tests/test_instantly.py -v
```

Expected: 3 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add instantly.py tests/test_instantly.py
git commit -m "feat: add Instantly API client"
```

---

## Task 7: `pipeline.py` — Orchestration

**Files:**
- Create: `pipeline.py`

- [ ] **Step 1: Create `pipeline.py`**

```python
import argparse
import csv
import logging
import sys

from config import INSTANTLY_API_KEY, INSTANTLY_CAMPAIGN_HAS_WEBSITE, INSTANTLY_CAMPAIGN_NO_WEBSITE
from filter import tier_leads
from template import build_payload
from tracker import load_sent_ids, record_sent
from instantly import upload_lead

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SENT_LOG = "sent_log.json"


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate_config():
    missing = [
        name for name, val in [
            ("INSTANTLY_API_KEY", INSTANTLY_API_KEY),
            ("INSTANTLY_CAMPAIGN_HAS_WEBSITE", INSTANTLY_CAMPAIGN_HAS_WEBSITE),
            ("INSTANTLY_CAMPAIGN_NO_WEBSITE", INSTANTLY_CAMPAIGN_NO_WEBSITE),
        ]
        if not val
    ]
    if missing:
        logger.error("Missing required env vars: %s", ", ".join(missing))
        sys.exit(1)


def process_tier(leads, tier_number, sent_log_path):
    sent_ids = load_sent_ids(sent_log_path)
    uploaded = 0
    for row in leads:
        if row["id"] in sent_ids:
            continue
        try:
            payload = build_payload(row)
            upload_lead(
                api_key=INSTANTLY_API_KEY,
                campaign_id=payload["campaign_id"],
                email=payload["email"],
                business_name=payload["business_name"],
                business_type=payload["business_type"],
                cta_type=payload["cta_type"],
            )
            record_sent(
                sent_log_path,
                lead_id=row["id"],
                email=payload["email"],
                business_name=payload["business_name"],
                tier=tier_number,
            )
            sent_ids.add(row["id"])
            uploaded += 1
            logger.info("[Tier %d] Uploaded: %s (%s)", tier_number, payload["business_name"], payload["email"])
        except Exception as e:
            logger.error("[Tier %d] Failed to upload %s: %s", tier_number, row.get("business_name"), e)
    return uploaded


def main():
    parser = argparse.ArgumentParser(description="Upload leads to Instantly campaigns.")
    parser.add_argument("--csv", required=True, help="Path to leads CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Print leads without uploading")
    args = parser.parse_args()

    validate_config()

    rows = load_csv(args.csv)
    sent_ids = load_sent_ids(SENT_LOG)
    tier1, tier2, tier3 = tier_leads(rows, sent_ids=sent_ids)

    logger.info("Leads found — Tier 1: %d | Tier 2: %d | Tier 3: %d", len(tier1), len(tier2), len(tier3))

    if args.dry_run:
        for t, leads in [(1, tier1), (2, tier2), (3, tier3)]:
            for row in leads:
                payload = build_payload(row)
                print(f"[DRY RUN Tier {t}] {payload['business_name']} | {payload['email']} | cta={payload['cta_type']}")
        return

    total = 0
    for tier_num, leads in [(1, tier1), (2, tier2), (3, tier3)]:
        total += process_tier(leads, tier_num, SENT_LOG)

    logger.info("Done. Uploaded %d leads.", total)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run a dry run against ex.csv to verify output**

First copy `.env.example` to `.env` and fill in real values:
```
cp .env.example .env
# edit .env and add your INSTANTLY_API_KEY and both campaign IDs
```

Then run:
```
python pipeline.py --csv ex.csv --dry-run
```

Expected: Lines printed like:
```
INFO Leads found — Tier 1: 18 | Tier 2: 0 | Tier 3: 14
[DRY RUN Tier 1] OU Beauty | ... | cta=booking
[DRY RUN Tier 1] Marmolade Barber Co @ The Studio | marmoladebarberco@gmail.com | cta=booking
...
```

Verify business names, emails, and CTA values look correct for a handful of rows before proceeding.

- [ ] **Step 3: Run all tests to confirm nothing broke**

```
pytest -v
```

Expected: All tests PASSED.

- [ ] **Step 4: Commit**

```bash
git add pipeline.py
git commit -m "feat: add pipeline orchestration with dry-run mode"
```

---

## Task 8: Instantly Campaign Setup (Manual — One Time)

Before running live, set up two campaigns in Instantly. This is done in the Instantly UI, not in code.

- [ ] **Step 1: Create Campaign A (has-website leads)**

1. Go to [instantly.ai](https://app.instantly.ai) → Campaigns → New Campaign
2. Name it: `Website Refresh — Has Website`
3. Add your sending account `will@williamdamato.com`
4. Set schedule: 9am–5pm PST, Mon–Fri
5. Set daily limit: 35 emails/day, delay: 120–180s (randomized)
6. Add email sequence step 1 — paste Template A exactly:

```
Subject: Quick idea for {{business_name}}

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

7. Copy the campaign ID from the URL (e.g., `https://app.instantly.ai/campaign/abc123` → ID is `abc123`)
8. Paste it into `.env` as `INSTANTLY_CAMPAIGN_HAS_WEBSITE=abc123`

- [ ] **Step 2: Create Campaign B (no-website leads)**

Repeat the above with:
- Name: `Website Refresh — No Website`
- Template B:

```
Subject: Quick idea for {{business_name}}

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

- Paste campaign ID into `.env` as `INSTANTLY_CAMPAIGN_NO_WEBSITE=xyz789`

- [ ] **Step 3: Run live against ex.csv**

```
python pipeline.py --csv ex.csv
```

Expected: Logs show each uploaded lead. Check Instantly UI → Campaign → Leads to confirm they appear with correct `business_name`, `business_type`, and `cta_type` values.

- [ ] **Step 4: Commit `.env.example` if any field names changed**

```bash
git add .env.example
git commit -m "chore: finalize env var names"
```

---

## Self-Review Notes

- Spec requires two templates → covered by two campaigns + `campaign_id` in payload ✓
- Spec requires tier priority (tier1 beats tier2 when `worth_reaching_out=1` even with `has_website=0`) → implemented in `filter.py` with `worth_reaching_out` check first ✓
- Spec requires `sent_log.json` to be gitignored → in `.gitignore` ✓
- Spec requires `ex.csv` to be gitignored → `*.csv` covers it ✓
- Spec requires 9am–5pm PST send window → documented in Task 8, set in Instantly UI ✓
- Spec requires opt-out line in both templates → present in both ✓
- Spec requires Cornell (not UCLA) → both templates say Cornell ✓
- Error handling: unknown category → warns + falls back to `contact` ✓
- Error handling: API failure → logs error, does NOT write to sent_log ✓
- `--dry-run` flag not in spec but essential for safe testing — included ✓
