# main.py
import os, yaml, argparse, time
from storage import init_db, db, upsert_component
from exporters.export_jsonl import export_jsonl
from exporters.export_markdown import export_markdown
from fetchers import github, huggingface, langchain_hub, haystack, awesome_lists
from utils import iso_now
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

FETCHERS = [github, huggingface, langchain_hub, haystack, awesome_lists]

def load_config(path="config.yml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def apply_activity_filter(rows, config):
    # if last_commit_iso older than threshold, mark inactive
    threshold_days = config["sources"]["github"].get("activity_threshold_days", 365)
    out = []
    for r in rows:
        last = r.get("last_commit_iso")
        if last:
            try:
                dt = datetime.fromisoformat(last.replace("Z",""))
                if datetime.utcnow() - dt > timedelta(days=threshold_days):
                    r["is_active"] = 0
            except Exception:
                pass
        out.append(r)
    return out

def run_once(config, db_path=None):
    init_db(db_path)
    all_rows = []
    # fetch sequentially per fetcher but you can tune concurrency
    for mod in FETCHERS:
        try:
            rows = mod.fetch(config)
            all_rows.extend(rows)
        except Exception as e:
            print(f"[WARN] fetcher {mod.__name__} failed: {e}")

    # dedupe by id
    seen = {}
    for r in all_rows:
        seen[r["id"]] = r
    rows = list(seen.values())

    # apply activity filter and other QC
    rows = apply_activity_filter(rows, config)

    # write to DB
    with db(db_path) as con:
        for r in rows:
            # add last_seen if missing
            if "last_seen_iso" not in r:
                r["last_seen_iso"] = iso_now()
            upsert_component(con, r)

    # export
    export_jsonl(rows, path=config["output"]["jsonl"])
    export_markdown(rows, path=config["output"]["markdown"])
    print(f"Done. Collected {len(rows)} components.")
    return rows

def continuous_run(config, interval_seconds=None, db_path=None):
    if interval_seconds is None:
        interval_seconds = config["scheduler"].get("idle_sleep_seconds", 300)
    try:
        while True:
            print(f"[{iso_now()}] Starting run...")
            run_once(config, db_path)
            print(f"[{iso_now()}] Sleeping for {interval_seconds} seconds...")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Stopping continuous run.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yml")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    parser.add_argument("--db", default=os.getenv("DATABASE_PATH","components.db"))
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.once or (not args.continuous and not args.once):
        run_once(cfg, db_path=args.db)
    elif args.continuous:
        continuous_run(cfg, db_path=args.db)
