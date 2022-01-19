from pathlib import Path
import dash_bootstrap_components as dbc
import dash_html_components as html
### GLOBAL VARIABLES and pre-processing ###
#
base_path = Path(__file__).resolve().parent.parent.absolute()
app_json = base_path / 'app' / 'app-data.json'
map_json = base_path / 'app' / 'map-data.json'
report_json = base_path / 'app' / 'report-data.json'
json_infiles_dir = base_path / 'SAM_flatJSON' / 'models' / 'inputs'
json_defaults_dir = base_path / 'SAM_flatJSON' / 'defaults'
sam_results_dir = base_path / 'SAM_flatJSON' / 'results'
sam_solar_simulation_outfile = sam_results_dir / 'Solar_output.json'
json_outpath = base_path / 'app' / 'user-generated-inputs'
gis_data_path = base_path / 'app' / 'GISData'
gis_query_path = base_path / 'GISQueryData'
parametric_results_dir = base_path / 'SAM_flatJSON' / 'parametric_results'
parametric_info = parametric_results_dir / 'Parametric_Info.json'
#NOTE does not include timestamp + '.json'
parametric_solar_simulation_outfile = parametric_results_dir / 'Solar_output'
weather_path = base_path / 'SAM_flatJSON' / 'solar_resource'



def build_file_lookup(solar,desal,finance,timestamp):
    '''
    returns dict containing dynamic file names that are created 
    by interpolating solar, desal and finance model names
    '''
    return {
    #created by SAM and an infile to display on the GUI side panel
    'desal_design_infile': base_path / 'SAM_flatJSON' / 'results' / f'{desal}_design_output.json',
    'desal_design_timestamp_infile': base_path / 'SAM_flatJSON' / 'results' / f'{desal}_design_output{timestamp}.json',
    'desal_design_parametric_infile': parametric_results_dir / f'{desal}_design_output.json',
    #and outfile from the GUI that is then run with SamBaseClass
    'desal_design_outfile': json_outpath / f'{desal}_design_inputs.json',
    #desal-finance variables and corresponding default values
    'desal_finance_values_file': json_defaults_dir/ f'{desal}_cost.json',
    'desal_finance_variables_file': json_infiles_dir/ f'{desal}_cost_inputs.json',
    #desal variables and corresponding default values
    'desal_values_file': json_defaults_dir / f'{desal}.json',
    'desal_variables_file': json_infiles_dir/ f'{desal}_inputs.json',
    #finance model variables and corresponding default values
    'finance_values_file': json_defaults_dir / f'{solar}_{finance}.json',
    'finance_variables_file': json_infiles_dir/ f'{finance}_inputs.json',
    #parametric desal cost and simulation files
    #NOTE does not include timestamp + '.json'
    'parametric_desal_finance_outfile': parametric_results_dir / f'{desal}_cost_output',
    'parametric_desal_simulation_outfile': parametric_results_dir / f'{desal}_simulation_output',
    'parametric_desal_design_outfile': parametric_results_dir / f'{desal}_design_output',
    #desal-finance cost output file after SamBaseClass is run
    'sam_desal_finance_outfile': sam_results_dir / f'{desal}_cost_output{timestamp}.json',
    #desal design simulation output file after SamBaseClass.desal_design is run
    'sam_desal_simulation_outfile': sam_results_dir / f'{desal}_simulation_output{timestamp}.json',
    #solar model variables and corresponding default values
    'solar_values_file' : json_defaults_dir / f'{solar}_{finance}.json',
    'solar_variables_file': json_infiles_dir/ f'{solar}_inputs.json',
    'sam_solar_simulation_outfile': sam_results_dir / f'Solar_output{timestamp}.json'
    }


app_json_init = {'solar':'Solar','desal':'Desal','finance':'Finance'}

#columns that will be used in data tables
cols = [{'name':'Variable', 'id':'Label','editable':False},
        {'name':'Value',    'id':'Value','editable':True},
        {'name':'Units',    'id':'Units','editable':False}]

# NOTE: make sure any changes to these values are also reflected 
# in model_selection.py and the Documentation dict below

# dict for desalination 'values' and 'labels'
Desal = {'FO':'Forward Osmosis (FO)                       ',
         'VAGMD':'Vacuum Air Gap Membrane Distillation (VAGMD-one pass)    ',
         'MDB':'Vacuum Air Gap Membrane Distillation - Batch  (VAGMD-batch)   ',
         'LTMED':'Low Temperature Multi-Effect Distillation (LT-MED)', 
         'ABS':'MED with Absorption Heat Pumps (MED-ABS)        ',
         'MEDTVC':'MED with Thermal Vapor Compression (MED-TVC)',
         #'NUN':'No Desalination Model                    ',
         'RO':'Reverse Osmosis (RO) - Grid Integrated   ', 
         # 'COMRO':'Cascading Osmotically Mediated Reverse Osmosis',
         'OARO': 'Osmotically Assisted Reverse Osmosis (OARO) - Grid Integrated ',
         # 'LSRRO': 'Low-salt-rejection Reverse Osmosis',
         'RO_FO': 'Hybrid System (RO - FO)',
         'RO_MDB': 'Hybrid System (RO - VAGMD-batch)',
         'Generic': 'Generic Model'
         }

#dict for financial model 'values' and 'labels' 
Financial = {'utilityrate5':'Commercial (Distributed)                   ',
             'lcoefcr' :'Levelized Cost of Electricity Calculator   ',
             'iph_to_lcoefcr' :'Levelized Cost of Heat Calculator          ',
             'levpartflip':'PPA Partnership Flip With Debt (Utility)   ',
             'equpartflip':'PPA Partnership Flip Without Debt (Utility)',
             'saleleaseback':'PPA Sale Leaseback (Utility)               ',
             'singleowner':'PPA Single Owner (Utility)                 ',
             }

# dict for solar/CSP 'values' and 'labels'
Solar = {'pvwattsv7': 'Photovoltaic (PVWatts)',
         'pvsamv1' :'Photovoltaic (Detailed)',
         'SC_FPC' :'Static Collector (Flat Plate)',
         'SC_ETC' :'Static Collector (Evacuated Tube)',
         'trough_physical_process_heat':'Industrial Process Heat Parabolic Trough   ',
         'linear_fresnel_dsg_iph':'Industrial Process Heat Linear Direct Steam',
         'tcslinear_fresnel':'Linear Fresnel Direct Steam     ',
         'tcsMSLF':'Linear Fresnel Molten Salt      ',
         'tcsdirect_steam':'Power Tower Direct Steam',
         'tcsmolten_salt':'Power Tower Molten Salt         ',
         'tcstrough_physical'  :'Parabolic Trough Physical       '
          }

# dict for which documentation page to link to based on our model code
SAMD = "/assets/docs/sam-help-2020-2-29-r1.pdf"
SDAT = "/assets/docs/documentation.pdf"
ADD = "/assets/docs/Detailed description for Input Variables.pdf"

Documentation = {
    #Desal
    'FO':{'doc':SDAT,'page':56}, 'VAGMD':{'doc':SDAT,'page':49}, 'MDB':{'doc':SDAT,'page':53}, 'LTMED':{'doc':SDAT,'page':38}, 'ABS':{'doc':SDAT,'page':44}, 'MEDTVC':{'doc':SDAT,'page':41}, 'NUN':{'doc':SDAT,'page':27}, 'RO':{'doc':SDAT,'page':61}, 'COMRO':{'doc':SDAT,'page':27}, 'OARO':{'doc':SDAT,'page':62}, 'LSRRO':{'doc':SDAT,'page':27}, 'RO_FO':{'doc':SDAT,'page':63}, 'RO_MDB':{'doc':SDAT,'page':65}, 'Generic':{'doc':SDAT,'page':65},
    #Financial
    'utilityrate5':{'doc':SAMD,'page':771}, 'lcoefcr':{'doc':SAMD,'page':829}, 'iph_to_lcoefcr':{'doc':SAMD,'page':829}, 'levpartflip':{'doc':SAMD,'page':803}, 'equpartflip':{'doc':SAMD,'page':813}, 'saleleaseback':{'doc':SAMD,'page':821}, 'singleowner':{'doc':SAMD,'page':787},
    #Solar
    'pvsamv1':{'doc':SAMD,'page':171},'SC_FPC':{'doc':SAMD,'page':19},'SC_ETC':{'doc':SAMD,'page':19},'trough_physical_process_heat':{'doc':SAMD,'page':706},'linear_fresnel_dsg_iph':{'doc':SAMD,'page':741},'tcslinear_fresnel':{'doc':SAMD,'page':605}, 'tcsMSLF':{'doc':SAMD,'page':627},
    'tcsdirect_steam':{'doc':SAMD,'page':563}, 'tcsmolten_salt':{'doc':SAMD,'page':526}, 'tcstrough_physical':{'doc':SAMD,'page':437}, 'pvwattsv7':{'doc':SAMD,'page':228}
}

# function to look up additional documentation for each tab
info = ['Weather file format requirement', 'Detailed description for inputs', 'Variables on this page are not required for input, please ignore them']
doc_info = {('pvsamv1',                'Location and Resource'):  {'text': info[0], 'href': f"{SAMD}#page=120"},
            # ('pvsamv1',                'General'):                {'text': info[2], 'href': f"{ADD}#page=1"},
            ('tcslinear_fresnel',      'Location and Resource'):  {'text': info[0], 'href': f"{SAMD}#page=120"},
            ('linear_fresnel_dsg_iph', 'Location and Resource'):  {'text': info[0], 'href': f"{SAMD}#page=120"},
            ('linear_fresnel_dsg_iph', 'Collector and Receiver'): {'text': info[1], 'href': f"{ADD}#page=4"},
            ('tcsMSLF',                'Auxiliary (Not used)'):                {'text': info[2], 'href': f"{ADD}#page=1"},
            ('tcsMSLF',                'Location and Resource'):  {'text': info[0], 'href': f"{SAMD}#page=120"},
            ('tcsMSLF',                'Solar Field'):            {'text': info[1], 'href': f"{ADD}#page=9"},
            ('SC_FPC',                 'Weather'):                {'text': info[0], 'href': f"{ADD}#page=2"},
            ('SC_ETC',                 'Weather'):                {'text': info[0], 'href': f"{ADD}#page=2"},
            ('pvsamv1',                'System Design'):          {'text': info[1], 'href': f"{ADD}#page=5"},
            ('tcstrough_physical',     'Collectors (SCAs)'):      {'text': info[1], 'href': f"{ADD}#page=6"},
            ('tcstrough_physical',     'Receivers (HCEs)'):       {'text': info[1], 'href': f"{ADD}#page=7"},
            ('tcstrough_physical',     'Location and Resource'):  {'text': info[0], 'href': f"{SAMD}#page=120"},
            ('tcstrough_physical',     'Solar Field'):            {'text': info[1], 'href': f"{ADD}#page=8"},
            # ('tcstrough_physical',     'General'):                {'text': info[2], 'href': f"{ADD}#page=1"},
            # ('tcsdirect_steam',        'General'):                {'text': info[2], 'href': f"{ADD}#page=1"},
            ('tcsdirect_steam',        'Location and Resource'):  {'text': info[0], 'href': f"{SAMD}#page=120"},
            # ('tcsmolten_salt',         'General'):                {'text': info[2], 'href': f"{ADD}#page=1"},
            ('tcsmolten_salt',         'Location and Resource'):  {'text': info[0], 'href': f"{SAMD}#page=120"},
            # ('trough_physical_process_heat','General'):           {'text': info[2], 'href': f"{ADD}#page=1"},
            ('trough_physical_process_heat','Location and Resource'):{'text': info[2], 'href': f"{ADD}#page=120"},
            ('trough_physical_process_heat','Collectors (SCAs)'):      {'text': info[1], 'href': f"{ADD}#page=10"},
            ('trough_physical_process_heat','Receivers (HCEs)'):       {'text': info[1], 'href': f"{ADD}#page=11"},
            ('trough_physical_process_heat','Solar Field'):            {'text': info[1], 'href': f"{ADD}#page=12"},
            }

def other_documentation(model, tab):
    if (model, tab) in doc_info:
        info = doc_info[(model, tab)]
        
        documentation = dbc.Button(
                        html.Div([
                        dbc.NavLink(info['text'], id= model + '_' +  tab,
                            href= info['href'],
                            target='_blank',
                            external_link=True,
                            style={
                                'float':'right',
                                'display':'inline-block', 
                                'padding': '4px',
                                'font-size': '17px'
                            },
                            className='fas fa-info-circle fa-2x text-info'
                            )
                        ]),
                        color="Success",
                        outline=True, 
                        size = 'sm',
                        style={'padding': '4px', 'padding-right': '6px', 'textAlign': 'center'}
                    )  
                
        return documentation
    

#dict containing the desalination options ('value' and 'disabled') after solar model chosen
solarToDesal = {
    'pvwattsv7' : [('FO',True),('VAGMD',True),('MDB',True),('LTMED',True),('ABS',True),('MEDTVC',True),('RO',False),('OARO',False),('RO_FO',True),('RO_MDB',True),('Generic',True)],
    'pvsamv1' : [('FO',True),('VAGMD',True),('MDB',True),('LTMED',True),('ABS',True),('MEDTVC',True),('RO',False),('OARO',False),('RO_FO',True),('RO_MDB',True),('Generic',True)],
    'SC_FPC' : [('FO',False),('VAGMD',False),('MDB',False),('LTMED',False),('ABS',False),('MEDTVC',False),('RO',True),('OARO',True),('RO_FO',False),('RO_MDB',False),('Generic',False)],
    'SC_ETC' : [('FO',False),('VAGMD',False),('MDB',False),('LTMED',False),('ABS',False),('MEDTVC',False),('RO',True),('OARO',True),('RO_FO',False),('RO_MDB',False),('Generic',False)],
    'trough_physical_process_heat': [('FO',False),('VAGMD',False),('MDB',False),('LTMED',False),('ABS',False),('MEDTVC',False),('RO',True),('OARO',True),('RO_FO',True),('RO_MDB',True),('Generic',False)],
    'linear_fresnel_dsg_iph': [('FO',False),('VAGMD',False),('MDB',False),('LTMED',False),('ABS',False),('MEDTVC',False),('RO',True),('OARO',True),('RO_FO',True),('RO_MDB',True),('Generic',False)],
    'tcslinear_fresnel': [('FO',False),('VAGMD',False),('MDB',False),('LTMED',False),('ABS',False),('MEDTVC',False),('RO',False),('OARO',False),('RO_FO',False),('RO_MDB',False),('Generic',False)],
    'tcsMSLF': [('FO',False),('VAGMD',False),('MDB',False),('LTMED',False),('ABS',False),('MEDTVC',False),('RO',False),('OARO',False),('RO_FO',False),('RO_MDB',False),('Generic',False)],
    'tcsdirect_steam': [('FO',False),('VAGMD',False),('MDB',False),('LTMED',False),('ABS',False),('MEDTVC',False),('RO',False),('OARO',False),('RO_FO',False),('RO_MDB',False),('Generic',False)],
    'tcsmolten_salt': [('FO',False),('VAGMD',False),('MDB',False),('LTMED',False),('ABS',False),('MEDTVC',False),('RO',False),('OARO',False),('RO_FO',False),('RO_MDB',False),('Generic',False)],
    'tcstrough_physical'  : [('FO',False),('VAGMD',False),('MDB',False),('LTMED',False),('ABS',False),('MEDTVC',False),('RO',False),('OARO',False),('RO_FO',False),('RO_MDB',False),('Generic',False)],
    }

#dict containing the finance options ('value' and 'disabled') after desal model chosen
solarToFinance = {
    'pvsamv1': [('utilityrate5',True),('lcoefcr',False),('iph_to_lcoefcr',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'pvwattsv7': [('utilityrate5',True),('lcoefcr',False),('iph_to_lcoefcr',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'SC_FPC': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',False),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'SC_ETC': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',False),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'trough_physical_process_heat': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',False),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'linear_fresnel_dsg_iph': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',False),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'tcsiscc': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',False)],
    'tcslinear_fresnel': [('utilityrate5',False),('lcoefcr',False),('iph_to_lcoefcr',True),('levpartflip',False),('equpartflip',False),('saleleaseback',False),('singleowner',False)],
    'tcsMSLF': [('utilityrate5',False),('lcoefcr',False),('iph_to_lcoefcr',True),('levpartflip',False),('equpartflip',False),('saleleaseback',False),('singleowner',False)],
    'tcsdirect_steam': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',True),('levpartflip',False),('equpartflip',False),('saleleaseback',False),('singleowner',False)],
    'tcsmolten_salt': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',True),('levpartflip',False),('equpartflip',False),('saleleaseback',False),('singleowner',False)],
    'tcstrough_physical'  : [('utilityrate5',False),('lcoefcr',False),('iph_to_lcoefcr',True),('levpartflip',False),('equpartflip',False),('saleleaseback',False),('singleowner',False)],
    }

