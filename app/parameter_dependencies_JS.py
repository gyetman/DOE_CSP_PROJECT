import app_config as cfg
import helpers

# list parameter names that have input or output dependencies
#NOTE: EACH TABLE CAN ONLY HAVE ONE CALLBACK OUTPUT!
#NOTE: so create no more than one function per table in a model
table_indexes = {
    'tcslinear_fresnel': 
        {'adjust:periods':'Power_CycleAvaialability_and_CurtailmentGeneral',
         'adjust:hourly':'Power_CycleAvaialability_and_CurtailmentGeneral'},
    'linear_fresnel_dsg_iph':
        {'nLoops': 'Solar_FieldSolar_Field_ParametersGeneral',
         'q_pb_des':'System_DesignDesign_Point_ParametersHeat_Sink',
         'I_bn_des':'System_DesignDesign_Point_ParametersSolar_Field'}
}

functions_per_model = {
    'tcslinear_fresnel': 
        [
            {
                'outputs':['adjust:periods'],
                'inputs':['adjust:hourly'],
                'function': 'adjuster'
            },
        ],
    'linear_fresnel_dsg_iph':
        [
            {
                'outputs': ['I_bn_des'],
                'inputs': ['q_pb_des'],
                'function': 'IPH_LFDS_I_bn_des'
            },
            {
                'outputs': ['nLoops'],
                'inputs': ['q_pb_des','I_bn_des'],
                'function': 'IPH_LFDS_nloops'
            },

        ]
}

#
# SWITCHER FUNCTIONS
#
def adjuster(intables):
    '''this is a sample function!'''
    adjcon=get_value(intables,'adjust:constant')
    adjper = str(float(adjcon)+.001)
    update_val([intables[-1]],'adjust:periods',adjper)
    return [intables[-1]]

def IPH_LFDS_nloops(intables):
    q_pb_des=get_value(intables,'q_pb_des')
    I_bn_des=get_value(intables,'I_bn_des')
    nloops = int(float(q_pb_des)+float(I_bn_des)) 
    update_val([intables[-1]],'nLoops',nloops)
    return [intables[-1]]

def IPH_LFDS_I_bn_des(intables):
    q_pb_des=get_value(intables,'q_pb_des')
    I_bn_des = float(q_pb_des) *10
    update_val([intables[-1]],'I_bn_des',I_bn_des)
    return [intables[-1]]
    
def function_switcher(func, intables):

    dependent_var_switcher = {
        'adjuster': adjuster,
        'IPH_LFDS_nloops': IPH_LFDS_nloops,
        'IPH_LFDS_I_bn_des': IPH_LFDS_I_bn_des
    }
    return dependent_var_switcher.get(func, KeyError("Function not found"))(intables)

#
#HELPER FUNCTIONS
#
def find_model_type(model):
    '''use the model name to determine what model type it is'''
    model_type={0:'solar',1:'desal',2:'finance'}
    list_of_dicts=[cfg.Solar, cfg.Desal, cfg.Financial]
    for index,d in enumerate(list_of_dicts):
        if model in d:
            return model_type[index]
    return None

def get_function(context):
    '''use callback context to determine the appropriate function name'''
    #get the model name and table id from input context
    model_name = context[0]['id']['model']
    tblid=context[0]['id']['index']
    #use configurations to determine the proper function
    for f in functions_per_model[model_name]:
        for var in f['outputs']:
            if table_indexes[model_name][var]==tblid:
                return f['function']
    return None


def get_table_id(varname, model_type, model):
    '''
    pull out the tab section and subsection that belongs to the 
    dependent variable, create the table ID and write the information
    to the dependencies json
    '''
    flkup = cfg.build_file_lookup(model,model,model)
    jfile = flkup[f'{model_type}_variables_file']
    with open(jfile, "r") as read_file:
        json_vars_load = helpers.json.load(read_file)
    index=helpers.index_in_list_of_dicts(json_vars_load[model],'Name',varname)
    jvar=json_vars_load[model][index]
    tab=jvar.get('Tab','General')
    sec=jvar.get('Section','General')
    subsec=jvar.get('Subsection','General')
    return f"{tab}{sec}{subsec}".replace(' ','_').replace('(','').replace(')','').replace('/','')
    
def get_value(tables, name):
    '''
    looks for 'Name' key in tables(list of lists of dicts) and returns 'Value' value
    '''
    ls,index=helpers.index_in_lists_of_dicts(tables,'Name',name)
    return ls[index]['Value']

def update_val(tables,name,value):
    '''
    @tables: list of lists of dicts
        NOTE: should only contain output dicts 
    @name: string
        key value to search containing value
    @value: ???
        value to search that matches the key,
        this value will be updated 
    '''
    ls,index=helpers.index_in_lists_of_dicts(tables,'Name',name)
    ls[index]['Value']=value



