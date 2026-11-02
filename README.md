# 📊 Annotator Productivity Report

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white) ![No dependencies](https://img.shields.io/badge/dependencies-none-2ea44f?style=flat-square) ![Tests](https://img.shields.io/badge/tests-unittest-2ea44f?style=flat-square) ![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

Weekly productivity and quality report for an annotation team: tasks per hour, median handling time, QA pass rate, and who needs a check-in.

## Why this exists

Speed and quality have to be read together. Someone very fast with a falling QA pass rate may be rushing, and someone very slow may be stuck on the guideline. This report puts both side by side and flags people for a supportive check-in.

## Features

- **Tasks, hours and tasks/hour** per annotator and for the team
- **Median seconds per task**, which outliers don't skew the way an average does
- **QA pass rate** from audited tasks only
- **Flags**: very fast vs. the team median, QA below target, pace below target
- Targets configurable with `--target-tph` and `--min-quality`

## Quick start

No installs needed, just Python 3.9+.

```bash
git clone https://github.com/afra-ozi/annotator-productivity-report.git
cd annotator-productivity-report
python productivity.py sample_task_log.csv
```

## Input

A task log CSV: `annotator, task_id, date (YYYY-MM-DD), seconds, qa_result` (`pass`, `fail` or blank if not audited).

## Sample output

Running `python productivity.py sample_task_log.csv` on the included sample data:

# Team report 2026-10-19 to 2026-10-23

| Annotator | Tasks | Hours | Tasks/hr | Median sec | Audited | QA pass |
|---|---|---|---|---|---|---|
| ann_a | 154 | 3.6 | 43 | 83 | 30 | 100% |
| ann_b | 146 | 3.9 | 38 | 96 | 23 | 96% |
| ann_c | 163 | 1.6 | 104 | 34 | 18 | 89% |
| ann_d | 151 | 6.7 | 22 | 158 | 20 | 100% |
| **Team** | **614** | **15.7** | **39** | | | |

## Needs a check-in

- **ann_c**: very fast (34s vs team 89s): check for rushing; QA pass rate 89% below 90%
- **ann_d**: 22 tasks/hour vs target 40

## Tests

```bash
python -m unittest -v test_productivity
```

## License

MIT
