# exporters/export_jsonl.py
import json, os

def export_jsonl(rows, path="export/components.jsonl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
