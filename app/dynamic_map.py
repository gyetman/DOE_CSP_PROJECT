
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
    visible=True

)

 # user-selected point placeholder
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
print(type(userPoint))
data = [solar,userPoint] # sets the order

layout = go.Layout(
    #height=600,
    #width=900,
    autosize=True,
    #hovermode='closest',
    #clickmode='text',
    title='Make this dynamic', # the Meta tag on traces should do it
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

fig = go.Figure(dict(data=data, layout=layout))
app.title = 'Site Selection'
app.layout = html.Div(children=[
    html.Div([
        dcc.Dropdown(
            id='select-map',
            options = [
                {'label':'Solar Resource', 'value':'solar'},
                {'label':'Electricity Prices', 'value':'price'},
                {'label':'Produced Waters','value':'produced'},
                {'label':'Brackish Waters', 'value':'brackish'},
                {'label':'Legal Framework', 'value':'legal'}
            ],
            value='solar',
            className='row'
        ),
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
        html.Div(
        dcc.Link(html.Button('Select Models'), 
        href='http://127.0.0.1:8073/model-selection', 
        id='next-button'),
        )
    ], className='row'
    )

])

# callback for dropdown theme choice


# callback for the button
""" @app.callback(
    Output(component_id='next-button',component_property='href'),
    [Input('next-button','n_clicks')]
) """
def nextStep(n_clicks):
    return('http://127.0.0.1:8073/model-selection')
# callback for updating geometries
@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input(component_id='map', component_property='clickData')],
    [State(component_id='map', component_property='relayoutData'),
    State(component_id='map', component_property='figure')]
)
def clickPoint(clicks,relay,fig):
    if not any([clicks,relay,fig]):
        raise PreventUpdate
    # clicked close enough to a point
    if clicks:
        # get geom from nearest point and add user point
        # user-selected point placeholder
        """         newUserPoint = go.Scattermapbox(
            name='Selected Site',
            lat=[clicks['points'][0]['lat']],
            lon=[clicks['points'][0]['lon']],
            # replaced None object with 'none', confusing but that turns it off!  
            #hoverinfo='none',
            mode='markers',
            marker=dict(
                size=13,
                color='red',
            ),
            showlegend=True,
            visible=True,
        ), """
        newUserPoint = userPoint
        newUserPoint['lat'] = [clicks['points'][0]['lat']]
        newUserPoint['lon'] = [clicks['points'][0]['lon']]
        newUserPoint['visible'] = True
        newUserPoint['showlegend'] = True
        print(type(newUserPoint))
        #return go.Figure(dict(data=[solar,userPoint], layout=layout))
        return go.Figure(dict(data=[solar,newUserPoint], layout=layout))
    if fig:
        #print(fig)
        raise PreventUpdate
    if relay:
        print(relay)
        raise PreventUpdate



if __name__ == '__main__':
    app.run_server(debug=True, port=8058)    
    
    
    