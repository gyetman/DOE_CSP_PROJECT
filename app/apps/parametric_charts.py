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

desal_outputs = {
    'Total water production':'parametric_desal_simulation_outfile',
    'Levelized cost of water':'parametric_desal_finance_outfile',
    'Total fossil fuel usage':'parametric_desal_simulation_outfile',
    'Percentage of fossil fuel consumption': 'parametric_desal_simulation_outfile',
    'Specific thermal power consumption': 'parametric_desal_design_outfile'
}
desal_units = {
    'Total water production':'m3',
    'Levelized cost of water':'$/m3',
    'Total fossil fuel usage':'kWh',
    'Percentage of fossil fuel consumption':'%',
    'Specific thermal power consumption':'kWh(th)/m3'}

chart_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Charts"), active=True),
              dbc.NavItem(dbc.NavLink("Report", href='/analysis-report'))],
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
                            for name in desal_outputs],
                    value=list(desal_outputs.keys())[0],
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
                                  alkup['finance'])

    # load simulation result info
    info = helpers.json_load(cfg.parametric_info)
    timestamps = list(info['Timestamps'].keys())

    desal_dict = {}

    for desal_output in desal_outputs:
        # get the desal directory and file prefix
        path = flkup[desal_outputs[desal_output]]

        # one variable route
        if len(info['Variables'])==1:
            var1 = [key for key in info['Variables']][0]
            print(f'var1: {var1}')
            # labels = list([var1['Label']])
            labels=info['Variables'][var1]['Label']
            units = info['Variables'][var1]['Unit']
            #build empty dataframe using values of variable intervals
            #for index and column labels
            # df = pd.DataFrame(index=[str(i) for i in info['Variables'][var1]['Values']])
            df = pd.DataFrame(index=[str(i) for i in info['Variables'][var1]['Values']],columns=['param'])
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
                df['param'][i]=para_dict[index]['Value']
            
            #pass on dataframe, label and units for output variable
            print(f'filled df: {df}')
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
    if len(pD['df'])==2:
        varlabel=f"{pD['label'][1].title()} ({pD['unit'][1]})"
        indexlabel=f"{pD['label'][0].title()} ({pD['unit'][0]})"
    else:
        varlabel=' '
        indexlabel=f"{pD['label'].title()} ({pD['unit']})"
    print(f'pD: {pD}')
    dd = pd.DataFrame.from_dict(pD['df'])

    # cast as float because column types need to be the same
    dd = dd.astype(float)
    fig = px.bar(dd,
                barmode='group', 
                labels={'index':indexlabel,  'value':f"{paramValue.title()} ({desal_units[paramValue]})",
                'variable':varlabel
                })
    fig.update_layout(xaxis_type='category')
    if len(pD['df'])==1: fig.update_layout(showlegend=False)
    return fig

# @app.callback(
#     Output('title','children'),
#     [Input('select-parametric-chart', 'value')])
# def title_chart(chartTitle):
#     return chartTitle.title()








