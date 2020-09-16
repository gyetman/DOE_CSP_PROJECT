# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 12:55:58 2020

@author: zzrfl
"""
import json

from SAM_flatJSON.SamBaseClass import SamBaseClass


a = 'D:/PhD/DOE/DOE_CSP_PROJECT/SAM_flatJSON/parametric_inputs/Parametric_sample.json'

with open(a, "r") as read_file:
    df = json.load(read_file)

original = ['iph_to_lcoefcr2020-08-20_16-19-53_inputs.json',
            'SC_FPC2020-08-20_16-19-53_inputs.json',
            'VAGMD2020-08-20_16-19-53_inputs.json']


'''
Create input files
''' 


def parametric_inputs_json(original_json):

    for key in df.keys():
        
        file_dict = {}
        for variable in df[key]:
            
            for file in original:
                if variable['Model'] in file:    
                    file_name = 'D:/PhD/DOE/DOE_CSP_PROJECT/app/user-generated-inputs/' + file
            
            with open(file_name, "r") as read_file:
                model_input = json.load(read_file)
            
            
            file_dict[variable['Model']] = []
            for x in range(int((variable['Max']-variable['Min'])/variable['Step']) + 1):
                model_input[variable['Name']] = variable['Min'] + x * variable['Step']
                

                file_dict[variable['Model']].append(variable['Name'] + str(x))
                
                json_infile =  'D:/PhD/DOE/DOE_CSP_PROJECT/SAM_flatJSON/parametric_inputs/' + variable['Name'] + str(x) + '.json'
                with open(json_infile, 'w') as outfile:
                    json.dump(model_input, outfile)
        
        return file_dict
                    
'''
Create output files
'''

input_dict = parametric_inputs_json(original)
input_folder = 'D:/PhD/DOE/DOE_CSP_PROJECT/SAM_flatJSON/parametric_inputs/'
from shutil import copyfile

for i in range(len(input_dict['SC_FPC'])):
    for j in range(len(input_dict['VAGMD'])):
        stdm = SamBaseClass(CSP='SC_FPC',
                    desalination='VAGMD',
                    financial='iph_to_lcoefcr',
                    json_value_filepath=       input_folder   + input_dict['SC_FPC'][i] + '.json',
                    desal_json_value_filepath= input_folder   + input_dict['VAGMD'][j]  + '.json',
                    cost_json_value_filepath='D:/PhD/DOE/DOE_CSP_PROJECT/app/user-generated-inputs/'+ original[0])
        stdm.main()
        
        output_list = ['Solar_output', 'VAGMD_cost_output', 'VAGMD_design_output', 'VAGMD_simulation_output' ]
        for out_file in output_list:
            src = 'D:/PhD/DOE/DOE_CSP_PROJECT/SAM_flatJSON/results/'            + out_file +'.json'
            dst = 'D:/PhD/DOE/DOE_CSP_PROJECT/SAM_flatJSON/parametric_results/' + out_file +'_'+ input_dict['SC_FPC'][i] +'_'+ input_dict['VAGMD'][j] + '.json'
        
            copyfile(src, dst)




            