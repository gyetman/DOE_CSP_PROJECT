# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 23:59:23 2019

General (simple) Economic Model for Desalination Plants
SI Units
@author: adamAatia
"""

## Capital Recovery Factor 
# t is time in years, r is discount or interest rate (fraction)
def CR_factor(t=30,r=0.05): 
    return 1/((1 - (1 / (1 + r) ** t)) / r)
    
daily_cap= 10000

unit_capex=1100 # USD/m3/day

specific_O_M=0.25

LCOE=0.01 #USD/kWh 

LCOH=0.0  #USD/kwhthermal

SEC_e=3 # kWh/m3 produced

SEC_th=20 #kWhthermal/m3

specific_energy_cost= SEC_e*LCOE + SEC_th*LCOH

utilization_factor=0.95


total_annual_water=daily_cap*365*utilization_factor


total_capex=daily_cap*unit_capex

lifetime=50

discount_rate=0.05

annualized_capex=total_capex*CR_factor(lifetime,discount_rate)

fixed_capex_per_m3=annualized_capex/total_annual_water

LCOW=fixed_capex_per_m3 + specific_O_M + specific_energy_cost