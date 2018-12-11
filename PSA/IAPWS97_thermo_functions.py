#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 10:04:01 2018
This set of functions are primarily used to compute enthalpy for a saturated liquid or 
saturated vapor in the MED PSA model.

We also can compute saturation pressure with only temperature input. 
@author: adamatia
"""
import numpy as np
import PSA.Stoffparameter_H2O as D

###############################################################################
    
def enthalpySatLiqTW(temp):
    # specific enthalpy of saturated liquid water as a function of temperature
    #
    # enthalpySatLiqTW in kJ / kg
    # temp in K
    #
      
    press = pSatW(temp)
    # region 1
    if (temp>= 273.15  and temp <= 623.15 ):
        enthalpysatliq = enthalpyreg1(temp,press)
    
    # region X
    
    # outside range
    else:
      enthalpysatliq=-1
  
      print (' ERROR in function enthalpySatLiqTW !!! Temperature outside range. Enthalpy is set to -1 ' )
    
    return enthalpysatliq


###############################################################################
    
def enthalpySatVapTW(temp):
    #%   enthalpySatVapTW = enthalpySatVapTW (temp)
    #%
    #%   specific enthalpy of saturated steam as a function of temperature
    #%
    #%   enthalpySatVapTW in kJ / kg
    #%   temp in K
    
    
    press = pSatW(temp)
    #% region 2
    if temp>= 273.15  and temp <= 623.15:
#        enthalpysatvap=np.zeros((len(t2),1))
        enthalpysatvap=enthalpyreg2(temp,press)
    
    #% region 3
    #% t3 = find (temp> 623.15 & temp <= 647,096);
    #%          pressure = pSatW (temperature) - 0.00001
    #%          density = densreg3 (temperature, pressure)
    #%          enthalpySatVapTW = enthalpyreg3 (temperature, density)
    
    #% outside range
    else:
#    tbad = np.where(temp <273.15 or temp> 623.15)
        enthalpysatvap = - 1 
#    if sum(tbad)>0:
        print( ' ERROR in function enthalpySatVapTW !!! Temperature outside range. Enthalpy is set to -1 ' )
    
    return enthalpysatvap

###############################################################################
    
def pSatW(temp):
    # computing 
    del_ = temp + D.nreg4[8]/(temp - D.nreg4[9])
    Aco = del_**2  + D.nreg4[0]*del_ + D.nreg4[1]
    Bco = D.nreg4[2]* del_** 2  + D.nreg4[3]* del_ + D.nreg4[4]
    cco = D.nreg4[5]* del_** 2  + D.nreg4[6]* del_ + D.nreg4[7]
    press = ( 2*cco/(-Bco + (Bco**2  -  4* Aco*cco)** 0.5 ))** 4.*10
    return press

###############################################################################

def enthalpyreg1(temp,press):
    #% specific enthalpy in region 1
    #% Spezifische Enthalpie für Wasser im flüssigen Zustand
    #% enthalpyreg1  in kJ/kg
    #% temp          in K
    #% press         in bar
    #%
    #% erstellt von Stefan Petersn
    #% 10/10/02

    tau=1386/temp
    pic=0.1*press/16.53
    myenthalpyreg1 = 0.001*D.rgas_water*temp*tau*gammataureg1(tau, pic)
    return myenthalpyreg1

###############################################################################

def enthalpyreg2(temp,press):
    #% specific enthalpy in region 1
    #% Spezifische Enthalpie für Wasser im flüssigen Zustand
    #% enthalpyreg1  in kJ/kg
    #% temp          in K
    #% press         in bar
    #%
    #% erstellt von Stefan Petersn
    #% 10/10/02

    tau = 540/temp
    pic = 0.1*press
    rgas_water = 461.526 
    myenthalpyreg2 = 0.001*rgas_water*temp*tau*(gamma0taureg2(tau, pic) + gammartaureg2(tau, pic))

    return myenthalpyreg2

###############################################################################

    
def gammataureg1(tau,pic):
    #% tau    reduced temperature     dimensionless
    #% pic    reduced pressure        dimensionless
    #%
    #% IAPWS water properties 1997
    #
    #% Unterfunktion zu den Stoffwerten für Wasser
    #% Stefan Petersen 10/10/02
    tauvec=np.zeros((len(D.nreg1),1))
    picvec=np.zeros((len(D.nreg1),1))

    tauvec[0:len(D.nreg1)]=np.tile(tau-1.222,(len(D.nreg1),1))
    picvec[0:len(D.nreg1)]=np.tile(7.1-pic,(len(D.nreg1),1))
#   MATLAB code  
#    nreg1=repmat(nreg1,len(tau),1);
#    ireg1=repmat(ireg1,len(tau),1);
#    jreg1=repmat(jreg1,len(tau),1);
    # Python rewrite: 
    nreg1=np.tile(D.nreg1,(1,1))
    ireg1=np.tile(D.ireg1,(1,1))
    jreg1=np.tile(D.jreg1,(1,1))
    gammataureg1_tmp=nreg1*picvec**ireg1*jreg1*tauvec**(jreg1-1)
    mygammataureg1=sum(gammataureg1_tmp)  ### Removed transposes as they seemed unnecessary
    return mygammataureg1

###############################################################################
    
def gamma0taureg2(tau,pic):
#    % tau = ones (1,9) * tau;
#    % gamma0taureg2 = sum (n0reg2. * j0reg2. * tau. ^ (j0reg2-1));
    
    
    tauvec=np.zeros((len(D.n0reg2),1))
    tauvec[0:len(D.n0reg2)] = np.tile(tau, (len(D.n0reg2),1))
    
    n0reg2 = np.tile(D.n0reg2,(1,1))
    j0reg2 = np.tile(D.j0reg2,(1,1))
    
    
    gamma0taureg2_tmp = n0reg2*j0reg2*tauvec**(j0reg2- 1)
    
    mygamma0taureg2 = sum(gamma0taureg2_tmp)
    return mygamma0taureg2

###############################################################################
    
def gammartaureg2(tau,pic):
    #% Second derivative in tau of residual part of fundamental equation for region 2
    #% Stefan Petersen
    #% 10/10/02
    
    #% pic=ones(1,43)*pic
    #% tau=ones(1,43)*tau-0.5
    #% gammartaureg2=sum(nreg2.*pic.^ireg2.*jreg2.*tau.^(jreg2-1))
    tauvec=np.zeros((len(D.nreg2),1))
    picvec=np.zeros((len(D.nreg2),1))

    tauvec[0:len(D.nreg2)]=np.tile(tau-0.5,(len(D.nreg2),1))
    picvec[0:len(D.nreg2)]=np.tile(pic,(len(D.nreg2),1))
    
    nreg2=np.tile(D.nreg2,(1,1))
    jreg2=np.tile(D.jreg2,(1,1))
    ireg2=np.tile(D.ireg2,(1,1))
    
    gammartaureg2_tmp=nreg2*picvec**ireg2*jreg2*tauvec**(jreg2-1)
    
    mygammartaureg2=sum(gammartaureg2_tmp)
    return mygammartaureg2

###############################################################################
    
