# research-journal

Structured experiment log for a research portfolio.

## Hypothesis

1. A structured experiment log (hypothesis, data, method, result, failure reason) beats ad-hoc notes for a research portfolio.
2. Schema validation catches incomplete experiments before they are marked done.
3. A small CLI/script can append experiments and render a markdown summary table from the log.

## What this is

A tiny Python package that stores one JSON file per experiment under `experiments/`, validates required fields with **pydantic**, and renders a markdown summary table.

Seed entries are **retrospective notes** from existing portfolio slices (KO/PEP pairs OOS Sharpe collapse; LSTM OOS dir_acc ~ chance; tabular calibration hurt on easy data). They are **not** live trading claims and invent **no** fake PnL.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest
```

## How to add an experiment

```bash
python scripts/new_experiment.py \
  --id 004_my_slice \
  --title "Short title" \
  --hypothesis "What you believed" \
  --data "What you used" \
  --method "How you tested" \
  --result "What happened" \
  --status failed \
  --failure-reason "Why it failed / why you stopped" \
  --tags "tag1,tag2" \
  --retrospective
```

Rules enforced by the schema:

- `status=done` requires non-empty hypothesis, data, method, result.
- `status=failed` or `abandoned` requires a non-empty `failure_reason`.
- Duplicate ids are rejected unless `--overwrite`.

You can also drop a hand-written JSON file under `experiments/` that matches the schema; `validate` / `load_all` will check it on render.

## How to render

```bash
python scripts/render_journal.py
python scripts/render_journal.py -o JOURNAL.md
```

## Layout

```
src/research_journal/   schema, validate, store, render, cli
scripts/                new_experiment.py, render_journal.py
experiments/            one JSON file per experiment
tests/                  schema, append, render
```

## Limits

- File-backed JSON only - no database, no multi-user locking.
- Metrics are free-form; the schema does not prove scientific validity.
- Retrospective seeds cite portfolio READMEs; re-run those repos for fresh numbers.
- No claim of live PnL, alpha, or production readiness.
