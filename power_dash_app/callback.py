from dash import Input, Output, dcc, html,State, ctx
import plotly.express as px
import pandas as pd
import json

#load data set
df = pd.read_csv('power_df.csv')
# read in the dictionary with state abbreviations
with open("state_to_abbr.json", "r") as f:
    STATE_TO_ABBR = json.load(f)
# create a state col
df['state'] = df['area-affected'].map(STATE_TO_ABBR) 

# register call backs
def register_callbacks(app):
    #call back for key insight button
    #Decides whether to show or hide the panel.Changes the button label.
    #Populates the insights panel with content (only if visible).
    @app.callback(
    Output("insight-panel", "style"),
    Output("insight-panel", "children"),
    Output("toggle-button", "children"),
    Input("toggle-button", "n_clicks"),
    State("insight-visible", "data"),
    prevent_initial_call=True)
    def toggle_insights(n_clicks, is_visible):
        visible = not is_visible
        style = {
            "padding": "20px",
            "backgroundColor": "#f9f9f9",
            "border": "1px solid #ddd",
            "borderRadius": "10px",
            "margin": "10px",
            "display": "block" if visible else "none"
        }
        button_text = "❌ Hide Insights" if visible else "📊 Click here for key insights of this dataset"

        insights = [
            html.H4("Key Insights"),
            html.Ul([
                html.Li("✅ Power outages have increased overtime.we see drastic increases in 2003,2008,2011"),
                html.Li("⚡ Kentucky records the highest number of outage events whereas Hawaii and PuertoRico have the least."),
                html.Li("🌪️ Severe weather is the leading outage cause followed by transmission issues."),
                html.Li("📈 suspicious events and cyber events are first recorded in 2011 and cases only increase afterwards."),
                html.Li("📈 Unique states affected rose incresed. we see drastic increase during 2002,2003,2004,2011."),
                html.Li("📈 2019 registers the highest ever power loss."),
                html.Li("📈 Number of customers reduced over the years with 84% decrease overall thus showing improvement."),
            ])
        ]

        return style, insights, button_text
    #Updates the internal insight-visible state for use the next time the button is clicked.
    @app.callback(
        Output("insight-visible", "data"),
        Input("toggle-button", "n_clicks"),
        State("insight-visible", "data"),
        prevent_initial_call=True
    )
    
    def update_visibility(n_clicks, is_visible):
        return not is_visible
    
    # Callback to update both plots
    @app.callback(
        [Output('unique-states-plot', 'figure'),
        Output('location-plot', 'figure')],
        [Input('dummy', 'value')])
    #function to generate choropleth plot
    def update_geographic_plots(dummy_value):
        # Line Plot (unique states per year)
        unique_states_per_year = df.groupby('year')['area-affected'].nunique().reset_index()
        unique_states_per_year.columns = ['year', 'unique_states']

        line_fig = px.line(
            unique_states_per_year,
            x='year',
            y='unique_states',
            markers=True,
            title="Number of Unique States Affected per Year"
        )

        # Choropleth Plot
        #create a state count column using frequency encoding
        df['state_count'] = df['area-affected'].map(df['area-affected'].value_counts())
        #create a chooropleth to visualize the number of usa states that received power challenges in our data
        choropleth_fig = px.choropleth(df,
                            locations = 'state',
                            locationmode="USA-states",
                            hover_name= 'area-affected',
                            scope='usa',
                            color='state_count',
                            color_continuous_scale=px.colors.sequential.Viridis,
                            title='map showing number of usa states that faced power challenges')

        

        return line_fig,choropleth_fig
    
    # callback for trend questions
    @app.callback(
        # Output for the three plots (bar plot and two line plots)
        [Output('bar-plot-1', 'figure'),
        Output('line-plot-1', 'figure'),
        Output('line-plot-2', 'figure'),
        Output('line-plot-3', 'figure')],
        [Input('state-dropdown', 'value')]  
    )
    def update_graphs(value):
        # Sample data filtering based on the selected state
        # If no state is selected (or empty list), show the entire dataset
        if not value:
            filtered_data = df  # Use the whole dataset
        else:
            filtered_data = df[df['area-affected'] == value]   # Filter by selected states
         
        # Bar Plot
        bar_fig = px.bar(filtered_data['year'].value_counts().sort_index(), 
                        title='Are outages becoming more or less frequent each year?')
        bar_fig.update_layout(showlegend = False,
                    yaxis_title = 'event counts per year')

        # Line Plot 1
        line_fig_1 = px.line(filtered_data.groupby(['year'])['loss-(megawatts)'].max(),
                title='What was the maximum power loss in each year?')
        line_fig_1.update_layout(showlegend = False,
                    yaxis_title = 'power loss in MW')

        # Line Plot 2
        line_fig_2 = px.line(filtered_data.groupby(['year'])['number-of-customers-affected'].mean(),
                title='Does average number of people affected change over time?')
        line_fig_2.update_layout(showlegend = False,
                    yaxis_title = 'Number of people affeced')
        #line-plot 3
        #get number of events recorded by year per cause
        df_grouped = filtered_data.groupby(['year','cause']).cause.count().reset_index(name='count')
        # Plot
        line_fig_3 =  px.line(
            df_grouped,
            x='year',
            y='count',
            color='cause',
            markers=True,
            title='Power Outage Trends by Cause Over the Years'
        )

        line_fig_3.update_layout(
            xaxis_title='Year',
            yaxis_title='Number of Outages',
            legend_title='Cause',
            template='plotly_white'
        )

        
        return bar_fig, line_fig_1, line_fig_2, line_fig_3
    # callback for choropleth, barplot and lineplot
    @app.callback(
        Output('choropleth-by-cause', 'figure'),
        Input('cause-dropdown', 'value')
    )
    def update_choropleth(selected_cause):
        
        """filters the power_df, creates a count column and returns a fig"""
        #filter the df basing on the cause column and create a copy
        data = df.query("cause == @selected_cause").copy()
        #create a count column
        data['count'] = data['state'].map(data['state'].value_counts())
        #create a fig
        fig = px.choropleth(data,
                            locations = 'state',
                            locationmode="USA-states",
                            hover_name= 'area-affected',
                            scope='usa',
                            color='count',
                            color_continuous_scale=px.colors.sequential.Viridis,
                            title=f"states that faced power challenges due to {selected_cause}")
        
        fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0},showlegend = False)
        return fig

    @app.callback(
        Output('barh-most-affected-states', 'figure'),
        Input('cause-dropdown', 'value'),
        Input('impact-metric-toggle', 'value')
    )
    def update_barh(selected_cause, metric):
        data = df[df['cause'] == selected_cause]
        avg = data.groupby('area-affected', as_index=False)[metric].mean()
        avg = avg.sort_values(by=metric, ascending=True).tail(10).dropna()
        fig = px.bar(
            avg,
            x=metric,
            y='area-affected',
            orientation='h',
            labels={metric: 'Average', 'area-affected': 'State'},
            title=f"Top States by Avg {metric.capitalize()} - {selected_cause}"
        )
        fig.update_layout(yaxis=dict(title=''), margin=dict(l=40, r=10, t=30, b=30))
        return fig

    @app.callback(
        Output('cause-trend-yearly', 'figure'),
        Input('yearly-cause-metric', 'value')
    )
    def update_cause_trend(metric):
        data = df.groupby(['year', 'cause'], as_index=False)[metric].sum()
        fig = px.line(
            data,
            x='year',
            y=metric,
            color='cause',
            markers=True,
            title=f"Yearly Total {metric.capitalize()} by Cause"
        )
        fig.update_layout(xaxis_title='Year', yaxis_title=metric.capitalize())
        return fig

