from SAM.PySSC import PySSC
import logging, json, os
from pathlib import Path
import numpy as np

class SamBaseClass(object):
    """description of class"""

    def __init__(self,
                 CSP          = 'tcstrough_physical',
                 financial    = 'singleowner',
                 cspInputFile = 'tcstrough_physical_singleowner.json',
                 financialInputFile = 'singleowner_tcstrough_physical.json',
                 desalination =  None,
                 weatherfile  = 'C:/SAM/2018.11.11/solar_resource/tucson_az_32.116521_-110.933042_psmv3_60_tmy.csv'):
        #Sets up logging for the SAM Modules
        self._setup_logging('SamBaseClass')
        self.cspModel = CSP
        self.financialModel = financial
        self.cspInputFile =cspInputFile
        self.financialInputFile =financialInputFile
        self.Desalination = desalination
        self.weatherFile = weatherfile

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
        
#        self.cspModel = "TcstroughPhysical_PhysicalTrough"
#        self.financialModel = "SingleOwner"
#        self.weatherFile = 'C:/SAM/2018.11.11/solar_resource/tucson_az_32.116521_-110.933042_psmv3_60_tmy.csv'
        self.varListCsp = self.collect_model_variables()
        #self.varListCsp = self.collect_all_vars_from_json(samPath + "/models/inputs/" + self.cspModel + ".json")
        self.set_data(self.varListCsp)
        self.module_create_execute(self.cspModel)
#        self.module_create_execute('tcstrough_physical')

        #self.varListFin = self.collect_all_vars_from_json(samPath + "/models/inputs/" + self.financialModel + ".json")
        #self.set_data(self.varListFin)
        if self.financialModel:
            self.module_create_execute(self.financialModel)
            if self.financialModel == 'iph_to_lcoefcr':
                self.module_create_execute('lcoefcr')
#        self.module_create_execute('singleowner')
        if self.Desalination:
            self.T_cond = self.P_T_conversion()
            self.GOR, self.MD = self.LT_MED_water_empirical(self.T_cond)
        
        
        self.print_impParams()
        self.data_free()
        

    def collect_model_variables(self):

        json_files = []
        cspPath = self.cspModel + '_inputs.json'
        finPath = self.financialModel + '_inputs.json'
        json_files.append(Path(self.samPath / "models" / "inputs" / cspPath))
        json_files.append(Path(self.samPath / "models" / "inputs" / finPath))


        # cspValues = self.cspModel + "_" + self.financialModel + ".json"
        # finValues = self.financialModel + "_" + self.cspModel + ".json"

        json_values = []
        json_values.append(Path(self.samPath / "defaults" / self.cspInputFile))
        json_values.append(Path(self.samPath / "defaults" / self.financialInputFile))
        # json_values.append( Path(self.samPath / "defaults" /cspValues))
        # json_values.append( Path(self.samPath / "defaults" /finValues))

        if self.financialModel == 'iph_to_lcoefcr':
            fin2Path = 'lcoefcr' + self.cspModel + '_inputs.json'
            json_files.append(Path(self.samPath / "models" / "inputs" / fin2Path))

            fin2Values= 'lcoefcr_' + self.cspModel + "_" + self.financialModel + '.json'
            json_values.append(Path(self.samPath / "defaults" /fin2Values))

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
                # elif variable['name'] not in values_json['defaults'][variable['group']] :
                #     varValue = ""

                elif variable['name'] not in values_json['defaults'][variable['group']] and variable['datatype'] == 'SSC_NUMBER':
                    if 'require' in variable:
                        if variable['require'] == '*':
                            varValue = 0
                        else:
                            varValue = float(variable['require'])
                    else:
                        varValue = ""     
                    # print(variable['name'], varValue)
                elif variable['name'] not in values_json['defaults'][variable['group']] and variable['datatype'] == 'SSC_ARRAY':
                    if 'require' in variable:
                        varValue = [0]
                    else:
                        varValue = ""
                    # print(variable['name'], varValue)
                    
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
            
            self.ssc.module_exec_set_print( 0 )
            if self.ssc.module_exec(module1, self.data) == 0:
                print ('{} simulation error'.format(module1))
                idx = 1
                msg = self.ssc.module_log(module1, 0)
                while (msg != None):
                    print ('	: ' + msg.decode("utf - 8"))
                    msg = self.ssc.module_log(module1, idx)
                    idx = idx + 1
                SystemExit( "Simulation Error" )
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

    def P_T_conversion(self):
        Cond_p = self.ssc.data_get_array(self.data, b'P_cond')
        Cond_temp=[]
        Cond_temp_root2=[]
        for i in Cond_p:
        #   Coefficients for the equation to find out Condenser Temperature
            coeff = [9.655*10**-4, -0.039, 4.426, -19.64, (1123.1 - i)]
            
            temps = np.roots(coeff)
            #Getting real roots
            temps_real = temps.real[abs(temps.imag < 1e-5)] #Imaginary parts are sometimes not exaclty zero becuase of approximations in calculation
            #Filtering for positive values
            temps_yearly = temps_real[temps_real >= 0]
            Cond_temp.append(temps_yearly) #Enter equation here
            
            #Making an array of the second real root as it seemed to model actual values better
            #By analyzing the outputs, it was found that root2 of the fourth order equation gave right values
            Cond_temp_root2.append(max(temps_yearly))

        # Eliminate any temperature below 60 deg C and above 75 deg C
        for temp in Cond_temp_root2:
            if temp < 60:
                temp = 0
            elif temp > 85:
                temp = 80
        #print(Cond_temp_root2)        
        return Cond_temp_root2
    
        
    def LT_MED_water_empirical(self, T_cond):
        Ms = self.ssc.data_get_array(self.data, b'm_dot_makeup')
        Ms_max = max(Ms)
        Ms_capacity = Ms_max/14/3600

        GOR = []
        Md = []
        for i in range(len(T_cond)):
            Ms[i] = Ms[i] /3600/Ms_capacity
            if T_cond[i] > 55 and T_cond[i] < 75:
                GOR.append(648.2-26.74* T_cond[i]-16.45*Ms[i]+0.3842*T_cond[i]**2+0.3137*T_cond[i]*Ms[i]+0.5995*Ms[i]**2-0.001835*T_cond[i]**3-0.002371*T_cond[i]**2*Ms[i]-0.0001411*T_cond[i]*Ms[i]**2-0.01844*Ms[i]**3)
                Md.append(-0.273+0.008409*T_cond[i]-0.04452*Ms[i]+0.0003093*T_cond[i]**2+0.001969*T_cond[i]*Ms[i]-0.002485*Ms[i]**2)
            else:
                GOR.append(0)
                Md.append(0)
#        print(Ms)
        print('GOR:',max(GOR))
        print('Md:',max(Md))
        return GOR, Md

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
            value = self.ssc.data_get_number(self.data, variable.encode('utf-8'))#bytes(variable, 'utf-8'));
            arrayVal = self.ssc.data_get_array(self.data, variable.encode('utf-8'))
            outputs.append({'name': variable,
                            'value': value,
                            'array': arrayVal})

        if self.financialModel == 'iph_to_lcoefcr':
            lcoe_fcr = self.ssc.data_get_number(self.data, b'lcoe_fcr')
            print ('\nLCOH = ', lcoe_fcr)
            annual_energy = self.ssc.data_get_number(self.data, b'annual_energy')
            print ('Annual energy (year 1) = ', annual_energy)

        else:
            capacity_factor = self.ssc.data_get_number(self.data, b'capacity_factor')
            print ('\nCapacity factor (year 1) = ', capacity_factor)
            annual_energy = self.ssc.data_get_number(self.data, b'annual_energy')
            print ('Annual energy (year 1) = ', annual_energy)
            lcoe_real = self.ssc.data_get_number(self.data, b'lcoe_real')
            print ('LCOE_real = ', lcoe_real)
        
            # outputs.append({'name': 'capacity_factor',
            #                 'value': capacity_factor})
    
            # outputs.append({'name': 'annual_energy',
            #                 'value': annual_energy})

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