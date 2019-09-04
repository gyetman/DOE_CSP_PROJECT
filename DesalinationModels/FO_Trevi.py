# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 11:28:52 2019
Converted from an Excel Model developed by Trevi Systems Inc. and shared by 
Michael Greene, Director of Manufacturing

It's a model used to size heat exhcangeers for the systems, design
heat exchangers and system flows

@author: zzrfl
"""
import numpy as np
from scipy.interpolate import interp1d, griddata


class FO_Trevi(object):
    
    # Define input variables
    def __init__(self,
                 Mprod    = 1      , # Product water flow rate (m3/day)
                 NF_rcr   = 0.2    , # Nanofilter retentate recirculation rate 
                 RO_r     = 0.1    , # RO retentate reject rate
                 A        = 0.8    , # Percentage of pure draw in strong draw
                 p_margin = 0      , # Desired DP of strong draw over seawater osmotic pressure in psi
                 p_weak   = 545.35 , # Required polymer osmotic pressure in psi
                 DS_c_p   = [[3.23608, 30.32329, 84.258, 174.14918, 316.77652, 516.69451, 825.68047, 1344.052947, 1753.477316],[1.00258,10.055,19.9824,29.9461,40.0552,49.9181,60.0252,70.0398,72.9075]],
                 # Polymer concentration as function of osmotic pressure (look-up table)
                 r        = 0.3    , # Recovery rate
                 salinity = 0.034  , # Salinity (%)
                 hm       = 105    , # Heat of mixing per m3 of product water for swing (MJ)
                 DS_density = [[0,0.57492,1.01314,2.06163,4.00907,8.07857,10.29748,20.322,38.57126,56.59887,66.45577,71.81646,84.16594,100],[1000,1001,1001.4,1002.95,1005.6,1011.26,1013.99,1027.94,1053.67,1073.775,1080.52,1086.355,1083.684,1069.866]],
                 # Draw solution density as function of concentration
                 DS_heatcap    = [[0,30,45,60,85],[4.1855,3.332,2.852,2.569,2.205]], # Draw solution specific heat capacity
                 T_memb        = 14.6338, # Membrane temperature (deg C)
                 
                 # Seawater density look-up table
                 SW_d_temp  = [0,10,20,30,40,50,60,70,80,90,100,110,120],  # Temperature (deg C)
                 SW_d_salinity = [0,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12],
                 SW_d_density = [[999.8,1007.9,1016,1024,1032,1040,1048,1056.1,1064.1,1072.1,1080.1,1088.1,1096.2],
                                 [999.7,1007.4,1015.2,1023,1030.9,1038.7,1046.6,1054.4,1062.2,1070.1,1077.9,1085.7,1093.6],
                                 [998.2,1005.7,1013.4,1021.1,1028.8,1036.5,1044.1,1051.8,1059.5,1067.2,1074.9,1082.6,1090.3],
                                 [995.7,1003.1,1010.7,1018.2,1025.8,1033.4,1040.9,1048.5,1056.1,1063.6,1071.2,1078.7,1086.3],
                                 [992.2,999.7,1007.1,1014.6,1022.1,1029.5,1037,1044.5,1052,1059.4,1066.9,1074.4,1081.6],
                                 [988,995.5,1002.9,1010.3,1017.7,1025.1,1032.5,1039.9,1047.3,1054.7,1062.1,1069.5,1076.9],
                                 [983.2,990.6,998,1005.3,1012.7,1020,1027.4,1034.7,1042.1,1049.5,1056.8,1064.2,1071.5],
                                 [977.8,985.1,992.5,999.8,1007.1,1014.5,1021.8,1029.1,1036.5,1043.8,1051.2,1058.5,1065.8],
                                 [971.8,979.1,986.5,993.8,1001.1,1008.5,1015.8,1023.1,1030.5,1037.8,1045.1,1052.5,1059.8],
                                 [965.3,972.6,980,987.3,994.7,1002,1009.4,1016.8,1024.1,1031.5,1038.8,1046.2,1053.5],
                                 [958.4,965.7,973.1,980.5,987.9,995.2,1002.6,1010,1017.4,1024.8,1032.2,1039.6,1047],
                                 [950.9,958.3,958.8,973.2,980.6,988.1,995.5,1003,1010.4,1017.8,1025.3,1032.7,1040.2],
                                 [943.1,950.6,958.1,965.6,973.1,980.6,988.1,995.6,1003.1,1010.6,1018.1,1025.6,1033.1]],
                 
                 # Seawater specific heat capacity look-up table
                 SW_cp_temp  = [0,10,20,30,40,50,60,70,80,90,100,110,120],
                 SW_cp_salinity = [0,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12],
                 SW_cp_cp =     [[4.2068,4.1421,4.0799,4.0201,3.9627,3.9078,3.9078,3.8052,3.7576,3.7124,3.6697,3.6293,3.5915],
                                 [4.1967,4.1367,4.0788,4.0228,3.9689,3.9169,3.9169,3.8192,3.7733,3.7295,3.6877,3.6479,3.6101],
                                 [4.1891,4.1326,4.0782,4.0253,3.9741,3.9245,3.9245,3.8304,3.7859,3.743,3.7018,3.6623,3.6245],
                                 [4.1839,4.1305,4.0785,4.0278,3.9786,3.9308,3.9308,3.8394,3.7958,3.7536,3.7127,3.6733,3.6353],
                                 [4.181,4.1297,4.0796,4.0307,3.9829,3.9364,3.9364,3.6467,3.8037,3.7618,3.7211,3.6816,3.6432],
                                 [4.1806,4.1308,4.0819,4.0341,3.9873,3.9415,3.9415,3.8529,3.8101,3.7683,3.7275,3.6878,3.649],
                                 [4.1827,4.1337,4.0855,4.0383,3.992,3.9465,3.9465,3.8583,3.8155,3.7737,3.7327,3.6926,3.6534],
                                 [4.1871,4.1365,4.0906,4.0436,3.9973,3.9519,3.9519,3.8636,3.8206,3.7785,3.7372,3.6967,3.657],
                                 [4.194,4.1453,4.0973,4.0501,4.0037,3.9581,3.9581,3.8692,3.8259,3.7835,3.7417,3.7008,3.6607],
                                 [4.2034,4.1542,4.1059,4.0583,4.0115,3.9654,3.9654,3.8757,3.832,3.7891,3.7469,3.7056,3.665],
                                 [4.2152,4.1654,4.1164,4.0682,4.0209,3.9743,3.9743,3.8836,3.8394,3.796,3.7535,3.7117,3.6708],
                                 [4.2294,4.1788,4.1291,4.0802,4.0322,3.9851,3.9851,3.8933,3.8486,3.8049,3.7619,3.7199,3.6786],
                                 [4.2461,4.1947,4.1442,4.0946,4.0459,3.9982,3.9982,3.9054,3.8603,3.8162,3.773,3.7307,3.6894]],

                 ):
        # Assign instance variables
        self.Mprod  = Mprod
        self.NF_rcr = NF_rcr
        self.RO_r   = RO_r
        self.A      = A
        self.p_margin = p_margin
        self.p_weak = p_weak
        self.DS_p   = DS_c_p[0]  # Osmotic pressure of draw solution (psi)
        self.DS_c   = DS_c_p[1]  # Polymer concentration in draw solution (wt%)
        self.r      = r
        self.salinity = salinity
        self.hm     = hm
        self.DS_c2  = DS_density[0] # Draw solution concentration list (wt%)
        self.DS_d   = DS_density[1] # Draw solution density list (kg/m3)
        self.DS_c3  = DS_heatcap[0] 
        self.DS_cp  = DS_heatcap[1] 
        self.SW_d_temp = SW_d_temp
        self.SW_d_salinity = SW_d_salinity
        self.SW_d_density = SW_d_density
        self.SW_cp_temp = SW_cp_temp
        self.SW_cp_salinity = SW_cp_salinity
        self.SW_cp_cp = SW_cp_cp
        self.T_memb = T_memb
        
        self.SW_d_points = []
        self.SW_d_values = []
        for temp in self.SW_d_temp:
            for s in self.SW_d_salinity:
                self.SW_d_points.append([temp,s])
        
        for i in range(len(self.SW_d_temp)):
            for j in range(len(self.SW_d_salinity)):
                self.SW_d_values.append(self.SW_d_density[i][j])
                
        self.SW_cp_points = []
        self.SW_cp_values = []
        for temp in self.SW_cp_temp:
            for s in self.SW_cp_salinity:
                self.SW_cp_points.append([temp,s])
        
        for i in range(len(self.SW_cp_temp)):
            for j in range(len(self.SW_cp_salinity)):
                self.SW_cp_values.append(self.SW_cp_cp[i][j])
        
    # 1-dimension interpolation (linear method)
    def OneDInterp(self, v, z):
        # To add: Raise exception for disordered array or z that is out of range
        if v == 'Draw concentration':
            v1 = self.DS_p
            v2 = self.DS_c
        elif v == 'Draw density':
            v1 = self.DS_c2
            v2 = self.DS_d 
        elif v == 'Draw cp':
            v1 = self.DS_c3
            v2 = self.DS_cp
        f = interp1d(v1, v2)
        return f(z)
    
    # 2-dimension interpolation (linear method)
    def TwoDInterp(self, v, z1, z2):
        if v == 'Seawater density':
            points = self.SW_d_points
            values = self.SW_d_values
        if v == 'Seawater Cp':
            points = self.SW_cp_points
            values = self.SW_cp_values
        
        return griddata(points, values, (z1, z2), method='linear')
        
    
    def flow_rate_calculations(self):
        
        self.RO_rf  = self.Mprod / (1/self.RO_r -1) # RO reject flow rate (m3/day)
        self.NF_pf  = self.Mprod + self.RO_rf       # Nanofilter permeate flow rate
        self.NF_rf  = self.NF_pf / (1/self.NF_rcr -1)  #Nanofilter rentate flow rate (m3/day)
        self.S      = self.Mprod + self.NF_rf + self.RO_rf  # Supernatant flow rate (m3/day)
        self.NF_rcc = self.S * 0.01 / self.NF_rf    # Nanofilter retentate polymer concentration       
        self.B      = self.OneDInterp('Draw concentration', self.p_weak) /100 # Percentage of pure draw in wak draw after membrane (%)
        self.SD_x   = self.B * self.NF_pf *(1-self.A) / (self.A - self.B) # Water in strong draw (m3/day)
        self.SD_y   = self.A * self.SD_x / (1-self.A)  # Pure draw in strong/weak draw (m3/day)
        self.SD     = self.SD_x + self.SD_y  #Strong draw (m3/day)
        self.WD_M_x = self.NF_pf + self.SD_x  # Water in weak draw after membrane (m3/day)
        self.WD_M   = self.WD_M_x + self.SD_y  # Weak draw after membrane (m3/day)
        self.WD_HX_x= self.WD_M_x + self.NF_rf * (1-self.NF_rcc)  # Water in weak draw through HXs (m3/day)
        self.WD_HX_y= self.SD_y + self.NF_rf * self.NF_rcc  # Pure draw in wak draw through HXs (m3/day)
        self.WD_HX  = self.WD_HX_x + self.WD_HX_y # Weak draw through HXs
        self.BHx    = self.WD_HX_y / self.WD_HX   # Percentage of pure draw in wak draw through HXs
        self.e      = self.NF_pf * (1- self.r)/self.r  # Water not recovered from seawater
        self.s      = (self.NF_pf + self.e) * self.salinity / (1-self.salinity) # Salt content in seawater
        self.sw     = self.NF_pf + self.e + self.s  # Seawater 
        self.e_s    = self.e + self.s  # Brine
        self.salinity_b = self.s / self.e_s # Salinity of brine (%)
#        self.p_b    = self.
        
    def membrane_heat_calculations(self):
        # To weak draw solution
        h_wd  = 0  # Heat transfered (MJ per m3/day)
        self.density_wd = self.OneDInterp('Draw density', self.B*100) # kg/m3
        f_wd = self.WD_M #m3/day
        self.cp_wd = self.OneDInterp('Draw cp', self.B*100)  # kJ/kg-deg C
        # To outgoing brine
        h_b   = self.hm # Heat transfered (MJ per m3/day)
        f_b = self.e_s # m3/day
        self.density_b = self.TwoDInterp('Seawater density', self.T_memb, self.salinity_b)  # kg/m3
        self.cp_b = self.TwoDInterp('Seawater Cp', self.T_memb, self.salinity_b)  # kJ/kg-deg C
        
        # Delta T in weak draw and brine
        dT_wd  = h_wd * 1000 / self.density_wd / f_wd / self.cp_wd
        dT_b   = h_b  * 1000 / self.density_b  / f_b  / self.cp_b
        i = 1
        # Modify the heat to weak draw to have the same Delta T in weak draw and brine
        while (abs(dT_wd - dT_b) > 0.0001):
            if dT_wd < dT_b:
                h_wd += self.hm / 2**i
            else:
                h_wd -= self.hm/ 2**i
            h_b  = self.hm - h_wd
            dT_wd  = h_wd * 1000 / self.density_wd / f_wd / self.cp_wd
            dT_b   = h_b  * 1000 / self.density_b  / f_b  / self.cp_b
            i += 1
        
        self.h_wd = h_wd
        self.h_b = h_b
        self.P_wd = h_wd *1000/24/3600
        self.P_b  = h_b *1000/24/3600
        
        # Nanofilter
        self.NF_cp = self.OneDInterp('Draw cp', self.NF_rcc*100) # Specific heat of nanofilter retentate
        self.NF_d  = self.OneDInterp('Draw density', self.NF_rcc*100) # kg/m3
#%%
case = FO_Trevi()
case.flow_rate_calculations()  
case.membrane_heat_calculations()      
        