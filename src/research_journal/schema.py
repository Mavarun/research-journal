"""Experiment log schema (pydantic).

Required narrative fields: hypothesis, data, method, result, failure_reason
(when status indicates failure/abandonment). Schema validation is meant to
catch incomplete experiments before they are marked done.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class ExperimentStatus(str, Enum):
    """Lifecycle status for a logged experiment."""

    planned = "planned"
    running = "running"
    done = "done"
    failed = "failed"
    abandoned = "abandoned"


class Experiment(BaseModel):
    """One research experiment entry.

    Fields mirror a lab notebook: what we believed, what we used, how we
    tested it, what happened, and (when relevant) why it failed.
    """

    id: str = Field(..., min_length=1, description="Stable slug, e.g. 001_ko_pep_oos")
    title: str = Field(..., min_length=1)
    hypothesis: str = Field(..., min_length=1)
    data: str = Field(..., min_length=1, description="Dataset / market / synthetic source")
    method: str = Field(..., min_length=1)
    result: str = Field(..., min_length=1)
    failure_reason: Optional[str] = Field(
        default=None,
        description="Required when status is failed or abandoned",
    )
    status: ExperimentStatus = ExperimentStatus.planned
    tags: list[str] = Field(default_factory=list)
    created_at: date
    updated_at: Optional[date] = None
    source_repo: Optional[str] = Field(
        default=None,
        description="Optional link/name of the portfolio repo this notes",
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional numeric/string metrics; never invent live PnL",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Free-form caveats; use for retrospective disclaimers",
    )
    retrospective: bool = Field(
        default=False,
        description="True when this is a retrospective note, not a live claim",
    )

    @field_validator("id")
    @classmethod
    def id_is_slug(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned or " " in cleaned or "/" in cleaned or "\\" in cleaned:
            raise ValueError("id must be a non-empty slug without spaces or path separators")
        return cleaned

    @field_validator("tags")
    @classmethod
    def tags_nonempty_strings(cls, value: list[str]) -> list[str]:
        return [t.strip() for t in value if t and t.strip()]

    @model_validator(mode="after")
    def enforce_completeness_rules(self) -> "Experiment":
        """Block marking done when core fields are blank; require failure_reason."""
        if self.status == ExperimentStatus.done:
            for name in ("hypothesis", "data", "method", "result"):
                if not getattr(self, name).strip():
                    raise ValueError(f"{name} must be non-empty when status is done")
            # Done experiments that failed scientifically still need a result;
            # failure_reason is optional for done (use failed status instead).
        if self.status in (ExperimentStatus.failed, ExperimentStatus.abandoned):
            if not (self.failure_reason and self.failure_reason.strip()):
                raise ValueError(
                    "failure_reason is required when status is failed or abandoned"
                )
        return self

    def to_dict(self) -> dict[str, Any]:
        """JSON-serializable dict (dates as ISO strings)."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Experiment":
        return cls.model_validate(payload)
