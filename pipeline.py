import argparse
import csv
import logging
import sys
import time

from config import INSTANTLY_API_KEY, INSTANTLY_CAMPAIGN_HAS_WEBSITE, INSTANTLY_CAMPAIGN_NO_WEBSITE
from filter import tier_leads
from template import build_payload
from tracker import load_sent_ids, record_sent, SENT_LOG_PATH
from instantly import upload_lead

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_csv(path):
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        logger.error("CSV file not found: %s", path)
        sys.exit(1)


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


def process_tier(leads, tier_number, sent_log_path, sent_ids):
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
            time.sleep(0.15)
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
    sent_ids = load_sent_ids(SENT_LOG_PATH)
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
        total += process_tier(leads, tier_num, SENT_LOG_PATH, sent_ids)

    logger.info("Done. Uploaded %d leads.", total)


if __name__ == "__main__":
    main()
