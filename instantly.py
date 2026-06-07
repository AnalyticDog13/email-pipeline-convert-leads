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
