# fetchers/haystack.py
import datetime
from utils import get, iso_now
from normalize import normalize_component

DOCS_IDX = "https://raw.githubusercontent.com/deepset-ai/haystack/main/README.md"

def fetch(config):
    readme = ""
    try:
        readme = get(DOCS_IDX).text
    except Exception:
        readme = ""
    out = []
    for comp in config["sources"]["haystack"]["components"]:
        raw = {
          "source": "haystack",
          "name": f"haystack-{comp}",
          "description": f"Haystack {comp} component",
          "repo_url": "https://github.com/deepset-ai/haystack",
          "homepage": "https://haystack.deepset.ai/",
          "docs_url": "https://docs.haystack.deepset.ai/",
          "license": "Apache-2.0",
          "languages": ["Python"],
          "tags": ["haystack", comp],
          "dependencies": ["haystack"],
          "example_code": "",
          "readme": readme[:4000],
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
