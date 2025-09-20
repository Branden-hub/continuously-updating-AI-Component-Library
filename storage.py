# storage.py
import json, sqlite3, os
from contextlib import contextmanager
from utils import DATABASE_PATH

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS components (
  id TEXT PRIMARY KEY,
  name TEXT,
  summary TEXT,
  domain TEXT,
  skills TEXT,
  source TEXT,
  repo_url TEXT,
  homepage TEXT,
  docs_url TEXT,
  license TEXT,
  languages TEXT,
  tags TEXT,
  dependencies TEXT,
  example_code TEXT,
  readme_excerpt TEXT,
  stars INTEGER,
  last_commit_iso TEXT,
  is_active INTEGER,
  added_at_iso TEXT,
  updated_at_iso TEXT,
  deprecated INTEGER,
  broken_links TEXT,
  last_seen_iso TEXT
);
CREATE INDEX IF NOT EXISTS idx_source ON components(source);
CREATE INDEX IF NOT EXISTS idx_name ON components(name);
CREATE INDEX IF NOT EXISTS idx_repo ON components(repo_url);
"""

@contextmanager
def db(path=None):
    if path is None:
        path = DATABASE_PATH
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    con = sqlite3.connect(path, timeout=30)
    try:
        yield con
    finally:
        con.commit()
        con.close()

def init_db(path=None):
    with db(path) as con:
        con.executescript(CREATE_TABLE)

def upsert_component(con, comp: dict):
    keys = list(comp.keys())
    cols = ",".join(keys)
    placeholders = ",".join(["?"]*len(keys))
    updates = ",".join([f"{k}=excluded.{k}" for k in keys if k != "id"])
    vals = [json.dumps(v) if isinstance(v, (list, dict)) else v for v in comp.values()]
    sql = f"INSERT INTO components ({cols}) VALUES ({placeholders}) ON CONFLICT(id) DO UPDATE SET {updates}"
    con.execute(sql, vals)
