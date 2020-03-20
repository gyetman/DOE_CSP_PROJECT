#!/usr/bin/env python
# coding: utf-8

# In[1]:


from datascience import*
from iapws import IAPWS95
import numpy as np
import math
import warnings
from iapws import SeaWater


# In[2]:


T0 = 20  #K
P0 = 101325*10**-6 #Mpa


# ## Function defined in EES

# define function that returns the value of the energy with the steam T and P

# In[3]:


def Exergiatp(T,P):
    h = IAPWS95(T=T+273.15,P=P).h
    s = IAPWS95(T=T+273.15,P=P).s
    h0 = IAPWS95(T=T0+273.15,P=P0).h
    s0 = IAPWS95(T=T0+273.15,P=P0).s
    return h-h0-(T0+273.15)*(s-s0)    


# define function that returns the value of the erergy with the steam title and T(saturation)

# In[4]:


def Exergiaxt(x,T):
    h = IAPWS95(T=T+273.15,x=x).h
    s = IAPWS95(T=T+273.15,x=x).s
    h0 = IAPWS95(T=T0+273.15,P=P0).h
    s0 = IAPWS95(T=T0+273.15,P=P0).s
    return h-h0-(T0+273.15)*(s-s0)    


# def function that returns the value of the energy with the steam title and P(saturation)

# In[5]:


def Exergiaxp(x,P):
    h = IAPWS95(P=P,x=x).h
    s = IAPWS95(P=P,x=x).s
    h0 = IAPWS95(T=T0+273.15,P=P0).h
    s0 = IAPWS95(T=T0+273.15,P=P0).s
    return h-h0-(T0+273.15)*(s-s0)  


# Function BPE : Boiling Point Elevation of Seawater

# In[6]:


def Bpe(T_b,X):
    if T_b<283.15:
        Bpe = 'Temperature is out of range'
    elif T_b<180+273.15:
        A=0.0825431+0.0001883*T_b+4.02*10**(-6)*(T_b)**2
        B=-7.625*10**(-4) +9.02*10**(-5)*T_b-5.2*10**(-7)*(T_b)**2
        C=1.522*10**(-4)-3*10**(-6)*T_b-3*10**(-8)*(T_b)**2
        if X<1:
            Bpe = "X is out of range"
        elif X<16:
            X_pe = X/1000
            Bpe = A*X_pe+B*X_pe**2+C*(X_pe)**3
        else:
            Bpe = "X is out of range"
    else:
        Bpe = "Temperature is out of range"
    return Bpe


# Function BPE: Boiling Point Elecation of Seawater - Sharqawy

# In[7]:


def bpe_mit(T,s):
    if T<0:
        Bpe_mit = 'Temperature is out of range'
    elif T<=200:
        if s<0:
            Bpe_mit = 's is out of range'
        elif s<=0.12:
            s_wt = s/1000
            A = -4.584*10**-4*T**2+2.823*10**-1*T+17.95
            B = 1.536*10**-4*T**2+5.267*10**-2*T+6.56
            Bpe_mit = A*s_wt+B*s_wt
        else:
            Bpe_mit = 's is out of range'
    else:
        Bpe_mit='T is out of range'
    return Bpe_mit


# Function U_e: Overall heat transfer coefficient of evaporation

# In[8]:


def U_e(T_b):
    A = 1.9695
    B = 1.2057*10**-2
    C = -8.5989*10**-5
    D = 2.5651*10**-7
    U_e = A+B*T_b+C*T_b**2+D*T_b**3 #Units = KW/m^2-C
    return U_e


# Function U_c: Overall Heat Transfer Coefficienf of Condenser

# In[9]:


def U_c(T_v):
    A=1.7194
    B=3.2063*10**-3
    C=-1.5971*10**-5
    D=-1.9918*10**-7
    U_c = A+B*T_v+C*T_v**2+D*T_v**3 #Units = KW/m^2-C
    return U_c


# NON-EQUILIBRIUM ALLOWANCE 
# EL-DESSOUKY (MIYATAKE et al (1973))

# In[10]:


def Nea(T1,T2,T_V):
    delta_T = T1-T2 #Temperature difference of boiling brine in effects 1 and 2
    Nea = 33*(abs(delta_T)**0.55)/abs(T_V)
    #T_V is the vapor temperature in effect 2. T_V2 = T2-BPE2
    return Nea #Nea in degrees C


# Pressure Drop in the Demister EL-DESSOUKY

# In[11]:


def Pressuredrop_demister(rho_p,V_vapor,delta_w):
    delta_P = 3.88178*(rho_p)**0.375798*(V_vapor)**0.81317*(delta_w)**(-1.56114147)
    return delta_P
#delta_P(Pa/m); delta_w(mm) grid diameter; rho_p(kg/m3) demister density
#V(m/s) vapor velocity in the demister


# Pressure Drop in the Connecting Lines

# In[12]:


def Pressuredrop_lines2(M,L,delta_i,T_v):
    rho_v = IAPWS95(T=T_v+273.15,x=1).rho
    M_kgh = M*3600
    delta_P = (0.6753*10**6*M_kgh**2*L*(1+91.4/d))/(rho_v*delta_i**5)
    return delta_P
#delta_P(Pa); M_kgh mass flow rate of vapor stream(kg/h); L length of pipe(m);
#d tube inner diameter (mm); T_v vapor temperature(C); rho_v Vapor density(kg/m^3)


# Frictional Pressure Drop

# In[13]:


def Pressuredrop_friction(m_dot,T_sat,D_i,N_T,chi,L):
    G = 4*m_dot/(math.pi*D_i**2*N_T)
    grav = 9.807 #m/s^2
    sigma = IAPWS95(T=T_sat+273.15,x=0).sigma #surfacetension
    mu_L = IAPWS95(T=T_sat+273.15,x=0).mu #Viscosity of the liquid
    mu_G = IAPWS95(T=T_sat+273.15,x=1).mu #Viscosity of the steam
    Re_L = G*D_i/mu_L
    Re_G = G*D_i/mu_G
    rho_L = IAPWS95(T=T_sat+273.15,x=0).rho
    rho_G = IAPWS95(T=T_sat+273.15, x=1).rho
    f_L = 0.079/(Re_L**0.25)
    f_G = 0.079/(Re_G**0.25)
    deltaP_L = 4*f_L*(L/D_i)*G**2*(1/(2*rho_L))
    rho_H = (chi/rho_G+(1-chi)/rho_L)**(-1)
    Fr_H - G**2/(grav*D_i*rho_H**2)
    E = (1-chi)**2+chi**2*rho_L*f_G/(rho_G*f_L)
    F = chi**0.78*(1-chi)**0.224
    H = (rho_L/rho_G)**0.91*(mu_G/mu_L)**0.19*abs(1-mu_G/mu_L)**0.7
    We_L = G**2*D_i/(sigma*rho_H)
    PHI_fr = math.sqrt(E+3.24*F*H/(Fr_H**0.045*We_L**0.035))
    deltaP_f = deltaP_L*PHI_fr**2
    return deltaP_f
#DELTAP_f (Pa); DELTAP_L = liquid phase pressure drop; PHI_fr = correction factor; M = mass flow rate (kg/s); 
#A = cross section area (m^2);  rho_v = vapor density at saturation (kg/m^3); rho_l = liquid density at saturation (kg/m^3);
#chi = vapor phase mass fraction; f_L liquid friction factor (-); G = mass flow rate per area unit (kg/m2-s)"


#  ## GRAVITATIONAL PRESSURE DROP EL-DESSOUKY Modificada

# In[14]:


def Pressuredrop_gravity_dessouky(chi_in,chi_out,T_sat,L,theta):
 
    g=9.807 #[m/s^2]  {At sea level}
    rho_L=IAPWS95(T=T_sat+273.15,x=0).rho
    rho_V=IAPWS95(T=T_sat+273.15,x=1).rho
    alpha_in=1 / (1+( (1-chi_in) / chi_in) * (rho_V/rho_L)**(0.5) )
    alpha_out=1 / (1+( (1-chi_out) / chi_out) * (rho_V/rho_L)**(0.5) )
    DELTAP_g_in = (rho_V*alpha_in+(1-alpha_in)*rho_L)*g*L*math.sin(theta*math.pi/180)
    DELTAP_g_out = (rho_V*alpha_out+(1-alpha_out)*rho_L)*g*L*math.sin(theta*math.pi/180)
    DELTAP_g=(DELTAP_g_in +DELTAP_g_out) / 2 
    return DELTAP_g


#  ## GRAVITATIONAL PRESSURE DROP El-DESSOUKY

# In[15]:


#Chi could be taken as 0.5 as a mean value between the entrance and the output
def Pressuredrop_gravity_dessouky2(chi,T_sat,L,theta): 
    g=9.807 #[m/s^2]  {At sea level}
    rho_L=IAPWS95(T=T_sat+273.15,x=0).rho
    rho_V=IAPWS95(T=T_sat+273.15,x=1).rho
    alpha =1/(1+((1-chi)/chi)*(rho_V/rho_L)**(0.5) )#Void fraction, Zivi (1964)
    DELTAP_g=(rho_V*alpha+(1-alpha)*rho_L)*g*L*math.sin(theta*math.pi/180)
    return DELTAP_g


# ## GRAVITATIONAL PRESSURE DROP Zhao

# In[16]:


def Pressuredrop_gravity(x_in,x_out,T_sat,L,theta):
    g=9.807 #[m/s^2]  {At sea level}
    rho_L= IAPWS95(T=T_sat+273.15,x=0).rho
    rho_V= IAPWS95(T=T_sat+273.15,x=1).rho
    alpha_1=1/(1+(1-x_in)/x_in*(rho_V/rho_L)**(2/3))
    alpha_2=1/(1+(1-x_out)/x_out*(rho_V/rho_L)**(2/3))
    rho_in=alpha_1*rho_V+(1-alpha_1)*rho_L
    rho_out=alpha_2*rho_V+(1-alpha_2)*rho_L
    rho_mean=(rho_in+rho_out)/2
    DELTAP_g=rho_mean*g*L*math.sin(theta*math.pi/180)
    return DELTAP_g


# ##       ACCELERATION PRESSURE DROP during condensation EL-DESSOUKY

# In[17]:


def Pressuredrop_acceleration(chi_1,chi_2,rho_v_1,rho_l_1,rho_v_2,rho_l_2,M,A):
    alpha_1=1/(1+((1-chi_1)/chi_1)*(rho_v_1/rho_l_1)**(0.5))
    alpha_2=1/(1+((1-chi_2)/chi_2)*(rho_v_2/rho_l_2)**(0.5))
    DELTAP_a = M**2*( chi_1**2 / (alpha_1*rho_v_1) + ((1-chi_1)**2) / ((1-alpha_1)*rho_l_1) - chi_2**2/(alpha_2*rho_v_2) - ((1-chi_2)**2) / ((1-alpha_2)*rho_l_2) ) / A**2
    return DELTAP_a


# ##       FRICTIONAL PRESSURE DROP TWO PHASE  -  ESDU 91023

# In[18]:



def Pressuredrop_condensation(N_T,D_i,L,epsilon,m_dot,T_sat,chi_1,chi_2):
    gr=9.81
    g_c=1 #Conversion constant for English Units: 32,174 [lbm * ft / lbf-s ^ 2] or 1 if the units are in the SI
 
    x_in=chi_1
    x_out=chi_2
 
    G=4*m_dot/(math.pi*D_i**2*N_T)#Mass flow per unit area
    if G==0:
        G=0.000001 
    #{DELTAh_v=1.285e5 [J/kg]}
    DELTAh_v=IAPWS95.Vapor_Enthalpy(T=T_sat+273.15, x=1) #Vapor enthalpy
 
    if DELTAh_v==0:
        DELTAh_v=0.000001
    
    H_dot=m_dot*DELTAh_v*(x_in-x_out)
    q_dot=H_dot/(math.pi*D_i*L*N_T) #Medium heat flow
 
    rho_L= IAPWS95(T=T_sat+273.15,x=0).rho
    rho_V= IAPWS95(T=T_sat+273.15,x=1).rho #Vapor density
    a=IAPWS95(T=T_sat+273.15,x=0)
    sigma=a._surface(T=T_sat+273.15)
    mu_L=IAPWS95(T=T_sat+273.15,x=0).mu #Dinamic Viscosity of the liquid
    mu_V=IAPWS95(T=T_sat+273.15,x=1).mu #Dinamic Viscosity of the vapor
 
    '''
    rho_L=1460 #[kg/m^3]
    rho_V=13.4 #[kg/m^3]
    mu_L=385e-6
    mu_V=11.4e-6
    sigma=0.0115
    '''
 
    rho_star=rho_L/rho_V #Density ratio
    mu_star=mu_L/mu_V
    x_m=(x_in+x_out) / 2 #Water vapor title at the midpoint of the pipe
    epsilon_rel=epsilon/D_i #Relative roughness
    Re_L=G*D_i/mu_L #Reynolds number when all the fluid is liquid
    Re_V=G*D_i/mu_V #Reynolds number when all the fluid is liquid
    Fr=(G/rho_L)**2/(gr*D_i) #Froude number for the liquid
    We=G^2*D_i/(rho_L*sigma*g_c) #Weber number for the liquid
    Co=q_dot/ (G*DELTAh_v)
 
    #f_L=0.079 / Re_L**0.25
    A=(-2.457*math.log( (7/Re_L)**0.9+0.27*epsilon_rel))**16 #The exponent 0.9 in equation 4.10 is 2"
    B=(37530/Re_L)**16
    f_L=2*( (8/Re_L)**12 +(A+B)**(-1.5))**(1/12)
    
    #f_V=0,079 / Re_V^0,25
    A2=(-2.457*math.log( (7/Re_V)**0.9+0.27*epsilon_rel ))**16
    B2=(37530/Re_V)**16
    f_V=2*( (8/Re_V)**12 +(A2+B2)**(-1.5))**(1/12)

 
 
    #It is necessary to calculate the gradient of friction pressures in the biphasic region for each of the chosen values of the vapor title
    dp_dz_fr_1=2*f_L*G**2 / (D_i*rho_L) 	#Friction pressure gradient considering all liquid [Pa/m]
    K_in=(1-x_in)**2+x_in**2*(rho_L/rho_V)*(f_V/f_L)
    R_in=K_in+3.43*(x_in**0.685*(1-x_in)**0.24)*(rho_L/rho_V)**0.8*((mu_L/mu_V)-1)**0.89*((1+10**(-220*epsilon_rel))/2) / (Fr**0.047*We**0.0334*(mu_L/mu_V)**1.11)
 
    K_m=(1-x_m)**2+x_m**2*(rho_L/rho_V)*(f_V/f_L)
    R_m=K_m+3.43*(x_m**0.685*(1-x_m)**0.24)*(rho_L/rho_V)**0.8*((mu_L/mu_V)-1)**0.89*((1+10**(-220*epsilon_rel))/2) / (Fr**0.047*We**0.0334*(mu_L/mu_V)**1.11)
 
    K_out=(1-x_out)**2+x_out**2*(rho_L/rho_V)*(f_V/f_L)
    R_out=K_out+3.43*(x_out**0.685*(1-x_out)**0.24)*(rho_L/rho_V)**0.8*((mu_L/mu_V)-1)**0.89*((1+10**(-220*epsilon_rel))/2) / (Fr**0.047*We**0.0334*(mu_L/mu_V)**1.11)
 
    #Calculation of the pressure drop in the biphasic zone
    z_m=L/2
    Int_R_0_L=(R_in+4*R_m+R_out)*z_m/3				#Simpson's Rule
    
    "Correction factor E"
 
    if Co>0 and Co<=0.0003:
        if rho_star>10 and rho_star<=40:
            E=1.4
        if rho_star >40 and rho_star <=150:
            E=1
        if rho_star>150 and rho_star<=600:
            E=1
        if rho_star>600 and rho_star<=1200: 
            E=0.73
        if rho_star>1200 and rho_star<=2100:
            E=0.76
        if rho_star>2100:
            E=1

    if Co>0.0003 and Co<=0.0005:
        if rho_star>10 and rho_star<=40:
            E=1.45
        if rho_star>40 and rho_star<=150:
            E=1
        if rho_star>150 and rho_star<=600:
            E=0.71
        if rho_star>600 and rho_star<=1200:
            E=0.77
        if rho_star>1200 and rho_star<=2100:
            E=0.60
        if rho_star>2100:
            E=1

 
    if Co>0.0005 and Co<=0.0007:
        if rho_star>10 and rho_star<=40:
            E=1.7
        if rho_star>40 and rho_star<=150:
            E=2.06
        if rho_star>150 and rho_star<=600:
            E=1.47
        if rho_star>600 and rho_star<=1200: 
            E=1.74
        if rho_star>1200 and rho_star<=2100: 
            E=1
        if rho_star>2100:
            E=1

    if Co>0.0007 and Co<=0.0009:
        if rho_star>10 and rho_star<=40:
            E=2.75
        if rho_star>40 and rho_star<=150:
            E=1.72
        if rho_star>150 and rho_star<=600:
            E=1.53
        if rho_star>600 and rho_star<=1200: 
            E=1.29
        if rho_star>1200 and rho_star<=2100: 
            E=1.14
        if rho_star>2100:
            E=1
  

 
    if Co>0.0009 and Co<=0.0015:
        if rho_star>10 and rho_star<=40:
            E=3.7
        if rho_star>40 and rho_star<=150:
            E=1.91
        if rho_star>150 and rho_star<=600:
            E=1.65
        if rho_star>600 and rho_star<=1200: 
            E=1.23
        if rho_star>1200 and rho_star<=2100: 
            E=1.43
        if rho_star>2100:
            E=1

 
    if Co>0.0015:
        if rho_star>10 and rho_star<=40:
            E=4
        if rho_star>40 and rho_star<=150:
            E=3
        if rho_star>150 and rho_star<=600:
            E=2.34
        if rho_star>600 and rho_star<=1200: 
            E=2.19
        if rho_star>1200 and rho_star<=2100: 
            E=3.58
        if rho_star>2100:
            E=1
 
 
    #Estimation of the pressure drop by adding the friction and moment components
    rho_V_in=rho_V
    rho_V_out=rho_V_in
 
    DELTAp_accel=G^2*(x_out/rho_V_out-x_in/rho_V_in-(x_out-x_in)/rho_L) 
    DELTAp_fric=dp_dz_fr_1*Int_R_0_L
 
    DELTAp_t=DELTAp_fric+DELTAp_accel
 
    #k_eff=0.04		Engineering coefficient that accounts for the minimization of pressure losses
    k_eff=0.04
 
    #DELTAp|c_t=DELTAp_t*E
    DELTAp_c_t=DELTAp_t*k_eff
 
 
    #Pressure drop at the inlet of the tubes
    DELTAp_in=0.75*G**2*(x_in/rho_V_in+(1-x_in)/rho_L)
    #Losses on departure
    #o losses if it is wel drained
 
    #Total pressure loss in the condenser
    #DELTAp_fric_acc=DELTAp|c_t+DELTAp_in
    DELTAp_fric_acc=DELTAp_c_t
 
    return DELTAp_fric_acc, DELTAp_fric, DELTAp_accel, G, dp_dz_fr_1, Int_R_0_L


# ##       DYNAMIC VISCOSITY OF SATURATED LIQUID WATER EL-DESSOUKY (2002)     

# In[19]:


def Mu_l(T):
    Mu_l = math.exp(-3.79418+604.129/(139.18+T))*0.001
    return Mu_l
#"Dynamic viscosity of saturated liquid water. mu_L in kg/m.s and T in C"


# ##    DYNAMIC VISCOSITY OF SATURATED  WATER VAPOR EL-DESSOUKY (2002)

# In[20]:


def Mu_g(T):
    Mu_g = math.exp (-3.609417664+275.928958/(-227.0446083-0.896081232*T-0.002291383*T^2))*0.001
    return Mu_g
#"Dynamic viscosity of saturated liquid water. mu_G in kg/m.s and T in C"


# ##       ENTRAINMENT RATIO expression for thermocompressor Hassan & Darwish (2014)

# In[21]:



def Hassanra(CR_th,ER):
    if ER>100:
        Ra = -1.93422581403321+2.152523807931*CR_th +113.490932154749 / ER -0.522221061154973*CR_th**2-14735.9653361836 / (ER**2)        -31.8519701023059*CR_th / ER + 0.047506773195604*CR_th**3 + 900786.044551787 / (ER**3)-495.581541338594*CR_th / (ER**2) + 10.0251265889018*(CR_th**2) / ER

    if ER>=10 and ER<=100:
        Ra = -3.20842210618164 + 3.93335312452389 * CR_th + 27.2360043794853/ER -1.19206948677452 * CR_th**2-141.423288255019/ER**2         -22.5455184193569 * CR_th/ER + 0.125812687624122 * CR_th**3 + 348.506574704109/ER**3 + 41.7960967174647 * CR_th/ER**2 + 6.43992939366982 * CR_th**2/ER

    if ER>=2 and ER<10:
        Ra = -1.61061763080868 + 11.0331387899116 * math.log (CR_th) +13.5281254171601/ER -14.9338191429307 * math.log (CR_th)**2-34.4397376531113/ER**2         -48.4767172051364 * math.log (CR_th)/ER + 6.46223679313751 * math.log(CR_th)**3 + 29.9699902855834/ER**3 + 70.8113406477665 * math.log (CR_th)/ER**2         + 46.9590107717394 * math.log (CR_th)**2/ER

    if ER<2:
        Ra = 0
        sys.exit ("This value of ER is not possible")

    return Ra


# ## ENTRAINMENT RATIO expression for thermocompressor El-Dessouky (2014)

# In[22]:


def Dessoukyra(p_m,p_suc,p_comp,T_suc):

    p_suc_kPa = p_suc*0.001
    p_comp_kPa = p_comp*0.001
    p_m_kPa = p_m*0.001
    #El-Dessouky
    PCF = 3E-7*p_m_kPa**2-0.0009*p_m_kPa+1.6101
    TCF = 2E-8*T_suc**2-0.0006*T_suc+1.0047

    Ra = 0.296*( p_comp_kPa**1.19 / p_suc_kPa**1.04 )*(p_m/p_suc)**0.015*(PCF/TCF)

    return Ra


# ## Equality of temperature jumps

# In[23]:


def Equaldeltat(N,salto_temp,salto_temp2):

    #Equal temperature jumps on the effects
    DELTAT=[]
    for i in range (0,N-1):
        DELTAT.append(salto_temp)
    #Equality of temperature jumps in the effects
    DELTAt_preh=[]
    for i in range (0,N-1):
        DELTAt_preh.append(saltp_temp2)
    return DELTAT,DELTAt_preh


# ## Equality of evaporator and preheater areas

# In[24]:


## empty in EES


# ## Equality of effects feeding

# In[25]:


def Equalfeed(N,q_F):
    q_F_series = []
    for i in np.range(N):
        q_F_series.append(q_F/N)
    return q_F_series 


# ## Maximum salinity achieved in the effects

# In[26]:


def Maxsalinity(N,X_b,X_f,q_F):
    q_T = []
    for i in np.range (N-1):
        #q_F[i] / q_T[i] = X_b / (X_b - X_f)
        q_T.append(q_F[i] / (X_b/(X_b-X_f)))
       # q_T(i) = q_F(i)/(X_b/(X_b-X_f))
    return q_T


# ## Calculate the enthalpy

# In[27]:


def Solveenthalpy(T,p):
    psat=IAPWS95(T=T+273.15,x=1).P
    if p<psat+0.0001 and p>psat-0.0001:
        h_vap=IAPWS95(T=T+273.15,x=1).h
        h_liq=IAPWS95(T=T+273.15,x=0).h
    else:
        h_vap=IAPWS95(T=T+273.15,P=p).h
        h_liq=h_vap
    return h_vap,h_liq


# ## Calculate the density

# In[28]:


def Solvedensity(T,p):
 
    psat=IAPWS95(T=T+273.15,x=1).P
    if p<psat+0.0001 and p>psat-0.0001:
        rho_vap=IAPWS95(T=T+273.15,x=1).rho
        rho_liq=IAPWS95(T=T+273.15,x=0).rho
    else:
        rho_vap=IAPWS95(T=T+273.15,P=p).rho
        rho_liq=rho_vap
    return rho_vap,rho_liq


# ## Calculate the specific heat cp

# In[29]:


def Solvecp(T,p):
    psat = IAPWS95(T=T+273.15,x=0).P
    if abs(p-psat)<0.0001:
        cp_vap = IPAWS95(T=T+273.15,x=1).cp
        cp_liq = IAPWS95(T=T+273.15,x=0).cp
    else:
        cp_vap = IAPWS95(T=T+273.15,P=p*10**-6).cp
        cp_liq = cp_vap
    return cp_vap


# ## Procedure that checks the friction losses in the pipes do not exceed a maximum limit

# In[30]:


def Compruebap(DELTAp_pipe_max,DELTAp_pipe):
    if DELTAp_pipe>DELTAp_pipe_max:
        warnings.warn("Pressure losses are very high. Increase the diameter of the pipes")
        DELTap_pipe2=DELTAp_pipe_max
    else:
        DELTap_pipe2=DELTAp_pipe
    return DELTap_pipe2


# ## Procedure that checks the pressure losses in the pipes that connect the effects

# In[31]:


def Compruebadeltap_pipe(p_prime_v,DELTAp_pipe2):
    if DELTAp_pipe2>p_prime_v:
        sys.exit("Pressure losses are very high in the pipes that connect the effects. Increase the diameter of the pipes")
    c = p_prime_v-DELTAp_pipe2
    return c


# ## Procedure that checks the pressure losses in the evaporator tubes

# In[32]:


def Compruebadeltap_cond(p_prime_v, DELTAp_cond):
    if DELTAp_cond>p_prime_v:
        sys.exit("Pressure losses are very high in the evaporator tubes. Increase the diameter of the pipes")
    return p_prime_v-DELTAp_cond


# ## Bookmark cooling "COMPRUEBA EL COOLING"

# In[33]:


def Compruebacooling(q_cw, beta):
    if q_cw<0:
        R_factor = beta-0.2;
    else:
        R_factor = beta;
    if beta>=0.9:
        R_factor = beta-0.06;
    else:
        R_factor = beta
        return R_factor


# In[34]:


def Calculafeed(N,N_effect,R_factor):
    if N_effect<N:
        for i in np.arange(N_effect-1):
            q_F[i]=q_F[i+1]
        for i in np.arange(N_effect,N):
            q_F[i]=q_F[N_effect-1]*R_factor
    if N_effect>=N:
        for i in np.arange(N-1):
            q_F[i+1]=q_F[i]       


# ## MODEL MED-TVC-PC

# In[35]:


## input to test the model and the real data from the plant; not all inputs are used, some are copy and paste from EES model.
# Take Table 1 and table 2 in the paper as reference for the base model.
N=12
N_effect = 12
X_f=40000            #[ppm]    {Salinity of seawater feed}
T_jump=10            #[c]      {Temperature jump in the final condenser}
T_f = 35            #[c]       {Feed seawater temperature}
T_in=22              #[C]      {Seawater temperature at the entrance}
T_s=64.5             #[C]      {Saturated external steam temperature}
T_VN = 37            #[C]      Vapor temperature in the last cell
X_b=70000            #[ppm]    {Salinity of brine output}
p_m=4414500         #[MPa]     {Steam pressure}
q_in=5               #[kg/s]   {Seawater inlet flow}
DTT_c=5              #[C]      {DTT in the final condenser}
DTT_preh=3           #[C]      {It is the minimum DTT in preheaters}
DTT_min=DTT_preh 
#DTT_preh[1]=3        #[C]      {When imposing the same Aprec restriction, one more equation needs to be added. If DTT_preh's are imposed, the areas are different}
rho_p=200            #[kg/m^3] {Density of the dehumidifying mesh}
L_demister=0.15    #[m]      {The thickness of the mesh is between 10 and 20 cm}
L_pipes=2            #[m]}     {Length of the pipes connecting the effects}
delta_w=0.28         #[mm]     {Grid holes diameter}
delta_i=75000        #[mm]     {Inner diameter of the pipes connecting the effects}
V_vapor=1            #[m/s]    {Vapor velocity in dehumidifying mesh}
epsilon=0.000005     #[m]      {Roughness tubes}
D_evap_int=0.018   #[m]      {Internal diameter of evaporator tubes}
D_evap_ext=0.022    #[m]     {External diameter of evaporator tubes}
L_evap=7             #[m]    {Length of evaporator tubes}
v_s_evap=30          #[m/s]    {Evaporator vapor velocity}
chi_in=0.99          #         {Vapor title at the inlet of the evaporator tubes}
chi_out=1*10**-9
T_s_sobrec=T_s+3    
q_D_m3d=9000        #[m^3/d]
rho_D = 1 #kg/L
q_D_Th=q_D_m3d*rho_D*1000/24 #kg/h
q_D = q_D_Th/3600
T = np.zeros(N)
A_fix=5656           #[m^2]
A_preh_fix=107.1     #[m^2]
A_c=2092             #[m^2]
t_preh = np.zeros(N)
Ra = 1.536
#beta? it should be the ratio of area of heat transfer after thermocompressor versus area before thermocompressor
t_preh[N-1]=T_f               #{The input temperature of the last preheater is that of the feed}	


# In[36]:


## Simplified calculation of the model


# ## Relationships and restrictions

# In[37]:


## Temperature is assumed in linear reduction 
T[N-1]= T_VN
T_V=T


# In[38]:


DELTAT = (T_s - T[N-1])/N 
for i in np.arange(N):
    if i == 0:
        T[i] = T_s - DELTAT # Ti is effect (brine) temperature
    else:
        T[i] = T[i-1] - DELTAT
t_preh[0] = t_preh[N-1]+DELTAT*(N-1) # temperature of preheaters
for i in np.arange(N-1):
    t_preh[i] = t_preh[0]-DELTAT
    


# In[39]:


## pressure


# In[40]:


p_i = np.zeros(N)
for i in np.arange (N):
    p_i[i]=(IAPWS95(T=T[i]+273.15,x=1).P)
p_prime=[]
for i in np.arange(N):
    p_prime.append(Pressuredrop_demister(rho_p,V_vapor,delta_w)*10**-6+p_i[i])


# In[41]:


## Property profiles


# In[42]:


lambda_v = []
h = []
h_prime = []
T_prime = []
rho_v = []
volume_v = []
lambda_v_prime = []
rho_prime = []
for i in np.arange (N):
    T_prime.append(IAPWS95(P=p_prime[i],x=1).T)
    h.append(IAPWS95(T=T_V[i]+273.15,x=1).h)
    rho_prime.append(IAPWS95(T=T_prime[i],P=p_prime[i]).rho)
    rho_v.append(IAPWS95(T=T_V[i],P=p_i[i]).rho)
    volume_v.append(IAPWS95(T=T_prime[i],P=p_prime[i]).v)
h_prime = h #The process that the steam undergoes through the mesh is assumed to be isentropic


# In[43]:


## mass flow rate


# In[44]:


q_Di=q_D / N
q_T_max=q_D
q_FE_i = []     # Flashing of the brine
q_B_i = []      # Brine flow rate
q_F_i = []      # Feed water mass flow rate
for i in np.arange (N+1):
    q_B_i.append(q_Di*2*i)
for i in np.arange (N):
    q_F_i.append(q_B_i[i+1]-q_B_i[i]+q_Di)
for i in np.arange(N):
    q_FE_i.append(q_F_i[i]+q_B_i[i]-q_B_i[i+1]-q_Di)
q_F = np.sum(q_F_i)

# empirical functions from EES design model
q_m = 0.02587*T_s**2-2.847*T_s+82.31 # in (kg/s)
q_intake = 1.971*math.exp(0.08069*T_s) # in (kg/s)

q_cw = q_intake-q_F
GOR = q_D/q_m


# In[45]:


## salinity


# In[46]:


X = np.zeros(N)


# In[47]:


X[0] = q_F_i[0]*X_f/1000/q_B_i[1]  ## Salinity of first effect


# In[48]:


for i in np.arange(1,N):
    X[i] = q_F_i[i]*X_f/1000/(q_B_i[i+1]-q_B_i[i]) ## Salinity of effect 2...N


# ## Flow rate in T/h

# In[49]:


q_F_Th = q_F*3.6
q_B_Th = q_B_i[N]*3.6
q_intake_Th = q_intake*3.6
q_m_Th = q_m*3.6
q_cw_Th = q_cw*3.6


# ## Evaparator area

# ### Heat transfer equation associated with the first evaporator

# In[50]:


A = (q_Di*h[0]+q_F_i[0]*Solvecp((T[0]+t_preh[0]),p_i[0])*(T[0]-t_preh[0]))/(T_s-T[0])/U_e(T[0])
# use function Solvecp and U_e defined before
print ('Evaporator area',A)


# ## Number of tubes of evaporator

# In[51]:


N_evap = A/(math.pi*D_evap_int*L_evap) # number of tubes
print('number of tubes',N_evap)


# ## TRAPANI ERROR VALIDATION 

# In[52]:


E_T1 = 100*(T[0]-62.2)/62.2
print('Vapor temperature in the 1st effect',E_T1)
E_T5 = 100*(T[4]-53)/53
print('Vapor temperature in the 5th effect',E_T5)
E_T11 = 100*(T[10]-39.3)/39.3
print('Vapor temperature in the 11th effect',E_T11)
E_qF = 100*(q_F_Th-1130.4)/1130.4
print ('Feed water flow rate', E_qF)
E_qB = 100*(q_B_Th-755)/755
print ('Brine Blowdown mass flow rate', E_qB)
E_s = 100*(X[11]-59.9)/59.9
print ('Brine blowdown salinity',E_s)
E_qintake = 100*(q_intake_Th-1280)/1280
print('Intake sea water mass flow rate',E_qintake)
E_qcw = 100*(q_cw_Th-149.6)/149.6
print('Cooling mass flow rate',E_qcw)
E_qm = 100*(q_m_Th-22.5)/22.5
print('Motive steam flow rate',E_qm)
E_GOR = 100*(GOR-16.7)/16.7 
print('GOR',E_GOR)
E_Nt = 100*(N_evap-11000)/11000
print('Number of tubes in evaporators',E_Nt)


# # EES equations for reference and further calculation:

# # Universal gas constant particularized
# Rg= 8314/18.02    #{Rg=(R# / Molarmass(water)，R# = 8314 J/kmol-K ; Molarmass = 18.02 kg/kmol }
# #{Feedwater water temperature after final condenser}
# T_f=T_in+DTT_c            
# #"Ec. Final condensador design"
# T_c=T_f+DTT_c

# ## Equal evaporator areas

# A_i= []
# for i in np.arange (0,N_effect): #i=1,N_effect
#     A_i.append(A_fix)

# for i in np.arange (N_effect,N):
#     A_i.append(A_fix*beta)
# #{A_after=A_fix*beta} 
# #beta=1-y_effect ?
# #y_efffect is the fraction of vapor from the former effect used as suction vapor in the thermocompressor 
# #find y-effect in q_suc=y_effect*(1-alpha[N_effect])*q_T[N_effect] in thermocompressor section
# 

# # Equal preheater areas

# A_preh=np.zeros(N)
# for i in np.arange (1,6):
#     A_preh[2*i-1]=A_preh_fix
# for i in np.arange(0,5):
#     T_prime[2*i-1]=t_preh[2*i-1]+DTT_preh[2*i-1] #The DTT_preh is calculated from here

# ## Initial estimation of the condensed steam fractions in the preheaters

# alpha_i = np.zeros(N)
# for i in np.arange(N):
#     alpha_i[i]= 0.1

# ## Variation range of some variables

# In[ ]:


#A_max=6000		:	A_min=600 for the parametric table with pm=3.04}
#A_max=10000
#A_min=400
#{T_min=10		:	T_max=90}
#{h_min=0,0001 	:	h_max=4500}
#{U_min=1		:	U_max=5}
#{X_min=0,0001	:	X_max=120000}
#{D_min=0,0001}	;	{D_max=q_D}
#{s_min=s_f		:	s_max=X_b/1000}
#s_min=20		
#s_max=120
#{A_preh_min=A_preh_i[1]-4	:	A_preh_max=A_preh_i[1]+4}
#A_preh_min=2		
#A_preh_max=300
#{p_min=10		:	p_max=101325 }
#{ER_min=2		:	ER_max=10000}
#{Ra_min=1		:	Ra_max=12}
#{cpmin=1		:	cpmax=5 }
#{NEA_min=0		:	NEA_max=10}
#{q_D_min=0.5	:	q_D_max=4200
#q_F_min=1			
#q_F_max=4000
#q_comp_min=0.5	
#q_comp_max=1000
#{q_dsh_min=0.001	:	q_dsh_max=20}
#{q_Di_min=q_D/(N+4):	q_Di_max=q_D/(N-4)}
#{q_Di_min=1:	q_Di_max=30}
#{q_Fi_max=q_D/2: Q_max=1000*q_D}
#EPE_max=2
#DTT_preh_max=30
#DELTAT_preh_max=20
#{DELTAT_max=DELTAT+10}
#DELTAp_pipe_max=80000 #Pa
#{K_area=70}
#{K_area_preh=15}
#X_guess=60000 # salinity of brine out in ppm


# ## Global mass and salt balances

# q_in=q_F+q_cw

# ## Total distilled flow produced

# q_D=sum(q_T)-sum(q_FB)

# ##original temperature equations in EES

# for i in np.arange (N-1):
#     EPE[i]=bpe_mit(T[i], s[i])
#     T[i]=T_V_sat[i]+EPE[i]
#     p[i]=IAPW95(T=T[i]+273.15,x=1).p #the vapor pressure could be calculated with the T_V and the library of pure water too
#     T_V_sat[i]=IAPWS95(P=p[i],x=1).T
#     p_prime[i]=p[i]-DELTAp_m[i]             #The vapor pressure after the demister is equal to the pressure before minus losses
#     T_V[i]=T[i] #{Thermodynamic Balance Condition}
#     lambda_v[i]=IAPWS95(T=T_V[i],P=p[i]).Hvap
#     h[i]=IAPWS95(T=T_V[i],P=p[i]).h
#     h_prime[i]=IAPWS95(T=T_prime_V[i],P=p_prime[i]).h
#     lambda_v_prime[i]=IAPWS95(T=T_prime_V[i],P=p_prime[i]).Hvap
#     p_prime_v[i] = p_prime[i]
#     rho_prime_v[i]=IAPWS95(T=T_prime_V[i],P=p_prime[i]).rho
#     rho_v[i]=IAPWS95(T=T_V[i],P=p[i]).rho
#     volume_v[i]=IAPWS95(T=T_prime_V[i],P=p_prime[i]).v
#     q_V_ef[i]=(1-alpha[i])*q_T[i]
#     q_C_ef[i]=alpha[i]*q_T[i]
#     p_sat[i]=IAPWS95(T=T_V_sat[i],x=1).P
#     h[i]=h_prime[i]#{The process that the steam undergoes through the mesh is assumed to be isentropic}

# ## Definition of steam condensation temperatures inside the evaporator tubes

# for i in np.arange(N-1):
#     T_c[i] = T_prime_V_sat[i] - DELTAT_pipe[i]-DELTAT_cond[i]
# T_c = T_prime_V[N-1] - EPE[N-1]- DELTAT_pipe[N-1]

# ## defination of temp jump

# for i in np.arange(N-1):
#     DELTAT[i]=T[i]-T[i+1]
#     DELTAt_preh[i]=t_preh[i]-t_preh[i+1]

# rho_brine = []
# for i in np.arange(N):
#     rho_brine.append(SeaWater(T=T[i],P=0.1,S=X[i]).rho) # EES define a seawater condition with only T and S, so assumed P is 0.1 MPa?

# DELTAT_m_sat = []
# for i in np.arange(N):
#     DELTAT_m_sat.append(T_V[i]-T_prime[i])

# ## Parallel power configuration ratios

# q_F= np.zeros(N)
# R_factor = Compruebacooling(q_cw, beta)
# for i in np.arange(N_effect-1):
#     q_F[i]=q_F[i+1]
# for i in np.arange(N_effect,N):
#     q_F[i]=q_F[N_effect]*R_factor

# ## Number of pipes

# for i in np.arange (N-1):
#     N_t_evap[i]=A[i+1] / (math.pi*D_evap_ext*L_evap)
#     v_s_evap[i]=(1-alpha[i])*(1-y[i])*q_T[i] / (rho_steam[i]*N_t_evap[i]*(math.pi*D_evap_int**2 / 4) )
#     rho_steam[i]=IAPWS95(T=T_prime_V[i],x=1).rho #{Assume saturated}

# ## Tube wetting rate

# for i in np.arange(N-1):
#         #{WR[i]=0.01} {debe estar entre 0,03 y 0,14 kg/m-s}
#         WR[i]=q_F[i+1]/ (N_rt[i]*L_evap)
#         N_rt[i]=math.sqrt(N_t_evap[i])

# ## Balances of the effects

# ## Effect 1

# q_s*lambda_s+ q_s*cp_s_sobrec*(T_s_sobrec-T_s) +q_F[0]*h_preh[1]+q_FB[0]*h_dprime_v[0]=(1-alpha[0])*q_T[0]*h_prime_v[0]+alpha[0]*q_T[0]*h_prime_c[0]+q_B[0]*h_B[0]	# Energy balance
# q_T[0]=q_D[0]+q_FB[0] #{In the first effect there is no flash steam, only the one produced by boiling and the flash of the FB1 associated to the q_suc + q_dsh due to the thermocompressor}
# q_F=q_B[0]+q_D[0] #"Material balance in the first effect"
# q_F[0]*X_f=q_B[0]*X[0] #{Salt balance}

# ## Properties

# T_s_mean=(T_s_sobrec+T_s)/2
# cp_s_sobrec=IAPWS95(T=T_s_mean+273.15,P=p_comp).cp
# lambda_s=IAPWS95(T=T_s,P=p_s).Hvap
# h_preh[1]=SeaWater(T=t_preh[1],P=1,S=s_f).h # kJ	
# s_f=X_f/1000
# h_prime_v[0]=IAPWS95(T=T_prime_V[0],P=p_prime[0]).h
# h_prime_c[0]=IAPWS95(T=T_prime_V[0],x=0).h
# h_B[0]=SeaWater(T=T[0],P=0.1,S=s[0]).h #kJ 
# s[0]=X[0]/1000

# ## Heat exchanged

# In[ ]:


Q[0]=q_F*cp_mean[0]*(T[0]-t_preh[0])+q_D[0]*lambda_v[0]
Q[0]=A[0]*U[0]*(T_s-T[0])
cp_mean[0]=SeaWater(T= T_mean[0],P=0.1, S=s_mean[0]).h # kJ
T_mean[0]=(T[0]+t_preh[0])/2
s_mean[0]=(s[0]+s_f)/2
U[0]=U_e(T[0])
p_s=IAPWS95(T=T_s,x=1).p
p_c[0]=p_s


# ## Effects 2..N-1

# for i in np.arange(1,N-1):
#     ((1-y[i-1])*(1-alpha[i-1])*q_T[i-1]*lambda_c[i-1]+q_FB[i]*h_dprime_v[i] + q_B[i-1]*h_B[i-1] = (1-alpha[i])*q_T[i]*h|star_v[i] + alpha[i]*q_T[i]*h|star_c[i] + q_F*cp_mean[i]*(t_preh[i]-t_preh[i+1]) + q_B[i]*h_B[i])
#     q_B[i-1]=q_B[i]+q_D[i]+q_FE[i] #"Mass balance"
#     q_F[i]*X_f+q_B[i-1]*X[i-1]=q_B[i]*X[i]
#     q_FE[i]*lambda_f[i]=q_B[i-1]*cp_mean_f[i]*(T[i-1]-T_f[i])	#"Flash steam generated in the effect"

# ## Properties

# lambda_c[i-1]=IAPWS95._Vapor_Enthalpy(T=T_c[i-1]) #Enthalpy_vaporization
#         #h|star_v[i]=Enthalpy(Steam_IAPWS;T=T_prime_V[i];P=p_prime[i])
# h_star_v[i]=2498-0.0001366*p_prime[i]+1.904*T_prime_V[i] #"Surface adjustment facilitates convergence"
# h_dprime_v[i]=IAPWS95(T=T_dprime_V[i],x=1).h
# h_star_c[i]=IAPWS95(T=T_prime_V[i],x=0).h
# h_B[i]=SeaWater(T=T[i],P=0.1,S=s[i]).h # kJ	Sw_enthalpy(T[i],s[i])*Convert('J','kJ')
# s[i]=X[i]/1000
# lambda_f[i]=SeaWater(T=T_mean[i],P=0.1,S=s_f).h - IAPWS95(T=T_mean[i],x=1).h  #Sw_latentheat(T[i],s[i-1])*Convert('J','kJ') 	"the latent heat of the flash steam produced is calculated at the temperature of the effect steam, Ti"
# cp_mean[i]=SeaWater(T=T_mean[i],P=0.1,S=s_f).cp #Sw_spcheat(T_mean[i],s_f)*Convert('J','kJ')		"! Using the internal EES function to calculate the CP slows convergence a lot, although the value of Apreh, Ac, etc. is more accurate."
# T_mean[i]=(t_preh[i]+t_preh[i+1])/2
# cp_mean_f[i]=SeaWater(T=T_mean_f[i],P=0.1,S=s[i-1]).cp #Sw_spcheat(T_mean_f[i],s[i-1])*Convert('J','kJ')
# T_mean_f[i]=(T[i-1]+T_f[i])/2
# T_f[i]=T[i]+NEA[i]
# NEA[i]=Nea(T[i-1],T[i],T_V[i])
# Q[i]=(1-y[i-1])*(1-alpha[i-1])*q_T[i-1]*lambda_c[i-1]
# Q[i]=A[i]*U[i]*(T_c[i-1]-T[i])
# U[i]=U_e(T[i])
# q_T[i]=q_D[i]+q_FE[i]+q_FB[i]
# p_c[i-1]=p[i-1]-DELTAp_m[i-1]-DELTAp_pipe[i-1]-DELTAp_cond[i-1]

# ## Effect N

# (1-y[N-2])*(1-alpha[N-2])*(q_D[N-2]+q_FE[N-2]+q_FB[N-2])*lambda_c[N-2]+q_FB[N-1]*h_dprime_v[N-1]+q_B[N-2]*h_B[N-2]+q_F[N-1]*h_f[N-1]=(q_D[N-1]+q_FE[N-1]+q_FB[N-1])*h_star_v[N-1]+q_B[N-1]*h_B[N-1]
# q_B[N-2]+q_F[N-1]=q_B[N-1]+q_D[N-1]+q_FE[N-1]
# q_B[N-2]*X[N-2]+q_F[N-1]*X_f=q_B[N-1]*X[N-1]
# q_FE[N-1]*lambda_f[N-1]=q_B[N-2]*cp_mean_f[N-]*(T[N-2]-T_f[N-1])
# #{	q_T[N-2]*lambda_c[N-2]=q_D[N-1]*lambda_v[N-1]}

# lambda_c[N-2]=IAPWS95._Vapor_Enthalpy(T=T_c[N-2])

# #Enthalpy
# h_star_v[N-1]=IAPWS95(T=T_prime_V[N-1],P=p_prime[N-1]).h
# 
# h_dprime_v[N-1]=IAPWS95(T=T_dprime_V[N-1],x=1).h
# 
# h_B[N-1]=SeaWater(T=T[N-1],P=0.1,S=s[N-1]).h
# 
# s[N-1]=X[N-1]/1000
# 
# lambda_f[N-1]=SeaWater(T=T[N-1],P=0.1,S=s[N-2])-IAPWS95(T=T[N-1],x=1) #KJ
# 
# cp_mean_f[N-1]=SeaWater(T=T_mean_f[N-1],P=0.1,S=s[N-2]).cp
# 
# T_mean_f[N-1]=(T[N-2]+T_f[N-1])/2
# T_f[N-1]=T[N-1]+NEA[N-1]
#  
# Nea[N-1]=Nea(T[N-2],T[N-1],T_V[N-1])
# U[N-1]=U_e(T[N-1])
# Q[N-1]=A[N-1]*U[N-1]*(T_c[N-2]-T[N-1])
# Q[N-1]=(1-y[N-2])*(1-alpha[N-2])*(q_D[N-2]+q_FE[N-2]+q_FB[N-2])*lambda_c[N-2]
# epsilon_ev[N-1]=1-math.exp(-NTU_ev[N-1])
# NTU_ev[N-1]=U[N-1]*A[N-1] / C_min[N-1]
# C_min[N-1]=Min(q_F[N-1]*c_p[N-1],q_T[N-2]*c_psteam[N-1])
# c_psteam[N-1]=IAPWS95(T=T[N-2],x=1).cp
# c_p[N-1]=SeaWater(T[N-1],s[N-2]).cp
#  
# 
# 
# p_c[N-1]=p[N-2]-DELTAp_m[N-2]-DELTAp_pipe[N-2]-DELTAp_cond[N-2]

# ## Condensador final

# q_in*(h_f[N-1]-h_in)=q_cond*lambda_c 
#  
# cp_sw_c=SeaWater(T=T_mean_c,P=0.1,S=s_f).cp #kJ
# T_mean_c=(T_in+T_f)/2
#  
# q_cond=(1-y[N-1])*(q_D[N-1]+q_FE[N-1]+q_FB[N-1])
#  
# h_in=SeaWater(T=T_in,P=0.1,S=s_f).h
# h_c=IAPWS95(T=T_c,x=0).h
# h_f=[]
# for i in range (N-2):
#     h_f[i]=SeaWater(T=t_preh[i],P=0.1,S=s_f).h
# 
# 
# h_f[N-1]=SeaWater(T=T_f,P=0.1,S=s_f).h
# p_c=IAPWS95(T=T_c,x=1).p
# lambda_c=IAPWS95._Vapor_Enthalpy(T=T_c)
# 
#  
# Q_c=(1-y[N-1])*(q_D[N-1]+q_FE[N-1]+q_FB[N-1])*lambda_c
# Q_c=A_c*Uc*DTLM_c
# DTLM_c=(DELTAT_e-DELTAT_s)/np.log(denC)
# denC=DELTAT_e/DELTAT_s
# DELTAT_e=T_c-T_in
# DELTAT_s=T_c-T_f
# 
# #"NTU-effectiveness method"
# #{cp_sw_c=(h_f[N-1]-h_in) / (T_f[N-1]-T_in) "Minimum heat capacity>= that of non-state-changing fluid"
# C_c_min=cp_sw_c*q_in
# Q_c_max=C_c_min*(T_c-T_in) #"Maximum heat: Cmin x DeltaTmax"
# Q_c=q_in*(h_f[N-1]-h_in)
# epsilon_c=Q_c / Q_c_max	        #"Exchanger efficiency"
# epsilon_c=1-math.exp(-NTU_c) #"For exchangers with phase change"
# UA_c=NTU_c*C_c_min
# 
# Uc=U_c(T_c)
# 
# #{T_f=T_c-math.exp((UA_c)/(q_in*cp_sw_c))*(T_c-T_in)}

# ## Preheaters

# #"From the i = 1..N-1. It takes into account the small steam overheating due to the EPE"
# T_prime_V_sat=[]
# for i in np.arange(N):
#     T_prime_V_sat.append(T_sat(Steam_IAPWS,P=p_prime[i]))
# 
# def Sum(lst,beginPos,endPos):
#     res=0
#     for i in range (beginPos,endPos):
#         res += lst[i]
#     return res
# 
# for j in np.arange(5):
#     (q_F-Sum(q_F,j*2,N-1))*cp_mean_preh[j*2]*(t_preh[j*2]-t_preh[j*2+1])=alpha[j*2]*(q_T[j*2])*lambda_star_v[j*2] + alpha[j*2]*(q_T[j*2])*cp_mean_EPE[j*2]*(T_prime_V[j*2]-T_prime_V_sat[j*2]) #Balance de energía utilizando cp (parece converger mejor)}
#     #{cp_mean_EPE[j*2]=cp(steam;T=T_mean_prime_V[j*2];p=p_prime[j*2])}
#     cp_mean_EPE[j*2]=1.917+7.303e-06*p_prime[j*2]-0.001324*T_mean_prime_V[j*2]+4.899e-12*p_prime[j*2]**2+-5.968e-08*p_prime[j*2]*T_mean_prime_V[j*2]+1.08e-05*T_mean_prime_V[j*2]
#     T_mean_prime_V[j*2]=(T_prime_V[j*2]+T_prime_V_sat[j*2])/2
#     lambda_star_v[j*2]=IAPWS95._Vapor_Enthalpy(T=T_prime_v[j*2])
#     cp_mean_preh[j*2]=SeaWater(T=T_mean_preh[j*2],P=0.1,S=s_f).cp
#     T_mean_preh[j*2]=(t_preh[j*2]+t_preh[j*2+1])/2
#  
#     #"Heat transfer equations"
#     q_F_int[j*2]=(q_F-Sum(q_F,j*2,N-1))
#     Q_preh[j*2]=A_preh[j*2]*U_preh[j*2]*DTLM_preh[j*2]
#     U_preh[j*2]=U_c(T_prime_V[j*2])
#     #{Q_preh[i]=alpha[i]*(q_T[i])*lambda_star_v[i]}
#     
#     DTLM_preh[j*2]=(t_preh[j*2]-t_preh[j*2+1]) / np.log(vble[j*2] )	
#     vble[j*2]= (T_prime_V[j*2]-t_preh[j*2+1]) / (T_prime_V[j*2]-t_preh[j*2])
#     t_preh[j*2]=T_prime_V[j*2]-math.exp( (-U_preh[j*2]*A_preh[j*2]) / (q_F_int[j*2]*cp_mean_preh[j*2]) )*(T_prime_V[j*2]-t_preh[j*2+1])  
# 
# for j in np.arange(6):
#     t_preh[2*j-1]=t_preh[2*j]
#     alpha[2*j-1]=0
#     A_preh[2*j-1]=0
#     q_F_int[2*j-1]=(q_F-Sum(q_F[k],k=2*j,12))
# 

# ## Condensate chambers (Flashing boxes)

# ## The first and last cameras are different from the rest

# ## Chamber 1

# h_s_c=IAPWS95(T=T_s,x=0).h
# h_dprime_c[0]=IAPWS95(T=T_dprime[0],x=0).h
# h_dprime_v[0]=IAPWS95(T=T_dprime_V[0],x=1).h
# 
# #"The flash chamber associated with effect 1 exists only with TVC"
#  
# (q_suc+q_dsh)+alpha[0]*q_T[0]=q_C[0]+q_FB[0]
#  
# (q_suc+q_dsh)*h_s_c+ alpha[0]*q_T[0]*h_prime_c[0] = q_C[0]*h_dprime_c[0] + q_FB[0]*h_dprime_v[0]
#  
# T_dprime[0]=T_dprime_V[0]+NEA_dprime[0] #"Imbalance: during the pressure change the temperature changes, under the residence time of the steam"
#  
# Nea_dprime[0]=nea(T_s,T_dprime[0],T_dprime_V[0])
#  
# T_dprime_V[0]=T_prime_V[0]  #{Hypothesis}

# ## Chambers 2...N-1

# for i in np.arange(2,N):
#     #q_C[i-1]*h_dprime_c[i-1]+(1-y[i-1])*(1-alpha[i-1])*q_T[i-1]*h_c[i-1] + alpha[i]*q_T[i]*h|star_c[i] = &
#     #q_FB[i]*h_dprime_v[i] + q_C[i]*h_dprime_c[i]
#     q_C[i] = q_C[i-1]+(1-y[i-1])*(1-alpha[i-1])*q_T[i-1]-q_FB[i]+alpha[i]*q_T[i]
#     T_dprime[i]=T_dprime_V[i]+NEA_dprime[i]
#     Nea_dprime[i]=Nea(T_c[i-1],T_dprime[i],T_dprime_V[i])
#     T_dprime_V[i]=T_prime_V[i]
#     #Properties
#     h_c[i-1]=IAPWS95(T=T_c[i-1],x=0).h
#     h_dprime_c[i]=IAPWS95(T=T_dprime[i],x=0).h

# ## Condensate mixer N

# #q_C[N-1]*h_dprime_c[N-1]+(1-y[N-1])*(1-alpha[N-1])*q_T[N-1]*h_c[N-1]+(1-y[N])*q_T[N]*h_c- q_FB[N]*h_dprime_v[N]=q_C[N]*h_dprime_c[N]
# q_C[N]=q_C[N-1]+(1-y[N-1])*(1-alpha[N-1])*q_T[N-1]+(1-y[N])*q_T[N]-q_FB[N] - q_dsh
# T_dprime[N]=T_dprime_V[N]+NEA_dprime[N]
# Nea_dprime[N]=Nea(T_c[N-1],T_dprime[N],T_dprime_V[N])
# T_dprime_V[N]=T_prime_V[N]
# h_c[N-1] = IAPWS95(T=T_c[N-1],X=0).h
# h_dprime_c[N]=IAPWS96(T=T_dprime[N],x=0).h
# q_T[N] = q_D[N]+q_FE[N]+q_FB[N]

# ## Plate Heat Exchangers

# #"PHX1 - Distillate"
# q_w_out_PHX1=q_w_in_PHX1
# T_d_in=T_dprime[N]
# T_w_in_PHX1=T_intake
# T_w_out_PHX1=T_w_in_PHX1
#  
# #"PHX2 - Brine"
# q_w_out_PHX2=q_w_in_PHX2
# T_b_in=T[N]
# T_b_out=T_b_in
# s_B=X[N]/1000
# T_w_in_PHX2=T_intake
# T_w_out_PHX2=T_w_in_PHX2
#  
# q_w_in_PHX1+q_w_in_PHX2=q_in
# 
#  
# #"Hipótesis"
# q_sw_in_PHX1=q_sw_in_PHX2

# ## Thermodynamic losses

# #Dehumidifying mesh
# DELTAP_p=[]
# DELTAT_m=[]
# DELTAT_m[0]=T_V_sat[0]-T_prime_V_sat[0]
# V_vapor[0] =(q_D[0])/(rho_v[0]*Pi*(D_vessel/2)**2)
# DELTAP_p.append(Pressuredrop_demister(rho_p,V_vapor[0],delta_w))
# DELTA_m.append(DELTApL_m[0]*L_demister)
# for i in np.arange(1,N):       
#     V_vapor[i] = (q_D[i]+q_FB[i])/(rho_v[i]*Pi*(D_vessel/2)**2)
#     DELTAP_p.append(Pressuredrop_demister(rho_p,V_vapor[i],delta_W))
#     DELTAT_m.append(0)

# In Trapani there are only demisters in some effects; It is assumed that only in the 1st effect"

# ## Pipeline transmission losses

# DELTAP_pipe=[]
# p_clines = []
# T_clines_sat = []
# DELTAT_pipe = []
# c = []
# for i in np.arange(0,N-1):
#     DELTAP_pipe.append(Pressuredrop_lines2((1-y[i])*(1-alpha[i])*q_T[i],L_pipes,delta_i,T_prime_V_sat[i])
# DELTAP_pipe2.append((1-y[N-1])*(q_D[N-1]+q_FE[N-1]+q_FB[N-1]),L_pipes,delta_i,T_prime_V_sat[N-1])    
# for i in np.arange(0,N):
#     c.append(Compruebadeltap_pipe(p_prime_v[i], DELTAP_pipe[i])
# for i in np.arange(0,N):
#     p_clines.append(p_prime_v[i]-DELTAP_pipe[i])
#     T_clines_sat.append(IAPWS95(P = p_clines[i],x=1).T)
#     DELTAT_pipe.append(T_prime_V_sat[i]-T_clines_sat[i])

# ## Condensation losses inside the evaporator tuves of effect 2 to N

# #Pressure losses inside the tubes are due to three effects: static pressure, linear momentum and friction 
# #2..N effects are considered, where the condensation temperature of the vapor inside the evaporator tubes i, is Tc, i-1
# theta = 0
# chi = 0.2
# d = []
# DELTAP_gD = []
# DELTAP_g2D = []
# DELTAP_g = []
# DELTAp_cond = []
# for i in np.arange(0,N-1):
#     d.append(Compruebadeltap_cond(p_prime_v[i], DELTAp_cond[i]))
#     DELTAP_gD.append(Pressuredrop_gravity_dessouky(chi_in,chi_out,T_clines_sat[i],L_evap,theta)
#     DELTAP_g2D.append(Pressuredrop_gravity_dessouky2(chi,T_clines_sat[i],L_evap,theta)
#     DELTAP_g.append(Pressuredrop_gravity(chi_in,chi_out,T_clines_sat[i],L_evap,theta,fluid$)
#     DELTAp_cond.append(Pressuredrop_condensation(N_t_evap[i],D_evap_ext,L_evap,epsilon,(1-y[i])*(1-alpha[i])*q_T[i],fluid$,T_clines_sat[i],chi_in,chi_out)[0]-DELTAp_g2D[i])
# p_cond = []  
# T_cond_sat = []
# for i in np.arange(0,N-1):
#     p_cond.append(p_clines[i] - DELTAp_cond[i])
#     T_cond_sat.append(IAPWS95(P=p_cond[i],x=1).T)
#     DELTAT_cond[i] = T_clines_sat[i] - T_cond_sat[i]

# ## Total losses : mesh + line + cond

# DELTAT_t = []
# for i  in np.arange(0,N-1):
#     DELTAT_t.append(DELTAT_m[i]+DELTAT_pipe[i]+DELTAT_cond[i])
# DELTAT_t.append(DELTAT_m[N-1]+DELTAT_pipe[N-1])

# # TERMOCOMPRESSION

# p_suc = p_prime_V[N_effect-1]
# T_suc = T_prime_V[N_effect-1]
# p_m_b = p_m * 10**-5 # Pa to bar
# p_suc_b =p_suc * 10**-5 #Pa to bar
# p_comp_b = p_comp *10**-5 #Pa to bar
# p_comp = p_s
# CR_th=p_comp/p_suc
# ER=p_m/p_suc
# Hassanra(CR_th, ER)
# Ra = q_m/q_suc

# y=np.zeros(N)
# alpha[N_effect-1]=0
# y_effect = q_suc/((1-alpha[N_effect-1])*q_T[N_effect-1]) 
# y[N_effect-1] = y_effect 

# Mass Balance

# q_comp = q_m+q_suc

# Energy Balance

# h_motive = IAPWS95(P=p_m, x=1).h
# h_entrainment = IAPWS95(T=T_suc, x=1).h
# h_comp = IAPWS95(T=T_comp_sobrec, P=p_comp).h
# 
# q_m*h_motive+q_suc*h_entrainment=q_comp*h_comp

# ## Desuperheater

# q_comp+q_dsh=q_s
# q_comp*h_comp+q_dsh*h_dprime_c[N-1] = q_s*h_s_sobrec
# h_s_sobrec = IAPWS95(T=T_s_sobrec, P=p_comp)

# Q_dot_m=q_m*h_motive
# P_Q_qm=q_m*h_motive
# ex_qm=exergiaxp(1,p_m) #{The steam motive is saturated at 17 bar => Tsat = 204.3}
# P_ex_qm=q_m*ex_qm

# # Parameters of interest    

# ## Gain output ratio

# GOR=q_D/q_m

# ## Performance ration

# lambda_m = IAPWS95(P=p_m,x=1).h-IAPWS95(P=p_m,x=0).h
# PR=q_D*2326/ (q_m*lambda_m)

# ## Specific energy consumption

# sE=q_m*lambda_m*rho_D/(q_D*3600)

# ## Conversion Ratio/ Recovery Ratio

# RR = q_D/q_F

# ## Specific area

# sA=(np.sum(A)+np.sum(A_preh)+A_c )/ q_D

# ## Specific cooling seawater

# sM_cw = q_cw/q_D

# Q_dot_cooling = q_cw*h_f #Thermal potential lost in cooling
# Q_dot_in=q_in*h_in       #Inlet sea water potential
# Q_dot_F=q_F*h_f
# #{Q_dot_s=q_s*lambda_s}
# #{Q_dot_s_specific=Q_dot_s /q_D_m3h	"kWh/m3"}
# Q_dot_D=h_dprime_C[N-1]*q_D

# ## Comparision of exergy

# ex_qs=Exergiaxt(1,T_s)
# P_ex_qs=q_s*ex_qs

# ## Energy comparison

# h_s=IAPWS95(T=T_s,x=1).h
# P_Q_qs=q_s*h_s

# ## Average temperature jump between effects

# DELTAT_av = np.average(DELTAT)
# Q_av = np.average(Q)
# U_av = np.average(U)

# ## qF from each effect in m^3/h

# for i in range(N-1):
#     q_F_m3h[i]=q_F_i[i]*3600/rho_brine[i]
