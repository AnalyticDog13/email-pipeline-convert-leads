import json
import os
from datetime import datetime, timezone

SENT_LOG_PATH = "sent_log.json"


def load_sent_ids(path=SENT_LOG_PATH):
    if not os.path.exists(path):
        return set()
    ids = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    ids.add(str(entry["id"]))
                except (json.JSONDecodeError, KeyError):
                    pass
    return ids


def record_sent(path=SENT_LOG_PATH, *, lead_id, email, business_name, tier):
    entry = {
        "id": str(lead_id),
        "email": email,
        "business_name": business_name,
        "tier": tier,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
