# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([
                                    html.Label("Select Launch Site:"),
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[
                                            {'label': 'All Sites', 'value': 'ALL'},
                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                        ],
                                        value='ALL',
                                        placeholder="Select a Launch Site",
                                        style={'width': '50%', 'margin': 'auto'}
                                    )
                                ], style={'textAlign': 'center', 'padding': '10px'}),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site

                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                html.P("Payload range (Kg):"),

                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)


                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload],
                                    marks={0: '0 kg',
                                           2500: '2500 kg',
                                           5000: '5000 kg',
                                           7500: '7500 kg',
                                           10000: '10000 kg'}
                                ),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # For all sites, show total successful launches count for each site
        # Group by launch site and count successful launches (class = 1)
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='counts')
        fig = px.pie(success_counts, values='counts', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        # For specific site, show Success vs Failed counts
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_failed = site_data['class'].value_counts().reset_index()
        success_failed.columns = ['class', 'count']
        success_failed['class'] = success_failed['class'].map({1: 'Success', 0: 'Failed'})
        fig = px.pie(success_failed, values='count', names='class',
                     title=f'Launch Outcomes for {selected_site}')

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data by payload range
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site == 'ALL':
        # For all sites, show all launches
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload vs. Launch Outcome for All Sites',
                         labels={'class': 'Launch Outcome (0=Fail, 1=Success)',
                                 'Payload Mass (kg)': 'Payload Mass (kg)'})
    else:
        # For specific site, filter by that site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(site_filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload vs. Launch Outcome for {selected_site}',
                         labels={'class': 'Launch Outcome (0=Fail, 1=Success)',
                                 'Payload Mass (kg)': 'Payload Mass (kg)'})

    # Improve scatter plot appearance
    fig.update_layout(yaxis=dict(tickmode='linear', tick0=0, dtick=1))
    fig.update_traces(marker=dict(size=10))

    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
