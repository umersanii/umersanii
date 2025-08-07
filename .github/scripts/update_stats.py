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

# Additional stats for enhanced profile
languages = {}
most_starred_repo = {"name": "", "stars": 0}
most_recent_repo = {"name": "", "updated": None}
total_repo_size = 0

# Contribution patterns analysis
commit_hours = {}  # Track commit times
commit_days = {}   # Track days of week
recent_commits = 0  # Commits in last 30 days
all_commit_dates = []  # All commit dates for streak analysis

print("Processing repositories...")
for i, repo in enumerate(repos, 1):
    print(f"Processing {i}/{len(repos)}: {repo.name}")
    
    # Existing stats
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
    
    # New enhanced stats
    try:
        # Track most starred repository
        if repo.stargazers_count > most_starred_repo["stars"]:
            most_starred_repo = {"name": repo.name, "stars": repo.stargazers_count}
        
        # Track most recently updated repository
        if most_recent_repo["updated"] is None or repo.updated_at > most_recent_repo["updated"]:
            most_recent_repo = {"name": repo.name, "updated": repo.updated_at}
        
        # Track repository size
        total_repo_size += repo.size
        
        # Track programming languages
        repo_languages = repo.get_languages()
        for lang, bytes_count in repo_languages.items():
            languages[lang] = languages.get(lang, 0) + bytes_count
        
        # Analyze commit patterns for contribution habits
        try:
            commits_iter = repo.get_commits(author=USERNAME)
            for commit in commits_iter:
                commit_date = commit.commit.author.date
                all_commit_dates.append(commit_date)
                
                # Track commit hours (for finding favorite coding time)
                hour = commit_date.hour
                commit_hours[hour] = commit_hours.get(hour, 0) + 1
                
                # Track commit days (for finding most productive day)
                day = commit_date.strftime('%A')
                commit_days[day] = commit_days.get(day, 0) + 1
                
                # Count recent commits (last 30 days)
                from datetime import datetime, timedelta
                if commit_date > datetime.now(commit_date.tzinfo) - timedelta(days=30):
                    recent_commits += 1
                    
        except Exception as e:
            print(f"  Error analyzing commit patterns: {e}")
            
        print(f"  Updated: {repo.updated_at.strftime('%Y-%m-%d')}")
        if repo_languages:
            print(f"  Languages: {', '.join(list(repo_languages.keys())[:3])}")
            
    except Exception as e:
        print(f"  Error getting additional stats: {e}")
        
        # Track most recently updated repository
        if most_recent_repo["updated"] is None or repo.updated_at > most_recent_repo["updated"]:
            most_recent_repo = {"name": repo.name, "updated": repo.updated_at}
        
        # Track repository size
        total_repo_size += repo.size
        
        # Track programming languages
        repo_languages = repo.get_languages()
        for lang, bytes_count in repo_languages.items():
            languages[lang] = languages.get(lang, 0) + bytes_count
            
        print(f"  Updated: {repo.updated_at.strftime('%Y-%m-%d')}")
        if repo_languages:
            print(f"  Languages: {', '.join(list(repo_languages.keys())[:3])}")
            
    except Exception as e:
        print(f"  Error getting additional stats: {e}")

print(f"\nFinal calculated stats:")
print(f"Total repos: {total_repos}")
print(f"Total stars: {total_stars}")
print(f"Total commits: {total_commits}")
print(f"Total pull requests: {total_pull_requests}")
print(f"Total issues: {total_issues}")

# Enhanced stats
print(f"\nEnhanced stats:")
print(f"Most starred repo: {most_starred_repo['name']} ({most_starred_repo['stars']} stars)")
print(f"Most recent work: {most_recent_repo['name']} (updated: {most_recent_repo['updated'].strftime('%Y-%m-%d')})")

# Analyze contribution patterns
from datetime import datetime, timedelta

# Find favorite coding hour
favorite_hour = max(commit_hours, key=commit_hours.get) if commit_hours else 0
favorite_hour_formatted = f"{favorite_hour:02d}:00"

# Find most productive day
most_productive_day = max(commit_days, key=commit_days.get) if commit_days else "Unknown"

# Calculate days since last activity
if all_commit_dates:
    last_commit_date = max(all_commit_dates)
    days_since_last = (datetime.now(last_commit_date.tzinfo) - last_commit_date).days
else:
    days_since_last = 0

# Calculate current streak (simplified version)
current_streak = min(len(all_commit_dates), 30) if all_commit_dates else 0

# Determine coding personality traits
coffee_dependency = "High" if favorite_hour >= 20 or favorite_hour <= 6 else "Medium" if favorite_hour >= 18 else "Low"
debug_efficiency = "Lightning Fast" if total_commits > 500 else "Eventually" if total_commits > 100 else "Still Learning"

print(f"\nCoding Habits Analysis:")
print(f"Favorite coding hour: {favorite_hour_formatted}")
print(f"Most productive day: {most_productive_day}")
print(f"Recent commits (30 days): {recent_commits}")
print(f"Coffee dependency: {coffee_dependency}")
print(f"Debug efficiency: {debug_efficiency}")
print(f"Days since last activity: {days_since_last}")

# Top 3 languages by usage
if languages:
    sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"Top languages: {', '.join([f'{lang} ({bytes_count//1000}KB)' for lang, bytes_count in sorted_languages])}")

# Calculate additional metrics
days_since_last_update = (user.updated_at - most_recent_repo["updated"]).days if most_recent_repo["updated"] else 0
avg_stars_per_repo = total_stars / total_repos if total_repos > 0 else 0

print(f"Days since last activity: {days_since_last_update}")
print(f"Average stars per repo: {avg_stars_per_repo:.1f}")

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

# Flexible pattern: replace only the dictionary inside fetch_stats
stats_dict_pattern = r"(def fetch_stats\(self\):[\s\S]*?stats\s*=\s*\{)[\s\S]*?(\}\s*return stats)"
stats_dict_replacement = (
    f'def fetch_stats(self):\n'
    f'        # (100% accurate, trust me bro)\n'
    f'        stats = {{\n'
    f'            "total_repos": {total_repos},\n'
    f'            "total_stars": {total_stars},\n'
    f'            "total_commits": {total_commits},\n'
    f'            "total_pull_requests": {total_pull_requests},\n'
    f'            "total_issues": {total_issues},\n'
    f'            "most_starred_repo": "{most_starred_repo["name"]}",\n'
    f'            "most_recent_repo": "{most_recent_repo["name"]}",\n'
    f'            "top_language": "{sorted_languages[0][0] if languages else "Unknown"}",\n'
    f'            "days_since_last_activity": {days_since_last}\n'
    f'        }}\n'
    f'        return stats'
)

new_content = re.sub(stats_dict_pattern, stats_dict_replacement, content, flags=re.MULTILINE)

# Flexible pattern: replace only the dictionary inside get_coding_habits
habits_dict_pattern = r"(def get_coding_habits\(self\):[\s\S]*?habits\s*=\s*\{)[\s\S]*?(\}\s*return habits)"
streak_days = f"{current_streak} days" if current_streak > 0 else "Building momentum"
habits_dict_replacement = (
    f'def get_coding_habits(self):\n'
    f'        # Coding habits: powered by midnight snacks and existential dread\n'
    f'        habits = {{\n'
    f'            "favorite_coding_hour": "{favorite_hour_formatted}",      # Night owl status confirmed\n'
    f'            "most_productive_day": "{most_productive_day}",     # Because deadlines exist\n'
    f'            "commit_streak": "{streak_days}",           # Fueled by coffee and panic\n'
    f'            "coffee_dependency": "{coffee_dependency}",          # Estimated caffeine requirement\n'
    f'            "debug_efficiency": "{debug_efficiency}",   \n'
    f'        }}\n'
    f'        return habits'
)

new_content2 = re.sub(habits_dict_pattern, habits_dict_replacement, new_content, flags=re.MULTILINE)

if new_content2 == content:
    print("No update needed: README.md already contains the latest stats and habits.")
    exit(0)
else:
    print("Successfully updated README.md with new stats and habits")

try:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content2)
    print("README.md file written successfully!")
except Exception as e:
    print(f"Error writing README.md: {e}")
    exit(1)
