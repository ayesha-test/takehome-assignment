# Task 1: GET /movies — Automated Tests

Pytest suite for the Aurora `GET /movies/` endpoint: contract, pagination, catalogue integrity, and search.

## Run

```bash
cd task1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

Default `pytest` runs the **CI gate** (tests 1–4) and skips `@reliability` and `@performance`.

| Command | What runs |
|---|---|
| `pytest -v` | CI gate (tests 1–4) |
| `pytest -v -m ""` | All six tests |
| `pytest -v -m reliability` | Reliability probe only |
| `pytest -v -m performance` | Performance smoke only |

## Layout

```
task1/
├── config.py           # URLs, timeouts
├── client.py           # HTTP calls
├── retry.py            # Retry + "Oops!" detection
├── validators.py       # Schema + domain checks
├── conftest.py         # Fixtures
├── pytest.ini          # Markers, default addopts
├── requirements.txt
└── tests/
    └── test_top_6.py   # All 6 tests
```

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `API_BASE_URL` | Cloud Run deployment URL | Target environment |
| `MAX_RESPONSE_TIME_SECONDS` | `2.0` | Warm latency threshold |
| `REQUEST_TIMEOUT_SECONDS` | `15` | HTTP client timeout |
| `CATALOGUE_FETCH_LIMIT` | `100` | Limit for full-catalogue integrity scan |
