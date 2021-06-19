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

RESULTS_MAP_ID = "map-id"
RESULTS_BASE_LAYER_ID = "results-base-layer-id"
RESULTS_BASE_LAYER_DROPDOWN_ID = "base-layer-drop-down-id"
RESULTS_SITE_DETAILS = "site-details-results"

classes = [0.0,1.0,2.0,3.0,4.0,5.0]
color_scale = ['#edf8fb','#ccece6','#99d8c9','#66c2a4','#2ca25f','#006d2c']
style = dict(weight=1, opacity=1, color='white', fillColor=None, dashArray='3', fillOpacity=1)
ctg = [f'${cls:.2f}' for cls in classes]
ctg[-1]+='+'

colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=color_scale, width=300, height=30, position="bottomright")

# load power plants JSON
power_plants = dl.GeoJSON(
    url='/assets/power_plants.geojson',
    id = {'type':'json_theme','index':'geojson_power'},
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={"radius": 75},
    hoverStyle=dict(weight=5, color='#666', dashArray=''),
)

# load Desal plants
desal = dl.GeoJSON(
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
)

# load wells
wells = dl.GeoJSON(
    url='/assets/wells_sw.geojson',
    id = {'type':'json_theme','index':'geojson_wells'},
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={'radius': 75},
    hoverStyle=dict(weight=5, color='#666', dashArray=''),
)

# regulatory layer from Mapbox
regulatory = dl.TileLayer(url=mapbox_url.format(id = 'gyetman/ckbgyarss0sm41imvpcyl09fp', access_token=mapbox_token))

# County price data
# with open('./assets/us_counties2.geojson','r', encoding = 'UTF-8') as f:
#     counties= json.load(f)

        
# us_counties = dl.GeoJSON(
#     #url='/assets/us_counties2.geojson',
#     data=counties,
#     id='water_prices',
#     options=dict(),
#     hideout=dict(colorscale=color_scale, classes=classes, style=style, color_prop="comm_price"),
# )

with open('./assets/global_water_tarrifs.geojson', 'r', encoding='UTF-8') as f:
    city_prices = json.load(f)

city_price_lyr = dl.GeoJSON(
    data=city_prices,
    id='city_water_prices',
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={"radius": 75},
    hoverStyle=dict(weight=5, color='#666', dashArray=''),
)
# placeholder for mouseover data
info = html.Div(children='',
                className="mapinfo",
                style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000", "background": "lightgrey"},
                id="results-info")


map_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Home", href='/home')),
              dbc.NavItem(dbc.NavLink("Charts", href='/chart-results')),
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
    id=RESULTS_MAP_ID, 
    style={'width': '100%', 'height': '500px'}, 
    zoom=10,
    children=[
        dl.LayerGroup(id="results-closest-facilities"),
        html.Div(id='init')
    ])

radios = dbc.FormGroup([
    dbc.RadioItems(
        id='theme-radios',
        options=[{'label':'Canals', 'value':'canals'},
                    {'label':'Power Plants', 'value':'pplants'},
                    {'label':'Desalination Plants', 'value':'desal'},
                    {'label':'Water wells', 'value':'wells'},
                    {'label': 'Regulatory', 'value':'regulatory'}],
        labelStyle={'display': 'inline-block'},
        value='canals',
        inline=True
    ),
    dbc.RadioItems(
        id=RESULTS_BASE_LAYER_DROPDOWN_ID,
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
'wells': html.Div([wells, info]),
'regulatory': regulatory
}

def render_results_map():
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
                    id='price-factor',
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
                html.Div(id=RESULTS_SITE_DETAILS)
            ],width=3)
        ],style={'padding':20})
    ],id='init_center')

# def register_results_map(app):
@app.callback(Output(RESULTS_BASE_LAYER_ID, "url"),
            [Input(RESULTS_BASE_LAYER_DROPDOWN_ID, "value")])
def set_baselayer(url):
    return url

@app.callback(Output(RESULTS_MAP_ID, "center"),
            [Input("init_center", "children")])
def set_center(initc):
    map_data = helpers.json_load(app_config.map_json)
    site_lat=map_data['latitude']
    site_long=map_data['longitude']
    return (site_lat,site_long)


@app.callback(Output('results-theme-layer','children'),
                [Input('theme-radios', 'value')])
def set_theme_layer(theme):
    return theme_ids[theme]

@app.callback([Output(RESULTS_MAP_ID, 'children'),
            Output('water-price', 'children')],
            Output('price_difference', 'children'),
            [Input("price-factor",'value')],
            [Input("results-closest-facilities",'children')])
def update_price_layers(price_factor,closest_from_map):
    ''' filter the Texas water data and City price data based on model or factor price '''
    if not price_factor:
        price_factor = 1.0 # handle null input
    app_json = helpers.json_load(app_config.app_json)
    model_lookup = app_config.build_file_lookup(app_json['solar'],app_json['desal'],app_json['finance'],app_json['timestamp'])
    finance = helpers.json_load(model_lookup['sam_desal_finance_outfile'])
    model_price =  finance[helpers.index_in_list_of_dicts(finance,'Name','Levelized cost of water')]['Value']
    # with open('./assets/us_counties2.geojson','r', encoding = 'UTF-8') as f:
    #     counties= json.load(f)
    # new_features = [feature for feature in counties['features'] if feature['properties']['comm_price']]
    # new_features = [feature for feature in new_features if feature['properties']['comm_price'] > model_price * price_factor]

    # counties['features'] = new_features

    # us_counties = dl.GeoJSON(
    #     data=counties,
    #     id='water_prices',
    #     options=dict(),
    #             hideout=dict(colorscale=color_scale, classes=classes, style=style, color_prop="comm_price"),
    # )

    with open('./assets/global_water_tarrifs.geojson','r', encoding = 'UTF-8') as f:
        city_prices = json.load(f)

    new_features = [feature for feature in city_prices['features'] if float(feature['properties']['CalcTot100M3CurrUSD'])/100 > model_price * price_factor]

    city_prices['features'] = new_features

    # city_price_lyr = dl.GeoJSON(
    #     data=city_prices,
    #     id='city_water_prices',
    #     cluster=True,
    #     zoomToBoundsOnClick=True,
    #     superClusterOptions={"radius": 75},
    #     hoverStyle=dict(weight=5, color='#666', dashArray=''),
    # )
    markers = []
    for pt in new_features:
        markers.append(
            dl.CircleMarker(center=(float(pt['properties']['UtilityLatitude']),float(pt['properties']['UtilityLongitude'])), 
            children=dl.Tooltip('Price (at 100m3): ${:0.2f}'.format(float(pt['properties']['CalcTot100M3CurrUSD'])/100))

        )
    )
    return([
            dl.TileLayer(id=RESULTS_BASE_LAYER_ID),
            dl.ScaleControl(metric=True, imperial=True),
            # us_counties,
            dl.LayerGroup(markers),
            info,
            dl.LayerGroup(id="results-closest-facilities",children=closest_from_map),
            html.Div(id='results-theme-layer'),
            ],
        f'Projected LCOW from desalination: ${model_price:,.2f}',
        html.P(f'Price difference between model and factor: ${abs(model_price - price_factor * model_price):.2f}',id="price_difference")

    )

@app.callback([Output(RESULTS_SITE_DETAILS, 'children'),
                Output("results-closest-facilities", 'children')],
                [Input('init', 'children')],
                State(RESULTS_SITE_DETAILS, 'children'),
                prevent_initial_call=False
            )
def get_point_info(_,site_details_state):
    '''update the site information based on user selected point'''
    map_data = helpers.json_load(app_config.map_json)
    site_lat=map_data['latitude']
    site_long=map_data['longitude']
    lat_lng = (site_lat, site_long)
    markdown = dcc.Markdown(str(pointLocationLookup.lookupLocation(lat_lng)))
    closest = pointLocationLookup.getClosestInfrastructure(lat_lng)
    # TODO: change to .get for keys and return result, leave location handling to pointLocationLookup.
    # Site selected by user from map-data. 
    user_point = dl.Marker(
                position=(site_lat, site_long), 
                icon={
                "iconUrl": "/assets/149059.svg",
                "iconSize": [20, 20]
                },
                children=[dl.Tooltip("Selected site")],
    )
    if not closest:
        return markdown, user_point
    elif 'plant' in closest.keys():
        desal = dl.Polyline(positions=[lat_lng,closest['desal']], color='#FF0000', children=[dl.Tooltip("Desal Plant")])          
        plant = dl.Polyline(positions=[lat_lng,closest['plant']], color='#ffa500', children=[dl.Tooltip("Power Plant")])
        canal = dl.Polyline(positions=[lat_lng,closest['canal']], color='#add8e6', children=[dl.Tooltip("Canal/Piped Water")])
        water = dl.Polyline(positions=[lat_lng,closest['water']], color='#000000', children=[dl.Tooltip("Water Network Proxy")])
        return markdown, [desal,plant,canal,water,user_point]
    else:
        desal = dl.Polyline(positions=[lat_lng,closest['desal']], color='#FF0000', children=[dl.Tooltip("Desal Plant")]) 
        return markdown, [desal,user_point]

@app.callback(Output('results-info', 'children'),
        [Input({'type':'json_theme', 'index': ALL}, 'hover_feature')],
        prevent_initial_call = True
    )
def get_info(features):
    ''' callback for feature hover '''
    header = ['Hover over a Feature\n']
    #feature is a list of dicts, grab first feature
    if features: 
       feature = features[0]
    else:
        return header
    if feature:
        #check if feature is a cluster
        if feature['properties']['cluster']:
            return ["Click cluster to expand"]
        #if feature is Desalination Plant
        elif 'Technology' in feature['properties'].keys():
            header = ['Desalination Plant\n', html.Br()]
            name = feature['properties']['Project name']
            capacity_field = feature['properties']['Capacity (m3/d)']
            units = 'm3/day'
            return header+[html.B(name), html.Br(),
                f"Capacity: {capacity_field} {units}"]
        elif 'TDS' in feature['properties'].keys():
            header = ['Well\n', html.Br()]
            name = feature['properties']['orgName']
            tds = feature['properties']['TDS']
            temperature = feature['properties']['TEMP']
            units = 'mg/L'
            temp_units = 'C'
            if all((temperature, tds)):
                return header + [html.B(name), html.Br(),
                    f"TDS: {tds:,} {units}", html.Br(), 
                    f"Temperature: {temperature:.1f} {temp_units}" ]
            elif(temperature):
                return header + [html.B(name), html.Br(),
                f"TDS: - {units}", html.Br(),
                f"Temperature: {temperature:.1f} {temp_units}"]
            elif(tds):
                return header + [html.B(name), html.Br(),
                f"TDS: {tds:,} {units}", html.Br(), 
                f"Temperature: - {temp_units}"]

        #feature is Power Plant
        else:
            header = ['Power Plant\n', html.Br()] 
            name = feature['properties']['Plant_name']
            fuel = feature['properties']['Plant_primary_fuel']
            capacity_field = feature['properties']['Plant_nameplate_capacity__MW_']
            units = 'MW'
            return header + [html.B(name), html.Br(),
                f"Fuel: {fuel}", html.Br(),
                f"Capacity: {float(capacity_field):,.1f} {units}"]
    else:
        return ['Hover over a feature']


external_stylesheets = [dbc.themes.FLATLY]
app.layout = render_results_map()

if __name__ == '__main__':
    app.run_server(debug=False, port=8155)


