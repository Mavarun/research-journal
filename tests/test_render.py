"""Markdown render tests."""

from __future__ import annotations

from datetime import date

from research_journal.render import render_summary_markdown, write_summary
from research_journal.schema import Experiment
from research_journal.store import ExperimentStore


def _exp(**overrides) -> Experiment:
    payload = {
        "id": "001_demo",
        "title": "Demo experiment",
        "hypothesis": "Structured logs beat ad-hoc notes",
        "data": "synthetic",
        "method": "unit test",
        "result": "table renders",
        "failure_reason": "OOS edge vanished",
        "status": "failed",
        "tags": ["demo", "oos"],
        "created_at": date(2026, 9, 9),
        "retrospective": True,
        "source_repo": "https://github.com/Mavarun/research-journal",
        "metrics": {"dir_acc": 0.5},
    }
    payload.update(overrides)
    return Experiment.model_validate(payload)


def test_render_contains_table_and_failure():
    md = render_summary_markdown([_exp()])
    assert "# Experiment journal" in md
    assert "| ID | Title | Status |" in md
    assert "001_demo" in md
    assert "failed" in md
    assert "OOS edge vanished" in md
    assert "Retrospective note" in md or "retrospective" in md.lower() or "Retro" in md
    assert "## Details" in md
    assert "dir_acc=0.5" in md


def test_render_empty():
    md = render_summary_markdown([])
    assert "no experiments yet" in md


def test_render_from_store(tmp_path):
    store = ExperimentStore(tmp_path)
    store.append(_exp().to_dict())
    md = render_summary_markdown(store=store)
    assert "001_demo" in md


def test_write_summary(tmp_path):
    out = tmp_path / "JOURNAL.md"
    write_summary(out, [_exp()])
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Experiment journal")
    assert "Demo experiment" in text
