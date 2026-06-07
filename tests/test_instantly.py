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
    assert payload["leads"][0]["custom_variables"]["business_type"] == "barber shops"
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
