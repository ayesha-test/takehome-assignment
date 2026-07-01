# Task 2: LLM Summary Evaluation

Scores summaries from `GET /summaries`. Offline rubric — rules, term coverage, local embeddings. No API keys or paid judges.

## Scoring

| Layer | Weight | Checks |
|---|---|---|
| **Structure** | 20% | Non-empty, 10–500 chars |
| **Coverage** | 50% | Critical facts from the ticket appear in the summary |
| **Similarity** | 30% | Cosine similarity (`all-MiniLM-L6-v2`) |

**Pass:** overall ≥ 0.75 **and** zero missing critical terms. Weights and thresholds in `config.py`.

Coverage pulls must-mention terms from `original_text` (regex for platforms/versions, keyword list, phrases like `no workaround`), matched case-insensitively. A missing term is a hard fail regardless of score.

Similarity loads `all-MiniLM-L6-v2` once per process (~80 MB on first run). ROUGE was skipped — it rewards copy-paste and punishes paraphrase.

## Known gap: faithfulness

Summaries can pass while adding invented facts (e.g. TCK-004 today). We catch missing terms, bad structure, and low overlap; we don't catch plausible hallucinations that still hit keywords. Full faithfulness would need NLI or LLM-as-judge — intentionally skipped for cost, latency, and determinism.

## Run

```bash
cd task2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_eval.py
```

Prints to stdout and writes `report.json` (gitignored).

| Variable | Default | Purpose |
|---|---|---|
| `API_BASE_URL` | Cloud Run deployment URL | Target environment |
| `REQUEST_TIMEOUT_SECONDS` | `15` | HTTP client timeout |

## Layout

```
task2/
├── config.py
├── client.py           # GET /summaries
├── structure.py        # Layer 1
├── coverage.py         # Layer 2
├── similarity.py       # Layer 3
├── evaluator.py        # Scoring + pass/fail
├── run_eval.py
└── requirements.txt
```
