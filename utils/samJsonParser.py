# -*- coding: utf-8 -*-
"""
Created on Wed May  8 12:30:18 2019

@author: vikas
"""
import json

class samjsonparser(object):
    def __init__(self):
        self.main()
        
    def main(self):
        json_sample = os.path.dirname(os.path.realpath(__file__)) + "/utils/samLinearFresnelDirectSteam.json"
        with open(json_sample, "r") as read_file:
            ssc_json = json.load(read_file)
            
        
        subsection_vars = {}
        section_subsections = {}
        section_json = {}
        tab_json = {}
        tab_json.setdefault("undefined", [])
        values = [];
        
        tabs = [];
        sections = [];
        subsections = [];
        count = 0
        for i in ssc_json["tcslinear_fresnel"]:
            count = count + 1
            variable_json = {}
            variable_json["name"] = i["Name"]
            variable_json["datatype"] = i["DataType"]        
            variable_json["label"] = i["Label"]         

            if ("Value" in i):
                variable_json["value"] = i["Value"]
            if ("Units" in i):
                variable_json["units"] = i["Units"]
            if ("Require" in i):
                variable_json["require"] = i["Require"]
            if ("Constraints" in i):
                variable_json["constraints"] = i["Constraints"]
            
            # Checks if the variable in csv (json input) has a tabname associated with it.
            if("Tab" in i):
                # Adding name of tab to the list
                 if(i["Tab"] not in tabs):
                     tabs.append(i["Tab"]);
                     print(i["Tab"])
                     values.append(i)
                     tab = i["Tab"]

                 # Checks if the variable in csv (json input) has a tab name associated with it.
                 if "Section" in i:
                     sect = i["Section"]
                     sect_var = {}
                     # Checks if the variable in csv (json input) has a section associated with it.
                     if "Subsection" in i:
                         # To be implemented
                        print(variable_json)
                        subsect = i["Subsection"]
                        subsect_var = {}
                        # Block gets executed when variable has a tab and section, but no subsection in csv.
                        # Checks if tab is present in the json being created.
                        if tab in tab_json:
                             # Adds variable to the tab section of json being created if the tab is present in the json being created.
                             sectExists = False

                             for index in range(len(tab_json[tab])):
                                # Checks if the section exists in the json being created.
                                for section in tab_json[tab][index]:
                                    if sect == section:
                                        sectExists = True
                                        subsectExists = False
                                        for index2 in range(len(tab_json[tab][index])):
                                            for subsection in tab_json[tab][index][sect][index2]:
                                                if subsect in subsection:
                                                    # Removes the existing section block from json being created.
                                                    # Appends the new variable to the existing subsection block and adds it to the original json being created.
                                                    subsectExists = True
                                                    valsToAdd = {}
                                                    vals = tab_json[tab][index][sect][index2]
                                                    vals[subsect].append(variable_json)
                                                    vals_sect = tab_json[tab][index]
                                                    vals_sect[sect].remove(tab_json[tab][index][sect][index2])
                                                    vals_sect[sect].append(vals)
                                                    tab_json[tab].remove(tab_json[tab][index])
                                                    valsToAdd[sect] = vals_sect
                                                    tab_json[tab].append(valsToAdd)
                                                    break
                                        if not subsectExists:
                                            # This block gets executed when subsection does not exist in the json being created,
                                            # but section and tab exists.
                                            # Adds the subsection and variable to the existing section and adds it to the json being created.
                                            subsect_var.setdefault(subsect, [])
                                            subsect_var[subsect].append(variable_json)
                                            sect_var = tab_json[tab][index]
                                            #sect_var[sect].remove(subsection)
                                            sect_var[sect].append(subsect_var)
                                            tab_json[tab].remove(section)
                                            tab_json[tab].append(sect_var)
                                            break
                             if not sectExists:
                                subsect_var.setdefault(subsect, [])
                                subsect_var[subsect].append(variable_json)
                                sect_var.setdefault(sect, [])
                                sect_var[sect].append(subsect_var)
                                tab_json[tab].append(sect_var)
                                #break
                        else:
                            # Creates json elements for tab and section, and appends the variable
                            tab_json.setdefault(tab, [])
                            sect_var.setdefault(sect, [])
                            sect_var[sect].append(variable_json)
                            tab_json[tab].append(sect_var)


                     else:
                         # Block gets executed when variable has a tab and section, but no subsection in csv.
                         # Checks if tab is present in the json being created.
                         if tab in tab_json:
                             # Adds variable to the tab section of json being created if the tab is present in the json being created.
                             sectExists = False

                             for section in tab_json[tab]:
                                # Checks if the section exists in the json being created.
                                if sect in section:
                                    # Removes the existing section block from json being created.
                                    # Appends the new variable to the existing section block and adds it to the original json being created.
                                    sectExists = True
                                    valsToAdd = {}
                                    vals = section[sect]
                                    vals.append(variable_json)
                                    tab_json[tab].remove(section)
                                    valsToAdd[sect] = vals
                                    tab_json[tab].append(valsToAdd)
                                    break

                             if not sectExists:
                                sect_var.setdefault(sect, [])
                                sect_var[sect].append(variable_json)
                                tab_json[tab].append(sect_var)
                                    
                         else:
                            # Creates json elements for tab and section, and appends the variable
                            tab_json.setdefault(tab, [])
                            sect_var.setdefault(sect, [])
                            sect_var[sect].append(variable_json)
                            tab_json[tab].append(sect_var)

                 else:
                     # Block gets executed when variable has a tab, but no section or subsection in csv.
                     # Checks if tab is present in the json being created.
                     if tab in tab_json:
                         # Adds variable to the tab if the tab is present in the json being created.
                        tab_json[tab].append(variable_json)
                     else:
                        # Creates the json element for the tab and appends the variable.
                        tab_json.setdefault(tab, [])
                        tab_json[tab].append(variable_json)


            else:
                # Adds variables to the json under tab_name = 'undefined' 
                # if there is no tab associated with the variable.
                tab_json["undefined"].append(variable_json)

        with open('lfjson.json', 'w') as outfile:
            json.dump(tab_json, outfile)

if __name__ == '__main__':
    sam = samjsonparser()
    sam.main()          