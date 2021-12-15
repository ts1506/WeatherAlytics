# Standard Imports
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd

app_color = {"graph_bg": "#252729", "graph_line": "#008019", "trace": "#379C4B", "trend": "#EB4034"}

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

def createPlot(data, x_axis, y_axis):
    """
    API to generate plots on demand, apply layout and styling
    Input: data (Pandas DataFrame), x_axis, y_axis
    Output: Plotly.Express Figure
    """
    fig = px.scatter(data, x=x_axis, y=y_axis, color_discrete_sequence=[app_color["trace"]])

    fig.update_layout(title="", plot_bgcolor=app_color["graph_bg"], height=400, paper_bgcolor=app_color["graph_bg"], font=dict(color="White"))
    fig.update_xaxes(title=labeldict["{}".format(x_axis)], showgrid=False, showline=True, zeroline=False, fixedrange=True)
    fig.update_yaxes(title=labeldict["{}".format(y_axis)], showgrid=True, showline=True, fixedrange=True, zeroline=False, gridcolor=app_color["graph_line"])
    return fig

def createTrendPlot(data, x_axis, y_axis, trend):
    """
    API to generate plots with various Linear and Non-Linear trendlines on demand, apply layout and styling
    Input: data (Pandas DataFrame), x_axis, y_axis, trend
    Output: Plotly.Express Figure
    """
    if (trend == 'ols'):
        fig = px.scatter(data, x=x_axis, y=y_axis, color_discrete_sequence=[app_color["trace"]], trendline="ols", title=trenddict["{}".format(trend)], trendline_color_override=app_color["trend"])
    elif (trend == 'olslog'):
        fig = px.scatter(data, x=x_axis, y=y_axis, color_discrete_sequence=[app_color["trace"]], trendline="ols", trendline_options=dict(log_x=True), title=trenddict["{}".format(trend)], trendline_color_override=app_color["trend"])
    elif (trend == '5ptrolling'):
        fig = px.scatter(data, x=x_axis, y=y_axis, color_discrete_sequence=[app_color["trace"]], trendline="rolling", trendline_options=dict(window=5), title=trenddict["{}".format(trend)], trendline_color_override=app_color["trend"])
    elif (trend == 'rollmedian'):
        fig = px.scatter(data, x=x_axis, y=y_axis, color_discrete_sequence=[app_color["trace"]], trendline="rolling", trendline_options=dict(function="median", window=5), title=trenddict["{}".format(trend)], trendline_color_override=app_color["trend"])
    elif (trend == 'expandmax'):
        fig = px.scatter(data, x=x_axis, y=y_axis, color_discrete_sequence=[app_color["trace"]], trendline="expanding", trendline_options=dict(function="max"), title=trenddict["{}".format(trend)], trendline_color_override=app_color["trend"])
    elif (trend == 'expomavg'):
        fig = px.scatter(data, x=x_axis, y=y_axis, color_discrete_sequence=[app_color["trace"]], trendline="ewm", trendline_options=dict(halflife=2), title=trenddict["{}".format(trend)], trendline_color_override=app_color["trend"])

    fig.update_layout(title="", plot_bgcolor=app_color["graph_bg"], height=400, paper_bgcolor=app_color["graph_bg"], font=dict(color="White"))
    fig.update_xaxes(title=labeldict["{}".format(x_axis)], showgrid=False, showline=True, zeroline=False, fixedrange=True)
    fig.update_yaxes(title=labeldict["{}".format(y_axis)], showgrid=True, showline=True, fixedrange=True, zeroline=False, gridcolor=app_color["graph_line"])
    return fig