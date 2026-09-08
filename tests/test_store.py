"""Store append/load tests."""

from __future__ import annotations

from datetime import date

import pytest

from research_journal.store import ExperimentStore
from research_journal.validate import ValidationError


def _payload(eid: str = "010_store_test", **overrides):
    data = {
        "id": eid,
        "title": "Store test",
        "hypothesis": "append works",
        "data": "tmp",
        "method": "unit test",
        "result": "ok",
        "status": "done",
        "created_at": date(2026, 9, 9).isoformat(),
        "tags": ["test"],
    }
    data.update(overrides)
    return data


def test_append_and_load(tmp_path):
    store = ExperimentStore(tmp_path)
    path = store.append(_payload())
    assert path.is_file()
    loaded = store.load("010_store_test")
    assert loaded.title == "Store test"
    assert loaded.status.value == "done"
    assert store.list_ids() == ["010_store_test"]


def test_append_duplicate_raises(tmp_path):
    store = ExperimentStore(tmp_path)
    store.append(_payload())
    with pytest.raises(ValidationError, match="already exists"):
        store.append(_payload())


def test_overwrite_allowed(tmp_path):
    store = ExperimentStore(tmp_path)
    store.append(_payload())
    store.save(_payload(title="Updated"), overwrite=True)
    assert store.load("010_store_test").title == "Updated"


def test_load_all_sorted(tmp_path):
    store = ExperimentStore(tmp_path)
    store.append(_payload("002_b"))
    store.append(_payload("001_a"))
    assert store.list_ids() == ["001_a", "002_b"]
    assert [e.id for e in store.load_all()] == ["001_a", "002_b"]


def test_invalid_payload_not_written(tmp_path):
    store = ExperimentStore(tmp_path)
    with pytest.raises(ValidationError):
        store.append(_payload(status="failed"))  # missing failure_reason
    assert store.list_ids() == []
