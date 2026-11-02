"""Weekly productivity and quality report for an annotation team.

Reads a task log and reports, per annotator:
- tasks completed and hours worked
- tasks per hour and median seconds per task
- QA pass rate (from audited tasks)
- flags: unusually fast work (possible rushing), low quality, or slow pace

Task log CSV columns:
    annotator, task_id, date (YYYY-MM-DD), seconds, qa_result (pass / fail / blank if not audited)

Usage:
    python productivity.py sample_task_log.csv [--target-tph 40] [--min-quality 0.9]
"""
import argparse
import csv
import statistics
from collections import defaultdict
from datetime import date


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["seconds"] = float(r["seconds"])
        if r["seconds"] <= 0:
            raise ValueError(f"task {r['task_id']}: seconds must be positive")
        r["date"] = date.fromisoformat(r["date"])
        r["qa_result"] = (r.get("qa_result") or "").strip().lower()
    return rows


def per_annotator(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[r["annotator"]].append(r)
    stats = {}
    for name, rs in sorted(groups.items()):
        secs = [r["seconds"] for r in rs]
        audited = [r for r in rs if r["qa_result"] in ("pass", "fail")]
        passed = sum(r["qa_result"] == "pass" for r in audited)
        hours = sum(secs) / 3600
        stats[name] = {
            "tasks": len(rs),
            "hours": hours,
            "tph": len(rs) / hours,
            "median_sec": statistics.median(secs),
            "audited": len(audited),
            "quality": passed / len(audited) if audited else None,
            "days": len({r["date"] for r in rs}),
        }
    return stats


def flags(stats, target_tph=40, min_quality=0.9):
    """Return {annotator: [reasons]} for anyone who needs a check-in."""
    team_median = statistics.median(s["median_sec"] for s in stats.values())
    out = {}
    for name, s in stats.items():
        reasons = []
        if s["median_sec"] < 0.5 * team_median:
            reasons.append(f"very fast ({s['median_sec']:.0f}s vs team {team_median:.0f}s): check for rushing")
        if s["quality"] is not None and s["quality"] < min_quality:
            reasons.append(f"QA pass rate {s['quality']:.0%} below {min_quality:.0%}")
        if s["tph"] < 0.6 * target_tph:
            reasons.append(f"{s['tph']:.0f} tasks/hour vs target {target_tph}")
        if reasons:
            out[name] = reasons
    return out


def report(rows, target_tph=40, min_quality=0.9):
    stats = per_annotator(rows)
    start, end = min(r["date"] for r in rows), max(r["date"] for r in rows)
    lines = [f"# Team report {start} to {end}", "",
             "| Annotator | Tasks | Hours | Tasks/hr | Median sec | Audited | QA pass |",
             "|---|---|---|---|---|---|---|"]
    for name, s in stats.items():
        q = f"{s['quality']:.0%}" if s["quality"] is not None else "n/a"
        lines.append(f"| {name} | {s['tasks']} | {s['hours']:.1f} | {s['tph']:.0f} | {s['median_sec']:.0f} | {s['audited']} | {q} |")
    total_tasks = sum(s["tasks"] for s in stats.values())
    total_hours = sum(s["hours"] for s in stats.values())
    lines.append(f"| **Team** | **{total_tasks}** | **{total_hours:.1f}** | **{total_tasks / total_hours:.0f}** | | | |")
    lines += ["", "## Needs a check-in", ""]
    f = flags(stats, target_tph, min_quality)
    lines += [f"- **{n}**: " + "; ".join(r) for n, r in f.items()] or ["- nobody, all within range"]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Annotator productivity and quality report")
    p.add_argument("csv")
    p.add_argument("--target-tph", type=float, default=40, help="expected tasks per hour (default 40)")
    p.add_argument("--min-quality", type=float, default=0.9, help="minimum QA pass rate (default 0.9)")
    a = p.parse_args(argv)
    print(report(load(a.csv), a.target_tph, a.min_quality))


if __name__ == "__main__":
    main()
