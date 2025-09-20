# fetchers/github.py
import os, datetime, re
from utils import get, head, GITHUB_TOKEN, iso_now
from normalize import normalize_component
from dateutil import parser as dtparser

def gh_headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h

def search_repos(query, per_page=50):
    url = "https://api.github.com/search/repositories"
    data = get(url, headers=gh_headers(), params={"q": query, "per_page": per_page, "sort":"stars","order":"desc"}).json()
    return data.get("items", [])

def get_readme(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    r = get(url, headers=gh_headers())
    if r.ok:
        j = r.json()
        if j.get("download_url"):
            return get(j["download_url"]).text
    return ""

def get_languages(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    try:
        j = get(url, headers=gh_headers()).json()
        return list(j.keys())
    except Exception:
        return []

def hydrate_repo(repo):
    owner, name = repo["full_name"].split("/")
    readme = ""
    try:
        readme = get_readme(owner, name)
    except Exception:
        readme = ""
    homepage = repo.get("homepage") or ""
    repo_url = repo.get("html_url")
    # basic broken link check for homepage
    broken = []
    if homepage:
        try:
            h = head(homepage)
            if getattr(h, "status_code", 0) >= 400:
                broken.append(homepage)
        except Exception:
            broken.append(homepage)
    languages = []
    try:
        languages = get_languages(owner, name)
    except Exception:
        languages = []
    last_commit_iso = repo.get("pushed_at")
    is_deprecated = repo.get("archived") or repo.get("disabled") or False
    return {
      "source": "github",
      "name": repo["name"],
      "description": repo.get("description"),
      "repo_url": repo_url,
      "homepage": homepage,
      "docs_url": repo_url,
      "license": (repo.get("license") or {}).get("spdx_id"),
      "languages": languages,
      "tags": repo.get("topics", []),
      "dependencies": [],
      "example_code": "",
      "readme": readme,
      "stars": repo.get("stargazers_count", 0),
      "last_commit_iso": last_commit_iso,
      "is_active": True,
      "added_at_iso": iso_now(),
      "updated_at_iso": iso_now(),
      "deprecated": is_deprecated,
      "broken_links": broken,
      "last_seen_iso": iso_now()
    }

def fetch(config):
    comps = []
    for q in config["sources"]["github"]["queries"]:
        items = search_repos(q, per_page=config["sources"]["github"]["per_query_limit"])
        for repo in items:
            raw = hydrate_repo(repo)
            comps.append(normalize_component(raw))
    return comps
