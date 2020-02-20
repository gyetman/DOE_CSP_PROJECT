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
import pandas as pd
import numpy as np

from textwrap import dedent as d

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
    
results = './results/sample.json'
with open(results,'r') as f:
    jsonData = json.loads(f.read())
    

def get_result_dict(nameValue,res=jsonData):
    ''' gets the dictionary with the name requested '''
    for element in res:
        if element['name'] == nameValue:
            return element


''' result arrays from dictionaries '''
t_loop_out = get_result_dict('T_loop_out')['array']
w_net = get_result_dict('W_net')['array']
p_cond = get_result_dict('P_cond')['array']
q_aux_fuel = get_result_dict('q_aux_fuel')['array']

''' use the names in sets to decide how to aggregate hourly data to
weekly, monthly, etc.  '''

sumCols = set(['Net hourly energy output','Fossil fuel usage'])
meanCols = set(['Condenser pressure','Solar field outlet temperature'])


''' combine results into list of series; note the .T for transpose,
otherwise the lists are read as rows, not columns. '''
arrData = np.array([pd.Series(x) for x in [t_loop_out,w_net,p_cond,q_aux_fuel]]).T


''' data frame of arrays, fortunately all the same shape!'''
df = pd.DataFrame(
        arrData,
        columns=['Solar field outlet temperature',
                 'Net hourly energy output',
                 'Condenser pressure',
                 'Fossil fuel usage'])

arrayUnits = {
        'Solar field outlet temperature':'oC',
        'Net hourly energy output':'kWh',
        'Condenser pressure':'Pa',
        'Fossil fuel usage':'mmBtu'
        }

''' single vlues '''
annual_energy = get_result_dict('annual_energy')['value']
capacity_factor = get_result_dict('capacity_factor')['value']

singValues = {
        'Annual energy output (kWh)': [annual_energy,'kWh'],
        'Capacity factor (%)': [capacity_factor,'%']
        }

# Desal data
distill = pd.Series(open('./results/Distillation production(m3 per h).csv').readlines())
gor = pd.Series(open('./results/GOR (Gained output ratio).csv').readlines())
df_dict={'dp':distill,'gor':gor}
df_desal = pd.DataFrame(df_dict)
print(df_desal.columns)
df_desal['Distillation Production'] = pd.to_numeric(df_desal.dp)
df_desal['Gained Output Ratio'] = pd.to_numeric(df_desal.gor)
print(df_desal.columns)
df_desal.drop('dp',inplace=True,axis=1)
df_desal.drop('gor',inplace=True,axis=1)
print(df_desal['Distillation Production'].describe())
app.title = 'Model Results'

desalUnits = {
    'Distillation Production':'m3 per hour',
    'Gained Output Ratio':'Ratio'
}

### Layout 
app.layout = html.Div([  
        
    html.Div([
       dcc.Markdown(d("""
           ### {}
       """.format('SAM Model Results')  ))
   ], className='title'),
        
    dcc.Graph(
        id='model-output',
        figure={
            'data': [
                {
                    'x': df.index,
                    'y': df['Net hourly energy output'],
                    'name': 'Net hourly energy output',
                    'mode': 'bar',
                    'marker': {'size': 12}
                }
            ],
            'layout': {
                'clickmode': 'event+select',
                'xaxis':{'title': 'Annual values by hour'},
                'yaxis':{'title': arrayUnits['Net hourly energy output']}
            }
        }
    ),

    html.Div(className='row', children=[
        html.Div([
            dcc.Markdown(d("""
                **Annual energy output**

                {0:,.1f} kWh
            """.format(singValues['Annual energy output (kWh)'][0])   ))
        ], className='two columns'),

        html.Div([
            dcc.Markdown(d("""
                **Capacity factor**

                {0:.2f}%
            """.format(singValues['Capacity factor (%)'][0])     ))
        ], className='two columns'),
            
        html.Div([
            dcc.Dropdown(
                    id='graph-dropdown',
                    options=[{'label':name, 'value':name} for name in list(df.columns)],
                    value=list(df.columns)[0],
                    clearable=False
                    ),

        ], className='two columns'),

        html.Div([
            dcc.Dropdown(
                    id='time-dropdown',
                    options=[{'label':'hourly', 'value':'hourly'},
                             {'label':'daily', 'value':'daily'},
                             {'label':'weekly','value':'weekly'}
                             ],
                    value='hourly',
                    clearable=False
                    ),

        ], className='two columns')
    ]), 
    html.Div([
       dcc.Markdown(d("""
           ### {}
       """.format('Desalination Model Results')  ))
   ], className='title'),


        dcc.Graph(
                id='desal-output',
                figure={
                    'data': [
                        {
                            'x': df_desal.index,
                            'y': df_desal['Distillation Production'],
                            'name': 'Distillation Production',
                            'mode': 'bar',
                            'marker': {'size': 12}
                        }
                    ],
                    'layout': {
                        'clickmode': 'event+select',
                        'xaxis':{'title': 'Annual values by hour'},
                        'yaxis':{'title': desalUnits['Distillation Production']}
                    }
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



#@app.callback(
#        Output('model-output','figure'),
#        [Input('time-dropdown','value')]
#        )
#def update_graph_agg(dropdownValue):
#    ''' update the figure object aggregation level '''
#    figure={
#        'data': [
#            {
#                'x': df.index,
#                'y': df[dropdownValue],
#                'name': dropdownValue,
#                'mode': 'bar',
#                'marker': {'size': 12}
#            }
#        ],
#        'layout': {
#            'clickmode': 'event+select',
#            'xaxis':{'title': 'Hourly values'},
#            'yaxis':{'title': arrayUnits[dropdownValue]}
#        }
#    }
#    return figure

@app.callback(
        Output('model-output','figure'),
        [Input('graph-dropdown', 'value'),
         Input('time-dropdown', 'value')]
        )
def update_graph(dropdownValue,timeAggValue):
    ''' updatge the figure object '''
    print(timeAggValue)
    print(dropdownValue)
    if timeAggValue == 'hourly':
        df_tmp = df
    elif timeAggValue == 'daily':
        if dropdownValue in sumCols:
            df_tmp = df.groupby(df.index // 24).sum().reset_index()
        else:
            df_tmp = df.groupby(df.index // 24).mean().reset_index()
    elif timeAggValue == 'weekly':
        if dropdownValue in sumCols:
            df_tmp = df.groupby(df.index // 168).sum().reset_index()
        else:
            df_tmp = df.groupby(df.index // 168).mean().reset_index()
    else:
        # shouldn't happen, just in case! 
        df_tmp = df
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
            'yaxis':{'title': arrayUnits[dropdownValue]}
        }
    }
    return figure

@app.callback(
        Output('desal-output','figure'),
        [Input('desal-dropdown', 'value'),
         Input('desal-time-dropdown', 'value')]
        )
def update_desal_graph(dropdownValue,timeAggValue):
    ''' updatge the figure object '''
    print(timeAggValue)
    print(dropdownValue)
    if timeAggValue == 'hourly':
        df_tmp = df_desal
    elif timeAggValue == 'daily':
        df_tmp = df_desal.groupby(df.index // 24).mean().reset_index()
    elif timeAggValue == 'weekly':
        df_tmp = df_desal.groupby(df.index // 168).mean().reset_index()
    else:
        # shouldn't happen, just in case! 
        df_tmp = df_desal
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
            'yaxis':{'title': desalUnits[dropdownValue]}
        }
    }
    return figure


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

