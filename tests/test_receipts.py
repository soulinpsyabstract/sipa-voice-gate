import json

from sipa_voice_gate.receipts import GENESIS, ReceiptLog


def _mk(tmp_path):
    return ReceiptLog(tmp_path / "r.jsonl")


def test_chain_links(tmp_path):
    log = _mk(tmp_path)
    a = log.append("acted", {"type": "read_data", "description": "x", "args": {}}, {"verdict": "allow"})
    b = log.append("acted", {"type": "read_data", "description": "y", "args": {}}, {"verdict": "allow"})
    c = log.append("acted", {"type": "read_data", "description": "z", "args": {}}, {"verdict": "allow"})

    assert a.prev_hash == GENESIS
    assert b.prev_hash == a.hash
    assert c.prev_hash == b.hash
    assert a.seq == 0 and b.seq == 1 and c.seq == 2


def test_reopen_continues_sequence(tmp_path):
    log = _mk(tmp_path)
    log.append("acted", {"type": "read_data", "description": "x", "args": {}}, {"verdict": "allow"})
    last = log.append("acted", {"type": "read_data", "description": "y", "args": {}}, {"verdict": "allow"})

    reopened = ReceiptLog(tmp_path / "r.jsonl")
    nxt = reopened.append("acted", {"type": "read_data", "description": "z", "args": {}}, {"verdict": "allow"})
    assert nxt.seq == 2
    assert nxt.prev_hash == last.hash


def test_tape_is_trimmed(tmp_path):
    log = _mk(tmp_path)
    log.append("blocked", {"type": "send_money", "description": "send $9000", "args": {}}, {"verdict": "block"})
    tape = log.tape()
    assert tape[0]["what"] == "send $9000"
    assert tape[0]["verdict"] == "block"
    assert len(tape[0]["hash"]) == 12


def test_entries_roundtrip(tmp_path):
    log = _mk(tmp_path)
    log.append("acted", {"type": "read_data", "description": "x", "args": {"q": 1}}, {"verdict": "allow"})
    raw = (tmp_path / "r.jsonl").read_text().strip()
    assert json.loads(raw)["action"]["args"] == {"q": 1}
