"""
Created on Thu Mar 19 22:47:09 2020
Static Solar Collector class 

@author: zz
TO DO: 
-Need to modify fraccion_solar to take thermal storage as input. For now, placing thermal storage under simulation method,
but will change so that it can be executed as its own design method. 

@author: adama
"""
import pandas as pd
import numpy as np




class StaticCollector(object):

    def __init__(self,
                 # Design parameters
                 collector_type = '1',  # '1' for flat-plate collector and '2' for evacuated tube collector
                 design_point_date=[2010, 6 ,21 ,13, 0, 0], # design day/time
                 initial_date   = [2010, 3 ,18, 9, 0, 0], # initial design day/time
                 final_date     = [2010, 3, 18, 17, 0 ,0], # final design day/time
                 desal_thermal_power_req= 2.237, # (MW)thermal power that solar collector field must supply to desal plant
                 initial_water_temp=85, # inlet water temperature in the solar field, ºC
                 outlet_water_temp=95, # outlet water temperature in the solar field, ºC
                 cleanless_factor = 0.95,
                
                 qm=0.02,   # specific mass flow rate of collector (kg/s m2)
                 Tamb_D=30, # design point ambient temperature, C

                 
                 G=1000,    # irradiance from collector datasheet
                 a=0.83,    # Optical efficiency 
                 b=3.523,   # datasheet 
                 c=0.015,   # datasheet 
                 d=4.18189, # datasheet 
                 A=10.1,    # aperture area of collector from datasheet 
               
                 Long=-112.02, # Longitude
                 Lat=33.4,  # Latitude
                 file_name  = 'D:/PhD/DOE/DOE_CSP_PROJECT/SAM_flatJSON/solar_resource/USA AZ Phoenix Sky Harbor Intl Ap (TMY3).csv',
                
                 tilt_angle=36.838, # tilt angle of collector
                 v_azim=180,     # surface azimuth angle, 180 degrees facing south
                 Interv=60,      # temporal resolution of simulation/data in # of minutes
                 tiempo_oper=10, # daily operational availability of desal plant in hours
                 pressure=1,      # water pressure in the solar field, bar
                 v1 = 50,
                 v2 = 0.92,
                 # v1=[10 ,20 ,30, 40 ,50, 60, 70], # incidencee angles from datasheet
                 # v2=[1, 1, 0.99, 0.97, 0.92, 0.84 ,0.68],       # Longitudinal incidence angle modifiers from datasheet
                 # v3=[1.04 ,1.09 ,1.23 ,1.38 ,1.78, 1.82, 2.08] # Transversal incidence angle modifiers from datasheet
                 ):
        
        self.collector_type  = collector_type
        self.design_point_date=design_point_date
        self.initial_date   = initial_date
        self.final_date   = final_date
        self.desal_thermal_power_req   = desal_thermal_power_req *1000
        self.initial_water_temp = initial_water_temp
        self.outlet_water_temp = outlet_water_temp
        self.qm = qm 
        self.Tamb_D = Tamb_D
        self.G = G
        self.a = a
        self.b = b
        self.c=c
        self.d=d
        self.A=A
        self.Long=Long
        self.Lat=Lat
        self.tilt_angle=tilt_angle
        self.v_azim=v_azim
        self.Interv=Interv
        self.pressure=pressure
        self.v1=v1
        self.v2=v2
        self.weatherfile= file_name
        self.cleanless_factor = cleanless_factor
        
 #% 
    def design(self):
        datacols=list(range(0,14))
        data=pd.read_csv(self.weatherfile,skiprows=2,usecols=datacols)
        datacols=list(range(0,9))
        loc=pd.read_csv(self.weatherfile,nrows=1,usecols=datacols)    
        self.Lat = float(loc['Latitude'])
        self.Long = float(loc['Longitude'])

        row_temp_dif = self.outlet_water_temp - self.initial_water_temp
        T_in_ave = (self.initial_water_temp + self.outlet_water_temp) / 2
        
        row_design=data.loc[(data['Month']==self.design_point_date[1]) & (data['Day']==self.design_point_date[2]) & (data['Hour']==self.design_point_date[3])].index.values[0]
        T_amb = np.asarray(data['Tdry'])
        T_amb_design = T_amb[row_design]

# Update Gk (in-plate radiation)
        Gk = np.maximum(np.asarray(data['DNI']), np.asarray(data['GHI']))
        
        Gk_design = Gk[row_design]
        
        Month = [0,31,59,90,120,151,181,212,243,273,304,334,365]
        dayofyear = []
        B = []
        EOT = []
        TC = []
        HRA = []
        declination = []
        zenith = []
        azimuth = []
        aoi = []
        for i in range(len(data)):
# Get hour angle (radian)
            dayofyear.append(Month[data['Month'].iloc[i]-1] + data['Day'].iloc[i])
            B.append(360/365*(dayofyear[i]-81) * np.pi / 180)
            EOT.append(9.87*np.sin(2*B[i]) - 7.53*np.cos(B[i]) - 1.5*np.sin(B[i])) # min
            TC.append(4*(self.Long - int(self.Long / 15) * 15 ) + EOT[i])
            HRA.append(15* (data['Hour'].iloc[i] - 12 + TC[i]/60) * np.pi / 180)  
# Get declination angle (radian)
            declination.append(23.45 * np.sin(360/365*(dayofyear[i]-81)* np.pi / 180) * np.pi / 180 )
# Get zenith and azimuth angle (radian)
            if data['GHI'].iloc[i] > 0:
                zenith.append( np.pi/2 - np.arcsin(np.sin(declination[i]) * np.sin(self.Lat* np.pi / 180) + np.cos(declination[i]) * np.cos(self.Lat* np.pi / 180) * np.cos(HRA[i])))
                
                if HRA[i] < 0:
                    azimuth.append(np.arccos((np.sin(declination[i])*np.cos(self.Lat*np.pi/180)-np.cos(declination[i])*np.sin(self.Lat*np.pi/180)*np.cos(HRA[i]))/np.sin(zenith[i])))
                else:
                    azimuth.append(2*np.pi-np.arccos((np.sin(declination[i])*np.cos(self.Lat*np.pi/180)-np.cos(declination[i])*np.sin(self.Lat*np.pi/180)*np.cos(HRA[i]))/np.sin(zenith[i])))
                
                aoi.append(np.arccos(  np.sin(declination[i])*np.sin(self.Lat*np.pi/180)*np.cos(self.tilt_angle*np.pi/180) 
                                     + np.sin(declination[i])*np.cos(self.Lat*np.pi/180)*np.sin(self.tilt_angle*np.pi/180)*np.cos(azimuth[i])
                                     + np.cos(declination[i])*np.cos(self.Lat*np.pi/180)*np.cos(self.tilt_angle*np.pi/180)*np.cos(HRA[i])
                                     - np.cos(declination[i])*np.sin(self.Lat*np.pi/180)*np.sin(self.tilt_angle*np.pi/180)*np.cos(azimuth[i])*np.cos(HRA[i])
                                     - np.cos(declination[i])*np.sin(self.tilt_angle*np.pi/180)*np.sin(azimuth[i])*np.sin(HRA[i])))
                
            else:
                zenith.append( 0 )
                azimuth.append( 0 )
                aoi.append(0)
          
        # print(np.dot(aoi[0:24], 180/pi))
        
        self.mass_flow_design = self.qm * self.A
        aoi_design = aoi[row_design]
        b0 = (1-self.v2) / (1/np.cos(self.v1*np.pi/180)-1)
        aoi_modifier = 1- b0*(1/np.cos(aoi_design)-1)
             
        const_A = self.A * self.b + 2*self.d*1000*self.mass_flow_design - 2*self.A*T_amb_design*self.c + self.A * T_in_ave * self.c
        const_B = (self.A**2*self.b**2/4 + (self.d*1000)**2 * self.mass_flow_design**2  + self.A * self.d*1000 * self.b *self.mass_flow_design+ 2*self.A*(self.d*1000)*self.c*self.mass_flow_design*(T_in_ave - T_amb_design)+ self.A**2 * self.cleanless_factor * Gk_design * self.c *self.a * aoi_modifier)**0.5
                 
        T_out = -(const_A - 2*const_B) / self.A / self.c          
        deltaT = T_out - T_in_ave
        

        
        self.num_col = int(np.ceil(row_temp_dif/deltaT))
        mass_flow_corrected = self.num_col / row_temp_dif * deltaT * self.mass_flow_design

        power_row = mass_flow_corrected * self.d * row_temp_dif 
        self.num_row = int(np.ceil(self.desal_thermal_power_req / power_row))
        self.num_total_col = self.num_row * self.num_col
        self.area = self.num_total_col * self.A
   
        staticcollector_output = []
        staticcollector_output.append({'Name':'Number of collectors per row','Value':self.num_col,'Unit':''})
        staticcollector_output.append({'Name':'Number of collector rows','Value':self.num_row,'Unit':''})
        staticcollector_output.append({'Name':'Total number of collectors','Value':self.num_total_col,'Unit':''})
        staticcollector_output.append({'Name':'Total aperture area','Value':self.area,'Unit':'m2'})       
     
        
        def get_Tout_col(Gk, T_amb, k_theta, Tin ):
            C1 = (4*Gk) / self.c
            C2 = (2 *self.A*self.b + 4*self.d*1000*self.mass_flow_design - 4*self.A*T_amb*self.c + 2*self.A*Tin*self.c) / (8*self.A*Gk)
            C3 = ((self.A**2*self.b**2)/4 + (self.d*1000)**2 * self.mass_flow_design**2 +self.A*self.d*1000*self.b*self.mass_flow_design- 2*self.A*T_amb*self.d*1000*self.c*self.mass_flow_design + 2*self.A*Tin*self.d*1000*self.c*self.mass_flow_design + self.A**2*self.cleanless_factor*Gk*self.c*self.a*k_theta)**0.5 / (2*self.A*Gk)
            return -C1*(C2-C3)
        
# Simulation part        
        k_theta = []
        gen = []
        Tout_col = []
        Tout_row = []
       
        for i in range(len(data)):
            if Gk[i] > 0:
                k_theta.append(1-b0*(1/np.cos(aoi[i])-1))
                T_input = self.initial_water_temp
                # Calculate T_out           
                Tout_col.append(get_Tout_col(Gk[i], T_amb[i], k_theta[i],T_input))
                
                for j in range(self.num_col):
                    T_output = get_Tout_col(Gk[i], T_amb[i], k_theta[i], T_input)
                    T_input = T_output
                
                Tout_row.append(max(self.initial_water_temp,T_output))
                gen.append(self.d*mass_flow_corrected*(Tout_row[i]-self.initial_water_temp)* self.num_total_col)
            else:
                k_theta.append(1)
                Tout_col.append(self.initial_water_temp)
                Tout_row.append(self.initial_water_temp)
                gen.append(0)
                
        staticcollector_output.append({'Name':'Field outlet temperature','Value':Tout_row,'Unit':'oC'})   
        staticcollector_output.append({'Name':'Thermal power generation','Value':gen,'Unit':'kWh'})   
        staticcollector_output.append({'Name':'Design capacity','Value':self.desal_thermal_power_req/1000,'Unit':'MWh'})   
        
     
        return gen, staticcollector_output



    def __repr__(self):
        collectors=('Flat Plate Collector','Evacuated Tube Collector')


        
 
#%%

case =StaticCollector()
case.design()
# # case.simulation()

            
        

   