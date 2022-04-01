import app_config as cfg
import helpers
import dependency_config as dpcfg
import ast

#NOTE: MOVING & REWRITING 
def get_table_id(varname, model_type, model):
    '''
    pull out the tab section and subsection that belongs to the 
    dependent variable, create the table ID and write the information
    to the dependencies json
    '''
    # if model_type == 'finance':
    #     model += '_cost'
    flkup = cfg.build_file_lookup(model,model,model,timestamp='')
    jfile = flkup[f'{model_type}_variables_file']

    with open(jfile, "r") as read_file:
        json_vars_load = helpers.json.load(read_file)
    # if model == 'FO_cost':
    #     model = model.split("_cost")[0]

    index=helpers.index_in_list_of_dicts(json_vars_load[model],'Name',varname)

    try:
        jvar=json_vars_load[model][index]
    except:
        print("Cannot find variable: ", varname)

    tab=jvar.get('Tab','General')
    sec=jvar.get('Section','General')
    subsec=jvar.get('Subsection','General')
    # ids = f"{tab}{sec}{subsec}".replace(' ','_').replace('(','').replace(')','').replace('/','')
    # if ids == 'Solar_Field_Solar_Field_ParametersGeneral':
    #     print(varname)
    # print ('dependency table ID:', f"{tab}{sec}{subsec}".replace(' ','_').replace('(','').replace(')','').replace('/',''))
    return f"{tab}{sec}{subsec}".replace(' ','_').replace('(','').replace(')','').replace('/','')

# list parameter names that have input or output dependencies
# table_indexes = {
#     'tcslinear_fresnel': 
#         {'adjust:periods':'Power_CycleAvaialability_and_CurtailmentGeneral',
#           'adjust:hourly':'Power_CycleAvaialability_and_CurtailmentGeneral'},
#     'linear_fresnel_dsg_iph':
#         {'nLoops': 'Solar_FieldSolar_Field_ParametersGeneral',
#           'q_pb_des':'System_DesignDesign_Point_ParametersHeat_Sink',
#           'I_bn_des':'System_DesignDesign_Point_ParametersSolar_Field'}
# }
functions_per_model = {
    'linear_fresnel_dsg_iph':
        [
            {
                'outputs': dpcfg.eqn1['outputs'],
                'output_ids': list(set([get_table_id(i, 'solar', 'linear_fresnel_dsg_iph') for i in dpcfg.eqn1['outputs']])),
                'inputs': dpcfg.eqn1['inputs'],
                'input_ids': list(set([get_table_id(i, 'solar', 'linear_fresnel_dsg_iph') for i in dpcfg.eqn1['inputs']])),
                'function': 'linear_fresnel_dsg_iph'
            }
        ],
    'tcslinear_fresnel': 
        [
            {
                'outputs': dpcfg.eqn01['outputs'],
                'output_ids': list(set([get_table_id(i, 'solar', 'tcslinear_fresnel') for i in dpcfg.eqn01['outputs']])),
                'inputs': dpcfg.eqn01['inputs'],
                'input_ids': list(set([get_table_id(i, 'solar', 'tcslinear_fresnel') for i in dpcfg.eqn01['inputs']])),
                'function': 'tcslinear_fresnel'
            }
        ],
    'trough_physical_process_heat': 
        [
            {
                'outputs': dpcfg.eqn02['outputs'],
                'output_ids': list(set([get_table_id(i, 'solar', 'trough_physical_process_heat') for i in dpcfg.eqn02['outputs']])),
                'inputs': dpcfg.eqn02['inputs'],
                'input_ids': list(set([get_table_id(i, 'solar', 'trough_physical_process_heat') for i in dpcfg.eqn02['inputs']])),
                'function': 'trough_physical_process_heat'
            }
        ],
    'tcstrough_physical': 
        [
            {
                'outputs': dpcfg.eqn03['outputs'],
                'output_ids': list(set([get_table_id(i, 'solar', 'tcstrough_physical') for i in dpcfg.eqn03['outputs']])),
                'inputs': dpcfg.eqn03['inputs'],
                'input_ids': list(set([get_table_id(i, 'solar', 'tcstrough_physical') for i in dpcfg.eqn03['inputs']])),
                'function': 'tcstrough_physical'
            },
        ],
    'pvsamv1': 
        [
            {
                'outputs': dpcfg.eqn05['outputs'],
                'output_ids': list(set([get_table_id(i, 'solar', 'pvsamv1') for i in dpcfg.eqn05['outputs']])),
                'inputs': dpcfg.eqn05['inputs'],
                'input_ids': list(set([get_table_id(i, 'solar', 'pvsamv1') for i in dpcfg.eqn05['inputs']])),
                'function': 'pvsamv1'
            },
        ],
    'tcsdirect_steam': 
        [
            {
                'outputs': dpcfg.eqn06['outputs'],
                'output_ids': list(set([get_table_id(i, 'solar', 'tcsdirect_steam') for i in dpcfg.eqn06['outputs']])),
                'inputs': dpcfg.eqn06['inputs'],
                'input_ids': list(set([get_table_id(i, 'solar', 'tcsdirect_steam') for i in dpcfg.eqn06['inputs']])),
                'function': 'tcsdirect_steam'
            },
        ],
    'tcsmolten_salt': 
        [
            {
                'outputs': dpcfg.eqn07['outputs'],
                'output_ids': list(set([get_table_id(i, 'solar', 'tcsmolten_salt') for i in dpcfg.eqn07['outputs']])),
                'inputs': dpcfg.eqn07['inputs'],
                'input_ids': list(set([get_table_id(i, 'solar', 'tcsmolten_salt') for i in dpcfg.eqn07['inputs']])),
                'function': 'tcsmolten_salt'
            },
        ],
    'tcsMSLF': 
        [
            {
                'outputs': dpcfg.eqn08['outputs'],
                'output_ids': list(set([get_table_id(i, 'solar', 'tcsMSLF') for i in dpcfg.eqn08['outputs']])),
                'inputs': dpcfg.eqn08['inputs'],
                'input_ids': list(set([get_table_id(i, 'solar', 'tcsMSLF') for i in dpcfg.eqn08['inputs']])),
                'function': 'tcsMSLF'
            },
        ],
}

#NOTE: EXAMPLE CALLBACK FROM model_parameters
# @app.callback(
#     Output({'type':'solar-table', 'index': 'Power_CycleAvaialability_and_CurtailmentGeneral', 'model': 'tcslinear_fresnel'},'data'),
#     [Input({'type':'solar-table', 'index': 'Power_CycleAvaialability_and_CurtailmentGeneral', 'model': 'tcslinear_fresnel'}, 'data_timestamp'),Input({'type':'solar-table', 'index': 'Power_CycleOperationGeneral', 'model': 'tcslinear_fresnel'}, 'data_timestamp')],
#     [State({'type':'solar-table', 'index': 'Power_CycleAvaialability_and_CurtailmentGeneral', 'model': 'tcslinear_fresnel'}, 'data')],

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

def find_model_type(model):
    '''use the model name to determine what model type it is'''
    model_type={0:'solar',1:'desal',2:'finance'}
    list_of_dicts=[cfg.Solar, cfg.Desal, cfg.Financial]
    for index,d in enumerate(list_of_dicts):
        if model in d:
            return model_type[index]
    return None


# def get_value(tables, name):
#     '''
#     looks for 'Name' key in list of dicts and returns 'Value' value
#     '''
#     ls, index=helpers.index_in_lists_of_dicts(tables,'Name',name)
#     return convert_strings_to_literal(ls[index])

# get values of a list of names
def get_values(tables, names):
    '''
    Update all values
    '''

    invalues = []
    for i in names:
        l, index=helpers.index_in_lists_of_dicts(tables,'Name',i)
        try:
            invalues.append(convert_strings_to_literal(tables[l][index]))
        except:
            print('error:', i, l, index)
    return invalues    

def update_val(tables,function, output_names,values):

    # Only the last few tables need to be updated
    # Doing this to avoid the situation where input and output share the same table
    indexes = -len(functions_per_model[function][0]['output_ids'])

    for i in range(len(output_names)):
        l, index=helpers.index_in_lists_of_dicts(tables[indexes:],'Name',output_names[i])    
        tables[indexes:][l][index]['Value']=values[i]    
        
    return tables[indexes:]

def function_switcher(func, intables):

    dependent_var_switcher = {
        'linear_fresnel_dsg_iph':      ['eqn1', 'linear_fresnel_dsg_iph'],
        'tcslinear_fresnel':           ['eqn01','tcslinear_fresnel'],
        'trough_physical_process_heat':['eqn02','trough_physical_process_heat'],
        'tcstrough_physical':          ['eqn03','tcstrough_physical'],
        'FO':                          ['eqn04','FO'],
        'pvsamv1':                     ['eqn05','pvsamv1'],
        'tcsdirect_steam':             ['eqn06','tcsdirect_steam'],
        'tcsmolten_salt':              ['eqn07','tcsmolten_salt'],
        'tcsMSLF':                     ['eqn08','tcsMSLF']
    }    
    
    # dependent_var_switcher = {
    #     'IPH_LFDS_nloops':             eqn1(intables),
    #     'tcslinear_fresnel_solarm':    eqn2(intables)
    # }        
    targets = dependent_var_switcher.get(func)
    inputs = getattr(dpcfg, targets[0])['inputs']
    outputs= getattr(dpcfg, targets[0])['outputs']

    invalues = get_values(intables, inputs )
    eqn = getattr(dpcfg, targets[1])
    result = eqn(invalues)
    
    output = update_val(intables, func, outputs, result)
    # update_val(intables, outputs[0], result)

    return output
    # return [intables[-1]]    
    
    # return dependent_var_switcher.get(func, KeyError("Function not found"))





