# -*- coding: utf-8 -*-
"""
Converted from PSA's LT-MED general design model
Created on Wed Aug 28 10:01:06 2019

@author: Zhuoran Zhang
"""

import numpy as np
import math
import DesalinationModels.IAPWS97_thermo_functions as TD_func
from DesalinationModels.LT_MED_calculation import lt_med_calculation
from scipy.optimize import fmin
from DesalinationModels.VAGMD_batch.SW_functions import SW_Density
# from DesalinationModels.LT_MED_calculation import lt_med_calculation

class ABS(object):
    
    def __init__(self,
         Xf      =  35 , # Feedwater salinity  (g/L)
         Ts      =  80     , # The temperature of the steam at the inlet of the first bundle tube, C
         Nef     =  14  , # The feed water salinity, ppm
         Capacity = 2000,    # Capacity of the plant (m3/day)
         Tin     = 15 , # Inlet seawater temperature
         RR      = 0.5 , # recovery ratio
         Tcond   = 35, # Temperature of end condenser
         pump_type = 1, # Absorption Heat Pump type ('1' for single effect, '2' for double effect (serial flow), '3' for double effect (parallel flow))
         Fossil_f = 1 # Fossil fuel fraction
         ):
        
        self.Ts = Ts
        self.Nef = Nef
        self.Capacity = Capacity
        self.Fossil_f = Fossil_f
        self.Xf = Xf *1000
        self.RR = RR
        self.Tin  = Tin
        self.Tcond = Tcond
        self.pump_type = pump_type
    
    def design(self):
        p1 = self.Xf
        p2 = self.RR
        p3 = self.Tin
        p4 = self.Capacity
        p5 = self.Ts
        qF_paras = [p1, p1**2, p2, p2*p1, p2*p1**2, p2**2, p2**2*p1, p3, p3*p1, p3*p1**2, p3**p2, p3*p2*p1, p3*p2**2, p3**2,
                    p3**2*p1, p3**2*p2, p4, p4*p1, p4*p1**2, p4*p2, p4*p2*p1, p4*p2**2, p4*p3, p4*p3*p1, p4*p3*p2, p4*p3**2, p4**2, p4**2*p1,
                    p4**2*p2, p4**2*p3, p5, p5*p1, p5*p1**2, p5*p2, p5*p2*p1, p5*p2**2, p5*p3, p5*p3*p1, p5*p3*p2, p5*p3**2, p5*p4, p5*p4*p1,
                    p5*p4*p2, p5*p4*p3, p5*p4**2, p5**2, p5**2*p1, p5**2*p2, p5**2*p3, p5**2*p4, 1, p5**3, p4**3, p3**3, p2**3, p1**3]
        paras = [p1, p2, p2*p1, p3, p3*p1, p3*p2, p4, p4*p1, p4*p2, p4*p3, p5, p5*p1, p5*p2, p5*p3, p5*p4, 1, p5**2, p4**2, p3**2, p2**2,p1**2]
        if self.Nef == 12:
            coeffs = [
                [3.78E-06,9.475024108,-6.71E-06,0.025502496,-5.68E-08,0.002142361,5.26E-06,7.48E-13,-4.13E-07,1.90E-08,-0.026811842,1.76E-08,-0.00403125,-9.75E-05,-7.06E-08,8.13073955,0.000113009,1.86E-12,-6.60E-05,-7.186574074,3.50E-13],
                [-9.60E-06,-21.51409613,2.42E-05,-0.061912353,2.07E-07,0.030173611,0.001216995,-1.40E-10,-0.000380288,-2.24E-06,0.137686707,-6.94E-08,-0.032135417,0.000468958,2.43E-06,0.35824605,-0.000958009,-6.89E-11,0.000166019,27.46921296,3.29E-13],
                [3.33E-06,0.677813505,-1.60E-05,-0.046184467,-7.50E-08,-0.001725347,-1.85E-05,-2.02E-12,-1.19E-06,3.47E-08,0.168129352,-6.74E-08,2.40E-05,-0.000370854,2.54E-07,-4.754444471,-0.000497023,-2.28E-11,-0.000111815,-0.58099537,-6.56E-11,],
                [-0.00230634,-15202.30125,0.005467824,0.095607094,1.65E-06,-0.116666667,0.215904117,-7.71E-08,-0.267987407,1.54E-06,-0.108918713,1.62E-08,0.279166667,-0.002399306,-4.49E-06,2970.129599,0.000423611,4.42E-11,0.001111111,18672.98611,9.07E-10,],
                [1.04E-05,0.264283592,1.32E-05,0.047163315,3.38E-07,0.016777778,9.20E-06,2.81E-11,1.70E-06,4.33E-08,-0.100193974,-3.51E-07,-0.019045139,-0.001225,-1.68E-07,3.645635965,0.000934421,1.40E-11,0.000734769,0.507407407,7.63E-11,]
                ]

        if self.Nef == 14:
            coeffs = [
                [4.93E-06,12.14444444,-9.44E-06,0.017453704,-8.52E-08,0.003333333,-5.59E-21,1.54E-24,1.74E-20,-5.52E-23,-0.018157407,3.33E-08,-0.005,5.00E-05,-1.06E-21,8.660509259,7.41E-06,2.76E-25,-9.26E-05,-9.203703704,-4.12E-12,],
                [-9.73E-06,-22.67687709,2.75E-05,-0.010527825,2.27E-07,0.023135417,0.001127253,-1.16E-10,-0.000384457,-1.68E-06,0.011084368,-1.09E-07,-0.018871528,-0.000242465,1.49E-06,4.266662392,4.93E-05,-8.73E-14,0.000185856,27.85023148,1.35E-11,],
                [6.75E-07,0.931018519,-1.66E-05,-0.069638611,-6.36E-08,-0.002311111,-2.91E-20,5.67E-25,1.48E-20,1.32E-22,0.072969167,-5.47E-08,-0.002188889,-3.17E-06,-5.42E-23,-1.027806019,-1.78E-06,3.88E-25,-3.44E-06,-0.68,-5.22E-11,],
                [-0.002387192,-15205.67551,0.005463889,0.022750069,2.02E-06,-0.070486111,0.215886167,-7.70E-08,-0.268027502,1.13E-06,-0.031589059,2.78E-08,0.240625,-0.0016875,-3.60E-06,2970.837205,-0.000141204,-1.89E-11,0.00081713,18679.35185,1.65E-09,],
                [1.06E-05,0.138408802,1.73E-05,0.052775079,4.72E-07,0.025378472,4.64E-10,2.38E-15,-2.08E-09,-3.81E-11,-0.074957782,-4.37E-07,-0.023222222,-0.001440799,-9.41E-12,2.683753369,0.000810648,1.63E-14,0.000828704,0.681481481,1.08E-10,]
                ]          
            
        if self.Nef == 16:
            coeffs = [
                [6.18E-06,15.06805556,-1.35E-05,0.019685185,-1.26E-07,0.0025,1.09E-19,9.04E-25,5.41E-21,-9.30E-22,-0.019824074,5.74E-08,-0.005555556,7.78E-05,-1.94E-21,9.242962963,-1.85E-06,-9.43E-26,-0.000118519,-11.35185185,-8.23E-12,],
                [-1.06E-05,-22.79269847,3.05E-05,-0.010484096,2.67E-07,0.025336806,0.001024431,-9.68E-11,-0.000380987,-1.44E-06,0.009776589,-1.25E-07,-0.019774306,-0.000281181,1.32E-06,4.357185487,7.20E-05,1.79E-13,0.000188981,27.84259259,1.33E-11,],
                [7.36E-07,0.932166667,-1.69E-05,-0.060634167,-6.45E-08,-0.002480556,-2.84E-20,2.04E-25,1.06E-20,1.43E-22,0.064106111,-5.49E-08,-0.002052778,-3.28E-06,1.42E-22,-0.943036574,-2.63E-06,3.41E-25,-3.13E-06,-0.68462963,-5.33E-11,],
                [-0.002376352,-15203.25577,0.005467593,0.017976383,2.00E-06,-0.06875,0.215886212,-7.70E-08,-0.26807285,9.48E-07,-0.085658082,2.55E-08,0.204513889,-0.001583333,-3.11E-06,2972.305599,0.000277778,1.45E-11,0.000791667,18679.44444,1.53E-09,],
                [1.45E-05,0.310544108,2.96E-05,0.05907776,7.85E-07,0.045659722,-1.33E-09,1.43E-14,4.15E-09,1.52E-11,-0.093275772,-7.39E-07,-0.042868056,-0.00199184,-1.17E-11,3.142157733,0.001137361,-4.09E-15,0.001181042,1.188194444,2.04E-10,]
                ]
                        
        self.GOR = np.dot(paras,coeffs[0])
        self.qs = np.dot(paras,coeffs[1])
        self.DELTAT = np.dot(paras,coeffs[2]) # the difference between the condensation temperature in the evaporator and the vapor temperature in such effect
        self.sA = np.dot(paras,coeffs[4])
        self.qF = np.dot(paras, coeffs[3])
        
        self.STEC = 1/self.GOR * (TD_func.enthalpySatVapTW(self.Ts+273.15)-TD_func.enthalpySatLiqTW(self.Ts+273.15))[0] *1000/3600
        self.P_req = 1/self.GOR * (TD_func.enthalpySatVapTW(self.Ts+273.15)-TD_func.enthalpySatLiqTW(self.Ts+273.15))[0] *self.Capacity *1000/24/3600
        self.PR = 2326 / self.STEC * 1000 /3600
        
        self.T_b = 37  # Brine temperature at last effect (T_b = T_d = T_cool = T_cond)
        self.h_b = TD_func.enthalpyreg1(self.T_b + 273.15, 1)    # Enthalpy of the flow at brine temperature
        self.h_sw = TD_func.enthalpyreg1(self.Tin + 273.15, 1)  
        
        self.brine_d = SW_Density(self.T_b,'c',0,'ppt',1,'bar')
        self.distillate_d = SW_Density(self.T_b,'c',self.Xf * 2,'ppm',1,'bar')     
        self.average_d = self.brine_d * self.RR + self.distillate_d * (1-self.RR)

        self.q_cooling = ( self.P_req * 3600 - (self.qF * self.average_d * self.h_b - self.qF * self.average_d * self.h_sw)) / (self.h_b - self.h_sw)

        # Add ABS  
        pp1 = self.Tcond
        pp2 = self.Ts

        if self.pump_type == 1:
            abs_coeff = [
                [0.009258,-0.0082026,-0.0001356,1.9532,5.4857e-5,7.8857e-5],
                [0.1686,0.0024348,4.7353e-5,-0.17905,-0.0085011,-0.00012585,-1.4067e-6,0.0052416,0.00016374,1.7127e-6,-6.8253e-5,-1.1867e-6,2.5029,3.44e-7,4.7067e-7],
                [-0.328,1.20229,-0.008,10.8171,0.00457143,0.00457143],
                [-0.736,1.808,-0.0264,22.0257,0.012,0.0142857]]
            abs_params = [
                [pp1, pp2, pp1*pp2, 1, pp2**2, pp1**2],
                [pp1, pp1^2, pp1^3, pp2, pp1*pp2, pp2*pp1**2, pp2*pp1**3,pp2**2,pp2**2*pp1,pp2**2*pp1**2,pp2**3,pp2**3*pp1,1,pp2**4,pp1**4],
                [pp1, pp2, pp1*pp2, 1,pp2**2, pp1**2],
                [pp1, pp2, pp1*pp2, 1,pp2**2, pp1**2]
                ]
       
        elif self.pump_type == 2:
            abs_coeff = [
                [0.002266,-0.022654,-0.0003024,2.8248,0.00014057,0.00017086],
                [0.0083408,-0.0097175,-0.0001152,0.97403,5.8114e-5,7.8286e-5],
                [-0.038,1.1574,-0.0068,3.0757,0.0028571,0.0028571],
                [-0.446,1.98886,-0.0956,37.9357,0.0417143,0.0514286]]
            abs_params = [
                [pp1, pp2, pp1*pp2, 1,pp2**2, pp1**2],
                [pp1, pp2, pp1*pp2, 1,pp2**2, pp1**2],
                [pp1, pp2, pp1*pp2, 1,pp2**2, pp1**2],
                [pp1, pp2, pp1*pp2, 1,pp2**2, pp1**2]                ]
        
        elif self.pump_type == 3:
            abs_coeff = [
                [0.023072,-0.022487,-0.00003024,2.8621,0.00013829,0.000168],
                [0.0067028,-0.0058181,-3.128e-5,0.80108,4.5714e-6,2.7771e-5],
                [-0.216,1.376,-0.0032,-1.4743,8.7918e-17,0.0022857],
                [-0.468,1.15086,-0.1136,70.5714,0.0537143,0.0657143]]

            abs_params = [
                [pp1, pp2, pp1*pp2, 1,pp2**2, pp1**2],
                [pp1, pp2, pp1*pp2, 1,pp2**2, pp1**2],
                [pp1, pp2, pp1*pp2, 1,pp2**2, pp1**2],
                [pp1, pp2, pp1*pp2, 1,pp2**2, pp1**2]                ]
        
        self.COP = np.dot(abs_params[0],abs_coeff[0])
        self.sA_pump = np.dot(abs_params[1],abs_coeff[1])        
        self.T_sh = np.dot(abs_params[2],abs_coeff[2])        
        self.T_gen = np.dot(abs_params[3],abs_coeff[3])
                
        print(self.COP, self.sA_pump, self.T_sh, self.T_gen)
         
        self.design_output = []
#        design_output.append({'Name':'Number of modules required','Value':self.num_modules,'Unit':''})
#        design_output.append({'Name':'Permeate flux of module','Value':self.Mprod,'Unit':'l/h'})
#        design_output.append({'Name':'Condenser outlet temperature','Value':self.TCO,'Unit':'oC'})
#        design_output.append({'Name':'Permeate flow rate','Value': self.F * self.num_modules,'Unit':'l/h'})    
        self.design_output.append({'Name':'Thermal power consumption','Value':self.P_req/1000 ,'Unit':'MW(th)'})
        self.design_output.append({'Name':'Specific thermal power consumption','Value':self.STEC,'Unit':'kWh(th)/m3'})
        self.design_output.append({'Name':'Feedwater flow rate','Value':self.qF,'Unit':'m3/h'})     
        if self.q_cooling[0] > 0:
            self.design_output.append({'Name':'Cooling water flow rate','Value':self.q_cooling[0] / 1000,'Unit':'m3/h'})         
        self.design_output.append({'Name':'The mass flow rate of the steam','Value':self.qs,'Unit':'kg/s'})
        self.design_output.append({'Name':'Specific heat transfer area of MED','Value':self.sA,'Unit':'m2/m3/day'})
        self.design_output.append({'Name':'Specific heat transfer area of the absorption heat pump','Value':self.sA_pump,'Unit':'m2/kW'})      
        self.design_output.append({'Name':'Overall performance ratio','Value':self.PR * self.COP,'Unit':'kg/kg'})   
        self.design_output.append({'Name':'Outlet temperature of the superheated steasm from the heat pump','Value':self.T_sh,'Unit':'oC'}) 
        self.design_output.append({'Name':'Temprature of the saturated steam required to drive the heat pump generator','Value':self.T_gen,'Unit':'oC'})   
        self.design_output.append({'Name':'Gained output ratio','Value':self.GOR,'Unit':''})  
        self.design_output.append({'Name':'Delta T','Value':self.DELTAT,'Unit':'oC'})
        if self.DELTAT < 2:
            self.design_output.append({'Name':'Warning','Value':'Delta T is too small, cost might be high','Unit':''})
        
        
        
        
        # self.design_output.append({'Name':'Specific heat exchanger area','Value':self.system.sA,'Unit':'m2/(kg/s)'}) 
        
        return self.design_output
        
    def simulation(self, gen, storage):
        self.thermal_load = self.P_req # kW
        self.max_prod = self.Capacity /24 # m3/h
        self.storage_cap = storage * self.thermal_load # kWh
        
        to_desal = [0 for i in range(len(gen))]
        to_storage =  [0 for i in range(len(gen))]
        storage_load =  [0 for i in range(len(gen))]
        storage_cap_1 =  [0 for i in range(len(gen))]
        storage_cap_2 = [0 for i in range(len(gen))]
        storage_status =  [0 for i in range(len(gen))]
        solar_loss =  [0 for i in range(len(gen))]
        load =  [0 for i in range(len(gen))]
        prod =  [0 for i in range(len(gen))]
        fuel =  [0 for i in range(len(gen))]   
        energy_consumption =  [0 for i in range(len(gen))] 
        for i in range(len(gen)):
            to_desal[i] = min(self.thermal_load, gen[i])
            to_storage[i] = abs(gen[i] - to_desal[i])
            storage_load[i] = gen[i] - self.thermal_load
            if i != 0:
                storage_cap_1[i] = storage_status[i-1]
            storage_cap_2[i] = max(storage_load[i] + storage_cap_1[i], 0)
            storage_status[i] = min(storage_cap_2[i] , self.storage_cap)
            solar_loss[i] = abs(storage_status[i] - storage_cap_2[i])
            load[i] = to_desal[i] + max(0, storage_cap_1[i] - storage_cap_2[i])
            if load[i] / self.thermal_load < self.Fossil_f:
                fuel[i] = self.thermal_load - load[i]
            energy_consumption[i] = fuel[i]+load[i]     
            prod[i] = (fuel[i]+load[i] )/ self.thermal_load * self.max_prod
        Month = [0,31,59,90,120,151,181,212,243,273,304,334,365]
        Monthly_prod = [ sum( prod[Month[i]*24:(Month[i+1]*24)] ) for i in range(12) ]
               
        simu_output = []
        simu_output.append({'Name':'Water production','Value':prod,'Unit':'m3'})
        simu_output.append({'Name':'Storage status','Value':storage_status,'Unit':'kWh'})
        simu_output.append({'Name':'Storage Capacity','Value':self.storage_cap,'Unit':'kWh'})
        simu_output.append({'Name':'Fossil fuel usage','Value':fuel,'Unit':'kWh'})
        simu_output.append({'Name':'Total water production','Value':sum(prod),'Unit':'m3'})
        simu_output.append({'Name':'Monthly water production','Value': Monthly_prod,'Unit':'m3'})
        simu_output.append({'Name':'Total fossil fuel usage','Value':sum(fuel),'Unit':'kWh'})
        simu_output.append({'Name':'Percentage of fossil fuel consumption','Value':sum(fuel)/sum(energy_consumption)*100,'Unit':'%'})        
        simu_output.append({'Name':'Solar energy curtailment','Value':solar_loss,'Unit':'kWh'})
               
        return simu_output
            
#%% MODEL EXECUTION            
# for t in range(15, 85, 5):
#     case = lt_med_general(Xf = 30, RR = 0.5, Tin = t, Capacity = 51000, Ts = 80, Nef = 12)
#     case.design()
#     print("Tin:", t, "STEC: ", case.design_output[1]['Value'], "GOR: ", case.design_output[4]['Value'])
#case.simulation(gen = [5000,6000,5000,3000,2500], storage =6)
            
        
        