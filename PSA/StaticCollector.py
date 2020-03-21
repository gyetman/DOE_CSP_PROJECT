# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 22:47:09 2020
Static Solar Collector class 

TO DO: 
-Need to modify fraccion_solar to take thermal storage as input. For now, placing thermal storage under simulation method,
but will change so that it can be executed as its own design method. 

@author: adama
"""
from PSA.StaticCollectorModel import *

class StaticCollector(object):
    '''
    Input variables:

    
    Output variables:
    
    '''

    def __init__(self,
                 # Design parameters
                 collector_type = '2',  # '1' for flat-plate collector and '2' for evacuated tube collector
                 design_point_date=[2010, 3 ,18 ,12, 0, 0], # design day/time
                 initial_date   = [2010, 3 ,18, 9, 0, 0], # initial design day/time
                 final_date     = [2010, 3, 18, 17, 0 ,0], # final design day/time
                 desal_thermal_power_req= 1000, # thermal power that solar collector field must supply to desal plant
                 initial_water_temp=25, # inlet water temperature in the solar field, ºC
                 outlet_water_temp=80, # outlet water temperature in the solar field, ºC
                 qm=0.02,   # mass flow rate of collector 
                 Tamb_D=25, # design point ambient temperature, C
                 
                 G=1000,    # irradiance from collector datasheet
                 a=0.64,    # datasheet 
                 b=1.494,   # datasheet 
                 c=0.012,   # datasheet 
                 d=4.18189, # datasheet 
                 A=2.83,    # aperture area of collector from datasheet 
                
                 Long=-2.460, # Longitude
                 Lat=36.838,  # Latitude
                 weatherfile  = 'C:/SAM/2018.11.11/solar_resource/tucson_az_32.116521_-110.933042_psmv3_60_tmy.csv',
                 
                 tilt_angle=36.838, # tilt angle of collector
                 v_azim=180,     # surface azimuth angle, 180 degrees facing south
                 Interv=60,      # temporal resolution of simulation/data in # of minutes
                 tiempo_oper=10, # daily operational availability of desal plant in hours
                 pressure=1,      # water pressure in the solar field, bar
                 v1=[10 ,20 ,30, 40 ,50, 60, 70], # incidencee angles from datasheet
                 v2=[1, 1, 0.99, 0.97, 0.92, 0.84 ,0.68],       # Longitudinal incidence angle modifiers from datasheet
                 v3=[1.04 ,1.09 ,1.23 ,1.38 ,1.78, 1.82, 2.08] # Transversal incidence angle modifiers from datasheet
                 ):
        
        self.collector_type  = collector_type
        self.design_point_date=design_point_date
        self.initial_date   = initial_date
        self.final_date   = final_date
        self.desal_thermal_power_req   = desal_thermal_power_req
        self.initial_water_temp = initial_water_temp
        self.outlet_water_temp = outlet_water_temp
        self.qm = qm
        self.Tamb_D = Tamb_D
        self.G = G
        self.a = a
        self.b= b
        self.c=c
        self.d=d
        self.A=A
        self.Long=Long
        self.Lat=Lat
        self.tilt_angle=tilt_angle
        self.v_azim=v_azim
        self.Interv=Interv
        self.tiempo_oper=tiempo_oper
        self.pressure=pressure
        self.v1=v1
        self.v2=v2
        self.v3=v3
        self.weatherfile=weatherfile
        
 #% 
    def design(self):
        if self.collector_type=='1':
            #v1=30   ### Made up value - should use a flat-plate collector datasheet to get this and should only be a single value
            #v2=0.99 ### Made up value - should use a flat-plate collector datasheet to get this  and should only be a single value
            self.num_col,self.num_fila, self.num_total_col, self.area_total_captacion = design_cpc_DOE(self.collector_type,self.design_point_date, self.initial_date, self.final_date, self.desal_thermal_power_req,self.initial_water_temp,self.outlet_water_temp,self.qm,self.Tamb_D,self.G,self.a,self.b,self.c,self.d,self.A,self.Long,self.Lat,self.weatherfile,self.tilt_angle,self.v_azim,self.Interv,self.tiempo_oper,self.v1,self.v2)        
            
        elif self.collector_type=='2':
            self.num_col,self.num_fila, self.num_total_col, self.area_total_captacion = design_cpc_DOE(self.collector_type,self.design_point_date, self.initial_date, self.final_date, self.desal_thermal_power_req,self.initial_water_temp,self.outlet_water_temp,self.qm,self.Tamb_D,self.G,self.a,self.b,self.c,self.d,self.A,self.Long,self.Lat,self.weatherfile,self.tilt_angle,self.v_azim,self.Interv,self.tiempo_oper,self.v1,self.v2,self.v3)        
        
        
        design_output = []
        design_output.append({'Name':'Number of collectors per row','Value':self.num_col,'Unit':''})
        design_output.append({'Name':'Number of collector rows','Value':self.num_fila,'Unit':''})
        design_output.append({'Name':'Total number of collectors','Value':self.num_total_col,'Unit':''})
        design_output.append({'Name':'Total aperture area','Value':self.area_total_captacion,'Unit':'m2'})       
        
        
        return design_output

    def simulation(self):
        if self.collector_type=='1':
            self.solar_fraction,self.Te, self.Ts_fila, self.Ts, self.qm, self.Pot_fila, self.Pot_campo, self.E_campo=fraccion_solar_DOE(self.collector_type,self.num_col, self.num_fila, self.desal_thermal_power_req,self.qm,self.initial_water_temp, self.outlet_water_temp,self.Long,self.Lat,self.weatherfile,self.tilt_angle, self.v_azim,self.a,self.b,self.c,self.d,self.A,self.pressure,self.Interv,self.tiempo_oper,self.v1,self.v2)
            self.thermal_storage_capacity_m3=Almacenamiento_cpc_DOE (self.E_campo,self.initial_date, self.final_date, self.outlet_water_temp, self.initial_water_temp,self.desal_thermal_power_req,self.Interv, self.pressure,self.weatherfile)

        elif self.collector_type=='2':
            self.solar_fraction,self.Te, self.Ts_fila, self.Ts, self.qm, self.Pot_fila, self.Pot_campo, self.E_campo=fraccion_solar_DOE(self.collector_type,self.num_col, self.num_fila, self.desal_thermal_power_req,self.qm,self.initial_water_temp, self.outlet_water_temp,self.Long,self.Lat,self.weatherfile,self.tilt_angle, self.v_azim,self.a,self.b,self.c,self.d,self.A,self.pressure,self.Interv,self.tiempo_oper,self.v1,self.v2,self.v3)
            self.thermal_storage_capacity_m3=Almacenamiento_cpc_DOE (self.E_campo,self.initial_date, self.final_date, self.outlet_water_temp, self.initial_water_temp,self.desal_thermal_power_req,self.Interv, self.pressure,self.weatherfile)


        simu_output = []
        simu_output.append({'Name':'Solar fraction','Value':self.solar_fraction,'Unit':''})
        simu_output.append({'Name':'Collector inlet temperature','Value':self.Te,'Unit':'°C'})
        simu_output.append({'Name':'Row outlet temperature','Value':self.Ts_fila,'Unit':'°C'})
        simu_output.append({'Name':'Collector outlet temperature','Value':self.Ts,'Unit':'°C'})
        simu_output.append({'Name':'Mass flow rate','Value': self.qm,'Unit':'kg/s'})
        simu_output.append({'Name':'Thermal power per row','Value': self.Pot_fila,'Unit':'kW?'})
        simu_output.append({'Name':'Total thermal power','Value': self.Pot_campo,'Unit':'kW?'})
        simu_output.append({'Name':'Thermal Energy','Value': self.E_campo,'Unit':'kWh?'})
        simu_output.append({'Name':'Thermal Storage Capacity','Value': self.thermal_storage_capacity_m3,'Unit':'m3'})

        return simu_output

    def __repr__(self):
        collectors=('Flat Plate Collector','Evacuated Tube Collector')
        collec_obj=collectors[int(self.collector_type)-1]
        return str(collec_obj)

        
 
            
        

   