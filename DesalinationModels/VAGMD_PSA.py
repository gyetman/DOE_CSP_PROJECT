# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 08:47:50 2019
Converted from PSA's AGMD model

@author: Zhuoran Zhang
"""


import numpy as np
import math
from DesalinationModels.VAGMD_cost import VAGMD_cost
from scipy.optimize import fmin

class VAGMD_PSA(object):
    # MD MODELS FOR AQUASTILL MODULES AS7C1.5L AND AS24C5L
    '''
    % Input variables:
    %  - Evaporator channel inlet temperature (TEI_r): 60 <= TEI_r <= 80 [ºC]
    %  - Condenser channel inlet temperature (TCI_r): 20 <= TCI_r <= 30 [ºC]
    %  - Feed flow rate (FFR_r): 400 <= FFR_r <= 1100 [l/h]
    %  - Feed concentration (FeedC_r): 35 <= FeedC_r <= 105 [g/l]
    
    % Output variables:
    %  - Permeate flow rate (PFR) [l/h]
    %  - Condenser channel outlet temperature (TCO) [ºC]
    %  - STEC (kWh_th/m3)
    '''
    MNaCl = 58.44247

    def __init__(self,
                 # Design parameters
                 module = 1,  # '0' for AS7C1.5L module and '1' for AS24C5L module
                 TEI_r  = 80, # Evaporator channel inlet temperature (ºC)
                 TCI_r  = 25, # Condenser channel inlet temperature (ºC)
                 FFR_r  = 582.7, # Feed flow rate (l/h)
                 FeedC_r= 35,  # Feed concentration (g/L)
                 Capacity = 1000, # System Capcity (m3/day)
                 Fossil_f = 1 # Fossil fuel fraction
                 ):
        
        self.module  = module
        self.TEI_r   = TEI_r
        self.TCI_r   = TCI_r
        self.FFR_r   = FFR_r
        self.FeedC_r = FeedC_r
        self.Capacity = Capacity
        self.Area_small = 7.2
        self.Area_big = 25.92
        self.Fossil_f = Fossil_f
        
    def design(self):
        if self.module == 0:
            self.Area = self.Area_small
            
            a0 = -5.92852056276695
            a1 = 0.0727051385344857
            a2 = 0.000171257319459785
            b0 = -1.58625328511844
            b1 = 0.00100772344603274
            b2 = 1.21886645045663E-06
            c0 = -5.88550175770424
            c1 = 0.267579272245288
            c2 = -0.00128636807748472
            d0 = -3.42043685144668
            d1 = 1.13278960319704
            d2 = -0.00168976175661686
            e0 = -1.86590588106158
            e1 = 0.022996902785667
            e2 = 0.0000673357015386866

            self.TEI_c = a0 + a1 * self.TEI_r + a2 * self.TEI_r**2;
            self.FFR_c = b0 + b1 * self.FFR_r + b2 * self.FFR_r**2;
            self.TCI_c = c0 + c1 * self.TCI_r + c2 * self.TCI_r**2;
            self.FeedC_rgkg = d0 + d1 * self.FeedC_r + d2 * self.FeedC_r**2;
            self.FeedC_c = e0 + e1 * self.FeedC_rgkg + e2 * self.FeedC_rgkg**2;

            # PFlux (l/h/m2)
            a0 = 5.15491715040315
            a1 = 1.34816811478689
            a2 = 1.9688194548982
            a3 = -0.476767577856363
            a4 = -0.234931551846368
            a5 = 0.519489260682274
            a6 = -0.515103837542192
            self.PFlux = a0 + a1 * self.TEI_c + a2 * self.FFR_c + a3 * self.TCI_c + a4 * self.FeedC_c + a5 * self.TEI_c * self.FFR_c + a6 * self.FFR_c**2
            
            # TCO (oC)
            a0 = 59.3299098792845
            a1 = 8.44054098164456
            a2 = -2.60106044085222
            a3 = 1.26732875019284
            a4 = -0.191713362784447
            a5 = -0.993311016905247
            a6 = 0.613515304196981
            self.TCO = a0 + a1 * self.TEI_c + a2 * self.FFR_c + a3 * self.TCI_c + a4 * self.FeedC_c + a5 * self.TEI_c * self.FFR_c + a6 * self.FFR_c**2
            
            # Physical properties
            
            # Source: http://web.mit.edu/seawater/
            self.RhoF = self.SW_Density((self.TEI_r + self.TCO)/2, self.FeedC_rgkg, 101325)
            self.CpF  = self.SW_SpcHeat((self.TEI_r + self.TCO)/2, self.FeedC_rgkg, 101325)
            self.RhoP = self.SW_Density((self.TEI_r+self.TCI_r)/2, 0 , 101325)
            self.AHvP = self.SW_LatentHeat((self.TEI_r+self.TCI_r)/2, 0)
            
            # Permeate flow rate
            self.F = self.PFlux * self.Area
            # Energy paramters

            # Thermal power (kWth)
            self.ThPower = (self.FFR_r * self.CpF * (self.TEI_r - self.TCO)) * (self.RhoF / (1000*3600*1000))
            # STEC (kWhth/m3)
            self.STEC    = (self.ThPower) / ((self.PFlux * self.Area)/1000)
            # GOR
            self.GOR     = ((self.PFlux * self.Area) * self.AHvP * self.RhoP / self.ThPower) / (3600*1000*1000)
        
        elif self.module == 1:
            self.Area = self.Area_big
            
            a0 = -4.58132767550252
            a1 = 0.0304572684711845
            a2 = 0.000499860996432572
            b0 = -1.59853289811683
            b1 = 0.00103551325811447
            b2 = 1.20331608066447E-06
            c0 = -6.45242015392136
            c1 = 0.313877713118005
            c2 = -0.00223123627844602
            d0 = -3.42043685144668
            d1 = 1.13278960319704
            d2 = -0.00168976175661686
            e0 = -1.86590588106158
            e1 = 0.022996902785667
            e2 = 0.0000673357015386866

            self.TEI_c = a0 + a1 * self.TEI_r + a2 * self.TEI_r**2;
            self.FFR_c = b0 + b1 * self.FFR_r + b2 * self.FFR_r**2;
            self.TCI_c = c0 + c1 * self.TCI_r + c2 * self.TCI_r**2;
            self.FeedC_rgkg = d0 + d1 * self.FeedC_r + d2 * self.FeedC_r**2;
            self.FeedC_c = e0 + e1 * self.FeedC_rgkg + e2 * self.FeedC_rgkg**2;


            # PFlux (l/h/m2)
            a0 = 1.4869977557046
            a1 = 0.398246057339935
            a2 = 0.696104956978965
            a3 = -0.168221817676666
            a4 = -0.213550364580167
            a5 = 0.138583563054577
            a6 = -0.105319845762804
            a7 = -0.129246504409905
            
            # TEI_c: Evaporator channel inlet temperature (ºC)
            
            self.PFlux = a0 + a1 * self.TEI_c + a2 * self.FFR_c + a4 * self.FeedC_c + a5 * self.TEI_c * self.FFR_c + a6 * self.TCI_c * self.FFR_c + a7 * self.FFR_c**2
            
            # TCO (oC)
            a0 = 66.3418043159458
            a1 = 9.45232195334816
            a2 = -0.729211549800743
            a3 = 0.434343924750824
            a4 = -0.418024395451331
            a5 = -0.231375452675282
            a6 = -0.531633527098017

            self.TCO = a0 + a1 * self.TEI_c + a2 * self.FFR_c + a3 * self.TCI_c + a4 * self.FeedC_c + a5 * self.TEI_c * self.FFR_c + a6 * self.TEI_c ** 2
            
            # Physical properties
            
            # Source: http://web.mit.edu/seawater/
            self.RhoF = self.SW_Density((self.TEI_r + self.TCO)/2, self.FeedC_rgkg, 101325)
            self.CpF  = self.SW_SpcHeat((self.TEI_r + self.TCO)/2, self.FeedC_rgkg, 101325)
            self.RhoP = self.SW_Density((self.TEI_r+self.TCI_r)/2, 0 , 101325)
            self.AHvP = self.SW_LatentHeat((self.TEI_r+self.TCI_r)/2, 0)
            
            # Permeate flow rate
            self.F= self.PFlux* self.Area
            # Energy paramters
            
            # Thermal power (kWth)
            self.ThPower = (self.FFR_r * self.CpF * (self.TEI_r - self.TCO)) * (self.RhoF / (1000*3600*1000))
            # STEC (kWhth/m3)
            self.STEC    = (self.ThPower) / ((self.PFlux * self.Area)/1000)
            # GOR
            self.GOR     = ((self.PFlux * self.Area) * self.AHvP * self.RhoP / self.ThPower) / (3600*1000*1000)
        
        
        self.num_modules = math.ceil(self.Capacity *1000 / self.F /24 )
        self.design_output = []
        self.design_output.append({'Name':'Number of modules required','Value':self.num_modules,'Unit':''})
        self.design_output.append({'Name':'Permeate flux of module','Value':self.PFlux,'Unit':'l/m2 h'})
        self.design_output.append({'Name':'Condenser outlet temperature','Value':self.TCO,'Unit':'oC'})
        self.design_output.append({'Name':'Permeate flow rate','Value':self.F * self.num_modules /1000 *24,'Unit':'m3/day'})    
        self.design_output.append({'Name':'Thermal power consumption','Value':self.ThPower * self.num_modules,'Unit':'kW(th)'})
        self.design_output.append({'Name':'Specific thermal power consumption','Value':self.STEC,'Unit':'kWh(th)/m3'})
        self.design_output.append({'Name':'Gained output ratio','Value':self.GOR,'Unit':''})
        return 
        
# Added optimization on parameter selection of TEI_r, TCI_r and FFR_r
    def opt(self):    
        def target(params):
            TEI_r, TCI_r, FFR_r = params[0:3]
            TEI_r = max(60, min (80, TEI_r))
            TCI_r = max(20, min (30, TCI_r))
            FFR_r = max(400, min (1100, FFR_r))

            temp = VAGMD_PSA(TEI_r=TEI_r, TCI_r=TCI_r, FFR_r=FFR_r, module= self.module,FeedC_r=self.FeedC_r, Capacity=self.Capacity)
            temp.design()
            temp_cost = VAGMD_cost(Capacity = temp.Capacity, Area = temp.Area, Pflux = temp.PFlux, th_module = temp.ThPower,STEC = temp.STEC, TCO = self.TCO, Prod = self.Capacity*365*0.9)
            temp_cost.lcow()
            return temp_cost.LCOW
        
        x0 =  np.asarray([80, 25, 528.7])
        xopt = fmin(target, x0)
        yopt = target(xopt)

        self.design_output.append({'Name':'(Suggested) Evaporator channel inlet temperature','Value':max(60,min(80,xopt[0])),'Unit':'oC'})
        self.design_output.append({'Name':'(Suggested) Condenser channel inlet temperature','Value':max(20,min(30,xopt[1])),'Unit':'oC'})
        self.design_output.append({'Name':'(Suggested) Feed flow rate ','Value':max(400, min(1100,xopt[2])),'Unit':'l/h'})
        self.design_output.append({'Name':'Estimated LCOW ','Value':yopt,'Unit':'$/m3'})

        return self.design_output
        

    
    def simulation(self, gen, storage):
        self.thermal_load = self.ThPower * self.num_modules # kWh
        self.max_prod = self.F /1000 * self.num_modules # m3/h
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
        
        # Add brine volume and concentration (using 100% rejection(make it a variable))
        
        return simu_output
            
        

    def SW_Density(self, T, S, P): # T in oC, S in ppt, P in Pa
        P = P/1E6
        if T < 100:
            P0 = 0.101325
        else:
            P0 = self.SW_Psat(T, S) / 1E6
        s = S/1000
        a = [9.9992293295E+02, 2.0341179217E-02, -6.1624591598E-03, 2.2614664708E-05, -4.6570659168E-08 ]
        b = [8.0200240891E+02, -2.0005183488E+00, 1.6771024982E-02, -3.0600536746E-05, -1.6132224742E-05] 
        
        rho_w = a[0] + a[1] * T + a[2] * T**2 + a[3] * T**3 + a[4] * T**4
        D_rho = b[0] * s + b[1] * s * T + b[2] * s * T**2 + b[3] * s * T**3 + b[4] * s**2 * T**2
        rho_sw_sharq = rho_w + D_rho
        
        c = [5.0792E-04, -3.4168E-06, 5.6931E-08, -3.7263E-10, 1.4465E-12, -1.7058E-15, -1.3389E-06, 4.8603E-09, -6.8039E-13]
        d = [-1.1077e-06, 5.5584e-09, -4.2539e-11, 8.3702e-09]
        
        kT = c[0] + c[1]*T + c[2]*T**2 + c[3]*T**3 + c[4]*T**4 + c[5]*T**5 + P*( c[6] + c[7]*T + c[8]*T**3) + S*(d[0] + d[1]*T + d[2]*T**2 + d[3]*P)
        
        F_P = np.exp((P-P0) * (c[0] + c[1]*T + c[2]*T**2 + c[3]*T**3 + c[4]*T**4 + c[5]*T**5 + S*(d[0] + d[1]*T + d[2]*T**2 )) + 0.5* (P**2 - P0**2) * (c[6] + c[7]*T + c[8]*T**3 + d[3]*S))
        rho = rho_sw_sharq * F_P
        return rho
        
    def SW_Psat(self, T, S): # T in oC, S in ppt
        T = T + 273.15
        a = [-5.8002206E+03, 1.3914993E+00, -4.8640239E-02, 4.1764768E-05, -1.4452093E-08, 6.5459673E+00]
        
        Pv_w = np.exp( a[0] / T + a[1] + a[2] * T + a[3] * T**2 + a[4] * T**3 + a[5] * np.log(T) )
        
        b = [-4.5818E-04, -2.0443E-06]
        
        Pv = Pv_w * np.exp(b[0] * S + b[1] * S**2)
        return Pv
            
    def SW_LatentHeat(self, T, S):  # T in oC, S in ppt
        a = [2.5008991412E+06, -2.3691806479E+03, 2.6776439436E-01, -8.1027544602E-03, -2.0799346624E-05]
        hfg_w = a[0] + a[1]*T + a[2]*T**2 + a[3]*T**3 + a[4]*T**4
        hfg = hfg_w * (1-0.001*S)
        return hfg
    
    def SW_SpcHeat(self,T,S,P): # T in oC, S in ppt, P in Pa
        P =P/1E6
        if T < 100:
            P0 = 0.101325
        else:
            P0 = self.SW_Psat(T, S) / 1E6
        
        T68 = 1.00024 * (T + 273.15)
        
        A = 5.328 - 9.76E-02 * S + 4.04E-04*S**2
        B = -6.913E-03 + 7.351E-04 *S - 3.15E-06*S**2
        C = 9.6E-06 -1.927E-06*S + 8.23E-09*S**2
        D = 2.5E-09 +1.666E-09*S - 7.125E-12*S**2
        cp_sw_P0 = 1000 * (A + B*T68 + C*T68**2 + D*T68**3)
        
        # Pressure dependent terms
        c = [-3.1118, 0.0157, 5.1014E-05, -1.0302E-06, 0.0107, -3.9716E-05, 3.2088E-08, 1.0119E-09]
        cp_sw_P = (P-P0) * ((c[0] + c[1]*T + c[2]*T**2 + c[3]*T**3) + S * (c[4] + c[5]*T + c[6]*T**2 + c[7]*T**3))
        
        cp = cp_sw_P0 + cp_sw_P
        return cp
            
        
        
#%% Model execution
#Feed = [35.064,46.752,58.44,70.128,81.816,93.504,105.192]
#Plux = []
#STEC =[]
#GOR =[]
#for f in Feed:
#case = VAGMD_PSA()
#output = case.design()
#a = [0.0, 0.0,  1031.3695068359375, 2253.046630859375, 2805.6748046875, 2788.9150390625, 1669.11767578125, 1146.8067626953125, 246.9362030029297, 0.0, 0.0]
#simu = case.simulation(gen = a, storage = 6)
##print(simu)
#
##    Plux.append(case.PFlux)
#    STEC.append(case.STEC)
#    GOR.append(case.GOR)
#    print('TCO7: ', case.F)
#    case2 = VAGMD_PSA(module =1,FFR_r=1100,FeedC_r=f)
#    case2.calculations()
#    print('TCO26: ', case2.F)
##    print('STEC: ', case.STEC_AS26_allM)
##    print('GOR: ', case.GOR_AS26_allM)
    
# case = VAGMD_PSA()
# case.design()
# case.opt()

            
        
