import sys
from collections import defaultdict
from datetime import datetime
from operator import itemgetter
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State

import app_config as cfg
sys.path.insert(0,str(cfg.base_path))

import helpers
from app import app

from SAM_flatJSON.SamBaseClass import SamBaseClass

#define columns used in data tables
cols = [{'name':'Variable', 'id':'Label','editable':False},
        {'name':'Value',    'id':'Value','editable':True},
        {'name':'Units',    'id':'Units','editable':False}]

app.title = 'Model Selection'

model_selection_layout = html.Div([
    dbc.FormGroup([
        dbc.Label("Solar Thermal System", width=2, size='lg',color='warning',style={'text-align':'center'}),
        dbc.Col(
            dbc.RadioItems(
                id='select-solar',
                options=[
                    {'label': 'Static Collector                ',
                    'value': 'StaticCollector_iph', 'disabled': False},
                    {'label': 'Integrated Solar Combined Cycle ',
                    'value': 'tcsiscc', 'disabled': False},
                    {'label': 'Linear Fresnel Direct Steam     ',
                    'value': 'tcslinear_fresnel', 'disabled': False},
                    {'label': 'Linear Fresnel Molten Salt      ',
                    'value': 'tcsMSLF', 'disabled': False},
                    {'label': 'Parabolic Trough Physical       ',
                    'value': 'tcstrough_physical', 'disabled': False},
                    {'label': 'Power Tower Direct Steam        ',
                    'value': 'tcsdirect_steam', 'disabled': False},
                    {'label': 'Power Tower Molten Salt         ',
                    'value': 'tcsmolten_salt', 'disabled': False},
                    {'label': 'Process Heat Parabolic Trough   ',
                    'value': 'trough_physical_process_heat', 'disabled': False},
                    {'label': 'Process Heat Linear Direct Steam',
                    'value': 'linear_fresnel_dsg_iph', 'disabled': False}, 
                ],
                value='tcslinear_fresnel',
            ),width=10,
        ),
    ],row=True),
    dbc.FormGroup([
        #dbc.Label("Desalination System", width=2, size='lg',color='success',style={'text-align':'center'}),
        dbc.Label("Desalination System",width=2, size='lg',color='success',style={'text-align':'center'}),
        dbc.Col(
            dbc.RadioItems(
                id='select-desal',
            ),width=10,
        ),
    ],row=True,),
    dbc.FormGroup([
        dbc.Label("Financial Model",width=2, size='lg',color='primary',style={'text-align':'center'}),
        dbc.Col(
            dbc.RadioItems(
                id='select-finance',
            ),width=10,
        ),
    ],row=True,),
    dbc.Col(id='model-parameters',
    width=2, 
    style={'horizontal-align':'center'})
])

@app.callback(
    Output('model-parameters', 'children'),
    [Input('select-solar', 'value'),
     Input('select-desal', 'value'),
     Input('select-finance', 'value')])
def display_model_parameters(solar, desal, finance):
    '''
    After all 3 models are selected updates app JSON file and 
    creates button to navigate to model variables page
    '''
    if solar and desal and finance:
        try:
            helpers.json_update(data={'solar':solar, 'desal':desal, 'finance':finance}, filename=cfg.app_json)
        except FileNotFoundError:
            helpers.initialize_json(cfg.app_json_init,cfg.app_json)
            helpers.json_update(data={'solar':solar, 'desal':desal, 'finance':finance}, filename=cfg.app_json)
        return html.Div([
            html.P(),
            dcc.Link(dbc.Button("Next", color="primary", block=True, size='lg'), href='/model-variables')])
  
# display desal model options after solar model has been selected
@app.callback(
    Output('select-desal', 'options'),
    [Input('select-solar', 'value')])
def set_desal_options(solarModel):
    return [{'label': cfg.Desal[i[0]], 'value': i[0], 'disabled': i[1]} for i in cfg.solarToDesal[solarModel]]

#TODO combine with select-desal above?
@app.callback(
    Output('select-finance', 'options'),
    [Input('select-solar', 'value')])
def set_finance_options(desalModel):
    return [{'label': cfg.Financial[i[0]], 'value': i[0], 'disabled': i[1]} for i in cfg.solarToFinance[desalModel]]
