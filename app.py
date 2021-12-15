# Standard Imports
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime
import numpy as np
import os
import pickle
import dash
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

# Custom Imports
from dataset.dataCleaning import cleanData
from db.connection import get_weatherData, get_weatherData_bySummary, get_weatherData_byCount, get_weatherData_byYear
from graphobjects.plots import createPlot, createTrendPlot

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 10000)
TRAINED_MODEL = "model/weathermodel.pickle"
with open(TRAINED_MODEL, "rb") as readFile:
    model = pickle.load(readFile)

pd.options.plotting.backend = 'plotly'

"""
Define dictionaries for class to label mapping later
"""
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
    'expomavg': 'Exponentially-Weighted Moving Average',
}

"""
Define general properties for the DASH app
"""
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Weather Dashboard"
app_color = {"graph_bg": "#252729", "graph_line": "#008019", "trace": "#379C4B", "trend": "#EB4034"}
server = app.server

"""
HTML layout for the DASH app
"""
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
                                    {'label': 'Exponentially-Weighted Moving Average', 'value': 'expomavg'},
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
        html.Div(
            [
            html.Div(
                    [
                        html.P(
                            "Precipitation Prediction",
                            className="graph__title",
                        ),
                        html.P("Temperature (C)", className="graph__title"),
                        dcc.Slider(
                            id="temperature-slider",
                                min=-60,
                                max=60,
                                step=5,
                                value=0,
                                updatemode="drag",
                                marks={
                                    -60: {"label": "-60"},
                                    -30: {"label": "-30"},
                                    0: {"label": "0"},
                                    30: {"label": "30"},
                                    60: {"label": "60"},
                                },
                        ),
                        html.P("Apparent Temperature (C)", className="graph__title"),
                        dcc.Slider(
                            id="app-temperature-slider",
                                min=-60,
                                max=60,
                                step=5,
                                value=0,
                                updatemode="drag",
                                marks={
                                    -60: {"label": "-60"},
                                    -30: {"label": "-30"},
                                    0: {"label": "0"},
                                    30: {"label": "30"},
                                    60: {"label": "60"},
                                },
                        ),
                        html.P("Humidity (%)", className="graph__title"),
                        dcc.Slider(
                            id="humidity-slider",
                                min=0,
                                max=1,
                                step=0.05,
                                value=0.5,
                                updatemode="drag",
                                marks={
                                    0: {"label": "0%"},
                                    0.2: {"label": "20%"},
                                    0.4: {"label": "40%"},
                                    0.6: {"label": "60%"},
                                    0.8: {"label": "80%"},
                                    1: {"label": "100%"},
                                },
                        ),
                        html.P("Wind Speed (km/h)", className="graph__title"),
                        dcc.Slider(
                            id="windspeed-slider",
                                min=0,
                                max=25,
                                step=1,
                                value=5,
                                updatemode="drag",
                                marks={
                                    0: {"label": "0"},
                                    5: {"label": "5"},
                                    10: {"label": "10"},
                                    15: {"label": "15"},
                                    20: {"label": "20"},
                                    25: {"label": "25"},
                                },
                        ),
                    ],
                    className="three columns",
                ),
                html.Div(
                    [
                        html.P(
                            "Parameters (contd.)",
                            className="graph__title",
                        ),
                        html.P("Wind Bearing", className="graph__title"),
                        dcc.Slider(
                            id="windbearing-slider",
                                min=0,
                                max=360,
                                step=30,
                                value=180,
                                updatemode="drag",
                                marks={
                                    0: {"label": "0"},
                                    60: {"label": "60"},
                                    120: {"label": "120"},
                                    180: {"label": "180"},
                                    240: {"label": "240"},
                                    300: {"label": "300"},
                                    360: {"label": "360"},
                                },
                        ),
                        html.P("Visibility (km)", className="graph__title"),
                        dcc.Slider(
                            id="visibility-slider",
                                min=0,
                                max=25,
                                step=1,
                                value=5,
                                updatemode="drag",
                                marks={
                                    0: {"label": "0"},
                                    5: {"label": "5"},
                                    10: {"label": "10"},
                                    15: {"label": "15"},
                                    20: {"label": "20"},
                                    25: {"label": "25"},
                                },
                        ),
                        html.P("Pressure (hPa)", className="graph__title"),
                        dcc.Slider(
                            id="pressure-slider",
                                min=950,
                                max=1050,
                                step=5,
                                value=1000,
                                updatemode="drag",
                                marks={
                                    950: {"label": "950"},
                                    975: {"label": "975"},
                                    1000: {"label": "1000"},
                                    1025: {"label": "1025"},
                                    1050: {"label": "1050"},
                                },
                        ),
                        html.P(
                            "",
                            className="graph__title",
                        ),
                        html.Button('Run Forecast', id='submit', n_clicks=0, style={'margin-left':'auto', 'margin-right':'auto', 'width':'100%'}),
                    ],
                    className="three columns",
                ),
                html.Div(
                    [
                        
                        html.Div(
                            [html.H6("Precipitation Forecast", className="graph__title")]
                        ),
                        html.Div(
                            [html.H6(id="predicttext", className="graph__title")]
                        )
                    ],
                    className="five columns prediction__container",
                ),
            ],
            className="predict_content",
        ),
    ],
    className="app__container",
)

@app.callback(
    Output("predicttext", "children"),
    [Input("submit", "n_clicks")],
    [
        State("temperature-slider", "value"),
        State("app-temperature-slider", "value"),
        State("humidity-slider", "value"),
        State("windspeed-slider", "value"), 
        State("windbearing-slider", "value"),
        State("visibility-slider", "value"),
        State("pressure-slider", "value")
    ],
)
def prediction(n_clicks, temp, app_temp, humidity, windspeed, windbearing, visibility, pressure):
    """
    Function to predict precipitation conditions
    Input: n_clicks, temp, app_temp, humidity, windspeed, windbearing, visibility, pressure
    Output: html.Div child text
    """
    if(n_clicks == 0):
        return "Click the button to run forecasting model"
    else:
        inputdata = [temp, app_temp, humidity, windspeed, windbearing, visibility, pressure]
        columnname = ['Temperature (C)', 'Apparent Temperature (C)', 'Humidity', 'Wind Speed (km/h)', 'Wind Bearing (degrees)', 'Visibility (km)', 'Pressure (millibars)']

        sampleinput = pd.DataFrame(data=[inputdata])
        sampleinput.columns = columnname
        prediction = model.predict(sampleinput)

        #Class Label corresponding to trained model 0,1,2
        labels = ["No Precipitation", "Rainfall", "Snowfall"]
        return "Based on input data, the prediction is: {}".format(labels[prediction[0]])

@app.callback(
    Output("trenddatatext", "children"), [Input("trend-dropdown", "value")], [Input("x-axis-dropdown3", "value")], [Input("y-axis-dropdown3", "value")],
)
def update_trenddatatext(value, x_axis, y_axis):
    """
    Function to update HTML text for Trend Data Plot
    Input: value, x_axis, y_axis
    Output: html.Div child text
    """
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
    """
    Function to generate Trend Data plots
    Input: interval, trend, x_axis, y_axis, slider_value, auto_state
    Output: Plotly.Express Figure
    """
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
    """
    Function to update HTML text for Yearly Data Plot
    Input: value
    Output: html.Div child text
    """
    return "Data for year {}".format(value)

@app.callback(
    Output("yeardataplot", "figure"), 
    [Input("yeardataplot-update", "n_intervals")], 
    [Input("year-dropdown", "value")], 
    [Input("x-axis-dropdown2", "value")], 
    [Input("y-axis-dropdown2", "value")],
)
def gen_yeardataplot(interval, value, x_axis, y_axis):
    """
    Function to generate Yearly Data plots
    Input: interval, value, x_axis, y_axis
    Output: Plotly.Express Figure
    """
    df = get_weatherData_byYear(value)
    df = cleanData(df)

    return createPlot(df,x_axis,y_axis)

@app.callback(
    Output("userdeftext", "children"), [Input("x-axis-dropdown", "value")], [Input("y-axis-dropdown", "value")],
)
def update_userdeftext(x_axis, y_axis):
    """
    Function to update HTML text for User Defined Data Plot
    Input: x_axis, y_axis
    Output: html.Div child text
    """
    return "{} VS {}".format(labeldict["{}".format(y_axis)],labeldict["{}".format(x_axis)])

@app.callback(
    Output("userdefplot", "figure"), [Input("userdefplot-update", "n_intervals")], [Input("x-axis-dropdown", "value")], [Input("y-axis-dropdown", "value")],
    [
        State("data-slider", "value"),
        State("show-all", "value"),
    ],
)
def gen_userdefplot(interval, x_axis, y_axis, slider_value, auto_state):
    """
    Function to generate User Defined Data plots
    Input: interval, x_axis, y_axis, slider_value, auto_state
    Output: Plotly.Express Figure
    """
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
    """
    Function to generate Temperature vs Reading Time Data plots
    Input: interval, slider_value, auto_state
    Output: Plotly.Express Figure
    """
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
    """
    Function to generate Apparent Temperature vs Humidity Data plots
    Input: interval, slider_value, auto_state
    Output: Plotly.Express Figure
    """
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
    """
    Function to generate Temperature vs Humidity Data plots
    Input: interval, slider_value, auto_state
    Output: Plotly.Express Figure
    """
    if "Show All" in auto_state:
        df = get_weatherData()
    else:
        df = get_weatherData_byCount(slider_value)

    df = cleanData(df)

    return createPlot(df,"humidity","temperature")

if __name__ == "__main__":
    app.run_server(debug=True)

