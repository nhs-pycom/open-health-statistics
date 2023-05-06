import pandas as pd
import numpy as np

# Data processing
import utilities.utilities as util

# Now we have a raw table we can begin to split and aggregate..
df = pd.read_csv("data/org_repos_raw.csv")

# tidy raw data
tidy_df = util.tidy_raw_df(df)

# aggregate to count cumulative open repos
aggregate_df = util.aggregate_org_raw(tidy_df)

# Now we need to get the top license + language for each organisation
top_license_df = util.create_top_column_df(tidy_df, "license_name")
top_language_df = util.create_top_column_df(tidy_df, "language")

# merge these dataframe together
aggregate_df = util.aggregate_github_data(aggregate_df, top_license_df, top_language_df)

# add data point at todays date and fill missing values
aggregate_df = util.fill_missing_values(aggregate_df)

# save to `data/` folder
aggregate_df.to_csv("data/org_repos_agg.csv", index=False)
