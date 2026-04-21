from app.services.policy_engine import PolicyEngine
from app.schemas.scan import Detection
from app.core.constants import Decision

def test_policy_allow_empty():
    engine = PolicyEngine()
    res = engine.evaluate([], {})
    assert res.decision == Decision.ALLOW

def test_policy_block_critical():
    engine = PolicyEngine()
    dets = [
        Detection(scanner="a", channel_id="p", severity="low", score=0.2, attack_type="x", explanation="", matched_text=""),
        Detection(scanner="b", channel_id="p", severity="critical", score=0.9, attack_type="y", explanation="", matched_text="")
    ]
    res = engine.evaluate(dets, {"p": 0.9})
    assert res.decision == Decision.BLOCK
    assert res.risk_score == 0.9

def test_policy_sanitize_medium():
    engine = PolicyEngine()
    dets = [
        Detection(scanner="a", channel_id="p", severity="medium", score=0.6, attack_type="x", explanation="", matched_text="bad", sanitized_text="good")
    ]
    res = engine.evaluate(dets, {"p": 0.6})
    assert res.decision == Decision.SANITIZE
    
def test_policy_allow_medium_without_sanitization():
    engine = PolicyEngine()
    dets = [
        Detection(scanner="a", channel_id="p", severity="medium", score=0.6, attack_type="x", explanation="", matched_text="bad")
    ]
    res = engine.evaluate(dets, {"p": 0.6})
    # Cannot sanitize if no sanitized_text is provided by scanners
    assert res.decision == Decision.ALLOW
