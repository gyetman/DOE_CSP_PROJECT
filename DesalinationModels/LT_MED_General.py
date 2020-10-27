# -*- coding: utf-8 -*-
"""
Converted from PSA's LT-MED general design model
Created on Wed Aug 28 10:01:06 2019

@author: Zhuoran Zhang
"""

import numpy as np
import math
import DesalinationModels.IAPWS97_thermo_functions as TD_func
# from DesalinationModels.LT_MED_calculation import lt_med_calculation
from scipy.optimize import fmin
# from DesalinationModels.LT_MED_calculation import lt_med_calculation

class lt_med_general(object):
    
#    regas_water = 461.526
#
#    #AddIn sub InitFieldsregl
#    ireg1 = [0,0,0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,3,3,3,4,4,4,5,8,8,21,23,29,30,31,32]
#    jreg1 = [-2,-1,0,1,2,3,4,5,-9,-7,-1,0,1,3,-3,0,1,3,17,-4,0,6,-5,-2,10,-8,-11,-6,-29,-31,-38,-39,-40,-41]
#    nreg1 = [0.14632971213167,-0.84548187169114,-3.756360367204,3.3855169168385,-0.95791963387872,0.15772038513228,-0.016616417199501,0.00081214629983568,0.00028319080123804,-0.00060706301565874,-0.018990068218419,-0.032529748770505,-0.021841717175414,-5.283835796993e-05,-0.00047184321073267,-0.00030001780793026,4.7661393906987e-05,-4.4141845330846e-06,-7.2694996297594e-16,-3.1679644845054e-05,-2.8270797985312e-06,-8.5205128120103e-10,-2.2425281908e-06,-6.5171222895601e-07,-1.4341729937924e-13,-4.0516996860117e-07,-1.2734301741641e-09,-1.7424871230634e-10,-6.8762131295531e-19,1.4478307828521e-20,2.6335781662795e-23,-1.1947622640071e-23,1.8228094581404e-24,-9.3537087292458e-26]
#
#    # AddIn InitFieldsreg2
#    j0reg2 = [0,1,-5,-4,-3,-2,-1,2,3]
#    n0reg2 = [-9.6927686500217,10.086655968018,-0.005608791128302,0.071452738081455,-0.40710498223928,1.4240819171444,-4.383951131945,-0.28408632460772,0.021268463753307]
#    ireg2  = [1,1,1,1,1,2,2,2,2,2,3,3,3,3,3,4,4,4,5,6,6,6,7,7,7,8,8,9,10,10,10,16,16,18,20,20,20,21,22,23,24,24,24]
#    jreg2  = [0,1,2,3,6,1,2,4,7,36,0,1,3,6,35,1,2,3,7,3,16,35,0,11,25,8,36,13,4,10,14,29,50,57,20,35,48,21,53,39,26,40,58]
#    nreg2  = [-0.0017731742473213,-0.017834862292358,-0.045996013696365,-0.057581259083432,-0.05032527872793,-3.3032641670203e-05,-0.00018948987516315,-0.0039392777243355,-0.043797295650573,-2.6674547914087e-05,2.0481737692309e-08,4.3870667284435e-07,-3.227767723857e-05,-0.0015033924542148,-0.040668253562649,-7.8847309559367e-10,1.2790717852285e-08,4.8225372718507e-07,2.2922076337661e-06,-1.6714766451061e-11,-0.0021171472321355,-23.895741934104,-5.905956432427e-18,-1.2621808899101e-06,-0.038946842435739,1.1256211360459e-11,-8.2311340897998,1.9809712802088e-08,1.0406965210174e-19,-1.0234747095929e-13,-1.0018179379511e-09,-8.0882908646985e-11,0.10693031879409,-0.33662250574171,8.9185845355421e-25,3.0629316876232e-13,-4.2002467698208e-06,-5.9056029685639e-26,3.7826947613457e-06,-1.2768608934681e-15,7.3087610595061e-29,5.5414715350778e-17,-9.436970724121e-07]
#    
#    # AddIn InitFieldsreg3
#    ireg3  = [0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,4,4,4,4,5,5,5,6,6,6,7,8,9,9,10,10,11]
#    jreg3  = [0,0,1,2,7,10,12,23,2,6,15,17,0,2,6,7,22,26,0,2,4,16,26,0,2,4,26,1,3,26,0,2,26,2,26,2,26,0,1,26]
#    nreg3  = [1.0658070028513,-15.732845290239,20.944396974307,-7.6867707878716,2.6185947787954,-2.808078114862,1.2053369696517,-0.0084566812812502,-1.2654315477714,-1.1524407806681,0.88521043984318,-0.64207765181607,0.38493460186671,-0.85214708824206,4.8972281541877,-3.0502617256965,0.039420536879154,0.12558408424308,-0.2799932969871,1.389979956946,-2.018991502357,-0.0082147637173963,-0.47596035734923,0.0439840744735,-0.44476435428739,0.90572070719733,0.70522450087967,0.10770512626332,-0.32913623258954,-0.50871062041158,-0.022175400873096,0.094260751665092,0.16436278447961,-0.013503372241348,-0.014834345352472,0.00057922953628084,0.0032308904703711,8.0964802996215e-05,-0.00016557679795037,-4.4923899061815e-05]
#    
#    # AddIn InitFIeldsreg4
#    nreg4  = [1167.0521452767,-724213.16703206,-17.073846940092,12020.82470247,-3232555.0322333,14.91510861353,-4823.2657361591,405113.40542057,-0.23855557567849,650.17534844798]
#    
#    # AddIn Sub InitFieldsbound
#    nbound = [348.05185628969,-1.1671859879975,0.0010192970039326,572.54459862746,13.91883977887]
#    
#    # AddIn Sub InitFieldsvisc
#    n0visc = [1,0.978197,0.579829,-0.202354]
#    ivisc  = [0,0,0,0,1,1,1,1,2,2,2,3,3,3,3,4,4,5,6]
#    jvisc  = [0,1,4,5,0,1,2,3,0,1,2,0,1,2,3,0,3,1,3] 
#    nvisc  = [0.5132047,0.3205656,-0.7782567,0.1885447,0.2151778,0.7317883,1.241044,1.476783,-0.2818107,-1.070786,-1.263184,0.1778064,0.460504,0.2340379,-0.4924179,-0.0417661,0.1600435,-0.01578386,-0.003629481]
#    
#    # AddIn Sub InitFieldsthcon
#    n0thcon = [1,6.978267,2.599096,-0.998254]
#    nthcon  = [[1.3293046 , -0.40452437,  0.2440949,  0.01866075,  -0.12961068,  0.04480995],
#                   [1.7018363 , -2.2156845 ,  1.6511057 , -0.76736002, 0.37283344 ,  -0.1120316],
#                   [5.2246158 , -10.124111 ,  4.9874687 , -0.27297694, -0.43083393,  0.13333849],
#                   [8.7127675 ,  -9.5000611,  4.3786606 , -0.91783782, 0.         ,  0.        ],
#                   [-1.8525999,  0.9340469 ,   0.       , 0.         , 0.         ,  0.        ]]
#            
#    def enthalpyreg1(self, temp, press):
#        self.tau = 1386 / temp
#        self.pic = 0.1 * press / 16.53
#        enthalpy1 = 0.001 * self.regas_water * self.temp * self.tau * self.gammataureg1(tau, pic)
#        
#        return enthalpy1
#    
#    
#    def gammataureg1(self, tau, pic):
#        for i in len(self.nreg1):
    def __init__(self,
         Xf      =  35 , # Feedwater salinity  (g/L)
         Ts      =  80     , # The temperature of the steam at the inlet of the first bundle tube, C
         Nef     =  14  , # The feed water salinity, ppm
         Capacity = 2000,    # Capacity of the plant (m3/day)
         Tin     = 15 , # Inlet seawater temperature
         RR      = 0.5 , # recovery ratio
         Fossil_f = 1 # Fossil fuel fraction
         ):
        
        self.Ts = Ts
        self.Nef = Nef
        self.Capacity = Capacity
        self.Fossil_f = Fossil_f
        self.Xf = Xf *1000
        self.RR = RR
        self.Tin  = Tin
    
    def design(self):
        p1 = self.Xf
        p2 = self.RR
        p3 = self.Tin
        p4 = self.Capacity
        p5 = self.Ts
        qF_paras = [p1, p1**2, p2, p2*p1, p2*p1**2, p2**2, p2**2*p1, p3, p3*p1, p3*p1**2, p3**p2, p3*p2*p1, p3*p2**2, p3**2,
                    p3**2*p1, p3**2*p2, p4, p4*p1, p4*p1**2, p4*p2, p4*p2*p1, p4*p2**2, p4*p3, p4*p3*p1, p4*p3*p2, p4*p3**2, p4**2, p4**2*p1,
                    p4**2*p2, p4**2*p3, p5, p5*p1, p5*p1**2, p5*p2, p5*p2*p1, p5*p2**2, p5*p3, p5*p3*p1, p5*p3*p2, p5*p3**2, p5*p4, p5*p4*p1,
                    p5*p4*p2, p5*p4*p3, p5*p4**2, p5**2, p5**2*p1, p5**2*p2, p5**2*p3, p5**2*p4, 1, p5**3, p4**3, p3**3, p2**3, p1**3]
        paras = [p1, p2, p2*p1, p3, p3*p1, p3*p2, p4, p4*p1, p4*p2, p4*p3, p5, p5*p1, p5*p2, p5*p3, p5*p4, 1, p5**2, p4**2, p3**2, p2**2,p1**2]
        if self.Nef == 12:
            coeffs = [
                [3.88E-06, 9.94537509, -6.60E-06, 0.02081813, -5.88E-08, 0.00382407, 4.63E-06, 7.68E-13, -6.27E-07, 3.70E-08, -0.02673288, 1.87E-08, -0.00525926, -2.94E-05, -6.87E-08, 7.89712504, 0.0001129, 4.78E-12, -0.00012154, -7.46728395, -1.26E-12],
                [-1.89E-05, -42.7147269, 4.46E-05, -0.09264028, 3.72E-07, 0.05007407, 0.0012586, -1.48E-10, -0.00041252, -2.30E-06, 0.18383092, -1.25E-07, -0.05408333, 0.00036713, 2.31E-06, 3.24567278, -0.00117469, -1.10E-10, 0.00068253, 54.1938272, 1.35E-11],
                [1.36E-06, 0.39846, -1.59E-05, -0.05117797, -6.68E-08, 0.00298148, -1.40E-05, -3.43E-13, -2.45E-06, 1.00E-07, 0.11720644, -6.30E-08, 0.00010185, -0.00019016, 1.65E-07, -2.6717911, -0.00020008, -3.20E-11, -0.00029527, -0.38061728, -5.07E-11]
                ]
            
            qf_coeffs = [0.043289853, -1.02E-06, 0, 0.00346228, -1.95E-09, 0, -0.004132482, 0, 6.93E-06, -9.32E-12, 0, -1.01E-05, 0, 0, -7.28E-08, 0, 0, -1.63E-07, 5.76E-14, -0.814943893, 1.97E-07, 0.671904382, -3.18E-07, 7.87E-11, 1.38E-06, 2.06E-08, 9.15E-06, -1.03E-15, -4.00E-10, 2.95E-12, 0, 8.91E-07, -3.70E-11, 0, 3.38E-06, 0, -0.004071561, 1.91E-08, 0.005631214, -5.83E-05, -1.13E-05, -1.51E-12, 9.35E-06, -6.55E-08, -9.72E-12, 0.000991866, 4.94E-09, -0.002346965, 2.65E-05, 3.89E-08, 0, -5.75E-06, -5.98E-11, 9.80E-05, 0, 7.56E-12]

        if self.Nef == 14:
            coeffs = [
                [5.09E-06, 12.5382496, -9.14E-06, 0.02337875, -9.14E-08, 0.00388889, 5.35E-06, 6.30E-13, -5.29E-07, 4.37E-08, -0.02950567, 3.09E-08, -0.0062037, 3.36E-18, -8.05E-08, 8.60476584, 0.00011852, 5.63E-12, -0.00017037, -9.33333333, -3.29E-12],
                [-2.16E-05, -43.3374773, 5.12E-05, -0.0844156, 4.36E-07, 0.04958333, 0.00112458, -1.31E-10, -0.0004077, -1.97E-06, 0.16401696, -1.47E-07, -0.04817593, 0.00017259, 2.01E-06, 4.02589763, -0.00101407, -9.88E-11, 0.00074556, 54.0981481, 1.56E-11],
                [1.53E-06, 0.58337733, -1.64E-05, -0.04490381, -7.16E-08, 0.00127685, -1.01E-05, 1.11E-13, -1.75E-06, 7.31E-08, 0.09611935, -6.41E-08, -0.00077222, -0.00013631, 1.19E-07, -2.18700134, -0.00014286, -2.31E-11, -0.00025182, -0.47691358, -5.10E-11]
                ]

            qf_coeffs = [0.043302615, -1.01E-06, 0, 0.003420977, -2.32E-09, 0, -0.004143076, 0, 8.29E-06, -1.81E-11, 0, -9.32E-06, 0, 0, -4.07E-08, 0, 0, -1.64E-07, 5.82E-14, -0.81504284, 1.97E-07, 0.67213148, -1.80E-06, 8.33E-11, 1.33E-06, 2.02E-08, 9.15E-06, 1.00E-15, -5.48E-11, 4.08E-12, 0, -6.41E-06, 2.02E-11, 0, 4.23E-06, 0, -0.00472654, -1.18E-08, 0.005339018, 7.19E-05, -8.87E-06, 3.97E-12, 7.45E-06, -5.27E-08, -7.48E-12, 0.003005769, 2.04E-08, -0.00235648, -1.52E-06, 2.72E-08, 0, -1.44E-05, -5.98E-11, -5.11E-05, 0, 7.49E-12]
            
            
        if self.Nef == 16:
            coeffs = [
                [4.38E-06, 12.7628206, -8.62E-06, 0.02240759, -8.28E-08, 0.00364815, -7.01E-05, 5.17E-13, -1.99E-05, 2.28E-08, -0.02745567, 3.23E-08, -0.0057963, 8.80E-06, -4.89E-08, 9.81244591, 9.77E-05, 5.43E-10, -0.00016377, -8.80432099, -2.25E-12],
                [-1.89E-05, -42.6863898, 4.48E-05, -0.09177962, 3.74E-07, 0.0502037, 0.00127438, -1.49E-10, -0.0004128, -2.31E-06, 0.18307881, -1.26E-07, -0.05415741, 0.00036463, 2.32E-06, 2.72511178, -0.00117346, -2.16E-10, 0.00068451, 54.1839506, 1.39E-11],
                [1.24E-06, 0.40745493, -1.62E-05, -0.03508409, -6.90E-08, 0.00286019, 1.00E-06, 3.67E-12, -2.24E-06, -1.02E-07, 0.09919098, -6.37E-08, 9.81E-05, -0.00018564, 3.80E-07, -2.61290998, -0.00020005, -2.06E-10, -0.0002832, -0.39753086, -5.09E-11]
                ]
            
            qf_coeffs = [0.043271339, -1.02E-06, 0, 0.003467941, -2.10E-09, 0, -0.004128463, 0, 6.90E-06, -8.36E-12, 0, -1.00E-05, 0, 0, -7.51E-08, 0, 0, -1.63E-07, 5.66E-14, -0.814945185, 1.97E-07, 0.671902186, -3.50E-07, 7.89E-11, 1.35E-06, 2.12E-08, 9.15E-06, -1.08E-15, -4.37E-10, 2.75E-12, 0, 8.18E-07, -4.03E-11, 0, 3.44E-06, 0, -0.004003383, 1.93E-08, 0.005621816, -5.45E-05, -1.17E-05, -1.89E-12, 9.49E-06, -6.51E-08, -9.22E-12, 0.001211251, 7.41E-09, -0.002442261, 2.45E-05, 4.06E-08, 0, -7.46E-06, -5.98E-11, 9.48E-05, 0, 7.56E-12]
            
        self.GOR = np.dot(paras,coeffs[0])
        self.qs = np.dot(paras,coeffs[1])
        self.DELTAT = np.dot(paras,coeffs[2]) # the difference between the condensation temperature in the evaporator and the vapor temperature in such effect
        
        self.qF = np.dot(qF_paras, qf_coeffs)
        
        self.STEC = 1/self.GOR * (TD_func.enthalpySatVapTW(self.Ts+273.15)-TD_func.enthalpySatLiqTW(self.Ts+273.15))[0] *1000/3600
        self.P_req = 1/self.GOR * (TD_func.enthalpySatVapTW(self.Ts+273.15)-TD_func.enthalpySatLiqTW(self.Ts+273.15))[0] *self.Capacity *1000/24/3600
        
        # self.system = lt_med_calculation(Nef = self.Nef, Ts = self.Ts, Ms = self.qs, Mf = self.qF, Tcwin = self.Tin)
        # self.system.model_execution() 
        # print('calculated STEC:', system.STE)
        # print('calculated GOR:', system.GOR)
        # print('calculated production:', system.Mprod_m3_day)
        
        from DesalinationModels.LTMED_cost import LTMED_cost
        lcow = LTMED_cost(STEC = self.STEC )
        
        self.design_output = []
#        design_output.append({'Name':'Number of modules required','Value':self.num_modules,'Unit':''})
#        design_output.append({'Name':'Permeate flux of module','Value':self.Mprod,'Unit':'l/h'})
#        design_output.append({'Name':'Condenser outlet temperature','Value':self.TCO,'Unit':'oC'})
#        design_output.append({'Name':'Permeate flow rate','Value': self.F * self.num_modules,'Unit':'l/h'})    
        self.design_output.append({'Name':'Thermal power consumption','Value':self.P_req / 1000,'Unit':'MW(th)'})
        self.design_output.append({'Name':'Specific thermal power consumption','Value':self.STEC,'Unit':'kWh(th)/m3'})
        self.design_output.append({'Name':'The mass flow rate of the steam','Value':self.qs,'Unit':'kg/s'})
        self.design_output.append({'Name':'Gained output ratio','Value':self.GOR,'Unit':''})  
        self.design_output.append({'Name':'Delta T','Value':self.DELTAT,'Unit':'oC'})
        if self.DELTAT < 2:
            self.design_output.append({'Name':'Warning','Value':'Delta T is too small, cost might be high','Unit':''})
        
        
        
        
        # self.design_output.append({'Name':'Specific heat exchanger area','Value':self.system.sA,'Unit':'m2/(kg/s)'}) 
        
        return self.design_output
    
    # class variables
#    DELTAT_loss = 0.05
#

#    def __init__(self,
#                 Tb1      = 76     , # The brine temperature in the first effect, ºC
#                 FeedC_r  = 35  , # The feed water salinity, ppm
#                 Ms       = 1.023  , # The mass flow rate of the steam entering the bundle tube of the first effect, kg/s
#                 Ts       = 80     , # The temperature of the steam at the inlet of the first bundle tube, ºC
#                 Tcwin    = 25     , # Seawater inlet temperature in the condenser, ºC
#                 DELTATcw = 7.3    , # The temperature difference between the inlet and outlet seawater temperature in the condenser, ºC
#                 Mf       = 38.27  , # Feed water mass flow rate sprayed on the bundle tube, kg/s
#                 Nef      = 16     , # Number of effects
#                 Nph      = 15     , # Number of preheaters
#                 Cp       = 4.18   , # Specific heat of distillate, feed and brine, that is considered. [J/(kg C)]
#                 BPE      = 0.5    , # The Boiling Point Elevation, ºC
#                 NEA      = 0.5    , # The Non Equilibrium Allowance, ºC
#                 Tol      = 0.0001 , # The tolarance applied to get equal area in the effects)
#                 Capacity = 971.96,    # Capacity of the plant (m3/day)
#                 storage_hour = 6, # Thermal storage hour (hr)
#                 Fossil_f = 1 # Fossil fuel fraction
#                 ):
#        
#        self.Tb1 = Tb1 
#        self.FeedC_r = FeedC_r *1000
#        self.Ms = Ms
#        self.Ts = Ts 
#        self.Tcwin = Tcwin 
#        self.DELTATcw = DELTATcw 
#        self.Mf = Mf
#        self.Nef = Nef
#        self.Nph = Nph
#        self.Cp = Cp
#        self.BPE = np.zeros(self.Nef)
#        self.NEA = np.zeros(self.Nef)
#        self.Tol = Tol
#        
#        # ASSUMPTIONS. They keep constant during the calculations
#        self.Tb = np.zeros(Nef) 
#        self.Tv = np.zeros(Nef)
#        self.DTb = np.zeros(Nef)
#        self.Tdb = np.zeros(Nef)
#        self.Tph = np.zeros(Nef)
#        
#        self.Tb[0] = self.Tb1 # The brine temperature in the first effect, ºC
#        self.Tb_last = 37  # Brine temperature in the last effect, ºC
#        self.Tv[0] = self.Tb1 - BPE - self.DELTAT_loss # The vapor temperature inside the first effect, ºC
#        self.Tf    = self.Tb1 -3 # The feed water temperature sprayed in the first effect, ºC
#        self.Tcwout= self.Tcwin + self.DELTATcw  # The seawater outlet temperature of the condenser, ºC
#        self.Tph[0] = self.Tf
#        self.Length_ef = 0.5 # Length of the tubes in the effects tube bundle, m
#        self.Length_ph = 0.75 * self.Length_ef # Lenghth of the tubes in the preheaters tube bundle, m
#        self.Length_c  = 1.5  * self.Length_ef # Length of the tubes in the condenser tube bundle, m
#        self.Di = 0.0254 # Inner diameter of the tubes in the bundle tubes, m
#        self.BPE[0] = BPE
#        self.NEA[0] = NEA
#
#        for i in range(self.Nef-1):
#            # Calculate the vapor temperature in each effect, ºC
#            self.BPE[i+1] = BPE
#            self.NEA[i+1] = NEA
#            self.Tb[i+1] = self.Tb[i] - (self.Tb[0]-self.Tb_last) / (self.Nef -1)
#            # Calculate the temperature of the brine after flashing process from effects 2 to Nef, Tdb(2,1), ºC
#            self.Tv[i+1] = self.Tb[i+1] - self.BPE[i+1] - self.DELTAT_loss
#            self.DTb[i+1] = self.Tb[i] - self.Tb[i+1]
#            self.Tdb[i+1] = self.Tv[i+1] - self.NEA[i]
#            # Calculate the seawater temperature in the preheater, Tph(i,1), ºC
#            self.Tph[i+1] = self.Tph[i] - (self.Tph[0] - self.Tcwout) / self.Nph
#
#    # PREHEATER calculations
#        # Calculations in the prehater:
##        % Calculate the seawater temperature in the preheater, Tph(i,1), ºC
##        % Calculate the feed water mass flow rate sprayed on the bundle tube, Mf, kg/s
##        % Calculate the vapor consumed in each preheater, Mvh(i,1), kg/s
##        % Calculate the heat transfer rate in the preheaters, Qph(i,1), kJ/s
##        % Calculate the overall heat transfer coefficient of the preheaters, Uph(i,1), kW/m2ºC. Correlation of El-Dessouky
##        % Calculate the condensate generated in the preheater,Mdh(i,1), kg/s
##        % Calculate the heat transfer area of the preheaters, Aph(i,1), m2
##        % Evh(i,1) is the enthalpy of the vapor that enters the preheater, kJ/kg
##        % Elh(i,1) is the enthalpy of the condensate that leaves the preheater, kJ/kg
##        % Lvh(i,1) is the latent heat of the vapor in the preheater, kJ/kg
##        % LTMDph (i,1)is the log mean temperature difference, ºC 
#    def design(self):
#        
#        self.Evh = np.zeros(self.Nph)
#        self.Elh = np.zeros(self.Nph)
#        self.Lvh = np.zeros(self.Nph)
#        self.Mvh = np.zeros(self.Nph)
#        self.Mdh = np.zeros(self.Nph)
#        self.Qph = np.zeros(self.Nph)
#        self.Uph = np.zeros(self.Nph)
#        self.LTMDph = np.zeros(self.Nph)
#        self.Aph = np.zeros(self.Nph)
#        
#        for i in range(self.Nph):
#            self.Evh[i] = TD_func.enthalpySatVapTW(self.Tv[i]+273.15) 
#            self.Elh[i] = TD_func.enthalpySatLiqTW(self.Tv[i]+273.15) 
#            self.Lvh[i] = self.Evh[i] -self.Elh[i] 
#            self.Mvh[i] = self.Mf * self.Cp * (self.Tph[i] - self.Tph[i+1]) / self.Lvh[i] 
#            self.Mdh[i] = self.Mvh[i] 
#            self.Qph[i] = self.Mf * self.Cp * (self.Tph[i] - self.Tph[i+1]) 
#            self.Uph[i] = 1.7194 + (3.2063e-3 * self.Tv[i]) + (1.5971e-5 * self.Tv[i]**2) - (1.9918e-7 * self.Tv[i]**3) 
#            self.LTMDph[i] = ((self.Tv[i] - self.Tph[i+1]) - (self.Tv[i] - self.Tph[i])) / math.log( (self.Tv[i] - self.Tph[i+1]) / (self.Tv[i] - self.Tph[i]) ) 
#            self.Aph[i] = self.Qph[i] / self.Uph[i] / self.LTMDph[i] 
#        
#    # FIRST EFFECT & OTHER EFFECTS calculations
##        % Definition of the variables used and calculated:
##
##        % Aef(i,1) is the heat transfer area of the bundle tube of each effect, m2
##        % Mgb(i,1) is the mass flow rate of the vapor generated by boiling, kg/s
##        % Mdf(i,1) is the mass flow rate of the vaspor generated by flash of the distillate in the
##        % flash box, kg/s
##        % Mgt(i,1) is the sum of the mass flow rate of total vapor leaving each
##        % effect plus vapor generated by flash in the flash box, kg/s
##        % Mv(i,1) is the vapor mass flow rate entering the bundle tube of each effect, kg/s
##        % Egv(i,1) is the enthalpy of the vapor entering the bundle tube of each effect, kJ/kg
##        % Egl(i,1) is the enthalpy of the condensate leaving the bundle tube of each effect, kJ/kg
##        % Lv(i,1) is the latent heat of the vapor entering the bundle tube of each effect, kJ/kg
##        % Lgf(i,1) is the latent heat of the vapor generated by flashing of the brine in each effect, kJ/kg
##        % Lgb(i,1) is the latent heat of the vapor generated by boiling of the brine in each effect, kJ/kg
##        % Mgf(i,1) is the mass flow rate of the vapor generated by flashing of the brine in each effect, kg/s
##        % Mfv(i,1) is the mass flow rate of the vapor generated in each effect (by boiling and flashing), kg/s
##        % Mdb(i,1) is the mass flow rate of the brine after flashing, kg/s
##        % Xdb is the salinity of the brine after flashing, ppm
##        % Md(i,1) is the distillate mass flow rate leaving each flash box, kg/s
##        % Mdaf(i,1) is the distillate mass flow rate leaving each effect, kg/s
##        % Uef(i,1) is the overall heat transfer coefficient of each effect, kW/m2ºC
##        % Mb(i,1) is the mass flow rate of the brine that leaves each effect mass flow rate, kg/s
##        % Xb(i,1) is the salinity of the brine leaving each effect, ppm 
#        
#        self.Egs = TD_func.enthalpySatVapTW(self.Ts+273.15) 
#        self.Els = TD_func.enthalpySatLiqTW(self.Ts+273.15) 
#        self.Ls = self.Egs - self.Els
#        self.Qs = self.Ms * self.Ls
#        self.Qef = np.zeros(self.Nef)
#        self.Qef[0] = self.Qs
#        self.max_DA = 20
#        self.Egbg = np.zeros(self.Nef)
#        self.Egbl = np.zeros(self.Nef)
#        self.Lgb  = np.zeros(self.Nef)
#        self.Uef  = np.zeros(self.Nef)
#        self.Mgb  = np.zeros(self.Nef)
#        self.Aef  = np.zeros(self.Nef)
#        self.Lv   = np.zeros(self.Nef)
#        self.Mgf  = np.zeros(self.Nef)
#        self.Mdf  = np.zeros(self.Nef)
#        self.Md   = np.zeros(self.Nef)
#        self.Mdb  = np.zeros(self.Nef)
##        self.DTb  = np.zeros(self.Nef)
#        self.Mfv  = np.zeros(self.Nef)
#        self.Mgt  = np.zeros(self.Nef)
#        self.Mb   = np.zeros(self.Nef)
#        self.Xb   = np.zeros(self.Nef)
#        
#        self.Mv   = np.zeros(self.Nef)
#        self.Mdaf = np.zeros(self.Nef)
#        self.Egv  = np.zeros(self.Nef)
#        self.Egl  = np.zeros(self.Nef)
#        self.Lgf  = np.zeros(self.Nef)
#        self.Lgb  = np.zeros(self.Nef)
#        self.Xdb  = np.zeros(self.Nef)
#        self.Uef  = np.zeros(self.Nef)
#        self.Ldf  = np.zeros(self.Nef)
#        self.Xb_w = np.zeros(self.Nef)
#        self.A    = np.zeros(self.Nef)
#        self.B    = np.zeros(self.Nef)
#        self.C    = np.zeros(self.Nef)
#        self.DA   = np.zeros(self.Nef)
#        
#        self.Mgf[0] = 0
#        self.Mdf[0] = 0
#        self.Md[0]  = 0
#        self.Mdb[0] = 0
#        self.DTb[0] = self.Ts - self.Tb[0]
#        self.count = 0
#        
#        while self.max_DA > self.Tol:
#            # Set up for the first effect
#            self.Egbg[0] = TD_func.enthalpySatVapTW(self.Tv[0]+273.15)
#            self.Egbl[0] = TD_func.enthalpySatLiqTW(self.Tv[0]+273.15)
#            self.Lgb[0]  = self.Egbg[0] - self.Egbl[0]
#            self.Uef[0]  = 1.9695 + (1.2057e-2  * self.Tb[0]) - (8.5989e-5 * self.Tb[0]**2) + (2.5651e-7 * self.Tb[0]**3)
#            self.Mgb[0]  = (self.Qef[0] - self.Mf * self.Cp * (self.Tb[0] - self.Tf)) / self.Lgb[0]
#            self.Aef[0]  = self.Qef[0] / (self.Uef[0] * (self.Ts - self.Tb[0]))
#            self.Lv[0]   = self.Lgb[0]
#            self.Mfv[0]  = (self.Mgb[0] + self.Mgf[0]) * 3600
#            self.Mgt[0]  = (self.Mgb[0] + self.Mgf[0] + self.Mdf[0])
#            self.Mb[0]   = self.Mf - self.Mgb[0]
#            self.Xb[0]   = self.FeedC_r * self.Mf / self.Mb[0]
#            
#            self.Sum_A = self.Aef[0]
#            
#            # Other effects calculations
#            
#            for i in range(1, self.Nef):
#                self.Mv[i]   = self.Mgt[i-1] - self.Mvh[i-1]
#                self.Mdaf[i] = self.Mv[i]
#                self.Egv[i]  = TD_func.enthalpySatVapTW(self.Tv[i]+273.15)
#                self.Egl[i]  = TD_func.enthalpySatLiqTW(self.Tv[i]+273.15)
#                self.Lv[i]   = self.Egv[i] - self.Egl[i]
#                self.Lgf[i]  = self.Lv[i]
#                self.Lgb[i]  = self.Lv[i]
#                self.Mgf[i]  = self.Mb[i-1] * self.Cp *(self.Tb[i-1] - self.Tdb[i]) / self.Lgf[i]
#                self.Mdb[i]  = self.Mb[i-1] - self.Mgf[i]
#                self.Xdb[i]  = self.Xb[i-1] * self.Mb[i-1] / self.Mdb[i]
#                self.Mgb[i]  = (self.Mv[i] * self.Lv[i-1] + self.Mdb[i] *self.Cp * (self.Tdb[i] - self.Tb[i])) / self.Lgb[i]
#                self.Mfv[i]  = (self.Mgb[i] + self.Mgf[i]) *3600
#                self.Qef[i]  = self.Mv[i] * self.Lv[i-1]
#                self.Uef[i]  = 1.9695 + (1.2057e-2 * self.Tb[i]) - (8.5989e-5 * self.Tb[i]**2) + (2.5651e-7 * self.Tb[i]**3)
#                self.Mb[i]   = self.Mdb[i] - self.Mgb[i]
#                self.Xb[i]   = self.Mdb[i] * self.Xdb[i] / self.Mb[i]
#                self.Ldf[i]  = self.Lv[i]
#                self.Mdf[i]  = (self.Mdh[i-1] * self.Cp * (self.Tv[i-1] - self.Tv[i]) + (self.Mdaf[i-1] * self.Cp * (self.Tv[i-1] - self.Tv[i])) + self.Md[i-1] * self.Cp * (self.Tv[i-1] - self.Tv[i]) ) / self.Ldf[i]
#                self.Mgt[i]  = self.Mgb[i] + self.Mgf[i] + self.Mdf[i] 
#                self.Md[i]   = self.Mdaf[i] + self.Mdh[i-1] + self.Md[i-1] - self.Mdf[i]
#                self.Aef[i]  = self.Qef[i] / self.Uef[i] / (self.Tv[i-1] - self.Tb[i])
#                
#                self.Sum_A += self.Aef[i]
#                
#            self.Am = self.Sum_A / self.Nef
#            self.DTb[0] *= (self.Aef[0] / self.Am)
#            self.Tb[0]   = self.Ts - self.DTb[0] 
#            self.Xb_w[0] = self.Xb[0] / (1000*1000) *100 # Salinity in weigth percentage
#            self.A[0]    = 8.325e-2 + (1.883e-4 * self.Tb[0]) + (4.02e-6 * self.Tb[0]**2)
#            self.B[0]    = -7.625e-4 + (9.02e-5 * self.Tb[0]) - (5.2e-7 * self.Tb[0]**2)
#            self.C[0]    = 1.552e-4- (3e-6 * self.Tb[0]) - (3e-8 * self.Tb[0]**2)
#            self.BPE[0]  = self.A[0] * self.Xb_w[0] + self.B[0] * self.Xb_w[0]**2 + self.C[0] * self.Xb_w[0]**3
#            self.Tv[0]   = self.Tb[0] - self.BPE[0] - self.DELTAT_loss
#            self.Uef[0]  = 1.9695 + (1.2057e-2  * self.Tb[0]) - (8.5989e-5 * self.Tb[0]**2) + (2.5651e-7 * self.Tb[0]**3)
#            
#            for i in range(1, self.Nef):
#                self.DTb[i] *= self.Aef[i] / self.Am
#                self.Tb[i]  = self.Tb[i-1] -self.DTb[i]
#                self.Xb_w[i] = self.Xb[i] / (1000*1000) *100
#                self.A[i]    = 8.325e-2 + (1.883e-4 * self.Tb[i]) + (4.02e-6 * self.Tb[i]**2)
#                self.B[i]    = -7.625e-4 + (9.02e-5 * self.Tb[i]) - (5.2e-7 * self.Tb[i]**2)
#                self.C[i]    = 1.552e-4- (3e-6 * self.Tb[i]) - (3e-8 * self.Tb[i]**2)
#                self.BPE[i]  = self.A[i] * self.Xb_w[i] + self.B[i] * self.Xb_w[i]**2 + self.C[i] * self.Xb_w[i]**3
#                self.NEA[i]  = 33 * self.DTb[i]**0.55 / self.Tv[i]
#                self.Tv[i]   = self.Tb[i] - self.BPE[i] - self.DELTAT_loss
#                self.Tdb[i]  = self.Tv[i] - self.NEA[i]
#                self.DA[i]   = abs(self.Aef[i-1] - self.Aef[i])
#            
#            self.count += 1
#            self.max_DA = max(self.DA)
#        
#        self.Nt_ef = np.zeros(self.Nef)
#        for i in range(self.Nef):
#            self.Nt_ef[i] = self.Aef[i] / (math.pi * self.Length_ef *self.Di)
#            
#    # CONDENSER calculations
##        % CONDENSER
##        % Calculate the vapor entering the condenser, Mgt, kg/s
##        % Calculate the seawater flow rate flowing through the condenser, Mcw, kg/s
##        % Calculate the distillate produced in the condenser, Mdc, kg/s
##        % Calculate the heat transfer rate in the condenser, Qc, kW
##        % Calculate the heat transfer area of the condenser, Ac, m2 
#
#        self.Mgt[self.Nef-1] = (self.Mgb[self.Nef-1] + self.Mgf[self.Nef-1] + self.Mdf[self.Nef-1]) / 0.99
#        self.Lgt = self.Lv[self.Nef-1]
#        self.Qc  = self.Mgt[self.Nef-1] * self.Lgt
#        self.Mcw = self.Qc / self.Cp / (self.Tcwout - self.Tcwin)
#        self.Mdc = self.Mgt[self.Nef-1]
#        self.LTMDc = ((self.Tv[self.Nef-1] - self.Tcwin) - (self.Tv[self.Nef-1] - self.Tcwout)) / math.log( (self.Tv[self.Nef-1] - self.Tcwin) / (self.Tv[self.Nef-1] - self.Tcwout) ) 
#        self.Uc  = 1.7194 + (3.2063e-3 * self.Tv[self.Nef-1]) + (1.5971e-5 * self.Tv[self.Nef-1]**2) - (1.9918e-7 * self.Tv[self.Nef-1]**3) 
#        self.Ac  = self.Qc / self.Uc / self.LTMDc
#        self.Nt_c= self.Ac / (math.pi * self.Length_c * self.Di)
#    
#    # MIXTURE OF DISTILLATES  
#
##% Calculate the final production, Mprod
##% Calculate the temperature of the distillate production, Tprod, ºC
#        self.Tvc = self.Tv[self.Nef-1] - self.DELTAT_loss
#        self.Mprod = self.Md[self.Nef-1] + self.Mdc  #kg/s
#        self.Tprod = (self.Md[self.Nef-1] * self.Tv[self.Nef-1] + self.Mdc * self.Tvc) / self.Mprod
#        
#        self.DELTAT_final = np.zeros(self.Nef-1)
#        for i in range(self.Nef-1):
#            self.DELTAT_final[i] = self.Tb[i] -self.Tb[i+1]
#        
#        self.STE = self.Qef[0] / self.Mprod / 3.6
#        self.GOR = self.Mprod / self.Ms
#        self.Mprod_m3_day = self.Mprod * 24 * 3.6  # m3/day
#        self.RR = self.Mprod / self.Mf
#        
##    % MIXER (mixture of brine, distillate product and rejected seawater)
##    % Calculate the temperature after the mixer, Tmix, ºC
##    % Mrej is the flow rate of the rejected seawater from the condenser, kg/s
#        self.Mr = self.Mcw - self.Mf
#        self.Tm = (self.Mb[self.Nef-1] * self.Tb[self.Nef-1] + self.Mprod * self.Tprod + self.Mr * self.Tcwout) / self.Mcw
#        self.Mbf = self.Mb[self.Nef-1] + self.Mr
#        self.Xbf = self.Xb[self.Nef-1] * self.Mb[self.Nef-1] / self.Mbf
#        
#       # % Specific heat transfer area, m2/m3/d
#        self.sum_A = sum(self.Aef)
#        self.sum_Aph = sum(self.Aph)
#        self.sA = (self.sum_A + self.sum_Aph + self.Ac) / self.Mprod
#       
#                
#        self.ThPower = self.STE * self.Mprod * 3.6  # (kW)
#        self.F = self.Mprod * 3.6 
        
        

    
    def simulation(self, gen, storage):
        self.thermal_load = self.P_req # kW
        self.max_prod = self.Capacity /24 # m3/h
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
        simu_output.append({'Name':'Solar energy curtailment','Value':solar_loss,'Unit':'kWh'})
               
        return simu_output
            
#%% MODEL EXECUTION            

# case = lt_med_general(Xf = 30000, RR = 0.5, Tin = 15, Capacity = 1000, Ts = 80, Nef = 12)
# case.design()
# print(case.design_output)
#case.simulation(gen = [5000,6000,5000,3000,2500], storage =6)
            
        
        