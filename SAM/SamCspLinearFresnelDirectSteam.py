"""
Generates annual hourly simulations for variables including but not limited to
    - Field thermal power produced
    - Field steam mass flow rate
    - Cycle electrical power output (net/gross)
    - Condenser pressure
    - Capacity factor

For a full list of available output variables please refer the documentation for
    Linear Fresnel direct steam model (tcslinear_fresnel) of NREL's System 
    Advisor Model software development kit.
    
Simulating desalination with wrapper from SAM for Linear Fresnel Direct Steam 
	+ Partnership flip with debt (variables to be included)
    

Created by: Vikas Vicraman
Create date: 11/22/2018

V1: - Wrapper from SAM v11.11
    Modified by: Vikas Vicraman
    Modified date: 11/14/2018
    - Added function for ssc.data_free

V2: Modular version of the wrapper
    Modified by: Vikas Vicraman
    Modified date: 3/17/2019 
    - Created different methods for variables belonging to each sub-group on UI 
          for different tabs
    - Assigning different default variable values for all variables in the methods
    - Used sys.argv so that the script can be executed directly from command prompt
    - Added placeholders for implementing logger and unit tests
   

"""
#import Model_MED_PSA as model
from SAM.PySSC import PySSC
import os, sys
import argparse
import logging
import unittest

        
class samCspLinearFresnelDirectSteam(object):
    
    def __init__(self):
        """
        Methods for setting up logger, unit testing and creating the ssc module 
        go here.
        """

        
        self.ssc = PySSC()
        
        print ('SSC Version = ', self.ssc.version())
        print ('SSC Build Information = ', self.ssc.build_info().decode("utf - 8"))
        
        #Initializes all the variables to default values if the class is called 
        #    from other classes
        if __name__ != '__main__':
            self.main()


    #Logger - to be implemented  
    def _setup_logging(verbose=False):
        if verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO

        frmt = '%(asctime)s %(levelname)s %(message)s'
        logging.basicConfig(
            stream=sys.stderr,
            level=level,
            format=frmt,
        )
    
    def main(self):
             
        """
        Main method gets initialized when the file is run on its own with default
            value for system_capacity = 50000 MWe. This method can also be 
            called from command line with the system_capacity parameter as inline 
            system argument. This argument takes numeric values.
        
        :param system_capacity Nameplate capacity: [kW]  Type: SSC_NUMBER
        """
        # Logger lines goes below - to be implemented
        """
        parser = argparse.ArgumentParser(description='Initializing samCspLinearFresnelDirectSteam.py method')
        parser.add_argument('house_location_file', help='Path to CSV file with house locations.')  # noqa
        #parser.add_argument('-n', '--num-workers', type=int, default=DEFAULT_PROCS, help='Number of procs to use.  Default {}'.format(DEFAULT_PROCS))  # noqa
        parser.add_argument('-v', '--verbose', action='store_true', help='Log more verbosely.')  # noqa
        args = parser.parse_args()
        self._setup_logging(args.verbose)
        logging.debug('ARGS: {}'.format(args))
        """       
        #test = sys.argv[0]
        print('File nmae = ', sys.argv[0])#, sys.argv[1])
        if len(sys.argv) == 2:
            system_capacity = float(sys.argv[1])
        else:           
            # Setting default value as 50000
            system_capacity = 50000
        print("System Capacity = " , system_capacity)

        #Creating SAM data and ssc modules. Parsing different default variables for all the different parameters.            
        self.create_ssc_module()
        self.weather()
        self.linear_fresnel(system_capacity = system_capacity)     
        self.tou_translator()
        self.solarField_steamCondnAtDesign()
        self.heliostat()
        self.module_create_execute()
        
        #Clears the ssc data if the module is executed on its own.
        if __name__ == '__main__':
            self.data_clear()


    def create_ssc_module(self):
        # Logging methods goes here
        """
        parser = argparse.ArgumentParser(description='Creating the ssc module of System Advisor model')
        #parser.add_argument('house_location_file',
        #                    help='Path to CSV file with house locations.')  
        #parser.add_argument('-n', '--num-workers', type=int, default=DEFAULT_PROCS,
        #    help='Number of procs to use.  Default {}'.format(DEFAULT_PROCS))  # noqa
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='Log more verbosely.')  # noqa
        args = parser.parse_args()
        #self._setup_logging(args.verbose)
        logging.debug('ARGS: {}'.format(args))
        """
        
        self.ssc.module_exec_set_print(0)
        self.data = self.ssc.data_create()
        
    # Tab title : Location and Resource
    def weather(self
                , file_name = os.path.dirname(os.path.realpath(__file__)) + "/solar_resource/United Arab Emirates ARE Abu_Dhabi (INTL).csv"
                , track_mode = 1
                , tilt = 0
                , azimuth = 0):
        """
        Initializes the weather file csv and assigns different variables to the parameters on the Location and Resource
            tab of System Advisor Model.
        
	    :param file_name local weather file path: []  Type: SSC_STRING    Constraint: LOCAL_FILE
	    :param track_mode Tracking mode: []  Type: SSC_NUMBER
	    :param tilt Tilt angle of surface/axis: []  Type: SSC_NUMBER
	    :param azimuth Azimuth angle of surface/axis: []  Type: SSC_NUMBER

        """
        #print(file_name)
        self.ssc.data_set_string( self.data, b'file_name', b''+file_name.encode("ascii", "backslashreplace")) #Giving input as binary string
        self.ssc.data_set_number( self.data, b'track_mode',  track_mode)
        self.ssc.data_set_number( self.data, b'tilt', tilt )
        self.ssc.data_set_number( self.data, b'azimuth', azimuth )
        
    # Tab title: Power Cycle
    def linear_fresnel(self, system_capacity = 50000):
        """
        Assigns the System capacity for the system under consideration. Assigns the 
            variable to sam.data.
	    :param system_capacity Nameplate capacity: [kW]  Type: SSC_NUMBER
        """
        
        self.ssc.data_set_number( self.data, b'system_capacity', system_capacity ) #50000.94921875 )
       
	# Tab title: Thermal Storage
    def tou_translator(self, 
                       weekday_schedule = [[ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ]],
                       weekend_schedule = [[ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ]]):
        """
        Assigns Time of Use translator as a 12x24 array for week days. For understanding 
            this array implementation, please see the Linear Fresnel Direct Steam ->
            Power Cycle -> Dispatch Control -> Weekday/Weekend schedule section of SAM.
            
		:param weekday_schedule 12x24 Time of Use Values for week days: []  Type: SSC_MATRIX
		:param weekend_schedule 12x24 Time of Use Values for week end days: []  Type: SSC_MATRIX
		"""
        self.ssc.data_set_matrix( self.data, b'weekday_schedule', weekday_schedule );
        self.ssc.data_set_matrix( self.data, b'weekend_schedule', weekend_schedule );
		
    # Tab : Solar Field; Section : Steam Conditions at Design; Sub Section: 
    def solarField_steamCondnAtDesign (self
                                       , x_b_des = 0.75
                                       , fP_hdr_c = 0.0099999997764825821
                                       , fP_sf_boil = 0.075000002980232239
                                       , fP_boil_to_sh =  0.004999999888241291
                                       , fP_sf_sh = 0.05000000074505806 
                                       , fP_hdr_h = 0.02500000037252903
                                       , P_boil_des = 110
                                       , T_hot = 440) :
        """
        Assigns default or user-specified values to the fields under Tab : Solar Field; 
            Section : Steam Conditions at Design for Linear Fresnel Direct Steam 
            model of SAM.
            
        :param x_b_des Design point boiler outlet steam quality: [none]  Type: SSC_NUMBER
        :param fP_hdr_c Average design-point cold header pressure drop fraction: [none]  Type: SSC_NUMBER
        :param fP_sf_boil Design-point pressure drop across the solar field boiler fraction: [none]  Type: SSC_NUMBER
        :param fP_boil_to_sh Design-point pressure drop between the boiler and superheater frac: [none]  Type: SSC_NUMBER
        :param fP_sf_sh Design-point pressure drop across the solar field superheater frac: [none]  Type: SSC_NUMBER
        :param fP_hdr_h Average design-point hot header pressure drop fraction: [none]  Type: SSC_NUMBER
        :param P_boil_des Boiler operating pressure @ design: [bar]  Type: SSC_NUMBER
        :param T_hot Hot HTF inlet temperature, from storage tank: [C]  Type: SSC_NUMBER
        """
        self.ssc.data_set_number( self.data, b'x_b_des', x_b_des )
        self.ssc.data_set_number( self.data, b'fP_hdr_c',  fP_hdr_c)
        self.ssc.data_set_number( self.data, b'fP_sf_boil', fP_sf_boil )
        self.ssc.data_set_number( self.data, b'fP_boil_to_sh', fP_boil_to_sh)
        self.ssc.data_set_number( self.data, b'fP_sf_sh', fP_sf_sh)
        self.ssc.data_set_number( self.data, b'fP_hdr_h', fP_hdr_h )
        self.ssc.data_set_number( self.data, b'P_boil_des', P_boil_des )
        self.ssc.data_set_number( self.data, b'T_hot', T_hot )
        
    def heliostat(self
                  , water_per_wash = 0.019999999552965164
                  , washes_per_year = 120):
        """
        #:param csp.lf.sf.water_per_wash Water usage per wash: [L/m2_aper]  Type: SSC_NUMBER
        #:param csp.lf.sf.washes_per_year Mirror washing frequency: []  Type: SSC_NUMBER

        """
        # Section title: Mirror washing
        self.ssc.data_set_number( self.data, b'csp.lf.sf.water_per_wash', water_per_wash )
        self.ssc.data_set_number( self.data, b'csp.lf.sf.washes_per_year',  washes_per_year)
    
        #The methods for the following variables yet to be written.
        self.ssc.data_set_number( self.data, b'tes_hours', 0 )
        self.ssc.data_set_number( self.data, b'q_max_aux', 255.63600158691406 )
        self.ssc.data_set_number( self.data, b'LHV_eff', 0.89999997615814209 ) 
        self.ssc.data_set_number( self.data, b'x_b_des', 0.75 )
        self.ssc.data_set_number( self.data, b'P_turb_des', 110 )
        self.ssc.data_set_number( self.data, b'fP_hdr_c', 0.0099999997764825821 )
        self.ssc.data_set_number( self.data, b'fP_sf_boil', 0.075000002980232239 )
        #ssc.data_set_number( data, b'fP_boil_to_sh', 0.004999999888241291 )
        #ssc.data_set_number( data, b'fP_sf_sh', 0.05000000074505806 )
        #ssc.data_set_number( data, b'fP_hdr_h', 0.02500000037252903 )
        self.ssc.data_set_number( self.data, b'q_pb_des', 143.37602233886719 )
        self.ssc.data_set_number( self.data, b'cycle_max_fraction', 1.0499999523162842 )
        self.ssc.data_set_number( self.data, b'cycle_cutoff_frac', 0.20000000298023224 )
        self.ssc.data_set_number( self.data, b't_sby', 2 )
        self.ssc.data_set_number( self.data, b'q_sby_frac', 0.20000000298023224 )
        self.ssc.data_set_number( self.data, b'solarm', 1.7999999523162842 )
        self.ssc.data_set_number( self.data, b'PB_pump_coef', 0 )
        self.ssc.data_set_number( self.data, b'PB_fixed_par', 0.0054999999701976776 )
        bop_array =[ 0, 1, 0.4830000102519989, 0.57099997997283936, 0 ];
        self.ssc.data_set_array( self.data, b'bop_array',  bop_array);
        aux_array =[ 0.023000000044703484, 1, 0.4830000102519989, 0.57099997997283936, 0 ];
        self.ssc.data_set_array( self.data, b'aux_array',  aux_array);
        self.ssc.data_set_number( self.data, b'fossil_mode', 1 )
        self.ssc.data_set_number( self.data, b'I_bn_des', 950 )
        self.ssc.data_set_number( self.data, b'is_sh', 1 )
        self.ssc.data_set_number( self.data, b'is_oncethru', 0 )
        self.ssc.data_set_number( self.data, b'is_multgeom', 1 )
        self.ssc.data_set_number( self.data, b'nModBoil', 12 )
        self.ssc.data_set_number( self.data, b'nModSH', 4 )
        self.ssc.data_set_number( self.data, b'nLoops', 53 )
        self.ssc.data_set_number( self.data, b'eta_pump', 0.85000002384185791 )
        self.ssc.data_set_number( self.data, b'latitude', 32.130001068115234 )
        self.ssc.data_set_number( self.data, b'theta_stow', 10 )
        self.ssc.data_set_number( self.data, b'theta_dep', 10 )
        self.ssc.data_set_number( self.data, b'm_dot_min', 0.05000000074505806 )
        self.ssc.data_set_number( self.data, b'T_fp', 10 )
        self.ssc.data_set_number( self.data, b'Pipe_hl_coef', 0.0035000001080334187 )
        self.ssc.data_set_number( self.data, b'SCA_drives_elec', 0.20000000298023224 )
        self.ssc.data_set_number( self.data, b'ColAz', 0 )
        self.ssc.data_set_number( self.data, b'e_startup', 2.7000000476837158 )
        self.ssc.data_set_number( self.data, b'T_amb_des_sf', 42 )
        self.ssc.data_set_number( self.data, b'V_wind_max', 20 )
       
    # Tab title: Solar Field    
        
        ffrac =[ 0, 0, 0, 0, 0, 0, 0, 0, 0 ];
        self.ssc.data_set_array( self.data, b'ffrac',  ffrac);
        A_aperture = [[ 513.5999755859375 ], [ 513.5999755859375 ]];
        self.ssc.data_set_matrix( self.data, b'A_aperture', A_aperture );
        L_col = [[ 44.799999237060547 ], [ 44.799999237060547 ]];
        self.ssc.data_set_matrix( self.data, b'L_col', L_col );
        OptCharType = [[ 1 ], [ 1 ]];
        self.ssc.data_set_matrix( self.data, b'OptCharType', OptCharType );
        IAM_T = [[ 0.98960000276565552,   0.043999999761581421,   -0.072099998593330383,   -0.23270000517368317,   0 ], [ 0.98960000276565552,   0.043999999761581421,   -0.072099998593330383,   -0.23270000517368317,   0 ]];
        self.ssc.data_set_matrix( self.data, b'IAM_T', IAM_T );
        IAM_L = [[ 1.0031000375747681,   -0.22589999437332153,   0.53680002689361572,   -1.6433999538421631,   0.72219997644424438 ], [ 1.0031000375747681,   -0.22589999437332153,   0.53680002689361572,   -1.6433999538421631,   0.72219997644424438 ]];
        self.ssc.data_set_matrix( self.data, b'IAM_L', IAM_L );
        TrackingError = [[ 1 ], [ 1 ]];
        self.ssc.data_set_matrix( self.data, b'TrackingError', TrackingError );
        GeomEffects = [[ 0.72399997711181641 ], [ 0.72399997711181641 ]];
        self.ssc.data_set_matrix( self.data, b'GeomEffects', GeomEffects );
        rho_mirror_clean = [[ 0.93500000238418579 ], [ 0.93500000238418579 ]];
        self.ssc.data_set_matrix( self.data, b'rho_mirror_clean', rho_mirror_clean );
        dirt_mirror = [[ 0.94999998807907104 ], [ 0.94999998807907104 ]];
        self.ssc.data_set_matrix( self.data, b'dirt_mirror', dirt_mirror );
        error = [[ 1 ], [ 1 ]];
        self.ssc.data_set_matrix( self.data, b'error', error );
        HLCharType = [[ 1 ], [ 1 ]];
        self.ssc.data_set_matrix( self.data, b'HLCharType', HLCharType );
        HL_dT = [[ 0,   0.67199999094009399,   0.0025559999048709869,   0,   0 ], [ 0,   0.67199999094009399,   0.0025559999048709869,   0,   0 ]];
        self.ssc.data_set_matrix( self.data, b'HL_dT', HL_dT );
        HL_W = [[ 1,   0,   0,   0,   0 ], [ 1,   0,   0,   0,   0 ]];
        self.ssc.data_set_matrix( self.data, b'HL_W', HL_W );
        D_2 = [[ 0.065999999642372131 ], [ 0.065999999642372131 ]];
        self.ssc.data_set_matrix( self.data, b'D_2', D_2 );
        D_3 = [[ 0.070000000298023224 ], [ 0.070000000298023224 ]];
        self.ssc.data_set_matrix( self.data, b'D_3', D_3 );
        D_4 = [[ 0.11500000208616257 ], [ 0.11500000208616257 ]];
        self.ssc.data_set_matrix( self.data, b'D_4', D_4 );
        D_5 = [[ 0.11999999731779099 ], [ 0.11999999731779099 ]];
        self.ssc.data_set_matrix( self.data, b'D_5', D_5 );
        D_p = [[ 0 ], [ 0 ]];
        self.ssc.data_set_matrix( self.data, b'D_p', D_p );
        Rough = [[ 4.5000000682193786e-05 ], [ 4.5000000682193786e-05 ]];
        self.ssc.data_set_matrix( self.data, b'Rough', Rough );
        Flow_type = [[ 1 ], [ 1 ]];
        self.ssc.data_set_matrix( self.data, b'Flow_type', Flow_type );
        AbsorberMaterial = [[ 1 ], [ 1 ]];
        self.ssc.data_set_matrix( self.data, b'AbsorberMaterial', AbsorberMaterial );
        HCE_FieldFrac = [[ 0.98500001430511475,   0.0099999997764825821,   0.004999999888241291,   0 ], [ 0.98500001430511475,   0.0099999997764825821,   0.004999999888241291,   0 ]];
        self.ssc.data_set_matrix( self.data, b'HCE_FieldFrac', HCE_FieldFrac );
        alpha_abs = [[ 0.95999997854232788,   0.95999997854232788,   0.80000001192092896,   0 ], [ 0.95999997854232788,   0.95999997854232788,   0.80000001192092896,   0 ]];
        self.ssc.data_set_matrix( self.data, b'alpha_abs', alpha_abs );
        b_eps_HCE1 = [[ 0 ], [ 0.13840000331401825 ]];
        self.ssc.data_set_matrix( self.data, b'b_eps_HCE1', b_eps_HCE1 );
        b_eps_HCE2 = [[ 0 ], [ 0.64999997615814209 ]];
        self.ssc.data_set_matrix( self.data, b'b_eps_HCE2', b_eps_HCE2 );
        b_eps_HCE3 = [[ 0 ], [ 0.64999997615814209 ]];
        self.ssc.data_set_matrix( self.data, b'b_eps_HCE3', b_eps_HCE3 );
        b_eps_HCE4 = [[ 0 ], [ 0.13840000331401825 ]];
        self.ssc.data_set_matrix( self.data, b'b_eps_HCE4', b_eps_HCE4 );
        sh_eps_HCE1 = [[ 0 ], [ 0.13840000331401825 ]];
        self.ssc.data_set_matrix( self.data, b'sh_eps_HCE1', sh_eps_HCE1 );
        sh_eps_HCE2 = [[ 0 ], [ 0.64999997615814209 ]];
        self.ssc.data_set_matrix( self.data, b'sh_eps_HCE2', sh_eps_HCE2 );
        sh_eps_HCE3 = [[ 0 ], [ 0.64999997615814209 ]];
        self.ssc.data_set_matrix( self.data, b'sh_eps_HCE3', sh_eps_HCE3 );
        sh_eps_HCE4 = [[ 0 ], [ 0.13840000331401825 ]];
        self.ssc.data_set_matrix( self.data, b'sh_eps_HCE4', sh_eps_HCE4 );
        alpha_env = [[ 0.019999999552965164,   0.019999999552965164,   0,   0 ], [ 0.019999999552965164,   0.019999999552965164,   0,   0 ]];
        self.ssc.data_set_matrix( self.data, b'alpha_env', alpha_env );
        EPSILON_4 = [[ 0.86000001430511475,   0.86000001430511475,   1,   0 ], [ 0.86000001430511475,   0.86000001430511475,   1,   0 ]];
        self.ssc.data_set_matrix( self.data, b'EPSILON_4', EPSILON_4 );
        Tau_envelope = [[ 0.96299999952316284,   0.96299999952316284,   1,   0 ], [ 0.96299999952316284,   0.96299999952316284,   1,   0 ]];
        self.ssc.data_set_matrix( self.data, b'Tau_envelope', Tau_envelope );
        GlazingIntactIn = [[ 1,   1,   0,   1 ], [ 1,   1,   0,   1 ]];
        self.ssc.data_set_matrix( self.data, b'GlazingIntactIn', GlazingIntactIn );
        AnnulusGas = [[ 27,   1,   1,   1 ], [ 27,   1,   1,   1 ]];
        self.ssc.data_set_matrix( self.data, b'AnnulusGas', AnnulusGas );
        P_a = [[ 9.9999997473787516e-05,   750,   750,   0 ], [ 9.9999997473787516e-05,   750,   750,   0 ]];
        self.ssc.data_set_matrix( self.data, b'P_a', P_a );
        Design_loss = [[ 150,   1100,   1500,   0 ], [ 150,   1100,   1500,   0 ]];
        self.ssc.data_set_matrix( self.data, b'Design_loss', Design_loss );
        Shadowing = [[ 0.95999997854232788,   0.95999997854232788,   0.95999997854232788,   0 ], [ 0.95999997854232788,   0.95999997854232788,   0.95999997854232788,   0 ]];
        self.ssc.data_set_matrix( self.data, b'Shadowing', Shadowing );
        Dirt_HCE = [[ 0.98000001907348633,   0.98000001907348633,   1,   0 ], [ 0.98000001907348633,   0.98000001907348633,   1,   0 ]];
        self.ssc.data_set_matrix( self.data, b'Dirt_HCE', Dirt_HCE );
        b_OpticalTable = [[ -180,   -160,   -140,   -120,   -100,   -80,   -60,   -40,   -20,   0,   20,   40,   60,   80,   100,   120,   140,   160,   180,   -999.9000244140625 ], [ 0,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1 ], [ 10,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633 ], [ 20,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737 ], [ 30,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563 ], [ 40,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949 ], [ 50,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896 ], [ 60,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869 ], [ 70,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842 ], [ 80,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821 ], [ 90,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0 ]];
        self.ssc.data_set_matrix( self.data, b'b_OpticalTable', b_OpticalTable );
        sh_OpticalTable = [[ -180,   -160,   -140,   -120,   -100,   -80,   -60,   -40,   -20,   0,   20,   40,   60,   80,   100,   120,   140,   160,   180,   -999.9000244140625 ], [ 0,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1 ], [ 10,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633 ], [ 20,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737 ], [ 30,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563 ], [ 40,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949 ], [ 50,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896 ], [ 60,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869 ], [ 70,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842 ], [ 80,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821 ]];
        self.ssc.data_set_matrix( self.data, b'sh_OpticalTable', sh_OpticalTable );
        self.ssc.data_set_number( self.data, b'dnifc', 0 )
        self.ssc.data_set_number( self.data, b'I_bn', 0 )
        self.ssc.data_set_number( self.data, b'T_db', 15 )
        self.ssc.data_set_number( self.data, b'T_dp', 10 )
        self.ssc.data_set_number( self.data, b'P_amb', 930.5 )
        self.ssc.data_set_number( self.data, b'V_wind', 0 )
        self.ssc.data_set_number( self.data, b'm_dot_htf_ref', 0 )
        self.ssc.data_set_number( self.data, b'm_pb_demand', 0 )
        self.ssc.data_set_number( self.data, b'shift', 0 )
        self.ssc.data_set_number( self.data, b'SolarAz_init', 0 )
        self.ssc.data_set_number( self.data, b'SolarZen', 0 )
        self.ssc.data_set_number( self.data, b'T_pb_out_init', 290 )
        self.ssc.data_set_number( self.data, b'eta_ref', 0.37099999189376831 )
        self.ssc.data_set_number( self.data, b'T_cold_ref', 230 )
        self.ssc.data_set_number( self.data, b'dT_cw_ref', 10 )
        self.ssc.data_set_number( self.data, b'T_amb_des', 42 )
        #ssc.data_set_number( data, b'P_boil_des', 110 )
        self.ssc.data_set_number( self.data, b'P_rh_ref', 0 )
        self.ssc.data_set_number( self.data, b'rh_frac_ref', 0 )
        self.ssc.data_set_number( self.data, b'CT', 2 )
        self.ssc.data_set_number( self.data, b'startup_time', 0.34999999403953552 )
        self.ssc.data_set_number( self.data, b'startup_frac', 0.34999999403953552 )
        self.ssc.data_set_number( self.data, b'T_approach', 5 )
        self.ssc.data_set_number( self.data, b'T_ITD_des', 40) #16 )
        self.ssc.data_set_number( self.data, b'P_cond_ratio', 1.0027999877929688 )
        self.ssc.data_set_number( self.data, b'pb_bd_frac', 0.019999999552965164 )
        self.ssc.data_set_number( self.data, b'P_cond_min', 1.25 )
        self.ssc.data_set_number( self.data, b'n_pl_inc', 8 )
        F_wc =[ 0, 0, 0, 0, 0, 0, 0, 0, 0 ];
        self.ssc.data_set_array( self.data, b'F_wc',  F_wc);
        self.ssc.data_set_number( self.data, b'pc_mode', 1 )
        #ssc.data_set_number( data, b'T_hot', 440 )
        self.ssc.data_set_number( self.data, b'm_dot_st', 0 )
        self.ssc.data_set_number( self.data, b'T_wb', 12.800000190734863 )
        self.ssc.data_set_number( self.data, b'demand_var', 53.192501068115234 )
        self.ssc.data_set_number( self.data, b'standby_control', 0 )
        self.ssc.data_set_number( self.data, b'T_db_pwb', 12.800000190734863 )
        self.ssc.data_set_number( self.data, b'P_amb_pwb', 960 )
        self.ssc.data_set_number( self.data, b'relhum', 0.25 )
        self.ssc.data_set_number( self.data, b'f_recSU', 1 )
        self.ssc.data_set_number( self.data, b'dp_b', 0 )
        self.ssc.data_set_number( self.data, b'dp_sh', 5 )
        self.ssc.data_set_number( self.data, b'dp_rh', 0 )
        self.ssc.data_set_number( self.data, b'adjust:constant', 4 )

    #Executes the SAM module after all variables are initialized
    def module_create_execute(self):
        module = self.ssc.module_create(b'tcslinear_fresnel')	
        self.ssc.module_exec_set_print( 0 );
        if self.ssc.module_exec(module, self.data) == 0:
            print ('tcslinear_fresnel simulation error')
            idx = 1
            msg = self.ssc.module_log(module, 0)
            while (msg != None):
                print ('	: ' + msg.decode("utf - 8"))
                msg = self.ssc.module_log(module, idx)
                idx = idx + 1
            SystemExit( "Simulation Error" );
            self.ssc.module_free(module)
        self.ssc.module_free(module)

        capacity_factor = self.ssc.data_get_number(self.data, b'capacity_factor');
        print ('\nCapacity factor (year 1) = ', capacity_factor)
#        annual_total_water_use = self.ssc.data_get_number(self.data, b'annual_total_water_use');
#        print ('Annual Water Usage = ', annual_total_water_use)
    
    #Clears the ssc data
    def data_clear(self):
        self.ssc.data_clear(self.data)
        
        
#To be implemented - Unit test cases for the method    
class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
            
if __name__ == '__main__':
    sam = samCspLinearFresnelDirectSteam()
    sam.main()
    
    #Argument for the unit test makes sure the unit test does not fail if system_capacity 
    #system_capacity is passed as a first argument on command line.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
 