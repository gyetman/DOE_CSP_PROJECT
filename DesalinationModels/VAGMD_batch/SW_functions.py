# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 10:16:22 2020

@author: zzrfl
"""
# Seawater functions
import math

def SW_Density(T, uT, S, uS, P, uP):  # (uT = C, uS = ppt, uP =mpa)
    if uT == 'k':
        T = T - 273.15
    elif uT == 'f':
        T = 5/9*(T-32)
    elif uT == 'r':
        T = 5/9*(T-491.67)
    
    if uS == 'ppm':
        S = S/1000
    elif uS == 'w':
        S = S *1000
    elif uS == '%':
        S = S * 10
        
    if uP == 'bar':
        P /= 10
    elif uP == 'kpa':
        P /= 1000
    elif uP == 'pa':
        P /= 1e6
    
    Psat = SW_Psat(T, 'C', S, 'ppt') / 1e6
    P0 = Psat
    
    if T <100:
        P0 = 0.101325
    
    s = S/1000
    a = [
         9.9992293295E+02,
         2.0341179217E-02,
        -6.1624591598E-03,
         2.2614664708E-05,
        -4.6570659168E-08
    ]    
    b = [
         8.0200240891E+02,
        -2.0005183488E+00,
         1.6771024982E-02,
        -3.0600536746E-05,
        -1.6132224742E-05
    ]    
    
    rho_w = a[0] + a[1] * T + a[2] *T**2 + a[3] * T**3 + a[4] * T**4
    D_rho = b[0] *s + b[1] *s *T + b[2] *s *T**2 + b[3] * s * T**3 + b[4] *s**2*T**2
    rho_sw_sharq = rho_w + D_rho
    

    c = [
         5.0792E-04,
        -3.4168E-06,
         5.6931E-08,
        -3.7263E-10,
         1.4465E-12,
        -1.7058E-15,
        -1.3389E-06,
         4.8603E-09,
        -6.8039E-13
    ]    
    
    d=[
        -1.1077e-06,
         5.5584e-09,
        -4.2539e-11,
         8.3702e-09
       ]    
    
    kT = c[0] + c[1]*T +c[2]*T**2 + c[3]*T**3 +c[4]*T**4 + c[5]*T**5 + P * (c[6] + c[7]*T + c[8]*T**3) + S * (d[0] + d[1]*T + d[2]*T**2 + d[3] * P)
    
    F_P = math.exp ( (P-P0) * (c[0] + c[1]*T +c[2]*T**2 + c[3]*T**3 +c[4]*T**4 + c[5]*T**5 + S * (d[0] + d[1]*T + d[2]*T**2) ) + 0.5*(P**2 - P0**2)*(c[6] + c[7]*T + c[8]*T**3 + d[3] * S))
    
    rho = rho_sw_sharq * F_P
    return rho
    
def SW_Psat(T, uT, S, uS):
    if uT == 'k':
        T = T - 273.15
    elif uT == 'f':
        T = 5/9*(T-32)
    elif uT == 'r':
        T = 5/9*(T-491.67)
    
    if uS == 'ppm':
        S = S/1000
    elif uS == 'w':
        S = S *1000
    elif uS == '%':    
        S = S * 10
        
    
    T += 273.15
    a = [-5.8002206E+03,
         1.3914993E+00,
        -4.8640239E-02,
         4.1764768E-05,
        -1.4452093E-08,
         6.5459673E+00
    ]    
    
    Pv_w = math.exp(a[0] / T) + a[1] +a[2] *T+ a[3]*T**2 + a[4] * T**3 + a[5] * math.log(T)
    
    b  = [
        -4.5818 * 10 ** -4,
        -2.0443 * 10 ** -6
    ]    
    
    Pv = Pv_w * math.exp(b[0]) * S + b[1] * S**2
    
    return Pv

def SW_LatentHeat(T, uT, S, uS):
    if uT == 'k':
        T = T - 273.15
    elif uT == 'f':
        T = 5/9*(T-32)
    elif uT == 'r':
        T = 5/9*(T-491.67)
    
    if uS == 'ppm':
        S = S/1000
    elif uS == 'w':
        S = S *1000
    elif uS == '%':    
        S = S * 10
    a = [
         2.5008991412E+06,
        -2.3691806479E+03,
         2.6776439436E-01,
        -8.1027544602E-03,
        -2.0799346624E-05
    ]            
    
    hfg_w = a[0] + a[1]*T + a[2] *T**2 + a[3]*T**3 + a[4]*T**4
    hfg = hfg_w * (1- 0.001*S)
    
    return hfg

def SW_SpcHeat(T,uT,S,uS,P,uP):
    if uT == 'k':
       T = T - 273.15
    elif uT == 'f':
       T = 5/9*(T-32)
    elif uT == 'r':
       T = 5/9*(T-491.67)
       
    if uS == 'ppm':
       S = S/1000
    elif uS == 'w':
       S = S *1000
    elif uS == '%':
       S = S * 10
       
    if uP == 'bar':
       P /= 10
    elif uP == 'kpa':
       P /= 1000
    elif uP == 'pa':
       P /= 1e6   
    Psat = SW_Psat(T, 'C', S, 'ppt') / 1e6
    P0 = Psat
       
    if T <100:
       P0 = 0.101325
       
    T68 = 1.00024 * (T+273.15)
    S_gkg = S
    
    A = 5.328 - 9.76 * 10 ** (-2) * S + 4.04*10**(-4)*S** 2
    B = -6.913 * 10 ** (-3) + 7.351 * 10 ** (-4) * S - 3.15*10**(-6)*S** 2
    C = 9.6 * 10 ** (-6) - 1.927 * 10 ** (-6) * S + 8.23 * 10**(-9) *S** 2
    D = 2.5 * 10 ** (-9) + 1.666 * 10 ** (-9) * S - 7.125 * 10**(-12)*S** 2
    cp_sw_P0 = 1000*(A + B*T68 + C*(T68**2) + D*(T68**3))
    
    c1 = -3.1118
    c2 = 0.0157
    c3 = 5.1014 * 10 ** (-5)
    c4 = -1.0302 * 10 ** (-6)
    c5 = 0.0107
    c6 = -3.9716 * 10 ** (-5)
    c7 = 3.2088 * 10 ** (-8)
    c8 = 1.0119 * 10 ** (-9)
    
    cp_sw_P = (P - P0)*(c1 + c2*T + c3*(T**2) + c4*(T**3) + S_gkg*(c5 + c6*T + c7*(T**2) + c8*(T**3)));
    
    cp = cp_sw_P0 + cp_sw_P    
    
    return cp