# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 11:45:25 2019
Created from RO_Fixed_Load_procedural, Adam Atia
@author: zzrfl
"""


from numpy import array,cumprod,insert
from numpy.matlib import repmat
from math import ceil, exp
from warnings import warn

class RO(object):
#
    def __init__(self,
    ###### (soon to be)JSON Inputs (Inputs available in GUI for user to modify)
                # Fluid properties
                Cf=32,                # Feed TDS, g/L or parts per trillion
                T=25,            # Feedwater Temperature [C]
                #Fossil_f = 0.8 , # Fossil fuel fraction 
    
    
                # CP=1.1,              # Concentration polarization factor
    
                #Pump and ERD Parameters
                nERD=0.95,            # Energy recovery device efficiency
                nBP=0.8,
                nHP=0.8,
                nFP=0.8,
    
    
                #RO Plant Design Specifications
                nominal_daily_cap_tmp=1000,
                Nel1=8,              #number elements per vessel in stage 1
                R1=.4,               #Desired overall recovery rate
    
                # RO Membrane Property Inputs: 
                #load in from a table of membrane types w/properties or enter manually.
                # Using default values here based on manufacturer's datasheet for seawater RO membrane element: SWC4B MAX
                Qpnom1=27.3/24.0,      #nominal permeate production per membrane element (m3/hr)
                Am1=40.8,            #membrane area per membrane element (m^2) 
                Pmax1=82.7,          #Max pressure of membrane element (bar)
                Ptest1=55.2,         #Applied test pressure for each mem element
                Ctest1=32,           #membrane manufacturer's test feed salinity (TDS) for each element (parts per thousand)
                SR1=99.8,            #rated salt rejection of each element (%)
                Rt1=.1,              #Test recovery rate for each element
                Pdropmax=1,          #maximum pressure drop per membrane element (bar)
                Pfp=1    ,            # Pressure of intake feed pumps
                Tmax = 318.15,
                minQb = 2.7,
                maxQf = 17
                ):
    
        # self.CP=CP
        self.nERD=nERD
        self.nBP=nBP
        self.nHP=nHP
        self.nFP=nFP
        self.nominal_daily_cap_tmp=nominal_daily_cap_tmp
        self.Nel1=Nel1
        self.R1=R1
        self.Cf=Cf  
        self.Pfp=Pfp
        self.T=T +273.15
        self.Am1=Am1
        self.Qpnom1=Qpnom1
        self.Ptest1 = Ptest1
        self.SR1 = SR1
        self.Rt1 = Rt1
        self.Ctest1 = Ctest1
        self.Pdropmax = Pdropmax
        self.maxQf = maxQf

        
    def RODesign(self):
        vhfactor =2
        MW_nacl = 58.443
        Ru = 0.0831
        Rel = 1/6
        Rel_avg = 1-(1-self.R1)**(1/self.Nel1)
        CPavg=exp(0.7*Rel_avg)
        self.CPb=exp(0.7*Rel)
        CPtest=exp(0.7*self.Rt1)
        Bs1=self.Qpnom1/self.Am1*(1-self.SR1/100)*self.Ctest1/CPtest/(self.Ctest1/(1-self.Rt1)-(1-self.SR1/100)*self.Ctest1)
        Posm1=vhfactor*Ru*self.T*CPtest/MW_nacl*self.Ctest1*(1-(1-self.SR1/100))/(1-self.Rt1)
        NDP1=self.Ptest1-Posm1
        A1=self.Qpnom1/(self.Am1*NDP1)
        Pd=self.Pdropmax*self.Nel1
        i_nel=cumprod(repmat((1-Rel),(self.Nel1-1),1))
        i_nel=insert(i_nel,0,1)
        self.R1_max=sum(Rel*(i_nel))
        NV1=ceil(self.nominal_daily_cap_tmp/24/self.maxQf/self.R1)
        self.nominal_daily_cap=self.Qpnom1*self.Nel1*NV1*24
        self.Qp1=self.nominal_daily_cap_tmp/24
        NDP1=self.Qp1/(self.Nel1*NV1*self.Am1*A1)
        Posm_f=vhfactor*Ru*self.T/MW_nacl*self.Cf
        Posm_b=vhfactor*Ru*self.T/MW_nacl*self.Cf/(1-self.R1)
        Posm_avgmem=CPavg*(Posm_f+Posm_b)*0.5
        Cm_avg=CPavg*(self.Cf+self.Cf/(1-self.R1))*0.5
        self.Cp=Bs1*Cm_avg*self.Nel1*NV1*self.Am1/self.Qp1
        Posm_perm=vhfactor*Ru*self.T/MW_nacl*self.Cp
        Pf1=NDP1 + Posm_avgmem + Pd*0.5 - Posm_perm
        self.Pb=Pf1-Pd
        Pbp=Pf1-self.nERD*self.Pb
        self.NV1=NV1
    
        self.Qf1=self.Qp1/self.R1
        self.Qb1=self.Qf1-self.Qp1
        self.Qbp=self.Qb1
        self.Qhp=self.Qp1
        self.Pf=Pf1
        self.Pbp=Pbp
    
    # if(self.Qb1>minQb*NV1)==0:
    #     print("\nConcentrate flow rate is %s m3/h but should be greater than %s m3/h" % (self.Qb1,(2.7*NV1)))
        
    # if(Qf1<maxQf*NV1)==0:
    #     print("\nFeed flow rate is %s m3/h but should be less than %s m3/h" % (Qf1,(17*NV1)))
    # if(Pf1<=Pmax1)==0:
    #     print("\nFeed pressure is %s bar but should be less than %s bar" % (Pf1,(Pmax1)))
    # if T>Tmax:
    #     print("\nFeed temperature is %s K but should be less than %s K" % (T,(Tmax)))
    
    
        BP_power=self.Qbp*Pbp/self.nBP/36
        HP_power=self.Qhp*Pf1/self.nHP/36
        FP_power=self.Qf1*self.Pfp/self.nFP/36
        PowerTotal=FP_power+HP_power+BP_power
        self.PowerRO=HP_power+BP_power
        self.SEC=PowerTotal/self.Qp1
        self.SEC_RO=self.PowerRO/self.Qp1
        self.BP_power=BP_power
        self.HP_power=HP_power
        self.FP_power=FP_power
        self.PowerTotal=PowerTotal
        
        design_output = []
        design_output.append({'Name':'Permeate flow rate of the system','Value':self.Qp1,'Unit':'m3/h'})
    #            design_output.append({'Name':'Condenser outlet temperature','Value':self.TCO,'Unit':'oC'})
    #            design_output.append({'Name':'Permeate flow rate','Value':self.F * self.num_modules /1000 *24,'Unit':'m3/day'})    
    #            design_output.append({'Name':'Thermal power consumption','Value':self.ThPower * self.num_modules,'Unit':'kW(th)'})
    #            design_output.append({'Name':'Specific thermal power consumption','Value':self.STEC,'Unit':'kWh(th)/m3'})
    #            design_output.append({'Name':'Gained output ratio','Value':self.GOR,'Unit':''})
        return design_output

    def ROSimulation(self):
        return

#%%
test = RO()
r = test.RODesign()
        


