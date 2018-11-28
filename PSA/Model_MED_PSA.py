"""
Converting the PSA MED Case Study MATLAB code to Python
11/5/2018
v1
Adam A
"""
import numpy as np
import PSA.IAPWS97_thermo_functions as F
import math as math
#modeling_MED_case_study


class medPsa:
    # INPUT VARIABLES
    Tcwin= 25           #Tcwin: Seawater inlet temperature in the condenser, ºC
    Mf= 2.22            #Mf is the feedwater mass flow rate. In MED-PSA it is 2.22   kg/s
    Nef=14              #Nef: Number of effects
    Nph= 13             #Nph: Number of preheaters
    Xf=35000            # Xf is the feedwater salinity, ppm.
    Cp=4.18             #Cp: Specific heat of distillate, feed and brine, that is considered constant in all the effects, kJ/kgºC
    y= 0.0028           #y: fraction of distillate that comes from 4th effect and enters the 7th effect, kg/s
    NEA= 0.5            #NEA: Non Equilibrium Allowance, ºC
#    Ts=70.8             #Ts is the steam temperature at the inlet of the first bundle tube, ºC

    def __init__(self):
        #Inputs from SAM
        self.Ts = 70.8                              #Ts is the steam temperature at the inlet of the first bundle tube, ºC
        self.Ms=0.082                                # Heating source mass flow rate, kg/s
        
        #Output Values
        self.Mpro=0 
        self.Tpro=0 
        self.Mprod_final=0
        
        # Performance parameters 
        self.PR=0
        self.RR=0      
        self.Xbn=0      
        self.sA=0
    
    def execute_module(self):
        Tcwout=medPsa.Tcwin+7.3    #Tcwout is the seawater outlet temperature of the condenser, ºC
        Tvc=Tcwout+1.5      #Tvc is the vapor temperature inside the condenser, ºC
        Tb=np.zeros((medPsa.Nef,1))
        Tb[medPsa.Nef-1]=36 
        Tb[0]=69 
        DELTATb=(Tb[0]-Tb[medPsa.Nef-1])/(medPsa.Nef-1) 
        
        for i in range(1,medPsa.Nef-1):
            Tb[i]=Tb[i-1]-DELTATb 
            
        
        
        TTL=1 
        
        Tv=Tb-TTL 
            
        Tf=Tv[0]-1.7 
        # 
        Tph=np.zeros((medPsa.Nef,1))
        Tph[0]=Tf 
        Tph[medPsa.Nef-1]=Tcwout 
        
        DELTATph=(Tph[0]-Tph[medPsa.Nef-1])/medPsa.Nph 
        
        for i in range(1,medPsa.Nef-1):
            Tph[i]=Tph[i-1]-DELTATph 
        
        
        # CALCULATIONS
        
        # Calculate the temperature of the distillate in the subooled area (when it flows from an effect to the next one it tranfers its sensible heat), ºC
        Tdv=np.zeros((medPsa.Nef,1))
        Tdv[0]=Tv[0]-2  
        for i in range(1,medPsa.Nef):
            Tdv[i]=Tv[i]-2 
        
        # Calculate the temperature difference between effects, ºC
            ## AAA- DOUBLE CHECK- first value in DTvo seems unnecessary or wrong
        DTvo=np.zeros((medPsa.Nef,1))
        DTvo[0]=Tv[0] 
        for i in range(1,medPsa.Nef):
            DTvo[i]=Tv[i-1]-Tv[i] 
        
        
        # Calculate the temperature of the brine after flashing process from effects 2 to medPsa.Nef, Tdb[i]. 
        Tdb=np.zeros((medPsa.Nef,1))
        for i in range(1,medPsa.Nef):
            Tdb[i]=Tv[i]-medPsa.NEA  #ºC 
        
        
        # Calculate the vapor consumed in each preheater, out of the vapor flowing from the effect, Mvh[i]
        
        Evh=np.zeros((medPsa.Nph,1))       # Enthalpy of the vapor that enters the preheater, kJ/kg
        Elh=np.zeros((medPsa.Nph,1))        # Enthalpy of the condensate that leaves the preheater, kJ/kg
        Lvh=np.zeros((medPsa.Nph,1))               # Latent heat of the vapor in the preheater, kJ/kg
        Mvh=np.zeros((medPsa.Nph,1))   # kg/s
        Mdh=np.zeros((medPsa.Nph,1))                        # Condensate generated in the preheater, kg/s
        Qph=np.zeros((medPsa.Nph,1))       # Heat transfer rate in the preheaters, kJ/s
        Uph=np.zeros((medPsa.Nph,1))   # Overall heat transfer coefficient of the preheaters, kW/m2ºC. Correlation of El-Dessouky
        LTMDph=np.zeros((medPsa.Nph,1))  # Log mean temperature difference, ºC
        Aph=np.zeros((medPsa.Nph,1)) 
        
        for i in range(0,medPsa.Nph):
            Evh[i]=F.enthalpySatVapTW(Tv[i]+273.15)       # Enthalpy of the vapor that enters the preheater, kJ/kg
            Elh[i]=F.enthalpySatLiqTW(Tv[i]+273.15)       # Enthalpy of the condensate that leaves the preheater, kJ/kg
            Lvh[i]=Evh[i]-Elh[i]                  # Latent heat of the vapor in the preheater, kJ/kg
            Mvh[i]=(medPsa.Mf*medPsa.Cp*(Tph[i]-Tph[i+1]))/Lvh[i]  # kg/s
            Mdh[i]=Mvh[i]                        # Condensate generated in the preheater, kg/s
            Qph[i]=medPsa.Mf*medPsa.Cp*(Tph[i]-Tph[i+1])       # Heat transfer rate in the preheaters, kJ/s
            Uph[i]=1.7194+(3.2063e-3*Tv[i])+(1.5971e-5*Tv[i]**2)-(1.9918e-7*Tv[i]**3)  # Overall heat transfer coefficient of the preheaters, kW/m2ºC. Correlation of El-Dessouky
            LTMDph[i]=((Tv[i]-Tph[i+1])-(Tv[i]-Tph[i]))/math.log((Tv[i]-Tph[i+1])/(Tv[i]-Tph[i]))  # Log mean temperature difference, ºC
            Aph[i]=Qph[i]/(Uph[i]*LTMDph[i]) 
        
        
        Sum_Aph=sum(Aph) 
        Amph=Sum_Aph/medPsa.Nph 
        
        ### AAA - Stop here for today , 11/5/2018 11:51 PM EST
        
        # Calculations and assumptions in the first effect that is fed with hot water as the heat source instead of steam 
        #Ms=0.082                                # Heating source mass flow rate, kg/s
        Mgf=np.zeros((medPsa.Nef,1))
        Egbl = np.zeros((medPsa.Nef,1))    # Enthalpy of the brine that has not evaporated, kJ/kg
        Lgb=np.zeros((medPsa.Nef,1))         # Latent heat of the generated vapor by boiling of the brine in the first effect, kJ/kg
        Lv=np.zeros((medPsa.Nef,1))                     # Latent heat of the vapor entering the bundle tube of the second effect (at temperature Tv[0], kJ/kg
        Esg=np.zeros((medPsa.Nef,1))
        Esl=np.zeros((medPsa.Nef,1))
        #Ls=np.zeros((medPsa.Nef,1))
        Mgb=np.zeros((medPsa.Nef,1))
        Mfv=np.zeros((medPsa.Nef,1))        # Mass flow rate of the vapor generated in the first effect (by boiling and flashing), kg/h
        Mb=np.zeros((medPsa.Nef,1))                         # Mass flow rate of the brine that leaves the first effect, kg/s
        Xb=np.zeros((medPsa.Nef,1))
        Mdb=np.zeros((medPsa.Nef,1))                                    # Mass flow rate of the brine after flashing process, which is 0 in the first effect, kg/s
        Mdr=np.zeros((medPsa.Nef,1))                                    # Mass flow rate of the distillate that remains from the distillate branches, which is 0 for the fourth effect, kg/s
        Uef=np.zeros((medPsa.Nef,1))
        Aef=np.zeros((medPsa.Nef,1))
        
        
        
        Mgf[0]=0                              # Mass flow rate of the vapor generated by flashing of the brine, which is 0 in the first effect, kg/s
        Md=np.zeros((medPsa.Nef,1))
        Md[0]=0                               # Distillate mass flow rate leaving the first effect, which is 0 in the first effect, kg/s
        Egbg=F.enthalpySatVapTW(Tv[0]+273.15)      # Enthalpy of the generated vapor by boiling of the brine, kJ/kg
        
        Egbl= F.enthalpySatLiqTW(Tv[0]+273.15)    # Enthalpy of the brine that has not evaporated, kJ/kg
        Lgb[0]=Egbg[0]-Egbl[0]            # Latent heat of the generated vapor by boiling of the brine in the first effect, kJ/kg
        Lv[0]=Lgb[0]                        # Latent heat of the vapor entering the bundle tube of the second effect (at temperature Tv[0], kJ/kg
        Esg[0]=F.enthalpySatVapTW(self.Ts+273.15) 
        Esl[0]=F.enthalpySatLiqTW(self.Ts+273.15) 
        Ls=Esg[0]-Esl[0] 
        Qs=self.Ms*Ls 
        Mgb[0]=((self.Ms*Ls[0])-(medPsa.Mf*medPsa.Cp*(Tb[0]-Tf)))/Lgb[0] 
        Mfv[0]=(Mgb[0]+Mgf[0])*3600               # Mass flow rate of the vapor generated in the first effect (by boiling and flashing), kg/h
        Mb[0]=medPsa.Mf-Mgb[0]                             # Mass flow rate of the brine that leaves the first effect, kg/s
        Xb[0]=(medPsa.Mf*medPsa.Xf)/Mb[0] 
        Mdb[0]=0                                      # Mass flow rate of the brine after flashing process, which is 0 in the first effect, kg/s
        Mdr[3]=0                                      # Mass flow rate of the distillate that remains from the distillate branches, which is 0 for the fourth effect, kg/s
        Uef[0]=1.9695+(1.2057e-2*(Tb[0]))-(8.5989e-5*Tb[0]**2)+(2.5651e-7*Tb[0]**3) 
        Aef[0]=Qs/(Uef[0]*(self.Ts-Tb[0])) 
        
        # Calculations in the effects from 2 to medPsa.Nef
        
        # Definition of the variables used:
        
        # Mv[i] is the vapor mass flow rate entering the bundle tube of each effect, kg/s
        # Egv[i] is the enthalpy of the vapor entering the bundle tube of each effect, kJ/kg
        # Egl[i] is the enthalpy of the condensate leaving the bundle tube of each effect, kJ/kg
        # Lv[i] is the latent heat of the vapor entering the bundle tube of each effect, kJ/kg
        # Lgf[i] is the latent heat of the vapor generated by flashing of the brine in each effect, kJ/kg
        # Lgb[i] is the latent heat of the vapor generated by boiling of the brine in each effect, kJ/kg
        # Mgf[i] is the mass flow rate of the vapor generated by flashing of the brine in each effect, kg/s
        # Mfv[i] is the mass flow rate of the vapor generated in each effect (by boiling and flashing), kg/s
        # Mdb[i] is the mass flow rate of the brine after flashing, kg/s
        # Md[i] is the distillate mass flow rate leaving each effect, kg/s
        # Td[i] is the temperature of the total distillate generated in each effect, ºC
        # Tdd[i] is the temperature of the total distillate that comes from the previous effect and enters the next one in the subcooled area, ºC
        # Tdv[i] is the temperature of the distillate leaving each preheater(subcooled area), ºC
        # Mda[i] is the mass flow rate of distillate coming from further effects and entering effects 7th, 10th and 13th effect (distillate external branches)
        # Mdr[i] is the mass flow rate of the rest of distillate that remains from distillate external branches, kg/s
        # Mdm[i] is the mass flow rate of the distillate that leaves each mixer point in the distillate branches, kg/s
        # c is the counter used in the calculations of Mda[i]
        # Tdm[i] is the temperature of the distillate that leaves the first mixer point in the distillate external branches, ºC
        # Qef[i] is the heat transfer rate in each effect, kW
        # Mvapor [i] is the mass flow rate of the vapor in each complete chamber(effect+preheater), kg/h
        # Uef[i] is the overall heat transfer coefficient of each effect, kW/m2ºC
        # Mb[i] is the mass flow rate of the brine that leaves each effect mass flow rate, kg/s
        # Mvent is the percentage of vapor that is sucked from the effect due to
        # the vacuum system
        Tbn=np.zeros((medPsa.Nef,1))
        Tbn[0]=Tb[0] 
        
        Mvent=np.zeros((medPsa.Nef,1))
        Mvent[1]=0.02 
        Mvent[6]=0.02 
        Mventc=0.02 
        
        Mv=np.zeros((medPsa.Nef,1))
        Egv=np.zeros((medPsa.Nef,1))
        Egl=np.zeros((medPsa.Nef,1))
        Lgf=np.zeros((medPsa.Nef,1)) 
        Xdb=np.zeros((medPsa.Nef,1))
        
        Td=np.zeros((medPsa.Nef,1))
        Tdd=np.zeros((medPsa.Nef,1))
        Qef=np.zeros((medPsa.Nef,1))
        Mda=np.zeros((medPsa.Nef,1))
        Mdm=np.zeros((medPsa.Nef,1))
        
        Tda=np.zeros((medPsa.Nef,1))
        Td=np.zeros((medPsa.Nef,1))
        Tdm=np.zeros((medPsa.Nef,1))
        Tddm=np.zeros((medPsa.Nef,1))  
        
        c=1  # Starting the counter
        d=1  # Starting the counter
        for i in range(1,medPsa.Nef):
                  Tbn[i]=Tb[i] 
                  Mv[i]=((Mgb[i-1]+Mgf[i-1])-Mvh[i-1])*(1-Mvent[i])  
                  Egv[i]=F.enthalpySatVapTW(Tv[i]+273.15)  
                  Egl[i]=F.enthalpySatLiqTW(Tv[i]+273.15)  
                  Lv[i]=Egv[i]-Egl[i]  
                  Lgf[i]=Lv[i]  
                  Lgb[i]=Lv[i]  
                  Mgf[i]=(Mb[i-1]*medPsa.Cp*(Tbn[i-1]-Tdb[i]))/Lgf[i]  
                  Mdb[i]=Mb[i-1]-Mgf[i] 
                  Xdb[i]=(Xb[i-1]*Mb[i-1])/Mdb[i] 
                  
                  if(i==1)or(i==4)or(i==7)or(i==10)or(i==13):    
                         Md[i]=(Mv[i]+Mdh[i-1]) 
                         Td[i]=((Mv[i]*Tv[i-1])+(Mdh[i-1]*Tdv[i-1]))/Md[i] 
                         Tdd[i]=Td[i]-2 
                         Mgb[i]=((Mv[i]*Lv[i-1])+(Mdb[i]*medPsa.Cp*(Tdb[i]-Tbn[i]))+(Mdh[i-1]*medPsa.Cp*(Tv[i-1]-Tdv[i-1])))/Lgb[i]  
                         Mfv[i]=(Mgb[i]+Mgf[i])*3600 
                         Qef[i]=Mv[i]*Lv[i-1] 
                  elif (i==2)or(i==3)or(i==5)or(i==8)or(i==11):
                         Md[i]=Mv[i]+Mdh[i-1]+Md[i-1] 
                         Td[i]=((Mv[i]*Tv[i-1])+(Mdh[i-1]*Tdv[i-1])+(Md[i-1]*Tdd[i-1]))/Md[i]  
                         Tdd[i]=Td[i]-2 
                         Mgb[i]=((Mv[i]*Lv[i-1])+(Mdb[i]*medPsa.Cp*(Tdb[i]-Tbn[i]))+(Mdh[i-1]*medPsa.Cp*(Tv[i-1]-Tdv[i-1]))+(Md[i-1]*medPsa.Cp*(Td[i-1]-Tdd[i-1])))/Lgb[i]  # Mass flow rate of the vapor generated by boiling of the brine, kg/s   
                         Mfv[i]=(Mgb[i]+Mgf[i])*3600 
                         Qef[i]=Mv[i]*Lv[i-1] 
                  elif (i==6)or(i==9)or(i==12):   
                         Mda[i]=medPsa.y*d  
                         Md[i]=Mv[i]+Mdh[i-1]+Md[i-1]+Mda[i] 
                         Mdr[i]=Md[i-3]+Mdr[i-3]-Mda[i]  
                         Mdm[i]=Md[i]+Mdr[i]  
                         c+=1  
                         if c==2:
                            d=50 
                         
                         if (i==6):
                                Tda[i]=Td[i-3]-6 
                                Td[i]=((Mv[i]*Tv[i-1])+(Mdh[i-1]*Tdv[i-1])+(Mda[i]*Tda[i])+(Md[i-1]*Tdd[i-1]))/Md[i] 
                                Tdm[i]=((Mdr[i]*Td[i-3])+(Md[i]*Td[i]))/Mdm[i]  
                                Tddm[i]=Tdm[i]-6    
                                Mgb[i]=((Mv[i]*Lv[i-1])+(Mdb[i]*medPsa.Cp*(Tdb[i]-Tbn[i]))+(Mdh[i-1]*medPsa.Cp*(Tv[i-1]-Tdv[i-1]))+(Md[i-1]*medPsa.Cp*(Td[i-1]-Tdd[i-1]))+(Mda[i]*medPsa.Cp*(Td[i-3]-Tda[i])))/Lgb[i] 
                                Mfv[i]=(Mgb[i]+Mgf[i])*3600 
                                Qef[i]=Mv[i]*Lv[i-1] 
                         elif (i==9)or(i==12):
                               Td[i]=((Mv[i]*Tv[i-1])+(Mdh[i-1]*Tdv[i-1])+(Mda[i]*Tddm[i-3])+(Md[i-1]*Tdd[i-1]))/Md[i] 
                               Tdm[i]=((Mdr[i]*Tdm[i-3])+(Md[i]*Td[i]))/Mdm[i]  
                               Tddm[i]=Tdm[i]-6 
                               Mgb[i]=((Mv[i]*Lv[i-1])+(Mdb[i]*medPsa.Cp*(Tdb[i]-Tbn[i]))+(Mdh[i-1]*medPsa.Cp*(Tv[i-1]-Tdv[i-1]))+(Md[i-1]*medPsa.Cp*(Td[i-1]-Tdd[i-1]))+(Mda[i]*medPsa.Cp*(Tdm[i-3]-Tddm[i-3])))/Lgb[i] 
                               Mfv[i]=(Mgb[i]+Mgf[i])*3600 
                               Qef[i]=Mv[i]*Lv[i-1] 
                         
        
                        
                  Uef[i]=1.9695+(1.2057e-2*(Tbn[i]))-(8.5989e-5*Tbn[i]**2)+(2.5651e-7*Tbn[i]**3)  
                  Aef[i]=Qef[i]/(Uef[i]*(Tv[i-1]-Tb[i])) 
                  Mb[i]=Mdb[i]-Mgb[i] 
                  Xb[i]=(Mdb[i]*Xdb[i])/Mb[i] 
        
        
        # Xbn=(Mf*medPsa.Xf)/Mb[medPsa.Nef-1] 
        Sum_Aef=sum(Aef) 
        Amef=Sum_Aef/medPsa.Nef #Area for heat transfer
        
        # Calculate the total distillate mass flow rate, Mdbc, and its temperature, Tdbc, before entering the end condenser
        Mdbc=Mdr[medPsa.Nef-2]+Md[medPsa.Nef-2]+Md[medPsa.Nef-1]  #kg/s
        Tdbc=((Mdm[medPsa.Nef-2]*Td[medPsa.Nef-2])+(Md[medPsa.Nef-1]*Td[medPsa.Nef-1]))/Mdbc  #ºC
        
        # Calculations in the end condenser
        Edfg=F.enthalpySatVapTW(Tvc+273.15)  # Enthalpy of the saturated vapor in the condenser, kJ/kg
        Edfg=F.enthalpySatLiqTW(Tvc+273.15)  # Enthalpy of the saturated liquid in the condenser, kJ/kg 
        Ldf=F.enthalpySatVapTW(Tvc+273.15)-F.enthalpySatLiqTW(Tvc+273.15)  # Latent heat of the vapor in the condenser, kJ/kg
        Mdf=(Mdbc*medPsa.Cp*(Tdbc-Tvc))/Ldf  # Mass flow rate of the vapor generated by flashing of the condensate entering the condenser, kg/s
        #Lv=Ldf 
        Msw=((Mgb[medPsa.Nef-1]+Mgf[medPsa.Nef-1]+Mdf)*(1-Mventc)*Ldf)/(medPsa.Cp*(Tcwout-medPsa.Tcwin))  # Mass flow rate of the cooling seawater in the condenser, kg/s
        Uc=1.7194+(3.2063e-3*Tv[medPsa.Nef-1])+(1.5971e-5*Tv[medPsa.Nef-1]**2)-(1.9918e-7*Tv[medPsa.Nef-1]**3)  
        Qc=Msw*medPsa.Cp*(Tcwout-medPsa.Tcwin) 
        LTMDc=((Tv[medPsa.Nef-1]-medPsa.Tcwin)-(Tv[medPsa.Nef-1]-Tcwout))/math.log((Tv[medPsa.Nef-1]-medPsa.Tcwin)/(Tv[medPsa.Nef-1]-Tcwout)) 
        Ac=Qc/(Uc*LTMDc) 
        
        # Calculation of the final product mass flow rate, kg/s
        self.Mpro=Mgb[medPsa.Nef-1]+Mgf[medPsa.Nef-1]+Mdbc 
        self.Tpro=((Mgb[medPsa.Nef-1]*Egv[medPsa.Nef-1])+(Mgf[medPsa.Nef-1]*Egv[medPsa.Nef-1])+(Mdf*Edfg))/(self.Mpro*medPsa.Cp) 
        self.Mprod_final=self.Mpro*24*3.6 
        
        # Performance parameters 
        self.PR=self.Mpro/self.Ms 
        self.RR=self.Mpro/medPsa.Mf 
        
        self.Xbn=medPsa.Xf/(1-self.RR) #Brine Salinity
        
        self.sA=(Sum_Aef+Sum_Aph+Ac)/self.Mprod_final  #Specific Area for heat transfer
    
    
    
    
    
    
    
    
    
