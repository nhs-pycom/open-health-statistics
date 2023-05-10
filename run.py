# Python notebook source
# -------------------------------------------------------------------------
# Copyright (c) 2023 NHS Python Community. All rights reserved.
# Licensed under the MIT License. See license.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# FILE:           run.py
# DESCRIPTION:    Process GitHub API data

# CONTRIBUTORS:   Craig R. Shenton
# CONTACT:        craig.shenton@nhs.net
# CREATED:        10 May 2023
# VERSION:        0.2.0

# -------------------------------------------------------------------------
import pandas as pd
import yaml
import timeit 
from pathlib import Path
import logging
from src.ingestion.github_api_call import query_org_repos
from src.processing.data_processing import tidy_raw_df, create_top_column_df, aggregate_org_raw, aggregate_github_data, fill_missing_values
from src.utils.file_paths import get_config
from src.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)

def load_yaml(org_list: str) -> list:
    logger.info(f"Load list of NHS GitHub organisations from {org_list}.")
    with open(org_list, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def get_raw_github_df(config: list) -> pd.DataFrame:
    return query_org_repos(github_org_dict=config["github_org_dict"],
                                           csv_path="open_health_stats/data/org_repos_raw.csv",
                                           max_retries=3)

def tidy_up_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    tidy_df = tidy_raw_df(raw_df)
    return aggregate_org_raw(tidy_df)

def get_top_license_and_language(tidy_df: pd.DataFrame) -> pd.DataFrame:
    top_license_df = create_top_column_df(tidy_df, "license_name")
    top_language_df = create_top_column_df(tidy_df, "language")
    return aggregate_github_data(aggregate_org_raw(tidy_df), top_license_df, top_language_df)

def add_missing_values_and_filter(tidy_df: pd.DataFrame) -> pd.DataFrame:
    filtered_org_df = tidy_df.groupby("owner_login").first().reset_index()
    merged_df = get_top_license_and_language(tidy_df).merge(filtered_org_df[["owner_html_url"] + ["owner_login"]], left_on="Organisation", right_on="owner_login")
    merged_df = merged_df.drop(["owner_login"], axis=1)
    merged_df = merged_df.rename(columns={'owner_html_url': 'URL'})
    merged_df = merged_df.reindex(columns=['Organisation', 'Date', 'Open Repositories', 'Top Language', 'Top License', 'URL'])
    return fill_missing_values(merged_df)

def main():
    # load config, here we load our project's parameters from the config.toml file
    config = get_config("config.toml") 
    raw_sink = Path(config['output_dir'])
    agg_sink = Path(config['output_dir'])
    org_list = Path(config['org_list'])
    log_dir = Path(config['log_dir'])

    # configure logging
    configure_logging(log_dir, config)
    logger.info(f"Configured logging with log folder: {log_dir}.")

    # run data pipeline
    github_org_list = load_yaml(org_list)
    raw_github_df = get_raw_github_df(github_org_list)
    raw_github_df.to_csv(raw_sink, index=False)
    logger.info(f"Saved raw data in folder: {raw_sink}.")
    agg_github_df = add_missing_values_and_filter(tidy_up_df(raw_github_df))
    agg_github_df.to_csv(agg_sink, index=False)
    logger.info(f"Saved aggregate data in folder: {agg_sink}.")

if __name__ == "__main__":
    print("Running processing script")
    start_time = timeit.default_timer()
    main()
    total_time = timeit.default_timer() - start_time
    print(f"Running time of processing script: {int(total_time / 60)} minutes and {round(total_time%60)} seconds.\n")
