# fetchers/awesome_lists.py
import datetime, re
from utils import get, iso_now
from normalize import normalize_component

LINK_RE = re.compile(r"-\s*\[([^\]]+)\]\((https?://[^\)]+)\)\s*-?\s*(.*)")

def fetch(config):
    out = []
    for url in config["sources"]["awesome_lists"]["urls"]:
        text = ""
        try:
            text = get(url).text
        except Exception:
            continue
        for m in LINK_RE.finditer(text):
            name, link, desc = m.groups()
            raw = {
              "source": "awesome",
              "name": name.strip(),
              "description": desc.strip()[:220],
              "repo_url": link,
              "homepage": link,
              "docs_url": link,
              "license": None,
              "languages": [],
              "tags": ["awesome"],
              "dependencies": [],
              "example_code": "",
              "readme": "",
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
