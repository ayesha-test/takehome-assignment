# GET /movies — Test Results

**Run date:** 2026-07-01  
**API:** https://november7-730026606190.europe-west1.run.app  
**Structure:** lean flat layout (`client.py`, `retry.py`, `validators.py`)

## Summary

| Suite | Passed | Failed |
|---|---|---|
| CI gate (`pytest -v`) | 4 | 0 |
| All 6 (`pytest -v -m ""`) | 5 | 1 |

## Results

| # | Test | Stage | Result |
|---|---|---|---|
| 1 | `test_contract_validation` | CI gate | **PASS** |
| 2 | `test_pagination_invariants` | CI gate | **PASS** |
| 3 | `test_data_integrity` | CI gate | **PASS** |
| 4 | `test_search_behaviour` | CI gate | **PASS** |
| 5 | `test_reliability_probe` | Reliability | **FAIL** — 5.0% `"Oops!"` (1/20), threshold 0.1% |
| 6 | `test_performance_smoke` | Performance | **PASS** |

## Notes

- Default `pytest -v` runs tests **1–4 only** — this is what reviewers run first.
- Test **5** fails when the live API returns intermittent `"Oops!"` responses. This is expected and documents a real API defect.
- Do **not** commit `.venv/` or `.pytest_cache/` (covered by `.gitignore`).
