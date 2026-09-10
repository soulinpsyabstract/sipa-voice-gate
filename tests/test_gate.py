from sipa_voice_gate.consequences import ConsequenceProfile
from sipa_voice_gate.gate import ConsequenceGate, Verdict

G = ConsequenceGate()


def test_read_only_is_allowed():
    d = G.evaluate("read_data", "check the balance", ConsequenceProfile(reversible=True))
    assert d.verdict is Verdict.ALLOW
    assert d.spoken == ""


def test_small_payment_needs_confirmation():
    d = G.evaluate(
        "send_money", "send $50 to Dana",
        ConsequenceProfile(reversible=False, external_effect=True, moves_value=True, magnitude=50),
    )
    assert d.verdict is Verdict.CONFIRM
    assert "yes" in d.spoken.lower()
    assert d.consequence_chain  # non-empty
    assert "moves money" in d.reasons


def test_over_ceiling_is_blocked():
    d = G.evaluate(
        "send_money", "wire $5000",
        ConsequenceProfile(reversible=False, external_effect=True, moves_value=True, magnitude=5000),
    )
    assert d.verdict is Verdict.BLOCK
    assert any("ceiling" in r for r in d.reasons)


def test_delete_needs_confirmation_and_has_chain():
    d = G.evaluate("delete_file", "delete the backups", ConsequenceProfile(reversible=False, destroys_data=True))
    assert d.verdict is Verdict.CONFIRM
    assert "destroys data" in d.reasons
    assert len(d.consequence_chain) >= 2


def test_config_change_needs_confirmation():
    d = G.evaluate("change_setting", "enable auto-reply", ConsequenceProfile(reversible=True, changes_config=True))
    assert d.verdict is Verdict.CONFIRM
    assert "changes standing configuration" in d.reasons


def test_unknown_action_fails_closed():
    # not obviously safe -> must not be ALLOW
    d = G.evaluate("frobnicate", "do the thing", ConsequenceProfile(reversible=False))
    assert d.verdict is Verdict.CONFIRM


def test_bulk_irreversible_external_blocked():
    d = G.evaluate(
        "send_email", "email the whole list",
        ConsequenceProfile(reversible=False, external_effect=True, target_count=200),
    )
    assert d.verdict is Verdict.BLOCK
