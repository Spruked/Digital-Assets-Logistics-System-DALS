# tests/test_advisory_only.py
import pytest
from ..shim_advisor import DALSAdvisor


def test_no_enforcement_capability():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="Transfer asset to Bob",
        evidence=["sig_valid", "id_match", "chain_intact"]
    )

    # SHiM v1.1 is advisory only - no enforcement
    assert result["shim_advisory"]["enforcement"] == "NONE"
    assert result["shim_advisory"]["advisory_mode"] is True


def test_human_authority_preserved():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="High value transfer",
        evidence=["strong_evidence"]
    )

    # Final decision must be made by human/multi-sig
    assert result["dals_final_decision"] is None

    # Should recommend human review
    recommended_action = result["shim_advisory"]["recommended_action"]
    assert "human review" in recommended_action.lower() or "multi-sig" in recommended_action.lower()


def test_advisory_mode_always_true():
    advisor = DALSAdvisor()

    # Test with various claims
    test_cases = [
        ("Simple transfer", ["basic_evidence"]),
        ("Complex claim", ["multiple", "evidence", "types"]),
        ("High risk operation", ["weak_evidence"])
    ]

    for claim, evidence in test_cases:
        result = advisor.analyze(claim=claim, evidence=evidence)
        assert result["shim_advisory"]["advisory_mode"] is True


def test_no_automatic_execution():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="Execute transaction",
        evidence=["all_checks_pass"]
    )

    # Even with perfect evidence, no automatic execution
    assert result["shim_advisory"]["enforcement"] == "NONE"
    assert "proceed to human review" in result["shim_advisory"]["recommended_action"].lower()


def test_audit_trail_required():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="Test claim",
        evidence=["test_evidence"]
    )

    # Must have audit trace ID
    assert "audit_trace_id" in result["shim_advisory"]
    assert result["shim_advisory"]["audit_trace_id"].startswith("SHIM-ADV-")

    # Must have explanation for auditability
    assert "explanation" in result["shim_advisory"]
    assert len(result["shim_advisory"]["explanation"]) > 0