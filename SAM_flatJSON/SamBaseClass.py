from SAM_flatJSON.PySSC import PySSC
import logging, json, os
from pathlib import Path
import numpy as np
from datetime import datetime
import app_config as cfg
import helpers
import csv
import xlwt


class SamBaseClass(object):
    """description of class"""

    def __init__(self,
                 CSP = 'linear_fresnel_dsg_iph',
                 financial = 'iph_to_lcoefcr',
                 desalination =  'VAGMD',
                 json_value_filepath = None,
                 desal_json_value_filepath = None,
                 cost_json_value_filepath = None,
                 timestamp = ''
                 ):
        #Sets up logging for the SAM Modules
        self._setup_logging('SamBaseClass')
        self.cspModel = CSP
        self.financialModel = financial
        self.desalination = desalination
        self.samPath = Path(__file__).resolve().parent
        self.timestamp = timestamp
        # Use the user defined json file as input values
        if json_value_filepath:
            self.json_values = json_value_filepath
            
        # For internal use only, if no json file is given, use default values
        else:
            if self.financialModel:
                Values = self.cspModel + "_" + self.financialModel + ".json"
                self.json_values = Path(self.samPath / "defaults" /Values)
            else: # if no finiancial model, just add CSP values
                Values = self.cspModel + "_none" + ".json"
                self.json_values = Path(self.samPath / "defaults" /Values)
         # Add json value filepath for desal models, if any      
        if desal_json_value_filepath:
            self.desal_json_values = desal_json_value_filepath
        else:
            desal_values = self.desalination + ".json"
            self.desal_json_values = Path(self.samPath / "defaults" /desal_values)
            
        if cost_json_value_filepath:
            self.cost_json_values = cost_json_value_filepath
        else:
            cost_values = self.desalination + "_cost.json"
            self.cost_json_values = Path(self.samPath / "defaults" /cost_values)  

        with open(cfg.app_json) as app_file: 
            app = json.load(app_file) 
            self.project_name = app['project_name']                
            self.parametric = app["parametric"]




    def create_ssc_module(self):
        try:
            self.ssc.module_exec_set_print(0)        
            #return self.data
        except Exception:
            self.logger.critical("Exception occurred while creating the SAM module. Please see the detailed error message below", exc_info=True)

    def main(self, param = None):
        if self.cspModel=='pvsamv1':
            self.ssc = PySSC()
            self.create_ssc_module()
            self.data = self.ssc.data_create()
            self.varListCsp = self.collect_model_variables()
    
            self.set_data(self.varListCsp)
            # execute csp model
            self.module_create_execute(self.cspModel)

            # execute financial model, if any
            if self.financialModel:
                self.module_create_execute(self.financialModel)
                if self.financialModel == 'utilityrate5':
                    self.module_create_execute('cashloan')
            self.elec_gen = self.ssc.data_get_array(self.data, b'gen')
            self.lcoe = self.ssc.data_get_number(self.data, b'lcoe_fcr')
            
            
            if self.desalination:
                self.desal_simulation(self.desalination)
                self.cost(self.desalination)
                            
            self.sam_calculation()
            self.print_impParams()
            self.data_free()

        elif self.cspModel=='pvwattsv7':
            self.ssc = PySSC()
            self.create_ssc_module()
            self.data = self.ssc.data_create()
            self.varListCsp = self.collect_model_variables()
    
            self.set_data(self.varListCsp)
            # execute csp model
            self.module_create_execute(self.cspModel)
            # execute grid limit model
            self.module_create_execute('grid')
            # execute financial model, if any
            if self.financialModel:
                self.module_create_execute(self.financialModel)
                if self.financialModel == 'utilityrate5':
                    self.module_create_execute('cashloan')
            self.elec_gen = self.ssc.data_get_array(self.data, b'gen')
            self.lcoe = self.ssc.data_get_number(self.data, b'lcoe_fcr')
            
            
            if self.desalination:
                self.desal_simulation(self.desalination)
                self.cost(self.desalination)
                            
            self.sam_calculation()
            self.print_impParams()
            self.data_free()
      
        
        elif self.cspModel=='SC_FPC':
            from PSA.StaticCollector_flatplate import StaticCollector_fp
            from PSA.SC_ETC_cost import ETC_cost
            
            with open(self.json_values, "r") as read_file:
                solar_input = json.load(read_file)
            
            self.staticcollector=StaticCollector_fp(desal_thermal_power_req = solar_input['desal_thermal_power_req'],initial_water_temp = solar_input['initial_water_temp'],outlet_water_temp = solar_input['outlet_water_temp'],cleanless_factor = solar_input['cleanless_factor'],G = solar_input['G'],a = solar_input['a'], b = solar_input['b'], c = solar_input['c'], A = solar_input['A'], file_name = solar_input['file_name'], tilt_angle = solar_input['tilt_angle'], v1 = solar_input['v1'], v2 = solar_input['v2'] , qm = solar_input['qm'], Tamb_D = solar_input['Tamb_D'] )
            self.heat_gen, self.sc_output = self.staticcollector.design()
            filename = 'Solar_output' + self.timestamp +'.json'
            
            if self.parametric:
                sc_output_json_outfile = self.samPath / 'parametric_results' / filename  
            else:
                sc_output_json_outfile =  self.samPath / 'results' /filename
            with open(sc_output_json_outfile, 'w') as outfile:
                json.dump(self.sc_output, outfile)
            
            # Run desal model first
            self.desal_simulation(self.desalination)            

            # Run solar cost model next
            finance_model_outfile = f"lcoh_calculator{self.timestamp}_inputs.json"
            finance_model_outfile_path = Path(cfg.json_outpath / finance_model_outfile)
            with open(finance_model_outfile_path, "r") as read_file:
                cost_input = json.load(read_file)            

            self.collector_cost = ETC_cost(aperture_area = self.sc_output[3]['Value'], non_solar_area_multiplier = cost_input['non_solar_area_multiplier'], capacity = solar_input['desal_thermal_power_req'] * 1000,
                                           EC = cost_input['EC'], yrs = cost_input['yrs'], int_rate = cost_input['int_rate'], coe = cost_input['coe'], p_OM = cost_input['p_OM'],
                                           unit_cost = cost_input['unit_cost'], cost_boiler = cost_input['cost_boiler'], thermal_gen = sum(self.heat_gen), P_req = self.P_req)
            self.cost_out = self.collector_cost.lcoh()
            self.lcoh = self.cost_out[2]['Value']  
            
            # Run desal cost at last
            self.cost(self.desalination)
            self.print_collector_params(self.sc_output)
            
        elif self.cspModel=='SC_ETC':
            from PSA.StaticCollector_evacuatedtube import StaticCollector_et
            from PSA.SC_ETC_cost import ETC_cost
            
            app = helpers.json_load(cfg.app_json)
            flkup = cfg.build_file_lookup(app['solar'],app['desal'],app['finance'],app['timestamp'])
            
            
            with open(self.json_values, "r") as read_file:
                solar_input = json.load(read_file)
            self.staticcollector=StaticCollector_et(desal_thermal_power_req = solar_input['desal_thermal_power_req'],
                                                    initial_water_temp = solar_input['initial_water_temp'],outlet_water_temp = solar_input['outlet_water_temp'],
                                                    cleanless_factor = solar_input['cleanless_factor'],G = solar_input['G'],a = solar_input['a'], b = solar_input['b'], c = solar_input['c'], 
                                                    A = solar_input['A'], file_name = solar_input['file_name'], tilt_angle = solar_input['tilt_angle'], v1 = solar_input['v1'], 
                                                    v2 = solar_input['v2'], v3 = solar_input['v3'], qm = solar_input['qm'], Tamb_D = solar_input['Tamb_D'] )
            self.heat_gen, self.et_output = self.staticcollector.design()
            filename = 'Solar_output' + self.timestamp +'.json'
            if self.parametric:
                et_output_json_outfile = self.samPath / 'parametric_results' / filename  
            else:
                et_output_json_outfile =  self.samPath / 'results' /filename
            with open(et_output_json_outfile, 'w') as outfile:
                json.dump(self.et_output, outfile)
            
            # Run desal model first
            self.desal_simulation(self.desalination)            

            # Run solar cost model next
            finance_model_outfile = f"lcoh_calculator{self.timestamp}_inputs.json"
            finance_model_outfile_path = Path(cfg.json_outpath / finance_model_outfile)
            with open(finance_model_outfile_path, "r") as read_file:
                cost_input = json.load(read_file)            

            self.collector_cost = ETC_cost(aperture_area = self.et_output[3]['Value'], non_solar_area_multiplier = cost_input['non_solar_area_multiplier'], capacity = solar_input['desal_thermal_power_req'] * 1000,
                                           EC = cost_input['EC'], yrs = cost_input['yrs'], int_rate = cost_input['int_rate'], coe = cost_input['coe'], p_OM = cost_input['p_OM'],
                                           unit_cost = cost_input['unit_cost'], cost_boiler = cost_input['cost_boiler'], thermal_gen = sum(self.heat_gen), P_req = self.P_req)
            self.cost_out = self.collector_cost.lcoh()
            self.lcoh = self.cost_out[2]['Value']  
            
            # Run desal cost at last
            self.cost(self.desalination)
            self.print_collector_params(self.et_output)
        
        elif self.cspModel== 'linear_fresnel_dsg_iph' or self.cspModel == 'trough_physical_process_heat':
            self.ssc = PySSC()
            self.create_ssc_module()
            self.data = self.ssc.data_create()
            self.varListCsp = self.collect_model_variables()
    
            self.set_data(self.varListCsp)
            # execute csp model
            self.module_create_execute(self.cspModel)

            # execute financial model, if any
            if self.financialModel:
                self.module_create_execute(self.financialModel)
                annual_energy = self.ssc.data_get_number(self.data, b'annual_energy')
                self.ssc.data_set_number( self.data, b'annual_energy', annual_energy )
                if self.financialModel == 'utilityrate5':
                    self.module_create_execute('cashloan')
                elif self.financialModel == 'iph_to_lcoefcr':
                    self.module_create_execute('lcoefcr')
            if self.cspModel== 'linear_fresnel_dsg_iph':
                self.heat_gen = self.ssc.data_get_array(self.data, b'gen')
            else:
                heat_genn = self.ssc.data_get_array(self.data, b'q_dot_to_heat_sink')
                self.heat_gen = np.dot(heat_genn, 1000)
            
            self.lcoh = self.ssc.data_get_number(self.data, b'lcoe_fcr')
            self.lcoe = 0
            

            if self.desalination:
                self.desal_simulation(self.desalination)
                self.cost(self.desalination)
            
            self.sam_calculation()
            self.print_impParams()
            self.data_free()
      

        elif self.cspModel== 'tcslinear_fresnel' or self.cspModel== 'tcsdirect_steam':
            
            self.ssc = PySSC()
            self.create_ssc_module()
            self.data = self.ssc.data_create()
            self.varListCsp = self.collect_model_variables()
    
            self.set_data(self.varListCsp)
            # execute csp model
            self.module_create_execute(self.cspModel)

            # execute financial model, if any
            if self.financialModel:
                annual_energy = self.ssc.data_get_number(self.data, b'annual_energy')
                self.ssc.data_set_number( self.data, b'annual_energy', annual_energy )
                
                self.module_create_execute(self.financialModel)
                if self.financialModel == 'utilityrate5':
                    self.module_create_execute('cashloan')

            self.P_cond = self.ssc.data_get_array(self.data, b'P_cond') # Pa
            # self.T_cond = self.P_T_conversion(self.P_cond) # oC

            self.T_amb = self.ssc.data_get_number(self.data, b'T_amb_des') # Pa
            self.T_dry = self.ssc.data_get_array(self.data, b'tdry') # Pa            
            with open(self.json_values, "r") as read_file:
                sam_input = json.load(read_file)
            T_ITD = sam_input['T_ITD_des']
            self.T_cond = [i + T_ITD for i in self.T_dry ]
            
            # self.mass_fr_hr = self.ssc.data_get_array(self.data, b'm_dot_st_bd') # kg/hr

            # self.mass_fr_hr = np.dot(self.mass_fr, 3600) # kg/hr
            # if  self.cspModel== 'tcslinear_fresnel':
            #     self.mass_fr_hr = self.ssc.data_get_array(self.data, b'm_dot_field') # kg/hr
            # elif self.cspModel== 'tcsdirect_steam':
            self.mass_fr_hr = self.ssc.data_get_array(self.data, b'm_dot_makeup') # kg/hr
            
            for i in range(len(self.mass_fr_hr)):
                self.mass_fr_hr[i] *= 50
            P_cond = np.dot(self.P_cond, 1e-6)
            
            # if  self.cspModel== 'tcslinear_fresnel':
            #     mass_fr_hr = self.ssc.data_get_array(self.data, b'm_dot_makeup') # kg/hr
            # elif self.cspModel== 'tcsdirect_steam':
            #     self.mass_fr_hr = self.ssc.data_get_array(self.data, b'm_dot_makeup') # kg/hr
            
            # P_cond = np.dot(self.P_cond, 1e-6)
            # self.mass_fr_hr = np.dot(mass_fr_hr, 50)
            
            self.elec_gen = self.ssc.data_get_array(self.data, b'gen')
            self.heat_gen = self.temp_to_heat(T_cond = self.T_cond, mass_fr=self.mass_fr_hr, T_feedin = 25)
            if self.financialModel == 'lcoefcr':
                self.lcoe = self.ssc.data_get_number(self.data, b'lcoe_fcr')
            else:
                self.lcoe = self.ssc.data_get_number(self.data, b'lcoe_real') / 100

            self.lcoh =  self.lcoe * 0.23
            # self.lcoh = self.lcoe * (sum(self.elec_gen) / sum(self.heat_gen))
            # print(self.elec_gen[0:24])
            # print(self.heat_gen[0:24])
            if self.desalination:
                self.desal_simulation(self.desalination)
                self.cost(self.desalination)
            
            self.sam_calculation()
            self.print_impParams()
            self.data_free()
        
        elif self.cspModel== 'tcstrough_physical' or self.cspModel== 'tcsMSLF'  or self.cspModel== 'tcsmolten_salt':
            
            self.ssc = PySSC()
            self.create_ssc_module()
            self.data = self.ssc.data_create()
            self.varListCsp = self.collect_model_variables()
    
            self.set_data(self.varListCsp)
            # execute csp model
            self.module_create_execute(self.cspModel)

            # execute financial model, if any
            if self.financialModel:
                annual_energy = self.ssc.data_get_number(self.data, b'annual_energy')
                self.ssc.data_set_number( self.data, b'annual_energy', annual_energy )
                gen = self.ssc.data_get_array(self.data, b'gen')
                self.ssc.data_set_array( self.data, b'gen', gen )
                self.module_create_execute(self.financialModel)
                if self.financialModel == 'utilityrate5':
                    self.module_create_execute('cashloan')       


            self.T_amb = self.ssc.data_get_number(self.data, b'T_amb_des') # Pa
            self.T_dry = self.ssc.data_get_array(self.data, b'tdry') # Pa            
            with open(self.json_values, "r") as read_file:
                sam_input = json.load(read_file)
            T_ITD = sam_input['T_ITD_des']
            self.T_cond = [i + T_ITD for i in self.T_dry ]
            
            if self.cspModel== 'tcsmolten_salt':
                self.mass_fr_hr = self.ssc.data_get_array(self.data, b'm_dot_water_pc') # kg/s
                for i in range(len(self.mass_fr_hr)):
                    self.mass_fr_hr[i] *= 3600 * 50                   
            else:
                self.mass_fr_hr = self.ssc.data_get_array(self.data, b'm_dot_makeup') # kg/hr
                for i in range(len(self.mass_fr_hr)):
                    self.mass_fr_hr[i] *= 50            
            
            self.elec_gen = self.ssc.data_get_array(self.data, b'gen')
            self.heat_gen = self.temp_to_heat(T_cond = self.T_cond, mass_fr=self.mass_fr_hr, T_feedin = 25)
            if self.financialModel == 'lcoefcr':
                self.lcoe = self.ssc.data_get_number(self.data, b'lcoe_fcr')
            else:
                self.lcoe = self.ssc.data_get_number(self.data, b'lcoe_real') / 100
            self.lcoh =  self.lcoe * 0.27
            
            if self.desalination:
                self.desal_simulation(self.desalination)
                self.cost(self.desalination)            
            
            self.sam_calculation()
            self.print_impParams()
            self.data_free()
        
        costcsv =   self.project_name + '_' +  self.desalination + '_cost_output' + '_' + self.timestamp + '.csv'
        designcsv = self.project_name + '_' +  self.desalination + '_design_output' + '_' + self.timestamp + '.csv'
        simucsv =   self.project_name + '_' +  self.desalination + '_simulation_output' + '_' + self.timestamp + '.csv'
        solarcsv =  self.project_name + '_' +  'Solar_output' + '_' + self.timestamp + '.csv'
        
        csvlist = [designcsv, simucsv, solarcsv, costcsv]
        typelist = ['Design output', 'Simulation output', 'Solar output', 'Cost output']
        
        wb = xlwt.Workbook()
        for i in range(len(csvlist)):
            if self.parametric:
                csvpath = self.samPath / 'CSV parametric_results' / csvlist[i]
            else:
                csvpath = self.samPath / 'CSV results' / csvlist[i]
            fname = typelist[i]

            ws = wb.add_sheet(fname)
            with open(csvpath, 'r') as f:
                reader = csv.reader(f)
                
                for r, row in enumerate(reader):
                    for c, col in enumerate(row):
                        ws.write(r, c, col)
        xlxsname = self.project_name + '_' +  'output' + '_' + self.timestamp + '.xls'
        wb.save(self.samPath / 'XLS results' / xlxsname)
        
    def sam_calculation(self):
        with open(self.json_values, "r") as read_file:
            sam_input = json.load(read_file)
            
        if self.cspModel == 'linear_fresnel_dsg_iph':
            self.actual_aper = sam_input['nLoops'] * sam_input['nModBoil'] *  sam_input['A_aperture'][0][0]
    

    
    def desal_design(self, desal):
        
        with open(self.desal_json_values, "r") as read_file:
            self.desal_values_json = json.load(read_file)

        if desal == 'RO':
            from DesalinationModels.RO_Fixed_Load import RO
            self.RO = RO(nominal_daily_cap_tmp = self.desal_values_json['nominal_daily_cap_tmp'], FeedC_r = self.desal_values_json['FeedC_r'],
                         stage = self.desal_values_json['stage'], has_erd =  1,
                         T  = self.desal_values_json['T'],R1 = self.desal_values_json['R1'],
                         R2 = self.desal_values_json['R2'], R3 = self.desal_values_json['R3'],
                         nERD= self.desal_values_json['nERD'],nBP= self.desal_values_json['nBP'],nHP= self.desal_values_json['nHP'],nFP= self.desal_values_json['nFP'],
                         Qpnom1= self.desal_values_json['Qpnom1'],Am1= self.desal_values_json['Am1'],Pmax1= self.desal_values_json['Pmax1'],Ptest1= self.desal_values_json['Ptest1'],
                         Ctest1= self.desal_values_json['Ctest1'],SR1= self.desal_values_json['SR1'],Rt1= self.desal_values_json['Rt1'],Pdropmax= self.desal_values_json['Pdropmax'],
                         Pfp= self.desal_values_json['Pfp'],maxQf= self.desal_values_json['maxQf'])
            self.design_output = self.RO.RODesign()


        elif desal == 'VAGMD':
            from DesalinationModels.VAGMD_PSA import VAGMD_PSA
            self.VAGMD = VAGMD_PSA(module = self.desal_values_json['module'], TEI_r = self.desal_values_json['TEI_r'],TCI_r  = self.desal_values_json['TCI_r'],FFR_r = self.desal_values_json['FFR_r'],FeedC_r = self.desal_values_json['FeedC_r'],Capacity= self.desal_values_json['Capacity'],Fossil_f= self.desal_values_json['Fossil_f'])
            self.VAGMD.design()
            self.P_req, self.design_output = self.VAGMD.opt()

        elif desal == 'MDB':
            from DesalinationModels.VAGMD_batch.VAGMD_batch import VAGMD_batch
            self.MDB = VAGMD_batch(module = self.desal_values_json['module'], TEI_r = self.desal_values_json['TEI_r'],TCI_r  = self.desal_values_json['TCI_r'],FFR_r = self.desal_values_json['FFR_r'],FeedC_r = self.desal_values_json['FeedC_r'],Capacity= self.desal_values_json['Capacity'],Fossil_f= self.desal_values_json['Fossil_f'], V0 =self.desal_values_json['V0'], RR = self.desal_values_json['RR'] )
            self.design_output =  self.MDB.design() 
            self.P_req = self.MDB.P_req

        elif desal == 'ABS':
            from DesalinationModels.ABS import ABS
            self.ABS = ABS(Capacity = self.desal_values_json['Capacity'],Xf =self.desal_values_json['FeedC_r'], RR =self.desal_values_json['RR'], Tin = self.desal_values_json['Tin'] ,Ts = self.desal_values_json['Ts'], Nef  = self.desal_values_json['Nef'], Fossil_f= self.desal_values_json['Fossil_f'], Tcond  = self.desal_values_json['Tcond'], pump_type= self.desal_values_json['pump_type'])
            self.design_output = self.ABS.design()        
            self.P_req = self.ABS.P_req
        
        elif desal == 'LTMED':
            from DesalinationModels.LT_MED_General import lt_med_general
            self.LTMED = lt_med_general(Capacity = self.desal_values_json['Capacity'],Xf =self.desal_values_json['FeedC_r'], RR =self.desal_values_json['RR'], Tin = self.desal_values_json['Tin'] ,Ts = self.desal_values_json['Ts'], Nef  = self.desal_values_json['Nef'], Fossil_f= self.desal_values_json['Fossil_f'])
            self.design_output = self.LTMED.design()
            self.P_req = self.LTMED.P_req
            
        elif desal == 'MEDTVC':
            from DesalinationModels.MED_TVC_General import med_tvc_general
            self.MEDTVC = med_tvc_general(Capacity = self.desal_values_json['Capacity'],Xf =self.desal_values_json['FeedC_r'], RR =self.desal_values_json['rr']/100,  Nef =self.desal_values_json['nef'], Tin =self.desal_values_json['tin'], Pm =self.desal_values_json['pm'], Fossil_f = self.desal_values_json['Fossil_f'] )
            self.design_output = self.MEDTVC.design()  
            self.P_req = self.MEDTVC.P_req
            
        elif desal == 'FO':
            from DesalinationModels.FO_Generalized import FO_generalized
            self.FO = FO_generalized(Mprod = self.desal_values_json['Mprod'],FeedC_r =self.desal_values_json['FeedC_r'], T_sw =self.desal_values_json['T_sw'], NF_rr = self.desal_values_json['NF_rr'] ,RO_rr = self.desal_values_json['RO_rr'], A  = self.desal_values_json['A'], Fossil_f= self.desal_values_json['Fossil_f'], p_margin= self.desal_values_json['p_margin'], r= self.desal_values_json['r'], hm= self.desal_values_json['hm'], T_DS= self.desal_values_json['T_DS'], dT_sw_sup= self.desal_values_json['dT_sw_sup'], dT_prod= self.desal_values_json['dT_prod'], T_separator= self.desal_values_json['T_separator'], T_loss_sep= self.desal_values_json['T_loss_sep'], dT_hotin= self.desal_values_json['dT_hotin'], dT_hotout= self.desal_values_json['dT_hotout'], T_app_C= self.desal_values_json['T_app_C'], T_app_1B= self.desal_values_json['T_app_1B'], T_app_2B= self.desal_values_json['T_app_2B'])
            self.design_output = self.FO.FO_design()
            self.P_req = self.FO.P_req            
            
        elif desal == 'OARO':
            from DesalinationModels.OARO import OARO
            self.OARO = OARO(FeedC_r =self.desal_values_json['FeedC_r'], Capacity =self.desal_values_json['Capacity'], rr =self.desal_values_json['rr'])
            self.design_output, self.costout = self.OARO.design()

        elif desal == 'LSRRO':
            from DesalinationModels.LSRRO import LSRRO
            self.LSRRO = LSRRO(FeedC_r =self.desal_values_json['FeedC_r'], Capacity =self.desal_values_json['Capacity'], rr =self.desal_values_json['rr'])
            self.design_output, self.costout = self.LSRRO.design()
        elif desal == 'COMRO':
            from DesalinationModels.COMRO import COMRO
            self.COMRO = COMRO(FeedC_r =self.desal_values_json['FeedC_r'], Capacity =self.desal_values_json['Capacity'], rr =self.desal_values_json['rr'])
            self.design_output, self.costout = self.COMRO.design()
            
        elif desal == 'RO_FO':
            from DesalinationModels.RO_FO import RO_FO
            self.RO_FO = RO_FO(capacity = self.desal_values_json['capacity'], RO_rr = self.desal_values_json['RO_rr'], FO_rr = self.desal_values_json['FO_rr'],
                               salinity = self.desal_values_json['FeedC_r'], T_sw = self.desal_values_json['T_sw'], 
                               nERD = self.desal_values_json['nERD'],nBP = self.desal_values_json['nBP'],nHP = self.desal_values_json['nHP'],
                               nFP = self.desal_values_json['nFP'], stage = 1, has_erd =  1, 
                         Qpnom1= self.desal_values_json['Qpnom1'],Am1= self.desal_values_json['Am1'],Pmax1= self.desal_values_json['Pmax1'],Ptest1= self.desal_values_json['Ptest1'],
                         Ctest1= self.desal_values_json['Ctest1'],SR1= self.desal_values_json['SR1'],Rt1= self.desal_values_json['Rt1'],Pdropmax= self.desal_values_json['Pdropmax'],
                         Pfp= self.desal_values_json['Pfp'],maxQf= self.desal_values_json['maxQf'])
            self.design_output = self.RO_FO.design()
            self.P_req = self.RO_FO.P_req
            
        elif desal == 'RO_MDB':
            from DesalinationModels.RO_MDB import RO_MDB
            self.RO_MDB = RO_MDB(capacity = self.desal_values_json['capacity'], RO_rr = self.desal_values_json['RO_rr'], 
                                 salinity = self.desal_values_json['FeedC_r'], T_sw = self.desal_values_json['T_sw'], 
                               nERD = self.desal_values_json['nERD'],nBP = self.desal_values_json['nBP'],nHP = self.desal_values_json['nHP'],
                               nFP = self.desal_values_json['nFP'],  has_erd =  1, 
                               Qpnom1= self.desal_values_json['Qpnom1'],Am1= self.desal_values_json['Am1'],Pmax1= self.desal_values_json['Pmax1'],Ptest1= self.desal_values_json['Ptest1'],
                               Ctest1= self.desal_values_json['Ctest1'],SR1= self.desal_values_json['SR1'],Rt1= self.desal_values_json['Rt1'],Pdropmax= self.desal_values_json['Pdropmax'],
                               Pfp= self.desal_values_json['Pfp'],maxQf= self.desal_values_json['maxQf'],
                               module = self.desal_values_json['module'],TCI_r = self.desal_values_json['TCI_r'],
                               TEI_r = self.desal_values_json['TEI_r'],FFR_r = self.desal_values_json['FFR_r'],
                               V0 = self.desal_values_json['V0'],RR = self.desal_values_json['RR'],
                               j = self.desal_values_json['j'], TCoolIn = self.desal_values_json['TCoolIn'],
                               Ttank = self.desal_values_json['Ttank'], dt = self.desal_values_json['dt'])
            self.design_output = self.RO_MDB.design()  
            self.P_req = self.RO_MDB.P_req
        
        elif desal == 'Generic':
            from DesalinationModels.generic import generic
            self.Generic = generic(Capacity = self.desal_values_json['Capacity'], FeedC_r = self.desal_values_json['FeedC_r'], RR = self.desal_values_json['RR'], 
                                   STEC = self.desal_values_json['STEC'], SEC = self.desal_values_json['SEC'], Fossil_f =self.desal_values_json['Fossil_f'])
            self.design_output = self.Generic.design()
            self.P_req = self.Generic.P_req
        
        # Write design output to json
        filename = desal + '_design_output' + self.timestamp + '.json'

        if self.parametric:
            design_json_outfile = self.samPath / 'parametric_results' / filename 

        else:
            design_json_outfile =  self.samPath / 'results' / filename

        with open(design_json_outfile, 'w') as outfile:
            json.dump(self.design_output, outfile)
        
        
        with open(design_json_outfile) as json_file: 
            data = json.load(json_file)              
        
        
    def desal_simulation(self, desal):
        with open(self.desal_json_values, "r") as read_file:
            self.desal_values_json = json.load(read_file)
        if desal == 'RO':
            from DesalinationModels.RO_Fixed_Load import RO
            self.RO = RO(nominal_daily_cap_tmp = self.desal_values_json['nominal_daily_cap_tmp'], FeedC_r = self.desal_values_json['FeedC_r'],
                         stage = self.desal_values_json['stage'], has_erd =  1,
                         T  = self.desal_values_json['T'],R1 = self.desal_values_json['R1'],
                         R2 = self.desal_values_json['R2'], R3 = self.desal_values_json['R3'],
                         nERD= self.desal_values_json['nERD'],nBP= self.desal_values_json['nBP'],nHP= self.desal_values_json['nHP'],nFP= self.desal_values_json['nFP'],
                         Qpnom1= self.desal_values_json['Qpnom1'],Am1= self.desal_values_json['Am1'],Pmax1= self.desal_values_json['Pmax1'],Ptest1= self.desal_values_json['Ptest1'],
                         Ctest1= self.desal_values_json['Ctest1'],SR1= self.desal_values_json['SR1'],Rt1= self.desal_values_json['Rt1'],Pdropmax= self.desal_values_json['Pdropmax'],
                         Pfp= self.desal_values_json['Pfp'],maxQf= self.desal_values_json['maxQf'])
            self.RO.RODesign()
            self.simu_output = self.RO.simulation(gen = self.elec_gen, storage = self.desal_values_json['storage_hour'])

            
        elif desal == 'VAGMD':
            from DesalinationModels.VAGMD_PSA import VAGMD_PSA
            self.VAGMD = VAGMD_PSA(module = self.desal_values_json['module'], TEI_r = self.desal_values_json['TEI_r'],TCI_r  = self.desal_values_json['TCI_r'],FFR_r = self.desal_values_json['FFR_r'],FeedC_r = self.desal_values_json['FeedC_r'],Capacity= self.desal_values_json['Capacity'],Fossil_f= self.desal_values_json['Fossil_f'])
            self.VAGMD.design()
            self.P_req, self.design_output = self.VAGMD.opt()
            
            self.simu_output = self.VAGMD.simulation(gen = self.heat_gen, storage = self.desal_values_json['storage_hour'])

        elif desal == 'MDB':
            from DesalinationModels.VAGMD_batch.VAGMD_batch import VAGMD_batch
            self.MDB = VAGMD_batch(module = self.desal_values_json['module'], TEI_r = self.desal_values_json['TEI_r'],TCI_r  = self.desal_values_json['TCI_r'],FFR_r = self.desal_values_json['FFR_r'],FeedC_r = self.desal_values_json['FeedC_r'],Capacity= self.desal_values_json['Capacity'],Fossil_f= self.desal_values_json['Fossil_f'], V0 =self.desal_values_json['V0'], RR = self.desal_values_json['RR'] )
            self.design_output = self.MDB.design()  

            self.simu_output = self.MDB.simulation(gen = self.heat_gen, storage = self.desal_values_json['storage_hour'])
        
        elif desal == 'LTMED':
            from DesalinationModels.LT_MED_General import lt_med_general
            self.LTMED = lt_med_general(Capacity = self.desal_values_json['Capacity'],Xf =self.desal_values_json['FeedC_r'], RR =self.desal_values_json['RR'], Tin = self.desal_values_json['Tin'] ,Ts = self.desal_values_json['Ts'], Nef  = self.desal_values_json['Nef'], Fossil_f= self.desal_values_json['Fossil_f'])
            self.design_output = self.LTMED.design()

            self.simu_output = self.LTMED.simulation(gen = self.heat_gen, storage = self.desal_values_json['storage_hour'])

        elif desal == 'ABS':
            from DesalinationModels.ABS import ABS
            self.ABS = ABS(Capacity = self.desal_values_json['Capacity'],Xf =self.desal_values_json['FeedC_r'], RR =self.desal_values_json['RR'], Tin = self.desal_values_json['Tin'] ,Ts = self.desal_values_json['Ts'], Nef  = self.desal_values_json['Nef'], Fossil_f= self.desal_values_json['Fossil_f'], Tcond  = self.desal_values_json['Tcond'], pump_type= self.desal_values_json['pump_type'])
            self.design_output = self.ABS.design() 

            self.simu_output = self.ABS.simulation(gen = self.heat_gen, storage = self.desal_values_json['storage_hour'])
            
        elif desal == 'MEDTVC':
            from DesalinationModels.MED_TVC_General import med_tvc_general
            self.MEDTVC = med_tvc_general(Capacity = self.desal_values_json['Capacity'],Xf =self.desal_values_json['FeedC_r'], RR =self.desal_values_json['rr']/100,  Nef =self.desal_values_json['nef'], Tin =self.desal_values_json['tin'], Pm =self.desal_values_json['pm'], Fossil_f = self.desal_values_json['Fossil_f'] )
            self.design_output = self.MEDTVC.design()  
         
            self.simu_output = self.MEDTVC.simulation(gen = self.heat_gen, storage = self.desal_values_json['storage_hour'])

        
            # solar_loss = self.simu_output[6]['Value']
            # np.savetxt("gen.csv",solar_loss,delimiter=',')
            
        elif desal == 'FO':
            from DesalinationModels.FO_Generalized import FO_generalized
            self.FO = FO_generalized(Mprod = self.desal_values_json['Mprod'],FeedC_r =self.desal_values_json['FeedC_r'], T_sw =self.desal_values_json['T_sw'], NF_rr = self.desal_values_json['NF_rr'] ,RO_rr = self.desal_values_json['RO_rr'], A  = self.desal_values_json['A'], Fossil_f= self.desal_values_json['Fossil_f'], p_margin= self.desal_values_json['p_margin'], r= self.desal_values_json['r'], hm= self.desal_values_json['hm'], T_DS= self.desal_values_json['T_DS'], dT_sw_sup= self.desal_values_json['dT_sw_sup'], dT_prod= self.desal_values_json['dT_prod'], T_separator= self.desal_values_json['T_separator'], T_loss_sep= self.desal_values_json['T_loss_sep'], dT_hotin= self.desal_values_json['dT_hotin'], dT_hotout= self.desal_values_json['dT_hotout'], T_app_C= self.desal_values_json['T_app_C'], T_app_1B= self.desal_values_json['T_app_1B'], T_app_2B= self.desal_values_json['T_app_2B'])
            self.design_output = self.FO.FO_design()

            self.simu_output = self.FO.FO_simulation(gen = self.heat_gen, storage = self.desal_values_json['storage_hour'])
        
        elif desal == 'OARO':
            from DesalinationModels.OARO import OARO
            self.OARO = OARO(FeedC_r =self.desal_values_json['FeedC_r'], Capacity =self.desal_values_json['Capacity'], rr =self.desal_values_json['rr'])
            self.design_output, self.costout =self.OARO.design()    

            self.simu_output = self.OARO.simulation(gen = self.elec_gen, storage = 0)
        
        elif desal == 'LSRRO':
            from DesalinationModels.LSRRO import LSRRO
            self.LSRRO = LSRRO(FeedC_r =self.desal_values_json['FeedC_r'], Capacity =self.desal_values_json['Capacity'], rr =self.desal_values_json['rr'])
            self.design_output, self.costout = self.LSRRO.design()    
            self.simu_output = self.LSRRO.simulation(gen = self.elec_gen, storage = 0)
            
        elif desal == 'COMRO':
            from DesalinationModels.COMRO import COMRO
            self.COMRO = COMRO(FeedC_r =self.desal_values_json['FeedC_r'], Capacity =self.desal_values_json['Capacity'],rr =self.desal_values_json['rr'])
            self.design_output, self.costout = self.COMRO.design()               
            self.simu_output = self.COMRO.simulation(gen = self.elec_gen, storage = 0)
        
        elif desal == 'RO_FO':
            from DesalinationModels.RO_FO import RO_FO
            self.RO_FO = RO_FO(capacity = self.desal_values_json['capacity'], RO_rr = self.desal_values_json['RO_rr'], FO_rr = self.desal_values_json['FO_rr'],
                               salinity = self.desal_values_json['FeedC_r'], T_sw = self.desal_values_json['T_sw'], 
                               nERD = self.desal_values_json['nERD'],nBP = self.desal_values_json['nBP'],nHP = self.desal_values_json['nHP'],
                               nFP = self.desal_values_json['nFP'], stage = 1, has_erd =  1, 
                         Qpnom1= self.desal_values_json['Qpnom1'],Am1= self.desal_values_json['Am1'],Pmax1= self.desal_values_json['Pmax1'],Ptest1= self.desal_values_json['Ptest1'],
                         Ctest1= self.desal_values_json['Ctest1'],SR1= self.desal_values_json['SR1'],Rt1= self.desal_values_json['Rt1'],Pdropmax= self.desal_values_json['Pdropmax'],
                         Pfp= self.desal_values_json['Pfp'],maxQf= self.desal_values_json['maxQf'])
            self.design_output = self.RO_FO.design()
            if self.cspModel=='pvsamv1':
                self.simu_output = self.RO_FO.simulation(elec_gen = self.elec_gen, thermal_gen = [0],  solar_type = 'pv', storage = 0)
            elif self.cspModel == 'linear_fresnel_dsg_iph' or self.cspModel == 'trough_physical_process_heat' or self.cspModel == 'SC_FPC' or self.cspModel == 'SC_ETC':
                self.simu_output = self.RO_FO.simulation(elec_gen = [0], thermal_gen = self.heat_gen, solar_type = 'thermal', storage = 0)
            else:
                self.simu_output = self.RO_FO.simulation(elec_gen = self.elec_gen, thermal_gen = self.heat_gen, solar_type = 'csp', storage = 0)
                
        elif desal == 'RO_MDB':
            from DesalinationModels.RO_MDB import RO_MDB
            self.RO_MDB = RO_MDB(capacity = self.desal_values_json['capacity'], RO_rr = self.desal_values_json['RO_rr'], 
                                 salinity = self.desal_values_json['FeedC_r'], T_sw = self.desal_values_json['T_sw'], 
                               nERD = self.desal_values_json['nERD'],nBP = self.desal_values_json['nBP'],nHP = self.desal_values_json['nHP'],
                               nFP = self.desal_values_json['nFP'],  has_erd =  1, 
                               Qpnom1= self.desal_values_json['Qpnom1'],Am1= self.desal_values_json['Am1'],Pmax1= self.desal_values_json['Pmax1'],Ptest1= self.desal_values_json['Ptest1'],
                               Ctest1= self.desal_values_json['Ctest1'],SR1= self.desal_values_json['SR1'],Rt1= self.desal_values_json['Rt1'],Pdropmax= self.desal_values_json['Pdropmax'],
                               Pfp= self.desal_values_json['Pfp'],maxQf= self.desal_values_json['maxQf'],
                               module = self.desal_values_json['module'],TCI_r = self.desal_values_json['TCI_r'],
                               TEI_r = self.desal_values_json['TEI_r'],FFR_r = self.desal_values_json['FFR_r'],
                               V0 = self.desal_values_json['V0'],RR = self.desal_values_json['RR'],
                               j = self.desal_values_json['j'], TCoolIn = self.desal_values_json['TCoolIn'],
                               Ttank = self.desal_values_json['Ttank'], dt = self.desal_values_json['dt'])
            self.design_output = self.RO_MDB.design() 
            if self.cspModel=='pvsamv1':
                self.simu_output = self.RO_MDB.simulation(elec_gen = self.elec_gen, thermal_gen = [0],  solar_type = 'pv', storage = 0)
            elif self.cspModel == 'linear_fresnel_dsg_iph' or self.cspModel == 'trough_physical_process_heat' or self.cspModel == 'SC_FPC' or self.cspModel == 'SC_ETC':
                self.simu_output = self.RO_MDB.simulation(elec_gen = [0], thermal_gen = self.heat_gen, solar_type = 'thermal', storage = 0)
            else:
                self.simu_output = self.RO_MDB.simulation(elec_gen = self.elec_gen, thermal_gen = self.heat_gen, solar_type = 'csp', storage = 0)    
                
        elif desal == 'Generic':
            from DesalinationModels.generic import generic
            self.Generic = generic(Capacity = self.desal_values_json['Capacity'], FeedC_r = self.desal_values_json['FeedC_r'], RR = self.desal_values_json['RR'], 
                                   STEC = self.desal_values_json['STEC'], SEC = self.desal_values_json['SEC'], Fossil_f =self.desal_values_json['Fossil_f'])
            self.design_output = self.Generic.design()

            self.simu_output = self.Generic.simulation(gen = self.heat_gen, storage = self.desal_values_json['storage_hour'])

        # Write design output to csv
        filename = desal + '_design_output' + self.timestamp + '.json'
        csvname  = self.project_name + '_' + desal + '_design_output' + '_' + self.timestamp + '.csv'
        if self.parametric:
            design_json_outfile = self.samPath / 'parametric_results' / filename 
            design_csv_outfile = self.samPath / 'CSV parametric_results' / csvname 
        else:
            design_json_outfile =  self.samPath / 'results' / filename
            design_csv_outfile =  self.samPath / 'CSV results' / csvname
        with open(design_json_outfile, 'w') as outfile:
            json.dump(self.design_output, outfile)
        
        
        with open(design_json_outfile) as json_file: 
            data = json.load(json_file)         
        # now we will open a file for writing 
        data_file = open(design_csv_outfile, 'w', newline='') 
        # create the csv writer object 
        csv_writer = csv.writer(data_file)
        map_json = cfg.map_json
        with open(map_json, "r") as read_file:
            map_data = json.load(read_file)   
        csv_writer.writerow(["Location", map_data['county'] + '  ' + map_data['state']])
        csv_writer.writerow(["Desal technology", cfg.Desal[self.desalination]])
        csv_writer.writerow(["Solar technology", cfg.Solar[self.cspModel]]) 
        csv_writer.writerow([])        
        
        count = 0
          
        for i in data: 
            if count == 0: 
          
                # Writing headers of CSV file 
                header = i.keys() 
                csv_writer.writerow(header) 
                count += 1
          
            # Writing data of CSV file 
            csv_writer.writerow(i.values()) 
          
        data_file.close()   

        # Write simulation output to csv
        filename = desal + '_simulation_output' + self.timestamp + '.json'
        csvname = self.project_name + '_' + desal + '_simulation_output' + '_' + self.timestamp + '.csv'  
        
        if self.parametric:
            simulation_json_outfile = self.samPath / 'parametric_results' / filename  
            simulation_csv_outfile = self.samPath / 'CSV parametric_results' / csvname
        else:
            simulation_json_outfile =  self.samPath / 'results' / filename
            simulation_csv_outfile = self.samPath / 'CSV results' /csvname
        with open(simulation_json_outfile, 'w') as outfile:
            json.dump(self.simu_output, outfile)
            
        with open(simulation_json_outfile) as json_file: 
            data = json.load(json_file)         
        # now we will open a file for writing 
        data_file = open(simulation_csv_outfile, 'w' ,newline='') 
        # create the csv writer object 
        csv_writer = csv.writer(data_file) 
        
        map_json = cfg.map_json
        with open(map_json, "r") as read_file:
            map_data = json.load(read_file)   
        csv_writer.writerow(["Location", map_data['county'] + '  ' + map_data['state']])
        csv_writer.writerow(["Desal technology", cfg.Desal[self.desalination]])
        csv_writer.writerow(["Solar technology", cfg.Solar[self.cspModel]]) 
        csv_writer.writerow([])
        count = 0
        time_series = []
        for i in data: 
            if count == 0: 
                # Writing headers of CSV file 
                header = i.keys() 
                csv_writer.writerow(header) 
                count += 1
          
            # Writing data of CSV file 
            if type(i["Value"]) != list:
                csv_writer.writerow(i.values()) 
            else:
                if i["Name"] != "Monthly water production":
                    time_series.append(i)
        
        header = []
        for i in time_series:
            header.append(i["Name"] + " (" + i["Unit"] + ")")

        csv_writer.writerow([])
        csv_writer.writerow(["Hour"] + header)
        for i in range(len(time_series[0]["Value"])):
            try:
                csv_writer.writerow([i] + [j["Value"][i] for j in time_series])
            except:
                continue
          
        data_file.close()          


    def cost(self, desal):
        with open(self.cost_json_values, "r") as read_file:
            self.cost_values_json = json.load(read_file)   


        if desal == 'RO':
            from DesalinationModels.RO_cost import RO_cost
            passes = self.desal_values_json['stage']
            if passes == 1:
                Capacity = [self.RO.case.nominal_daily_cap_tmp]
                unit_capex = [self.cost_values_json['unit_capex_main']]
            elif passes == 2:
                Capacity = [self.RO.case.nominal_daily_cap_tmp, self.RO.case2.nominal_daily_cap_tmp]
                unit_capex = [self.cost_values_json['unit_capex_main'], self.cost_values_json['unit_capex_passes'] ]
            elif passes == 3:
                Capacity = [self.RO.case.nominal_daily_cap_tmp, self.RO.case2.nominal_daily_cap_tmp, self.RO.case3.nominal_daily_cap_tmp]
                unit_capex = [self.cost_values_json['unit_capex_main'], self.cost_values_json['unit_capex_passes'] , self.cost_values_json['unit_capex_passes'] ]
            
            self.LCOW = RO_cost(Capacity = Capacity, Prod = sum(self.simu_output[0]['Value']), fuel_usage = self.simu_output[7]['Value'], 
                                Area =  self.desal_values_json['Am1'], yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], 
                                num_modules = self.RO.total_num_modules, solar_coe = self.cost_values_json['solar_coe'], IX_cost = self.cost_values_json['IX_cost'],
                                chem_cost =  self.cost_values_json['chem_cost'], labor_cost =  self.cost_values_json['labor_cost'], rep_rate =  self.cost_values_json['rep_rate'],
                                unit_capex =  unit_capex, sec =  self.RO.SEC ,disposal_cost =  self.cost_values_json['disposal_cost'], sam_coe = self.lcoe, cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.RO.storage_cap )

            self.cost_output = self.LCOW.lcow()

   
        elif desal == 'VAGMD':
            from DesalinationModels.VAGMD_cost import VAGMD_cost

            self.LCOW = VAGMD_cost(Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], Area = self.VAGMD.Area, Pflux = self.VAGMD.PFlux, TCO = self.VAGMD.TCO, TEI = self.VAGMD.TEI_r, FFR = self.VAGMD.FFR_r, th_module = self.VAGMD.ThPower, STEC = self.VAGMD.STEC, SEEC = self.cost_values_json['SEEC'], downtime = self.cost_values_json['downtime'],
                                   MD_membrane = self.cost_values_json['MD_membrane'], MD_module = self.cost_values_json['MD_module'], MD_module_capacity = self.cost_values_json['MD_module_capacity'], HX = self.cost_values_json['HX'], endplates = self.cost_values_json['endplates'], endplates_capacity = self.cost_values_json['endplates_capacity'], other_capacity = self.cost_values_json['other_capacity'], heat_cool = self.cost_values_json['heat_cool'], heat_cool_capacity = self.cost_values_json['heat_cool_capacity'], h_r = self.cost_values_json['h_r'], h_r_capacity = self.cost_values_json['h_r_capacity'], tank = self.cost_values_json['tank'], tank_capacity = self.cost_values_json['tank_capacity'], pump = self.cost_values_json['pump'], pump_capacity = self.cost_values_json['pump_capacity'], other = self.cost_values_json['other'], 
                                   yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], coh =  self.cost_values_json['coh'], solar_coh =  self.cost_values_json['solar_coh'], sam_coh = self.lcoh, solar_inlet =  self.cost_values_json['solar_inlet'], solar_outlet =  self.cost_values_json['solar_outlet'], HX_eff =  self.cost_values_json['HX_eff'], cost_module_re =  self.cost_values_json['cost_module_re'] , cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.VAGMD.storage_cap )

            self.cost_output = self.LCOW.lcow()

        elif desal == 'MDB':
            
            from DesalinationModels.MDB_cost import MDB_cost

            self.LCOW = MDB_cost(Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], Area = self.MDB.Area,
                                 Pflux = self.MDB.PFlux_avg, RR = self.MDB.R[-1], downtime = self.cost_values_json['downtime'],
                                 TCO = sum(self.MDB.TCO) / len(self.MDB.TCO), TEI = self.MDB.TEI_r, FFR = self.MDB.FFR_r, th_module = sum(self.MDB.ThPower)/len(self.MDB.ThPower),
                                 STEC = self.MDB.STEC[-1], SEEC = self.MDB.SEEC[-1],  MD_membrane = self.cost_values_json['MD_membrane'],
                                 MD_module = self.cost_values_json['MD_module'], MD_module_capacity = self.cost_values_json['MD_module_capacity'], 
                                 HX = self.cost_values_json['HX'], endplates = self.cost_values_json['endplates'], endplates_capacity = self.cost_values_json['endplates_capacity'], 
                                 other_capacity = self.cost_values_json['other_capacity'], heat_cool = self.cost_values_json['heat_cool'], 
                                 heat_cool_capacity = self.cost_values_json['heat_cool_capacity'], h_r = self.cost_values_json['h_r'], 
                                 h_r_capacity = self.cost_values_json['h_r_capacity'], tank = self.cost_values_json['tank'], 
                                 tank_capacity = self.cost_values_json['tank_capacity'], pump = self.cost_values_json['pump'], 
                                 pump_capacity = self.cost_values_json['pump_capacity'], other = self.cost_values_json['other'], 
                                 yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], 
                                 coh =  self.cost_values_json['coh'], solar_coh =  self.cost_values_json['solar_coh'], sam_coh = self.lcoh, solar_inlet =  self.cost_values_json['solar_inlet'], 
                                 solar_outlet =  self.cost_values_json['solar_outlet'], HX_eff =  self.cost_values_json['HX_eff'], 
                                 cost_module_re =  self.cost_values_json['cost_module_re'] , cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.MDB.storage_cap )

            self.cost_output = self.LCOW.lcow()
        
        elif desal == 'LTMED':
            from DesalinationModels.LTMED_cost import LTMED_cost
            self.LCOW = LTMED_cost(f_HEX = self.cost_values_json['f_HEX'], downtime = self.cost_values_json['downtime'],
                                    HEX_area = self.LTMED.sA,
                                   Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], SEEC = self.cost_values_json['SEEC'], STEC = self.LTMED.STEC,
                                    Chemicals = self.cost_values_json['Chemicals'], Labor = self.cost_values_json['Labor'], Discharge = self.cost_values_json['Discharge'], Maintenance = self.cost_values_json['Maintenance'],  Miscellaneous = self.cost_values_json['Miscellaneous'],
                                   yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], solar_coh =  self.cost_values_json['solar_coh'], coh =  self.cost_values_json['coh'], sam_coh = self.lcoh, cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.LTMED.storage_cap)
            self.cost_output = self.LCOW.lcow()
            
        elif desal == 'ABS':
            from DesalinationModels.ABS_cost import ABS_cost
            self.LCOW = ABS_cost(f_HEX = self.cost_values_json['f_HEX'], P_req = self.P_req,  downtime = self.cost_values_json['downtime'],
                                   # HEX_area = self.LTMED.system.sum_A,
                                   Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], SEEC = self.cost_values_json['SEEC'], STEC = self.ABS.STEC,
                                    Chemicals = self.cost_values_json['Chemicals'], Labor = self.cost_values_json['Labor'], Discharge = self.cost_values_json['Discharge'], Maintenance = self.cost_values_json['Maintenance'],  Miscellaneous = self.cost_values_json['Miscellaneous'],
                                   yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'],  solar_coh =  self.cost_values_json['solar_coh'], coh =  self.cost_values_json['coh'], sam_coh = self.lcoh, cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.ABS.storage_cap)
            self.cost_output = self.LCOW.lcow()  
            
        elif desal == 'MEDTVC':
            from DesalinationModels.MEDTVC_cost import MEDTVC_cost
            self.LCOW = MEDTVC_cost(f_HEX = self.cost_values_json['f_HEX'], downtime = self.cost_values_json['downtime'],
                                    HEX_area = self.MEDTVC.sA,
                                   Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], SEEC = self.cost_values_json['SEEC'], STEC = self.MEDTVC.STEC,
                                    Chemicals = self.cost_values_json['Chemicals'], Labor = self.cost_values_json['Labor'], Discharge = self.cost_values_json['Discharge'], Maintenance = self.cost_values_json['Maintenance'],  Miscellaneous = self.cost_values_json['Miscellaneous'],
                                   yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'],  solar_coh =  self.cost_values_json['solar_coh'], coh =  self.cost_values_json['coh'], sam_coh = self.lcoh, cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.MEDTVC.storage_cap)
            self.cost_output = self.LCOW.lcow()
            
        elif desal == 'FO':
            from DesalinationModels.FO_cost import FO_cost
            self.LCOW = FO_cost(    Capacity = self.desal_values_json['Mprod'], downtime = self.cost_values_json['downtime'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], SEEC = self.cost_values_json['SEEC'], STEC = self.cost_values_json['STEC'], labor = self.cost_values_json['labor'], 
                                    unit_capex = self.cost_values_json['unit_capex'], chem_cost = self.cost_values_json['chem_cost'], goods_cost = self.cost_values_json['goods_cost'], 
                                    Cap_membrane = self.cost_values_json['Cap_membrane'], Cap_HXs = self.cost_values_json['Cap_HXs'], Cap_construct = self.cost_values_json['Cap_construct'], Cap_DS = self.cost_values_json['Cap_DS'],
                                    Cap_coalescers = self.cost_values_json['Cap_coalescers'], Cap_structural = self.cost_values_json['Cap_structural'], Cap_polishing = self.cost_values_json['Cap_polishing'], Cap_pipes = self.cost_values_json['Cap_pipes'],
                                    Cap_filtration = self.cost_values_json['Cap_filtration'], Cap_electrical = self.cost_values_json['Cap_electrical'], Cap_pumps = self.cost_values_json['Cap_pumps'], Cap_instrumentation = self.cost_values_json['Cap_instrumentation'],
                                    Cap_valves = self.cost_values_json['Cap_valves'], Cap_CIP = self.cost_values_json['Cap_CIP'], Cap_tanks = self.cost_values_json['Cap_tanks'], Cap_pretreatment = self.cost_values_json['Cap_pretreatment'],
                                    yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], coh =  self.cost_values_json['coh'], solar_coh =  self.cost_values_json['solar_coh'], sam_coh = self.lcoh, cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.FO.storage_cap)
            self.cost_output = self.LCOW.lcow()

        elif desal == 'OARO':
            from DesalinationModels.OARO_cost import OARO_cost
            print('lcoe', self.lcoe)
            self.LCOW = OARO_cost(Capacity = self.desal_values_json['Capacity'], Prod = (self.simu_output[4]['Value']), fuel_usage = self.simu_output[7]['Value'], oaro_area  = self.costout['oaro_area'], ro_area  = self.costout['ro_area'],  yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], 
                                downtime =  self.cost_values_json['downtime'],chem_cost =  self.cost_values_json['chem_cost'], labor_cost =  self.cost_values_json['labor_cost'], rep_rate =  self.cost_values_json['rep_rate'], pumpcost = self.costout['pumpcost'], erdcost  = self.costout['erdcost'], ro_cost  =  self.cost_values_json['ro_cost'], oaro_cost  =  self.cost_values_json['oaro_cost'],
                                solar_coe = self.cost_values_json['solar_coe'], sec =  self.costout['sec'], sam_coe = self.lcoe, practical_inv_factor = self.cost_values_json['practical_inv_factor'], storage_cap = self.OARO.storage_cap )
        
            self.cost_output = self.LCOW.lcow()
            
        elif desal == 'LSRRO':
            from DesalinationModels.LSRRO_cost import LSRRO_cost

            self.LCOW = LSRRO_cost(Capacity = self.desal_values_json['Capacity'], Prod = (self.simu_output[4]['Value']), fuel_usage = self.simu_output[7]['Value'], oaro_area  = self.costout['oaro_area'], ro_area  = self.costout['ro_area'],  yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], 
                                downtime =  self.cost_values_json['downtime'],chem_cost =  self.cost_values_json['chem_cost'], labor_cost =  self.cost_values_json['labor_cost'], rep_rate =  self.cost_values_json['rep_rate'], pumpcost = self.costout['pumpcost'], erdcost  = self.costout['erdcost'], ro_cost  =  self.cost_values_json['ro_cost'], oaro_cost  =  self.cost_values_json['oaro_cost'],
                                sec =  self.costout['sec'], sam_coe = self.cost_values_json['sam_coe'], practical_inv_factor = self.cost_values_json['practical_inv_factor'], storage_cap = self.LSRRO.storage_cap )
        
            self.cost_output = self.LCOW.lcow()
        elif desal == 'COMRO':
            from DesalinationModels.COMRO_cost import COMRO_cost

            self.LCOW = COMRO_cost(Capacity = self.desal_values_json['Capacity'], Prod = (self.simu_output[4]['Value']), fuel_usage = self.simu_output[7]['Value'], oaro_area  = self.costout['oaro_area'], ro_area  = self.costout['ro_area'], yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], 
                                downtime =  self.cost_values_json['downtime'],chem_cost =  self.cost_values_json['chem_cost'], labor_cost =  self.cost_values_json['labor_cost'], rep_rate =  self.cost_values_json['rep_rate'], pumpcost = self.costout['pumpcost'], erdcost  = self.costout['erdcost'], ro_cost  =  self.cost_values_json['ro_cost'], oaro_cost  =  self.cost_values_json['oaro_cost'],
                                sec =  self.costout['sec'], sam_coe = self.cost_values_json['sam_coe'], practical_inv_factor = self.cost_values_json['practical_inv_factor'], storage_cap = self.COMRO.storage_cap )
        
            self.cost_output = self.LCOW.lcow()
            
        elif desal == 'RO_FO':
            from DesalinationModels.RO_FO_cost import RO_FO_cost
            if self.cspModel=='pvsamv1':
                self.sam_lcoe = self.lcoe
                self.sam_lcoh = 0

            elif self.cspModel == 'linear_fresnel_dsg_iph' or self.cspModel == 'trough_physical_process_heat' or self.cspModel == 'SC_FPC' or self.cspModel == 'SC_ETC':
                self.sam_lcoh = self.lcoh
                self.sam_lcoe = 0
            else:
                self.sam_lcoe = self.lcoe
                self.sam_lcoh = self.lcoh
            # Look for capacity of RO
            Capacity = [self.RO_FO.RO_capacity]
            unit_capex = [self.cost_values_json['unit_capex']]
            
            self.LCOW = RO_FO_cost(Capacity = Capacity, Prod = self.simu_output[4]['Value'],chem_cost = self.cost_values_json['chem_cost'], labor_cost = self.cost_values_json['labor_cost'],
                                          unit_capex = unit_capex,rep_rate = self.cost_values_json['rep_rate'], FO_unit_capex = self.cost_values_json['FO_unit_capex'], 
                                          FO_labor = self.cost_values_json['FO_labor'], FO_chem_cost = self.cost_values_json['FO_chem_cost'], FO_goods_cost = self.cost_values_json['FO_goods_cost'], 
                                          cost_storage = self.cost_values_json['cost_storage'],  insurance = self.cost_values_json['insurance'], 
                                          FO_SEC = self.cost_values_json['FO_SEC'], FO_capacity = self.design_output[2]['Value'], FO_STEC = self.design_output[8]['Value'], disposal_cost = self.cost_values_json['disposal_cost'], 
                                          FO_fuel_usage = self.simu_output[8]['Value'], coe = self.cost_values_json['coe'], solar_coe = self.cost_values_json['solar_coe'], solar_coh = self.cost_values_json['solar_coh'], coh = self.cost_values_json['coh'],sam_coe = self.sam_lcoe, sam_coh = self.sam_lcoh)
            self.cost_output = self.LCOW.lcow()
            
        elif desal == 'RO_MDB':
            from DesalinationModels.RO_MDB_cost import RO_MDB_cost
            if self.cspModel=='pvsamv1':
                self.sam_lcoe = self.lcoe
                self.sam_lcoh = 0

            elif self.cspModel == 'linear_fresnel_dsg_iph' or self.cspModel == 'trough_physical_process_heat' or self.cspModel == 'SC_FPC' or self.cspModel == 'SC_ETC':
                self.sam_lcoh = self.lcoh
                self.sam_lcoe = 0
            else:
                self.sam_lcoe = self.lcoe
                self.sam_lcoh = self.lcoh
            
            Capacity = [self.RO_MDB.RO_capacity]
            unit_capex = [self.cost_values_json['unit_capex']]
            self.LCOW = RO_MDB_cost(Capacity = Capacity, Prod = self.simu_output[4]['Value'],chem_cost = self.cost_values_json['chem_cost'], labor_cost = self.cost_values_json['labor_cost'],
                                          unit_capex = unit_capex, rep_rate = self.cost_values_json['rep_rate'], 
                                          MDB_Area = self.RO_MDB.MDB.Area, Pflux = self.RO_MDB.MDB.PFlux[0], TCO = self.RO_MDB.MDB.TCO[0], TEI = self.RO_MDB.MDB.TEI_r, FFR = self.RO_MDB.MDB.FFR_r, 
                                          th_module = self.RO_MDB.MDB.ThPower[0], 
                                          MD_membrane = self.cost_values_json['MD_membrane'], MD_module = self.cost_values_json['MD_module'], 
                                          MD_module_capacity = self.cost_values_json['MD_module_capacity'], HX = self.cost_values_json['HX'], 
                                          endplates = self.cost_values_json['endplates'], endplates_capacity = self.cost_values_json['endplates_capacity'], 
                                          other_capacity = self.cost_values_json['other_capacity'], heat_cool = self.cost_values_json['heat_cool'], 
                                          heat_cool_capacity = self.cost_values_json['heat_cool_capacity'], h_r = self.cost_values_json['h_r'], 
                                          h_r_capacity = self.cost_values_json['h_r_capacity'], tank = self.cost_values_json['tank'], 
                                          tank_capacity = self.cost_values_json['tank_capacity'], pump = self.cost_values_json['pump'], 
                                          pump_capacity = self.cost_values_json['pump_capacity'], other = self.cost_values_json['other'], 
                                   
                                          cost_storage = self.cost_values_json['cost_storage'],  insurance = self.cost_values_json['insurance'], 
                                          MDB_SEC = self.RO_MDB.MDB.SEEC[-1], MDB_capacity = self.design_output[2]['Value'], MDB_STEC = self.design_output[8]['Value'], disposal_cost = self.cost_values_json['disposal_cost'], 
                                          MDB_fuel_usage = self.simu_output[8]['Value'], coe = self.cost_values_json['coe'], solar_coe = self.cost_values_json['solar_coe'], solar_coh = self.cost_values_json['solar_coh'], coh = self.cost_values_json['coh'], sam_coe = self.sam_lcoe, sam_coh = self.sam_lcoh)
            self.cost_output = self.LCOW.lcow()
            
        elif desal == 'Generic':
            from DesalinationModels.Generic_cost import Generic_cost
            self.LCOW = Generic_cost(unit_cost = self.cost_values_json['unit_cost'], downtime = self.cost_values_json['downtime'],
                                    Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], SEEC = self.desal_values_json['SEC'], STEC = self.desal_values_json['STEC'],
                                    Chemicals = self.cost_values_json['Chemicals'], Labor = self.cost_values_json['Labor'], Discharge = self.cost_values_json['Discharge'], Maintenance = self.cost_values_json['Maintenance'],  Miscellaneous = self.cost_values_json['Miscellaneous'],
                                   yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], solar_coh = self.cost_values_json['solar_coh'], coh =  self.cost_values_json['coh'], sam_coh = self.lcoh, cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.Generic.storage_cap)
            self.cost_output = self.LCOW.lcow()



        filename = desal + '_cost_output' + self.timestamp + '.json'
        csvname = self.project_name + '_' +  desal + '_cost_output' + '_' + self.timestamp + '.csv'
        
        if self.parametric:
            cost_json_outfile = self.samPath / 'parametric_results' / filename  
            cost_csv_outfile = self.samPath / 'CSV parametric_results' / csvname  
        else:
            cost_json_outfile = self.samPath / 'results' /filename 
            cost_csv_outfile = self.samPath / 'CSV results' / csvname                  
        with open(cost_json_outfile, 'w') as outfile:
            json.dump(self.cost_output, outfile)

        with open(cost_json_outfile) as json_file: 
            data = json.load(json_file)         
        # now we will open a file for writing 
        data_file = open(cost_csv_outfile, 'w', newline='') 
        # create the csv writer object 
        csv_writer = csv.writer(data_file) 
        
        map_json = cfg.map_json
        with open(map_json, "r") as read_file:
            map_data = json.load(read_file)   
        csv_writer.writerow(["Location", map_data['county'] + '  ' + map_data['state']])
        csv_writer.writerow(["Desal technology", cfg.Desal[self.desalination]])
        csv_writer.writerow(["Solar technology", cfg.Solar[self.cspModel]])        
        csv_writer.writerow([])        
        
        count = 0
        for i in data: 
            if count == 0: 
          
                # Writing headers of CSV file 
                header = i.keys() 
                csv_writer.writerow(header) 
                count += 1
          
            # Writing data of CSV file 
            csv_writer.writerow(i.values()) 
          
        data_file.close()  
            
    def collect_model_variables(self):
        # Add CSP variables
        json_files = []
        cspPath = self.cspModel + '_inputs.json'
        json_files.append(Path(self.samPath / "models" / "inputs" / cspPath))
        
        if self.financialModel: # if there's a finiancial model
            # Then add finiancial variables
            finPath = self.financialModel + '_inputs.json'
            json_files.append(Path(self.samPath / "models" / "inputs" / finPath))
            if self.financialModel == 'utilityrate5':
                json_files.append(Path(self.samPath / "models" / "inputs" / 'cashloan_inputs.json'))
#            elif self.financialModel == 'iph_to_lcoefcr':
#                json_files.append(Path(self.samPath / "models" / "inputs" / 'lcoefcr_inputs.json'))

            
        variableValues = []
        # Load variable values from JSON
        with open(self.json_values, "r") as read_file:
            values_json = json.load(read_file)
        
        with open(self.cost_json_values, "r") as read_file:
            cost_json = json.load(read_file)
        values_json.update(cost_json)
            
        # Load variable names from JSON
        for json_file in json_files:
            all_variables = []
            with open(json_file, "r") as read_file:
                ssc_json = json.load(read_file)
            #ssc_json dictionary has all the data
            for model, items in ssc_json.items():
                for item in items:
                    all_variables.append(item)    
                
            for variable in all_variables:
                # Set default value for non-specified variables
                if self.cspModel in [ 'tcsdirect_steam' , 'pvsamv1' , 'tcsmolten_salt' , 'pvwattsv7']: 
                    if variable['Name'] == 'file_name':
                        varValue = values_json['file_name']
                        variableValues.append({'name': 'solar_resource_file',
                                               'value': varValue,
                                               'datatype': variable['DataType'] })   
                        continue
                

                
                if variable['Name'] not in values_json and variable['DataType'] == 'SSC_NUMBER':
                    if 'Require' in variable:
                        if variable['Require'] == "*":
                            varValue = 0
                        elif "?=" in variable['Require']:
                            varValue = float(variable['Require'][2:])
                        else:
                            varValue = 0
                    else:
                        continue
   
                elif variable['Name'] not in values_json and variable['DataType'] == 'SSC_ARRAY':
                    if 'Require' in variable:
                        if variable['Require'] == "*":
                            varValue = [0]
                        else:
                            continue
                    else:
                        continue
                elif variable['Name'] not in values_json and variable['DataType'] == 'SSC_MATRIX':
                    if 'Require' in variable:
                        if variable['Require'] == "*":
                            varValue = [[0]]
                        else:
                            continue
                    else:
                        continue     
                elif variable['Name'] not in values_json and variable['DataType'] == 'SSC_TABLE':
                    if 'Require' in variable:
                        if variable['Require'] == "*":
                            varValue = []
                        else:
                            continue
                    else:
                        continue  
                elif variable['Name'] not in values_json and variable['DataType'] == 'SSC_STRING':
                    if 'Require' in variable:
                        if variable['Require'] == "*":
                            varValue = []
                        else:
                            varValue = variable['Require'][2:]
                    else:
                        continue  
                else:
                    varValue = values_json[variable['Name']]
#                    print(variable['Name'], varValue)
                    
                try:
                    variableValues.append({'name': variable['Name'],
                                           'value': varValue,
                                           'datatype': variable['DataType'],
                                           'constraint': variable['Constraints'] })
                except KeyError:
                    variableValues.append({'name': variable['Name'],
                                           'value': varValue,
                                           'datatype': variable['DataType'] })
    
            #variable.valu
            inputfile = self.samPath / 'results' /'inputdata.json'
                    
            with open(inputfile, 'w') as outfile:
                json.dump(variableValues, outfile)
        return variableValues 
    
    map_json = cfg.map_json
    with open(map_json, "r") as read_file:
        map_data = json.load(read_file)       
        latitude = map_data['latitude']
    other_input_variables = {
        "tcstrough_physical":{},
        "tcsMSLF":{},
        "tcsmolten_salt":{},
        "tcsdirect_steam":{},
        "trough_physical_process_heat":{'track_mode': 1,
                                        'tilt': 0,
                                        'azimuth': 0,
                                        'accept_mode': 0,
                                        'accept_init': 0,
                                        'accept_loc': 1,
                                        'mc_bal_hot': 20000000298023224,
                                        'mc_bal_cold': 20000000298023224,
                                        'mc_bal_sca': 4.5},
        "linear_fresnel_dsg_iph":{},  
        "pvsamv1":{},   
        "pvwattsv7":{},   
        "SC_FPC":{},
        "tcslinear_fresnel":{'track_mode': 1,
                             'tilt': 0,
                             'azimuth': 0,
                             'PB_pump_coef': 0,
                             'pc_mode': 1,
                             'm_dot_st':0,
                             'T_wb': 12.800000190734863,
                             'T_db_pwb': 12.800000190734863,
                             'P_amb_pwb': 960,
                             'relhum': 0.25,
                             'dp_b': 0,
                             'dp_sh': 5,
                             'dp_rh': 0,
                             'tes_hours': 0,
                             'dnifc': 0,
                             'I_bn': 0,
                             "T_db" : 15,
	                         "T_dp" : 10,
	                         "P_amb" : 930.5,
                             "V_wind" : 0,
                             "m_dot_htf_ref" : 0,
                             "m_pb_demand" : 0,
                             "shift" : 0,
                             "SolarAz_init" : 0,
                             "SolarZen" : 0,
                             "T_pb_out_init" : 290,
                             'standby_control': 0,
                             'latitude': latitude
                             },
        "singleowner": {
                        "cp_battery_nameplate": 0,}
						
        }

    def set_data(self, variables):

        # Map all the strings present in the json file.
        stringsInJson = {}
        added_variables = {}
        
        for name, value in self.other_input_variables[self.cspModel].items():
            self.ssc.data_set_number( self.data, b''+ name.encode("ascii", "backslashreplace"), value )

        if self.financialModel == 'singleowner':
            for name, value in self.other_input_variables['singleowner'].items():     
                if type(value) == list:
                    self.ssc.data_set_array(  self.data, b''+ name.encode("ascii", "backslashreplace"), value )
                else:
                    self.ssc.data_set_number( self.data, b''+ name.encode("ascii", "backslashreplace"), value )
                
               						            
        
        # Increment complete TODOs count for each user.

        for ssc_var in variables:
            try:
                #Checking if the variable value is present in the json and if value of the variable is a valid one.
                if ("value" in ssc_var and ssc_var["value"] != "#N/A" ):
                    # Add value to the dictionary.
                    
                    
                    varName = ssc_var["name"]
                    added_variables[varName] = False
                    
                    # assign capacity for singleowner:
                    if self.financialModel == 'singleowner' and varName == 'system_capacity':
                        varValue = ssc_var["value"] / 1000
                        tempName = 'cp_system_nameplate'
                        self.ssc.data_set_number( self.data, b''+ tempName.encode("ascii", "backslashreplace"), varValue)
                    
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
#                        if "constraint" in ssc_var:
#                        if (ssc_var["constraint"] == "INTEGER" or ssc_var["constraint"] == "BOOLEAN"  ):
#                            self.ssc.data_set_number( self.data, b''+ varName.encode("ascii", "backslashreplace"), int(varValue))
#                            added_variables[varName] = True
##                            if (ssc_var["constraint"] == "MAX=100"):
##                                #Verify if the variable is above 100
##                                if (varValue > 100 or varValue <0):
##                                    raise Exception("The value specified for '" + varName + "' is not within the specified range.")
##                                else:
##                                    self.ssc.data_set_number( self.data, b''+ varName.encode("ascii", "backslashreplace"), int(varValue))
##                                    added_variables[varName] = True
#                        else:

                        self.ssc.data_set_number( self.data, b''+ varName.encode("ascii", "backslashreplace"), varValue)
                        added_variables[varName] = True
                    
                    
                    
                    else:
                        # Add value to the dictionary.
                        raise Exception("Specified variable type for SAM file from the JSON is not found in definitions.")
                    stringsInJson[varName] = varValue

            except Exception as error:
                self.logger.critical(error)
                print(error)
                print(ssc_var)
#                self.logger.info(stringsInJson)
#        print(added_variables)

    def module_create_execute(self, module):
        module1 = self.ssc.module_create(b'' + module.encode("ascii", "backslashreplace"))	
        try:
            # self.logger.debug("Running execute statements for the SAM module '" + module + "'.")
            
            self.ssc.module_exec_set_print( 0 )
            if self.ssc.module_exec(module1, self.data) == 0:
                # print ('{} simulation error'.format(module1))
                idx = 1
                msg = self.ssc.module_log(module1, 0)
                while (msg != None):
                    # print ('	: ' + msg.decode("utf - 8"))
                    # msg = self.ssc.module_log(module1, idx)
                    idx = idx + 1
                # SystemExit( "Simulation Error" )
            self.ssc.module_free(module1)
        except Exception as e:
            # print(e)
            idx = 1
            msg = self.ssc.module_log(module1, 0)
            while (msg != None):
                # print ('	: ' + msg.decode("utf - 8"))
                self.logger.info('	: ' + msg.decode("utf - 8"))
                msg = self.ssc.module_log(module1, idx)
                idx = idx + 1
            self.logger.critical("Exception occurred while executing the SAM module. Please see the detailed error message below", exc_info=True)

    def P_T_conversion(self, Cond_p):
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
    
    def temp_to_heat(self, T_cond, mass_fr, T_feedin):
        import DesalinationModels.IAPWS97_thermo_functions as TD_func
        Q_capacity = []

        for i in range(len(T_cond)):

            try:
                if T_cond[i] > 65:
                    Q_capacity.append(0.95* max(0, 1.996 * mass_fr[i] * (T_cond[i] - T_feedin) / 3600)  # sensible heat 
                                 +  0.95 * mass_fr[i] / 3600 * (TD_func.enthalpySatVapTW(T_cond[i]+273.15)-TD_func.enthalpySatLiqTW(T_cond[i]+273.15))[0]) # latent heat
                else:
                    Q_capacity.append(0)
            except:
                Q_capacity.append(0)
                        
        return Q_capacity
    
        
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
        print('GOR-Gained output ratio:',max(GOR)) # GOR: Gained output ratio 
        print('Md-Distillate water (m3/h):',max(Md)) # Distillate water (m3/h)
        # Generate csv
        np.savetxt("GOR-Gained output ratio.csv", GOR,delimiter=',')
        np.savetxt("Md-Distillate water.csv",  Md, delimiter=',')
        return GOR, Md

    def data_free(self):
        self.ssc.data_clear(self.data)

    def print_collector_params(self, collector_outputs):
        outputs = []
        for i in collector_outputs:
            outputs.append({'Name': i['Name'],
                            'Value':i['Value'],
                            'Unit': i['Unit']})       
        
        filename = 'Solar_output' + self.timestamp + '.json'
        csvname = self.project_name + '_Solar_output' + '_' + self.timestamp + '.csv'
        if self.parametric:
            json_outfile = self.samPath / 'parametric_results' / filename 
            csv_outfile = self.samPath / 'CSV parametric_results' / csvname
        else:
            json_outfile = self.samPath / 'results' / filename
            csv_outfile = self.samPath / 'CSV results' / csvname
        with open(json_outfile, 'w') as outfile:
            json.dump(outputs, outfile)
        #print ('outputs = ', outputs)
        with open(json_outfile) as json_file: 
            data = json.load(json_file)         
        # now we will open a file for writing 
        data_file = open(csv_outfile, 'w', newline = '') 
        # create the csv writer object 
        csv_writer = csv.writer(data_file) 
        map_json = cfg.map_json
        with open(map_json, "r") as read_file:
            map_data = json.load(read_file)   
        csv_writer.writerow(["Location", map_data['county'] + map_data['state']])
        csv_writer.writerow(["Solar technology", cfg.Solar[self.cspModel]]) 
        csv_writer.writerow([])
        count = 0
        time_series = []
        for i in data: 
            if count == 0: 
                # Writing headers of CSV file 
                header = i.keys() 
                csv_writer.writerow(header) 
                count += 1
          
            # Writing data of CSV file 
            if type(i["Value"]) != list:
                csv_writer.writerow(i.values()) 
            elif len(i["Value"]) > 24:
                time_series.append(i)
        
        header = []
        for i in time_series:
            header.append(i["Name"] + " (" + i["Unit"] + ")")

        csv_writer.writerow([])
        csv_writer.writerow(["Hour"] + header)
        for i in range(8760):
            try:
                csv_writer.writerow([i] + [j["Value"][i] for j in time_series])
            except:
                continue
          
        data_file.close()     
        
        
    def print_impParams(self):
        cspOuts = self.cspModel + "_outputs.json"

        output_values = Path(self.samPath / "models" / "outputs" / cspOuts)
        with open(output_values, "r") as read_file:
            outputs_json = json.load(read_file)
        outputs = []
        for variable in outputs_json['Output']:

#            if variable == 'twet': continue
            if variable['Data'] == 'SSC_NUMBER':
                value = self.ssc.data_get_number(self.data, variable['Name'].encode('utf-8'))#bytes(variable, 'utf-8'))
            elif variable['Data'] == 'SSC_ARRAY':
                value = self.ssc.data_get_array(self.data, variable['Name'].encode('utf-8'))
            
            if 'Unit' in variable:
                unit = variable['Unit']
            elif 'Units' in variable:
                unit = variable['Units']
            
            else:
                unit = ''
            
            outputs.append({'Name': variable['Label'],
                            'Value': value,
                            'Unit': unit})
        # append more results
        if self.cspModel == 'linear_fresnel_dsg_iph':
            outputs.append({'Name': 'Actual aperture',
                            'Value': self.actual_aper,
                            'Unit': 'm2'})
        if self.cspModel == 'tcslinear_fresnel' or self.cspModel== 'tcsdirect_steam':
            outputs.append({'Name': 'Condenser steam temperature',
                            'Value': self.T_cond,
                            'Unit': 'oC'})  
            outputs.append({'Name': 'Steam mass flow rate',
                            'Value': self.mass_fr_hr,
                            'Unit': 'kg/hr'})   
            outputs.append({'Name': 'Waste heat generation',
                            'Value': self.heat_gen,
                            'Unit': 'kWh'})  
        if self.cspModel == 'tcstrough_physical'  or self.cspModel== 'tcsMSLF' or self.cspModel== 'tcsmolten_salt':
            outputs.append({'Name': 'Steam mass flow rate',
                            'Value': self.mass_fr_hr,
                            'Unit': 'kg/hr'})   
            outputs.append({'Name': 'Waste heat generation',
                            'Value': self.heat_gen,
                            'Unit': 'kWh'})              
        
        

        filename = 'Solar_output' + self.timestamp + '.json'
        csvname = self.project_name + '_Solar_output' + '_' + self.timestamp + '.csv'
        if self.parametric:
            json_outfile = self.samPath / 'parametric_results' / filename 
            csv_outfile = self.samPath / 'CSV parametric_results' / csvname
        else:
            json_outfile = self.samPath / 'results' / filename
            csv_outfile = self.samPath / 'CSV results' / csvname
        with open(json_outfile, 'w') as outfile:
            json.dump(outputs, outfile)
        #print ('outputs = ', outputs)
        with open(json_outfile) as json_file: 
            data = json.load(json_file)         
        # now we will open a file for writing 
        data_file = open(csv_outfile, 'w', newline = '') 
        # create the csv writer object 
        csv_writer = csv.writer(data_file) 
        map_json = cfg.map_json
        with open(map_json, "r") as read_file:
            map_data = json.load(read_file)   
        csv_writer.writerow(["Location", map_data['county'] + map_data['state']])
        csv_writer.writerow(["Solar technology", cfg.Solar[self.cspModel]]) 
        csv_writer.writerow([])
        count = 0
        time_series = []
        for i in data: 
            if count == 0: 
                # Writing headers of CSV file 
                header = i.keys() 
                csv_writer.writerow(header) 
                count += 1
          
            # Writing data of CSV file 
            if type(i["Value"]) != list:
                csv_writer.writerow(i.values()) 
            elif len(i["Value"]) > 24:
                time_series.append(i)
        
        header = []
        for i in time_series:
            header.append(i["Name"] + " (" + i["Unit"] + ")")

        csv_writer.writerow([])
        csv_writer.writerow(["Hour"] + header)
        for i in range(8760):
            try:
                csv_writer.writerow([i] + [j["Value"][i] for j in time_series])
            except:
                continue
          
        data_file.close()     

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
        #self.logger.info('Logger started.')
        #self.logger.debug('detailed statements here...')
        #self.logger.warning('Warning message! Be forewarned!')
        #self.logger.critical('Critical error, omg!')


if __name__ == '__main__':
    sam = SamBaseClass( CSP = 'tcslinear_fresnel',
                       desalination =  'VAGMD',
                  financial = 'lcoefcr')
    # sam = SamBaseClass(CSP = 'tcslinear_fresnel',
    #           financial = 'lcoefcr')
    # sam.desal_design(sam.desalination)
    sam.main()
    
    #Argument for the unit test makes sure the unit test does not fail if system_capacity 
    #system_capacity is passed as a first argument on command line.
    #unittest.main(argv=['first-arg-is-ignored'], exit=False)