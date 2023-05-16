from dash.html.Label import Label
import app_config
import itertools
import json
import dash
import dash_bootstrap_components as dbc
# import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
#import helpers
import pointLocationLookup
import lookup_openei_rates
from dash.dependencies import ALL, Input, Output, State, MATCH
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import arrow_function, assign

import plotly.graph_objects as go
from pathlib import Path

from app import app

gis_data = app_config.gis_data_path


#TODO:
# nothing current

# Mapbox setup
mapbox_url = "https://api.mapbox.com/styles/v1/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"
# public mapbox token
mapbox_token = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'

# Dictionary to hold map theme labels and ID values
# add any new themes here to make them appear in the 
# list of radio buttons. note: first item is the 
# default for when map loads, change order to update. 
mapbox_ids = {    
    'Topographic': 'mapbox/outdoors-v9',
    'Satellite': 'mapbox/satellite-streets-v9', 
    # 'Regulatory':'gyetman/ck7avopr400px1ilc7j49bi6j', # duplicate entry
}

MAP_ID = "map-id"
BASE_LAYER_ID = "base-layer-id"
BASE_LAYER_DROPDOWN_ID = "base-layer-drop-down-id"
SITE_DETAILS2 = "site-details-selection"
USER_POINT = 'user_point'
QUERY_STATUS = 'query_status'
LINKS='site-links-section'
POP_GRAPH = 'pop-graph'
POP_FIELDS = []
for i in range(1,6):
    POP_FIELDS.append([f'ssp{i}{x}' for x in range(2020,2051,5)])

NEW_INDEX = list(range(2020,2051,5))
SSPS = [f'SSP{x}' for x in range(1,6)]

SSPS_LABELS = {
    'SSP1':'Sustainability',
    'SSP2':'Middle of the Road',
    'SSP3':'Regional Rivalry',
    'SSP4':'Inequality',
    'SSP5':'Fossil-fueled development'
}
def get_style(feature):
    return dict()
def get_d_style(feature):
    return dict(fillColor='orange', weight=2, opacity=1, color='white')

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

# load wells
wells = dl.GeoJSON(
    url='/assets/wells_tds.geojson',
    id = {'type':'json_theme','index':'geojson_wells'},
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={'radius': 75},
    hoverStyle=dict(weight=5, color='#666', dashArray=''),
)

# load weather file
weather_stations = dl.GeoJSON(
    url='/assets/global_weather_file.geojson',
    id = {'type':'json_theme','index':'geojson_weather'},
    cluster=True,
    zoomToBoundsOnClick=True,
    superClusterOptions={'radius': 74},
    hoverStyle=dict(weight=5, color='#666', dashArray=''),
)

# regulatory layer from Mapbox
regulatory = dl.TileLayer(url=mapbox_url.format(id = 'gyetman/ckbgyarss0sm41imvpcyl09fp', access_token=mapbox_token))

# us Counties for population projections
classes = [-50,-25,-5,5,25,50,295]
#colorscale = ['#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026']
colorscale = ["#2166ac","#67a9cf","#d1e5f0","#f7f7f7","#fddbc7","#ef8a62","#b2182b"]
style = dict(weight=1, opacity=.5, color='white', dashArray='3', fillOpacity=0.9)
ctg = ["{}%".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}%".format(classes[-1])]
colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30, position="bottomleft")
# Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
    return style;
}""")

pop_projections = dl.GeoJSON(
    url="/assets/us_county.geojson",  # url to geojson file
    options=dict(style=style_handle),  # how to style each polygon
    zoomToBounds=True,  # when true, zooms to bounds when data changes (e.g. on load)
    zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
    hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),  # style applied on hover
    hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp="pop_change_percent"),
    id="pop-projections"
)

# # California water use
wclasses = [25,50,100,250]
wcolorscale = ['#f1eef6', '#bdc9e1','#74a9cf', '#2b8cbe'] #'#045a8d'
wstyle = dict(weight=1, opacity=.5, color='white', dashArray='3', fillOpacity=0.9)
wctg =["{} mgd".format(cls, wclasses[i + 1]) for i, cls in enumerate(wclasses[:-1])] + ["{} mgd".format(wclasses[-1])]
wcolorbar = dlx.categorical_colorbar(categories=wctg, colorscale=wcolorscale, width=300, height=30, position="topright")
# # Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
    return style;
}""")

water_use = dl.GeoJSON(
    url="/assets/ca_ag_water.geojson",  # url to geojson file
    options=dict(style=style_handle),  # how to style each polygon
    zoomToBounds=True,  # when true, zooms to bounds when data changes (e.g. on load)
    zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
    hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),  # style applied on hover
    hideout=dict(colorscale=wcolorscale, classes=wclasses, style=wstyle, colorProp="TEST"),
    id="wgeojson"
)


# placeholder for mouseover data
info = html.Div(children='',
                className="mapinfo",
                style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000", "background": "lightgrey"},
                id="info")

map_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Home", href='/home')),
              #dbc.NavItem(dbc.NavLink("Site Selection"), active=True)],
              dbc.NavItem(dbc.NavLink("Site Selection"))],
    brand='Site Selection',
    color='primary',
    dark=True,
    sticky='top',
    # style={'margin-bottom':20}
)

legend = html.Img(
    id='legend',
    src='assets/legend_update2.png'
)

query_status = dcc.Loading(
    id=QUERY_STATUS,
    type='default',
    color='#ffff', 
    style={"position": "absolute", "top": "200px", "right": "50%", "zIndex": "1000"},
)

site_selection_map = dl.Map(
    id=MAP_ID, 
    style={'width': '100%', 'height': '500px'}, 
    center=[40.25,-97.05], 
    zoom=4,
    children=[
        dl.TileLayer(
            id=BASE_LAYER_ID, 
            tileSize=512,
            zoomOffset=-1,
        ),
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
    ])

radios = dbc.FormGroup([
    dbc.RadioItems(
        id='theme-dropdown',
        options=[{'label':'Canals', 'value':'canals'},
                    {'label':'Power Plants', 'value':'pplants'},
                    {'label':'Desalination Plants', 'value':'desal'},
                    {'label':'Water Wells', 'value':'wells'},
                    {'label': 'Regulatory', 'value':'regulatory'}, 
                    {'label': 'Weather Stations', 'value':'weather'},
                    {'label': 'Projected Population Change to 2050','value':'pop_projections'},
                    {'label': 'CA Agricultural Water Use','value':'water_use'},
        ],               
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

def render_map():
    return [
        map_navbar,
        dbc.Row([
            dbc.Col([
                query_status,
                site_selection_map,
                dbc.Row([
                    dbc.Col([radios,html.Div(id='next-button'),],width=9),
                    dbc.Col(legend)
                ]),
            ],width=8),
            dbc.Col([
                html.H3('Site details:', className='text-success'),
                html.Div(id=POP_GRAPH),
                html.Div(id=SITE_DETAILS2),
                html.Div(id=LINKS)
            ]),
        ],style={'padding':30}),
    ]


theme_ids = {
    'canals': html.Div([canals]),
    'pplants': html.Div([power_plants, info]),
    'desal': html.Div([desal, info]),
    'wells': html.Div([wells, info]),
    'regulatory': regulatory,
    'weather': html.Div([weather_stations, info]),
    'pop_projections': ([pop_projections,colorbar]),
    'water_use': ([water_use,wcolorbar])
}

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

@app.callback([
        Output(SITE_DETAILS2, 'children'),
        Output("closest-facilities", 'children'),
        Output(QUERY_STATUS, 'children'),
        Output(LINKS, 'children'),
        Output('session', 'data'),
    ],
    [Input(MAP_ID, 'click_lat_lng')],
    prevent_initial_call=True)

def get_point_info(lat_lng):
    # prevent_initial_call not working, not sure why
    if lat_lng is None:
        return None, [None,None,None,None], None, None, None
    ## Temporarily returning closest to store in session! 
    markdown, links = pointLocationLookup.lookupLocation(lat_lng)
    markdown = dcc.Markdown(markdown)
    #markdown = pointLocationLookup.lookupLocation(lat_lng)
    # print(f'Links: {links}')
    emd = lookup_openei_rates.lookup_rates(lat_lng[0],lat_lng[1])
    if emd:
        links.append(emd)
        
    closest = pointLocationLookup.getClosestInfrastructure(lat_lng)
    if not closest:
        return markdown, [None,None,None,None], None, links, None
    elif 'plant' in closest.keys():
        desal = dl.Polyline(positions=[lat_lng,closest['desal']], color='#FF0000', children=[dl.Tooltip("Desal Plant")])          
        plant = dl.Polyline(positions=[lat_lng,closest['plant']], color='#ffa500', children=[dl.Tooltip("Power Plant")])
        canal = dl.Polyline(positions=[lat_lng,closest['canal']], color='#add8e6', children=[dl.Tooltip("Canal/Piped Water")])
        water = dl.Polyline(positions=[lat_lng,closest['water']], color='#000000', children=[dl.Tooltip("Water Network Proxy")])
        return markdown, [desal,plant,canal,water], None, links, closest
    elif 'desal' in closest.keys():
        desal = dl.Polyline(positions=[lat_lng,closest['desal']], color='#FF0000', children=[dl.Tooltip("Desal Plant")])
        return markdown, [desal,None,None,None], None, links, closest
    else:
        return markdown, [None,None,None,None], None, links, closest

        
@app.callback(
    Output(component_id='next-button',component_property='children'),
    [Input(component_id=SITE_DETAILS2,component_property='children')],
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
                dbc.Button('Select Models', color="primary",
                        href='http://127.0.0.1:8077/model-selection'), 
            ], className='row',
            ) 
        )


@app.callback(Output('info', 'children'),
        [Input({'type':'json_theme', 'index': ALL}, 'hover_feature')]
    )
def info_hover(features):
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
            name = feature['properties']['name']
            tds = feature['properties']['TDS']
            if not tds:
                tds = '-'
            else:
                tds = round(tds,1)
            depth = feature['properties']['DEPTH']
            if not depth:
                depth = '-'
            else:
                depth = round(depth,1)
            # todo, get this dynamically
            depth_units = 'feet'
            temperature = feature['properties']['TEMP']
            units = 'mg/L'
            temp_units = 'C'
            if all((temperature, tds)):
                return header + [html.B(name), html.Br(),
                    f"TDS: {tds:,} {units}", html.Br(), 
                    f"Depth: {depth} ft", html.Br(),
                    f"Temperature: {temperature:.1f} {temp_units}" ]
            elif(temperature):
                return header + [html.B(name), html.Br(),
                f"TDS: - {units}", html.Br(),
                f"Temperature: {temperature:.1f} {temp_units}"]
            elif(tds):
                return header + [html.B(name), html.Br(),
                f"TDS: {tds:,} {units}", html.Br(), 
                f"Depth: {depth} ft", html.Br(),
                f"Temperature: - {temp_units}"]
        elif 'City' in feature['properties'].keys():
            header = ['Weather Station', html.Br()]
            name = feature['properties']['City']
            return header + [name]

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


@app.callback(
    Output(POP_GRAPH,'children'),
    [Input(component_id='pop-projections',component_property='hover_feature')]
)

def plot_pop_projection(feature):
    if feature:
        ## get the info and turn it into a dataframe
        pop_df = pd.DataFrame(feature['properties'], index=[0])
        ssps = pop_df[POP_FIELDS[0]].transpose()
        ssps.rename(columns={ssps.columns[0]: 'SSP1'}, inplace=True)
        ssps.index = NEW_INDEX
        for i in range(2,6):
            tmp = pop_df[POP_FIELDS[i-1]].transpose()
            tmp.rename(columns={tmp.columns[0]: f'SSP{i}'}, inplace=True)
            tmp.index = NEW_INDEX
            ssps = ssps.join(tmp)

        ## make the graph and return it

        fig = go.Figure()
        fig.update_layout(
            title='Shared Socioecomic Pathways Population Projections',
            xaxis_title = 'Year',
            yaxis_title= 'County Population',
            legend = dict(
                yanchor="bottom",
                y=-1,
                xanchor="left",
                x=0.01
            )
        )
        for ssp in SSPS:
            fig.add_trace(go.Scatter(
                x = list(ssps.index),
                y = list(ssps[ssp]),
                mode = 'lines',
                name = f'{ssp}: {SSPS_LABELS[ssp]}'
            ))
        return(dcc.Graph(figure=fig))
    else:
        return None

external_stylesheets = [dbc.themes.FLATLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Site Selection (Beta)'

# register_map(app)

if __name__ == '__main__':
    app.run_server(debug=False, port=8150)

