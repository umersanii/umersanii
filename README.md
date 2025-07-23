

[comment]: <> (View Counter)
<p align="middle"> <img src="https://komarev.com/ghpvc/?username=umersanii&label=Visits&color=00FFFF&style=flat" alt="daenges" /> </p>


```python
class Sani:
    def __init__(self):
        self.username = "Umer Sani"
        self.education = "BS Computer Science"
        self.hobbies = ["Gaming", "Working Out", "Procastinating"]
        self.skills = [
            "Python",
            "C++",
            "C",
            "Git",
            "ChatGPT", #YES!
        ]
        self.fun_fact = "I write code that works... eventually, maybe"
        self.links = {
            "Discord": "https://discord.gg/d3eqSYmhyB",
            "Gmail": "mailto:iamumersani@gmail.com",
            "Steam": "https://steamcommunity.com/profiles/76561198965901738/",
            "LinkedIn": "https://www.linkedin.com/in/umer-sani-656372221/"
        }

        self.stats = self.fetch_stats()

    def fetch_stats(self):
        stats = {
            "total_repos": 0,
            "total_stars": 0,
            "total_commits": 0,
            "total_pull_requests": 0,
            "total_issues": 0,
            "total_followers": 0
        }
        return stats


```