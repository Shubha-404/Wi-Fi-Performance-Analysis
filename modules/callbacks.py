from dash import Input, Output, html, dcc
from modules.data_loader import load_wifi_data,prepare_heatmap_data
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from modules.utils import get_pixel_coords
import dash_bootstrap_components as dbc
from datetime import datetime


def register_callbacks(dash_app, colors):

    @dash_app.callback(
        Output('tab-content', 'children'),
        Input('main-tabs', 'value')
    )
    def render_tab_content(tab):
        if tab == 'overview':
            df = load_wifi_data()
            if df.empty:
                return html.Div("❌ No data available for overview")

            # Get latest run for each location
            latest_data = df.sort_values('timestamp').groupby('location').last().reset_index()
            
            # Define parameters to show
            parameters = {
                'download_speed': {'icon': '📥', 'unit': 'Mbps', 'name': 'Download Speed'},
                'upload_speed': {'icon': '📤', 'unit': 'Mbps', 'name': 'Upload Speed'},
                'latency_ms': {'icon': '⏱️', 'unit': 'ms', 'name': 'Latency'},
                'jitter_ms': {'icon': '📊', 'unit': 'ms', 'name': 'Jitter'},
                'packet_loss': {'icon': '📉', 'unit': '%', 'name': 'Packet Loss'},
                'rssi': {'icon': '📶', 'unit': 'dBm', 'name': 'RSSI'}
            }

            # Get unique locations for dropdown
            locations = latest_data['location'].unique()
            location_options = [{'label': loc, 'value': loc} for loc in locations]

            # Get unique dates and run numbers
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            dates = sorted(df['date'].unique())
            date_options = [{'label': str(date), 'value': str(date)} for date in dates]
            
            # Get run numbers for the first date
            first_date_data = df[df['date'] == dates[0]]
            first_date_runs = sorted(first_date_data['run_no'].unique())
            run_options = [{'label': f"Run {run}", 'value': str(run)} for run in first_date_runs]

            return html.Div([
                html.H3("📊 Latest Parameters", style={'marginBottom': '20px', 'color': 'white'}),
                html.Div([
                    html.Label("Select Location:", style={'color': 'white', 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='location-selector',
                        options=location_options,
                        value=locations[0] if len(locations) > 0 else None,
                        clearable=False,
                        style={'width': '200px', 'display': 'inline-block', 'marginRight': '20px'}
                    )
                ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),
                html.Div(id='parameter-cards', style={'marginTop': '30px'}),
                html.Hr(style={'borderColor': 'white', 'margin': '30px 0'}),
                html.H3("Run Analysis", style={'marginTop': '40px', 'marginBottom': '20px', 'color': 'white'}),
                html.Div([
                    html.Div([
                        html.Label("Select Date:", style={'color': 'white', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='date-selector',
                            options=date_options,
                            value=str(dates[0]) if len(dates) > 0 else None,
                            clearable=False,
                            style={'width': '200px', 'display': 'inline-block', 'marginRight': '20px'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),
                    html.Div([
                        html.Label("Select Run:", style={'color': 'white', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='run-selector',
                            options=run_options,
                            value=str(first_date_runs[0]) if len(first_date_runs) > 0 else None,
                            clearable=False,
                            style={'width': '200px', 'display': 'inline-block', 'marginRight': '20px'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'})
                ]),
                html.Div(id='location-plots')
            ], style={'padding': '20px'})

        elif tab == 'trends':
            df = load_wifi_data()
            if df.empty:
                return html.Div("❌ No data available for trends view")

            locations = sorted(df['location'].unique())
            parameters = ['download_speed', 'upload_speed', 'latency_ms', 'jitter_ms', 'packet_loss', 'rssi']
            parameter_labels = {
                'download_speed': 'Download Speed (Mbps)',
                'upload_speed': 'Upload Speed (Mbps)',
                'latency_ms': 'Latency (ms)',
                'jitter_ms': 'Jitter (ms)',
                'packet_loss': 'Packet Loss (%)',
                'rssi': 'RSSI (dBm)'
            }
            hours = ['All Hours'] + sorted(df['hour'].unique())

            return html.Div([
            html.Div([
                html.Div([
                    html.Div("Location", className='filter-label'),
                    dcc.Dropdown(
                        id='trends-location',
                        options=[{'label': loc, 'value': loc} for loc in locations],
                        value=locations[0],
                        clearable=False
                    )
                ], className='filter-item'),

                html.Div([
                    html.Div("Parameter", className='filter-label'),
                    dcc.Dropdown(
                        id='trends-parameter',
                        options=[{'label': parameter_labels[p], 'value': p} for p in parameters],
                        value='download_speed',
                        clearable=False
                    )
                ], className='filter-item'),

                html.Div([
                    html.Div("Time of Day", className='filter-label'),
                    dcc.Dropdown(
                        id='trends-hour',
                        options=[{'label': hour, 'value': hour} for hour in hours],
                        value='All Hours',
                        clearable=False
                    )
                ], className='filter-item'),
            ], style={
                'display': 'flex',
                'gap': '20px',
                'marginBottom': '20px',
                'flexWrap': 'wrap'
            }),

            dcc.Graph(id='trends-time-series', className='graph-container'),
            html.Div(id='hourly-bar-wrapper')  # We'll dynamically show/hide this
        ])

        elif tab == 'heatmap':
            df = load_wifi_data()
            parameters = ['download_speed', 'upload_speed', 'latency_ms', 'jitter_ms', 'packet_loss', 'rssi']
            return html.Div([
                html.Div([
                    html.Div("Select Parameter", className='filter-label'),
                    dcc.Dropdown(
                        id='heatmap-param',
                        options=[{'label': p.replace("_", " ").title(), 'value': p} for p in parameters],
                        value='rssi',
                        clearable=False
                    ),
                ], style={'maxWidth': '300px', 'marginBottom': '20px'}),

                dcc.Graph(id='heatmap-graph', className='graph-container')
            ])
        elif tab == 'insights':
            return html.Div([
                html.H3("🧠 AI-based insights will go here.")
            ])
        return html.Div("🚧 This section is under construction.")
    
    
    @dash_app.callback(
    Output('trends-time-series', 'figure'),
    Input('trends-location', 'value'),
    Input('trends-parameter', 'value'),
    Input('trends-hour', 'value')

)
    def update_trend_timeseries(location, parameter, selected_hour):
        df = load_wifi_data()
        if df.empty or not location:
            return {}

        filtered = df[df['location'] == location]

        if selected_hour != 'All Hours':
            filtered = filtered[filtered['hour'] == selected_hour]

        fig = px.line(
            filtered,
            x='timestamp',
            y=parameter,
            title=f"{parameter.replace('_', ' ').title()} Over Time - {location}",
            markers=True,
            hover_data={
                'timestamp': True,
                'location': False,
                'download_speed': ':.2f',
                'upload_speed': ':.2f',
                'rssi': ':.0f',
                'latency_ms': ':.1f',
                'jitter_ms': ':.1f',
                'packet_loss': ':.2f',
                parameter: True
            }
        )

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': colors['text']},
            margin=dict(l=60, r=20, t=50, b=50),
            height=400
        )
        return fig



    @dash_app.callback(
    Output('hourly-bar-wrapper', 'children'),
    Input('trends-location', 'value'),
    Input('trends-parameter', 'value'),
    Input('trends-hour', 'value')
    )
    def update_hourly_avg(location, parameter, selected_hour):
        df = load_wifi_data()
        if df.empty or not location or selected_hour != 'All Hours':
            return None  # hides the entire container

        filtered = df[df['location'] == location]
        hourly_avg = filtered.groupby('hour')[parameter].mean().reset_index()

        fig = px.bar(
            hourly_avg,
            x='hour',
            y=parameter,
            title=f"Hourly Average of {parameter.replace('_', ' ').title()} - {location}",
            color=parameter,
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=colors['text'], size=14),
            margin=dict(l=60, r=20, t=50, b=50),
            height=400
        )

        return dcc.Graph(figure=fig, className='graph-container')

    # Track whether collection is active

        
        
    @dash_app.callback(
        Output('data-toggle-btn', 'children'),
        Output('collection-state', 'data'),
        Input('data-toggle-btn', 'n_clicks'),
        State('collection-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_button(n_clicks, state_data):
        if not state_data or 'active' not in state_data:
            state_data = {'active': False}

        # Toggle the state
        new_state = not state_data['active']
        new_label = "Stop" if new_state else "Start"

        return new_label, {'active': new_state}
    
    @dash_app.callback(
    Output('heatmap-graph', 'figure'),
    Input('heatmap-param', 'value')
    )
    def update_heatmap(param):
        df = load_wifi_data()
        if df.empty:
            return go.Figure()

        # Group by location to get averages + count
        agg_df = df.groupby('location').agg({
            'download_speed': 'mean',
            'upload_speed': 'mean',
            'latency_ms': 'mean',
            'jitter_ms': 'mean',
            'packet_loss': 'mean',
            'rssi': 'mean',
            'timestamp': 'count'
        }).reset_index().rename(columns={'timestamp': 'count'})

        # Add pixel coordinates
        agg_df['x'], agg_df['y'] = zip(*agg_df['location'].map(get_pixel_coords))
        agg_df = agg_df.dropna(subset=[param, 'x', 'y'])

        # Remove (0, 0) default fallbacks (i.e., unmapped locations)
        agg_df = agg_df[(agg_df['x'] != 0) | (agg_df['y'] != 0)]

        # Normalize marker size
        max_count = agg_df['count'].max()
        agg_df['size'] = agg_df['count'] / max_count * 40 + 10  # Scale 10–50 px

        fig = go.Figure(data=go.Scatter(
            x=agg_df['x'],
            y=agg_df['y'],
            mode='markers',
            marker=dict(
                size=agg_df['size'],
                color=agg_df[param],
                colorscale='Viridis',
                colorbar=dict(title=param.replace('_', ' ').title()),
                showscale=True,
                line=dict(width=1, color='black')
            ),
            customdata=agg_df[['location', 'download_speed', 'upload_speed', 'latency_ms', 'jitter_ms', 'packet_loss', 'rssi', 'count']],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" +
                "Download: %{customdata[1]:.2f} Mbps<br>" +
                "Upload: %{customdata[2]:.2f} Mbps<br>" +
                "Latency: %{customdata[3]:.2f} ms<br>" +
                "Jitter: %{customdata[4]:.2f} ms<br>" +
                "Packet Loss: %{customdata[5]:.2f}<br>" +
                "RSSI: %{customdata[6]}<br>" +
                "Data Points: %{customdata[7]}<extra></extra>"
            )
        ))

        fig.update_layout(
            title=f"📍 Average {param.replace('_', ' ').title()} Across Locations",
            xaxis=dict(title="X", showgrid=False, zeroline=False),
            yaxis=dict(title="Y", showgrid=False, zeroline=False),
            plot_bgcolor='white',
            height=600
        )

        return fig

    @dash_app.callback(
        Output('run-analysis-graph', 'figure'),
        Input('run-selector', 'value')
    )
    def update_run_analysis(selected_run):
        df = load_wifi_data()
        if df.empty or not selected_run:
            return go.Figure()

        # Filter data for selected run
        run_data = df[df['timestamp'] == selected_run]
        
        # Create stacked bar chart
        fig = go.Figure()
        
        parameters = ['download_speed', 'upload_speed', 'latency_ms', 'jitter_ms', 'packet_loss', 'rssi']
        parameter_labels = {
            'download_speed': 'Download Speed (Mbps)',
            'upload_speed': 'Upload Speed (Mbps)',
            'latency_ms': 'Latency (ms)',
            'jitter_ms': 'Jitter (ms)',
            'packet_loss': 'Packet Loss (%)',
            'rssi': 'RSSI (dBm)'
        }

        for param in parameters:
            fig.add_trace(go.Bar(
                name=parameter_labels[param],
                x=run_data['location'],
                y=run_data[param],
                text=run_data[param].round(2),
                textposition='auto'
            ))

        fig.update_layout(
            barmode='stack',
            title=f"Parameters for Run: {selected_run}",
            xaxis_title="Location",
            yaxis_title="Value",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=colors['text']),
            margin=dict(l=60, r=20, t=50, b=50),
            height=500
        )

        return fig

    @dash_app.callback(
        Output('parameter-cards', 'children'),
        Input('location-selector', 'value')
    )
    def update_parameter_cards(selected_location):
        df = load_wifi_data()
        if df.empty or not selected_location:
            return html.Div()

        # Get latest data for selected location
        latest_data = df[df['location'] == selected_location].sort_values('timestamp').iloc[-1]
        
        parameters = {
            'download_speed': {'icon': '📥', 'unit': 'Mbps', 'name': 'Download Speed'},
            'upload_speed': {'icon': '📤', 'unit': 'Mbps', 'name': 'Upload Speed'},
            'latency_ms': {'icon': '⏱️', 'unit': 'ms', 'name': 'Latency'},
            'jitter_ms': {'icon': '📊', 'unit': 'ms', 'name': 'Jitter'},
            'packet_loss': {'icon': '📉', 'unit': '%', 'name': 'Packet Loss'},
            'rssi': {'icon': '📶', 'unit': 'dBm', 'name': 'RSSI'}
        }

        cards = []
        for param, info in parameters.items():
            cards.append(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(info['icon'], style={
                            'fontSize': '3rem', 
                            'textAlign': 'center',
                            'display': 'flex',
                            'justifyContent': 'center',
                            'alignItems': 'center',
                            'height': '80px',
                            'transition': 'transform 0.3s ease'
                        }),
                        html.H5(info['name'], style={
                            'textAlign': 'center', 
                            'color': 'white',
                            'display': 'flex',
                            'justifyContent': 'center',
                            'alignItems': 'center',
                            'marginTop': '10px',
                            'fontWeight': 'bold'
                        }),
                        html.H4(f"{latest_data[param]:.2f} {info['unit']}", 
                               style={
                                   'textAlign': 'center', 
                                   'marginTop': '5px', 
                                   'color': 'white',
                                   'display': 'flex',
                                   'justifyContent': 'center',
                                   'alignItems': 'center'
                               })
                    ], style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'height': '100%'}),
                    style={
                        'height': '200px',
                        'margin': '10px',
                        'backgroundColor': '#1f2c3e',
                        'color': 'white',
                        'borderRadius': '15px',
                        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.3)',
                        'flex': '1',
                        'minWidth': '0',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'transition': 'all 0.3s ease',
                        'cursor': 'pointer',
                        ':hover': {
                            'transform': 'translateY(-5px)',
                            'boxShadow': '0 8px 16px rgba(0, 0, 0, 0.4)'
                        }
                    },
                    className='hover-card'
                )
            )

        return html.Div(
            cards,
            style={
                'display': 'flex',
                'flexDirection': 'row',
                'justifyContent': 'space-between',
                'gap': '10px',
                'flexWrap': 'nowrap',
                'overflowX': 'auto'
            }
        )

    @dash_app.callback(
        Output('location-plots', 'children'),
        Input('date-selector', 'value'),
        Input('run-selector', 'value')
    )
    def update_location_plots(selected_date, selected_run):
        df = load_wifi_data()
        if df.empty or not selected_date or not selected_run:
            return html.Div()

        # Filter data for selected date and run
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        run_data = df[(df['date'] == pd.to_datetime(selected_date).date()) & 
                     (df['run_no'] == int(selected_run))]
        
        locations = run_data['location'].unique()
        if len(locations) == 0:
            return html.Div("No data available for selected date and run")
        
        plots = []
        for location in locations:
            loc_data = run_data[run_data['location'] == location]
            
            # Get the time for this location's data
            time_str = loc_data['timestamp'].iloc[0].strftime('%H:%M:%S')
            
            # Create separate figures for each parameter to handle different scales
            parameters = {
                'download_speed': {'title': 'Download Speed (Mbps)', 'color': '#1f77b4'},
                'upload_speed': {'title': 'Upload Speed (Mbps)', 'color': '#ff7f0e'},
                'latency_ms': {'title': 'Latency (ms)', 'color': '#2ca02c'},
                'jitter_ms': {'title': 'Jitter (ms)', 'color': '#d62728'},
                'packet_loss': {'title': 'Packet Loss (%)', 'color': '#9467bd'},
                'rssi': {'title': 'RSSI (dBm)', 'color': '#8c564b'}
            }

            fig = go.Figure()
            for param, info in parameters.items():
                fig.add_trace(go.Bar(
                    name=info['title'],
                    x=[param],
                    y=[loc_data[param].iloc[0]],
                    marker_color=info['color'],
                    text=[f"{loc_data[param].iloc[0]:.2f}"],
                    textposition='auto',
                    hovertemplate=f"<b>{info['title']}</b><br>Value: %{{y:.2f}}<br>Time: {time_str}<extra></extra>"
                ))

            fig.update_layout(
                title=dict(
                    text=f"Parameters for {location}<br><sup>Date: {selected_date} | Time: {time_str} | Run: {selected_run}</sup>",
                    x=0.5,
                    xanchor='center',
                    yanchor='top'
                ),
                barmode='group',
                showlegend=True,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color=colors['text']),
                margin=dict(l=60, r=20, t=80, b=50),  # Increased top margin for the title
                height=400,
                xaxis=dict(
                    tickangle=45,
                    tickfont=dict(size=12)
                ),
                hovermode='closest',
                hoverlabel=dict(
                    bgcolor='white',
                    font_size=12,
                    font_family="Rockwell"
                )
            )

            plots.append(
                html.Div([
                    html.H4(location, style={
                        'color': 'white', 
                        'marginBottom': '20px', 
                        'textAlign': 'center',
                        'padding': '10px',
                        'backgroundColor': '#1f2c3e',
                        'borderRadius': '10px',
                        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)'
                    }),
                    dcc.Graph(figure=fig, className='graph-container'),
                    html.Hr(style={'borderColor': 'white', 'margin': '30px 0'})
                ], style={
                    'marginBottom': '40px',
                    'transition': 'all 0.3s ease',
                    ':hover': {
                        'transform': 'scale(1.02)'
                    }
                }, className='plot-container')
            )

        return plots

    @dash_app.callback(
        Output('run-selector', 'options'),
        Input('date-selector', 'value')
    )
    def update_run_options(selected_date):
        df = load_wifi_data()
        if df.empty or not selected_date:
            return []
        
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        runs = sorted(df[df['date'] == pd.to_datetime(selected_date).date()]['run_no'].unique())
        return [{'label': f"Run {run}", 'value': str(run)} for run in runs]

    @dash_app.callback(
        Output('run-selector', 'value'),
        Input('run-selector', 'options')
    )
    def update_run_value(options):
        if not options:
            return None
        return options[0]['value']
