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
from DesalinationModels.VAGMD_batch.SW_functions import SW_Density
from iapws import IAPWS97, SeaWater
# from DesalinationModels.LT_MED_calculation import lt_med_calculation

class med_tvc_general(object):

    def __init__(self,
         Xf      =  35 , # Feedwater salinity  (g/L)
         Nef     =  14  , # Number of effects
         Capacity = 2000,    # Capacity of the plant (m3/day)\
         Pm      = 20,  # motive steam pressure entering the thermocompressor (bar)
         Tin     = 15 , # Inlet seawater temperature
         RR      = 0.5 , # recovery ratio
         Fossil_f = 1 # Fossil fuel fraction
         ):
        
        self.Pm = Pm
        self.Nef = Nef
        self.Capacity = Capacity
        self.Fossil_f = Fossil_f
        self.Xf = Xf *1000
        self.RR = RR
        self.Tin  = Tin
    
    def design(self):
        xf = self.Xf
        rr = self.RR
        tin = self.Tin
        qd = self.Capacity
        pm = self.Pm
        qF_paras = [xf, xf**2, rr, rr*xf, rr*xf**2, rr**2, rr**2*xf, tin, tin*xf, tin*xf**2, tin**rr, tin*rr*xf, tin*rr**2, tin**2,
                    tin**2*xf, tin**2*rr, qd, qd*xf, qd*xf**2, qd*rr, qd*rr*xf, qd*rr**2, qd*tin, qd*tin*xf, qd*tin*rr, qd*tin**2, qd**2, qd**2*xf,
                    qd**2*rr, qd**2*tin, pm, pm*xf, pm*xf**2, pm*rr, pm*rr*xf, pm*rr**2, pm*tin, pm*tin*xf, pm*tin*rr, pm*tin**2, pm*qd, pm*qd*xf,
                    pm*qd*rr, pm*qd*tin, pm*qd**2, pm**2, pm**2*xf, pm**2*rr, pm**2*tin, pm**2*qd, 1, pm**3, qd**3, tin**3, rr**3, xf**3]
        
        paras = [xf, rr, rr*xf, tin, tin*xf, tin*rr, qd, qd*xf, qd*rr, qd*tin, pm, pm*xf, pm*rr, pm*tin, pm*qd, 1, pm**2, qd**2, tin**2, rr**2,xf**2]
        if self.Nef == 8:
            coeffs = [
                [-1.42E-06,7.764150858,-1.15E-05,0.582960027,1.24E-07,0.056555556,-2.57E-19,3.63E-25,3.23E-19,3.04E-21,0.104803303,-2.08E-09,0.012249322,-0.000299729,6.28E-22,-5.098563697,-0.001263974,-3.56E-25,-0.005858519,-8.896296296,-1.98E-11],
                [-7.59E-06,-34.3908768,9.69E-06,-0.131363139,1.48E-07,0.200569444,0.002087075,-1.31E-10,-0.000541286,-5.70E-06,-0.109758232,-3.05E-09,0.000630081,0.000228591,-9.38E-08,8.029964774,0.002098453,-2.59E-10,0.000841111,40.08888889,-1.42E-12],
                [1.49E-05,-29.83707466,2.86E-05,-2.345398834,-9.10E-07,0.267902778,0.002171651,4.00E-10,-0.000324519,-2.78E-05,-0.489303064,-7.25E-08,0.033783875,0.006929505,-4.33E-06,43.26022001,0.005568346,-1.65E-10,0.035492222,28.25555556,4.56E-11],
                [3.44E-06,2.566973803,-4.53E-05,-0.124425745,-5.15E-08,5.52E-16,-3.28E-20,7.43E-25,6.21E-20,4.94E-23,3.99E-05,8.13E-10,0.000108401,-1.90E-06,1.32E-22,6.962250661,-7.49E-07,-1.23E-25,-3.70E-06,-3.014814815,-7.42E-11],
                [-0.00256597,-18759.69206,0.006751389,-0.082041658,1.89E-06,-0.268055556,0.240057439,-8.51E-08,-0.336138884,3.40E-06,-6.791460792,3.61E-08,-0.000338753,0.000111789,-6.52E-09,3273.041084,0.138495604,-1.79E-08,0.001416667,26508.05556,1.86E-09],
                [-0.000113631,-13.11517461,0.000106181,-0.494480795,2.52E-06,0.214458333,9.34E-06,2.00E-11,1.72E-06,1.04E-07,-0.045572653,-6.57E-09,-0.000291328,6.29E-05,-7.80E-13,12.94569696,0.000878721,-1.10E-10,0.007633796,6.371296296,3.41E-10],
                ]

            
        if self.Nef == 10:
            coeffs = [
                [-2.28E-06,10.98911472,-1.31E-05,0.689378726,1.47E-07,0.080111111,-2.98E-19,-6.15E-25,4.06E-19,4.44E-21,0.124314705,-1.81E-10,0.018184282,-0.000334959,6.98E-22,-6.475922544,-0.001524489,-5.72E-25,-0.006804444,-12.28888889,-1.68E-11,],
                [1.59E-05,-29.09136792,-2.04E-05,-0.066787419,-7.21E-08,0.145083333,0.001764972,-1.33E-10,-0.000559573,-5.46E-06,0.005482395,-6.00E-08,-0.017926829,8.64E-06,-7.40E-08,5.722781223,5.07E-05,8.14E-12,0.00026963,36.86296296,-6.77E-11,],
                [2.43E-05,-27.0360671,8.10E-06,-1.966013646,-8.70E-07,0.257819444,0.001822688,3.13E-10,-0.000341778,-2.35E-05,-0.349886659,-9.33E-08,0.025067751,0.00570271,-3.59E-06,36.5052648,0.003546979,4.13E-12,0.029556389,25.92222222,7.53E-12,],
                [3.61E-06,2.682529359,-4.76E-05,-0.099299819,-4.93E-08,0.000666667,-3.27E-21,3.07E-25,1.57E-20,-5.31E-23,3.45E-05,9.03E-10,0.000108401,-1.90E-06,2.50E-23,5.43789161,-7.05E-07,-3.29E-26,-9.63E-06,-3.185185185,-7.74E-11,],
                [-0.000990423,-18467.6448,0.004966667,5.003994201,-1.63E-05,-5.769444444,0.237246749,-8.43E-08,-0.33485663,3.92E-06,1.130490409,-4.49E-06,-1.344850949,-0.013448509,2.73E-07,3132.119986,-0.002181241,6.53E-10,-0.0355,26326.66667,-2.46E-09,],
                [-0.000275164,-30.34222168,0.000245662,-0.964861655,5.70E-06,0.49675,-7.92E-07,1.92E-12,5.90E-07,5.40E-09,0.001209732,-2.56E-08,-0.005934959,-1.36E-06,1.14E-09,25.22049669,1.96E-05,3.20E-12,0.013141389,14.14444444,8.80E-10]
                ]
            
        if self.Nef == 12:
            coeffs = [
                [-3.05E-06,14.55682317,-1.30E-05,0.425476523,1.61E-07,0.097638889,6.39E-06,2.07E-13,-2.09E-06,-3.91E-08,0.143261656,6.78E-10,0.027642276,-0.00025,4.65E-08,-2.620877082,-0.001921861,-5.22E-11,-0.001659259,-15.9537037,-1.83E-11,],
                [-4.48E-06,-38.28037765,1.02E-07,-0.413517098,1.86E-07,0.304472222,0.001604017,-1.50E-10,-0.00055003,-6.73E-06,-0.008556022,-3.24E-09,-0.002256098,0.000298408,-9.02E-08,12.82816936,3.81E-05,-3.04E-11,0.005071204,41.34814815,-1.16E-11,],
                [1.12E-05,-32.60635053,1.54E-05,-1.366729008,-6.01E-07,0.362472222,0.001598178,2.60E-10,-0.000344721,-2.04E-05,-0.312617943,-5.56E-08,0.035501355,0.004905556,-3.20E-06,28.5739492,0.003185042,2.08E-11,0.019064444,28.63333333,3.01E-11,],
                [3.36E-06,2.702679242,-4.94E-05,0.009323864,-3.18E-08,0.003726389,-3.25E-06,1.22E-12,1.63E-07,6.35E-08,0.000292748,-1.09E-09,-1.15E-05,-8.66E-05,1.44E-09,3.072728374,4.32E-05,1.46E-11,-0.001488676,-3.314537037,-7.95E-11,],
                [-0.002624415,-18984.93745,0.006843981,0.690965815,2.10E-06,-0.241666667,0.237373559,-8.47E-08,-0.335102104,7.07E-06,0.005182314,-6.78E-09,0.00203252,-0.00053523,5.10E-08,3327.037242,0.000127239,8.54E-11,-0.01225,26691.66667,1.83E-09,],
                [-0.00059378,-70.68831403,0.000537912,-2.002884776,1.10E-05,1.071916667,2.61E-05,-7.91E-11,-8.33E-06,-4.78E-07,-0.020075596,9.86E-08,0.014342818,0.000726897,-3.18E-08,52.69512155,-0.000184651,-6.33E-11,0.024886019,34.90462963,2.02E-09,]
                ]

        if self.Nef == 14:
            coeffs = [
                [-5.77E-06,18.58044758,-9.55E-06,0.758813856,1.78E-07,0.148784722,2.27E-06,-4.93E-13,-3.10E-06,-3.26E-08,0.157319103,4.40E-09,0.033536585,-0.000335027,1.13E-08,-7.631229505,-0.002018089,-1.01E-11,-0.006560185,-21.38310185,-7.92E-12,],
                [-7.83E-07,-40.03225543,-7.58E-06,-0.359841547,1.82E-07,0.30859375,0.00148361,-1.61E-10,-0.000593416,-6.66E-06,-0.001763606,-3.31E-09,0.001147527,0.00014878,-6.89E-08,11.96567201,-5.86E-05,-7.44E-11,0.004328148,45.25318287,-2.16E-11,],
                [1.20E-05,-33.97061713,7.27E-06,-1.345914579,-4.99E-07,0.39046875,0.001457515,2.05E-10,-0.000376928,-1.86E-05,-0.283422499,-4.47E-08,0.04076897,0.004456843,-2.85E-06,28.05931057,0.002831752,2.13E-11,0.018738704,30.55700231,1.65E-11,],
                [2.94E-06,2.616721522,-4.85E-05,-0.077700137,-4.56E-08,0.002335069,-6.71E-06,4.15E-13,2.59E-08,1.38E-07,-0.008647437,-2.48E-09,-0.000322239,0.00018497,1.72E-08,4.058084535,4.57E-05,2.29E-11,-3.88E-05,-3.251880787,-7.84E-11,],
                [-0.002641551,-19938.05077,0.007098958,0.694852634,1.84E-06,-0.484375,0.243049214,-8.68E-08,-0.352814592,6.64E-06,-0.02390267,1.13E-08,-3.27E-13,6.78E-05,-1.07E-08,3408.114255,0.000435147,2.44E-10,-0.011212963,28876.01273,1.93E-09,],
                [-0.00121164,-152.5537433,0.001101146,-3.461298325,2.14E-05,2.249461806,4.67E-05,-1.99E-10,-2.11E-05,-9.28E-07,-0.054534982,3.70E-07,0.068449356,0.001176152,-3.36E-08,97.79031075,-0.000342235,-6.33E-11,0.038331481,78.17853009,4.22E-09,]
                ]
            
            
        if self.Nef == 16:
            coeffs = [
                [-8.38E-06,20.76389007,-3.04E-06,0.967432521,1.85E-07,0.216269841,1.58E-05,-6.41E-13,-2.27E-06,-4.83E-07,0.185976144,2.71E-09,0.046360821,-0.000913957,-4.66E-08,-10.82641732,-0.002230429,-1.06E-11,-0.009318519,-25.09448224,-4.22E-12,],
                [3.35E-06,-38.68477421,-1.90E-05,-0.86243177,2.00E-07,0.233531746,0.00126754,-1.68E-10,-0.000627918,-4.45E-06,-0.077815222,-4.48E-09,-0.046564073,0.001702812,-8.14E-07,20.5725045,0.002389423,5.92E-10,0.012013148,49.04383976,-3.29E-11,],
                [1.33E-05,-33.90192114,-1.17E-06,-1.544393645,-4.29E-07,0.364702381,0.001274023,1.65E-10,-0.000401789,-1.57E-05,-0.282901411,-2.79E-08,0.014909988,0.004355014,-3.09E-06,31.51108079,0.004025387,4.05E-10,0.021729259,33.11413454,8.59E-12,],
                [2.35E-06,2.517164048,-4.92E-05,-0.02903322,-3.63E-08,0.003853175,-1.67E-06,1.11E-12,1.05E-07,6.47E-08,0.001350052,-1.22E-09,-0.000112756,-3.70E-05,1.94E-09,2.74565514,-7.52E-06,6.62E-13,-0.00055637,-3.226379441,-7.85E-11,],
                [-0.002772659,-20962.67876,0.007532407,1.910151843,2.63E-06,-0.097222222,0.238165747,-8.65E-08,-0.356693566,1.45E-06,1.864836524,-4.34E-06,-17.64082462,-0.004363144,-0.000137989,3583.329852,0.287794963,7.47E-08,-0.03125,30836.73469,1.99E-09,],
                [-0.003702813,-566.9002008,0.003490278,-10.24802298,5.87E-05,8.029940476,0.000180849,-1.67E-09,-0.000223884,-5.19E-06,-0.699017368,3.49E-06,0.438254936,0.010243428,-2.60E-06,312.1661769,0.00564047,1.39E-09,0.098896296,317.9402872,1.27E-08,]
                ]
            
        self.GOR = np.dot(paras,coeffs[0])
        self.qs = np.dot(paras,coeffs[1])
        self.qm = np.dot(paras, coeffs[2]) # movive steam mass flow rate entering the thermocompressor (kg/s)
        self.DELTAT = np.dot(paras,coeffs[3]) # the difference between the condensation temperature in the evaporator and the vapor temperature in such effect
        self.qF = np.dot(paras,coeffs[4])
        self.sA = np.dot(paras,coeffs[5])
        self.Ts = 70
        # self.STEC = 1/self.GOR * (TD_func.enthalpySatVapTW(self.Ts+273.15)-TD_func.enthalpySatLiqTW(self.Tin + 10 +273.15))[0] *1000/3600
        

        h_steam = IAPWS97(P=20,x=1).h
        h_cond = IAPWS97(T=273.15+70,x=0).h
        
        self.STEC = 1/self.GOR * (h_steam-h_cond) *1000/3600
        self.P_req = self.STEC *self.Capacity *1000/24/3600       
       
        self.T_b = self.Tin + 10  # Brine temperature at last effect (T_b = T_d = T_cool = T_cond)
        self.h_b = IAPWS97(T=273.15+ self.T_b,x=0).h    # Enthalpy of the flow at brine temperature
        self.h_sw = SeaWater(T=273.15+15,P = 0.101325, S = 0.035).h   
        # print('QMED', self.P_req)
        # print('enthalpy:', self.h_b, self.h_sw)
        
        self.brine_d = SW_Density(self.T_b,'c',0,'ppt',1,'bar')
        self.distillate_d = SW_Density(self.T_b,'c',self.Xf * 2,'ppm',1,'bar')     
        self.average_d = self.brine_d * self.RR + self.distillate_d * (1-self.RR)        
        # self.q_cooling = ( self.P_req * 3600 - (self.qF * self.average_d * self.h_b - self.qF * self.average_d * self.h_sw)) / (self.h_b - self.h_sw)
        self.q_cooling = 0.95 * self.P_req * 3.6   /(self.h_b - self.h_sw)
        print(self.P_req * 3600)
        print((self.h_b - self.h_sw))
        
        from DesalinationModels.LTMED_cost import LTMED_cost
        lcow = LTMED_cost(STEC = self.STEC )
        
        brine_s = self.Xf /1000 / ( 1- self.RR)
        
        self.design_output = []
#        design_output.append({'Name':'Number of modules required','Value':self.num_modules,'Unit':''})
#        design_output.append({'Name':'Permeate flux of module','Value':self.Mprod,'Unit':'l/h'})
#        design_output.append({'Name':'Condenser outlet temperature','Value':self.TCO,'Unit':'oC'})
#        design_output.append({'Name':'Permeate flow rate','Value': self.F * self.num_modules,'Unit':'l/h'})    
        self.design_output.append({'Name':'Thermal power requirement','Value':self.P_req / 1000 ,'Unit':'MW(th)'})
        self.design_output.append({'Name':'Specific thermal power consumption','Value':self.STEC,'Unit':'kWh(th)/m3'})
        self.design_output.append({'Name':'Brine concentration','Value':brine_s,'Unit':'g/L'})
        self.design_output.append({'Name':'Feedwater flow rate','Value':self.qF,'Unit':'m3/h'})
        # if self.q_cooling > 0:
            # self.design_output.append({'Name':'Cooling water flow rate','Value':self.q_cooling,'Unit':'m3/h'}) 
        self.design_output.append({'Name':'Heating steam mass flow rate entering the first effect','Value':self.qs,'Unit':'kg/s'})
        self.design_output.append({'Name':'Motive steam mass flow rate entering the thermocompressor','Value':self.qm,'Unit':'kg/s'})
        self.design_output.append({'Name':'Specific area','Value':self.sA,'Unit':'m2 per m3/day'})
        self.design_output.append({'Name':'Gained output ratio','Value':self.GOR,'Unit':'kg permeate/kg steam'})  
        self.design_output.append({'Name':'Mean temperature difference between effects','Value':self.DELTAT,'Unit':'oC'})
        if self.DELTAT < 1.5:
            self.design_output.append({'Name':'Warning','Value':'Delta T is too small, resulting in high heat transfer area and associated cost.','Unit':''})
        
        
        
        
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
    
# for t in range(25, 40, 5):
#     case = med_tvc_general(Xf = 30, RR = 0.3, Tin = t, Capacity = 51000,  Nef = 12)
#     case.design()
#     print("Tin:", t, "STEC: ", case.design_output[1]['Value'], "GOR: ", case.design_output[5]['Value'])
#case.simulation(gen = [5000,6000,5000,3000,2500], storage =6)
            
        
        