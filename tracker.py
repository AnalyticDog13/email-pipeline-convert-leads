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
