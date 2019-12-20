# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 13:55:35 2019

@author: jsquires
"""

import dash
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
#from SAM.SamBaseClass import SamBaseClass
from SAM_flatJSON.SamBaseClass import SamBaseClass

# GLOBAL VARIABLES ###
model = 'tcstrough_physical'
finance = 'none'
json_infiles_dir = base_path / 'SAM_flatJSON' / 'models' / 'inputs'
json_defaults_dir = base_path / 'SAM_flatJSON' / 'defaults'

#TODO: build this later based on model selection within the GUI
model_variables_file = json_infiles_dir/ '{}_inputs.json'.format(model)
model_values_file = json_defaults_dir / '{}_{}.json'.format(model,finance)
json_outpath = base_path / 'app' / 'user-generated-inputs'

default_weather_file = base_path / 'SAM' / 'solar_resource' / 'tucson_az_32.116521_-110.933042_psmv3_60_tmy.csv'
weather_file_path = json_outpath / 'weather-file-location.txt'

# dict for desalination 'values' and 'labels'
Desal = {'FOR':'Forward Osmosis                          ',
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
    'FPC' : [('FOR',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'IPHP': [('FOR',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'IPHD': [('FOR',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'ISCC': [('FOR',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'DSLF': [('FOR',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'MSLF': [('FOR',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'DSPT': [('FOR',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'MSPT': [('FOR',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'PT'  : [('FOR',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
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
        {'name':'Value',    'id':'Value','editable':True, 'type':'numeric'},
        {'name':'Units',    'id':'Units','editable':False}]


def create_callback_for_tables(variables):
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
        
    states = []
    
    #Collect the table ids
    table_ids = table_ids = [*{*[ '{}{}{}'.format(v['Tab'],v['Section'],v['Subsection'])\
                                 .replace(' ','_').replace('(','').replace(')','')\
                                 for v in model_vars]}]

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
        def _update_model_variables(tbl_data):
            '''find the dict with the unique value of Name and update that dict'''
            for td in tbl_data:
                unique_val=td['Name']
                index = index_in_list_of_dicts(model_vars,'Name',unique_val)
                model_vars[index].update(td)
   
        if n_clicks:
            #tableData states are in groups of threes
            #i is the table data_timestamp, i+1 is the id and i+2 is the data
            for i in range(0,len(tableData),2):
                updated = tableData[i]
                tbl_data = tableData[i+1]
                if updated:
                    #overwrite the dict with the updated data from the table
                    _update_model_variables(tbl_data)  
            #create the json file that will be the input to the model
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            model_outfile = model+timestamp+'_inputs.json'
            model_outfile_path = Path(json_outpath / model_outfile)
            with model_outfile_path.open('w') as write_file:
                json.dump(model_vars, write_file)
        
            index = index_in_list_of_dicts(model_vars,'Name','file_name')
            weather_from_user=model_vars[index]['Value']

            #run the model
            run_model(csp=model,
                      desal=None,
                      finance=None,
                      json_file=model_outfile_path,               
                      weather=weather_from_user)
            return (
                    dcc.Markdown('''Model run complete. [View results.](http://127.0.0.1:8051/)''')
                    )
        else:
            return 'Edit the variables in the tabs below and then Run Model'
                        
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

def create_model_variable_page(tab):
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
                tab_page.append(html.H6(sec))
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
              weather=default_weather_file):
    '''
    runs solar thermal desal model
    currently only setup for SAM models
    financial model is currently hardcoded
    '''
    #TODO run non-SAM models
    stdm = SamBaseClass(CSP=csp,
                        desalination=desal,
                        financial=finance,
                        json_value_filepath=json_file,
                        weatherfile=weather)
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

def index_in_list_of_dicts(array,key,value):
    '''
    returns None or index of first dict 
    containing the key and value
    none: index 0 can be returned, so use explicit tests with result
    '''
    for index, d in enumerate(array):
        if d[key] == value:
            return index
    return None

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
#MAIN PROGRAM (TODO create main() after testing...)
#
    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# open and load the json variables file
with open(model_variables_file, "r") as read_file:
    json_load = json.load(read_file)
    
# open and load the json values file
with open(model_values_file, "r") as read_file:
    model_values = json.load(read_file)
    
# creates a list of defaultdicts 
model_vars=[]
for var in json_load[model]:
    tempdict=defaultdict(lambda:'000General')
    tempdict.update(var)
    #add the value from the model_values dict
    #tempdict['Value']=model_values[var['Name']]
    #rank = dict.get(key, 1.0)
    tempdict['Value']=model_values.get(var['Name'],None)
    model_vars.append(tempdict)
    
# sort the list by hierarchy
model_vars.sort(key=itemgetter('Tab','Section','Subsection'))

#fix 000General, which was a hack for sorting purposes
for mv in model_vars:
    for k in mv.keys():
        if k == 'Tab' or k == 'Section' or k == 'Subsection':
            mv[k] = mv[k].replace('000General','General')

# update weather file_name
wf_index = index_in_list_of_dicts(model_vars,'Name','file_name')
model_vars[wf_index]['Value']=get_weather_file()
            
# collect all unique tab names, sorting because set has no order
model_tabs = sorted([*{*[t['Tab'] for t in model_vars]}])
# move General to the front
if 'General' in model_tabs:
    model_tabs.insert(0, model_tabs.pop(model_tabs.index('General')))
        
# run the app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
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
#    html.Div([
#        html.Div(id='model-parameters'),
#    ],className='four columns'),
])
            
model_tables_layout = html.Div([
    html.H6('{} Model Parameters'.format('TCS Linear Fresnel')), #TODO replace with a lookup and the model variable
    
    html.P(),
    dcc.Loading(id="model-loading", children=[html.Div(id="model-loading-output")], type="default"),
    html.Div([html.Button('Run Model', id='model-button', title='Run the model after making changes to the variables in the tabs below')]),
    html.Div([
        dcc.Tabs(id='tabs', value='Model-Tabs', children=[
            dcc.Tab(label=i, value=i, style=tab_style, 
                    selected_style=tab_selected_style, 
                    children=create_model_variable_page(i)
            )for i in model_tabs
        ]),
    ],id='tabs-container'),
])
            
create_callback_for_tables(model_vars)

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

@app.callback(
    Output('select-desal', 'options'),
    [Input('select-solar', 'value')])
def set_desal_options(solarModel):
    return [{'label': Desal[i[0]], 'value': i[0], 'disabled': i[1]} for i in solarToDesal[solarModel]]#,value='ABS'

#TODO combine with select-desal above?
@app.callback(
    Output('select-finance', 'options'),
    [Input('select-solar', 'value')])
def set_finance_options(desalModel):
    return [{'label': Financial[i[0]], 'value': i[0], 'disabled': i[1]} for i in solarToFinance[desalModel]]
    
if __name__ == '__main__':
    app.run_server(debug=False, port=8068)



