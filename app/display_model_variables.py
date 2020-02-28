# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 13:55:35 2019

@author: jsquires
"""

import ast
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import json
import sys

from collections import defaultdict
from dash.dependencies import Input, Output, State
from datetime import datetime
from operator import itemgetter
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent.absolute()
sys.path.insert(0,str(base_path))
from SAM_flatJSON.SamBaseClass import SamBaseClass

#
### GLOBAL VARIABLES and pre-processing ###
#
model = 'linear_fresnel_dsg_iph'
desal = 'VAGMD'
finance = 'iph_to_lcoefcr'
json_infiles_dir = base_path / 'SAM_flatJSON' / 'models' / 'inputs'
json_defaults_dir = base_path / 'SAM_flatJSON' / 'defaults'

#TODO: build this later based on model selection within the GUI
solar_variables_file = json_infiles_dir/ '{}_inputs.json'.format(model)
solar_model_values_file = json_defaults_dir / '{}_{}.json'.format(model,finance)
desal_variables_file = json_infiles_dir/ '{}_inputs.json'.format(desal)
desal_values_file = json_defaults_dir / '{}.json'.format(desal)
finance_variables_file = json_infiles_dir/ f'{finance}_inputs.json'
finance_values_file = json_defaults_dir / f'{model}_{finance}.json'
desal_finance_variables_file = json_infiles_dir/ f'{desal}_cost_inputs.json'
desal_finance_values_file = json_defaults_dir/ f'{desal}_cost.json'
desal_design_infile = base_path / 'app' / f'{desal}_design_output.json'
##

json_outpath = base_path / 'app' / 'user-generated-inputs'

default_weather_file = base_path / 'SAM' / 'solar_resource' / 'tucson_az_32.116521_-110.933042_psmv3_60_tmy.csv'
weather_file_path = json_outpath / 'weather-file-location.txt'

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

#columns that will be used in data tables
cols = [{'name':'Variable', 'id':'Label','editable':False},
       # {'name':'Value',    'id':'Value','editable':True, 'type':'numeric'},
        {'name':'Value',    'id':'Value','editable':True},
        {'name':'Units',    'id':'Units','editable':False}]

#
### FUNCTIONS ###
#

def create_callback_for_tables(desal_variables,solar_variables):
    '''
    processes model variables and generates a table_id with the form:
    'Solar_Field_Mirror_WashingGeneral'
    
    where Solar_Field, Mirror_Washing, and General are the
    tab, section and subsection names with spaces replaced with underscores.
     
    Then creates states for each table_id. These store changes to the tables.
    Finally, creates a callback that fires when the Run Model button is hit.
        
    '''        

    def _create_state(table_id):
        ''' 
        creates states for each table by appending
        data_timestamp, id and data to the states list
        '''
        states.append(State(table_id,'data_timestamp'))
        #states.append(State(table_id,'id'))
        states.append(State(table_id,'data'))
    
    # loop through variables for each model, create table_ids and
    # use those to create State lists
    states = []
    print('entered create_callback_for_tables')
    #for model_vars in (desal_variables,solar_variables):
    #for model_vars in solar_variables:
        
    #Collect the table ids
    table_ids = [*{*[ '{}{}{}'.format(v['Tab'],v['Section'],v['Subsection'])\
                                 .replace(' ','_').replace('(','').replace(')','')\
                                     for v in solar_variables]}]
                                 #for v in model_vars]}]
                                    

    #Create States for each table id
    for table_id in table_ids:
        _create_state(table_id)
    
    
    #Then create the callback
    @app.callback(
        Output('model-loading-output','children'),
        [Input('model-button','n_clicks')],
        states)
    def update_model_variables_and_run_model(n_clicks, *tableData): 
        '''
        Once someone is done editing the tables they hit the Run Model button
        This triggers the callback.
        We then check through the state of each table to see if it has been 
        edited. We can tell by whether or not it has a data_timestamp.
        If it has been edited we update the model variables dict which will be 
        converted to json and used as input to run the model.
        Finally the model is run.
        '''
        print('entered update_model_variables_and_run_model')
        def _update_model_variables(tbl_data):
            print('entered _update_model_variables')
            '''find the list with the dict containing the unique value of Name and update that dict'''
            for td in tbl_data:
                unique_val=td['Name']
                mvars,index = index_in_list_of_dicts(model_vars_list,'Name',unique_val)
                mvars[index].update(td)
        
        def _convert_strings_to_literal(str_val):
            '''converts string values to their literal values'''
            #arrays and matrices need to be converted back from string
            if str_val['DataType']=='SSC_ARRAY' or str_val['DataType']=='SSC_MATRIX':
                return ast.literal_eval(str_val['Value'])
            else:
                return str_val['Value']
              
        print('n_clicks is: {}'.format(n_clicks))
        if n_clicks:
            print('entered n_clicks')
            #tableData states is in groups of twos
            #i is the table data_timestamp, i+1 is the data
            for i in range(0,len(tableData),2):
                updated = tableData[i]
                tbl_data = tableData[i+1]
                if updated:
                    #overwrite the dict with the updated data from the table
                    _update_model_variables(tbl_data)  
            #create simple name:value dicts from model variables
            # to be used by SamBaseClass
            solar_output_vars = {}
            desal_output_vars = {}
            # for dvar in desal_model_vars:
            #         desal_output_vars[var['Name']] = _convert_strings_to_literal(var)
            # for svar in solar_model_vars:
            #         solar_output_vars[var['Name']] = _convert_strings_to_literal(var)
            for dvar in desal_model_vars:
                    desal_output_vars[dvar['Name']] = _convert_strings_to_literal(dvar)
            for svar in solar_model_vars:
                    solar_output_vars[svar['Name']] = _convert_strings_to_literal(svar)
            #create the solar json file that will be the input to the model
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            solar_model_outfile = model+timestamp+'_inputs.json'
            solar_model_outfile_path = Path(json_outpath / solar_model_outfile)
            with solar_model_outfile_path.open('w') as write_file:
                json.dump(solar_output_vars, write_file)
            #create the desal json file that will be the input to the model
            desal_model_outfile = desal+timestamp+'_inputs.json'
            desal_model_outfile_path = Path(json_outpath / desal_model_outfile)
            with desal_model_outfile_path.open('w') as write_file:
                json.dump(desal_output_vars, write_file)    
            print('attempting to run model')
            
            #run the model
            run_model(csp=model,
                      desal=desal,
                      finance=None,
                      json_file=solar_model_outfile_path,
                      desal_file=desal_model_outfile_path)
            return (
                    dcc.Markdown('''Model run complete. [View results.](http://127.0.0.1:8051/)''')
                    )
        else:
            return ""
                        
def create_data_table(table_data, table_id):
    return html.Div([
        html.P(),
        dash_table.DataTable(
            id=table_id,
            columns=cols,
            data=table_data,
            editable=True,
            style_cell={
                'textAlign': 'left',
                'maxWidth': '360px',
                'whiteSpace': 'no-wrap',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Label'},
                 'width': '40%'},
                {'if': {'column_id': 'Value'},
                 'width': '55%'},
                {'if': {'column_id': 'Units'},
                 'width': '5%'},
            ],
            css=[{
                'selector': '.dash-cell div.dash-cell-value',
                'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
            }],
            style_header={
                'backgroundColor': '#300C2D',
                'color': 'white',
                'font-family': 'Helvetica',
                #'fontWeight': 'bold',
            },
            #column_static_tooltip=tips
        ),
        html.P(),
    ])

def create_model_variable_page(tab,model_vars):
    '''
    for the provided tab, collects all variables under
    the same section+subsection combination
    and creates the corresponding model variable tables
    '''

    tab_page=[]
    tableData=[]
    sec = None
    subsec = None
    tableID = None
    
    #subset the variables belonging to the tab
    tab_vars = [mv for mv in model_vars if mv['Tab']==tab]
    #first prime tableData with the first variable
    tableData=[dict(tab_vars[0])]
    #iterate over the tab variables
    for tv in tab_vars:
        if tv['Section']==sec and tv['Subsection']==subsec:
            #add the variable to the table collection
            tableData.append(dict(tv))
        else:
            if sec:
                tableID = '{}{}{}'.format(tab,sec,subsec).replace(' ','_').replace('(','').replace(')','')
                tab_page.append(create_data_table(tableData,tableID))
                tableData=[dict(tv)]
            if tv['Section']!=sec:
                sec=tv['Section']
                #tab_page.append(html.Div([html.P(),html.H6(sec)]))
                tab_page.append(html.Div(html.H6(sec)))
            if tv['Subsection']!=subsec:
                subsec=tv['Subsection']
                if tv['Subsection']!='General':
                    tab_page.append(subsec)
    #add the final table
    tableID = '{}{}{}'.format(tab,sec,subsec).replace(' ','_').replace('(','').replace(')','')
    tab_page.append(create_data_table(tableData,tableID))
    return tab_page
 
def run_model(csp='tcslinear_fresnel',
              desal=None,
              finance=None,
              json_file=None,
              desal_file=None):
    '''
    runs solar thermal desal system with financial model
    '''
    print('entered run_model')
    stdm = SamBaseClass(CSP=csp,
                        desalination=desal,
                        financial=finance,
                        json_value_filepath=json_file,
                        desal_json_value_filepath=desal_file)
    stdm.main()

#copied from samJsonParser.py
#TODO seperate dict functions into separate module
def search_array_for_dict_with_key(s_array,key):
    '''
    returns False if dict is not found in array
    otherwise returns array index
    note: index 0 can be returned, so use explicit tests with result
    '''
    return next((i for i,item in enumerate(s_array) if key in item), False)

def unpack_keys_from_array_of_dicts(array_of_dicts):
    keys = []
    for k in array_of_dicts:
        keys.append(*k)
    return keys

def index_in_list_of_dicts(lists,key,value):
    '''
    checks lists to see if a key value exists in it
    returns the list and index of the first dict where the key and 
    value was found, else returns None,None

    none: index 0 can be returned, so use explicit tests with result
    '''
    for l in lists:
        for index, d in enumerate(l):
            if d[key] == value:
                return l,index
    return None,None

def get_weather_file():
    '''
    checks to see if a weather file was written to the user directory and
    returns it or the default weather file
    
    '''
    if weather_file_path.is_file():
        with open(weather_file_path, 'r') as f:
            return f.readline().strip()
    else:
        return default_weather_file
    
        
#
#MAIN PROGRAM
#
    
# open and load the json variables file
with open(solar_variables_file, "r") as read_file:
    solar_json_load = json.load(read_file)    
# open and load the json values file
with open(solar_model_values_file, "r") as read_file:
    solar_model_values = json.load(read_file)

# open and load the json desal variables file
with open(desal_variables_file, "r") as read_file:
    desal_json_load = json.load(read_file)   
# open and load the json desal values file
with open(desal_values_file, "r") as read_file:
    desal_model_values = json.load(read_file)

    
# creates a list of defaultdicts 
solar_model_vars=[]
for var in solar_json_load[model]:
    tempdict=defaultdict(lambda:'000General')
    tempdict.update(var)
    #add the value from the solar_model_values dict
    tempdict['Value']=solar_model_values.get(var['Name'],None)
    #clean up spaces in the tab, section, subsection names
    tempdict['Tab']=tempdict['Tab'].strip()
    tempdict['Section']=tempdict['Section'].strip()
    tempdict['Subsection']=tempdict['Subsection'].strip()
    #TODO create a better way to display and edit arrays/matrices
    #converting to string, otherwise array brackets are removed in tables
    if tempdict['DataType']=='SSC_ARRAY' or tempdict['DataType']=='SSC_MATRIX':
        tempdict['Value']=str(tempdict['Value'])
    solar_model_vars.append(tempdict)
    
# now do the same for desalination
desal_model_vars=[]
for dvar in desal_json_load[desal]:
    tempdict=defaultdict(lambda:'000General')
    tempdict.update(dvar)
    #add the value from the desal model_values dict
    tempdict['Value']=desal_model_values.get(dvar['Name'],None)
    #clean up spaces in the tab, section, subsection names
    tempdict['Tab']='Desalination'
    tempdict['Section']=tempdict['Section'].strip()
    tempdict['Subsection']=tempdict['Subsection'].strip()
    #converting to string, otherwise array brackets are removed in tables
    if tempdict['DataType']=='SSC_ARRAY' or tempdict['DataType']=='SSC_MATRIX':
        tempdict['Value']=str(tempdict['Value'])
    desal_model_vars.append(tempdict)

for modelVars in (desal_model_vars,solar_model_vars):
    # sort the lists by hierarchy
    modelVars.sort(key=itemgetter('Tab','Section','Subsection'))

    #fix 000General, which was a hack for sorting purposes
    for mv in modelVars:
            for k in mv.keys():
                try:
                    mv[k] = mv[k].replace('000General','General')
                except:
                    pass

# update weather file_name
l,wf_index = index_in_list_of_dicts([solar_model_vars],'Name','file_name')
solar_model_vars[wf_index]['Value']=str(get_weather_file())

# collect all unique solar tab names, sorting because set has no order
solar_tabs = sorted([*{*[t['Tab'] for t in solar_model_vars]}])
# move General to the front
if 'General' in solar_tabs:
    solar_tabs.insert(0, solar_tabs.pop(solar_tabs.index('General')))
    
# now do the same for desal tabs
desal_tabs = sorted([*{*[t['Tab'] for t in desal_model_vars]}])
# move General to the front
if 'General' in desal_tabs:
    desal_tabs.insert(0, solar_tabs.pop(desal_tabs.index('General')))

# references to which tabs and variables to use based on the button that was pressed
models = ['Desalination System','Solar Thermal System','Financial Model']

#NOTE! using desal variables in place of financial until finance in place 
Model_tabs = {models[0]:desal_tabs,
              models[2]:desal_tabs,
              models[1]:solar_tabs}
Model_vars = {models[0]:desal_model_vars,
              models[2]:desal_model_vars,
              models[1]:solar_model_vars}

model_vars_list = [desal_model_vars,solar_model_vars]


#
### APP LAYOUTS ###
#
#external_stylesheets = [dbc.themes.FLATLY]
#external_stylesheets = [dbc.themes.FLATLY,'https://codepen.io/chriddyp/pen/bWLwgP.css',]
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

tab_style = {
    'borderBottom': '1px solid #300C2D',
}

tab_selected_style = {
    'borderTop': '1px solid #300C2D',
    'borderLeft': '1px solid #300C2D',
    'borderRight': '1px solid #300C2D',
    #'borderBottom': '1px solid #d6d6d6',
    #'backgroundColor': '#119DFF',
    'color': '#300C2D',
    #'padding': '6px'
}

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
app.title = 'Model and Parameter Selection'

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

# not used at the moment but keeping in case we can figure out how
# to make a collaspible button group
# button_group = dbc.ButtonGroup(
#     [dbc.Button("Desalination System",id='desal-button'), 
#      dbc.Button("Solar Thermal System",id='solar-button'),
#      dbc.Button("Financial Model",id='finance-button')]
# )

loading = html.Div([
    html.P(),
    dcc.Loading(id="model-loading", children=[html.Div(id="model-loading-output")], type="default")]
)

model_vars_title = html.H3('Model Variables', className='page-header')

# used when the button_group was in place,
# keeping code in case we want to bring it back

# model_buttons = html.Div([
#     dbc.Row([
#         dbc.Col(button_group),
#         #dbc.Col(dbc.Button('Run Model', id='model-button')),
#         #dbc.Tooltip('Run the model after making changes to the variables in the tabs below',
#         #target='model-button')
#      ],justify="between")
# ])

def make_tabs_in_collapse(i):
    return dbc.Card(
        [
            dbc.Button(
                f"{i}",
                color="primary",
                id=f"{i}-toggle".replace(' ','_'),
            ),
            dbc.Collapse(
                dbc.CardBody(
                    [dcc.Tabs(id='tabs', value=Model_tabs[i][0], children=[
                        dcc.Tab(label=j, value=j, style=tab_style, 
                                selected_style=tab_selected_style, 
                                children=dbc.CardBody(      create_model_variable_page(j,Model_vars[i]))
                                )for j in Model_tabs[i]
                    ])]
                ),
                id=f"collapse-{i}".replace(' ','_'),
            ),
        ],style={'padding':0} #TODO need to figure out how to properly override the padding
    )

tabs_accordion = dbc.Card(
    [make_tabs_in_collapse(models[0]), make_tabs_in_collapse(models[1]), make_tabs_in_collapse(models[2])], className="accordion h-100"
) 

primary_card = dbc.Card(
    dbc.CardBody([
        html.Blockquote([
            html.H4("SIDE PANEL", className="card-title"),
            html.P(
                "Instructions and design model output can go here.",
                className="card-text"),
            html.Small("'Run Desal Design Model' and"
                        "'Run Model' buttons here?",
                        className="card-text"),
        ],className="blockquote"),
        # add a Spinner (and remove dcc.Loading)
        # when we figure out how to toggle it
        # dbc.Button(
        #     [dbc.Spinner(size="sm"), " Run Model"],
        #     color="primary",
        #     id='model-button'),
        dbc.Button("Run Model",color="primary",id="model-button"),
        dbc.Tooltip(
            "Run the model after reviewing and editing the Desalination, Solar Thermal and Financial variables",
            # "Run the Desal Design Model after editing and approving the variables "
            # "under Desalination System ",
            target="model-button"),
    ]),color="secondary", className="text-white"
)

desal_side_panel = dbc.CardBody([
    html.H6("DESALINATION SYSTEM INSTRUCTIONS", className="card-title"),
    html.P("blah blah blah", className='card-text'),
    dbc.Button('Run Desal Design', 
        color="primary", 
        id='run-desal-design'),
    dbc.Tooltip(
        "Run the Desal Design Model after editing and approving the variables under Desalination System",
        target="run-desal-design"),
    html.P(),
    html.Div(id='desal-design-results')
])

solar_side_panel = dbc.CardBody([
    html.H6("SOLAR THERMAL SYSTEM INSTRUCTIONS", className="card-title"),
    html.P("blah blah blah", className='card-text')
])
finance_side_panel = dbc.CardBody([
    html.H6("FINANCE MODEL INSTRUCTIONS", className="card-title"),
    html.P("blah blah blah", className='card-text')
])

model_card = dbc.Card(children=desal_side_panel,id='model-card',color="secondary", className="text-white")

side_panel = dbc.Card([model_card,primary_card,],className="h-100", color="secondary")

# side_panel = dbc.Card(
#     dbc.CardBody([
#         html.Blockquote([
#             html.H4("SIDE PANEL", className="card-title"),
#             html.P(
#                 "Instructions and design model output can go here.",
#                 className="card-text"),
#             html.Small("'Run Desal Design Model' and"
#                        "'Run Model' buttons here?",
#                        className="card-text"),
#         ],className="blockquote"),
#         dbc.Button('Run Desal Design', color="primary", id='run-desal-design'),
#         dbc.Tooltip(
#             "Run the Desal Design Model after editing and approving the variables "
#             "under Desalination System ",
#             target="run-desal-design"),
#         html.P(),
#         html.Div(id='desal-design-results')
#     ]),color="secondary", className="text-white h-100"
# )

# tabs = dbc.Row([dbc.Col(side_panel, width=3), dbc.Col(tabs_accordion, width=9)],no_gutters=True)
tabs = dbc.Row([dbc.Col(side_panel, width=3), dbc.Col(tabs_accordion, width=9)],no_gutters=True)

model_tables_layout = html.Div([model_vars_title, loading, tabs])

#
### CALLBACKS
#     
    
# the table callbacks are defined in a function above
create_callback_for_tables(desal_model_vars,solar_model_vars)

# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/model-selection':
        return model_selection_layout
    elif pathname == '/model-variables':
        return model_tables_layout
    else:
        return html.H5('404 URL not found')
  
# Once all three models have been selected,
# create a button to navigate to the model variables page
@app.callback(
    Output('model-parameters', 'children'),
    [Input('select-solar', 'value'),
     Input('select-desal', 'value'),
     Input('select-finance', 'value')])
def display_model_parameters(solar, desal, finance):
    if model and desal and finance:
        return html.Div([
            html.P(),
            
            dcc.Link(html.Button('Next'), href='/model-variables'),
        ])

# Displays tabs depending on what model type button is pushed
# @app.callback(Output('tabs-container','children'),
#               [Input('desal-button','n_clicks'),
#                Input('solar-button','n_clicks'),
#                Input('finance-button','n_clicks')])
# def display_model_tabs(solar,desal,finance):
#     ctx = dash.callback_context
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
#     if button_id == 'finance-button':
#         #until finance tabs are implemented,
#         #then we can remove the if statement
#         return('Finance Tabs go here')
#     else: 
#         return(
#             [dcc.Tabs(id='tabs', value='General', children=[
#             dcc.Tab(label=i, value=i, style=tab_style, 
#                     selected_style=tab_selected_style, 
#                     children=create_model_variable_page(i,Model_vars[button_id])
#             )for i in Model_tabs[button_id]
#         ])])
## models = ['Desalination System','Solar Thermal System','Financial Model']
        
@app.callback(
    Output('desal-design-results', 'children'),
    [Input('run-desal-design', 'n_clicks')])
def run_desal_design(desalDesign):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return ""
    else:
        stdm = SamBaseClass()
        stdm.desal_design(desal=desal)
        with open(desal_design_infile, "r") as read_file:
            desal_design_load = json.load(read_file)
        dd_outputs = []
        for dd in desal_design_load:
            dd_outputs.append(html.Div(f"{dd['Name']}: {dd['Value']} {dd['Unit']}"))
        return dbc.Alert(dd_outputs)

@app.callback(
    Output('model-card','children'),
    [Input(f"{i}-toggle".replace(' ','_'), "n_clicks") for i in models],
)
def toggle_model_side_panel(m1,m2,m3):
    ctx = dash.callback_context

    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    else:
        button_id = 'default'

    if button_id == 'Solar_Thermal_System-toggle':
        return solar_side_panel
    elif button_id == 'Financial_Model-toggle':
        return finance_side_panel
    else: #default and 'Desalination_System-toggle'
        return desal_side_panel

@app.callback(
    [Output(f"collapse-{i}".replace(' ','_'), "is_open") for i in models],
    [Input(f"{i}-toggle".replace(' ','_'), "n_clicks") for i in models],
    [State(f"collapse-{i}".replace(' ','_'), "is_open") for i in models])
def toggle_model_tabs(n1, n2, n3, is_open1, is_open2, is_open3):
    ctx = dash.callback_context

    if not ctx.triggered:
        return ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
   
    if button_id == f"{models[0]}-toggle".replace(' ','_') and n1:
        return not is_open1, False, False
    elif button_id == f"{models[1]}-toggle".replace(' ','_') and n2:
        return False, not is_open2, False
    elif button_id == f"{models[2]}-toggle".replace(' ','_') and n3:
        return False, False, not is_open3
    return False, False, False
  
    
    # if button_id == 'finance-button':
    #     #until finance tabs are implemented,
    #     #then we can remove the if statement
    #     return('Finance Tabs go here')
    # else: 
    #     return(
    #         [dcc.Tabs(id='tabs', value=Model_tabs[button_id][0], children=[
    #         dcc.Tab(label=i, value=i, style=tab_style, 
    #                 selected_style=tab_selected_style, 
    #                 children=create_model_variable_page(i,Model_vars[button_id])
    #         )for i in Model_tabs[button_id]
    #     ])])
    
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

#TODO Dynamic Table title based on model selection
# @app.callback(
#     Output('solar-tables-title', 'children'),
#     [Input('select-solar','value')])
# def set_tables_title(solar_value):
#     return '{} Model Parameters'.format(Solar[solar_value])
    
if __name__ == '__main__':
    app.run_server(debug=True, port=8073)



