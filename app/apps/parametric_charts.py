import json
import numpy as np
import pandas as pd
import re

import dash
import dash_bootstrap_components as dbc
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output
from pathlib import Path
import plotly.express as px

import app_config as cfg
import helpers
from app import app

desal_outputs = {
        'RO': {
        'Total water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Total fossil fuel usage':'parametric_desal_simulation_outfile',
        'Percentage of fossil fuel consumption': 'parametric_desal_simulation_outfile',
        'Specific energy consumption': 'parametric_desal_design_outfile'},
        'OARO': {
        'Total water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Total fossil fuel usage':'parametric_desal_simulation_outfile',
        'Percentage of fossil fuel consumption': 'parametric_desal_simulation_outfile',
        'Specific electricity consumption': 'parametric_desal_design_outfile'
        },
        'LTMED':{
        'Total water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Total fossil fuel usage':'parametric_desal_simulation_outfile',
        'Percentage of fossil fuel consumption': 'parametric_desal_simulation_outfile',
        'Specific thermal power consumption': 'parametric_desal_design_outfile'},
        'FO':{
        'Total water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Total fossil fuel usage':'parametric_desal_simulation_outfile',
        'Percentage of fossil fuel consumption': 'parametric_desal_simulation_outfile',
        'Specific thermal power consumption': 'parametric_desal_design_outfile'},        
        'VAGMD':{
        'Total water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Total fossil fuel usage':'parametric_desal_simulation_outfile',
        'Percentage of fossil fuel consumption': 'parametric_desal_simulation_outfile',
        'Specific thermal power consumption': 'parametric_desal_design_outfile'},
        'MEDTVC':{
        'Total water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Total fossil fuel usage':'parametric_desal_simulation_outfile',
        'Percentage of fossil fuel consumption': 'parametric_desal_simulation_outfile',
        'Specific thermal power consumption': 'parametric_desal_design_outfile'},
        'MDB':{
        'Total water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Total fossil fuel usage':'parametric_desal_simulation_outfile',
        'Percentage of fossil fuel consumption': 'parametric_desal_simulation_outfile',
        'Specific thermal power consumption': 'parametric_desal_design_outfile'},
        'ABS':{
        'Total water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Total fossil fuel usage':'parametric_desal_simulation_outfile',
        'Percentage of fossil fuel consumption': 'parametric_desal_simulation_outfile',
        'Specific thermal power consumption': 'parametric_desal_design_outfile'},
        'Generic':{
        'Total water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Total fossil fuel usage':'parametric_desal_simulation_outfile',
        'Percentage of fossil fuel consumption': 'parametric_desal_simulation_outfile'},       
        'RO_MDB':{
        'Annual water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Percentage of grid electricity consumption': 'parametric_desal_simulation_outfile',
        'Percentage of external fossil fuel consumption': 'parametric_desal_simulation_outfile',
        'SEC-RO (Specific electricity consumption)': 'parametric_desal_design_outfile',
        'STEC-MD (Specific thermal power consumption)': 'parametric_desal_design_outfile'},
        'RO_FO':{
        'Annual water production':'parametric_desal_simulation_outfile',
        'Levelized cost of water':'parametric_desal_finance_outfile',
        'Percentage of grid electricity consumption': 'parametric_desal_simulation_outfile',
        'Percentage of external fossil fuel consumption': 'parametric_desal_simulation_outfile',
        'SEC-RO (Specific electricity consumption)': 'parametric_desal_design_outfile',
        'STEC-FO (Specific thermal power consumption)': 'parametric_desal_design_outfile'}
        }
    
desal_units = {
    'Total water production':'m3',
    'Annual water production':'m3',
    'Levelized cost of water':'$/m3',
    'Total fossil fuel usage':'kWh',
    'Percentage of fossil fuel consumption':'%',
    'Specific thermal power consumption':'kWh(th)/m3',
    'Specific energy consumption':'kWh(e)/m3',
    'Specific electricity consumption': 'kWh(e)/m3',
    'Water production': 'm3',
    'SEC-RO (Specific electricity consumption)': 'kWh(e)/m3',
    'STEC-MD (Specific thermal power consumption)': 'kWh(th)/m3',
    'STEC-FO (Specific thermal power consumption)': 'kWh(th)/m3',
    'Percentage of grid electricity consumption':'%',
    'Percentage of external fossil fuel consumption':'%'
    }

chart_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Home", href='/home')),
              dbc.NavItem(dbc.NavLink("Charts"), active=True)],
    brand="Parametric Study",
    color="primary",
    dark=True,
    sticky='top',
    style={'margin-bottom':60}
)

def real_time_layout():
    app = helpers.json_load(cfg.app_json)
    title=f"{cfg.Solar[app['solar']]} / {cfg.Desal[app['desal']]}"
    parametric_radios = html.Div([
        dbc.Row([
            dbc.Col(
                dcc.RadioItems(
                    id='select-parametric-chart',
                    options=[{'label': f" {name}", 'value': name}
                            for name in desal_outputs[helpers.json_load(cfg.app_json)['desal']]],
                    value=list(desal_outputs[helpers.json_load(cfg.app_json)['desal']].keys())[0],
                    labelStyle = {'display': 'block'}),
                width=4),
        ], justify="center")
    ])

    parametric_charts_layout = html.Div([
        html.Div(id='initialize'),
        chart_navbar,
        dcc.Store(id='parametric-storage'),
        dbc.Container([ 
            html.H4(children=title,
                id='title', className='text-success', 
            style={'margin-bottom':0, 'text-align':'center'}),
            dcc.Graph(id='parametric-graph'),
            parametric_radios,
        ],style={'margin-bottom':150})
    ])  
    return parametric_charts_layout

## CREATE STORE
# read in paramatric json to get variables and steps info 
# -this might be outside of the Store callback
# read in output JSONs to get values from each run
# store as lists
@app.callback(
    Output('parametric-storage', 'data'),
    [Input('initialize', 'children')])
def store_desal_data(x):
    # create a file lookup 
    alkup = helpers.json_load(cfg.app_json)
    flkup = cfg.build_file_lookup(alkup['solar'], alkup['desal'], 
                                  alkup['finance'],alkup['timestamp'])

    # load simulation result info
    info = helpers.json_load(cfg.parametric_info)
    timestamps = list(info['Timestamps'].keys())

    desal_dict = {}

    for desal_output in desal_outputs[alkup['desal']]:
        # get the desal directory and file prefix
        path = flkup[desal_outputs[alkup['desal']][desal_output]]
        # one variable route
        if len(info['Variables'])==1:
            var1 = [key for key in info['Variables']][0]

            # labels = list([var1['Label']])
            labels=info['Variables'][var1]['Label']
            units = info['Variables'][var1]['Unit']
            #build empty dataframe using values of variable intervals
            #for index and column labels
            # df = pd.DataFrame(index=[str(i) for i in info['Variables'][var1]['Values']])
            df = pd.DataFrame(index=[str(i) for i in info['Variables'][var1]['Values']],columns=[f'{labels}'])
            # read through files one timestamp at a time and add values to dataframe
            for i,t in enumerate(timestamps):
                #load the json
                para_dict=helpers.json_load(f'{path}{t}.json')

                #find the location of the specific value for the variable 
                index = helpers.index_in_list_of_dicts(para_dict,'Name',desal_output)
                #get location within dataframe 
                loc = [str(l) for l in info['Timestamps'][t]]
                #set dataframe value at location
                # df.at[loc[0],0]=para_dict[index]['Value']
                df[f'{labels}'][i]=para_dict[index]['Value']
            
            #pass on dataframe, label and units for output variable

            desal_dict[desal_output]={'df':df.to_dict(),'label':labels,'unit':units}

        # two variable route
        if len(info['Variables'])==2:
            var1,var2 = info['Variables']
            labels = list([info['Variables'][var1]['Label'],info['Variables'][var2]['Label']])
            units = list([info['Variables'][var1]['Unit'],info['Variables'][var2]['Unit']])
            #build empty dataframe using values of variable intervals
            #for index and column labels
            df = pd.DataFrame(index=[str(i) for i in info['Variables'][var1]['Values']], columns=[str(c) for c in info['Variables'][var2]['Values']])
            # read through files one timestamp at a time and add values to dataframe
            for t in timestamps:
                #load the json
                para_dict=helpers.json_load(f'{path}{t}.json')
                #find the location of the specific value for the variable
                index = helpers.index_in_list_of_dicts(para_dict,'Name',desal_output)
                #get location within dataframe 
                loc = [str(l) for l in info['Timestamps'][t]]
                #set dataframe value at location
                df.at[loc[0],loc[1]]=para_dict[index]['Value']
            #pass on dataframe, label and units for output variable
            desal_dict[desal_output]={'df':df.to_dict(),'label':labels,'unit':units}

    return desal_dict

@app.callback(
    Output('parametric-graph','figure'),
    [Input('select-parametric-chart', 'value'),
     Input('parametric-storage', 'data')])
# def update_desal_graph(desalValue, timeAggValue, desalData):
def update_parametric_graph(paramValue, parametricData):
    ''' update the desal figure object '''

    pD=parametricData[paramValue]
    if len(pD['label'])==2:
        varlabel=f"{pD['label'][1].title()} ({pD['unit'][1]})"
        indexlabel=f"{pD['label'][0].title()} ({pD['unit'][0]})"
    else:
        varlabel=' '
        indexlabel=f"{pD['label'].title()} ({pD['unit']})"

    dd = pd.DataFrame.from_dict(pD['df'])

    # cast as float because column types need to be the same
    dd = dd.astype(float)
    fig = px.bar(dd,
                barmode='group', 
                labels={'index':indexlabel,  'value':f"{paramValue.title()} ({desal_units[paramValue]})",
                'variable':varlabel
                })
    fig.update_layout(xaxis_type='category')

    return fig

# @app.callback(
#     Output('title','children'),
#     [Input('select-parametric-chart', 'value')])
# def title_chart(chartTitle):
#     return chartTitle.title()








