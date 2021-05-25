from pathlib import Path

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
         'VAGMD':'Vacuum Air Gap Membrane Distillation (VAGMD)    ',
         'MDB':'Vacuum Air Gap Membrane Distillation - Batch  (VAGMD-batch)   ',
         'LTMED':'Low Temperature Multi-Effect Distillation (LT-MED)', 
         'ABS':'MED with Absorption Heat Pumps (MED-ABS)        ',
         'MEDTVC':'MED with Thermal Vapor Compression (MED-TVC)',
         #'NUN':'No Desalination Model                    ',
         'RO':'Reverse Osmosis (RO)                      ', 
         # 'COMRO':'Cascading Osmotically Mediated Reverse Osmosis',
         'OARO': 'Osmotically Assisted Reverse Osmosis (OARO)',
         # 'LSRRO': 'Low-salt-rejection Reverse Osmosis',
         'RO_FO': 'Hybrid System (RO - FO)',
         'RO_MDB': 'Hybrid System (RO - VAGMD-batch)',
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
Solar = {'pvsamv1' :'Photovoltaic (Detailed)',
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
Documentation = {
    #Desal
    'FO':27, 'VAGMD':27, 'MDB':27, 'LTMED':27, 'ABS':27, 'MEDTVC':27,
    'NUN':27, 'RO':27, 'COMRO':27, 'OARO':27, 'LSRRO':27, 'RO_FO':27,
    'RO_MDB':27,
    #Financial
    'utilityrate5':30, 'lcoefcr':30, 'iph_to_lcoefcr':30, 'levpartflip':30,
    'equpartflip':30, 'saleleaseback':30, 'singleowner':30,
    #Solar
    'pvsamv1':19,'SC_FPC':19,'SC_ETC':19,'trough_physical_process_heat':19,'linear_fresnel_dsg_iph':19,'tcslinear_fresnel':19, 'tcsMSLF':19,
    'tcsdirect_steam':19, 'tcsmolten_salt':19, 'tcstrough_physical':19
}

#dict containing the desalination options ('value' and 'disabled') after solar model chosen
solarToDesal = {
    'pvsamv1' : [('FO',True),('VAGMD',True),('LTMED',True),('ABS',True),('MEDTVC',True),('MDB',True),('RO',False),('OARO',False),('RO_FO',False),('RO_MDB',False)],
    'SC_FPC' : [('FO',False),('VAGMD',False),('LTMED',False),('ABS',False),('MEDTVC',False),('MDB',False),('RO',True),('OARO',False),('RO_FO',False),('RO_MDB',False)],
    'SC_ETC' : [('FO',False),('VAGMD',False),('LTMED',False),('ABS',False),('MEDTVC',False),('MDB',False),('RO',True),('OARO',False),('RO_FO',False),('RO_MDB',False)],
    'trough_physical_process_heat': [('FO',False),('VAGMD',False),('LTMED',False),('ABS',False),('MEDTVC',False),('MDB',False),('RO',True),('OARO',False),('RO_FO',False),('RO_MDB',False)],
    'linear_fresnel_dsg_iph': [('FO',False),('VAGMD',False),('LTMED',False),('ABS',False),('MEDTVC',False),('MDB',False),('RO',True),('OARO',False),('RO_FO',False),('RO_MDB',False)],
    'tcslinear_fresnel': [('FO',False),('VAGMD',False),('LTMED',False),('ABS',False),('MEDTVC',False),('MDB',False),('RO',True),('OARO',False),('RO_FO',False),('RO_MDB',False)],
    'tcsMSLF': [('FO',False),('VAGMD',False),('LTMED',False),('ABS',False),('MEDTVC',False),('MDB',False),('RO',True),('OARO',False),('RO_FO',False),('RO_MDB',False)],
    'tcsdirect_steam': [('FO',False),('VAGMD',False),('LTMED',False),('ABS',False),('MEDTVC',False),('MDB',False),('RO',True),('OARO',False),('RO_FO',False),('RO_MDB',False)],
    'tcsmolten_salt': [('FO',False),('VAGMD',False),('LTMED',False),('ABS',False),('MEDTVC',False),('MDB',False),('RO',True),('OARO',False),('RO_FO',False),('RO_MDB',False)],
    'tcstrough_physical'  : [('FO',False),('VAGMD',False),('LTMED',False),('ABS',False),('MEDTVC',False),('MDB',False),('RO',True),('OARO',False),('RO_FO',False),('RO_MDB',False)],
    }

#dict containing the finance options ('value' and 'disabled') after desal model chosen
solarToFinance = {
    'pvsamv1': [('utilityrate5',True),('lcoefcr',False),('iph_to_lcoefcr',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
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
