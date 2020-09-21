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

# To chart priority
# 1. "Total water production" from simulation_output files
# 2. "Levelized cost of water" from cost_output files

# from app import app
external_stylesheets = [dbc.themes.FLATLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

chart_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Charts"), active=True),
              dbc.NavItem(dbc.NavLink("Report", href='/analysis-report'))],
    brand="Parametric Study",
    color="primary",
    dark=True,
    style={'margin-bottom':60}
)

def real_time_layout():
    parametric_charts_layout = html.Div([
        html.Div(id='initialize'),
        chart_navbar,
        dcc.Store(id='solar-storage'),
        dcc.Store(id='desal-storage'),
        dbc.Container([ 
            html.H3('Levelized Cost of Water',className='text-success', 
            style={'margin-bottom':0, 'text-align':'center'}),
            dcc.Graph(id='parametric-desal-graph'),
            # solar_radios,
            # html.H3(cfg.Desal[helpers.json_load(cfg.app_json)['desal']], className='text-success',style={'margin-top':45, 'margin-bottom':0, 'text-align':'center'}),
            # dcc.Graph(id='desal-graph'),
            # desal_radios,
        ],style={'margin-bottom':150})
    ])    
    return parametric_study_layout

## CREATE STORE
# read in paramatric json to get variables and steps info 
# -this might be outside of the Store callback
# read in output JSONs to get values from each run
# store as lists
@app.callback(
    Output('desal-storage', 'data'),
    [Input('initialize', 'children')])
def store_desal_data(x):
    outf = 'VAGMD_cost_output_'
    var1 = 'desal_thermal_power_req'
    var1_steps = 3
    var2 = 'TEI_r'
    var2_steps = 4
    pr = Path('D:\GitHub\DOE_CSP_PROJECT\SAM_flatJSON\parametric_results')
    # read in files
    para_files=list(pr.glob(f'{outf}*'))
    # create empty dataframe
    df = pd.DataFrame(index=range(var1_steps),columns=range(var2_steps))
    # read through each file and add values to dataframe
    for pf in para_files:
        # extract the parametric study step numbers from the filenames
        steps = [int(s) for s in re.findall('\d+', str(pf))]
        # load the json
        para_dict = helpers.json_load(pf)
        # find the specific value for the variable
        index = helpers.index_in_list_of_dicts(para_dict,'Name','Levelized cost of water')
        # and update the dataframe
        df.at[steps[0],steps[1]]=para_dict[index]['Value']
    return df.to_dict()


@app.callback(
    Output('parametric-desal-graph','figure'),
    # [Input('select-desal-chart', 'value'),
    # Input('select-desal-time', 'value'),
    # Input('desal-storage', 'data')])
    [Input('desal-storage', 'data')])
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
    dd = pd.DataFrame.from_dict(desalData)
    fig = px.bar(dd, barmode='group')
    return fig



app.layout = parametric_charts_layout
if __name__ == '__main__':
    app.run_server(debug=True)





