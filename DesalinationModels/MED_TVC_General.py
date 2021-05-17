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
                [-1.40E-05,-1.785127142,1.65E-05,-0.086087998,2.85E-07,0.027513889,1.92E-06,3.26E-12,2.86E-07,9.24E-09,-0.011468447,-5.61E-09,-3.73E-05,6.36E-05,-6.21E-12,2.315966265,0.000180162,-1.92E-11,0.001250185,0.912962963,5.25E-11],
                ]

            
        if self.Nef == 10:
            coeffs = [
                [-2.28E-06,10.98911472,-1.31E-05,0.689378726,1.47E-07,0.080111111,-2.98E-19,-6.15E-25,4.06E-19,4.44E-21,0.124314705,-1.81E-10,0.018184282,-0.000334959,6.98E-22,-6.475922544,-0.001524489,-5.72E-25,-0.006804444,-12.28888889,-1.68E-11,],
                [1.59E-05,-29.09136792,-2.04E-05,-0.066787419,-7.21E-08,0.145083333,0.001764972,-1.33E-10,-0.000559573,-5.46E-06,0.005482395,-6.00E-08,-0.017926829,8.64E-06,-7.40E-08,5.722781223,5.07E-05,8.14E-12,0.00026963,36.86296296,-6.77E-11,],
                [2.43E-05,-27.0360671,8.10E-06,-1.966013646,-8.70E-07,0.257819444,0.001822688,3.13E-10,-0.000341778,-2.35E-05,-0.349886659,-9.33E-08,0.025067751,0.00570271,-3.59E-06,36.5052648,0.003546979,4.13E-12,0.029556389,25.92222222,7.53E-12,],
                [3.61E-06,2.682529359,-4.76E-05,-0.099299819,-4.93E-08,0.000666667,-3.27E-21,3.07E-25,1.57E-20,-5.31E-23,3.45E-05,9.03E-10,0.000108401,-1.90E-06,2.50E-23,5.43789161,-7.05E-07,-3.29E-26,-9.63E-06,-3.185185185,-7.74E-11,],
                [-0.000990423,-18467.6448,0.004966667,5.003994201,-1.63E-05,-5.769444444,0.237246749,-8.43E-08,-0.33485663,3.92E-06,1.130490409,-4.49E-06,-1.344850949,-0.013448509,2.73E-07,3132.119986,-0.002181241,6.53E-10,-0.0355,26326.66667,-2.46E-09,],
                [-2.72E-05,-3.117132674,2.71E-05,-0.117750379,5.41E-07,0.050611111,-8.94E-08,2.40E-13,6.63E-08,5.71E-10,-0.002920717,-6.90E-09,-0.000762195,4.66E-05,1.42E-10,3.113358038,2.54E-05,3.63E-13,0.00157037,1.459259259,9.65E-11,]
                ]
            
        if self.Nef == 12:
            coeffs = [
                [-3.05E-06,14.55682317,-1.30E-05,0.425476523,1.61E-07,0.097638889,6.39E-06,2.07E-13,-2.09E-06,-3.91E-08,0.143261656,6.78E-10,0.027642276,-0.00025,4.65E-08,-2.620877082,-0.001921861,-5.22E-11,-0.001659259,-15.9537037,-1.83E-11,],
                [-4.48E-06,-38.28037765,1.02E-07,-0.413517098,1.86E-07,0.304472222,0.001604017,-1.50E-10,-0.00055003,-6.73E-06,-0.008556022,-3.24E-09,-0.002256098,0.000298408,-9.02E-08,12.82816936,3.81E-05,-3.04E-11,0.005071204,41.34814815,-1.16E-11,],
                [1.12E-05,-32.60635053,1.54E-05,-1.366729008,-6.01E-07,0.362472222,0.001598178,2.60E-10,-0.000344721,-2.04E-05,-0.312617943,-5.56E-08,0.035501355,0.004905556,-3.20E-06,28.5739492,0.003185042,2.08E-11,0.019064444,28.63333333,3.01E-11,],
                [3.36E-06,2.702679242,-4.94E-05,0.009323864,-3.18E-08,0.003726389,-3.25E-06,1.22E-12,1.63E-07,6.35E-08,0.000292748,-1.09E-09,-1.15E-05,-8.66E-05,1.44E-09,3.072728374,4.32E-05,1.46E-11,-0.001488676,-3.314537037,-7.95E-11,],
                [-0.002624415,-18984.93745,0.006843981,0.690965815,2.10E-06,-0.241666667,0.237373559,-8.47E-08,-0.335102104,7.07E-06,0.005182314,-6.78E-09,0.00203252,-0.00053523,5.10E-08,3327.037242,0.000127239,8.54E-11,-0.01225,26691.66667,1.83E-09,],
                [-5.11E-05,-6.149003438,4.83E-05,-0.139275285,9.41E-07,0.092694444,2.56E-07,-2.33E-12,-5.21E-07,3.29E-09,-0.003791651,-3.11E-09,0.000904472,3.33E-05,5.65E-09,4.278549654,2.77E-05,-4.61E-13,0.001539352,3.043518519,1.81E-10,]
                ]

        if self.Nef == 14:
            coeffs = [
                [-5.77E-06,18.58044758,-9.55E-06,0.758813856,1.78E-07,0.148784722,2.27E-06,-4.93E-13,-3.10E-06,-3.26E-08,0.157319103,4.40E-09,0.033536585,-0.000335027,1.13E-08,-7.631229505,-0.002018089,-1.01E-11,-0.006560185,-21.38310185,-7.92E-12,],
                [-7.83E-07,-40.03225543,-7.58E-06,-0.359841547,1.82E-07,0.30859375,0.00148361,-1.61E-10,-0.000593416,-6.66E-06,-0.001763606,-3.31E-09,0.001147527,0.00014878,-6.89E-08,11.96567201,-5.86E-05,-7.44E-11,0.004328148,45.25318287,-2.16E-11,],
                [1.20E-05,-33.97061713,7.27E-06,-1.345914579,-4.99E-07,0.39046875,0.001457515,2.05E-10,-0.000376928,-1.86E-05,-0.283422499,-4.47E-08,0.04076897,0.004456843,-2.85E-06,28.05931057,0.002831752,2.13E-11,0.018738704,30.55700231,1.65E-11,],
                [2.94E-06,2.616721522,-4.85E-05,-0.077700137,-4.56E-08,0.002335069,-6.71E-06,4.15E-13,2.59E-08,1.38E-07,-0.008647437,-2.48E-09,-0.000322239,0.00018497,1.72E-08,4.058084535,4.57E-05,2.29E-11,-3.88E-05,-3.251880787,-7.84E-11,],
                [-0.002641551,-19938.05077,0.007098958,0.694852634,1.84E-06,-0.484375,0.243049214,-8.68E-08,-0.352814592,6.64E-06,-0.02390267,1.13E-08,-3.27E-13,6.78E-05,-1.07E-08,3408.114255,0.000435147,2.44E-10,-0.011212963,28876.01273,1.93E-09,],
                [-8.74E-05,-11.07665413,8.11E-05,-0.236638811,1.53E-06,0.163402778,1.33E-06,-1.01E-11,-1.39E-06,-1.90E-08,-0.006881133,2.25E-08,0.004924627,0.000116565,-3.65E-09,7.091650789,7.55E-06,2.59E-12,0.002463056,5.668402778,3.11E-10,]
                ]
            
            
        if self.Nef == 16:
            coeffs = [
                [-8.38E-06,20.76389007,-3.04E-06,0.967432521,1.85E-07,0.216269841,1.58E-05,-6.41E-13,-2.27E-06,-4.83E-07,0.185976144,2.71E-09,0.046360821,-0.000913957,-4.66E-08,-10.82641732,-0.002230429,-1.06E-11,-0.009318519,-25.09448224,-4.22E-12,],
                [3.35E-06,-38.68477421,-1.90E-05,-0.86243177,2.00E-07,0.233531746,0.00126754,-1.68E-10,-0.000627918,-4.45E-06,-0.077815222,-4.48E-09,-0.046564073,0.001702812,-8.14E-07,20.5725045,0.002389423,5.92E-10,0.012013148,49.04383976,-3.29E-11,],
                [1.33E-05,-33.90192114,-1.17E-06,-1.544393645,-4.29E-07,0.364702381,0.001274023,1.65E-10,-0.000401789,-1.57E-05,-0.282901411,-2.79E-08,0.014909988,0.004355014,-3.09E-06,31.51108079,0.004025387,4.05E-10,0.021729259,33.11413454,8.59E-12,],
                [2.35E-06,2.517164048,-4.92E-05,-0.02903322,-3.63E-08,0.003853175,-1.67E-06,1.11E-12,1.05E-07,6.47E-08,0.001350052,-1.22E-09,-0.000112756,-3.70E-05,1.94E-09,2.74565514,-7.52E-06,6.62E-13,-0.00055637,-3.226379441,-7.85E-11,],
                [-0.002772659,-20962.67876,0.007532407,1.910151843,2.63E-06,-0.097222222,0.238165747,-8.65E-08,-0.356693566,1.45E-06,1.864836524,-4.34E-06,-17.64082462,-0.004363144,-0.000137989,3583.329852,0.287794963,7.47E-08,-0.03125,30836.73469,1.99E-09,],
                [-0.000231584,-35.58704252,0.000220126,-0.61721372,3.66E-06,0.504761905,9.88E-06,-1.03E-10,-1.41E-05,-3.01E-07,-0.044436295,2.17E-07,0.028039102,0.000582419,-1.89E-07,19.37394183,0.000416997,9.97E-11,0.005732222,19.92063492,8.00E-10,]
                ]
            
        self.GOR = np.dot(paras,coeffs[0])
        self.qs = np.dot(paras,coeffs[1])
        self.qm = np.dot(paras, coeffs[2]) # movive steam mass flow rate entering the thermocompressor (kg/s)
        self.DELTAT = np.dot(paras,coeffs[3]) # the difference between the condensation temperature in the evaporator and the vapor temperature in such effect
        self.qF = np.dot(paras,coeffs[4])
        self.sA = np.dot(paras,coeffs[5])
        self.Ts = 70
        self.STEC = 1/self.GOR * (TD_func.enthalpySatVapTW(self.Ts+273.15)-TD_func.enthalpySatLiqTW(self.Ts+273.15))[0] *1000/3600
        self.P_req = 1/self.GOR * (TD_func.enthalpySatVapTW(self.Ts+273.15)-TD_func.enthalpySatLiqTW(self.Ts+273.15))[0] *self.Capacity *1000/24/3600
        
        # self.system = lt_med_calculation(Nef = self.Nef, Ts = self.Ts, Ms = self.qs, Mf = self.qF, Tcwin = self.Tin)
        # self.system.model_execution() 
        # print('calculated STEC:', system.STE)
        # print('calculated GOR:', system.GOR)
        # print('calculated production:', system.Mprod_m3_day)
        
        from DesalinationModels.LTMED_cost import LTMED_cost
        lcow = LTMED_cost(STEC = self.STEC )
        
        self.design_output = []
#        design_output.append({'Name':'Number of modules required','Value':self.num_modules,'Unit':''})
#        design_output.append({'Name':'Permeate flux of module','Value':self.Mprod,'Unit':'l/h'})
#        design_output.append({'Name':'Condenser outlet temperature','Value':self.TCO,'Unit':'oC'})
#        design_output.append({'Name':'Permeate flow rate','Value': self.F * self.num_modules,'Unit':'l/h'})    
        self.design_output.append({'Name':'Thermal power consumption','Value':self.P_req / 1000,'Unit':'MW(th)'})
        self.design_output.append({'Name':'Specific thermal power consumption','Value':self.STEC,'Unit':'kWh(th)/m3'})
        self.design_output.append({'Name':'Feedwater flow rate','Value':self.qF,'Unit':'m3/h'})
        self.design_output.append({'Name':'Heating steam mass flow rate entering the first effect','Value':self.qs,'Unit':'kg/s'})
        self.design_output.append({'Name':'Movive steam mass flow rate entering the thermocompressor','Value':self.qm,'Unit':'kg/s'})
        self.design_output.append({'Name':'Specific area','Value':self.sA,'Unit':'m2 per m3/day'})
        self.design_output.append({'Name':'Gained output ratio','Value':self.GOR,'Unit':''})  
        self.design_output.append({'Name':'Mean temperature difference between effects','Value':self.DELTAT,'Unit':'oC'})
        if self.DELTAT < 2:
            self.design_output.append({'Name':'Warning','Value':'Delta T is too small, the cost might be high','Unit':''})
        
        
        
        
        # self.design_output.append({'Name':'Specific heat exchanger area','Value':self.system.sA,'Unit':'m2/(kg/s)'}) 
        
        return self.design_output
    
    # class variables
#    DELTAT_loss = 0.05
#

#    def __init__(self,
#                 Tb1      = 76     , # The brine temperature in the first effect, ºC
#                 FeedC_r  = 35  , # The feed water salinity, ppm
#                 Ms       = 1.023  , # The mass flow rate of the steam entering the bundle tube of the first effect, kg/s
#                 Ts       = 80     , # The temperature of the steam at the inlet of the first bundle tube, ºC
#                 Tcwin    = 25     , # Seawater inlet temperature in the condenser, ºC
#                 DELTATcw = 7.3    , # The temperature difference between the inlet and outlet seawater temperature in the condenser, ºC
#                 Mf       = 38.27  , # Feed water mass flow rate sprayed on the bundle tube, kg/s
#                 Nef      = 16     , # Number of effects
#                 Nph      = 15     , # Number of preheaters
#                 Cp       = 4.18   , # Specific heat of distillate, feed and brine, that is considered. [J/(kg C)]
#                 BPE      = 0.5    , # The Boiling Point Elevation, ºC
#                 NEA      = 0.5    , # The Non Equilibrium Allowance, ºC
#                 Tol      = 0.0001 , # The tolarance applied to get equal area in the effects)
#                 Capacity = 971.96,    # Capacity of the plant (m3/day)
#                 storage_hour = 6, # Thermal storage hour (hr)
#                 Fossil_f = 1 # Fossil fuel fraction
#                 ):
#        
#        self.Tb1 = Tb1 
#        self.FeedC_r = FeedC_r *1000
#        self.Ms = Ms
#        self.Ts = Ts 
#        self.Tcwin = Tcwin 
#        self.DELTATcw = DELTATcw 
#        self.Mf = Mf
#        self.Nef = Nef
#        self.Nph = Nph
#        self.Cp = Cp
#        self.BPE = np.zeros(self.Nef)
#        self.NEA = np.zeros(self.Nef)
#        self.Tol = Tol
#        
#        # ASSUMPTIONS. They keep constant during the calculations
#        self.Tb = np.zeros(Nef) 
#        self.Tv = np.zeros(Nef)
#        self.DTb = np.zeros(Nef)
#        self.Tdb = np.zeros(Nef)
#        self.Tph = np.zeros(Nef)
#        
#        self.Tb[0] = self.Tb1 # The brine temperature in the first effect, ºC
#        self.Tb_last = 37  # Brine temperature in the last effect, ºC
#        self.Tv[0] = self.Tb1 - BPE - self.DELTAT_loss # The vapor temperature inside the first effect, ºC
#        self.Tf    = self.Tb1 -3 # The feed water temperature sprayed in the first effect, ºC
#        self.Tcwout= self.Tcwin + self.DELTATcw  # The seawater outlet temperature of the condenser, ºC
#        self.Tph[0] = self.Tf
#        self.Length_ef = 0.5 # Length of the tubes in the effects tube bundle, m
#        self.Length_ph = 0.75 * self.Length_ef # Lenghth of the tubes in the preheaters tube bundle, m
#        self.Length_c  = 1.5  * self.Length_ef # Length of the tubes in the condenser tube bundle, m
#        self.Di = 0.0254 # Inner diameter of the tubes in the bundle tubes, m
#        self.BPE[0] = BPE
#        self.NEA[0] = NEA
#
#        for i in range(self.Nef-1):
#            # Calculate the vapor temperature in each effect, ºC
#            self.BPE[i+1] = BPE
#            self.NEA[i+1] = NEA
#            self.Tb[i+1] = self.Tb[i] - (self.Tb[0]-self.Tb_last) / (self.Nef -1)
#            # Calculate the temperature of the brine after flashing process from effects 2 to Nef, Tdb(2,1), ºC
#            self.Tv[i+1] = self.Tb[i+1] - self.BPE[i+1] - self.DELTAT_loss
#            self.DTb[i+1] = self.Tb[i] - self.Tb[i+1]
#            self.Tdb[i+1] = self.Tv[i+1] - self.NEA[i]
#            # Calculate the seawater temperature in the preheater, Tph(i,1), ºC
#            self.Tph[i+1] = self.Tph[i] - (self.Tph[0] - self.Tcwout) / self.Nph
#
#    # PREHEATER calculations
#        # Calculations in the prehater:
##        % Calculate the seawater temperature in the preheater, Tph(i,1), ºC
##        % Calculate the feed water mass flow rate sprayed on the bundle tube, Mf, kg/s
##        % Calculate the vapor consumed in each preheater, Mvh(i,1), kg/s
##        % Calculate the heat transfer rate in the preheaters, Qph(i,1), kJ/s
##        % Calculate the overall heat transfer coefficient of the preheaters, Uph(i,1), kW/m2ºC. Correlation of El-Dessouky
##        % Calculate the condensate generated in the preheater,Mdh(i,1), kg/s
##        % Calculate the heat transfer area of the preheaters, Aph(i,1), m2
##        % Evh(i,1) is the enthalpy of the vapor that enters the preheater, kJ/kg
##        % Elh(i,1) is the enthalpy of the condensate that leaves the preheater, kJ/kg
##        % Lvh(i,1) is the latent heat of the vapor in the preheater, kJ/kg
##        % LTMDph (i,1)is the log mean temperature difference, ºC 
#    def design(self):
#        
#        self.Evh = np.zeros(self.Nph)
#        self.Elh = np.zeros(self.Nph)
#        self.Lvh = np.zeros(self.Nph)
#        self.Mvh = np.zeros(self.Nph)
#        self.Mdh = np.zeros(self.Nph)
#        self.Qph = np.zeros(self.Nph)
#        self.Uph = np.zeros(self.Nph)
#        self.LTMDph = np.zeros(self.Nph)
#        self.Aph = np.zeros(self.Nph)
#        
#        for i in range(self.Nph):
#            self.Evh[i] = TD_func.enthalpySatVapTW(self.Tv[i]+273.15) 
#            self.Elh[i] = TD_func.enthalpySatLiqTW(self.Tv[i]+273.15) 
#            self.Lvh[i] = self.Evh[i] -self.Elh[i] 
#            self.Mvh[i] = self.Mf * self.Cp * (self.Tph[i] - self.Tph[i+1]) / self.Lvh[i] 
#            self.Mdh[i] = self.Mvh[i] 
#            self.Qph[i] = self.Mf * self.Cp * (self.Tph[i] - self.Tph[i+1]) 
#            self.Uph[i] = 1.7194 + (3.2063e-3 * self.Tv[i]) + (1.5971e-5 * self.Tv[i]**2) - (1.9918e-7 * self.Tv[i]**3) 
#            self.LTMDph[i] = ((self.Tv[i] - self.Tph[i+1]) - (self.Tv[i] - self.Tph[i])) / math.log( (self.Tv[i] - self.Tph[i+1]) / (self.Tv[i] - self.Tph[i]) ) 
#            self.Aph[i] = self.Qph[i] / self.Uph[i] / self.LTMDph[i] 
#        
#    # FIRST EFFECT & OTHER EFFECTS calculations
##        % Definition of the variables used and calculated:
##
##        % Aef(i,1) is the heat transfer area of the bundle tube of each effect, m2
##        % Mgb(i,1) is the mass flow rate of the vapor generated by boiling, kg/s
##        % Mdf(i,1) is the mass flow rate of the vaspor generated by flash of the distillate in the
##        % flash box, kg/s
##        % Mgt(i,1) is the sum of the mass flow rate of total vapor leaving each
##        % effect plus vapor generated by flash in the flash box, kg/s
##        % Mv(i,1) is the vapor mass flow rate entering the bundle tube of each effect, kg/s
##        % Egv(i,1) is the enthalpy of the vapor entering the bundle tube of each effect, kJ/kg
##        % Egl(i,1) is the enthalpy of the condensate leaving the bundle tube of each effect, kJ/kg
##        % Lv(i,1) is the latent heat of the vapor entering the bundle tube of each effect, kJ/kg
##        % Lgf(i,1) is the latent heat of the vapor generated by flashing of the brine in each effect, kJ/kg
##        % Lgb(i,1) is the latent heat of the vapor generated by boiling of the brine in each effect, kJ/kg
##        % Mgf(i,1) is the mass flow rate of the vapor generated by flashing of the brine in each effect, kg/s
##        % Mfv(i,1) is the mass flow rate of the vapor generated in each effect (by boiling and flashing), kg/s
##        % Mdb(i,1) is the mass flow rate of the brine after flashing, kg/s
##        % Xdb is the salinity of the brine after flashing, ppm
##        % Md(i,1) is the distillate mass flow rate leaving each flash box, kg/s
##        % Mdaf(i,1) is the distillate mass flow rate leaving each effect, kg/s
##        % Uef(i,1) is the overall heat transfer coefficient of each effect, kW/m2ºC
##        % Mb(i,1) is the mass flow rate of the brine that leaves each effect mass flow rate, kg/s
##        % Xb(i,1) is the salinity of the brine leaving each effect, ppm 
#        
#        self.Egs = TD_func.enthalpySatVapTW(self.Ts+273.15) 
#        self.Els = TD_func.enthalpySatLiqTW(self.Ts+273.15) 
#        self.Ls = self.Egs - self.Els
#        self.Qs = self.Ms * self.Ls
#        self.Qef = np.zeros(self.Nef)
#        self.Qef[0] = self.Qs
#        self.max_DA = 20
#        self.Egbg = np.zeros(self.Nef)
#        self.Egbl = np.zeros(self.Nef)
#        self.Lgb  = np.zeros(self.Nef)
#        self.Uef  = np.zeros(self.Nef)
#        self.Mgb  = np.zeros(self.Nef)
#        self.Aef  = np.zeros(self.Nef)
#        self.Lv   = np.zeros(self.Nef)
#        self.Mgf  = np.zeros(self.Nef)
#        self.Mdf  = np.zeros(self.Nef)
#        self.Md   = np.zeros(self.Nef)
#        self.Mdb  = np.zeros(self.Nef)
##        self.DTb  = np.zeros(self.Nef)
#        self.Mfv  = np.zeros(self.Nef)
#        self.Mgt  = np.zeros(self.Nef)
#        self.Mb   = np.zeros(self.Nef)
#        self.Xb   = np.zeros(self.Nef)
#        
#        self.Mv   = np.zeros(self.Nef)
#        self.Mdaf = np.zeros(self.Nef)
#        self.Egv  = np.zeros(self.Nef)
#        self.Egl  = np.zeros(self.Nef)
#        self.Lgf  = np.zeros(self.Nef)
#        self.Lgb  = np.zeros(self.Nef)
#        self.Xdb  = np.zeros(self.Nef)
#        self.Uef  = np.zeros(self.Nef)
#        self.Ldf  = np.zeros(self.Nef)
#        self.Xb_w = np.zeros(self.Nef)
#        self.A    = np.zeros(self.Nef)
#        self.B    = np.zeros(self.Nef)
#        self.C    = np.zeros(self.Nef)
#        self.DA   = np.zeros(self.Nef)
#        
#        self.Mgf[0] = 0
#        self.Mdf[0] = 0
#        self.Md[0]  = 0
#        self.Mdb[0] = 0
#        self.DTb[0] = self.Ts - self.Tb[0]
#        self.count = 0
#        
#        while self.max_DA > self.Tol:
#            # Set up for the first effect
#            self.Egbg[0] = TD_func.enthalpySatVapTW(self.Tv[0]+273.15)
#            self.Egbl[0] = TD_func.enthalpySatLiqTW(self.Tv[0]+273.15)
#            self.Lgb[0]  = self.Egbg[0] - self.Egbl[0]
#            self.Uef[0]  = 1.9695 + (1.2057e-2  * self.Tb[0]) - (8.5989e-5 * self.Tb[0]**2) + (2.5651e-7 * self.Tb[0]**3)
#            self.Mgb[0]  = (self.Qef[0] - self.Mf * self.Cp * (self.Tb[0] - self.Tf)) / self.Lgb[0]
#            self.Aef[0]  = self.Qef[0] / (self.Uef[0] * (self.Ts - self.Tb[0]))
#            self.Lv[0]   = self.Lgb[0]
#            self.Mfv[0]  = (self.Mgb[0] + self.Mgf[0]) * 3600
#            self.Mgt[0]  = (self.Mgb[0] + self.Mgf[0] + self.Mdf[0])
#            self.Mb[0]   = self.Mf - self.Mgb[0]
#            self.Xb[0]   = self.FeedC_r * self.Mf / self.Mb[0]
#            
#            self.Sum_A = self.Aef[0]
#            
#            # Other effects calculations
#            
#            for i in range(1, self.Nef):
#                self.Mv[i]   = self.Mgt[i-1] - self.Mvh[i-1]
#                self.Mdaf[i] = self.Mv[i]
#                self.Egv[i]  = TD_func.enthalpySatVapTW(self.Tv[i]+273.15)
#                self.Egl[i]  = TD_func.enthalpySatLiqTW(self.Tv[i]+273.15)
#                self.Lv[i]   = self.Egv[i] - self.Egl[i]
#                self.Lgf[i]  = self.Lv[i]
#                self.Lgb[i]  = self.Lv[i]
#                self.Mgf[i]  = self.Mb[i-1] * self.Cp *(self.Tb[i-1] - self.Tdb[i]) / self.Lgf[i]
#                self.Mdb[i]  = self.Mb[i-1] - self.Mgf[i]
#                self.Xdb[i]  = self.Xb[i-1] * self.Mb[i-1] / self.Mdb[i]
#                self.Mgb[i]  = (self.Mv[i] * self.Lv[i-1] + self.Mdb[i] *self.Cp * (self.Tdb[i] - self.Tb[i])) / self.Lgb[i]
#                self.Mfv[i]  = (self.Mgb[i] + self.Mgf[i]) *3600
#                self.Qef[i]  = self.Mv[i] * self.Lv[i-1]
#                self.Uef[i]  = 1.9695 + (1.2057e-2 * self.Tb[i]) - (8.5989e-5 * self.Tb[i]**2) + (2.5651e-7 * self.Tb[i]**3)
#                self.Mb[i]   = self.Mdb[i] - self.Mgb[i]
#                self.Xb[i]   = self.Mdb[i] * self.Xdb[i] / self.Mb[i]
#                self.Ldf[i]  = self.Lv[i]
#                self.Mdf[i]  = (self.Mdh[i-1] * self.Cp * (self.Tv[i-1] - self.Tv[i]) + (self.Mdaf[i-1] * self.Cp * (self.Tv[i-1] - self.Tv[i])) + self.Md[i-1] * self.Cp * (self.Tv[i-1] - self.Tv[i]) ) / self.Ldf[i]
#                self.Mgt[i]  = self.Mgb[i] + self.Mgf[i] + self.Mdf[i] 
#                self.Md[i]   = self.Mdaf[i] + self.Mdh[i-1] + self.Md[i-1] - self.Mdf[i]
#                self.Aef[i]  = self.Qef[i] / self.Uef[i] / (self.Tv[i-1] - self.Tb[i])
#                
#                self.Sum_A += self.Aef[i]
#                
#            self.Am = self.Sum_A / self.Nef
#            self.DTb[0] *= (self.Aef[0] / self.Am)
#            self.Tb[0]   = self.Ts - self.DTb[0] 
#            self.Xb_w[0] = self.Xb[0] / (1000*1000) *100 # Salinity in weigth percentage
#            self.A[0]    = 8.325e-2 + (1.883e-4 * self.Tb[0]) + (4.02e-6 * self.Tb[0]**2)
#            self.B[0]    = -7.625e-4 + (9.02e-5 * self.Tb[0]) - (5.2e-7 * self.Tb[0]**2)
#            self.C[0]    = 1.552e-4- (3e-6 * self.Tb[0]) - (3e-8 * self.Tb[0]**2)
#            self.BPE[0]  = self.A[0] * self.Xb_w[0] + self.B[0] * self.Xb_w[0]**2 + self.C[0] * self.Xb_w[0]**3
#            self.Tv[0]   = self.Tb[0] - self.BPE[0] - self.DELTAT_loss
#            self.Uef[0]  = 1.9695 + (1.2057e-2  * self.Tb[0]) - (8.5989e-5 * self.Tb[0]**2) + (2.5651e-7 * self.Tb[0]**3)
#            
#            for i in range(1, self.Nef):
#                self.DTb[i] *= self.Aef[i] / self.Am
#                self.Tb[i]  = self.Tb[i-1] -self.DTb[i]
#                self.Xb_w[i] = self.Xb[i] / (1000*1000) *100
#                self.A[i]    = 8.325e-2 + (1.883e-4 * self.Tb[i]) + (4.02e-6 * self.Tb[i]**2)
#                self.B[i]    = -7.625e-4 + (9.02e-5 * self.Tb[i]) - (5.2e-7 * self.Tb[i]**2)
#                self.C[i]    = 1.552e-4- (3e-6 * self.Tb[i]) - (3e-8 * self.Tb[i]**2)
#                self.BPE[i]  = self.A[i] * self.Xb_w[i] + self.B[i] * self.Xb_w[i]**2 + self.C[i] * self.Xb_w[i]**3
#                self.NEA[i]  = 33 * self.DTb[i]**0.55 / self.Tv[i]
#                self.Tv[i]   = self.Tb[i] - self.BPE[i] - self.DELTAT_loss
#                self.Tdb[i]  = self.Tv[i] - self.NEA[i]
#                self.DA[i]   = abs(self.Aef[i-1] - self.Aef[i])
#            
#            self.count += 1
#            self.max_DA = max(self.DA)
#        
#        self.Nt_ef = np.zeros(self.Nef)
#        for i in range(self.Nef):
#            self.Nt_ef[i] = self.Aef[i] / (math.pi * self.Length_ef *self.Di)
#            
#    # CONDENSER calculations
##        % CONDENSER
##        % Calculate the vapor entering the condenser, Mgt, kg/s
##        % Calculate the seawater flow rate flowing through the condenser, Mcw, kg/s
##        % Calculate the distillate produced in the condenser, Mdc, kg/s
##        % Calculate the heat transfer rate in the condenser, Qc, kW
##        % Calculate the heat transfer area of the condenser, Ac, m2 
#
#        self.Mgt[self.Nef-1] = (self.Mgb[self.Nef-1] + self.Mgf[self.Nef-1] + self.Mdf[self.Nef-1]) / 0.99
#        self.Lgt = self.Lv[self.Nef-1]
#        self.Qc  = self.Mgt[self.Nef-1] * self.Lgt
#        self.Mcw = self.Qc / self.Cp / (self.Tcwout - self.Tcwin)
#        self.Mdc = self.Mgt[self.Nef-1]
#        self.LTMDc = ((self.Tv[self.Nef-1] - self.Tcwin) - (self.Tv[self.Nef-1] - self.Tcwout)) / math.log( (self.Tv[self.Nef-1] - self.Tcwin) / (self.Tv[self.Nef-1] - self.Tcwout) ) 
#        self.Uc  = 1.7194 + (3.2063e-3 * self.Tv[self.Nef-1]) + (1.5971e-5 * self.Tv[self.Nef-1]**2) - (1.9918e-7 * self.Tv[self.Nef-1]**3) 
#        self.Ac  = self.Qc / self.Uc / self.LTMDc
#        self.Nt_c= self.Ac / (math.pi * self.Length_c * self.Di)
#    
#    # MIXTURE OF DISTILLATES  
#
##% Calculate the final production, Mprod
##% Calculate the temperature of the distillate production, Tprod, ºC
#        self.Tvc = self.Tv[self.Nef-1] - self.DELTAT_loss
#        self.Mprod = self.Md[self.Nef-1] + self.Mdc  #kg/s
#        self.Tprod = (self.Md[self.Nef-1] * self.Tv[self.Nef-1] + self.Mdc * self.Tvc) / self.Mprod
#        
#        self.DELTAT_final = np.zeros(self.Nef-1)
#        for i in range(self.Nef-1):
#            self.DELTAT_final[i] = self.Tb[i] -self.Tb[i+1]
#        
#        self.STE = self.Qef[0] / self.Mprod / 3.6
#        self.GOR = self.Mprod / self.Ms
#        self.Mprod_m3_day = self.Mprod * 24 * 3.6  # m3/day
#        self.RR = self.Mprod / self.Mf
#        
##    % MIXER (mixture of brine, distillate product and rejected seawater)
##    % Calculate the temperature after the mixer, Tmix, ºC
##    % Mrej is the flow rate of the rejected seawater from the condenser, kg/s
#        self.Mr = self.Mcw - self.Mf
#        self.Tm = (self.Mb[self.Nef-1] * self.Tb[self.Nef-1] + self.Mprod * self.Tprod + self.Mr * self.Tcwout) / self.Mcw
#        self.Mbf = self.Mb[self.Nef-1] + self.Mr
#        self.Xbf = self.Xb[self.Nef-1] * self.Mb[self.Nef-1] / self.Mbf
#        
#       # % Specific heat transfer area, m2/m3/d
#        self.sum_A = sum(self.Aef)
#        self.sum_Aph = sum(self.Aph)
#        self.sA = (self.sum_A + self.sum_Aph + self.Ac) / self.Mprod
#       
#                
#        self.ThPower = self.STE * self.Mprod * 3.6  # (kW)
#        self.F = self.Mprod * 3.6 
        
        

    
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
    
# for t in range(25, 40, 5):
#     case = med_tvc_general(Xf = 30, RR = 0.3, Tin = t, Capacity = 51000,  Nef = 12)
#     case.design()
#     print("Tin:", t, "STEC: ", case.design_output[1]['Value'], "GOR: ", case.design_output[5]['Value'])
#case.simulation(gen = [5000,6000,5000,3000,2500], storage =6)
            
        
        