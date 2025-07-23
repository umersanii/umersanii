import os
import re
from github import Github

USERNAME = "umersanii"
TOKEN = os.environ.get("GITHUB_TOKEN")

g = Github(TOKEN)
user = g.get_user(USERNAME)

total_repos = user.public_repos
total_followers = user.followers

repos = list(user.get_repos())
total_stars = sum([repo.stargazers_count for repo in repos])

# Commits, PRs, and issues must be counted across all repositories
total_commits = 0
total_pull_requests = 0
total_issues = 0

for repo in repos:
    try:
        total_commits += repo.get_commits(author=USERNAME).totalCount
    except Exception:
        pass
    try:
        total_pull_requests += repo.get_pulls(state="all").totalCount
    except Exception:
        pass
    try:
        total_issues += repo.get_issues(state="all", creator=USERNAME).totalCount
    except Exception:
        pass

# Update README.md
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

# Pattern to match the self.stats dict inside Sani class
pattern = (
    r"(self\.stats\s*=\s*\{\s*\n)"
    r"\s*\"total_repos\":\s*\d+,\s*\n"
    r"\s*\"total_stars\":\s*\d+,\s*\n"
    r"\s*\"total_commits\":\s*\d+,\s*\n"
    r"\s*\"total_pull_requests\":\s*\d+,\s*\n"
    r"\s*\"total_issues\":\s*\d+,\s*\n"
    r"\s*\"total_followers\":\s*\d+\s*\n"
    r"\s*\}"
)

replacement = (
    f'self.stats = {{\n'
    f'            "total_repos": {total_repos},\n'
    f'            "total_stars": {total_stars},\n'
    f'            "total_commits": {total_commits},\n'
    f'            "total_pull_requests": {total_pull_requests},\n'
    f'            "total_issues": {total_issues},\n'
    f'            "total_followers": {total_followers}\n'
    f'        }}'
)

new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_content)