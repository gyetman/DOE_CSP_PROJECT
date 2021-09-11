# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 11:43:07 2021

@author: zzrfl
"""
from DesalinationModels.VAGMD_cost import VAGMD_cost
from numpy import array,cumprod,insert
from numpy.matlib import repmat
from math import ceil, exp
from warnings import warn
import numpy as np
from scipy.interpolate import interp1d, griddata
from scipy.optimize import fmin
from DesalinationModels.RO_Fixed_Load import RO
from DesalinationModels.FO_Generalized import FO_generalized

#%%
class RO_FO(object):
    def __init__(self,
                 capacity = 1000, 
                 RO_rr=40, 
                 FO_rr=30, 
                 salinity=35, 
                 T_sw=15, 
                 
                 # RO parameters
                 nERD=0.95,            # Energy recovery device efficiency
                 nBP=0.8,
                 nHP=0.8,
                 nFP=0.8,                
                 nominal_daily_cap_tmp=1000,
                 stage = 1,
                 Nel1=None,              #number elements per vessel in stage 1
                 R1=.4,               #Desired overall recovery rate
                 R2 = 0.833,          # 2nd stage recovery rate
                 R3 = 0.9,            # 3rd stage recovery rate
                 # RO Membrane Property Inputs: 
                 #load in from a table of membrane types w/properties or enter manually.
                 # Using default values here based on manufacturer's datasheet for seawater RO membrane element: SWC4B MAX
                 Qpnom1=27.3/24.0,      #nominal permeate production per membrane element (m3/hr)
                 Am1=40.8,            #membrane area per membrane element (m^2) 
                 Pmax1=82.7,          #Max pressure of membrane element (bar)
                 Ptest1=55.2,         #Applied test pressure for each mem element
                 Ctest1=32,           #membrane manufacturer's test feed salinity (TDS) for each element (parts per thousand)
                 SR1=99.8,            #rated salt rejection of each element (%)
                 Rt1=.1,              #Test recovery rate for each element
                 Pdropmax=0.6895,     #maximum pressure drop per membrane element (bar)
                 Pfp=1    ,            # Pressure of intake feed pumps
                 Tmax = 318.15,
                 minQb = 2.7,
                 maxQf = 17,
                 Fossil_f = 1,
                
                 # Booleans
                 has_erd = 1, # include erd with booster pump
                 is_first_stage = True, # include intake/feed pump powr requirement if first stage
                 pretreat_power = 1,  # kWh/m3 assumed for pretreatment
                 # FO parameters
                 FO_salt_rej =0.95):
        self.capacity = capacity
        self.RO_rr = RO_rr /100
        self.FO_rr = FO_rr /100
        self.salinity = salinity
        self.T_sw = T_sw
        self.FO_salt_rej = FO_salt_rej
        self.nERD=nERD
        self.nBP=nBP
        self.nHP=nHP
        self.nFP=nFP          
        self.nominal_daily_cap_tmp=nominal_daily_cap_tmp
        self.Nel1=Nel1
        self.R1=R1
        self.Cf=salinity  
        self.Pfp=Pfp
        self.T=T_sw 
        self.Am1=Am1
        self.Qpnom1=Qpnom1 
        self.Ptest1 = Ptest1
        self.SR1 = SR1
        self.Rt1 = Rt1
        self.Ctest1 = Ctest1
        self.Pdropmax = Pdropmax
        self.maxQf = maxQf
        self.Fossil_f = Fossil_f
        
        self.has_erd = True if has_erd == 1 else False
        self.is_first_stage = is_first_stage
        self.pretreat_power = pretreat_power
        self.stage = stage
        self.R2 = R2
        self.R3 = R3
    def design(self):
        self.RO_capacity = self.capacity / (1 + (1-self.RO_rr)/self.RO_rr * self.FO_rr * 0.9)
        RO_case = RO(T = self.T_sw, nominal_daily_cap_tmp=self.RO_capacity, R1=self.RO_rr, FeedC_r = self.salinity, stage = 1,
                     nERD = self.nERD, nBP = self.nBP, nHP = self.nHP, nFP = self.nFP, Nel1 = self.Nel1,
                    Qpnom1=self.Qpnom1 ,  Am1=self.Am1,  Ptest1=self.Ptest1, Ctest1=self.Ctest1,          
                    SR1=self.SR1,  Rt1=self.Rt1, Pdropmax=self.Pdropmax,  Pfp=self.Pfp  ,     
                    maxQf = self.maxQf, Fossil_f = self.Fossil_f, has_erd = self.has_erd, 
                    is_first_stage = self.is_first_stage, 
                    pretreat_power = self.pretreat_power) 
        RO_case.RODesign()
        # Retreive system performance from RO model
        RO_feed = RO_case.case.Qf1*24
        RO_brine = RO_case.case.Qb1*24
        RO_permeate = RO_case.case.Qp1*24
        RO_p_s = RO_case.case.Cp *1000
        RO_brine_salinity = (RO_case.case.Cf * RO_feed - RO_case.case.Cp * RO_permeate)/ RO_brine  #  g/L 
        FO_Mprod = self.capacity - self.RO_capacity
        
        FO = FO_generalized( T_sw = self.T_sw, FeedC_r = RO_brine_salinity, r=self.FO_rr, Mprod = FO_Mprod, Salt_rej = self.FO_salt_rej)
        FO.FO_design() 
        Thermal_load = FO.Thermal_power
        STEC = FO.STEC
        FO_p_s = (1-FO.Salt_rej) * RO_brine_salinity  * RO_brine / FO_Mprod
        FO_b_s = FO.Salt_rej * RO_brine_salinity  * RO_brine / (RO_brine - FO_Mprod)
                   # RO power[0],      FO power[1],   , RO_bs[2]         , FO_bs[3],Recovery rate[4],           #   RO permeate[5],     FO permeate[6],   Overall STEC,[7]                  Overall SEC[8],                            ,[9]Feed water flowrate
        #result = [RO_case.PowerTotal, Thermal_load[0], RO_brine_salinity, FO_b_s, (FO_Mprod+RO_permeate)/RO_feed, self.RO_capacity,     FO_Mprod,         STEC[0]*FO_Mprod/self.capacity,   RO_case.SEC_RO*RO_capacity/self.capacity,   RO_feed ]
        self.P_req = FO.Thermal_power[0] 
        self.design_output = []
        self.design_output.append({'Name':'Overall recovery rate','Value':(FO_Mprod+RO_permeate)/RO_feed * 100,'Unit':'%'})        
        self.design_output.append({'Name':'RO capacity','Value':self.RO_capacity,'Unit':'m3/day'})
        self.design_output.append({'Name':'FO capacity','Value':FO_Mprod,'Unit':'m3/day'})        
        # self.design_output.append({'Name':'Number of vessels in RO','Value':RO.NV1,'Unit':''})
        self.design_output.append({'Name':'RO brine salinity','Value':RO_brine_salinity,'Unit':'g/L'})
        self.design_output.append({'Name':'FO brine salinity','Value':FO_b_s,'Unit':'g/L'})        
        
        self.design_output.append({'Name':'Electric energy requirement','Value':RO_case.case.PowerTotal,'Unit':'kW(e)'})
        self.design_output.append({'Name':'Thermal power requirement','Value':FO.Thermal_power[0] / 1000,'Unit':'MW(th)'})
        
        self.design_output.append({'Name':'SEC-RO (Specific electricity consumption)','Value':RO_case.case.SEC,'Unit':'kWh(e)/m3'})
        self.design_output.append({'Name':'STEC-FO (Specific thermal power consumption)','Value':FO.STEC[0],'Unit':'kWh(th)/m3'})   
        
        self.design_output.append({'Name':'Feed flow rate','Value':RO_case.case.Qf1,'Unit':'m3/h'})        
        self.design_output.append({'Name':'(FO) Weak draw solution concentration','Value':FO.B*100,'Unit':'%'})
        # self.design_output.append({'Name':'(FO) Strong draw solution flow rate','Value':FO.SD,'Unit':'m3/day'}) 
      
        return self.design_output
    
    def simulation(self, elec_gen, thermal_gen, solar_type = "pv", storage = 0 ): # solar_type = (pv, csp, thermal)

        if solar_type == 'pv':
            gen = elec_gen
            self.elec_load = self.design_output[5]['Value']  # kWh
            self.thermal_load = self.design_output[6]['Value']*1000 # kWh
            self.max_prod = self.capacity / 24 # m3/h
            self.storage_cap = 0 # kWh
            self.Fossil_f = 1
            to_desal = [0 for i in range(len(gen))]
            to_storage =  [0 for i in range(len(gen))]
            storage_load =  [0 for i in range(len(gen))]
            storage_cap_1 =  [0 for i in range(len(gen))]
            storage_cap_2 = [0 for i in range(len(gen))]
            storage_status =  [0 for i in range(len(gen))]
            solar_loss =  [0 for i in range(len(gen))]
            load =  [0 for i in range(len(gen))]
            prod =  [0 for i in range(len(gen))]
            grid =  [0 for i in range(len(gen))]
            fuel =  [0 for i in range(len(gen))]
            energy_consumption =  [0 for i in range(len(gen))]
            for i in range(len(gen)):
                to_desal[i] = min(self.elec_load, gen[i])
                to_storage[i] = abs(gen[i] - to_desal[i])
                storage_load[i] = gen[i] - self.thermal_load
                if i != 0:
                    storage_cap_1[i] = storage_status[i-1]
                storage_cap_2[i] = max(storage_load[i] + storage_cap_1[i], 0)
                storage_status[i] = min(storage_cap_2[i] , self.storage_cap)
                solar_loss[i] = abs(storage_status[i] - storage_cap_2[i])
                load[i] = to_desal[i] + max(0, storage_cap_1[i] - storage_cap_2[i])
                if max(0,load[i] / self.elec_load) < self.Fossil_f:
                    grid[i] = self.elec_load - load[i]
    
                energy_consumption[i] = grid[i]+load[i]
                prod[i] = (grid[i]+load[i] )/ self.elec_load * self.max_prod  
                fuel[i] = self.thermal_load

            th_energy_consumption = [0]
            elec_load = load            
            
            grid_percentage = sum(grid)/sum(energy_consumption)*100
            fossil_percentage = 1
            Month = [0,31,59,90,120,151,181,212,243,273,304,334,365]
            Monthly_prod = [ sum( prod[Month[i]*24:(Month[i+1]*24)] ) for i in range(12) ]
        
        if solar_type == 'thermal':
            gen = thermal_gen
            self.thermal_load = self.design_output[6]['Value'] * 1000 # kWh
            self.max_prod = self.capacity / 24 # m3/h
            self.storage_cap = 0 # kWh
            self.Fossil_f = 1
            to_desal = [0 for i in range(len(gen))]
            to_storage =  [0 for i in range(len(gen))]
            storage_load =  [0 for i in range(len(gen))]
            storage_cap_1 =  [0 for i in range(len(gen))]
            storage_cap_2 = [0 for i in range(len(gen))]
            storage_status =  [0 for i in range(len(gen))]
            solar_loss =  [0 for i in range(len(gen))]
            load =  [0 for i in range(len(gen))]
            prod =  [0 for i in range(len(gen))]
            fuel =  [0 for i in range(len(gen))]
            grid =  [0 for i in range(len(gen))]
            energy_consumption =  [0 for i in range(len(gen))]
            for i in range(len(gen)):
                to_desal[i] = min(self.thermal_load, gen[i])
                to_storage[i] = abs(gen[i] - to_desal[i])
                storage_load[i] = gen[i] - self.thermal_load
                if i != 0:
                    storage_cap_1[i] = storage_status[i-1]
                storage_cap_2[i] = max(storage_load[i] + storage_cap_1[i], 0)
                storage_status[i] = min(storage_cap_2[i] , self.storage_cap)
                solar_loss[i] = abs(storage_status[i] - storage_cap_2[i])
                load[i] = to_desal[i] + max(0, storage_cap_1[i] - storage_cap_2[i])
                if max(0,load[i] / self.thermal_load) < self.Fossil_f:
                    fuel[i] = self.thermal_load - load[i]
    
                energy_consumption[i] = fuel[i]+load[i]
                prod[i] = (fuel[i]+load[i] )/ self.thermal_load * self.max_prod  
                grid[i] = self.design_output[5]['Value'] 

            th_energy_consumption = energy_consumption
            elec_load = [0]
            
            grid_percentage = 1
            fossil_percentage = sum(fuel)/sum(energy_consumption)*100
            Month = [0,31,59,90,120,151,181,212,243,273,304,334,365]
            Monthly_prod = [ sum( prod[Month[i]*24:(Month[i+1]*24)] ) for i in range(12) ]           
        
        if solar_type == 'csp':
            gen = thermal_gen
            self.elec_load = self.design_output[5]['Value']
            self.thermal_load = self.design_output[6]['Value'] * 1000 # kWh
            self.max_prod = self.capacity / 24 # m3/h
            self.storage_cap = 0 # kWh
            self.Fossil_f = 1
            to_desal = [0 for i in range(len(gen))]
            to_storage =  [0 for i in range(len(gen))]
            storage_load =  [0 for i in range(len(gen))]
            storage_cap_1 =  [0 for i in range(len(gen))]
            storage_cap_2 = [0 for i in range(len(gen))]
            storage_status =  [0 for i in range(len(gen))]
            solar_loss =  [0 for i in range(len(gen))]
            load =  [0 for i in range(len(gen))]
            prod =  [0 for i in range(len(gen))]
            fuel =  [0 for i in range(len(gen))]
            grid =  [0 for i in range(len(gen))]
            th_energy_consumption =  [0 for i in range(len(gen))]
            elec_energy_consumption =  [0 for i in range(len(gen))]
            elec_load =  [0 for i in range(len(gen))]
            for i in range(len(gen)):
                to_desal[i] = min(self.thermal_load, gen[i])
                to_storage[i] = abs(gen[i] - to_desal[i])
                storage_load[i] = gen[i] - self.thermal_load
                if i != 0:
                    storage_cap_1[i] = storage_status[i-1]
                storage_cap_2[i] = max(storage_load[i] + storage_cap_1[i], 0)
                storage_status[i] = min(storage_cap_2[i] , self.storage_cap)
                solar_loss[i] = abs(storage_status[i] - storage_cap_2[i])
                load[i] = to_desal[i] + max(0, storage_cap_1[i] - storage_cap_2[i])
                if max(0,load[i] / self.thermal_load) < self.Fossil_f:
                    fuel[i] = self.thermal_load - load[i]
                if max(0,elec_gen[i] / self.elec_load) < self.Fossil_f:
                    grid[i] = self.elec_load - max(0,elec_gen[i])
                elec_load[i] = min(self.elec_load, max(0,elec_gen[i]))
                    
                th_energy_consumption[i] = fuel[i]+load[i]
                elec_energy_consumption[i] = self.elec_load
                prod[i] = (fuel[i]+load[i] )/ self.thermal_load * self.max_prod  
                grid_percentage = sum(grid)/max(1, sum(elec_energy_consumption))*100  
                fossil_percentage = sum(fuel)/max(1, sum(th_energy_consumption))*100                             
                Month = [0,31,59,90,120,151,181,212,243,273,304,334,365]
                Monthly_prod = [ sum( prod[Month[i]*24:(Month[i+1]*24)] ) for i in range(12) ]
                
    
        simu_output = []

        simu_output.append({'Name':'Water production','Value':prod,'Unit':'m3'})
        simu_output.append({'Name':'Storage status','Value':storage_status,'Unit':'kWh'})
        simu_output.append({'Name':'Storage Capacity','Value':self.storage_cap,'Unit':'kWh'})
        simu_output.append({'Name':'Grid electricity usage','Value':grid,'Unit':'kWh'})
        simu_output.append({'Name':'Annual water production','Value':sum(prod),'Unit':'m3'})
        simu_output.append({'Name':'Monthly water production','Value': Monthly_prod,'Unit':'m3'})
        simu_output.append({'Name':'Total grid electricity usage','Value':sum(grid),'Unit':'kWh'})
        
        simu_output.append({'Name':'Percentage of grid electricity consumption','Value': grid_percentage,'Unit':'%'})
        simu_output.append({'Name':'Percentage of external fossil fuel consumption','Value':fossil_percentage,'Unit':'%'})        
        simu_output.append({'Name':'Total external thermal energy usage','Value':sum(fuel),'Unit':'kWh'})
        simu_output.append({'Name':'External thermal energy usage','Value':fuel,'Unit':'kWh'})
        simu_output.append({'Name':'Overall recovery rate','Value':self.design_output[0]['Value'],'Unit':'%'})

        print(elec_gen[0:24])
        print(elec_load[0:24])
        simu_output.append({'Name':'Curtailed solar thermal energy','Value':(sum(thermal_gen) - sum(load)) / 1000000 ,'Unit':'GWh'})   
        simu_output.append({'Name':'Percentage of curtailed thermal energy','Value':(sum(thermal_gen) - sum(load)) / (sum(thermal_gen)+1) * 100 ,'Unit':'%'})
        simu_output.append({'Name':'Curtailed solar electric energy','Value':max(0, (sum(elec_gen) - sum(elec_load))) / 1000000 ,'Unit':'GWh'})   
        simu_output.append({'Name':'Percentage of curtailed electric energy','Value':max(0,(sum(elec_gen) - sum(elec_load))) / (sum(elec_gen)+1) * 100 ,'Unit':'%'})
        return simu_output            
        
        # elif solar_type == 'thermal':
            
        
        # elif solar_type == 'csp'
            
            
        return self.simulation_output
            
            
            
            
            
        