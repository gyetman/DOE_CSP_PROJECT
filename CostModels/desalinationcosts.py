# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 23:59:23 2019
General (simple) Economic Model for Desalination Plants
SI Units
@author: adamAatia
"""

## Capital Recovery Factor function: compute capital recovery factor based on plant lifetime and discount rate. 
# This capital recovery factor is multiplied by the total capex to compute the fixed charge capital cost.
# t is time in years, r is discount or interest rate (fraction)
def CR_factor(t=30,r=0.05): 
    return 1/((1 - (1 / (1 + r) ** t)) / r)


# user-provided inputs (or supplied by model)    
daily_cap= 10000         # daily capacity of desalination plant, m3/day

unit_capex=1100          # unit installed cost of desal plant, USD/m3/day

specific_O_M=0.25        # specific O&M costs excluding energy cost, USD/m3 (per cubic meter of water produced)

LCOE=0.01                #levelized cost of electricity, USD/kWh 

LCOH=0.0                 #levelized cost of heat, USD/kwhthermal

SEC_e=3                  # specific electrical energy consumption,  kWh/m3 produced

SEC_th=20                # specific thermal energy consumption, kWhthermal/m3

utilization_factor=0.95  #percent of year that desalination plant operates at full capacity (i.e., capacity factor), unitless

lifetime=50              # desalination plant lifetime, years        

discount_rate=0.05       #discount rate, unitless

# calculations
specific_energy_cost= SEC_e*LCOE + SEC_th*LCOH          #total specific energy cost, USD/m3

total_annual_water=daily_cap*365*utilization_factor     #total annual water produced by desalination plant, m3


total_capex=daily_cap*unit_capex                        # total capital cost of desalination plant, USD


annualized_capex=total_capex*CR_factor(lifetime,discount_rate) # annualized (fixed) capital cost, USD/year

fixed_capex_per_m3=annualized_capex/total_annual_water      #fixed capital cost per cubic meter of water produced, USD/m3

LCOW=fixed_capex_per_m3 + specific_O_M + specific_energy_cost   #levelized cost of water, USD/m3
