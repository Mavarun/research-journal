"""Thin CLI entry points used by console_scripts and scripts/ wrappers."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from research_journal.render import render_summary_markdown, write_summary
from research_journal.schema import Experiment, ExperimentStatus
from research_journal.store import ExperimentStore
from research_journal.validate import ValidationError, validate_experiment


def _repo_root() -> Path:
    # scripts/ and package both live under the repo; prefer CWD experiments/.
    return Path.cwd()


def main_new(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Append a validated experiment JSON under experiments/"
    )
    parser.add_argument("--id", required=True, help="Stable slug id")
    parser.add_argument("--title", required=True)
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--method", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--failure-reason", default=None)
    parser.add_argument(
        "--status",
        default=ExperimentStatus.planned.value,
        choices=[s.value for s in ExperimentStatus],
    )
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--source-repo", default=None)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--metrics-json", default=None, help='e.g. \'{"sharpe_oos": -0.3}\'')
    parser.add_argument("--retrospective", action="store_true")
    parser.add_argument(
        "--experiments-dir",
        default=None,
        help="Defaults to ./experiments",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--from-json",
        default=None,
        help="Load fields from a JSON file (CLI flags override)",
    )
    args = parser.parse_args(argv)

    payload: dict = {}
    if args.from_json:
        payload = json.loads(Path(args.from_json).read_text(encoding="utf-8"))

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    metrics = json.loads(args.metrics_json) if args.metrics_json else payload.get("metrics", {})

    payload.update(
        {
            "id": args.id or payload.get("id"),
            "title": args.title or payload.get("title"),
            "hypothesis": args.hypothesis or payload.get("hypothesis"),
            "data": args.data or payload.get("data"),
            "method": args.method or payload.get("method"),
            "result": args.result or payload.get("result"),
            "failure_reason": args.failure_reason
            if args.failure_reason is not None
            else payload.get("failure_reason"),
            "status": args.status,
            "tags": tags or payload.get("tags", []),
            "created_at": payload.get("created_at", date.today().isoformat()),
            "source_repo": args.source_repo or payload.get("source_repo"),
            "notes": args.notes or payload.get("notes"),
            "metrics": metrics or {},
            "retrospective": args.retrospective or payload.get("retrospective", False),
        }
    )

    root = Path(args.experiments_dir) if args.experiments_dir else _repo_root() / "experiments"
    store = ExperimentStore(root)
    try:
        path = store.save(payload, overwrite=args.overwrite)
    except ValidationError as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1
    print(path)
    return 0


def main_render(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a markdown summary table from experiments/"
    )
    parser.add_argument(
        "--experiments-dir",
        default=None,
        help="Defaults to ./experiments",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Write markdown to this path (default: stdout)",
    )
    parser.add_argument("--title", default="Experiment journal")
    args = parser.parse_args(argv)

    root = Path(args.experiments_dir) if args.experiments_dir else _repo_root() / "experiments"
    store = ExperimentStore(root)
    try:
        text = render_summary_markdown(store=store, title=args.title)
    except ValidationError as exc:
        print(f"validation error while loading: {exc}", file=sys.stderr)
        return 1

    if args.output:
        write_summary(args.output, store=store)
        print(args.output)
    else:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")
    return 0


def main() -> int:
    """Dispatch helper: python -m research_journal.cli <new|render> ..."""
    if len(sys.argv) < 2 or sys.argv[1] not in {"new", "render"}:
        print("usage: python -m research_journal.cli {new,render} ...", file=sys.stderr)
        return 2
    cmd = sys.argv[1]
    rest = sys.argv[2:]
    if cmd == "new":
        return main_new(rest)
    return main_render(rest)


if __name__ == "__main__":
    raise SystemExit(main())
