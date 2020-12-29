"""
Model name: Process Heat Linear Fresnel Direct Steam
Model label: linear_fresnel_dsg_iph
"""


# Number of loops equation
eqn1  = {
        'model': 'linear_fresnel_dsg_iph',
        'outputs': ['nLoops'],
        'inputs':['specified_solar_multiple','q_pb_des','I_bn_des','A_aperture','L_col','nModBoil', 'hl_mode',
                  'TrackingError', 'GeomEffects','rho_mirror_clean','dirt_mirror','error',
                  'T_cold_ref','T_amb_des_sf','HL_dT','HCE_FieldFrac','Shadowing','Dirt_HCE','Design_loss'
                  ],
        'function': 'linear_fresnel_dsg_iph'
        }

def linear_fresnel_dsg_iph(invalues):
    
    specified_solar_multiple,  q_pb_des,  I_bn_des,  A_aperture, L_col, nModBoil, hl_mode, \
    TrackingError, GeomEffects, rho_mirror_clean, dirt_mirror, error, \
    T_cold_ref, T_amb_des_sf, HL_dT, HCE_FieldFrac, Shadowing, Dirt_HCE, Design_loss = invalues
    
    T_hot = 393
    coll_opt_loss_norm_inc = TrackingError[0][0] * GeomEffects[0][0] * rho_mirror_clean[0][0] * dirt_mirror[0][0] * error[0][0]
    avg_field_temp_dt_design = (T_cold_ref + T_hot) / 2 - T_amb_des_sf
    
    
    if hl_mode == 0:
        rec_optical_derate = 1
        heat_loss_at_design = HL_dT[0][0] + HL_dT[0][1] * avg_field_temp_dt_design    + HL_dT[0][2] * avg_field_temp_dt_design**2 +\
                                            HL_dT[0][3] * avg_field_temp_dt_design**3 + HL_dT[0][4] * avg_field_temp_dt_design**4
    else:
        rec_optical_derate  = HCE_FieldFrac[0][0] * Shadowing[0][0] * Dirt_HCE[0][0] +\
                              HCE_FieldFrac[0][1] * Shadowing[0][1] * Dirt_HCE[0][1] +\
                              HCE_FieldFrac[0][2] * Shadowing[0][2] * Dirt_HCE[0][2] +\
                              HCE_FieldFrac[0][3] * Shadowing[0][3] * Dirt_HCE[0][3] 
        heat_loss_at_design = HCE_FieldFrac[0][0] * Design_loss[0][0] +\
                              HCE_FieldFrac[0][1] * Design_loss[0][1] +\
                              HCE_FieldFrac[0][2] * Design_loss[0][2] +\
                              HCE_FieldFrac[0][3] * Design_loss[0][3] 
                              
    nLoops = specified_solar_multiple * q_pb_des / (I_bn_des * rec_optical_derate * coll_opt_loss_norm_inc * \
            (1 - heat_loss_at_design/( I_bn_des * A_aperture[0][0] / L_col[0][0])) )* 1e6 / (nModBoil * A_aperture[0][0] )

    return [int(nLoops) + 1]

#%%
"""
Model name: Linear Fresnel Direct Steam
Model label: tcslinear_fresnel
Combined Function
"""

eqn01 = {
        'model': 'tcslinear_fresnel',
        'outputs': ['nLoops', 'q_pb_des','q_max_aux','solarm','specified_total_aperture', 'P_turb_des', 'system_capacity'],
        'inputs':['sm_or_area', 'demand_var','eta_ref','I_bn_des','sh_geom_unique', 'nModBoil','nModSH','A_aperture',
                  'TrackingError','GeomEffects','rho_mirror_clean','dirt_mirror','error','HLCharType',
                  'HCE_FieldFrac','Shadowing', 'Dirt_HCE','L_col','T_cold_ref','T_amb_des_sf','T_hot','HL_dT','Design_loss',
                  'Pipe_hl_coef','solarm','specified_total_aperture', 'P_boil_des', 'gross_net_conv_factor'
                  ],
        'function': 'tcslinear_fresnel'        
        }
def tcslinear_fresnel(invalues):
    sm_or_area, demand_var, eta_ref, I_bn_des, sh_geom_unique, nModBoil, nModSH, A_aperture,\
    TrackingError, GeomEffects, rho_mirror_clean, dirt_mirror, error, HLCharType,\
    HCE_FieldFrac, Shadowing, Dirt_HCE, L_col, T_cold_ref, T_amb_des_sf, T_hot, HL_dT, Design_loss,\
    Pipe_hl_coef, solarm, specified_total_aperture, P_boil_des, gross_net_conv_factor     = invalues
    
    
    total_loop_conv_eff, loop_aperture = tcslinear_fresnel_loop_eff(I_bn_des, sh_geom_unique, nModBoil, nModSH, A_aperture,
                               TrackingError, GeomEffects, rho_mirror_clean, dirt_mirror, error, HLCharType,
                               HCE_FieldFrac, Shadowing, Dirt_HCE, L_col, T_cold_ref, T_amb_des_sf, T_hot, HL_dT, Design_loss,
                               Pipe_hl_coef)
    sm1_aperture = demand_var / eta_ref / I_bn_des / total_loop_conv_eff * 1e6
        
    if sm_or_area == 0:
        solarm = solarm
        nLoops = int(solarm * sm1_aperture / loop_aperture )        
        specified_total_aperture = loop_aperture * nLoops
    else:
    	nLoops = int(specified_total_aperture / loop_aperture)
    	solarm = loop_aperture * nLoops / sm1_aperture   

    
    q_pb_des = demand_var / eta_ref
    actual_aper = loop_aperture * nLoops
    q_max_aux = 1e-6 * actual_aper * I_bn_des * total_loop_conv_eff 
    P_turb_des = P_boil_des
    system_capacity = demand_var * gross_net_conv_factor
    
    return [nLoops, q_pb_des, q_max_aux, solarm, specified_total_aperture, P_turb_des, system_capacity]

# help function to calcualte loop_eff and loop_aperture
def tcslinear_fresnel_loop_eff(I_bn_des, sh_geom_unique, nModBoil, nModSH, A_aperture,
                               TrackingError, GeomEffects, rho_mirror_clean, dirt_mirror, error, HLCharType,
                               HCE_FieldFrac, Shadowing, Dirt_HCE, L_col, T_cold_ref, T_amb_des_sf, T_hot, HL_dT, Design_loss,
                               Pipe_hl_coef):
    if sh_geom_unique == 0:
        geom1_area_frac = 1
        geom2_area_frac = 0
        loop_aperture   = (nModBoil + nModSH) * A_aperture[0][0]
    else:
        geom1_area_frac = nModBoil * A_aperture[0][0] / (nModBoil * A_aperture[0][0] + nModSH * A_aperture[1][0])
        geom2_area_frac = nModBoil * A_aperture[1][0] / (nModBoil * A_aperture[0][0] + nModSH * A_aperture[1][0]) 
        loop_aperture   = (nModBoil * A_aperture[0][0] + nModSH * A_aperture[1][0]) 
    
        
    avg_field_temp_dt_design = (T_cold_ref + T_hot) / 2 - T_amb_des_sf
    
    if HLCharType[0][0] == 1:
        geom1_rec_optical_derate = 1
        geom1_heat_loss_at_design = HL_dT[0][0] + HL_dT[0][1] * avg_field_temp_dt_design    + HL_dT[0][2] * avg_field_temp_dt_design**2 +\
                                            HL_dT[0][3] * avg_field_temp_dt_design**3 + HL_dT[0][4] * avg_field_temp_dt_design**4
    else:
        geom1_rec_optical_derate  = HCE_FieldFrac[0][0] * Shadowing[0][0] * Dirt_HCE[0][0] +\
                                    HCE_FieldFrac[0][1] * Shadowing[0][1] * Dirt_HCE[0][1] +\
                                    HCE_FieldFrac[0][2] * Shadowing[0][2] * Dirt_HCE[0][2] +\
                                    HCE_FieldFrac[0][3] * Shadowing[0][3] * Dirt_HCE[0][3] 
        geom1_heat_loss_at_design = HCE_FieldFrac[0][0] * Design_loss[0][0] +\
                                    HCE_FieldFrac[0][1] * Design_loss[0][1] +\
                                    HCE_FieldFrac[0][2] * Design_loss[0][2] +\
                                    HCE_FieldFrac[0][3] * Design_loss[0][3]   

    if HLCharType[1][0] == 1:
        geom2_rec_optical_derate = 1
        geom2_heat_loss_at_design = HL_dT[1][0] + HL_dT[1][1] * avg_field_temp_dt_design    + HL_dT[1][2] * avg_field_temp_dt_design**2 +\
                                            HL_dT[1][3] * avg_field_temp_dt_design**3 + HL_dT[1][4] * avg_field_temp_dt_design**4
    else:
        geom2_rec_optical_derate  = HCE_FieldFrac[1][0] * Shadowing[1][0] * Dirt_HCE[1][0] +\
                                    HCE_FieldFrac[1][1] * Shadowing[1][1] * Dirt_HCE[1][1] +\
                                    HCE_FieldFrac[1][2] * Shadowing[1][2] * Dirt_HCE[1][2] +\
                                    HCE_FieldFrac[1][3] * Shadowing[1][3] * Dirt_HCE[1][3] 
        geom2_heat_loss_at_design = HCE_FieldFrac[1][0] * Design_loss[1][0] +\
                                    HCE_FieldFrac[1][1] * Design_loss[1][1] +\
                                    HCE_FieldFrac[1][2] * Design_loss[1][2] +\
                                    HCE_FieldFrac[1][3] * Design_loss[1][3] 

    
    geom1_coll_opt_loss_norm_inc = TrackingError[0][0] * GeomEffects[0][0] * rho_mirror_clean[0][0] * dirt_mirror[0][0] * error[0][0] 
    geom2_coll_opt_loss_norm_inc = TrackingError[1][0] * GeomEffects[1][0] * rho_mirror_clean[1][0] * dirt_mirror[1][0] * error[1][0]
    
    geom1_rec_thermal_derate = 1 - geom1_heat_loss_at_design / (I_bn_des * A_aperture[0][0] / L_col[0][0] )
    geom2_rec_thermal_derate = 1 - geom2_heat_loss_at_design / (I_bn_des * A_aperture[1][0] / L_col[1][0] )
     
    
    loop_opt_eff = geom1_area_frac * geom1_rec_optical_derate * geom1_coll_opt_loss_norm_inc + geom2_area_frac * geom2_rec_optical_derate * geom2_coll_opt_loss_norm_inc
    loop_therm_eff = geom1_rec_thermal_derate * geom1_area_frac + geom2_rec_thermal_derate * geom2_area_frac
    piping_therm_eff = 1 - Pipe_hl_coef * avg_field_temp_dt_design / I_bn_des

    total_loop_conv_eff = loop_opt_eff * loop_therm_eff * piping_therm_eff   
    
    return total_loop_conv_eff, loop_aperture


#%%
"""
Model name: Industrial Process Heat Parabolic Trough
Model label: trough_physical_process_heat
"""
# nLoops
eqn02 = {
        'model': 'trough_physical_process_heat',
        'outputs': ['nLoops', 'solar_mult', 'L_aperture'],
        'inputs':['specified_solar_multiple', 'q_pb_design', 'I_bn_des', 'trough_loop_control','A_aperture',
                  'L_SCA', 'TrackingError', 'GeomEffects', 'Rho_mirror_clean', 'Dirt_mirror', 'Error',
                  'HCE_FieldFrac','Shadowing', 'Dirt_HCE', 'alpha_abs', 'Tau_envelope', 'Design_loss', 'ColperSCA'
                  
                  ],
        'function': 'trough_physical_process_heat'
        }
                                                                                    
def trough_physical_process_heat(invalues):
    specified_solar_multiple, q_pb_design, I_bn_des, trough_loop_control, A_aperture,\
    L_SCA, TrackingError, GeomEffects, Rho_mirror_clean, Dirt_mirror, Error,\
    HCE_FieldFrac, Shadowing, Dirt_HCE, alpha_abs, Tau_envelope, Design_loss, ColperSCA = invalues
    
    ncol = trough_loop_control[0]
    sca_eff = [TrackingError[i] * GeomEffects[i] * Rho_mirror_clean[i] * Dirt_mirror[i] * Error[i] for i in range(len(TrackingError))]
    
    total_len = 0
    weighted_sca_eff =0
    for i in range(ncol):
        sca_t = min(max(trough_loop_control[1 + 3*i], 1), 4) - 1
        total_len += L_SCA[sca_t]
        weighted_sca_eff += L_SCA[sca_t] *sca_eff[sca_t]
        
    hce_eff = [HCE_FieldFrac[i][0]*Shadowing[i][0]*Dirt_HCE[i][0]*alpha_abs[i][0]*Tau_envelope[i][0]+
               HCE_FieldFrac[i][1]*Shadowing[i][1]*Dirt_HCE[i][1]*alpha_abs[i][1]*Tau_envelope[i][1]+
               HCE_FieldFrac[i][2]*Shadowing[i][2]*Dirt_HCE[i][2]*alpha_abs[i][2]*Tau_envelope[i][2]+
               HCE_FieldFrac[i][3]*Shadowing[i][3]*Dirt_HCE[i][3]*alpha_abs[i][3]*Tau_envelope[i][3]
               for i in range(len(HCE_FieldFrac))]
    
    hce_design_heat_loss = [HCE_FieldFrac[i][0] * Design_loss[i][0] + HCE_FieldFrac[i][1] * Design_loss[i][1] +
                            HCE_FieldFrac[i][2] * Design_loss[i][2] + HCE_FieldFrac[i][3] * Design_loss[i][3]
                            for i in range(len(HCE_FieldFrac))]
    
    total_len = 0
    weighted_hce_eff = 0
    derate = 0
    for i in range(ncol):
        hce_t = min(max(trough_loop_control[2 + 3*i], 1), 4) - 1
        sca_t = min(max(trough_loop_control[1 + 3*i], 1), 4) - 1
        total_len += L_SCA[sca_t]
        weighted_hce_eff += L_SCA[sca_t] *hce_eff[hce_t]    
        derate += L_SCA[sca_t] * (1 - hce_design_heat_loss[hce_t] / (I_bn_des * A_aperture[sca_t] / L_SCA[sca_t]))
    
    weighted_sca_eff /= total_len
    weighted_hce_eff /= total_len
    loop_optical_efficiency = weighted_hce_eff * weighted_sca_eff
    cspdtr_loop_hce_heat_loss = derate / total_len
    total_loop_conversion_efficiency = loop_optical_efficiency * cspdtr_loop_hce_heat_loss
    total_required_aperture_for_SM1 = q_pb_design / I_bn_des / total_loop_conversion_efficiency * 1e6
    

    
    nsca = trough_loop_control[0]
    total_ap = 0
    for i in range(nsca):
        sca_t = min(max(trough_loop_control[1 + 3*i], 1), 4) - 1
        total_ap += A_aperture[sca_t]
    single_loop_aperature = total_ap
    
    nLoops = int(specified_solar_multiple * total_required_aperture_for_SM1 / single_loop_aperature) + 1

    total_aperture = single_loop_aperature * nLoops
    field_thermal_output = I_bn_des * total_loop_conversion_efficiency * total_aperture / 1e6
    solar_mult = field_thermal_output / q_pb_design
    
    L_aperture = []
    for i in range(ncol):
        L_aperture.append(L_SCA[i] / ColperSCA[i])
    
    
    return [nLoops, solar_mult, L_aperture]


#%%
"""
Model name: Parabolic Trough Physical
Model label: tcstrough_physical
"""
# nLoops
eqn03 = {
        'model': 'tcstrough_physical',
        'outputs': ['nLoops', 'solar_mult', 'total_aperture', 'system_capacity', 'is_hx', 'W_pb_design'],
        # , 'vol_tank'],
        'inputs':['sm_or_area', 'specified_solar_multiple', 'trough_loop_control', 'TrackingError', 'GeomEffects',
                  'Rho_mirror_clean', 'Dirt_mirror', 'Error', 'L_SCA', 'HCE_FieldFrac', 'Shadowing', 'Dirt_HCE',
                  'alpha_abs', 'Tau_envelope', 'Design_loss', 'I_bn_des', 'A_aperture', 'P_ref', 'eta_ref',
                  'specified_total_aperture', 'gross_net_conversion_factor', 'Fluid', 'store_fluid', 'tshours'
                  ],
        'function': 'tcstrough_physical'
        }
                                                                                    
def tcstrough_physical(invalues):
    sm_or_area, specified_solar_multiple, trough_loop_control, TrackingError, GeomEffects,  \
    Rho_mirror_clean,  Dirt_mirror, Error, L_SCA, HCE_FieldFrac, Shadowing,  Dirt_HCE, \
    alpha_abs,  Tau_envelope, Design_loss, I_bn_des, A_aperture, P_ref, eta_ref, \
    specified_total_aperture, gross_net_conversion_factor, Fluid, store_fluid, tshours \
    = invalues

    ncol = trough_loop_control[0]
    sca_eff = [TrackingError[i] * GeomEffects[i] * Rho_mirror_clean[i] * Dirt_mirror[i] * Error[i] for i in range(len(TrackingError))]
    
    total_len = 0
    weighted_sca_eff =0
    for i in range(ncol):
        sca_t = min(max(trough_loop_control[1 + 3*i], 1), 4) - 1
        total_len += L_SCA[sca_t]
        weighted_sca_eff += L_SCA[sca_t] *sca_eff[sca_t]
        
    hce_eff = [HCE_FieldFrac[i][0]*Shadowing[i][0]*Dirt_HCE[i][0]*alpha_abs[i][0]*Tau_envelope[i][0]+
               HCE_FieldFrac[i][1]*Shadowing[i][1]*Dirt_HCE[i][1]*alpha_abs[i][1]*Tau_envelope[i][1]+
               HCE_FieldFrac[i][2]*Shadowing[i][2]*Dirt_HCE[i][2]*alpha_abs[i][2]*Tau_envelope[i][2]+
               HCE_FieldFrac[i][3]*Shadowing[i][3]*Dirt_HCE[i][3]*alpha_abs[i][3]*Tau_envelope[i][3]
               for i in range(len(HCE_FieldFrac))]
    
    hce_design_heat_loss = [HCE_FieldFrac[i][0] * Design_loss[i][0] + HCE_FieldFrac[i][1] * Design_loss[i][1] +
                            HCE_FieldFrac[i][2] * Design_loss[i][2] + HCE_FieldFrac[i][3] * Design_loss[i][3]
                            for i in range(len(HCE_FieldFrac))]
    
    total_len = 0
    weighted_hce_eff = 0
    derate = 0
    for i in range(ncol):
        hce_t = min(max(trough_loop_control[2 + 3*i], 1), 4) - 1
        sca_t = min(max(trough_loop_control[1 + 3*i], 1), 4) - 1
        total_len += L_SCA[sca_t]
        weighted_hce_eff += L_SCA[sca_t] *hce_eff[hce_t]    
        derate += L_SCA[sca_t] * (1 - hce_design_heat_loss[hce_t] / (I_bn_des * A_aperture[sca_t] / L_SCA[sca_t]))
    
    weighted_sca_eff /= total_len
    weighted_hce_eff /= total_len    
    loop_optical_efficiency = weighted_hce_eff * weighted_sca_eff    
    cspdtr_loop_hce_heat_loss = derate / total_len    
    total_loop_conversion_efficiency = loop_optical_efficiency * cspdtr_loop_hce_heat_loss 
    total_required_aperture_for_SM1 = P_ref / eta_ref / I_bn_des / total_loop_conversion_efficiency * 1e6
    
    
    nsca = trough_loop_control[0]
    total_ap = 0
    for i in range(nsca):
        sca_t = min(max(trough_loop_control[1 + 3*i], 1), 4) - 1
        total_ap += A_aperture[sca_t]
    single_loop_aperature = total_ap  
    
    if sm_or_area == 0:
        retval = specified_solar_multiple * total_required_aperture_for_SM1
    else:
        retval = specified_total_aperture
        
    nLoops = int(retval / single_loop_aperature) + 1
    total_aperture = single_loop_aperature * nLoops
    if sm_or_area == 0:
        solar_mult = specified_solar_multiple
    else:
        solar_mult = total_aperture / total_required_aperture_for_SM1    
    
    nameplate = P_ref * gross_net_conversion_factor
    system_capacity = nameplate * 1000
    
    if Fluid == store_fluid:
        is_hx = 0
    else:
        is_hx = 1
    
    W_pb_design = P_ref
    # thermal_capacity = P_ref / eta_ref * tshours
    # vol_tank = thermal_capacity * 1e6 * 3600 / (fluid_dens * fluid_sph * 1000 * hx_derate * ( (T_loop_out - dt_hot) - (T_loop_in_des - dt_cold)))
    print('total_required_aperture_for_SM1', total_required_aperture_for_SM1)
    print('total_loop_conversion_efficiency', total_loop_conversion_efficiency)
    print('loop_optical_efficiency', loop_optical_efficiency)
    print('cspdtr_loop_hce_heat_loss', cspdtr_loop_hce_heat_loss)
    print('single_loop_aperature', single_loop_aperature)
    return [nLoops, solar_mult, total_aperture, system_capacity, is_hx, W_pb_design]#, vol_tank]
    