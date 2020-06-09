import json
import numpy as np
import pandas as pd

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import app_config as cfg
import helpers

from app import app

# external_stylesheets = [dbc.themes.FLATLY,'https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Chart Results'

HOURS_IN_YEAR = 8760

alkup = helpers.json_load(cfg.app_json)
flkup = cfg.build_file_lookup(alkup['solar'], alkup['desal'], alkup['finance'])
# load simulation results from JSONs
sol = helpers.json_load(cfg.sam_solar_simulation_outfile)
des = helpers.json_load(flkup['sam_desal_simulation_outfile'])

# Note: solar_names need to match 'Name' values in the JSON
updates = helpers.json_load(cfg.app_json)
# solar_names = ('System power generated','Receiver mass flow rate',
#                     'Receiver thermal losses','Resource Beam normal irradiance')
if updates['solar'] == 'linear_fresnel_dsg_iph':
    solar_names = ('System power generated','Receiver mass flow rate',
                    'Receiver thermal losses','Resource Beam normal irradiance')
elif updates['solar'] == 'SC_FPC':
    solar_names = ('Thermal power generation','Field outlet temperature')
solar_indexes = [helpers.index_in_list_of_dicts(sol,'Name', x)
                for x in solar_names]
solar_units = {sol[x]['Name']:sol[x]['Unit'] for x in solar_indexes}
# the arrays all need to be the same size
# creates dummy variables (zeros) if they are not
# on failed runs of SamBaseClass the file can have empty values
solar_arrays = []
for x in solar_indexes:
    if len(sol[x]['Value']) == HOURS_IN_YEAR:
        solar_arrays.append(sol[x]['Value'])
    else:
        solar_arrays.append(np.zeros(HOURS_IN_YEAR))

# combine results into list of series; note the .T for transpose,
# otherwise the lists are read as rows, not columns. '''
solar_array_data = np.array([pd.Series(x) for x in solar_arrays]).T

# data frame of arrays, fortunately all the same shape!'''
df_solar = pd.DataFrame(
        solar_array_data,
        columns = solar_names
).round(2)

# Note: desal_names need to match 'Name' values in the JSON
desal_names = ('Water production','Fossil fuel usage', 'Storage status')
desal_indexes = [helpers.index_in_list_of_dicts(des,'Name', x)
                for x in desal_names]
desal_arrays = [des[x]['Value'] for x in desal_indexes]
desal_units = {des[x]['Name']:des[x]['Unit'] for x in desal_indexes}

desal_array_data = np.array([pd.Series(x) for x in desal_arrays]).T

# data frame of arrays, fortunately all the same shape!'''
df_desal = pd.DataFrame(
        desal_array_data,
        columns = desal_names
).round(2)

# determine how weekly and monthly data is aggregated
# SUM if in sumCols set, else MEAN
sumCols = {'System power generated','Receiver thermal losses',
           'Water production', 'Fossil fuel usage'}

def aggregate_data(dataframe, variable, time):
    '''returns dataframe aggregated by selected time value'''
    if time == 'Hourly':
        return dataframe
    elif time == 'Daily': 
        if variable in sumCols:
            return dataframe.groupby(dataframe.index // 24).sum().round(2).reset_index()
        else:
            return dataframe.groupby(dataframe.index // 24).mean().round(2).reset_index()
    elif time == 'Weekly':
        if variable in sumCols:
            return dataframe.groupby(dataframe.index // 168).sum().round(2).reset_index()
        else:
            return dataframe.groupby(dataframe.index // 168).mean().round(2).reset_index()

def gen_title(variable, time):
    d = {'Hourly':'Hour', 'Daily':'Day', 'Weekly':'Week'}
    return f"{variable.title()} per {d[time]}"

#
### Layout 
#

time_series = [{'label':' Hourly', 'value':'Hourly'},
               {'label':' Daily', 'value':'Daily'},
               {'label':' Weekly','value':'Weekly'}]

chart_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Charts"), active=True),
              dbc.NavItem(dbc.NavLink("Report", href='/analysis-report'))],
    brand="Model Results",
    color="primary",
    dark=True,
    style={'margin-bottom':60}
)

solar_radios = html.Div([
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(
                id='select-solar-chart',
                options=[{'label': f" {name}", 'value': name}
                        for name in solar_names],
                value=solar_names[0],
                labelStyle = {'display': 'block'}),
            width=4),
        dbc.Col(
            dcc.RadioItems(
                id='select-solar-time',
                options=time_series,
                value='Hourly',
                labelStyle={'display': 'block'}),
        width=2)
    ], justify="center")
])

desal_radios = html.Div([
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(
                id='select-desal-chart',
                options=[{'label': f" {name}", 'value': name}
                        for name in desal_names],
                value=desal_names[0],
                labelStyle = {'display': 'block'}),
            width=2),
        dbc.Col(
            dcc.RadioItems(
                id='select-desal-time',
                options=time_series,
                value='Hourly',
                labelStyle={'display': 'block'}),
        width=2)
    ], justify="center")
])


chart_results_layout = html.Div([
    chart_navbar,
    dbc.Container([ 
        html.H3('Solar Thermal Model', className='text-success', style={'margin-bottom':0, 'text-align':'center'}),
        dcc.Graph(id='solar-graph'),
        solar_radios,
        html.H3('Desalination Model Results', className='text-success',style={'margin-top':45, 'margin-bottom':0, 'text-align':'center'}),
        dcc.Graph(id='desal-graph'),
        desal_radios,
    ],style={'margin-bottom':150})
])

@app.callback(
        Output('solar-graph','figure'),
        [Input('select-solar-chart', 'value'),
         Input('select-solar-time', 'value')])
def update_solar_graph(solarValue,timeAggValue):
    ''' update the figure object '''
    df_tmp = aggregate_data(dataframe=df_solar, 
                            variable=solarValue,
                            time=timeAggValue)
    figure={
        'data': [
            {
                'x': df_tmp.index,
                'y': df_tmp[solarValue],
                'name': solarValue,
                'mode': 'bar',
                'marker': {'size': 10, 'color':'#2C3E50'},
            }
        ],
        'layout': {
            'title': {'text':gen_title(solarValue,timeAggValue),
                      'font':{'color':'#2C3E50'}},
            'clickmode': 'event+select',
            'xaxis':{'title': '{} values'.format(timeAggValue)},
            'yaxis':{'title': solar_units[solarValue]},
        }
    }
    return figure

@app.callback(
        Output('desal-graph','figure'),
        [Input('select-desal-chart', 'value'),
         Input('select-desal-time', 'value')])
def update_desal_graph(desalValue,timeAggValue):
    ''' update the figure object '''
    df_tmp = aggregate_data(dataframe=df_desal,
                            variable=desalValue,
                            time=timeAggValue)
    figure={
        'data': [
            {
                'x': df_tmp.index,
                'y': df_tmp[desalValue],
                'name': desalValue,
                'mode': 'bar',
                'marker': {'size': 12, 'color':'#2C3E50'},
            }
        ],
        'layout': {
            'title': {'text':gen_title(desalValue,timeAggValue),
                      'font':{'color':'#2C3E50'}},
            'clickmode': 'event+select',
            'xaxis':{'title': '{} values'.format(timeAggValue)},
            'yaxis':{'title': desal_units[desalValue]},
        }
    }
    return figure
