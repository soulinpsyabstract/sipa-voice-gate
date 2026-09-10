import json

from sipa_voice_gate.receipts import ReceiptLog
from sipa_voice_gate.verifier import verify


def _populate(path):
    log = ReceiptLog(path)
    log.append("acted", {"type": "read_data", "description": "balance", "args": {}}, {"verdict": "allow"})
    log.append("acted_after_confirmation", {"type": "send_money", "description": "send $50", "args": {"amount": 50}}, {"verdict": "confirm"})
    log.append("blocked", {"type": "send_money", "description": "send $9000", "args": {"amount": 9000}}, {"verdict": "block"})
    return log


def test_clean_log_verifies(tmp_path):
    p = tmp_path / "r.jsonl"
    _populate(p)
    res = verify(p)
    assert res.ok
    assert res.count == 3
    assert res.problems == []


def test_missing_file(tmp_path):
    res = verify(tmp_path / "nope.jsonl")
    assert not res.ok
    assert "no such log" in res.problems[0]


def test_altered_entry_is_caught(tmp_path):
    p = tmp_path / "r.jsonl"
    _populate(p)
    lines = p.read_text().splitlines()
    tampered = json.loads(lines[1])
    tampered["action"]["args"]["amount"] = 5  # change the amount, keep the hash
    lines[1] = json.dumps(tampered)
    p.write_text("\n".join(lines) + "\n")

    res = verify(p)
    assert not res.ok
    assert any("was altered" in x for x in res.problems)


def test_dropped_entry_is_caught(tmp_path):
    p = tmp_path / "r.jsonl"
    _populate(p)
    lines = p.read_text().splitlines()
    del lines[1]  # drop the middle entry
    p.write_text("\n".join(lines) + "\n")

    res = verify(p)
    assert not res.ok
    assert any(("seq is" in x) or ("chain broken" in x) for x in res.problems)
