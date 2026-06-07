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
