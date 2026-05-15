from pathlib import Path
import json
import audit_agent


def test_query_ledger_returns_schema_guidance_for_malformed_select():
    result = json.loads(audit_agent.query_ledger("select p.Payment_Amount from Payments p"))

    assert result["error"] == "Invalid SELECT for this ledger schema"
    assert "Tables: Vendors, Invoices, Payments" in result["schema_hint"]


def test_penalty_skill_contains_business_rule():
    text = Path("skills/penalty_logic/SKILL.md").read_text(encoding="utf-8")
    assert "If Days Late > 7" in text
    assert "0.05" in text


def test_agent_builder_loads_penalty_skill(monkeypatch):
    calls = {}

    def fake_create_deep_agent(**kwargs):
        calls.update(kwargs)
        return "agent"

    monkeypatch.setattr(audit_agent, "create_deep_agent", fake_create_deep_agent)
    audit_agent.build_agent("test-model")

    assert calls["skills"] == ["./skills/penalty_logic/"]
    assert "multiply Invoice Amount by 0.05" not in audit_agent.SYSTEM_PROMPT


def test_build_augmented_prompt_includes_penalty_skill_reminder_for_known_vendor():
    prompt = audit_agent.build_augmented_prompt("Audit the account for Gujarat Steel Corp.")

    assert "Gujarat Steel Corp" in prompt
    assert "VEN-1000" in prompt
    assert "Tables: Vendors, Invoices, Payments" in prompt
    assert "INV-2000" in prompt
    assert "REC-500" in prompt
    assert "Use the penalty_logic skill" in prompt
    assert "check_delivery_log(\"VEN-1000\")" in prompt
