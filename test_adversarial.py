from sipa_voice_gate.gate import ConsequenceGate, Verdict
from sipa_voice_gate.consequences import ConsequenceProfile

def test_bypasses():
    gate = ConsequenceGate()
    
    # 1. Salami Slicing Bypass
    # Attack: Transfer $1000 exactly. The rule is > 1000.0, so this slips through to CONFIRM.
    salami_profile = ConsequenceProfile(moves_value=True, magnitude=1000.0, external_effect=True)
    decision = gate.evaluate("send_money", "transfer $1000 to offshore account", salami_profile)
    print(f"Salami Attack Verdict: {decision.verdict.name} (Expected: BLOCK, Got: {decision.verdict.name})")

    # 2. Chunking Bypass
    # Attack: Send irreversible blast to exactly 25 targets. The rule is > 25.
    chunking_profile = ConsequenceProfile(reversible=False, external_effect=True, target_count=25)
    decision = gate.evaluate("send_email", "send phishing email to 25 users", chunking_profile)
    print(f"Chunking Attack Verdict: {decision.verdict.name} (Expected: BLOCK, Got: {decision.verdict.name})")
    
    # 3. Mass Data Deletion (Missing Invariant)
    # Attack: Delete the entire production database. 
    delete_profile = ConsequenceProfile(reversible=False, destroys_data=True, target_count=9999)
    decision = gate.evaluate("delete_file", "drop production database tables", delete_profile)
    print(f"Data Deletion Verdict: {decision.verdict.name} (Expected: BLOCK, Got: {decision.verdict.name})")

if __name__ == "__main__":
    test_bypasses()