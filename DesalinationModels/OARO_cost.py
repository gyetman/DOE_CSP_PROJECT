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


class OARO_cost(object):
    def __init__(self,
                 Capacity = 1000, # Desalination plant capacity (m3/day)
                 Prod = 328500, # Annual permeate production (m3)
                 oaro_area = 40.8 , # Membrane area (m2)
                 ro_area = 30,
                 Ma = 1.6e-13,
                 fuel_usage = 0, # Total fuel usage (%)
                 pumpcost = 123568,
                 erdcost = 12474,
                 # Pflux = 1.1375,  # Permeate flow per module (m3/h/module)
                 ro_cost = 30,
                 oaro_cost=50, # cost per unit area of membrane (USD/m2)
                 pressure_vessel_cost= 1000, # cost per pressure vessel (USD/vessel)-- just guessing 1000 to fill value for now: 2/25/2020 
#                 FFR  = 17, # Feed flow rate per module (m3/h/module)
#                 GOR = 10.475,  # Gained output ratio
                # downtime = 0.1, # Yearly downtime of the plant (ratio)
                 yrs = 20, # Expected plant lifetime
                 int_rate = 0.04 , # Average interest rate
                 coe = 0.07,  # Unit cost of electricity ($/kWh)
                 sam_coe = 0.07,
                 downtime = 10, # Annual downtime percentage (%)
                 sec = 5.3, #
                 chem_cost=0.03, # specific chemical cost ($/m3)
                 labor_cost=0.05,  # specific labor cost ($/m3)
                 disposal_cost = 0.01, # specific disposal cost ($/m3)
                 insurance = 0.5, # percentage of capex (%)
                 rep_rate=5,    # membrane replacement 
                 practical_inv_factor = 1.6, # Practical investment factor to convert total equipment costs to total capital investment
                 storage_cap = 0, # Capacity of battery (kWh)
                 cost_storage = 26,
                 solar_coe = None,
                 ):

        self.chem_cost=chem_cost 
        self.labor_cost=labor_cost 
        self.disposal_cost = disposal_cost
        self.insurance = insurance / 100
        self.downtime = downtime #* (1-downtime) # Average daily operation hour (h/day)
        # self.Pflux = Pflux
        self.oaro_area = oaro_area
        self.ann_prod=Prod * (1-downtime/100)
        self.ro_area = ro_area
        self.Ma = Ma
        self.pumpcost = pumpcost
        self.erdcost = erdcost
        # self.PF_module = self.Pflux * self.Area
        self.ro_cost = ro_cost
        self.oaro_cost =oaro_cost
        # self.total_area = self.num_modules*self.Area

        self.SEC=sec
        self.capacity=Capacity

        # calculate membrane replacement cost
        rep_yr = rep_rate
        self.replacement_rate = 0
        while rep_yr < yrs:
            self.replacement_rate += 1 / (1+int_rate) ** rep_yr
            rep_yr += rep_rate              
        self.replacement_rate *= CR_factor(yrs,int_rate)

        
        if solar_coe:
            self.sam_coe = solar_coe
        else:
            self.sam_coe = sam_coe
        self.coe = coe
        self.fuel_usage = fuel_usage / 100
        self.practical_inv_factor = practical_inv_factor
#        self.cost_module_re = cost_module_re
        self.yrs = yrs
        self.int_rate = int_rate
        self.cost_storage = cost_storage
        self.storage_cap = storage_cap  
        
        
    def lcow(self):

        self.CAPEX = (self.oaro_area * self.oaro_cost + self.ro_area * self.ro_cost + self.pumpcost + self.erdcost ) * self.practical_inv_factor
        self.memrepcost = (self.oaro_area * self.oaro_cost + self.ro_area * self.ro_cost) * self.replacement_rate / self.ann_prod
        self.maintlaborcost = self.labor_cost 
        self.chemicost = self.chem_cost 
        self.disposalcost = self.disposal_cost 
        self.energycost = self.SEC * (self.fuel_usage * self.coe + (1-self.fuel_usage) * self.sam_coe)
        self.salmakeupcost = 0.025 *self.Ma* 3600* self.ann_prod/self.capacity
        self.insurance_cost = self.insurance * self.CAPEX / self.ann_prod
        self.OPEX = self.memrepcost +  self.chemicost + self.maintlaborcost + self.salmakeupcost + self.disposalcost + self.insurance_cost + self.energycost
        

        CR_factor = 1/((1 - (1 /(1 + self.int_rate ) ** self.yrs)) / self.int_rate )
        self.annualized_CAPEX = CR_factor * self.CAPEX / self.ann_prod
        
        self.cost_elec = self.SEC * (self.fuel_usage * self.coe + (1-self.fuel_usage) * self.sam_coe)
        
        self.LCOW = self.annualized_CAPEX + self.OPEX 

        mem_capex = CR_factor * (self.oaro_area * self.oaro_cost + self.ro_area * self.ro_cost) / self.ann_prod

        cost_output = []
        cost_output.append({'Name':'Desal Annualized CAPEX','Value':self.annualized_CAPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Desal OPEX','Value':self.OPEX,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of water','Value':self.LCOW,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of electricity (from fossile fuel)','Value':self.coe,'Unit':'$/m3'})
        cost_output.append({'Name':'Levelized cost of electricity (from solar field)','Value':self.sam_coe,'Unit':'$/m3'})
        cost_output.append({'Name':'Energy cost','Value':self.cost_elec,'Unit':'$/m3'})    

        return cost_output
    
    
    #%%
# rocost=OARO_cost()
# print(rocost.lcow())
