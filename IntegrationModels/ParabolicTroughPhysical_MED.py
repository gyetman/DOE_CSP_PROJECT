# -*- coding: utf-8 -*-
"""
Simulating desalination with wrapper from SAM
    + CSP Parabolic Trough
    + LCOE financial model
    + PSA models for MED
Created by: Vikas Vicraman
Create date: 11/22/2018
V1: - Integration by implementing Python classes for wrappers
    - Code able to access variables from both modules
    - Condenser Pressure to be calculated from SAM User-defined Power Cycle
    - Calculate Condenser Temperature from Condenser Pressure using Thermodynamic equaitons
"""

from PSA.Model_MED_PSA import medPsa as psaMed
from SAM.SamCspParabolicTroughPhysical import samCspParabolicTroughPhysical as SamCsp

sam = SamCsp()
Condenser_pressure = sam.ssc.data_get_array(sam.data, b'P_cond');
print ('Condenser Pressure (year 1) = ')
for i in Condenser_pressure:
    print (', ', i)
Condenser_pressure = sam.ssc.data_get_array(sam.data, b'T_sys_h');
print ('Field HTF temperature hot header outlet (year 1) = ')
#for i in Condenser_pressure:
#    print (i, ', ')
sam.data_free()

psa = psaMed()