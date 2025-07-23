import os
import re
from github import Github

# Try to load from .env file if available
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"\'')

load_env()

USERNAME = "umersanii"
TOKEN = os.environ.get("GITHUB_TOKEN")

if not TOKEN:
    print("Error: GITHUB_TOKEN environment variable is not set")
    exit(1)

try:
    g = Github(TOKEN)
    user = g.get_user(USERNAME)
    print(f"Successfully authenticated as: {user.login}")
except Exception as e:
    print(f"Error authenticating with GitHub: {e}")
    exit(1)

total_repos = user.public_repos
total_followers = user.followers

repos = list(user.get_repos())
total_stars = sum([repo.stargazers_count for repo in repos])

print(f"Found {len(repos)} repositories")
print(f"Public repos: {total_repos}")
print(f"Total stars: {total_stars}")
print(f"Followers: {total_followers}")

# Commits, PRs, and issues must be counted across all repositories
total_commits = 0
total_pull_requests = 0
total_issues = 0

print("Processing repositories...")
for i, repo in enumerate(repos, 1):
    print(f"Processing {i}/{len(repos)}: {repo.name}")
    try:
        commits = repo.get_commits(author=USERNAME).totalCount
        total_commits += commits
        print(f"  Commits: {commits}")
    except Exception as e:
        print(f"  Error getting commits: {e}")
    try:
        prs = repo.get_pulls(state="all").totalCount
        total_pull_requests += prs
        print(f"  PRs: {prs}")
    except Exception as e:
        print(f"  Error getting PRs: {e}")
    try:
        issues = repo.get_issues(state="all", creator=USERNAME).totalCount
        total_issues += issues
        print(f"  Issues: {issues}")
    except Exception as e:
        print(f"  Error getting issues: {e}")

print(f"\nFinal calculated stats:")
print(f"Total repos: {total_repos}")
print(f"Total stars: {total_stars}")
print(f"Total commits: {total_commits}")
print(f"Total pull requests: {total_pull_requests}")
print(f"Total issues: {total_issues}")
print(f"Total followers: {total_followers}")

# Update README.md
print("Updating README.md...")
try:
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("Error: README.md file not found!")
    exit(1)
except Exception as e:
    print(f"Error reading README.md: {e}")
    exit(1)

# Pattern to match the stats dict inside fetch_stats method
pattern = (
    r"(def fetch_stats\(self\):\s*\n\s*stats\s*=\s*\{\s*\n)"
    r"\s*\"total_repos\":\s*\d+,\s*\n"
    r"\s*\"total_stars\":\s*\d+,\s*\n"
    r"\s*\"total_commits\":\s*\d+,\s*\n"
    r"\s*\"total_pull_requests\":\s*\d+,\s*\n"
    r"\s*\"total_issues\":\s*\d+,\s*\n"
    r"\s*\"total_followers\":\s*\d+\s*\n"
    r"(\s*\}\s*\n\s*return stats)"
)

replacement = (
    f'def fetch_stats(self):\n'
    f'        stats = {{\n'
    f'            "total_repos": {total_repos},\n'
    f'            "total_stars": {total_stars},\n'
    f'            "total_commits": {total_commits},\n'
    f'            "total_pull_requests": {total_pull_requests},\n'
    f'            "total_issues": {total_issues},\n'
    f'            "total_followers": {total_followers}\n'
    f'        }}\n'
    f'        return stats'
)

new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Check if the replacement was successful
if new_content == content:
    print("Warning: No replacement made. Pattern might not match.")
    # Print the relevant section for debugging
    if "fetch_stats" in content:
        start = content.find("def fetch_stats")
        end = content.find("return stats", start) + len("return stats")
        print("Found fetch_stats section:")
        print(content[start:end])
    else:
        print("Error: fetch_stats method not found in README.md")
    exit(1)
else:
    print("Successfully updated README.md with new stats")

try:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README.md file written successfully!")
except Exception as e:
    print(f"Error writing README.md: {e}")
    exit(1)