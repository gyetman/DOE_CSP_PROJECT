#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sun Aug  4 20:25:27 2019
Display results from SAM model output (Linear Fresnel)
TODO:
    -update to handle any suite of results from SAM by changing
    hard-coded arrays to parameters or a lookup from file. 
    -add more than four array options for display, perhaps via
    organizing via tabs. 

# TODO: 
    update the static values under the graph to use parameters so that
    they can be changed easily, or perhaps even changed by the user (add 
    via links maybe, like a "more details" button?)
@author: gyetman
"""

import json
import numpy as np
import pandas as pd
import sys

from textwrap import dedent as d

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

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# load simulation results from JSONs
sol = helpers.json_load(cfg.sam_solar_simulation_outfile)
des = helpers.json_load(cfg.sam_desal_simulation_outfile)

# get solar array values
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

# get desal array values
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
    '''returns dataframe aggregated by values chosen in dropdowns'''
    if time == 'hourly':
        return dataframe
    elif time == 'daily': 
        if variable in sumCols:
            return dataframe.groupby(dataframe.index // 24).sum().reset_index()
        else:
            return dataframe.groupby(dataframe.index // 24).mean().reset_index()
    elif time == 'weekly':
        if variable in sumCols:
            return dataframe.groupby(dataframe.index // 168).sum().reset_index()
        else:
            return dataframe.groupby(dataframe.index // 168).mean().reset_index()

# distill = pd.Series(open('./results/Distillation production(m3 per h).csv').readlines())
# gor = pd.Series(open('./results/GOR (Gained output ratio).csv').readlines())
# df_dict={'dp':distill,'gor':gor}
# df_desal = pd.DataFrame(df_dict)
# print(df_desal.columns)
# df_desal['Distillation Production'] = pd.to_numeric(df_desal.dp)
# df_desal['Gained Output Ratio'] = pd.to_numeric(df_desal.gor)
# print(df_desal.columns)
# df_desal.drop('dp',inplace=True,axis=1)
# df_desal.drop('gor',inplace=True,axis=1)
# print(df_desal['Distillation Production'].describe())

# ''' single vlues '''
# annual_energy = get_result_dict('annual_energy')['value']
# capacity_factor = get_result_dict('capacity_factor')['value']

# singValues = {
#         'Annual energy output (kWh)': [annual_energy,'kWh'],
#         'Capacity factor (%)': [capacity_factor,'%']
#     
#    }

#
### Layout 
#
solar_radios = html.Div([
    dbc.Row([
        dbc.Col([
            html.B(html.Label('Title Here?')),
            dcc.RadioItems(
                id='select-solar',
                options=[{'label': f" {name}", 'value': name} 
                        for name in list(df_solar.columns)],
                value=list(df_solar.columns)[0],
                labelStyle = {'display': 'block'}
            ),
        ], width=2),
        dbc.Col(html.Div("One of two columns"), width=2),
    ], justify="center")
])

app.layout = html.Div([  
        
    html.Div([
       dcc.Markdown(d("""
           ### {}
       """.format('SAM Model Results')  ))
   ], className='title'),
        
    dcc.Graph(
        id='solar-graph',
        figure={
            'data': [
                {
                    'x': df_solar.index,
                    'y': df_solar[solar_names[0]],
                    'name': solar_names[0],
                    'mode': 'bar',
                    'marker': {'size': 12}
                }
            ],
            'layout': {
                'clickmode': 'event+select',
                'xaxis':{'title': 'Annual values by hour'},
                'yaxis':{'title': solar_units[solar_names[0]]}
            },
        }
    ),

    html.Div(className='row', children=[
        # html.Div([
        #     dcc.Markdown(d("""
        #         **Annual energy output**

        #         {0:,.1f} kWh
        #     """.format(singValues['Annual energy output (kWh)'][0])   ))
        # ], className='two columns'),

        # html.Div([
        #     dcc.Markdown(d("""
        #         **Capacity factor**

        #         {0:.2f}%
        #     """.format(singValues['Capacity factor (%)'][0])     ))
        # ], className='two columns'),
            
        html.Div([
            dcc.Dropdown(
                    id='solar-dropdown',
                    options=[{'label':name, 'value':name} for name in list(df_solar.columns)],
                    value=list(df_solar.columns)[0],
                    clearable=False
                    ),

        ], className='two columns'),

        html.Div([
            dcc.Dropdown(
                    id='solar-time-dropdown',
                    options=[{'label':'hourly', 'value':'hourly'},
                             {'label':'daily', 'value':'daily'},
                             {'label':'weekly','value':'weekly'}
                             ],
                    value='hourly',
                    clearable=False
                    ),

        ], className='two columns')
    ]),
    solar_radios,

    html.Div([
       dcc.Markdown(d("""
           ### {}
       """.format('Desalination Model Results')  ))
   ], className='title'),

    dcc.Graph(
            id='desal-graph',
            figure={
                'data': [
                    {
                        'x': df_desal.index,
                        'y': df_desal[list(desal_names)[0]],
                        'name': list(desal_names)[0],
                        'mode': 'bar',
                        'marker': {'size': 12}
                    }
                ],
                'layout': {
                    'clickmode': 'event+select',
                    'xaxis':{'title': 'Annual values by hour'},
                    'yaxis':{'title': desal_units[list(desal_units)[0]]}
                },
            }
        ),

    html.Div([
        dcc.Dropdown(
                id='desal-dropdown',
                options=[{'label':name, 'value':name} for name in list(df_desal.columns)],
                value=list(df_desal.columns)[0],
                clearable=False
                ),

    ], className='two columns'),

    html.Div([
        dcc.Dropdown(
                id='desal-time-dropdown',
                options=[{'label':'hourly', 'value':'hourly'},
                        {'label':'daily', 'value':'daily'},
                        {'label':'weekly','value':'weekly'}
                        ],
                value='hourly',
                clearable=False
                ),

    ], className='two columns'),
    html.Div([
       dcc.Markdown(d("""
           ### {}
       """.format('\n\n\n\n')  ))
   ], className='title'),
])

@app.callback(
        Output('solar-graph','figure'),
        [Input('solar-dropdown', 'value'),
         Input('solar-time-dropdown', 'value')])
def update_solar_graph(dropdownValue,timeAggValue):
    ''' update the figure object '''
    df_tmp = aggregate_data(dataframe=df_solar, 
                            variable=dropdownValue,
                            time=timeAggValue)
    figure={
        'data': [
            {
                'x': df_tmp.index,
                'y': df_tmp[dropdownValue],
                'name': dropdownValue,
                'mode': 'bar',
                'marker': {'size': 12}
            }
        ],
        'layout': {
            'clickmode': 'event+select',
            'xaxis':{'title': '{} values'.format(timeAggValue)},
            'yaxis':{'title': solar_units[dropdownValue]}
        }
    }
    return figure

@app.callback(
        Output('desal-graph','figure'),
        [Input('desal-dropdown', 'value'),
         Input('desal-time-dropdown', 'value')])
def update_desal_graph(dropdownValue,timeAggValue):
    ''' update the figure object '''
    df_tmp = aggregate_data(dataframe=df_desal,
                            variable=dropdownValue,
                            time=timeAggValue)
    figure={
        'data': [
            {
                'x': df_tmp.index,
                'y': df_tmp[dropdownValue],
                'name': dropdownValue,
                'mode': 'bar',
                'marker': {'size': 12}
            }
        ],
        'layout': {
            'clickmode': 'event+select',
            'xaxis':{'title': '{} values'.format(timeAggValue)},
            'yaxis':{'title': desal_units[dropdownValue]}
        }
    }
    return figure

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

