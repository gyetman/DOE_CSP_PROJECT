import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# TODO:
# -show both residential & commercial water prices
# -add table on right to show values (use markdown?)
# -update STATE on callback to speed up reload
# -replace geojson of solar square polygons with 
# centroid points (should be faster)
# -add all lookup value / distances to centroids (some added)
# write weather file out to appropriate location for use by model
# replace hard-coded link to model selection with button (?)
# change hard-coded link to "skip site selection" (?)
# IMPORTANT: draw order interferes with click & mouseover events. Figure this out!!!
# TODO: add line features (water network) in California. Line features should be easy
# but the json file is not formatted right, I think. 

CENTER_LAT=32.7767
CENTER_LON=-96.7970

external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_key = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'
app = dash.Dash(__name__, external_stylesheets=external_stylesheet)

# load water price point data (global)
df_point_prices = pd.read_csv('./gisData/global_water_cost_pt.csv')
df_point_prices['text'] = '$' + df_point_prices['Water_bill'].round(2).astype(str) + '/m3'


#df_canals = pd.read_csv('./gisData/canals_update.csv')
#df_
# s['']

# load geoJSON geometries for solar resource (location proxy)
with open('./gisData/solar_resources3.geojson','r') as f:
    geojSolar = json.load(f)
# load the data frame of solar resources
df_solar = pd.read_csv('./gisData/solar_data.csv')

#load geoJSON geometries for price data
with open('./gisData/tx_county_water_prices.geojson','r') as f:
    geoj = json.load(f)

# TODO: only load fields that we need! 
# load matching table for geometries
df_county_prices = pd.read_csv('./gisData/tx_county_water_price.csv')

#TODO: this could be stored statically, not created at run time! 
# formatted Series for hover text
df_county_prices['text'] = '$' + df_county_prices['Max_Water_Price_perKgal_Res'].round(2).astype(str) + '/Kgal'
# solarData is the polygon layer (squares) that are not visible, but used for click events
# note that in testing, if marker_opacity is set to zero, the click events don't seem to be 
# fired! Also, if visible is set to False, the click events are not fired! 
solarData = go.Choroplethmapbox(
    geojson=geojSolar,
    locations=df_solar.ID,
    z=df_solar.ANN_DNI,
    colorscale='Viridis',
    marker_opacity=.00000001,
    marker_line_width=0,
    hoverinfo='none',
    visible=True, # not available for click when this is False
    showscale=False,
)

# canalData = go.Scattermapbox(
#     name='Canals and Aqueducts',    
#     #lon=df_canals.lon_conv.values.tolist(),
#     #lat=df_canals.lat_conv.values.tolist(),
#     lon = [[-117,-116],[-115,-113]],
#     lat=[[33,34],[35,36]],
#     mode = "markers+lines",
#     marker=dict(
#         size=10,
#         color='red',

#     )
    

userPoint = go.Scattermapbox(
    name='Selected Site',
    lat=[0],
    lon=[0],
    # replaced None object with 'none', confusing but that turns it off!  
    hoverinfo='none',
    mode='markers',
    marker=dict(
        size=13,
    ),
    showlegend=False,
    visible=False,

)

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

globalData = go.Scattermapbox(
    #text=df_point_prices['City_Name'],
    name='City Water Prices',
    lat=df_point_prices.Latitude,
    lon=df_point_prices.Longitude,
    text=df_point_prices.text,
    #hoverinfo='none',
    visible=True,
    mode='markers',
    marker=dict(
        color=df_point_prices.Water_bill,
        size=9,
    )
    )

data = [countyData,globalData,solarData,userPoint] # sets the order, I think. 

layout = go.Layout(
    height=600,
    width=800,
    autosize=True,
    #hovermode='closest',
    #clickmode='text',
    title='Maximum Residential Water Price per County; Global City Water Prices',
    showlegend=True,
    legend_orientation='h',
    mapbox=dict(
            accesstoken=mapbox_key,
            zoom=5,
            center=dict(
                lat=CENTER_LAT,
                lon=CENTER_LON
            ),
    )
)

#TODO: figure out how to update markdownText so it's interpreted as such! 
markdownText = '''

 

'''
fig = go.Figure(dict(data=data, layout=layout))
app.title = 'Water Prices'
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


@app.callback(
    Output(component_id='callback-div', component_property='children'),
    [Input(component_id='map', component_property='clickData')]
)
def output_site_attributes(clicks):
    # grab the attributes to show in the click data in the second div
    if clicks is None:
        raise PreventUpdate
    if 'points' not in set(clicks.keys()):
        raise PreventUpdate
    ptID = clicks['points'][0]['location']
    print(clicks)
    print(ptID)
    # TODO: make one temp df and get values from that
    solar = df_solar.loc[df_solar.ID == int(ptID)]['ANN_DNI'].values[0]
    network = df_solar.loc[df_solar.ID == int(ptID)]['Name'].values[0]
    networkOp = df_solar.loc[df_solar.ID == int(ptID)]['Operator'].values[0]
    networkDist = df_solar.loc[df_solar.ID == int(ptID)]['NEAR_DIST'].values[0]/1000
    wxStation = df_solar.loc[df_solar.ID == int(ptID)]['City'].values[0]
    resWater = df_solar.loc[df_solar.ID == int(ptID)]['Avg_F5000gal_res_perKgal'].values[0]
    resUsage = df_solar.loc[df_solar.ID == int(ptID)]['Avg_Average_Usage_Residentia_13'].values[0]
    customers = df_solar.loc[df_solar.ID == int(ptID)]['Avg_Total_Customers'].values[0]
    #TODO: Improve markdown or use a table.

    if resWater is np.nan:
        resWater = -1
    if network is np.nan: 
        network = '-'
        networkDist = -1.0
        networkOp = '-'
    mdText = "#### Site Details\n\n"
    mdText += "Annual DNI: {:,.1f}kWh\n\n".format(solar)
    mdText += "Network Name: {}\n\n".format(network)
    mdText += "Network Operator: {}\n\n".format(networkOp)
    mdText += "Distance to network: {:.1f}km\n\n".format(networkDist)
    mdText += "Weather station file: {}\n\n".format(wxStation)
    mdText += "Average county residential price: ${:,.2f}/Kgal\n\n".format(resWater)
    mdText += "Residential usage: {:,.1f} gal\n\n".format(resUsage)
    mdText += "Approximate number of customers: {:,.0f}\n\n".format(customers)
    return(dcc.Markdown(mdText))

@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input(component_id='map', component_property='clickData')]
)

def update_user_point(input_value):
    ''' use the point number to get the corresponding DF values '''
    if input_value is None:
        # handles an empty click without updating the map
        print('empty click')
        raise PreventUpdate
    else:
        if 'points' not in set(input_value.keys()):
            print('bad data')
            raise PreventUpdate
        else:
            ptID = input_value['points'][0]['location']
            userPoint = go.Scattermapbox(
                name='Selected Site',
                lat=df_solar.loc[df_solar.ID == int(ptID)]['CENTROID_Y'].values,
                lon=df_solar.loc[df_solar.ID == int(ptID)]['CENTROID_X'].values,
                showlegend=True,
                visible=True,
                mode='markers',
                marker=dict(
                    color='red',
                    size=11,
                ),
            )
            print(userPoint['lat'])
    # TODO: instead of returning figure, need to update (extend) the userPoint, not replace it.     
    return go.Figure(dict(data=[countyData,globalData,solarData,userPoint], layout=layout))


# @app.callback(
#     Output(component_id='map', component_property='extendData'),
#     [Input(component_id='map', component_property='clickData')]
# )

# def update_point(input_click):
#     if input_click is None:
#         # handles an empty click without updating the map
#         print('empty click')
#         raise PreventUpdate
#     else:
#         if 'points' not in set(input_click.keys()):
#             print('click outside fishnet')
#             raise PreventUpdate
#         else:
#             # do the update
#             ptID = input_click['points'][0]['location']
#             lats=df_solar.loc[df_solar.ID == int(ptID)]['CENTROID_Y'].values,
#             lons=df_solar.loc[df_solar.ID == int(ptID)]['CENTROID_X'].values,
#         print(len(lats))
#         return({'lat':[lats],'lon':[lons]},2,1)

#         # if 'points' not in set(input_click.keys()): 
#         #     raise PreventUpdate
#         # else:
#         #     ptID = input_click['points'][0]['location']
#         #     userPt = go.Scattermapbox(
#         #         lat=[[df_solar.loc[df_solar.ID == int(ptID)]['CENTROID_Y'].values[0]]],
#         #         lon=[[df_solar.loc[df_solar.ID == int(ptID)]['CENTROID_X'].values[0]]],
#         #         hoverinfo=None,
#         #         showlegend=False,
#         #         mode='markers',
#         #         marker=dict(
#         #             color='red',
#         #             size=11,
#         #         ),
#         #     )
#         # print(userPt['lat'])    
#         # return (userPt,2)


if __name__ == '__main__':
    app.run_server(debug=False, port=8067)
    