"""Validate experiment payloads before they are stored or marked done."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from research_journal.schema import Experiment, ExperimentStatus


class ValidationError(ValueError):
    """Raised when an experiment payload fails schema or policy checks."""


def validate_experiment(payload: dict[str, Any] | Experiment) -> Experiment:
    """Parse and validate an experiment.

    Accepts a dict or Experiment instance. Re-raises as ValidationError with
    a readable message so CLI scripts can print a single failure reason.
    """
    try:
        if isinstance(payload, Experiment):
            # Re-validate to catch mutated instances.
            experiment = Experiment.model_validate(payload.model_dump())
        else:
            experiment = Experiment.model_validate(payload)
    except PydanticValidationError as exc:
        raise ValidationError(_format_pydantic(exc)) from exc

    _policy_checks(experiment)
    return experiment


def _policy_checks(experiment: Experiment) -> None:
    """Extra rules beyond pydantic field constraints."""
    if experiment.status == ExperimentStatus.done and not experiment.result.strip():
        raise ValidationError("result must be filled before status=done")
    if experiment.status in (ExperimentStatus.failed, ExperimentStatus.abandoned):
        if not (experiment.failure_reason and experiment.failure_reason.strip()):
            raise ValidationError(
                "failure_reason required for failed/abandoned experiments"
            )


def _format_pydantic(exc: PydanticValidationError) -> str:
    parts: list[str] = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", ())) or "(root)"
        parts.append(f"{loc}: {err.get('msg', 'invalid')}")
    return "; ".join(parts) if parts else str(exc)


def can_mark_done(payload: dict[str, Any] | Experiment) -> tuple[bool, str]:
    """Return (ok, reason) without raising - useful for CLI preflight."""
    try:
        data = (
            payload.model_dump()
            if isinstance(payload, Experiment)
            else dict(payload)
        )
        data = {**data, "status": ExperimentStatus.done.value}
        validate_experiment(data)
        return True, ""
    except ValidationError as exc:
        return False, str(exc)
