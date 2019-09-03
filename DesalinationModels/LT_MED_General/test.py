# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 12:46:21 2019

@author: zzrfl
""" 
default_case = lt_med_general()
while default_case.max_DA > default_case.Tol:
    # Set up for the first effect
    default_case.Egbg[0] = TD_func.enthalpySatVapTW(default_case.Tv[0]+273.15)
    default_case.Egbl[0] = TD_func.enthalpySatLiqTW(default_case.Tv[0]+273.15)
    default_case.Lgb[0]  = default_case.Egbg[0] - default_case.Egbl[0]
    default_case.Uef[0]  = 1.9695 + (1.2057e-2  * default_case.Tb[0]) - (8.5989e-5 * default_case.Tb[0]**2) + (2.5651e-7 * default_case.Tb[0]**3)
    default_case.Mgb[0]  = (default_case.Qef[0] - default_case.Mf * default_case.Cp * (default_case.Tb[0] - default_case.Tf)) / default_case.Lgb[0]
    default_case.Aef[0]  = default_case.Qef[0] / (default_case.Uef[0] * (default_case.Ts - default_case.Tb[0]))
    default_case.Lv[0]   = default_case.Lgb[0]
    default_case.Mfv[0]  = (default_case.Mgb[0] + default_case.Mgf[0]) * 3600
    default_case.Mgt[0]  = (default_case.Mgb[0] + default_case.Mgf[0] + default_case.Mdf[0])
    default_case.Mb[0]   = default_case.Mf - default_case.Mgb[0]
    default_case.Xb[0]   = default_case.Xf * default_case.Mf / default_case.Mb[0]
    
    default_case.Sum_A = default_case.Aef[0]
    
    # Other effects calculations
    
    for i in range(1, default_case.Nef):
        default_case.Mv[i]   = default_case.Mgt[i-1] - default_case.Mvh[i-1]
        default_case.Mdaf[i] = default_case.Mv[i]
        default_case.Egv[i]  = TD_func.enthalpySatVapTW(default_case.Tv[i]+273.15)
        default_case.Egl[i]  = TD_func.enthalpySatLiqTW(default_case.Tv[i]+273.15)
        default_case.Lv[i]   = default_case.Egv[i] - default_case.Egl[i]
        default_case.Lgf[i]  = default_case.Lv[i]
        default_case.Lgb[i]  = default_case.Lv[i]
        default_case.Mgf[i]  = default_case.Mb[i-1] * default_case.Cp *(default_case.Tb[i-1] - default_case.Tdb[i]) / default_case.Lgf[i]
        default_case.Mdb[i]  = default_case.Mb[i-1] - default_case.Mgf[i]
        default_case.Xdb[i]  = default_case.Xb[i-1] * default_case.Mb[i-1] / default_case.Mdb[i]
        default_case.Mgb[i]  = (default_case.Mv[i] * default_case.Lv[i-1] + default_case.Mdb[i] *default_case.Cp * (default_case.Tdb[i] - default_case.Tb[i]) )/ default_case.Lgb[i]
        default_case.Mfv[i]  = (default_case.Mgb[i] + default_case.Mgf[i]) *3600
        default_case.Qef[i]  = default_case.Mv[i] * default_case.Lv[i-1]
        default_case.Uef[i]  = 1.9695 + (1.2057e-2 * default_case.Tb[i]) - (8.5989e-5 * default_case.Tb[i]**2) + (2.5651e-7 * default_case.Tb[i]**3)
        default_case.Mb[i]   = default_case.Mdb[i] - default_case.Mgb[i]
        default_case.Xb[i]   = default_case.Mdb[i] * default_case.Xdb[i] / default_case.Mb[i]
        default_case.Ldf[i]  = default_case.Lv[i]
        default_case.Mdf[i]  = (default_case.Mdh[i-1] * default_case.Cp * (default_case.Tv[i-1] - default_case.Tv[i]) + (default_case.Mdaf[i-1] * default_case.Cp * (default_case.Tv[i-1] - default_case.Tv[i])) + default_case.Md[i-1] * default_case.Cp * (default_case.Tv[i-1] - default_case.Tv[i]) ) / default_case.Ldf[i]
        default_case.Mgt[i]  = default_case.Mgb[i] + default_case.Mgf[i] + default_case.Mdf[i] 
        default_case.Md[i]   = default_case.Mdaf[i] + default_case.Mdh[i-1] + default_case.Md[i-1] - default_case.Mdf[i]
        default_case.Aef[i]  = default_case.Qef[i] / default_case.Uef[i] / (default_case.Tv[i-1] - default_case.Tb[i])
        
        default_case.Sum_A += default_case.Aef[i]
      
    default_case.Am = default_case.Sum_A / default_case.Nef
    default_case.DTb[0] *= (default_case.Aef[0] / default_case.Am)
    default_case.Tb[0]   = default_case.Ts - default_case.DTb[0]
    default_case.Xb_w[0] = default_case.Xb[0] / (1000*1000) *100 # Salinity in weigth percentage
    default_case.A[0]    = 8.325e-2 + (1.883e-4 * default_case.Tb[0]) + (4.02e-6 * default_case.Tb[0]**2)
    default_case.B[0]    = -7.625e-4 + (9.02e-5 * default_case.Tb[0]) - (5.2e-7 * default_case.Tb[0]**2)
    default_case.C[0]    = 1.552e-4- (3e-6 * default_case.Tb[0]) - (3e-8 * default_case.Tb[0]**2)
    default_case.BPE[0]  = default_case.A[0] * default_case.Xb_w[0] + default_case.B[0] * default_case.Xb_w[0]**2 + default_case.C[0] * default_case.Xb_w[0]**3
    default_case.Tv[0]   = default_case.Tb[0] - default_case.BPE[0] - default_case.DELTAT_loss
    default_case.Uef[0]  = 1.9695 + (1.2057e-2 * default_case.Tb[0]) - (8.5989e-5 * default_case.Tb[0]**2) + (2.5651e-7 * default_case.Tb[0]**3)
    default_case.max_DA *= 0.1
    
    for i in range(1, default_case.Nef):
        default_case.DTb[i] *= default_case.Aef[i] / default_case.Am
        default_case.Tb[i]  = default_case.Tb[i-1] - default_case.DTb[i]
        default_case.Xb_w[i] = default_case.Xb[i] / (1000*1000) *100
        default_case.A[i]    = 8.325e-2 + (1.883e-4 * default_case.Tb[i]) + (4.02e-6 * default_case.Tb[i]**2)
        default_case.B[i]    = -7.625e-4 + (9.02e-5 * default_case.Tb[i]) - (5.2e-7 * default_case.Tb[i]**2)
        default_case.C[i]    = 1.552e-4- (3e-6 * default_case.Tb[i]) - (3e-8 * default_case.Tb[i]**2)
        default_case.BPE[i]  = default_case.A[i] * default_case.Xb_w[i] + default_case.B[i] * default_case.Xb_w[i]**2 + default_case.C[i] * default_case.Xb_w[i]**3
        default_case.NEA[i]  = 33 * default_case.DTb[i]**0.55 / default_case.Tv[i]
        default_case.Tv[i]   = default_case.Tb[i] - default_case.BPE[i] - default_case.DELTAT_loss
        default_case.Tdb[i]  = default_case.Tv[i] - default_case.NEA[i]
        default_case.DA[i]   = abs(default_case.Aef[i-1] - default_case.Aef[i])
        
    default_case.max_DA = max(default_case.DA)