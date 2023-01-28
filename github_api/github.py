import urllib.request
import json
import time
import pandas as pd
import os

def pull_raw_df(org_dict):

    access_token = os.environ['ACCESS_TOKEN']
    results_per_page = 100
    # Initialise a dataframe
    df = pd.DataFrame()

    for org in org_dict.values():
        page = 1
        while True:
            url = "https://api.github.com/orgs/" + org + "/repos?access_token=" + access_token + "&per_page=" + str(results_per_page) + "&page=" + str(page)
            req = urllib.request.Request(url)
            req.add_header('Authorization', f'Token {access_token}')

            response = urllib.request.urlopen(req)

            try:
                data = json.loads(response.read())
                data = [repo for repo in data if not repo["private"]]
                data = [repo for repo in data if not repo["fork"]]

            except json.decoder.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                continue
            flat_data = pd.json_normalize(data)
            df = pd.concat([df, flat_data], axis = 0)
            repos_count = len(data)

            # check if we have reached the API limit
            if response.status == 403:
                reset_time = response.getheader("X-RateLimit-Reset")
                current_time = int(time.time())
                wait_time = int(reset_time) - current_time
                print(
                    f"API limit reached. Waiting for {str(wait_time)} seconds until limit is reset."
                )
                time.sleep(wait_time)
                continue

            # check if there are more pages
            if repos_count < results_per_page:
                break
            else:
                page += 1



def tidy_raw_df(df):
    
    # Add a column of 1s to sum for open_repos (this enables us to use sum() on 
    # all columns later)
    df["open_repo_count"] = 1

    # Filter and rename columns
    keep = ['id','name','full_name','private','html_url','description','fork','owner.login','owner.type',
        'license.key','license.name','topics','visibility','forks','open_issues','watchers','default_branch',
        'created_at','updated_at','pushed_at','homepage','size	stargazers_count','watchers_count','language',
        'has_issues','has_projects','has_downloads','has_wiki	has_pages','has_discussions','forks_count',
        'mirror_url','archived','disabled','open_issues_count','allow_forking','is_template',
        'permissions.admin','permissions.maintain','permissions.push','permissions.triage','permissions.pull',
        'security_and_analysis.secret_scanning.status',
        'security_and_analysis.secret_scanning_push_protection.status','license']

    filtered_df = df.filter(items=keep)
    filtered_df.rename(
        columns={
                 "security_and_analysis.secret_scanning.status": "secret_scanning.status",
                 "security_and_analysis.secret_scanning_push_protection.status": "push_protection.status"
                }, inplace=True)
    filtered_df.rename(columns=lambda x: x.replace(".", "_"), inplace=True)

        
    return filtered_df