# Standard imports
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime
import numpy as np
from dataset.dataCleaning import cleanData
from db.connection import get_weatherData, get_weatherData_bySummary, get_weatherData_byCount, get_weatherData_byYear
import os

import dash
from dash import dcc
from dash import html

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from graphobjects.plots import createPlot, createTrendPlot

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

trenddict={
    'ols': 'Ordinary Least Squares',
    'olslog': 'Ordinary Least Squares (Log Transformed)',
    '5ptrolling': '5 Point Moving Average',
    'rollmedian': 'Rolling Median',
    'expandmax': 'Expanding Maximum',
}

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Weather Dashboard"
app_color = {"graph_bg": "#252729", "graph_line": "#008019", "trace": "#379C4B", "trend": "#EB4034"}

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
        html.Div(
            [
            html.Div(
                    [
                        html.P(
                            "Yearly Data",
                            className="graph__title",
                        ),
                        html.P("Select Year", className="graph__title"),
                        dcc.Dropdown(
                            id="year-dropdown",
                                options=[
                                    {'label': '2006', 'value': '2006'},
                                    {'label': '2007', 'value': '2007'},
                                    {'label': '2008', 'value': '2008'},
                                    {'label': '2009', 'value': '2009'},
                                    {'label': '2010', 'value': '2010'},
                                    {'label': '2011', 'value': '2011'},
                                    {'label': '2012', 'value': '2012'},
                                    {'label': '2013', 'value': '2013'},
                                    {'label': '2014', 'value': '2014'},
                                    {'label': '2015', 'value': '2015'},
                                    {'label': '2016', 'value': '2016'},
                                ],
                                value='2006'
                        ),
                        html.P("X-Axis", className="graph__title"),
                        dcc.Dropdown(
                            id="x-axis-dropdown2",
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
                            id="y-axis-dropdown2",
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
                            [html.H6(id="yeardatatext", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="yeardataplot",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="yeardataplot-update",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ),
                    ],
                    className="nine columns yeardataplot__container",
                ),
            ],
            className="year_selector_content",
        ),
        html.Div(
            [
            html.Div(
                    [
                        html.P(
                            "Trendlines",
                            className="graph__title",
                        ),
                        html.P("Select Trend", className="graph__title"),
                        dcc.Dropdown(
                            id="trend-dropdown",
                                options=[
                                    {'label': 'Ordinary Least Squares', 'value': 'ols'},
                                    {'label': 'OLS (Log Transformed)', 'value': 'olslog'},
                                    {'label': '5-pt Moving Average', 'value': '5ptrolling'},
                                    {'label': 'Rolling Median', 'value': 'rollmedian'},
                                    {'label': 'Expanding Maximum', 'value': 'expandmax'},
                                ],
                                value='ols'
                        ),
                        html.P("X-Axis", className="graph__title"),
                        dcc.Dropdown(
                            id="x-axis-dropdown3",
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
                            id="y-axis-dropdown3",
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
                            [html.H6(id="trenddatatext", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="trenddataplot",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="trenddataplot-update",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ),
                    ],
                    className="nine columns trenddataplot__container",
                ),
            ],
            className="trend_selector_content",
        ),
    ],
    className="app__container",
)

@app.callback(
    Output("trenddatatext", "children"), [Input("trend-dropdown", "value")], [Input("x-axis-dropdown3", "value")], [Input("y-axis-dropdown3", "value")],
)
def update_yeardatatext(value, x_axis, y_axis):
    return "{} Trend for {} vs {}".format(trenddict["{}".format(value)],labeldict["{}".format(y_axis)],labeldict["{}".format(x_axis)])

@app.callback(
    Output("trenddataplot", "figure"), 
    [Input("trenddataplot-update", "n_intervals")],
    [Input("trend-dropdown", "value")], 
    [Input("x-axis-dropdown3", "value")], 
    [Input("y-axis-dropdown3", "value")],
    [
        State("data-slider", "value"),
        State("show-all", "value"),
    ],
)
def gen_trenddataplot(interval, trend, x_axis, y_axis, slider_value, auto_state):
    
    if "Show All" in auto_state:
        df = get_weatherData()
    else:
        df = get_weatherData_byCount(slider_value)

    df = cleanData(df)

    return createTrendPlot(df,x_axis,y_axis,trend)


@app.callback(
    Output("yeardatatext", "children"), [Input("year-dropdown", "value")],
)
def update_yeardatatext(value):
    return "Data for year {}".format(value)

@app.callback(
    Output("yeardataplot", "figure"), 
    [Input("yeardataplot-update", "n_intervals")], 
    [Input("year-dropdown", "value")], 
    [Input("x-axis-dropdown2", "value")], 
    [Input("y-axis-dropdown2", "value")],
)
def gen_yeardataplot(interval, value, x_axis, y_axis):
    
    df = get_weatherData_byYear(value)
    df = cleanData(df)

    return createPlot(df,x_axis,y_axis)

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

    return createPlot(df,x_axis,y_axis)

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

    return createPlot(df,"reading_time","temperature")

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

    return createPlot(df,"humidity","apparent_temperature")

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

    return createPlot(df,"humidity","temperature")

if __name__ == "__main__":
    app.run_server(debug=False)

