from dash import Input, Output, html, dcc
from modules.data_loader import load_wifi_data,prepare_heatmap_data
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from modules.utils import get_pixel_coords


def register_callbacks(dash_app, colors):

    @dash_app.callback(
        Output('tab-content', 'children'),
        Input('main-tabs', 'value')
    )
    def render_tab_content(tab):
        if tab == 'overview':
            return html.Div([
                html.H3("📊 Overview content will go here.")
            ])
    

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
            html.Div(id='hourly-bar-wrapper')  # We’ll dynamically show/hide this
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
