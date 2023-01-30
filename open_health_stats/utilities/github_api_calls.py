import urllib.request
import json
import time
import pandas as pd
import os

def pull_raw_df(github_org_dict):

    access_token = os.environ['ACCESS_TOKEN']
    results_per_page = 100
    # Initialise a dataframe
    df = pd.DataFrame()

    for key, org in github_org_dict.items():
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
            print(f'{org} repo count = {repos_count}')

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