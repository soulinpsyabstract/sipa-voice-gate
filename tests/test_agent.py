from sipa_voice_gate.agent import VoiceGateAgent
from sipa_voice_gate.verifier import verify


def mk(tmp_path):
    return VoiceGateAgent(log_path=tmp_path / "r.jsonl")


def test_read_only_acts_immediately(tmp_path):
    a = mk(tmp_path)
    turn = a.hear("What's my account balance?")
    assert turn.acted
    assert turn.receipt_hash
    assert not a.awaiting


def test_payment_holds_then_acts_on_yes(tmp_path):
    a = mk(tmp_path)
    t1 = a.hear("Send $50 to Dana")
    assert t1.awaiting_confirmation and not t1.acted
    assert a.awaiting

    t2 = a.hear("yes")
    assert t2.acted
    assert not a.awaiting
    kinds = [e["kind"] for e in a.log.entries()]
    assert "confirm_requested" in kinds
    assert "acted_after_confirmation" in kinds


def test_payment_cancelled_on_no(tmp_path):
    a = mk(tmp_path)
    a.hear("Send $50 to Dana")
    t = a.hear("no")
    assert not t.acted
    assert not a.awaiting
    assert a.log.entries()[-1]["kind"] == "cancelled"


def test_ambiguous_answer_keeps_waiting(tmp_path):
    a = mk(tmp_path)
    a.hear("Send $50 to Dana")
    t = a.hear("maybe later, what's the weather")
    assert t.awaiting_confirmation
    assert a.awaiting
    assert not t.acted


def test_over_ceiling_blocked_and_logged(tmp_path):
    a = mk(tmp_path)
    t = a.hear("Wire $5000 to this new account")
    assert not t.acted
    assert not a.awaiting
    assert t.decision.verdict.value == "block"
    assert a.log.entries()[-1]["kind"] == "blocked"


def test_full_session_receipt_chain_verifies(tmp_path):
    a = mk(tmp_path)
    for line in ["What's my balance?", "Send $20 to Sam", "yes", "Wire $9000 somewhere"]:
        a.hear(line)
    res = verify(tmp_path / "r.jsonl")
    assert res.ok
    assert res.count == 4  # acted, confirm_requested, acted_after_confirmation, blocked
