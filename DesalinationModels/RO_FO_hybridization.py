   # -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:35:50 2019
@author: zzrfl
"""

from DesalinationModels.RO_Fixed_Load import RO
from DesalinationModels.FO_Generalized import FO_generalized


# def RO_FO(capacity, RO_rr, FO_rr, salinity, T_sw, FO_salt_rej  ):
# # Initiate calculation from RO designing
#     RO_case = RO(T = T_sw, nominal_daily_cap_tmp=capacity, R1=RO_rr, FeedC_r = salinity)
#     RO_case.RODesign()
#     # Retreive system performance from RO model
#     RO_feed = RO_case.Qf1*24
#     RO_brine = RO_case.Qb1*24
#     RO_permeate = RO_case.Qp1*24
#     RO_p_s = RO_case.Cp *1000
#     RO_brine_salinity = (RO_case.Cf * RO_feed - RO_case.Cp * RO_permeate)/ RO_brine  #  g/L 
    
    
#     # Initiate calculation in FO model
#     FO_Mprod = RO_brine * FO_rr * (1-0.1)
    
#     FO = FO_generalized(Salt_rej = FO_salt_rej, T_sw = RO_case.T, FeedC_r = RO_brine_salinity, r=FO_rr, Mprod = FO_Mprod )
#     FO.FO_design()  

#     Thermal_load = FO.Thermal_power
#     STEC = FO.STEC
#     FO_p_s = (1-FO.Salt_rej) * RO_brine_salinity *1000 * RO_brine / FO_Mprod
#     FO_b_s =  RO_brine_salinity *1000 * RO_brine / (RO_brine - FO_Mprod)
    
#     result = [RO_case.PowerTotal, Thermal_load, FO_b_s, (FO_Mprod+RO_permeate)/RO_feed]
    
#     return result
    
    
    # print('Total feed water (m3/day): {:,.1f}'.format(RO_feed))
    # print('RO permeate (m3/day):  {:,.1f}'.format(RO_permeate))
    # print('RO permeate salinity (mg/L):  {:,.1f}'.format(RO_p_s))
    # print('RO brine  (m3/day): ', RO_brine)
    # print('RO brine salinity (mg/L): ', RO_brine_salinity*1000)
    
    # print('FO permeate (m3/day): ', FO_Mprod)
    # print('FO permeate salinity (mg/L): ', FO_p_s)
    # print('FO brine (m3/day): ', RO_brine - FO_Mprod)
    # print('FO brine salinity (mg/L): ', FO_b_s)
    # print('RO recovery rate: ', RO_permeate/RO_feed)
    # print('FO recovery rate: ', FO_Mprod/RO_brine)
    # print('System recovery rate: ', (FO_Mprod+RO_permeate)/RO_feed)
    # print('RO power consumption(kW): ', RO_case.PowerTotal)
    # print('FO thermal load (kW): ', Thermal_load)
    #specific power consumption, concentration of the brine,
#%%
# a = RO_FO(capacity= 1000, RO_rr=0.4, FO_rr=0.3, salinity=35, T_sw=15, FO_salt_rej =0.95)

def RO_FO (capacity = 1000, RO_rr=0.4, FO_rr=0.3, salinity=35, T_sw=15, FO_salt_rej =0.95):
    RO_capacity = capacity / (1 + (1-RO_rr)/RO_rr * FO_rr * 0.9)
    RO_case = RO(T = T_sw, nominal_daily_cap_tmp=RO_capacity, R1=RO_rr, FeedC_r = salinity) 
    RO_case.RODesign()
    # Retreive system performance from RO model
    RO_feed = RO_case.Qf1*24
    RO_brine = RO_case.Qb1*24
    RO_permeate = RO_case.Qp1*24
    RO_p_s = RO_case.Cp *1000
    RO_brine_salinity = (RO_case.Cf * RO_feed - RO_case.Cp * RO_permeate)/ RO_brine  #  g/L 
    FO_Mprod = capacity - RO_capacity
    
    FO = FO_generalized( T_sw = T_sw, FeedC_r = RO_brine_salinity, r=FO_rr, Mprod = FO_Mprod, Salt_rej = FO_salt_rej)
    FO.FO_design() 
    Thermal_load = FO.Thermal_power
    STEC = FO.STEC
    FO_p_s = (1-FO.Salt_rej) * RO_brine_salinity  * RO_brine / FO_Mprod
    FO_b_s = FO.Salt_rej * RO_brine_salinity  * RO_brine / (RO_brine - FO_Mprod)
              # RO power[0],      FO power[1],   , RO_bs[2]         , FO_bs[3],Recovery rate[4],           # RO permeate[5],  FO permeate[6],   Overall STEC,[7]             Overall SEC[8],                       ,[9]Feed water flowrate
    result = [RO_case.PowerTotal, Thermal_load[0], RO_brine_salinity, FO_b_s, (FO_Mprod+RO_permeate)/RO_feed,RO_capacity,     FO_Mprod,         STEC[0]*FO_Mprod/capacity,   RO_case.SEC_RO*RO_capacity/capacity,   RO_feed ]
    
    return result

#%%
#study on rr design
    
import matplotlib.pyplot  as plt
rr = [x for x in range(30,61,5)]

result = []
for r in rr:
    result.append(RO_FO(FO_rr=r/100))
    

elec = []
thermal = []
for r in range(len(rr)):
    elec.append(result[r][3])
    thermal.append(result[r][2])

# 2 curves
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

ax1.plot(rr, elec, 'g-')
ax2.plot(rr, thermal, 'b-')

ax1.set_xlabel('FO recovery rate(%)')
ax1.set_ylabel('FO brine salinity (g/L)', color = 'g')
ax2.set_ylabel('RO brine salinity (g/L)', color = 'b')
plt.show()  

# 1 curve
target = []

for r in range(len(rr)):
    target.append(result[r][4])

fig, ax1 = plt.subplots()

ax1.plot(rr, elec, 'g-')
ax1.plot(rr, thermal, 'b-')
ax1.set_xlabel('FO recovery rate(%)')
ax1.set_ylabel('Brine alinity (g/L)', color = 'g')
plt.show()

#%%
from mpl_toolkits.mplot3d import Axes3D  
import numpy as np
FO_rr = [x for x in range(30,51,5)]
RO_rr = [x for x in range(30,51,5)]

output1 = np.zeros([len(RO_rr),len(FO_rr)])
output2 = np.zeros([len(RO_rr),len(FO_rr)])
for t in range(len(RO_rr)):
    for ss in range(len(FO_rr)):       
        output1[t,ss] = RO_FO(RO_rr=RO_rr[t]/100, FO_rr=FO_rr[ss]/100)[7]
        output2[t,ss] = RO_FO(RO_rr=RO_rr[t]/100, FO_rr=FO_rr[ss]/100)[8]
        print(t,ss)

#%%
import matplotlib.pyplot as plt
fig = plt.figure()
X,Y = np.meshgrid(FO_rr,RO_rr)

x = []
y = []
result = []
for i in range(len(X)):
    for j in range(len(X[0])):
        x.append(X[i][j])

for i in range(len(Y)):
    for j in range(len(Y[0])):
        y.append(Y[i][j])
        
for i in range(len(output1)):
    for j in range(len(output1[0])):
        result.append(output1[i][j])



plt.scatter(x, y, c=result, s = 50)
plt.show()


#%%
ax = plt.axes(projection='3d')
X,Y = np.meshgrid(FO_rr,RO_rr)
X.astype('int')
Y.astype('int')

ax.contourf(X, Y, output2,100, cmap='viridis')
ax.set_xlabel('FO recovery rate (%)')
ax.set_ylabel('RO recovery rate (%)')
ax.set_zlabel('Overall SEC(kWh(e)/m3)')

ax.view_init(200,15)
fig
#%%

# study on feed salinity
ss = [x for x in range(10,62,5)]

result_salinity = []
for s in ss:
    result_salinity.append(RO_FO(salinity=s))
    

elec = []
thermal = []
for s in range(len(ss)):
    elec.append(result_salinity[s][3])
    thermal.append(result_salinity[s][2])

# 2 curves
fig, ax1 = plt.subplots()


ax1.plot(ss, elec, 'g-',label='FO brine salinity (g/L)')
ax1.plot(ss, thermal, 'b-',label='RO brine salinity (g/L)')

ax1.set_xlabel('Feed salinity (g/L)')
ax1.set_ylabel('Brine salinity (g/L)', color = 'g')
ax1.legend()
plt.ylim(0,140)
plt.show()  

# study on feed salinity
ss = [x for x in range(15,40,3)]

result_Ts = []
for s in ss:
    result_Ts.append(RO_FO(T_sw=s))
    

elec = []
thermal = []
for s in range(len(ss)):
    elec.append(result_Ts[s][7])
    thermal.append(result_Ts[s][8])

# 2 curves
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

ax1.plot(ss, elec, 'g-')
ax2.plot(ss, thermal, 'b-')

ax1.set_xlabel('Feed water temperature (oC)')
ax1.set_ylabel('FO STEC', color = 'g')
ax2.set_ylabel('RO SEC', color = 'b')
plt.show()  


