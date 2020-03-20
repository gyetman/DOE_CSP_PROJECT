import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import plotly.graph_objs as go
import numpy as np

CENTER_LAT=32.7767
CENTER_LON=-96.7970

# TODO: add code for user-selected point, 
# then dump TDS value for use in software. 

external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_key = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'
app = dash.Dash(__name__, external_stylesheets=external_stylesheet)

# load well data
df = pd.read_csv('./GISData/dissolved_solids.csv')
df['text'] = df['TDS_mgL'].round(1).astype(str) + ' mg/L'

# TODO: add waste heat for power plants from Jason's data
# 
# TODO: add plant names

# load county attributes
df_county = pd.read_csv('./GISData/county_tds.csv')
df_county['text'] = df_county['TDS_mgL'].round(1).astype(str) + ' mg/L'

# load desal plants
df_desal = pd.read_csv('./GISData/desal_plants.csv')
df_desal['text'] = 'Capacity: ' + df_desal['Capacity_m3_d'].astype(str) + ' m3/day'

# load power plants
df_power = pd.read_csv('./GISData/power_plants_energy.csv')
df_power['text'] = 'Plant Type: ' + df_power['Plant_prim']


#load geoJSON geometries for county data (average TDS)
with open('./gisData/county_tds.geojson','r') as f:
    geoj = json.load(f)

userPoint = go.Scattermapbox(
    name='Selected Site',
    lat=[0],
    lon=[0],
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

wellLocation = go.Scattermapbox(
    name='Well Location',
    lat=df.dec_lat_va,
    lon=df.dec_long_va,
    mode='markers',
    hoverinfo='text',
    text=df_county.text,
    marker=dict(
        size=5,
    ),
    visible=False
    # TODO: duplicate this layer to have cutoffs:
    # 5,000
    # 10,000
    # 20,000

)


desalLocation = go.Scattermapbox(
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


plantLocation = go.Scattermapbox(
    name='Power Plants',
    lat=df_power.Plant_lati,
    lon=df_power.Plant_long,
    mode='markers',
    hoverinfo='text',
    text=df_power.text,
    #marker = go.scattermapbox.Marker(
    #    symbol='industry',
    #),
    marker=dict(
        size=9,
        color='green',
    ),
    visible=True
    # TODO: filter to show only coal, gas & nuclear
    
)

tdsData = go.Choroplethmapbox(
    name='Mean TDS',
    geojson=geoj, 
    locations=df_county.IDField, 
    # featureidkey='ZCTA5CE10',
    z=df_county.TDS_mgL,
    colorscale="Viridis", 
    colorbar=dict(
        title='Average TDS mg/L',
    ),
    marker_opacity=1, 
    marker_line_width=0,
    #hoverinfo='skip',
    text=df.text,
    visible=True,
    )

data = [tdsData,wellLocation,plantLocation,desalLocation,userPoint] # sets the order

layout = go.Layout(
    height=600,
    width=900,
    autosize=True,
    #hovermode='closest',
    #clickmode='text',
    title='Average TDS per county and Well Location Data',
    showlegend=True,
    legend_orientation='h',
    uirevision='Change to reload whole map',
    mapbox=dict(
            accesstoken=mapbox_key,
            zoom=5,
            center=dict(
                lat=CENTER_LAT,
                lon=CENTER_LON
            ),
    )
)

# placeholder for output text
markdownText = '''

'''

fig = go.Figure(dict(data=data, layout=layout))
app.title = 'Produced Waters'
app.layout = html.Div(children=[
    html.Div([
        html.Div([
            html.H3(children='Site Exploration and Selection'),
             dcc.Graph(
                id='map', figure=fig
            )], className='row'
        ),
        html.Div([
            html.Div(id='callback-div'),
            dcc.Markdown(children=markdownText)
            ], className='row'
        )

    ], className='row'),
    html.Div([
        html.Div(id='next-button'),
        dcc.Link(html.Button('Select Models'), href='http://127.0.0.1:8073/model-selection')
    ], className='row'
    )

])

# TODO:
# add texas specific data on plant capacity, type, etc. 

@app.callback(
    Output(component_id='callback-div', component_property='children'),
    [Input(component_id='map', component_property='clickData')]
)
def output_site_attributes(clicks):
    # grab the attributes to show in the click data in the second div
    if clicks is None:
        print('empty click')
        raise PreventUpdate
    if 'points' not in set(clicks.keys()):
        print(clicks.keys())
        raise PreventUpdate
    else:
        ptDict = clicks['points'][0]
        ptKeys = ptDict.keys()
        #print(type(ptDict))
        #for key, value in ptDict.items():
        #    print('{}: {}'.format(key, value))

        if 'location' in ptKeys:

            ptID = ptDict['location']
            countyName = df_county.loc[df_county.IDField == ptID]['NAME'].values[0]
            avgTDS = df_county.loc[df_county.IDField == ptID]['TDS_mgL'].values[0]
            avgPH = df_county.loc[df_county.IDField == ptID]['ph'].values[0]

            mdText = "###### Produced Water Measurements for {} County, ST\n\n".format(countyName)
            mdText += 'Source: USGS Produced Waters Database\n\n'
            mdText += 'Average TDS: {:,.0f} mg/L\n\n'.format(avgTDS)
            mdText += 'Average PH: {:0.1f}\n\n'.format(avgPH)
            return(dcc.Markdown(mdText))
        # handle point clicks
        else:
            if 'Capacity' in ptDict['text']:
                print(ptDict.keys())
                for key, value in ptDict.items():
                    print('{}: {}'.format(key,value))
                #ptID = ptDict['curveNumber']
                #plantName = df_power[ptID]['Plant_name']
                #plantFuel = df_power[ptID]['Plant_prim']
                #plantCapacity = df_power[ptID]['Plant_annu']
                #wasteHeat = df_power[ptID]['Total_Pote']

                #mdText = '###### Details for Power Plant {}\n\n'.format(plantName)
                #mdText += 'Fuel Type: {}\n\n'.format(plantFuel)
                #mdText += 'Annual Capacity: {} <units>\n\n'.format(plantCapacity)
                #mdText += 'Potential Waste Heat: {} <units>\n\n'.format(wasteHeat)

                #return(dcc.Markdown(mdText))

            elif 'Plant Type' in ptDict['text']:
                print(ptDict.keys())
                #ptID = ptDict['curveNumber']
                #plantName = df_desal['Project_name']
                #mdText = '###### Details for Desalination Plant {}\n\n'.format(plantName)

                #return(dcc.Markdown(mdText))






# TODO: add callback for layer visibility
# add callback for point attributes
@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input(component_id='map', component_property='config')],
    [State(component_id='map', component_property='relayoutData')]
)
def updateDisplay(restyleData,relayoutData):
    print(relayoutData)
    print(restyleData)
    # update display if zoom level tripped and map not already visible
    if not relayoutData:
        raise PreventUpdate
    else:
        print(relayoutData)
        print(restyleData)
        # TODO: pull zoom level from relayData and update map if 
        # passing zoom level X AND layer is not already on! 
"""         if relayData['mapbox.zoom'] <= 5 and not relayData['']wellLocation.visible:
            wellLocation.visible = True
            wellLocation = go.Scattermapbox(
                name='Well Location',
                lat=df.dec_lat_va,
                lon=df.dec_long_va,
                mode='markers',
                hoverinfo='text',
                text=df_county.text,
                marker=dict(
                    size=5,
                ),
                visible=True
            )
            return(
                (go.Figure(data=[tdsData,wellLocation,plantLocation,desalLocation,userPoint],layout= layout))
            )

        elif relayData['mapbox.zoom'] > 5 and wellLocation.visible:
            wellLocation.visible = False
            #return new map, keep zoom & zoom
        else:          
            raise PreventUpdate
"""

if __name__ == '__main__':
    app.run_server(debug=True, port=8058)
    