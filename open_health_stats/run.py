# Python notebook source
# -------------------------------------------------------------------------
# Copyright (c) 2023 NHS Python Community. All rights reserved.
# Licensed under the MIT License. See license.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# FILE:           run.py
# DESCRIPTION:    Pull GitHub API data

# CONTRIBUTORS:   Craig R. Shenton
# CONTACT:        craig.shenton@nhs.net
# CREATED:        10 May 2023
# VERSION:        0.2.0

# -------------------------------------------------------------------------
import yaml
import pandas as pd
import logging

import utilities.utilities as util
import utilities.github_api_call as github_api_call

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] - %(message)s",
                    handlers=[logging.StreamHandler()])

def load_config():
    with open("open_health_stats/org_list.yaml", "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def get_raw_github_df(config):
    return github_api_call.query_org_repos(github_org_dict=config["github_org_dict"],
                                           csv_path="open_health_stats/data/org_repos_raw.csv",
                                           max_retries=3)

def tidy_up_df(raw_df):
    tidy_df = util.tidy_raw_df(raw_df)
    return util.aggregate_org_raw(tidy_df)

def get_top_license_and_language(tidy_df):
    top_license_df = util.create_top_column_df(tidy_df, "license_name")
    top_language_df = util.create_top_column_df(tidy_df, "language")
    return util.aggregate_github_data(util.aggregate_org_raw(tidy_df), top_license_df, top_language_df)

def add_missing_values_and_filter(tidy_df):
    filtered_org_df = tidy_df.groupby("owner_login").first().reset_index()
    merged_df = get_top_license_and_language(tidy_df).merge(filtered_org_df[["owner_html_url"] + ["owner_login"]], left_on="Organisation", right_on="owner_login")
    merged_df = merged_df.drop(["owner_login"], axis=1)
    merged_df = merged_df.rename(columns={'owner_html_url': 'URL'})
    merged_df = merged_df.reindex(columns=['Organisation', 'Date', 'Open Repositories', 'Top Language', 'Top License', 'URL'])
    return util.fill_missing_values(merged_df)

def main():
    config = load_config()
    raw_github_df = get_raw_github_df(config)
    raw_github_df.to_csv("open_health_stats/data/org_repos_raw.csv", index=False)
    agg_github_df = add_missing_values_and_filter(tidy_up_df(raw_github_df))
    agg_github_df.to_csv("open_health_stats/data/org_repos_agg.csv", index=False)

if __name__ == "__main__":
    main()