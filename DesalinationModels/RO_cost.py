# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 02:38:36 2020
RO COST MODEL
Following a structure similar to VAGMD_cost.py
@author: adama

Battery cost
"""



import numpy as np
import math
from CostModels.desalinationcosts import CR_factor


class RO_cost(object):
    def __init__(self,
                 Capacity = [1000], # Desalination plant capacity (m3/day)
                 Prod = 328500, # Annual permeate production (m3)
                 Area = 40.8 , # Membrane area (m2)
                 fuel_usage = 0, # Total fuel usage (%)
                 # Pflux = 1.1375,  # Permeate flow per module (m3/h/module)
                 num_modules = 100, # Number of module (from design model) 
                 membrane_cost=30, # cost per unit area of membrane (USD/m2)
                 pressure_vessel_cost= 1000, # cost per pressure vessel (USD/vessel)-- just guessing 1000 to fill value for now: 2/25/2020 
#                 FFR  = 17, # Feed flow rate per module (m3/h/module)
#                 GOR = 10.475,  # Gained output ratio
                # downtime = 0.1, # Yearly downtime of the plant (ratio)
                 yrs = 20, # Expected plant lifetime
                 int_rate = 0.04 , # Average interest rate
                 coe = 0.05,  # Unit cost of electricity ($/kWh)
                 sam_coe = 0.02,
                 solar_coe =  0,
                 chem_cost=0.05, # specific chemical cost ($/m3)
                 labor_cost=0.1,  # specific labor cost ($/m3)
                 rep_rate=5,    # membrane replacement rate (yrs)
                 equip_cost_method='general', # Option 1:'general' capex breakdown by cost factor; Option 2: 'specify' equipment costs
                 sec= 2.5, # specific energy consumption (kwh/m3)
                 HP_pump_pressure=60, # high pressure pump discharge pressure (bar)
                 HP_pump_flowrate=41.67,   # high pressure pump flowrate (m3/hr)
                 BP_pump_pressure=10.5, # booster pump discharge pressure (bar)
                 BP_pump_flowrate=62.5, # booster pump flowrate (m3/hr)
                 ERD_flowrate=62.5,     # ERD flowrate set to brine flowrate(m3/hr)
                 ERD_pressure=49  ,      # ERD pressure set to brine pressure entering (bar)  
                 disposal_cost=0.03,    # specific waste disposal cost($/m3)
                 IX_cost = 0.15, # ion-exchange cost ($/m3)
                 insurance = 0.5, # insurance (percentage of CAPEX)
                 #coh = 0.01 , # Unit cost of heat ($/kWh)
                 #sam_coh = 0.02, # Unit cost of heat from SAM ($/kWh)
                 #solar_inlet = 85, # Solar field inlet temperature
                 #solar_outlet = 95, # Solar field outlet temperature
                 #HX_eff = 0.85, # Heat exchanger efficiency
                 #cost_module_re = 0.220 , # Cost of module replacement ($/m3)
                 unit_capex = [1000],
                 unit_capex_main= 1647,  # total EPC cost, USD/(m3/day)
                 unit_capex_passes=668,  # total EPC cost, USD/(m3/day)              
                 downtime = 10, # downtime percentage
                 cost_storage = 26 , # Cost of battery ($/kWh)
                 storage_cap = 0 # Capacity of battery (kWh)
                 
                 ):
        self.HP_pump_pressure=HP_pump_pressure
        self.HP_pump_flowrate=HP_pump_flowrate
        self.BP_pump_pressure=BP_pump_pressure
        self.BP_pump_flowrate=BP_pump_flowrate
        self.ERD_flowrate=ERD_flowrate
        self.ERD_pressure=ERD_pressure
        self.ann_prod=Prod * (1-downtime /100)
        self.chem_cost=chem_cost 
        self.labor_cost=labor_cost 
        self.operation_hour = 24 #* (1-downtime) # Average daily operation hour (h/day)
        # self.Pflux = Pflux
        self.Area = Area
        # self.PF_module = self.Pflux * self.Area
        self.num_modules = num_modules
        self.total_area = self.num_modules*self.Area
        self.membrane_cost=membrane_cost
        self.pressure_vessel_cost=pressure_vessel_cost
        self.SEC=sec
        self.capacity=Capacity
        self.equip_cost_method=equip_cost_method
        
        # calculate membrane replacement cost
        rep_yr = rep_rate
        self.replacement_rate = 0
        while rep_yr < yrs:
            self.replacement_rate += 1 / (1+int_rate) ** rep_yr
            rep_yr += rep_rate              
        self.replacement_rate *= CR_factor(yrs,int_rate)
        self.membrane_replacement_cost=self.membrane_cost*self.total_area*self.replacement_rate/self.ann_prod
        
        
        self.disposal_cost=disposal_cost 
#        self.HX_eff = HX_eff
        
        self.unit_capex = unit_capex
        self.unit_capex_main = unit_capex_main
        self.unit_capex_passes = unit_capex_passes
        self.downtime = downtime / 100
#        self.th_module = th_module
#        self.FFR = FFR
        self.IX_cost = IX_cost
        self.insurance = insurance / 100
        self.coe = coe
        if solar_coe is None:
            self.sam_coe = sam_coe
        else:
            self.sam_coe = float(solar_coe)

        self.fuel_usage = fuel_usage / 100
#        self.cost_module_re = cost_module_re
        self.yrs = yrs
        self.int_rate = int_rate
        self.cost_storage = cost_storage
        self.storage_cap = storage_cap
                
    def lcow(self):
        if self.equip_cost_method=='specify':
            self.total_module_cost = self.total_area*self.membrane_cost + self.NV*self.pressure_vessel_cost
            self.HPpump_cost=53*self.HP_pump_flowrate*self.HP_pump_pressure
#            self.test=pump_cost(HP_pump_pressure,HP_pump_flowrate)
            self.BPpump_cost=53*self.BP_pump_flowrate*self.BP_pump_pressure
    #        self.ERD_cost=
#            self.other_equip_cost=
#            self.equip_cost=self.HPpump_cost + self.BPpump_cost +self.ERD_cost + self.other_equip_cost
            self.CAPEX = self.total_module_cost*CR_factor(self.yrs,self.int_rate) / self.ann_prod
#           (self.cost_sys*1000*self.int_rate*(1+self.int_rate)**self.yrs) / ((1+self.int_rate)**self.yrs-1) / self.Prod
            self.unit_capex=self.total_module_cost/self.capacity  
#        elif self.equip_cost_method=='general':
        else:    
            for i in range(len(self.unit_capex)):
                if i == 0 :
                    if self.unit_capex[i]:
                        self.unit_capex_empirical = [self.capacity[i]]
                    else:
                        self.unit_capex_empirical = [3726.1 * self.capacity[i] ** (-0.071)]
                else:
                    if self.unit_capex[i]:
                        self.unit_capex_empirical.append(self.capacity[i])
                    else:
                        self.unit_capex_empirical.append(808.39 * self.capacity[i] ** (-0.017))
            
            self.EPC_cost = sum([self.capacity[i] * self.unit_capex_empirical[i] for i in range(len(self.capacity)) ])

            
            self.CAPEX =(self.EPC_cost +  self.cost_storage * self.storage_cap)*CR_factor(self.yrs,self.int_rate) / self.ann_prod

        self.cost_elec = self.SEC * (self.fuel_usage * self.coe + (1-self.fuel_usage) * self.sam_coe)
        self.insurance_cost = self.EPC_cost * self.insurance / self.ann_prod
        self.OPEX = self.disposal_cost + self.chem_cost +self.labor_cost + self.cost_elec + self.insurance_cost + self.IX_cost  + self.membrane_replacement_cost#maintenance and membrane replacement

        self.LCOW = self.CAPEX + self.OPEX

        
#        self.test=(self.total_capex*self.int_rate*(1+self.int_rate)**self.yrs) / ((1+self.int_rate)**self.yrs-1) / self.ann_prod
        cost_output = []
        cost_output.append({'Name':'Desal Annualized CAPEX','Value':self.CAPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Desal OPEX','Value':self.OPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of water','Value':self.LCOW,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of electricity (from fossile fuel)','Value':self.coe,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of electricity (from solar field)','Value':self.sam_coe,'Unit':'$/m3'})
        cost_output.append({'Name':'Energy cost','Value':self.cost_elec,'Unit':'$/m3'})    
        
        return cost_output
    
#    def pump_cost(pumppressure,pumpflowrate):
#        pumpcapex=53*pumppressure*pumpflowrate
#        return pumpcapex
#    def cost_method(self):
    
    #%%
    # rocost=RO_cost()
    # rocost.lcow()
