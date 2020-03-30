
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import helpers
from pathlib import Path
import app_config as cfg 


#TODO:
# 1. update to use paths from app_config.py
# 2. Update content with more detailed solar data
# 3. Test using lookup function / caches for faster loading

# texas as default location
CENTER_LAT=32.7767
CENTER_LON=-97.7970

markdownText = '\n\n'
external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_key = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'
app = dash.Dash(__name__, external_stylesheets=external_stylesheet)

# load solar geojson
with open('./GISData/solar_resources3.geojson','r') as f:
    solarGeoJson = json.load(f)
# load data frame of solar values

df_solar = pd.read_csv('./GISData/solar_data.csv',usecols=['ID','ANN_DNI','CENTROID_X','CENTROID_Y'])
df_solar['text'] = 'DNI: ' + df_solar['ANN_DNI'].round(1).astype(str)

solarViz = go.Choroplethmapbox(
    name='Solar Resource',
    geojson=solarGeoJson, 
    locations=df_solar.ID, 
    z=df_solar['ANN_DNI'],
    colorscale='Inferno', 
    colorbar=dict(
        title='kWh/m2/day',
    ),
    marker_opacity=1, 
    marker_line_width=0,
    #text = df_solar['text'],
    #hoverinfo='text',
    hoverinfo='none',
    visible=True,
)


# load point mesh data with pre-calculated attributes
df = pd.read_csv('./GISData/solar_sw.csv')
df['text'] = 'DNI: ' + df_solar['ANN_DNI'].round(1).astype(str)
solar = go.Scattermapbox(
    name='solar',
    lat=df.CENTROID_Y,
    lon=df.CENTROID_X,
    mode='markers',
    hoverinfo='text',
    text=df.text,
    marker=dict(
        size=0,
        color='red',
    ),
    visible=True,
    showlegend=False,
)

# load county polygons and dataframe of attributes
#with open('./GISData/counties.geojson','r') as f:
#    counties = json.load(f)

#df_county = '' #TODO

# load existing desal plants

df_desal = pd.read_csv('./GISData/desal_plants.csv')
df_desal['text'] = 'Capacity: ' + df_desal['Capacity_m3_d'].astype(str) + ' m3/day'
desal = go.Scattermapbox(
    name='Desalination Plants',
    lat=df_desal.Latitude,
    lon=df_desal.Longitude,
    mode='markers',
    hoverinfo='text',
    text=df_desal.text,
    marker=dict(
        size=7,
        color='green',
    ),
    visible=True
    # TODO: duplicate this layer to have cutoffs:
    # 5,000
    # 10,000
    # 20,000
    
)
# user-point placeholder
userPoint = go.Scattermapbox(
    name='Selected Site',
    lon=[0],
    lat=[0],
    # replaced None object with 'none', confusing but that turns it off!  
    hoverinfo='none',
    mode='markers',
    marker=dict(
        size=13,
        color='red',
    ),
    showlegend=False,
    visible=False,
)

layout = go.Layout(
    #height=600,
    #width=900,
    autosize=True,
    #hovermode='closest',
    #clickmode='text',
    title='Solar Resource', # default value in dropdown
    showlegend=True,
    legend_orientation='h',
    uirevision='initial load',
    mapbox=dict(
            accesstoken=mapbox_key,
            zoom=5,
            center=dict(
                lat=CENTER_LAT,
                lon=CENTER_LON
            ),
    )
)

# data object for the figure
data = [solarViz,solar,desal,userPoint]

dropDownOptions = [
    {'label':'Solar Resource', 'value':'solar'},
    {'label':'Water Prices', 'value':'wprice'},
    {'label':'Electric Prices', 'value':'eprice','disabled':True},
    {'label':'Produced Waters','value':'produced'},
    {'label':'Brackish Waters', 'value':'brackish','disabled':True},
    {'label':'Legal Framework', 'value':'legal','disabled':True}
]
# lookup used in callback
dropDownTitles = dict()
for opt in dropDownOptions:
    dropDownTitles[opt['value']] = opt['label']

fig = go.Figure(dict(data=data, layout=layout))
app.title = 'Site Selection'

app.layout = html.Div(children=[
        html.Div([
            dcc.Dropdown(
            id='select-map',
            options = dropDownOptions,
            value='solar',
            className='row',
            clearable=False,
            persistence=True,
            persistence_type='session',
            style= {
                'position': 'relative',
                'display': 'inline-block',
                'min-width': '160px'
            }
        ),
        html.Div([
            html.H3(children='Site Exploration and Selection'),
             dcc.Graph(
                id='map', figure=fig
            )], className='row'
        ),
        html.Div([
            html.Div(id='markdown-div'),
            dcc.Markdown(children=markdownText)
            ], className='row'
        ),

        html.Div([
            html.Div(
            html.A(
                html.Button('Select Models', 
                    #href='http://127.0.0.1:8077/model-selection', 
                    id='next-button',
                ),
            href='http://127.0.0.1:8077/model-selection'
            )   
            )
        ], className='row'
        )
]
    )])


def loadData(mapTheme,fg):
    ''' loads data based on the chosen theme after a user selects a 
    different theme from the dropdown '''
    # keep existing user point 
    # always the layer on top (last)
    userPt = fg['data'][-1]

    if mapTheme == 'solar':   
        ''' default loaded data can be returned, with user point'''
        # update visibility
        solar.hoverinfo='text'
        return [solarViz,solar,desal,userPt]
    elif mapTheme == 'wprice':
        # turn hoverinfo off
        solar.hoverinfo='none'
        # display the counties by price
        # load water price point data (global)
        df_point_prices = pd.read_csv('./gisData/global_water_cost_pt.csv')
        df_point_prices['text'] = 'City Price: $' + df_point_prices['Water_bill'].round(2).astype(str) + ' /m3'
        globalPriceData = go.Scattermapbox(
            #text=df_point_prices['City_Name'],
            name='City Prices',
            lat=df_point_prices.Latitude,
            lon=df_point_prices.Longitude,
            text=df_point_prices.text,
            hoverinfo='text',
            visible=True,
            showlegend=True,
            mode='markers',
            marker=dict(
                color=df_point_prices.Water_bill,
                size=9,
            )
        )
        
        #load geoJSON geometries for price data
        with open('./gisData/tx_county_water_prices.geojson','r') as f:
            geoj = json.load(f)
        # load data frame of prices
        # TODO: only load fields that we need! 
        df_county_prices = pd.read_csv('./gisData/tx_county_water_price.csv')
        df_county_prices['text'] = '$' + df_county_prices['Max_Water_Price_perKgal_Res'].round(2).astype(str) + '/Kgal'
        countyData = go.Choroplethmapbox(
            name='County Water Prices (residential)',
            geojson=geoj, 
            locations=df_county_prices.ID, 
            z=df_county_prices.Max_F5000gal_res_perKgal,
            colorscale="Viridis", 
            colorbar=dict(
                title='Price $/Kgal',
            ),
            marker_opacity=1, 
            marker_line_width=0,
            text=df_county_prices['text'],
            hoverinfo='text',
            visible=True,
            # TODO: add year to map GUI (year of data)
        )
        # load canal data
        df_canals = pd.read_csv('./gisData/canals.csv')
        with open('./gisData/canals.geojson','r') as f:
            canalGeoJson = json.load(f)
        canalData = go.Choroplethmapbox(
            name='Canals and Aqueducts',
            geojson=canalGeoJson, 
            locations=df_canals.IDField, 
            z=df_canals['IDField'],
            colorscale='Inferno', 
            text=df_canals['Name'],
            hoverinfo='text',
            visible=True,
            showscale=False,
            showlegend=True
        )
        return [countyData,solar,globalPriceData,canalData,userPt]

    elif mapTheme == 'eprice':
        # turn hoverinfo off
        solar.hoverinfo='none'
        # load electric price data
        df_electric = pd.read_csv('./GISData/electric_prices_zcta.csv')
        df_electric['text'] = '$' + df_electric['MEAN_ind_rate'].round(3).astype(str) + '/kWh'
        #load geoJSON geometries for price data (zip codes)
        with open('./gisData/zcta.geojson','r') as f:
            geoj = json.load(f)
        electricPriceData = go.Choroplethmapbox(
            name='Industrial Electric Prices',
            geojson=geoj, 
            locations=df_electric.ZCTA5CE10, 
            z=df_electric.MEAN_ind_rate,
            colorscale="Viridis", 
            colorbar=dict(
                title='Price $/kWH',
            ),
            marker_opacity=1, 
            marker_line_width=0,
            text=df_electric.text,
            hoverinfo='text',
            visible=True,
        )
        return [electricPriceData,solar,userPt]

    elif mapTheme == 'produced':
    # turn hoverinfo off
        solar.hoverinfo='none'
        return [solar,userPt]
    elif mapTheme == 'brackish':
    # turn hoverinfo off
        solar.hoverinfo='none'
        return [solar,userPt]
    elif mapTheme == 'legal':
    # turn hoverinfo off
        solar.hoverinfo='none'
        return [solar,userPt]
    

    
""" callback to handle click events and dropdown changes. Capturing map 
info with the click event (figure, relayoutData) for clicks that are 
not close enough to a point (zoomed in too far). """
@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input(component_id='map', component_property='clickData'),
    Input(component_id='select-map', component_property='value')],
    [State('map','relayoutData'),
    State('map','figure')]
)
def clickPoint(clicks,dropDown,relay,figure):
    if not any([clicks,dropDown,relay,figure]):
        # not sure this is a required check here, but in 
        # callbacks with fewer outputs it prevents an error
        # on load. 
        #print('no objects')
        raise PreventUpdate
    # clicked close enough to a point
    #if dropDown:
    ''' if the dropdown is not the same as the title text, 
    we need to reload the map with the new choice. Dropdown
    is supplied with callback regardless of status (updated
    or not)'''
    existingTitle = figure['layout']['title']['text']
    if existingTitle != dropDownTitles[dropDown]:
        # change title and load appropriate data
        figure['layout']['title']['text'] = dropDownTitles[dropDown]
        # update data and return a go.Figure! 
        return (go.Figure(dict(data=loadData(dropDown,figure),layout = figure['layout'])))
    if clicks:
        # update he user point 
        tmpData = figure['data']
        pt = tmpData[-1]
        tmpData = tmpData[:-1]
        pt['visible'] = True
        pt['showlegend'] = True
        pt['lon'] = [clicks['points'][0]['lon']]
        pt['lat'] = [clicks['points'][0]['lat']]
        #figure['data'] = tmpData
        tmpData.append(pt)
        return go.Figure(dict(data=tmpData, layout=figure['layout']))

    if relay:
        #print(relay)
        raise PreventUpdate
    if fig:
        #print(fig.keys())
        raise PreventUpdate


def createMarkdown(mddf,theme):
    ''' helper method to return the markdown text relevant for the given 
    map theme '''
    print('create md called')
    # markdown used with all themes
    mdText = '###### Site Properties in {}, {}\n\n'.format(mddf.CountyName[0],mddf.StatePosta[0])
    if theme not in dropDownTitles.keys():
        print('Bad dropdown value!')
        return markdownText
    mdText += 'Hellooooo\n\n'
    return(mdText)


# callback to update Markdown text
@app.callback(
    Output(component_id='markdown-div',component_property='children'),
    [Input(component_id='map',component_property='clickData')],
    [State('map','figure')] 
)
def updateMarkdown(clicks,fig):
    ''' pulls properties from dataframe and updates markdown div '''
    if clicks is None:
        print('no clicks')
        raise PreventUpdate
    userPt = fig['data'][-1]
    if userPt['lat'][0] == 0:
        raise PreventUpdate
    else:
        print('creating data frame')
        dfTmp = df.loc[(df['CENTROID_Y'] == userPt['lat'][0]) & (df['CENTROID_X'] == userPt['lon'][0])]
        theme = fig['layout']['title']['text']
        markdownText = createMarkdown(dfTmp,theme)
    
    return dcc.Markdown(markdownText)

def paramHelper(dfAtts):
    ''' helper method to write out parameters. Uses the solar dataframe point ID 
    to write out map paramers to  '''
    #TODO: initialize the map-data json and write all params (read and update?)
    print('getting params')
    mParams = dict()
    # update dictionary
    weatherPath = cfg.base_path
    mParams['file_name'] = str(weatherPath / 'SAM_flatJSON' / 'solar_resource' / dfAtts.filename.values[0])
    mParams['county'] = dfAtts.CountyName.values[0]
    mParams['state'] = dfAtts.StatePosta.values[0]
    mParams['water_price'] = '2.08'
    mParams['water_price_res'] = dfAtts.Avg_F5000gal_res_perKgal.values[0]
    mParams['latitude'] = dfAtts.CENTROID_Y.values[0]
    mParams['dni'] = dfAtts.ANN_DNI.values[0]
    mParams['ghi'] = dfAtts.GHI.values[0]

    # update json file
    helpers.json_update(mParams,'./map-data.json')

# callback for model selection button click
@app.callback(
    Output(component_id='next-button',component_property='children'),
     [Input(component_id='next-button',component_property='n_clicks')],
     [State('map','figure')]
 )
def writeOutParams(btn,mapFigure):
    userPt = mapFigure['data'][-1]
    if userPt['lat'][0] == 0:
        raise PreventUpdate
    else:
        dfTmp = df.loc[(df['CENTROID_Y'] == userPt['lat'][0]) & (df['CENTROID_X'] == userPt['lon'][0])]
        paramHelper(dfTmp)
    
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True, port=8058)    
    
    
    