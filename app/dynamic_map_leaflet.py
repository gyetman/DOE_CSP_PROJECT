import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import pandas as pd

from dash.dependencies import Output, Input


# TODO:
# 1. separate map theme loading (regulatory, solar, etc.) from
# basemap selection. Default to satellite, but allow streets,
# outdoor, any others ??
# 2. use a map-config file to load data, file locations, etc. 
# 3. use a geo helper module to lookup nearest features by theme and
# all required features used as input parameters. 
# 4. transfer & adapt code to write out parameters as json
# 5. style to be consistent with menu interface

# Methods for data loading
def loadPowerPlants():
    ''' load power plant data & return mapbox layer '''
    # TODO: use helper functions & config for loading / location
    pplants = df.load(csv('./GISData/'))





# Mapbox setup
mapbox_url = "https://api.mapbox.com/styles/v1/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"
mapbox_token = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'

# Dictionary to hold map theme labels and ID values
# add any new themes here to make them appear in the 
# list of radio buttons
mapbox_ids = {
    'Regulatory':'gyetman/ck7avopr400px1ilc7j49bi6j',
    'Outdoors': 'mapbox/outdoors-v9',
    'Satellie with streets': 'mapbox/satellite-streets-v9', 

}

MAP_ID = "map-id"
BASE_LAYER_ID = "base-layer-id"
BASE_LAYER_DROPDOWN_ID = "base-layer-drop-down-id"
SITE_DETAILS = "site-details"
USER_POINT = 'user_point'

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
                dl.ScaleControl(metric=True, imperial=False),

                # Placeholder for user-selected site. 
                # TODO: get an icon that's "invisible"
                dl.Marker(id=USER_POINT,position=[0, 0], icon={
                    "iconUrl": "/assets/149059.svg",
                    "iconSize": [20, 20]
                    },
                    children=[
                        dl.Tooltip("Selected site")
                ]),

                # TODO: load layers for default selection

                # power plants
                #plantMarkers = loadPowerPlants()
        ]),

        # map theme selection
        # TODO: change to tabs / buttons
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

    
def register_map(app):
    @app.callback(Output(BASE_LAYER_ID, "url"),
                [Input(BASE_LAYER_DROPDOWN_ID, "value")])
    def set_baselayer(url):
        return url

    # Callback for updating the map after a user click 
    # TODO: in addition to returning 0,0, update icon
    # to be "invisible".
    @app.callback(Output(USER_POINT, 'position'),
                  [Input(MAP_ID, 'click_lat_lng')])
    def click_coord(coords):
        if coords is not None:
            return(coords)
        else:
            return [0,0]

    @app.callback(Output(SITE_DETAILS, 'children'),
                  [Input(MAP_ID, 'click_lat_lng')])
    def get_point_info(coords):
        if coords is None:
            return('Click on Map')
        else:
            # TODO: use coords and theme to lookup layer. 
            # theme should come from a state in the callback...
            # module to lookup info will called...
            return('Placeholder text: clicked!')



app = dash.Dash(__name__, external_scripts=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

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