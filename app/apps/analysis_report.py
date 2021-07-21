import sys
from pathlib import Path
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import app_config as cfg
sys.path.insert(0,str(cfg.base_path))

import helpers
from app import app

import pandas as pd 
app.title = "Analysis Report"

chart_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Home", href='/home')),
              dbc.NavItem(dbc.NavLink("Charts", href='/chart-results')),
              dbc.NavItem(dbc.NavLink("Report"), active=True),
              dbc.NavItem(dbc.NavLink("Results Map", href='/results-map')),
              html.P(id='data-initialize')],
    brand="Analysis Report",
    color="primary",
    dark=True,
    sticky='top',
    style={'margin-bottom':60},  
    id='report-title'
)

# analysis_report_title = html.Div([
#     html.H2('Analysis Report', className='page-header', id='report-title'),
#     html.P(id='data-initialize')])

local_condition = dbc.CardBody(id='local-condition')

desal_config = dbc.CardBody(id='desal-config')

solar_config = dbc.CardBody(id='solar-config')

system_performance = dbc.CardBody(id='system-performance')

sam_performance = dbc.CardBody(id='sam-performance')

cost_analysis = dbc.CardBody(id='cost-analysis')

system_description = dbc.Card([dbc.CardHeader(html.H4('System Description')),local_condition, desal_config, solar_config], id='system-description', color='primary', inverse=True)

simulation_results = dbc.Card([dbc.CardHeader(html.H4('Simulation Results')),system_performance, sam_performance, cost_analysis], id='simulation-results', color='dark', inverse=True)

analysis_report_layout = [chart_navbar, 
                          dbc.Container(dbc.CardDeck([system_description, simulation_results]),style={'margin-bottom':150})]

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
    # create the file lookup dict for dynamic file names
    flkup = cfg.build_file_lookup(updates['solar'], updates['desal'], updates['finance'],updates['timestamp'])
    
    if updates['desal'] == 'VAGMD':
    # add specific data from desalination GUI output
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        fossil_fuel = "Yes" if d['Fossil_f'] else "No"
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['Capacity'],
                        'storage_hour':d['storage_hour'],
                        'fossil_fuel': fossil_fuel})
        # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total fossil fuel usage')
        updates.update({'fossil_usage':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar thermal energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed energy')
        updates.update({'curtail_p':ds[index]['Value']})         
        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power requirement')
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific thermal power consumption') 
        updates.update({'specific_thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Gained output ratio')
        updates.update({'gained_output_ratio':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Number of modules required')
        updates.update({'n_modules':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Recovery ratio')
        updates.update({'RR':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Brine concentration')
        updates.update({'p_brine':dd[index]['Value']})
        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from fossile fuel)')
        updates.update({'lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from solar field)')
        updates.update({'sam_lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Energy cost')
        updates.update({'energy_cost':dc[index]['Value']})
        


        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'electric_energy_consumption':f['SEEC']})
        updates.update({'lcoe':f['coe']})
    elif updates['desal'] == 'MDB':
    # add specific data from desalination GUI output
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        fossil_fuel = "Yes" if d['Fossil_f'] else "No"
        m_type = "AS7C1.5L" if d['module']==0 else "AS26C2.7L"
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['Capacity'],
                        'storage_hour':d['storage_hour'],
                        'fossil_fuel': fossil_fuel,
                        'm_type': m_type}
                       )
        # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total fossil fuel usage')
        updates.update({'fossil_usage':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar thermal energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed energy')
        updates.update({'curtail_p':ds[index]['Value']})   
        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power requirement')
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific thermal power consumption') 
        updates.update({'specific_thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Gained output ratio')
        updates.update({'gained_output_ratio':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Number of modules required')
        updates.update({'n_modules':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Actual recovery rate')
        updates.update({'RR':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Number of modules required')
        updates.update({'n_modules':dd[index]['Value']}) 
        index = helpers.index_in_list_of_dicts(dd,'Name','Brine concentration')
        updates.update({'p_brine':dd[index]['Value']}) 
        
        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from fossile fuel)')
        updates.update({'lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from solar field)')
        updates.update({'sam_lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Energy cost')
        updates.update({'energy_cost':dc[index]['Value']})
        


        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'electric_energy_consumption':f['SEEC']})
        updates.update({'lcoe':f['coe']})        
    ## Temporal 'if' condition for another desal technology
    elif updates['desal'] == 'LTMED' :
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        fossil_fuel = "Yes" if d['Fossil_f'] else "No"
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['Capacity'],
                        'storage_hour':d['storage_hour'],
                        'fossil_fuel': fossil_fuel})
        # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total fossil fuel usage')
        updates.update({'fossil_usage':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar thermal energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed energy')
        updates.update({'curtail_p':ds[index]['Value']})   
        
        
        # add data from desal design input
        ddin = helpers.json_load(flkup['desal_design_outfile'])
        updates.update({'RR':ddin['RR'] })        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power requirement')
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific thermal power consumption') 
        updates.update({'specific_thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Gained output ratio')
        updates.update({'gained_output_ratio':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Brine concentration')
        updates.update({'p_brine':dd[index]['Value']})

        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from fossile fuel)')
        updates.update({'lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from solar field)')
        updates.update({'sam_lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Energy cost')
        updates.update({'energy_cost':dc[index]['Value']})
        
        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'electric_energy_consumption':f['SEEC']})
        updates.update({'lcoe':f['coe']})

    elif updates['desal'] == 'ABS':
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        fossil_fuel = "Yes" if d['Fossil_f'] else "No"
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['Capacity'],
                        'storage_hour':d['storage_hour'],
                        'fossil_fuel': fossil_fuel})
        # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total fossil fuel usage')
        updates.update({'fossil_usage':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar thermal energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed energy')
        updates.update({'curtail_p':ds[index]['Value']})         
        
        
        # add data from desal design input
        ddin = helpers.json_load(flkup['desal_design_outfile'])
        updates.update({'RR':ddin['RR'] * 100}) 
    
        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power requirement')
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific thermal power consumption') 
        updates.update({'specific_thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Gained output ratio')
        updates.update({'gained_output_ratio':dd[index]['Value']})       
        index = helpers.index_in_list_of_dicts(dd,'Name','Brine concentration')
        updates.update({'p_brine':dd[index]['Value']})    

        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from fossile fuel)')
        updates.update({'lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from solar field)')
        updates.update({'sam_lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Energy cost')
        updates.update({'energy_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Absorption heat pump capital cost')
        updates.update({'AHP_cost':dc[index]['Value']})
        
        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'electric_energy_consumption':f['SEEC']})
        updates.update({'lcoe':f['coe']})        
        
    elif updates['desal'] == 'MEDTVC':
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        fossil_fuel = "Yes" if d['Fossil_f'] else "No"
        # add data from desal design input
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['Capacity'],
                        'storage_hour':d['storage_hour'],
                        'fossil_fuel': fossil_fuel,
                        'RR': d['rr']})
        # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total fossil fuel usage')
        updates.update({'fossil_usage':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar thermal energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed energy')
        updates.update({'curtail_p':ds[index]['Value']}) 
        
        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power requirement')
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific thermal power consumption') 
        updates.update({'specific_thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Gained output ratio')
        updates.update({'gained_output_ratio':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Brine concentration')
        updates.update({'p_brine':dd[index]['Value']})

        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from fossile fuel)')
        updates.update({'lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from solar field)')
        updates.update({'sam_lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Energy cost')
        updates.update({'energy_cost':dc[index]['Value']})
        
        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'electric_energy_consumption':f['SEEC']})
        updates.update({'lcoe':f['coe']})        
    elif updates['desal'] == 'RO':
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        fossil_fuel = "Yes" if d['Fossil_f'] else "No"
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['nominal_daily_cap_tmp'],
                        'storage_hour':d['storage_hour'],
                        'fossil_fuel': fossil_fuel,
                        'RR': d['R1'] * 100})
        # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total fossil fuel usage')
        updates.update({'fossil_usage':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar electric energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed energy')
        updates.update({'curtail_p':ds[index]['Value']})         
        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Number of vessels')
        updates.update({'number_vessels':dd[index]['Value']})        
        index = helpers.index_in_list_of_dicts(dd,'Name','Electric energy requirement')
        updates.update({'electric_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific energy consumption') 
        updates.update({'specific_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Brine concentration')
        updates.update({'p_brine':dd[index]['Value']})


        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal Annualized CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Energy cost')
        updates.update({'energy_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of electricity (from solar field)')
        updates.update({'sam_lcoe':dc[index]['Value']})        
        
        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'lcoe':f['coe']})

        
    elif updates['desal'] == 'RO_FO':
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['capacity']
                        })
        # # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        # index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        # updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total grid electricity usage')
        updates.update({'grid_usage':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total external thermal energy usage')
        updates.update({'external_heat':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of grid electricity consumption')
        updates.update({'grid_percent':ds[index]['Value']})
        updates.update({'elec_solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of external fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'thermal_solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar thermal energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed thermal energy')
        updates.update({'curtail_p':ds[index]['Value']})         
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar electric energy')
        updates.update({'curtail2':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed electric energy')
        updates.update({'curtail2_p':ds[index]['Value']}) 
        
        # # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Overall recovery rate')
        updates.update({'RR':dd[index]['Value']})        
        index = helpers.index_in_list_of_dicts(dd,'Name','Electric energy requirement')
        updates.update({'electric_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power requirement') 
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','RO capacity')
        updates.update({'RO_capacity':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','FO capacity') 
        updates.update({'FO_capacity':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','FO brine salinity')
        updates.update({'p_brine':dd[index]['Value']})


        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal Annualized CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Annual water production')
        updates.update({'water_prod':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of electricity (from solar field)')
        updates.update({'sam_lcoe':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from solar field)')
        updates.update({'sam_lcoh':dc[index]['Value']})

        
        # add from cost input 
        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'lcoe':f['coe']})
        updates.update({'lcoh':f['coh']})
        
        # add from 
       
    elif updates['desal'] == 'RO_MDB':
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['capacity']
                        })
        # # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        # index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        # updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total grid electricity usage')
        updates.update({'grid_usage':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total external thermal energy usage')
        updates.update({'external_heat':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of grid electricity consumption')
        updates.update({'grid_percent':ds[index]['Value']})
        updates.update({'elec_solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of external fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'thermal_solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar thermal energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed thermal energy')
        updates.update({'curtail_p':ds[index]['Value']})         
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar electric energy')
        updates.update({'curtail2':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed electric energy')
        updates.update({'curtail2_p':ds[index]['Value']})         
        
        # # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Overall recovery rate')
        updates.update({'RR':dd[index]['Value']})        
        index = helpers.index_in_list_of_dicts(dd,'Name','Electric energy requirement')
        updates.update({'electric_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power requirement') 
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','RO capacity')
        updates.update({'RO_capacity':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','MD capacity') 
        updates.update({'MD_capacity':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','MD brine salinity')
        updates.update({'p_brine':dd[index]['Value']})


        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal Annualized CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Annual water production')
        updates.update({'water_prod':dc[index]['Value']})        
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of electricity (from solar field)')
        updates.update({'sam_lcoe':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from solar field)')
        updates.update({'sam_lcoh':dc[index]['Value']})

        # add from cost input 
        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'lcoe':f['coe']})
        updates.update({'lcoh':f['coh']})
        
    elif updates['desal'] == 'OARO' or updates['desal'] == 'LSRRO' or updates['desal'] == 'COMRO':
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        #fossil_fuel = "Yes" if d['Fossil_f'] else "No"
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['Capacity']
                       # 'storage_hour':d['storage_hour'],
                       # 'fossil_fuel': fossil_fuel
                       })
                      #  'RR': d['R1'] * 100})
        # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total fossil fuel usage')
        updates.update({'fossil_usage':ds[index]['Value']/1000})
        indexp = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[indexp]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'solar_percent': 100-ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar electric energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed energy')
        updates.update({'curtail_p':ds[index]['Value']})              
        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
   
        index = helpers.index_in_list_of_dicts(dd,'Name','Electric energy requirement')
        updates.update({'electric_power_consumption':dd[index]['Value'] * 1000})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific electricity consumption') 
        updates.update({'specific_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Recovery ratio')
        updates.update({'rr':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Brine concentration')
        updates.update({'p_brine':dd[index]['Value']})

        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal Annualized CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Energy cost')
        updates.update({'energy_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of electricity (from solar field)')
        updates.update({'sam_lcoe':dc[index]['Value']})        
        
        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'lcoe':f['coe']})
        updates.update({'downtime': f['downtime']})
        updates.update({'actual_prod':(1-f['downtime']/100) * ds[indexp]['Value']})
        
    elif updates['desal'] == 'FO':
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        fossil_fuel = "Yes" if d['Fossil_f'] else "No"
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['Mprod'],
                        'storage_hour':d['storage_hour'],
                        'fossil_fuel': fossil_fuel,
                        'RR': d['r']*100})
        # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total fossil fuel usage')
        updates.update({'fossil_usage':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'solar_percent': 100-ds[index]['Value']})  
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar thermal energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed energy')
        updates.update({'curtail_p':ds[index]['Value']})       
        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power requirement')
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific thermal power consumption')     
        updates.update({'specific_thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Brine concentration')
        updates.update({'p_brine':dd[index]['Value']})

        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from fossile fuel)')
        updates.update({'lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from solar field)')
        updates.update({'sam_lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal Annualized CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Energy cost')
        updates.update({'energy_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Unit CAPEX')
        updates.update({'unit_capex':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Labor cost')
        updates.update({'labor':dc[index]['Value']})
        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'lcoe':f['coe']})
        
    elif updates['desal'] == 'Generic':
        d = helpers.json_load(cfg.json_outpath / updates['desal_outfile'])
        fossil_fuel = "Yes" if d['Fossil_f'] else "No"
        updates.update({'FeedC_r':d['FeedC_r'],
                        'Capacity':d['Capacity'],
                        'storage_hour':d['storage_hour'],
                        'fossil_fuel': fossil_fuel,
                        'RR': d['RR']})
        # add specific data from desal simulation output
        ds = helpers.json_load(flkup['sam_desal_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(ds,'Name','Storage Capacity')
        updates.update({'thermal_storage_capacity':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total fossil fuel usage')
        updates.update({'fossil_usage':ds[index]['Value']/1000})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of fossil fuel consumption')
        updates.update({'fossil_percent':ds[index]['Value']})
        updates.update({'solar_percent': 100-ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Curtailed solar thermal energy')
        updates.update({'curtail':ds[index]['Value']})        
        index = helpers.index_in_list_of_dicts(ds,'Name','Percentage of curtailed energy')
        updates.update({'curtail_p':ds[index]['Value']})                 
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
      
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power requirement')
        updates.update({'thermal_power_consumption':dd[index]['Value'] * 1000})
        index = helpers.index_in_list_of_dicts(dd,'Name','Brine concentration')
        updates.update({'p_brine':dd[index]['Value']})

        # add specific data from desal cost output
        dc = helpers.json_load(flkup['sam_desal_finance_outfile'])
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of water')
        updates.update({'lcow':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from fossile fuel)')
        updates.update({'lcoh':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Levelized cost of heat (from solar field)')
        updates.update({'sam_lcoh':dc[index]['Value']})
        # index = helpers.index_in_list_of_dicts(dc,'Name','Desal CAPEX')
        # updates.update({'capital_cost':dc[index]['Value']})
        # index = helpers.index_in_list_of_dicts(dc,'Name','Energy cost')
        # updates.update({'energy_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal CAPEX')
        updates.update({'capital_cost':dc[index]['Value']})
        index = helpers.index_in_list_of_dicts(dc,'Name','Desal OPEX')
        updates.update({'ops_cost':dc[index]['Value']})
        # index = helpers.index_in_list_of_dicts(dc,'Name','Labor cost')
        # updates.update({'labor':dc[index]['Value']})
        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'lcoe':f['coe']})
        
    if updates['solar'] == 'linear_fresnel_dsg_iph':
        # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['q_pb_des']})
        updates.update({'footprint1':s['q_pb_des'] * 6})
        updates.update({'footprint2':s['q_pb_des'] * 8})

        # add sam simulation output
        so = helpers.json_load(flkup['sam_solar_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(so,'Name','Actual aperture')
        updates.update({'actual_aperture':so[index]['Value']})
        index = helpers.index_in_list_of_dicts(so,'Name','System power generated')
        updates.update({'heat_gen':sum(so[index]['Value']) / 1000 / 1000})
        updates.update({'cf':sum(so[index]['Value']) / 3650 /24 / s['q_pb_des']})        
   
    elif updates['solar'] == 'trough_physical_process_heat':
        # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['q_pb_design']})
        updates.update({'footprint1':s['q_pb_design'] * 6})
        updates.update({'footprint2':s['q_pb_design'] * 8})
        # add sam simulation output
        so = helpers.json_load(flkup['sam_solar_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(so,'Name','Heat sink thermal power')
        updates.update({'heat_gen':sum(so[index]['Value']) / 1000})
        updates.update({'cf':sum(so[index]['Value'])  / 3.65 /24 / s['q_pb_design']})
        
    elif updates['solar'] == 'pvsamv1':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['system_capacity']})
        updates.update({'footprint1':s['system_capacity'] * 6 /1000})
        updates.update({'footprint2':s['system_capacity'] * 8 /1000})

        # add sam simulation output
        so = helpers.json_load(flkup['sam_solar_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(so,'Name','System power generated')
        updates.update({'elec_gen':sum(so[index]['Value']) / 1000 / 1000})
        updates.update({'cf':sum(so[index]['Value'])  / 3.65 /24 / s['system_capacity']})

    elif updates['solar'] == 'SC_FPC' or updates['solar'] == 'SC_ETC':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['desal_thermal_power_req']})
        updates.update({'footprint1':s['desal_thermal_power_req'] * 6 })
        updates.update({'footprint2':s['desal_thermal_power_req'] * 8 })
        # add sam simulation output        
        so = helpers.json_load(flkup['sam_solar_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(so,'Name','Thermal power generation')
        updates.update({'elec_gen':sum(so[index]['Value']) / 1000 / 1000})
        updates.update({'cf':sum(so[index]['Value'])/1000  / 3.65 /24 / s['desal_thermal_power_req']})
        
    elif updates['solar'] == 'tcslinear_fresnel':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['system_capacity']})
        updates.update({'footprint1':s['system_capacity'] * 6 /1000 })
        updates.update({'footprint2':s['system_capacity'] * 8 /1000})
    # add sam simulation output        
        so = helpers.json_load(flkup['sam_solar_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(so,'Name','System power generated')
        updates.update({'elec_gen':sum(so[index]['Value']) / 1000 / 1000})
        updates.update({'cf':sum(so[index]['Value'])  / 3.65 /24 / s['system_capacity']})
        index = helpers.index_in_list_of_dicts(so,'Name','Waste heat generation')
        updates.update({'heat_gen':sum(so[index]['Value']) / 1000 / 1000})
        
    elif updates['solar'] == 'tcsmolten_salt':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['system_capacity']})
        updates.update({'footprint1':s['P_ref'] * 6 })
        updates.update({'footprint2':s['P_ref'] * 8 })
    # add sam simulation output        
        so = helpers.json_load(flkup['sam_solar_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(so,'Name','Total electric power to grid w/ avail. derate')
        updates.update({'elec_gen':sum(so[index]['Value']) / 1000 / 1000})
        updates.update({'cf':sum(so[index]['Value'])/1000  / 3.65 /24 / s['P_ref']})
        index = helpers.index_in_list_of_dicts(so,'Name','Waste heat generation')
        updates.update({'heat_gen':sum(so[index]['Value']) / 1000 / 1000})

    elif updates['solar'] == 'tcsMSLF':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['system_capacity']})
        updates.update({'footprint1':s['P_ref'] * 6  })
        updates.update({'footprint2':s['P_ref'] * 8  })
    # add sam simulation output        
        so = helpers.json_load(flkup['sam_solar_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(so,'Name','System power generated')
        updates.update({'elec_gen':sum(so[index]['Value']) / 1000 / 1000})
        updates.update({'cf':sum(so[index]['Value'])/1000  / 3.65 /24 / s['P_ref']})
        index = helpers.index_in_list_of_dicts(so,'Name','Waste heat generation')
        updates.update({'heat_gen':sum(so[index]['Value']) / 1000 / 1000})
        
    elif updates['solar'] == 'tcsdirect_steam':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['system_capacity']})
        updates.update({'footprint1':s['system_capacity'] * 6 /1000})
        updates.update({'footprint2':s['system_capacity'] * 8 /1000})
    # add sam simulation output        
        so = helpers.json_load(flkup['sam_solar_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(so,'Name','System power generated')
        updates.update({'elec_gen':sum(so[index]['Value']) / 1000 / 1000})
        updates.update({'cf':sum(so[index]['Value'])  / 3.65 /24 / s['system_capacity']})
        index = helpers.index_in_list_of_dicts(so,'Name','Waste heat generation')
        updates.update({'heat_gen':sum(so[index]['Value']) / 1000 / 1000})

    elif updates['solar'] == 'tcstrough_physical':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['system_capacity']})
        updates.update({'footprint1':s['system_capacity'] * 6 /1000})
        updates.update({'footprint2':s['system_capacity'] * 8 /1000})
    # add sam simulation output        
        so = helpers.json_load(flkup['sam_solar_simulation_outfile'])
        index = helpers.index_in_list_of_dicts(so,'Name','System power generated')
        updates.update({'elec_gen':sum(so[index]['Value']) / 1000 / 1000})
        updates.update({'cf':sum(so[index]['Value'])  / 3.65 /24 / s['system_capacity']})
        index = helpers.index_in_list_of_dicts(so,'Name','Waste heat generation')
        updates.update({'heat_gen':sum(so[index]['Value']) / 1000 / 1000})
    
        
    
    # finally create the report json
    helpers.initialize_json(updates,cfg.report_json)
    return ''

@app.callback(
    Output('local-condition', 'children'),
    [Input('data-initialize', 'children')])
def set_local_condition(x):
    # For area lacking data of GHI/DNI/others, it reports error
    try:
        r = helpers.json_load(cfg.report_json)
    except FileNotFoundError:
        return None
    city = r.get('city')
    if not city:
        city = r.get('county')
    if not city:
        city = '-'

    wn_dist = r.get('dist_water_network')
    wn_dist = round(wn_dist,1) if wn_dist else '-'

    pp_dist = r.get('dist_power_plant')
    pp_dist = round(pp_dist) if pp_dist else '-'
 
    return ([
    html.H5('Local Condition', className='card-title'),
    html.Div(f"Location: {city}, {r['state']}"),
    html.Div(f"Daily average DNI: {r['dni']:.1f} kWh/m2/day"),
    html.Div(f"Daily average GHI: {r['ghi']:.1f} kWh/m2/day"),
    html.Div(f"Feedwater salinity: {r['FeedC_r']:.1f} g/L"),
    html.Div(f"Market water price: {r['water_price']} $/m3"), 
    html.Div(f"Distance to nearest desalination plant: {r['dist_desal_plant']:.1f} km"),
    html.Div(f"Distance to nearest water network: {wn_dist} km"),
    html.Div(f"Distance to nearest power plant: {pp_dist} km")
    ])

@app.callback(
    Output('desal-config', 'children'),
    [Input('data-initialize', 'children')])
def set_desal_config(x):
    r = helpers.json_load(cfg.report_json)
    app = helpers.json_load(cfg.app_json)
    
    if app['desal'] == "VAGMD" :
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"Number of module required: {r['n_modules']}"),
        html.Div(f"Thermal storage hour: {r['storage_hour']} hrs"),
        html.Div(f"Thermal storage capacity: {r['thermal_storage_capacity']:.0f} kWh"),
        html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
        html.Div(f"Specific thermal energy consumption: {r['specific_thermal_power_consumption']:.2f} kWh/m3"),
        # html.Div(f"Specific electric energy consumption: {r['electric_energy_consumption']:.2f}  kWh/m3"),
        html.Div(f"Required thermal energy: {r['thermal_power_consumption']:.2f} MW")
        ])
    elif app['desal'] == 'LTMED' or app['desal'] == 'MEDTVC' or app['desal'] == 'ABS':
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"Thermal storage hour: {r['storage_hour']} hrs"),
        html.Div(f"Thermal storage capacity: {r['thermal_storage_capacity']:.0f} kWh"),
        html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
        html.Div(f"Specific thermal energy consumption: {r['specific_thermal_power_consumption']:.2f} kWh/m3"),
        html.Div(f"Required thermal energy: {r['thermal_power_consumption']:.2f} MW"),
        # html.Div(f"Required electric energy: {r['electric_energy_consumption']:.2f}  kWh/m3")
        ])
    elif app['desal'] == 'RO':
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"Number of vessels: {r['number_vessels']} "),
        html.Div(f"Battery storage hour: {r['storage_hour']} hrs"),
        html.Div(f"Battery storage capacity: {r['thermal_storage_capacity']:.0f} kWh"),
        html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
        html.Div(f"Specific energy consumption: {r['specific_power_consumption']:.2f} kWh/m3"),
        html.Div(f"Required electric energy: {r['electric_power_consumption']:.0f} kW")
        ])
    elif app['desal'] == 'OARO' or app['desal'] == 'LSRRO' or app['desal'] == 'COMRO':
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        #html.Div(f"Battery storage hour: {r['storage_hour']} hrs"),
        #html.Div(f"Battery storage capacity: {r['thermal_storage_capacity']:.0f} kWh"),
        #html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
        html.Div(f"Specific energy consumption: {r['specific_power_consumption']:.2f} kWh/m3"),
        html.Div(f"Required electric energy: {r['electric_power_consumption']:.0f} kW")
        ])
    elif app['desal'] == "FO":
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"Thermal storage hour: {r['storage_hour']} hrs"),
        html.Div(f"Thermal storage capacity: {r['thermal_storage_capacity']:.0f} kWh"),
        html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
        html.Div(f"Specific thermal energy consumption: {r['specific_thermal_power_consumption']:.2f} kWh/m3"),
        html.Div(f"Required thermal energy: {r['thermal_power_consumption']:.2f} MW")
        ])
    elif app['desal'] == "MDB":
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"Thermal storage hour: {r['storage_hour']} hrs"),
        html.Div(f"Thermal storage capacity: {r['thermal_storage_capacity']:.0f} kWh"),
        html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
        html.Div(f"Specific thermal energy consumption: {r['specific_thermal_power_consumption']:.2f} kWh/m3"),
        html.Div(f"Thermal power consumption: {r['thermal_power_consumption']:.2f} MW")
        ])
    elif app['desal'] == "RO_FO":
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"RO capacity: {r['RO_capacity']:.1f} m3/day"),
        html.Div(f"FO capacity: {r['FO_capacity']:.1f} m3/day"),
        html.Div(f"Electric energy consumption: {r['electric_power_consumption']:.1f} kW(e)"),
        html.Div(f"Thermal power consumption: {r['thermal_power_consumption']:.2f} MW(th)")
        ])
    elif app['desal'] == "RO_MDB":
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"RO capacity: {r['RO_capacity']:.1f} m3/day"),
        html.Div(f"MD capacity: {r['MD_capacity']:.1f} m3/day"),
        html.Div(f"Electric energy consumption: {r['electric_power_consumption']:.1f} kW(e)"),
        html.Div(f"Thermal power consumption: {r['thermal_power_consumption']:.2f} MW(th)")
        ])
    elif app['desal'] == "Generic":
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"Thermal storage hour: {r['storage_hour']} hrs"),
        html.Div(f"Thermal storage capacity: {r['thermal_storage_capacity']:.0f} kWh"),
        html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
        # html.Div(f"Specific thermal energy consumption: {r['specific_thermal_power_consumption']:.2f} kWh/m3"),
        html.Div(f"Required thermal energy: {r['thermal_power_consumption']:.0f} kW")
        ])
    
@app.callback(
    Output('solar-config', 'children'),
    [Input('data-initialize', 'children')])
def set_solar_config(x):
    r = helpers.json_load(cfg.report_json)
    app = helpers.json_load(cfg.app_json)
    
    if app['solar'] == "linear_fresnel_dsg_iph":
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design thermal energy production: {r['q_pb_des']:.2f} MW"),
        html.Div(f"Actual aperture: {r['actual_aperture']:.0f} m2"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])
    elif app['solar'] == "trough_physical_process_heat":
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design thermal energy production: {r['q_pb_des']:.2f} MW"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])
    elif app['solar'] == "pvsamv1":
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design electric energy production: {r['q_pb_des']:.2f} kWdc"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])
    elif app['solar'] == "SC_FPC" or app['solar'] == 'SC_ETC':
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design thermal energy production: {r['q_pb_des']:.2f} MW"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])
    elif app['solar'] == "tcsdirect_steam" :
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design electricity production: {r['q_pb_des']:.2f} kW"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])
    elif  app['solar'] == "tcsmolten_salt":
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design electricity production: {r['q_pb_des']:.0f} MW"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])
    elif app['solar'] == "tcslinear_fresnel":
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design electricity production: {r['q_pb_des']:.2f} kW"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])
    elif app['solar'] == "tcstrough_physical":
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design electricity production: {r['q_pb_des']:.2f} kW"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])
    elif app['solar'] == "tcsMSLF":
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design electricity production: {r['q_pb_des']:.2f} kW"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])

@app.callback(
    Output('sam-performance', 'children'),
    [Input('data-initialize', 'children')])
def sam_performance(x):
    r = helpers.json_load(cfg.report_json)
    app = helpers.json_load(cfg.app_json)


    def curtailed_thermal(cte):
        if cte > 20:
            return html.Div([
                html.Div(f"Percentage of curtailed thermal energy: {cte:.1f} %"),
                html.Div(f"High energy curtailment!",style={'color':'yellow'}),
                html.Div(f"Consider adding Thermal Storage hours in the Desalination Model Input and/or Reduce the Capacity of the Solar Field in Power Cycle Input" , style = {'color':'yellow'})
            ])
        else:
            return html.Div(f"Percentage of curtailed thermal energy: {cte:.1f} %")

    def curtailed_thermal2(cte):
        if cte > 20:
            return html.Div([
                html.Div(f"Percentage of curtailed thermal energy: {cte:.1f} %"),
                html.Div(f"High energy curtailment!",style={'color':'yellow'}),
                html.Div(f"Consider adding Thermal Storage hours in the Desalination Model Input or Increase the Capacity of desalination" , style = {'color':'yellow'})
            ])
        else:
            return html.Div(f"Percentage of curtailed thermal energy: {cte:.1f} %")

    if app['solar'] == "linear_fresnel_dsg_iph":
        return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),     
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal(r['curtail_p']) ,  
        ])
    elif app['solar'] == "trough_physical_process_heat":
        return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal(r['curtail_p']) ,       
        ])
    elif app['solar'] == "pvsamv1":
        if app['desal'] =='RO_FO' or app['desal'] =='RO_MDB':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),     
        html.Div(f"Curtailed electric energy: {r['curtail2']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail2_p']:.1f} %"),   
        ])
        else:        
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),     
        html.Div(f"Curtailed electric energy: {r['curtail']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail_p']:.1f} %"),   
        ])
    elif app['solar'] == "SC_FPC" or app['solar'] == 'SC_ETC':
        return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual thermal energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor: {r['cf']:.1f} %"),  
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal(r['curtail_p']) ,     
        ])
    elif app['solar'] == "tcsdirect_steam" :
        if app['desal'] =='RO_FO' or app['desal'] =='RO_MDB':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal2(r['curtail_p']) ,
        html.Div(f"Curtailed electric energy: {r['curtail2']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail2_p']:.1f} %"),         
        ])
        
        if app['desal'] =='RO' or app['desal'] == 'OARO':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"), 
        html.Div(f"Curtailed electric energy: {r['curtail']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail_p']:.1f} %"),         
        ])
                
        else:
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal2(r['curtail_p']) , 
        ])
    elif  app['solar'] == "tcsmolten_salt":
        if app['desal'] =='RO_FO' or app['desal'] == 'RO_MDB':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal2(r['curtail_p']) ,
        html.Div(f"Curtailed electric energy: {r['curtail2']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail2_p']:.1f} %"),         
        ])
        
        if app['desal'] =='RO' or app['desal'] == 'OARO':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Curtailed electric energy: {r['curtail']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail_p']:.1f} %"),         
        ])
                
        else:
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal2(r['curtail_p']) , 
        ])
    elif app['solar'] == "tcslinear_fresnel":
        if app['desal'] =='RO_FO' or app['desal'] =='RO_MDB':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal(r['curtail_p']) ,
        html.Div(f"Curtailed electric energy: {r['curtail2']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail2_p']:.1f} %"),         
        ])
        
        if app['desal'] =='RO' or app['desal'] == 'OARO':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Curtailed electric energy: {r['curtail']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail_p']:.1f} %"),         
        ])
                
        else:
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal(r['curtail_p']) , 
        ])
    elif app['solar'] == "tcstrough_physical":
        if app['desal'] =='RO_FO' or app['desal'] =='RO_MDB':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal(r['curtail_p']) ,
        html.Div(f"Curtailed electric energy: {r['curtail2']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail2_p']:.1f} %"),         
        ])
        
        if app['desal'] =='RO' or app['desal'] == 'OARO':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Curtailed electric energy: {r['curtail']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail_p']:.1f} %"),         
        ])
                
        else:
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal(r['curtail_p']) , 
        ])
    elif app['solar'] == "tcsMSLF":
        if app['desal'] =='RO_FO' or app['desal'] =='RO_MDB':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal(r['curtail_p']) ,
        html.Div(f"Curtailed electric energy: {r['curtail2']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail2_p']:.1f} %"),         
        ])
        
        if app['desal'] =='RO' or app['desal'] == 'OARO':
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),  
        html.Div(f"Curtailed electric energy: {r['curtail']:.2f} GWh"),    
        html.Div(f"Percentage of curtailed electric energy: {r['curtail_p']:.1f} %"),         
        ])
                
        else:
            return ([
        html.H5('Solar Field Performance', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Annual electric energy production: {r['elec_gen']:.2f} GWh"), 
        html.Div(f"Capacity factor (based on design capacity, not the actual one): {r['cf']:.1f} %"),   
        html.Div(f"Annual thermal energy production: {r['heat_gen']:.2f} GWh"), 
        html.Div(f"Curtailed thermal energy: {r['curtail']:.2f} GWh"),    
        curtailed_thermal(r['curtail_p']) , 
        ])
    
@app.callback(
    Output('system-performance', 'children'),
    [Input('data-initialize', 'children')])
def set_system_performance(x):
    r = helpers.json_load(cfg.report_json)
    app = helpers.json_load(cfg.app_json)
    if app['desal'] == 'LTMED' or app['desal'] == 'VAGMD' or app['desal'] == 'MEDTVC' or app['desal'] == 'ABS':
        return ([
        html.H5('Desalination System Performance', className='card-title'),
        html.Div(f"Annual water production: {r['water_prod']:.0f} m3"),
        html.Div(f"Brine concentration: {r['p_brine']:.1f} g/L"),        
        html.Div(f"Gained output ratio: {r['gained_output_ratio']:.2f}"),
        html.Div(f"Assumed recovery ratio: {r['RR']:.2f} %"),    
        html.Div(f"Total fuel usage: {r['fossil_usage']:.0f} MWh"),
        html.Div(f"Percentage of energy from solar field: {r['solar_percent']:.1f} %"),    
        html.Div(f"Percentage of energy from other sources: {r['fossil_percent']:.1f} %"), 
        ])
    elif app['desal'] == 'RO' or app['desal'] == 'FO':
        return ([
        html.H5('Desalination System Performance', className='card-title'),
        html.Div(f"Annual water production: {r['water_prod']:.0f} m3"),
        html.Div(f"Brine concentration: {r['p_brine']:.1f} g/L"),   
        html.Div(f"Assumed recovery ratio: {r['RR']:.2f} %"),    
        html.Div(f"Total fuel usage: {r['fossil_usage']:.0f} MWh"),
        html.Div(f"Percentage of energy from solar field: {r['solar_percent']:.1f} %"),    
        html.Div(f"Percentage of energy from grid: {r['fossil_percent']:.1f} %"), 
        ])
    elif app['desal'] == 'RO_FO' or app['desal'] == 'RO_MDB':
        return ([
        html.H5('Desalination System Performance', className='card-title'),
        html.Div(f"Annual water production: {r['water_prod']:.0f} m3"),
        html.Div(f"Brine concentration: {r['p_brine']:.1f} g/L"),   
        html.Div(f"Overall recovery ratio: {r['RR']:.2f} %"),    
        html.Div(f"Total grid electricity usage: {r['grid_usage']:.0f} MWh"),
        html.Div(f"Total external heat usage: {r['external_heat']:.0f} MWh"),
        html.Div(f"Percentage of electric energy from solar field: {r['elec_solar_percent']:.1f} %"),    
        html.Div(f"Percentage of electric energy from grid: {r['grid_percent']:.1f} %"), 
        html.Div(f"Percentage of thermal energy from solar field: {r['thermal_solar_percent']:.1f} %"),    
        html.Div(f"Percentage of thermal energy from other sources: {r['fossil_percent']:.1f} %"),
        ])
    elif app['desal'] == 'OARO' or app['desal'] == 'LSRRO' or app['desal'] == 'COMRO' :
        return ([
        html.H5('Desalination System Performance', className='card-title'),
        html.Div(f"Annual water production: {r['actual_prod']:.0f} m3"),
        html.Div(f"Brine concentration: {r['p_brine']:.1f} g/L"),   
        html.Div(f"Annual downtime: {r['downtime']: .0f} %"),
        html.Div(f"Assumed recovery ratio: {r['rr']:.1f} %"),    
        #html.Div(f"Total fuel usage: {r['fossil_usage']:.0f} kWh"),
        html.Div(f"Percentage of energy from solar field: {r['solar_percent']:.1f} %"),    
        html.Div(f"Percentage of energy from other sources: {r['fossil_percent']:.1f} %"), 
        ])
    elif app['desal'] == 'MDB':       
        df = pd.read_csv(cfg.sam_results_dir/'MDB_output.csv',skiprows = 1)      
        for i in range(1,len(df.columns.values)):
            df.columns.values[i] = str(i)
        return ([
        html.H5('Desalination System Performance', className='card-title'),
        html.Div(f"Annual water production: {r['water_prod']:.0f} m3"),
        html.Div(f"Brine concentration: {r['p_brine']:.1f} g/L"),   
        html.Div(f"Assumed recovery ratio: {r['RR']:.2f} %"),    
        html.Div(f"Total fuel usage: {r['fossil_usage']:.0f} MWh"),
        html.Div(f"Percentage of energy from solar field: {r['solar_percent']:.1f} %"),    
        html.Div(f"Percentage of energy from other sources: {r['fossil_percent']:.1f} %"), 
        html.Div(f"Number of modules required: {r['n_modules']:.0f} "),
        html.Div(f"Module type: {r['m_type']} "),
        html.Div("   Single module performance",
                 style = {'textAlign':'center','font-size': '18px', 'fontWeight':'bold','color':'rgb(230, 247, 240)'}),
        dash_table.DataTable(id='table',
                              columns= [{"name": i, "id": i} for i in df.columns], 
                              data=df.to_dict('records'),
                              style_cell={'backgroundColor': 'rgb(230, 247, 240)','color':'black','font-size':'12px'},
                              style_header = {'fontWeight':'bold','color':'rgb(9, 131, 143)','font-size':'16px'},
                              style_cell_conditional=[
                                  {
                                      'if': {'column_id': 'Step'},
                                      'color': 'rgb(9, 131, 143)', 'font-size':'12px'
                                  }],
                              export_format = 'xlsx'
                              ),
        ])
    elif app['desal'] == 'Generic':
        return ([
        html.H5('Desalination System Performance', className='card-title'),
        html.Div(f"Annual water production: {r['water_prod']:.0f} m3"),
        html.Div(f"Brine concentration: {r['p_brine']:.1f} g/L"),   
        html.Div(f"Assumed recovery ratio: {r['RR']:.2f} %"),    
        html.Div(f"Total fuel usage: {r['fossil_usage']:.0f} MWh"),
        html.Div(f"Percentage of energy from solar field: {r['solar_percent']:.1f} %"),    
        html.Div(f"Percentage of energy from other sources: {r['fossil_percent']:.1f} %"), 
        ])
@app.callback(
    Output('cost-analysis', 'children'),
    [Input('data-initialize', 'children')])
def set_cost_analysis(x):
    r = helpers.json_load(cfg.report_json)
    app = helpers.json_load(cfg.app_json)
    if app['desal'] == 'LTMED' or app['desal'] == 'VAGMD' or app['desal'] == 'MEDTVC' or app['desal'] == "MDB":
        return ([
        html.H5('Cost Analysis', className='card-title'),
        html.Div(f"Levelized cost of water (LCOW): {r['lcow']:.2f} $/m3"),
        html.Div(f"Assumed cost of heat (LCOH, from other sources): {r['lcoh']:.3f} $/kWh"),
        html.Div(f"Levelized cost of heat (LCOH, from solar field): {r['sam_lcoh']:.3f} $/kWh"),
        html.Div(f"Levelized cost of electric energy (LCOE): {r['lcoe']:.2f} $/kWh"),
        html.Div(f"Capital cost: {r['capital_cost']:.2f} $/m3"),
        html.Div(f"Operational and Maintenance cost: {r['ops_cost']:.2f} $/m3"),
        html.Div(f"Unit energy cost: {r['energy_cost']:.2f} $/m3",
                 style = { 'margin-left' : '30px' }),
        ])
    elif app['desal'] =='ABS':
        return ([
        html.H5('Cost Analysis', className='card-title'),
        html.Div(f"Levelized cost of water (LCOW): {r['lcow']:.2f} $/m3"),
        html.Div(f"Assumed cost of heat (LCOH, from other sources): {r['lcoh']:.3f} $/kWh"),
        html.Div(f"Levelized cost of heat (LCOH, from solar field): {r['sam_lcoh']:.3f} $/kWh"),
        html.Div(f"Levelized cost of electric energy (LCOE): {r['lcoe']:.2f} $/kWh"),
        html.Div(f"Capital cost of heat pump: {r['AHP_cost']:.0f} $/kW"),        
        html.Div(f"Capital cost: {r['capital_cost']:.2f} $/m3"),
        html.Div(f"Operational and Maintenance cost: {r['ops_cost']:.2f} $/m3"),
        html.Div(f"Unit energy cost: {r['energy_cost']:.2f} $/m3",
                 style = { 'margin-left' : '30px' }),
        ])
    elif app['desal'] =='FO':
        return ([
        html.H5('Cost Analysis', className='card-title'),

        html.Div(f"Levelized cost of water (LCOW): {r['lcow']:.2f} $/m3"),
        html.Div(f"Capital cost: {r['capital_cost']:.2f} $/m3"),
        html.Div(f"Operational and Maintenance cost: {r['ops_cost']:.2f} $/m3"),
        html.Div(f"Assumed cost of heat (LCOH, from other sources): {r['lcoh']:.3f} $/kWh"),
        html.Div(f"Levelized cost of heat (LCOH, from solar field): {r['sam_lcoh']:.3f} $/kWh"),
        html.Div(f"Assumed cost of electric energy (LCOE): {r['lcoe']:.2f} $/kWh"),

        html.Div(f"     -Unit energy cost: {r['energy_cost']:.2f} $/m3",
                 style = { 'margin-left' : '30px' }),
        html.Div(f"     -Unit CAPEX: {r['unit_capex']:.2f} $/m3/day",
                 style = { 'margin-left' : '30px' }),
        html.Div(f"     -Labor cost: {r['labor']:.2f} $/m3",
                 style = { 'margin-left' : '30px' }),          
        ])
    elif app['desal'] == 'RO' or app['desal'] == 'OARO' or app['desal'] == 'LSRRO' or app['desal'] == 'COMRO':
        return ([
        html.H5('Cost Analysis', className='card-title'),
        html.Div(f"Levelized cost of water (LCOW): {r['lcow']:.2f} $/m3"),
    #    html.Div(f"Levelized cost of heat (LCOH, calculated): {r['lcoh_cal']:.2f} $/m3"),
        html.Div(f"Assumed cost of electricity (LCOE, from grid): {r['lcoe']:.3f} $/kWh"),
        html.Div(f"Levelized cost of electricity (LCOE, from solar field): {r['sam_lcoe']:.3f} $/kWh"),
        html.Div(f"Capital cost: {r['capital_cost']:.2f} $/m3"),
        html.Div(f"Operational and Maintenance cost: {r['ops_cost']:.2f} $/m3"),
        html.Div(f"Unit energy cost: {r['energy_cost']:.2f} $/m3",
                 style = { 'margin-left' : '30px' }),
          
        ])
    elif app['desal'] == 'RO_FO' or app['desal'] == 'RO_MDB' :
        return ([
        html.H5('Cost Analysis', className='card-title'),
        html.Div(f"Levelized cost of water (LCOW): {r['lcow']:.2f} $/m3"),
    #    html.Div(f"Levelized cost of heat (LCOH, calculated): {r['lcoh_cal']:.2f} $/m3"),
        html.Div(f"Capital cost: {r['capital_cost']:.2f} $/m3"),
        html.Div(f"Operational and Maintenance cost: {r['ops_cost']:.2f} $/m3"),
        html.Div(f"Assumed cost of heat (LCOH, from other sources): {r['lcoh']:.3f} $/kWh"),
        html.Div(f"Levelized cost of heat (LCOH, from solar field): {r['sam_lcoh']:.3f} $/kWh"),
        html.Div(f"Assumed cost of electric energy (LCOE, from grid): {r['lcoe']:.2f} $/kWh"),
        html.Div(f"Levelized cost of electric energy (LCOE, from solar field): {r['sam_lcoe']:.2f} $/kWh"),          
        ])
    elif app['desal'] =='Generic':
        return ([
        html.H5('Cost Analysis', className='card-title'),

        html.Div(f"Levelized cost of water (LCOW): {r['lcow']:.2f} $/m3"),
        html.Div(f"Capital cost: {r['capital_cost']:.2f} $/m3"),
        html.Div(f"Operational and Maintenance cost: {r['ops_cost']:.2f} $/m3"),
        html.Div(f"Assumed cost of heat (LCOH, from other sources): {r['lcoh']:.3f} $/kWh"),
        html.Div(f"Levelized cost of heat (LCOH, from solar field): {r['sam_lcoh']:.3f} $/kWh"),
        html.Div(f"Levelized cost of electric energy (LCOE): {r['lcoe']:.2f} $/kWh"),

        # html.Div(f"Unit energy cost: {r['energy_cost']:.2f} $/m3"),
        # html.Div(f"Unit CAPEX: {r['unit_capex']:.2f} $/m3/day"),
        # html.Div(f"Labor cost: {r['labor']:.2f} $/m3"),          
        ])    