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

chart_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Charts", href='/chart-results')),
              dbc.NavItem(dbc.NavLink("Report"), active=True),
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

cost_analysis = dbc.CardBody(id='cost-analysis')

system_description = dbc.Card([dbc.CardHeader(html.H4('System Description')),local_condition, desal_config, solar_config], id='system-description', color='primary', inverse=True)

simulation_results = dbc.Card([dbc.CardHeader(html.H4('Simulation Results')),system_performance, cost_analysis], id='simulation-results', color='dark', inverse=True)

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
    flkup = cfg.build_file_lookup(updates['solar'], updates['desal'], updates['finance'])
    
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
        updates.update({'fossil_usage':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power consumption')
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific thermal power consumption') 
        updates.update({'specific_thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Gained output ratio')
        updates.update({'gained_output_ratio':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Number of modules required')
        updates.update({'n_modules':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Recovery ratio')
        updates.update({'RR':dd[index]['Value']})
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
    elif updates['desal'] == 'LTMED':
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
        updates.update({'fossil_usage':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        # add data from desal design input
        ddin = helpers.json_load(flkup['desal_design_outfile'])
        updates.update({'RR':ddin['RR'] * 100})        
        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power consumption')
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific thermal power consumption') 
        updates.update({'specific_thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Gained output ratio')
        updates.update({'gained_output_ratio':dd[index]['Value']})

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
        updates.update({'fossil_usage':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        
        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
        index = helpers.index_in_list_of_dicts(dd,'Name','Number of vessels')
        updates.update({'number_vessels':dd[index]['Value']})        
        index = helpers.index_in_list_of_dicts(dd,'Name','Electric energy consumption')
        updates.update({'electric_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific energy consumption') 
        updates.update({'specific_power_consumption':dd[index]['Value']})


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
        
        
        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'lcoe':f['coe']})
        
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
        updates.update({'fossil_usage':ds[index]['Value']})
        index = helpers.index_in_list_of_dicts(ds,'Name','Total water production')
        updates.update({'water_prod':ds[index]['Value']})
        
        
        # add specific data from desal design output
        dd = helpers.json_load(flkup['desal_design_infile'])
      
        index = helpers.index_in_list_of_dicts(dd,'Name','Thermal power consumption')
        updates.update({'thermal_power_consumption':dd[index]['Value']})
        index = helpers.index_in_list_of_dicts(dd,'Name','Specific thermal power consumption') 
        updates.update({'specific_thermal_power_consumption':dd[index]['Value']})

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

        f = helpers.json_load(cfg.json_outpath / updates['finance_outfile'])
        updates.update({'lcoe':f['coe']})

    if updates['solar'] == 'linear_fresnel_dsg_iph':
        # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['q_pb_des']})
        updates.update({'footprint1':s['q_pb_des'] * 6})
        updates.update({'footprint2':s['q_pb_des'] * 8})

        # add sam simulation output
        so = helpers.json_load(cfg.sam_solar_simulation_outfile)
        index = helpers.index_in_list_of_dicts(so,'Name','Actual aperture')
        updates.update({'actual_aperture':so[index]['Value']})
   
    elif updates['solar'] == 'trough_physical_process_heat':
        # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['q_pb_design']})
        updates.update({'footprint1':s['q_pb_design'] * 6})
        updates.update({'footprint2':s['q_pb_design'] * 8})
        # add sam simulation output
        
    elif updates['solar'] == 'pvsamv1':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['system_capacity']})
        updates.update({'footprint1':s['system_capacity'] * 6 /1000})
        updates.update({'footprint2':s['system_capacity'] * 8 /1000})

        # add sam simulation output
    elif updates['solar'] == 'SC_FPC':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['desal_thermal_power_req']})
        updates.update({'footprint1':s['desal_thermal_power_req'] * 6 })
        updates.update({'footprint2':s['desal_thermal_power_req'] * 8 })
    elif updates['solar'] == 'tcslinear_fresnel':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['system_capacity']})
        updates.update({'footprint1':s['system_capacity'] * 6 /1000 })
        updates.update({'footprint2':s['system_capacity'] * 8 /1000})
    elif updates['solar'] == 'tcsdirect_steam':
    # add specific data from solar GUI output
        s = helpers.json_load(cfg.json_outpath / updates['solar_outfile'])
        updates.update({'q_pb_des':s['system_capacity']})
        updates.update({'footprint1':s['system_capacity'] * 6 /1000})
        updates.update({'footprint2':s['system_capacity'] * 8 /1000})

    
        
    
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
    html.Div(f"Daily average DNI: {r['dni']:.1f} kWh/m2/day"),
    html.Div(f"Daily average GHI: {r['ghi']:.1f} kWh/m2/day"),
    html.Div(f"Feedwater salinity: {r['FeedC_r']:.1f} g/L"),
    html.Div(f"Market water price: {r['water_price']} $/m3"), 
    html.Div(f"Distance to nearest desalination plant: {r['dist_desal_plant']:.1f} km"),
    html.Div(f"Distance to nearest water network: {r['dist_water_network']:.1f} km"),
    html.Div(f"Distance to nearest power plant: {r['dist_power_plant']:.1f} km")
    ])

@app.callback(
    Output('desal-config', 'children'),
    [Input('data-initialize', 'children')])
def set_desal_config(x):
    r = helpers.json_load(cfg.report_json)
    app = helpers.json_load(cfg.app_json)
    
    if app['desal'] == "VAGMD":
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"Number of module required: {r['n_modules']}"),
        html.Div(f"Thermal storage hour: {r['storage_hour']} hrs"),
        html.Div(f"Thermal storage capacity: {r['thermal_storage_capacity']:.0f} kWh"),
        html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
        html.Div(f"Specific thermal energy consumption: {r['specific_thermal_power_consumption']:.2f} kWh/m3"),
        html.Div(f"Required thermal energy: {r['thermal_power_consumption']:.0f} kW"),
        html.Div(f"Required electric energy: {r['electric_energy_consumption']:.2f}  kWh")
        ])
    elif app['desal'] == 'LTMED':
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"Thermal storage hour: {r['storage_hour']} hrs"),
        html.Div(f"Thermal storage capacity: {r['thermal_storage_capacity']:.0f} kWh"),
        html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
        html.Div(f"Specific thermal energy consumption: {r['specific_thermal_power_consumption']:.2f} kWh/m3"),
        html.Div(f"Required thermal energy: {r['thermal_power_consumption']:.0f} kW"),
        html.Div(f"Required electric energy: {r['electric_energy_consumption']:.2f}  kWh")
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
    elif app['desal'] == "FO":
        return ([
        html.H5('Desalination System Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Desal[r['desal']]}"),
        html.Div(f"Design capacity: {r['Capacity']} m3/day"),
        html.Div(f"Thermal storage hour: {r['storage_hour']} hrs"),
        html.Div(f"Thermal storage capacity: {r['thermal_storage_capacity']:.0f} kWh"),
        html.Div(f"Waste heat / fossil fuel enabled: {r['fossil_fuel']}"),
        html.Div(f"Specific thermal energy consumption: {r['specific_thermal_power_consumption']:.2f} kWh/m3"),
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
    elif app['solar'] == "SC_FPC":
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design thermal energy production: {r['q_pb_des']:.2f} MW"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])
    elif app['solar'] == "tcsdirect_steam":
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design electricity production: {r['q_pb_des']:.2f} kW"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])
    elif app['solar'] == "tcslinear_fresnel":
        return ([
        html.H5('Solar Field Configuration', className='card-title'),
        html.Div(f"Technology: {cfg.Solar[r['solar']]}"),
        html.Div(f"Design electricity production: {r['q_pb_des']:.2f} kW"),
        html.Div(f"Land footprint area: {r['footprint1']:.0f} to {r['footprint2']:.0f} acres"),    
        ])


@app.callback(
    Output('system-performance', 'children'),
    [Input('data-initialize', 'children')])
def set_system_performance(x):
    r = helpers.json_load(cfg.report_json)
    app = helpers.json_load(cfg.app_json)
    if app['desal'] == 'LTMED' or app['desal'] == 'VAGMD':
        return ([
        html.H5('System Performance', className='card-title'),
        html.Div(f"Annual water production: {r['water_prod']:.0f} m3"),
        html.Div(f"Gained output ratio: {r['gained_output_ratio']:.2f}"),
        html.Div(f"Recovery ratio: {r['RR']:.2f} %"),    
        html.Div(f"Total fuel usage: {r['fossil_usage']:.0f} kWh"),
        ])
    elif app['desal'] == 'RO' or app['desal'] == 'FO':
        return ([
        html.H5('System Performance', className='card-title'),
        html.Div(f"Annual water production: {r['water_prod']:.0f} m3"),
        html.Div(f"Recovery ratio: {r['RR']:.2f} %"),    
        html.Div(f"Total fuel usage: {r['fossil_usage']:.0f} kWh"),
        ])

@app.callback(
    Output('cost-analysis', 'children'),
    [Input('data-initialize', 'children')])
def set_cost_analysis(x):
    r = helpers.json_load(cfg.report_json)
    app = helpers.json_load(cfg.app_json)
    if app['desal'] == 'LTMED' or app['desal'] == 'VAGMD' or app['desal'] == 'FO':
        return ([
        html.H5('Cost Analysis', className='card-title'),
        html.Div(f"Levelized cost of water (LCOW): {r['lcow']:.2f} $/m3"),
        html.Div(f"Levelized cost of heat (LCOH, from fossil fuel): {r['lcoh']:.3f} $/kWh"),
        html.Div(f"Levelized cost of heat (LCOH, from solar field): {r['sam_lcoh']:.3f} v"),
        html.Div(f"Levelized cost of electric energy (LCOE): {r['lcoe']:.2f} $/kWh"),
        html.Div(f"Capital cost: {r['capital_cost']:.2f} $/m3"),
        html.Div(f"Operational and Maintenance cost: {r['ops_cost']:.2f} $/m3"),
        html.Div(f"Unit energy cost: {r['energy_cost']:.2f} $/m3"),
          
        ])
    elif app['desal'] == 'RO':
        return ([
        html.H5('Cost Analysis', className='card-title'),
        html.Div(f"Levelized cost of water (LCOW): {r['lcow']:.2f} $/m3"),
    #    html.Div(f"Levelized cost of heat (LCOH, calculated): {r['lcoh_cal']:.2f} $/m3"),
        html.Div(f"Levelized cost of energy (LCOE): {r['lcoe']:.2f} $/kWh"),
        html.Div(f"Capital cost: {r['capital_cost']:.2f} $/m3"),
        html.Div(f"Operational and Maintenance cost: {r['ops_cost']:.2f} $/m3"),
        html.Div(f"Unit energy cost: {r['energy_cost']:.2f} $/m3"),
          
        ])

