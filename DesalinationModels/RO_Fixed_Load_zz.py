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

class RODesign(object):
#
    def __init__(self,
###### (soon to be)JSON Inputs (Inputs available in GUI for user to modify)
                # Fluid properties
                Cf=32,                # Feed TDS, g/L or parts per trillion
                T=298.15,            # Feedwater Temperature [Kelvin]


                # CP=1.1,              # Concentration polarization factor

                #Pump and ERD Parameters
                nERD=0.95,            # Energy recovery device efficiency
                nBP=0.8,
                nHP=0.8,
                nFP=0.8,


                #RO Plant Design Specifications
                nominal_daily_cap_tmp=550000,
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
        self.T=T
        self.Am1=Am1
        self.Qpnom1=Qpnom1
        vhfactor =2
        MW_nacl = 58.443
        Ru = 0.0831
        Rel = 1/6
        Rel_avg = 1-(1-R1)**(1/Nel1)
        CPavg=exp(0.7*Rel_avg)
        CPb=exp(0.7*Rel)
        CPtest=exp(0.7*Rt1)
        Bs1=Qpnom1/Am1*(1-SR1/100)*Ctest1/CPtest/(Ctest1/(1-Rt1)-(1-SR1/100)*Ctest1)
        Posm1=vhfactor*Ru*T*CPtest/MW_nacl*Ctest1*(1-(1-SR1/100))/(1-Rt1)
        NDP1=Ptest1-Posm1
        A1=Qpnom1/(Am1*NDP1)
        Pd=Pdropmax*Nel1
        i_nel=cumprod(repmat((1-Rel),(Nel1-1),1))
        i_nel=insert(i_nel,0,1)
        R1_max=sum(Rel*(i_nel))
        NV1=ceil(nominal_daily_cap_tmp/24/maxQf/R1)
        nominal_daily_cap=Qpnom1*Nel1*NV1*24
        self.Qp1=nominal_daily_cap_tmp/24
        NDP1=self.Qp1/(Nel1*NV1*Am1*A1)
        Posm_f=vhfactor*Ru*T/MW_nacl*Cf
        Posm_b=vhfactor*Ru*T/MW_nacl*Cf/(1-R1)
        Posm_avgmem=CPavg*(Posm_f+Posm_b)*0.5
        Cm_avg=CPavg*(Cf+Cf/(1-R1))*0.5
        self.Cp=Bs1*Cm_avg*Nel1*NV1*Am1/self.Qp1
        Posm_perm=vhfactor*Ru*T/MW_nacl*self.Cp
        Pf1=NDP1 + Posm_avgmem + Pd*0.5 - Posm_perm
        Pb1=Pf1-Pd
        Pbp=Pf1-nERD*Pb1
        self.NV1=NV1

        self.Qf1=self.Qp1/R1
        self.Qb1=self.Qf1-self.Qp1
        Qbp=self.Qb1
        Qhp=self.Qp1

        # if(self.Qb1>minQb*NV1)==0:
        #     print("\nConcentrate flow rate is %s m3/h but should be greater than %s m3/h" % (self.Qb1,(2.7*NV1)))
            
        # if(Qf1<maxQf*NV1)==0:
        #     print("\nFeed flow rate is %s m3/h but should be less than %s m3/h" % (Qf1,(17*NV1)))
        # if(Pf1<=Pmax1)==0:
        #     print("\nFeed pressure is %s bar but should be less than %s bar" % (Pf1,(Pmax1)))
        # if T>Tmax:
        #     print("\nFeed temperature is %s K but should be less than %s K" % (T,(Tmax)))


        BP_power=Qbp*Pbp/nBP/36
        HP_power=Qhp*Pf1/nHP/36
        FP_power=self.Qf1*Pfp/nFP/36
        PowerTotal=FP_power+HP_power+BP_power
        self.PowerRO=HP_power+BP_power
        self.SEC=PowerTotal/self.Qp1
        self.SEC_RO=self.PowerRO/self.Qp1
        


