import app_config
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import pandas as pd
import helpers

from dash.dependencies import Output, Input
import dash_leaflet as dl
from pathlib import Path

gis_data = app_config.gis_data_path

# globals for map and layers
MAP_ID = "map-id"
BASE_LAYER_ID = "base-layer-id"
BASE_LAYER_DROPDOWN_ID = "base-layer-drop-down-id"
SITE_DETAILS = "site-details"
USER_POINT = 'user_point'

# Mapbox setup
mapbox_url = "https://api.mapbox.com/styles/v1/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"
# public mapbox token
mapbox_token = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'
def render_map():
    ''' Sets up layers and options for the map '''
    comment = """ Click on a location to examine site details.  """
    return[
        html.H1("Site Selection"),
        html.P(comment),
        dl.Map(
            style={'width': '1000px', 'height': '500px'}, 
            center=[33.25,-110.5], 
            zoom=6,
            children = [
                dl.TileLayer(),
                dl.GeoJSON(url='/assets/canals.geojson',id='canals')
            ],
        ),
        html.Div(id='canal')
        html.Div(id='info')
    ]


app = dash.Dash(__name__)
app.title = 'Site Selection (Beta)'
app.layout = html.Div(
    render_map()
)
# register_map(app)


@app.callback(Output("canal", "children"), [Input("canals", "hover_feature")])
def state_hover(feature):
    if feature is not None:
        return f"{feature['properties']['Name']}"




if __name__ == '__main__':
    app.run_server(debug=True, port=8150)






