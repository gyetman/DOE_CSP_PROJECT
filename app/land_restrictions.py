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

# load easement data
df_easements = pd.read_csv('./GISData/easements.csv')
df_easements['text'] = 'Easement: ' + df_easements['d_Mang_Typ']
df_easements['z'] = 1

# load federal data
df_federal = pd.read_csv('./GISData/federal.csv')
df_federal['text'] = 'Agency: ' + df_federal['ADMIN1']
df_federal['z'] = 5

# load padus data
#df_padus = pd.read_csv('./GISData/padus.csv')
#df_padus['text'] = 'For fee land: {}'.format(df_padus['???'])

#load geoJSON geometries for easements
with open('./gisData/easements_non_federal.geojson','r') as f:
    geoj_easements = json.load(f)

#load geoJSON geometries for federal lands
with open('./gisData/federal_lands.geojson','r') as f:
    geoj_federal = json.load(f)

#with open('./gisData/padus_4fee_non_fed.geojson', 'r') as f:
#    geoj_padus = json.load(f)


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

easementData = go.Choroplethmapbox(
    name='Easements',
    geojson=geoj_easements, 
    locations=df_easements.ID,
    text=df_easements.text,
    z=df_easements.z,
    hoverinfo='text',
    # featureidkey='ZCTA5CE10',
    #z=df_county.TDS_mgL,
    #colorscale="Viridis", 
    #colorbar=dict(
    #    title='Average TDS mg/L',
    #),
    showlegend=True,
    marker_opacity=1, 
    marker_line_width=0,
    #hoverinfo='skip',
    visible=True,
    showscale=False,
    )

federalData = go.Choroplethmapbox(
    name='Federal Lands',
    geojson=geoj_federal, 
    locations=df_federal.ID,
    text=df_federal.text,
    z=df_federal.z,
    hoverinfo='text',
    # featureidkey='ZCTA5CE10',
    #z=df_county.TDS_mgL,
    colorscale="Viridis", 
    #colorbar=dict(
    #    title='Average TDS mg/L',
    #),
    showlegend=True,
    marker_opacity=1, 
    marker_line_width=0,
    #hoverinfo='skip',
    visible=True,
    showscale=False,
    )

'''
padusData = go.Choroplethmapbox(
    name='Land for fee',
    geojson=geoj_padus, 
    locations=df_padus.ID, 
    # featureidkey='ZCTA5CE10',
    #z=df_county.TDS_mgL,
    #colorscale="Viridis", 
    #colorbar=dict(
    #    title='Average TDS mg/L',
    #),
    marker_opacity=1, 
    marker_line_width=0,
    #hoverinfo='skip',
    text=df.text,
    visible=True,
    )
'''
data = [easementData,federalData] # sets the order

layout = go.Layout(
    height=600,
    #width=900,
    autosize=True,
    #hovermode='closest',
    #clickmode='text',
    title='Land restrictions',
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
app.title = 'Federal, State and Local restrictions'
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
        print('empty click')
        raise PreventUpdate

    else:
        ptID = clicks['points'][0]['location']
        txt = clicks['points'][0]['text']
        if 'Easement:' in txt:
            # use text to get type
            # TODO: setup dict to hold var names and labels
            # then iterate the dict to create the markdown text
            # attributes = {}

            countyName = df_easements.loc[df_easements.ID == ptID]['CountyName'].values[0]
            #stateName = df_easements.loc[df_easements.ID == ptID]['State_Nm'].values[0]
            easementType = df_easements.loc[df_easements.ID == ptID]['Loc_Ds'].values[0]
            category = df_easements.loc[df_easements.ID == ptID]['d_Mang_Typ'].values[0]
            managementName = df_easements.loc[df_easements.ID == ptID]['d_Mang_Nam'].values[0]
            gapStatus = df_easements.loc[df_easements.ID == ptID]['d_GAP_Sts'].values[0]
            duration = df_easements.loc[df_easements.ID == ptID]['Duration'].values[0]

            mdText = "###### Status for land parcel in {} County, {}\n\n".format(countyName,'ST')
            mdText += "Permit information: [State](https://docs.google.com/spreadsheets/d/1DiMFwzUfq7evlDDYER5D9XLekhZJWd7-DODjV3hX9-w/edit?usp=sharing) [Local](https://docs.google.com/spreadsheets/d/1YY-JVnjpbGqc_Q26FfOu8Wf34qBKiHFgvSrcsAVcPbs/edit?usp=sharing)\n\n"
            mdText += 'Source: Federal Protected Areas Database\n\n'
            mdText += 'Management category: {}\n\n'.format(category)
            mdText += 'Easement type: {}\n\n'.format(easementType)
            mdText += 'Management body: {}\n\n'.format(managementName)
            mdText += 'Status: {}\n\n'.format(gapStatus)
            mdText += 'Duration: {}\n\n'.format(duration)

            return(dcc.Markdown(mdText))
        elif 'Agency:' in txt:
            #countyName = df_federal.loc[df_federal.ID == ptID]['COUNTY'].values[0]
            stateName = df_federal.loc[df_federal.ID == ptID]['STATE'].values[0]
            landName = df_federal.loc[df_federal.ID == ptID]['NAME1'].values[0]
            altName = df_federal.loc[df_federal.ID == ptID]['NAME2'].values[0]
            adminBody = df_federal.loc[df_federal.ID == ptID]['ADMIN1'].values[0]

            mdText = "###### Permit information: \n\n"
            mdText += "&nbsp&nbsp&nbsp[State](https://docs.google.com/spreadsheets/d/1DiMFwzUfq7evlDDYER5D9XLekhZJWd7-DODjV3hX9-w/edit?usp=sharing)\n\n"
            mdText += "&nbsp&nbsp&nbsp[Local](https://docs.google.com/spreadsheets/d/1YY-JVnjpbGqc_Q26FfOu8Wf34qBKiHFgvSrcsAVcPbs/edit?usp=sharing)\n\n"
            mdText += "###### Status for Federal land parcel in {} County, {}\n\n".format('cn',stateName)
            mdText += 'Source: Federal Lands Data, USGS\n\n'
            mdText += 'Facility name: {}\n\n'.format(landName)
            mdText += 'Second/alternate name: {}\n\n'.format(altName)
            mdText += 'Administrative body: {}\n\n'.format(adminBody)

            return(dcc.Markdown(mdText))










if __name__ == '__main__':
    app.run_server(debug=True, port=8058)
    