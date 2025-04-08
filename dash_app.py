from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
from datetime import datetime
import json
import os

def load_wifi_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'data', r'wifi_data.json')
        with open(json_path, 'r') as file:
            data = json.load(file)

        records = []
        for location, measurements in data.items():
            for measurement in measurements:
                try:
                    timestamp = datetime.strptime(measurement['timestamp'], '%Y-%m-%d %H:%M:%S')
                    record = {
                        'timestamp': timestamp,
                        'date': timestamp.strftime('%Y-%m-%d'),
                        'hour': timestamp.strftime('%H:00'),
                        'location': measurement['location']['position[name]'],
                        'download_speed': measurement['download_speed'],
                        'upload_speed': measurement['upload_speed'],
                        'latency_ms': measurement['latency_ms'],
                        'jitter_ms': measurement['jitter_ms'],
                        'packet_loss': measurement['packet_loss'],
                        'rssi': measurement['rssi']
                    }
                    records.append(record)
                except Exception as e:
                    print(f"⚠️ Skipping bad record: {e}")
                    continue

        df = pd.DataFrame(records)
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return pd.DataFrame()

def create_dash_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dashboard/')

    colors = {
        'background': '#FFFFFF',
        'navbar': '#1976D2',
        'sidebar': '#F8F9FA',
        'text': '#2C3E50',
        'primary': '#1976D2',
        'secondary': '#90CAF9'
    }

    # Load initial data to get filter options
    initial_df = load_wifi_data()
    locations = sorted(initial_df['location'].unique()) if not initial_df.empty else []
    dates = sorted(initial_df['date'].unique()) if not initial_df.empty else []
    hours = sorted(initial_df['hour'].unique()) if not initial_df.empty else []

    # Add "All" options
    dates = ['All Dates'] + dates
    hours = ['All Hours'] + hours

    dash_app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>WiFi Performance Analysis</title>
            {%favicon%}
            {%css%}
            <style>
                body {
                    margin: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                }
                .nav-link {
                    color: white !important;
                    padding: 10px 15px;
                    text-decoration: none;
                    transition: background-color 0.3s;
                }
                .nav-link:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                .graph-container {
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    background: white;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 20px;
                }
                .dash-radio-items label {
                    color: #1976D2 !important;
                    text-align: left !important;
                }
                .filter-container {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 20px;
                    padding: 15px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .filter-item {
                    flex: 1;
                }
                .filter-label {
                    font-weight: 500;
                    margin-bottom: 5px;
                    color: #2C3E50;
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''

    dash_app.layout = html.Div([
        # Fixed navbar
        html.Nav([
            html.Div([
                html.H4("WiFi Performance Analysis", style={'color': 'white', 'margin': 0}),
                html.Div([
                    html.A("Graphs", href="#", className="nav-link", id="graphs-link"),
                    html.A("Heatmap", href="#", className="nav-link", id="heatmap-link"),
                ])
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'padding': '0 20px',
                'maxWidth': '1400px',
                'margin': '0 auto',
                'width': '100%'
            })
        ], style={
            'backgroundColor': colors['navbar'],
            'padding': '10px 0',
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'right': 0,
            'zIndex': 1000,
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }),

        # Main content with top margin to account for fixed navbar
        html.Div([
            # Sidebar
            html.Div([
                html.H3("Parameters", style={
                    'color': colors['text'],
                    'textAlign': 'center',
                    'marginBottom': '20px'
                }),
                dcc.RadioItems(
                    id='parameter-selector',
                    options=[
                        {'label': 'Upload Speed', 'value': 'upload_speed'},
                        {'label': 'Download Speed', 'value': 'download_speed'},
                        {'label': 'Latency', 'value': 'latency_ms'},
                        {'label': 'Jitter', 'value': 'jitter_ms'},
                        {'label': 'Packet Loss', 'value': 'packet_loss'},
                        {'label': 'RSSI', 'value': 'rssi'}
                    ],
                    value='download_speed',
                    className='dash-radio-items',
                    style={
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '10px'
                    }
                )
            ], style={
                'width': '15%',
                'backgroundColor': colors['sidebar'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'height': 'calc(100vh - 100px)',
                'position': 'fixed',
                'top': '80px'
            }),

            # Main content area
            html.Div([
                # Filters
                html.Div([
                    html.Div([
                        html.Div("Location", className='filter-label'),
                        dcc.Dropdown(
                            id='location-filter',
                            options=[{'label': loc, 'value': loc} for loc in locations],
                            value=locations[0] if locations else None,
                            clearable=False,
                            className='filter-dropdown'
                        )
                    ], className='filter-item'),
                    
                    html.Div([
                        html.Div("Date", className='filter-label'),
                        dcc.Dropdown(
                            id='date-filter',
                            options=[{'label': date, 'value': date} for date in dates],
                            value='All Dates',
                            clearable=False,
                            className='filter-dropdown'
                        )
                    ], className='filter-item'),

                    html.Div([
                        html.Div("Time", className='filter-label'),
                        dcc.Dropdown(
                            id='time-filter',
                            options=[{'label': hour, 'value': hour} for hour in hours],
                            value='All Hours',
                            clearable=False,
                            className='filter-dropdown'
                        )
                    ], className='filter-item')
                ], className='filter-container'),

                # Graph
                html.Div([
                    dcc.Graph(id='time-series-graph', className='graph-container'),
                ])
            ], style={
                'width': '80%',
                'marginLeft': '17%',
                'padding': '20px',
                'marginTop': '60px'
            })
        ], style={
            'display': 'flex',
            'backgroundColor': colors['background'],
            'minHeight': '100vh',
            'paddingTop': '20px'
        })
    ])

    @callback(
        Output('time-series-graph', 'figure'),
        [Input('parameter-selector', 'value'),
         Input('location-filter', 'value'),
         Input('date-filter', 'value'),
         Input('time-filter', 'value')]
    )
    def update_graph(selected_parameter, selected_location, selected_date, selected_time):
        df = load_wifi_data()

        if df.empty:
            return create_empty_figure("No data available")

        # Filter data based on selections
        filtered_df = df.copy()
        
        # Apply location filter
        if selected_location:
            filtered_df = filtered_df[filtered_df['location'] == selected_location]
            
        # Apply date filter
        if selected_date != 'All Dates':
            # Convert both to datetime for proper comparison
            filtered_df['date_dt'] = pd.to_datetime(filtered_df['date'])
            selected_date_dt = pd.to_datetime(selected_date)
            filtered_df = filtered_df[filtered_df['date_dt'].dt.date == selected_date_dt.date()]
            filtered_df = filtered_df.drop('date_dt', axis=1)
            
        # Apply time filter
        if selected_time != 'All Hours':
            filtered_df = filtered_df[filtered_df['hour'] == selected_time]

        # Create time series plot
        time_series = px.line(
            filtered_df,
            x='timestamp',
            y=selected_parameter,
            color='location',
            title=f'{selected_parameter.replace("_", " ").title()} Over Time'
        )

        time_series.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': colors['text']},
            hovermode='x unified',
            xaxis={'gridcolor': '#EAEAEA'},
            yaxis={'gridcolor': '#EAEAEA'}
        )

        # Update hover template
        time_series.update_traces(
            hovertemplate="<br>".join([
                "Location: %{customdata[0]}",
                "Time: %{x}",
                f"{selected_parameter.replace('_', ' ').title()}: %{{y:.2f}}",
                "<extra></extra>"
            ]),
            customdata=filtered_df[['location']]
        )

        return time_series

    def create_empty_figure(title):
        return {
            'data': [],
            'layout': {
                'title': title,
                'paper_bgcolor': 'white',
                'font': {'color': colors['text']},
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': title,
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 20, 'color': colors['text']}
                }]
            }
        }

    return dash_app