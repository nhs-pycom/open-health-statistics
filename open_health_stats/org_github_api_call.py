import yaml
import pandas as pd

import utilities.github_api_calls as github_api_call

# Load in the config parameters
with open("open_health_stats/org_list.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Pull the raw data from the APIs
access_token = "token"
raw_github_df = github_api_call.pull_raw_df(config["github_org_dict"])

# save file to .csvç
raw_github_df.to_csv("data/org_repos_raw.csv", index=False)