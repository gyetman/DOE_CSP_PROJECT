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
      
        
        elif self.cspModel=='SC_FPC':
            from PSA.StaticCollector_flatplate import StaticCollector_fp
            from PSA.SC_ETC_cost import ETC_cost
            
            with open(self.json_values, "r") as read_file:
                solar_input = json.load(read_file)
            
            self.staticcollector=StaticCollector_fp(design_point_date = solar_input['design_point_date'],desal_thermal_power_req = solar_input['desal_thermal_power_req'],initial_water_temp = solar_input['initial_water_temp'],outlet_water_temp = solar_input['outlet_water_temp'],cleanless_factor = solar_input['cleanless_factor'],G = solar_input['G'],a = solar_input['a'], b = solar_input['b'], c = solar_input['c'], A = solar_input['A'], file_name = solar_input['file_name'], tilt_angle = solar_input['tilt_angle'], v1 = solar_input['v1'], v2 = solar_input['v2'] , qm = solar_input['qm'], Tamb_D = solar_input['Tamb_D'] )
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
            self.staticcollector=StaticCollector_et(design_point_date = solar_input['design_point_date'],desal_thermal_power_req = solar_input['desal_thermal_power_req'],
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
                if self.cspModel == 'tcslinear_fresnel':
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
            if self.cspModel == 'tcslinear_fresnel':
                self.lcoe = self.ssc.data_get_number(self.data, b'lcoe_fcr')
            else:
                # tempelate value 
                self.lcoe = 0.136
            self.lcoh =  self.lcoe * 0.23
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
                if self.cspModel != 'tcsmolten_salt':
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
            if self.cspModel != 'tcsmolten_salt':
                self.lcoe = self.ssc.data_get_number(self.data, b'lcoe_fcr')
            else:
                # tempelate value   
                self.lcoe = 0.136
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
            self.RO = RO(nominal_daily_cap_tmp = self.desal_values_json['nominal_daily_cap_tmp'], FeedC_r = self.desal_values_json['FeedC_r'],T  = self.desal_values_json['T'],Nel1 = self.desal_values_json['Nel1'],R1 = self.desal_values_json['R1'],nERD= self.desal_values_json['nERD'],nBP= self.desal_values_json['nBP'],nHP= self.desal_values_json['nHP'],nFP= self.desal_values_json['nFP'],Fossil_f =self.desal_values_json['Fossil_f'] )
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
                               nFP = self.desal_values_json['nFP'],Nel1 = self.desal_values_json['Nel1'])
            self.design_output = self.RO_FO.design()
            self.P_req = self.RO_FO.P_req
            
        elif desal == 'RO_MDB':
            from DesalinationModels.RO_MDB import RO_MDB
            self.RO_MDB = RO_MDB(capacity = self.desal_values_json['capacity'], RO_rr = self.desal_values_json['RO_rr'], salinity = self.desal_values_json['FeedC_r'], T_sw = self.desal_values_json['T_sw'], 
                               nERD = self.desal_values_json['nERD'],nBP = self.desal_values_json['nBP'],nHP = self.desal_values_json['nHP'],
                               nFP = self.desal_values_json['nFP'],Nel1 = self.desal_values_json['Nel1'],
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
            self.RO = RO(nominal_daily_cap_tmp = self.desal_values_json['nominal_daily_cap_tmp'], FeedC_r = self.desal_values_json['FeedC_r'],T  = self.desal_values_json['T'],Nel1 = self.desal_values_json['Nel1'],R1 = self.desal_values_json['R1'],nERD= self.desal_values_json['nERD'],nBP= self.desal_values_json['nBP'],nHP= self.desal_values_json['nHP'],nFP= self.desal_values_json['nFP'], Fossil_f =self.desal_values_json['Fossil_f'] )
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
            # self.elec_gen = [-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,72194,136206,176233,197079,204039,195293,171973,130436,69934.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,69048.1,133852,175627,197064,204295,195206,171042,128602,69736,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,66516.3,128523,168840,191720,151406,27467.4,59413.4,129702,70691.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,71632,135347,176669,195393,202545,194654,170036,130602,71796.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,67979.5,132465,172146,194957,202610,195311,171386,132376,73019.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,65354.6,128417,169407,190185,197398,189568,169133,130056,72226.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,63278.7,126755,169210,194244,200852,193373,170553,129234,69846.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,61123.9,129039,177996,207620,217510,210709,184785,140171,77497.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,20679.8,129764,171536,194663,203310,128786,173341,132605,61115.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,65770.3,128604,168713,187913,194236,139816,172317,79087.7,75547.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,22808.8,87293.4,79394.8,113069,157487,123088,119524,102290,30764.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,306.399,19929.8,98003.6,146541,46994.3,74659.9,56914,71632.8,78123.2,3133.06,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,76549.2,142292,184714,205758,214007,206546,183377,143148,84188.2,6508.65,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,21245.5,67577.5,175438,142856,166737,178359,113011,23177.8,3828.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,482.889,23292.6,18238.5,45077.9,14202.4,61749.9,36968,26709.9,5096.19,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12504.1,124001,168605,125223,153278,133761,104365,130919,72564.3,3557.48,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,64617.3,129090,173992,196044,204706,197267,172028,134591,76934.1,4660.33,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,65900.5,129732,172066,191619,200361,193842,173878,135258,79061.5,5889.36,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,63489.5,128136,170960,191588,198069,189537,171951,137356,83491.1,9572.14,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,66167,129871,171601,191662,201052,195255,177149,138070,82069.2,9999.27,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,17135.1,46552.2,84222.6,48290.1,48621.3,38387.5,126839,133930,72520.4,1811.78,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,69501.5,78260.2,109660,107672,151846,111293,91166.5,32452.7,37143.1,1026.19,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,31255.5,129869,112328,81188.6,90537.7,99120.6,116150,26704.4,14707.5,1043.22,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,67295.8,133997,182288,208330,218018,213934,190494,148884,89043.7,12856.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,72251.9,138563,186053,212754,218018,217034,192630,151733,91917.3,14870.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,69144.4,133324,174365,194789,203816,198489,179550,143106,88496.5,13666.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,18906.2,88754.1,92584.9,110405,83246.3,110431,119019,74212.2,19389.6,1144.88,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,72063.3,138915,184028,209693,218018,214853,191921,151431,93879.9,18250.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,71442.9,137768,180906,205072,215924,209861,187334,147888,92624.9,18586.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,70929.8,134328,172477,196246,204318,196760,180257,148103,92818.9,20038.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,13419.4,128693,68540.3,199141,206266,201988,183473,146261,91198.1,12806.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,79912.6,146990,194354,218018,218018,218018,201153,159590,101574,26723.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,74113.9,139183,182034,204824,214402,209892,189821,151779,95419.1,25503.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,73781.5,137485,179928,159858,215084,209313,187610,113958,78286.7,27064.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,74950.5,137283,178786,201662,211055,204861,184849,147847,95769.2,29269.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,74541.7,134062,174637,197391,207661,203647,184028,147895,97475.1,29730.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,552.431,72415.2,134632,126322,202342,213265,177546,187403,127882,73283.5,18775.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1689.61,69076.6,133260,179234,208674,218018,211204,190430,151185,92404.2,24333.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,440.261,48758.5,84788.1,105990,218018,218018,166657,155130,159315,99953.8,30573.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3918.71,75877.9,141907,190178,218018,218018,218018,203453,164639,106147,33858.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2138.02,78509.6,141136,182596,175619,194095,208062,138357,152924,99025.7,26579.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5053.21,76754.3,140159,181325,203157,212340,209261,191460,158775,104699,34727.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7318.33,78720.8,140579,184902,214282,218018,218018,200330,161708,105895,35210.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7193.53,78660.3,143878,188678,171148,122624,36564.9,15149.9,130101,66212.1,14428.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1850.91,6463.8,57690.4,96034.3,55859.9,138293,5029.94,159026,160510,7633.73,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8355.39,81048.4,145145,188757,212845,218018,214643,195486,159765,106673,37970.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1820.61,35532.1,85436.5,116015,146874,161280,187354,199078,163843,108375,39442,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8821.48,64661.5,94617,142461,189356,128661,103364,90369.4,60244.7,58245.9,12458.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1889.37,57251.3,142062,181208,199587,210381,210233,193140,159797,106067,38151.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10718,83108.2,144968,185356,207966,214259,208165,192183,157129,103542,35827.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9184.04,77925.9,137940,179727,204976,212016,206083,189269,157840,105853,39099.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12401.5,81850,142156,184891,174844,218018,213398,194009,158354,103113,36787,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9592.53,44421.1,136134,145078,165440,174961,159751,136855,117971,50049,34522.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,18246.3,14622.5,145381,218018,218018,218018,209350,169473,84919.1,37962.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,16302.9,85042.5,146371,191806,218018,218018,190612,202112,133683,79788.1,21718.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1413.08,21814.4,87725.5,104511,168646,159842,120836,106946,63933.2,27836.2,5895.99,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1272.24,39256.1,146083,129739,151975,184694,53536,102291,162231,107346,41317.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,18759,84661.3,104596,147775,186490,124092,126089,7546.45,51151,28369.2,7067.55,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10817.2,62815.1,118454,48519.8,30159,122248,11183.1,10181.4,77488.3,20840.5,42208.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6681.81,39049.2,103541,150307,203950,213848,190570,171868,157057,104552,39745.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,21718.8,91054.2,148734,185309,173574,175143,208805,190255,157647,107107,17587.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,22954.6,89798.4,147166,187265,213540,218018,218018,199373,164278,97878.4,42936.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5332.79,58843.6,93110.1,136741,168022,185804,184682,151158,123829,108202,41997.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,22526.6,90684.5,148828,186710,208251,213719,204531,188282,157623,108431,44159.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,24328.1,91261.8,150264,191089,217460,218018,218018,203743,166121,112194,44372.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,23416.1,89303.1,9365.84,26304.3,8203.89,53311.9,27402.8,36815.7,83736.9,47344.8,131.623,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,24253.7,91546,149048,192121,218018,218018,218018,204148,166456,112426,28048.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,26355.9,95022.8,153670,195120,218018,218018,218018,199235,163495,110817,44771.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9483.66,69627.9,155096,193392,215656,218018,215735,196609,162152,109200,44396.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,26480.8,91713.1,151276,193761,218018,218018,218018,204303,163757,94679.5,35932.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,27911,95739,156957,201687,218018,218018,218018,206757,167598,111454,44417.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,30438.8,97694,152319,186489,212651,218018,218018,200350,164598,110726,45041.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,30957.2,96895.6,152304,192922,190776,199910,192867,133075,127195,7046.92,21789.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,15672.1,24423.5,83997.9,187532,218018,218018,218018,205796,165469,109371,42968.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,309.589,55158.5,3707.47,24595.9,54914,55293.6,85244.9,91722.4,135601,2548.55,7097.21,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,18672.9,29926.2,20966,67331.6,37418.7,63284.7,104043,150903,156313,75826.1,20889.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,32161.1,97319.5,153254,194516,218018,218018,218018,198879,162548,108322,43540.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,33030.8,98077.7,154225,193969,218018,218018,218018,199513,147804,108885,44036,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,33700.7,77740.9,122793,183976,208162,218018,216170,195017,159145,108408,45255.3,586.536,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,36136.1,103121,159382,198387,218018,218018,218018,197715,160700,108617,45401.7,729.028,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,36575.8,102688,157395,191539,209049,217917,215087,196564,162265,109303,45453.6,837.945,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,34369.9,98446.5,155706,197115,218018,218018,218018,196151,158778,105594,43340.5,828.748,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,35597.4,99039.4,151724,184571,202895,213274,208679,189202,155363,104491,43079,946.393,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,31025.4,42695.6,128192,179162,187343,218018,188922,131674,52454,25723,23808.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1209.97,33777.3,63519.3,130012,143491,110753,78168.8,41371.5,92283.5,66653.4,42680.7,1475.79,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,37207.6,100243,154599,193999,216821,218018,216486,195371,158284,106029,44076.1,1360.23,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,38620.1,101680,153557,190068,212969,218018,211387,191266,156413,105953,44059.8,1266.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,549.145,38728.9,99037.6,150372,187457,212225,218018,214678,192163,155245,102110,41416.4,1080.34,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,545.611,37986.4,99518.5,151758,187426,205787,214761,209161,186839,153539,103605,42041,1500.69,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,816.877,39155.2,102632,157600,197470,218018,218018,218018,197479,158572,103609,43080.8,1381.95,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1199.68,41311.8,103251,151845,182723,198238,209549,206295,188030,154320,103011,43161.6,1515.82,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1101.1,39169.5,98151.4,147924,181099,197552,203459,172716,122281,93878.1,89787.2,22014,1673.09,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1821.71,37940.6,101755,153407,188171,206636,212368,208079,190171,153926,101526,41360,2000.96,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1793.75,46839.3,115055,170973,209451,218018,218018,218018,199353,161732,109562,46283.6,1782.65,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1773.01,45425.8,107013,152808,185442,204706,211011,186797,165044,147221,83283.1,34902.7,1930.78,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1385.44,5338.96,46418.7,86899.6,96922.9,39602.8,31533.4,64673.8,3850.11,91224.8,6185.57,25669,972.472,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,883.086,25810.8,103780,154373,192347,215482,147574,215281,195222,157503,105032,43990.4,2421.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2423.75,25520.4,73252.2,103033,193248,170255,189591,211131,159111,117985,78534.1,21759.7,2837.59,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11964.3,2429.09,21536,60419.4,64712.1,87204.7,82648,127371,163228,109902,46536.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3671.46,49365,113912,165632,199544,216267,218018,218018,196950,159100,106464,44920.5,3325.08,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3969.65,49953.2,113890,165146,198595,214990,201255,213047,194189,159943,108078,45580.4,3236.68,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,45600.8,109602,159977,192001,206700,208375,199768,181744,148068,99469.3,42633.9,3262.32,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4667.02,46866.3,106353,155959,190372,208711,214142,210486,194724,157744,104641,43357.2,4169.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5682.71,49887.2,112457,166218,205409,218018,218018,218018,196811,157607,104516,44247.1,4280.93,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5550.08,49667.2,111311,163410,198152,217794,218018,212282,190205,153640,102227,43301.7,3819.07,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5511.36,49165.7,109604,159559,193215,210651,215592,207389,184006,149493,99548.1,41874.6,3831.08,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5396.35,47762.1,105423,152340,184605,203272,210037,202446,186921,149144,97545.7,40734.5,4537.67,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6083.16,44870.1,106348,153695,185401,205640,211935,203770,182750,149088,69189.1,29555.1,309.89,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6823.19,47487.6,105088,152832,184795,184080,204660,195852,163527,135397,71811.6,35741.3,4991.66,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7073.41,48645.9,105408,151282,148399,192043,182548,169369,176687,145860,99101.6,42149.4,4598.87,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6621.09,49476.6,108812,158157,192140,210770,217938,209586,187302,150016,99480,42401.4,4945.87,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6764.54,50105,108947,157032,188567,206319,211930,204259,182947,148661,99323.2,41937.3,4586.73,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3880.33,12629.6,34679.5,153084,154204,192506,191007,160362,146922,121045,75670.1,36029.7,5328.24,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8317.4,48852.7,105706,154039,188971,206265,213250,206918,186394,133362,91014.7,41482.7,6356.18,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9179.73,49863.5,107106,155561,187596,206169,210366,201682,180645,146315,97189.7,41947.5,6337.84,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8327.81,52767.5,113325,164888,200460,216832,218018,214445,190811,153540,101803,43613.8,5205.31,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6755.36,54654.2,116117,165438,198852,216110,218018,207730,185810,151157,102127,43003.6,4392.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7174.33,52660.1,110109,155450,190249,206867,210701,199777,176716,142316,95076.8,41816.6,5474.34,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8219.88,52302.7,110823,160109,194239,215316,218018,212461,189459,152316,101631,43104.5,5686.42,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9483.75,55820,117312,168768,205978,218018,218018,218018,198800,158025,105257,41524.3,6080.15,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9679.12,51938,108105,154923,188795,208014,214176,207066,186739,149345,99253.4,42743.8,6392.28,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9468.72,53384.4,109419,153322,180650,197505,200172,191163,174087,144081,96832.5,42204.8,6610.78,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9628.29,46466.3,115491,168184,204727,218018,218018,218018,197467,158683,105911,44728.1,6348.97,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9398.96,55219.5,113977,162440,196341,216281,218018,211019,188574,152839,101498,43183,6062.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9168.62,53828.8,110831,157463,192131,213331,218018,211165,188773,151779,101241,43112.3,6191.65,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11149.7,53320,108999,153274,186163,208269,214311,205881,184460,147159,98011.5,41785.7,6416.79,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10628.3,52856.8,107704,149772,178296,196377,200941,192510,172541,139741,94208.4,40699.5,5924.34,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9414.34,52758.6,107123,150921,179073,190385,187610,186964,171611,139709,94472.3,40717,6000.67,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10055.3,51541.3,102587,144377,175571,195331,202724,195916,176283,142930,95239.6,41462.4,6612.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10678.2,52041.4,104567,148411,180177,200184,206280,198177,177319,143003,94873.2,41354.4,6461.88,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10246.9,52261.5,105782,150819,181389,199772,205532,197923,177246,142761,94955.5,41311.6,6736.86,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11694.2,51613.9,103779,147495,179249,196714,201697,192911,170885,136161,70523,30180.2,3689.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10502.6,50787.5,101056,142764,171018,124894,189845,173985,157984,120949,89453.2,37864,8007.04,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11809.4,52328.2,104653,147929,179193,198468,204994,198572,177396,143823,96362.2,39656.1,8385.71,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10336,52805.7,107218,152081,184803,204770,211188,204055,182856,147223,98782.3,42496,8360.79,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9379.59,53874.6,108280,151535,182243,200575,207325,200829,181665,147653,99460.2,42977.8,5498.76,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8685.24,52685.4,103722,124765,171121,179005,137500,192108,173940,140896,94666.4,40713,6109.05,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10579.3,51183,99750.1,53187.6,175368,194600,155941,131260,124058,5234.34,74564.4,28330.2,8825.34,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,16046.5,22813,99959.4,152517,72611,135853,139824,146830,63082.1,30217.8,157.007,7200.62,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10778.5,51379.1,103718,146920,176316,192299,193645,184595,165616,135884,91310.3,40298.3,7169.85,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10297.5,52134.1,105667,147496,174131,187846,186745,179501,163116,133913,91662.4,40802.7,5846.67,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9283.52,52912.2,105275,147142,174899,189379,191862,186177,169365,138895,94514.4,41644.9,5616.96,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8732.69,53076.9,105845,146828,173496,188187,194441,189486,170997,139395,94759.7,41594.8,5631.58,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9103.21,52012.4,103396,142181,170718,191990,199826,193449,174010,140706,94734.2,41545.9,6275.69,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10131.1,50755.2,101934,144720,176222,195051,201465,195819,176286,142623,95873.5,41626.6,6816.17,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10102,33721.9,102064,144865,175788,184424,187772,185651,166655,142231,95439.8,38607.5,6470.87,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8340.25,48129.4,78658,124744,150993,169166,174687,167350,115652,47946.8,54575.2,30385.3,1043.93,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11682.5,53957.1,107934,152600,181978,198798,203849,196222,176211,142001,95830.3,42247.7,6810.81,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,266.851,10509.3,51898.8,103485,143211,172413,191256,196533,188980,169396,137264,81466,39949,8943.15,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,364.874,10713.5,50936.8,103051,145576,174182,191596,196948,189426,169488,137319,92525.1,41326.5,7871.94,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,364.642,10217.7,50555.9,101738,142367,171037,189043,195747,190227,172249,139556,94448.4,42064.8,7428.57,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,496.175,9496.02,50428,101182,140770,167362,183807,190549,163278,167740,136376,93067,42207.9,7533.28,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,195.269,10893.6,49861.9,100567,143592,173235,190819,196823,191140,171044,139074,93940,42434.1,8047.04,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,485.118,9286.21,50946.5,102792,146048,176660,194387,199743,192971,173582,141283,95961.9,43151,7968.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,735.885,9140.91,49397.7,99498,140157,170107,187629,193193,187064,166204,135764,92652.3,42963.7,9129.65,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,232.421,11738.8,50689.7,100405,141384,168512,179649,185710,182931,166304,136244,93853.5,42643.7,7427.01,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,473.217,9475.04,49535.6,101042,141312,167133,178143,184901,183247,164423,134374,91570.2,42879.5,9978.26,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,340.49,11679.3,48952.1,96956.2,135305,162432,180552,188942,184238,167845,136719,93485.2,42409.1,7823.27,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,459.55,9807.41,49431.1,101597,145838,177791,198062,203314,194971,173299,139407,93822.5,44078.7,10073.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,472.077,10485.3,49086.1,100175,142485,170973,187779,194939,189398,173599,141097,96092.6,43952.1,7099.21,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,590.946,9068.36,49613.8,100402,141835,172646,172325,198765,192538,172286,139341,94252.2,43943.2,9021.39,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,473.087,10551.2,48570.6,98098.5,135633,157516,175301,180388,174363,159414,131525,91465.2,43217.5,8758.04,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,425.546,9895.62,47458.7,97134.6,138377,156013,162280,182381,180869,165704,134252,91849.6,43836.3,9460.82,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12781.8,47830.3,94929.9,88712.4,128025,172512,176069,164621,151475,126284,88549.6,43356.7,9811.12,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,13373.7,47587.5,92791.1,131518,161459,184006,191135,185887,167559,137513,94437.9,43798.9,8188.93,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,443.398,10704.7,46944.5,94044.8,133987,161768,178575,184302,178140,159991,130412,89962.8,43852.4,10474.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,459.209,10235.1,47148.7,96771.9,138104,164470,173274,179288,178248,163283,135401,93736.5,44209.1,8742.36,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,443.853,7919.04,48451.2,100874,141789,166478,181339,192479,188617,171026,140553,97077.1,45580.9,7816.45,204.601,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,458.874,9288.53,48015,99405.6,139279,168488,188366,195186,189355,173676,142465,98821.6,46606.9,7532.06,361.604,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,485.545,9851.93,48879.9,101212,143926,172030,187189,188731,179315,162130,133882,93303.2,44840.4,9728.02,97.7281,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,496.538,8890.65,47570.6,99098.6,139294,165354,182209,191000,188062,170143,139574,96836.1,46019.1,9328.35,99.1062,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,364.279,9558.41,47615.9,98862.4,126505,153516,176444,172847,121119,171060,140451,96466.8,46344.2,10310.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,340.095,9335.49,44427.1,86467.8,139886,134676,143001,141077,161584,168082,138196,96370.7,45662.2,9507,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,232.237,10066.2,46804,96411.2,137110,167934,188805,196762,191389,174069,141969,97915.2,46423.2,9367.78,362.168,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,353.106,8554.65,46305.4,96574.5,135803,162039,165642,187957,162782,136088,134413,93320.2,45410.3,9946.12,361.604,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,496.538,7829.02,46352.5,98000.7,139849,166617,176030,175763,171909,160170,134127,94727.5,46272.1,9781.17,177.241,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,221.486,8167.58,47282.6,99461.8,144037,177023,196926,203874,197233,176806,143798,99688.9,47061.5,8445.57,310.361,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8566.92,45675.7,95469.4,134953,163412,181510,188351,182170,165823,134835,93396.9,46091.2,9937.63,176.396,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10064.7,44785.4,93495.3,135173,163101,177137,180552,174126,155759,125593,85327.5,45025.4,8897.25,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2585.13,37785.9,85219.5,82871.3,155613,169645,177119,171845,155091,126262,87506.1,44707,10498.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9919.98,44121.7,86380.3,124241,154436,176530,183187,177702,156699,127517,69061,46592.4,8671.42,108.939,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9008.47,45774.9,97483.7,140628,172077,191872,198465,193060,172664,141313,97928.7,46486.1,8708.07,277.083,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7700.79,43948.9,94589.6,136950,166793,182507,187217,181516,165158,134947,93721.3,44773.3,8640.12,110.234,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8610.02,42544.2,90679.1,133535,163447,184109,191149,185567,167616,137363,95509.1,45888.5,9249.78,110.533,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8316.31,43254,92881.8,135520,165854,185095,192460,187314,170325,139605,97481,46500,8436.13,110.387,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10152.5,43630.4,91415.4,133968,165243,185235,192609,187246,168748,139222,97106.6,46500.2,9084.83,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8881.08,42783.5,89115.3,129843,158829,176390,181890,178120,163583,135337,95079.6,45723.2,10158.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10119.3,42401.2,89271.2,130409,160111,176972,178301,174135,158466,130969,85457.6,43506.2,12389.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9093.95,41885.6,89270,90428.2,161100,177606,183388,178433,160726,122168,74248.1,37702,12638.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9897.52,41542.8,87475.4,127663,158889,180864,186294,181866,164504,134312,93305.9,45832.4,9612.43,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8609.15,42713.2,92749.5,136035,164537,182460,190991,186954,168322,137652,96274.7,46270.6,9107,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10139,39684.7,58743,101443,148670,136162,116748,181092,164873,135638,85440.6,43396.1,9129.08,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8918.38,40847.5,87150.9,128020,158696,178825,186707,181547,164331,135162,93886.1,45696.6,9847.07,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8454.32,41048.1,87877.1,128858,160661,181077,188742,183734,166460,137131,94863.9,45615.3,9744.05,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8601.89,41072.9,88576.5,130378,159780,178595,185829,181099,162900,133697,91751.1,42004.8,11446.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9755.57,38822.5,87011.6,127893,156927,174191,180610,175927,159508,131481,91561.7,38214.9,12233.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5797.02,17359.8,65181.7,126001,155155,174522,182349,180012,162529,133779,93177.5,46158.9,9813.75,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7811.85,24261.6,12004.8,77987.3,129320,150467,174113,187292,167340,137650,95695.5,42027.9,11929.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8837.38,40645.2,88097.4,130229,161902,182668,189594,181820,161012,131163,2333,1860.07,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9696.2,41274.6,88523.5,131201,161033,180501,185265,149466,142152,120995,74153.9,33539.8,11981,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10028.3,32228.4,67196.8,71637.4,49708.5,169562,172218,170097,158755,131831,92844.2,45994.4,9971.42,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9137.17,40822.8,76776.1,132109,164483,185212,192423,186598,167566,136637,94290.6,46059.2,9305.58,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8148.16,29668.3,72303.2,85693.4,163485,182307,189353,183643,166399,134671,88614.4,32672.4,11514.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8672.36,38100.2,51068.4,130199,160325,179441,184828,181952,164481,135798,94587.2,46344.2,9326.71,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9655.65,38083,36166,3944.89,6841.59,96566.9,133868,176694,113495,105351,84927.7,47130.6,9845.89,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7544.71,40500,89016.4,132324,108213,172531,186972,181983,164696,52623.4,94174.8,45795.5,9041.99,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6570.91,37989.3,87978.2,129688,161458,183150,192114,188283,170659,140039,97526.5,45685.6,8845.68,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6323.42,39256.8,88764.1,131171,161796,180732,188156,183550,165676,136662,83112.9,12837.4,4303.48,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8821.13,30781,5042.55,96503.7,58210.8,180137,194103,193355,177035,143748,98921.9,47217.1,9093.71,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8008.61,35164.5,71585.3,103808,142676,180888,187690,56834.3,87296.4,128363,67055.1,32369.7,10750.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7960.72,26452.4,53145.9,111312,143453,165893,140618,178681,161022,132420,91999.8,24765.6,8907.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7527.23,35689.2,87940,108600,127907,180066,187006,181043,161067,131225,92568,45279.9,10474.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7254.52,40534.3,89866.5,133461,165343,184509,191159,185152,168339,138847,97683.7,21153.5,7255.84,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6569.4,12287.9,93098.9,136682,165215,179670,187138,186496,171016,141427,99016.3,47223.4,6875.35,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5760.21,39818.6,89940.5,133131,165772,185156,180726,160840,140938,124407,74881.4,38204,5672.96,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3556.07,19155.7,56751.4,25417.7,17040.4,29409.4,107666,138979,177881,144886,100015,46706.5,7170.03,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6198.75,40513.1,92276.9,136080,170033,191265,199824,195969,177955,146825,102174,48141.4,6708.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5516.93,40853.2,93729.8,136827,162642,177144,187880,185486,167303,138574,96943.8,45688,7045.99,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5904.58,39813.6,91663.4,136021,163485,177184,188412,185408,169010,138962,80256.7,37221.2,9265.18,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5869.75,36853.1,76413.4,129871,158313,175940,186299,184310,168871,137955,94852.6,41973.9,7491.99,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4235.13,21938.7,70850.6,108976,133629,146552,175661,148582,152744,128443,88347,43198.6,8450.92,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6722.8,19221.1,38966,64055.7,139116,184984,191221,184826,164432,134768,92915.1,44135,6432.78,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5518.68,39813.6,90525.4,132312,149908,184197,193807,99393.4,172558,141690,89256.9,44803,7682.14,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6333.65,37016.8,80582.9,114253,148568,184252,181064,189768,172439,142305,97476.6,42374.2,7846.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5828.63,37650.3,83361.2,105215,149711,185808,195029,191647,157481,141300,89146.7,44554.5,7944.89,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6319.11,40015.4,90376.4,133142,161148,177961,187465,185204,167840,137428,86652.1,40756.8,2011.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4413.7,23182.6,82831.2,111322,66685,104331,121929,135543,127859,138174,95146.7,40421.9,6741.13,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5997.68,30611.7,65415.4,107998,166673,187179,175672,191394,174884,130792,90444.1,43152.8,5750.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5003.17,40737.8,93736.8,135756,164728,184374,192766,187937,171189,140951,97677.9,44028.1,5431.09,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4817.1,37737.1,96138.3,140979,172462,188841,191874,183693,166461,137171,94847.1,42982,5510.63,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5089.06,36536.6,95957.1,141716,173829,190788,193921,184046,163399,135621,94920.8,43433.1,5464.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4817.33,41116,94001.5,138945,166033,167650,175736,168021,147244,107918,72653.1,41756,5708.78,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4768.74,40324.3,90965.2,133042,164655,183730,190254,186156,169863,126106,76574.6,16965.3,4569.54,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5143.25,16423,13358.4,34012.4,137963,51233.4,108845,67830.1,68498.8,142654,95677.4,41800.1,5183.83,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4367.5,40497.3,92812,137685,168299,186825,192710,186650,166702,135084,82234.1,37641.3,4578.07,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,18628.2,9552.61,29657,112259,149622,167351,163166,150017,136975,93046.2,40700.8,4626.07,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,329.083,7985.11,37173,98576.6,91095.1,104559,190237,186452,170311,139687,93636.3,19181.7,4539.34,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4712.08,41719.1,95151.1,139168,166954,181249,190193,187244,169430,137392,92769,40354.3,4277.85,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4104.11,43478.5,100510,146620,178168,195334,198260,192322,175367,144133,98192.2,41878.8,3494.12,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4027.01,44820.7,101797,145192,173233,185113,187808,183026,169578,140351,96382.2,40991.5,3216.92,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4095.67,42487.8,98099.1,146007,179246,201700,208199,201916,179373,145465,96406.8,39925.6,2875.01,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4003,40876,93937.4,139750,173767,193257,200759,194120,174945,139659,59850.5,10466.4,2749.51,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3971.68,39605.8,91915.3,136723,168316,186875,192484,185574,166723,134413,47660.1,37846.6,2293.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3739.93,39940.3,91023.5,90113.6,132560,146113,183934,177109,158011,138875,90527.8,36732.1,1855.94,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3465.15,37793.8,69014.2,135716,167169,166427,163874,190738,171018,138524,91620.7,36997.8,1436.57,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3185.47,42860.2,98747.2,142518,171490,181602,187494,186979,170110,138995,92043.4,36910.2,1289.91,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3398.73,41203.5,95595.2,143314,177914,196359,203030,194564,171840,136430,88074.2,33165.6,1297.32,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1101.72,12143.9,50201.6,87787,178804,199404,204810,196099,175688,140677,91727.5,35734,1040.97,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2981.92,41058.1,94754.7,138768,169144,189090,196298,167843,149648,87974.1,9992.46,26100.7,1716.97,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2793.72,34027.6,50132.6,123973,166794,186776,194973,188804,171410,137480,89297.6,34320.6,773.46,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2433.45,42350.6,96241,139969,176237,198761,206149,198394,175382,140223,80014.9,25402.2,471.778,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2409.1,38273.1,81354.6,74938,175590,156933,128780,163017,105556,133863,85259.6,31757.2,805.597,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2313.45,35298.6,58096.9,70821.6,176863,192990,197137,188130,168170,134721,87977.9,34290.2,557.23,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1991.82,44054.9,103769,150566,184340,202223,206170,197439,175661,141010,91224.6,34226.5,254.073,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2004.01,47357.1,107255,155150,187184,204729,208719,199644,177793,142126,92137,33646.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1926.27,45420.5,104478,152121,182656,195249,190649,187937,171998,140011,90161.4,33671.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1783.29,44137.1,104866,150846,177834,196393,205599,198593,177836,142191,91436.8,32645.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1684.24,45265.4,102372,148642,183024,204346,211297,202400,180128,142885,90190.9,31512.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1678.37,44242.7,101664,148047,173652,187582,196674,190703,171683,137965,89237.7,31347.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1689.17,44528.6,102833,150798,185225,203134,207816,200464,179622,143581,91458.7,31628.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1774.37,47874.2,109890,155737,181482,193849,200928,194294,171726,135771,87351.9,30330.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1662.99,47517.6,106896,151984,180208,194559,196395,183059,164306,134731,86677.2,29758.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1510.58,46504.9,106531,150716,178138,194302,201291,191377,171564,136778,86822.9,29699.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1456.81,48442.7,109678,154545,181669,190094,188815,183202,169350,136196,86618,28641.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1404.6,47383.6,106673,150663,180054,197053,202380,122966,140483,96308.2,43197.6,9671.14,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12339.8,41330,94260.9,133396,115327,133839,102310,121727,50322.1,30393.1,2125.98,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,365.027,19980.1,64104.2,26723.3,42360.4,54459.9,54863.3,31002.2,13273.5,14152.6,25598.3,181.442,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10068.4,60533.2,126646,155254,143042,198210,187706,164989,129048,50821.2,24185.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,841.026,45406.8,105480,152033,182535,199337,201268,189744,166698,131193,81464.3,24485.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,699.46,45722.1,106943,155360,188306,205713,209398,198546,173884,135405,81637.6,23601.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,497.656,44494.1,105659,151727,182619,200313,204138,194468,170778,133664,80594.9,23135.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,572.907,45460.3,104813,150107,181084,198665,203655,195185,170800,132891,79600.8,22170.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,43753.3,103331,149632,180328,198268,203115,193939,170284,133046,79457.6,20023.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,42226.3,99405.4,118675,152296,191269,198122,190330,168108,130291,77718.6,20282.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,27336.6,61288.1,111317,10220.5,163906,151543,59751.4,4212.21,4642.97,67434.7,15244.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,47552.1,112530,164855,199785,218018,218018,211843,186390,143505,85144,21335.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,49133.4,113964,163800,196199,211550,212190,200056,174278,135323,79955.1,18693.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,44164.7,106783,155939,187370,203766,207181,196028,173350,133778,59476.5,13806.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,44362.2,104821,127028,192008,206011,207688,197789,174025,135335,79349,18121.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,48337.6,113003,160886,190995,206480,207389,194689,168054,129064,74687.4,16151.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,29618.3,79177.7,135662,159125,191627,187608,178448,158843,122684,70819.1,14272.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,40866.4,99019.5,145215,179194,196326,201312,191038,168274,126951,71935,14308.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,41230.7,102632,151196,184083,203236,206445,196041,171009,129511,73480.3,13950.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,45860.9,108127,155303,186717,201070,202159,190465,165203,126076,70873.1,12499,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,42970.3,104586,150042,139451,196329,105012,134224,169889,129689,75109.5,13513.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,45588.4,109400,158603,187973,199839,200570,190653,167210,128981,73652.9,12083.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,44626.8,106792,153859,184409,199018,199926,189577,166356,128156,72364.8,10664.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,45293.5,108203,155287,184130,195885,202312,192383,167276,128144,71756.3,8880.65,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,44177.1,107469,157229,187789,166711,198854,146988,132337,124746,49331.8,5104.26,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,42948.5,107554,158972,192815,210133,211417,197549,172325,129537,70420.8,7520.35,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,42410.3,105788,154795,184396,198941,201364,189574,165695,123868,66883.3,6030.55,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,41066.4,105869,157472,190953,207964,211292,198570,173007,129915,70597.1,7057.73,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,46245.9,112764,161170,193401,209070,210378,196415,168722,124298,66870.4,5748.69,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,39949.5,101957,148182,177431,192176,193554,180589,157518,119715,65394.7,5694.56,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,38142.6,98400.5,145012,173728,186406,188752,180088,156290,116436,60272.2,3684.86,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,38274.5,94273.1,133360,158519,156091,193246,183491,160191,119558,62580.2,3266.41,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,25941.5,77509.9,103594,95933.8,114830,141269,104016,79172.9,23973.5,10529.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,34855.3,97344.2,147023,179788,193806,194238,182771,157858,117092,61056.8,2667.23,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,38300.7,100468,146688,172687,190985,194177,183192,158916,119179,62582.9,3001.63,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,21623.2,61234.1,131807,149560,140180,135191,130687,119040,89359.9,44515.8,336.368,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,28049.9,33590.4,97496.9,56209.9,139551,161777,178959,155770,69781.1,34711.3,179.374,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,37983.5,100167,147759,175482,189075,190914,180258,156872,116082,59384.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,36125.1,73726.5,130108,154403,188723,160476,131787,155114,96188.7,46180.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,34395.9,92779.1,139114,153664,151594,129471,139658,161849,70377.6,32654.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,39604,107667,158123,188238,203983,204847,189950,162155,85886.9,42510.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,19635.4,104852,157933,140661,209142,167805,160509,131134,94302.2,42943,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,85.5803,15153.1,27581.8,39252.6,49816.7,83581.1,116476,49504.1,114204,55231.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,34929.2,102360,155417,189547,206718,209288,196654,169330,123218,60842.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,36979,106333,159753,191453,207076,205330,190884,162769,121362,61902.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,36657.7,99795.6,121956,149900,154786,177300,164836,166519,64409,7740.87,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,33716.3,100944,107780,156635,202493,181261,158943,132614,114853,28909,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,17865.6,98088,108129,177185,177238,197497,187673,139286,86985.3,42994.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,20724,83344.2,127980,156861,167218,130904,149806,109117,81410.6,41688,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10672.8,43496.2,76223,123767,70950.3,77951.5,39151.7,49530.7,44905.8,28524.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,26190.6,92853.1,147043,183607,200763,204121,194349,164379,118487,54913.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,28797.1,98683.2,151631,185272,202453,204987,192098,165121,120308,57888.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,31742.6,104198,157599,191463,207173,208767,195495,166399,121698,58733.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,28924.6,99454.5,150955,185496,202591,205166,192291,162705,118021,55930.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,28257.9,104353,161962,200372,218018,218018,208118,177351,129537,62456.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,28745.6,104267,159107,195308,213254,215612,201601,169412,123173,58512.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,25584.4,101106,156829,190864,208886,212267,198624,168151,122142,57828.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,26888.3,105024,160348,197128,216239,218018,206427,174460,126950,60367.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,24154.7,101529,155459,190470,207268,210444,197038,165756,120211,56939.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,21113.7,99571.7,154626,190508,208632,212450,199585,169520,121234,56588,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,15179.2,83686.7,108589,147761,160679,184915,149685,168256,120990,56456.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6873.12,96262.3,102840,118519,151114,143868,146326,135946,87122.3,43331.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2063.13,35979.9,59825.5,88442.7,41693.6,92310.3,36028.2,113730,33427.2,26510.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11167.9,81992.8,137047,171897,191518,194175,181910,157019,112605,51730.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,14897.4,91961.2,147799,180814,198234,201278,190278,162837,106711,44925,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,123.971,41312.2,120323,178982,194527,164938,190972,167629,118604,51352.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2102.1,47102.4,101380,203134,218018,218018,213442,179679,130324,60160.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,17218.5,101960,160154,199584,218018,218018,208884,176549,128796,59686.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12755.2,92037.2,149918,184953,204778,208165,195040,166753,121075,14408.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12380.1,91340.6,149883,185223,205425,208528,196677,167962,122240,56453.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6076.57,80479.6,138183,176307,194716,197266,185420,154522,109513,47009.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5435.76,79095.9,134995,170759,184716,185233,174094,156307,116332,38309,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7120.88,81188.9,102155,149802,190981,193811,181506,154526,109769,47798.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,682.698,37117.9,67656.8,170942,184932,186364,176968,91692.4,112597,51931.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,281.147,26514.6,136635,112159,191409,195555,183960,159709,114853,52748.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,285.036,36631.5,71945,110881,148570,195510,142773,87649.1,53136.4,13920.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5333.98,79324.1,137444,174926,193759,197721,186344,160531,115135,52710.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4328.23,78827.6,137852,174765,192774,195820,185801,162957,119141,55263.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,77874.6,134588,173687,194882,201719,192664,166053,120645,35327.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,88314.8,148822,189508,211258,217727,206453,174752,128163,60403.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,85226.6,144284,180851,195810,199787,188459,164965,121947,27460.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,81058.7,141857,106732,150899,204655,195146,167944,121384,56220,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,69867,41326.7,107086,150688,98466.8,78496,64568.9,31639.3,11894.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,74355.2,69924.2,180344,202943,209971,199708,8305.32,121357,26631.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11453.4,697.337,14954.3,32908.6,58433.9,39950,62983.1,4005.56,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,72110.9,132088,172948,190741,196591,189857,166130,121963,12513.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,72784,133682,173002,191892,197684,188895,162909,120031,56278.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,24795,131429,98841.2,119799,135305,55134.1,19924.2,18149,4406.98,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,74850.3,141822,188709,214148,218018,211808,182898,136128,67295.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,83634.1,147706,189734,209616,216098,205605,177213,87382.9,28450,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,78151.6,142700,182013,202851,206831,196730,172080,77919.9,18817.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,67662.5,128340,168255,181884,187758,118570,115776,33178.7,63581.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,65261.3,129339,171217,193989,199518,189551,167251,57764.6,14644.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3977.68,128207,173004,198021,205380,197410,166263,119820,54638.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4852.4,68654.6,115649,103865,71208.2,144216,75970.7,60232.1,21766.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7817.93,78360.5,122264,125264,134708,134060,174427,129168,64474.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12658.6,61051.3,57956,142078,207122,120206,174219,130066,67130.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,73988.7,139671,181274,203524,209588,199472,174665,131612,69489.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,71950.4,136836,179890,198522,201623,115337,102347,73263.1,32141.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1248.86,23551.1,16373,47739.2,92958.6,49453.4,48978.6,26609.3,2960.89,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,61584.8,127540,174760,200209,208197,200346,114106,132401,68428.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,]
            self.simu_output = self.LSRRO.simulation(gen = self.elec_gen, storage = 0)
            
        elif desal == 'COMRO':
            from DesalinationModels.COMRO import COMRO
            self.COMRO = COMRO(FeedC_r =self.desal_values_json['FeedC_r'], Capacity =self.desal_values_json['Capacity'],rr =self.desal_values_json['rr'])
            self.design_output, self.costout = self.COMRO.design()    
            # self.elec_gen = [-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,72194,136206,176233,197079,204039,195293,171973,130436,69934.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,69048.1,133852,175627,197064,204295,195206,171042,128602,69736,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,66516.3,128523,168840,191720,151406,27467.4,59413.4,129702,70691.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,71632,135347,176669,195393,202545,194654,170036,130602,71796.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,67979.5,132465,172146,194957,202610,195311,171386,132376,73019.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,65354.6,128417,169407,190185,197398,189568,169133,130056,72226.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,63278.7,126755,169210,194244,200852,193373,170553,129234,69846.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,61123.9,129039,177996,207620,217510,210709,184785,140171,77497.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,20679.8,129764,171536,194663,203310,128786,173341,132605,61115.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,65770.3,128604,168713,187913,194236,139816,172317,79087.7,75547.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,22808.8,87293.4,79394.8,113069,157487,123088,119524,102290,30764.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,306.399,19929.8,98003.6,146541,46994.3,74659.9,56914,71632.8,78123.2,3133.06,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,76549.2,142292,184714,205758,214007,206546,183377,143148,84188.2,6508.65,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,21245.5,67577.5,175438,142856,166737,178359,113011,23177.8,3828.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,482.889,23292.6,18238.5,45077.9,14202.4,61749.9,36968,26709.9,5096.19,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12504.1,124001,168605,125223,153278,133761,104365,130919,72564.3,3557.48,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,64617.3,129090,173992,196044,204706,197267,172028,134591,76934.1,4660.33,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,65900.5,129732,172066,191619,200361,193842,173878,135258,79061.5,5889.36,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,63489.5,128136,170960,191588,198069,189537,171951,137356,83491.1,9572.14,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,66167,129871,171601,191662,201052,195255,177149,138070,82069.2,9999.27,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,17135.1,46552.2,84222.6,48290.1,48621.3,38387.5,126839,133930,72520.4,1811.78,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,69501.5,78260.2,109660,107672,151846,111293,91166.5,32452.7,37143.1,1026.19,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,31255.5,129869,112328,81188.6,90537.7,99120.6,116150,26704.4,14707.5,1043.22,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,67295.8,133997,182288,208330,218018,213934,190494,148884,89043.7,12856.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,72251.9,138563,186053,212754,218018,217034,192630,151733,91917.3,14870.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,69144.4,133324,174365,194789,203816,198489,179550,143106,88496.5,13666.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,18906.2,88754.1,92584.9,110405,83246.3,110431,119019,74212.2,19389.6,1144.88,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,72063.3,138915,184028,209693,218018,214853,191921,151431,93879.9,18250.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,71442.9,137768,180906,205072,215924,209861,187334,147888,92624.9,18586.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,70929.8,134328,172477,196246,204318,196760,180257,148103,92818.9,20038.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,13419.4,128693,68540.3,199141,206266,201988,183473,146261,91198.1,12806.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,79912.6,146990,194354,218018,218018,218018,201153,159590,101574,26723.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,74113.9,139183,182034,204824,214402,209892,189821,151779,95419.1,25503.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,73781.5,137485,179928,159858,215084,209313,187610,113958,78286.7,27064.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,74950.5,137283,178786,201662,211055,204861,184849,147847,95769.2,29269.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,74541.7,134062,174637,197391,207661,203647,184028,147895,97475.1,29730.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,552.431,72415.2,134632,126322,202342,213265,177546,187403,127882,73283.5,18775.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1689.61,69076.6,133260,179234,208674,218018,211204,190430,151185,92404.2,24333.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,440.261,48758.5,84788.1,105990,218018,218018,166657,155130,159315,99953.8,30573.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3918.71,75877.9,141907,190178,218018,218018,218018,203453,164639,106147,33858.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2138.02,78509.6,141136,182596,175619,194095,208062,138357,152924,99025.7,26579.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5053.21,76754.3,140159,181325,203157,212340,209261,191460,158775,104699,34727.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7318.33,78720.8,140579,184902,214282,218018,218018,200330,161708,105895,35210.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7193.53,78660.3,143878,188678,171148,122624,36564.9,15149.9,130101,66212.1,14428.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1850.91,6463.8,57690.4,96034.3,55859.9,138293,5029.94,159026,160510,7633.73,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8355.39,81048.4,145145,188757,212845,218018,214643,195486,159765,106673,37970.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1820.61,35532.1,85436.5,116015,146874,161280,187354,199078,163843,108375,39442,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8821.48,64661.5,94617,142461,189356,128661,103364,90369.4,60244.7,58245.9,12458.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1889.37,57251.3,142062,181208,199587,210381,210233,193140,159797,106067,38151.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10718,83108.2,144968,185356,207966,214259,208165,192183,157129,103542,35827.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9184.04,77925.9,137940,179727,204976,212016,206083,189269,157840,105853,39099.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12401.5,81850,142156,184891,174844,218018,213398,194009,158354,103113,36787,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9592.53,44421.1,136134,145078,165440,174961,159751,136855,117971,50049,34522.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,18246.3,14622.5,145381,218018,218018,218018,209350,169473,84919.1,37962.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,16302.9,85042.5,146371,191806,218018,218018,190612,202112,133683,79788.1,21718.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1413.08,21814.4,87725.5,104511,168646,159842,120836,106946,63933.2,27836.2,5895.99,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1272.24,39256.1,146083,129739,151975,184694,53536,102291,162231,107346,41317.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,18759,84661.3,104596,147775,186490,124092,126089,7546.45,51151,28369.2,7067.55,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10817.2,62815.1,118454,48519.8,30159,122248,11183.1,10181.4,77488.3,20840.5,42208.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6681.81,39049.2,103541,150307,203950,213848,190570,171868,157057,104552,39745.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,21718.8,91054.2,148734,185309,173574,175143,208805,190255,157647,107107,17587.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,22954.6,89798.4,147166,187265,213540,218018,218018,199373,164278,97878.4,42936.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5332.79,58843.6,93110.1,136741,168022,185804,184682,151158,123829,108202,41997.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,22526.6,90684.5,148828,186710,208251,213719,204531,188282,157623,108431,44159.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,24328.1,91261.8,150264,191089,217460,218018,218018,203743,166121,112194,44372.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,23416.1,89303.1,9365.84,26304.3,8203.89,53311.9,27402.8,36815.7,83736.9,47344.8,131.623,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,24253.7,91546,149048,192121,218018,218018,218018,204148,166456,112426,28048.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,26355.9,95022.8,153670,195120,218018,218018,218018,199235,163495,110817,44771.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9483.66,69627.9,155096,193392,215656,218018,215735,196609,162152,109200,44396.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,26480.8,91713.1,151276,193761,218018,218018,218018,204303,163757,94679.5,35932.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,27911,95739,156957,201687,218018,218018,218018,206757,167598,111454,44417.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,30438.8,97694,152319,186489,212651,218018,218018,200350,164598,110726,45041.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,30957.2,96895.6,152304,192922,190776,199910,192867,133075,127195,7046.92,21789.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,15672.1,24423.5,83997.9,187532,218018,218018,218018,205796,165469,109371,42968.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,309.589,55158.5,3707.47,24595.9,54914,55293.6,85244.9,91722.4,135601,2548.55,7097.21,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,18672.9,29926.2,20966,67331.6,37418.7,63284.7,104043,150903,156313,75826.1,20889.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,32161.1,97319.5,153254,194516,218018,218018,218018,198879,162548,108322,43540.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,33030.8,98077.7,154225,193969,218018,218018,218018,199513,147804,108885,44036,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,33700.7,77740.9,122793,183976,208162,218018,216170,195017,159145,108408,45255.3,586.536,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,36136.1,103121,159382,198387,218018,218018,218018,197715,160700,108617,45401.7,729.028,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,36575.8,102688,157395,191539,209049,217917,215087,196564,162265,109303,45453.6,837.945,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,34369.9,98446.5,155706,197115,218018,218018,218018,196151,158778,105594,43340.5,828.748,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,35597.4,99039.4,151724,184571,202895,213274,208679,189202,155363,104491,43079,946.393,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,31025.4,42695.6,128192,179162,187343,218018,188922,131674,52454,25723,23808.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1209.97,33777.3,63519.3,130012,143491,110753,78168.8,41371.5,92283.5,66653.4,42680.7,1475.79,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,37207.6,100243,154599,193999,216821,218018,216486,195371,158284,106029,44076.1,1360.23,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,38620.1,101680,153557,190068,212969,218018,211387,191266,156413,105953,44059.8,1266.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,549.145,38728.9,99037.6,150372,187457,212225,218018,214678,192163,155245,102110,41416.4,1080.34,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,545.611,37986.4,99518.5,151758,187426,205787,214761,209161,186839,153539,103605,42041,1500.69,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,816.877,39155.2,102632,157600,197470,218018,218018,218018,197479,158572,103609,43080.8,1381.95,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1199.68,41311.8,103251,151845,182723,198238,209549,206295,188030,154320,103011,43161.6,1515.82,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1101.1,39169.5,98151.4,147924,181099,197552,203459,172716,122281,93878.1,89787.2,22014,1673.09,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1821.71,37940.6,101755,153407,188171,206636,212368,208079,190171,153926,101526,41360,2000.96,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1793.75,46839.3,115055,170973,209451,218018,218018,218018,199353,161732,109562,46283.6,1782.65,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1773.01,45425.8,107013,152808,185442,204706,211011,186797,165044,147221,83283.1,34902.7,1930.78,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1385.44,5338.96,46418.7,86899.6,96922.9,39602.8,31533.4,64673.8,3850.11,91224.8,6185.57,25669,972.472,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,883.086,25810.8,103780,154373,192347,215482,147574,215281,195222,157503,105032,43990.4,2421.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2423.75,25520.4,73252.2,103033,193248,170255,189591,211131,159111,117985,78534.1,21759.7,2837.59,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11964.3,2429.09,21536,60419.4,64712.1,87204.7,82648,127371,163228,109902,46536.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3671.46,49365,113912,165632,199544,216267,218018,218018,196950,159100,106464,44920.5,3325.08,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3969.65,49953.2,113890,165146,198595,214990,201255,213047,194189,159943,108078,45580.4,3236.68,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,45600.8,109602,159977,192001,206700,208375,199768,181744,148068,99469.3,42633.9,3262.32,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4667.02,46866.3,106353,155959,190372,208711,214142,210486,194724,157744,104641,43357.2,4169.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5682.71,49887.2,112457,166218,205409,218018,218018,218018,196811,157607,104516,44247.1,4280.93,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5550.08,49667.2,111311,163410,198152,217794,218018,212282,190205,153640,102227,43301.7,3819.07,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5511.36,49165.7,109604,159559,193215,210651,215592,207389,184006,149493,99548.1,41874.6,3831.08,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5396.35,47762.1,105423,152340,184605,203272,210037,202446,186921,149144,97545.7,40734.5,4537.67,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6083.16,44870.1,106348,153695,185401,205640,211935,203770,182750,149088,69189.1,29555.1,309.89,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6823.19,47487.6,105088,152832,184795,184080,204660,195852,163527,135397,71811.6,35741.3,4991.66,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7073.41,48645.9,105408,151282,148399,192043,182548,169369,176687,145860,99101.6,42149.4,4598.87,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6621.09,49476.6,108812,158157,192140,210770,217938,209586,187302,150016,99480,42401.4,4945.87,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6764.54,50105,108947,157032,188567,206319,211930,204259,182947,148661,99323.2,41937.3,4586.73,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3880.33,12629.6,34679.5,153084,154204,192506,191007,160362,146922,121045,75670.1,36029.7,5328.24,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8317.4,48852.7,105706,154039,188971,206265,213250,206918,186394,133362,91014.7,41482.7,6356.18,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9179.73,49863.5,107106,155561,187596,206169,210366,201682,180645,146315,97189.7,41947.5,6337.84,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8327.81,52767.5,113325,164888,200460,216832,218018,214445,190811,153540,101803,43613.8,5205.31,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6755.36,54654.2,116117,165438,198852,216110,218018,207730,185810,151157,102127,43003.6,4392.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7174.33,52660.1,110109,155450,190249,206867,210701,199777,176716,142316,95076.8,41816.6,5474.34,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8219.88,52302.7,110823,160109,194239,215316,218018,212461,189459,152316,101631,43104.5,5686.42,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9483.75,55820,117312,168768,205978,218018,218018,218018,198800,158025,105257,41524.3,6080.15,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9679.12,51938,108105,154923,188795,208014,214176,207066,186739,149345,99253.4,42743.8,6392.28,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9468.72,53384.4,109419,153322,180650,197505,200172,191163,174087,144081,96832.5,42204.8,6610.78,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9628.29,46466.3,115491,168184,204727,218018,218018,218018,197467,158683,105911,44728.1,6348.97,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9398.96,55219.5,113977,162440,196341,216281,218018,211019,188574,152839,101498,43183,6062.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9168.62,53828.8,110831,157463,192131,213331,218018,211165,188773,151779,101241,43112.3,6191.65,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11149.7,53320,108999,153274,186163,208269,214311,205881,184460,147159,98011.5,41785.7,6416.79,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10628.3,52856.8,107704,149772,178296,196377,200941,192510,172541,139741,94208.4,40699.5,5924.34,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9414.34,52758.6,107123,150921,179073,190385,187610,186964,171611,139709,94472.3,40717,6000.67,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10055.3,51541.3,102587,144377,175571,195331,202724,195916,176283,142930,95239.6,41462.4,6612.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10678.2,52041.4,104567,148411,180177,200184,206280,198177,177319,143003,94873.2,41354.4,6461.88,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10246.9,52261.5,105782,150819,181389,199772,205532,197923,177246,142761,94955.5,41311.6,6736.86,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11694.2,51613.9,103779,147495,179249,196714,201697,192911,170885,136161,70523,30180.2,3689.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10502.6,50787.5,101056,142764,171018,124894,189845,173985,157984,120949,89453.2,37864,8007.04,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11809.4,52328.2,104653,147929,179193,198468,204994,198572,177396,143823,96362.2,39656.1,8385.71,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10336,52805.7,107218,152081,184803,204770,211188,204055,182856,147223,98782.3,42496,8360.79,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9379.59,53874.6,108280,151535,182243,200575,207325,200829,181665,147653,99460.2,42977.8,5498.76,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8685.24,52685.4,103722,124765,171121,179005,137500,192108,173940,140896,94666.4,40713,6109.05,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10579.3,51183,99750.1,53187.6,175368,194600,155941,131260,124058,5234.34,74564.4,28330.2,8825.34,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,16046.5,22813,99959.4,152517,72611,135853,139824,146830,63082.1,30217.8,157.007,7200.62,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10778.5,51379.1,103718,146920,176316,192299,193645,184595,165616,135884,91310.3,40298.3,7169.85,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10297.5,52134.1,105667,147496,174131,187846,186745,179501,163116,133913,91662.4,40802.7,5846.67,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9283.52,52912.2,105275,147142,174899,189379,191862,186177,169365,138895,94514.4,41644.9,5616.96,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8732.69,53076.9,105845,146828,173496,188187,194441,189486,170997,139395,94759.7,41594.8,5631.58,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9103.21,52012.4,103396,142181,170718,191990,199826,193449,174010,140706,94734.2,41545.9,6275.69,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10131.1,50755.2,101934,144720,176222,195051,201465,195819,176286,142623,95873.5,41626.6,6816.17,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10102,33721.9,102064,144865,175788,184424,187772,185651,166655,142231,95439.8,38607.5,6470.87,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8340.25,48129.4,78658,124744,150993,169166,174687,167350,115652,47946.8,54575.2,30385.3,1043.93,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11682.5,53957.1,107934,152600,181978,198798,203849,196222,176211,142001,95830.3,42247.7,6810.81,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,266.851,10509.3,51898.8,103485,143211,172413,191256,196533,188980,169396,137264,81466,39949,8943.15,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,364.874,10713.5,50936.8,103051,145576,174182,191596,196948,189426,169488,137319,92525.1,41326.5,7871.94,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,364.642,10217.7,50555.9,101738,142367,171037,189043,195747,190227,172249,139556,94448.4,42064.8,7428.57,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,496.175,9496.02,50428,101182,140770,167362,183807,190549,163278,167740,136376,93067,42207.9,7533.28,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,195.269,10893.6,49861.9,100567,143592,173235,190819,196823,191140,171044,139074,93940,42434.1,8047.04,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,485.118,9286.21,50946.5,102792,146048,176660,194387,199743,192971,173582,141283,95961.9,43151,7968.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,735.885,9140.91,49397.7,99498,140157,170107,187629,193193,187064,166204,135764,92652.3,42963.7,9129.65,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,232.421,11738.8,50689.7,100405,141384,168512,179649,185710,182931,166304,136244,93853.5,42643.7,7427.01,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,473.217,9475.04,49535.6,101042,141312,167133,178143,184901,183247,164423,134374,91570.2,42879.5,9978.26,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,340.49,11679.3,48952.1,96956.2,135305,162432,180552,188942,184238,167845,136719,93485.2,42409.1,7823.27,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,459.55,9807.41,49431.1,101597,145838,177791,198062,203314,194971,173299,139407,93822.5,44078.7,10073.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,472.077,10485.3,49086.1,100175,142485,170973,187779,194939,189398,173599,141097,96092.6,43952.1,7099.21,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,590.946,9068.36,49613.8,100402,141835,172646,172325,198765,192538,172286,139341,94252.2,43943.2,9021.39,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,473.087,10551.2,48570.6,98098.5,135633,157516,175301,180388,174363,159414,131525,91465.2,43217.5,8758.04,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,425.546,9895.62,47458.7,97134.6,138377,156013,162280,182381,180869,165704,134252,91849.6,43836.3,9460.82,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12781.8,47830.3,94929.9,88712.4,128025,172512,176069,164621,151475,126284,88549.6,43356.7,9811.12,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,13373.7,47587.5,92791.1,131518,161459,184006,191135,185887,167559,137513,94437.9,43798.9,8188.93,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,443.398,10704.7,46944.5,94044.8,133987,161768,178575,184302,178140,159991,130412,89962.8,43852.4,10474.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,459.209,10235.1,47148.7,96771.9,138104,164470,173274,179288,178248,163283,135401,93736.5,44209.1,8742.36,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,443.853,7919.04,48451.2,100874,141789,166478,181339,192479,188617,171026,140553,97077.1,45580.9,7816.45,204.601,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,458.874,9288.53,48015,99405.6,139279,168488,188366,195186,189355,173676,142465,98821.6,46606.9,7532.06,361.604,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,485.545,9851.93,48879.9,101212,143926,172030,187189,188731,179315,162130,133882,93303.2,44840.4,9728.02,97.7281,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,496.538,8890.65,47570.6,99098.6,139294,165354,182209,191000,188062,170143,139574,96836.1,46019.1,9328.35,99.1062,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,364.279,9558.41,47615.9,98862.4,126505,153516,176444,172847,121119,171060,140451,96466.8,46344.2,10310.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,340.095,9335.49,44427.1,86467.8,139886,134676,143001,141077,161584,168082,138196,96370.7,45662.2,9507,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,232.237,10066.2,46804,96411.2,137110,167934,188805,196762,191389,174069,141969,97915.2,46423.2,9367.78,362.168,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,353.106,8554.65,46305.4,96574.5,135803,162039,165642,187957,162782,136088,134413,93320.2,45410.3,9946.12,361.604,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,496.538,7829.02,46352.5,98000.7,139849,166617,176030,175763,171909,160170,134127,94727.5,46272.1,9781.17,177.241,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,221.486,8167.58,47282.6,99461.8,144037,177023,196926,203874,197233,176806,143798,99688.9,47061.5,8445.57,310.361,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8566.92,45675.7,95469.4,134953,163412,181510,188351,182170,165823,134835,93396.9,46091.2,9937.63,176.396,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10064.7,44785.4,93495.3,135173,163101,177137,180552,174126,155759,125593,85327.5,45025.4,8897.25,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2585.13,37785.9,85219.5,82871.3,155613,169645,177119,171845,155091,126262,87506.1,44707,10498.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9919.98,44121.7,86380.3,124241,154436,176530,183187,177702,156699,127517,69061,46592.4,8671.42,108.939,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9008.47,45774.9,97483.7,140628,172077,191872,198465,193060,172664,141313,97928.7,46486.1,8708.07,277.083,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7700.79,43948.9,94589.6,136950,166793,182507,187217,181516,165158,134947,93721.3,44773.3,8640.12,110.234,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8610.02,42544.2,90679.1,133535,163447,184109,191149,185567,167616,137363,95509.1,45888.5,9249.78,110.533,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8316.31,43254,92881.8,135520,165854,185095,192460,187314,170325,139605,97481,46500,8436.13,110.387,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10152.5,43630.4,91415.4,133968,165243,185235,192609,187246,168748,139222,97106.6,46500.2,9084.83,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8881.08,42783.5,89115.3,129843,158829,176390,181890,178120,163583,135337,95079.6,45723.2,10158.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10119.3,42401.2,89271.2,130409,160111,176972,178301,174135,158466,130969,85457.6,43506.2,12389.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9093.95,41885.6,89270,90428.2,161100,177606,183388,178433,160726,122168,74248.1,37702,12638.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9897.52,41542.8,87475.4,127663,158889,180864,186294,181866,164504,134312,93305.9,45832.4,9612.43,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8609.15,42713.2,92749.5,136035,164537,182460,190991,186954,168322,137652,96274.7,46270.6,9107,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10139,39684.7,58743,101443,148670,136162,116748,181092,164873,135638,85440.6,43396.1,9129.08,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8918.38,40847.5,87150.9,128020,158696,178825,186707,181547,164331,135162,93886.1,45696.6,9847.07,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8454.32,41048.1,87877.1,128858,160661,181077,188742,183734,166460,137131,94863.9,45615.3,9744.05,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8601.89,41072.9,88576.5,130378,159780,178595,185829,181099,162900,133697,91751.1,42004.8,11446.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9755.57,38822.5,87011.6,127893,156927,174191,180610,175927,159508,131481,91561.7,38214.9,12233.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5797.02,17359.8,65181.7,126001,155155,174522,182349,180012,162529,133779,93177.5,46158.9,9813.75,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7811.85,24261.6,12004.8,77987.3,129320,150467,174113,187292,167340,137650,95695.5,42027.9,11929.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8837.38,40645.2,88097.4,130229,161902,182668,189594,181820,161012,131163,2333,1860.07,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9696.2,41274.6,88523.5,131201,161033,180501,185265,149466,142152,120995,74153.9,33539.8,11981,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10028.3,32228.4,67196.8,71637.4,49708.5,169562,172218,170097,158755,131831,92844.2,45994.4,9971.42,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9137.17,40822.8,76776.1,132109,164483,185212,192423,186598,167566,136637,94290.6,46059.2,9305.58,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8148.16,29668.3,72303.2,85693.4,163485,182307,189353,183643,166399,134671,88614.4,32672.4,11514.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8672.36,38100.2,51068.4,130199,160325,179441,184828,181952,164481,135798,94587.2,46344.2,9326.71,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,9655.65,38083,36166,3944.89,6841.59,96566.9,133868,176694,113495,105351,84927.7,47130.6,9845.89,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7544.71,40500,89016.4,132324,108213,172531,186972,181983,164696,52623.4,94174.8,45795.5,9041.99,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6570.91,37989.3,87978.2,129688,161458,183150,192114,188283,170659,140039,97526.5,45685.6,8845.68,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6323.42,39256.8,88764.1,131171,161796,180732,188156,183550,165676,136662,83112.9,12837.4,4303.48,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8821.13,30781,5042.55,96503.7,58210.8,180137,194103,193355,177035,143748,98921.9,47217.1,9093.71,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,8008.61,35164.5,71585.3,103808,142676,180888,187690,56834.3,87296.4,128363,67055.1,32369.7,10750.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7960.72,26452.4,53145.9,111312,143453,165893,140618,178681,161022,132420,91999.8,24765.6,8907.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7527.23,35689.2,87940,108600,127907,180066,187006,181043,161067,131225,92568,45279.9,10474.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7254.52,40534.3,89866.5,133461,165343,184509,191159,185152,168339,138847,97683.7,21153.5,7255.84,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6569.4,12287.9,93098.9,136682,165215,179670,187138,186496,171016,141427,99016.3,47223.4,6875.35,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5760.21,39818.6,89940.5,133131,165772,185156,180726,160840,140938,124407,74881.4,38204,5672.96,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3556.07,19155.7,56751.4,25417.7,17040.4,29409.4,107666,138979,177881,144886,100015,46706.5,7170.03,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6198.75,40513.1,92276.9,136080,170033,191265,199824,195969,177955,146825,102174,48141.4,6708.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5516.93,40853.2,93729.8,136827,162642,177144,187880,185486,167303,138574,96943.8,45688,7045.99,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5904.58,39813.6,91663.4,136021,163485,177184,188412,185408,169010,138962,80256.7,37221.2,9265.18,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5869.75,36853.1,76413.4,129871,158313,175940,186299,184310,168871,137955,94852.6,41973.9,7491.99,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4235.13,21938.7,70850.6,108976,133629,146552,175661,148582,152744,128443,88347,43198.6,8450.92,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6722.8,19221.1,38966,64055.7,139116,184984,191221,184826,164432,134768,92915.1,44135,6432.78,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5518.68,39813.6,90525.4,132312,149908,184197,193807,99393.4,172558,141690,89256.9,44803,7682.14,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6333.65,37016.8,80582.9,114253,148568,184252,181064,189768,172439,142305,97476.6,42374.2,7846.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5828.63,37650.3,83361.2,105215,149711,185808,195029,191647,157481,141300,89146.7,44554.5,7944.89,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6319.11,40015.4,90376.4,133142,161148,177961,187465,185204,167840,137428,86652.1,40756.8,2011.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4413.7,23182.6,82831.2,111322,66685,104331,121929,135543,127859,138174,95146.7,40421.9,6741.13,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5997.68,30611.7,65415.4,107998,166673,187179,175672,191394,174884,130792,90444.1,43152.8,5750.38,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5003.17,40737.8,93736.8,135756,164728,184374,192766,187937,171189,140951,97677.9,44028.1,5431.09,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4817.1,37737.1,96138.3,140979,172462,188841,191874,183693,166461,137171,94847.1,42982,5510.63,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5089.06,36536.6,95957.1,141716,173829,190788,193921,184046,163399,135621,94920.8,43433.1,5464.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4817.33,41116,94001.5,138945,166033,167650,175736,168021,147244,107918,72653.1,41756,5708.78,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4768.74,40324.3,90965.2,133042,164655,183730,190254,186156,169863,126106,76574.6,16965.3,4569.54,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5143.25,16423,13358.4,34012.4,137963,51233.4,108845,67830.1,68498.8,142654,95677.4,41800.1,5183.83,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4367.5,40497.3,92812,137685,168299,186825,192710,186650,166702,135084,82234.1,37641.3,4578.07,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,18628.2,9552.61,29657,112259,149622,167351,163166,150017,136975,93046.2,40700.8,4626.07,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,329.083,7985.11,37173,98576.6,91095.1,104559,190237,186452,170311,139687,93636.3,19181.7,4539.34,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4712.08,41719.1,95151.1,139168,166954,181249,190193,187244,169430,137392,92769,40354.3,4277.85,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4104.11,43478.5,100510,146620,178168,195334,198260,192322,175367,144133,98192.2,41878.8,3494.12,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4027.01,44820.7,101797,145192,173233,185113,187808,183026,169578,140351,96382.2,40991.5,3216.92,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4095.67,42487.8,98099.1,146007,179246,201700,208199,201916,179373,145465,96406.8,39925.6,2875.01,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4003,40876,93937.4,139750,173767,193257,200759,194120,174945,139659,59850.5,10466.4,2749.51,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3971.68,39605.8,91915.3,136723,168316,186875,192484,185574,166723,134413,47660.1,37846.6,2293.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3739.93,39940.3,91023.5,90113.6,132560,146113,183934,177109,158011,138875,90527.8,36732.1,1855.94,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3465.15,37793.8,69014.2,135716,167169,166427,163874,190738,171018,138524,91620.7,36997.8,1436.57,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3185.47,42860.2,98747.2,142518,171490,181602,187494,186979,170110,138995,92043.4,36910.2,1289.91,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3398.73,41203.5,95595.2,143314,177914,196359,203030,194564,171840,136430,88074.2,33165.6,1297.32,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1101.72,12143.9,50201.6,87787,178804,199404,204810,196099,175688,140677,91727.5,35734,1040.97,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2981.92,41058.1,94754.7,138768,169144,189090,196298,167843,149648,87974.1,9992.46,26100.7,1716.97,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2793.72,34027.6,50132.6,123973,166794,186776,194973,188804,171410,137480,89297.6,34320.6,773.46,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2433.45,42350.6,96241,139969,176237,198761,206149,198394,175382,140223,80014.9,25402.2,471.778,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2409.1,38273.1,81354.6,74938,175590,156933,128780,163017,105556,133863,85259.6,31757.2,805.597,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2313.45,35298.6,58096.9,70821.6,176863,192990,197137,188130,168170,134721,87977.9,34290.2,557.23,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1991.82,44054.9,103769,150566,184340,202223,206170,197439,175661,141010,91224.6,34226.5,254.073,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2004.01,47357.1,107255,155150,187184,204729,208719,199644,177793,142126,92137,33646.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1926.27,45420.5,104478,152121,182656,195249,190649,187937,171998,140011,90161.4,33671.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1783.29,44137.1,104866,150846,177834,196393,205599,198593,177836,142191,91436.8,32645.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1684.24,45265.4,102372,148642,183024,204346,211297,202400,180128,142885,90190.9,31512.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1678.37,44242.7,101664,148047,173652,187582,196674,190703,171683,137965,89237.7,31347.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1689.17,44528.6,102833,150798,185225,203134,207816,200464,179622,143581,91458.7,31628.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1774.37,47874.2,109890,155737,181482,193849,200928,194294,171726,135771,87351.9,30330.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1662.99,47517.6,106896,151984,180208,194559,196395,183059,164306,134731,86677.2,29758.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1510.58,46504.9,106531,150716,178138,194302,201291,191377,171564,136778,86822.9,29699.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1456.81,48442.7,109678,154545,181669,190094,188815,183202,169350,136196,86618,28641.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1404.6,47383.6,106673,150663,180054,197053,202380,122966,140483,96308.2,43197.6,9671.14,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12339.8,41330,94260.9,133396,115327,133839,102310,121727,50322.1,30393.1,2125.98,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,365.027,19980.1,64104.2,26723.3,42360.4,54459.9,54863.3,31002.2,13273.5,14152.6,25598.3,181.442,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10068.4,60533.2,126646,155254,143042,198210,187706,164989,129048,50821.2,24185.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,841.026,45406.8,105480,152033,182535,199337,201268,189744,166698,131193,81464.3,24485.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,699.46,45722.1,106943,155360,188306,205713,209398,198546,173884,135405,81637.6,23601.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,497.656,44494.1,105659,151727,182619,200313,204138,194468,170778,133664,80594.9,23135.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,572.907,45460.3,104813,150107,181084,198665,203655,195185,170800,132891,79600.8,22170.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,43753.3,103331,149632,180328,198268,203115,193939,170284,133046,79457.6,20023.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,42226.3,99405.4,118675,152296,191269,198122,190330,168108,130291,77718.6,20282.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,27336.6,61288.1,111317,10220.5,163906,151543,59751.4,4212.21,4642.97,67434.7,15244.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,47552.1,112530,164855,199785,218018,218018,211843,186390,143505,85144,21335.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,49133.4,113964,163800,196199,211550,212190,200056,174278,135323,79955.1,18693.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,44164.7,106783,155939,187370,203766,207181,196028,173350,133778,59476.5,13806.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,44362.2,104821,127028,192008,206011,207688,197789,174025,135335,79349,18121.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,48337.6,113003,160886,190995,206480,207389,194689,168054,129064,74687.4,16151.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,29618.3,79177.7,135662,159125,191627,187608,178448,158843,122684,70819.1,14272.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,40866.4,99019.5,145215,179194,196326,201312,191038,168274,126951,71935,14308.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,41230.7,102632,151196,184083,203236,206445,196041,171009,129511,73480.3,13950.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,45860.9,108127,155303,186717,201070,202159,190465,165203,126076,70873.1,12499,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,42970.3,104586,150042,139451,196329,105012,134224,169889,129689,75109.5,13513.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,45588.4,109400,158603,187973,199839,200570,190653,167210,128981,73652.9,12083.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,44626.8,106792,153859,184409,199018,199926,189577,166356,128156,72364.8,10664.9,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,45293.5,108203,155287,184130,195885,202312,192383,167276,128144,71756.3,8880.65,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,44177.1,107469,157229,187789,166711,198854,146988,132337,124746,49331.8,5104.26,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,42948.5,107554,158972,192815,210133,211417,197549,172325,129537,70420.8,7520.35,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,42410.3,105788,154795,184396,198941,201364,189574,165695,123868,66883.3,6030.55,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,41066.4,105869,157472,190953,207964,211292,198570,173007,129915,70597.1,7057.73,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,46245.9,112764,161170,193401,209070,210378,196415,168722,124298,66870.4,5748.69,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,39949.5,101957,148182,177431,192176,193554,180589,157518,119715,65394.7,5694.56,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,38142.6,98400.5,145012,173728,186406,188752,180088,156290,116436,60272.2,3684.86,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,38274.5,94273.1,133360,158519,156091,193246,183491,160191,119558,62580.2,3266.41,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,25941.5,77509.9,103594,95933.8,114830,141269,104016,79172.9,23973.5,10529.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,34855.3,97344.2,147023,179788,193806,194238,182771,157858,117092,61056.8,2667.23,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,38300.7,100468,146688,172687,190985,194177,183192,158916,119179,62582.9,3001.63,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,21623.2,61234.1,131807,149560,140180,135191,130687,119040,89359.9,44515.8,336.368,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,28049.9,33590.4,97496.9,56209.9,139551,161777,178959,155770,69781.1,34711.3,179.374,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,37983.5,100167,147759,175482,189075,190914,180258,156872,116082,59384.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,36125.1,73726.5,130108,154403,188723,160476,131787,155114,96188.7,46180.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,34395.9,92779.1,139114,153664,151594,129471,139658,161849,70377.6,32654.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,39604,107667,158123,188238,203983,204847,189950,162155,85886.9,42510.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,19635.4,104852,157933,140661,209142,167805,160509,131134,94302.2,42943,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,85.5803,15153.1,27581.8,39252.6,49816.7,83581.1,116476,49504.1,114204,55231.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,34929.2,102360,155417,189547,206718,209288,196654,169330,123218,60842.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,36979,106333,159753,191453,207076,205330,190884,162769,121362,61902.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,36657.7,99795.6,121956,149900,154786,177300,164836,166519,64409,7740.87,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,33716.3,100944,107780,156635,202493,181261,158943,132614,114853,28909,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,17865.6,98088,108129,177185,177238,197497,187673,139286,86985.3,42994.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,20724,83344.2,127980,156861,167218,130904,149806,109117,81410.6,41688,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,10672.8,43496.2,76223,123767,70950.3,77951.5,39151.7,49530.7,44905.8,28524.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,26190.6,92853.1,147043,183607,200763,204121,194349,164379,118487,54913.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,28797.1,98683.2,151631,185272,202453,204987,192098,165121,120308,57888.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,31742.6,104198,157599,191463,207173,208767,195495,166399,121698,58733.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,28924.6,99454.5,150955,185496,202591,205166,192291,162705,118021,55930.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,28257.9,104353,161962,200372,218018,218018,208118,177351,129537,62456.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,28745.6,104267,159107,195308,213254,215612,201601,169412,123173,58512.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,25584.4,101106,156829,190864,208886,212267,198624,168151,122142,57828.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,26888.3,105024,160348,197128,216239,218018,206427,174460,126950,60367.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,24154.7,101529,155459,190470,207268,210444,197038,165756,120211,56939.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,21113.7,99571.7,154626,190508,208632,212450,199585,169520,121234,56588,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,15179.2,83686.7,108589,147761,160679,184915,149685,168256,120990,56456.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6873.12,96262.3,102840,118519,151114,143868,146326,135946,87122.3,43331.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2063.13,35979.9,59825.5,88442.7,41693.6,92310.3,36028.2,113730,33427.2,26510.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11167.9,81992.8,137047,171897,191518,194175,181910,157019,112605,51730.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,14897.4,91961.2,147799,180814,198234,201278,190278,162837,106711,44925,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,123.971,41312.2,120323,178982,194527,164938,190972,167629,118604,51352.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,2102.1,47102.4,101380,203134,218018,218018,213442,179679,130324,60160.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,17218.5,101960,160154,199584,218018,218018,208884,176549,128796,59686.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12755.2,92037.2,149918,184953,204778,208165,195040,166753,121075,14408.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12380.1,91340.6,149883,185223,205425,208528,196677,167962,122240,56453.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,6076.57,80479.6,138183,176307,194716,197266,185420,154522,109513,47009.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5435.76,79095.9,134995,170759,184716,185233,174094,156307,116332,38309,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7120.88,81188.9,102155,149802,190981,193811,181506,154526,109769,47798.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,682.698,37117.9,67656.8,170942,184932,186364,176968,91692.4,112597,51931.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,281.147,26514.6,136635,112159,191409,195555,183960,159709,114853,52748.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,285.036,36631.5,71945,110881,148570,195510,142773,87649.1,53136.4,13920.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,5333.98,79324.1,137444,174926,193759,197721,186344,160531,115135,52710.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4328.23,78827.6,137852,174765,192774,195820,185801,162957,119141,55263.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,77874.6,134588,173687,194882,201719,192664,166053,120645,35327.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,88314.8,148822,189508,211258,217727,206453,174752,128163,60403.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,85226.6,144284,180851,195810,199787,188459,164965,121947,27460.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,81058.7,141857,106732,150899,204655,195146,167944,121384,56220,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,69867,41326.7,107086,150688,98466.8,78496,64568.9,31639.3,11894.8,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,74355.2,69924.2,180344,202943,209971,199708,8305.32,121357,26631.2,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,11453.4,697.337,14954.3,32908.6,58433.9,39950,62983.1,4005.56,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,72110.9,132088,172948,190741,196591,189857,166130,121963,12513.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,72784,133682,173002,191892,197684,188895,162909,120031,56278.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,24795,131429,98841.2,119799,135305,55134.1,19924.2,18149,4406.98,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,74850.3,141822,188709,214148,218018,211808,182898,136128,67295.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,83634.1,147706,189734,209616,216098,205605,177213,87382.9,28450,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,78151.6,142700,182013,202851,206831,196730,172080,77919.9,18817.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,67662.5,128340,168255,181884,187758,118570,115776,33178.7,63581.6,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,65261.3,129339,171217,193989,199518,189551,167251,57764.6,14644.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,3977.68,128207,173004,198021,205380,197410,166263,119820,54638.3,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,4852.4,68654.6,115649,103865,71208.2,144216,75970.7,60232.1,21766.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,7817.93,78360.5,122264,125264,134708,134060,174427,129168,64474.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,12658.6,61051.3,57956,142078,207122,120206,174219,130066,67130.7,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,73988.7,139671,181274,203524,209588,199472,174665,131612,69489.4,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,71950.4,136836,179890,198522,201623,115337,102347,73263.1,32141.5,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,1248.86,23551.1,16373,47739.2,92958.6,49453.4,48978.6,26609.3,2960.89,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,61584.8,127540,174760,200209,208197,200346,114106,132401,68428.1,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,-66.7267,]
            self.simu_output = self.COMRO.simulation(gen = self.elec_gen, storage = 0)
        
        elif desal == 'RO_FO':
            from DesalinationModels.RO_FO import RO_FO
            self.RO_FO = RO_FO(capacity = self.desal_values_json['capacity'], RO_rr = self.desal_values_json['RO_rr'], FO_rr = self.desal_values_json['FO_rr'],
                               salinity = self.desal_values_json['FeedC_r'], T_sw = self.desal_values_json['T_sw'], 
                               nERD = self.desal_values_json['nERD'],nBP = self.desal_values_json['nBP'],nHP = self.desal_values_json['nHP'],
                               nFP = self.desal_values_json['nFP'],Nel1 = self.desal_values_json['Nel1'])
            self.design_output = self.RO_FO.design()
            if self.cspModel=='pvsamv1':
                self.simu_output = self.RO_FO.simulation(elec_gen = self.elec_gen, thermal_gen = [0],  solar_type = 'pv', storage = 0)
            elif self.cspModel == 'linear_fresnel_dsg_iph' or self.cspModel == 'trough_physical_process_heat' or self.cspModel == 'SC_FPC' or self.cspModel == 'SC_ETC':
                self.simu_output = self.RO_FO.simulation(elec_gen = [0], thermal_gen = self.heat_gen, solar_type = 'thermal', storage = 0)
            else:
                self.simu_output = self.RO_FO.simulation(elec_gen = self.elec_gen, thermal_gen = self.heat_gen, solar_type = 'csp', storage = 0)
                
        elif desal == 'RO_MDB':
            from DesalinationModels.RO_MDB import RO_MDB
            self.RO_MDB = RO_MDB(capacity = self.desal_values_json['capacity'], RO_rr = self.desal_values_json['RO_rr'], salinity = self.desal_values_json['FeedC_r'], T_sw = self.desal_values_json['T_sw'], 
                               nERD = self.desal_values_json['nERD'],nBP = self.desal_values_json['nBP'],nHP = self.desal_values_json['nHP'],
                               nFP = self.desal_values_json['nFP'],Nel1 = self.desal_values_json['Nel1'],
                               module = self.desal_values_json['module'],TCI_r = self.desal_values_json['TCI_r'],
                               TEI_r = self.desal_values_json['TEI_r'],FFR_r = self.desal_values_json['FFR_r'],
                               V0 = self.desal_values_json['V0'],RR = self.desal_values_json['RR'])
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

            self.LCOW = RO_cost(Capacity = self.desal_values_json['nominal_daily_cap_tmp'], Prod = sum(self.simu_output[0]['Value']), fuel_usage = self.simu_output[7]['Value'], Area = self.cost_values_json['Area'], yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], 
                                chem_cost =  self.cost_values_json['chem_cost'], labor_cost =  self.cost_values_json['labor_cost'], rep_rate =  self.cost_values_json['rep_rate'],
                                unit_capex =  self.cost_values_json['unit_capex'],sec =  self.cost_values_json['sec'],disposal_cost =  self.cost_values_json['disposal_cost'], sam_coe = self.lcoe, cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.RO.storage_cap )

            self.cost_output = self.LCOW.lcow()

   
        elif desal == 'VAGMD':
            from DesalinationModels.VAGMD_cost import VAGMD_cost

            self.LCOW = VAGMD_cost(Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], Area = self.VAGMD.Area, Pflux = self.VAGMD.PFlux, TCO = self.VAGMD.TCO, TEI = self.VAGMD.TEI_r, FFR = self.VAGMD.FFR_r, th_module = self.VAGMD.ThPower, STEC = self.VAGMD.STEC, SEEC = self.cost_values_json['SEEC'],
                                   MD_membrane = self.cost_values_json['MD_membrane'], MD_module = self.cost_values_json['MD_module'], MD_module_capacity = self.cost_values_json['MD_module_capacity'], HX = self.cost_values_json['HX'], endplates = self.cost_values_json['endplates'], endplates_capacity = self.cost_values_json['endplates_capacity'], other_capacity = self.cost_values_json['other_capacity'], heat_cool = self.cost_values_json['heat_cool'], heat_cool_capacity = self.cost_values_json['heat_cool_capacity'], h_r = self.cost_values_json['h_r'], h_r_capacity = self.cost_values_json['h_r_capacity'], tank = self.cost_values_json['tank'], tank_capacity = self.cost_values_json['tank_capacity'], pump = self.cost_values_json['pump'], pump_capacity = self.cost_values_json['pump_capacity'], other = self.cost_values_json['other'], 
                                   yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], coh =  self.cost_values_json['coh'], solar_coh =  self.cost_values_json['solar_coh'], sam_coh = self.lcoh, solar_inlet =  self.cost_values_json['solar_inlet'], solar_outlet =  self.cost_values_json['solar_outlet'], HX_eff =  self.cost_values_json['HX_eff'], cost_module_re =  self.cost_values_json['cost_module_re'] , cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.VAGMD.storage_cap )

            self.cost_output = self.LCOW.lcow()

        elif desal == 'MDB':
            
            from DesalinationModels.MDB_cost import MDB_cost

            self.LCOW = MDB_cost(Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], Area = self.MDB.Area,
                                 Pflux = self.MDB.PFlux_avg, RR = self.MDB.R[-1],
                                 TCO = sum(self.MDB.TCO) / len(self.MDB.TCO), TEI = self.MDB.TEI_r, FFR = self.MDB.FFR_r, th_module = sum(self.MDB.ThPower)/len(self.MDB.ThPower),
                                 STEC = self.MDB.ave_stec, SEEC = self.cost_values_json['SEEC'],  MD_membrane = self.cost_values_json['MD_membrane'],
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

            # from DesalinationModels.VAGMD_cost import VAGMD_cost

            # self.LCOW = VAGMD_cost(Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], Area = self.VAGMD.Area, Pflux = self.VAGMD.PFlux, TCO = self.VAGMD.TCO, TEI = self.VAGMD.TEI_r, FFR = self.VAGMD.FFR_r, th_module = self.VAGMD.ThPower, STEC = self.VAGMD.STEC, SEEC = self.cost_values_json['SEEC'],
            #                        MD_membrane = self.cost_values_json['MD_membrane'], MD_module = self.cost_values_json['MD_module'], MD_module_capacity = self.cost_values_json['MD_module_capacity'], HX = self.cost_values_json['HX'], endplates = self.cost_values_json['endplates'], endplates_capacity = self.cost_values_json['endplates_capacity'], other_capacity = self.cost_values_json['other_capacity'], heat_cool = self.cost_values_json['heat_cool'], heat_cool_capacity = self.cost_values_json['heat_cool_capacity'], h_r = self.cost_values_json['h_r'], h_r_capacity = self.cost_values_json['h_r_capacity'], tank = self.cost_values_json['tank'], tank_capacity = self.cost_values_json['tank_capacity'], pump = self.cost_values_json['pump'], pump_capacity = self.cost_values_json['pump_capacity'], other = self.cost_values_json['other'], 
            #                        yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], coh =  self.cost_values_json['coh'], sam_coh =self.cost_values_json['sam_coh'], solar_inlet =  self.cost_values_json['solar_inlet'], solar_outlet =  self.cost_values_json['solar_outlet'], HX_eff =  self.cost_values_json['HX_eff'], cost_module_re =  self.cost_values_json['cost_module_re'] , cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.VAGMD.storage_cap )

            # self.cost_output = self.LCOW.lcow()
        
        elif desal == 'LTMED':
            from DesalinationModels.LTMED_cost import LTMED_cost
            self.LCOW = LTMED_cost(f_HEX = self.cost_values_json['f_HEX'], 
                                    HEX_area = self.LTMED.sA,
                                   Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], SEEC = self.cost_values_json['SEEC'], STEC = self.LTMED.STEC,
                                    Chemicals = self.cost_values_json['Chemicals'], Labor = self.cost_values_json['Labor'], Discharge = self.cost_values_json['Discharge'], Maintenance = self.cost_values_json['Maintenance'],  Miscellaneous = self.cost_values_json['Miscellaneous'],
                                   yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'], solar_coh =  self.cost_values_json['solar_coh'], coh =  self.cost_values_json['coh'], sam_coh = self.lcoh, cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.LTMED.storage_cap)
            self.cost_output = self.LCOW.lcow()
            
        elif desal == 'ABS':
            from DesalinationModels.ABS_cost import ABS_cost
            self.LCOW = ABS_cost(f_HEX = self.cost_values_json['f_HEX'], P_req = self.P_req,
                                   # HEX_area = self.LTMED.system.sum_A,
                                   Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], SEEC = self.cost_values_json['SEEC'], STEC = self.ABS.STEC,
                                    Chemicals = self.cost_values_json['Chemicals'], Labor = self.cost_values_json['Labor'], Discharge = self.cost_values_json['Discharge'], Maintenance = self.cost_values_json['Maintenance'],  Miscellaneous = self.cost_values_json['Miscellaneous'],
                                   yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'],  solar_coh =  self.cost_values_json['solar_coh'], coh =  self.cost_values_json['coh'], sam_coh = self.lcoh, cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.ABS.storage_cap)
            self.cost_output = self.LCOW.lcow()  
            
        elif desal == 'MEDTVC':
            from DesalinationModels.MEDTVC_cost import MEDTVC_cost
            self.LCOW = MEDTVC_cost(f_HEX = self.cost_values_json['f_HEX'], 
                                    HEX_area = self.MEDTVC.sA,
                                   Capacity = self.desal_values_json['Capacity'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], SEEC = self.cost_values_json['SEEC'], STEC = self.MEDTVC.STEC,
                                    Chemicals = self.cost_values_json['Chemicals'], Labor = self.cost_values_json['Labor'], Discharge = self.cost_values_json['Discharge'], Maintenance = self.cost_values_json['Maintenance'],  Miscellaneous = self.cost_values_json['Miscellaneous'],
                                   yrs = self.cost_values_json['yrs'], int_rate =  self.cost_values_json['int_rate'], coe =  self.cost_values_json['coe'],  solar_coh =  self.cost_values_json['solar_coh'], coh =  self.cost_values_json['coh'], sam_coh = self.lcoh, cost_storage = self.cost_values_json['cost_storage'], storage_cap = self.MEDTVC.storage_cap)
            self.cost_output = self.LCOW.lcow()
            
        elif desal == 'FO':
            from DesalinationModels.FO_cost import FO_cost
            self.LCOW = FO_cost(    Capacity = self.desal_values_json['Mprod'], Prod = self.simu_output[4]['Value'], fuel_usage = self.simu_output[7]['Value'], SEEC = self.cost_values_json['SEEC'], STEC = self.cost_values_json['STEC'], labor = self.cost_values_json['labor'], 
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
                                sec =  self.costout['sec'], sam_coe = self.lcoe, practical_inv_factor = self.cost_values_json['practical_inv_factor'], storage_cap = self.OARO.storage_cap )
        
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
            self.LCOW = RO_FO_cost(Capacity = self.design_output[1]['Value'], Prod = self.simu_output[4]['Value'],chem_cost = self.cost_values_json['chem_cost'], labor_cost = self.cost_values_json['labor_cost'],
                                          unit_capex = self.cost_values_json['unit_capex'],rep_rate = self.cost_values_json['rep_rate'], FO_unit_capex = self.cost_values_json['FO_unit_capex'], 
                                          FO_labor = self.cost_values_json['FO_labor'], FO_chem_cost = self.cost_values_json['FO_chem_cost'], FO_goods_cost = self.cost_values_json['FO_goods_cost'], 
                                          cost_storage = self.cost_values_json['cost_storage'],  insurance = self.cost_values_json['insurance'], 
                                          FO_SEC = self.cost_values_json['FO_SEC'], FO_capacity = self.design_output[2]['Value'], FO_STEC = self.design_output[8]['Value'], disposal_cost = self.cost_values_json['disposal_cost'], 
                                          FO_fuel_usage = self.simu_output[8]['Value'], coe = self.cost_values_json['coe'], solar_coh = self.cost_values_json['solar_coh'], coh = self.cost_values_json['coh'],sam_coe = self.sam_lcoe, sam_coh = self.sam_lcoh)
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

            self.LCOW = RO_MDB_cost(Capacity = self.design_output[1]['Value'], Prod = self.simu_output[4]['Value'],chem_cost = self.cost_values_json['chem_cost'], labor_cost = self.cost_values_json['labor_cost'],
                                          unit_capex = self.cost_values_json['unit_capex'],rep_rate = self.cost_values_json['rep_rate'], 
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
                                          MDB_SEC = self.cost_values_json['MDB_SEC'], MDB_capacity = self.design_output[2]['Value'], MDB_STEC = self.design_output[8]['Value'], disposal_cost = self.cost_values_json['disposal_cost'], 
                                          MDB_fuel_usage = self.simu_output[8]['Value'], coe = self.cost_values_json['coe'], solar_coh = self.cost_values_json['solar_coh'], coh = self.cost_values_json['coh'], sam_coe = self.sam_lcoe, sam_coh = self.sam_lcoh)
            self.cost_output = self.LCOW.lcow()
            
        elif desal == 'Generic':
            from DesalinationModels.Generic_cost import Generic_cost
            self.LCOW = Generic_cost(unit_cost = self.cost_values_json['unit_cost'],
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
                if self.cspModel== 'tcsdirect_steam' or self.cspModel== 'pvsamv1' or self.cspModel== 'tcsmolten_salt': 
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
                             }
        }

    def set_data(self, variables):

        # Map all the strings present in the json file.
        stringsInJson = {}
        added_variables = {}
        
        for name, value in self.other_input_variables[self.cspModel].items():

            self.ssc.data_set_number( self.data, b''+ name.encode("ascii", "backslashreplace"), value )

            # self.ssc.data_set_number( self.data, b''+ name.encode("ascii", "backslashreplace"), b'' + varValue)
            
        
        # Increment complete TODOs count for each user.

        for ssc_var in variables:
            try:
                #Checking if the variable value is present in the json and if value of the variable is a valid one.
                if ("value" in ssc_var and ssc_var["value"] != "#N/A" ):
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


                        if varName == 'ppa_price_input':
                            self.ssc.data_set_array( self.data, b''+ varName.encode("ascii", "backslashreplace"), [varValue] )
                        else:
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
    sam = SamBaseClass( CSP = 'SC_FPC',
                       desalination =  'VAGMD',
                  financial = 'iph_to_lcoefcr')
    # sam = SamBaseClass(CSP = 'tcslinear_fresnel',
    #           financial = 'lcoefcr')
    # sam.desal_design(sam.desalination)
    sam.main()
    
    #Argument for the unit test makes sure the unit test does not fail if system_capacity 
    #system_capacity is passed as a first argument on command line.
    #unittest.main(argv=['first-arg-is-ignored'], exit=False)