import sys
from pathlib import Path

import dash_bootstrap_components as dbc
#import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output

import app_config as cfg
sys.path.insert(0,str(cfg.base_path))

import helpers
from app import app

#define columns used in data tables
cols = [{'name':'Variable', 'id':'Label','editable':False},
        {'name':'Value',    'id':'Value','editable':True},
        {'name':'Units',    'id':'Units','editable':False}]

chart_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Home", href='/home')),
              dbc.NavItem(dbc.NavLink("Models"), active=True)],
    brand="Model Selection",
    color="primary",
    dark=True,
    sticky='top',
    style={'margin-bottom':60}
)

model_selection_layout = html.Div([
    chart_navbar,
    dbc.Label("Project Name", width=2, size='lg',style={'text-align':'center'}),
    dcc.Input(  id='project_name',
                value = 'Project_1',
                type="text",
            ),    
   
    dbc.FormGroup([
        dbc.Label("Solar Thermal System", width=2, size='lg',color='warning',style={'text-align':'center'}),
        dbc.Col(
            dbc.RadioItems(
                id='select-solar',
                options=[
                    {'label': 'Photovoltaic (PVWatts)   ',
                    'value': 'pvwattsv7', 'disabled': False},
                    {'label': 'Photovoltaic (Detailed)   ',
                    'value': 'pvsamv1', 'disabled': False},
                    {'label': 'Static Collector (Flat Plate)   ',
                    'value': 'SC_FPC', 'disabled': False},
                    {'label': 'Static Collector (Evacuated Tube)',
                    'value': 'SC_ETC', 'disabled': False},
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
                    {'label': 'Industrial Process Heat Parabolic Trough   ',
                    'value': 'trough_physical_process_heat', 'disabled': False},
                    {'label': 'Industrial Process Heat Linear Fresnel Direct Steam',
                    'value': 'linear_fresnel_dsg_iph', 'disabled': False}, 
                ],
                value='linear_fresnel_dsg_iph',
            ),width=10,
        ),
    ],row=True),
    dbc.FormGroup([
        #dbc.Label("Desalination System", width=2, size='lg',color='success',style={'text-align':'center'}),
        dbc.Label("Desalination System",width=2, size='lg',color='info',style={'text-align':'center'}),
        dbc.Col(
            dbc.RadioItems(
                id='select-desal',
            ),width=10,
        ),
    ],row=True,),
    dbc.FormGroup([
        dbc.Label("Financial Model",width=2, size='lg',color='success',style={'text-align':'center'}),
        dbc.Col(
            dbc.RadioItems(
                id='select-finance',
            ),width=10,
        ),
    ],row=True,),
    dbc.FormGroup([
        dbc.Label("Parametric Study",width=2, size='lg',color='primary',style={'text-align':'center', 'padding':0}),
        dbc.Col(
            dbc.Checklist(
                options=[{'label': 'Enable Parametric Study Option', 'value':True}],
                id='parametric-toggle',
                switch=True,
            ),width=10,
        ),
    ],row=True, inline=True), 
    dbc.Col(id='model-parameters',
    width=2, 
    style={'horizontal-align':'center'})
],style={'margin-bottom':150})





@app.callback(
    Output('model-parameters', 'children'),
    [Input('select-solar', 'value'),
     Input('select-desal', 'value'),
     Input('select-finance', 'value'),
     Input('parametric-toggle', 'value'),
     Input('project_name', 'value')])
def display_model_parameters(solar, desal, finance, parametric, project_name):
    '''
    After all 3 models are selected updates app JSON file and 
    creates button to navigate to model variables page
    '''
    if solar and desal and finance:
        toggle=True if parametric else False
        try:
            helpers.json_update(data={'solar':solar, 'desal':desal, 'finance':finance, 'parametric':toggle, 'project_name': project_name, 'timestamp': '2021-06-19_10-03-11'}, filename=cfg.app_json)
        except FileNotFoundError:
            helpers.initialize_json(cfg.app_json_init,cfg.app_json)
            helpers.json_update(data={'solar':solar, 'desal':desal, 'finance':finance, 'parametric':toggle, 'project_name': project_name, 'timestamp': '2021-06-19_10-03-11'}, filename=cfg.app_json)
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
