# -*- coding: utf-8 -*-
"""
Created on Tue May 25 12:52:00 2021

@author: zzrfl
"""


class generic(object):
    def __init__(self,
               FeedC_r = 35, # Feed concentration
               STEC = 50, # kWh/m3
               SEC = 1.5, # kWh/m3
               RR = 50, # recovery rate %
               Capacity = 2000, # m3/day
               storage_hour = 0, # hr
               Fossil_f = 0, 
               ):
        self.FeedC_r = FeedC_r
        self.STEC = STEC
        self.RR = RR/100
        self.Capacity = Capacity
        self.storag_hour = storage_hour
        self.Fossil_f = Fossil_f
        self.SEC = SEC
        
    def design(self):
        
        self.P_req = self.Capacity * self.STEC / 24  # kW        
        self.Cb  =  self.FeedC_r / (1 - self.RR)
        self.elec = self.SEC * self.Capacity / 24 # kW
        
        
        
        self.design_output = []
        self.design_output.append({'Name':'Thermal power consumption','Value': self.P_req / 1000 ,'Unit':'MW(th)'})
        self.design_output.append({'Name':'Brine salinity', 'Value': self.Cb, 'Unit': 'g/L'})
        self.design_output.append({'Name':'Thermal energy consumption','Value':self.elec,'Unit':'kW(e)'})        
        
        return self.design_output
        
    def simulation(self, gen ,storage):
        self.thermal_load = self.Capacity / 24 * self.STEC # kWh per hour
        self.max_prod = self.Capacity / 24 # m3/h
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
        # simu_output.append({'Name':'Dataframe','Value':self.json_df,'Unit':''})        
        # Add brine volume and concentration (using 100% rejection(make it a variable))
        
        return simu_output        