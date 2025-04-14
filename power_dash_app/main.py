import dash
from dash import html, dcc, Output, Input, callback
import pandas as pd
import plotly.express as px

#load data set
df = pd.read_csv('power_df.csv')

app = dash.Dash(__name__)
app.title = "US Power Outage Dashboard"

#app layout
app.layout = html.Div([
    html.H1("⚡ US Power Outage Dashboard", style={'textAlign': 'center'}),
    # collapsible key insight section
    html.Div([
        # Toggle Button
        html.Button("📊 Click here for key insights of this dataset", id="toggle-button", n_clicks=0, style={"margin": "10px"}),

        # Hidden state to store toggle status
        dcc.Store(id="insight-visible", data=False),

        # Collapsible Key Insight Panel
        html.Div(id="insight-panel", style={
            "padding": "20px",
            "backgroundColor": "#f9f9f9",
            "border": "1px solid #ddd",
            "borderRadius": "10px",
            "margin": "10px",
            "display": "none"
    })]),
    # KPI cards
    html.Div([

        html.P(
            f"{df['year'].nunique()} years run down- {df['year'].min()} to {df['year'].max()}.",
            style={'fontSize': '18px', 'textAlign': 'center'}
        ),

        # KPI Cards Row
        html.Div([
            html.Div([
                html.H6('Total power outage events', className='kpi_title'),
                html.P(f"{len(df):,.0f} events.", className='kpi_value')
            ], className='kpi_card'),

            html.Div([
                html.H6('Areas affected', className='kpi_title'),
                html.P(f"{df['area-affected'].nunique()} states.", className='kpi_value')
            ], className='kpi_card'),

            html.Div([
                html.H6('Average power loss', className='kpi_title'),
                html.P(f"{round(df['loss-(megawatts)'].astype(float).mean(), 2)} MW",
                        className='kpi_value')
            ], className='kpi_card'),
            html.Div([
                html.H6('In a typical event, these people lose power', className='kpi_title'),
                html.P(f"{df['number-of-customers-affected'].median():,.0f} people",
                        className='kpi_value')
            ],className='kpi_card')
        ],
    className='kpi_container')
    ]),
    #geographic specific
    html.Div([
        # Header
        html.H1('Geographic Specific', style={'textAlign': 'center', 'marginBottom': '30px'}),
        # create a choropleth and line plot
        html.Div([
            dcc.Graph(id='unique-states-plot')],
              style={'display': 'inline-block', "width": "49%"}),

        html.Div([
            dcc.Graph(id='location-plot')],
              style={'display': 'inline-block', "width": "49%"})
    ]),

    #filters
    html.Div([
    # Markdown guide
    dcc.Markdown(
        """
        ### Filter Events  
        Use the controls below to filter this dashboard based on **Year**, **State(s)**, and **Cause(s)**.
        """,
        style={'marginBottom': '10px'}
    ),

    # Filters row
    html.Div([
        #dummy that is hidden.trigger for static plots
        html.Div([dcc.Input(id='dummy', value='initial', type='text', style={'display': 'none'})]),
        # Year Slider
        html.Div([
            html.Label("Select Year", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='date-range',
                min=df['year'].min(),
                max=df['year'].max(),
                step=1,
                marks={year: str(year) for year in range(df['year'].min(), df['year'].max() + 1)},
                value=df['year'].min(),
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'flex': '2', 'paddingRight': '20px'}),

        # State Dropdown
        html.Div([
            html.Label("Select State(s)", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': s, 'value': s} for s in df['area-affected'].dropna().unique()],
                #multi=True,
                placeholder="Select state(s)",
                style={'width': '100%'}
            )
        ], style={'flex': '1', 'minWidth': '200px'}),

        # Cause Dropdown
        html.Div([
            html.Label("Select Cause(s)", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='cause-dropdown',
                options=[{'label': c, 'value': c} for c in df['cause'].dropna().unique()],
                value='Weather Events',
                style={'width': '100%'}
            )
        ], style={'flex': '1', 'minWidth': '200px'})
    ], style={'display': 'flex', 'gap': '20px', 'alignItems': 'center', 'marginTop': '10px'})
]),
    #trend questions,Three plots in the same row
    html.Div([
    # Header
    html.H1('Trend Questions - Year Specific', style={'textAlign': 'center', 'marginBottom': '30px'}),

    # Instructions text
    html.Div(
        children=[
            html.P("Filter by state using the dropdown menu above to get trends for a particular state.")
        ],
        style={'textAlign': 'center', 'marginBottom': '30px'}
    ),

    # First row: Bar Plot & Line Plot
    html.Div([
        html.Div([
            dcc.Graph(id='bar-plot-1')
        ], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='line-plot-1')
        ], style={'width': '50%', 'display': 'inline-block'}),
    ], style={'width': '100%'}),

    # Second row: Two more plots
    html.Div([
        html.Div([
            dcc.Graph(id='line-plot-2')
        ], style={'width': '41%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='line-plot-3')
        ], style={'width': '55%', 'display': 'inline-block'}),
    ], style={'width': '100%'})
]),
    html.Div([
        html.H1("Cause Specific Insights", style={'textAlign': 'center', 'marginBottom': '20px'}),

        # Section 1: Choropleth + Barh side by side
        html.Div([
            html.Div([
                html.H3("Where did this cause hit?"),
                dcc.Graph(id='choropleth-by-cause')
            ], style={'width': '55%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'top'}),

            html.Div([
                html.H3("Which states suffer the most?"),
                html.Div([
                    dcc.RadioItems(
                        id='impact-metric-toggle',
                        options=[
                            {'label': 'Power Loss', 'value': 'loss-(megawatts)'},
                            {'label': 'Customers Affected', 'value': 'number-of-customers-affected'}
                        ],
                        value='loss-(megawatts)',
                        labelStyle={'display': 'inline-block', 'marginRight': '15px'})
                ], style={'marginBottom': '10px'}),
                dcc.Graph(id='barh-most-affected-states')
            ], style={'width': '40%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'top'})
        ]),

        # Section 2: Yearly trend of cause impact
        html.Div([
            html.H3("Which cause contributed the most per year?"),
            html.Div([
                dcc.RadioItems(
                    id='yearly-cause-metric',
                    options=[
                        {'label': 'Power Loss', 'value': 'loss-(megawatts)'},
                        {'label': 'Customers Affected', 'value': 'number-of-customers-affected'}
                    ],
                    value='loss-(megawatts)' ,
                    labelStyle={'display': 'inline-block', 'marginRight': '15px'}
                )
            ], style={'marginBottom': '10px'}),
            dcc.Graph(id='cause-trend-yearly')
        ], style={'padding': '10px'})
    ])


])

# Import callbacks from the callback file
from callback import register_callbacks

# Register callbacks
register_callbacks(app)

#run app
if __name__ == '__main__':
    app.run_server(debug=True)