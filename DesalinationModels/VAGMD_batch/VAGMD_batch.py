# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 11:16:22 2020

@author: zzrfl
"""
# To do:
    #Dynamic path for .mat file
from scipy.io import loadmat
from DesalinationModels.VAGMD_batch.SW_functions import SW_Density, SW_Psat, SW_LatentHeat, SW_SpcHeat
import numpy as np
import math
import pandas as pd
from pathlib import Path
import math
import json

import app_config as cfg

class VAGMD_batch(object):
    def __init__(self,
        # Design parameters
        module = 0,  # '0' for AS7C1.5L module and '1' for AS26C2.7L module
        TEI_r  = 80, # Evaporator channel inlet temperature (ºC)
        TCI_r  = 25, # Condenser channel inlet temperature (ºC)
        FFR_r  = 600, # Feed flow rate (l/h)
        FeedC_r= 35,  # Feed concentration (g/L)
        V0     = 30,  # Initial batch volume (m3)
        RR     = 30,  # Recovery rate
        
        Capacity = 1000, # System Capcity (m3/day)
        Fossil_f = 1, # Fossil fuel fraction
        
        j = 'c', # cooling system: 'c' for closed, 'o' for open
        Ttank = 25, # Initial temeprature of the saline feed
        TCoolIn = 15, # Initial tmeeprature of the cooling water
        dt = 60, # Time step for the simulation (< 480 second)
        ):
        
        self.module  = module
        self.TEI_r   = TEI_r
        self.TCI_r   = TCI_r
        self.FFR_r   = FFR_r
        self.FeedC_r = FeedC_r
        self.Capacity = Capacity
        self.Area_small = 7.2
        self.Area_big = 25.92
        self.V0       = V0
        self.RR       = RR
        self.Fossil_f = Fossil_f        
        self.j = j
        self.Ttank = Ttank
        self.TCoolIn = TCoolIn
        self.dt = dt
        self.base_path = Path(__file__).resolve().parent.parent.parent.absolute()

    def design(self):
        Vdisch  = 3.2175 # (L)
        minS   = 35     # (g/L)       
        maxS   = 292.2 # g/L
        if self.module == 0:
            k = 7
            c0=-158.2007422
            c1=0.39402609
            c2=0
            c3=0.000585345
            c4=8.93618E-05
            c5=-0.000287828
            self.Area = self.Area_small

        else:
            k = 26
            c0=-72.53793298
            c1=0.110437201
            c2=0
            c3=0.000643495
            c4=0.000189924
            c5=-0.001111447
            self.Area = self.Area_big
        
        self.RRf   = 100 * (1 - self.FeedC_r/maxS) # Maximum value of final recovery ratio allowed
        # maxRR = 100 * (1 - (minS/maxS))  # 

        if self.RR > self.RRf:
            raise Exception("The recovery rate must be below ", self.RRf, "%")
        
        
        self.Sf = self.FeedC_r / ( 1 - self.RR/100)  # Final feed salinity (g/L)  
       
       # Selection of model and ocoling system
        if ( k == 7 and self.Sf > 175.3) or ( k ==26 and self.Sf > 140.2):
            self.TEI_r = 80
            self.FFR_r = 1100
            self.TCI_r = 25
            self.j = 'c' # cooling circuit is closed to maintain TCI constant
        
       
        #  Calculate [PFlux, TCO, TEO, PFR, ATml, ThPower, STEC, GOR]
        #                 0,   1,   2,   3,    4,       5,    6,   7
        
        results = self.VAGMD_Models_NaCl(self.TEI_r, self.FFR_r, self.TCI_r, self.FeedC_r, k, self.Ttank)
        #  Calculate [PFlux, TCO, TEO, RhoF, CpF, RhoC, CpC, RhoP, AHvP, A, ATml, ThPower, STEC, GOR]
        #             0      1    2    3     4    5     6    7     8     9   10   11       12    13
    
        U = 3168 # Wth/m2/oC (overall heat transefr coefficient)
        AHX = 1.34 # m2 (effective heat transfer surface)
        self.CFR = 1265 # l/h (cooling flow rate)
        self.TCoolIn = [self.TCoolIn]        
        
        # Initialize the time series
        self.PFlux = [results[0]] # kg/h/m2        
        self.PFR   = [results[0] * results[9]] # kg/h
        self.Vd = [0]
        self.AccVd = [0]
        self.Discharges = [math.floor(self.AccVd[0] / Vdisch)]
        self.t = [0]        
        self.tminute = [0]  
        self.R = [0]
        self.S = [self.FeedC_r]
        self.RR = [100 * ( 1- ((self.FFR_r - self.PFR[0])/self.FFR_r*(self.S[0]/self.S[0])*(1-self.R[0]/100)))]
        self.TCO   = [results[1]]
        self.TEO   = [results[2]]    
        self.ATml  = [results[10]]
        self.ThPower = [results[11]] # kW(th)             
        self.ThEnergy = [0] # kW(th)
        self.AccThEnergy = [0]  # kW(th)
        self.TCoolOut = [20]
        self.Ch = [0]
        self.Cc = [0]
        self.Eff = [0]        
        self.CPower = [0]  # kW(th)
        self.CEnergy = [0] # kWh(th)
        self.AccCEnergy = [0] # kWh(th)        
        self.GOR = [0]
        self.STEC = [0]
        self.V = [self.V0]
        
        self.RhoF = results[3]
        self.CpF = results[4]
        self.RhoC = results[5]        
        self.CpC = results[6]
        
        self.TCI = [self.TCI_r]
        self.Ttank = [self.Ttank]
        
        EffPumpFFR = 0.6
        EffPumpCFR = 0.6
        APdropCFR = 170 # mbar
        self.ElPowerCooling = [(8.3140/(1013.25*0.082*3600*1000))*(APdropCFR/EffPumpCFR)*(self.CFR)]
        self.APdropFFR  = [c0 + c1 * self.FFR_r + c2 * self.S[0] + c3 * self.FFR_r * self.S[0] + c4 * self.FFR_r**2 + c5 * self.S[0]**2]
        self.ElPowerFeed = [(8.3140/(1013.25*0.082*3600*1000)) *(self.APdropFFR[0] / EffPumpFFR) * (self.FFR_r)]
        self.ElPower = [self.ElPowerFeed[0] + self.ElPowerCooling[0]]
        self.ElEnergy = [0]
        self.AccElEnergy = [0]
        self.SEEC = [0]
        
        # Complete the time series
        while self.S[-1] < self.Sf and self.V[-1] > 0:
            self.t.append(self.t[-1]+ self.dt/3600)
            self.tminute.append(self.t[-1]*60)
            self.Vd.append(self.PFR[-1] * self.dt/3600)
            self.V.append(self.V[-1] - self.Vd[-1])
            self.S.append(self.V[-2]/self.V[-1]*self.S[-1])
            self.Ttank.append((self.FFR_r * self.dt/3600 * self.TEO[-1] + self.V[-2] * self.Ttank[-1]) / (self.V[-2] + self.FFR_r * self.dt/3600))
            self.Ch.append(self.FFR_r * self.RhoF * self.CpF / 3600 / 1000) # Wth/oC
            self.Cc.append(self.CFR * self.RhoC * self.CpC / 3600 / 1000)
            self.Cmin = min(self.Ch[-1], self.Cc[-1])
            self.Cmax = max(self.Ch[-1], self.Cc[-1]) 
            self.NTU = U * AHX / self.Cmin
            self.Eff.append( (1-math.exp(-(1-(self.Cmin/self.Cmax))*self.NTU))/(1-self.Cmin/self.Cmax*math.exp(-(1-(self.Cmin/self.Cmax))*self.NTU)))
            self.ElPowerCooling.append(self.ElPowerCooling[-1])
            
            if self.j == 'o':
                self.TCoolIn.append(self.TCoolIn[-1])
                self.CPower.append(self.Eff[-1] * self.Cmin * (self.Ttank[-1] - self.TCoolIn[-1]) / 1000) # kWth
                self.TCoolOut.append(self.TCoolIn[-1] + (self.CPower[-1] * 1000 / self.Cc[-1]))
                self.TCI.append(self.Ttank[-1] - self.CPower[-1] * 1000 / self.Ch[-1])

            else:
                self.TCI.append(self.TCI[-1])
                self.CPower.append(self.Ch[-1] * (self.Ttank[-1]-self.TCI[-1])/1000)
                self.TCoolIn.append(self.Ttank[-1] - self.CPower[-1] * 1000 / (self.Eff[-1] * self.Cmin))
                self.TCoolOut.append(self.TCoolIn[-1] + self.Ch[-1] / self.Cc[-1] * (self.Ttank[-1] - self.TCI[-1]))
            
            new_results = self.VAGMD_Models_NaCl(self.TEI_r, self.FFR_r, self.TCI[-1], self.S[-1], k, self.Ttank[-1])
            self.PFlux.append(new_results[0])
            self.PFR.append(new_results[0] * new_results[9])
            self.AccVd.append(self.Vd[-1] + self.AccVd[-1])
            self.Discharges.append(math.floor(self.AccVd[-1]/ Vdisch))
            self.R.append(100 * (1-self.S[0]/self.S[-1]))
            self.RR.append(100 * ( 1- ((self.FFR_r - self.PFR[-1])/self.FFR_r*(self.S[-1]/self.S[0])*(1-self.R[-1]/100))))
            self.TCO.append(new_results[1])
            self.TEO.append(new_results[2])             
            self.ATml.append(new_results[10])
            self.ThPower.append(new_results[11])    # kW-th        
            self.ThEnergy.append(self.ThPower[-1] * self.dt/3600 * 1000)  # Wh-th
            self.AccThEnergy.append(self.ThEnergy[-1] + self.AccThEnergy[-1])            
            self.CEnergy.append(self.CPower[-1] * (self.t[-1] - self.t[-2]) * 1000)  # Wh-th           
            self.AccCEnergy.append(self.CEnergy[-1] + self.AccCEnergy[-1])
            self.GOR.append((self.AccVd[-1] * new_results[8] * new_results[7] / 1000) / (self.AccThEnergy[-1] * 3.6e3))
            self.STEC.append(self.AccThEnergy[-1] / (self.AccVd[-1] / 1000) / 1000)
            self.APdropFFR.append(c0 + c1 * self.FFR_r + c2 * self.S[-1] + c3 * self.FFR_r * self.S[-1] + c4 * self.FFR_r**2 + c5 * self.S[-1]**2)
            self.ElPowerFeed.append((8.3140/(1013.25*0.082*3600*1000)) *(self.APdropFFR[-1] / EffPumpFFR) * (self.FFR_r) )
            self.ElPower.append( self.ElPowerFeed[-1] + self.ElPowerCooling[-1])
            self.ElEnergy.append( self.ElPower[-2] * (self.t[-1] - self.t[-2]))
            self.AccElEnergy.append(self.ElEnergy[-1] + self.AccElEnergy[-1])
            self.SEEC.append(self.AccElEnergy[-1] / (self.AccVd[-1] / 1000))
            

        
        self.output = np.array([[i for i in range(len(self.STEC))], self.tminute, self.V, self.AccVd, self.S, self.PFlux, self.R, self.ThEnergy, self.CEnergy])
        self.df = pd.DataFrame(data=self.output,  index=['Step',                                                
                                                          'Operation time (min)',
                                                          'Batch volume (L)',
                                                          'Accumulated discharge volume (L)',
                                                          'Brine salinity (g/L)',
                                                          'Permeate flux (kg/hr/m2)',
                                                          'Recovery rate (%)',
                                                          'Thermal energy (Wh-th)',
                                                          'Cooling energy (Wh-th)',])#,
                                # columns = [ str(i) for i in range(len(self.STEC))])         
        
        self.num_modules = math.ceil(self.Capacity *1000 / (self.AccVd[-1] / self.t[-1] * 24) )
        self.ave_stec = sum(self.STEC)/len(self.STEC)
        self.PFlux_avg= sum(self.PFlux) / len(self.PFlux)
        self.df = self.df.round(decimals = 1)
        self.df.to_csv(cfg.sam_results_dir/'MDB_output.csv')
        self.P_req = self.STEC[-1] * self.Capacity / 24   # kW
        # self.df.to_csv('D:/PhD/DOE/DOE_CSP_PROJECT/SAM_flatJSON/results/MDB_output.csv')
        
        self.design_output = []
        self.design_output.append({'Name':'Selected module size','Value':self.Area,'Unit':'m2'})
        self.design_output.append({'Name':'Number of modules required','Value':self.num_modules,'Unit':''})
        self.design_output.append({'Name':'Maximum potential recovery rate','Value':self.RRf,'Unit':'%'})  
        self.design_output.append({'Name':'Actual recovery rate','Value':self.R[-1],'Unit':'%'})    
        self.design_output.append({'Name':'Brine concentration','Value':self.Sf,'Unit':'g/L'})      
        # self.design_output.append({'Name':'Total processing time for one batch volume','Value':self.t[-1],'Unit':'h'})
        # self.design_output.append({'Name':'Permeate flow volume for each batch volume','Value':self.Vd[-1],'Unit':'L'})
        self.design_output.append({'Name':'Thermal power requirement','Value': self.P_req / 1000 ,'Unit':'MW(th)'})
        self.design_output.append({'Name':'Specific thermal power consumption','Value':self.STEC[-1],'Unit':'kWh(th)/m3'})
        self.design_output.append({'Name':'Specific electrical energy consumption','Value': self.SEEC[-1],'Unit':'kWh(e)/m3'})
        self.design_output.append({'Name':'Gained output ratio','Value':self.GOR[-1],'Unit':'kJ/kJ'})
        if ( k == 7 and self.Sf > 175.3):
            self.design_output.append({'Name':'    Note','Value':"Since the final brine salinity > 175.3 g/L in module AS7C1.5L(268), the model includes feed salinity as the only input, and closed cooling system will be applied.",'Unit':''})            
        if ( k == 26 and self.Sf > 140.2):
            self.design_output.append({'Name':'    Note','Value':"Since the final brine salinity > 140.2 g/L in module AS26C2.7L(373), the model includes feed salinity as the only input, and closed cooling system will be applied.",'Unit':''})            
        # print(self.PFlux_avg)
                
        
        return self.design_output
                
    def VAGMD_Models_NaCl(self, TEI_r, FFR_r, TCI_r, Sgl_r, k, Ttank):
        a1 = 0.983930048493388
        a2 = -4.8359231959954E-04
        S_r = a1 * Sgl_r + a2 * Sgl_r**2             
        FullModels_CoderVars =[ [ 1, TEI_r, TEI_r**2],
                                [ 1, FFR_r, FFR_r**2],
                                [ 1, TCI_r, TCI_r**2],
                                [ 1,   S_r,   S_r**2] ]

        matfile = loadmat(self.base_path /'DesalinationModels'/'VAGMD_batch'/'VAGMD_Models_NaCl.mat')
        # matfile = loadmat('D:/PhD/DOE/DOE_CSP_PROJECT/DesalinationModels/VAGMD_batch/VAGMD_Models_NaCl.mat')
        
        FullModels_Coder  = matfile['FullModels_Coder'].transpose().tolist()
                
        if k == 7:
            A = 7.2
            self.Area = 7.2
            if self.Sf > 175.3:
                FullModel_PFlux268 = matfile['FullModel_PFlux268_high'].transpose().tolist()[0]        
                FullModel_TCO268 = matfile['FullModel_TCO268_high'].transpose().tolist()[0]
                FullModel_TEO268 = matfile['FullModel_TEO268_high'].transpose().tolist()[0]                
                
                TEI_c = 0
                FFR_c = 0
                TCI_c = 0
                S_c = S_r

                FullModels_VarsPFlux268 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                PFlux = np.dot(FullModel_PFlux268, FullModels_VarsPFlux268)
                
                FullModels_VarsTCO268 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, FFR_c**2, S_c**2, FFR_c**3]
                TCO   = np.dot(FullModel_TCO268, FullModels_VarsTCO268)
            
                FullModels_VarsTEO268 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                TEO   = np.dot(FullModel_TEO268, FullModels_VarsTEO268)                
                
                
            else:
                FullModel_PFlux268 = matfile['FullModel_PFlux268_low'].transpose().tolist()[0]      
                FullModel_TCO268 = matfile['FullModel_TCO268_low'].transpose().tolist()[0]
                FullModel_TEO268 = matfile['FullModel_TEO268_low'].transpose().tolist()[0]
                
                TEI_c = np.dot(FullModels_CoderVars[0], FullModels_Coder[0])
                FFR_c = np.dot(FullModels_CoderVars[1], FullModels_Coder[1])
                TCI_c = np.dot(FullModels_CoderVars[2], FullModels_Coder[2])
                S_c   = np.dot(FullModels_CoderVars[3], FullModels_Coder[3])
    
                FullModels_VarsPFlux268 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                PFlux = np.dot(FullModel_PFlux268, FullModels_VarsPFlux268)
                
                FullModels_VarsTCO268 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, FFR_c**2, S_c**2, FFR_c**3]
                TCO   = np.dot(FullModel_TCO268, FullModels_VarsTCO268)
            
                FullModels_VarsTEO268 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                TEO   = np.dot(FullModel_TEO268, FullModels_VarsTEO268)
        
        elif k == 26:
            A = 25.92
            self.Area = 25.92
            if self.Sf > 140.2:
                FullModel_PFlux373 = matfile['FullModel_PFlux373_high'].transpose().tolist()[0]
                FullModel_TCO373   = matfile['FullModel_TCO373_high'].transpose().tolist()[0]
                FullModel_TEO373   = matfile['FullModel_TEO373_high'].transpose().tolist()[0]                

                TEI_c = 0
                FFR_c = 0
                TCI_c = 0
                S_c = S_r

                FullModels_VarsPFlux373 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                PFlux = np.dot(FullModel_PFlux373, FullModels_VarsPFlux373) 
            
                FullModels_VarsTCO373 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                TCO   = np.dot(FullModel_TCO373, FullModels_VarsTCO373) 
                
                FullModels_VarsTEO373 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                TEO   = np.dot(FullModel_TEO373, FullModels_VarsTEO373)                
                
            elif self.Sf <= 140.2 and Sgl_r > 105 and Sgl_r <= 145.2:                
                FullModel_PFlux373 = matfile['FullModel_PFlux373_low'].transpose().tolist()[0]
                FullModel_TCO373   = matfile['FullModel_TCO373_low'].transpose().tolist()[0]
                FullModel_TEO373   = matfile['FullModel_TEO373_low'].transpose().tolist()[0]
                
                TEI_c = np.dot(FullModels_CoderVars[0], FullModels_Coder[4])
                FFR_c = np.dot(FullModels_CoderVars[1], FullModels_Coder[5])
                TCI_c = np.dot(FullModels_CoderVars[2], FullModels_Coder[6])
                S_c   = np.dot(FullModels_CoderVars[3], FullModels_Coder[7])  
                
                FullModels_VarsPFlux373 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                PFlux = np.dot(FullModel_PFlux373, FullModels_VarsPFlux373) 
            
                FullModels_VarsTCO373 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                TCO   = np.dot(FullModel_TCO373, FullModels_VarsTCO373) 
                
                FullModels_VarsTEO373 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                TEO   = np.dot(FullModel_TEO373, FullModels_VarsTEO373)
            
            else:
                FullModel_PFlux373 = matfile['FullModel_PFlux373_verylow'].transpose().tolist()[0]
                FullModel_TCO373   = matfile['FullModel_TCO373_verylow'].transpose().tolist()[0]
                FullModel_TEO373   = matfile['FullModel_TEO373_verylow'].transpose().tolist()[0]
                
                TEI_c = np.dot(FullModels_CoderVars[0], FullModels_Coder[4])
                FFR_c = np.dot(FullModels_CoderVars[1], FullModels_Coder[5])
                TCI_c = np.dot(FullModels_CoderVars[2], FullModels_Coder[6])
                S_c   = np.dot(FullModels_CoderVars[3], FullModels_Coder[7])  
                
                FullModels_VarsPFlux373 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                PFlux = np.dot(FullModel_PFlux373, FullModels_VarsPFlux373) 
            
                FullModels_VarsTCO373 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                TCO   = np.dot(FullModel_TCO373, FullModels_VarsTCO373) 
                
                FullModels_VarsTEO373 =[ 1, TEI_c, FFR_c, TCI_c, S_c, FFR_c*TEI_c, TCI_c*TEI_c, S_c*TEI_c, FFR_c*TCI_c, FFR_c*S_c, S_c*TCI_c, TEI_c**2, FFR_c**2, TCI_c**2, S_c**2]
                TEO   = np.dot(FullModel_TEO373, FullModels_VarsTEO373)                
            
            
            
        P = 101325 #% [Pa].
        nullS = 0 #% [g/kg].
        RhoF = SW_Density(TEI_r,'c',S_r,'ppt',P,'pa') #% [kg/m3].
        CpF = SW_SpcHeat(TEI_r,'c',S_r,'ppt',P,'pa') #% [J/kg/ºC].
        RhoP = SW_Density(((TEI_r + TCI_r) / 2),'c',nullS,'ppt',P,'pa') # % [kg/m3].
        AHvP = SW_LatentHeat(((TEI_r + TCI_r) / 2),'c',nullS,'ppt') #% [J/kg].  
        RhoC = SW_Density(((TCI_r + Ttank ) / 2), 'c', nullS, 'ppt', P, 'pa') # [kg/m3]
        CpC = SW_SpcHeat((TCI_r + Ttank ) /2,'c',S_r,'ppt',P,'pa') #% [J/kg/ºC].
        # Permeate flow rate (kg/h)
        PFR = PFlux * A
        
        # Log mean temp difference (C)
        ATml = ((TEI_r - TCO) - (TEO - TCI_r )) / (math.log((TEI_r - TCO)/(TEO - TCI_r)))
        
        # Thermal power  (kW(th))
        ThPower = (FFR_r * CpF * (TEI_r - TCO)) * (RhoF / 1000 / 3600 / 1000)
        
        # STEC (kWh(th)/m3)
        STEC = ThPower / PFR * 1000
        
        # GOR 
        GOR = PFR * AHvP * RhoP / ThPower / 3600 / 1000 / 1000
        
        # return  0  , 1  , 2  , 3   , 4  , 5   , 6  , 7   , 8   , 9, 10  , 11     ,12   , 13
        return [PFlux, TCO, TEO, RhoF, CpF, RhoC, CpC, RhoP, AHvP, A, ATml, ThPower, STEC, GOR]
    
    
    def simulation(self, gen, storage):
        self.thermal_load = self.P_req # kWh per hour
        self.max_prod = self.AccVd[-1] / self.t[-1] /1000 * self.num_modules # m3/h
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
        # print(self.thermal_load)

        simu_output.append({'Name':'Water production','Value':prod,'Unit':'m3'})
        simu_output.append({'Name':'Storage status','Value':storage_status,'Unit':'kWh'})
        simu_output.append({'Name':'Storage Capacity','Value':self.storage_cap,'Unit':'kWh'})
        simu_output.append({'Name':'Fossil fuel usage','Value':fuel,'Unit':'kWh'})
        simu_output.append({'Name':'Total water production','Value':sum(prod),'Unit':'m3'})
        simu_output.append({'Name':'Monthly water production','Value': Monthly_prod,'Unit':'m3'})
        simu_output.append({'Name':'Total fossil fuel usage','Value':sum(fuel),'Unit':'kWh'})
        simu_output.append({'Name':'Percentage of fossil fuel consumption','Value':sum(fuel)/sum(energy_consumption)*100,'Unit':'%'}) 
        simu_output.append({'Name':'Curtailed solar thermal energy','Value':(sum(gen) - sum(load)) / 1000000 ,'Unit':'GWh'})   
        simu_output.append({'Name':'Percentage of curtailed energy','Value':(sum(gen) - sum(load)) / sum(gen) * 100 ,'Unit':'%'})
        # simu_output.append({'Name':'Dataframe','Value':self.json_df,'Unit':''})        
        # Add brine volume and concentration (using 100% rejection(make it a variable))
        
        return simu_output
    