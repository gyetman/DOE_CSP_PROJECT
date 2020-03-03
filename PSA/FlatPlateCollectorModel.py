# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 17:06:21 2020

@author: adama
"""
import numpy as np
from math import pi,sqrt
#%% Number of columns in collector field
def num_col_fila_DOE(tipo_col,Tent_campo,Tsal_campo,Time,Long,Lat,inc_captador,v_azim,Tamb_D,qm,a,b,c,d,G,A,*args):

#    % num_col_fila_DOE(tipo_col,Tent_campo,Tsal_campo,Time,Long,Lat,inc_captador,v_azim,Tamb_D,qm,a,b,c,d,G,A,varargin)
#    
#    
#    
#    
#    % tipo_col '1' '2'
#    
#    % tipo_col '1': Flat Plate Collectors (FPC)
#    % tipo_col '2': Evacuated Tube Collectors(ETC) or Compound Parabolic Collectors (CPC)
#    
#    % Tent_campo is the inlet water temperature in the solar field, ºC
#    % Tsal campo is the outlet water temperature in the solar field, ºC
#    % Time is the date of the design point [Year Month Day Hour Minute Second],
#    % Example [2010 3 18 12 0 0] (Normally at solar noon)
#    % qm is the water mass flow rate in the collector, given by the manufacturer, kg/s
#    % a, b, c are the performance parameters of the collector, which can be found in the Certificate delivered by the manufacturer (the first one is
#    % whithout units, the second one in W/ºCm2, and the third one in W/m2ºC2)
#    % d is the specific heat of water, 4.18189 kJ/kgºC
#    % A is the aperture area of the collector, m2
#    % Long is the Longitude of the location, º
#    % Lat is the Latitude of the location, º
#    % inc_captador is the inclination of the collectors
#    % v_azim is the azimut, which is 180º 
#    % Tamb_D is the ambient temperature in the design point
#    % G is the beam global radiation at the design point, W/m2
#    % A is the aperture area of the collector, m2
#    
#    % VARARGIN:
#    
#    % tipo_col '1':
#         % varargin{1}: incidence angle in the certificate of the manufacturer
#         % varargin{2}: incidence angle modifier for the incidence angle of the manufacturer
#    % tipo_col '2'
#         % varargin{1}: Longitudinal and transversal incidence angles (theta L y theta T) in the certificate of the manufacturer. Example: [0 10 20 30 40 50 60 70 80 90] 
#         % varargin{2}: Incidence angle modifier for the theta L in the certificate. Example: [1 1 1 0.99 0.98 0.95 0.90 0.70 0.48 0] 
#         % varargin{3}: Incidence angle modifier for the theta T. Example: [1 1 1.05 1.15 1.3 1.35 1.30 1.05 0.6 0] 
#    
#             
#    % Calculate the inlet water temperature to the collector
    Te=(Tent_campo+Tsal_campo)/2
    
#    % Calculate the outlet water temperature from the collector
    Ts=temp_salida_DOE(tipo_col,Time,Long,Lat,inc_captador,v_azim,Te,Tamb_D,qm,a,b,c,d,G,A,*args)
    
    
#    % Calculate the number of collectors per row
    Increm_fila=Tsal_campo-Tent_campo
    Increm_capt=Ts-Te
    
    num_col=Increm_fila/Increm_capt
    
    resto=num_col-floor(num_col)
    
    if (resto>=0.3):
        num_col=floor(num_col)+1
    else:
        num_col=floor(num_col)
        
    
    x=0;
    return num_col





#%% Determines the number of rows for the solar field
def design_cpc_DOE(tipo_col,Time, fecha_inicio, fecha_fin, Pot_term_kW,Tent_campo,Tsal_campo,qm,Tamb_D,G,a,b,c,d,A,Long,Lat,inc_captador,v_azim,Interv,tiempo_oper,*args):

    #% design_cpc_pvsyst(tipo_col,fecha_inicio, fecha_fin,Pot_term_kW,Tent_campo,Tsal_campo,qm,a,b,c,d,A,Long,Lat,inc_captador,v_azim,Interv,tiempo_oper,varargin)
    #
    #% tipo_col '1' '2'
    #
    #% tipo_col '1': Flat Plate Collectors (FPC)
    #% tipo_col '2': Evacuated Tube Collectors(ETC) or Compound Parabolic Collectors (CPC)
    #
    #% Time is the date of the design point [Year Month Day Hour Minute Second], Example [2010 3 18 12 0 0] (Normally at solar noon)
    #% fecha_inicio is the initial date of the design day [year month day hour minute second]
    #% fecha_fin is the final date of the design day [year month day hour minute second]
    #% Pot_term_kW is the thermal power that the solar field has to supply to the desalination plant
    #% Tent_campo is the inlet water temperature in the solar field, ºC
    #% Tsal campo is the outlet water temperature in the solar field, ºC
    #% qm is the water mass flow rate in the collector, given by the manufacturer, kg/s
    #% a, b, c are the performance parameters of the collector, which can be found in the Certificate delivered by the manufacturer (the first one is
    #% whithout units, the second one in W/ºCm2, and the third one in W/m2ºC2)
    #% d is the specific heat of water, 4.18189 kJ/kgºC
    #% A is the aperture area of the collector, m2
    #% Long is the Longitude of the location, º
    #% Lat is the Latitude of the location, º
    #% inc_captador is the inclination of the collectors
    #% v_azim is the azimut, which is 180º 
    #% Interv is the time interval of the data, min
    #% tiempo_oper is the operation time of the desalination plant, hours
    #
    #% VARARGIN:
    #
    #% tipo_col '1':
    #     % varargin{1}: incidence angle in the certificate of the manufacturer
    #     % varargin{2}: incidence angle modifier for the incidence angle of the manufacturer
    #% tipo_col '2'
    #     % varargin{1}: Longitudinal and transversal incidence angles (theta L y theta T) in the certificate of the manufacturer. Example: [0 10 20 30 40 50 60 70 80 90] 
    #     % varargin{2}: Incidence angle modifier for the theta L in the certificate. Example: [1 1 1 0.99 0.98 0.95 0.90 0.70 0.48 0] 
    #     % varargin{3}: Incidence angle modifier for the theta T. Example: [1 1 1.05 1.15 1.3 1.35 1.30 1.05 0.6 0] 
    #  
    #% Constants
    rad=pi/180;
    Interv_horas=Interv/60;    #% Time interval of the data, hours
    
    #% Open the meteo data file and upload the data 
    [FileName, PathName]=uigetfile('*.*', 'Select the.mat File');
    
    NombreFichero=[PathName FileName];
    #eval(['load ''' NombreFichero '''']);
    
    #% Calculation of the julian date of "fecha_inicio" and "fecha_fin"
    julian_date_inicio=juliano(fecha_inicio);
    julian_date_fin=juliano(fecha_fin);
    
    #% Find the rows between the julian date corresponding to "fecha_inicio" and "fecha_fin"
    rows=find((julian_date_inicio<=Julian_Date) & (Julian_Date<=julian_date_fin));
    
    #% Extract the data of julian date, ambient temperature and Solar Radiation (beam global radiation) corresponding to the rows
    Julian_date_D=Julian_Date(rows);
    temp_amb_D=temp_amb(rows);
    Rad_sol_global_D=Rad_Global_inclin(rows);
    
    #% Calculation of the inlet temperature to the collector, assuming that it is the average between the inlet and outlet water temperatures in the solar field
    Te=(Tent_campo+Tsal_campo)/2;
    
    #% Number of collectors per row
    num_col=num_col_fila_DOE(tipo_col,Tent_campo,Tsal_campo,Time,Long,Lat,inc_captador,v_azim,Tamb_D,qm,a,b,c,d,G,A,varargin{:});
    
    #% Determine the number of rows of the vector Julian_Date_D to establish the indicator of FOR loop
    num_instantes=size(Julian_date_D,1);
    
    #% Create the matrix of zeros
    Julian_date_vec=np.zeros((num_instantes,6))
    Ts=np.zeros(num_instantes)
    Pot_capt=np.zeros(num_instantes)
    Pot_fila=np.zeros(num_instantes)
    E_term_fila_kWh=np.zeros(num_instantes)
    E_term_fila_valida=np.zeros(num_instantes)
    #% FOR Loop
    #% Calculate Ts, which is the water outlet temperature in one collector
    #% Calculate the thermal power delivered by one collector, Pot_capt, kW
    #% Calculate the thermal power delivered by one row of collectors, Pot_fila,kW
    #% Calculate the thermal energy delivered by one row. E_term_fila_kWh, kWh
    #% If the thermal energy is positive (higher than zero), keep the values in a vector called E_term_fila_valida
    
        for k=1:num_instantes:
            Julian_date_vec(k,:)=jul2calg(Julian_date_D(k,1));
            Ts(k,1)=temp_salida_DOE(tipo_col,Julian_date_vec(k,:),Long,Lat,inc_captador,v_azim,Te,temp_amb_D(k,1),qm,a,b,c,d,Rad_sol_global_D(k,1),A,varargin{:});
            Pot_capt(k,1)=qm*(d*(Ts(k,1)-Te));
            Pot_fila(k,1)=Pot_capt(k,1)*num_col;                      
            E_term_fila_kWh(k,1)= Pot_fila(k,1)*Interv_horas;
            if E_term_fila_kWh(k,1)>0:
               E_term_fila_valida(k,1)=E_term_fila_kWh(k,1);         
            
         
        
    #% Calculate the useful thermal energy supplied by one row of collectors during the design day, kWh
    E_term_fila_total=sum(E_term_fila_valida);  
        
    #% Calculate the total thermal energy that the desalination plant needs to operate a number of hours of operation, kWh 
    E_term_total=Pot_term_kW*tiempo_oper;
    
    #% Calculate the number of rows
    num_fila=E_term_total/E_term_fila_total;
    
    #% Calculate the decimal part of the resulting number of rows
    #% If the decimal part is higher than 0.5, then sum 1 to the number of rows obtained before
    #% If the decimal part is lower than 0.5, then rest 1 to the number of rows obtained before
    resto=num_fila-floor(num_fila);
    
        if (resto>=0.5):
            num_fila=floor(num_fila)+1
        else:
            num_fila=floor(num_fila)-1;
        
    
    #% Calculate the total number of collectors (num_total_col) and the total aperture area (area_total_captacion)
    num_total_col=num_col*num_fila;
    area_total_captacion=num_total_col*A;        #m2
    
    #% Save the data
    FileNuevo='numfilas';
    [FileName, PathName, FilterIndex]=uiputfile('*.mat', 'Save variables in .mat file', FileNuevo);
    NombreFichero=[PathName FileName];
    #eval(['save ''' NombreFichero ''' num_fila num_total_col area_total_captacion']);

        
    return num_fila, num_total_col, area_total_captacion

#%% Determines solar fraction of static collector field and gives annual thermal power profile on hourly basis
def fraccion_solar_DOE(tipo_col,num_col, num_fila, Pot_term_kW, qmo,Tent_campo, Tsal_campo,Long,Lat,inc_captador, v_azim,a,b,c,d,A,pressure,Interv,tiempo_oper,varargin):

#    % fraccion_solar_DOE(tipo_col,Pot_term_kW, qmo,coord_geo, orient_captador,Tent_campo, Tsal_campo,a,b,c,d,A,pressure,Interv,tiempo_oper,varargin) 
#    % tipo_col '1' '2'
#    
#    % tipo_col '1': Flat Plate Collectors (FPC)
#    % tipo_col '2': Evacuated Tube Collectors(ETC) or Compound Parabolic Collectors (CPC)
#    
#    % Pot_term_kW is the thermal power that the solar field has to supply to the desalination plant
#    % Tent_campo is the inlet water temperature in the solar field, ºC
#    % Tsal campo is the outlet water temperature in the solar field, ºC
#    % qm0 is the water mass flow rate in the collector, given by the manufacturer, kg/s
#    % a, b, c are the performance parameters of the collector, which can be found in the Certificate delivered by the manufacturer (the first one is
#    % whithout units, the second one in W/ºCm2, and the third one in W/m2ºC2)
#    % d is the specific heat of water, 4.18189 kJ/kgºC
#    % A is the aperture area of the collector, m2
#    % pressure is the water pressure in the solar field, bar
#    % Long is the Longitude of the location, º
#    % Lat is the Latitude of the location, º
#    % inc_captador is the inclination of the collectors
#    % v_azim is the azimut, which is 180º 
#    % Interv is the time interval of the data, min
#    % tiempo_oper is the operation time of the desalination plant, hours
#    
#    % VARARGIN:
#    
#    % tipo_col '1':
#         % varargin{1}: incidence angle in the certificate of the manufacturer
#         % varargin{2}: incidence angle modifier for the incidence angle of the manufacturer
#    % tipo_col '2'
#         % varargin{1}: Longitudinal and transversal incidence angles (theta L y theta T) in the certificate of the manufacturer. Example: [0 10 20 30 40 50 60 70 80 90] 
#         % varargin{2}: Incidence angle modifier for the theta L in the certificate. Example: [1 1 1 0.99 0.98 0.95 0.90 0.70 0.48 0] 
#         % varargin{3}: Incidence angle modifier for the theta T. Example: [1 1 1.05 1.15 1.3 1.35 1.30 1.05 0.6 0] 
#    
#    % Constants 
    rad=pi/180;
    D=37;                    # in mm
    Interv_horas=Interv/60;
    
#    % Select the meteo data file.mat and load the file 
    [FileName, PathName]=uigetfile('*.*', 'Select the data.mat File');
    
    NombreFichero=[PathName FileName];
    #eval(['load ''' NombreFichero '''']);
    
#    % Determine the number of rows of the Julian_Date vector to establish the FOR loop 
    num_instantes=size(Julian_Date,1);
    
#    % Calculate the maximum and minimum water mass flow rate, kg/s
#    % If the certificate given by the manufacturer does not provide the minimum and maximum water mass flow rates, assume qm_min=0.3 L/m2min and maximum water
#    % velocity in the collectors at 2 m/s
    qm_min=0.3;                                   # L/m2min
    Tm=(Tent_campo+Tsal_campo)/2;                 # ºC
    density_water = densW(Tm,pressure);           # kg/m3
    qm_min=(qm_min*A*density_water)/(60*1000);    # kg/s
    v_max=2;                                      # m/s
    Seccion=(pi/4)*((D/1000)**2);                 # m2
    qm_max=v_max*Seccion;                         # m3/s
    qm_max=qm_max*density_water;                  # kg/s
    
#    % If the certificate given by the manufacturer does provide the minimum and maximum water mass flow rates
#    % qm_min=((qm_min*density_water)/1000)/3600;  % En kg/s
#    % qm_max=((qm_max*density_water)/1000)/3600;  % En kg/s
    
    
#    % Create matrix of zeros
    Julian_date_vec=zeros(num_instantes,6);
    ang_inc=zeros(num_instantes,1);
    Ts=zeros(num_instantes,num_col-1);
    Te=zeros(num_instantes,num_col);
    Ts_fila=zeros(num_instantes,1);
    Pot_fila=zeros(num_instantes,1);
    Pot_campo=zeros(num_instantes,1);
    qm_recalc=zeros(num_instantes,1);
    E_campo=zeros(num_instantes,1);
    
#    % Initialize the water mass flow rate and the inlet temperature of the first collector in the first instant
    Te(1,1)=temp_amb(1,1);
    qm(1,1)=qmo;                    #% The water mass flow rate is initially equal to the nominal mass flow rate (qmo)
    
#    % FOR loop
#    
#        % Calculation of the date in the format[year month day hour minute second] from the data vector of the julian day 
#        % Call function ang_inc_staticcol to determine the incidence angle
#        % Calculation of the sun_cenit and sun_acimut by the function "psasunpos"
#        
#             % FOR loop for each collector 
#        
#                % Calculation of the water outlet temperature of each collector 
#                % Calculation of the water inlet temperature of each collector, which is the outlet temperature of the previous collector
#        
#        % Calculation of the water outlet temperature of the row from the inlet temperature at the last collector 
#        % Calculation of the thermal power supplied by the row of collectors with the mass flow rate in that instant
#        % Calculation of the thermal power supplied by the solar field in that instant
#        % If the water outlet temperature of the row is lower than the water outlet temperature from the solar field, re-calculate the mass flow
#        % rate such that the outlet temperature of the row is equal to the water outlet temperature from the solar field
#        % If qm is higher than qm_min, then establish that the water inlet
#        % temperature of the following instant is equal to the water inlet temperature to the
#        % solar field
#        % Calculation of the thermal power supplied by the row of collectors with the re-calculated mass flow rate
#        % Calculation of the thermal power supplied by the solar field from the previous thermal power and the number of rows
#        % If qm is lower than qm_min, the mass flow rate at the following
#        % instant is the nominal one and the inlet temperature of the row at
#        % the following instant is the outlet temperature of the row
#        % If the outlet temperature of the row is higher than water outlet temperature from the solar field, re-calculate the mass flow
#        % rate such that the outlet temperature of the row is equal to the water outlet temperature from the solar field
       
    
      for k=1:num_instantes
          Julian_date_vec(k,:)=jul2calg(Julian_Date(k,1));
          ang_inc(k,1)= ang_inc_staticcol(Julian_date_vec(k,:),[Long Lat],[inc_captador v_azim]);
          [sun_cenit(k,1) sun_acimut(k,1)]=psasunpos(Julian_date_vec(k,:),Long,Lat);
        if num_col~=1  
          for n=1:num_col-1
              Ts(k,n)=temp_salida_DOE(tipo_col,Julian_date_vec(k,:),Long,Lat,inc_captador,v_azim,Te(k,n),temp_amb(k,1),qm(k,1),a,b,c,d,Rad_Global_inclin(k,1),A,varargin{:});
              Te(k,n+1)=Ts(k,n);
          end
        end
          Ts_fila(k,1)=temp_salida_DOE(tipo_col,Julian_date_vec(k,:),Long,Lat,inc_captador,v_azim,Te(k,num_col),temp_amb(k,1),qm(k,1),a,b,c,d,Rad_Global_inclin(k,1),A,varargin{:});   
          Ts_fila(k,1)=real(Ts_fila(k,1));
          Pot_fila(k,1)=qm(k,1)*(d*(Ts_fila(k,1)-Te(k,1)));
          Pot_campo(k,1)=Pot_fila(k,1)*num_fila;      
          if Ts_fila(k,1)<Tsal_campo 
             qm_recalc(k,1)=Pot_fila(k,1)/(d*(Tsal_campo-Te(k,1)));
             if qm_recalc(k,1)>qm_min
                Te(k+1,1)=Tent_campo;
                Pot_fila(k,1)=qm_recalc(k,1)*(d*(Tsal_campo-Te(k,1)));
                Pot_campo(k,1)=Pot_fila(k,1)*num_fila;
                qm(k+1,1)=qm_recalc(k,1);
             elseif qm_recalc(k,1)<qm_min
                 qm(k+1,1)=qmo;
                 Te(k+1,1)=Ts_fila(k,1);
             end
          elseif Ts_fila(k,1)>Tsal_campo
              qm_recalc(k,1)=Pot_fila(k,1)/(d*(Tsal_campo-Te(k,1)));
              if qm_recalc(k,1)<qm_max
                 Ts_fila(k,1)=Tsal_campo;
                 Te(k+1,1)=Tent_campo;
                 Pot_fila(k,1)=qm_recalc(k,1)*(d*(Tsal_campo-Te(k,1)));
                 Pot_campo(k,1)=Pot_fila(k,1)*num_fila;
                 qm(k+1,1)=qm_recalc(k,1);
              elseif qm_recalc(k,1)>qm_max
                 Ts_fila(k,1)=temp_salida_DOE(tipo_col,Julian_date_vec(k,:),Long,Lat,inc_captador,v_azim,Te(k,num_col),temp_amb(k,1),qm_max,a,b,c,d,Rad_Global_inclin(k,1),A,varargin{:});
                 Pot_fila(k,1)=qm_max*(d*(Ts_fila(k,1)-Te(k,1)));
                 Pot_campo(k,1)=Pot_fila(k,1)*num_fila;
                 Te(k+1,1)=Tent_campo;
                 qm(k+1,1)=qm_max;
              end
          end
    
          if Pot_campo(k,1)>0
              E_campo(k,1)=Pot_campo(k,1)*Interv_horas;
          end
      end
      
      
#    % Calculate the total energy delivered by the solar field (E_total_campo) by the sum of the thermal energy delivered in every instant
#    % Calculate the nominal thermal energy required by the desalination plant (E_nominal) along the year. Normally, it should be considered that the desalination
#    % plant must work 24 hours/day 365 days
    Etotal_campo=sum(E_campo);                    # En kWh
    E_nominal=Pot_term_kW*tiempo_oper*365;        # En kWh
    
#    % Calculate the solar fraction
    fraccion_solar=Etotal_campo/E_nominal;
    
    x=0
    return fraccion_solar
#%% dot product 
def dot_product(vector1,vector2):
    producto_escalar=np.empty([np.shape(vector1)[0],1])
    if np.shape(vector1)[0]!=np.size(vector1):
        producto_escalar = vector1[:,0]*vector2[:,0]+vector1[:,1]*vector2[:,1]+vector1[:,2]*vector2[:,2]
    else:
        producto_escalar = vector1[0]*vector2[0]+vector1[1]*vector2[1]+vector1[2]*vector2[2]
    return producto_escalar 
#%% converts angles to cartesian coordinates
def cartesianas(v_theta,v_azim):

    rad=pi/180
    
    v_theta_rad=v_theta*rad
    v_azim_rad=v_azim*rad
    
    
    vx=np.sin(v_theta_rad)*np.sin(v_azim_rad)
    vy=np.sin(v_theta_rad)*np.cos(v_azim_rad)
    vz=np.cos(v_theta_rad)
    return [vx ,vy ,vz]
#%% uses zenith and azimuth angles to compute sun vector
def sunvector(cenit,acimut):

    #% SUNVECTOR.M
    #% function [sunvec]=sunvector(cenit,acimut);
    #%
    
    rad=pi/180;
    cenit=cenit*rad;
    acimut=acimut*rad;
    sx=sin(cenit).*cos(acimut);
    sy=sin(cenit).*sin(acimut);
    sz=cos(cenit);
    sunvec=[sx sy sz];

    return sunvec
#%% Gets zenith and azimuth angles based on time, longitude and latitude 
def psasunpos(Time,Longitude,Latitude):

    #% PSASUNPOS.M
    #% function [zenith_distance,azimuth]=psasunpos(time,longitude,latitude)
    #%
    #
    #% Constants
    twopi=2*pi;
    rad=pi/180;
    EarthMeanRadius=6371.01;
    AstronomicalUnit=149597890;
    
    
    
    #% Calculate difference in days between the current Julian Day and JD 2451545.0, which is 
    #% noon 1 January 2000 Universal Time
    #
    #% Calculate time of the day in UT decimal hours
    DecimalHours=Time(:,4)+(Time(:,5)+Time(:,6)/60)/60;
    #% Calculate current Julian Day
    Aux1=fix((Time(:,2)-14)/12);
    Aux2=fix((1461*(Time(:,1)+4800+Aux1))/4)+fix((367*(Time(:,2)-2-12*Aux1))/12)-fix((3*(fix((Time(:,1)+4900+Aux1)/100)))/4)+Time(:,3)-32075;
    JulianDate=Aux2-0.5+DecimalHours/24;
    #% Calculate difference between current Julian Day and JD 2451545.0
    ElapsedJulianDays=JulianDate-2451545;
    
    #% Calculate ecliptic coordinates (ecliptic longitude and obliquity of the
    #% ecliptic in radians but without limiting the angle to be less than 2*Pi
    #% (i.e., the result may be greater than 2*Pi)
    
    Omega=2.1429-0.0010394594*ElapsedJulianDays;
    MeanLongitude=4.8950630+0.017202791698*ElapsedJulianDays;
    MeanAnomaly=6.2400600+0.0172019699*ElapsedJulianDays;
    EclipticLongitude=MeanLongitude+0.03341607*sin(MeanAnomaly)+0.00034894*sin(2*MeanAnomaly)-0.0001134-0.0000203*sin(Omega);
    EclipticObliquity=0.4090928-6.2140e-9*ElapsedJulianDays+0.0000396*cos(Omega);
    
    #% Calculate celestial coordinates (right ascension and declination) in radians
    #% but without limiting the angle to be less than 2*Pi (i.e., the result may be greater
    #% than 2*Pi)
    
    Sin_EclipticLongitude=sin(EclipticLongitude);
    Y=cos(EclipticObliquity).*Sin_EclipticLongitude;
    X=cos(EclipticLongitude);
    RightAscension=atan2(Y,X);
    Temp=(RightAscension<0);
    RightAscension=(Temp).*(RightAscension+twopi)+(~Temp).*RightAscension;
    Declination=asin(sin(EclipticObliquity).*Sin_EclipticLongitude);
    
    #% Calculate local coordinates (azimuth and zenith angle) in degrees
    
    GreenwichMeanSiderealTime=6.6974243242+0.0657098283*ElapsedJulianDays+DecimalHours;
    LocalMeanSiderealTime=(GreenwichMeanSiderealTime*15+Longitude)*rad;
    HourAngle=LocalMeanSiderealTime-RightAscension;
    EOT=MeanLongitude-RightAscension;
    LatitudeInRadians=Latitude*rad;
    Cos_Latitude=cos(LatitudeInRadians);
    Sin_Latitude=sin(LatitudeInRadians);
    Cos_HourAngle=cos(HourAngle);
    ZenithAngle=acos(Cos_Latitude.*Cos_HourAngle.*cos(Declination)+sin(Declination).*Sin_Latitude);
    Y=-sin(HourAngle);
    X=tan(Declination).*Cos_Latitude-Sin_Latitude.*Cos_HourAngle;
    Azimuth=atan2(Y,X);
    Temp=(Azimuth<0);
    Azimuth=(Temp).*(Azimuth+twopi)+(~Temp).*(Azimuth);
    Azimuth=Azimuth/rad;
    Parallax=EarthMeanRadius/AstronomicalUnit*sin(ZenithAngle);
    ZenithAngle=(ZenithAngle+Parallax)/rad;
    
    return [ZenithAngle, Azimuth]

#%% Determines incidence angle modifier of the collector
def k_teta_DOE(tipo_col,inc_captador,v_azim,Time,Long,Lat,*args):
    
#    % [f_theta]= k_teta_DOE(tipo_col,inc_captador,v_azim,Time,Long,Lat,varargin)    
#    % tipo_col '1' '2'
#    
#    % tipo_col '1': Flat Plate Collectors (FPC)
#    % tipo_col '2': Evacuated Tube Collectors(ETC) or Compound Parabolic Collectors (CPC)
#    
#    %Time [2010 3 18 12 0 0]
#    
#    % VARARGIN:
#    
#    % tipo_col '1':
#         % varargin{1}: incidence angle in the certificate of the manufacturer
#         % varargin{2}: incidence angle modifier for the incidence angle of the manufacturer
#    % tipo_col '2'
#         % varargin{1}: Longitudinal and transversal incidence angles (theta L y theta T) in the certificate of the manufacturer. Example: [0 10 20 30 40 50 60 70 80 90] 
#         % varargin{2}: Incidence angle modifier for the theta L in the certificate. Example: [1 1 1 0.99 0.98 0.95 0.90 0.70 0.48 0] 
#         % varargin{3}: Incidence angle modifier for the theta T. Example: [1 1 1.05 1.15 1.3 1.35 1.30 1.05 0.6 0] 
#    
#    % Long is the Longitude of the location, º
#    % Lat is the Latitude of the location, º
#    % inc_captador is the inclination of the collectors
#    % v_azim is the azimut, which is 180º      
#        
#    % Constants    
    rad = pi/180
      
#    % Calculate the normal vector to the collector 
    [nx ny nz]=cartesianas(inc_captador,v_azim)
    
#    % Calculate the solar vector
    [cenit,acimut]=psasunpos(Time,Long,Lat)
    [sx sy sz]=cartesianas(cenit,acimut)
    
#    % Calculate the incidence angle of the sun 
    prod_escalar=dot_product([sx sy sz],[nx ny nz])
    ang_incid=acos(prod_escalar)/rad;
    
#    % Calculate the projection planes
#    % Normal vector to the transversal plane
    
    normal_vec_transv_u = [-ny./sqrt(ny.^2+ nx.^2) nz./sqrt(ny.^2+ nx.^2) 0]
    
#    % Normal vector to the longitudinal plane
    
    normal_vec_long_u = cross([nx ny nz],normal_vec_transv_u)
    
#    % Calculate the projection of the solar vector over the transversal plane and its unit vector
    
    sunvector_trans = cross(cross(normal_vec_transv_u,[sx sy sz]),normal_vec_transv_u)
    sunvector_trans_unit = normalize(sunvector_trans)
    
#    % Calculate the projection of the solar vector over the transversal plane and its unit vector
    
    sunvector_long = cross(cross(normal_vec_long_u,[sx sy sz]),normal_vec_long_u)
    sunvector_long_unit = normalize(sunvector_long)
    
#    % Calculate the incidence angle longitudinal and transversal 
    
    incidence_angle_long_rad = acos(dot_product(sunvector_long_unit,[nx ny nz]))
    incidence_angle_long_deg=incidence_angle_long_rad/rad
    
    incidence_angle_trans_rad = acos(dot_product(sunvector_trans_unit,[nx ny nz]))
    incidence_angle_trans_deg=incidence_angle_trans_rad/rad
    
#    % Calculate the incidence angle modifier
    
#    switch (tipo_col)
#    
#        case {'1'} #% FPC
    if tipo_col=='1':
           
          ang_inc_D=ang_inc_staticcol(Time,[Long Lat],[inc_captador v_azim])
          Ang_incid_rad=varargin{1}*rad
          bo=(1-varargin{2})/((1/cos(Ang_incid_rad)-1))
          Ang_incid_rad_max = acos(1/((1/bo)+1))
          ang_inc_D_rad=ang_inc_D*rad
          condicion1 = ang_inc_D_rad<Ang_incid_rad_max
          f_theta = (condicion1).*(1-bo.*(1./cos(ang_inc_D_rad)-1))+(~condicion1).*0
          
#       case {'2'}   #% ETC or CPC con datos experimentales de kteta L y kteta T
    elif tipo_col=='2':
        
         if ang_incid<90:
            Mod_L=interp1(varargin{1},varargin{2},incidence_angle_long_deg,'cubic')   
            Mod_T=interp1(varargin{1},varargin{3},incidence_angle_trans_deg,'cubic')         
            f_theta = Mod_L*Mod_T
         else:
              f_theta=0

         
                                                                     
    
    
    
    
    
    
    return f_theta
#%% Determines the water outlet temperature from the collector
def temp_salida_DOE(tipo_col,Time,Long,Lat,inc_captador,v_azim,Te,Tamb_D,qm,a,b,c,d,G,A,*args):

#    % Ts=temp_salida_DOE(tipo_col,Time,Long,Lat,inc_captador,v_azim,Te,Tamb_D,qm,a,b,c,d,G,A,varargin)
#    
#    % tipo_col '1' '2'
#    
#    % tipo_col '1': Flat Plate Collectors (FPC)
#    % tipo_col '2': Evacuated Tube Collectors(ETC) or Compound Parabolic Collectors (CPC)
#    
#    %Time [2010 3 18 12 0 0]
#    
#    % VARARGIN:
#    
#    % tipo_col '1':
#         % varargin{1}: incidence angle in the certificate of the manufacturer
#         % varargin{2}: incidence angle modifier for the incidence angle of the manufacturer
#    % tipo_col '2'
#         % varargin{1}: Longitudinal and transversal incidence angles (theta L y theta T) in the certificate of the manufacturer. Example: [0 10 20 30 40 50 60 70 80 90] 
#         % varargin{2}: Incidence angle modifier for the theta L in the certificate. Example: [1 1 1 0.99 0.98 0.95 0.90 0.70 0.48 0] 
#         % varargin{3}: Incidence angle modifier for the theta T. Example: [1 1 1.05 1.15 1.3 1.35 1.30 1.05 0.6 0] 
#    
#    % Long is the Longitude of the location, º
#    % Lat is the Latitude of the location, º
#    % inc_captador is the inclination of the collectors
#    % v_azim is the azimut, which is 180º      
      
    
    
#    % Call the function that calculates the incidence angle modifier
    [f_theta]= k_teta_DOE(tipo_col,inc_captador,v_azim,Time,Long,Lat,*args)
    
#    % Calculate the water outlet temperature from the solar collector         
    Ts= -(A*b - 2*((A**2*b**2)/4 + 1000000*d**2*qm**2 + 1000*A*b*d*qm - 2000*A*Tamb_D*c*d*qm + 2000*A*Te*c*d*qm + A**2*G*a*c*f_theta)**(1/2) + 2000*d*qm - 2*A*Tamb_D*c + A*Te*c)/(A*c)
    return Ts
#%% Determines storage capacity of water tanks according to selected design date.

def Almacenamiento_cpc_DOE (Fecha_inicio, Fecha_fin, Tst, Tamb,Pot_term_kW,Interv, pressure):

#    % Capacidad_m3=Almacenamiento_cpc_DOE (Fecha_inicio, Fecha_fin, Tst, Tamb,Pot_term_kW,Interv)
#    
#    % fecha_inicio is the initial date of the design day [year month day hour minute second]
#    % fecha_fin is the final date of the design day [year month day hour minute second]
#    % Tst is the maximum water temperature achieved by the solar field 
#    % pressure is the water pressure in the solar field, bar
#    
#    
#    % Constants
    Cp=4.1819 #% Specific heat of water
    
#    % Calculate the vector of data of nominal thermal energy required by the desalination plant every instant
    Interv_horas=Interv/60
    E_term_kWh=Pot_term_kW*Interv_horas                  # % kWth 
    
#    % Select the file with the meteo data and upload the data 
    [FileName, PathName]=uigetfile('*.*', 'Select the meteo data.mat File')
    
    NombreFichero=[PathName FileName]
    eval(['load ','', NombreFichero, '',''])
    
#    % Select the file with the data saved of fraccion_solar and upload the data
    [FileName, PathName]=uigetfile('*.*', 'Select the fraccion_solar.mat File')
    
    NombreFichero=[PathName FileName]
    eval(['load ','', NombreFichero, '',''])
    
#    % Calculate the julian day of "fecha_inicio" and "fecha_fin"
    julian_date_inicio=juliano(Fecha_inicio)
    julian_date_fin=juliano(Fecha_fin)
    
#    % Find the rows between the julian date corresponding to "fecha_inicio" and "fecha_fin"
    rows=find((julian_date_inicio<=Julian_Date) & (Julian_Date<=julian_date_fin))
    
#    % Extract the data (from the fraccion_solar.mat file)of thermal energy provided by the solar field corresponding to the rows
    E_campo_D=E_campo(rows)
    
#    % Determine the number of rows of the vector Julian_Date_D to establish the indicator of FOR loop
    num_filas_vector=np.size(E_campo_D)
    
#    % Create the matrix of zeros
    E_almac=np.zeros(num_filas_vector)
    
#    % Calculate the total thermal energy stored------- TRY REPLACING WITH VECTORIZATION
#        for k in range(1,num_filas_vector):
#            if E_campo_D[k]>E_term_kWh:
#               E_almac=E_campo_D[k]-E_term_kWh
    E_almac=(E_campo_D>E_term_kWh)*(E_campo_D-E_term_kWh)+ ~(E_campo_D>E_term_kWh)*0
            
            
        
    E_total_almac=np.sum(E_almac)   # kWh
    
#    % Calculate the capacity of the thermal storage tank
    T=(Tst+Tamb)/2                                   # ºC
    E_total_almac_kJ=E_total_almac*3600              # kJ
    Capacidad_kg=E_total_almac_kJ/(Cp*(Tst-Tamb))    # kg
    density_water = densW(T,pressure)                # kg/m3
    Capacidad_m3=Capacidad_kg/density_water          # m3
    
    x=0
    return Capacidad_m3
#%% Obtain Normal vector
def normalize(vector):

    d_modulo = np.sqrt(sum(vector.T**2))
#    d_modulo = np.tile(d_modulo,(1,3))
#    normal_vector=vector/d_modulo
    normal_vector=np.empty(np.shape(vector))
    normal_vector[:,0] = vector[:,0] / d_modulo
    normal_vector[:,1] = vector[:,1] / d_modulo
    normal_vector[:,2] = vector[:,2] / d_modulo
    
    return normal_vector
