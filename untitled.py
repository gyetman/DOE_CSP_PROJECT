from PySSC import PySSC
if __name__ == "__main__":
	ssc = PySSC()
	print ('Current folder = D:/PhD/DOE')
	print ('SSC Version = ', ssc.version())
	print ('SSC Build Information = ', ssc.build_info().decode("utf - 8"))
	ssc.module_exec_set_print(0)
	data = ssc.data_create()
	ssc.data_set_string( data, b'file_name', b'C:/SAM/2020.2.29/solar_resource/tucson_az_32.116521_-110.933042_psmv3_60_tmy.csv' );
	ssc.data_set_number( data, b'track_mode', 1 )
	ssc.data_set_number( data, b'tilt', 0 )
	ssc.data_set_number( data, b'azimuth', 0 )
	ssc.data_set_number( data, b'I_bn_des', 950 )
	ssc.data_set_number( data, b'solar_mult', 2.6771607398986816 )
	ssc.data_set_number( data, b'T_loop_in_des', 90 )
	ssc.data_set_number( data, b'T_loop_out', 150 )
	ssc.data_set_number( data, b'q_pb_design', 5.1879099999999996 )
	ssc.data_set_number( data, b'tshours', 6 )
	ssc.data_set_number( data, b'nSCA', 4 )
	ssc.data_set_number( data, b'nHCEt', 4 )
	ssc.data_set_number( data, b'nColt', 4 )
	ssc.data_set_number( data, b'nHCEVar', 4 )
	ssc.data_set_number( data, b'nLoops', 8 )
	ssc.data_set_number( data, b'eta_pump', 0.84999999999999998 )
	ssc.data_set_number( data, b'HDR_rough', 4.57e-05 )
	ssc.data_set_number( data, b'theta_stow', 170 )
	ssc.data_set_number( data, b'theta_dep', 10 )
	ssc.data_set_number( data, b'Row_Distance', 15 )
	ssc.data_set_number( data, b'FieldConfig', 1 )
	ssc.data_set_number( data, b'is_model_heat_sink_piping', 0 )
	ssc.data_set_number( data, b'L_heat_sink_piping', 50 )
	ssc.data_set_number( data, b'm_dot_htfmin', 1 )
	ssc.data_set_number( data, b'm_dot_htfmax', 12 )
	ssc.data_set_number( data, b'Fluid', 31 )
	ssc.data_set_number( data, b'wind_stow_speed', 25 )
	field_fl_props = [[ 20,   4.1799999999999997,   999,   0.001,   9.9999999999999995e-07,   0.58699999999999997,   85.299999999999997 ], [ 40,   4.1799999999999997,   993,   0.00065300000000000004,   6.5799999999999999e-07,   0.61799999999999999,   169 ], [ 60,   4.1799999999999997,   984,   0.00046700000000000002,   4.75e-07,   0.64200000000000002,   252 ], [ 80,   4.1900000000000004,   972,   0.00035500000000000001,   3.65e-07,   0.65700000000000003,   336 ], [ 100,   4.21,   959,   0.00028200000000000002,   2.9400000000000001e-07,   0.66600000000000004,   420 ], [ 120,   4.25,   944,   0.000233,   2.4600000000000001e-07,   0.67000000000000004,   505 ], [ 140,   4.2800000000000002,   927,   0.00019699999999999999,   2.1199999999999999e-07,   0.67000000000000004,   590 ], [ 160,   4.3399999999999999,   908,   0.00017100000000000001,   1.8799999999999999e-07,   0.66700000000000004,   676 ], [ 180,   4.4000000000000004,   887,   0.00014999999999999999,   1.6899999999999999e-07,   0.66100000000000003,   764 ], [ 200,   4.4900000000000002,   865,   0.000134,   1.55e-07,   0.65100000000000002,   852 ], [ 220,   4.5800000000000001,   842,   0.000118,   1.4100000000000001e-07,   0.64100000000000001,   941 ]];
	ssc.data_set_matrix( data, b'field_fl_props', field_fl_props );
	ssc.data_set_number( data, b'T_fp', 10 )
	ssc.data_set_number( data, b'Pipe_hl_coef', 0.45000000000000001 )
	ssc.data_set_number( data, b'SCA_drives_elec', 125 )
	ssc.data_set_number( data, b'water_usage_per_wash', 0.69999999999999996 )
	ssc.data_set_number( data, b'washing_frequency', 12 )
	ssc.data_set_number( data, b'accept_mode', 0 )
	ssc.data_set_number( data, b'accept_init', 0 )
	ssc.data_set_number( data, b'accept_loc', 1 )
	ssc.data_set_number( data, b'mc_bal_hot', 0.20000000000000001 )
	ssc.data_set_number( data, b'mc_bal_cold', 0.20000000000000001 )
	ssc.data_set_number( data, b'mc_bal_sca', 4.5 )
	W_aperture =[ 6, 6, 6, 6 ];
	ssc.data_set_array( data, b'W_aperture',  W_aperture);
	A_aperture =[ 656, 656, 656, 656 ];
	ssc.data_set_array( data, b'A_aperture',  A_aperture);
	TrackingError =[ 0.98799999999999999, 0.98799999999999999, 0.98799999999999999, 0.98799999999999999 ];
	ssc.data_set_array( data, b'TrackingError',  TrackingError);
	GeomEffects =[ 0.95199999999999996, 0.95199999999999996, 0.95199999999999996, 0.95199999999999996 ];
	ssc.data_set_array( data, b'GeomEffects',  GeomEffects);
	Rho_mirror_clean =[ 0.93000000000000005, 0.93000000000000005, 0.93000000000000005, 0.93000000000000005 ];
	ssc.data_set_array( data, b'Rho_mirror_clean',  Rho_mirror_clean);
	Dirt_mirror =[ 0.96999999999999997, 0.96999999999999997, 0.96999999999999997, 0.96999999999999997 ];
	ssc.data_set_array( data, b'Dirt_mirror',  Dirt_mirror);
	Error =[ 1, 1, 1, 1 ];
	ssc.data_set_array( data, b'Error',  Error);
	Ave_Focal_Length =[ 2.1499999999999999, 2.1499999999999999, 2.1499999999999999, 2.1499999999999999 ];
	ssc.data_set_array( data, b'Ave_Focal_Length',  Ave_Focal_Length);
	L_SCA =[ 115, 115, 115, 115 ];
	ssc.data_set_array( data, b'L_SCA',  L_SCA);
	L_aperture =[ 14.375, 14.375, 14.375, 14.375 ];
	ssc.data_set_array( data, b'L_aperture',  L_aperture);
	ColperSCA =[ 8, 8, 8, 8 ];
	ssc.data_set_array( data, b'ColperSCA',  ColperSCA);
	Distance_SCA =[ 1, 1, 1, 1 ];
	ssc.data_set_array( data, b'Distance_SCA',  Distance_SCA);
	IAM_matrix = [[ 1,   0.0327,   -0.1351 ], [ 1,   0.0327,   -0.1351 ], [ 1,   0.0327,   -0.1351 ], [ 1,   0.0327,   -0.1351 ]];
	ssc.data_set_matrix( data, b'IAM_matrix', IAM_matrix );
	HCE_FieldFrac = [[ 1,   0,   0,   0 ], [ 1,   0,   0,   0 ], [ 1,   0,   0,   0 ], [ 1,   0,   0,   0 ]];
	ssc.data_set_matrix( data, b'HCE_FieldFrac', HCE_FieldFrac );
	D_2 = [[ 0.075999999999999998,   0.075999999999999998,   0.075999999999999998,   0.075999999999999998 ], [ 0.075999999999999998,   0.075999999999999998,   0.075999999999999998,   0.075999999999999998 ], [ 0.075999999999999998,   0.075999999999999998,   0.075999999999999998,   0.075999999999999998 ], [ 0.075999999999999998,   0.075999999999999998,   0.075999999999999998,   0.075999999999999998 ]];
	ssc.data_set_matrix( data, b'D_2', D_2 );
	D_3 = [[ 0.080000000000000002,   0.080000000000000002,   0.080000000000000002,   0.080000000000000002 ], [ 0.080000000000000002,   0.080000000000000002,   0.080000000000000002,   0.080000000000000002 ], [ 0.080000000000000002,   0.080000000000000002,   0.080000000000000002,   0.080000000000000002 ], [ 0.080000000000000002,   0.080000000000000002,   0.080000000000000002,   0.080000000000000002 ]];
	ssc.data_set_matrix( data, b'D_3', D_3 );
	D_4 = [[ 0.115,   0.115,   0.115,   0.115 ], [ 0.115,   0.115,   0.115,   0.115 ], [ 0.115,   0.115,   0.115,   0.115 ], [ 0.115,   0.115,   0.115,   0.115 ]];
	ssc.data_set_matrix( data, b'D_4', D_4 );
	D_5 = [[ 0.12,   0.12,   0.12,   0.12 ], [ 0.12,   0.12,   0.12,   0.12 ], [ 0.12,   0.12,   0.12,   0.12 ], [ 0.12,   0.12,   0.12,   0.12 ]];
	ssc.data_set_matrix( data, b'D_5', D_5 );
	D_p = [[ 0,   0,   0,   0 ], [ 0,   0,   0,   0 ], [ 0,   0,   0,   0 ], [ 0,   0,   0,   0 ]];
	ssc.data_set_matrix( data, b'D_p', D_p );
	Flow_type = [[ 1,   1,   1,   1 ], [ 1,   1,   1,   1 ], [ 1,   1,   1,   1 ], [ 1,   1,   1,   1 ]];
	ssc.data_set_matrix( data, b'Flow_type', Flow_type );
	Rough = [[ 4.5000000000000003e-05,   4.5000000000000003e-05,   4.5000000000000003e-05,   4.5000000000000003e-05 ], [ 4.5000000000000003e-05,   4.5000000000000003e-05,   4.5000000000000003e-05,   4.5000000000000003e-05 ], [ 4.5000000000000003e-05,   4.5000000000000003e-05,   4.5000000000000003e-05,   4.5000000000000003e-05 ], [ 4.5000000000000003e-05,   4.5000000000000003e-05,   4.5000000000000003e-05,   4.5000000000000003e-05 ]];
	ssc.data_set_matrix( data, b'Rough', Rough );
	alpha_env = [[ 0.02,   0.02,   0,   0 ], [ 0.02,   0.02,   0,   0 ], [ 0.02,   0.02,   0,   0 ], [ 0.02,   0.02,   0,   0 ]];
	ssc.data_set_matrix( data, b'alpha_env', alpha_env );
	epsilon_3_11 = [[ 100,   0.064000000000000001 ], [ 150,   0.066500000000000004 ], [ 200,   0.070000000000000007 ], [ 250,   0.074499999999999997 ], [ 300,   0.080000000000000002 ], [ 350,   0.086499999999999994 ], [ 400,   0.094 ], [ 450,   0.10249999999999999 ], [ 500,   0.112 ]];
	ssc.data_set_matrix( data, b'epsilon_3_11', epsilon_3_11 );
	epsilon_3_12 = [[ 0.65000000000000002 ]];
	ssc.data_set_matrix( data, b'epsilon_3_12', epsilon_3_12 );
	epsilon_3_13 = [[ 0.65000000000000002 ]];
	ssc.data_set_matrix( data, b'epsilon_3_13', epsilon_3_13 );
	epsilon_3_14 = [[ 0 ]];
	ssc.data_set_matrix( data, b'epsilon_3_14', epsilon_3_14 );
	epsilon_3_21 = [[ 100,   0.064000000000000001 ], [ 150,   0.066500000000000004 ], [ 200,   0.070000000000000007 ], [ 250,   0.074499999999999997 ], [ 300,   0.080000000000000002 ], [ 350,   0.086499999999999994 ], [ 400,   0.094 ], [ 450,   0.10249999999999999 ], [ 500,   0.112 ]];
	ssc.data_set_matrix( data, b'epsilon_3_21', epsilon_3_21 );
	epsilon_3_22 = [[ 0.65000000000000002 ]];
	ssc.data_set_matrix( data, b'epsilon_3_22', epsilon_3_22 );
	epsilon_3_23 = [[ 0.65000000000000002 ]];
	ssc.data_set_matrix( data, b'epsilon_3_23', epsilon_3_23 );
	epsilon_3_24 = [[ 0 ]];
	ssc.data_set_matrix( data, b'epsilon_3_24', epsilon_3_24 );
	epsilon_3_31 = [[ 100,   0.064000000000000001 ], [ 150,   0.066500000000000004 ], [ 200,   0.070000000000000007 ], [ 250,   0.074499999999999997 ], [ 300,   0.080000000000000002 ], [ 350,   0.086499999999999994 ], [ 400,   0.094 ], [ 450,   0.10249999999999999 ], [ 500,   0.112 ]];
	ssc.data_set_matrix( data, b'epsilon_3_31', epsilon_3_31 );
	epsilon_3_32 = [[ 0.65000000000000002 ]];
	ssc.data_set_matrix( data, b'epsilon_3_32', epsilon_3_32 );
	epsilon_3_33 = [[ 0.65000000000000002 ]];
	ssc.data_set_matrix( data, b'epsilon_3_33', epsilon_3_33 );
	epsilon_3_34 = [[ 0 ]];
	ssc.data_set_matrix( data, b'epsilon_3_34', epsilon_3_34 );
	epsilon_3_41 = [[ 100,   0.064000000000000001 ], [ 150,   0.066500000000000004 ], [ 200,   0.070000000000000007 ], [ 250,   0.074499999999999997 ], [ 300,   0.080000000000000002 ], [ 350,   0.086499999999999994 ], [ 400,   0.094 ], [ 450,   0.10249999999999999 ], [ 500,   0.112 ]];
	ssc.data_set_matrix( data, b'epsilon_3_41', epsilon_3_41 );
	epsilon_3_42 = [[ 0.65000000000000002 ]];
	ssc.data_set_matrix( data, b'epsilon_3_42', epsilon_3_42 );
	epsilon_3_43 = [[ 0.65000000000000002 ]];
	ssc.data_set_matrix( data, b'epsilon_3_43', epsilon_3_43 );
	epsilon_3_44 = [[ 0 ]];
	ssc.data_set_matrix( data, b'epsilon_3_44', epsilon_3_44 );
	alpha_abs = [[ 0.96299999999999997,   0.96299999999999997,   0.80000000000000004,   0 ], [ 0.96299999999999997,   0.96299999999999997,   0.80000000000000004,   0 ], [ 0.96299999999999997,   0.96299999999999997,   0.80000000000000004,   0 ], [ 0.96299999999999997,   0.96299999999999997,   0.80000000000000004,   0 ]];
	ssc.data_set_matrix( data, b'alpha_abs', alpha_abs );
	Tau_envelope = [[ 0.96399999999999997,   0.96399999999999997,   1,   0 ], [ 0.96399999999999997,   0.96399999999999997,   1,   0 ], [ 0.96399999999999997,   0.96399999999999997,   1,   0 ], [ 0.96399999999999997,   0.96399999999999997,   1,   0 ]];
	ssc.data_set_matrix( data, b'Tau_envelope', Tau_envelope );
	EPSILON_4 = [[ 0.85999999999999999,   0.85999999999999999,   1,   0 ], [ 0.85999999999999999,   0.85999999999999999,   1,   0 ], [ 0.85999999999999999,   0.85999999999999999,   1,   0 ], [ 0.85999999999999999,   0.85999999999999999,   1,   0 ]];
	ssc.data_set_matrix( data, b'EPSILON_4', EPSILON_4 );
	EPSILON_5 = [[ 0.85999999999999999,   0.85999999999999999,   1,   0 ], [ 0.85999999999999999,   0.85999999999999999,   1,   0 ], [ 0.85999999999999999,   0.85999999999999999,   1,   0 ], [ 0.85999999999999999,   0.85999999999999999,   1,   0 ]];
	ssc.data_set_matrix( data, b'EPSILON_5', EPSILON_5 );
	GlazingIntactIn = [[ 1,   1,   0,   1 ], [ 1,   1,   0,   1 ], [ 1,   1,   0,   1 ], [ 1,   1,   0,   1 ]];
	ssc.data_set_matrix( data, b'GlazingIntactIn', GlazingIntactIn );
	P_a = [[ 0.0001,   750,   750,   0 ], [ 0.0001,   750,   750,   0 ], [ 0.0001,   750,   750,   0 ], [ 0.0001,   750,   750,   0 ]];
	ssc.data_set_matrix( data, b'P_a', P_a );
	AnnulusGas = [[ 27,   1,   1,   1 ], [ 27,   1,   1,   1 ], [ 27,   1,   1,   27 ], [ 27,   1,   1,   27 ]];
	ssc.data_set_matrix( data, b'AnnulusGas', AnnulusGas );
	AbsorberMaterial = [[ 1,   1,   1,   1 ], [ 1,   1,   1,   1 ], [ 1,   1,   1,   1 ], [ 1,   1,   1,   1 ]];
	ssc.data_set_matrix( data, b'AbsorberMaterial', AbsorberMaterial );
	Shadowing = [[ 0.93500000000000005,   0.93500000000000005,   0.93500000000000005,   0.96299999999999997 ], [ 0.93500000000000005,   0.93500000000000005,   0.93500000000000005,   0.96299999999999997 ], [ 0.93500000000000005,   0.93500000000000005,   0.93500000000000005,   0.96299999999999997 ], [ 0.93500000000000005,   0.93500000000000005,   0.93500000000000005,   0.96299999999999997 ]];
	ssc.data_set_matrix( data, b'Shadowing', Shadowing );
	Dirt_HCE = [[ 0.97999999999999998,   0.97999999999999998,   1,   0.97999999999999998 ], [ 0.97999999999999998,   0.97999999999999998,   1,   0.97999999999999998 ], [ 0.97999999999999998,   0.97999999999999998,   1,   0.97999999999999998 ], [ 0.97999999999999998,   0.97999999999999998,   1,   0.97999999999999998 ]];
	ssc.data_set_matrix( data, b'Dirt_HCE', Dirt_HCE );
	Design_loss = [[ 190,   1270,   1500,   0 ], [ 190,   1270,   1500,   0 ], [ 190,   1270,   1500,   0 ], [ 190,   1270,   1500,   0 ]];
	ssc.data_set_matrix( data, b'Design_loss', Design_loss );
	SCAInfoArray = [[ 1,   1 ], [ 1,   1 ], [ 1,   1 ], [ 1,   1 ]];
	ssc.data_set_matrix( data, b'SCAInfoArray', SCAInfoArray );
	SCADefocusArray =[ 4, 3, 2, 1 ];
	ssc.data_set_array( data, b'SCADefocusArray',  SCADefocusArray);
	ssc.data_set_number( data, b'pb_pump_coef', 0.55000000000000004 )
	ssc.data_set_number( data, b'init_hot_htf_percent', 30 )
	ssc.data_set_number( data, b'h_tank', 15 )
	ssc.data_set_number( data, b'cold_tank_max_heat', 0.5 )
	ssc.data_set_number( data, b'u_tank', 0.29999999999999999 )
	ssc.data_set_number( data, b'tank_pairs', 1 )
	ssc.data_set_number( data, b'cold_tank_Thtr', 60 )
	ssc.data_set_number( data, b'h_tank_min', 0.5 )
	ssc.data_set_number( data, b'hot_tank_Thtr', 110 )
	ssc.data_set_number( data, b'hot_tank_max_heat', 1 )
	weekday_schedule = [[ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ]];
	ssc.data_set_matrix( data, b'weekday_schedule', weekday_schedule );
	weekend_schedule = [[ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ]];
	ssc.data_set_matrix( data, b'weekend_schedule', weekend_schedule );
	ssc.data_set_number( data, b'is_tod_pc_target_also_pc_max', 0 )
	ssc.data_set_number( data, b'is_dispatch', 0 )
	ssc.data_set_number( data, b'disp_frequency', 24 )
	ssc.data_set_number( data, b'disp_horizon', 48 )
	ssc.data_set_number( data, b'disp_max_iter', 35000 )
	ssc.data_set_number( data, b'disp_timeout', 5 )
	ssc.data_set_number( data, b'disp_mip_gap', 0.001 )
	ssc.data_set_number( data, b'disp_time_weighting', 0.98999999999999999 )
	ssc.data_set_number( data, b'disp_rsu_cost', 950 )
	ssc.data_set_number( data, b'disp_csu_cost', 10000 )
	ssc.data_set_number( data, b'disp_pen_delta_w', 0.10000000000000001 )
	ssc.data_set_number( data, b'is_wlim_series', 0 )
	ssc.data_set_array_from_csv( data, b'wlim_series', b'D:/PhD/DOE/wlim_series.csv');
	f_turb_tou_periods =[ 1.05, 1, 1, 1, 1, 1, 1, 1, 1 ];
	ssc.data_set_array( data, b'f_turb_tou_periods',  f_turb_tou_periods);
	ssc.data_set_number( data, b'is_dispatch_series', 0 )
	dispatch_series =[ 0 ];
	ssc.data_set_array( data, b'dispatch_series',  dispatch_series);
	ssc.data_set_number( data, b'pb_fixed_par', 0.0054999999999999997 )
	bop_array =[ 0, 1, 0, 0.48299999999999998, 0 ];
	ssc.data_set_array( data, b'bop_array',  bop_array);
	aux_array =[ 0.023, 1, 0.48299999999999998, 0.57099999999999995, 0 ];
	ssc.data_set_array( data, b'aux_array',  aux_array);
	ssc.data_set_number( data, b'calc_design_pipe_vals', 1 )
	ssc.data_set_number( data, b'V_hdr_cold_max', 3 )
	ssc.data_set_number( data, b'V_hdr_cold_min', 2 )
	ssc.data_set_number( data, b'V_hdr_hot_max', 3 )
	ssc.data_set_number( data, b'V_hdr_hot_min', 2 )
	ssc.data_set_number( data, b'N_max_hdr_diams', 10 )
	ssc.data_set_number( data, b'L_rnr_pb', 25 )
	ssc.data_set_number( data, b'L_rnr_per_xpan', 70 )
	ssc.data_set_number( data, b'L_xpan_hdr', 20 )
	ssc.data_set_number( data, b'L_xpan_rnr', 20 )
	ssc.data_set_number( data, b'Min_rnr_xpans', 1 )
	ssc.data_set_number( data, b'northsouth_field_sep', 20 )
	ssc.data_set_number( data, b'N_hdr_per_xpan', 2 )
	ssc.data_set_number( data, b'offset_xpan_hdr', 1 )
	K_cpnt = [[ 0.90000000000000002,   0,   0.19,   0,   0.90000000000000002,   -1,   -1,   -1,   -1,   -1,   -1 ], [ 0,   0.59999999999999998,   0.050000000000000003,   0,   0.59999999999999998,   0,   0.59999999999999998,   0,   0.41999999999999998,   0,   0.14999999999999999 ], [ 0.050000000000000003,   0,   0.41999999999999998,   0,   0.59999999999999998,   0,   0.59999999999999998,   0,   0.41999999999999998,   0,   0.14999999999999999 ], [ 0.050000000000000003,   0,   0.41999999999999998,   0,   0.59999999999999998,   0,   0.59999999999999998,   0,   0.41999999999999998,   0,   0.14999999999999999 ], [ 0.050000000000000003,   0,   0.41999999999999998,   0,   0.59999999999999998,   0,   0.59999999999999998,   0,   0.41999999999999998,   0,   0.14999999999999999 ], [ 0.050000000000000003,   0,   0.41999999999999998,   0,   0.59999999999999998,   0,   0.59999999999999998,   0,   0.14999999999999999,   0.59999999999999998,   0 ], [ 0.90000000000000002,   0,   0.19,   0,   0.90000000000000002,   -1,   -1,   -1,   -1,   -1,   -1 ]];
	ssc.data_set_matrix( data, b'K_cpnt', K_cpnt );
	D_cpnt = [[ 0.085000000000000006,   0.063500000000000001,   0.085000000000000006,   0.063500000000000001,   0.085000000000000006,   -1,   -1,   -1,   -1,   -1,   -1 ], [ 0.085000000000000006,   0.085000000000000006,   0.085000000000000006,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.085000000000000006 ], [ 0.085000000000000006,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.085000000000000006 ], [ 0.085000000000000006,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.085000000000000006 ], [ 0.085000000000000006,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.085000000000000006 ], [ 0.085000000000000006,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.063500000000000001,   0.085000000000000006,   0.085000000000000006,   0.085000000000000006 ], [ 0.085000000000000006,   0.063500000000000001,   0.085000000000000006,   0.063500000000000001,   0.085000000000000006,   -1,   -1,   -1,   -1,   -1,   -1 ]];
	ssc.data_set_matrix( data, b'D_cpnt', D_cpnt );
	L_cpnt = [[ 0,   0,   0,   0,   0,   -1,   -1,   -1,   -1,   -1,   -1 ], [ 0,   0,   0,   1,   0,   0,   0,   1,   0,   1,   0 ], [ 0,   1,   0,   1,   0,   0,   0,   1,   0,   1,   0 ], [ 0,   1,   0,   1,   0,   0,   0,   1,   0,   1,   0 ], [ 0,   1,   0,   1,   0,   0,   0,   1,   0,   1,   0 ], [ 0,   1,   0,   1,   0,   0,   0,   1,   0,   0,   0 ], [ 0,   0,   0,   0,   0,   -1,   -1,   -1,   -1,   -1,   -1 ]];
	ssc.data_set_matrix( data, b'L_cpnt', L_cpnt );
	Type_cpnt = [[ 0,   1,   0,   1,   0,   -1,   -1,   -1,   -1,   -1,   -1 ], [ 1,   0,   0,   2,   0,   1,   0,   2,   0,   2,   0 ], [ 0,   2,   0,   2,   0,   1,   0,   2,   0,   2,   0 ], [ 0,   2,   0,   2,   0,   1,   0,   2,   0,   2,   0 ], [ 0,   2,   0,   2,   0,   1,   0,   2,   0,   2,   0 ], [ 0,   2,   0,   2,   0,   1,   0,   2,   0,   0,   1 ], [ 0,   1,   0,   1,   0,   -1,   -1,   -1,   -1,   -1,   -1 ]];
	ssc.data_set_matrix( data, b'Type_cpnt', Type_cpnt );
	ssc.data_set_number( data, b'custom_sf_pipe_sizes', 0 )
	sf_rnr_diams = [[ -1 ]];
	ssc.data_set_matrix( data, b'sf_rnr_diams', sf_rnr_diams );
	sf_rnr_wallthicks = [[ -1 ]];
	ssc.data_set_matrix( data, b'sf_rnr_wallthicks', sf_rnr_wallthicks );
	sf_rnr_lengths = [[ -1 ]];
	ssc.data_set_matrix( data, b'sf_rnr_lengths', sf_rnr_lengths );
	sf_hdr_diams = [[ -1 ]];
	ssc.data_set_matrix( data, b'sf_hdr_diams', sf_hdr_diams );
	sf_hdr_wallthicks = [[ -1 ]];
	ssc.data_set_matrix( data, b'sf_hdr_wallthicks', sf_hdr_wallthicks );
	sf_hdr_lengths = [[ -1 ]];
	ssc.data_set_matrix( data, b'sf_hdr_lengths', sf_hdr_lengths );
	ssc.data_set_number( data, b'adjust:constant', 4 )
	module = ssc.module_create(b'trough_physical_process_heat')	
	ssc.module_exec_set_print( 0 );
	if ssc.module_exec(module, data) == 0:
		print ('trough_physical_process_heat simulation error')
		idx = 1
		msg = ssc.module_log(module, 0)
		while (msg != None):
			print ('	: ' + msg.decode("utf - 8"))
			msg = ssc.module_log(module, idx)
			idx = idx + 1
		SystemExit( "Simulation Error" );
	ssc.module_free(module)
	ssc.data_set_number( data, b'electricity_rate', 0.059999999999999998 )
	ssc.data_set_number( data, b'fixed_operating_cost', 103758.203125 )
	module = ssc.module_create(b'iph_to_lcoefcr')	
	ssc.module_exec_set_print( 0 );
	if ssc.module_exec(module, data) == 0:
		print ('iph_to_lcoefcr simulation error')
		idx = 1
		msg = ssc.module_log(module, 0)
		while (msg != None):
			print ('	: ' + msg.decode("utf - 8"))
			msg = ssc.module_log(module, idx)
			idx = idx + 1
		SystemExit( "Simulation Error" );
	ssc.module_free(module)
	ssc.data_set_number( data, b'capital_cost', 7263074 )
	ssc.data_set_number( data, b'variable_operating_cost', 0.0010000000474974513 )
	ssc.data_set_number( data, b'fixed_charge_rate', 0.10807878524065018 )
	module = ssc.module_create(b'lcoefcr')	
	ssc.module_exec_set_print( 0 );
	if ssc.module_exec(module, data) == 0:
		print ('lcoefcr simulation error')
		idx = 1
		msg = ssc.module_log(module, 0)
		while (msg != None):
			print ('	: ' + msg.decode("utf - 8"))
			msg = ssc.module_log(module, idx)
			idx = idx + 1
		SystemExit( "Simulation Error" );
	ssc.module_free(module)
	annual_energy = ssc.data_get_number(data, b'annual_energy');
	print ('Annual net energy (year 1) = ', annual_energy)
	annual_gross_energy = ssc.data_get_number(data, b'annual_gross_energy');
	print ('Annual gross energy (year 1) = ', annual_gross_energy)
	annual_thermal_consumption = ssc.data_get_number(data, b'annual_thermal_consumption');
	print ('Annual thermal freeze protection (year 1) = ', annual_thermal_consumption)
	capacity_factor = ssc.data_get_number(data, b'capacity_factor');
	print ('Capacity factor = ', capacity_factor)
	annual_electricity_consumption = ssc.data_get_number(data, b'annual_electricity_consumption');
	print ('Annual electricity load (year 1) = ', annual_electricity_consumption)
	lcoe_fcr = ssc.data_get_number(data, b'lcoe_fcr');
	print ('Levelized cost of heat = ', lcoe_fcr)
	ssc.data_free(data);