import app_config
import json
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import pandas as pd
import helpers
import pointLocationLookup
import dash_leaflet.express as dlx

from dash.dependencies import ALL, Input, Output, State, MATCH
from dash.exceptions import PreventUpdate
from pathlib import Path
from app import app

app.title='Results Map'
price_difference = 0
gis_data = app_config.gis_data_path
# Div for legend
# Site Selection

# TODO:
# 2. use a map-config file to load data, file locations, etc. 
# 4. transfer & adapt code to write out parameters as json
# Fix bug: line to closest desal plan is removed after factor
# is adjusted. 

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
    'Topographic': 'mapbox/outdoors-v9',
    # 'Regulatory':'gyetman/ck7avopr400px1ilc7j49bi6j', # duplicate entry
}

MAP_ID = "map-id"
BASE_LAYER_ID = "base-layer-id"
BASE_LAYER_DROPDOWN_ID = "base-layer-drop-down-id"
SITE_DETAILS = "site-details"
USER_POINT = 'user_point'

classes = [0.0,1.0,2.0,3.0,4.0,5.0]
color_scale = ['#edf8fb','#ccece6','#99d8c9','#66c2a4','#2ca25f','#006d2c']
style = dict(weight=1, opacity=1, color='white', fillColor=None, dashArray='3', fillOpacity=1)
ctg = ["${:,.2f}".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["${:,.2f}+".format(classes[-1])]
colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=color_scale, width=300, height=30, position="bottomright")

''' load data layers and objects used in layout '''
map_data = helpers.json_load(app_config.map_json)
site_lat=map_data['latitude']
site_long=map_data['longitude']
# Read in the model price from the right file via cfg and helpers
# TODO: this needs to be part of a callback so that it dynamically updates 
# after the model update! 
# app_json = helpers.json_load(app_config.app_json)
# model_lookup = app_config.build_file_lookup(app_json['solar'],app_json['desal'],app_json['finance'])
# finance = helpers.json_load(model_lookup['sam_desal_finance_outfile'])
# model_price =  finance[helpers.index_in_list_of_dicts(finance,'Name','Levelized cost of water')]['Value']

# load power plants JSON
power_plants = dl.GeoJSON(
    url='/assets/power_plants.geojson',
    #id='geojson_power',
    id = {'type':'json_theme','index':'geojson_power'},
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={"radius": 75},
    hoverStyle=dict(weight=5, color='#666', dashArray=''),
)

# load Desal plants
desal = dl.GeoJSON(
    #url='/assets/desal_plants_update.geojson',
    url='/assets/global_desal_plants.geojson',
    id = {'type':'json_theme','index':'geojson_desal'},
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={'radius': 75},
    hoverStyle=dict(weight=5, color='#666', dashArray=''),
)

# load canals json
canals = dl.GeoJSON(
    url='/assets/canals.geojson', 
    id='geojson_canals', 
    #defaultstyle=dict(fillColor='blue', weight=2, opacity=1, color='blue'),
)

# regulatory layer from Mapbox
regulatory = dl.TileLayer(url=mapbox_url.format(id = 'gyetman/ckbgyarss0sm41imvpcyl09fp', access_token=mapbox_token))

# tx_counties = dl.GeoJSON(
#     url='/assets/tx_water_prices.geojson',
#     id='tx_water_prices',
    #options=dict(style=dlx.choropleth.style),
        #hoverStyle=dict(weight=5, color='#666', dashArray=''),
    #     hideout=dict(colorscale=color_scale, classes=classes, style=style, color_prop="comm_avg"),
#)


# County price data
with open('./assets/us_counties2.geojson','r', encoding = 'UTF-8') as f:
    counties= json.load(f)
# new_features = [feature for feature in counties['features'] if feature['properties']['comm_price']]
# new_features = [feature for feature in new_features if feature['properties']['comm_price'] > model_price]
#new_feautres = [feature for feature in new_features if new_features['properties']['comm_price'] > model_price]

# counties['features'] = new_features

us_counties = dl.GeoJSON(
    #url='/assets/us_counties2.geojson',
    data=counties,
    id='water_prices',
    options=dict(style=dlx.choropleth.style),
        #hoverStyle=dict(weight=5, color='#666', dashArray=''),
        hideout=dict(colorscale=color_scale, classes=classes, style=style, color_prop="comm_price"),
)


# city price data
# with open('./assets/city_water_prices.geojson','r', encoding = 'UTF-8') as f:
#     city_prices = json.load(f)

with open('./assets/global_water_tarrifs.geojson', 'r', encoding='UTF-8') as f:
    city_prices = json.load(f)

# new_features = [feature for feature in city_prices['features'] if feature['properties']['Water_bill'] > model_price]
# city_prices['features'] = new_features

city_price_lyr = dl.GeoJSON(
    data=city_prices,
    id='city_water_prices',
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={"radius": 75},
    hoverStyle=dict(weight=5, color='#666', dashArray=''),
)
# placeholder for mouseover data
info = html.Div(children='Hover over a Feature',
                className="mapinfo",
                style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"},
                id="info")


map_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Charts", href='/chart-results')),
            dbc.NavItem(dbc.NavLink("Report", href='/analysis-report')),
            dbc.NavItem(dbc.NavLink("Results Map"), active=True)],
    brand='Water Prices',
    color='primary',
    dark=True,
    sticky='top',
    style={'marginBottom':20}
)

legend = html.Img(
    id='legend',
    src='assets/legend_update2.png'
)

site_results_map = dl.Map(
    id=MAP_ID, 
    style={'width': '100%', 'height': '500px'}, 
    center=[site_lat,site_long], 
    zoom=10,
    children=[
        dl.TileLayer(id=BASE_LAYER_ID),
        dl.ScaleControl(metric=True, imperial=True),
        info,
        us_counties,
        city_price_lyr,
        #colorbar,
        #dl.GeoJSON(url='/assets/tx_counties.geojson',id='counties'),
        #dl.GeoJSON(url='/assets/us_counties2.geojson',id='counties'),
        # placeholder for lines to nearby plants
        dl.GeoJSON(id="closest-facilities"),
        # Site selected by user from map-data. 
        dl.Marker(id=USER_POINT,position=[site_lat, site_long], icon={
            "iconUrl": "/assets/149059.svg",
            "iconSize": [20, 20]
            },
            children=[
                dl.Tooltip("Selected site")
        ]),
        html.Div(id='theme-layer')
    ])

radios = dbc.FormGroup([
    dbc.RadioItems(
        id='theme-dropdown',
        options=[{'label':'Canals', 'value':'canals'},
                    {'label':'Power Plants', 'value':'pplants'},
                    {'label':'Desalination Plants', 'value':'desal'},
                    {'label': 'Regulatory', 'value':'regulatory'}],
        labelStyle={'display': 'inline-block'},
        value='canals',
        inline=True
    ),
    dbc.RadioItems(
        id=BASE_LAYER_DROPDOWN_ID,
        options = [
            {'label': name, 'value': mapbox_url.format(id = url, access_token=mapbox_token)}
            for name,url in mapbox_ids.items()
        ],
        labelStyle={'display': 'inline-block'},
        # use the first item as the default
        value=mapbox_url.format(id=next(iter(mapbox_ids.values())), access_token=mapbox_token),
        inline=True
    ),
],row=True)


theme_ids = {
'canals': html.Div([canals]),
'pplants': html.Div([power_plants, info]),
'desal': html.Div([desal, info]),
'regulatory': regulatory
}

def get_info(feature=None):
    header = [html.H4("Feature Details")]
    if feature:
        if 'cluster' in list(feature[0]["properties"].keys()):
            return [html.H4("Click on a cluster to see details")]
        if 'Technology' in list(feature[0]["properties"].keys()):
            units = 'm3/day'
        elif 'Country' in list(feature[0]["properties"].keys()):
            units = 'MW'
        return header + [html.B(feature[0]["properties"]["name"]), html.Br(),
            f"{float(feature[0]['properties']['capacity_mw']):,.1f} Capacity {units}"]
    else:
        #return header + ["Hover over a feature"]
        return None


def render_map():
    # create and return the div
    return html.Div([
        map_navbar,
        dbc.Row([
            dbc.Col([
                site_results_map,
                dbc.Row([
                    dbc.Col(radios, width=7),
                    dbc.Col(legend),
                ]),
            ],width=8),
            dbc.Col([
                html.H4('Water Price:'),
                html.P(id='water-price'),
                html.P(f'Price difference in closest demand location: ${price_difference:.2f}', id='price_difference'),
                html.P(f'Factor for adapting LCOW for incremental costs or credits:', id='factor_tooltip'),
                dcc.Input(
                    id='price_factor',
                    type="number",
                    value=1.0,
                    step = 0.1,
                    min=0.3,
                    max=3.0,
                ),
                dbc.Tooltip(
                    "If subsidies, decrease LCOW. If additional costs, increase it. ",
                    target='factor_tooltip'
                ),
                html.H3('Site details:', className='text-success'),
                html.Div(id=SITE_DETAILS)
            ],width=3)
        ],style={'padding':20})
    ])

def register_map(app):
    @app.callback(Output(BASE_LAYER_ID, "url"),
                [Input(BASE_LAYER_DROPDOWN_ID, "value")])
    def set_baselayer(url):
        return url

    @app.callback(Output('theme-layer','children'),
                 [Input('theme-dropdown', 'value')])
    def set_theme_layer(theme):
        return theme_ids[theme]

    @app.callback([Output(MAP_ID, 'children'),
                Output('water-price', 'children')],
                [Input("price_factor",'value')],
                [Input("closest-facilities",'children')], 
                prevent_initial_call = True,

    )

    def update_price_layers(price_factor,closest_from_map):
        if closest_from_map:
            print(closest_from_map)
        else:
            print('No closest layers')

        ''' filter the Texas water data and City price data based on model or factor price '''
        if not price_factor:
            price_factor = 1.0 # handle null input
        app_json = helpers.json_load(app_config.app_json)
        model_lookup = app_config.build_file_lookup(app_json['solar'],app_json['desal'],app_json['finance'])
        finance = helpers.json_load(model_lookup['sam_desal_finance_outfile'])
        model_price =  finance[helpers.index_in_list_of_dicts(finance,'Name','Levelized cost of water')]['Value']
        with open('./assets/us_counties2.geojson','r', encoding = 'UTF-8') as f:
            counties= json.load(f)
        new_features = [feature for feature in counties['features'] if feature['properties']['comm_price']]
        new_features = [feature for feature in new_features if feature['properties']['comm_price'] > model_price * price_factor]
        #new_feautres = [feature for feature in new_features if new_features['properties']['comm_price'] > model_price]

        counties['features'] = new_features

        us_counties = dl.GeoJSON(
            #url='/assets/us_counties2.geojson',
            data=counties,
            id='water_prices',
            options=dict(style=dlx.choropleth.style),
                    #hoverStyle=dict(weight=5, color='#666', dashArray=''),
                    hideout=dict(colorscale=color_scale, classes=classes, style=style, color_prop="comm_price"),
        )

        with open('./assets/global_water_tarrifs.geojson','r', encoding = 'UTF-8') as f:
            city_prices = json.load(f)

        new_features = [feature for feature in city_prices['features'] if float(feature['properties']['CalcTot100M3CurrUSD'])/100 > model_price * price_factor]

        city_prices['features'] = new_features

        city_price_lyr = dl.GeoJSON(
            data=city_prices,
            id='city_water_prices',
            cluster=True,
            zoomToBoundsOnClick=True,
            superClusterOptions={"radius": 75},
            hoverStyle=dict(weight=5, color='#666', dashArray=''),
        )
        markers = []
        for pt in new_features:
            markers.append(
                dl.CircleMarker(center=(float(pt['properties']['UtilityLatitude']),float(pt['properties']['UtilityLongitude'])), 
                children=dl.Tooltip('Price (at 100m3): ${:0.2f}'.format(float(pt['properties']['CalcTot100M3CurrUSD'])/100))

            )
        )
        return([
                dl.TileLayer(id=BASE_LAYER_ID),
                dl.ScaleControl(metric=True, imperial=True),
                us_counties,
                dl.LayerGroup(markers),
                #ccolorbar,
                info,
                dl.GeoJSON(id="closest-facilities",data=closest_from_map),
                #closest_from_map,
                # Site selected by user from map-data. 
                dl.Marker(id=USER_POINT,position=[site_lat, site_long], icon={
                    "iconUrl": "/assets/149059.svg",
                    "iconSize": [20, 20]
                    },
                    children=[
                        dl.Tooltip("Selected site")
                ],),
                html.Div(id='theme-layer'),
                ],
            f'Projected LCOW from desalination: ${model_price:,.2f}'

        )

    @app.callback([Output(SITE_DETAILS, 'children'),Output("closest-facilities", 'children')],
                    [Input(USER_POINT, 'position'),
                    State(SITE_DETAILS, 'children')],
                    prevent_initial_call=False
                )
                
        
    def get_point_info(lat_lng,site_details_state):
        ''' callback to update the site information based on the user selected point'''
        # prevent the callback from triggering after initial load
        # if site_details_state:
        #     raise PreventUpdate
        # if lat_lng is None:
        #     return('Click on the Map to see site details.'), [0,0]
        #else:
        markdown = dcc.Markdown(str(pointLocationLookup.lookupLocation(lat_lng)))
        closest = pointLocationLookup.getClosestInfrastructure(lat_lng)
        # TODO: change to .get for keys and return result, leave location handling to pointLocationLookup. 
        if not closest:
            return markdown, [None, None, None, None]
        elif 'plant' in closest.keys():
            desal = dl.Polyline(positions=[lat_lng,closest['desal']], color='#FF0000', children=[dl.Tooltip("Desal Plant")])          
            plant = dl.Polyline(positions=[lat_lng,closest['plant']], color='#ffa500', children=[dl.Tooltip("Power Plant")])
            canal = dl.Polyline(positions=[lat_lng,closest['canal']], color='#add8e6', children=[dl.Tooltip("Canal/Piped Water")])
            water = dl.Polyline(positions=[lat_lng,closest['water']], color='#000000', children=[dl.Tooltip("Water Network Proxy")])
            return markdown, [desal,plant,canal,water]
        else:
            desal = dl.Polyline(positions=[lat_lng,closest['desal']], color='#FF0000', children=[dl.Tooltip("Desal Plant")]) 
            return markdown, desal

    @app.callback(Output('info', 'children'),
            [Input({'type':'json_theme', 'index': ALL}, 'hover_feature')]
        )
    def info_hover(feature):
        ''' callback for feature hover '''
        return(get_info(feature))


external_stylesheets = [dbc.themes.FLATLY]
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app.title = 'Site Details'
# app.layout = html.Div(
#     render_map()
# )
# app.layout = render_map()
register_map(app)

if __name__ == '__main__':
    app.run_server(debug=True, port=8155)


