# AI Component Aggregator

A lightweight crawler/normalizer/exporter to build a deduplicated AI component library from GitHub, Hugging Face, LangChain Hub, Haystack, and Awesome lists.

## Quick start

1. Clone project and enter directory.

2. Create virtualenv and install:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
Copy .env.example to .env and add tokens (GitHub/HF) if available.

Edit config.yml to tune queries and limits.

Run once:python main.py --once
Or run continuously:python main.py --continuous
Outputs:

components.db (SQLite)

export/components.jsonl

export/index.md

---

# Usage notes, constraints & next-steps

**What I implemented now**
- Fully runnable aggregator that fetches from the sources you listed.
- Readme scraping for `example_code` via fenced code block extraction.
- Broken-link check for homepage (HEAD fallback to GET).
- Activity filter: mark components inactive based on `last_commit_iso`.
- Dedupe by stable UUID based on (source, name, repo_url).
- JSONL + Markdown exporters.
- Safe default query limits and retry/backoff built in `utils.py`.
- SQLite upsert with `last_seen_iso` storage field.

**Limitations / things to add later (easy)**
- Full language detection of repo content (you can add GitHub languages API calls to store more detailed languages).
- A robust HEAD/checker for all asset links inside README (could add link extraction + parallel HEAD checks).
- A web UI (FastAPI) for browsing/filtering/searching the DB.
- Rate-limit handling for very large scale crawling (queue + token bucket).
- A job scheduler (e.g., Airflow, cron or systemd timers) if you want production-grade periodic crawling.
- Optionally index into an actual search engine (Whoosh, Elastic, or SQLite FTS) for fast text queries.

**Operational tips**
- Set `GITHUB_TOKEN` and `HUGGINGFACE_TOKEN` for heavier runs to avoid rate limits.
- Reduce `per_query_limit` in `config.yml` if you hit GitHub API limits.
- Run initially with `--once` then inspect exports and DB to tune queries.


