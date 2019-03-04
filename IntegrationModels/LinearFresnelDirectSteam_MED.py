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
feedwater_outlet_temp = sam.ssc.data_get_array(sam.data, b'T_fw');


#Code for calculating Condenser temerature goes below
Cond_temp = []
Cond_temp_root2 = []
Cond_temp_root1 = []
distillate_flow_rate = []
mf = 12
gor_empirical = []

print ('Condenser Pressure (year 1) = ')
temps_yearly=np.zeros([len(Condenser_pressure),1])
count=0
for i in Condenser_pressure:
#   Coefficients for the equation to find out Condenser Temperature

    coeff = [9.655*10**-4, -0.039, 4.426, -19.64, (1123.1 - i)]
    
    temps = np.roots(coeff)
    #Getting real roots
    temps=temps[temps.imag<1e-5]
    temps=temps[temps.imag>=0]
    if len(temps)>0:
        temps_yearly[count]=np.real(max(temps))
    
    
#    temps_real = temps.real[max(temps[temps.imag < 1e-5 and temps.imag >=0])] #Imaginary parts are sometimes not exaclty zero becuase of approximations in calculation
    #Filtering for positive values
#    temps_yearly = temps_real[temps_real >= 0]
    ###Cond_temp.append(temps_yearly) #Enter equation here
    
    #Making an array of the second real root as it seemed to model actual values better
    #By analyzing the outputs, it was found that root2 of the fourth order equation gave right values
    ###Cond_temp_root2.append(temps_yearly[1])
    ### Cond_temp_root1.append(temps_yearly[0])
    
    ### Get mass flow rate also from SAM (Mf in PSA)
    ### Equations will change for different Temperature Thresholds in PSA models
    ### Check for other SAM outputs to understand what the model is actually
    ### Cut-off temperature
#    if temps_yearly[1] > 74 :
#        temps_yearly[1] = 74
    if temps_yearly[count] >= 60 and temps_yearly[count] <= 74 :
        dist_flow_rate = -0.273 + 0.008409 * temps_yearly[count] - 0.04452 * mf + 0.0003093 * temps_yearly[count] ** 2 + 0.001969 * temps_yearly[count] * mf - 0.002485 * mf **2
        distillate_flow_rate.append(dist_flow_rate)
        gor = 648.2 - 26.74 * temps_yearly[count] - 16.45 * mf + 0.3842 * temps_yearly[count] ** 2 + 0.3137 * temps_yearly[count] * mf + 0.5995 * mf ** 2 + - 0.001835 * temps_yearly[count] ** 3 - 0.002371 * (temps_yearly[count] ** 2) * ( mf) - 0.0001411 * temps_yearly[count] * mf ** 2 - 0.01844 * mf ** 3
        gor_empirical.append(gor)
    else:
        distillate_flow_rate.append(0)
        gor_empirical.append(0)
    
    count+=1  
    
    
    #print(temps_yearly)
#Condenser_pressure = sam.ssc.data_get_array(sam.data, b'T_sys_h');
Condenser_temperature = temps_yearly
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
'''    
PR = np.asarray(PerfRatio)
np.savetxt("PerfRatio.csv", PR, delimiter = ",")

RR = np.asarray(RecoveryRatio)
np.savetxt("RecRatio.csv", RR, delimiter = ",")

Xbn_array = np.asarray(Xbn)
np.savetxt("Xbn_array.csv", Xbn_array, delimiter = ",")

sA_array = np.asarray(sA)
np.savetxt("sA_array.csv", sA_array, delimiter = ",")

Field_mf2 = np.asarray(Field_mf)
np.savetxt("Field_mf.csv", Field_mf, delimiter = ",")

feedwater_outlet_temp2 = np.asarray(feedwater_outlet_temp)
np.savetxt("feedwater_outlet_temp.csv", feedwater_outlet_temp2, delimiter = ",")
'''
mf_distillate = np.asarray(distillate_flow_rate)
np.savetxt("mf_distillate2.csv", mf_distillate, delimiter = ",")

gor_distillate = np.asarray(gor_empirical)
np.savetxt("gor_distillate2.csv", gor_distillate, delimiter = ",")


cond_root2 = np.asarray(Cond_temp_root2)
np.savetxt("cond_root2_2.csv", cond_root2, delimiter = ",")
 
cond_pressure = np.asarray(Condenser_pressure)
np.savetxt("cond_pressure.csv", cond_pressure, delimiter = ",")
 
cond_root1 = np.asarray(Cond_temp_root1)
np.savetxt("cond_root1.csv", cond_root1, delimiter = ",")
    