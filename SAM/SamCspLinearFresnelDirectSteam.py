"""
Simulating desalination with wrapper from SAM for Linear Fresnel Direct Steam 
	+ Partnership flip with debt
Created by: Vikas Vicraman
Create date: 11/22/2018
V1: - Wrapper from SAM v11.11
    - Added function for ssc.data_free
Modified by: Vikas Vicraman
Modified date: 11/14/2018
"""
#import Model_MED_PSA as model
from SAM.PySSC import PySSC
import os

class samCspLinearFresnelDirectSteam:
	ssc = PySSC()
	print ('Current folder = D:/Columbia/Thesis/SAMProjects/Integration/V11_11/LF_DS')
	print ('SSC Version = ', ssc.version())
	print ('SSC Build Information = ', ssc.build_info().decode("utf - 8"))
	ssc.module_exec_set_print(0)
	data = ssc.data_create()
	path_solar_resource=os.path.dirname(os.path.realpath(__file__))+'/solar_resource'
	ssc.data_set_string( data, b'file_name', b''+path_solar_resource.encode("ascii", "backslashreplace") + ('/United Arab Emirates ARE Abu_Dhabi (INTL).csv').encode("ascii","backslashreplace"));
	ssc.data_set_number( data, b'track_mode', 1 )
	ssc.data_set_number( data, b'tilt', 0 )
	ssc.data_set_number( data, b'azimuth', 0 )
	ssc.data_set_number( data, b'system_capacity', 50000.94921875 )
	weekday_schedule = [[ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ]];
	ssc.data_set_matrix( data, b'weekday_schedule', weekday_schedule );
	weekend_schedule = [[ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ]];
	ssc.data_set_matrix( data, b'weekend_schedule', weekend_schedule );
	ssc.data_set_number( data, b'tes_hours', 0 )
	ssc.data_set_number( data, b'q_max_aux', 255.63600158691406 )
	ssc.data_set_number( data, b'LHV_eff', 0.89999997615814209 )
	ssc.data_set_number( data, b'x_b_des', 0.75 )
	ssc.data_set_number( data, b'P_turb_des', 110 )
	ssc.data_set_number( data, b'fP_hdr_c', 0.0099999997764825821 )
	ssc.data_set_number( data, b'fP_sf_boil', 0.075000002980232239 )
	ssc.data_set_number( data, b'fP_boil_to_sh', 0.004999999888241291 )
	ssc.data_set_number( data, b'fP_sf_sh', 0.05000000074505806 )
	ssc.data_set_number( data, b'fP_hdr_h', 0.02500000037252903 )
	ssc.data_set_number( data, b'q_pb_des', 143.37602233886719 )
	ssc.data_set_number( data, b'cycle_max_fraction', 1.0499999523162842 )
	ssc.data_set_number( data, b'cycle_cutoff_frac', 0.20000000298023224 )
	ssc.data_set_number( data, b't_sby', 2 )
	ssc.data_set_number( data, b'q_sby_frac', 0.20000000298023224 )
	ssc.data_set_number( data, b'solarm', 1.7999999523162842 )
	ssc.data_set_number( data, b'PB_pump_coef', 0 )
	ssc.data_set_number( data, b'PB_fixed_par', 0.0054999999701976776 )
	bop_array =[ 0, 1, 0.4830000102519989, 0.57099997997283936, 0 ];
	ssc.data_set_array( data, b'bop_array',  bop_array);
	aux_array =[ 0.023000000044703484, 1, 0.4830000102519989, 0.57099997997283936, 0 ];
	ssc.data_set_array( data, b'aux_array',  aux_array);
	ssc.data_set_number( data, b'fossil_mode', 1 )
	ssc.data_set_number( data, b'I_bn_des', 950 )
	ssc.data_set_number( data, b'is_sh', 1 )
	ssc.data_set_number( data, b'is_oncethru', 0 )
	ssc.data_set_number( data, b'is_multgeom', 1 )
	ssc.data_set_number( data, b'nModBoil', 12 )
	ssc.data_set_number( data, b'nModSH', 4 )
	ssc.data_set_number( data, b'nLoops', 53 )
	ssc.data_set_number( data, b'eta_pump', 0.85000002384185791 )
	ssc.data_set_number( data, b'latitude', 32.130001068115234 )
	ssc.data_set_number( data, b'theta_stow', 10 )
	ssc.data_set_number( data, b'theta_dep', 10 )
	ssc.data_set_number( data, b'm_dot_min', 0.05000000074505806 )
	ssc.data_set_number( data, b'T_fp', 10 )
	ssc.data_set_number( data, b'Pipe_hl_coef', 0.0035000001080334187 )
	ssc.data_set_number( data, b'SCA_drives_elec', 0.20000000298023224 )
	ssc.data_set_number( data, b'ColAz', 0 )
	ssc.data_set_number( data, b'e_startup', 2.7000000476837158 )
	ssc.data_set_number( data, b'T_amb_des_sf', 42 )
	ssc.data_set_number( data, b'V_wind_max', 20 )
	ssc.data_set_number( data, b'csp.lf.sf.water_per_wash', 0.019999999552965164 )
	ssc.data_set_number( data, b'csp.lf.sf.washes_per_year', 120 )
	ffrac =[ 0, 0, 0, 0, 0, 0, 0, 0, 0 ];
	ssc.data_set_array( data, b'ffrac',  ffrac);
	A_aperture = [[ 513.5999755859375 ], [ 513.5999755859375 ]];
	ssc.data_set_matrix( data, b'A_aperture', A_aperture );
	L_col = [[ 44.799999237060547 ], [ 44.799999237060547 ]];
	ssc.data_set_matrix( data, b'L_col', L_col );
	OptCharType = [[ 1 ], [ 1 ]];
	ssc.data_set_matrix( data, b'OptCharType', OptCharType );
	IAM_T = [[ 0.98960000276565552,   0.043999999761581421,   -0.072099998593330383,   -0.23270000517368317,   0 ], [ 0.98960000276565552,   0.043999999761581421,   -0.072099998593330383,   -0.23270000517368317,   0 ]];
	ssc.data_set_matrix( data, b'IAM_T', IAM_T );
	IAM_L = [[ 1.0031000375747681,   -0.22589999437332153,   0.53680002689361572,   -1.6433999538421631,   0.72219997644424438 ], [ 1.0031000375747681,   -0.22589999437332153,   0.53680002689361572,   -1.6433999538421631,   0.72219997644424438 ]];
	ssc.data_set_matrix( data, b'IAM_L', IAM_L );
	TrackingError = [[ 1 ], [ 1 ]];
	ssc.data_set_matrix( data, b'TrackingError', TrackingError );
	GeomEffects = [[ 0.72399997711181641 ], [ 0.72399997711181641 ]];
	ssc.data_set_matrix( data, b'GeomEffects', GeomEffects );
	rho_mirror_clean = [[ 0.93500000238418579 ], [ 0.93500000238418579 ]];
	ssc.data_set_matrix( data, b'rho_mirror_clean', rho_mirror_clean );
	dirt_mirror = [[ 0.94999998807907104 ], [ 0.94999998807907104 ]];
	ssc.data_set_matrix( data, b'dirt_mirror', dirt_mirror );
	error = [[ 1 ], [ 1 ]];
	ssc.data_set_matrix( data, b'error', error );
	HLCharType = [[ 1 ], [ 1 ]];
	ssc.data_set_matrix( data, b'HLCharType', HLCharType );
	HL_dT = [[ 0,   0.67199999094009399,   0.0025559999048709869,   0,   0 ], [ 0,   0.67199999094009399,   0.0025559999048709869,   0,   0 ]];
	ssc.data_set_matrix( data, b'HL_dT', HL_dT );
	HL_W = [[ 1,   0,   0,   0,   0 ], [ 1,   0,   0,   0,   0 ]];
	ssc.data_set_matrix( data, b'HL_W', HL_W );
	D_2 = [[ 0.065999999642372131 ], [ 0.065999999642372131 ]];
	ssc.data_set_matrix( data, b'D_2', D_2 );
	D_3 = [[ 0.070000000298023224 ], [ 0.070000000298023224 ]];
	ssc.data_set_matrix( data, b'D_3', D_3 );
	D_4 = [[ 0.11500000208616257 ], [ 0.11500000208616257 ]];
	ssc.data_set_matrix( data, b'D_4', D_4 );
	D_5 = [[ 0.11999999731779099 ], [ 0.11999999731779099 ]];
	ssc.data_set_matrix( data, b'D_5', D_5 );
	D_p = [[ 0 ], [ 0 ]];
	ssc.data_set_matrix( data, b'D_p', D_p );
	Rough = [[ 4.5000000682193786e-05 ], [ 4.5000000682193786e-05 ]];
	ssc.data_set_matrix( data, b'Rough', Rough );
	Flow_type = [[ 1 ], [ 1 ]];
	ssc.data_set_matrix( data, b'Flow_type', Flow_type );
	AbsorberMaterial = [[ 1 ], [ 1 ]];
	ssc.data_set_matrix( data, b'AbsorberMaterial', AbsorberMaterial );
	HCE_FieldFrac = [[ 0.98500001430511475,   0.0099999997764825821,   0.004999999888241291,   0 ], [ 0.98500001430511475,   0.0099999997764825821,   0.004999999888241291,   0 ]];
	ssc.data_set_matrix( data, b'HCE_FieldFrac', HCE_FieldFrac );
	alpha_abs = [[ 0.95999997854232788,   0.95999997854232788,   0.80000001192092896,   0 ], [ 0.95999997854232788,   0.95999997854232788,   0.80000001192092896,   0 ]];
	ssc.data_set_matrix( data, b'alpha_abs', alpha_abs );
	b_eps_HCE1 = [[ 0 ], [ 0.13840000331401825 ]];
	ssc.data_set_matrix( data, b'b_eps_HCE1', b_eps_HCE1 );
	b_eps_HCE2 = [[ 0 ], [ 0.64999997615814209 ]];
	ssc.data_set_matrix( data, b'b_eps_HCE2', b_eps_HCE2 );
	b_eps_HCE3 = [[ 0 ], [ 0.64999997615814209 ]];
	ssc.data_set_matrix( data, b'b_eps_HCE3', b_eps_HCE3 );
	b_eps_HCE4 = [[ 0 ], [ 0.13840000331401825 ]];
	ssc.data_set_matrix( data, b'b_eps_HCE4', b_eps_HCE4 );
	sh_eps_HCE1 = [[ 0 ], [ 0.13840000331401825 ]];
	ssc.data_set_matrix( data, b'sh_eps_HCE1', sh_eps_HCE1 );
	sh_eps_HCE2 = [[ 0 ], [ 0.64999997615814209 ]];
	ssc.data_set_matrix( data, b'sh_eps_HCE2', sh_eps_HCE2 );
	sh_eps_HCE3 = [[ 0 ], [ 0.64999997615814209 ]];
	ssc.data_set_matrix( data, b'sh_eps_HCE3', sh_eps_HCE3 );
	sh_eps_HCE4 = [[ 0 ], [ 0.13840000331401825 ]];
	ssc.data_set_matrix( data, b'sh_eps_HCE4', sh_eps_HCE4 );
	alpha_env = [[ 0.019999999552965164,   0.019999999552965164,   0,   0 ], [ 0.019999999552965164,   0.019999999552965164,   0,   0 ]];
	ssc.data_set_matrix( data, b'alpha_env', alpha_env );
	EPSILON_4 = [[ 0.86000001430511475,   0.86000001430511475,   1,   0 ], [ 0.86000001430511475,   0.86000001430511475,   1,   0 ]];
	ssc.data_set_matrix( data, b'EPSILON_4', EPSILON_4 );
	Tau_envelope = [[ 0.96299999952316284,   0.96299999952316284,   1,   0 ], [ 0.96299999952316284,   0.96299999952316284,   1,   0 ]];
	ssc.data_set_matrix( data, b'Tau_envelope', Tau_envelope );
	GlazingIntactIn = [[ 1,   1,   0,   1 ], [ 1,   1,   0,   1 ]];
	ssc.data_set_matrix( data, b'GlazingIntactIn', GlazingIntactIn );
	AnnulusGas = [[ 27,   1,   1,   1 ], [ 27,   1,   1,   1 ]];
	ssc.data_set_matrix( data, b'AnnulusGas', AnnulusGas );
	P_a = [[ 9.9999997473787516e-05,   750,   750,   0 ], [ 9.9999997473787516e-05,   750,   750,   0 ]];
	ssc.data_set_matrix( data, b'P_a', P_a );
	Design_loss = [[ 150,   1100,   1500,   0 ], [ 150,   1100,   1500,   0 ]];
	ssc.data_set_matrix( data, b'Design_loss', Design_loss );
	Shadowing = [[ 0.95999997854232788,   0.95999997854232788,   0.95999997854232788,   0 ], [ 0.95999997854232788,   0.95999997854232788,   0.95999997854232788,   0 ]];
	ssc.data_set_matrix( data, b'Shadowing', Shadowing );
	Dirt_HCE = [[ 0.98000001907348633,   0.98000001907348633,   1,   0 ], [ 0.98000001907348633,   0.98000001907348633,   1,   0 ]];
	ssc.data_set_matrix( data, b'Dirt_HCE', Dirt_HCE );
	b_OpticalTable = [[ -180,   -160,   -140,   -120,   -100,   -80,   -60,   -40,   -20,   0,   20,   40,   60,   80,   100,   120,   140,   160,   180,   -999.9000244140625 ], [ 0,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1 ], [ 10,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633 ], [ 20,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737 ], [ 30,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563 ], [ 40,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949 ], [ 50,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896 ], [ 60,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869 ], [ 70,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842 ], [ 80,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821 ], [ 90,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0 ]];
	ssc.data_set_matrix( data, b'b_OpticalTable', b_OpticalTable );
	sh_OpticalTable = [[ -180,   -160,   -140,   -120,   -100,   -80,   -60,   -40,   -20,   0,   20,   40,   60,   80,   100,   120,   140,   160,   180,   -999.9000244140625 ], [ 0,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1 ], [ 10,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633 ], [ 20,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737 ], [ 30,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563 ], [ 40,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949 ], [ 50,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896 ], [ 60,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869 ], [ 70,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842 ], [ 80,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821 ]];
	ssc.data_set_matrix( data, b'sh_OpticalTable', sh_OpticalTable );
	ssc.data_set_number( data, b'dnifc', 0 )
	ssc.data_set_number( data, b'I_bn', 0 )
	ssc.data_set_number( data, b'T_db', 15 )
	ssc.data_set_number( data, b'T_dp', 10 )
	ssc.data_set_number( data, b'P_amb', 930.5 )
	ssc.data_set_number( data, b'V_wind', 0 )
	ssc.data_set_number( data, b'm_dot_htf_ref', 0 )
	ssc.data_set_number( data, b'm_pb_demand', 0 )
	ssc.data_set_number( data, b'shift', 0 )
	ssc.data_set_number( data, b'SolarAz_init', 0 )
	ssc.data_set_number( data, b'SolarZen', 0 )
	ssc.data_set_number( data, b'T_pb_out_init', 290 )
	ssc.data_set_number( data, b'eta_ref', 0.37099999189376831 )
	ssc.data_set_number( data, b'T_cold_ref', 230 )
	ssc.data_set_number( data, b'dT_cw_ref', 10 )
	ssc.data_set_number( data, b'T_amb_des', 42 )
	ssc.data_set_number( data, b'P_boil_des', 110 )
	ssc.data_set_number( data, b'P_rh_ref', 0 )
	ssc.data_set_number( data, b'rh_frac_ref', 0 )
	ssc.data_set_number( data, b'CT', 2 )
	ssc.data_set_number( data, b'startup_time', 0.34999999403953552 )
	ssc.data_set_number( data, b'startup_frac', 0.34999999403953552 )
	ssc.data_set_number( data, b'T_approach', 5 )
	ssc.data_set_number( data, b'T_ITD_des', 40) #16 )
	ssc.data_set_number( data, b'P_cond_ratio', 1.0027999877929688 )
	ssc.data_set_number( data, b'pb_bd_frac', 0.019999999552965164 )
	ssc.data_set_number( data, b'P_cond_min', 1.25 )
	ssc.data_set_number( data, b'n_pl_inc', 8 )
	F_wc =[ 0, 0, 0, 0, 0, 0, 0, 0, 0 ];
	ssc.data_set_array( data, b'F_wc',  F_wc);
	ssc.data_set_number( data, b'pc_mode', 1 )
	ssc.data_set_number( data, b'T_hot', 440 )
	ssc.data_set_number( data, b'm_dot_st', 0 )
	ssc.data_set_number( data, b'T_wb', 12.800000190734863 )
	ssc.data_set_number( data, b'demand_var', 53.192501068115234 )
	ssc.data_set_number( data, b'standby_control', 0 )
	ssc.data_set_number( data, b'T_db_pwb', 12.800000190734863 )
	ssc.data_set_number( data, b'P_amb_pwb', 960 )
	ssc.data_set_number( data, b'relhum', 0.25 )
	ssc.data_set_number( data, b'f_recSU', 1 )
	ssc.data_set_number( data, b'dp_b', 0 )
	ssc.data_set_number( data, b'dp_sh', 5 )
	ssc.data_set_number( data, b'dp_rh', 0 )
	ssc.data_set_number( data, b'adjust:constant', 4 )
	module = ssc.module_create(b'tcslinear_fresnel')	
	ssc.module_exec_set_print( 0 );
	if ssc.module_exec(module, data) == 0:
		print ('tcslinear_fresnel simulation error')
		idx = 1
		msg = ssc.module_log(module, 0)
		while (msg != None):
			print ('	: ' + msg.decode("utf - 8"))
			msg = ssc.module_log(module, idx)
			idx = idx + 1
		SystemExit( "Simulation Error" );
	ssc.module_free(module)
	ssc.data_set_number( data, b'analysis_period', 25 )
	federal_tax_rate =[ 21 ];
	ssc.data_set_array( data, b'federal_tax_rate',  federal_tax_rate);
	state_tax_rate =[ 7 ];
	ssc.data_set_array( data, b'state_tax_rate',  state_tax_rate);
	ssc.data_set_number( data, b'property_tax_rate', 0 )
	ssc.data_set_number( data, b'prop_tax_cost_assessed_percent', 100 )
	ssc.data_set_number( data, b'prop_tax_assessed_decline', 0 )
	ssc.data_set_number( data, b'real_discount_rate', 6.4000000953674316 )
	ssc.data_set_number( data, b'inflation_rate', 2.5 )
	ssc.data_set_number( data, b'insurance_rate', 0.5 )
	om_fixed =[ 0 ];
	ssc.data_set_array( data, b'om_fixed',  om_fixed);
	ssc.data_set_number( data, b'om_fixed_escal', 0 )
	om_production =[ 4 ];
	ssc.data_set_array( data, b'om_production',  om_production);
	ssc.data_set_number( data, b'om_production_escal', 0 )
	om_capacity =[ 55 ];
	ssc.data_set_array( data, b'om_capacity',  om_capacity);
	ssc.data_set_number( data, b'om_capacity_escal', 0 )
	om_fuel_cost =[ 0 ];
	ssc.data_set_array( data, b'om_fuel_cost',  om_fuel_cost);
	ssc.data_set_number( data, b'om_fuel_cost_escal', 0 )
	ssc.data_set_number( data, b'itc_fed_amount', 0 )
	ssc.data_set_number( data, b'itc_fed_amount_deprbas_fed', 1 )
	ssc.data_set_number( data, b'itc_fed_amount_deprbas_sta', 1 )
	ssc.data_set_number( data, b'itc_sta_amount', 0 )
	ssc.data_set_number( data, b'itc_sta_amount_deprbas_fed', 0 )
	ssc.data_set_number( data, b'itc_sta_amount_deprbas_sta', 0 )
	ssc.data_set_number( data, b'itc_fed_percent', 30 )
	ssc.data_set_number( data, b'itc_fed_percent_maxvalue', 9.9999996802856925e+37 )
	ssc.data_set_number( data, b'itc_fed_percent_deprbas_fed', 1 )
	ssc.data_set_number( data, b'itc_fed_percent_deprbas_sta', 1 )
	ssc.data_set_number( data, b'itc_sta_percent', 0 )
	ssc.data_set_number( data, b'itc_sta_percent_maxvalue', 9.9999996802856925e+37 )
	ssc.data_set_number( data, b'itc_sta_percent_deprbas_fed', 0 )
	ssc.data_set_number( data, b'itc_sta_percent_deprbas_sta', 0 )
	ptc_fed_amount =[ 0 ];
	ssc.data_set_array( data, b'ptc_fed_amount',  ptc_fed_amount);
	ssc.data_set_number( data, b'ptc_fed_term', 10 )
	ssc.data_set_number( data, b'ptc_fed_escal', 0 )
	ptc_sta_amount =[ 0 ];
	ssc.data_set_array( data, b'ptc_sta_amount',  ptc_sta_amount);
	ssc.data_set_number( data, b'ptc_sta_term', 10 )
	ssc.data_set_number( data, b'ptc_sta_escal', 0 )
	ssc.data_set_number( data, b'ibi_fed_amount', 0 )
	ssc.data_set_number( data, b'ibi_fed_amount_tax_fed', 1 )
	ssc.data_set_number( data, b'ibi_fed_amount_tax_sta', 1 )
	ssc.data_set_number( data, b'ibi_fed_amount_deprbas_fed', 0 )
	ssc.data_set_number( data, b'ibi_fed_amount_deprbas_sta', 0 )
	ssc.data_set_number( data, b'ibi_sta_amount', 0 )
	ssc.data_set_number( data, b'ibi_sta_amount_tax_fed', 1 )
	ssc.data_set_number( data, b'ibi_sta_amount_tax_sta', 1 )
	ssc.data_set_number( data, b'ibi_sta_amount_deprbas_fed', 0 )
	ssc.data_set_number( data, b'ibi_sta_amount_deprbas_sta', 0 )
	ssc.data_set_number( data, b'ibi_uti_amount', 0 )
	ssc.data_set_number( data, b'ibi_uti_amount_tax_fed', 1 )
	ssc.data_set_number( data, b'ibi_uti_amount_tax_sta', 1 )
	ssc.data_set_number( data, b'ibi_uti_amount_deprbas_fed', 0 )
	ssc.data_set_number( data, b'ibi_uti_amount_deprbas_sta', 0 )
	ssc.data_set_number( data, b'ibi_oth_amount', 0 )
	ssc.data_set_number( data, b'ibi_oth_amount_tax_fed', 1 )
	ssc.data_set_number( data, b'ibi_oth_amount_tax_sta', 1 )
	ssc.data_set_number( data, b'ibi_oth_amount_deprbas_fed', 0 )
	ssc.data_set_number( data, b'ibi_oth_amount_deprbas_sta', 0 )
	ssc.data_set_number( data, b'ibi_fed_percent', 0 )
	ssc.data_set_number( data, b'ibi_fed_percent_maxvalue', 9.9999996802856925e+37 )
	ssc.data_set_number( data, b'ibi_fed_percent_tax_fed', 1 )
	ssc.data_set_number( data, b'ibi_fed_percent_tax_sta', 1 )
	ssc.data_set_number( data, b'ibi_fed_percent_deprbas_fed', 0 )
	ssc.data_set_number( data, b'ibi_fed_percent_deprbas_sta', 0 )
	ssc.data_set_number( data, b'ibi_sta_percent', 0 )
	ssc.data_set_number( data, b'ibi_sta_percent_maxvalue', 9.9999996802856925e+37 )
	ssc.data_set_number( data, b'ibi_sta_percent_tax_fed', 1 )
	ssc.data_set_number( data, b'ibi_sta_percent_tax_sta', 1 )
	ssc.data_set_number( data, b'ibi_sta_percent_deprbas_fed', 0 )
	ssc.data_set_number( data, b'ibi_sta_percent_deprbas_sta', 0 )
	ssc.data_set_number( data, b'ibi_uti_percent', 0 )
	ssc.data_set_number( data, b'ibi_uti_percent_maxvalue', 9.9999996802856925e+37 )
	ssc.data_set_number( data, b'ibi_uti_percent_tax_fed', 1 )
	ssc.data_set_number( data, b'ibi_uti_percent_tax_sta', 1 )
	ssc.data_set_number( data, b'ibi_uti_percent_deprbas_fed', 0 )
	ssc.data_set_number( data, b'ibi_uti_percent_deprbas_sta', 0 )
	ssc.data_set_number( data, b'ibi_oth_percent', 0 )
	ssc.data_set_number( data, b'ibi_oth_percent_maxvalue', 9.9999996802856925e+37 )
	ssc.data_set_number( data, b'ibi_oth_percent_tax_fed', 1 )
	ssc.data_set_number( data, b'ibi_oth_percent_tax_sta', 1 )
	ssc.data_set_number( data, b'ibi_oth_percent_deprbas_fed', 0 )
	ssc.data_set_number( data, b'ibi_oth_percent_deprbas_sta', 0 )
	ssc.data_set_number( data, b'cbi_fed_amount', 0 )
	ssc.data_set_number( data, b'cbi_fed_maxvalue', 9.9999996802856925e+37 )
	ssc.data_set_number( data, b'cbi_fed_tax_fed', 1 )
	ssc.data_set_number( data, b'cbi_fed_tax_sta', 1 )
	ssc.data_set_number( data, b'cbi_fed_deprbas_fed', 0 )
	ssc.data_set_number( data, b'cbi_fed_deprbas_sta', 0 )
	ssc.data_set_number( data, b'cbi_sta_amount', 0 )
	ssc.data_set_number( data, b'cbi_sta_maxvalue', 9.9999996802856925e+37 )
	ssc.data_set_number( data, b'cbi_sta_tax_fed', 1 )
	ssc.data_set_number( data, b'cbi_sta_tax_sta', 1 )
	ssc.data_set_number( data, b'cbi_sta_deprbas_fed', 0 )
	ssc.data_set_number( data, b'cbi_sta_deprbas_sta', 0 )
	ssc.data_set_number( data, b'cbi_uti_amount', 0 )
	ssc.data_set_number( data, b'cbi_uti_maxvalue', 9.9999996802856925e+37 )
	ssc.data_set_number( data, b'cbi_uti_tax_fed', 1 )
	ssc.data_set_number( data, b'cbi_uti_tax_sta', 1 )
	ssc.data_set_number( data, b'cbi_uti_deprbas_fed', 0 )
	ssc.data_set_number( data, b'cbi_uti_deprbas_sta', 0 )
	ssc.data_set_number( data, b'cbi_oth_amount', 0 )
	ssc.data_set_number( data, b'cbi_oth_maxvalue', 9.9999996802856925e+37 )
	ssc.data_set_number( data, b'cbi_oth_tax_fed', 1 )
	ssc.data_set_number( data, b'cbi_oth_tax_sta', 1 )
	ssc.data_set_number( data, b'cbi_oth_deprbas_fed', 0 )
	ssc.data_set_number( data, b'cbi_oth_deprbas_sta', 0 )
	pbi_fed_amount =[ 0 ];
	ssc.data_set_array( data, b'pbi_fed_amount',  pbi_fed_amount);
	ssc.data_set_number( data, b'pbi_fed_term', 0 )
	ssc.data_set_number( data, b'pbi_fed_escal', 0 )
	ssc.data_set_number( data, b'pbi_fed_tax_fed', 1 )
	ssc.data_set_number( data, b'pbi_fed_tax_sta', 1 )
	pbi_sta_amount =[ 0 ];
	ssc.data_set_array( data, b'pbi_sta_amount',  pbi_sta_amount);
	ssc.data_set_number( data, b'pbi_sta_term', 0 )
	ssc.data_set_number( data, b'pbi_sta_escal', 0 )
	ssc.data_set_number( data, b'pbi_sta_tax_fed', 1 )
	ssc.data_set_number( data, b'pbi_sta_tax_sta', 1 )
	pbi_uti_amount =[ 0 ];
	ssc.data_set_array( data, b'pbi_uti_amount',  pbi_uti_amount);
	ssc.data_set_number( data, b'pbi_uti_term', 0 )
	ssc.data_set_number( data, b'pbi_uti_escal', 0 )
	ssc.data_set_number( data, b'pbi_uti_tax_fed', 1 )
	ssc.data_set_number( data, b'pbi_uti_tax_sta', 1 )
	pbi_oth_amount =[ 0 ];
	ssc.data_set_array( data, b'pbi_oth_amount',  pbi_oth_amount);
	ssc.data_set_number( data, b'pbi_oth_term', 0 )
	ssc.data_set_number( data, b'pbi_oth_escal', 0 )
	ssc.data_set_number( data, b'pbi_oth_tax_fed', 1 )
	ssc.data_set_number( data, b'pbi_oth_tax_sta', 1 )
	degradation =[ 0 ];
	ssc.data_set_array( data, b'degradation',  degradation);
	ssc.data_set_number( data, b'loan_moratorium', 0 )
	ssc.data_set_number( data, b'system_use_recapitalization', 0 )
	ssc.data_set_number( data, b'system_use_lifetime_output', 0 )
	ssc.data_set_number( data, b'ppa_multiplier_model', 0 )
	ssc.data_set_array_from_csv( data, b'dispatch_factors_ts', b'SAM/AssociatedFiles/dispatch_factors_ts.csv');
	ssc.data_set_number( data, b'dispatch_factor1', 2.0639998912811279 )
	ssc.data_set_number( data, b'dispatch_factor2', 1.2000000476837158 )
	ssc.data_set_number( data, b'dispatch_factor3', 1 )
	ssc.data_set_number( data, b'dispatch_factor4', 1.1000000238418579 )
	ssc.data_set_number( data, b'dispatch_factor5', 0.80000001192092896 )
	ssc.data_set_number( data, b'dispatch_factor6', 0.69999998807907104 )
	ssc.data_set_number( data, b'dispatch_factor7', 1 )
	ssc.data_set_number( data, b'dispatch_factor8', 1 )
	ssc.data_set_number( data, b'dispatch_factor9', 1 )
	dispatch_sched_weekday = [[ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ]];
	ssc.data_set_matrix( data, b'dispatch_sched_weekday', dispatch_sched_weekday );
	dispatch_sched_weekend = [[ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ]];
	ssc.data_set_matrix( data, b'dispatch_sched_weekend', dispatch_sched_weekend );
	ssc.data_set_number( data, b'total_installed_cost', 185785712 )
	ssc.data_set_number( data, b'reserves_interest', 1.75 )
	ssc.data_set_number( data, b'equip1_reserve_cost', 0 )
	ssc.data_set_number( data, b'equip1_reserve_freq', 12 )
	ssc.data_set_number( data, b'equip2_reserve_cost', 0 )
	ssc.data_set_number( data, b'equip2_reserve_freq', 15 )
	ssc.data_set_number( data, b'equip3_reserve_cost', 0 )
	ssc.data_set_number( data, b'equip3_reserve_freq', 3 )
	ssc.data_set_number( data, b'equip_reserve_depr_sta', 0 )
	ssc.data_set_number( data, b'equip_reserve_depr_fed', 0 )
	ssc.data_set_number( data, b'salvage_percentage', 0 )
	ssc.data_set_number( data, b'ppa_soln_mode', 0 )
	ssc.data_set_number( data, b'ppa_price_input', 0.12999999523162842 )
	ssc.data_set_number( data, b'ppa_escalation', 1 )
	ssc.data_set_number( data, b'construction_financing_cost', 9289286 )
	ssc.data_set_number( data, b'term_tenor', 18 )
	ssc.data_set_number( data, b'term_int_rate', 7 )
	ssc.data_set_number( data, b'dscr', 1.2999999523162842 )
	ssc.data_set_number( data, b'dscr_reserve_months', 6 )
	ssc.data_set_number( data, b'debt_percent', 50 )
	ssc.data_set_number( data, b'debt_option', 1 )
	ssc.data_set_number( data, b'payment_option', 0 )
	ssc.data_set_number( data, b'cost_dev_fee_percent', 3 )
	ssc.data_set_number( data, b'cost_debt_closing', 450000 )
	ssc.data_set_number( data, b'cost_debt_fee', 2.75 )
	ssc.data_set_number( data, b'cost_equity_closing', 300000 )
	ssc.data_set_number( data, b'months_working_reserve', 6 )
	ssc.data_set_number( data, b'months_receivables_reserve', 0 )
	ssc.data_set_number( data, b'cost_other_financing', 0 )
	ssc.data_set_number( data, b'tax_investor_equity_percent', 98 )
	ssc.data_set_number( data, b'tax_investor_preflip_cash_percent', 98 )
	ssc.data_set_number( data, b'tax_investor_postflip_cash_percent', 10 )
	ssc.data_set_number( data, b'tax_investor_preflip_tax_percent', 98 )
	ssc.data_set_number( data, b'tax_investor_postflip_tax_percent', 10 )
	ssc.data_set_number( data, b'flip_target_percent', 11 )
	ssc.data_set_number( data, b'flip_target_year', 9 )
	ssc.data_set_number( data, b'depr_alloc_macrs_5_percent', 89 )
	ssc.data_set_number( data, b'depr_alloc_macrs_15_percent', 1.5 )
	ssc.data_set_number( data, b'depr_alloc_sl_5_percent', 0 )
	ssc.data_set_number( data, b'depr_alloc_sl_15_percent', 3 )
	ssc.data_set_number( data, b'depr_alloc_sl_20_percent', 3.5 )
	ssc.data_set_number( data, b'depr_alloc_sl_39_percent', 0 )
	ssc.data_set_number( data, b'depr_alloc_custom_percent', 0 )
	depr_custom_schedule =[ 0 ];
	ssc.data_set_array( data, b'depr_custom_schedule',  depr_custom_schedule);
	ssc.data_set_number( data, b'depr_bonus_sta', 0 )
	ssc.data_set_number( data, b'depr_bonus_sta_macrs_5', 1 )
	ssc.data_set_number( data, b'depr_bonus_sta_macrs_15', 1 )
	ssc.data_set_number( data, b'depr_bonus_sta_sl_5', 0 )
	ssc.data_set_number( data, b'depr_bonus_sta_sl_15', 0 )
	ssc.data_set_number( data, b'depr_bonus_sta_sl_20', 0 )
	ssc.data_set_number( data, b'depr_bonus_sta_sl_39', 0 )
	ssc.data_set_number( data, b'depr_bonus_sta_custom', 0 )
	ssc.data_set_number( data, b'depr_bonus_fed', 0 )
	ssc.data_set_number( data, b'depr_bonus_fed_macrs_5', 1 )
	ssc.data_set_number( data, b'depr_bonus_fed_macrs_15', 1 )
	ssc.data_set_number( data, b'depr_bonus_fed_sl_5', 0 )
	ssc.data_set_number( data, b'depr_bonus_fed_sl_15', 0 )
	ssc.data_set_number( data, b'depr_bonus_fed_sl_20', 0 )
	ssc.data_set_number( data, b'depr_bonus_fed_sl_39', 0 )
	ssc.data_set_number( data, b'depr_bonus_fed_custom', 0 )
	ssc.data_set_number( data, b'depr_itc_sta_macrs_5', 1 )
	ssc.data_set_number( data, b'depr_itc_sta_macrs_15', 0 )
	ssc.data_set_number( data, b'depr_itc_sta_sl_5', 0 )
	ssc.data_set_number( data, b'depr_itc_sta_sl_15', 0 )
	ssc.data_set_number( data, b'depr_itc_sta_sl_20', 0 )
	ssc.data_set_number( data, b'depr_itc_sta_sl_39', 0 )
	ssc.data_set_number( data, b'depr_itc_sta_custom', 0 )
	ssc.data_set_number( data, b'depr_itc_fed_macrs_5', 1 )
	ssc.data_set_number( data, b'depr_itc_fed_macrs_15', 0 )
	ssc.data_set_number( data, b'depr_itc_fed_sl_5', 0 )
	ssc.data_set_number( data, b'depr_itc_fed_sl_15', 0 )
	ssc.data_set_number( data, b'depr_itc_fed_sl_20', 0 )
	ssc.data_set_number( data, b'depr_itc_fed_sl_39', 0 )
	ssc.data_set_number( data, b'depr_itc_fed_custom', 0 )
	ssc.data_set_number( data, b'pbi_fed_for_ds', 0 )
	ssc.data_set_number( data, b'pbi_sta_for_ds', 0 )
	ssc.data_set_number( data, b'pbi_uti_for_ds', 0 )
	ssc.data_set_number( data, b'pbi_oth_for_ds', 0 )
	ssc.data_set_number( data, b'depr_stabas_method', 1 )
	ssc.data_set_number( data, b'depr_fedbas_method', 1 )
	module = ssc.module_create(b'levpartflip')	
	ssc.module_exec_set_print( 0 );
	if ssc.module_exec(module, data) == 0:
		print ('levpartflip simulation error')
		idx = 1
		msg = ssc.module_log(module, 0)
		while (msg != None):
			print ('	: ' + msg.decode("utf - 8"))
			msg = ssc.module_log(module, idx)
			idx = idx + 1
		SystemExit( "Simulation Error" );
	ssc.module_free(module)
	annual_energy = ssc.data_get_number(data, b'annual_energy');
	print ('Annual energy (year 1) = ', annual_energy)
	capacity_factor = ssc.data_get_number(data, b'capacity_factor');
	print ('Capacity factor (year 1) = ', capacity_factor)
	annual_total_water_use = ssc.data_get_number(data, b'annual_total_water_use');
	print ('Annual Water Usage = ', annual_total_water_use)
	ppa = ssc.data_get_number(data, b'ppa');
	print ('PPA price (year 1) = ', ppa)
	lppa_nom = ssc.data_get_number(data, b'lppa_nom');
	print ('Levelized PPA price (nominal) = ', lppa_nom)
	lppa_real = ssc.data_get_number(data, b'lppa_real');
	print ('Levelized PPA price (real) = ', lppa_real)
	lcoe_nom = ssc.data_get_number(data, b'lcoe_nom');
	print ('Levelized COE (nominal) = ', lcoe_nom)
	lcoe_real = ssc.data_get_number(data, b'lcoe_real');
	print ('Levelized COE (real) = ', lcoe_real)
	flip_actual_irr = ssc.data_get_number(data, b'flip_actual_irr');
	print ('Investor IRR = ', flip_actual_irr)
	flip_actual_year = ssc.data_get_number(data, b'flip_actual_year');
	print ('Year investor IRR acheived = ', flip_actual_year)
	tax_investor_aftertax_irr = ssc.data_get_number(data, b'tax_investor_aftertax_irr');
	print ('Investor IRR at end of project = ', tax_investor_aftertax_irr)
	tax_investor_aftertax_npv = ssc.data_get_number(data, b'tax_investor_aftertax_npv');
	print ('Investor NPV over project life = ', tax_investor_aftertax_npv)
	sponsor_aftertax_irr = ssc.data_get_number(data, b'sponsor_aftertax_irr');
	print ('Developer IRR at end of project = ', sponsor_aftertax_irr)
	sponsor_aftertax_npv = ssc.data_get_number(data, b'sponsor_aftertax_npv');
	print ('Developer NPV over project life = ', sponsor_aftertax_npv)
	cost_installed = ssc.data_get_number(data, b'cost_installed');
	print ('Net capital cost = ', cost_installed)
	size_of_equity = ssc.data_get_number(data, b'size_of_equity');
	print ('Equity = ', size_of_equity)
	size_of_debt = ssc.data_get_number(data, b'size_of_debt');
	print ('Debt = ', size_of_debt)
	def data_free(self):
		self.ssc.data_free(self.data);
#	ssc.data_free(data);