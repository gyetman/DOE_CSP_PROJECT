import json
import numpy as np
import pandas as pd

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import ../app_config as cfg
import helpers

from app import app

chart_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Charts"), active=True),
              dbc.NavItem(dbc.NavLink("Report", href='/analysis-report'))],
    brand="Model Results",
    color="primary",
    dark=True,
    style={'margin-bottom':60}
)

parametric_study_layout = html.Div([
    html.Div(id='initialize'),
    chart_navbar,
    dcc.Store(id='solar-storage'),
    dcc.Store(id='desal-storage'),
    dbc.Container([ 
        html.H3(cfg.Solar[helpers.json_load(cfg.app_json)['solar']], className='text-success', style={'margin-bottom':0, 'text-align':'center'}),
        dcc.Graph(id='solar-graph'),
        solar_radios,
        html.H3(cfg.Desal[helpers.json_load(cfg.app_json)['desal']], className='text-success',style={'margin-top':45, 'margin-bottom':0, 'text-align':'center'}),
        dcc.Graph(id='desal-graph'),
        desal_radios,
    ],style={'margin-bottom':150})
])    
# return parametric_study_layout

## CREATE STORE
# read in paramatric json to get variables and steps info 
# -this might be outside of the Store callback
# read in output JSONs to get values from each run
# store as lists
var1 = 'desal_thermal_power_req'
var2 = 'TEI_r'
pr = Path('D:\GitHub\DOE_CSP_PROJECT\SAM_flatJSON\parametric_results')





