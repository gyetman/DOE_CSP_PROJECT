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


class RO_MDB_cost(object):
    def __init__(self,
                 Capacity = 689.66, # Desalination plant capacity (m3/day)
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
                 sam_coe = 0.02,
                 solar_coe = None,
                 chem_cost=0.05, # specific chemical cost ($/m3)
                 labor_cost=0.1,  # specific labor cost ($/m3)
                 rep_rate=5,    # membrane replacement rate
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
                 cost_storage = 26 , # Cost of battery ($/kWh)
                 storage_cap = 0, # Capacity of battery (kWh)
                 
                 MDB_capacity = 310.34,
                 MDB_SEC = 1.8, # kWh/m3
                 MDB_STEC = 62.18, # kWh/m3
                 MDB_OM = 1.8, # % of unit capex

                 solar_inlet = 85, # Solar field inlet temperature
                 solar_outlet = 95, # Solar field outlet temperature
                 HX_eff = 0.85, # Heat exchanger efficiency
                 cost_module_re = 0.220 , # Cost of module replacement ($/m3)

                 MD_membrane = 0.075*1.2, # Base price of AGMD membrane (k$/m2)
                 HX = 0.35 * 1.2, # Base price of heat exchanger (k$/m2)
                 
                 MD_module = 1.95* 1.2,# Base price of AGMD module assembly (k$/base capacity)
                 MD_module_capacity = 3, # Base capacity of module assembly (modules)   
                                  
                 endplates = 0.85* 1.2,# Base price of HX endplates (k$/base capacity)
                 endplates_capacity =10, # Base capacity of housing rack (m2)
                 heat_cool = 5* 1.2, # Base price of heating/cooling installation (k$/base capacity)
                 heat_cool_capacity =10, # Base capacity of housing rack (m3/h)
                 
                 h_r = 5* 1.2,  # Base price of housing rack (k$/base capacity)
                 h_r_capacity = 3, # Base capacity of housing rack (modules)
                 tank = 5* 1.2,  # Base price of tank (with plumbing) (k$/base capacity)
                 tank_capacity = 3, # Base capacity of tank (modules)
                 pump = 3* 1.2,  # Base price of pump (k$/base capacity)
                 pump_capacity = 5, # Base capacity of pump (m3/h)
                 other = 15* 1.2,  # Base price of controller, cabling and programming (k$/base capacity)
                 other_capacity = 3, # Base capacity of controller, cabling and programming (modules)

                 MDB_Area = 25.92 , # Membrane area (m2)
                 Pflux = 2.832,  # Permeate flux per module (l/h/module)
                 TCO  = 76.288, # Condenser channel outlet temperature (ยบC)
                 TEI  = 80, # Condenser channel inlet temperature (C)
                 FFR  = 1100, # Feed flow rate per module (l/h/module)
                 th_module  = 4.560, # Thermal power supplied per module (kW(th)/module)
                 insurance = 0.5,  # %
                 solar_coh = None,
                 sam_coh = 0.02, # $/kWh
                 coh = 0.01, # $/kWh
                 MDB_fuel_usage = 0, # %
                 downtime = 10  # % 

                 
                 ):
        self.HP_pump_pressure=HP_pump_pressure
        self.HP_pump_flowrate=HP_pump_flowrate
        self.BP_pump_pressure=BP_pump_pressure
        self.BP_pump_flowrate=BP_pump_flowrate
        self.ERD_flowrate=ERD_flowrate
        self.ERD_pressure=ERD_pressure
        self.downtime = downtime
        self.Prod=Prod * (1 - self.downtime / 100)
        self.chem_cost=chem_cost
        self.labor_cost=labor_cost
        self.operation_hour = 24 #* (1-downtime) # Average daily operation hour (h/day)
        # self.Pflux = Pflux
        self.Area = Area
        # self.PF_module = self.Pflux * self.Area
        self.total_area = NV*Nel*self.Area
        self.membrane_cost=membrane_cost
        self.pressure_vessel_cost=pressure_vessel_cost
        self.NV=NV
        self.SEC=sec
        self.capacity=Capacity
        self.equip_cost_method=equip_cost_method
        self.replacement_rate=1 / rep_rate
        self.membrane_replacement_cost=self.membrane_cost*self.total_area*self.replacement_rate/self.Prod
        self.disposal_cost=disposal_cost
#        self.HX_eff = HX_eff
        self.unit_capex = unit_capex
#        self.th_module = th_module
#        self.FFR = FFR

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
        
        self.Pflux = Pflux
        self.MDB_Area = MDB_Area
        self.PF_module = self.Pflux * self.MDB_Area
        self.MDB_capacity = MDB_capacity
        self.num_modules = math.ceil(MDB_capacity *1000 / self.PF_module / self.operation_hour)
        self.HX_eff = HX_eff
        self.solar_inlet = solar_inlet
        self.solar_outlet = solar_outlet
        self.th_module = th_module
        self.TEI = TEI
        self.TCO = TCO
        self.FFR = FFR        
        self.cost_module_re = cost_module_re
        self.MD_membrane = MD_membrane
        self.HX = HX
        self.MD_module = MD_module
        self.MD_module_capacity = MD_module_capacity
        self.endplates = endplates
        self.endplates_capacity =endplates_capacity
        self.heat_cool = heat_cool
        self.heat_cool_capacity =heat_cool_capacity
        
        self.h_r = h_r
        self.h_r_capacity = h_r_capacity
        self.tank = tank
        self.tank_capacity = tank_capacity
        self.pump = pump
        self.pump_capacity = pump_capacity
        self.other = other
        self.other_capacity = other_capacity
        self.insurance = insurance / 100
        if solar_coh:
            self.sam_coh = float(solar_coh)
        else:
            self.sam_coh = sam_coh
        self.coh = coh # $/kWh
        self.MDB_fuel_usage = MDB_fuel_usage / 100 # %
        self.MDB_SEC = MDB_SEC
        self.MDB_STEC = MDB_STEC
                
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

            self.RO_CAPEX =(self.EPC_cost)*self.int_rate*(1+self.int_rate)**self.yrs / ((1+self.int_rate)**self.yrs-1) #/ self.ann_prod
            

# MDB capital cost
        self.module_cost = (self.MD_module*self.MD_module_capacity*(self.num_modules/self.MD_module_capacity)**0.8 + self.MD_membrane * self.MDB_Area * self.num_modules) 
        self.delta_T2 = self.solar_outlet - self.TEI
        self.delta_T1 = self.solar_inlet - self.TCO
        self.LMTD = (self.delta_T2 - self.delta_T1) / math.log(self.delta_T2/self.delta_T1)
        self.HX_area = self.num_modules * self.th_module / self.HX_eff / 2.5 / self.LMTD
        self.HX_cost = 2 * ( self.endplates * (self.HX_area/self.endplates_capacity)**0.6 + self.HX * self.HX_area) 
        self.Feed = self.FFR * self.num_modules / 1000
        self.other_cap = (self.h_r * (self.num_modules/self.h_r_capacity)**0.6 + self.tank * (self.num_modules/self.tank_capacity)**0.5 + self.pump*(self.Feed/self.pump_capacity)**0.6 + self.other *(self.num_modules/self.other_capacity)**0.3 + 0.25*5 + 2*self.heat_cool*(self.Feed/self.heat_cool_capacity)**0.6) 
        self.cost_sys = (self.module_cost + self.HX_cost + self.other_cap + self.cost_storage * self.storage_cap / 1000)

        self.MDB_CAPEX = (self.cost_sys*1000*self.int_rate*(1+self.int_rate)**self.yrs) / ((1+self.int_rate)**self.yrs-1)
 


# Energy cost
        self.cost_elec = (self.SEC + self.MDB_SEC) * (self.grid_usage * self.coe + (1-self.grid_usage) * self.sam_coe)
        self.cost_heat = self.MDB_STEC * (self.MDB_fuel_usage * self.coh + (1-self.MDB_fuel_usage) * self.sam_coh) 
                
# RO OM cost        
        self.RO_OPEX = self.disposal_cost+self.cost_elec+self.chem_cost +self.labor_cost + self.membrane_replacement_cost#maintenance and membrane replacement
# MDB OM cost        
        self.other_OM = self.MDB_CAPEX  *0.018 / self.Prod
        self.MDB_OPEX = self.cost_module_re + self.other_OM + self.cost_heat
 
        self.OPEX = self.RO_OPEX + self.MDB_OPEX
        self.insurance_cost = (self.RO_CAPEX + self.MDB_CAPEX ) * self.insurance / (self.Prod)
        #### ADD disposal cost
        self.CAPEX = (self.RO_CAPEX + self.MDB_CAPEX ) / self.Prod
        self.LCOW = self.CAPEX + self.OPEX + self.insurance_cost

#        self.test=(self.total_capex*self.int_rate*(1+self.int_rate)**self.yrs) / ((1+self.int_rate)**self.yrs-1) / self.ann_prod
        cost_output = []
        cost_output.append({'Name':'Desal Annualized CAPEX','Value':self.CAPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Desal OPEX','Value':self.OPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of water','Value':self.LCOW,'Unit':'$/m3'})
        cost_output.append({'Name':'Annual water production','Value':self.Prod,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of electricity (from fossile fuel)','Value':self.coe,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of electricity (from solar field)','Value':self.sam_coe,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of heat (from fossile fuel)','Value':self.coh,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of heat (from solar field)','Value':self.sam_coh,'Unit':'$/m3'})
        cost_output.append({'Name':'Electricity cost','Value':self.cost_elec,'Unit':'$/m3'})   
        cost_output.append({'Name':'Thermal energy cost','Value':self.cost_heat,'Unit':'$/m3'}) 
        
        return cost_output
    
#    def pump_cost(pumppressure,pumpflowrate):
#        pumpcapex=53*pumppressure*pumpflowrate
#        return pumpcapex
#    def cost_method(self):
    
    #%%
    # rocost=RO_cost()
    # rocost.lcow()
