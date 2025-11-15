# tests/test_hybrid_output.py
import pytest
from datetime import datetime
from ..shim_advisor import DALSAdvisor


def test_advisory_output_structure():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="Transfer asset to Bob",
        evidence=["sig_valid", "id_match", "chain_intact"]
    )

    # Check shim_advisory structure
    assert "shim_advisory" in result
    advisory = result["shim_advisory"]

    assert advisory["advisory_mode"] is True
    assert advisory["enforcement"] == "NONE"
    assert "explanation" in advisory
    assert isinstance(advisory["explanation"], list)
    assert len(advisory["explanation"]) > 0

    # Check required fields
    required_fields = [
        "version", "timestamp", "asset_id", "claim", "shim_score",
        "verdict", "confidence_band", "evidence_weighting",
        "recommended_action", "audit_trace_id"
    ]
    for field in required_fields:
        assert field in advisory

    # Check dals_final_decision is null
    assert result["dals_final_decision"] is None


def test_shim_score_range():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="Test claim",
        evidence=["test_evidence"]
    )

    score = result["shim_advisory"]["shim_score"]
    assert 0.0 <= score <= 1.0


def test_verdict_enum():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="Test claim",
        evidence=["test_evidence"]
    )

    verdict = result["shim_advisory"]["verdict"]
    valid_verdicts = ["HIGH_SUPPORT", "MODERATE", "LOW", "CONFLICT"]
    assert verdict in valid_verdicts


def test_confidence_band_enum():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="Test claim",
        evidence=["test_evidence"]
    )

    band = result["shim_advisory"]["confidence_band"]
    valid_bands = ["NARROW", "WIDE"]
    assert band in valid_bands


def test_timestamp_format():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="Test claim",
        evidence=["test_evidence"]
    )

    timestamp = result["shim_advisory"]["timestamp"]
    # Should be ISO format
    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))


def test_asset_id_format():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="Test claim",
        evidence=["test_evidence"]
    )

    asset_id = result["shim_advisory"]["asset_id"]
    # Should match pattern DAL-YYYY-MM-NNN
    import re
    assert re.match(r"^DAL-\d{4}-\d{2}-\d{3}$", asset_id)


def test_audit_trace_id_format():
    advisor = DALSAdvisor()
    result = advisor.analyze(
        claim="Test claim",
        evidence=["test_evidence"]
    )

    trace_id = result["shim_advisory"]["audit_trace_id"]
    # Should match pattern SHIM-ADV-YYYY-MM-DD-NNN
    import re
    assert re.match(r"^SHIM-ADV-\d{4}-\d{2}-\d{2}-\d{3}$", trace_id)