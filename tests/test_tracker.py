import json
from tracker import load_sent_ids, record_sent


def test_load_sent_ids_returns_empty_set_when_file_missing(tmp_path):
    path = tmp_path / "sent_log.json"
    result = load_sent_ids(str(path))
    assert result == set()


def test_load_sent_ids_returns_ids_from_existing_file(tmp_path):
    path = tmp_path / "sent_log.json"
    path.write_text(
        json.dumps({"id": "1"}) + "\n" + json.dumps({"id": "42"}) + "\n"
    )
    result = load_sent_ids(str(path))
    assert result == {"1", "42"}


def test_record_sent_appends_to_file(tmp_path):
    path = tmp_path / "sent_log.json"
    record_sent(str(path), lead_id="7", email="a@b.com", business_name="Biz", tier=1)
    entries = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    assert len(entries) == 1
    assert entries[0]["id"] == "7"
    assert entries[0]["email"] == "a@b.com"
    assert entries[0]["tier"] == 1
    assert "sent_at" in entries[0]


def test_record_sent_appends_to_existing_file(tmp_path):
    path = tmp_path / "sent_log.json"
    record_sent(str(path), lead_id="1", email="a@b.com", business_name="A", tier=1)
    record_sent(str(path), lead_id="2", email="c@d.com", business_name="B", tier=2)
    entries = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    assert len(entries) == 2
