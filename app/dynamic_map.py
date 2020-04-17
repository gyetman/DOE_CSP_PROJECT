
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
# 1. Update content with more detailed solar data
# 2. Test using lookup function / caches for faster loading

# default location
CENTER_LAT=32.7767
CENTER_LON=-99.7970

# global pandas display option
#pd.options.display.float_format = '{:,.0f}'.format
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
    hoverinfo='none',
    text=df['text'],
    marker=dict(
        size=0,
        color='red',
    ),
    visible=True,
    showlegend=False,
)

# load existing desal plants
df_desal = pd.read_csv('./GISData/desal_plants.csv')
df_desal['text'] = 'Desalination Capacity: ' + df_desal['Capacity_m3_d'].astype(str) + ' m3/day'
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
    visible=True,

    
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

# natural gas power plants
df_ng = pd.read_csv('./GISData/ng.csv')
df_ng['text'] = df_ng.Plant_prim.astype(str).apply(str.title) \
    + ' Residual Heat: ' + df_ng['Exhaust_Re'].map('{:,.0f}'.format) + 'MJ'

ng = go.Scattermapbox(
    name='Natural Gas Plants',
    lat=df_ng.Plant_lati,
    lon=df_ng.Plant_long,
    mode='markers',
    hoverinfo='text',
    text= df_ng.text,
    marker=dict(
        size=7,
        symbol='circle',
    ),
    visible=True,
    showlegend=True,
)

# Nuclear power plants
df_nuclear = pd.read_csv('./GISData/nuclear.csv')
df_nuclear['text'] = df_nuclear.Plant_prim.astype(str).apply(str.title) \
    + ' Concenser heat: ' + df_nuclear['Condenser'].map('{:,.0f}'.format) + ' MJ' 

nuclear = go.Scattermapbox(
    name='Nuclear Plants',
    lat=df_nuclear.Plant_lati,
    lon=df_nuclear.Plant_long,
    mode='markers',
    hoverinfo='text',
    text= df_nuclear.text,
    marker=dict(
        size=7,
        symbol='square',
    ),
    visible=True
)

# Coal power plants
df_coal = pd.read_csv('./GISData/coal.csv')
df_coal['text'] = df_coal.Plant_prim.astype(str).apply(str.title) \
    + ' Residual Heat: ' + df_coal['Exhaust_Re'].map('{:,.0f}'.format)

coal = go.Scattermapbox(
    name='Coal Plants',
    lat=df_coal.Plant_lati,
    lon=df_coal.Plant_long,
    mode='markers',
    hoverinfo='text',
    text=df_coal.text,
    marker=dict(
        #size=7,
        symbol='circle',
    ),
    visible=True,
)

layout = go.Layout(
    #height=600,
    #width=900,
    autosize=True,
    hovermode='closest',
    #clickmode='text',
    title='Solar Resource', # default value in dropdown
    showlegend=True,
    legend_orientation='h',
    uirevision='initial load',
    mapbox=dict(
            accesstoken=mapbox_key,
            zoom=6,
            center=dict(
                lat=CENTER_LAT,
                lon=CENTER_LON
            ),
    )
)

# data object for the figure
data = [solarViz,solar,ng,nuclear,coal,desal,userPoint]

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
            html.Div(id='next-button'),
            
        ], className = 'row',
        )
]
    )])


def loadData(mapTheme,fg):
    ''' loads data based on the chosen theme after a user selects a 
    different theme from the dropdown '''
    # keep existing user point 
    # always the layer on top (last)
    userPt = fg['data'][-1]

    if mapTheme == 'wprice':
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
        return [solar,userPt]
    elif mapTheme == 'brackish':
        return [solar,userPt]
    elif mapTheme == 'legal':
        return [solar,userPt]
    
    elif mapTheme == 'solar':   
        ''' default loaded data can be returned, with user point'''
        # update visibility
        return [solarViz,solar,ng,nuclear,coal,desal,userPt]

    
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

    # if relay:
    #     print(relay)
    #     print(clicks)
    #     print(type(fig))

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

    else:
        raise PreventUpdate


def createMarkdown(mddf,theme):
    ''' helper method to return the markdown text relevant for the given 
    map theme '''
    # TODO: add distance to closest plants
    # markdown used with all themes
    mdText = '##### Site Properties in {} County, {}\n\n'.format(
        mddf.CountyName.values[0],
        mddf.StatePosta.values[0]
    ) 
    mdText += '###### Existing plants nearby\n\nWithin 100km\n\n'
    # TODO
    mdText += 'Closest power plant: {}\n\n'.format(mddf.Plant_prim.values.astype(str)[0].title())
    # TODO: go back to e-grid data and add in plant capacity MW
    #mdText += 'Annual Plant Capacity: {:,.0f}\n\n'.format(mddf.???.values[0])
    mdText += '&nbsp&nbsp Distance: {:,.0f} km\n\n'.format(mddf.PowerPlantDistance.values[0]/1000)
    mdText += '&nbsp&nbsp Exhaust Residual Heat: {:,.0f} MJ (91 C < T < 128 C)\n\n'.format(mddf.Exhaust_Re.values[0])
    mdText += '&nbsp&nbsp Condenser Heat: {:,.0f} MJ (29 C < T < 41 C)\n\n'.format(mddf.Condenser.values[0])

    mdText += 'Closest desalination plant: {}\n\n'.format(mddf.DesalProjName.values[0])
    mdText += '&nbsp&nbsp Distance to plant: {:,.1f} km\n\n'.format(mddf.DesalDist.values[0] / 1000)
    mdText += '&nbsp&nbsp Plant Capacity: {:,.0f} (m3/day)\n\n'.format(mddf.DesalCapacity.values[0])
    mdText += '&nbsp&nbsp Plant Technology: {}\n\n'.format(mddf.DesalTechnology.values[0])
    mdText += '&nbsp&nbsp Plant Feedwater: {}\n\n'.format(mddf.DesalFeedwater.values[0])
    mdText += '&nbsp&nbsp Plant Customer Type : {}\n\n'.format(mddf.DesalCustomerType.values[0])

    if theme not in list(dropDownTitles.values()):
        return mdText
    elif theme == 'Water Prices':
        mdText += '###### Water Price Information\n\n'
        mdText += 'Texas county average price: ${:,.2f}\n\n'.format(mddf.Avg_F5000gal_res_perKgal.values[0])
        mdText += '{} city water price: ${:.2f}\n\n'.format(mddf.WaterUtilityCity.values[0], mddf.WaterPrice.values[0])
        mdText += '&nbsp&nbsp Provider: {}\n\n'.format(mddf.WaterUtilityName.values[0])
        mdText += '&nbsp&nbsp Distance to site: {:,.1f} km\n\n'.format(mddf.WaterPriceDist.values[0] / 1000)
        wnd = mddf.WaterNetworkDistance.values[0]
        if wnd > 0:
            mdText += 'Distance to water network proxy location: {:,.0f} km\n\n'.format(wnd / 1000)
        cnl = mddf.CanalsDist.values[0]
        if cnl > 0:
            mdText += 'Distance to closest Canal: {:,.0f} km\n\n'.format(cnl/1000)
            mdText += '&nbsp&nbspName: {}\n\n'.format(mddf.CanalName.values[0])
            mdText += '&nbsp&nbspOperator: {}\n\n'.format(mddf.CanalOperator.values[0])

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
        raise PreventUpdate
    
    lat = [clicks['points'][0]['lat']]
    lon = [clicks['points'][0]['lon']]
    dfTmp = df.loc[(df['CENTROID_Y'] == lat[0]) & (df['CENTROID_X'] == lon[0])]
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
    # TODO: pull from city or Texas county data
    mParams['water_price'] =  dfAtts.WaterPrice.values[0]
    mParams['water_price_res'] = dfAtts.Avg_F5000gal_res_perKgal.values[0]
    mParams['latitude'] = dfAtts.CENTROID_Y.values[0]
    mParams['dni'] = dfAtts.ANN_DNI.values[0]
    mParams['ghi'] = dfAtts.GHI.values[0]
    mParams['dist_desal_plant'] = dfAtts.DesalDist.values[0] / 1000
    mParams['dist_water_network'] = dfAtts.WaterNetworkDistance.values[0] / 1000
    mParams['dist_power_plant'] = dfAtts.PowerPlantDistance.values[0] / 1000

    # update json file
    helpers.json_update(mParams,'./map-data.json')

# callback for model selection button click
@app.callback(
    Output(component_id='next-button',component_property='children'),
     [Input(component_id='map',component_property='figure')],
     [State('map','figure')]
 )
def writeOutParams(btn,mapFigure):
    userPt = mapFigure['data'][-1]
    if userPt['lat'][0] == 0:
        raise PreventUpdate
    else:
        dfTmp = df.loc[(df['CENTROID_Y'] == userPt['lat'][0]) & (df['CENTROID_X'] == userPt['lon'][0])]
        paramHelper(dfTmp)
        # return the next-model button
        return(
            html.Div([
                html.Div(id='button-div'),
                html.Div(html.A(
                    html.Button('Select Models', 
                            id='model-button',
                        ),
                    href='http://127.0.0.1:8077/model-selection'
                    )  )
            ], className='row',
            ) 
        )        

if __name__ == '__main__':
    app.run_server(debug=True, port=8058)    
    
    
    