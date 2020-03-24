import sys
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import app_config as cfg
sys.path.insert(0,str(cfg.base_path))

import helpers
from app import app

app.title = "Analysis Report"

analysis_report_title = html.Div([
    html.H2('Analysis Report', className='page-header', id='report-title'),
    html.P(id='data-initialize')])

local_condition = dbc.CardBody(id='local-condition')

desal_config = dbc.CardBody(id='desal-config')

solar_config = dbc.CardBody(id='solar-config')

system_performance = dbc.CardBody(id='system-performance')

cost_analysis = dbc.CardBody(id='cost-analysis')

system_description = dbc.Card([dbc.CardHeader(html.H4('System Description')),local_condition, desal_config, solar_config], id='system-description', color='primary', inverse=True)

simulation_results = dbc.Card([dbc.CardHeader(html.H4('Simulation Results')),system_performance, cost_analysis], id='simulation-results', color='dark', inverse=True)

analysis_report_layout = [analysis_report_title, 
                          dbc.CardDeck([system_description, simulation_results])]

@app.callback(
    Output('data-initialize', 'children'),
    [Input('report-title', 'children')])
def gather_data(x):
    '''initial callback to gather data for callbacks chained below
    updates app_json dict with all values needed for analysis report
    '''
    # initialize with all data from map_json
    updates = helpers.json_load(cfg.map_json)
    # add all data from app_json
    updates.update(helpers.json_load(cfg.app_json))
    # add specific data from desalination GUI output
    d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
    fossil_fuel = "Yes" if d['Fossil_f'] else "No"
    updates.update({'FeedC_r':d['FeedC_r'],
                    'Capacity':d['Capacity'],
                    'storage_hour':d['storage_hour'],
                    'fossil_fuel': fossil_fuel})
    # add specific data from desal simulation output
    ds = helpers.json_load(cfg.sam_desal_simulation_outfile)
    index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
    updates.update({'thermal_storage_capacity':ds[index]['Value']})
    # add specific data from desal design output
    dd = helpers.json_load(cfg.desal_design_infile)
    index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power consumption')
    updates.update({'thermal_power_consumption':ds[index]['Value']})
    index = helpers.index_in_list_of_dicts(dd,'Name','Specific thermal power consumption') 
    updates.update({'specific_thermal_power_consumption':dd[index]['Value']})
    index = helpers.index_in_list_of_dicts(dd,'Name','Gained output ratio')
    updates.update({'gained_output_ratio':dd[index]['Value']})
    # add specific data from desal cost output
    dc = helpers.json_load(cfg.sam_desal_finance_outfile)
    index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
    updates.update({'lcow':dc[index]['Value']})
    index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat')
    updates.update({'lcoh':dc[index]['Value']})
    index = helpers.index_in_list_of_dicts(dc,'Name','Desal CAPEX')
    updates.update({'capital_cost':dc[index]['Value']})
    index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
    updates.update({'ops_cost':dc[index]['Value']})
    # add specific data from solar GUI output
    s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
    updates.update({'q_pb_des':s['q_pb_des']})
    f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
    updates.update({'electric_energy_consumption':f['SEEC']})
    updates.update({'lcoe':f['coe']})

    # finally create the report json
    helpers.initialize_json(updates,cfg.report_json)
    return ''

@app.callback(
    Output('local-condition', 'children'),
    [Input('data-initialize', 'children')])
def set_local_condition(x):
    try:
        r = helpers.json_load(cfg.report_json)
    except FileNotFoundError:
        return None
    return ([
    html.H5('Local Condition', className='card-title'),
    html.Div(f"Location: {r['county']}, {r['state']}"),
    html.Div(f"Daily average DNI: {r['dni']}"),
    html.Div(f"Daily average GHI: {r['ghi']}"),
    html.Div(f"Feedwater salinity: {r['FeedC_r']}"),
    html.Div(f"Market water price: ${r['water_price']}"), 
    html.Div(f"Distance to nearest desalination plant: {r['dist_desal_plant']} km"),
    html.Div(f"Distance to nearest water network: {r['dist_water_network']} km"),
    html.Div(f"Distance to nearest power plant: {r['dist_power_plant']} km")
    ])

@app.callback(
    Output('desal-config', 'children'),
    [Input('data-initialize', 'children')])
def set_desal_config(x):
    r = helpers.json_load(cfg.report_json)
    return ([
    html.H5('Desalination System Configuration', className='card-title'),
    html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
    html.Div(f"Design capacity: {r['Capacity']}"),
    html.Div(f"Thermal storage hour: {r['storage_hour']}"),
    html.Div(f"Thermal storage capacity: {r['thermal_storage_capacity']}"),
    html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
    html.Div(f"Specific thermal energy consumption: {r['specific_thermal_power_consumption']}"),
    html.Div(f"Required thermal energy: {r['thermal_power_consumption']}"),
    html.Div(f"Required electric energy {r['electric_energy_consumption']}")
    ])

@app.callback(
    Output('solar-config', 'children'),
    [Input('data-initialize', 'children')])
def set_solar_config(x):
    r = helpers.json_load(cfg.report_json)
    return ([
    html.H5('Solar Field Configuration', className='card-title'),
    html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
    html.Div(f"Design thermal energy production: {r['q_pb_des']}"),
    ])

@app.callback(
    Output('system-performance', 'children'),
    [Input('data-initialize', 'children')])
def set_system_performance(x):
    r = helpers.json_load(cfg.report_json)
    return ([
    html.H5('System Performance', className='card-title'),
    html.Div(f"Gained output ratio: {r['gained_output_ratio']}"),
    ])

@app.callback(
    Output('cost-analysis', 'children'),
    [Input('data-initialize', 'children')])
def set_cost_analysis(x):
    r = helpers.json_load(cfg.report_json)
    return ([
    html.H5('Cost Analysis', className='card-title'),
    html.Div(f"Levelized cost of water (LCOW): {r['lcow']}"),
    html.Div(f"Levelized cost of heat (LCOH): {r['lcoh']}"),
    html.Div(f"Levelized cost of energy (LCOE): {r['lcoe']}"),
    html.Div(f"Capital cost: {r['capital_cost']}"),
    html.Div(f"Operational and Maintenance cost: {r['ops_cost']}"),
    ])
