import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import plotly.graph_objs as go
import numpy as np

CENTER_LAT=32.7767
CENTER_LON=-96.7970

external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_key = 'pk.eyJ1IjoiZ3lldG1hbiIsImEiOiJjanRhdDU1ejEwZHl3NDRsY3NuNDRhYXd1In0.uOqHLjY8vJEVndoGbugWWg'
app = dash.Dash(__name__, external_stylesheets=external_stylesheet)

# load well data
df = pd.read_csv('./GISData/dissolved_solids.csv')
df['text'] = df['TDS_mgL'].round(1).astype(str) + ' mg/L'

# load county attributes
df_county = pd.read_csv('./GISData/county_tds.csv')
df_county['text'] = df_county['TDS_mgL'].round(1).astype(str) + ' mg/L'

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

)


tdsData = go.Choroplethmapbox(
    name='Mean TDS per county',
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
    # TODO: add year to map GUI (year of data)
    )

data = [tdsData,wellLocation,userPoint] # sets the order

layout = go.Layout(
    height=600,
    width=800,
    autosize=True,
    #hovermode='closest',
    #clickmode='text',
    title='Average TDS per county and Well Location Data',
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

# placeholder for output text
markdownText = '''

'''

fig = go.Figure(dict(data=data, layout=layout))
app.title = 'Electric Rates'
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
    if 'points' not in set(clicks.keys()):
        raise PreventUpdate
    else:
        ptKeys = clicks['points'][0].keys()

        ptID = clicks['points'][0]['location']
        countyName = df_county.loc[df_county.IDField == ptID]['NAME'].values[0]
        avgTDS = df_county.loc[df_county.IDField == ptID]['TDS_mgL'].values[0]
        avgPH = df_county.loc[df_county.IDField == ptID]['ph'].values[0]

        mdText = "###### Produced Water Measurements for {} County, ST\n\n".format(countyName)
        mdText += 'Source: USGS Produced Waters Database\n\n'
        mdText += 'Average TDS: {:,.1f} mg/L\n\n'.format(avgTDS)
        mdText += 'Average PH: {:0.1f}\n\n'.format(avgPH)
        return(dcc.Markdown(mdText))



# TODO: add callback for layer visibility
# add callback for point attributes

if __name__ == '__main__':
    app.run_server(debug=True, port=8058)
    