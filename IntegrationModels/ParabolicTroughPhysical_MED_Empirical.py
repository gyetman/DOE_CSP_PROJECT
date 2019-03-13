#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 11:16:32 2019

@author: zhuoranzhang
"""

from PSA.Model_MED_PSA import medPsa as psaMed
from SAM.SamCspParabolicTroughPhysical import samCspParabolicTroughPhysical as SamCsp
import numpy as np

#Initializing SAM Csp Modules
sam = SamCsp()
Condenser_pressure = sam.ssc.data_get_array(sam.data, b'P_cond');
Field_mf = sam.ssc.data_get_array(sam.data, b'm_dot_makeup');
feedwater_outlet_temp = sam.ssc.data_get_array(sam.data, b'T_fw');

#Initializing the ITD design temperature
Temp_ITD_design = 40
sam.ssc.data_set_number(sam.data, b'T_ITD_des', Temp_ITD_design)

#Code for calculating Condenser temerature goes below
mf = Field_mf/3600/(max(Field_mf)/14) #Hot water mass flow rate (L/s). Assumed to be 12 for initial calculations

#Initializing array of zeroes for condenser temperature, distillate mass flow rate, and GOR
temps_yearly = np.zeros([len(Condenser_pressure),1])   #Condenser temperature array
temps_yearly_for_empirical = np.zeros([len(Condenser_pressure),1])  #Condenser temperature used in empirical equation
distillate_flow_rate = np.zeros([len(Condenser_pressure),1])  #Massflow rate of distillate hourly (m^3/hour)
gor_empirical = np.zeros([len(Condenser_pressure),1])   #Gain output ratio or Performance ratio of the MED Plant

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
    
    #Setting the temperature as 74 DegC for calculations as it is the maximum limit for the empirical equation.
    if temps_yearly[count] > 74 :
        temps_yearly_for_empirical[count] = 74
    else:
        temps_yearly_for_empirical[count] = temps_yearly[count]
        
    #Calculating distillate flow rate and GOR using empirical equations from Experimental characterization of a multi-effect distillation system
    #coupled to a flat plate solar collector field: Empirical correlations by Chorak et. al. (2017)   
    if temps_yearly_for_empirical[count] >= 55 and temps_yearly_for_empirical[count] <= 74 :
        distillate_flow_rate[count] = max(Field_mf)/3600/14*(-0.273 + 0.008409 * temps_yearly_for_empirical[count] - 0.04452 * mf[count] + 0.0003093 * temps_yearly_for_empirical[count] ** 2 + 0.001969 * temps_yearly_for_empirical[count] * mf[count] - 0.002485 * mf[count] **2 )       
        gor_empirical[count] = (648.2 - 26.74 * temps_yearly_for_empirical[count] - 16.45 * mf[count] + 0.3842 * temps_yearly_for_empirical[count] ** 2 + 0.3137 * temps_yearly_for_empirical[count] * mf[count] + 0.5995 * mf[count] ** 2 + - 0.001835 * temps_yearly_for_empirical[count] ** 3 - 0.002371 * (temps_yearly_for_empirical[count] ** 2) * ( mf[count]) - 0.0001411 * temps_yearly_for_empirical[count] * mf[count] ** 2 - 0.01844 * mf[count] ** 3)
            
    count += 1  

Condenser_temperature = temps_yearly
np.savetxt("CondTemp.csv", Condenser_temperature, delimiter = ",")
#print ('Field HTF temperature hot header outlet (year 1) = ')
#for i in Condenser_pressure:
#    print (i, ', ')
sam.data_free()
'''
Old: PSA design model integration 
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
mf_distillate = np.asarray(distillate_flow_rate)
np.savetxt("mf_distillate2.csv", mf_distillate, delimiter = ",")

gor_distillate = np.asarray(gor_empirical)
np.savetxt("gor_distillate2.csv", gor_distillate, delimiter = ",")
 
cond_pressure = np.asarray(Condenser_pressure)
np.savetxt("cond_pressure.csv", cond_pressure, delimiter = ",")

np.savetxt("temperature_empirical.csv", temps_yearly_for_empirical, delimiter = ",")