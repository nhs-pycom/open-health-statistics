import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta

df = pd.read_csv("data/org_repos_agg.csv")

# Convert the "Date" column to a datetime dtype
df['Date'] = pd.to_datetime(df['Date'])

# Filter the latest date for each organization
latest_dates = df.groupby('Organisation')['Date'].idxmax()
latest_df = df.loc[latest_dates]

# Create a new column with hyperlinks for the "Organisation" column
latest_df['Organisation'] = latest_df.apply(lambda x: f"[{x['Organisation']}]({x['URL']})", axis=1)

# Drop the "Date" column and sort by "Open Repositories"
latest_df = latest_df.drop(['Date', 'URL'], axis=1).sort_values('Open Repositories', ascending=False)

# Convert the sorted DataFrame to a markdown table and print it
md_table = latest_df.to_markdown(index=False)

def plotly_chart(df: pd.DataFrame,
                     group_col: str,
                     values_col: str,
                     date_col: str,
                     plot_title: str,
                     x_lab: str,
                     y_lab: str) -> None:
    # Group the DataFrame by Organisation
    grouped_df = df.groupby(group_col)
    
    data = []
    for org, org_df in grouped_df:
        
        # Create a scatter plot of the data points for each organisation
        scatter = go.Scatter(
            x=org_df[date_col],
            y=org_df[values_col],
            name=org,
            mode='lines',
            line=dict(width=3, dash='solid'),
            hovertemplate=f'%{{y:.0f}}'
        )
        data.append(scatter)
    
    # Set options
    min_xaxis = min(df[date_col])
    max_xaxis = max(df[date_col])
    max_yaxis = max(df[values_col])
    remove = ['zoom2d','pan2d', 'select2d', 'lasso2d', 'zoomIn2d',
            'zoomOut2d', 'autoScale2d', 'resetScale2d', 'zoom',
            'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale',
            'resetScale', 'toggleSpikelines', 'hoverClosestCartesian',
            'hoverCompareCartesian', 'toImage']
    
    # Set layout
    layout = go.Layout(title=plot_title,
                       font=dict(size=12),
                       xaxis=dict(title=x_lab,
                                  # add more time to x-axis to show plot circles
                                  range=[min_xaxis - relativedelta(days=5),
                                         max_xaxis + relativedelta(days=5)]),
                       yaxis=dict(title=y_lab,
                                  # fix y0 at 0 and add 10% to y1
                                  range=[0, max_yaxis + (max_yaxis * 0.1)]),
                       showlegend=False,
                       hovermode="x unified")
    
    # Set configuration
    config = {'displaylogo': False,
              'displayModeBar': True,
              'modeBarButtonsToRemove': remove}
    
    # Create the figure and show()
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(template='plotly_white')
    fig.show(config=config)

open_repo_chart = plotly_chart(df, "Organisation", "Open Repositories", "Date", "The growth of open-source in healthcare", "Date", "Open Repositories")