import os 
import json 
import requests
import datetime
import pandas as pd 

url = "https://api.github.com/search/repositories"
class RepositoryInfo:
    """
    This class is for anylizing MPS repositories on GitHub 
    to find out which is fit for the research. 
    
    It will use metrics as:
    - Number of commits - that can help to find active repositories and might have many breaking changes
    - Number of contributors 
    - Years of activity - likely to have breaking changes as the metamodels evolve
    - Number of breaking changes - give me more data about the evolution
    - Last date of commit - to find active repositories
    """
    
    def __init__(self, name, owner, contributors_count, commits_count, created_at, description, url, last_commit_date):
        self.name = name
        self.owner = owner
        self.contributors_count = contributors_count
        self.commits_count = commits_count
        self.created_at = created_at
        self.description = description
        self.url = url
        self.last_commit_date = last_commit_date
        
        
    def is_valid(self):
        """
        This function will check if the repository is valid for the research. 
        It will use as metrics: 
        - Number of commits > 50
        - Number of contributors > 2
        - Months of activity > 5
        - Last commit date < 1 month         
        """
        today = datetime.datetime.now()
        created_at = datetime.datetime.strptime(self.created_at, "%Y-%m-%dT%H:%M:%SZ")
        last_commit_date = datetime.datetime.strptime(self.last_commit_date, "%Y-%m-%dT%H:%M:%SZ")
        months_of_activity = (today.year - created_at.year) * 12 + today.month - created_at.month
        last_commit_days = (today - last_commit_date).days
        if self.commits_count > 50 and self.contributors_count > 2 and months_of_activity > 5 and last_commit_days < 30:
            return True
        return False    

    def search_repositories(self, query, per_page=10):
        params = {
            'q': query,
            'per_page': per_page,
            'sort': 'stars',
            'order': 'desc',
            'type': 'Repositories',
            'language': 'mps'
        }
        response = requests.get(url, params=params)
        self.repositories = []
        if response.status_code == 200:
            repos_data = response.json().get('items', [])
            for item in repos_data:
                repo = RepositoryInfo(
                    name=item['name'],
                    owner=item['owner']['login'],
                    contributors_count=self.get_contributors_count(item['contributors_url']),
                    commits_count=self.get_commits_count(item['commits_url'].split('{')[0]),
                    created_at=item['created_at'],
                    description=item['description'],
                    url=item['html_url'],
                    last_commit_date=self.get_last_commit_date(item['commits_url'].split('{')[0])
                )
                if repo.is_valid():
                    self.repositories.append(repo)
            return self.repositories
        else:
            print(f"Error: {response.status_code}")
            return []
        
    def get_contributors_count(self, contributors_url):
        response = requests.get(contributors_url) 
        if response.status_code == 200:
            contributors_data = response.json()
            return len(contributors_data) 
        else:
            return 0
    
    def get_commits_count(self, commits_url):
        response = requests.get(commits_url)
        
        if response.status_code == 200:
            commit_data = response.json()
            return len(commit_data)
        else: 
            return 0 
        
    def get_last_commit_date(self, commits_url):
        response = requests.get(commits_url)
        if response.status_code == 200:
            commit_data = response.json()
            if commit_data: 
                return commit_data[0] ['commit']['committer']['date']
            else:
                return "No commits"
        else:
            print(f"Error fetching commits: {response.status_code}")
            return "Error"
        
    def obj_to_dict(self):
        repo_dict = {
            "name": self.name,
            "owner": self.owner,
            "contributors_count": self.contributors_count,
            "commits_count": self.commits_count,
            "created_at": self.created_at,
            "last_commit_date": self.last_commit_date,
            "description": self.description,
            "url": self.url
        }
        return repo_dict
        
    def save_results_to_json(self, filename):
        all_data = []
        
        for repo in self.repositories:
            data = repo.obj_to_dict()
            all_data.append(data)
            
        with open(filename, 'w') as f:
            json.dump(all_data, f, indent=4)
        print(f"Results saved to {filename}")
        
if __name__ == "__main__":
    analyzer = RepositoryInfo(
        name="", owner="", contributors_count=0, commits_count=0,
        created_at="2025-01-01T00:00:00Z", description="", url="", last_commit_date="2025-01-01T00:00:00Z"
    )

    analyzer.search_repositories("mbeddr", per_page=5)

    print("\nValid repositories found:")
    for repo in analyzer.repositories:
        print(f"- {repo.name} | Owner: {repo.owner} | Commits: {repo.commits_count} | Contributors: {repo.contributors_count}")

    analyzer.save_results_to_json("saida.json")
 
       
        
     
        
        