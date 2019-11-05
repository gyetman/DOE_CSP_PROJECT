# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:35:50 2019

@author: zzrfl
"""

from RO_Fixed_Load_class import RODesign
from FO_Trevi import FO_Trevi

# Initiate calculation from RO designing
RO = RODesign(nominal_daily_cap_tmp=50000, R1=0.75, Cf = 6)

# Retreive system performance from RO model
RO_feed = RO.Qf1*24
RO_brine = RO.Qb1*24
RO_permeate = RO.Qp1*24
RO_brine_salinity = RO.Cf * RO_feed / RO_brine /1000 # weight percentage (34 g/L = 0.034%)


# Initiate calculation in FO model
FO_RR = 0.9
FO_ror = 0.1
FO_Mprod = RO_brine * FO_RR * (1-FO_ror) * (1-RO_brine_salinity)

FO = FO_Trevi(T_sw = RO.T, salinity = RO_brine_salinity/1000, RO_r = FO_ror, r=FO_RR, Mprod = FO_Mprod, f_sw_sup = FO_Mprod * 0.6 )
FO.flow_rate_calculations()  
FO.membrane_heat_calculations()      
FO.system_calculations()

Thermal_load = FO.HX1C['Hot side heat load(kW)'] + FO.HX2C['Hot side heat load(kW)']



print('Total feed water (m3/day): ', RO_feed)
print('Permeate from RO (m3/day): ', RO_permeate)
print('Permeate from FO (m3/day): ', FO_Mprod)
print('RO recovery rate: ', RO_permeate/RO_feed)
print('FO recovery rate: ', FO_Mprod/RO_brine)
print('System recovery rate: ', (FO_Mprod+RO_permeate)/RO_feed)
print('RO power consumption(kW): ', RO.PowerRO)
print('FO thermal load (kW): ', Thermal_load)
#specific power consumption, concentration of the brine,