import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import plotly.graph_objs as go
import numpy as np

CENTER_LAT=32.7767
CENTER_LON=-96.7970

external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_key = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'
app = dash.Dash(__name__, external_stylesheets=external_stylesheet)

# load electric price data
df = pd.read_csv('./GISData/electric_prices_zcta.csv')
df['text'] = '$' + df['MEAN_ind_rate'].round(3).astype(str) + '/kWH'

#load geoJSON geometries for price data (zip codes)
with open('./gisData/zcta.geojson','r') as f:
    geoj = json.load(f)

userPoint = go.Scattermapbox(
    name='Selected Site',
    lat=[0],
    lon=[0],
    # replaced None object with 'none', confusing but that turns it off!  
    hoverinfo='none',
    mode='markers',
    marker=dict(
        size=13,
    ),
    showlegend=False,
    visible=False,

)

priceData = go.Choroplethmapbox(
    name='Industrial Electric Prices',
    geojson=geoj, 
    locations=df.ZCTA, 
    z=df.Mean_ind_rate,
    colorscale="Viridis", 
    colorbar=dict(
        title='Price $/kWH, 2018',
    ),
    marker_opacity=1, 
    marker_line_width=0,
    text=df.text,
    hoverinfo='text',
    visible=True,
    # TODO: add year to map GUI (year of data)
    )