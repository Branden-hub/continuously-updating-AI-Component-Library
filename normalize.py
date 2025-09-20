# normalize.py
import json, re, uuid
from hashlib import sha1
from datetime import datetime
from dateutil import parser as dtparser

DOMAINS = {
  "nlp": ["token", "language", "bert", "gpt", "llm", "text", "qa", "ner", "summarization", "transformer", "nlp"],
  "cv": ["image", "vision", "opencv", "segmentation", "detection", "pose", "yolo", "object-detection"],
  "audio": ["speech", "asr", "tts", "audio", "whisper"],
  "multimodal": ["clip", "vision-language", "vlm", "multimodal", "mm"],
  "reasoning": ["agent", "tool", "planning", "chain-of-thought", "symbolic"],
  "robotics": ["ros", "manipulation", "kinematics"],
  "data": ["etl", "dataset", "preprocessing", "dataset"],
  "infra": ["inference", "deployment", "quantization", "optimization", "serving", "docker", "kubernetes"]
}

def stable_id(source: str, name: str, repo_url: str) -> str:
    basis = f"{source}|{name}|{repo_url}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, sha1(basis.encode()).hexdigest()))

def infer_domains(text: str):
    if not text:
        return ["N/A"]
    text_low = text.lower()
    hits = []
    for dom, keys in DOMAINS.items():
        if any(k in text_low for k in keys):
            hits.append(dom.upper())
    return sorted(set(hits)) or ["N/A"]

def readme_code_snippets(readme_text: str, max_chars=2000):
    if not readme_text:
        return ""
    # extract fenced code blocks
    import re
    blocks = re.findall(r"```(?:\w*\n)?(.*?)```", readme_text, re.S)
    if not blocks:
        # fallback: first 2000 chars
        return readme_text[:max_chars]
    # join first few blocks up to max_chars
    out = ""
    for b in blocks:
        if len(out) + len(b) > max_chars:
            break
        out += b.strip() + "\n\n"
    return out[:max_chars]

def normalize_component(raw: dict) -> dict:
    text = " ".join(filter(None, [
        raw.get("name",""), raw.get("description",""), raw.get("readme","")
    ]))
    domains = infer_domains(text)
    doc = {
      "id": stable_id(raw["source"], raw.get("name",""), raw.get("repo_url","")),
      "name": raw.get("name"),
      "summary": (raw.get("description") or "")[:220],
      "domain": domains,
      "skills": raw.get("skills", []),
      "source": raw.get("source"),
      "repo_url": raw.get("repo_url"),
      "homepage": raw.get("homepage"),
      "docs_url": raw.get("docs_url"),
      "license": raw.get("license"),
      "languages": raw.get("languages", []),
      "tags": raw.get("tags", []),
      "dependencies": raw.get("dependencies", []),
      "example_code": readme_code_snippets(raw.get("readme","")) or (raw.get("example_code") or "")[:2000],
      "readme_excerpt": (raw.get("readme") or "")[:1500],
      "stars": raw.get("stars", 0),
      "last_commit_iso": raw.get("last_commit_iso"),
      "is_active": 1 if raw.get("is_active", True) else 0,
      "added_at_iso": raw.get("added_at_iso") or (raw.get("added_at_iso") or ""),
      "updated_at_iso": raw.get("updated_at_iso") or "",
      "deprecated": 1 if raw.get("deprecated") else 0,
      "broken_links": raw.get("broken_links", [])
    }
    return doc
