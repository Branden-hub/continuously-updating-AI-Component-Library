# fetchers/langchain_hub.py
import datetime
from utils import get, iso_now
from normalize import normalize_component

BASE = "https://api.langchain.plus/api/hub"

def fetch_category(cat, limit=100):
    url = f"{BASE}/{cat}?limit={limit}"
    return get(url).json().get("items", [])

def fetch(config):
    out = []
    cats = config["sources"]["langchain_hub"]["categories"]
    for c in cats:
        try:
            items = fetch_category(c, config["sources"]["langchain_hub"]["per_category_limit"])
        except Exception:
            items = []
        for it in items:
            raw = {
              "source": "langchain_hub",
              "name": it.get("name"),
              "description": it.get("description"),
              "repo_url": it.get("url"),
              "homepage": it.get("url"),
              "docs_url": it.get("url"),
              "license": None,
              "languages": ["Python"],
              "tags": [c],
              "dependencies": [],
              "example_code": it.get("content","")[:2000],
              "readme": it.get("content","")[:4000],
              "stars": 0,
              "last_commit_iso": None,
              "is_active": True,
              "added_at_iso": iso_now(),
              "updated_at_iso": iso_now(),
              "deprecated": False,
              "broken_links": [],
              "last_seen_iso": iso_now()
            }
            out.append(normalize_component(raw))
    return out
