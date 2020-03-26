# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 13:53:34 2020

MIT Thermophysical Properties of Seawater
Citations: Add based on MIT's request
    
@author: adama
"""
import numpy as np

#%%
def SW_ConductivityP(T,S,P): # T in C, S in ppt, P in MPa
    '''
    Thermal conductivity of seawater accounting for pressure dependency
    VALIDITY: (1) 10 < T < 90 C; 0 < S < 120 g/kg;  P = P0
              (2) 10 < T < 60 C; 0 < S < 35 g/kg; 0.1 < P < 12 MPa
    
    ACCURACY: (1) 2.59%
              (2) 2.59%
    '''
    T_star = (T + 273.15)/300
    P_star = (P - 0.1)/(139.9)
    k_fw0 = 0.797015135*T_star**(-0.193823894) - 0.251242021*T_star**(-4.7166384) + 0.0964365893*T_star**(-6.38463554) - 0.0326956491*T_star**(-2.13362102)
    A = 13.464*T_star**4 - 60.727*T_star**3 + 102.81*T_star**2 - 77.387*T_star + 21.942
    k_fw = k_fw0*(1 + A* P_star)

    B = 0.00022
    k_sw = k_fw/(B*S + 1)

    return k_sw

def SW_viscosity(T,S): # T in oC, S in ppt
    '''
    VALIDITY: 0 < T < 180 C and 0 < S < 150 g/kg
    ACCURACY: 1.5%
    '''
    S = S/1000;
    
    a = [
        1.5700386464E-01,
        6.4992620050E+01,
       -9.1296496657E+01,
        4.2844324477E-05,
        1.5409136040E+00,
        1.9981117208E-02,
       -9.5203865864E-05,
        7.9739318223E+00,
       -7.5614568881E-02,
        4.7237011074E-04
        ]
    
    mu_w = a[3] + 1/(a[0]*(T+a[1])**2+a[2])
     
    A  = a[4] + a[5] * T + a[6] * T**2
    B  = a[7] + a[8] * T + a[9]* T**2
    mu = mu_w*(1 + A*S + B*S**2)
    
    return mu
    

def SW_Density(T, S, P): # T in oC, S in ppt, P in MPa
    '''
    Density of seawater, Zhuoran's transcription
    '''
#    P = P/1E6
    if T < 100:
        P0 = 0.101325
    else:
        P0 = SW_Psat(T, S) / 1E6
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
    

def SW_Psat(T, S): # T in oC, S in ppt
    '''
    Saturated vapor pressure of seawater, Zhuoran's transcription
    returns saturated vapor pressure in N/m^2 (Pa)
    '''
    T = T + 273.15
    a = [-5.8002206E+03, 1.3914993E+00, -4.8640239E-02, 4.1764768E-05, -1.4452093E-08, 6.5459673E+00]
    
    Pv_w = np.exp( a[0] / T + a[1] + a[2] * T + a[3] * T**2 + a[4] * T**3 + a[5] * np.log(T) )
    
    b = [-4.5818E-04, -2.0443E-06]
    
    Pv = Pv_w * np.exp(b[0] * S + b[1] * S**2)
    return Pv
        
def SW_LatentHeat(T, S):  # T in oC, S in ppt
    '''
    Latent heat of seawater, Zhuoran's transcription
    '''
    a = [2.5008991412E+06, -2.3691806479E+03, 2.6776439436E-01, -8.1027544602E-03, -2.0799346624E-05]
    hfg_w = a[0] + a[1]*T + a[2]*T**2 + a[3]*T**3 + a[4]*T**4
    hfg = hfg_w * (1-0.001*S)
    return hfg

def SW_SpcHeat(T,S,P): # T in oC, S in ppt, P in MPa
    '''
    Specific heat of seawater, Zhuoran's transcription
    '''
#    P =P/1E6
    if T < 100:
        P0 = 0.101325
    else:
        P0 = SW_Psat(T, S) / 1E6
    
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