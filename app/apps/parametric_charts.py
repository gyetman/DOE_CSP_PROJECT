import json
import numpy as np
import pandas as pd
import re

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from pathlib import Path
import plotly.express as px

import app_config as cfg
import helpers
from app import app

# To chart priority
# 1. "Total water production" from simulation_output files
# 2. "Levelized cost of water" from cost_output files


# external_stylesheets = [dbc.themes.FLATLY]
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

chart_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Charts"), active=True),
              dbc.NavItem(dbc.NavLink("Report", href='/analysis-report'))],
    brand="Parametric Study",
    color="primary",
    dark=True,
    style={'margin-bottom':60}
)

def real_time_layout():
    print('printing is working')
    parametric_charts_layout = html.Div([
        html.Div(id='initialize'),
        chart_navbar,
        dcc.Store(id='solar-storage'),
        dcc.Store(id='parametric-desal-storage'),
        dbc.Container([ 
            html.H3('Total Water Production',className='text-success', 
            style={'margin-bottom':0, 'text-align':'center'}),
            dcc.Graph(id='parametric-desal-graph'),
            # solar_radios,
            # html.H3(cfg.Desal[helpers.json_load(cfg.app_json)['desal']], className='text-success',style={'margin-top':45, 'margin-bottom':0, 'text-align':'center'}),
            # dcc.Graph(id='desal-graph'),
            # desal_radios,
        ],style={'margin-bottom':150})
    ])  
    return parametric_charts_layout

## CREATE STORE
# read in paramatric json to get variables and steps info 
# -this might be outside of the Store callback
# read in output JSONs to get values from each run
# store as lists
@app.callback(
    Output('parametric-desal-storage', 'data'),
    [Input('initialize', 'children')])
def store_desal_data(x):
    print('store_desal_data trigger')
    # create a file lookup 
    alkup = helpers.json_load(cfg.app_json)
    flkup = cfg.build_file_lookup(alkup['solar'], alkup['desal'], 
                                  alkup['finance'])
    # get the desal directory and file prefix
    path = flkup['parametric_desal_simulation_outfile']

    # load simulation result info
    info = helpers.json_load(cfg.parametric_info)
    timestamps = list(info['Timestamps'].keys())

    #NOTE QUESTION: How to know if variable is desal/solar or finance?

    # two variable route
    if len(info['Variables'])==2:
        print('entered if')
        var1,var2 = info['Variables']
        #build empty dataframe using values of variable intervals
        #for index and column labels
        df = pd.DataFrame(index=[str(i) for i in info['Variables'][var1]['Values']], columns=[str(c) for c in info['Variables'][var2]['Values']])
        # read through files one timestamp at a time and add values to dataframe
        for t in timestamps:
            #load the json
            para_dict=helpers.json_load(f'{path}{t}.json')
            #find the location of the specific value for the variable
            index = helpers.index_in_list_of_dicts(para_dict,'Name','Total water production')
            #get location within dataframe 
            loc = [str(l) for l in info['Timestamps'][t]]
            #set dataframe value at location
            df.at[loc[0],loc[1]]=para_dict[index]['Value']
        print(df)
        return df.to_dict()

@app.callback(
    Output('parametric-desal-graph','figure'),
    # [Input('select-desal-chart', 'value'),
    # Input('select-desal-time', 'value'),
    # Input('desal-storage', 'data')])
    [Input('parametric-desal-storage', 'data')])
# def update_desal_graph(desalValue, timeAggValue, desalData):
def update_desal_graph(desalData):
    ''' update the desal figure object '''
    # figure={
    #     'data': [
    #         {
    #             'x': df_tmp.index,
    #             'y': df_tmp[desalValue],
    #             'name': desalValue,
    #             'mode': 'bar',
    #             'marker': {'size': 12, 'color':'#2C3E50'},
    #         }
    #     ],
    #     'layout': {
    #         'title': {'text':gen_title(desalValue,timeAggValue),
    #                   'font':{'color':'#2C3E50'}},
    #         'clickmode': 'event+select',
    #         'xaxis':{'title': '{} values'.format(timeAggValue)},
    #         'yaxis':{'title': desal_units[desalValue]},
    #     }
    # }
    print('update_desal_graph triggered')
    dd = pd.DataFrame.from_dict(desalData)
    fig = px.bar(dd, barmode='group')
    return fig






