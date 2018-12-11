# -*- coding: utf-8 -*-
"""
Simulating desalination with wrapper from SAM
    + CSP Linear Fresnel Direct Steam
    + PPA Partnership flip with Debt
    + PSA models for MED
Created by: Vikas Vicraman
Create date: 11/22/2018
V1: - Integration by implementing Python classes for wrappers
    - Code able to access variables from both modules
    - Condenser Pressure to be calculated from SAM User-defined Power Cycle
    - Calculate Condenser Temperature from Condenser Pressure using Thermodynamic equaitons
"""

from PSA.Model_MED_PSA import medPsa as psaMed
from SAM.SamCspLinearFresnelDirectSteam import samCspLinearFresnelDirectSteam as SamCsp
import numpy as np

#Initializing SAM Csp Modules
sam = SamCsp()
Condenser_pressure = sam.ssc.data_get_array(sam.data, b'P_cond');
Field_mf = sam.ssc.data_get_array(sam.data, b'm_dot');

#Code for calculating Condenser temerature goes below
Cond_temp = []
Cond_temp_root2 = []

print ('Condenser Pressure (year 1) = ')
for i in Condenser_pressure:
#   Coefficients for the equation to find out Condenser Temperature
    coeff = [9.655*10**-4, -0.039, 4.426, -19.64, (1123.1 - i)]
    
    temps = np.roots(coeff)
    #Getting real roots
    temps_real = temps.real[abs(temps.imag < 1e-5)] #Imaginary parts are sometimes not exaclty zero becuase of approximations in calculation
    #Filtering for positive values
    temps_yearly = temps_real[temps_real >= 0]
    Cond_temp.append(temps_yearly) #Enter equation here
    
    #Making an array of the second real root as it seemed to model actual values better
    #By analyzing the outputs, it was found that root2 of the fourth order equation gave right values
    Cond_temp_root2.append(temps_yearly[1])
    
    ### Get mass flow rate also from SAM (Mf in PSA)
    ### Equations will change for different Temperature Thresholds in PSA models
    ### Check for other SAM outputs to understand what the model is actually
    ### Cut-off temperature
    
    
    
    
    
    
    
    
    #print(temps_yearly)
#Condenser_pressure = sam.ssc.data_get_array(sam.data, b'T_sys_h');
Condenser_temperature = np.asarray(Cond_temp)
np.savetxt("CondTemp.csv", Condenser_temperature, delimiter = ",")
print ('Field HTF temperature hot header outlet (year 1) = ')
#for i in Condenser_pressure:
#    print (i, ', ')
sam.data_free()

PerfRatio= [] 
RecoveryRatio= []
Xbn= [] 
sA= []

#print(Field_mf)
k = 0
for j in Cond_temp_root2:
    psa = psaMed()
    psa.Ts = j 
    #psa.Ms = Field_mf[k]#/3600 #As the unit for M-dot_to_pb is (kg/hr)
    
    psa.execute_module()
    PerfRatio.append(psa.PR)
    RecoveryRatio.append(psa.RR)
    Xbn.append(psa.Xbn)
    sA.append(psa.sA)
    
    k += 1
    
PR = np.asarray(PerfRatio)
np.savetxt("PerfRatio.csv", PR, delimiter = ",")

RR = np.asarray(RecoveryRatio)
np.savetxt("RecRatio.csv", RR, delimiter = ",")

Xbn_array = np.asarray(Xbn)
np.savetxt("Xbn_array.csv", Xbn_array, delimiter = ",")

sA_array = np.asarray(sA)
np.savetxt("sA_array.csv", sA_array, delimiter = ",")

cond_root2 = np.asarray(Cond_temp_root2)
np.savetxt("cond_root2.csv", cond_root2, delimiter = ",")

Field_mf2 = np.asarray(Field_mf)
np.savetxt("Field_mf.csv", Field_mf, delimiter = ",")


    
    