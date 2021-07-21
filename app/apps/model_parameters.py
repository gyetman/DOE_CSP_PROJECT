import ast
import json
import sys
from collections import defaultdict
from datetime import datetime
from operator import itemgetter
from pathlib import Path
import itertools
import base64

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import ALL, Input, Output, State

import app_config as cfg
sys.path.insert(0,str(cfg.base_path))

import parameter_dependencies as pdeps
import helpers
from app import app
from SAM_flatJSON.SamBaseClass import SamBaseClass

models = ['desal','solar','finance']


#TODO:
# use dictionary .get function for parameters on parametric study
# without it, empty results throw an error, where they should just
# not enable the run model button. 
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

def convert_strings_to_literal(v):
    '''converts some string values to their literal values'''
    #arrays and matrices need to be converted back from string
    if v['DataType']=='SSC_ARRAY' or v['DataType']=='SSC_MATRIX':
        return ast.literal_eval(v['Value'])
    #SSC_NUMBER, now represented as string after user edited in table
    #need to be changed back to numbers
    elif v['DataType']=='SSC_NUMBER' and isinstance(v['Value'],str):
        return ast.literal_eval(v['Value'])
    else:
        return v['Value']
                        
def create_data_table(table_data, table_index, model_type, model_name, selectable): #ZZZ
    return html.Div([
        html.P(),
        dash_table.DataTable(
            #type i.e. 'solar-table'
            #index is the tab-section-subsection 
            id={'type':f'{model_type}-table', 'model': model_name, 'index':table_index}, #ZZZ
            columns=cols,
            data=table_data,
            editable=True,
            row_selectable='multi' if selectable else False,
            style_cell={
                'textAlign': 'left',
                'maxWidth': '360px',
                'whiteSpace': 'no-wrap',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Label'},
                    'width': '65%'},
                {'if': {'column_id': 'Value'},
                    'width': '15%','textAlign': 'right'},
                {'if': {'column_id': 'Units'},
                    'width': '5%','textAlign': 'right'},
                {'if': {'column_id': 'Min'},
                    'display':'none' if not selectable else 'true',
                    'width': '5%','textAlign': 'right'},
                 {'if': {'column_id': 'Max'},
                    'display':'none' if not selectable else 'true',
                    'width': '5%','textAlign': 'right'},
                 {'if': {'column_id': 'Interval'},
                    'display':'none' if not selectable else 'true',
                    'width': '5%','textAlign': 'right'},
                #hide DataType this field is used for processing
                {'if': {'column_id': 'DataType'},
                    'display': 'none'}
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

def create_model_variable_page(tab, model_vars, model_type):
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
    
    app = helpers.json_load(cfg.app_json)
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
                tab_page.append(create_data_table(tableData,tableID,model_type, app[model_type], app['parametric'])) #ZZZ
                tableData=[dict(tv)]
            if tv['Section']!=sec:
                sec=tv['Section']
                tab_page.append(html.H5(sec))
            if tv['Subsection']!=subsec:
                subsec=tv['Subsection']
                if tv['Subsection']!='General':
                    tab_page.append(html.H6(subsec))
    #add the final table
    tableID = '{}{}{}'.format(tab,sec,subsec).replace(' ','_').replace('(','').replace(')','').replace('/','')

    tab_page.append(create_data_table(tableData,tableID,model_type, app[model_type],app['parametric'])) #ZZZ
    return tab_page

def create_variable_lists(model_name, json_vars, json_vals):
    '''
    @json_vars: string containing path to json model variables file
    @json_vals: string containing path to json model values file
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
        tempdict['id']=var['Name']
        tempdict['Value']=json_vals_load.get(var['Name'],None)
        #clean up spaces in the tab, section, subsection names
        tempdict['Tab']=tempdict['Tab'].strip()
        tempdict['Section']=tempdict['Section'].strip()
        tempdict['Subsection']=tempdict['Subsection'].strip()
        
        # #Hide variables
        # if "Hidden" in var.keys():
        #     print(var['Lab'])
        #     continue
        
        #TODO create a better way to display and edit arrays/matrices
        #converting to string, otherwise array brackets are removed in tables
        if tempdict['DataType']=='SSC_ARRAY' or tempdict['DataType']=='SSC_MATRIX':
            tempdict['Value']=str(tempdict['Value'])
        elif tempdict['DataType'] == 'SSC_NUMBER':
            tempval = tempdict['Value']
            if type(tempval) is float:
                if tempval < 1:
                    tempdict['Value'] = round(tempval,4)
                else:
                    tempdict['Value'] = round(tempval, 1)
                    
        model_vars.append(tempdict)
    # sort the lists by hierarchy
    model_vars.sort(key=itemgetter('Tab','Section','Subsection'))
    #fix 000General, which was a hack for sorting purposes
    for mv in model_vars:
            for k in mv.keys():
                try:
                    mv[k] = mv[k].replace('000General','General')
                except:
                    pass
    return model_vars

def run_model(csp, desal, finance, json_file, desal_file, finance_file, timestamps):
    '''
    runs solar thermal desal system with financial model
    '''
    stdm = SamBaseClass(CSP=csp,
                        desalination=desal,
                        financial=finance,
                        json_value_filepath=json_file,
                        desal_json_value_filepath=desal_file,
                        cost_json_value_filepath=finance_file,
                        timestamp = timestamps)
    stdm.desal_design(desal)
    stdm.main()

#
### APP LAYOUTS ###
#

#define columns used in data tables
cols = [{'name':'Variable', 'id':'Label','editable':False},
        {'name':'Value',    'id':'Value','editable':True},
        {'name':'Units',    'id':'Units','editable':False},
        {'name':'DataType', 'id':'DataType'},
        {'name':'Min',      'id':'Min',  'editable':True},
        {'name':'Max',      'id':'Max',  'editable':True},
        {'name':'Interval',     'id':'Interval', 'editable':True}
        ]

tab_style = {
    'borderBottom': '1px solid #300C2D',
}

tab_selected_style = {
    'borderTop': '1px solid #300C2D',
    'borderLeft': '1px solid #300C2D',
    'borderRight': '1px solid #300C2D',
    'color': '#0C300F',
}

app.title = 'Model Parameters'

loading = html.Div([
    html.P(''),
    dcc.Loading(id="model-loading", type="default", color="#18BC9C")]
)

parameters_navbar = dbc.NavbarSimple(
    children=[dbc.NavItem(dbc.NavLink("Home", href='/home')),
              dbc.NavItem(dbc.NavLink("Models", href='/model-selection')),
              dbc.NavItem(dbc.NavLink("Parameters"), active=True),
              dbc.NavItem(dbc.NavLink('Help', href='/assets/docs/documentation.pdf', target='_blank', external_link=True))
    ],
    brand="System Configuration",
    color="primary",
    dark=True,
    sticky='top',
    style={'margin-bottom':60}
)

parametric_alert = html.Div([
    dbc.Alert([html.Strong("For Parametric Studies"), 
        html.P("Check the box for up to two targeted variables and input Min, Max and Interval values. Be aware that parametric study may take more than 5 minutes and does not produce an analysis report.")],
        className="alert alert-dismissible alert-light",
        dismissable=True,
        id='parametric-alert',
        is_open = False,
        style={'color':'Brown'})
    ],id='p-alert-init')

powertower_alert = html.Div([
    dbc.Alert([html.Strong("For Power Tower Molten Salt system"), 
        html.P("System capacity should be larger than 20 MW, and the desalination plant should be sized accordingly. Be aware that power tower models take longer than other models.")],
        className="alert alert-dismissible alert-light",
        dismissable=True,
        id='powertower-alert',
        is_open = False,
        style={'color':'Brown'})
    ],id='powertower-alert-init')

powertower2_alert = html.Div([
    dbc.Alert([html.Strong("For Power Tower Direct Steam system"), 
        html.P("System capacity should be larger than 30 MW, and the desalination plant should be sized accordingly. Be aware that power tower models take longer than other models.")],
        className="alert alert-dismissible alert-light",
        dismissable=True,
        id='powertower2-alert',
        is_open = False,
        style={'color':'Brown'})
    ],id='powertower2-alert-init')

tabs_accordion = html.Div([
    parametric_alert, 
    powertower_alert,
    powertower2_alert,
    dbc.Card('TEST',
        className="accordion h-100", 
        id='tabs-card')
])

desal_side_panel = dbc.CardBody([
    html.H4("Desalination Design Model", className="card-title"),
    html.P("This model estimates the nominal power consumption given the specified parameters in the desalination system. For thermal desalination models, you should run the design model first if you change any variable in the desalination system. Then you should size the solar field capacity according to the resulted thermal power consumption. \nThe solar system capacity in different solar thermal models can be found in the following sub-folders:", className='card-text'),
    html.P("Static Collector model: System Design / Design capacity", className='card-text'),
    html.P("Industrial Process Heat Parabolic Trough: System Design / Design Point Parameters / Heat Sink / Heat sink power ", className='card-text'),
    html.P("Industrial Process Linear Fresnel Direct Steam: System Design / Heat sink power", className='card-text'),
    dbc.Button('Run Design Model', 
        color="primary", 
        id='run-desal-design'),
    dbc.Tooltip(
        "Run the Desal Design Model after editing and approving the variables under Desalination System",
        target="run-desal-design"),
])

solar_side_panel = dbc.CardBody([
    html.H4("Solar Thermal System Model", className="card-title"),
    html.P("", className='card-text'),
])
finance_side_panel = dbc.CardBody([
    html.H4("Finance Model", className="card-title"),
    html.P("", className='card-text'),
])

primary_card = dbc.Card(
    dbc.CardBody([
        html.H4(
            "System Performance Simulation", 
            className="card-title"),
        html.P(
            "Simulate the hourly performance of the solar field and desalination components, and estimate the cost of the system.",
            className="card-text"),
        #HERE
        dbc.Row([dbc.Col([html.Div([
            dbc.Button("Run Simulation Model",color="primary",id="model-button"),
            dbc.Tooltip(
                "Run the model after reviewing and editing the Desalination, Solar Thermal and Financial variables. The model takes 1-2 minutes to run.",
                target="model-button"),
            ])]),
            dbc.Col([loading])
        ],id='sim-button'),
        html.Div(id="model-loading-output")
    ]),color="secondary", className="text-white"
)


SAM_JSON_BUTTON = html.Div(children=html.Div(id='sam-json'),id='sam-json-button')

SAM_JSON_file = dcc.Upload(
    html.Button('If you start your project from SAM, you may click here to upload a SAM generated JSON file and import the inputs'),
    style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '45px',
        'textAlign': 'center',
        'margin': '10px'
    },
    id = 'sam-json')

model_card = dbc.Card(children=desal_side_panel,id='model-card',color="secondary", className="text-white")

desal_design_results_card = dbc.Card(
    dbc.CardBody([
        html.Div(id='desal-design-results')
    ]), color="secondary", className="text-white"
)

side_panel = dbc.Card([model_card, desal_design_results_card, primary_card,],className="h-100", color="secondary")

tabs = dbc.Row([dbc.Col(side_panel, width=3), dbc.Col([tabs_accordion, SAM_JSON_BUTTON], width=9, id='tabs-data-initialize')],no_gutters=True)

model_tables_layout = html.Div([parameters_navbar, tabs])

#
### CALLBACKS
#     

# NOTE: we'll want to eventually unpack the dict for the function call... 
for model, functions in pdeps.functions_per_model.items():
    model_type=pdeps.find_model_type(model)
    for function in functions:    
        @app.callback(
            [Output({'type': f'{model_type}-table',
                    'index': outp,
                    'model': model},
                    'data')
                for outp in function['output_ids']],
            [Input({'type': f'{model_type}-table',
                    'index': inp,
                    'model': model},
                    'data_timestamp')
                for inp in function['input_ids']],
            [State({'type': f'{model_type}-table',
                    'index': state,
                    'model': model},
                    'data') 
                for state in function['input_ids'] + function['output_ids']],
            prevent_initial_call=True)
        def get_table_outputs(*states, function = function):

            intables = [state for state in states if type(state)==list]
            return pdeps.function_switcher(function['function'],intables)

                
@app.callback(
    Output('tabs-card', 'children'),
    [Input('tabs-data-initialize', 'children'),
     Input('sam-json','contents')]
)
def create_tabs_and_tables(x, samjson):
    # return the tabs belonging to the collapse button

    #create dict lookups for model and filenames
    app = helpers.json_load(cfg.app_json)
    flkup = cfg.build_file_lookup(app['solar'],app['desal'],app['finance'],app['timestamp'])
      

    solar_model_vars = create_variable_lists(
        model_name=app['solar'], 
        json_vars=flkup['solar_variables_file'],
        json_vals=flkup['solar_values_file']) 
    desal_model_vars = create_variable_lists(
        model_name=app['desal'], 
        json_vars=flkup['desal_variables_file'],
        json_vals=flkup['desal_values_file'])
    
    if app['solar'] == "SC_ETC" or app['solar'] == "SC_FPC" :
        
        flkup2 = cfg.build_file_lookup(app['solar'],app['desal'],"lcoh_calculator",app['timestamp'])
        finance_model_vars = create_variable_lists(
            model_name="lcoh_calculator", 
            json_vars=flkup2['finance_variables_file'],
            json_vals=flkup2['finance_values_file'])
    else:
        finance_model_vars = create_variable_lists(
            model_name=app['finance'], 
            json_vars=flkup['finance_variables_file'],
            json_vals=flkup['finance_values_file'])
        
    desal_finance_model_vars = create_variable_lists(
        model_name=app['desal'],
        json_vars=flkup['desal_finance_variables_file'],
        json_vals=flkup['desal_finance_values_file'])

    # get values derived from the GIS map that we want to update
    map_dict = helpers.json_load(cfg.map_json)
    weather_file = map_dict.get('file_name')
    tds_value = map_dict.get('FeedC_r')

    # find the weather file table and update
    if weather_file:
        wf_index = helpers.index_in_list_of_dicts(solar_model_vars,'Name','file_name')
        solar_model_vars[wf_index]['Value']=str(weather_file)

    # find the TDS Feed Concentration table and update
    if tds_value:
        tds_index = helpers.index_in_list_of_dicts(desal_model_vars,'Name','FeedC_r')
        desal_model_vars[tds_index]['Value']=tds_value

    # Update value from SAM generated JSON 
    print(f'{samjson}')
    if samjson:
        content_type, content_string = samjson.split(',')
        decoded = base64.b64decode(content_string)
        imported_json = json.loads(decoded.decode('utf-8'))
        for i in solar_model_vars:
            try:
                if i['DataType']=='SSC_ARRAY' or i['DataType']=='SSC_MATRIX':
                    i['Value']=str(imported_json[i['id']])
                else:
                    i['Value']=imported_json[i['id']]
            except:
                i['Value'] = None
        for i in finance_model_vars:
            try:
                if i['DataType']=='SSC_ARRAY' or i['DataType']=='SSC_MATRIX':
                    i['Value']=str(imported_json[i['id']])
                else:
                    i['Value']=imported_json[i['id']]
            except:
                i['Value'] = None


    # append the desal_finance variables to the finance variables
    finance_model_vars += desal_finance_model_vars

    # collect the tab names for the various models
    solar_tabs = collect_and_sort_model_tabs(solar_model_vars)
    desal_tabs = collect_and_sort_model_tabs(desal_model_vars)
    finance_tabs = collect_and_sort_model_tabs(finance_model_vars)

    # lookups for model variable and tabs
    Model_tabs = {models[0]:desal_tabs,
                  models[2]:finance_tabs,
                  models[1]:solar_tabs}
    Model_vars = {models[0]:desal_model_vars,
                  models[2]:finance_model_vars,
                  models[1]:solar_model_vars}

    def _make_tabs_in_collapse(i):
        return dbc.Card(
            [
                dbc.Button(
                    html.Div([html.Div("Title Here",id=f'collapse-title-{i}', style={'display':'inline-block', 'padding-top':'6px'}),
                    dbc.NavLink('', id=f'collapse-doc-link-{i}',
                        href='/assets/docs/documentation.pdf',
                        target='_blank',
                        external_link=True,
                        style={
                            'float':'right',
                            'display':'inline-block', 
                            'padding': '4px' 
                        },
                        className='fas fa-info-circle fa-2x text-info'
                        )
                    ]),
                    color="primary",
                    id=f"{i}-toggle".replace(' ','_'),
                    style={'padding': '0px', 'padding-right': '6px'}
                ),
                dbc.Collapse(
                    dbc.CardBody(
                        [dcc.Tabs(value=Model_tabs[i][0], children=[
                            dcc.Tab(label=j, value=j, style=tab_style, 
                                    selected_style=tab_selected_style,
                                    children=dbc.CardBody(      
                                        create_model_variable_page(
                                            tab=j,
                                            model_vars=Model_vars[i],
                                            model_type=i))
                                    )for j in Model_tabs[i]
                        ])]
                    ),
                    id=f"collapse-{i}",
                ),
            ],style={'padding':0} #TODO need to figure out how to properly override the padding
        )
    return [_make_tabs_in_collapse(m) for m in models] 

@app.callback(
    Output('desal-design-results', 'children'),
    [Input('run-desal-design', 'n_clicks')],
    [State({'type':'desal-table', 'index': ALL, 'model': ALL}, 'data')], 
    prevent_initial_call=True)
def run_desal_design(desalDesign, desalData):
    #create dict lookups for model and filenames
    app = helpers.json_load(cfg.app_json)
    flkup = cfg.build_file_lookup(app['solar'],app['desal'],app['finance'],app['timestamp'])

    desal_design_vars = dict()
    # pull out variable names and values and add to new dict
    for table in desalData:
        for row in table:
            desal_design_vars[row['Name']]=convert_strings_to_literal(row)

    #write the dict out into a JSON
    with flkup['desal_design_outfile'].open('w') as write_file:
        json.dump(desal_design_vars, write_file)

    #run the desal design simulation model
    stdm = SamBaseClass(desalination=app['desal'], 
                        desal_json_value_filepath=flkup['desal_design_outfile'])
    stdm.desal_design(desal=app['desal'])

    #read the the results and format to display
    with open(flkup['desal_design_infile'], "r") as read_file:
        desal_design_load = json.load(read_file)
    dd_outputs = []
    for dd in desal_design_load:
        dd_val = dd['Value']
        if isinstance(dd_val,int):
            dd_val = f'{dd_val:,}'
        elif isinstance(dd_val,float):
            dd_val = f'{dd_val:,.2f}'
        dd_outputs.append(html.Div(f"{dd['Name']}: {dd_val} {dd['Unit']}"))
        
    if desalDesign:
        return (html.H5("Model run complete", className='text-primary'),
                html.H4('Desalination Design Results',className="card-title"),
                dbc.Alert(dd_outputs))
    else:
        return

@app.callback([Output(f"collapse-title-{i}", 'children') for i in models],
            [Output(f'collapse-doc-link-{i}', 'href') for i in models],
            [Input('tabs-card','children')])
def title_collapse_buttons(x):
    '''
    Titles the collapse buttons based on values stored in JSON file
    For the models selected, figures out the page in our documentation
    to point the user to and returns the link to that page
    '''
    app_vals = helpers.json_load(cfg.app_json)
    # shorter references
    dref = app_vals['desal']
    sref = app_vals['solar']
    fref = app_vals['finance']
    # pull out model names
    d = f"{cfg.Desal[dref].rstrip()} Desalination System"
    s = cfg.Solar[sref].rstrip()
    f = cfg.Financial[fref].rstrip()
    # create documentation links
    ddoc = f"{cfg.Documentation[dref]['doc']}#page={cfg.Documentation[dref]['page']}"
    sdoc = f"{cfg.Documentation[sref]['doc']}#page={cfg.Documentation[sref]['page']}"
    fdoc = f"{cfg.Documentation[fref]['doc']}#page={cfg.Documentation[fref]['page']}"
    return d,s,f,ddoc,sdoc,fdoc

@app.callback(
    Output('model-card','children'),
    [Input(f"{i}-toggle", "n_clicks") for i in models],
)
def toggle_model_side_panel(m1,m2,m3):
    ctx = dash.callback_context

    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    else:
        button_id = 'default'

    if button_id == 'solar-toggle':
        return desal_side_panel
    elif button_id == 'finance-toggle':
        return desal_side_panel
    else: #default and 'Desalination_System-toggle'
        return desal_side_panel

@app.callback(
    [Output(f"collapse-{i}", "is_open") for i in models],
    [Input(f"{i}-toggle", "n_clicks") for i in models],
    [State(f"collapse-{i}", "is_open") for i in models])
def toggle_model_tabs(n1, n2, n3, is_open1, is_open2, is_open3):
    ctx = dash.callback_context

    if not ctx.triggered:
        return False, False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
   
    if button_id == f"{models[0]}-toggle".replace(' ','_') and n1:
        return not is_open1, False, False
    elif button_id == f"{models[1]}-toggle".replace(' ','_') and n2:
        return False, not is_open2, False
    elif button_id == f"{models[2]}-toggle".replace(' ','_') and n3:
        return False, False, not is_open3
    return False, False, False

@app.callback(
    Output('parametric-alert', 'is_open'),
    [Input('p-alert-init', 'children')])
def toggle_parametric_alert(_init):
    '''reads app json and opens alert if parametric set to true'''
    appj = helpers.json_load(cfg.app_json)
    return appj["parametric"]

@app.callback(
    Output('sam-json', 'children'),
    [Input('sam-json-button', 'children')])
def sam_json_button(_init):
    '''reads app json and opens alert if parametric set to true'''
    appj = helpers.json_load(cfg.app_json)
    if not appj["parametric"]:
        return SAM_JSON_file

@app.callback(
    Output('powertower-alert', 'is_open'),
    [Input('powertower-alert-init', 'children')])
def toggle_powertower_alert(_init):
    '''reads app json and opens alert if parametric set to true'''
    appj = helpers.json_load(cfg.app_json)
    return  appj["solar"] == 'tcsmolten_salt' 

@app.callback(
    Output('powertower2-alert', 'is_open'),
    [Input('powertower2-alert-init', 'children')])
def toggle_powertower2_alert(_init):
    '''reads app json and opens alert if parametric set to true'''
    appj = helpers.json_load(cfg.app_json)
    return appj["solar"] == 'tcsdirect_steam' 

@app.callback(
    [Output('model-loading-output','children'),
    Output('model-loading', 'children'),
    Output('sim-button', 'children')],
    [Input('model-button','n_clicks')],
    [State({'type':'solar-table', 'index': ALL, 'model': ALL}, 'data'), 
    State({'type':'desal-table', 'index': ALL, 'model': ALL}, 'data'),
    State({'type':'finance-table', 'index': ALL, 'model': ALL}, 'data'),
    State({'type':'solar-table', 'index': ALL, 'model': ALL}, 'selected_row_ids'),
    State({'type':'desal-table', 'index': ALL, 'model': ALL}, 'selected_row_ids'),
    State({'type':'finance-table', 'index': ALL, 'model': ALL}, 'selected_row_ids')],
    prevent_initial_call=True)
    # For pulling the selected parametric variables???
    #  Input('datatable-row-ids', 'selected_row_ids'),
def update_model_variables_and_run_model(n_clicks, solTableData, desTableData, finTableData,
                                         selectedSolarRows, selectedDesalRows, selectedFinRows  ): 
    '''
    Once someone is done editing the tables they hit the Run Model button
    This triggers the callback.
    We then check through the state of each table to see if it has been 
    edited. We can tell by whether or not it has a data_timestamp.
    If it has been edited we update the model variables dict which will be 
    converted to json and used as input to run the model.
    Finally the model is run.
    '''
    if n_clicks:
        #create dict lookups for model and filenames
        app = helpers.json_load(cfg.app_json)

        #create simple name:value dicts from model variables
        # to be used by SamBaseClass
        solar_output_vars = dict()
        desal_output_vars = dict()
        finance_output_vars = dict()
        parametric_info = dict()



        #NOTE need to transform the selectedXRows data to simple lists or sets
        # so that we can do a simple inclusion case  i.e. if x in y:
        # Collect selected variables from all tables into a single list
        selected_solar = []
        selected_desal = []
        selected_fin   = []
        for sR in selectedSolarRows:
            if sR:
                selected_solar.extend(sR)
        for dR in selectedDesalRows:
            if dR:
                selected_desal.extend(dR)
        for fR in selectedFinRows:
            if fR:
                selected_fin.extend(fR)
                
        # pull out variable names and values and add to new dict

        for solTable in solTableData:
            for sRow in solTable:
                if sRow['id'] in selected_solar:
                    parametric_info[sRow['id']] = [sRow['Min'], sRow['Max'], sRow['Interval'],'solar' , sRow['Label'], sRow['Units'] ]     
                solar_output_vars[sRow['Name']]=convert_strings_to_literal(sRow)

        for desTable in desTableData:
            for dRow in desTable:
                if dRow['id'] in selected_desal:
                    parametric_info[dRow['id']] = [dRow['Min'], dRow['Max'], dRow['Interval'],'desal', dRow['Label'], dRow['Units']] 
                desal_output_vars[dRow['Name']]=convert_strings_to_literal(dRow)
        for finTable in finTableData:
            for fRow in finTable:
                if fRow['id'] in selected_fin:
                    parametric_info[fRow['id']] = [fRow['Min'], fRow['Max'], fRow['Interval'],'finance', fRow['Label'], fRow['Units']] 
                finance_output_vars[fRow['Name']]=convert_strings_to_literal(fRow)


        #create the solar JSON file that will be the input to the model
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        solar_model_outfile = f"{app['solar']}{timestamp}_inputs.json"
        solar_model_outfile_path = Path(cfg.json_outpath / solar_model_outfile)
        with solar_model_outfile_path.open('w') as write_file:
            json.dump(solar_output_vars, write_file)
        #create the desal JSON file that will be the input to the model
        desal_model_outfile = f"{app['desal']}{timestamp}_inputs.json"
        desal_model_outfile_path = Path(cfg.json_outpath / desal_model_outfile)
        with desal_model_outfile_path.open('w') as write_file:
            json.dump(desal_output_vars, write_file)
        #create the finance JSON file that will be the input to the model
        if app['solar'] == 'SC_FPC' or app['solar'] == 'SC_ETC':
            finance_model_outfile = f"lcoh_calculator{timestamp}_inputs.json"
        else:
            finance_model_outfile = f"{app['finance']}{timestamp}_inputs.json"
            
        finance_model_outfile_path = Path(cfg.json_outpath / finance_model_outfile)
        with finance_model_outfile_path.open('w') as write_file:
            json.dump(finance_output_vars, write_file)

        # write the outfiles to the app_json for reference by other apps
        gui_out_files = {'solar_outfile': solar_model_outfile,
                        'desal_outfile': desal_model_outfile,
                        'finance_outfile': finance_model_outfile,
                        'timestamp': timestamp}
        helpers.json_update(gui_out_files, cfg.app_json) 
            
        # Update input json files according to the selected rows
        if len(parametric_info) > 0:
            
            # Create dict to collect interval values
            input_combinations = {"Variables":{}, "Timestamps": {}}
            
            # Loop to update the variables            
            key_index = 0
            timestamps = []
            parametric_simulation(parametric_info,
                                  key_index,
                                  timestamps,
                                  solar_output_vars, desal_output_vars, finance_output_vars,
                                  input_combinations,
                                  solar_model_outfile_path, desal_model_outfile_path, finance_model_outfile_path )   
            
            temp = []
            for key in input_combinations["Variables"].keys():
                temp.append(input_combinations["Variables"][key]["Values"])                     
            combs = list(itertools.product(*temp))
            
            for t in range(len(timestamps)):
                input_combinations["Timestamps"][timestamps[t]] = combs[t] 
                
                    
            # Export the parametric info
            comb_outfile = f"Parametric_Info.json"
            combination_outfile_path = Path(cfg.parametric_results_dir / comb_outfile)
            with combination_outfile_path.open('w') as write_file:
                json.dump(input_combinations, write_file)
                    
        #run the model once if no parametric variables selected
        else:
            run_model(csp=app['solar'],
                      desal=app['desal'],
                      finance=app['finance'],
                      json_file=solar_model_outfile_path,
                      desal_file=desal_model_outfile_path,
                      finance_file=finance_model_outfile_path,
                      timestamps = timestamp)
        # return a new button with a link to charts
        link = '/parametric-charts' if len(parametric_info)>0 else '/chart-results'
        return (   (html.Div([
                    html.H5("Model run complete", className='text-primary'),
                    dcc.Link(dbc.Button("View Results", color="primary"),
                    href=link) 
        ])),
        # send 'nothing' to dcc.Loading (since it will be removed)
        html.Div(''),
        # and replace the old button
        html.P()   )
    
def find_interval_values(Min, Max, Interval):

    try:
        Min = float(Min)
        Max = float(Max)
        Interval = float(Interval)
    except:
        print('Invalid input for Min, Max and Interval values')
        
    if Min>Max or Interval <= 0:
        raise Exception('Min, Max and Interval values must be greater than 0')
    values = [Min]        
    while values[-1] + Interval < Max:
        values.append(values[-1] + Interval)
    if values[-1] + Interval >= Max:
        values.append(Max)
        return values
        
        
def parametric_simulation(parametric_dict,
                          key_index, 
                          timestamps,
                          # Carry on the dataframe of each JSON file  
                          solar_output_vars, 
                          desal_output_vars, 
                          finance_output_vars,
                          # Carry on the dict recording the parametric info  
                          input_combinations,
                          # Carry on the model input JSON files path
                          solar_model_outfile_path,  
                          desal_model_outfile_path,  finance_model_outfile_path  
                          ):
    
    app = helpers.json_load(cfg.app_json)    
    
    if key_index < len(parametric_dict):
        variable_name = list(parametric_dict.keys())[key_index]
        interval_values = find_interval_values(parametric_dict[variable_name][0], parametric_dict[variable_name][1], parametric_dict[variable_name][2])                
        input_combinations["Variables"][variable_name] = {"Values": interval_values , "Label":  parametric_dict[variable_name][4], "Unit": parametric_dict[variable_name][5] }
        key_index += 1
        

        # Update variable values for each interval
        for v in interval_values:

            if parametric_dict[variable_name][3] == 'solar':
                solar_output_vars[variable_name] = v            
            elif parametric_dict[variable_name][3] == 'desal':
                desal_output_vars[variable_name] = v    
            elif parametric_dict[variable_name][3] == 'finance':
                finance_output_vars[variable_name] = v
                
            parametric_simulation(parametric_dict, key_index, timestamps, solar_output_vars, desal_output_vars, finance_output_vars,  input_combinations, solar_model_outfile_path,desal_model_outfile_path,finance_model_outfile_path )
    
            # Update JSON and run model when the last variable is assigned
            if key_index == len(parametric_dict):
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
                solar_model_outfile = f"{app['solar']}{timestamp}_inputs.json"
                solar_model_outfile_path = Path(cfg.json_outpath / solar_model_outfile)
                with solar_model_outfile_path.open('w') as write_file:
                    json.dump(solar_output_vars, write_file)                
                desal_model_outfile = f"{app['desal']}{timestamp}_inputs.json"
                desal_model_outfile_path = Path(cfg.json_outpath / desal_model_outfile)
                with desal_model_outfile_path.open('w') as write_file:
                    json.dump(desal_output_vars, write_file)
                if app['solar'] == 'SC_FPC' or app['solar'] == 'SC_ETC':
                    finance_model_outfile = f"lcoh_calculator{timestamp}_inputs.json"
                else:
                    finance_model_outfile = f"{app['finance']}{timestamp}_inputs.json"
                finance_model_outfile_path = Path(cfg.json_outpath / finance_model_outfile)
                with finance_model_outfile_path.open('w') as write_file:
                    json.dump(finance_output_vars, write_file)
                
                input_combinations["Timestamps"][timestamp] = []
                timestamps.append(timestamp)
                
                run_model(csp=app['solar'],
                          desal=app['desal'],
                          finance=app['finance'],
                          json_file=solar_model_outfile_path,
                          desal_file=desal_model_outfile_path,
                          finance_file=finance_model_outfile_path,
                          timestamps = timestamp)                        
         