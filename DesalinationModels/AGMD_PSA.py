# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 08:47:50 2019
Converted from PSA's AGMD model

@author: Zhuoran Zhang
"""


import numpy as np

class AGMD_PSA(object):
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
    '''
    MNaCl = 58.44247
    Area_small = 7.2
    Area_big = 24
    def __init__(self,
                 module = 0,  # '0' for AS7C1.5L module and '1' for AS24C5L module
                 TEI_r  = 80, # Evaporator channel inlet temperature (ºC)
                 TCI_r  = 25, # Condenser channel inlet temperature (ºC)
                 FFR_r  = 582.7, # Feed flow rate (l/h)
                 FeedC_r= 35,  # Feed concentration (g/L)
                 ):
        
        self.module  = module
        self.TEI_r   = TEI_r
        self.TCI_r   = TCI_r
        self.FFR_r   = FFR_r
        self.FeedC_r = FeedC_r
        
        self.TEI_c   = 0.1 * self.TEI_r - 7
        self.FFR_c   = -1.61904761904762 + 0.00107142857142857 * self.FFR_r + 1.19047619047619E-06 * FFR_r**2
        self.TCI_c   = 0.2 * self.TCI_r -5
        self.FeedC_rM = self.FeedC_r / self.MNaCl
        self.FeedC_c  = 1.666666667 * self.FeedC_rM - 2
        
    def calculations(self):
        if self.module == 0:
            # PFlux (l/h/m2)
            a0 = 5.1736633875212
            a1 = 1.30735853812174
            a2 = 1.92497787391827
            a3 = -0.452032651637654
            a4 = -0.236018840235782
            a5 = 0.508528516411701
            a6 = -0.533945395042034
            
            self.PFlux_AS7_allM = a0 + a1 * self.TEI_c + a2 * self.FFR_c + a3 * self.TCI_c + a4 * self.FeedC_c + a5 * self.TEI_c * self.FFR_c + a6 * self.FFR_c**2
            
            # TCO (oC)
            a0 = 59.3878010910582
            a1 = 8.16074166971919
            a2 = -2.60915661582559
            a3 = 1.32417975241345
            a4 = -0.19364409802822
            a5 = -0.869096051478881
            a6 = 0.344756994802462
            a7 = 0.249090304647952
            a8 = 0.545163097718411 
            
            self.TCO_AS7_allM = a0 + a1 * self.TEI_c + a2 * self.FFR_c + a3 * self.TCI_c + a4 * self.FeedC_c + a5 * self.TEI_c * self.FFR_c + a6 * self.TCI_c * self.FFR_c + a7 * self.FFR_c * self.FeedC_c + a8 * self.FFR_c**2
            
            # Physical properties
            
            # Source: http://web.mit.edu/seawater/
            self.RhoF = self.SW_Density((self.TEI_r + self.TCO_AS7_allM)/2, (0.93644908*self.FeedC_r+0.56530373), 0.101325)
            self.CpF  = self.SW_SpcHeat((self.TEI_r + self.TCO_AS7_allM)/2, (0.93644908*self.FeedC_r+0.56530373), 0.101325)
            self.RhoP = self.SW_Density((self.TEI_r+self.TCI_r)/2, 0 , 0.101325)
            self.AHvP = self.SW_LatentHeat((self.TEI_r+self.TCI_r)/2, 0)
            
            # Permeate flow rate
            self.F_AS7_prod = self.PFlux_AS7_allM * self.Area_small
            # Energy paramters
            
            # Thermal power (kWth)
            self.ThPower_AS7_allM = (self.FFR_r * self.CpF * (self.TEI_r - self.TCO_AS7_allM)) * (self.RhoF / (1000*3600*1000))
            # STEC (kWhth/m3)
            self.STEC_AS7_allM    = (self.ThPower_AS7_allM) / ((self.PFlux_AS7_allM * self.Area_small)/1000)
            # GOR
            self.GOR_AS7_allM     = ((self.PFlux_AS7_allM * self.Area_small) * self.AHvP * self.RhoP / self.ThPower_AS7_allM) / (3600*1000*1000)
        
        elif self.module == 1:
            # PFlux (l/h/m2)
            a0 = 1.62205064163164
            a1 = 0.43010755918575
            a2 = 0.749745477059481
            a3 = -0.182577015724501
            a4 = -0.230447322413984
            a5 = 0.149994484727092
            a6 = -0.113629065991225
            a7 = -0.143058030558187
            
            self.PFlux_AS24_allM = a0 + a1 * self.TEI_c + a2 * self.FFR_c + a4 * self.FeedC_c + a5 * self.TEI_c * self.FFR_c + a6 * self.TCI_c * self.FFR_c + a7 * self.FFR_c**2
            
            # TCO (oC)
            a0 = 66.3403441037031
            a1 = 9.40190581573215
            a2 = -0.767996394594217
            a3 = 0.431467953662469
            a4 = -0.452156366689151
            a5 = -0.112279984442214
            a6 = 0.111320020706051
            
            self.TCO_AS24_allM = a0 + a1 * self.TEI_c + a2 * self.FFR_c + a3 * self.TCI_c + a4 * self.FeedC_c + a5 * self.TEI_c * self.FFR_c + a7 * self.FFR_c * self.FeedC_c
            
            # Physical properties
            
            # Source: http://web.mit.edu/seawater/
            self.RhoF = self.SW_Density((self.TEI_r + self.TCO_AS24_allM)/2, (0.93644908*self.FeedC_r+0.56530373), 0.101325)
            self.CpF  = self.SW_SpcHeat((self.TEI_r + self.TCO_AS24_allM)/2, (0.93644908*self.FeedC_r+0.56530373), 0.101325)
            self.RhoP = self.SW_Density((self.TEI_r+self.TCI_r)/2, 0 , 0.101325)
            self.AHvP = self.SW_LatentHeat((self.TEI_r+self.TCI_r)/2, 0)
            
            # Permeate flow rate
            self.F_AS24_prod = self.PFlux_AS24_allM * self.Area_big
            # Energy paramters
            
            # Thermal power (kWth)
            self.ThPower_AS24_allM = (self.FFR_r * self.CpF * (self.TEI_r - self.TCO_AS24_allM)) * (self.RhoF / (1000*3600*1000))
            # STEC (kWhth/m3)
            self.STEC_AS24_allM    = (self.ThPower_AS24_allM) / ((self.PFlux_AS24_allM * self.Area_big)/1000)
            # GOR
            self.GOR_AS24_allM     = ((self.PFlux_AS24_allM * self.Area_big) * self.AHvP * self.RhoP / self.ThPower_AS24_allM) / (3600*1000*1000)
   

    def SW_Density(self, T, S, P): # T in oC, S in ppt, P in Pa
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

case = AGMD_PSA(module =1)
case.calculations()

            
            
            
        
