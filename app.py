# Standard imports
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime
import numpy as np
from dataset.dataCleaning import cleanData
from db.connection import get_weatherData, get_weatherData_bySummary, get_weatherData_byCount
import os

import dash
from dash import dcc
from dash import html

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 10000)

pd.options.plotting.backend = 'plotly'

labeldict={
    'reading_time': 'Reading Time',
    'temperature': 'Temperature (C)',
    'apparent_temperature': 'Apparent Temperature (C)',
    'humidity': 'Humidity',
    'wind_speed': 'Wind Speed (km/h)',
    'wind_bearing': 'Wind Bearing',
    'visibility': 'Visibility (km)',
    'pressure': 'Pressure (hPA)',
}

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Weather Dashboard"
app_color = {"graph_bg": "#252729", "graph_line": "#008019", "trace": "#379C4B"}

server = app.server

app.layout = html.Div(
    [
        # header
        html.Div(
            [
                html.Div(
                    [
                        html.H2("WEATHER DASHBOARD", className="app__header__title"),
                        html.P(
                            "This app queries a MySQL database and displays real-time charts of meteorological data.",
                            className="app__header__title--grey",
                        ),
                    ],
                    className="app__header__desc",
                ),
            ],
            className="app__header",
        ),
        html.Div(
            [
            html.Div(
                    [
                        html.P(
                            "Number of Data Points (Newest First)",
                            className="app__header__title--grey",
                        ),
                        dcc.Slider(
                            id="data-slider",
                                min=100,
                                max=50000,
                                step=300,
                                value=5000,
                                updatemode="drag",
                                marks={
                                    100: {"label": "100"},
                                    10000: {"label": "10K"},
                                    20000: {"label": "20K"},
                                    30000: {"label": "30K"},
                                    40000: {"label": "40K"},
                                    50000: {"label": "50K"},
                                },
                        ),
                        dcc.Checklist(
                            id="show-all",
                                options=[
                                    {"label": "Show All Data", "value": "Show All"}
                                ],
                            value=[],
                            inputClassName="auto__checkbox",
                            labelClassName="auto__label",
                        ),
                    ],
                    className="slider",
                ),
            ],
            className="data_slider_content",
        ),
        html.Div(
            [
                # Temperature
                html.Div(
                    [
                        html.Div(
                            [html.H6("Temperature (C) vs Reading Time", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="temperature",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="temperature-update",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ),
                    ],
                    className="twelve column temperature__container",
                ),
            ],
            className="app__content",
        ),
        html.Div(
            [
                # Apparent Temperature vs Humidity
                html.Div(
                    [
                        html.Div(
                            [html.H6("Apparent Temperature (C) vs Humidity", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="apptempVsHumidity",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="apptempVsHumidity-update",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ),
                    ],
                    className="one-half column apptempVsHumidity__container",
                ),
                # Temperature vs Humidity
                html.Div(
                    [
                        html.Div(
                            [html.H6("Temperature (C) vs Humidity", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="tempVsHumidity",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="tempVsHumidity-update",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ),
                    ],
                    className="one-half column tempVsHumidity__container",
                ),
            ],
            className="app__content2",
        ),
        html.Div(
            [
            html.Div(
                    [
                        html.P(
                            "User Defined Plot",
                            className="graph__title",
                        ),
                        html.P("X-Axis", className="graph__title"),
                        dcc.Dropdown(
                            id="x-axis-dropdown",
                                options=[
                                    {'label': 'Reading Time', 'value': 'reading_time'},
                                    {'label': 'Temperature (C)', 'value': 'temperature'},
                                    {'label': 'Apparent Temperature (C)', 'value': 'apparent_temperature'},
                                    {'label': 'Humidity', 'value': 'humidity'},
                                    {'label': 'Wind Speed (km/h)', 'value': 'wind_speed'},
                                    {'label': 'Wind Bearing', 'value': 'wind_bearing'},
                                    {'label': 'Visibility (km)', 'value': 'visibility'},
                                    {'label': 'Pressure (hPA)', 'value': 'pressure'},
                                ],
                                value='reading_time'
                        ),
                        html.P("Y-Axis", className="graph__title"),
                        dcc.Dropdown(
                            id="y-axis-dropdown",
                                options=[
                                    {'label': 'Reading Time', 'value': 'reading_time'},
                                    {'label': 'Temperature (C)', 'value': 'temperature'},
                                    {'label': 'Apparent Temperature (C)', 'value': 'apparent_temperature'},
                                    {'label': 'Humidity', 'value': 'humidity'},
                                    {'label': 'Wind Speed (km/h)', 'value': 'wind_speed'},
                                    {'label': 'Wind Bearing', 'value': 'wind_bearing'},
                                    {'label': 'Visibility (km)', 'value': 'visibility'},
                                    {'label': 'Pressure (hPA)', 'value': 'pressure'},
                                ],
                                value='temperature'
                        ),
                    ],
                    className="three columns",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.H6(id="userdeftext", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="userdefplot",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="userdefplot-update",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ),
                    ],
                    className="nine columns userdefplot__container",
                ),
            ],
            className="parameter_selector_content",
        ),
    ],
    className="app__container",
)

@app.callback(
    Output("userdeftext", "children"), [Input("x-axis-dropdown", "value")], [Input("y-axis-dropdown", "value")],
)
def update_userdeftext(x_axis, y_axis):
    return "{} VS {}".format(labeldict["{}".format(y_axis)],labeldict["{}".format(x_axis)])

@app.callback(
    Output("userdefplot", "figure"), [Input("userdefplot-update", "n_intervals")], [Input("x-axis-dropdown", "value")], [Input("y-axis-dropdown", "value")],
    [
        State("data-slider", "value"),
        State("show-all", "value"),
    ],
)
def gen_userdefplot(interval, x_axis, y_axis, slider_value, auto_state):
    
    if "Show All" in auto_state:
        df = get_weatherData()
    else:
        df = get_weatherData_byCount(slider_value)
    
    df = cleanData(df)

    trace = dict(
        type="scatter",
        y=df["{}".format(y_axis)],
        x=df["{}".format(x_axis)],
        line={"color": app_color["trace"]},
        mode="markers",
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=400,
        xaxis={
            "title": labeldict["{}".format(x_axis)],
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
        },
        yaxis={
            "title": labeldict["{}".format(y_axis)],
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
        },
    )

    return dict(data=[trace], layout=layout)

@app.callback(
    Output("temperature", "figure"), [Input("temperature-update", "n_intervals")],
    [
        State("data-slider", "value"),
        State("show-all", "value"),
    ]
)
def gen_temperature(interval, slider_value, auto_state):
    
    if "Show All" in auto_state:
        df = get_weatherData()
    else:
        df = get_weatherData_byCount(slider_value)
    
    df = cleanData(df)

    trace = dict(
        type="scatter",
        y=df["temperature"],
        x=df["reading_time"],
        line={"color": app_color["trace"]},
        mode="markers",
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=400,
        xaxis={
            "title": "Reading Time",
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
        },
        yaxis={
            "title": "Temperature",
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
        },
    )

    return dict(data=[trace], layout=layout)

@app.callback(
    Output("apptempVsHumidity", "figure"), [Input("apptempVsHumidity-update", "n_intervals")],
    [
        State("data-slider", "value"),
        State("show-all", "value"),
    ]
)
def gen_apptempVsHumidity(interval, slider_value, auto_state):

    if "Show All" in auto_state:
        df = get_weatherData()
    else:
        df = get_weatherData_byCount(slider_value)

    df = cleanData(df)

    trace = dict(
        type="scatter",
        y=df["apparent_temperature"],
        x=df["humidity"],
        line={"color": app_color["trace"]},
        mode="markers",
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=400,
        xaxis={
            "title": "Humidity",
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
        },
        yaxis={
            "title": "Apparent Temperature",
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
        },
    )

    return dict(data=[trace], layout=layout)

@app.callback(
    Output("tempVsHumidity", "figure"), [Input("tempVsHumidity-update", "n_intervals")],
    [
        State("data-slider", "value"),
        State("show-all", "value"),
    ]
)
def gen_tempVsHumidity(interval, slider_value, auto_state):

    if "Show All" in auto_state:
        df = get_weatherData()
    else:
        df = get_weatherData_byCount(slider_value)

    df = cleanData(df)

    trace = dict(
        type="scatter",
        y=df["temperature"],
        x=df["humidity"],
        line={"color": app_color["trace"]},
        mode="markers",
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=400,
        xaxis={
            "title": "Humidity",
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
        },
        yaxis={
            "title": "Temperature",
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
        },
    )

    return dict(data=[trace], layout=layout)

if __name__ == "__main__":
    app.run_server(debug=False)

