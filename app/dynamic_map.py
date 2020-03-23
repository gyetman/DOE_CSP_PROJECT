
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# texas as default location
CENTER_LAT=32.7767
CENTER_LON=-96.7970

markdownText = '\n\n'
external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_key = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'
app = dash.Dash(__name__, external_stylesheets=external_stylesheet)

# load point mesh data with pre-calculated attributes
df = pd.read_csv('./GISData/solar_sw.csv')
solar = go.Scattermapbox(
    name='solar',
    lat=df.CENTROID_Y,
    lon=df.CENTROID_X,
    mode='markers',
    hoverinfo=None,
    #hovertext=df.ID,
    marker=dict(
        size=0,
        color='green',
    ),
    visible=True,
    showlegend=False,
)

# load county polygons and dataframe of attributes
with open('./GISData/counties.geojson','r') as f:
    counties = json.load(f)

df_county = '' #TODO

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
        color='red',
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
data = [solar,desal,userPoint]

dropDownOptions = [
    {'label':'Solar Resource', 'value':'solar'},
    {'label':'Electricity Prices', 'value':'price'},
    {'label':'Produced Waters','value':'produced'},
    {'label':'Brackish Waters', 'value':'brackish'},
    {'label':'Legal Framework', 'value':'legal'}
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
                'min-width': '150px'
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
        )

    ], className='row'),
    html.Div([
        html.Div(
        dcc.Link(html.Button('Select Models'), 
        href='http://127.0.0.1:8073/model-selection', 
        id='next-button'),
        )
    ], className='row'
    )

])

def loadData(mapTheme,fg):
    ''' loads data based on the chosen theme after a user selects a 
    different theme from the dropdown '''
    # keep existing user point 
    # always the layer on top (last)
    userPt = fg['data'][-1]
    print(userPt)
    newData = []
    if mapTheme == 'solar':
        newData.append(solar)
        newData.append(desal)
        newData.append(userPt)    
        return newData
    elif mapTheme == 'price':
        # display the counties by price
        # load water price point data (global)
        df_point_prices = pd.read_csv('./gisData/global_water_cost_pt.csv')
        df_point_prices['text'] = '$' + df_point_prices['Water_bill'].round(2).astype(str) + '/m3'
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
            text=df_county_prices.text,
            hoverinfo='text',
            visible=True,
            # TODO: add year to map GUI (year of data)
        )
        newData.append(countyData)
        newData.append(solar)
        newData.append(userPt)
        return newData

    elif mapTheme == 'produced':
        newData.append(solar)
        newData.append(userPt)
        return newData
    elif mapTheme == 'brackish':
        newData.append(solar)
        newData.append(userPt)
        return newData
    elif mapTheme == 'legal':
        newData.append(solar)
        newData.append(userPt)
        return newData
    

    
    
""" callback to handle click events. Capturing map info with the click 
event (figure, relayoutData) for clicks that are not close enough to a 
point (zoomed in too far). """
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
    if dropDown:
        ''' if the dropdown is not the same as the title text, 
        we need to reload the map with the new choice. Dropdown
        is supplied with callback regardless of status (updated
        or not)'''
        existingTitle = figure['layout']['title']['text']
        if existingTitle != dropDownTitles[dropDown]:
            print('Dropdown Changed to {}'.format(dropDown))
            # change title and load appropriate data
            figure['layout']['title']['text'] = dropDownTitles[dropDown]
            # update data and return a go.Figure! 
            return (go.Figure(dict(data=loadData(dropDown,figure),layout = figure['layout'])))
    if clicks:
        # update he user point 
        tmpData = figure['data']
        pt = tmpData[-1]
        tmpData = tmpData[:-1]
        print(type(tmpData))
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


# callback to update Markdown text
@app.callback(
    Output(component_id='markdown-div',component_property='children'),
    [Input(component_id='map',component_property='clickData')] 
)
def updateMarkdown(clicks):
    ''' pulls properties from dataframe and updates markdown div '''
    if clicks is None:
        raise PreventUpdate
    markdownText = '###### Site Properties in {}, {}\n\n'.format('County','State')
    return dcc.Markdown(markdownText)

if __name__ == '__main__':
    app.run_server(debug=True, port=8058)    
    
    
    