# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 14:04:17 2020

@author: zzrfl
"""

import numpy as np
import math

class ETC_cost(object):
    def __init__(self,
                 aperture_area = 1000, 
                 non_solar_area_multiplier = 1.1,
                 land_cost = 10000, # $/acre
                 capacity = 1000, # solar field capacity (kW)
                 EC = 1, # % of capacity (kW)
                 yrs = 20, # Expected plant lifetime
                 int_rate = 4 , # Average interest rate
                 coe = 0.05 , # Unit cost of electricity ($/kWh)
                 p_OM = 0.5, # % of the capital cost
                 unit_cost = 372, # unit cost ($/m2)
                 P_req = 200, # required thermal energy from the desalination (kW)
                 cost_boiler = 102.36, # $/kW
                 
                 thermal_gen = 1000 * 0.3 * 24 * 365, # annual energy generation (kWh)
                 
                 ):
        


        self.coe = coe
        self.yrs = yrs
        self.int_rate = int_rate / 100
        self.EC = EC / 100
        self.capacity = capacity
        self.unit_cost = unit_cost
        self.aperture_area = aperture_area
        self.gross_area = aperture_area * non_solar_area_multiplier
        self.cost_boiler = cost_boiler
        self.p_OM = p_OM / 100
        self.thermal_gen = thermal_gen
        self.land_cost = land_cost
        self.P_req = P_req # kW
        
    def lcoh(self):
        
        if self.unit_cost:
            self.c_solar = self.gross_area * self.unit_cost 
        else:
            self.unit_cost = 1 # add regression model
        self.c_boiler = self.cost_boiler * self.P_req
        self.land_cost = self.gross_area * self.land_cost / 4046.86
        self.OM = self.p_OM * self.c_solar
        self.elec_cost = self.EC *  self.capacity * self.coe
        
        self.factor = self.int_rate*(1+self.int_rate)**self.yrs / ((1+self.int_rate)**self.yrs-1) 
        self.CAPEX = (self.c_solar + self.land_cost + self.c_boiler) * self.factor / self.thermal_gen
        self.OPEX = (self.OM + self.elec_cost) / self.thermal_gen
        
        self.lcoh = self.CAPEX + self.OPEX
        
        
        
        cost_output = []
        cost_output.append({'Name':'Desal CAPEX','Value':self.CAPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Desal OPEX','Value':self.OPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of heat','Value':self.lcoh,'Unit':'$/kWh'}) 
        
        return cost_output
#%%
# case2 = VAGMD_cost(coh = 100)
# print(case2.lcow())
