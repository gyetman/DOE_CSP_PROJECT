#import Model_MED_PSA as model
from SAM.PySSC import PySSC

class samCspParabolicTroughEmpirical:
	ssc = PySSC()
	print ('Current folder = C:/Users/Thomas/Documents/GitHub/SAM_temp')
	print ('SSC Version = ', ssc.version())
	print ('SSC Build Information = ', ssc.build_info().decode("utf - 8"))
	ssc.module_exec_set_print(0)
	data = ssc.data_create()
	ssc.data_set_string( data, b'file_name', b'C:/SAM/2017.9.5/solar_resource/USA AZ Tucson (TMY2).csv' );
	ssc.data_set_number( data, b'track_mode', 1 )
	ssc.data_set_number( data, b'tilt', 0 )
	ssc.data_set_number( data, b'azimuth', 0 )
	ssc.data_set_number( data, b'system_capacity', 99899.9921875 )
	weekday_schedule = [[ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ]];
	ssc.data_set_matrix( data, b'weekday_schedule', weekday_schedule );
	weekend_schedule = [[ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ]];
	ssc.data_set_matrix( data, b'weekend_schedule', weekend_schedule );
	ssc.data_set_number( data, b'i_SfTi', -999 )
	ssc.data_set_number( data, b'SfPipeHl300', 10 )
	ssc.data_set_number( data, b'SfPipeHl1', 0.0016929999692365527 )
	ssc.data_set_number( data, b'SfPipeHl2', -1.6829999367473647e-05 )
	ssc.data_set_number( data, b'SfPipeHl3', 6.7800002057083475e-08 )
	ssc.data_set_number( data, b'Stow_Angle', 170 )
	ssc.data_set_number( data, b'DepAngle', 10 )
	ssc.data_set_number( data, b'Distance_SCA', 1 )
	ssc.data_set_number( data, b'Row_Distance', 15 )
	ssc.data_set_number( data, b'NumScas', 4 )
	ssc.data_set_number( data, b'Solar_Field_Area', 858767.75 )
	ssc.data_set_number( data, b'Solar_Field_Mult', 2 )
	ssc.data_set_number( data, b'SfInTempD', 293 )
	ssc.data_set_number( data, b'SfOutTempD', 391 )
	ssc.data_set_number( data, b'MinHtfTemp', 50 )
	ssc.data_set_number( data, b'HtfGalArea', 0.61400002241134644 )
	ssc.data_set_number( data, b'SFTempInit', 100 )
	ssc.data_set_number( data, b'HTFFluid', 21 )
	ssc.data_set_number( data, b'IamF0', 1 )
	ssc.data_set_number( data, b'IamF1', 0.050599999725818634 )
	ssc.data_set_number( data, b'IamF2', -0.17630000412464142 )
	ssc.data_set_number( data, b'Ave_Focal_Length', 1.7999999523162842 )
	ssc.data_set_number( data, b'ScaLen', 100 )
	ssc.data_set_number( data, b'SCA_aper', 5 )
	ssc.data_set_number( data, b'SfAvail', 0.99000000953674316 )
	ssc.data_set_number( data, b'TrkTwstErr', 0.99400001764297485 )
	ssc.data_set_number( data, b'GeoAcc', 0.98000001907348633 )
	ssc.data_set_number( data, b'MirRef', 0.93500000238418579 )
	ssc.data_set_number( data, b'MirCln', 0.97000002861022949 )
	ssc.data_set_number( data, b'ConcFac', 1 )
	ssc.data_set_number( data, b'NumHCETypes', 4 )
	HCEtype =[ 1, 1, 1, 1 ];
	ssc.data_set_array( data, b'HCEtype',  HCEtype);
	HCEFrac =[ 0.98500001430511475, 0.0099999997764825821, 0.004999999888241291, 0 ];
	ssc.data_set_array( data, b'HCEFrac',  HCEFrac);
	HCEdust =[ 0.98000001907348633, 0.98000001907348633, 0.98000001907348633, 0.98000001907348633 ];
	ssc.data_set_array( data, b'HCEdust',  HCEdust);
	HCEBelShad =[ 0.96299999952316284, 0.96299999952316284, 0.96299999952316284, 0 ];
	ssc.data_set_array( data, b'HCEBelShad',  HCEBelShad);
	HCEEnvTrans =[ 0.96299999952316284, 0.96299999952316284, 1, 0 ];
	ssc.data_set_array( data, b'HCEEnvTrans',  HCEEnvTrans);
	HCEabs =[ 0.95999997854232788, 0.95999997854232788, 0.80000001192092896, 0 ];
	ssc.data_set_array( data, b'HCEabs',  HCEabs);
	HCEmisc =[ 1, 1, 1, 0 ];
	ssc.data_set_array( data, b'HCEmisc',  HCEmisc);
	PerfFac =[ 1, 1, 1, 0 ];
	ssc.data_set_array( data, b'PerfFac',  PerfFac);
	RefMirrAper =[ 5, 5, 5, 5 ];
	ssc.data_set_array( data, b'RefMirrAper',  RefMirrAper);
	HCE_A0 =[ 4.0500001907348633, 50.799999237060547, -9.9499998092651367, 0 ];
	ssc.data_set_array( data, b'HCE_A0',  HCE_A0);
	HCE_A1 =[ 0.24699999392032623, 0.90399998426437378, 0.46500000357627869, 0 ];
	ssc.data_set_array( data, b'HCE_A1',  HCE_A1);
	HCE_A2 =[ -0.0014600000577047467, 0.00057899998500943184, -0.00085399998351931572, 0 ];
	ssc.data_set_array( data, b'HCE_A2',  HCE_A2);
	HCE_A3 =[ 5.6499998208892066e-06, 1.1299999641778413e-05, 1.8500000805943273e-05, 0 ];
	ssc.data_set_array( data, b'HCE_A3',  HCE_A3);
	HCE_A4 =[ 7.6200002752102591e-08, 1.7300000365594315e-07, 6.8899998950655572e-07, 0 ];
	ssc.data_set_array( data, b'HCE_A4',  HCE_A4);
	HCE_A5 =[ -1.7000000476837158, -43.200000762939453, 24.700000762939453, 0 ];
	ssc.data_set_array( data, b'HCE_A5',  HCE_A5);
	HCE_A6 =[ 0.012500000186264515, 0.52399998903274536, 3.369999885559082, 0 ];
	ssc.data_set_array( data, b'HCE_A6',  HCE_A6);
	ssc.data_set_number( data, b'TurbOutG', 111 )
	ssc.data_set_number( data, b'TurbEffG', 0.37740001082420349 )
	ssc.data_set_number( data, b'PTTMAX', 1.1499999761581421 )
	ssc.data_set_number( data, b'PTTMIN', 0.25 )
	ssc.data_set_number( data, b'MaxGrOut', 1.1499999761581421 )
	ssc.data_set_number( data, b'MinGrOut', 0.25 )
	ssc.data_set_number( data, b'TurSUE', 0.20000000298023224 )
	ssc.data_set_number( data, b'T2EPLF0', -0.03772599995136261 )
	ssc.data_set_number( data, b'T2EPLF1', 1.0061999559402466 )
	ssc.data_set_number( data, b'T2EPLF2', 0.076315999031066895 )
	ssc.data_set_number( data, b'T2EPLF3', -0.044775001704692841 )
	ssc.data_set_number( data, b'T2EPLF4', 0 )
	ssc.data_set_number( data, b'E2TPLF0', 0.037370000034570694 )
	ssc.data_set_number( data, b'E2TPLF1', 0.98822999000549316 )
	ssc.data_set_number( data, b'E2TPLF2', -0.064990997314453125 )
	ssc.data_set_number( data, b'E2TPLF3', 0.039388000965118408 )
	ssc.data_set_number( data, b'E2TPLF4', 0 )
	ssc.data_set_number( data, b'TempCorrF', 1 )
	ssc.data_set_number( data, b'TempCorr0', 1.0087300539016724 )
	ssc.data_set_number( data, b'TempCorr1', 0.0043584201484918594 )
	ssc.data_set_number( data, b'TempCorr2', -0.00025102301151491702 )
	ssc.data_set_number( data, b'TempCorr3', -9.0200001068296842e-07 )
	ssc.data_set_number( data, b'TempCorr4', 4.8200000435372203e-08 )
	ssc.data_set_number( data, b'LHVBoilEff', 0.89999997615814209 )
	ssc.data_set_number( data, b'TurTesEffAdj', 0.98500001430511475 )
	ssc.data_set_number( data, b'TurTesOutAdj', 0.99800002574920654 )
	ssc.data_set_number( data, b'TnkHL', 0.97000002861022949 )
	ssc.data_set_number( data, b'PTSmax', 294.11764526367188 )
	ssc.data_set_number( data, b'PFSmax', 297.9993896484375 )
	ssc.data_set_number( data, b'TSHOURS', 6 )
	ssc.data_set_number( data, b'NUMTOU', 9 )
	TSLogic = [[ 1,   0.10000000149011612,   0.10000000149011612,   1.0499999523162842 ], [ 2,   0.10000000149011612,   0.10000000149011612,   1 ], [ 3,   0.10000000149011612,   0.10000000149011612,   1 ], [ 4,   0.10000000149011612,   0.10000000149011612,   1 ], [ 5,   0.10000000149011612,   0.10000000149011612,   1 ], [ 6,   0.10000000149011612,   0.10000000149011612,   1 ], [ 7,   0.10000000149011612,   0.10000000149011612,   1 ], [ 8,   0.10000000149011612,   0.10000000149011612,   1 ], [ 9,   0.10000000149011612,   0.10000000149011612,   1 ]];
	ssc.data_set_matrix( data, b'TSLogic', TSLogic );
	FossilFill =[ 0, 0, 0, 0, 0, 0, 0, 0, 0 ];
	ssc.data_set_array( data, b'FossilFill',  FossilFill);
	ssc.data_set_number( data, b'E_tes_ini', 0 )
	ssc.data_set_number( data, b'SfPar', 0.22843222320079803 )
	ssc.data_set_number( data, b'SfParPF', 1 )
	ssc.data_set_number( data, b'ChtfPar', 9.0342369079589844 )
	ssc.data_set_number( data, b'ChtfParPF', 1 )
	ssc.data_set_number( data, b'CHTFParF0', -0.035999998450279236 )
	ssc.data_set_number( data, b'CHTFParF1', 0.24199999868869781 )
	ssc.data_set_number( data, b'CHTFParF2', 0.79400002956390381 )
	ssc.data_set_number( data, b'AntiFrPar', 0.9034237265586853 )
	ssc.data_set_number( data, b'BOPPar', 2.7383699417114258 )
	ssc.data_set_number( data, b'BOPParPF', 1 )
	ssc.data_set_number( data, b'BOPParF0', 0.4830000102519989 )
	ssc.data_set_number( data, b'BOPParF1', 0.51700001955032349 )
	ssc.data_set_number( data, b'BOPParF2', 0 )
	ssc.data_set_number( data, b'CtOpF', 1 )
	ssc.data_set_number( data, b'CtPar', 1.8919950723648071 )
	ssc.data_set_number( data, b'CtParPF', 1 )
	ssc.data_set_number( data, b'CtParF0', -0.035999998450279236 )
	ssc.data_set_number( data, b'CtParF1', 0.24199999868869781 )
	ssc.data_set_number( data, b'CtParF2', 0.79400002956390381 )
	ssc.data_set_number( data, b'HtrPar', 2.5230300426483154 )
	ssc.data_set_number( data, b'HtrParPF', 1 )
	ssc.data_set_number( data, b'HtrParF0', 0.4830000102519989 )
	ssc.data_set_number( data, b'HtrParF1', 0.51700001955032349 )
	ssc.data_set_number( data, b'HtrParF2', 0 )
	ssc.data_set_number( data, b'HhtfPar', 2.2200000286102295 )
	ssc.data_set_number( data, b'HhtfParPF', 1 )
	ssc.data_set_number( data, b'HhtfParF0', -0.035999998450279236 )
	ssc.data_set_number( data, b'HhtfParF1', 0.24199999868869781 )
	ssc.data_set_number( data, b'HhtfParF2', 0.79400002956390381 )
	ssc.data_set_number( data, b'PbFixPar', 0.61049997806549072 )
	ssc.data_set_number( data, b'adjust:constant', 4 )
	module = ssc.module_create(b'tcstrough_empirical')	
	ssc.module_exec_set_print( 0 );
	if ssc.module_exec(module, data) == 0:
		print ('tcstrough_empirical simulation error')
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
	ssc.data_free(data);