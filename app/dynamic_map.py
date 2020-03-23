
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
    newData = [solar]
    if mapTheme == 'solar':
        #default, no need to change
        newData.append(desal)
        newData.append(userPt)    
        return newData
    elif mapTheme == 'price':
        # display the counties by price
        # load water price point data (global)
        df_point_prices = pd.read_csv('./gisData/global_water_cost_pt.csv')
        df_point_prices['text'] = '$' + df_point_prices['Water_bill'].round(2).astype(str) + '/m3'
        newData.append(userPt)
        return newData
    elif mapTheme == 'produced':
        newData.append(userPt)
        return newData
    elif mapTheme == 'brackish':
        newData.append(userPt)
        return newData
    elif mapTheme == 'legal':
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
        print(dropDown)
        existingTitle = figure['layout']['title']['text']
        if existingTitle != dropDownTitles[dropDown]:
            print('Dropdown Changed')
            # change title and load appropriate data
            figure['layout']['title']['text'] = dropDownTitles[dropDown]
            # TODO: update data and return a go.Figure! 
            return (go.Figure(dict(data=loadData(dropDown,figure),layout = figure['layout'])))
    if clicks:
        # update he user point 
        pt = figure['data'][-1]
        pt['visible'] = True
        pt['showlegend'] = True
        pt['lon'] = [clicks['points'][0]['lon']]
        pt['lat'] = [clicks['points'][0]['lat']]

        # update the figure title, otherwise default of solar is used
        #layout['title']['text'] = dropDownTitles[dropDown]
        # return the figure with the updated point
        return go.Figure(dict(data=[solar,desal,pt], layout=figure['layout']))

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
    
    
    