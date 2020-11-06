import app_config as cfg
import helpers

# list parameter names that have input or output dependencies
table_indexes = {
    'tcslinear_fresnel': 
        {'adjust:periods':'Power_CycleAvaialability_and_CurtailmentGeneral',
         'adjust:hourly':'Power_CycleAvaialability_and_CurtailmentGeneral'}
}

functions_per_model = {
    'tcslinear_fresnel': 
        [
            {
                'outputs':['adjust:periods'],
                'inputs':['adjust:hourly'],
                'function': 'adjuster'
            },
            # {
            #     'outputs':['adjust:hourly'],
            #     'inputs':['adjust:hourly'],
            #     'function': 'func2'
            # },
        ]
}

#NOTE: EXAMPLE CALLBACK FROM model_parameters
# @app.callback(
#     Output({'type':'solar-table', 'index': 'Power_CycleAvaialability_and_CurtailmentGeneral', 'model': 'tcslinear_fresnel'},'data'),
#     [Input({'type':'solar-table', 'index': 'Power_CycleAvaialability_and_CurtailmentGeneral', 'model': 'tcslinear_fresnel'}, 'data_timestamp'),Input({'type':'solar-table', 'index': 'Power_CycleOperationGeneral', 'model': 'tcslinear_fresnel'}, 'data_timestamp')],
#     [State({'type':'solar-table', 'index': 'Power_CycleAvaialability_and_CurtailmentGeneral', 'model': 'tcslinear_fresnel'}, 'data')],


def find_model_type(model):
    '''use the model name to determine what model type it is'''
    model_type={0:'solar',1:'desal',2:'finance'}
    list_of_dicts=[cfg.Solar, cfg.Desal, cfg.Financial]
    for index,d in enumerate(list_of_dicts):
        if model in d:
            return model_type[index]
    return None

# #NOTE: we'll want to eventually unpack the dict for the function call...
# #BELIEVE THIS, CODE WILL GO IN model_parameters.py
# for model, functions in functions_per_model.items():
#     model_type=find_model_type(model)
#     for function in functions:
#         @app.callback(
#             Output[{'type': f'{model_type}-table',
#                     'index': table_indexes[model[outp]],
#                     'model': model}] 
#                 for outp in function['outputs'],
#             Input[{'type': f'{model_type}-table',
#                     'index': table_indexes[model[inp]],
#                     'model': model}] 
#                 for inp in function['inputs'],
#             State[{'type': f'{model_type}-table',
#                     'index': table_indexes[model[inp]],
#                     'model': model}] 
#                 for inp in function['inputs'])
#             def get_table_outputs(inputs, states):
#                 print(f'inputs: {inputs}')
#                 print(f'outputs: {outputs}')
#                 return states[0]



# for model, functions in functions_per_model.items():
#     model_type=find_model_type(model)
#     for function in functions:
#         print(function)
#         print(f'{[table_indexes[model][output] for output in function["outputs"]]}')

#NOTE: EXAMPLE CODE FOR CALLBACK GENERATOR
# def generate_output_callback(datasource_1_value, datasource_2_value):
#     def output_callback(control_1_value, control_2_value):
#         # This function can display different outputs depending on
#         # the values of the dynamic controls
#         return '''
#             You have selected {} and {} which were
#             generated from {} (datasource 1) and and {} (datasource 2)
#         '''.format(
#             control_1_value,
#             control_2_value,
#             datasource_1_value,
#             datasource_2_value
#         )
#     return output_callback



# def get_table_outputs(outvar, *invars):
#     def x(invars):
#         pass
        
#     dependent_var_switcher = {
#         'var 1': x(invars)
#     }
# return dependent_var_switcher.get(outvar, "Variable not registered")


#NOTE: MOVING & REWRITING 
def register_tables(pdict):
    '''
    pull out the tab section and subsection that belongs to the 
    dependent variable, create the table ID and write the information
    to the dependencies json
    '''
    dvdict = dict()
    dp = pdict['id']
    dvdict[dp] = f"{pdict['Tab']}{pdict['Section']}{pdict['Subsection']}".replace(' ','_').replace('(','').replace(')','').replace('/','').replace('000General','General')
    # update json file
    try:
        helpers.json_update(data=dvdict, filename=cfg.dependencies_json)
    except FileNotFoundError:
        helpers.initialize_json(data=dvdict, filename=cfg.dependencies_json)


