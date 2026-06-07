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
