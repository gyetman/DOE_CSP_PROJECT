# -*- coding: utf-8 -*-
"""
Converted from PSA's LT-MED general design model
Created on Wed Aug 28 10:01:06 2019

@author: Zhuoran Zhang
"""

import numpy as np
import math
import DesalinationModels.IAPWS97_thermo_functions as TD_func

class lt_med_calculation(object):
        
    # class variables
    DELTAT_loss = 0.05

        
    def __init__(self,
                 Tb1      = 76     , # The brine temperature in the first effect, ºC
                 Xf       = 35000  , # The feed water salinity, ppm
                 Ms       = 1.023  , # The mass flow rate of the steam entering the bundle tube of the first effect, kg/s
                 Ts       = 70     , # The temperature of the steam at the inlet of the first bundle tube, ºC
                 Tcwin    = 25     , # Seawater inlet temperature in the condenser, ºC
                 DELTATcw = 7.3    , # The temperature difference between the inlet and outlet seawater temperature in the condenser, ºC
                 Mf       = 38.27  , # Feed water mass flow rate sprayed on the bundle tube, kg/s
                 Nef      = 12     , # Number of effects
                 Nph      = 11     , # Number of preheaters
                 Cp       = 4.18   , # Specific heat of distillate, feed and brine, that is considered. [J/(kg C)]
                 BPE      = 0.5    , # The Boiling Point Elevation, ºC
                 NEA      = 0.5    , # The Non Equilibrium Allowance, ºC
                 Tol      = 0.0001 , # The tolarance applied to get equal area in the effects)
                 ):
        
        self.Tb1 = Tb1 
        self.Xf = Xf
        self.Ms = Ms
        self.Ts = Ts 
        self.Tcwin = Tcwin 
        self.DELTATcw = DELTATcw 
        self.Mf = Mf
        self.Nef = Nef
        self.Nph = Nef-1
        self.Cp = Cp
        self.BPE = np.zeros(self.Nef)
        self.NEA = np.zeros(self.Nef)
        self.Tol = Tol
        
        # ASSUMPTIONS. They keep constant during the calculations
        self.Tb = np.zeros(Nef) 
        self.Tv = np.zeros(Nef)
        self.DTb = np.zeros(Nef)
        self.Tdb = np.zeros(Nef)
        self.Tph = np.zeros(Nef)
        
        self.Tb[0] = self.Tb1 # The brine temperature in the first effect, ºC
        self.Tb_last = 37  # Brine temperature in the last effect, ºC
        self.Tv[0] = self.Tb1 - BPE - self.DELTAT_loss # The vapor temperature inside the first effect, ºC
        self.Tf    = self.Tb1 -3 # The feed water temperature sprayed in the first effect, ºC
        self.Tcwout= self.Tcwin + self.DELTATcw  # The seawater outlet temperature of the condenser, ºC
        self.Tph[0] = self.Tf
        self.Length_ef = 0.5 # Length of the tubes in the effects tube bundle, m
        self.Length_ph = 0.75 * self.Length_ef # Lenghth of the tubes in the preheaters tube bundle, m
        self.Length_c  = 1.5  * self.Length_ef # Length of the tubes in the condenser tube bundle, m
        self.Di = 0.0254 # Inner diameter of the tubes in the bundle tubes, m
        self.BPE[0] = BPE
        self.NEA[0] = NEA

        for i in range(self.Nef-1):
            # Calculate the vapor temperature in each effect, ºC
            self.BPE[i+1] = BPE
            self.NEA[i+1] = NEA
            self.Tb[i+1] = self.Tb[i] - (self.Tb[0]-self.Tb_last) / (self.Nef -1)
            # Calculate the temperature of the brine after flashing process from effects 2 to Nef, Tdb(2,1), ºC
            self.Tv[i+1] = self.Tb[i+1] - self.BPE[i+1] - self.DELTAT_loss
            self.DTb[i+1] = self.Tb[i] - self.Tb[i+1]
            self.Tdb[i+1] = self.Tv[i+1] - self.NEA[i]
            # Calculate the seawater temperature in the preheater, Tph(i,1), ºC
            self.Tph[i+1] = self.Tph[i] - (self.Tph[0] - self.Tcwout) / self.Nph

    # PREHEATER calculations
        # Calculations in the prehater:
#        % Calculate the seawater temperature in the preheater, Tph(i,1), ºC
#        % Calculate the feed water mass flow rate sprayed on the bundle tube, Mf, kg/s
#        % Calculate the vapor consumed in each preheater, Mvh(i,1), kg/s
#        % Calculate the heat transfer rate in the preheaters, Qph(i,1), kJ/s
#        % Calculate the overall heat transfer coefficient of the preheaters, Uph(i,1), kW/m2ºC. Correlation of El-Dessouky
#        % Calculate the condensate generated in the preheater,Mdh(i,1), kg/s
#        % Calculate the heat transfer area of the preheaters, Aph(i,1), m2
#        % Evh(i,1) is the enthalpy of the vapor that enters the preheater, kJ/kg
#        % Elh(i,1) is the enthalpy of the condensate that leaves the preheater, kJ/kg
#        % Lvh(i,1) is the latent heat of the vapor in the preheater, kJ/kg
#        % LTMDph (i,1)is the log mean temperature difference, ºC 
    def preheater_calculations(self):
        
        self.Evh = np.zeros(self.Nph)
        self.Elh = np.zeros(self.Nph)
        self.Lvh = np.zeros(self.Nph)
        self.Mvh = np.zeros(self.Nph)
        self.Mdh = np.zeros(self.Nph)
        self.Qph = np.zeros(self.Nph)
        self.Uph = np.zeros(self.Nph)
        self.LTMDph = np.zeros(self.Nph)
        self.Aph = np.zeros(self.Nph)
        
        for i in range(self.Nph):
            self.Evh[i] = TD_func.enthalpySatVapTW(self.Tv[i]+273.15) 
            self.Elh[i] = TD_func.enthalpySatLiqTW(self.Tv[i]+273.15) 
            self.Lvh[i] = self.Evh[i] -self.Elh[i] 
            self.Mvh[i] = self.Mf * self.Cp * (self.Tph[i] - self.Tph[i+1]) / self.Lvh[i] 
            self.Mdh[i] = self.Mvh[i] 
            self.Qph[i] = self.Mf * self.Cp * (self.Tph[i] - self.Tph[i+1]) 
            self.Uph[i] = 1.7194 + (3.2063e-3 * self.Tv[i]) + (1.5971e-5 * self.Tv[i]**2) - (1.9918e-7 * self.Tv[i]**3) 
            self.LTMDph[i] = ((self.Tv[i] - self.Tph[i+1]) - (self.Tv[i] - self.Tph[i])) / math.log( (self.Tv[i] - self.Tph[i+1]) / (self.Tv[i] - self.Tph[i]) ) 
            self.Aph[i] = self.Qph[i] / self.Uph[i] / self.LTMDph[i] 
        
    # FIRST EFFECT & OTHER EFFECTS calculations
#        % Definition of the variables used and calculated:
#
#        % Aef(i,1) is the heat transfer area of the bundle tube of each effect, m2
#        % Mgb(i,1) is the mass flow rate of the vapor generated by boiling, kg/s
#        % Mdf(i,1) is the mass flow rate of the vaspor generated by flash of the distillate in the
#        % flash box, kg/s
#        % Mgt(i,1) is the sum of the mass flow rate of total vapor leaving each
#        % effect plus vapor generated by flash in the flash box, kg/s
#        % Mv(i,1) is the vapor mass flow rate entering the bundle tube of each effect, kg/s
#        % Egv(i,1) is the enthalpy of the vapor entering the bundle tube of each effect, kJ/kg
#        % Egl(i,1) is the enthalpy of the condensate leaving the bundle tube of each effect, kJ/kg
#        % Lv(i,1) is the latent heat of the vapor entering the bundle tube of each effect, kJ/kg
#        % Lgf(i,1) is the latent heat of the vapor generated by flashing of the brine in each effect, kJ/kg
#        % Lgb(i,1) is the latent heat of the vapor generated by boiling of the brine in each effect, kJ/kg
#        % Mgf(i,1) is the mass flow rate of the vapor generated by flashing of the brine in each effect, kg/s
#        % Mfv(i,1) is the mass flow rate of the vapor generated in each effect (by boiling and flashing), kg/s
#        % Mdb(i,1) is the mass flow rate of the brine after flashing, kg/s
#        % Xdb is the salinity of the brine after flashing, ppm
#        % Md(i,1) is the distillate mass flow rate leaving each flash box, kg/s
#        % Mdaf(i,1) is the distillate mass flow rate leaving each effect, kg/s
#        % Uef(i,1) is the overall heat transfer coefficient of each effect, kW/m2ºC
#        % Mb(i,1) is the mass flow rate of the brine that leaves each effect mass flow rate, kg/s
#        % Xb(i,1) is the salinity of the brine leaving each effect, ppm 
        
    def effects_calculation(self):
        self.Egs = TD_func.enthalpySatVapTW(self.Ts+273.15) 
        self.Els = TD_func.enthalpySatLiqTW(self.Ts+273.15) 
        self.Ls = self.Egs - self.Els
        self.Qs = self.Ms * self.Ls
        self.Qef = np.zeros(self.Nef)
        self.Qef[0] = self.Qs
        self.max_DA = 20
        self.Egbg = np.zeros(self.Nef)
        self.Egbl = np.zeros(self.Nef)
        self.Lgb  = np.zeros(self.Nef)
        self.Uef  = np.zeros(self.Nef)
        self.Mgb  = np.zeros(self.Nef)
        self.Aef  = np.zeros(self.Nef)
        self.Lv   = np.zeros(self.Nef)
        self.Mgf  = np.zeros(self.Nef)
        self.Mdf  = np.zeros(self.Nef)
        self.Md   = np.zeros(self.Nef)
        self.Mdb  = np.zeros(self.Nef)
#        self.DTb  = np.zeros(self.Nef)
        self.Mfv  = np.zeros(self.Nef)
        self.Mgt  = np.zeros(self.Nef)
        self.Mb   = np.zeros(self.Nef)
        self.Xb   = np.zeros(self.Nef)
        
        self.Mv   = np.zeros(self.Nef)
        self.Mdaf = np.zeros(self.Nef)
        self.Egv  = np.zeros(self.Nef)
        self.Egl  = np.zeros(self.Nef)
        self.Lgf  = np.zeros(self.Nef)
        self.Lgb  = np.zeros(self.Nef)
        self.Xdb  = np.zeros(self.Nef)
        self.Uef  = np.zeros(self.Nef)
        self.Ldf  = np.zeros(self.Nef)
        self.Xb_w = np.zeros(self.Nef)
        self.A    = np.zeros(self.Nef)
        self.B    = np.zeros(self.Nef)
        self.C    = np.zeros(self.Nef)
        self.DA   = np.zeros(self.Nef)
        
        self.Mgf[0] = 0
        self.Mdf[0] = 0
        self.Md[0]  = 0
        self.Mdb[0] = 0
        self.DTb[0] = self.Ts - self.Tb[0]
        self.count = 0
        
        while self.max_DA > self.Tol:
            # Set up for the first effect
            self.Egbg[0] = TD_func.enthalpySatVapTW(self.Tv[0]+273.15)
            self.Egbl[0] = TD_func.enthalpySatLiqTW(self.Tv[0]+273.15)
            self.Lgb[0]  = self.Egbg[0] - self.Egbl[0]
            self.Uef[0]  = 1.9695 + (1.2057e-2  * self.Tb[0]) - (8.5989e-5 * self.Tb[0]**2) + (2.5651e-7 * self.Tb[0]**3)
            self.Mgb[0]  = (self.Qef[0] - self.Mf * self.Cp * (self.Tb[0] - self.Tf)) / self.Lgb[0]
            self.Aef[0]  = self.Qef[0] / (self.Uef[0] * (self.Ts - self.Tb[0]))
            self.Lv[0]   = self.Lgb[0]
            self.Mfv[0]  = (self.Mgb[0] + self.Mgf[0]) * 3600
            self.Mgt[0]  = (self.Mgb[0] + self.Mgf[0] + self.Mdf[0])
            self.Mb[0]   = self.Mf - self.Mgb[0]
            self.Xb[0]   = self.Xf * self.Mf / self.Mb[0]
            
            self.Sum_A = self.Aef[0]
            
            # Other effects calculations
            
            for i in range(1, self.Nef):
                self.Mv[i]   = self.Mgt[i-1] - self.Mvh[i-1]
                self.Mdaf[i] = self.Mv[i]
                self.Egv[i]  = TD_func.enthalpySatVapTW(self.Tv[i]+273.15)
                self.Egl[i]  = TD_func.enthalpySatLiqTW(self.Tv[i]+273.15)
                self.Lv[i]   = self.Egv[i] - self.Egl[i]
                self.Lgf[i]  = self.Lv[i]
                self.Lgb[i]  = self.Lv[i]
                self.Mgf[i]  = self.Mb[i-1] * self.Cp *(self.Tb[i-1] - self.Tdb[i]) / self.Lgf[i]
                self.Mdb[i]  = self.Mb[i-1] - self.Mgf[i]
                self.Xdb[i]  = self.Xb[i-1] * self.Mb[i-1] / self.Mdb[i]
                self.Mgb[i]  = (self.Mv[i] * self.Lv[i-1] + self.Mdb[i] *self.Cp * (self.Tdb[i] - self.Tb[i])) / self.Lgb[i]
                self.Mfv[i]  = (self.Mgb[i] + self.Mgf[i]) *3600
                self.Qef[i]  = self.Mv[i] * self.Lv[i-1]
                self.Uef[i]  = 1.9695 + (1.2057e-2 * self.Tb[i]) - (8.5989e-5 * self.Tb[i]**2) + (2.5651e-7 * self.Tb[i]**3)
                self.Mb[i]   = self.Mdb[i] - self.Mgb[i]
                self.Xb[i]   = self.Mdb[i] * self.Xdb[i] / self.Mb[i]
                self.Ldf[i]  = self.Lv[i]
                self.Mdf[i]  = (self.Mdh[i-1] * self.Cp * (self.Tv[i-1] - self.Tv[i]) + (self.Mdaf[i-1] * self.Cp * (self.Tv[i-1] - self.Tv[i])) + self.Md[i-1] * self.Cp * (self.Tv[i-1] - self.Tv[i]) ) / self.Ldf[i]
                self.Mgt[i]  = self.Mgb[i] + self.Mgf[i] + self.Mdf[i] 
                self.Md[i]   = self.Mdaf[i] + self.Mdh[i-1] + self.Md[i-1] - self.Mdf[i]
                self.Aef[i]  = self.Qef[i] / self.Uef[i] / (self.Tv[i-1] - self.Tb[i])
                
                self.Sum_A += self.Aef[i]
                
            self.Am = self.Sum_A / self.Nef
            self.DTb[0] *= (self.Aef[0] / self.Am)
            self.Tb[0]   = self.Ts - self.DTb[0] 
            self.Xb_w[0] = self.Xb[0] / (1000*1000) *100 # Salinity in weigth percentage
            self.A[0]    = 8.325e-2 + (1.883e-4 * self.Tb[0]) + (4.02e-6 * self.Tb[0]**2)
            self.B[0]    = -7.625e-4 + (9.02e-5 * self.Tb[0]) - (5.2e-7 * self.Tb[0]**2)
            self.C[0]    = 1.552e-4- (3e-6 * self.Tb[0]) - (3e-8 * self.Tb[0]**2)
            self.BPE[0]  = self.A[0] * self.Xb_w[0] + self.B[0] * self.Xb_w[0]**2 + self.C[0] * self.Xb_w[0]**3
            self.Tv[0]   = self.Tb[0] - self.BPE[0] - self.DELTAT_loss
            self.Uef[0]  = 1.9695 + (1.2057e-2  * self.Tb[0]) - (8.5989e-5 * self.Tb[0]**2) + (2.5651e-7 * self.Tb[0]**3)
            
            for i in range(1, self.Nef):
                self.DTb[i] *= self.Aef[i] / self.Am
                self.Tb[i]  = self.Tb[i-1] -self.DTb[i]
                self.Xb_w[i] = self.Xb[i] / (1000*1000) *100
                self.A[i]    = 8.325e-2 + (1.883e-4 * self.Tb[i]) + (4.02e-6 * self.Tb[i]**2)
                self.B[i]    = -7.625e-4 + (9.02e-5 * self.Tb[i]) - (5.2e-7 * self.Tb[i]**2)
                self.C[i]    = 1.552e-4- (3e-6 * self.Tb[i]) - (3e-8 * self.Tb[i]**2)
                self.BPE[i]  = self.A[i] * self.Xb_w[i] + self.B[i] * self.Xb_w[i]**2 + self.C[i] * self.Xb_w[i]**3
                self.NEA[i]  = 33 * self.DTb[i]**0.55 / self.Tv[i]
                self.Tv[i]   = self.Tb[i] - self.BPE[i] - self.DELTAT_loss
                self.Tdb[i]  = self.Tv[i] - self.NEA[i]
                self.DA[i]   = abs(self.Aef[i-1] - self.Aef[i])
            
            self.count += 1
            self.max_DA = max(self.DA)
        
        
        self.Nt_ef = np.zeros(self.Nef)
        for i in range(self.Nef):
            self.Nt_ef[i] = self.Aef[i] / (math.pi * self.Length_ef *self.Di)
            
    # CONDENSER calculations
#        % CONDENSER
#        % Calculate the vapor entering the condenser, Mgt, kg/s
#        % Calculate the seawater flow rate flowing through the condenser, Mcw, kg/s
#        % Calculate the distillate produced in the condenser, Mdc, kg/s
#        % Calculate the heat transfer rate in the condenser, Qc, kW
#        % Calculate the heat transfer area of the condenser, Ac, m2 
    def condenser_calculations(self):
        self.Mgt[self.Nef-1] = (self.Mgb[self.Nef-1] + self.Mgf[self.Nef-1] + self.Mdf[self.Nef-1]) / 0.99
        self.Lgt = self.Lv[self.Nef-1]
        self.Qc  = self.Mgt[self.Nef-1] * self.Lgt
        self.Mcw = self.Qc / self.Cp / (self.Tcwout - self.Tcwin)
        self.Mdc = self.Mgt[self.Nef-1]
        self.LTMDc = ((self.Tv[self.Nef-1] - self.Tcwin) - (self.Tv[self.Nef-1] - self.Tcwout)) / math.log( (self.Tv[self.Nef-1] - self.Tcwin) / (self.Tv[self.Nef-1] - self.Tcwout) ) 
        self.Uc  = 1.7194 + (3.2063e-3 * self.Tv[self.Nef-1]) + (1.5971e-5 * self.Tv[self.Nef-1]**2) - (1.9918e-7 * self.Tv[self.Nef-1]**3) 
        self.Ac  = self.Qc / self.Uc / self.LTMDc
        self.Nt_c= self.Ac / (math.pi * self.Length_c * self.Di)
    
    # MIXTURE OF DISTILLATES  
    def distilllates_calculations(self):
#% Calculate the final production, Mprod
#% Calculate the temperature of the distillate production, Tprod, ºC
        self.Tvc = self.Tv[self.Nef-1] - self.DELTAT_loss
        self.Mprod = self.Md[self.Nef-1] + self.Mdc  #kg/s
        self.Tprod = (self.Md[self.Nef-1] * self.Tv[self.Nef-1] + self.Mdc * self.Tvc) / self.Mprod
        
        self.DELTAT_final = np.zeros(self.Nef-1)
        for i in range(self.Nef-1):
            self.DELTAT_final[i] = self.Tb[i] -self.Tb[i+1]
        
        self.STE = self.Qef[0] / self.Mprod / 3.6
        self.GOR = self.Mprod / self.Ms
        self.Mprod_m3_day = self.Mprod * 24 * 3.6  # m3/day
        self.RR = self.Mprod / self.Mf
        
#    % MIXER (mixture of brine, distillate product and rejected seawater)
#    % Calculate the temperature after the mixer, Tmix, ºC
#    % Mrej is the flow rate of the rejected seawater from the condenser, kg/s
        self.Mr = self.Mcw - self.Mf
        self.Tm = (self.Mb[self.Nef-1] * self.Tb[self.Nef-1] + self.Mprod * self.Tprod + self.Mr * self.Tcwout) / self.Mcw
        self.Mbf = self.Mb[self.Nef-1] + self.Mr
        self.Xbf = self.Xb[self.Nef-1] * self.Mb[self.Nef-1] / self.Mbf
        
       # % Specific heat transfer area, m2/kg/s
        self.sum_A = sum(self.Aef)
        self.sum_Aph = sum(self.Aph)
        self.sA = (self.sum_A + self.sum_Aph + self.Ac) / self.Mprod
       
    def model_execution(self):
        self.preheater_calculations()
        self.effects_calculation()
        self.condenser_calculations()
        self.distilllates_calculations()
        
#%% MODEL EXECUTION            

default_case = lt_med_calculation()
default_case.model_execution()
            
        
        