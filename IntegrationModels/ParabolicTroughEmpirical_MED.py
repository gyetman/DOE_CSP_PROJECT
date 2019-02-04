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
from SAM.SamCspParabolicTroughEmpirical import samCspParabolicTroughEmpirical as SamCsp
import numpy as np

sam = SamCsp()

#Initializing the ITD design temperature
Temp_ITD_design = 16
#sam.ssc.data_set_number(sam.data, b'T_ITD_des', Temp_ITD_design)

#
#module = sam.ssc.module_create(b'tcstrough_physical')	
#sam.ssc.module_exec_set_print(0);
#if sam.ssc.module_exec(module, sam.data) == 0:
#	print ('tcstrough_physical simulation error')
#	idx = 1
#	msg = sam.ssc.module_log(module, 0)
#	while (msg != None):
#		print ('	: ' + msg.decode("utf - 8"))
#		msg = sam.ssc.module_log(module, idx)
#		idx = idx + 1
#	SystemExit( "Simulation Error" );
#sam.ssc.module_free(module)

Cond_temp = [];
count = 0;
Dry_bulb_temp = sam.ssc.data_get_array(sam.data, b'tdry');
print ('Condenser Pressure (year 1) = ')
for i in Dry_bulb_temp:
    #print (', ', i)
    Cond_temp.append(i + Temp_ITD_design);
    print(Cond_temp[count]);
    count += 1;
sam.data_free()

psa = psaMed()
    
PerfRatio= [] 
RecoveryRatio= []
Xbn= [] 
sA= []

#print(Field_mf)
k = 0
for j in Cond_temp:
    psa = psaMed()
    psa.Ts = j 
    #psa.Ms = Field_mf[k]#/3600 #As the unit for M-dot_to_pb is (kg/hr)
    
    psa.execute_module()
    PerfRatio.append(psa.PR)
    RecoveryRatio.append(psa.RR)
    Xbn.append(psa.Xbn)
    sA.append(psa.sA)
    
    k += 1

#Wet_bulb_temp = sam.ssc.data_get_array(sam.data, b'twet');
#print ('Condenser Pressure (year 1) = ')
#for i in Wet_bulb_temp:
#    print (', ', i)
    
#Ref_temp_diff = sam.ssc.data_get_number(sam.data, b'dT_cw_ref')
#print ('Temperature difference = ')
#Condenser_pressure = sam.ssc.data_get_array(sam.data, b'T_sys_h');
#print ('Field HTF temperature hot header outlet (year 1) = ')
#for i in Condenser_pressure:
#    print (i, ', ')
PR = np.asarray(PerfRatio)
np.savetxt("PerfRatio_pt.csv", PR, delimiter = ",")

RR = np.asarray(RecoveryRatio)
np.savetxt("RecRatio_pt.csv", RR, delimiter = ",")

Xbn_array = np.asarray(Xbn)
np.savetxt("Xbn_array_pt.csv", Xbn_array, delimiter = ",")

sA_array = np.asarray(sA)
np.savetxt("sA_array_pt.csv", sA_array, delimiter = ",")

cond_root2 = np.asarray(Cond_temp)
np.savetxt("cond_root_pt.csv", cond_root2, delimiter = ",")

# -*- coding: utf-8 -*-

