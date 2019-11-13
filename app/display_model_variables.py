# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 13:55:35 2019

@author: jsquires
"""

import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table
from datetime import datetime
import json
from pathlib import Path
import re
import sys

base_path = Path().resolve().parent
sys.path.insert(0,str(base_path))
from SAM.SamBaseClass import SamBaseClass

# GLOBAL VARIABLES ###
model = 'tcslinear_fresnel'
#json_infiles_dir = r'D:\\Github\DOE_CSP_PROJECT\utils'
json_infiles_dir = base_path / 'utils'
#model_variables_file = json_infiles_dir+os.sep+'tcslinear_fresnel_for_ss.json'
model_variables_file = base_path / 'utils' / 'tcslinear_fresnel_for_ss.json'
#json_outfile = r'D:\\Github\DOE_CSP_PROJECT\SAM\models\inputs\{}'.format(model)
json_outfile = base_path / 'SAM' / 'models' / 'inputs' / model
#weather_file = r'D:\\Github\DOE_CSP_PROJECT\app\solar_resource\tucson_az_32.116521_-110.933042_psmv3_60_tmy.csv'
weather_file = base_path / 'app' / 'solar_resource' / 'tucson_az_32.116521_-110.933042_psmv3_60_tmy.csv'
levels = ['sections','subsections'] #'tabs' is also a level but they will always exist


# dict for desalination 'values' and 'labels'
Desal = {'FOR':'Forward Osmosis                   ',
         'MBD':'Membrane Distillation             ',
         'MED':'Multi-Effect Distillation (MED)   ', 
         'ABS':'MED with Absorption Heat Pumps    ',
         'TLV':'MED with Thermal Vapor Compression',
         'ROM':'Reverse Osmosis                   ', 
         }

#dict for financial model 'values' and 'labels' 
Financial = {'COMML':'Commercial (Distributed)                   ',
             'LCOEH':'LCOE/LCOH Calculator                       ',
             'PPFWD':'PPA Partnership Flip With Debt (Utility)   ',
             'PPFWO':'PPA Partnership Flip Without Debt (Utility)',
             'PPALS':'PPA Sale Leaseback (Utility)               ',
             'PPASO':'PPA Single Owner (Utility)                 ',
             }

# dict for solar 'values' and 'labels'
Solar = {'FPC' :'Flat-Plate Collector            ',
         'ISCC':'Integrated Solar Combined Cycle ',
         'LFDS':'Linear Fresnel Direct Steam     ',
         'LFMS':'Linear Fresnel Molten Salt      ',
         'PTDS':'Power Tower Direct Steam        ',
         'PTMS':'Power Tower Molten Salt         ',
         'PTP' :'Parabolic Trough Physical       ',
         'PHPT':'Process Heat Parabolic Trough   ',
         'PHDS':'Process Heat Linear Direct Steam',
         }

#dict containing the desalination options ('value' and 'disabled') after solar model chosen
solarToDesal = {
    'LFDS': [('FOR',True),('MBD',True),('MED',False),('ABS',False),('TLV',True),('ROM',True)],
    'PTP' : [('FOR',True),('MBD',True),('MED',False),('ABS',True),('TLV',False),('ROM',True)]
    }

#dict containing the finance options ('value' and 'disabled') after desal model chosen
desalToFinance = {
    'ABS': [('COMML',True),('LCOEH',True),('PPFWD',True),('PPFWO',True),('PPALS',True),('PPASO',True)],
    'MED': [('COMML',True),('LCOEH',True),('PPFWD',False),('PPFWO',True),('PPALS',True),('PPASO',True)],
    'TLV': [('COMML',True),('LCOEH',True),('PPFWD',True),('PPFWO',True),('PPALS',True),('PPASO',True)],
    }

#columns that will be used in data tables
cols = [{'name':'Variable', 'id':'label','editable':False},
        {'name':'Value',    'id':'value','editable':True, 'type':'numeric'},
        {'name':'Units',    'id':'units','editable':False}]


def create_callback_for_tables(tabs):
    '''
    takes in tabs of json and generates a table_id with the form:
    "Power_Cycle4Plant_Design4Plant_Cooling_Mode0"
    
    Power_Cycle, Plant_Design and Plant_Cooling Mode are the
    tab, section and subsection names with spaces replaced with underscores
    The numbers 4,4 and 0 are the tab, section and subsection array positions 
    in the example above.
     
    Then creates states for each table_id. These store changes to the tables.
    Finally, creates a callback that fires when the Run Model button is hit.
        
    '''        

    def _create_state(table_id):
        ''' 
        creates states for each table by appending
        data_timestamp, id and data to the states list
        '''
        states.append(State(table_id,'data_timestamp'))
        states.append(State(table_id,'id'))
        states.append(State(table_id,'data'))
        
        
      
    #First collect all the State declarations
    states = []
    #create states for the model's 'general' variables
    _create_state('General0')
    #create states for the tabs, get the tab names and their location within the 'tabs' array
    for i,tab in enumerate(unpack_keys_from_array_of_dicts(tabs)):
        #some tabs do not have general variables (i.e. not belonging to a section) so check if they do
        #length is 1 if it only contains sections, otherwise it has general variables and we assume more than 1:
        if(len(tabs[i][tab])) > 1:
            _create_state('{}{}'.format(tab.replace(' ','_'),i))
        #now find the next level
        #TODO hardcoding for now but this can be relative by iterating through 'levels' variables and
        #passing parts of the json like in _recursive_json
        if search_array_for_dict_with_key(tabs[i][tab], 'sections') is 0:
            #now get the sections names and positions
            for j,sec in enumerate(unpack_keys_from_array_of_dicts(tabs[i][tab][0]['sections'])):
                _create_state('{}{}{}{}'.format(tab.replace(' ','_'),i,sec.replace(' ','_'),j))
                #find the next level
                if search_array_for_dict_with_key(tabs[i][tab][0]['sections'][j][sec],'subsections') is 0:
                    #get the subsection names and positions
                    for k,sub in enumerate(unpack_keys_from_array_of_dicts(tabs[i][tab][0]['sections'][j][sec][0]['subsections'])):
                        _create_state('{}{}{}{}{}{}'.format(tab.replace(' ','_'),i,sec.replace(' ','_'),j,sub.replace(' ','_'),k))
    
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
        If it has been edited we update the model variables dict which will 
        converted to json and used as input to run the model.
        Finally the model is run.
        '''
        def _update_model_variables(names,tbl_data):
            '''overwrite the portion of the model variables dict that the data belongs to'''
            if len(names)>1:
                tab,tab_pos=names[0],int(names[1])
                
                if len(names)>3:
                    sec,sec_pos=names[2],int(names[3])
                    
                    if len(names)>5:
                        #this is the lowest level, subsection variables
                        subsec,subsec_pos=names[4],int(names[5])
                        model_vars[model][0]['tabs'][tab_pos][tab][0]['sections'][sec_pos][sec][0]['subsections'][subsec_pos][subsec]=tbl_data
                        return
                    
                    else: #NOT len(names)>5, these are section variables
                        #determines whether first position contain a variable or is part of the heierarchy
                        if search_array_for_dict_with_key(model_vars[model][0]['tabs'][tab_pos][tab][0]['sections'][sec_pos][sec][0],'name') is False:
                            model_vars[model][0]['tabs'][tab_pos][tab][0]['sections'][sec_pos][sec][1:]=tbl_data
                        else: #there are no more hierarchy steps so replace the entire array with model variables
                            model_vars[model][0]['tabs'][tab_pos][tab][0]['sections'][sec_pos][sec]=tbl_data
                        return
               
                else: #NOT len(names)>3   variables are at tab level unless they belong to'General'
                    if tab == 'General': #at the model level
                        #replace table data after the tabs at position 0
                        model_vars[model][1:]=tbl_data
                    else:
                        #determines whether the first position contains a variable or is part of the heierarchy
                        if search_array_for_dict_with_key(model_vars[model][0]['tabs'][tab_pos][tab][0],'name') is False:
                            model_vars[model][0]['tabs'][tab_pos][tab][1:]=tbl_data
                        else: #there are no more hierarchy steps so replace the entire array with model variables
                            model_vars[model][0]['tabs'][tab_pos][tab]=tbl_data
                    return    
                
            else: #NOT len(names)>1
                raise ValueError('The table names, {}, should have more values'.format(names))
            
        if n_clicks:
            #tableData states are in groups of threes
            #i is the table data_timestamp, i+1 is the id and i+2 is the data
            for i in range(0,len(tableData),3):
                updated = tableData[i]
                table = tableData[i+1]
                tbl_data = tableData[i+2]
                if updated:
                    #print('{};{};{}'.format(updated,table,tbl_data)) #debug
                    # break apart the table names to find the tab, sections, subsections
                    # along with their position in dict arrays
                    names = re.split('(\d+)',table)
                    # clean up the table names
                    try:
                        names.remove('')
                    except ValueError:
                        pass
                    try:
                        names = [x.replace('_',' ') for x in names]
                    except ValueError:
                        pass
                    
                    #using the table id, overwrite the dict with the updated portion
                    _update_model_variables(names,tbl_data)  
            #create the json file that will be the input to the model
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            model_outfile = Path(str(json_outfile)+timestamp+'_inputs.json')
            with model_outfile.open('w') as write_file:
                json.dump(model_vars, write_file)
                
            #run the model
            #TODO create config or dict with model names when there's more than one
#                if model == 'tcslinear_fresnel':
#                    csp_model = 'TcslinearFresnel_DSLF'
            run_model(csp=model_outfile,finance=None,weather=weather_file)
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
                {'if': {'column_id': 'label'},
                 'width': '40%'},
                {'if': {'column_id': 'value'},
                 'width': '55%'},
                {'if': {'column_id': 'units'},
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
    for the provided tab, reads JSON file
    and creates the corresponding model variable tables
    '''
    #get the 'general' variables for the tab
    if tab == 'General':
        #don't process any of the named levels ('tabs', etc.) at position 0
        model_variables=[]
        for v in dict_level[1:]:
            #use if you want to exclue matrices
#            if v['datatype']=='SSC_MATRIX':
#                #print('skipping matrix: {}'.format(v)) #debug
#                continue
            #create a list of dicts
            model_variables.append(v)
        return create_data_table(model_variables,'General0')
    else:
        #get the variables under the rest of the tab's hierarchy
        return iter_json(dict_level,levels,tab)
    
def iter_json(dl,levs,tab):
    tab_index = search_array_for_dict_with_key(dl[0]['tabs'],tab)
    tab_level=dl[0]['tabs'][tab_index][tab]    
    tableID = '{}{}'.format(tab.replace(' ','_'),tab_index)
    tab_page = []
    #print('**TAB**: {}'.format(tab)) #debug
    def _recursive_json(tl,l,tID):
        #first get variables belonging to the base level
        # named levels: 'tabs', etc will be at position 0, if they exist
        # searching array for name because variables have a name key
        if search_array_for_dict_with_key([tl[0]],'name') is False:
            #print('model vars not in lowest group...') #debug
            #variables that do not belong to the lowest hierarchy level
            model_variables = []
            for v in tl[1:]:
#                if v['datatype']=='SSC_MATRIX': #skipping matrixes for now...
#                    continue
                model_variables.append(v)
                #print('model variables: {}'.format(v)) #debug
            #tab_page.append(create_data_table(model_variables))
        else:
            #print('model vars in lowest group...') #debug
            #variables that belong to the lowest hierarchy level
            model_variables = []
            for v in tl:
#                if v['datatype']=='SSC_MATRIX':
#                    continue
                model_variables.append(v)
                #print('model variables: {}'.format(v)) #debug
            #tab_page.append(create_data_table(model_variables))
        # append the a variable table if any exist
        if model_variables:
            #if the tab page is empty add header for general tab-level variables
            if not tab_page:
                tab_page.append(html.H6('General {} variables'.format(tab)))
            #print('CREATING DATATABLE with tID: {}'.format(tID)) #debug
            tab_page.append(create_data_table(model_variables,tID))
        if l:
            lev = l[0]
            #print('level is {}'.format(lev)) #debug
            #update the dict_level with the next level if that level exists
            index = search_array_for_dict_with_key(tl,lev)
            # if it does not exist end the iteration else move into the next level
            if index is False:
                #print('{} does not exist here...'.format(lev)) #debug
                return
            else:
                #print('WORKING IN {}'.format(lev)) #debug
                tl=tl[index][lev]
            #get a list of titles from that level
            titles = unpack_keys_from_array_of_dicts(tl)
            #print('TITLES: {}'.format(titles)) #debug
            for t in titles:
                #print('TITLE: {}'.format(t)) #debug
                t_index = search_array_for_dict_with_key(tl,t)
                if lev=='sections':
                    tab_page.append(html.H6('{}'.format(t)))
                else:
                    tab_page.append('{}'.format(t))
                # call the function again... drilling down to the next level
                new_tID='{}{}{}'.format(tID,t.replace(' ','_'),t_index)
                _recursive_json(tl[t_index][t],l[1:],new_tID)
        else:  #levels is empty, end iteration
            return
    
    _recursive_json(tab_level,levs,tableID)
    #print('RETURNING tab page...')  #debug
    return tab_page 
 
def run_model(csp='TcslinearFresnel_DSLF',finance='LeveragedPartnershipFlip',weather=None):
    '''
    runs solar thermal desal model
    currently only setup for SAM models
    financial model is currently hardcoded
    '''
    #TODO run non-SAM models
    stdm = SamBaseClass(cspModel=csp,financialModel=finance,weatherFile=weather)
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
#MAIN PROGRAM (TODO create main() after testing...)
#
    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

with open(model_variables_file, "r") as read_file:
    model_vars = json.load(read_file)

# code to unpack the keys from the tabs and add to new list, these are the tab names
model_tabs=['General']
for i in model_vars[model][0]['tabs']:
    model_tabs.append(*i)

#this is where we start in the dict 
dict_level = model_vars[model]

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
                    {'label': 'Integrated Solar Combined Cycle ', 'value': 'ISCC', 'disabled': True},
                    {'label': 'Linear Fresnel Direct Steam     ', 'value': 'LFDS', 'disabled': False},
                    {'label': 'Linear Fresnel Molten Salt      ', 'value': 'LFMS', 'disabled': True},
                    {'label': 'Parabolic Trough Physical       ', 'value': 'PTP',  'disabled': False},
                    {'label': 'Power Tower Direct Steam        ', 'value': 'PTDS', 'disabled': True},
                    {'label': 'Power Tower Molten Salt         ', 'value': 'PTMS', 'disabled': True},
                    {'label': 'Process Heat Parabolic Trough   ', 'value': 'PHPT', 'disabled': True},
                    {'label': 'Process Heat Linear Direct Steam', 'value': 'PHDS', 'disabled': True}, 
                ],value='LFDS',
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
            
create_callback_for_tables(model_vars[model][0]['tabs'])

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
#            html.P('{} with {} and {}'.format(Solar[solar],Desal[desal],Financial[finance])),
#            html.P(),
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
    [Input('select-desal', 'value')])
def set_finance_options(desalModel):
    return [{'label': Financial[i[0]], 'value': i[0], 'disabled': i[1]} for i in desalToFinance[desalModel]]
    
if __name__ == '__main__':
    app.run_server(debug=True, port=8066)



