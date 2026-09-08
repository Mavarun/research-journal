"""JSON file store under experiments/."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, Optional

from research_journal.schema import Experiment
from research_journal.validate import ValidationError, validate_experiment


DEFAULT_DIR_NAME = "experiments"


class ExperimentStore:
    """Append/load experiments as one JSON file per id."""

    def __init__(self, root: Path | str | None = None) -> None:
        if root is None:
            root = Path.cwd() / DEFAULT_DIR_NAME
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, experiment_id: str) -> Path:
        safe = _safe_filename(experiment_id)
        return self.root / f"{safe}.json"

    def exists(self, experiment_id: str) -> bool:
        return self.path_for(experiment_id).is_file()

    def save(self, experiment: Experiment | dict, *, overwrite: bool = False) -> Path:
        """Validate and write one experiment. Raises if id exists unless overwrite."""
        validated = validate_experiment(experiment)
        path = self.path_for(validated.id)
        if path.exists() and not overwrite:
            raise ValidationError(
                f"experiment id already exists: {validated.id} ({path})"
            )
        path.write_text(
            json.dumps(validated.to_dict(), indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )
        return path

    def append(self, experiment: Experiment | dict) -> Path:
        """Alias for save(..., overwrite=False)."""
        return self.save(experiment, overwrite=False)

    def load(self, experiment_id: str) -> Experiment:
        path = self.path_for(experiment_id)
        if not path.is_file():
            raise FileNotFoundError(f"no experiment file for id={experiment_id!r}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        return validate_experiment(payload)

    def list_ids(self) -> list[str]:
        return sorted(p.stem for p in self.root.glob("*.json") if p.is_file())

    def load_all(self) -> list[Experiment]:
        experiments: list[Experiment] = []
        for experiment_id in self.list_ids():
            experiments.append(self.load(experiment_id))
        return experiments

    def iter_all(self) -> Iterable[Experiment]:
        yield from self.load_all()


def _safe_filename(experiment_id: str) -> str:
    cleaned = experiment_id.strip()
    if not cleaned or re.search(r"[/\\]", cleaned):
        raise ValidationError(f"unsafe experiment id: {experiment_id!r}")
    return cleaned
