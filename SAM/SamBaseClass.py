

from SAM.PySSC import PySSC
import logging, json
import ast

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
        self.varList = self.collect_all_vars_from_json()
        self.set_data(self.varList)
        self.module_create_execute('tcslinear_fresnel')
        self.print_impParams()
        self.data_free()
        

    def collect_all_vars_from_json(self):
        with open(r"D:\Drive\Thesis\Github\DOE_CSP_PROJECT\SAM\models\tcslinear_fresnel.json", "r") as read_file:
            ssc_json = json.load(read_file)
        all_variables = []

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
        return all_variables

    def set_data(self, variables):
        with open(r"D:\Drive\Thesis\Data\Json\samLinearFresnelDirectSteam.json", "r") as read_file:
            ssc_json = json.load(read_file)


        # Map all the strings present in the json file.
        stringsInJson = {}
        added_variables = {}

        # Increment complete TODOs count for each user.
        try:
            for ssc_var in variables:
                #Checking if the variable value is present in the json and if value of the variable is a valid one.
                if ("value" in ssc_var and ssc_var["value"] != "#N/A"):
                    # Add value to the dictionary.
                    
                    
                    varName = ssc_var["name"]
                    added_variables[varName] = False
                    
                    if (ssc_var["datatype"] == "SSC_STRING"):
                        varValue = ssc_var["value"].encode("ascii", "backslashreplace")
                        self.ssc.data_set_string( self.data, b''+ varName.encode("ascii", "backslashreplace"), b'' + varValue)
                        added_variables[varName] = True

                    elif (ssc_var["datatype"] == "SSC_ARRAY"):
                        varValue = ast.literal_eval( ssc_var["value"] )
                        self.ssc.data_set_array( self.data, b''+ varName.encode("ascii", "backslashreplace"), varValue )
                        added_variables[varName] = True

                    elif (ssc_var["datatype"] == "SSC_MATRIX"):
                        varValue = ast.literal_eval( ssc_var["value"] )
                        self.ssc.data_set_matrix( self.data, b''+ varName.encode("ascii", "backslashreplace"), varValue)
                        added_variables[varName] = True

                    elif (ssc_var["datatype"] == "SSC_NUMBER"):
                        varValue = ast.literal_eval( ssc_var["value"] )
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
        capacity_factor = self.ssc.data_get_number(self.data, b'capacity_factor');
        print ('\nCapacity factor (year 1) = ', capacity_factor)
#        annual_total_water_use = self.ssc.data_get_number(self.data, b'annual_total_water_use');
#        print ('Annual Water Usage = ', annual_total_water_use)
        annual_energy = self.ssc.data_get_number(self.data, b'annual_energy');
        print ('Annual energy (year 1) = ', annual_energy)


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