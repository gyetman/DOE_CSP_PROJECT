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

def build_file_lookup(solar,desal,finance):
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
    #desal-finance cost output file after SamBaseClass is run
    'sam_desal_finance_outfile': sam_results_dir / f'{desal}_cost_output.json',
    #desal design simulation output file after SamBaseClass.desal_design is run
    'sam_desal_simulation_outfile': sam_results_dir / f'{desal}_simulation_output.json',
    #solar model variables and corresponding default values
    'solar_values_file' : json_defaults_dir / f'{solar}_{finance}.json',
    'solar_variables_file': json_infiles_dir/ f'{solar}_inputs.json',
    }


app_json_init = {'solar':'Solar','desal':'Desal','finance':'Finance'}

#columns that will be used in data tables
cols = [{'name':'Variable', 'id':'Label','editable':False},
       # {'name':'Value',    'id':'Value','editable':True, 'type':'numeric'},
        {'name':'Value',    'id':'Value','editable':True},
        {'name':'Units',    'id':'Units','editable':False}]

# dict for desalination 'values' and 'labels'
Desal = {'FO':'Forward Osmosis                          ',
         'VAGMD':'Vacuum Air Gap Membrane Distillation     ',
         'LTMED':'Low Temperature Multi-Effect Distillation', 
         'ABS':'MED with Absorption Heat Pumps           ',
         'TLV':'MED with Thermal Vapor Compression       ',
         'MBD':'Membrane Distillation                    ',
         'NUN':'No Desalination Model                    ',
         'RO':'Reverse Osmosis                          ', 
         }

#dict for financial model 'values' and 'labels' 
Financial = {'utilityrate5':'Commercial (Distributed)                   ',
             'lcoefcr' :'Levelized Cost of Electricity Calculator   ',
             'iph_to_lcoefcr' :'Levelized Cost of Heat Calculator          ',
             'none' :'No Financial Model                         ',
             'levpartflip':'PPA Partnership Flip With Debt (Utility)   ',
             'equpartflip':'PPA Partnership Flip Without Debt (Utility)',
             'saleleaseback':'PPA Sale Leaseback (Utility)               ',
             'singleowner':'PPA Single Owner (Utility)                 ',
             }

# NOTE: make sure any changes in this table are also reflected in app.layout
# dict for solar/CSP 'values' and 'labels'
Solar = {'pvsamv1' :'Photovoltaic (Detailed)',
         'SC_FPC' :'Static Collector (Flat Plate)',
         'SC_ETC' :'Static Collector (Evacuated Tube)',
         'trough_physical_process_heat':'Industrial Process Heat Parabolic Trough   ',
         'linear_fresnel_dsg_iph':'Industrial Process Heat Linear Direct Steam',
         'tcsiscc':'Integrated Solar Combined Cycle ',
         'tcslinear_fresnel':'Linear Fresnel Direct Steam     ',
         'tcsMSLF':'Linear Fresnel Molten Salt      ',
         'tcsdirect_steam':'Power Tower Direct Steam',
         'tcsmolten_salt':'Power Tower Molten Salt         ',
         'tcstrough_physical'  :'Parabolic Trough Physical       ',
         'none': 'No Solar Thermal System'
          }

#dict containing the desalination options ('value' and 'disabled') after solar model chosen
solarToDesal = {
    'pvsamv1' : [('FO',True),('VAGMD',True),('LTMED',True),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',False)],
    'SC_FPC' : [('FO',False),('VAGMD',False),('LTMED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',True)],
    'SC_ETC' : [('FO',True),('VAGMD',False),('LTMED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',True)],
    'trough_physical_process_heat': [('FO',False),('VAGMD',False),('LTMED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',True)],
    'linear_fresnel_dsg_iph': [('FO',False),('VAGMD',False),('LTMED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',True)],
    'tcsiscc': [('FO',True),('VAGMD',True),('LTMED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',True)],
    'tcslinear_fresnel': [('FO',False),('VAGMD',False),('LTMED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',True)],
    'tcsMSLF': [('FO',True),('VAGMD',True),('LTMED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',True)],
    'tcsdirect_steam': [('FO',False),('VAGMD',False),('LTMED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',True)],
    'tcsmolten_salt': [('FO',True),('VAGMD',True),('LTMED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',True)],
    'tcstrough_physical'  : [('FO',False),('VAGMD',False),('LTMED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',True)],
    'none'  : [('FO',True),('VAGMD',True),('LTMED',True),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('RO',False)],
    }

#dict containing the finance options ('value' and 'disabled') after desal model chosen
solarToFinance = {
    'pvsamv1': [('utilityrate5',True),('lcoefcr',False),('iph_to_lcoefcr',True),('none',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'SC_FPC': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',False),('none',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'SC_ETC': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',False),('none',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'trough_physical_process_heat': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',False),('none',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'linear_fresnel_dsg_iph': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',False),('none',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    'tcsiscc': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',True),('none',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',False)],
    'tcslinear_fresnel': [('utilityrate5',False),('lcoefcr',False),('iph_to_lcoefcr',True),('none',True),('levpartflip',False),('equpartflip',False),('saleleaseback',False),('singleowner',False)],
    'tcsMSLF': [('utilityrate5',False),('lcoefcr',False),('iph_to_lcoefcr',True),('none',True),('levpartflip',False),('equpartflip',False),('saleleaseback',False),('singleowner',False)],
    'tcsdirect_steam': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',True),('none',True),('levpartflip',False),('equpartflip',False),('saleleaseback',False),('singleowner',False)],
    'tcsmolten_salt': [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',True),('none',True),('levpartflip',False),('equpartflip',False),('saleleaseback',False),('singleowner',False)],
    'tcstrough_physical'  : [('utilityrate5',False),('lcoefcr',False),('iph_to_lcoefcr',True),('none',True),('levpartflip',False),('equpartflip',False),('saleleaseback',False),('singleowner',False)],
    'none'  : [('utilityrate5',True),('lcoefcr',True),('iph_to_lcoefcr',True),('none',True),('levpartflip',True),('equpartflip',True),('saleleaseback',True),('singleowner',True)],
    }
