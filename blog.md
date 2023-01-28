# Open Health Statistics - How it's made

The [Open Health Statistics](https://nhsx.github.io/open-health-statistics/) project has been developed using an end-to-end open source analytics pipeline consisting four key components:

The four components come together to create a very light and reusable pipeline for open analytics.

## [Github](https://docs.github.com/en/rest/reference/orgs)

An API (Application Program Interface) allows us to access web tools or data in the cloud. The Github / GitLab API's are designed so that we can create and manage our repositories, branches, issues, pull requests programmatically. Typically you would need to sign into your own account to access these features, but some information is publicly available. In this project we are using the API to access publicly available information on open source repositories published by NHS and health related organisations.

We use the `urllib.request` python library to access the API as follows:

```python
url = (
        "https://api.github.com/orgs/"  # github REST call
        + org_id                        # organisation github name
        + "/repos?page="                # list of open repos
        + str(page)                     # page count
        + "&per_page=100"               # no of results per page
      )
```

Note: you can only make 60 calls per hour to the public GitHub API, so we need to bear this in mind when looping through the API calls.

The outputs of the API call returns a `.json` file from which we can flatten to a `pandas` dataframe.

```Python
flat_data = pd.json_normalize(data)
```

