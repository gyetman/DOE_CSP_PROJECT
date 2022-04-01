# -*- coding: utf-8 -*-
"""
Converted from PSA's LT-MED general design model
Created on Wed Aug 28 10:01:06 2019

@author: Zhuoran Zhang
"""

import numpy as np
import math
import DesalinationModels.IAPWS97_thermo_functions as TD_func
# from DesalinationModels.LT_MED_calculation import lt_med_calculation
from scipy.optimize import fmin
from DesalinationModels.VAGMD_batch.SW_functions import SW_Density, BPE, SW_Enthalpy
from iapws import IAPWS97, SeaWater
# from DesalinationModels.LT_MED_calculation import lt_med_calculation

class lt_med_general(object):
    
    def __init__(self,
         Xf      =  35 , # Feedwater salinity  (g/L)
         Ts      =  80     , # The temperature of the steam at the inlet of the first bundle tube, C
         Nef     =  14  , # The feed water salinity, ppm
         Capacity = 2000,    # Capacity of the plant (m3/day)
         Tin     = 15 , # Inlet seawater temperature
         RR      = 50 , # recovery ratio (%),
         TN      = 35 , # Last effect vapor temperature
         Fossil_f = 1 # Fossil fuel fraction
         ):
        
        self.Ts = Ts
        self.Nef = Nef
        self.Capacity = Capacity
        self.Fossil_f = Fossil_f
        self.Xf = Xf *1000
        self.RR = RR / 100
        self.Tin  = Tin
        self.TN = Tin +10
    
    def design(self):
        if self.Nef in [12,14]:
            Xf, RR, TN, Ts = self.Xf, self.RR, self.TN, self.Ts
            GOR_paras = [Xf, RR, RR* Xf, TN, TN*Xf, TN*RR, Ts, Ts*Xf, Ts*RR, Ts*TN, 1 , Ts**2, TN**2, RR**2, Xf**2]
                        #1           2           3               4           5             6                7
            sA_paras  = [Xf,         Xf**2,      Xf**3,          RR,         RR*Xf,        RR*Xf**2,        RR*Xf**3,
                         RR**2,      RR**2*Xf,   RR**2*Xf**2,    RR**3,      RR**3*Xf,     TN,              TN*Xf,
                         TN*Xf**2,   TN*Xf**3,   TN*RR,          TN*RR*Xf,   TN*RR*Xf**2,  TN*RR**2,        TN*RR**2*Xf,
                         TN*RR**3,   TN**2,      TN**2*Xf,       TN**2*Xf**2,TN**2*RR,     TN**2*RR*Xf,     TN**2*RR**2,
                         TN**3,      TN**3*Xf,   TN**3*RR,       Ts,         Ts*Xf,        Ts*Xf**2,        Ts*Xf**3,
                         Ts*RR,      Ts*RR*Xf,   Ts*RR*Xf**2,    Ts*RR**2,   Ts*RR**2*Xf,  Ts*RR**3,        Ts*TN,
                         Ts*TN*Xf,   Ts*TN*Xf**2,Ts*TN*RR,       Ts*TN*RR*Xf,Ts*TN*RR**2,  Ts*TN**2,        Ts*TN**2*Xf,
                         Ts*TN**2*RR,Ts*TN**3,   Ts**2,          Ts**2*Xf,   Ts**2*Xf**2,  Ts**2*RR,        Ts**2*RR*Xf,
                         Ts**2*RR**2,Ts**2*TN,   Ts**2*TN*Xf,    Ts**2*TN*RR,Ts**2*TN**2,  Ts**3,           Ts**3*Xf,
                         Ts**3*RR,   Ts**3*TN,   1,              Ts**4,      TN**4,        RR**4,           Xf**4
                         ]
            
            GOR_coeffs = {12:[3.30E-06,9.621851852,-7.98E-06,0.016637037,-1.09E-07,0.002,-0.012637326,5.13E-08,-0.003277778,8.28E-05,7.592772368,-3.09E-05,-9.98E-05,-7.425925926,-6.09E-12],
                          14:[5.27E-06,12.44928443,-1.15E-05,0.019398098,-1.59E-07,0.001666667,-0.013396636,7.88E-08,-0.003333333,0.000121663,8.195669495,-5.34E-05,-0.00013251,-9.627577763,-1.80E-11]}
            
            sA_coeffs  = {12:[0.000000E+00,3.304374E-08,-6.761157E-13,0.000000E+00,0.000000E+00,-5.496094E-09,1.958695E-13,0.000000E+00,0.000000E+00,6.105760E-09,0.000000E+00,0.000000E+00,0.000000E+00,0.000000E+00,-8.520444E-10,2.227182E-14,0.000000E+00,0.000000E+00,6.610470E-10,0.000000E+00,0.000000E+00,0.000000E+00,0.000000E+00,3.561099E-06,9.693068E-12,0.000000E+00,1.148815E-06,0.000000E+00,0.000000E+00,-1.049434E-08,0.000000E+00,0.000000E+00,0.000000E+00,1.734819E-10,-1.367980E-14,0.000000E+00,0.000000E+00,-5.044097E-10,0.000000E+00,0.000000E+00,0.000000E+00,0.000000E+00,-2.717657E-06,-3.905605E-11,0.000000E+00,-1.397796E-06,0.000000E+00,0.000000E+00,-4.132341E-08,0.000000E+00,0.000000E+00,0.000000E+00,4.380618E-07,2.072263E-11,0.000000E+00,4.398758E-07,0.000000E+00,0.000000E+00,5.991695E-08,0.000000E+00,0.000000E+00,0.000000E+00,-1.833849E-08,0.000000E+00,-3.505028E-06,0.000000E+00,1.713226E-06,0.000000E+00,0.000000E+00,6.273434E-18],
                          14:[0.000000E+00,4.368251E-08,2.260942E-13,0.000000E+00,0.000000E+00,-4.762111E-08,1.282504E-12,0.000000E+00,0.000000E+00,3.611544E-08,0.000000E+00,0.000000E+00,0.000000E+00,0.000000E+00,-3.197411E-09,8.656950E-14,0.000000E+00,0.000000E+00,3.617982E-09,0.000000E+00,0.000000E+00,0.000000E+00,0.000000E+00,6.034818E-06,4.276140E-11,0.000000E+00,4.908627E-06,0.000000E+00,0.000000E+00,-1.357859E-08,0.000000E+00,0.000000E+00,0.000000E+00,1.131144E-10,-5.279738E-14,0.000000E+00,0.000000E+00,-2.836528E-09,0.000000E+00,0.000000E+00,0.000000E+00,0.000000E+00,-3.906973E-06,-1.642642E-10,0.000000E+00,-6.562415E-06,0.000000E+00,0.000000E+00,-1.071227E-07,0.000000E+00,0.000000E+00,0.000000E+00,7.876487E-07,8.941839E-11,0.000000E+00,2.276216E-06,0.000000E+00,0.000000E+00,1.772933E-07,0.000000E+00,0.000000E+00,0.000000E+00,-6.455677E-08,0.000000E+00,-1.423548E-05,0.000000E+00,7.012498E-06,0.000000E+00,0.000000E+00,1.716278E-19]}
            
            self.GOR = np.dot(GOR_paras, GOR_coeffs[self.Nef])
            self.sA  = np.dot(sA_paras, sA_coeffs[self.Nef])
            
            self.qF = self.Capacity / self.RR / 24
            self.qs = self.Capacity * 1000 / self.GOR / 24 / 3600
        
        else:
            Xf, RR, TN, Ts = self.Xf, self.RR, self.TN, self.Ts
            GOR_paras = [Xf, RR, RR* Xf, TN, TN*Xf, TN*RR, Ts, Ts*Xf, Ts*RR, Ts*TN, 1 , Ts**2, TN**2, RR**2, Xf**2]
            sA_paras  = [Xf,    Xf**2,  RR,         RR*Xf,      RR*Xf**2,   RR**2,      RR**2*Xf,
                         TN,    TN*Xf,  TN*Xf**2,   TN*RR,      TN*RR*Xf,   TN*RR**2,   TN**2,
                         TN**2*Xf, TN**2*RR, Ts, Ts*Xf, Ts*Xf**2, Ts*RR, Ts*RR*Xf, 
                         Ts*RR**2, Ts*TN, Ts*TN*Xf, Ts*TN*RR, Ts*TN**2, Ts**2, Ts**2*Xf,
                         Ts**2*RR, Ts**2*TN, 1, Ts**3, TN**3, RR**3, Xf**3]
            
            GOR_coeffs = {3:[1.60E-07,0.826895712,-2.04E-07,0.003340838,-5.56E-09,0.000666667,-0.003295958,1.17E-10,-0.000549708,-2.46E-06,2.662545127,-1.98E-07,7.41E-07,-0.675925926,-4.12E-13],
                          6:[5.86E-07,2.940942982,-1.44E-06,0.007985234,-2.26E-08,0.001472222,-0.007157144,8.73E-09,-0.001540936,4.88E-06,4.741753363,-1.04E-06,-1.67E-05,-2.333333333,-7.41E-13],
                          9:[1.67E-06,5.9507846,-3.94E-06,0.012607651,-5.50E-08,0.002222222,-0.010203548,2.47E-08,-0.002549708,2.94E-05,6.350104873,-1.05E-05,-5.09E-05,-4.653703704,-2.88E-12],
                          12:[3.30E-06,9.621851852,-7.98E-06,0.016637037,-1.09E-07,0.002,-0.012637326,5.13E-08,-0.003277778,8.28E-05,7.592772368,-3.09E-05,-9.98E-05,-7.425925926,-6.09E-12],
                          15:[5.18E-06,13.78669547,-1.35E-05,0.020924649,-1.83E-07,0.000277778,-0.014688955,9.82E-08,-0.002836257,0.000158919,8.538343343,-6.45E-05,-0.000167731,-10.58982036,-1.63E-11]}
            
            sA_coeffs  = {3:[0.000596217,-3.66E-09,0,-2.44E-05,1.93E-09,0,5.60E-05,0,-2.95E-07,5.30E-11,0,7.14E-06,0,0.064807392,2.06E-07,0.00974051,0,-1.16E-05,-3.96E-11,0,-5.27E-06,0,-0.05718687,-2.61E-07,-0.011936049,-0.000702529,0.013464849,1.65E-07,0.003686623,0.000759933,0,-0.00019293,-0.000182949,0,3.20E-14],
                          6:[0.00040105,-6.57E-09,0,-1.56E-05,3.67E-10,0,2.62E-05,0,7.08E-07,8.73E-12,0,1.46E-06,0,0.032775092,5.04E-08,0.002499309,0,-3.30E-06,-6.53E-12,0,-1.02E-06,0,-0.028641745,-6.66E-08,-0.002735652,-0.000301667,0.005600544,4.10E-08,0.000713386,0.000329733,0,-7.31E-05,-0.00010089,0,4.94E-14],
                          9:[0.000596217,-3.66E-09,0,-2.44E-05,1.93E-09,0,5.60E-05,0,-2.95E-07,5.30E-11,0,7.14E-06,0,0.064807392,2.06E-07,0.00974051,0,-1.16E-05,-3.96E-11,0,-5.27E-06,0,-0.05718687,-2.61E-07,-0.011936049,-0.000702529,0.013464849,1.65E-07,0.003686623,0.000759933,0,-0.00019293,-0.000182949,0,3.20E-14],
                          12:[0.000894724,1.62E-08,0,-0.000287808,1.22E-08,0,0.00028908,0,-1.82E-05,2.99E-10,0,3.71E-05,0,0.130413747,8.00E-07,0.040822216,0,-3.51E-05,-2.21E-10,0,-2.85E-05,0,-0.110185354,-9.65E-07,-0.05537221,-0.001731678,0.03194821,6.33E-07,0.019196432,0.001859674,0,-0.000543621,-0.000374878,0,-9.94E-14],
                          15:[0.005685486,2.79E-07,0,-0.01767792,4.20E-07,0,0.014972954,0,-0.000685465,5.31E-09,0,0.001021958,0,0.598562516,9.56E-06,0.879295485,0,-0.000125358,-3.88E-09,0,-0.000845281,0,-0.237595008,-1.07E-05,-1.342398325,-0.012480131,0.109771476,7.64E-06,0.527896922,0.013668637,0,-0.004866016,-0.003499437,0,-2.36E-12]}
            
            self.GOR = np.dot(GOR_paras, GOR_coeffs[self.Nef])
            self.sA  = np.dot(sA_paras, sA_coeffs[self.Nef])
            
            self.qF = self.Capacity / self.RR / 24
            self.qs = self.Capacity * 1000 / self.GOR / 24 / 3600
                    
        self.T_d = self.Tin + 10  # Brine temperature at last effect 
        
        # Calculate cooling water flow rate
        Q_loss = 0.054 # System thermal loss
        
            # mass balance
        q_d = self.Capacity / 24 # Hourly distillate production (m3/hr)
        self.q_feed = q_d / self.RR # Feed seawater flow rate (m3/hr)
        q_b = self.q_feed - q_d # Brine flow rate (m3/hr)

        self.s_b = self.Xf /1000/ (1- self.RR) #  brine salinity (g/L)
 
            # BPE calculation
        SW_BPE = BPE(self.T_d, self.s_b)
        
        self.T_b =  self.T_d + SW_BPE # brine temperature
        self.T_cool = self.T_d - 3 # cooling reject temperature (Assume DHTP = 3)
        
            # densities
        rho_b = SW_Density(self.T_b,'c',self.s_b*1000,'ppm',1,'bar')  # brine density
        rho_d = SW_Density(self.T_d,'c',0,'ppm',1,'bar')  # distillate density
        rho_sw= SW_Density(self.Tin,'c',self.Xf,'ppm',1,'bar')  # seawater density
        rho_f = SW_Density(self.T_cool,'c',self.Xf,'ppm',1,'bar')  # cooling reject density
        
            # enthalpies
        h_d = IAPWS97(T=273.15+ self.T_d,x=0).h 
        h_b = SW_Enthalpy(self.T_b, self.s_b)/ 1000
        h_sw = SW_Enthalpy(self.Tin, self.Xf/1000)/ 1000
        h_cool = SW_Enthalpy(self.T_cool, self.Xf/1000)/ 1000
        
            # energy consumption
        self.STEC = 1/self.GOR * (TD_func.enthalpySatVapTW(self.Ts+273.15)-TD_func.enthalpySatLiqTW(self.Ts+273.15))[0] *rho_d/3600
        self.P_req = self.STEC *self.Capacity /24 
        
            # mass flow rates
        self.m_d = q_d * rho_d / 3600 # distillate mass flow rate (kg/s)
        self.m_b = q_b * rho_b / 3600 # brine mass flow rate (kg/s)
        self.m_f = self.q_feed * rho_f / 3600 # feed mass flow rate (kg/s)
        self.m_sw = ((1-Q_loss)*self.P_req - self.m_b * h_b - self.m_d * h_d + h_cool * self.m_f) / (h_cool - h_sw) # intake + cooling water mass flow rate (kg/s)
        
        
            # volume flow rates
        self.q_sw = self.m_sw / rho_sw * 3600 # m3/h
        self.q_cooling = self.q_sw - self.q_feed
              
        
        # self.T_d = self.Tin + 10  
        # self.T_b = self.T_d + 1  
        # self.DTPH = 3
        # self.T_cool = self.T_d - self.DTPH
        # self.h_b = TD_func.enthalpyreg1(self.T_b + 273.15, 1)    # Enthalpy of the flow at brine temperature
        # self.h_sw = TD_func.enthalpyreg1(self.Tin + 273.15, 1)  
        # self.h_d = TD_func.enthalpyreg1(self.T_d + 273.15, 1)
        # self.h_cool = TD_func.enthalpyreg1(self.T_cool + 273.15, 1)
        
        # brine_s = self.Xf / 1000 / (1- self.RR)        
        # self.brine_d = SW_Density(self.T_b,'c',brine_s,'ppt',1,'bar')
        # self.distillate_d = SW_Density(self.T_b,'c',0,'ppm',1,'bar')     
        # self.average_d = self.brine_d * self.RR + self.distillate_d * (1-self.RR)
        
        
        # # Calculate cooling water flow rate
        # self.q_cooling = (0.85 * self.P_req * 3600 - self.brine_d * self.qF * (1- self.RR) * self.h_b - self.distillate_d * self.qF * self.RR * self.h_d + self.qF * self.average_d * self.h_sw ) / (self.h_cool - self.h_sw)
        # # self.q_cooling = ( 0.85 * self.P_req * 3600 - (self.qF * self.average_d * self.h_b - self.qF * self.average_d * self.h_sw)) / (self.h_b - self.h_sw)

        self.design_output = []
#        design_output.append({'Name':'Number of modules required','Value':self.num_modules,'Unit':''})
#        design_output.append({'Name':'Permeate flux of module','Value':self.Mprod,'Unit':'l/h'})
#        design_output.append({'Name':'Condenser outlet temperature','Value':self.TCO,'Unit':'oC'})
#        design_output.append({'Name':'Permeate flow rate','Value': self.F * self.num_modules,'Unit':'l/h'})    
        self.design_output.append({'Name':'Thermal power requirement','Value':self.P_req/1000 ,'Unit':'MW(th)'})
        self.design_output.append({'Name':'Specific thermal power consumption','Value':self.STEC,'Unit':'kWh(th)/m3'})
        self.design_output.append({'Name':'Brine concentration','Value':self.s_b,'Unit':'g/L'})
        self.design_output.append({'Name':'Feedwater flow rate','Value':self.qF,'Unit':'m3/h'})  
        if self.q_cooling > 0:
            self.design_output.append({'Name':'Rejected cooling water flow rate','Value':self.q_cooling ,'Unit':'m3/h'})         
        self.design_output.append({'Name':'The mass flow rate of the steam','Value':self.qs,'Unit':'kg/s'})
        self.design_output.append({'Name':'Specific heat transfer area','Value':self.sA,'Unit':'m2/m3/day'})
        self.design_output.append({'Name':'Gained output ratio','Value':self.GOR,'Unit':'kg permeate/kg steam'})  
        # self.design_output.append({'Name':'Delta T','Value':self.DELTAT,'Unit':'oC'})
        # if self.DELsssssssssTAT < 1.5:
        #     self.design_output.append({'Name':'Warning','Value':'Delta T is too small, resulting in high heat transfer area and associated cost.','Unit':''})
        
        
        
        
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
        simu_output.append({'Name':'Percentage of fossil fuel consumption','Value':sum(fuel)/max(1,sum(energy_consumption))*100,'Unit':'%'})        
        simu_output.append({'Name':'Solar energy curtailment','Value':solar_loss,'Unit':'kWh'})
        simu_output.append({'Name':'Curtailed solar thermal energy','Value':(sum(gen) - sum(load)) / 1000000 ,'Unit':'GWh'})   
        simu_output.append({'Name':'Percentage of curtailed energy','Value':(sum(gen) - sum(load)) / sum(gen) * 100 ,'Unit':'%'})               
        return simu_output
            
#%% MODEL EXECUTION            
# for t in range(15, 85, 5):
#     case = lt_med_general(Xf = 30, RR = 0.5, Tin = t, Capacity = 51000, Ts = 80, Nef = 12)
#     case.design()
#     print("Tin:", t, "STEC: ", case.design_output[1]['Value'], "GOR: ", case.design_output[4]['Value'])
#case.simulation(gen = [5000,6000,5000,3000,2500], storage =6)
            
        
        