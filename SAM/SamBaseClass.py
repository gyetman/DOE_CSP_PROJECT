from SAM.PySSC import PySSC
import logging, json, os
from pathlib import Path

class SamBaseClass(object):
    """description of class"""

    def __init__(self):
        #Sets up logging for the SAM Modules
        self._setup_logging('SamBaseClass')

    def create_ssc_module(self):
        try:
            self.ssc.module_exec_set_print(0)        
            #return self.data
        except Exception:
            self.logger.critical("Exception occurred while creating the SAM module. Please see the detailed error message below", exc_info=True)

    def main(self):
        self.ssc = PySSC()
        self.create_ssc_module()
        self.data = self.ssc.data_create()

        self.samPath = Path(__file__).resolve().parent
        #self.samPath = Path("source_data/text_files/")
        self.cspModel = "TcslinearFresnel_DSLF"
        self.financialModel = "LeveragedPartnershipFlip"
        self.weatherFile = 'C:\\SAM/2018.11.11\\solar_resource\\USA_AZ_Tucson_32.116699_-110.932999_psmv3_60_tmy.csv'
        self.varListCsp = self.collect_model_variables()
        #self.varListCsp = self.collect_all_vars_from_json(samPath + "/models/inputs/" + self.cspModel + ".json")
        self.set_data(self.varListCsp)
        self.module_create_execute('tcslinear_fresnel')

        #self.varListFin = self.collect_all_vars_from_json(samPath + "/models/inputs/" + self.financialModel + ".json")
        #self.set_data(self.varListFin)
        self.module_create_execute('levpartflip')

        self.print_impParams()
        self.data_free()
        

    def collect_model_variables(self):

        json_files = []
        cspPath = self.cspModel + '_inputs.json'
        finPath = self.financialModel + '_inputs.json'
        json_files.append(Path(self.samPath / "models" / "inputs" / cspPath))
        json_files.append(Path(self.samPath / "models" / "inputs" / finPath))

        cspValues = self.cspModel + self.financialModel + ".json"
        finValues = "Levpartflip_DSLFLeveragedPartnershipFlip.json"
        json_values = []
        json_values.append( Path(self.samPath / "defaults" /cspValues))
        json_values.append( Path(self.samPath / "defaults" /finValues))
        variableValues = []

        i = 0
        for json_file in json_files:
            all_variables = []
            with open(json_file, "r") as read_file:
                ssc_json = json.load(read_file)
            with open(json_values[i], "r") as read_file:
                values_json = json.load(read_file)
            i = i + 1
            #ssc_json dictionary has all the data
            for model, tabsOrVars in ssc_json.items():
                #Tabs or variables present in the main json
                for tabOrVar in tabsOrVars:
                    try:
                        tabs = tabOrVar['tabs']
                        # Iterate over all tabs in the json.
                        for tab in tabs:
                            for tabName, sectsOrVars in tab.items():
                                for sectOrVar in sectsOrVars:
                                    try:
                                        sects = sectOrVar['sections']
                                        # Iterate over all sections in the json.
                                        for sect in sects:
                                            for sectName, subSectsOrVars in sect.items():
                                                for subSectOrVar in subSectsOrVars:
                                                    try:
                                                        subSect = subSectOrVar['subsections']
                                                        # Iterate over all subsections in the json.
                                                        for subSector in subSect:
                                                            for subSectName, variables in subSector.items():
                                                                # Add variables in a subsection.
                                                                for variable in variables:
                                                                    all_variables.append(variable)
                                                    # Add variables that does not belong to any subsection, but is in a section.
                                                    except KeyError:
                                                        all_variables.append(subSectOrVar)
                                    # Add variables that does not belong to any section, but is in a tab.
                                    except KeyError:
                                        all_variables.append(sectOrVar)
                    # Add variables that does not belong to any tab.
                    except KeyError:
                        all_variables.append(tabOrVar)


            for variable in all_variables:
                if variable['name'] == 'file_name':
                    varValue = self.weatherFile
                elif variable['name'] == 'gen':
                    varValue = 0.050000001
                else:
                    varValue = values_json['defaults'][variable['group']][variable['name']]
                try:
                    variableValues.append({'name': variable['name'],
                                           'value': varValue,
                                           'datatype': variable['datatype'],
                                           'constraint': variable['constraint'] })
                except KeyError:
                    variableValues.append({'name': variable['name'],
                                           'value': varValue,
                                           'datatype': variable['datatype'] })

            #variable.valu
        return variableValues


    def set_data(self, variables):

        # Map all the strings present in the json file.
        stringsInJson = {}
        added_variables = {}

        # Increment complete TODOs count for each user.

        for ssc_var in variables:
            try:
                #Checking if the variable value is present in the json and if value of the variable is a valid one.
                if ("value" in ssc_var and ssc_var["value"] != "#N/A" and ssc_var["value"] != ""):
                    # Add value to the dictionary.
                    
                    
                    varName = ssc_var["name"]
                    added_variables[varName] = False
                    
                    if (ssc_var["datatype"] == "SSC_STRING"):
                        varValue = ssc_var["value"].encode("ascii", "backslashreplace")
                        self.ssc.data_set_string( self.data, b''+ varName.encode("ascii", "backslashreplace"), b'' + varValue)
                        added_variables[varName] = True

                    elif (ssc_var["datatype"] == "SSC_ARRAY"):
                        varValue = ssc_var["value"] #ast.literal_eval( ssc_var["value"] )
                        self.ssc.data_set_array( self.data, b''+ varName.encode("ascii", "backslashreplace"), varValue )
                        added_variables[varName] = True

                    elif (ssc_var["datatype"] == "SSC_MATRIX"):
                        varValue = ssc_var["value"] #ast.literal_eval( ssc_var["value"] )
                        self.ssc.data_set_matrix( self.data, b''+ varName.encode("ascii", "backslashreplace"), varValue)
                        added_variables[varName] = True

                    elif (ssc_var["datatype"] == "SSC_NUMBER"):
                        varValue = ssc_var["value"] #ast.literal_eval( ssc_var["value"] )
                        if "constraint" in ssc_var:
                            if (ssc_var["constraint"] == "INTEGER"):
                                self.ssc.data_set_number( self.data, b''+ varName.encode("ascii", "backslashreplace"), int(varValue))
                                added_variables[varName] = True
                            if (ssc_var["constraint"] == "MAX=100"):
                                #Verify if the variable is above 100
                                if (varValue > 100 or varValue <0):
                                    raise Exception("The value specified for '" + varName + "' is not within the specified range.")
                                else:
                                    self.ssc.data_set_number( self.data, b''+ varName.encode("ascii", "backslashreplace"), int(varValue))
                                    added_variables[varName] = True

                        else:
                            self.ssc.data_set_number( self.data, b''+ varName.encode("ascii", "backslashreplace"), float(varValue))
                            added_variables[varName] = True

                    else:
                        # Add value to the dictionary.
                        raise Exception("Specified variable type for SAM file from the JSON is not found in definitions.")
                    stringsInJson[varName] = varValue

            except Exception as error:
                self.logger.critical(error)
                print(error)
                print(ssc_var)
                self.logger.info(stringsInJson)

    def module_create_execute(self, module):
        module1 = self.ssc.module_create(b'' + module.encode("ascii", "backslashreplace"))	
        try:
            self.logger.debug("Running execute statements for the SAM module '" + module + "'.")
            
            self.ssc.module_exec_set_print( 0 );
            if self.ssc.module_exec(module1, self.data) == 0:
                print ('{} simulation error'.format(module1))
                idx = 1
                msg = self.ssc.module_log(module1, 0)
                while (msg != None):
                    print ('	: ' + msg.decode("utf - 8"))
                    msg = self.ssc.module_log(module1, idx)
                    idx = idx + 1
                SystemExit( "Simulation Error" );
            self.ssc.module_free(module1)
        except Exception as e:
            print(e)
            idx = 1
            msg = self.ssc.module_log(module1, 0)
            while (msg != None):
                print ('	: ' + msg.decode("utf - 8"))
                self.logger.info('	: ' + msg.decode("utf - 8"))
                msg = self.ssc.module_log(module1, idx)
                idx = idx + 1
            self.logger.critical("Exception occurred while executing the SAM module. Please see the detailed error message below", exc_info=True)

    def data_free(self):
        self.ssc.data_clear(self.data)

    def print_impParams(self):
        cspOuts = self.cspModel + "_outputs.json"

        output_values = Path(self.samPath / "models" / "outputs" / cspOuts)
        with open(output_values, "r") as read_file:
            outputs_json = json.load(read_file)
        output_vars = []
        for outputs in outputs_json['TcslinearFresnel_LFDS']:
            output_vars.append(outputs['Name'])

        outputs = []
        for variable in output_vars:
            if variable == 'twet': continue
            value = self.ssc.data_get_number(self.data, variable.encode('utf-8'));#bytes(variable, 'utf-8'));
            arrayVal = self.ssc.data_get_array(self.data, variable.encode('utf-8'));
            outputs.append({'name': variable,
                            'value': value,
                            'array': arrayVal})

        capacity_factor = self.ssc.data_get_number(self.data, b'capacity_factor');
        print ('\nCapacity factor (year 1) = ', capacity_factor)
#        annual_total_water_use = self.ssc.data_get_number(self.data, b'annual_total_water_use');
#        print ('Annual Water Usage = ', annual_total_water_use)
        annual_energy = self.ssc.data_get_number(self.data, b'annual_energy');
        print ('Annual energy (year 1) = ', annual_energy)
        
        outputs.append({'name': 'capacity_factor',
                        'value': capacity_factor})

        outputs.append({'name': 'annual_energy',
                        'value': annual_energy})
        json_outfile = 'sample.json'
        with open(json_outfile, 'w') as outfile:
            json.dump(outputs, outfile)
        #print ('outputs = ', outputs)


    #Setup logging for the SAM modules
    def _setup_logging(self, className, verbose=False, level = logging.INFO):
        # create logger
        logging.basicConfig(level=logging.DEBUG)
        #The below statement works only once. New loggers have to be created for each module.
        self.logger = logging.getLogger(className)
        #logger.setLevel(logging.DEBUG)
    
        # create console handler and set level to debug - echo to the output - on DOS or anything
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
    
        # create file handler and set level to warning - log level for file
        fh = logging.FileHandler('./logs/applog.log')
        fh.setLevel(logging.INFO)
    
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # add formatter to ch    
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
    
        # add ch to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    
        # test statements; note the use of "logger" instead of "logging";
        # using the latter will still work for the default logger but will not
        # write anything to a file. 
        self.logger.info('Logger started.')
        self.logger.debug('detailed statements here...')
        self.logger.warning('Warning message! Be forewarned!')
        self.logger.critical('Critical error, omg!')


if __name__ == '__main__':
    sam = SamBaseClass()
    sam.main()
    
    #Argument for the unit test makes sure the unit test does not fail if system_capacity 
    #system_capacity is passed as a first argument on command line.
    #unittest.main(argv=['first-arg-is-ignored'], exit=False)