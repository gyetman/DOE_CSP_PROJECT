# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:35:50 2019
@author: zzrfl
"""

from DesalinationModels.AGMD_PSA import AGMD_PSA
from DesalinationModels.FO_Trevi import FO_Trevi

# Initiate calculation from RO designing
MD = AGMD_PSA(FFR_r= 317958.3, FeedC_r= 6)
MD.calculations()
# Retreive system performance from RO model
RO_feed = RO.Qf1*24
RO_brine = RO.Qb1*24
RO_permeate = MD.F_AS7_prod*24
RO_p_s = RO.Cp *1000
RO_brine_salinity = (RO.Cf * RO_feed - RO.Cp * RO_permeate)/ RO_brine /1000 # weight percentage (34 g/L = 0.034%)


# Initiate calculation in FO model
FO_RR = 0.9
FO_ror = 0.0000001
FO_Mprod = RO_brine * FO_RR * (1-FO_ror)

FO = FO_Trevi(Salt_rej = 0.962, T_sw = RO.T, salinity = RO_brine_salinity, RO_r = FO_ror, r=FO_RR, Mprod = FO_Mprod, f_sw_sup = FO_Mprod * 0.6 )
FO.flow_rate_calculations()  
FO.membrane_heat_calculations()      
FO.system_calculations()

Thermal_load = FO.HX1C['Hot side heat load(kW)'] + FO.HX2C['Hot side heat load(kW)']
FO_p_s = (1-FO.Salt_rej) * RO_brine_salinity *1000 * RO_brine / FO_Mprod
FO_b_s = FO.Salt_rej * RO_brine_salinity *1000 * RO_brine / (RO_brine - FO_Mprod)


print('Total feed water (m3/day): ', RO_feed)
print('RO permeate (m3/day): ', RO_permeate)
print('RO permeate salinity (mg/L): ', RO_p_s)
print('RO brine  (m3/day): ', RO_brine)
print('RO brine salinity (mg/L): ', RO_brine_salinity*1000)

print('FO permeate (m3/day): ', FO_Mprod)
print('FO permeate salinity (mg/L): ', FO_p_s)
print('FO brine (m3/day): ', RO_brine - FO_Mprod)
print('FO brine salinity (mg/L): ', FO_b_s)
print('RO recovery rate: ', RO_permeate/RO_feed)
print('FO recovery rate: ', FO_Mprod/RO_brine)
print('System recovery rate: ', (FO_Mprod+RO_permeate)/RO_feed)
print('RO power consumption(kW): ', RO.PowerRO)
print('FO thermal load (kW): ', Thermal_load)
#specific power consumption, concentration of the brine,