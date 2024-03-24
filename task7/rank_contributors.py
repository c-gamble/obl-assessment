import os
import requests
from dotenv import load_dotenv
import pickle
from tqdm.auto import tqdm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

load_dotenv()

# Hyperparameters
UPDATE = {
    'contributors': False,
    'commits': False,
    'pulls': False,
    'issues': False,
    'comments': False,
    'lines': False # if True, execution will take a long time
} # Set to True to update data

OWNER = "paritytech"
REPO = "polkadot-sdk"

METRICS = {
    'n_commits': 0.3, 
    'n_pr_merged': 0.25, 
    'n_issues_opened': 0.2, 
    'n_comments': 0.15, 
    'n_lines': 0.1
}

# Fetch contributors
URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contributors?per_page=100"
def get_contributors(URL):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_API_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(URL, headers=headers)
    return response

CONTRIBUTORS = []
if UPDATE['contributors']:
    pages_remaining = True
    while pages_remaining:
        response = get_contributors(URL)
        contributors = response.json()
        CONTRIBUTORS.extend(contributors)
        if "next" in response.links:
            URL = response.links["next"]["url"]
        else:
            pages_remaining = False
    pickle.dump(CONTRIBUTORS, open('./data/contributors.pkl', 'wb'))
    print(f'{len(CONTRIBUTORS)} contributors found and saved to data/contributors.pkl')
else: 
    CONTRIBUTORS = pickle.load(open('./data/contributors.pkl', 'rb'))
    print(f'{len(CONTRIBUTORS)} contributors loaded from data/contributors.pkl')

# Fetch commits
URL = f"https://api.github.com/repos/{OWNER}/{REPO}/commits?per_page=100"
def get_commits(URL):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_API_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(URL, headers=headers)
    return response

COMMITS = []
if UPDATE['commits']:
    pages_remaining = True
    while pages_remaining:
        response = get_commits(URL)
        commits = response.json()
        COMMITS.extend(commits)
        if "next" in response.links:
            URL = response.links["next"]["url"]
        else:
            pages_remaining = False
    pickle.dump(COMMITS, open('./data/commits.pkl', 'wb'))
    print(f'{len(COMMITS)} commits found and saved to data/commits.pkl')
else:
    COMMITS = pickle.load(open('./data/commits.pkl', 'rb'))
    print(f'{len(COMMITS)} commits loaded from data/commits.pkl')


# Fetch pull requests
URL = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls?per_page=100&state=closed"
def get_pulls(URL):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_API_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(URL, headers=headers)
    return response

PULLS = []
if UPDATE['pulls']:
    pages_remaining = True
    while pages_remaining:
        response = get_pulls(URL)
        pulls = response.json()
        PULLS.extend(pulls)
        if "next" in response.links:
            URL = response.links["next"]["url"]
        else:
            pages_remaining = False
    MERGED_PULLS = [pull for pull in PULLS if pull['merged_at']]
    pickle.dump(MERGED_PULLS, open('./data/merged_pulls.pkl', 'wb'))
    print(f'{len(MERGED_PULLS)} merged pull requests found and saved to data/merged_pulls.pkl')
else:
    MERGED_PULLS = pickle.load(open('./data/merged_pulls.pkl', 'rb'))
    print(f'{len(MERGED_PULLS)} merged pull requests loaded from data/merged_pulls.pkl')


# Fetch issues
URL = f"https://api.github.com/repos/{OWNER}/{REPO}/issues?per_page=100&state=open"
def get_issues(URL):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_API_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(URL, headers=headers)
    return response

ISSUES = []
if UPDATE['issues']:
    pages_remaining = True
    while pages_remaining:
        response = get_issues(URL)
        issues = response.json()
        ISSUES.extend(issues)
        if "next" in response.links:
            URL = response.links["next"]["url"]
        else:
            pages_remaining = False
    pickle.dump(ISSUES, open('./data/issues.pkl', 'wb'))
    print(f'{len(ISSUES)} issues found and saved to data/issues.pkl')
else:
    ISSUES = pickle.load(open('./data/issues.pkl', 'rb'))
    print(f'{len(ISSUES)} issues loaded from data/issues.pkl')


# Fetch comments
URL = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/comments?per_page=100"
def get_comments(URL):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_API_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }   
    response = requests.get(URL, headers=headers)
    return response

COMMENTS = []
if UPDATE['comments']:
    pages_remaining = True
    while pages_remaining:
        response = get_comments(URL)
        comments = response.json()
        COMMENTS.extend(comments)
        if "next" in response.links:
            URL = response.links["next"]["url"]
        else:
            pages_remaining = False
    pickle.dump(COMMENTS, open('./data/comments.pkl', 'wb'))
    print(f'{len(COMMENTS)} comments found and saved to data/comments.pkl')
else:
    COMMENTS = pickle.load(open('./data/comments.pkl', 'rb'))
    print(f'{len(COMMENTS)} comments loaded from data/comments.pkl')


# Fetch lines of code
def get_lines_from_commit(commit):
    url = commit['url']
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_API_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(url, headers=headers)
    response = response.json()

    total = 0

    if 'files' not in response or 'author' not in response or response['files'] == None or response['author'] == None:
        return (None, total)
    
    for file in response['files']:
        total += file['additions'] + file['deletions']
    return (response['author']['login'], total)

LINES = []
if UPDATE['lines']:
    for commit in tqdm(COMMITS):
        lines = get_lines_from_commit(commit)
        if lines[0]: LINES.append(lines)
    pickle.dump(LINES, open('./data/lines.pkl', 'wb'))
    print(f'{len(LINES)} commits reviewed and saved to data/lines.pkl')
else:
    LINES = pickle.load(open('./data/lines.pkl', 'rb'))
    print(f'{len(LINES)} commits reviewed and loaded from data/lines.pkl')


CONTRIBUTOR_METRICS = {contributor['login']: {metric: 0 for metric in METRICS} for contributor in CONTRIBUTORS}


"""These could be optimized but since the data is not too large, I will keep it simple"""
# Populate n_commits
for contributor in CONTRIBUTORS:
    contributor_name = contributor['login']
    CONTRIBUTOR_METRICS[contributor_name]['n_commits'] = len([commit for commit in COMMITS if commit['author'] and commit['author']['login'] == contributor_name])

# Populate n_pr_merged
for contributor in CONTRIBUTORS:
    contributor_name = contributor['login']
    CONTRIBUTOR_METRICS[contributor_name]['n_pr_merged'] = len([pull for pull in MERGED_PULLS if pull['user']['login'] == contributor_name])
    
# Populate n_issues_opened
for contributor in CONTRIBUTORS:
    contributor_name = contributor['login']
    CONTRIBUTOR_METRICS[contributor_name]['n_issues_opened'] = len([issue for issue in ISSUES if issue['user']['login'] == contributor_name])

# Populate n_comments
for contributor in CONTRIBUTORS:
    contributor_name = contributor['login']
    CONTRIBUTOR_METRICS[contributor_name]['n_comments'] = len([comment for comment in COMMENTS if comment['user']['login'] == contributor_name])

# Populate n_lines
for contributor in CONTRIBUTORS:
    contributor_name = contributor['login']
    CONTRIBUTOR_METRICS[contributor_name]['n_lines'] = sum([lines[1] for lines in LINES if lines[0] == contributor_name])

# Calculate scores
CONTRIBUTOR_SCORES = {contributor: sum([CONTRIBUTOR_METRICS[contributor][metric] * METRICS[metric] for metric in METRICS]) for contributor in CONTRIBUTOR_METRICS}

# Normalize scores between 0 and 100
min_score = np.min(list(CONTRIBUTOR_SCORES.values()))
max_score = np.max(list(CONTRIBUTOR_SCORES.values()))

for contributor in CONTRIBUTOR_SCORES:
    CONTRIBUTOR_SCORES[contributor] = (CONTRIBUTOR_SCORES[contributor] - min_score) / (max_score - min_score) * 100

# Create dataframe structure
CONTRIBUTOR_DICT = {
    'gh_username': list(CONTRIBUTOR_METRICS.keys()),
    'n_commits': [CONTRIBUTOR_METRICS[contributor]['n_commits'] for contributor in CONTRIBUTOR_METRICS],
    'n_pr_merged': [CONTRIBUTOR_METRICS[contributor]['n_pr_merged'] for contributor in CONTRIBUTOR_METRICS],
    'n_issues_opened': [CONTRIBUTOR_METRICS[contributor]['n_issues_opened'] for contributor in CONTRIBUTOR_METRICS],
    'n_comments': [CONTRIBUTOR_METRICS[contributor]['n_comments'] for contributor in CONTRIBUTOR_METRICS],
    'n_lines': [CONTRIBUTOR_METRICS[contributor]['n_lines'] for contributor in CONTRIBUTOR_METRICS],
    'score': [CONTRIBUTOR_SCORES[contributor] for contributor in CONTRIBUTOR_METRICS]
}

# Plot distribution of scores
plt.hist(list(CONTRIBUTOR_SCORES.values()), bins=50)
plt.title('Distribution of Normalized Contributor Scores')
plt.xlabel('Score')
plt.ylabel('Frequency')
plt.savefig('./output/scores_distribution.png')

# Reorder dataframe by score (best first)
CONTRIBUTOR_DF = pd.DataFrame(CONTRIBUTOR_DICT)
CONTRIBUTOR_DF = CONTRIBUTOR_DF.sort_values(by='score', ascending=False)
CONTRIBUTOR_DF.to_csv('./output/contributors.csv', index=False)