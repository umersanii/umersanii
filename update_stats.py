#!/usr/bin/env python3
"""Fetch live GitHub stats for umersanii and update README.md."""

import re
import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

USERNAME = "umersanii"
README_PATH = os.path.join(os.path.dirname(__file__), "README.md")


def gh_get(url, token=None):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "umersanii-stats-updater")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def gh_search_count(query, token=None):
    url = f"https://api.github.com/search/issues?q={urllib.parse.quote(query)}&per_page=1"
    data = gh_get(url, token)
    return data.get("total_count", 0)


def fetch_stats(token=None):
    # All repos (up to 100 per page, paginate if needed)
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}"
        batch = gh_get(url, token)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    total_repos = len(repos)
    total_stars = sum(r["stargazers_count"] for r in repos)

    most_starred = max(repos, key=lambda r: r["stargazers_count"]) if repos else {}

    # Top language by repo count
    lang_counts = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    top_language = max(lang_counts, key=lang_counts.get) if lang_counts else "Unknown"

    # Commits in the last year via search
    year = datetime.now(timezone.utc).year
    commit_query = f"author:{USERNAME} committer-date:{year-1}-01-01..{year}-12-31"
    commit_url = f"https://api.github.com/search/commits?q={urllib.parse.quote(commit_query)}&per_page=1"
    req = urllib.request.Request(commit_url)
    req.add_header("Accept", "application/vnd.github.cloak-preview+json")
    req.add_header("User-Agent", "umersanii-stats-updater")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as r:
            commit_data = json.loads(r.read())
        total_commits = commit_data.get("total_count", 0)
    except Exception:
        total_commits = 0

    return {
        "total_repos": total_repos,
        "total_stars": total_stars,
        "total_commits": total_commits,
        "most_starred_repo": most_starred.get("name", "N/A"),
        "top_language": top_language,
    }


def update_readme(stats):
    with open(README_PATH) as f:
        content = f.read()

    def repl(m):
        indent = m.group(1)
        lines = [
            f'{indent}"total_repos": {stats["total_repos"]},',
            f'{indent}"total_stars": {stats["total_stars"]},  # growing 📈',
            f'{indent}"total_commits": {stats["total_commits"]},  # Last Year',
            f'{indent}"most_starred_repo": "{stats["most_starred_repo"]}",',
            f'{indent}"top_language": "{stats["top_language"]}",',
        ]
        return "\n".join(lines)

    # Match the entire stats dict body between the braces
    pattern = (
        r'( +)"total_repos":.*?"top_language": "[^"]*",(?:  # [^\n]*)?'
    )
    new_content = re.sub(pattern, repl, content, flags=re.DOTALL)

    if new_content == content:
        print("No changes detected in README.md")
        return None

    with open(README_PATH, "w") as f:
        f.write(new_content)
    print("README.md updated with fresh stats.")
    return new_content


def gh_push_readme(content, token):
    import base64
    # Get current file SHA (required by the API to update)
    meta = gh_get(
        f"https://api.github.com/repos/{USERNAME}/{USERNAME}/contents/README.md",
        token,
    )
    sha = meta["sha"]

    payload = json.dumps({
        "message": "Update GitHub stats",
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha,
    }).encode()

    req = urllib.request.Request(
        f"https://api.github.com/repos/{USERNAME}/{USERNAME}/contents/README.md",
        data=payload,
        method="PUT",
    )
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "umersanii-stats-updater")

    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
    print(f"Pushed: {resp['commit']['html_url']}")


def _load_dotenv(path):
    """Parse key=value pairs from a .env file into os.environ (no overwrite)."""
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                os.environ.setdefault(key, val)
    except OSError:
        pass


def main():
    _load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        token_file = os.path.expanduser("~/.github_token")
        if os.path.exists(token_file):
            with open(token_file) as f:
                token = f.read().strip()
    if not token:
        print("Note: No GITHUB_TOKEN set — unauthenticated rate limits apply (60 req/hr).")

    print(f"Fetching GitHub stats for {USERNAME}...")
    stats = fetch_stats(token)

    print("Stats fetched:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    new_content = update_readme(stats)
    if new_content:
        if not token:
            print("GITHUB_TOKEN required to push via API.")
        else:
            print("Pushing to GitHub...")
            gh_push_readme(new_content, token)


if __name__ == "__main__":
    main()
