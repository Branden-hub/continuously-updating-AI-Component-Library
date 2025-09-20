# fetchers/huggingface.py
import os, datetime
from utils import get, iso_now
from normalize import normalize_component

HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

def hf_headers():
    h = {"Accept": "application/json"}
    if HF_TOKEN:
        h["Authorization"] = f"Bearer {HF_TOKEN}"
    return h

def list_models(task, limit=50):
    url = "https://huggingface.co/api/models"
    params = {"pipeline_tag": task, "limit": limit, "sort":"downloads"}
    return get(url, headers=hf_headers(), params=params).json()

def model_card(repo_id):
    url = f"https://huggingface.co/api/models/{repo_id}"
    return get(url, headers=hf_headers()).json()

def fetch(config):
    out = []
    for task in config["sources"]["huggingface"]["tasks"]:
        arr = list_models(task, config["sources"]["huggingface"]["per_task_limit"])
        for m in arr:
            meta = model_card(m["modelId"])
            readme = meta.get("cardData", {}).get("README", "") or ""
            raw = {
              "source": "huggingface",
              "name": meta.get("id"),
              "description": ",".join(meta.get("tags", [])) or meta.get("pipeline_tag"),
              "repo_url": f"https://huggingface.co/{meta.get('id')}",
              "homepage": f"https://huggingface.co/{meta.get('id')}",
              "docs_url": f"https://huggingface.co/{meta.get('id')}",
              "license": meta.get("license"),
              "languages": ["Python"],
              "tags": meta.get("tags", []),
              "dependencies": [],
              "example_code": "",
              "readme": str(readme)[:5000],
              "stars": meta.get("likes", 0),
              "last_commit_iso": meta.get("lastModified"),
              "is_active": True,
              "added_at_iso": iso_now(),
              "updated_at_iso": iso_now(),
              "deprecated": False,
              "broken_links": [],
              "last_seen_iso": iso_now()
            }
            out.append(normalize_component(raw))
    return out
