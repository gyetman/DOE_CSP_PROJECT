# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 14:04:17 2020

@author: zzrfl
"""

import numpy as np
import math

class VAGMD_cost(object):
    def __init__(self,
                 Capacity = 1000, # Desalination plant capacity (m3/day)
                 Prod = 328500, # Annual permeate production (m3)
                 Area = 25.92 , # Membrane area (m2)
                 Pflux = 2.832,  # Permeate flux per module (l/h/module)
                 TCO  = 76.288, # Condenser channel outlet temperature (ºC)
                 TEI  = 80, # Condenser channel inlet temperature (C)
                 FFR  = 1100, # Feed flow rate per module (l/h/module)
                 th_module  = 4.560, # Thermal power supplied per module (kW(th)/module)
                 STEC  = 62.180, # Specific thermal energy consumption (kWh(th)/m3) 
                 SEEC = 1.25, # Specific electric energy consumption (kWh(e)/m3) 
#                 GOR = 10.475,  # Gained output ratio
                # downtime = 0.1, # Yearly downtime of the plant (ratio)
                 yrs = 20, # Expected plant lifetime
                 int_rate = 0.04 , # Average interest rate
                 coe = 0.05 , # Unit cost of electricity ($/kWh)
                 coh = 0.01 , # Unit cost of heat ($/kWh)
                 sam_coh = 0.02, # Unit cost of heat from SAM ($/kWh)
                 solar_inlet = 85, # Solar field inlet temperature
                 solar_outlet = 95, # Solar field outlet temperature
                 HX_eff = 0.85, # Heat exchanger efficiency
                 cost_module_re = 0.220 , # Cost of module replacement ($/m3)
                 ):
        
        self.operation_hour = 24 #* (1-downtime) # Average daily operation hour (h/day)
        self.Pflux = Pflux
        self.Area = Area
        self.PF_module = self.Pflux * self.Area
        self.num_modules = math.ceil(Capacity *1000 / self.PF_module / self.operation_hour) # Number of module required
        self.TEI = TEI
        self.TCO = TCO
        self.HX_eff = HX_eff
        self.solar_inlet = solar_inlet
        self.solar_outlet = solar_outlet
        self.th_module = th_module
        self.FFR = FFR
        self.coe = coe
        if coh:
            self.coh = coh
        else:
            self.coh = sam_coh
        self.cost_module_re = cost_module_re
        self.Prod = Prod
        self.STEC = STEC
        self.yrs = yrs
        self.int_rate = int_rate
        self.SEEC = SEEC
        
    def lcow(self):
        self.module_cost = (1.95*3*(self.num_modules/3)**0.8 + 0.075 * self.Area * self.num_modules) *1.11
        self.delta_T2 = self.solar_outlet - self.TEI
        self.delta_T1 = self.solar_inlet - self.TCO
        self.LMTD = (self.delta_T2 - self.delta_T1) / math.log(self.delta_T2/self.delta_T1)
        self.HX_area = self.num_modules * self.th_module / self.HX_eff / 2.5 / self.LMTD
        self.HX_cost = 2 * ( 0.85 * (self.HX_area/10)**0.6 + 0.35 * self.HX_area) * 1.11
        self.Feed = self.FFR * self.num_modules / 1000
        self.other_cap = (5 * (self.num_modules/3)**0.6 + 5 * (self.num_modules/3)**0.5 + 3*(self.Feed/5)**0.6 + 15 *(self.num_modules/3)**0.3 + 0.25*5 + 2*5*(self.Feed/10)**0.6) *1.11
        self.cost_sys = (self.module_cost + self.HX_cost + self.other_cap)
        self.CAPEX = (self.cost_sys*1000*self.int_rate*(1+self.int_rate)**self.yrs) / ((1+self.int_rate)**self.yrs-1) / (self.Prod+0.1) 
        
        self.cost_elec = self.SEEC * self.coe
        self.other_OM = self.cost_sys *1000 *0.018 / (self.Prod+0.1) +0.1
        self.cost_th = self.STEC * self.coh
        self.OPEX = self.cost_elec + self.cost_th + self.cost_module_re + self.other_OM
        
        self.LCOW = self.CAPEX + self.OPEX
        
        cost_output = []
        cost_output.append({'Name':'Desal CAPEX','Value':self.CAPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Desal OPEX','Value':self.OPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of water','Value':self.LCOW,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of heat','Value':self.coh,'Unit':'$/m3'})
        
        return cost_output
#%%

