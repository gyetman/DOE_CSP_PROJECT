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


class RO_FO_cost(object):
    def __init__(self,
                 Capacity = 712, # Desalination plant capacity (m3/day)
                 Prod = 328500, # Annual permeate production (m3)
                 Area = 40.8 , # Membrane area (m2)
                 grid_usage = 0, # Total fuel usage (%)
                 # Pflux = 1.1375,  # Permeate flow per module (m3/h/module)
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
                 solar_coh = None,
                 solar_coe = None,
                 sam_coe = 0.02,
                 chem_cost=0.05, # specific chemical cost ($/m3)
                 labor_cost=0.1,  # specific labor cost ($/m3)
                 rep_rate= 5 ,    # membrane replacement rate (year)
                 equip_cost_method='general', # Option 1:'general' capex breakdown by cost factor; Option 2: 'specify' equipment costs
                 sec= 2.5, # specific energy consumption (kwh/m3)
                 HP_pump_pressure=60, # high pressure pump discharge pressure (bar)
                 HP_pump_flowrate=41.67,   # high pressure pump flowrate (m3/hr)
                 BP_pump_pressure=10.5, # booster pump discharge pressure (bar)
                 BP_pump_flowrate=62.5, # booster pump flowrate (m3/hr)
                 ERD_flowrate=62.5,     # ERD flowrate set to brine flowrate(m3/hr)
                 ERD_pressure=49  ,      # ERD pressure set to brine pressure entering (bar)  
                 disposal_cost=0.03,    # specific waste disposal cost($/m3)
                 #coh = 0.01 , # Unit cost of heat ($/kWh)
                 #sam_coh = 0.02, # Unit cost of heat from SAM ($/kWh)
                 #solar_inlet = 85, # Solar field inlet temperature
                 #solar_outlet = 95, # Solar field outlet temperature
                 #HX_eff = 0.85, # Heat exchanger efficiency
                 #cost_module_re = 0.220 , # Cost of module replacement ($/m3)
                 unit_capex=1100,  # total EPC cost, USD/(m3/day)
                 cost_storage = 26 , # Cost of thermal storage ($/kWh)
                 cost_battery = 150, # cost of battery ($/kWh)
                 storage_cap = 0, # Capacity of thermal storage (kWh)
                 battery_cap = 0, # Capacity of battery (kWh)
                 
                 FO_capacity = 288,
                 FO_SEC = 1, # kWh/m3
                 FO_STEC = 30, # kWh/m3
                 FO_labor = 0.13, # $/m3
                 FO_chem_cost = 0.07 , # $/m3
                 FO_goods_cost = 0.05, # $/m3
                 FO_unit_capex= 1000, # $/m3/day
                 sam_coh = 0.02, # $/kWh
                 coh = 0.01, # $/kWh
                 FO_fuel_usage = 0, # %
                 
                 insurance = 0.5, # %
                 downtime = 10,  # % 
                 
                 ):
        self.HP_pump_pressure=HP_pump_pressure
        self.HP_pump_flowrate=HP_pump_flowrate
        self.BP_pump_pressure=BP_pump_pressure
        self.BP_pump_flowrate=BP_pump_flowrate
        self.ERD_flowrate=ERD_flowrate
        self.ERD_pressure=ERD_pressure
        self.downtime = downtime
        self.Prod=Prod * (1-self.downtime/100)
        self.chem_cost=chem_cost
        self.labor_cost=labor_cost
        self.operation_hour = 24 #* (1-downtime) # Average daily operation hour (h/day)
        # self.Pflux = Pflux
        self.Area = Area
        # self.PF_module = self.Pflux * self.Area
        self.num_modules = NV*Nel
        self.total_area = self.num_modules*self.Area
        self.membrane_cost=membrane_cost
        self.pressure_vessel_cost=pressure_vessel_cost
        self.NV=NV
        self.SEC=sec
        self.capacity=Capacity
        self.equip_cost_method=equip_cost_method
        self.replacement_rate= 1/ rep_rate
        self.membrane_replacement_cost=self.membrane_cost*self.total_area*self.replacement_rate/self.Prod
        self.disposal_cost=disposal_cost
#        self.HX_eff = HX_eff
        self.unit_capex = unit_capex
#        self.th_module = th_module
#        self.FFR = FFR
        self.insurance = insurance / 100
        self.coe = coe
        if solar_coe:
            self.sam_coe = solar_coe
        else:
            self.sam_coe = sam_coe
        self.grid_usage = grid_usage / 100

#        self.cost_module_re = cost_module_re
        self.yrs = yrs
        self.int_rate = int_rate
        self.cost_storage = cost_storage
        self.storage_cap = storage_cap
        self.battery_cap = battery_cap
        self.cost_battery = cost_battery

        self.FO_capacity = FO_capacity
        self.FO_SEC = FO_SEC # kWh/m3
        self.FO_STEC = FO_STEC # kWh/m3
        if FO_labor != 0.13:
            self.FO_labor = FO_labor
        else:
            self.FO_labor = 0.04757 * self.FO_capacity ** (-0.178)
            
        
        if FO_unit_capex != 1000:
            self.FO_unit_capex = FO_unit_capex
        else:
            self.FO_unit_capex = 26784 * self.FO_capacity ** (-0.428)
        self.FO_goods_cost = FO_goods_cost # $/m3
        self.FO_chem_cost = FO_chem_cost
        if solar_coh:
            self.sam_coh = float(solar_coh)
        else:
            self.sam_coh = sam_coh
        self.coh = coh # $/kWh
        self.FO_fuel_usage = FO_fuel_usage / 100   # %

        
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
            if self.unit_capex[0]:
                self.unit_capex_empirical = [self.unit_capex]
            else:
                self.unit_capex_empirical = [3726.1 * self.capacity[0] ** (-0.071)]
            self.EPC_cost = self.capacity[0] * self.unit_capex_empirical[0]

            self.RO_CAPEX =(self.EPC_cost + self.cost_battery * self.battery_cap)*self.int_rate*(1+self.int_rate)**self.yrs / ((1+self.int_rate)**self.yrs-1) #/ self.ann_prod
           
        self.FO_total_CAPEX = self.FO_capacity * self.FO_unit_capex
        self.FO_CAPEX = ((self.FO_total_CAPEX + self.cost_storage * self.storage_cap)*self.int_rate*(1+self.int_rate)**self.yrs) / ((1+self.int_rate)**self.yrs-1) 

        self.cost_elec = (self.SEC + self.FO_SEC) * (self.grid_usage * self.coe + (1-self.grid_usage) * self.sam_coe)
        self.cost_heat = self.FO_STEC * (self.FO_fuel_usage * self.coh + (1-self.FO_fuel_usage) * self.sam_coh) 
        
        
        self.RO_OPEX = self.cost_elec + self.chem_cost +self.labor_cost + self.membrane_replacement_cost#maintenance and membrane replacement
        self.FO_OPEX = self.cost_heat + self.FO_labor + self.FO_chem_cost + self.FO_goods_cost 
 
        self.insurance_cost = (self.EPC_cost + self.FO_total_CAPEX + + self.cost_battery * self.battery_cap + self.cost_storage * self.storage_cap) *self.insurance  / (self.Prod)
        self.OPEX = self.RO_OPEX + self.FO_OPEX  + self.disposal_cost
        self.CAPEX = (self.RO_CAPEX + self.FO_CAPEX ) / self.Prod
        self.LCOW = self.CAPEX + self.OPEX + self.insurance_cost 
#        self.test=(self.total_capex*self.int_rate*(1+self.int_rate)**self.yrs) / ((1+self.int_rate)**self.yrs-1) / self.ann_prod
        cost_output = []
        cost_output.append({'Name':'Desal Annualized CAPEX','Value':self.CAPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Desal OPEX','Value':self.OPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of water','Value':self.LCOW,'Unit':'$/m3'})
        cost_output.append({'Name':'Annual water production','Value':self.Prod,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of electricity (from solar field)','Value':self.sam_coe,'Unit':'$/kWh(e)'})
        cost_output.append({'Name':'Levelized cost of heat (from solar field)','Value':self.sam_coh,'Unit':'$/kWh(th)'})
        cost_output.append({'Name':'Levelized cost of heat (from fossile fuel)','Value':self.coh,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of heat (from solar field)','Value':self.sam_coh,'Unit':'$/m3'})
        # cost_output.append({'Name':'Energy cost','Value':self.cost_elec,'Unit':'$/m3'})    
        
        return cost_output
    
#    def pump_cost(pumppressure,pumpflowrate):
#        pumpcapex=53*pumppressure*pumpflowrate
#        return pumpcapex
#    def cost_method(self):
    
    #%%
    # rocost=RO_cost()
    # rocost.lcow()
