from pathlib import Path

### GLOBAL VARIABLES and pre-processing ###
#
solar = 'linear_fresnel_dsg_iph'
desal = 'VAGMD'
finance = 'iph_to_lcoefcr'
base_path = Path(__file__).resolve().parent.parent.absolute()
app_json = base_path / 'app' / 'app-data.json'
map_json = base_path / 'app' / 'map-data.json'
report_json = base_path / 'app' / 'report-data.json'
json_infiles_dir = base_path / 'SAM_flatJSON' / 'models' / 'inputs'
json_defaults_dir = base_path / 'SAM_flatJSON' / 'defaults'
sam_results_dir = base_path / 'SAM_flatJSON' / 'results'

#TODO: build this later based on model selection within the GUI
solar_variables_file = json_infiles_dir/ f'{solar}_inputs.json'
solar_values_file = json_defaults_dir / f'{solar}_{finance}.json'
desal_variables_file = json_infiles_dir/ f'{desal}_inputs.json'
desal_values_file = json_defaults_dir / f'{desal}.json'
finance_variables_file = json_infiles_dir/ f'{finance}_inputs.json'
finance_values_file = json_defaults_dir / f'{solar}_{finance}.json'
desal_finance_variables_file = json_infiles_dir/ f'{desal}_cost_inputs.json'
desal_finance_values_file = json_defaults_dir/ f'{desal}_cost.json'
desal_design_infile = base_path / 'SAM_flatJSON' / 'results' / f'{desal}_design_output.json'
sam_desal_finance_outfile = sam_results_dir / f'{desal}_cost_output.json'
sam_desal_simulation_outfile = sam_results_dir / f'{desal}_simulation_output.json'
sam_solar_simulation_outfile = sam_results_dir / 'Solar_output.json'
##

json_outpath = base_path / 'app' / 'user-generated-inputs'

app_json_init = {'solar':'Solar','desal':'Desal','finance':'Finance'}

#columns that will be used in data tables
cols = [{'name':'Variable', 'id':'Label','editable':False},
       # {'name':'Value',    'id':'Value','editable':True, 'type':'numeric'},
        {'name':'Value',    'id':'Value','editable':True},
        {'name':'Units',    'id':'Units','editable':False}]

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

# dict desalination output file naming conventions (from SAMBaseClass.py)
desalFilenames = {'VAM':'VAGMD'}

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
Solar = {'FPC' :'Flat-Plate Collector',
         'IPHP':'Industrial Process Heat Parabolic Trough   ',
         'IPHD':'Industrial Process Heat Linear Direct Steam',
         'ISCC':'Integrated Solar Combined Cycle ',
         'DSLF':'Linear Fresnel Direct Steam     ',
         'MSLF':'Linear Fresnel Molten Salt      ',
         'DSPT':'Power Tower Direct Steam        ',
         'MSPT':'Power Tower Molten Salt         ',
         'PT'  :'Parabolic Trough Physical       ',
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
                 ('FPC','LCOH') :'StaticCollector_iph_iph_to_lcoefcr',
    }

#dict containing the desalination options ('value' and 'disabled') after solar model chosen
solarToDesal = {
    'FPC' : [('FOR',True),('VAM',False),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'IPHP': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'IPHD': [('FOR',True),('VAM',False),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'ISCC': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'DSLF': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'MSLF': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'DSPT': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'MSPT': [('FOR',True),('VAM',True),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    'PT'  : [('FOR',True),('VAM',False),('MED',False),('ABS',True),('TLV',True),('MBD',True),('NUN',True),('ROM',True)],
    }

#dict containing the finance options ('value' and 'disabled') after desal model chosen
solarToFinance = {
    'FPC': [('COMML',True),('LCOE',True),('LCOH',False),('NONE',True),('PPFWD',True),('PPFWO',True),('PPALS',True),('PPASO',True)],
    'IPHP': [('COMML',True),('LCOE',True),('LCOH',False),('NONE',False),('PPFWD',True),('PPFWO',True),('PPALS',True),('PPASO',True)],
    'IPHD': [('COMML',True),('LCOE',True),('LCOH',False),('NONE',False),('PPFWD',True),('PPFWO',True),('PPALS',True),('PPASO',True)],
    'ISCC': [('COMML',True),('LCOE',True),('LCOH',True),('NONE',True),('PPFWD',True),('PPFWO',True),('PPALS',True),('PPASO',False)],
    'DSLF': [('COMML',False),('LCOE',False),('LCOH',True),('NONE',False),('PPFWD',False),('PPFWO',False),('PPALS',False),('PPASO',False)],
    'MSLF': [('COMML',False),('LCOE',False),('LCOH',True),('NONE',False),('PPFWD',False),('PPFWO',False),('PPALS',False),('PPASO',False)],
    'DSPT': [('COMML',True),('LCOE',True),('LCOH',True),('NONE',True),('PPFWD',False),('PPFWO',False),('PPALS',False),('PPASO',False)],
    'MSPT': [('COMML',True),('LCOE',True),('LCOH',True),('NONE',True),('PPFWD',False),('PPFWO',False),('PPALS',False),('PPASO',False)],
    'PT'  : [('COMML',False),('LCOE',False),('LCOH',True),('NONE',False),('PPFWD',False),('PPFWO',False),('PPALS',False),('PPASO',False)],
    }
