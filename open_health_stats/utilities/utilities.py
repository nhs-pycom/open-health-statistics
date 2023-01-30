import pandas as pd
import numpy as np

# Tidy the raw data
def tidy_raw_df(df):
    
    # Add a column of 1s to sum for open_repos (this enables us to use sum() on 
    # all columns later)
    df["open_repo_count"] = 1

    # Replace synonym languages
    replace_dict = {'Jupyter Notebook': 'Python', 'SCSS': 'HTML', 'CSS': 'HTML'}

    # replace the values in col1 using the dictionary
    df['language'] = df['language'].replace(replace_dict)


    # Filter and rename columns
    keep = ['id','name','full_name','private','html_url','description','fork','owner.login','owner.type',
        'license.key','license.name','topics','visibility','forks','open_issues','watchers','default_branch',
        'created_at','updated_at','pushed_at','homepage','size','stargazers_count','watchers_count','language',
        'has_issues','has_projects','has_downloads','has_wiki	has_pages','has_discussions','forks_count',
        'mirror_url','archived','disabled','open_issues_count','allow_forking','is_template',
        'permissions.admin','permissions.maintain','permissions.push','permissions.triage','permissions.pull','open_repo_count']

    filtered_df = df.filter(items=keep)
    filtered_df.rename(columns=lambda x: x.replace(".", "_"), inplace=True)

        
    return filtered_df

def aggregate_org_raw(df):
    # start by changing date to a date type (day only)
    df['created_at'] = pd.to_datetime(df['created_at']).apply(lambda x: x.strftime("%Y-%m-%d"))

    # Cumulative sum by org, link and date of the numerical columns
    aggregate_df = (
        df.groupby(['owner_login', 'created_at'])
        .sum(['open_repo_count','size'])
        .groupby(level=[0])
        .cumsum()
        .reset_index()
    )
    return aggregate_df[['owner_login', 'created_at', 'open_repo_count']]

def create_top_column_df(df, column):
    return (
        df
        # Get the count of new columns values at each date
        .groupby(['owner_login', 'created_at', column])
        .size()
        # Convert to a cumulative count of the column values
        .groupby(level=[0, 2])
        .cumsum()
        .reset_index(level=column)
        # Get a column per value
        .pivot(columns=column)
        .droplevel(0, axis=1)
        # Forward fill so that each column has the previous value until it
        # increases again
        .groupby(['owner_login'])
        .ffill()
        # Convert to long and remove NaNs
        .reset_index()
        .melt(id_vars=['owner_login', 'created_at'], var_name=column, value_name = 'count')
        .dropna()
        # Keep the column value with the largest count each day
        .sort_values(by = ['owner_login', 'created_at', "count"])
        .drop_duplicates(subset = ['owner_login', 'created_at'], keep = 'last')
        # Get rid of the count column
        .drop(columns = ['count'])
        .reset_index(drop = True)
    )

def aggregate_github_data(aggregate_df, top_license_df, top_language_df):
    aggregate_df = (
        aggregate_df
        .merge(top_license_df, how="left")
        .merge(top_language_df, how="left")
        .apply(lambda df: df.ffill())
    )
    aggregate_df = aggregate_df.rename(
        columns={
            "owner_login": "Organisation",
            "created_at": "Date",
            "open_repo_count": "Open Repositories",
            "license_name": "Top License",
            "language": "Top Language",
        }
    )
    return aggregate_df

def fill_missing_values(df):
    df['Date'] = pd.to_datetime(df['Date'])
    from datetime import datetime,date
    #create a new dataframe with today's date for each organization
    today_df = pd.DataFrame(columns=df.columns)
    organizations = df['Organisation'].unique()
    for org in organizations:
        today_df = pd.concat([today_df, pd.DataFrame({'Organisation': [org], 'Date': [date.today()]})], ignore_index=True)

    # concatenate the new dataframe with today's date and the original dataframe
    df = pd.concat([df, today_df], ignore_index=True)

    #sort the dataframe by date and organization
    df = df.sort_values(by=['Organisation','Date'])

    #group by organization and fill missing values with the last known value
    df = df.ffill()

    #reset index to keep the organisation col
    #df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df