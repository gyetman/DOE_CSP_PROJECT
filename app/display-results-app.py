#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sun Aug  4 20:25:27 2019
Display results from SAM model output
@author: gyetman
"""

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

external_stylesheets = [dbc.themes.FLATLY,'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Model Results'

# load simulation results from JSONs
sol = helpers.json_load(cfg.sam_solar_simulation_outfile)
des = helpers.json_load(cfg.sam_desal_simulation_outfile)

# Note: solar_names need to match 'Name' values in the JSON
solar_names = ('System power generated','Receiver mass flow rate',
               'Receiver thermal losses','Resource Beam normal irradiance')
solar_indexes = [helpers.index_in_list_of_dicts(sol,'Name', x)
                for x in solar_names]
solar_arrays = [sol[x]['Value'] for x in solar_indexes]
solar_units = {sol[x]['Name']:sol[x]['Unit'] for x in solar_indexes}

# combine results into list of series; note the .T for transpose,
# otherwise the lists are read as rows, not columns. '''
solar_array_data = np.array([pd.Series(x) for x in solar_arrays]).T

# data frame of arrays, fortunately all the same shape!'''
df_solar = pd.DataFrame(
        solar_array_data,
        columns = solar_names
)

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
)

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
            return dataframe.groupby(dataframe.index // 24).sum().reset_index()
        else:
            return dataframe.groupby(dataframe.index // 24).mean().reset_index()
    elif time == 'Weekly':
        if variable in sumCols:
            return dataframe.groupby(dataframe.index // 168).sum().reset_index()
        else:
            return dataframe.groupby(dataframe.index // 168).mean().reset_index()

def gen_title(variable, time):
    d = {'Hourly':'Hour', 'Daily':'Day', 'Weekly':'Week'}
    return f"{variable.title()} per {d[time]}"

#
### Layout 
#

time_series = [{'label':' Hourly', 'value':'Hourly'},
               {'label':' Daily', 'value':'Daily'},
               {'label':' Weekly','value':'Weekly'}]

solar_radios = html.Div([
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(
                id='select-solar',
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
                id='select-desal',
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


app.layout = dbc.Container([  
    html.H3('Solar Thermal Model Results', className='text-success', style={'margin-bottom':0, 'text-align':'center'}),
    dcc.Graph(id='solar-graph'),
    solar_radios,
    html.H3('Desalination Model Results', className='text-success',style={'margin-top':45, 'margin-bottom':0, 'text-align':'center'}),
    dcc.Graph(id='desal-graph'),
    desal_radios,
],style={'margin-bottom':150})

@app.callback(
        Output('solar-graph','figure'),
        [Input('select-solar', 'value'),
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
        [Input('select-desal', 'value'),
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

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

