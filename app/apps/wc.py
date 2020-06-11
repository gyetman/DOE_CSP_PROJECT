import json
import sys
from collections import defaultdict
from datetime import datetime
from operator import itemgetter
from pathlib import Path

# -*- coding: utf-8 -*-
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State, ALL

import app_config as cfg
sys.path.insert(0,str(cfg.base_path))

import helpers
from app import app

base_path = Path(__file__).resolve().parent.parent.absolute()
ajson = base_path / 't_folder' / 'a.json'

# define table columns
cols = [{'name':'Variable', 'id':'Name','editable':False},
        {'name':'Value',    'id':'Val','editable':True},
        {'name':'Units',    'id':'Units','editable':False},
        {'name':'DataType', 'id':'DataType',}]

# get values from app json to determine the selected models
app_vals = helpers.json_load(cfg.app_json)
s = app_vals['solar']
d = app_vals['desal']
f = app_vals['finance']

# now determine json input files to build variable tables with
avars = helpers.json_load(ajson)

wc_layout = html.Div([
    html.H3('WILDCARD TABLE CALLBACKS DEMO'),
    html.H5('???', id='solar_label'),
    html.Div(id='tab-page'),
    html.Button('Write Ouput', id='button'),
    html.Div('Place Holder', id='output')],
    id='data-initialize'
)

@app.callback(
    [Output('tab-page', 'children'),
    Output('solar_label', 'children')],
    [Input('data-initialize', 'children')])
def set_cost_analysis(x):
    '''
    x is not used
    the callback is should trigger on page-load
    '''
    # get values from app json to determine the selected models
    app_vals = helpers.json_load(cfg.app_json)
    # our table is determined by the 'solar' value
    s = app_vals['solar']
    # load the variables that will be used to make up the table
    # the DOE app will have a function to determine which file
    # to pull those values from
    avars = helpers.json_load(ajson)
    # fairly random appointment of what tables will be used
    if s == 'IPHD':
        table_vals = avars[:3]
    elif s == 'PT':
        table_vals = avars[3:8]
    else:
        table_vals = avars[8:]
    return (
        html.Div([
            dash_table.DataTable(
                id={'type': 'vartable', 'index': f"table-{i}"},
                #id={'type': 'vartable', 'index': f'{i}'},
                columns=cols,
                data=table_vals[i:i+3], 
                # css=[{"selector": ".show-hide", "rule": "display: none"}],
                style_cell_conditional=[
                {'if': {'column_id': 'DataType'},'display': 'none'}]
                # {'if': {'column_id': 'Label'},'width': '80%'},
            ) for i in range(0,len(table_vals),3)
        ]),
        #second return value
        f"Solar Model: {s}"
    )

            
@app.callback(
    Output('output','children'),
    [Input('button','n_clicks')],
    [State({'type':'vartable', 'index': ALL}, 'data')],
    prevent_initial_call=True
)
def update_model_variables_and_run_model(n_clicks, tableData): 
    #return(f"Table Data: {tableData}")
    tableVals = []
    tv=[]
    json={}
    # for e,x in enumerate(tableData):
    #     tableVals.append(html.Div(f"Table {e+1}: {x}"))
    for i in tableData:
        for j in i:
            tv.append(j)
            json[j['Name']]=j['Val']
    tableVals.append(html.Div(f"Table Data: {tableData}"))
    tableVals.append(html.Div(f"Also: {tv}"))
    tableVals.append(html.Div(f"Finally: {json}"))
    return(tableVals)


if __name__ == '__main__':
    app.run_server(debug=True)



