import app_config
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import pandas as pd
import helpers
import pointLocationLookup

from dash.dependencies import ALL, Input, Output, State, MATCH
from dash.exceptions import PreventUpdate
from pathlib import Path

gis_data = app_config.gis_data_path

# TODO:
# add link (lines) and symbols for closest features
# add legend(s)
# 2. use a map-config file to load data, file locations, etc. 
# 4. transfer & adapt code to write out parameters as json
# 5. style to be consistent with menu interface

# Mapbox setup
mapbox_url = "https://api.mapbox.com/styles/v1/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"
# public mapbox token
mapbox_token = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'

# Dictionary to hold map theme labels and ID values
# add any new themes here to make them appear in the 
# list of radio buttons. note: first item is the 
# default for when map loads, change order to update. 
mapbox_ids = {
    'Satellite': 'mapbox/satellite-streets-v9', 
    'Outdoors': 'mapbox/outdoors-v9',
    # 'Regulatory':'gyetman/ck7avopr400px1ilc7j49bi6j', # duplicate entry
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
    header = [html.H4("Feature Details")]
    if feature:
        return header + [html.B(feature[0]["properties"]["name"]), html.Br(),
            f"{float(feature[0]['properties']['capacity_mw']):.3f} capacity MW"]
    else:
        return header + ["Hover over a feature"]


# load power plants JSON
power_plants = dl.GeoJSON(
    url='/assets/power_plants.geojson',
    #id='geojson_power',
    id = {'type':'json_theme','index':'geojson_power'},
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={"radius": 75},
    hoverStyle=dict(weight=5, color='#666', dashArray='')
)


# load canals json
canals = dl.GeoJSON(
    url='/assets/canals.geojson', 
    id='geojson_canals', 
    #defaultstyle=dict(fillColor='blue', weight=2, opacity=1, color='blue'),
)

# regulatory layer from Mapbox
regulatory = dl.TileLayer(url=mapbox_url.format(id = 'gyetman/ckbgyarss0sm41imvpcyl09fp', access_token=mapbox_token))

# placeholder for mouseover data
info = html.Div(children=get_info(), id="info", className="mapinfo",
                style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"})

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
                # placeholder for lines to nearby plants
                dl.LayerGroup(id="closest-facilities"),
                # Placeholder for user-selected site. 
                dl.Marker(id=USER_POINT,position=[0, 0], icon={
                    "iconUrl": "/assets/149059.svg",
                    "iconSize": [20, 20]
                    },
                    children=[
                        dl.Tooltip("Selected site")
                ]),
                html.Div(id='theme-layer')
            ]),
        html.Div([
            html.Div(id='next-button')
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
    'canals': html.Div([canals, info]),
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

    @app.callback([Output(SITE_DETAILS, 'children'),Output("closest-facilities", 'children')],
                  [Input(MAP_ID, 'click_lat_lng')])

    def get_point_info(lat_lng):
        ''' callback to update the site information based on the user selected point'''
        if lat_lng is None:
            print('no coords')
            return('Click on the Map to see site details.')
        else:
            markdown = dcc.Markdown(str(pointLocationLookup.lookupLocation(lat_lng)))
            #positions = 
            desal = dl.Polyline(positions=[lat_lng,[45,-90]], color='#FF0000')
            plant = dl.Polyline(positions=[lat_lng,[45,-95]],color='#ffa500')
            return markdown, [desal,plant]
            #return dcc.Markdown(str(pointLocationLookup.lookupLocation(lat_lng)))
            
    @app.callback(
        Output(component_id='next-button',component_property='children'),
        [Input(component_id=SITE_DETAILS,component_property='children')],
        [State(MAP_ID,'children')],
        prevent_initial_call=True
    )
    def enableButton(site,site_properties):
        ''' output to enable next button after a site has been selected '''
        if site == 'Click on the Map to see site details.':
            raise PreventUpdate
        else:
            return(
                html.Div([
                    html.Div(id='button-div'),
                    html.Div(html.A(
                        html.Button('Select Models', 
                                id='model-button',
                            ),
                        href='http://127.0.0.1:8077/model-selection'
                        )
                      )
                ], className='row',
                ) 
            )

        # [Input("geojson_power", "hover_feature")],
        # [State("theme-dropdown",'value')]
    @app.callback(Output('info', 'children'),
        [Input({'type':'json_theme', 'index': ALL}, 'hover_feature')],
    )
    def info_hover(feature):
        ''' callback for feature hover '''
        if feature:
            print(len(feature))
            return get_info(feature)
        else:
            header = [html.H4("Feature Details")]
            return header + ["Hover over a feature"]

    # @app.callback(Output('info', 'children'),[Input("info", "featureHover")])
    # def info_hover(feature):
    #     return get_info(feature)

# app = dash.Dash(__name__, external_scripts=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app = dash.Dash(__name__)
app.title = 'Site Selection (Beta)'
app.layout = html.Div(
    render_map()
)
register_map(app)

if __name__ == '__main__':
    app.run_server(debug=True, port=8150)


