# exporters/export_markdown.py
from collections import defaultdict
import os

def export_markdown(rows, path="export/index.md"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows_by_domain = defaultdict(list)
    for r in rows:
        for d in r.get("domain", []):
            rows_by_domain[d].append(r)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# AI Component Library\n\n")
        for dom in sorted(rows_by_domain.keys()):
            f.write(f"## {dom}\n\n")
            for r in rows_by_domain[dom]:
                name = r.get('name') or 'Unnamed'
                repo = r.get('repo_url') or r.get('homepage') or ''
                summary = r.get('summary') or ''
                f.write(f"- **{name}** — {summary} [{repo}]\n")
            f.write("\n")
