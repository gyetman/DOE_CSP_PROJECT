# -*- coding: utf-8 -*-
"""
Created on Wed May  8 12:30:18 2019

@author: vikas

Processes JSON input file into new JSON file with the following format:
{SAM model name}
   [{tabs and model variables}] 
      {tab1}
         [{sections and tab variables}] 
            {section 1}
               [{sub sections and section variables}] 
                  {sub section 1}
                      [{sub section variables}]

       
Example from infile: 
    {"DataType": "SSC_MATRIX", "Name": "HL_W", "Label": "(boiler, SH) Heat loss coef adj wind velocity (0,1,2,3,4 order terms)", "Units": "1/(m/s)^order", "Require": "*", "Tab": "Collector and Receiver ", "Section": " Receiver Geometry and Heat loss ", "Subsection": " Polynomial fit heat loss model", "Value": "[ [ 1, 0, 0, 0, 0 ], [ 1, 0, 0, 0, 0 ] ]"}
"""

#import collections
import json
import os

### variables hard-coded here but should be passed to the class
json_infile = 'samLinearFresnelDirectSteam.json'
model = "tcslinear_fresnel" ###

json_outfile = '{}.json'.format(model)

# these could be passed in too, if we think the hierarchy or variable attributes could change,
# otherwise just hard-coded here
hierarchy_map = {'Tab':'tabs','Section':'sections','Subsection':'subsections'}
recursion_path = ['Tab','Section','Subsection']
var_attributes = {"Name":'name',"DataType":'datatype','Label':'label','Value':'value',
                  'Units':'units','Require':'require','Constraints':'constraints'}
###

def add_to_dict(raw_variable, dict_out, hierarchy=None):
    # pull out levels that pertain to the variable
    if hierarchy is None:
        hierarchy=[key for key in recursion_path if key in raw_variable]
    return _add_to_dict_recursion(raw_variable, hierarchy, dict_out[model])
  
def _add_to_dict_recursion(rv, h, ja): #d = dict_out, h = header, ja = jason_append
    '''ja will be the json piece that travels through the recursion and builds down to lower levels
    when adding new level insert into 0 position if list exists: a.insert(0, x)'''
    
    print('Hierachy currently: {}'.format(h))
    # if headers are empty, end the recursion, create variable dict and append to 
    # current level
    if len(h)==0:
        variable_json={}
        print('Hierarchy is empty, creating variable')
        for key in var_attributes:
            if key in rv: 
                variable_json[var_attributes[key]]=rv[key]
        print('Appending variable: {}'.format(variable_json))
        ja.append(variable_json)
        return
    raw_level = h.pop(0)  #level from raw variable
    json_level = hierarchy_map[raw_level]   #mapped to level to be used in json
    print('raw_level: {} and json_level: {}'.format(raw_level,json_level))
    #check if level needs to be added to hierarchy structure then add if needed
    if not ja or json_level not in ja[0].keys():
        #levels are always in the [0] position
        ja.insert(0,{json_level:[]})
        print('Inserted json_level: {} into jason_append "ja": {}'.format(json_level,ja))
    print('ja: {}'.format(ja))
    
    # now check if the named raw_level already exists as a dict in the array
    # each dict in the array needs to be checked for the key
    index = search_array_for_dict_with_key(ja[0][json_level],rv[raw_level])
    if index is False:
    #if not ja[0][json_level][0] or rv[raw_level] not in ja[0][json_level][0].keys():
        #append the new level
        new_level = {rv[raw_level]:[]}
        ja[0][json_level].insert(0,new_level)
        index = 0
        print('Inserted new level to jason_append: {}'.format(ja))
    #move into the next level
    ja=ja[0][json_level][index][rv[raw_level]]
    print('Moved into the next level: {}'.format(ja))
    _add_to_dict_recursion(rv,h,ja)

def search_array_for_dict_with_key(s_array,key):
    '''
    returns False if dict is not found in array
    otherwise returns array index
    note: index 0 can be returned, so use explicit tests with result
    '''
    return next((i for i,item in enumerate(s_array) if key in item), False)


class samjsonparser(object):
    def __init__(self):
        self.main()
    
    def main(self):
        json_sample = os.path.dirname(os.path.realpath(__file__)) + os.sep + json_infile
        with open(json_sample, "r") as read_file:
            ssc_json = json.load(read_file)
            
            # initalize json_out dict
            first_level = {hierarchy_map[recursion_path[0]]:[]}
            json_out = {model:[first_level]}
            
            for i in ssc_json[model]:
                print('\nWorking with variable: {}'.format(i))
                add_to_dict(i,json_out)
        with open(json_outfile, 'w') as outfile:
            json.dump(json_out, outfile)
                
# =============================================================================
#         subsection_vars = {}
#         section_subsections = {}
#         section_json = {}
#         tab_json = {}
#         tab_json.setdefault("undefined", [])
#         values = [];
#         
#         tabs = [];
#         sections = [];
#         subsections = [];
#         count = 0
#         for i in ssc_json["tcslinear_fresnel"]:
#             count = count + 1
#             variable_json = {}
#             variable_json["name"] = i["Name"]
#             variable_json["datatype"] = i["DataType"]        
#             variable_json["label"] = i["Label"]         
# 
#             if ("Value" in i):
#                 variable_json["value"] = i["Value"]
#             if ("Units" in i):
#                 variable_json["units"] = i["Units"]
#             if ("Require" in i):
#                 variable_json["require"] = i["Require"]
#             if ("Constraints" in i):
#                 variable_json["constraints"] = i["Constraints"]
#             
#             # Checks if the variable in csv (json input) has a tabname associated with it.
#             if("Tab" in i):
#                 # Adding name of tab to the list
#                  if(i["Tab"] not in tabs):
#                      tabs.append(i["Tab"]);
#                      print("tab: {}".format(i["Tab"])
#                      values.append(i)
#                      tab = i["Tab"]
# 
#                  # Checks if the variable in csv (json input) has a tab name associated with it.
#                  if "Section" in i:
#                      sect = i["Section"]
#                      sect_var = {}
#                      # Checks if the variable in csv (json input) has a section associated with it.
#                      if "Subsection" in i:
#                          # To be implemented
#                         print(variable_json)
#                         subsect = i["Subsection"]
#                         subsect_var = {}
#                         # Block gets executed when variable has a tab and section, but no subsection in csv.
#                         # Checks if tab is present in the json being created.
#                         if tab in tab_json:
#                              # Adds variable to the tab section of json being created if the tab is present in the json being created.
#                              sectExists = False
# 
#                              for index in range(len(tab_json[tab])):
#                                 # Checks if the section exists in the json being created.
#                                 for section in tab_json[tab][index]:
#                                     if sect == section:
#                                         sectExists = True
#                                         subsectExists = False
#                                         for index2 in range(len(tab_json[tab][index])):
#                                             for subsection in tab_json[tab][index][sect][index2]:
#                                                 if subsect in subsection:
#                                                     # Removes the existing section block from json being created.
#                                                     # Appends the new variable to the existing subsection block and adds it to the original json being created.
#                                                     subsectExists = True
#                                                     valsToAdd = {}
#                                                     vals = tab_json[tab][index][sect][index2]
#                                                     vals[subsect].append(variable_json)
#                                                     vals_sect = tab_json[tab][index]
#                                                     vals_sect[sect].remove(tab_json[tab][index][sect][index2])
#                                                     vals_sect[sect].append(vals)
#                                                     tab_json[tab].remove(tab_json[tab][index])
#                                                     valsToAdd[sect] = vals_sect
#                                                     tab_json[tab].append(valsToAdd)
#                                                     break
#                                         if not subsectExists:
#                                             # This block gets executed when subsection does not exist in the json being created,
#                                             # but section and tab exists.
#                                             # Adds the subsection and variable to the existing section and adds it to the json being created.
#                                             subsect_var.setdefault(subsect, [])
#                                             subsect_var[subsect].append(variable_json)
#                                             sect_var = tab_json[tab][index]
#                                             #sect_var[sect].remove(subsection)
#                                             sect_var[sect].append(subsect_var)
#                                             tab_json[tab].remove(section)
#                                             tab_json[tab].append(sect_var)
#                                             break
#                              if not sectExists:
#                                 subsect_var.setdefault(subsect, [])
#                                 subsect_var[subsect].append(variable_json)
#                                 sect_var.setdefault(sect, [])
#                                 sect_var[sect].append(subsect_var)
#                                 tab_json[tab].append(sect_var)
#                                 #break
#                         else:
#                             # Creates json elements for tab and section, and appends the variable
#                             tab_json.setdefault(tab, [])
#                             sect_var.setdefault(sect, [])
#                             sect_var[sect].append(variable_json)
#                             tab_json[tab].append(sect_var)
# 
# 
#                      else:
#                          # Block gets executed when variable has a tab and section, but no subsection in csv.
#                          # Checks if tab is present in the json being created.
#                          if tab in tab_json:
#                              # Adds variable to the tab section of json being created if the tab is present in the json being created.
#                              sectExists = False
# 
#                              for section in tab_json[tab]:
#                                 # Checks if the section exists in the json being created.
#                                 if sect in section:
#                                     # Removes the existing section block from json being created.
#                                     # Appends the new variable to the existing section block and adds it to the original json being created.
#                                     sectExists = True
#                                     valsToAdd = {}
#                                     vals = section[sect]
#                                     vals.append(variable_json)
#                                     tab_json[tab].remove(section)
#                                     valsToAdd[sect] = vals
#                                     tab_json[tab].append(valsToAdd)
#                                     break
# 
#                              if not sectExists:
#                                 sect_var.setdefault(sect, [])
#                                 sect_var[sect].append(variable_json)
#                                 tab_json[tab].append(sect_var)
#                                     
#                          else:
#                             # Creates json elements for tab and section, and appends the variable
#                             tab_json.setdefault(tab, [])
#                             sect_var.setdefault(sect, [])
#                             sect_var[sect].append(variable_json)
#                             tab_json[tab].append(sect_var)
# 
#                  else:
#                      # Block gets executed when variable has a tab, but no section or subsection in csv.
#                      # Checks if tab is present in the json being created.
#                      if tab in tab_json:
#                          # Adds variable to the tab if the tab is present in the json being created.
#                         tab_json[tab].append(variable_json)
#                      else:
#                         # Creates the json element for the tab and appends the variable.
#                         tab_json.setdefault(tab, [])
#                         tab_json[tab].append(variable_json)
# 
# 
#             else: #NOT ("Tab" in i):
#                 # Adds variables to the json under tab_name = 'undefined' 
#                 # if there is no tab associated with the variable.
#                 tab_json["undefined"].append(variable_json)
# 
#         with open('lfjson.json', 'w') as outfile:
#             json.dump(tab_json, outfile)
# 
# =============================================================================
if __name__ == '__main__':
    sam = samjsonparser()
    sam.main()          