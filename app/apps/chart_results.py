import json
import numpy as np
import pandas as pd

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import app_config as cfg
import helpers

from app import app

app.title = 'Chart Results'

#
### GLOBALS 
#

HOURS_IN_YEAR = 8760
# Note: names need to match 'Name' values in the JSON
# solar_names = ('System power generated','Receiver mass flow rate',
#                 'Receiver thermal losses','Resource Beam normal irradiance')
# desal_names = ('Water production','Fossil fuel usage','Storage status')

# sumCols = {'System power generated','Irradiance GHI from weather file','Water production'}
# determine how weekly and monthly data is aggregated
# SUM if in sumCols set, else MEAN

solar_names = {'linear_fresnel_dsg_iph':('System power generated','Receiver mass flow rate','Receiver thermal losses','Resource Beam normal irradiance'),
               'SC_FPC':('Thermal power generation','Field outlet temperature'),
               'tcslinear_fresnel':('Condenser steam temperature','Steam mass flow rate', 'Waste heat generation'),
               'tcsdirect_steam':('Condenser steam temperature','Steam mass flow rate', 'Waste heat generation'),
               'trough_physical_process_heat':('Heat sink thermal power','Field total mass flow delivered', 'Receiver thermal losses','Resource Beam normal irradiance'),
               'pvsamv1':('System power generated','Irradiance GHI from weather file'),
               'tcstrough_physical':('Steam mass flow rate', 'Waste heat generation'),
               'tcsMSLF':('Steam mass flow rate', 'Waste heat generation'),
               'tcsmolten_salt':('Steam mass flow rate', 'Waste heat generation')}    
desal_names = {'FO': ('Water production','Storage status','Fossil fuel usage'),
               'RO': ('Water production','Storage status','Fossil fuel usage'),
               'VAGMD':('Water production','Fossil fuel usage', 'Storage status'),
               'LTMED':('Water production','Fossil fuel usage', 'Storage status'),
               'MEDTVC':('Water production','Fossil fuel usage', 'Storage status'),
               'MDB':('Water production','Fossil fuel usage', 'Storage status')}    
sumCols = {'Field total mass flow delivered','Heat sink thermal power','Thermal power generation','System power generated','Irradiance GHI from weather file','Water production','Receiver thermal losses','Fossil fuel usage','Steam mass flow rate','Waste heat generation'}


# #
### METHODS 
#

def aggregate_data(dataframe, variable, time):
    '''returns dataframe aggregated by selected time value'''
    if time == 'Hourly':
        return dataframe
    elif time == 'Daily': 
        if variable in sumCols:
            return dataframe.groupby(dataframe.index // 24).sum().round(2).reset_index()
        else:
            return dataframe.groupby(dataframe.index // 24).mean().round(2).reset_index()
    elif time == 'Weekly':
        if variable in sumCols:
            return dataframe.groupby(dataframe.index // 168).sum().round(2).reset_index()
        else:
            return dataframe.groupby(dataframe.index // 168).mean().round(2).reset_index()

def gen_title(variable, time):
    d = {'Hourly':'Hour', 'Daily':'Day', 'Weekly':'Week'}
    return f"{variable.title()} per {d[time]}"

#
### LAYOUT 
#

time_series = [{'label':' Hourly', 'value':'Hourly'},
               {'label':' Daily', 'value':'Daily'},
               {'label':' Weekly','value':'Weekly'}]

chart_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Charts"), active=True),
              dbc.NavItem(dbc.NavLink("Report", href='/analysis-report')),
              dbc.NavItem(dbc.NavLink("Results Map", href='/results-map'))],
    brand="Model Results",
    color="primary",
    dark=True,
    sticky='top',
    style={'margin-bottom':60}
)

def real_time_layout():
    solar_radios = html.Div([
        dbc.Row([
            dbc.Col(
                dcc.RadioItems(
                    id='select-solar-chart',
                    options=[{'label': f" {name}", 'value': name}
                            for name in solar_names[helpers.json_load(cfg.app_json)['solar']]],
                    value=solar_names[helpers.json_load(cfg.app_json)['solar']][0],
                    labelStyle = {'display': 'block'}),
                width=4),
            dbc.Col(
                dcc.RadioItems(
                    id='select-solar-time',
                    options=time_series,
                    value='Hourly',
                    labelStyle={'display': 'block'}),
            width=2)
        ], justify="center")
    ])
    
    desal_radios = html.Div([
        dbc.Row([
            dbc.Col(
                dcc.RadioItems(
                    id='select-desal-chart',
                    options=[{'label': f" {name}", 'value': name}
                            for name in desal_names[helpers.json_load(cfg.app_json)['desal']]],
                    value=desal_names[helpers.json_load(cfg.app_json)['desal']][0],
                    labelStyle = {'display': 'block'}),
                width=2),
            dbc.Col(
                dcc.RadioItems(
                    id='select-desal-time',
                    options=time_series,
                    value='Hourly',
                    labelStyle={'display': 'block'}),
            width=2)
        ], justify="center")
    ])
    
    chart_results_layout = html.Div([
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
    return chart_results_layout

#
### CALLBACKS 
#

@app.callback(
    Output('solar-storage', 'data'),
    [Input('initialize', 'children')])
def store_solar_data(x):

    # load simulation results from JSONs
    sol = helpers.json_load(cfg.sam_solar_simulation_outfile)

    solar_indexes = [helpers.index_in_list_of_dicts(sol,'Name', x)
                    for x in solar_names[helpers.json_load(cfg.app_json)['solar']]]
    solar_units = {sol[x]['Name']:sol[x]['Unit'] for x in solar_indexes}
    # the arrays all need to be the same size
    # creates dummy variables (zeros) if they are not
    # on failed runs of SamBaseClass the file can have empty values
    solar_arrays = []
    for x in solar_indexes:
        if len(sol[x]['Value']) == HOURS_IN_YEAR:
            solar_arrays.append(sol[x]['Value'])
        else:
            solar_arrays.append(np.zeros(HOURS_IN_YEAR))

    # combine results into list of series; note the .T for transpose,
    # otherwise the lists are read as rows, not columns. '''
    solar_array_data = np.array([pd.Series(x) for x in solar_arrays]).T

    # data frame of arrays, fortunately all the same shape!
    df_solar = pd.DataFrame(
            solar_array_data,
            columns = solar_names[helpers.json_load(cfg.app_json)['solar']]
    ).round(2)
    df = df_solar.to_dict()
    solarDict = {'units': solar_units, 'df_dict': df}
    return solarDict

@app.callback(
    Output('desal-storage', 'data'),
    [Input('initialize', 'children')])
def store_desal_data(x):
    alkup = helpers.json_load(cfg.app_json)
    flkup = cfg.build_file_lookup(alkup['solar'], alkup['desal'], 
                                  alkup['finance'])
    des = helpers.json_load(flkup['sam_desal_simulation_outfile'])

    desal_indexes = [helpers.index_in_list_of_dicts(des,'Name', x)
                    for x in desal_names[helpers.json_load(cfg.app_json)['desal']]]
    desal_arrays = [des[x]['Value'] for x in desal_indexes]
    desal_units = {des[x]['Name']:des[x]['Unit'] for x in desal_indexes}

    desal_array_data = np.array([pd.Series(x) for x in desal_arrays]).T

    # data frame of arrays, fortunately all the same shape!
    df_desal = pd.DataFrame(
            desal_array_data,
            columns = desal_names[helpers.json_load(cfg.app_json)['desal']]
    ).round(2)

    dfd = df_desal.to_dict()
    desalDict = {'units': desal_units, 'df_dict': dfd}
    return desalDict

@app.callback(
    Output('solar-graph','figure'),
    [Input('select-solar-chart', 'value'),
    Input('select-solar-time', 'value'),
    Input('solar-storage', 'data')])
def update_solar_graph(solarValue, timeAggValue, solarData):
    ''' update the solar figure object '''

    solar_units = solarData['units']
    df_solar = pd.DataFrame.from_dict(solarData['df_dict'])
    # change index from dict conversion from string back to int
    df_solar.index = df_solar.index.astype(int)
    df_tmp = aggregate_data(dataframe=df_solar, 
                            variable=solarValue,
                            time=timeAggValue)
    figure={
        'data': [
            {
                'x': df_tmp.index,
                'y': df_tmp[solarValue],
                'name': solarValue,
                'mode': 'bar',
                'marker': {'size': 10, 'color':'#2C3E50'},
            }],
        'layout': {
            'title': {'text':gen_title(solarValue,timeAggValue),
                      'font':{'color':'#2C3E50'}},
            'clickmode': 'event+select',
            'xaxis':{'title': '{} values'.format(timeAggValue)},
            'yaxis':{'title': solar_units[solarValue]},
        }
    }
    # print(solarValue)
    return figure

@app.callback(
    Output('desal-graph','figure'),
    [Input('select-desal-chart', 'value'),
    Input('select-desal-time', 'value'),
    Input('desal-storage', 'data')])
def update_desal_graph(desalValue, timeAggValue, desalData):
    ''' update the desal figure object '''

    desal_units = desalData['units']
    df_desal = pd.DataFrame.from_dict(desalData['df_dict'])
    # change index from dict conversion from string back to int
    df_desal.index = df_desal.index.astype(int)
    df_tmp = aggregate_data(dataframe=df_desal,
                            variable=desalValue,
                            time=timeAggValue)
    figure={
        'data': [
            {
                'x': df_tmp.index,
                'y': df_tmp[desalValue],
                'name': desalValue,
                'mode': 'bar',
                'marker': {'size': 12, 'color':'#2C3E50'},
            }
        ],
        'layout': {
            'title': {'text':gen_title(desalValue,timeAggValue),
                      'font':{'color':'#2C3E50'}},
            'clickmode': 'event+select',
            'xaxis':{'title': '{} values'.format(timeAggValue)},
            'yaxis':{'title': desal_units[desalValue]},
        }
    }
    return figure
