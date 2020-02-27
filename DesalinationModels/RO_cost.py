# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 02:38:36 2020
RO COST MODEL
Following a structure similar to VAGMD_cost.py
@author: adama
"""

import numpy as np
import math
from CostModels.desalinationcosts import CR_factor


class RO_cost(object):
    def __init__(self,
                 Capacity = 1000, # Desalination plant capacity (m3/day)
                 Prod = 328500, # Annual permeate production (m3)
                 Area = 40.8 , # Membrane area (m2)
                 Pflux = 1.1375,  # Permeate flow per module (m3/h/module)
                 NV=7,
                 Nel=8,
                 membrane_cost=30, # cost per unit area of membrane (USD/m2)
                 
                 pressure_vessel_cost= 1000, # cost per pressure vessel (USD/vessel)-- just guessing 1000 to fill value for now: 2/25/2020 
#                 FFR  = 17, # Feed flow rate per module (m3/h/module)
#                 GOR = 10.475,  # Gained output ratio
                # downtime = 0.1, # Yearly downtime of the plant (ratio)
                 yrs = 20, # Expected plant lifetime
                 int_rate = 0.04 , # Average interest rate
                 coe = 0.05,  # Unit cost of electricity ($/kWh)
                 chem_cost=0.05, # specific chemical cost ($/m3)
                 labor_cost=0.1,  # specific labor cost ($/m3)
                 rep_rate=0.15,    # membrane replacement rate
                 equip_cost_method='general', # Option 1:'general' capex breakdown by cost factor; Option 2: 'specify' equipment costs
                 sec= 2.5 # specific energy consumption (kwh/m3)
                 #coh = 0.01 , # Unit cost of heat ($/kWh)
                 #sam_coh = 0.02, # Unit cost of heat from SAM ($/kWh)
                 #solar_inlet = 85, # Solar field inlet temperature
                 #solar_outlet = 95, # Solar field outlet temperature
                 #HX_eff = 0.85, # Heat exchanger efficiency
                 #cost_module_re = 0.220 , # Cost of module replacement ($/m3)
                 ):
        self.ann_prod=Prod
        self.chem_cost=chem_cost
        self.labor_cost=labor_cost
        self.operation_hour = 24 #* (1-downtime) # Average daily operation hour (h/day)
        self.Pflux = Pflux
        self.Area = Area
        self.PF_module = self.Pflux * self.Area
        self.num_modules = NV*Nel
        self.total_area = self.num_modules*self.Area
        self.membrane_cost=membrane_cost
        self.pressure_vessel_cost=pressure_vessel_cost
        self.NV=NV
        self.SEC=sec
        self.capacity=Capacity
        self.equip_cost_method=equip_cost_method
        self.replacement_rate=rep_rate
        self.membrane_replacement_cost=self.membrane_cost*self.total_area*self.replacement_rate/self.ann_prod

#        self.HX_eff = HX_eff

#        self.th_module = th_module
#        self.FFR = FFR
        if coe:
            self.coe = coe
        else:
            self.coe = sam_coe
#        self.cost_module_re = cost_module_re
        self.yrs = yrs
        self.int_rate = int_rate
        
    def lcow(self):
        if self.equip_cost_method=='specify':
            self.total_module_cost = self.total_area*self.membrane_cost + self.NV*self.pressure_vessel_cost
    #        self.HPpump_cost=
    #        self.BPpump_cost=
    #        self.ERD_cost=
#            self.other_equip_cost=
#            self.equip_cost=self.HPpump_cost + self.BPpump_cost +self.ERD_cost + self.other_equip_cost
            self.CAPEX = self.total_module_cost*CR_factor(self.yrs,self.int_rate) / self.ann_prod
#           (self.cost_sys*1000*self.int_rate*(1+self.int_rate)**self.yrs) / ((1+self.int_rate)**self.yrs-1) / self.Prod
            self.unit_capex=self.total_module_cost/self.capacity  
#        elif self.equip_cost_method=='general':
        else:    
            self.total_capex=1100  # total EPC cost, USD/(m3/day)
            self.CAPEX =self.total_capex*CR_factor(self.yrs,self.int_rate) / self.ann_prod
#           self.equip_cost=
#        self.other_cap = (5 * (self.num_modules/3)**0.6 + 5 * (self.num_modules/3)**0.5 + 3*(self.Feed/5)**0.6 + 15 *(self.num_modules/3)**0.3 + 0.25*5 + 2*5*(self.Feed/10)**0.6) *1.11
#        self.cost_sys = (self.module_cost + self.HX_cost + self.other_cap)
        self.cost_elec = self.SEC * self.coe
        self.OPEX = self.cost_elec+self.chem_cost +self.labor_cost + self.membrane_replacement_cost#maintenance and membrane replacement
        
        self.LCOW = self.CAPEX + self.OPEX
        
        cost_output = []
        cost_output.append({'Name':'Desal Annualized CAPEX','Value':self.CAPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Desal OPEX','Value':self.OPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of water','Value':self.LCOW,'Unit':'$/m3'})
        
        return cost_output
    
#    def cost_method(self):
    
    #%%
    rocost=RO_cost()
    rocost.lcow()
    