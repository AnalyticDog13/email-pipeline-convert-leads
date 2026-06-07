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
