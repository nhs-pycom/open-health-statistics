import requests
import json
import time
import pandas as pd
import os

def fetch_public_repos(org_name, page=1, results_per_page=100):
    """
    Fetches public GitHub repositories for a given organization and returns the raw JSON data.

    Args:
        org_name (str): The name of the GitHub organization to fetch repositories for.
        page (int, optional): The page of results to fetch. Defaults to 1.
        results_per_page (int, optional): The number of results to fetch per page. Defaults to 100.

    Returns:
        dict: A dictionary containing the JSON data returned by the GitHub API.
    """
    url = f"https://api.github.com/orgs/{org_name}/repos"
    headers = {"Accept": "application/vnd.github.v3+json"}
    params = {"page": page, "per_page": results_per_page}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()

def parse_github_repos(raw_data):
    """
    Parses raw GitHub repository JSON data into a Pandas DataFrame.

    Args:
        raw_data (dict): A dictionary containing the raw JSON data returned by the GitHub API.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing repository information.
    """
    data = [repo for repo in raw_data if not repo["private"]]
    data = [repo for repo in data if not repo["fork"]]
    return pd.json_normalize(data)

def pull_raw_df(github_org_dict, max_retries=3):
    """
    Pulls raw GitHub repository data for multiple organizations and returns a consolidated DataFrame.

    Args:
        github_org_dict (dict): A dictionary containing GitHub organizations to fetch repositories for.
            Values should be organization names.
        max_retries (int, optional): The maximum number of times to retry the API request if a rate limit is encountered.
            Defaults to 3.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing information about repositories for all specified organizations.
    """
    df = pd.DataFrame()

    for org in github_org_dict.values():
        page = 1
        retries = 0
        while True:
            try:
                raw_data = fetch_public_repos(org, page=page)
                repos_count = len(raw_data)
                print(f"{org} repo count = {repos_count}")

                if repos_count == 0:
                    break

                parsed_data = parse_github_repos(raw_data)
                df = pd.concat([df, parsed_data], axis=0)

                # check if there are more pages
                if repos_count < 100:
                    break
                else:
                    page += 1

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"Rate limit exceeded for organization {org}.")
                    if retries >= max_retries:
                        print(f"Max retries exceeded for organization {org}. Moving on.")
                        break
                    reset_time = int(e.response.headers.get("X-RateLimit-Reset"))
                    wait_time = reset_time - time.time() + 1
                    print(f"Waiting {wait_time} seconds until rate limit is reset.")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    print(f"Error fetching data for {org}: {e}")
                    break

    return df