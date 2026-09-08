"""Render a markdown summary table from stored experiments."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from research_journal.schema import Experiment
from research_journal.store import ExperimentStore


def render_summary_markdown(
    experiments: Sequence[Experiment] | None = None,
    *,
    store: ExperimentStore | None = None,
    title: str = "Experiment journal",
) -> str:
    """Build a markdown document with a summary table + brief details.

    If ``experiments`` is omitted, load from ``store`` (or default store).
    """
    rows = list(experiments) if experiments is not None else _load(store)
    rows = sorted(rows, key=lambda e: (e.created_at, e.id))

    lines: list[str] = [
        f"# {title}",
        "",
        "Retrospective portfolio notes are marked in the **Retro** column. "
        "Numbers below are research-slice diagnostics, **not** live PnL.",
        "",
        "| ID | Title | Status | Retro | Tags | Created | Failure reason |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for exp in rows:
        tags = ", ".join(exp.tags) if exp.tags else "-"
        fail = _cell(exp.failure_reason) if exp.failure_reason else "-"
        lines.append(
            "| {id} | {title} | {status} | {retro} | {tags} | {created} | {fail} |".format(
                id=_cell(exp.id),
                title=_cell(exp.title),
                status=exp.status.value,
                retro="yes" if exp.retrospective else "no",
                tags=_cell(tags),
                created=exp.created_at.isoformat(),
                fail=fail,
            )
        )

    if not rows:
        lines.append("| - | *(no experiments yet)* | - | - | - | - | -")

    lines.extend(["", "## Details", ""])
    if not rows:
        lines.append("_Add an experiment with `python scripts/new_experiment.py`._")
        lines.append("")
        return "\n".join(lines)

    for exp in rows:
        lines.append(f"### {exp.id}: {exp.title}")
        lines.append("")
        lines.append(f"- **Status:** {exp.status.value}")
        lines.append(f"- **Hypothesis:** {_one_line(exp.hypothesis)}")
        lines.append(f"- **Data:** {_one_line(exp.data)}")
        lines.append(f"- **Method:** {_one_line(exp.method)}")
        lines.append(f"- **Result:** {_one_line(exp.result)}")
        if exp.failure_reason:
            lines.append(f"- **Failure reason:** {_one_line(exp.failure_reason)}")
        if exp.source_repo:
            lines.append(f"- **Source repo:** {exp.source_repo}")
        if exp.metrics:
            metric_bits = ", ".join(f"{k}={v}" for k, v in sorted(exp.metrics.items()))
            lines.append(f"- **Metrics:** {metric_bits}")
        if exp.notes:
            lines.append(f"- **Notes:** {_one_line(exp.notes)}")
        if exp.retrospective:
            lines.append(
                "- **Disclaimer:** Retrospective note from portfolio work - "
                "not a live trading claim."
            )
        lines.append("")

    return "\n".join(lines)


def write_summary(
    path: Path | str,
    experiments: Sequence[Experiment] | None = None,
    *,
    store: ExperimentStore | None = None,
) -> Path:
    out = Path(path)
    text = render_summary_markdown(experiments, store=store)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    return out


def _load(store: ExperimentStore | None) -> list[Experiment]:
    st = store if store is not None else ExperimentStore()
    return st.load_all()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _one_line(value: str, limit: int = 240) -> str:
    text = " ".join(value.split())
    if len(text) > limit:
        return text[: limit - 1] + "..."
    return text
