"""Schema validation tests."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError as PydanticValidationError

from research_journal.schema import Experiment, ExperimentStatus
from research_journal.validate import ValidationError, can_mark_done, validate_experiment


def _base(**overrides):
    payload = {
        "id": "t_example",
        "title": "Example",
        "hypothesis": "H",
        "data": "D",
        "method": "M",
        "result": "R",
        "status": "planned",
        "created_at": date(2026, 9, 9),
    }
    payload.update(overrides)
    return payload


def test_valid_planned_experiment():
    exp = validate_experiment(_base())
    assert exp.id == "t_example"
    assert exp.status == ExperimentStatus.planned
    assert exp.failure_reason is None


def test_failed_requires_failure_reason():
    with pytest.raises((ValidationError, PydanticValidationError)):
        validate_experiment(_base(status="failed"))


def test_failed_with_reason_ok():
    exp = validate_experiment(
        _base(status="failed", failure_reason="OOS Sharpe collapsed")
    )
    assert exp.status == ExperimentStatus.failed
    assert "Sharpe" in exp.failure_reason


def test_abandoned_requires_failure_reason():
    with pytest.raises(ValidationError):
        validate_experiment(_base(status="abandoned", failure_reason="  "))


def test_id_rejects_path_separators():
    with pytest.raises(ValidationError):
        validate_experiment(_base(id="../evil"))


def test_done_ok_when_fields_filled():
    exp = validate_experiment(_base(status="done"))
    assert exp.status == ExperimentStatus.done


def test_can_mark_done_helper():
    ok, reason = can_mark_done(_base())
    assert ok is True
    assert reason == ""


def test_from_dict_roundtrip():
    exp = Experiment.from_dict(_base(tags=["a", "b"], retrospective=True))
    again = Experiment.from_dict(exp.to_dict())
    assert again.tags == ["a", "b"]
    assert again.retrospective is True
    assert again.created_at == date(2026, 9, 9)
