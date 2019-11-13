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
    
daily_cap= 100

unit_capex=800 # USD/m3/day

specific_O_M=0.18 # total O&M cost per cubic meter

LCOE=0.05 #USD/kWh 

LCOH=0.0  #USD/kwhthermal

SEC_e=1 # Average specific electrical energy consumption, kWh/m3 produced

SEC_th=25 # Average specific thermal energy consumption,kWhthermal/m3

specific_energy_cost= SEC_e*LCOE + SEC_th*LCOH

utilization_factor=.4


total_annual_water=daily_cap*365*utilization_factor


total_capex=daily_cap*unit_capex

lifetime=30

discount_rate=0.05

annualized_capex=total_capex*CR_factor(lifetime,discount_rate)

fixed_capex_per_m3=annualized_capex/total_annual_water

LCOW=fixed_capex_per_m3 + specific_O_M + specific_energy_cost

print('\nTotal Capex=',total_capex,'\n\nAnnualized Capex=',annualized_capex,'\n\nLCOW=',LCOW)