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
