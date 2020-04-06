# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 12:12:09 2020

App with radio button groups that allow user to select a solar thermal, 
desalination and financial model combination to run.

@author: jsquires
"""

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import sys

from dash.dependencies import Input, Output
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent.absolute()
sys.path.insert(0,str(base_path))

# dict for desalination 'values' and 'labels'
Desal = {'FOR':'Forward Osmosis                          ',
         'VAM':'Vacuum Air Gap Membrane Distillation     ',
         'MED':'Low Temperature Multi-Effect Distillation', 
         'ABS':'MED with Absorption Heat Pumps           ',
         'TLV':'MED with Thermal Vapor Compression       ',
         'MBD':'Membrane Distillation                    ',
         'NUN':'No Desalination Model                    ',
         'ROM':'Reverse Osmosis                          ', 
         }

#dict for financial model 'values' and 'labels' 
Financial = {'COMML':'Commercial (Distributed)                   ',
             'LCOE' :'Levelized Cost of Electricity Calculator   ',
             'LCOH' :'Levelized Cost of Heat Calculator          ',
             'NONE' :'No Financial Model                         ',
             'PPFWD':'PPA Partnership Flip With Debt (Utility)   ',
             'PPFWO':'PPA Partnership Flip Without Debt (Utility)',
             'PPALS':'PPA Sale Leaseback (Utility)               ',
             'PPASO':'PPA Single Owner (Utility)                 ',
             }

# NOTE: make sure any changes in this table are also reflected in app.layout
# dict for solar/CSP 'values' and 'labels'
Solar = {'FPC ':'Flat-Plate Collector',
         'IPHP':'Industrial Process Heat Parabolic Trough   ',
         'IPHD':'Industrial Process Heat Linear Direct Steam',
         'ISCC':'Integrated Solar Combined Cycle ',
         'DSLF':'Linear Fresnel Direct Steam     ',
         'MSLF':'Linear Fresnel Molten Salt      ',
         'DSPT':'Power Tower Direct Steam        ',
         'MSPT':'Power Tower Molten Salt         ',
         'PT  ':'Parabolic Trough Physical       ',
          }

#dict containing the desalination options ('value' and 'disabled') after solar model chosen
solarToDesal = {
    'FPC' : [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'IPHP': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'IPHD': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'ISCC': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'DSLF': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'MSLF': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'DSPT': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'MSPT': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'PT'  : [('FOR',True),('VAM',False),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    }

#dict containing the finance options ('value' and 'disabled') after desal model chosen
solarToFinance = {
    'FPC': [('COMML',True),('LCOE',True),('LCOH',True),('NONE',True),('PPFWD',True),('PPFWO',True),('PPALS',True),('PPASO',True)],
    'IPHP': [('COMML',True),('LCOE',True),('LCOH',False),('NONE',False),('PPFWD',True),('PPFWO',True),('PPALS',True),('PPASO',True)],
    'IPHD': [('COMML',True),('LCOE',True),('LCOH',False),('NONE',False),('PPFWD',True),('PPFWO',True),('PPALS',True),('PPASO',True)],
    'ISCC': [('COMML',True),('LCOE',True),('LCOH',True),('NONE',True),('PPFWD',True),('PPFWO',True),('PPALS',True),('PPASO',False)],
    'DSLF': [('COMML',False),('LCOE',False),('LCOH',True),('NONE',False),('PPFWD',False),('PPFWO',False),('PPALS',False),('PPASO',False)],
    'MSLF': [('COMML',False),('LCOE',False),('LCOH',True),('NONE',False),('PPFWD',False),('PPFWO',False),('PPALS',False),('PPASO',False)],
    'DSPT': [('COMML',True),('LCOE',True),('LCOH',True),('NONE',True),('PPFWD',False),('PPFWO',False),('PPALS',False),('PPASO',False)],
    'MSPT': [('COMML',True),('LCOE',True),('LCOH',True),('NONE',True),('PPFWD',False),('PPFWO',False),('PPALS',False),('PPASO',False)],
    'PT'  : [('COMML',False),('LCOE',False),('LCOH',True),('NONE',False),('PPFWD',False),('PPFWO',False),('PPALS',False),('PPASO',False)],
    }

#dict containing Solar / Finance combinations
solarFinance = {('PT','PPASO')  :'tcstrough_physical_singleowner',
                 ('PT','PPFWD')  :'tcstrough_physical_levpartflip',
                 ('PT','COMML')  :'tcstrough_physical_utilityrate5',
                 ('PT','PPFWO')  :'tcstrough_physical_equpartflip',
                 ('PT','LCOE')   :'tcstrough_physical_lcoefcr',
                 ('PT','PPALS')  :'tcstrough_physical_saleleaseback',
                 ('PT','NONE')   :'tcstrough_physical_none',
                 ('DSLF','PPASO'):'tcslinear_fresnel_singleowner',
                 ('DSLF','PPFWD'):'tcslinear_fresnel_levpartflip',
                 ('DSLF','COMML'):'tcslinear_fresnel_utilityrate5',
                 ('DSLF','PPFWO'):'tcslinear_fresnel_equpartflip',
                 ('DSLF','LCOE') :'tcslinear_fresnel_lcoefcr',
                 ('DSLF','PPALS'):'tcslinear_fresnel_saleleaseback',
                 ('DSLF','NONE') :'tcslinear_fresnel_none',
                 ('MSLF','PPASO'):'tcsMSLF_singleowner',
                 ('MSLF','PPFWD'):'tcsMSLF_levpartflip',
                 ('MSLF','COMML'):'tcsMSLF_utilityrate5',
                 ('MSLF','PPFWO'):'tcsMSLF_equpartflip',
                 ('MSLF','LCOE') :'tcsMSLF_lcoefcr',
                 ('MSLF','PPALS'):'tcsMSLF_saleleaseback',
                 ('MSLF','NONE') :'tcsMSLF_none',
                 ('MSPT','PPASO'):'tcsmolten_salt_singleowner',
                 ('MSPT','PPFWD'):'tcsmolten_salt_levpartflip',
                 ('MSPT','PPFWO'):'tcsmolten_salt_equpartflip',
                 ('MSPT','PPALS'):'tcsmolten_salt_saleleaseback',
                 ('DSPT','PPASO'):'tcsdirect_steam_singleowner',
                 ('DSPT','PPFWD'):'tcsdirect_steam_levpartflip',
                 ('DSPT','PPFWO'):'tcsdirect_steam_equpartflip',
                 ('DSPT','PPALS'):'tcsdirect_steam_saleleaseback',
                 ('ISCC','PPASO'):'tcsiscc_singleowner',
                 ('IPHP','LCOH') :'trough_physical_process_heat_iph_to_lcoefcr',
                 ('IPHP','NONE') :'trough_physical_process_heat_none',
                 ('IPHD','LCOH') :'linear_fresnel_dsg_iph_iph_to_lcoefcr',
                 ('IPHD','NONE') :'linear_fresnel_dsg_iph_none',    
    }

external_stylesheets = [dbc.themes.FLATLY,'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
app.title = 'Model Selection'

model_selection_layout = html.Div([
    html.Div([
        html.Div([    
            html.B(html.Label('Solar Thermal System')),
            dcc.RadioItems(
                id='select-solar',
                options=[
                    {'label': 'Flat-Plate Collector            ', 'value': 'FPC',  'disabled': True},
                    {'label': 'Integrated Solar Combined Cycle ', 'value': 'ISCC', 'disabled': False},
                    {'label': 'Linear Fresnel Direct Steam     ', 'value': 'DSLF', 'disabled': False},
                    {'label': 'Linear Fresnel Molten Salt      ', 'value': 'MSLF', 'disabled': False},
                    {'label': 'Parabolic Trough Physical       ', 'value': 'PT'  , 'disabled': False},
                    {'label': 'Power Tower Direct Steam        ', 'value': 'DSPT', 'disabled': False},
                    {'label': 'Power Tower Molten Salt         ', 'value': 'MSPT', 'disabled': False},
                    {'label': 'Process Heat Parabolic Trough   ', 'value': 'IPHP', 'disabled': False},
                    {'label': 'Process Heat Linear Direct Steam', 'value': 'IPHD', 'disabled': False}, 
                ],value='DSLF',
            )
        ]),
        html.P(),
        html.Div([
            html.B(html.Label('Desalination System')),
            dcc.RadioItems(id='select-desal',value='ABS'),
        ]),
        html.P(),
        html.Div([
            html.B(html.Label('Financial Model')),
            dcc.RadioItems(id='select-finance'),
        ]),
        html.P(),
        html.Div([
            html.Div(id='model-parameters'),
        ]),
    ],className='three columns'),
])

# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/model-selection':
        return model_selection_layout
    elif pathname == '/model-variables':
        return html.h5('Please run the display-model-variables app')
    else:
        return html.H5('404 URL not found')
  
# when all three models have been selected a button is displayed to bring the user
# to the model variables page
@app.callback(
    Output('model-parameters', 'children'),
    [Input('select-solar', 'value'),
     Input('select-desal', 'value'),
     Input('select-finance', 'value')])
def display_model_parameters(solar, desal, finance):
    if model and desal and finance:
        pickle_model_selection(solar,desal,finance)
        return html.Div([
            html.P(),
            dcc.Link(html.Button('Next'), href='/model-variables'),
        ])
    
# display desal model options after solar model has been selected
@app.callback(
    Output('select-desal', 'options'),
    [Input('select-solar', 'value')])
def set_desal_options(solarModel):
    return [{'label': Desal[i[0]], 'value': i[0], 'disabled': i[1]} for i in solarToDesal[solarModel]]

#TODO combine with select-desal above?
@app.callback(
    Output('select-finance', 'options'),
    [Input('select-solar', 'value')])
def set_finance_options(desalModel):
    return [{'label': Financial[i[0]], 'value': i[0], 'disabled': i[1]} for i in solarToFinance[desalModel]]