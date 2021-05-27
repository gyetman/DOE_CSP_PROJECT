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
        self.V0       = V0
        self.RR       = RR
        self.Fossil_f = Fossil_f        
      
        self.base_path = Path(__file__).resolve().parent.parent.parent.absolute()

    def design(self):
        Vdisch  = 3.2175 # (L)
        minS   = 35     # (g/L)       
        
        if self.module == 0:
            maxS = 175.3
            k = 7
            self.Area = self.Area_small
        else:
            maxS = 105
            k = 26
            self.Area = self.Area_big
        
        RRf   = 100 * (1 - self.FeedC_r/maxS) # Maximum value of final recovery ratio allowed
        maxRR = 100 * (1 - (minS/maxS))  # 

        if self.RR > RRf:
            raise Exception("The recovery rate must be below ", RRf, "%")
        
        
        self.Sf = self.FeedC_r / ( 1 - self.RR/100)  # Final feed salinity (g/L)  
       
        #  Calculate [PFlux, TCO, TEO, PFR, ATml, ThPower, STEC, GOR]
        #                 0,   1,   2,   3,    4,       5,    6,   7
        results = self.VAGMD_Models_NaCl(self.TEI_r, self.FFR_r, self.TCI_r, self.FeedC_r, k)
    
        # Initialize the time series
        self.t = [0]
        self.tminute = [0]
        self.V = [self.V0]
        self.Vd = [0]
        self.S = [self.FeedC_r]
        self.RR = [0]
        self.PFlux = [results[0]] # kg/h/m2
        self.PFR   = [results[3]] # kg/h
        self.TCO   = [results[1]]
        self.TEO   = [results[2]]    
        self.ATml  = [results[4]] 
        self.ThPower = [results[5]] # kW(th)
        t_next = Vdisch / self.PFR[0]
        self.Ttank = [(self.FFR_r * t_next * self.TEO[0] + self.V0 * self.TCI_r) / (self.V0 + self.FFR_r * t_next)] 
        self.ThEnergy = [0] # kW(th)
        self.AccThEnergy = [0]  # kW(th)
        self.CPower = [self.FFR_r / 3600 * 4180 * (self.Ttank[0] - self.TCI_r) / 1000]  # kW(th)
        self.CEnergy = [0] # kWh(th)
        self.AccCEnergy = [0] # kWh(th)
        self.GOR = [results[7]]
        self.STEC = [results[6]]
        
        # Complete the time series
        while self.S[-1] < self.Sf:
            self.t.append(self.t[-1]+t_next)
            self.tminute.append(self.t[-1]*60)
            
            self.V.append(self.V[-1] - Vdisch)
            self.Vd.append(self.Vd[-1] + Vdisch)
            self.S.append(self.V[-2]/self.V[-1]*self.S[-1])
            
            new_results = self.VAGMD_Models_NaCl(self.TEI_r, self.FFR_r, self.TCI_r, self.S[-1], k)
            self.PFlux.append(new_results[0])
            self.PFR.append(new_results[3])
            self.RR.append(100*(1-self.S[0]/self.S[-1]))
            self.TCO.append(new_results[1])
            self.TEO.append(new_results[2])            
            self.ATml.append(new_results[4])            
            self.ThPower.append(new_results[5])
            
            t_next = Vdisch / self.PFR[-1] 
            self.Ttank.append( (self.FFR_r * t_next * self.TEO[-1] + self.V[-1] * self.TCI_r) / (self.V[-1] + self.FFR_r * t_next))
            self.ThEnergy.append(self.ThPower[-1] * (self.t[-1]-self.t[-2]))
            self.AccThEnergy.append(self.ThEnergy[-1] + self.AccThEnergy[-1])
            self.CPower.append(self.FFR_r / 3600 * 4180 * (self.Ttank[-1] - self.TCI_r) / 1000)
            self.CEnergy.append(self.CPower[-1] * (self.t[-1] - self.t[-2]))
            self.AccCEnergy.append(self.CEnergy[-1] + self.AccCEnergy[-1])
            self.GOR.append(new_results[7])
            self.STEC.append(new_results[6])
        
        self.output = np.array([[i for i in range(len(self.STEC))], self.tminute, self.V, self.Vd, self.S, self.PFR, self.PFlux, self.RR, self.TCO, self.TEO, self.Ttank, self.ATml, self.ThPower, self.ThEnergy, self.AccThEnergy, self.CPower, self.CEnergy, self.AccCEnergy, self.GOR, self.STEC])

        self.df = pd.DataFrame(data=self.output,  index=['Step',                                                
                                                         'Operation time (min)',
                                                         'Batch volume (m3)',
                                                         'Discharged volume (m3)',
                                                         'Brine salinity (g/L)',
                                                         'Permeate flow rate (kg/hr)',
                                                         'Permeate flux (kg/hr/m2)',
                                                         'Recovery rate (%)',
                                                         'Condenser outlet temperature (oC)',
                                                         'Evaporator outlet temperature (oC)',
                                                         'Tank temperature (oC)',
                                                         'Log mean temp difference (oC)',
                                                         'Thermal power (kW-th)',
                                                         'Thermal energy (kWh-th)',
                                                         'Accumulated thermal energy (kWh-th)',
                                                         'Cooling power (kW-th)',
                                                         'Cooling energy (kWh-th)',
                                                         'Accumulated cooling energy (kWh-th)',
                                                         'GOR (kg/kg)',
                                                         'STEC (kWh-th/m3)'])#,
                               # columns = [ str(i) for i in range(len(self.STEC))])         
        
        self.num_modules = math.ceil(self.Capacity *1000 / (self.Vd[-1] / self.t[-1] * 24) )
        self.ave_stec = sum(self.STEC)/len(self.STEC)
        self.PFlux_avg= sum(self.PFlux) / len(self.PFlux)
        self.df = self.df.round(decimals = 1)
        self.df.to_csv(cfg.sam_results_dir/'MDB_output.csv')
        self.P_req = self.ave_stec * self.Capacity / 24   # kW
        # self.df.to_csv('D:/PhD/DOE/DOE_CSP_PROJECT/SAM_flatJSON/results/MDB_output.csv')
        
        self.design_output = []
        self.design_output.append({'Name':'Number of modules required','Value':self.num_modules,'Unit':''})
        self.design_output.append({'Name':'Maximum recovery rate allowed','Value':RRf,'Unit':'%'})  
        self.design_output.append({'Name':'Actual recovery rate','Value':self.RR[-1],'Unit':'%'})          
        self.design_output.append({'Name':'Total processing time for one batch volume','Value':self.t[-1],'Unit':'h'})
        self.design_output.append({'Name':'Permeate flow volume for each batch volume','Value':self.Vd[-1],'Unit':'L'})
        self.design_output.append({'Name':'Thermal power consumption','Value': self.P_req / 1000 ,'Unit':'MW(th)'})
        self.design_output.append({'Name':'Specific thermal power consumption','Value':self.ave_stec,'Unit':'kWh(th)/m3'})
        self.design_output.append({'Name':'Gained output ratio','Value':sum(self.GOR)/len(self.GOR),'Unit':''})
        
        
        return self.design_output
                
    def VAGMD_Models_NaCl(self, TEI_r, FFR_r, TCI_r, Sgl_r, k):
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
            FullModel_PFlux268 = matfile['FullModel_PFlux268'].transpose().tolist()[0]      
            FullModel_TCO268 = matfile['FullModel_TCO268'].transpose().tolist()[0]
            FullModel_TEO268 = matfile['FullModel_TEO268'].transpose().tolist()[0]
            
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
            FullModel_PFlux373 = matfile['FullModel_PFlux373'].transpose().tolist()[0]
            FullModel_TCO373   = matfile['FullModel_TCO373'].transpose().tolist()[0]
            FullModel_TEO373   = matfile['FullModel_TEO373'].transpose().tolist()[0]
            
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
        
        return [PFlux, TCO, TEO, PFR, ATml, ThPower, STEC, GOR]
    
    
    def simulation(self, gen, storage):
        self.thermal_load = sum(self.ThEnergy) / self.t[-1] * self.num_modules # kWh per hour
        self.max_prod = self.Vd[-1] / self.t[-1] /1000 * self.num_modules # m3/h
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
        # simu_output.append({'Name':'Dataframe','Value':self.json_df,'Unit':''})        
        # Add brine volume and concentration (using 100% rejection(make it a variable))
        
        return simu_output
    