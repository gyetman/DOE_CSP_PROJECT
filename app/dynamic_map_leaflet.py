import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import pandas as pd
import helpers

from dash.dependencies import Output, Input
from dash_leaflet import express as dlx
from pathlib import Path

gis_data = Path('./GISdata')

# TODO:
# 1. separate map theme loading (regulatory, solar, etc.) from
# basemap selection. Default to satellite, but allow streets,
# outdoor, any others ??
# 2. use a map-config file to load data, file locations, etc. 
# 3. use a geo helper module to lookup nearest features by theme and
# all required features used as input parameters. 
# 4. transfer & adapt code to write out parameters as json
# 5. style to be consistent with menu interface

# GREG'S REGULATORY LAYER (by itself)
test_layer = 'mapbox://styles/gyetman/ckbgyarss0sm41imvpcyl09fp'

# Mapbox setup
mapbox_url = "https://api.mapbox.com/styles/v1/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"
mapbox_token = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'

# Dictionary to hold map theme labels and ID values
# add any new themes here to make them appear in the 
# list of radio buttons. note: first item is the 
# default for when map loads, change order to update. 
mapbox_ids = {
    'Regulatory':'gyetman/ck7avopr400px1ilc7j49bi6j',
    'Outdoors': 'mapbox/outdoors-v9',
    'Satellite': 'mapbox/satellite-streets-v9', 
}

MAP_ID = "map-id"
BASE_LAYER_ID = "base-layer-id"
BASE_LAYER_DROPDOWN_ID = "base-layer-drop-down-id"
SITE_DETAILS = "site-details"
USER_POINT = 'user_point'

def get_style(feature):
    return dict()

def get_d_style(feature):
    return dict(fillColor='orange', weight=2, opacity=1, color='white')

def get_info(feature=None):
    header = [html.H4("US Power Plants")]
    if not feature:
        return header + ["Hover over a power plant"]
    return header + [html.B(feature["properties"]["name"]), html.Br(),
                     f"{float(feature['properties']['capacity_mw']):.3f} capacity MW"]

# load power plants JSON
power_plants_json = gis_data / 'power_plants.geojson'
pp_data = helpers.json_load(power_plants_json)
power_plants = dlx.geojson(pp_data, id="geojson", style=get_style, defaultStyle=dict(fillColor='orange', weight=2, opacity=1, color='white'))
# power_plants = dlx.geojson(pp_data, id="geojson", style=get_style)
# print(power_plants.featureStyle[0])
# power_plants.featureStyle[0]={'color':'orange'}
# print({power_plants.available_properties[0]})
# print({power_plants})
# should see if we can get Canvas circle markers instead? 
# they draw faster and can be styled#

#load canals JSON
canals_json = gis_data / 'canals.geojson'
ca_data = helpers.json_load(canals_json)
canals = dlx.geojson(ca_data, id='canals', style=get_style, defaultStyle=dict(fillColor='blue', weight=2, opacity=1, color='blue'))


info = html.Div(children=get_info(), id="info", className="mapinfo",
                style={"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000"})

regulatory = dl.TileLayer(url=mapbox_url.format(id = 'gyetman/ckbgyarss0sm41imvpcyl09fp', access_token=mapbox_token))

def render_map():
    comment = """ Click on a location to examine site details.  """
    return [
        html.H1("Site Selection"),
        html.P(comment),
        dl.Map(
            id=MAP_ID, 
            style={'width': '1000px', 'height': '500px'}, 
            center=[30.25,-97.05], 
            zoom=10,
            children=[
                dl.TileLayer(id=BASE_LAYER_ID),
                dl.ScaleControl(metric=True, imperial=True),

                # Placeholder for user-selected site. 
                # TODO: get an icon that's "invisible"
                dl.Marker(id=USER_POINT,position=[0, 0], icon={
                    "iconUrl": "/assets/149059.svg",
                    "iconSize": [20, 20]
                    },
                    children=[
                        dl.Tooltip("Selected site")
                ]),
                html.Div(id='theme-layer')
                # power_plants,
                # canals,
                # info,

                # TODO: load layers for default selection

                # power plants
                #plantMarkers = loadPowerPlants()
        ]),

        # map theme selection
        # TODO: change to tabs / buttons
        dcc.RadioItems(
            id='theme-dropdown',
            options=[{'label':'Canals', 'value':'canals'},
                     {'label':'Power Plants', 'value':'pplants'},
                     {'label': 'Regulatory', 'value':'regulatory'}],
            labelStyle={'display': 'inline-block'},
            value='canals'
        ),
        dcc.RadioItems(
            id=BASE_LAYER_DROPDOWN_ID,
            options = [
                {'label': name, 'value': mapbox_url.format(id = url, access_token=mapbox_token)}
                for name,url in mapbox_ids.items()
            ],
            labelStyle={'display': 'inline-block'},
            # use the first item as the default
            value=mapbox_url.format(id=next(iter(mapbox_ids.values())), access_token=mapbox_token)
        ),
        dcc.Markdown('#### Site details:'),
        html.Div(id=SITE_DETAILS),
    ]


theme_ids = {
    'canals': canals,
    'pplants': html.Div([power_plants, info]),
    'regulatory': regulatory
}

def register_map(app):
    @app.callback(Output(BASE_LAYER_ID, "url"),
                [Input(BASE_LAYER_DROPDOWN_ID, "value")])
    def set_baselayer(url):
        return url

    @app.callback(Output('theme-layer','children'),
                 [Input('theme-dropdown', 'value')])
    def set_theme_layer(theme):
        return theme_ids[theme]


    @app.callback(Output(USER_POINT, 'position'),
                  [Input(MAP_ID, 'click_lat_lng')])
    def click_coord(coords):
    # '''
    # Callback for updating the map after a user click 
    # TODO: in addition to returning 0,0, update icon
    # to be "invisible".
    # '''
        if not coords:
            return [0,0]
        else:
            return coords

    @app.callback(Output(SITE_DETAILS, 'children'),
                  [Input(MAP_ID, 'click_lat_lng')])
    def get_point_info(coords):
        if coords is None:
            return('Click on Map')
        else:
            # TODO: use coords and theme to lookup layers. 
            # theme should come from a state in the callback...
            # module to lookup info will called...
            return('Placeholder text: clicked!')

    @app.callback(Output('info', 'children'),
                 [Input("geojson", "featureHover")])
    def info_hover(feature):
        return get_info(feature)

# app = dash.Dash(__name__, external_scripts=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app = dash.Dash(__name__)

app.layout = html.Div(
    render_map()
)
register_map(app)

if __name__ == '__main__':
    app.run_server(debug=True, port=8150)


''' Example code for different types. 
see: https://dash-leaflet.herokuapp.com/ for documentation
# TODO: remove before alpha release. 

            dl.Marker(position=[56, 9.8], children=[
                dl.Tooltip("Marker tooltip"),
                dl.Popup([
                    html.H1("Marker popup"),
                    html.P("with inline html")
                ])
            ]),
            # Marker with custom icon.
            dl.Marker(position=[55.94, 9.96], icon={
                "iconUrl": "/assets/149059.svg",
                "iconSize": [25, 25]
            }, children=[
                dl.Tooltip("Marker with custom icon")
            ]),
            # Circle marker (with fixed radius in pixel).
            dl.CircleMarker(center=[56.05, 10.15], radius=20, children=[
                dl.Popup('Circle marker, 20px')
            ]),
            # Circle with fixed radius in meters.
            dl.Circle(center=[56.145, 10.21], radius=2000, color='rgb(255,128,0)', children=[
                dl.Tooltip('Circle, 2km radius')
            ]),
            # Polyline marker.
            dl.Polyline(id='polyline', positions=[[56.06, 10.0],
                                                  [56.056, 10.01],
                                                  [56.064, 10.028],
                                                  [56.0523, 10.0717],
                                                  [56.044, 10.073]], children=[
                dl.Tooltip('Polyline')
            ]),
            # Polygon marker.
            dl.Polygon(id='polygon', positions=[[56.013, 9.84],
                                                [56.0544, 9.939],
                                                [56.003, 10.001]], children=[
                dl.Tooltip('Polygon')
            ]),
            # Rectangle marker.
            dl.Rectangle(id='rectangle', bounds=[[55.9, 10.2], [56.0, 10.5]], children=[
                dl.Tooltip('Rectangle')
            ]
'''