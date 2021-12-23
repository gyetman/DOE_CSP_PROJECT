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
import numpy as np
#%%
class RO(object):
#
    def __init__(self,
    ###### (soon to be)JSON Inputs (Inputs available in GUI for user to modify)
                # Fluid properties
                FeedC_r=32,                # Feed TDS, g/L or parts per thousand
                T=25,            # Feedwater Temperature [C]
                #Fossil_f = 0.8 , # Fossil fuel fraction 
                stage = 1, # Number of stages
    
                # CP=1.1,              # Concentration polarization factor
    
                #Pump and ERD Parameters
                nERD=0.95,            # Energy recovery device efficiency
                nBP=0.8,
                nHP=0.8,
                nFP=0.8,
    
    
                #RO Plant Design Specifications
                nominal_daily_cap_tmp=1000,
                Nel1=None,              #number elements per vessel in stage 1
                R1=40,               #Desired overall recovery rate
                R2 = 83.3,          # 2nd stage recovery rate
                R3 = 90,            # 3rd stage recovery rate
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
                Pdropmax=0.6895,     #maximum pressure drop per membrane element (bar)
                Pfp=1    ,            # Pressure of intake feed pumps
                Tmax = 318.15,
                minQb = 2.7,
                maxQf = 17,
                Fossil_f = 1,
                
                # Booleans
                has_erd = 1, # include erd with booster pump
                is_first_stage = True, # include intake/feed pump powr requirement if first stage
                pretreat_power = 1  # kWh/m3 assumed for pretreatment
                
                ):
        self.nERD=nERD
        self.nBP=nBP
        self.nHP=nHP
        self.nFP=nFP
        self.nominal_daily_cap_tmp=nominal_daily_cap_tmp
        self.Nel1=Nel1
        self.R1=R1/100
        self.Cf=FeedC_r  
        self.Pfp=Pfp
        self.T=T 
        self.Am1=Am1
        self.Qpnom1=Qpnom1 
        self.Ptest1 = Ptest1
        self.SR1 = SR1
        self.Rt1 = Rt1
        self.Ctest1 = Ctest1
        self.Pdropmax = Pdropmax
        self.maxQf = maxQf
        self.Fossil_f = Fossil_f
        
        self.has_erd = True if has_erd == 1 else False
        self.is_first_stage = is_first_stage
        self.pretreat_power = pretreat_power
        self.stage = stage
        self.R2 = R2/100
        self.R3 = R3/100
    
    def RODesign(self):
        if self.stage == 1:
            self.case = self.Base_Unit(
                    FeedC_r=self.Cf,    
                    T=self.T , 
                    #Pump and ERD Parameters
                    nERD=self.nERD,
                    nBP=self.nBP,
                    nHP=self.nHP,
                    nFP=self.nFP,
                    #RO Plant Design Specifications
                    nominal_daily_cap_tmp=self.nominal_daily_cap_tmp,
                    Nel1=self.Nel1,
                    R1=self.R1,               #Desired overall recovery rate
                    # RO Membrane Property Inputs: 
                    #load in from a table of membrane types w/properties or enter manually.
                    # Using default values here based on manufacturer's datasheet for seawater RO membrane element: SWC4B MAX
                    Qpnom1=self.Qpnom1 ,      #nominal permeate production per membrane element (m3/hr)
                    Am1=self.Am1,            #membrane area per membrane element (m^2) 
                    Ptest1=self.Ptest1,         #Applied test pressure for each mem element
                    Ctest1=self.Ctest1,           #membrane manufacturer's test feed salinity (TDS) for each element (parts per thousand)
                    SR1=self.SR1,            #rated salt rejection of each element (%)
                    Rt1=self.Rt1,              #Test recovery rate for each element
                    Pdropmax=self.Pdropmax,     #maximum pressure drop per membrane element (bar)
                    Pfp=self.Pfp    ,     
                    maxQf = self.maxQf,
                    Fossil_f = self.Fossil_f,
                    # Booleans
                    has_erd = self.has_erd, # include erd with booster pump
                    is_first_stage = self.is_first_stage, # include intake/feed pump powr requirement if first stage
                    pretreat_power = self.pretreat_power  # kWh/m3 assumed for pretreatment)
                    )
            self.case.Unit_Design()
            self.PowerTotal = self.case.PowerTotal    
            self.SEC = self.case.SEC
            self.total_num_modules = self.case.num_modules
            design_output = []
            design_output.append({'Name':'Actual capacity of the system','Value':self.case.nominal_daily_cap,'Unit':'m3/day'})
            design_output.append({'Name':'Estimated EPC cost','Value':self.case.EPC ,'Unit':'$ per m3/day'})            
            design_output.append({'Name':'Final permeate salinity','Value':self.case.Cp * 1000,'Unit':'mg/L'})            
            design_output.append({'Name':'Number of vessels','Value':self.case.NV1,'Unit':''})
            design_output.append({'Name':'Number of elements per vessel','Value':self.case.Nel1,'Unit':''})
            design_output.append({'Name':'Brine concentration','Value':self.case.RO_brine_salinity,'Unit':'g/L'})
        #            design_output.append({'Name':'Permeate flow rate','Value':self.F * self.num_modules /1000 *24,'Unit':'m3/day'})    
            design_output.append({'Name':'Electric energy requirement','Value':self.case.PowerTotal,'Unit':'kW(e)'})
            design_output.append({'Name':'Specific energy consumption','Value':self.case.SEC,'Unit':'kWh(e)/m3'})
        #            design_output.append({'Name':'Gained output ratio','Value':self.GOR,'Unit':''})
            return design_output
        
        if self.stage == 2:
            self.case = self.Base_Unit(
                    FeedC_r=self.Cf,    
                    T=self.T, 
                    #Pump and ERD Parameters
                    nERD=self.nERD,
                    nBP=self.nBP,
                    nHP=self.nHP,
                    nFP=self.nFP,
                    #RO Plant Design Specifications
                    nominal_daily_cap_tmp=self.nominal_daily_cap_tmp / self.R2,
                    Nel1=self.Nel1,
                    R1=self.R1,               #Desired overall recovery rate
                    # RO Membrane Property Inputs: 
                    #load in from a table of membrane types w/properties or enter manually.
                    # Using default values here based on manufacturer's datasheet for seawater RO membrane element: SWC4B MAX
                    Qpnom1=self.Qpnom1,      #nominal permeate production per membrane element (m3/hr)
                    Am1=self.Am1,            #membrane area per membrane element (m^2) 
                    Ptest1=self.Ptest1,         #Applied test pressure for each mem element
                    Ctest1=self.Ctest1,           #membrane manufacturer's test feed salinity (TDS) for each element (parts per thousand)
                    SR1=self.SR1,            #rated salt rejection of each element (%)
                    Rt1=self.Rt1,              #Test recovery rate for each element
                    Pdropmax=self.Pdropmax,     #maximum pressure drop per membrane element (bar)
                    Pfp=self.Pfp    ,     
                    maxQf = self.maxQf,
                    Fossil_f = self.Fossil_f,
                    # Booleans
                    has_erd = self.has_erd, # include erd with booster pump
                    is_first_stage = self.is_first_stage, # include intake/feed pump powr requirement if first stage
                    pretreat_power = self.pretreat_power  # kWh/m3 assumed for pretreatment)
                    )
            self.case.Unit_Design()
            self.case2 = self.Base_Unit(
                    FeedC_r=self.case.Cp,    
                    T=self.T, 
                    #Pump and ERD Parameters
                    nERD=self.nERD,
                    nBP=self.nBP,
                    nHP=self.nHP,
                    nFP=self.nFP,
                    #RO Plant Design Specifications
                    nominal_daily_cap_tmp=self.nominal_daily_cap_tmp,
                    Nel1=self.Nel1,
                    R1=self.R2,               #Desired overall recovery rate
                    # RO Membrane Property Inputs: 
                    #load in from a table of membrane types w/properties or enter manually.
                    # Using default values here based on manufacturer's datasheet for seawater RO membrane element: SWC4B MAX
                    Qpnom1=self.Qpnom1,      #nominal permeate production per membrane element (m3/hr)
                    Am1=self.Am1,            #membrane area per membrane element (m^2) 
                    Ptest1=self.Ptest1,         #Applied test pressure for each mem element
                    Ctest1=self.Ctest1,           #membrane manufacturer's test feed salinity (TDS) for each element (parts per thousand)
                    SR1=self.SR1,            #rated salt rejection of each element (%)
                    Rt1=self.Rt1,              #Test recovery rate for each element
                    Pdropmax=self.Pdropmax,     #maximum pressure drop per membrane element (bar)
                    Pfp=self.Pfp    ,     
                    maxQf = self.maxQf,
                    Fossil_f = self.Fossil_f,
                    # Booleans
                    has_erd = self.has_erd, # include erd with booster pump
                    is_first_stage = False, # include intake/feed pump powr requirement if first stage
                    pretreat_power = 0  # kWh/m3 assumed for pretreatment)
                    )
            self.case2.Unit_Design()
                        
            self.PowerTotal = self.case.PowerTotal + self.case2.PowerTotal    
            # print('SEC', self.case.SEC, self.case2.SEC, self.case.nominal_daily_cap_tmp, self.case2.nominal_daily_cap_tmp)
            self.SEC = (self.case.SEC * self.case.nominal_daily_cap_tmp + self.case2.SEC * self.case2.nominal_daily_cap_tmp)  / (self.nominal_daily_cap_tmp )
            self.total_num_modules = self.case.num_modules + self.case2.num_modules 
            design_output = []
            design_output.append({'Name':'Actual capacity of the system','Value':self.case2.nominal_daily_cap,'Unit':'m3/day'})
            design_output.append({'Name':'Estimated EPC cost of the first pass','Value':self.case.EPC ,'Unit':'$ per m3/day'}) 
            design_output.append({'Name':'Estimated EPC cost of the second pass','Value':self.case2.EPC ,'Unit':'$ per m3/day'}) 
            design_output.append({'Name':'Pass 1 permeate salinity','Value':self.case.Cp * 1000,'Unit':'mg/L'})   
            design_output.append({'Name':'Final permeate salinity','Value':self.case2.Cp * 1000,'Unit':'mg/L'})            
            design_output.append({'Name':'Pass 1: Number of vessels','Value':self.case.NV1,'Unit':''})
            design_output.append({'Name':'Pass 2: Number of vessels','Value':self.case2.NV1,'Unit':''})
            design_output.append({'Name':'Pass 1:Number of elements per vessel','Value':self.case.Nel1,'Unit':''})
            design_output.append({'Name':'Pass 2:Number of elements per vessel','Value':self.case2.Nel1,'Unit':''})
            design_output.append({'Name':'Pass 1:Brine concentration','Value':self.case.RO_brine_salinity,'Unit':'g/L'})
            design_output.append({'Name':'Pass 2:Brine concentration','Value':self.case2.RO_brine_salinity,'Unit':'g/L'})  
            design_output.append({'Name':'Pass 1:Electric energy requirement','Value':self.case.PowerTotal,'Unit':'kW(e)'})
            design_output.append({'Name':'Pass 2:Electric energy requirement','Value':self.case2.PowerTotal,'Unit':'kW(e)'})
            design_output.append({'Name':'Specific energy consumption','Value':self.SEC,'Unit':'kWh(e)/m3'})

            return design_output        

        if self.stage == 3:
            self.case = self.Base_Unit(
                    FeedC_r=self.Cf,    
                    T=self.T, 
                    #Pump and ERD Parameters
                    nERD=self.nERD,
                    nBP=self.nBP,
                    nHP=self.nHP,
                    nFP=self.nFP,
                    #RO Plant Design Specifications
                    nominal_daily_cap_tmp=self.nominal_daily_cap_tmp / self.R2 / self.R3,
                    Nel1=self.Nel1,
                    R1=self.R1,               #Desired overall recovery rate
                    # RO Membrane Property Inputs: 
                    #load in from a table of membrane types w/properties or enter manually.
                    # Using default values here based on manufacturer's datasheet for seawater RO membrane element: SWC4B MAX
                    Qpnom1=self.Qpnom1,      #nominal permeate production per membrane element (m3/hr)
                    Am1=self.Am1,            #membrane area per membrane element (m^2) 
                    Ptest1=self.Ptest1,         #Applied test pressure for each mem element
                    Ctest1=self.Ctest1,           #membrane manufacturer's test feed salinity (TDS) for each element (parts per thousand)
                    SR1=self.SR1,            #rated salt rejection of each element (%)
                    Rt1=self.Rt1,              #Test recovery rate for each element
                    Pdropmax=self.Pdropmax,     #maximum pressure drop per membrane element (bar)
                    Pfp=self.Pfp    ,     
                    maxQf = self.maxQf,
                    Fossil_f = self.Fossil_f,
                    # Booleans
                    has_erd = self.has_erd, # include erd with booster pump
                    is_first_stage = self.is_first_stage, # include intake/feed pump powr requirement if first stage
                    pretreat_power = self.pretreat_power  # kWh/m3 assumed for pretreatment)
                    )
            self.case.Unit_Design()
            self.case2 = self.Base_Unit(
                    FeedC_r=self.case.Cp,    
                    T=self.T , 
                    #Pump and ERD Parameters
                    nERD=self.nERD,
                    nBP=self.nBP,
                    nHP=self.nHP,
                    nFP=self.nFP,
                    #RO Plant Design Specifications
                    nominal_daily_cap_tmp=self.nominal_daily_cap_tmp / self.R3,
                    Nel1=self.Nel1,
                    R1=self.R2,               #Desired overall recovery rate
                    # RO Membrane Property Inputs: 
                    #load in from a table of membrane types w/properties or enter manually.
                    # Using default values here based on manufacturer's datasheet for seawater RO membrane element: SWC4B MAX
                    Qpnom1=self.Qpnom1 ,      #nominal permeate production per membrane element (m3/hr)
                    Am1=self.Am1,            #membrane area per membrane element (m^2) 
                    Ptest1=self.Ptest1,         #Applied test pressure for each mem element
                    Ctest1=self.Ctest1,           #membrane manufacturer's test feed salinity (TDS) for each element (parts per thousand)
                    SR1=self.SR1,            #rated salt rejection of each element (%)
                    Rt1=self.Rt1,              #Test recovery rate for each element
                    Pdropmax=self.Pdropmax,     #maximum pressure drop per membrane element (bar)
                    Pfp=self.Pfp    ,     
                    maxQf = self.maxQf,
                    Fossil_f = self.Fossil_f,
                    # Booleans
                    has_erd = self.has_erd, # include erd with booster pump
                    is_first_stage = False, # include intake/feed pump powr requirement if first stage
                    pretreat_power = 0  # kWh/m3 assumed for pretreatment)
                    )
            self.case2.Unit_Design()
            self.case3 = self.Base_Unit(
                    FeedC_r=self.case2.Cp,    
                    T=self.T , 
                    #Pump and ERD Parameters
                    nERD=self.nERD,
                    nBP=self.nBP,
                    nHP=self.nHP,
                    nFP=self.nFP,
                    #RO Plant Design Specifications
                    nominal_daily_cap_tmp=self.nominal_daily_cap_tmp ,
                    Nel1=self.Nel1,
                    R1=self.R3,               #Desired overall recovery rate
                    # RO Membrane Property Inputs: 
                    #load in from a table of membrane types w/properties or enter manually.
                    # Using default values here based on manufacturer's datasheet for seawater RO membrane element: SWC4B MAX
                    Qpnom1=self.Qpnom1 ,      #nominal permeate production per membrane element (m3/hr)
                    Am1=self.Am1,            #membrane area per membrane element (m^2) 
                    Ptest1=self.Ptest1,         #Applied test pressure for each mem element
                    Ctest1=self.Ctest1,           #membrane manufacturer's test feed salinity (TDS) for each element (parts per thousand)
                    SR1=self.SR1,            #rated salt rejection of each element (%)
                    Rt1=self.Rt1,              #Test recovery rate for each element
                    Pdropmax=self.Pdropmax,     #maximum pressure drop per membrane element (bar)
                    Pfp=self.Pfp    ,     
                    maxQf = self.maxQf,
                    Fossil_f = self.Fossil_f,
                    # Booleans
                    has_erd = self.has_erd, # include erd with booster pump
                    is_first_stage = False, # include intake/feed pump powr requirement if first stage
                    pretreat_power = 0  # kWh/m3 assumed for pretreatment)
                    )
            self.case3.Unit_Design()                        
            self.PowerTotal = self.case.PowerTotal + self.case2.PowerTotal + self.case3.PowerTotal
            self.SEC = self.PowerTotal / (self.nominal_daily_cap_tmp / 24)
            self.total_num_modules = self.case.num_modules + self.case2.num_modules + self.case3.num_modules 
            
            design_output = []
            design_output.append({'Name':'Actual capacity of the system','Value':self.case3.nominal_daily_cap,'Unit':'m3/day'})
            design_output.append({'Name':'Estimated EPC cost of the first pass','Value':self.case.EPC ,'Unit':'$ per m3/day'}) 
            design_output.append({'Name':'Estimated EPC cost of the second pass','Value':self.case2.EPC ,'Unit':'$ per m3/day'}) 
            design_output.append({'Name':'Estimated EPC cost of the third pass','Value':self.case3.EPC ,'Unit':'$ per m3/day'}) 
            design_output.append({'Name':'Pass 1 permeate salinity','Value':self.case.Cp * 1000,'Unit':'mg/L'})    
            design_output.append({'Name':'Pass 2 permeate salinity','Value':self.case2.Cp * 1000,'Unit':'mg/L'})    
            design_output.append({'Name':'Final permeate salinity','Value':self.case3.Cp * 1000,'Unit':'mg/L'})            
            design_output.append({'Name':'Pass 1: Number of vessels','Value':self.case.NV1,'Unit':''})
            design_output.append({'Name':'Pass 2: Number of vessels','Value':self.case2.NV1,'Unit':''})
            design_output.append({'Name':'Pass 3: Number of vessels','Value':self.case3.NV1,'Unit':''})
            design_output.append({'Name':'Pass 1:Number of elements per vessel','Value':self.case.Nel1,'Unit':''})
            design_output.append({'Name':'Pass 2:Number of elements per vessel','Value':self.case2.Nel1,'Unit':''})
            design_output.append({'Name':'Pass 3:Number of elements per vessel','Value':self.case3.Nel1,'Unit':''})
            design_output.append({'Name':'Pass 1:Brine concentration','Value':self.case.RO_brine_salinity,'Unit':'g/L'})
            design_output.append({'Name':'Pass 2:Brine concentration','Value':self.case2.RO_brine_salinity,'Unit':'g/L'}) 
            design_output.append({'Name':'Pass 3:Brine concentration','Value':self.case3.RO_brine_salinity*1000,'Unit':'mg/L'})  
            design_output.append({'Name':'Pass 1:Electric energy requirement','Value':self.case.PowerTotal,'Unit':'kW(e)'})
            design_output.append({'Name':'Pass 2:Electric energy requirement','Value':self.case2.PowerTotal,'Unit':'kW(e)'})
            design_output.append({'Name':'Pass 3:Electric energy requirement','Value':self.case3.PowerTotal,'Unit':'kW(e)'})
            design_output.append({'Name':'Specific energy consumption','Value':self.SEC,'Unit':'kWh(e)/m3'})

            return design_output        
                
        
    class Base_Unit(object):
        def __init__(self,
        ###### (soon to be)JSON Inputs (Inputs available in GUI for user to modify)
                    # Fluid properties
                    FeedC_r=32,                # Feed TDS, g/L or parts per thousand
                    T=25,            # Feedwater Temperature [C]
                    #Fossil_f = 0.8 , # Fossil fuel fraction 
                    stage = 1, # Number of stages
        
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
                    R2 = 0.833,          # 2nd stage recovery rate
                    R3 = 0.9,            # 3rd stage recovery rate
                    # RO Membrane Property Inputs: 
                    #load in from a table of membrane types w/properties or enter manually.
                    # Using default values here based on manufacturer's datasheet for seawater RO membrane element: SWC4B MAX
                    Qpnom1=27.3,      #nominal permeate production per membrane element (m3/hr)
                    Am1=40.8,            #membrane area per membrane element (m^2) 
                    Pmax1=82.7,          #Max pressure of membrane element (bar)
                    Ptest1=55.2,         #Applied test pressure for each mem element
                    Ctest1=32,           #membrane manufacturer's test feed salinity (TDS) for each element (parts per thousand)
                    SR1=99.8,            #rated salt rejection of each element (%)
                    Rt1=.1,              #Test recovery rate for each element
                    Pdropmax=0.6895,     #maximum pressure drop per membrane element (bar)
                    Pfp=1    ,            # Pressure of intake feed pumps
                    Tmax = 318.15,
                    minQb = 2.7,
                    maxQf = 17,
                    Fossil_f = 1,
                    
                    # Booleans
                    has_erd = True, # include erd with booster pump
                    is_first_stage = True, # include intake/feed pump powr requirement if first stage
                    pretreat_power = 1  # kWh/m3 assumed for pretreatment
                    
                    ):
            
        
        
            
            # self.CP=CP
            self.nERD=nERD
            self.nBP=nBP
            self.nHP=nHP
            self.nFP=nFP
            self.nominal_daily_cap_tmp=nominal_daily_cap_tmp
            self.Nel1=Nel1
            self.R1=R1
            self.Cf=FeedC_r  
            self.Pfp=Pfp
            self.T=T +273.15
            self.Am1=Am1
            self.Qpnom1=Qpnom1 /24
            self.Ptest1 = Ptest1
            self.SR1 = SR1
            self.Rt1 = Rt1
            self.Ctest1 = Ctest1
            self.Pdropmax = Pdropmax
            self.maxQf = maxQf
            self.Fossil_f = Fossil_f
            
            self.has_erd = has_erd
            self.is_first_stage = is_first_stage
            self.pretreat_power = pretreat_power
            self.stage = stage
            self.R2 = R2
            self.R3 = R3
        
        
        def Unit_Design(self):
            vhfactor =2
            MW_nacl = 58.443
            Ru = 0.0831
                        
            self.total_number_elements = ceil(self.nominal_daily_cap_tmp/self.Qpnom1/24)
            self.NV1_min=ceil(self.nominal_daily_cap_tmp/24/self.maxQf/self.R1)
            self.Nel1_max=ceil(self.total_number_elements/self.NV1_min)
            
            
            if self.Nel1 is None:
                self.Nel1= self.Nel1_max
                self.NV1 = self.NV1_min
    
            else:
                self.Nel1 = int(self.Nel1)
                self.NV1 = max(self.NV1_min, ceil(self.total_number_elements / self.Nel1))
                   
    
            self.nominal_daily_cap=self.Qpnom1*self.Nel1*self.NV1*24
            Rel = 1/6  # max recovery rate of membrane element
            Rel_avg = 1-(1-self.R1)**(1/self.Nel1)
            CPavg=exp(0.7*Rel_avg)
            self.CPb=exp(0.7*Rel)
            CPtest=exp(0.7*self.Rt1)
            self.Bs1=self.Qpnom1/self.Am1*(1-self.SR1/100)*self.Ctest1/(CPtest*self.Ctest1/(1-self.Rt1)-(1-self.SR1/100)*self.Ctest1)
            Posm1=vhfactor*Ru*self.T*CPtest/MW_nacl*self.Ctest1*(1-(1-self.SR1/100))/(1-self.Rt1)
            NDP1=self.Ptest1-Posm1
            self.A1=self.Qpnom1/(self.Am1*NDP1)
            self.Pd=self.Pdropmax*self.Nel1
            i_nel=cumprod(repmat((1-Rel),(self.Nel1-1),1))
            i_nel=insert(i_nel,0,1)
            self.R1_max=sum(Rel*(i_nel))
    
            self.Qp1=self.nominal_daily_cap_tmp/24
            NDP1=self.Qp1/(self.Nel1*self.NV1*self.Am1*self.A1)
            self.Posm_f=vhfactor*Ru*self.T/MW_nacl*self.Cf
            self.Posm_b=vhfactor*Ru*self.T/MW_nacl*self.Cf/(1-self.R1)
            self.Posm_avgmem=CPavg*(self.Posm_f+self.Posm_b)*0.5
            Cm_avg=CPavg*(self.Cf+self.Cf/(1-self.R1))*0.5
            self.Cp=self.Bs1*Cm_avg*self.Nel1*self.NV1*self.Am1/self.Qp1
            self.Posm_perm=vhfactor*Ru*self.T/MW_nacl*self.Cp
            Pf1=NDP1 + self.Posm_avgmem + self.Pd*0.5 - self.Posm_perm
            # print(NDP1, self.Posm_avgmem, self.Pd, self.Posm_perm)
            self.Qf1=self.Qp1/self.R1
            self.Qb1=self.Qf1-self.Qp1
    
            self.Pf=Pf1
           
            
            # if(self.Qb1 > self.minQb*self.NV1) == 0:
            #     print("\nConcentrate flow rate is %s m3/h but should be greater than %s m3/h" % (self.Qb1,(2.7*self.NV1)))
    
            # if(self.Qf1 < self.maxQf*self.NV1)==0:
            #     print("\nFeed flow rate is %s m3/h but should be less than %s m3/h" % (self.Qf1, (17*self.NV1)))
            # if(self.Pf<=self.Pmax1)==0:
            #     print("\nFeed pressure is %s bar but should be less than %s bar" % (self.Pf, self.Pmax1))
            # if self.T>self.Tmax:
            #     print("\nFeed temperature is %s K but should be less than %s K" % (self.T, self.Tmax))
    
            if self.has_erd:
                self.Pb = Pf1 - self.Pd
                self.Pbp = Pf1 - self.nERD * self.Pb
                self.Qbp = self.Qb1
                self.Qhp = self.Qp1
                BP_power = self.Qbp * self.Pbp / self.nBP / 36
            else:
                BP_power=0
                self.Qhp = self.Qf1
    
            if self.is_first_stage:
                FP_power = self.Qf1 * self.Pfp / self.nFP / 36
    
            else:
                FP_power = 0
    
            HP_power=self.Qhp*Pf1/self.nHP/36
            PowerTotal=FP_power+HP_power+BP_power
        
            self.PowerRO=HP_power+BP_power
            # SEC is added 1 for pretreatment
            self.SEC=PowerTotal/self.Qp1 + self.pretreat_power
            
            self.SEC_RO=self.PowerRO/self.Qp1
            self.BP_power=BP_power
            self.HP_power=HP_power
            self.FP_power=FP_power
            self.PowerTotal=self.SEC * self.Qp1
            
            RO_brine = self.Qb1*24        
            RO_permeate = self.Qp1*24
            RO_feed = self.Qf1*24
            self.RO_brine_salinity = (self.Cf * RO_feed - self.Cp * RO_permeate)/ RO_brine
            # print('actual capacity ', self.nominal_daily_cap, '\noperating capacity',self.nominal_daily_cap_tmp )
            self.utilization_rate= self.nominal_daily_cap_tmp/self.nominal_daily_cap  
            self.num_modules = self.Nel1 * self.NV1
            
            if self.is_first_stage:
                self.EPC = int(3726.1 * self.nominal_daily_cap ** (-0.071))
            else:
                self.EPC = int(808.39 * self.nominal_daily_cap ** (-0.017))
            

    def simulation(self, gen, storage=None):
        # if not isinstance(gen,np.ndarray):
        #     count_hours= np.asarray(gen)>=self.PowerTotal
        # else:
        #     count_hours= gen>=self.PowerTotal

        # self.Qp_hourly_sim=np.zeros(8760)
        # self.Qp_hourly_sim=count_hours.reshape(1,-1)*repmat(self.Qp1,1,8760)
        # self.Qp_annual_total= np.sum(count_hours)*self.Qp1
        
        # self.Qp = self.Qp_hourly_sim.tolist()[0]
        
        # simu_output = []
        # simu_output.append({'Name':'Water production','Value': self.Qp,'Unit':'m3/h'})
        # simu_output.append({'Name':'Water production2','Value': self.Qp,'Unit':'m3/h'})
        # simu_output.append({'Name':'Annual total water production','Value':self.Qp_annual_total,'Unit':'m3/year'})
        
        
        self.thermal_load = self.PowerTotal # kWh
        self.max_prod = self.nominal_daily_cap_tmp / 24 # m3/h
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
        actual_load =  [0 for i in range(len(gen))]
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
            if max(0,load[i] / self.thermal_load) < self.Fossil_f:
                fuel[i] = self.thermal_load - load[i]
            
            actual_load[i] = max(0,load[i])
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
        simu_output.append({'Name':'Curtailed solar electric energy','Value':max(0, (sum(gen) - sum(load)) / 1000000) ,'Unit':'GWh'})   
        simu_output.append({'Name':'Percentage of curtailed energy','Value':max(0, (sum(gen) - sum(load))) / sum(gen) * 100 ,'Unit':'%'}) 
        
        return simu_output

#%% EXAMPLE
# gen=[100,110]*4380
# r = RO()
# r.RODesign()
# r.simulation(gen)
        


