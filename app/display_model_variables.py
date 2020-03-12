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
import dmv_config as cfg
import json
import sys

from collections import defaultdict
from dash.dependencies import Input, Output, State
from datetime import datetime
from operator import itemgetter
from pathlib import Path

sys.path.insert(0,str(cfg.base_path))
from SAM_flatJSON.SamBaseClass import SamBaseClass

#define columns used in data tables
cols = [{'name':'Variable', 'id':'Label','editable':False},
        {'name':'Value',    'id':'Value','editable':True},
        {'name':'Units',    'id':'Units','editable':False}]

#
### FUNCTIONS ###
#

def collect_and_sort_model_tabs(model_variable_list):
    '''
    @model_variable_lists = list of model variable dicts
        to pull tabs from
    Returns sorted unique tabs list
    '''
    mv_tabs = [*(dict.fromkeys([t['Tab'] for t in model_variable_list]).keys())]
    # move General to the front
    if 'General' in mv_tabs:
        mv_tabs.insert(0, mv_tabs.pop(mv_tabs.index('General')))
    return mv_tabs

def create_callback_for_tables(model_vars_list):
    '''
    processes model variables and generates a table_id with the form:
    'Solar_FieldMirror_WashingGeneral'
    
    where Solar_Field, Mirror_Washing, and General are the
    tab, section and subsection names with spaces replaced by underscores.
     
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

    for mVs in model_vars_list:
        #Collect the table ids
        table_ids = [*{*[ f"{v['Tab']}{v['Section']}{v['Subsection']}"\
                    .replace(' ','_').replace('(','').replace(')','')\
                    .replace('/','') for v in mVs]}]
                                        
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

        if n_clicks:
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
            solar_output_vars = dict()
            desal_output_vars = dict()
            finance_output_vars = dict()
            for dvar in desal_model_vars:
                desal_output_vars[dvar['Name']] = _convert_strings_to_literal(dvar)
            for svar in solar_model_vars:
                solar_output_vars[svar['Name']] = _convert_strings_to_literal(svar)
            for fvar in finance_model_vars:
                finance_output_vars[fvar['Name']] = _convert_strings_to_literal(fvar)
                
            #create the solar json file that will be the input to the model
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            solar_model_outfile = cfg.solar+timestamp+'_inputs.json'
            solar_model_outfile_path = Path(cfg.json_outpath / solar_model_outfile)
            with solar_model_outfile_path.open('w') as write_file:
                json.dump(solar_output_vars, write_file)
            #create the desal json file that will be the input to the model
            desal_model_outfile = cfg.desal+timestamp+'_inputs.json'
            desal_model_outfile_path = Path(cfg.json_outpath / desal_model_outfile)
            with desal_model_outfile_path.open('w') as write_file:
                json.dump(desal_output_vars, write_file)  
            #create the finance json file that will be the input to the model
            finance_model_outfile = cfg.finance+timestamp+'_inputs.json'
            finance_model_outfile_path = Path(cfg.json_outpath / finance_model_outfile)
            with finance_model_outfile_path.open('w') as write_file:
                json.dump(finance_output_vars, write_file)  
            
            #TODO these should not be hardcoded
            #run the model
            run_model(csp=cfg.solar,
                      desal=cfg.desal,
                      finance=cfg.finance,
                      json_file=solar_model_outfile_path,
                      desal_file=desal_model_outfile_path,
                      finance_file=finance_model_outfile_path)
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
                tableID = '{}{}{}'.format(tab,sec,subsec).replace(' ','_').replace('(','').replace(')','').replace('/','')
                tab_page.append(create_data_table(tableData,tableID))
                tableData=[dict(tv)]
            if tv['Section']!=sec:
                sec=tv['Section']
                #tab_page.append(html.Div([html.P(),html.H6(sec)]))
                tab_page.append(html.H5(sec))
            if tv['Subsection']!=subsec:
                subsec=tv['Subsection']
                if tv['Subsection']!='General':
                    tab_page.append(html.H6(subsec))
    #add the final table
    tableID = '{}{}{}'.format(tab,sec,subsec).replace(' ','_').replace('(','').replace(')','').replace('/','')
    tab_page.append(create_data_table(tableData,tableID))
    return tab_page

def create_variable_lists(model_name, json_vars, json_vals):
    '''
    @json_vars: string containing path to json
        model variables file
    @json_vals: string containing path to json
        model values file
    opens and loads json variable and value files,
    matches up variables to values,
    cleans up the values, removing spaces
    sorts the values by hierarchy
    returns: a list of default dicts
    '''  
    model_vars = []
    # open and load the json variables file
    with open(json_vars, "r") as read_file:
        json_vars_load = json.load(read_file)    
    # open and load the json values file
    with open(json_vals, "r") as read_file:
        json_vals_load = json.load(read_file)
    # create a list of default dicts
    for var in json_vars_load[model_name]:
        tempdict=defaultdict(lambda:'000General')
        tempdict.update(var)
        #add the value from the solar_model_values dict
        tempdict['Value']=json_vals_load.get(var['Name'],None)
        #clean up spaces in the tab, section, subsection names
        tempdict['Tab']=tempdict['Tab'].strip()
        tempdict['Section']=tempdict['Section'].strip()
        tempdict['Subsection']=tempdict['Subsection'].strip()
        #TODO create a better way to display and edit arrays/matrices
        #converting to string, otherwise array brackets are removed in tables
        if tempdict['DataType']=='SSC_ARRAY' or tempdict['DataType']=='SSC_MATRIX':
            tempdict['Value']=str(tempdict['Value'])
        model_vars.append(tempdict)
    # sort the lists by hierarchy
    #model_vars.sort(key=itemgetter('Tab','Section','Subsection'))
    #fix 000General, which was a hack for sorting purposes
    for mv in model_vars:
            for k in mv.keys():
                try:
                    mv[k] = mv[k].replace('000General','General')
                except:
                    pass
    return model_vars

def json_update(data, filename):
    '''
    updates dict in json file
    @data dict: data to update json dict
    @filename str: json file path containing dict to update
    '''
    tmp = json_load(filename)
    tmp.update(data)
    with open(filename,'w') as json_file:
        json.dump(tmp, json_file) 

def json_load(filename):
    '''returns contents of json file'''
    try: 
        with open(filename) as json_file: 
            return json.load(json_file)
    except FileNotFoundError:
        return {}
    
def get_weather_file():
    '''
    checks to see if a weather file was written to the user directory and
    returns it or the default weather file
    
    '''
    if cfg.weather_file_path.is_file():
        with open(cfg.weather_file_path, 'r') as f:
            return f.readline().strip()
    else:
        return cfg.default_weather_file

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

def run_model(csp='tcslinear_fresnel',
              desal=None,
              finance=None,
              json_file=None,
              desal_file=None,
              finance_file=None):
    '''
    runs solar thermal desal system with financial model
    '''
    stdm = SamBaseClass(CSP=csp,
                        desalination=desal,
                        financial=finance,
                        json_value_filepath=json_file,
                        desal_json_value_filepath=desal_file,
                        cost_json_value_filepath=finance_file)
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
        
#
#MAIN PROGRAM
#

# first prime the app_json
json_update(cfg.app_json_init,cfg.app_json)

solar_model_vars = create_variable_lists(
    model_name=cfg.solar, 
    json_vars=cfg.solar_variables_file,
    json_vals=cfg.solar_values_file)
desal_model_vars = create_variable_lists(
    model_name=cfg.desal, 
    json_vars=cfg.desal_variables_file,
    json_vals=cfg.desal_values_file)
finance_model_vars = create_variable_lists(
    model_name=cfg.finance, 
    json_vars=cfg.finance_variables_file,
    json_vals=cfg.finance_values_file)
desal_finance_model_vars = create_variable_lists(
    model_name=cfg.desal, 
    json_vars=cfg.desal_finance_variables_file,
    json_vals=cfg.desal_finance_values_file)

# append the desal_finance variables to the finance variables
finance_model_vars += desal_finance_model_vars

#process desal_finance_vars =
# then append to finance model vars

# PULL SORT functions out of create_variable_lists
# create new SORT function

# update weather file_name
l,wf_index = index_in_list_of_dicts([solar_model_vars],'Name','file_name')
solar_model_vars[wf_index]['Value']=str(get_weather_file())

solar_tabs = collect_and_sort_model_tabs(solar_model_vars)
desal_tabs = collect_and_sort_model_tabs(desal_model_vars)
finance_tabs = collect_and_sort_model_tabs(finance_model_vars)

# references for tabs and variables to use based on selected button
models = ['desal','solar','finance']

Model_tabs = {models[0]:desal_tabs,
              models[2]:finance_tabs,
              models[1]:solar_tabs}
Model_vars = {models[0]:desal_model_vars,
              models[2]:finance_model_vars,
              models[1]:solar_model_vars}

model_vars_list = [desal_model_vars,solar_model_vars,finance_model_vars]


#
### APP LAYOUTS ###
#
external_stylesheets = [dbc.themes.FLATLY]
#external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
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
    'color': '#0C300F',
    #'padding': '6px'
}

def serve_layout():
    return application_layout

application_layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
app.layout = serve_layout
app.title = 'Model and Parameter Selection'

model_selection_layout = html.Div([
    dbc.FormGroup([
        dbc.Label("Solar Thermal System", width=2, size='lg',color='warning',style={'text-align':'center'}),
        dbc.Col(
            dbc.RadioItems(
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
                ],
                value='DSLF',
            ),width=10,
        ),
    ],row=True),
    dbc.FormGroup([
        #dbc.Label("Desalination System", width=2, size='lg',color='success',style={'text-align':'center'}),
        dbc.Label("Desalination System",width=2, size='lg',color='success',style={'text-align':'center'}),
        dbc.Col(
            dbc.RadioItems(
                id='select-desal',
            ),width=10,
        ),
    ],row=True,),
    dbc.FormGroup([
        dbc.Label("Financial Model",width=2, size='lg',color='primary',style={'text-align':'center'}),
        dbc.Col(
            dbc.RadioItems(
                id='select-finance',
            ),width=10,
        ),
    ],row=True,),
    dbc.Col(id='model-parameters',
    width=2, 
    style={'horizontal-align':'center'})
])

loading = html.Div([
    html.P(),
    dcc.Loading(id="model-loading", children=[html.Div(id="model-loading-output")], type="default", color="#18BC9C")]
)

model_vars_title = html.Div([
    html.H3('System Configuration', className='page-header'),
    html.P()])

def make_tabs_in_collapse(i):
    # return the tabs belonging to the collapse button
    return dbc.Card(
        [
            dbc.Button(
                html.Div("Title Here",id=f'collapse-title-{i}'),
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
    [make_tabs_in_collapse(m) for m in models],
    className="accordion h-100", 
    id='tabs-card'
)

primary_card = dbc.Card(
    dbc.CardBody([
        html.H4(
            "System Performance Simulation", 
            className="card-title"),
        html.P(
            "Simulate the hourly performance of the solar field and desalination components, and estimate the cost of the system.",
            className="card-text"),
        # add a Spinner (and remove dcc.Loading)
        # when we figure out how to toggle it
        # dbc.Button(
        #     [dbc.Spinner(size="sm"), " Run Model"],
        #     color="primary",
        #     id='model-button'),
        dbc.Button("Run Simulation Model",color="primary",id="model-button"),
        dbc.Tooltip(
            "Run the model after reviewing and editing the Desalination, Solar Thermal and Financial variables. The model takes 1-2 minutes to run.",
            target="model-button"),
        loading,
    ]),color="secondary", className="text-white"
)

desal_side_panel = dbc.CardBody([
    html.H4("Desalination Design Model", className="card-title"),
    html.P("This model estimates the nominal power consumption given the specified parameters in the desalination system. Please run the design model first and specify the thermal load in the solar thermal model accordingly.", className='card-text'),
    dbc.Button('Run Design Model', 
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

tabs = dbc.Row([dbc.Col(side_panel, width=3), dbc.Col(tabs_accordion, width=9)],no_gutters=True)

model_tables_layout = html.Div([model_vars_title, tabs])

#
### CALLBACKS
#     
    
# the table callbacks are defined in a function above
create_callback_for_tables(model_vars_list)

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
    '''
    After all 3 models are selected updates app JSON file and 
    creates button to navigate to model variables page
    '''
    if solar and desal and finance:
        json_update(data={'solar':solar, 'desal':desal, 'finance':finance},  
                    filename=cfg.app_json)
        return html.Div([
            html.P(),
            dcc.Link(dbc.Button("Next", color="primary", block=True, size='lg'), href='/model-variables')])
        
@app.callback(
    Output('desal-design-results', 'children'),
    [Input('run-desal-design', 'n_clicks')])
def run_desal_design(desalDesign):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return ""
    else:
        stdm = SamBaseClass()
        stdm.desal_design(desal=cfg.desal)
        with open(cfg.desal_design_infile, "r") as read_file:
            desal_design_load = json.load(read_file)
        dd_outputs = []
        for dd in desal_design_load:
            dd_val = dd['Value']
            if isinstance(dd_val,int):
                dd_val = f'{dd_val:,}'
            elif isinstance(dd_val,float):
                dd_val = f'{dd_val:,.2f}'
            dd_outputs.append(html.Div(f"{dd['Name']}: {dd_val} {dd['Unit']}"))
        return dbc.Alert(dd_outputs)

@app.callback([Output(f"collapse-title-{i}", 'children') for i in models],
            [Input('tabs-card','children')])
def title_collapse_buttons(x):
    '''Titles the collapse buttons based on values stored in JSON file'''
    app_vals = json_load(cfg.app_json)
    d = f"{cfg.Desal[app_vals['desal']].rstrip()} Desalination System"
    s = cfg.Solar[app_vals['solar']].rstrip()
    f = cfg.Financial[app_vals['finance']].rstrip()
    return d,s,f

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

    if button_id == 'solar-toggle':
        return solar_side_panel
    elif button_id == 'finance-toggle':
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
 
if __name__ == '__main__':
    app.run_server(debug=True, port=8074)
