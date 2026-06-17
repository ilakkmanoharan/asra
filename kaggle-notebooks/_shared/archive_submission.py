#!/usr/bin/env python3
"""Archive a Kaggle competition submit into kaggle-notebooks/phaseN/submissions/.

Run ONLY after a submission is made (ref assigned). Snapshots notebook + template
agent and writes log/theory/testing stubs for you to fill when scoring completes.

Usage:
  python3 kaggle-notebooks/_shared/archive_submission.py \\
    --phase 5 --version 3 --ref 53799999 \\
    --message "asra-v0.7-phase5 v3 official gateway pattern" \\
    --status PENDING

After Kaggle scoring finishes:
  python3 kaggle-notebooks/_shared/archive_submission.py \\
    --phase 5 --version 3 --ref 53799999 --update-score 0.00 --status COMPLETE
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase_registry import PHASES, PhaseConfig


def _theory_source_path(phase: PhaseConfig) -> Path | None:
    """Best-effort locate phase concept paper in phase dir."""
    candidates = sorted(phase.phase_dir.glob("asra-phase*.md"))
    if candidates:
        return candidates[0]
    candidates = sorted(phase.phase_dir.glob("phase*.md"))
    return candidates[0] if candidates else None


def _theory_stub(phase: PhaseConfig, version: int, ref: int, message: str) -> str:
    paper = _theory_source_path(phase)
    paper_link = f"[`theory-source.md`](theory-source.md)" if paper else "*(add theory-source.md)*"
    return f"""# Theory — Phase {phase.number} (v{version} ref {ref})

**Agent tag:** `{phase.agent_tag}`  
**Submit message:** `{message}`  
**Full paper:** {paper_link}

## What this notebook implements

*(Fill after submit — ASRA layer stack for this phase.)*

## Gateway notebook structure

1. Install competition wheels
2. `%%writefile /tmp/my_agent.py`
3. Rerun: gateway sidecar → `main.py --agent myagent`
4. Validation gate: dummy `submission.parquet`

## Design intent for this submit

**Track A:** Gateway **Succeeded** (Stage 1).  
**Track B:** Public score informational until Stage 2.
"""


def _testing_stub(phase: int, version: int) -> str:
    return f"""# Testing — Phase {phase} v{version}

## Pre-submit (local)

- [ ] `python3 -m py_compile asra_phase{phase}_kaggle_template_agent.py`
- [ ] Rebuild notebook: `python3 build_phase{phase}_kaggle_notebook.py`
- [ ] Notebook cell 2 contains required classes (no `NameError` at import)
- [ ] Gateway cells match `_shared/gateway_notebook.py` pattern

## Validation run (Kaggle Run All)

| Check | Expected |
|-------|----------|
| Session status | `COMPLETE` |
| Outputs | `submission.parquet` |
| Agent path | `/tmp/my_agent.py` (not `/kaggle/working/`) |

## Scoring rerun (competition)

| Check | Expected |
|-------|----------|
| Status | `COMPLETE` / `Succeeded` (not `ERROR`) |
| Public score | Record in `submission-log.md` |

## Self-test (optional, Swarm agent only)

```bash
python3 asra_phase{phase}_my_agent.py --self-test
```
"""


def _log_md(phase: PhaseConfig, version: int, ref: int, message: str, status: str, score: str | None) -> str:
    score_s = score if score is not None else "*TBD*"
    return f"""# Submission log — Phase {phase.number} v{version} ref {ref}

| Field | Value |
|-------|-------|
| **Date (UTC)** | {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")} |
| **Ref** | **{ref}** |
| **Kernel** | [{phase.kernel_slug.split("/")[-1]}](https://www.kaggle.com/code/{phase.kernel_slug}) v**{version}** |
| **Agent tag** | `{phase.agent_tag}` |
| **Message** | `{message}` |
| **Status** | {status} |
| **Public score** | {score_s} |

## Command

```bash
cd kaggle-notebooks/phase{phase.number}
./submit.sh all "{message}"
```

## Machine-readable

See [`submission-log.json`](submission-log.json).
"""


def archive_dir(phase: PhaseConfig, version: int, ref: int) -> Path:
    return phase.phase_dir / "submissions" / f"v{version}-ref{ref}"


def write_phase_submissions_readme(phase: PhaseConfig) -> None:
    sub_root = phase.phase_dir / "submissions"
    sub_root.mkdir(parents=True, exist_ok=True)
    rows: list[str] = []
    for d in sorted(sub_root.glob("v*-ref*")):
        if not d.is_dir():
            continue
        m = re.match(r"v(\d+)-ref(\d+)$", d.name)
        if not m:
            continue
        ver, ref = m.group(1), m.group(2)
        log_json = d / "submission-log.json"
        status, score = "—", "—"
        if log_json.is_file():
            data = json.loads(log_json.read_text())
            status = str(data.get("status", "—")).replace("SubmissionStatus.", "")
            score = data.get("public_score")
            score = str(score) if score is not None else "—"
        rows.append(f"| v{ver} | {ref} | {score} | {status} | [{d.name}]({d.name}/) |")

    body = f"""# Phase {phase.number} — submission archive

**Agent tag:** `{phase.agent_tag}`  
**Working notebook:** [`../{phase.notebook_name}`](../{phase.notebook_name})

Archive a folder **only after** each competition submit. See [`../../SUBMISSIONS.md`](../../SUBMISSIONS.md).

| Kernel ver | Ref | Score | Status | Folder |
|------------|-----|-------|--------|--------|
"""
    body += "\n".join(rows) if rows else "| — | — | — | *No submissions yet* | — |"
    body += "\n\n## New archive\n\n```bash\npython3 kaggle-notebooks/_shared/archive_submission.py --phase "
    body += f"{phase.number} --version N --ref REF --message \"...\"\n```\n"
    (sub_root / "README.md").write_text(body, encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Archive Kaggle submission under phaseN/submissions/")
    p.add_argument("--phase", type=int, required=True)
    p.add_argument("--version", type=int, required=True)
    p.add_argument("--ref", type=int, required=True)
    p.add_argument("--message", default="")
    p.add_argument("--status", default="PENDING")
    p.add_argument("--score", type=float, default=None)
    p.add_argument("--update-score", type=float, default=None, dest="update_score")
    p.add_argument("--update-status", default=None, dest="update_status")
    args = p.parse_args()

    if args.phase not in PHASES:
        p.error(f"Unknown phase {args.phase}")
    phase = PHASES[args.phase]
    dest = archive_dir(phase, args.version, args.ref)

    if args.update_score is not None or args.update_status:
        if not dest.is_dir():
            p.error(f"Archive missing: {dest}")
        log_json = dest / "submission-log.json"
        data = json.loads(log_json.read_text()) if log_json.is_file() else {}
        if args.update_score is not None:
            data["public_score"] = args.update_score
        if args.update_status:
            data["status"] = args.update_status
        log_json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        log_md = dest / "submission-log.md"
        if log_md.is_file():
            text = log_md.read_text()
            if args.update_score is not None:
                text = re.sub(r"\| \*\*Public score\*\* \| [^\n]+", f"| **Public score** | **{args.update_score}**", text)
            if args.update_status:
                text = re.sub(r"\| \*\*Status\*\* \| [^\n]+", f"| **Status** | {args.update_status}", text)
            log_md.write_text(text, encoding="utf-8")
        write_phase_submissions_readme(phase)
        print(f"Updated {dest}")
        return

    dest.mkdir(parents=True, exist_ok=True)
    nb_src = phase.notebook_path
    if nb_src.is_file():
        shutil.copy2(nb_src, dest / "notebook.ipynb")
    tpl = phase.template_agent
    if tpl.is_file():
        shutil.copy2(tpl, dest / "template-agent.py")

    paper = _theory_source_path(phase)
    if paper and paper.is_file():
        shutil.copy2(paper, dest / "theory-source.md")

    (dest / "theory.md").write_text(_theory_stub(phase, args.version, args.ref, args.message), encoding="utf-8")
    (dest / "testing.md").write_text(_testing_stub(phase.number, args.version), encoding="utf-8")
    (dest / "submission-log.md").write_text(
        _log_md(phase, args.version, args.ref, args.message, args.status, args.score), encoding="utf-8"
    )
    payload = {
        "phase": phase.number,
        "agent_tag": phase.agent_tag,
        "kernel_slug": phase.kernel_slug,
        "kernel_version": args.version,
        "submission_ref": args.ref,
        "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
        "message": args.message,
        "status": args.status,
        "public_score": args.score,
        "archive_path": str(dest.relative_to(phase.phase_dir.parent.parent)),
    }
    (dest / "submission-log.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (dest / "log-analysis.md").write_text(
        f"# Log analysis — Phase {phase.number} v{args.version} ref {args.ref}\n\n"
        f"**Status:** {args.status}\n\n"
        "## Track A (plumbing)\n\n*(Fill when scoring completes.)*\n\n"
        "## Track B (score)\n\n*(Fill public score and interpretation.)*\n",
        encoding="utf-8",
    )
    (dest / "next-submission-plan.md").write_text(
        f"# Next submission\n\nSee `private/next-steps/kaggle/` calendar after this ref is **COMPLETE**.\n",
        encoding="utf-8",
    )

    write_phase_submissions_readme(phase)
    print(f"Archived → {dest}")


if __name__ == "__main__":
    main()
