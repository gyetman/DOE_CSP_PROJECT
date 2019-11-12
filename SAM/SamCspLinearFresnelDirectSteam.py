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
    - Added method for ssc.data_free

V2: Modular version of the wrapper
    Modified by: Vikas Vicraman
    Modified date: 3/17/2019 
    - Created different methods for variables belonging to each sub-group on UI 
          for different tabs
    - Assigning different default variable values for all variables in the methods
    - Used sys.argv so that the script can be executed directly from command prompt
    - Added placeholders for implementing logger and unit tests
   
"""

from SAM.PySSC import PySSC
from SAM.SamBaseClass import SamBaseClass
import os, sys
import argparse
import unittest
from SAM.SamFinPpaPartnershipFlipWithDebt import  samFinPpaPartnershipFlipWithDebt as finPPFWD

     
class samCspLinearFresnelDirectSteam(SamBaseClass):
    
    def __init__(self):
        
        #Initializes all the variables to default values if the class is called 
        #    from other classes
        if __name__ != '__main__':
            self.main()
            #unittest.main(argv=['first-arg-is-ignored'], exit=False)

    
    def main(self):
             
        """
        Main method gets initialized when the file is run on its own with default
            value for system_capacity = 50000 MWe. This method can also be 
            called from command line with the system_capacity parameter as inline 
            system argument. This argument takes numeric values.
        
        :param system_capacity Nameplate capacity: [kW]  Type: SSC_NUMBER
        """
        try:
            # Logger lines goes below - from Base class
            SamBaseClass._setup_logging(SamBaseClass, 'samCspLinearFresnelDirectSteam')
            SamBaseClass.logger.debug('Running SAM Linear Fresnel Direct Steam with Partnership Flip with Debt')

            print('File nmae = ', sys.argv[0])#, sys.argv[1])
            if len(sys.argv) == 2:
                system_capacity = float(sys.argv[1])
            else:           
                # Setting default value as 50000
                system_capacity = 50000
            print("System Capacity = " , system_capacity)
        
            #Creating SAM data and ssc modules. 
            self.data = SamBaseClass.create_ssc_module(SamBaseClass)
        
            #Parsing different default or UI input values for all the different parameters.
            self.locationResouce_weatherDataInf()
        
        
            self.solarField_steamCondnAtDesign()
            self.solarFiled_mirrorWash()
            self.solarField_solarFieldParams()
            self.solarField_designPoint()
            self.solarField_fieldControl()
        
        
            self.powerCycle_plantCoolingMode()
            self.powerCycle_plantDesign(system_capacity = system_capacity)
            self.powerCycle_operation()
            self.powerCycle_availAndCurtailment()
            self.powerCycle_dispatchControl()
            self.powerCycle_dispatchControl()
        
        
            self.collectorReceiver_BoilerGeomOptPerf()
            self.collectorReceiver_IncAngModifiers()
            self.collectorReceiver_receiverGeomHeatLoss()
            self.collectorReceiver_receiverGeomHeatLoss_evacTubeHeatLoss()
            self.collectorReceiver_receiverGeomHeatLoss_PolyFitHeatLossModel()
        
        
            self.parasitics()
            self.remainingParams()
        
            #Executes the module and creates annual hourly simulations
            SamBaseClass.module_create_execute(SamBaseClass, 'tcslinear_fresnel', self.ssc, self.data)
        
            self.print_impParams()
            finModel = finPPFWD(SamBaseClass)

            #Variables for unit tests

            self.test_capacity_factor = self.ssc.data_get_number(self.data, b'capacity_factor');
        
            SamBaseClass.data_free(SamBaseClass)
        except Exception:
            SamBaseClass.logger.critical("Error in executing SAM Linear Fresnel Direct Steam Model.", exc_info=True)

    # Tab title : Location and Resource
    def locationResouce_weatherDataInf(self
                , file_name = os.path.dirname(os.path.realpath(__file__)) + "/solar_resource/United Arab Emirates ARE Abu_Dhabi (INTL).csv"
                , track_mode = 1
                , tilt = 0
                , azimuth = 0
                , latitude = 32.130001068115234
                ) :
        """
        Assigns default or user-specified values to the fields under Tab : Location and Resource; 
            Section : Weather Data Information for Linear Fresnel Direct Steam model of SAM.
        
        :param latitude Site latitude resource page: [deg]  Type: SSC_NUMBER
	    :param file_name local weather file path: []  Type: SSC_STRING    Constraint: LOCAL_FILE
	    :param track_mode Tracking mode: []  Type: SSC_NUMBER
	    :param tilt Tilt angle of surface/axis: []  Type: SSC_NUMBER
	    :param azimuth Azimuth angle of surface/axis: []  Type: SSC_NUMBER

        """
        SamBaseClass.logger.debug("Setting values for Tab: Location and Resource, Section: Weather data information.")
        self.ssc.data_set_string( self.data, b'file_name', b''+file_name.encode("ascii", "backslashreplace")) #Giving input as binary string
        self.ssc.data_set_number( self.data, b'track_mode',  track_mode)
        self.ssc.data_set_number( self.data, b'tilt', tilt )
        self.ssc.data_set_number( self.data, b'azimuth', azimuth )
        self.ssc.data_set_number( self.data, b'latitude', latitude )
        
    


    # Tab : Solar Field; Section : Steam Conditions at Design; Sub Section: 
    def solarField_steamCondnAtDesign (self
                                       , x_b_des = 0.75
                                       , fP_hdr_c = 0.0099999997764825821
                                       , fP_sf_boil = 0.075000002980232239
                                       , fP_boil_to_sh =  0.004999999888241291
                                       , fP_sf_sh = 0.05000000074505806 
                                       , fP_hdr_h = 0.02500000037252903
                                       , P_boil_des = 110
                                       , T_hot = 440
                                       ) :
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
        SamBaseClass.logger.debug("Setting values for Tab : Solar Field; Section : Steam Conditions at Design.")
        self.ssc.data_set_number( self.data, b'x_b_des', x_b_des )
        self.ssc.data_set_number( self.data, b'fP_hdr_c',  fP_hdr_c)
        self.ssc.data_set_number( self.data, b'fP_sf_boil', fP_sf_boil )
        self.ssc.data_set_number( self.data, b'fP_boil_to_sh', fP_boil_to_sh)
        self.ssc.data_set_number( self.data, b'fP_sf_sh', fP_sf_sh)
        self.ssc.data_set_number( self.data, b'fP_hdr_h', fP_hdr_h )
        self.ssc.data_set_number( self.data, b'P_boil_des', P_boil_des )
        self.ssc.data_set_number( self.data, b'T_hot', T_hot )
        
    def solarFiled_mirrorWash(self
                  , water_per_wash = 0.019999999552965164
                  , washes_per_year = 120
                  ) :
        """
        #:param csp.lf.sf.water_per_wash Water usage per wash: [L/m2_aper]  Type: SSC_NUMBER
        #:param csp.lf.sf.washes_per_year Mirror washing frequency: []  Type: SSC_NUMBER

        """
        SamBaseClass.logger.debug("Setting values for Tab : Solar Field; Section : Mirror Washing.")
        self.ssc.data_set_number( self.data, b'csp.lf.sf.water_per_wash', water_per_wash )
        self.ssc.data_set_number( self.data, b'csp.lf.sf.washes_per_year',  washes_per_year)

    # Tab : Solar Field; Section : Steam Conditions at Design; Sub Section: 
    def solarField_solarFieldParams (self
                                       , solarm = 1.7999999523162842
                                       , I_bn_des = 950
                                       , is_oncethru = 0
                                       , is_multgeom = 1
                                       , nModBoil = 12
                                       , nModSH = 4
                                       , eta_pump = 0.85000002384185791
                                       , ColAz = 0
                                       , e_startup = 2.7000000476837158
                                       , T_amb_des_sf = 42
                                       ) :
        """
        Assigns default or user-specified values to the fields under Tab : Solar Field; 
            Section : Solar Field Parameters for Linear Fresnel Direct Steam 
            model of SAM.
            
        :param solarm Solar multiple: [none]  Type: SSC_NUMBER
        :param I_bn_des Design point irradiation value: [W/m2]  Type: SSC_NUMBER
        :param is_oncethru Flag indicating whether flow is once through with superheat: [none]  Type: SSC_NUMBER    Constraint: INTEGER
        :param is_multgeom Does the superheater have a different geometry from the boiler {1=yes}: [none]  Type: SSC_NUMBER    Constraint: INTEGER
        :param nModBoil Number of modules in the boiler section: [none]  Type: SSC_NUMBER    Constraint: INTEGER
        :param nModSH Number of modules in the superheater section: [none]  Type: SSC_NUMBER    Constraint: INTEGER
        :param eta_pump Feedwater pump efficiency: [none]  Type: SSC_NUMBER
        :param ColAz Collector azimuth angle: [deg]  Type: SSC_NUMBER
        :param e_startup Thermal inertia contribution per sq meter of solar field: [kJ/K-m2]  Type: SSC_NUMBER
        :param T_amb_des_sf Design-point ambient temperature: [C]  Type: SSC_NUMBER
        """
        SamBaseClass.logger.debug("Setting values for Tab : Solar Field; Section : Solar Field Parameters.")
        self.ssc.data_set_number( self.data, b'solarm', solarm )
        self.ssc.data_set_number( self.data, b'I_bn_des',  I_bn_des)
        self.ssc.data_set_number( self.data, b'is_oncethru',  is_oncethru)
        self.ssc.data_set_number( self.data, b'is_multgeom',  is_multgeom)
        self.ssc.data_set_number( self.data, b'nModBoil', nModBoil )
        self.ssc.data_set_number( self.data, b'nModSH', nModSH )
        self.ssc.data_set_number( self.data, b'eta_pump', eta_pump )
        self.ssc.data_set_number( self.data, b'ColAz', ColAz )
        self.ssc.data_set_number( self.data, b'e_startup', e_startup )
        self.ssc.data_set_number( self.data, b'T_amb_des_sf', T_amb_des_sf )
        
    def solarField_designPoint(self
                               , nLoops = 53
                               
                               
                               ):
        """
        Assigns default or user-specified values to the fields under Tab : Solar Field; 
            Section : Design Point for Linear Fresnel Direct Steam 
            model of SAM.
        
        :param nLoops Number of loops: [none]  Type: SSC_NUMBER
        """
        SamBaseClass.logger.debug("Setting values for Tab : Solar Field; Section : Design Point.")
        self.ssc.data_set_number( self.data, b'nLoops', nLoops )
        
    def solarField_fieldControl(self
                                , theta_stow = 10
                                , theta_dep = 10
                                , m_dot_min = 0.05000000074505806
                                , T_fp = 10
                                , V_wind_max = 20
                                ) :    
        """
        Assigns default or user-specified values to the fields under Tab : Solar Field; 
            Section : Filed Control for Linear Fresnel Direct Steam model of SAM.
        
        :param theta_stow stow angle: [deg]  Type: SSC_NUMBER
        :param theta_dep deploy angle: [deg]  Type: SSC_NUMBER
        :param m_dot_min Minimum loop flow rate: [kg/s]  Type: SSC_NUMBER
        :param T_fp Freeze protection temperature (heat trace activation temperature): [C]  Type: SSC_NUMBER
        :param V_wind_max Maximum allowable wind velocity before safety stow: [m/s]  Type: SSC_NUMBER
        """
        SamBaseClass.logger.debug("Setting values for Tab : Solar Field; Section : Field Control.")
        self.ssc.data_set_number( self.data, b'theta_stow', theta_stow )
        self.ssc.data_set_number( self.data, b'theta_dep', theta_dep )
        self.ssc.data_set_number( self.data, b'm_dot_min', m_dot_min )
        self.ssc.data_set_number( self.data, b'T_fp', T_fp )
        self.ssc.data_set_number( self.data, b'V_wind_max', V_wind_max )
        
        
        
    def powerCycle_plantCoolingMode(self
                                    , dT_cw_ref = 10
                                    , CT = 2
                                    , T_approach = 5
                                    , T_ITD_des = 16
                                    , P_cond_ratio = 1.0027999877929688
                                    , P_cond_min = 1.25
                                    , n_pl_inc = 8
                                    ):
        """
        Assigns default or user-specified values to the fields under Tab : Power Cycle; 
            Section : Plant Cooling Mode for Linear Fresnel Direct Steam model of SAM.
        
        :param dT_cw_ref Reference condenser cooling water inlet/outlet T diff: [C]  Type: SSC_NUMBER
        :param CT Flag for using dry cooling or wet cooling system: [none]  Type: SSC_NUMBER    Constraint: INTEGER
        :param T_approach Cooling tower approach temperature: [C]  Type: SSC_NUMBER
        :param T_ITD_des ITD at design for dry system: [C]  Type: SSC_NUMBER
        :param P_cond_ratio Condenser pressure ratio: [none]  Type: SSC_NUMBER
        :param P_cond_min Minimum condenser pressure: [inHg]  Type: SSC_NUMBER
        :param n_pl_inc Number of part-load increments for the heat rejection system: [none]  Type: SSC_NUMBER    Constraint: INTEGER
        """
        SamBaseClass.logger.debug("Setting values for Tab : Power Cycle; Section : Plant Cooling Mode.")
        self.ssc.data_set_number( self.data, b'dT_cw_ref', dT_cw_ref )
        self.ssc.data_set_number( self.data, b'CT', CT )
        self.ssc.data_set_number( self.data, b'T_approach', T_approach )
        self.ssc.data_set_number( self.data, b'T_ITD_des', T_ITD_des )
        self.ssc.data_set_number( self.data, b'P_cond_ratio', P_cond_ratio )
        self.ssc.data_set_number( self.data, b'P_cond_min', P_cond_min )
        self.ssc.data_set_number( self.data, b'n_pl_inc', 8 )
        
        
    def powerCycle_plantDesign(self
                               , LHV_eff = 0.89999997615814209
                               , P_turb_des = 110
                               , q_pb_des = 143.37602233886719
                               , eta_ref = 0.37099999189376831
                               , T_amb_des = 42
                               , P_rh_ref = 0
                               , rh_frac_ref = 0
                               , pb_bd_frac = 0.019999999552965164
                               , system_capacity = 50000.94921875
                               ):
        """
        Assigns default or user-specified values to the fields under Tab : Power Cycle; 
            Section : Plant Design for Linear Fresnel Direct Steam model of SAM.
        
        :param LHV_eff Fuel LHV efficiency (0..1): [none]  Type: SSC_NUMBER
        :param P_turb_des Design-point turbine inlet pressure: [bar]  Type: SSC_NUMBER
        :param q_pb_des Design heat input to the power block: [MW]  Type: SSC_NUMBER
        :param eta_ref Reference conversion efficiency at design condition: [none]  Type: SSC_NUMBER
        :param T_amb_des Reference ambient temperature at design point: [C]  Type: SSC_NUMBER
        :param P_rh_ref Reheater operating pressure at design: [bar]  Type: SSC_NUMBER
        :param rh_frac_ref Reheater flow fraction at design: [none]  Type: SSC_NUMBER
        :param pb_bd_frac Power block blowdown steam fraction : [none]  Type: SSC_NUMBER
        :param system_capacity Nameplate capacity: [kW]  Type: SSC_NUMBER
        """
        SamBaseClass.logger.debug("Setting values for Tab : Power Cycle; Section : Plant Design.")
        self.ssc.data_set_number( self.data, b'LHV_eff', LHV_eff ) 
        self.ssc.data_set_number( self.data, b'P_turb_des', P_turb_des )
        self.ssc.data_set_number( self.data, b'q_pb_des', q_pb_des )
        self.ssc.data_set_number( self.data, b'eta_ref', eta_ref )
        self.ssc.data_set_number( self.data, b'T_amb_des', T_amb_des )
        self.ssc.data_set_number( self.data, b'P_rh_ref', P_rh_ref )
        self.ssc.data_set_number( self.data, b'rh_frac_ref', rh_frac_ref )
        self.ssc.data_set_number( self.data, b'pb_bd_frac', pb_bd_frac )
        self.ssc.data_set_number( self.data, b'system_capacity', system_capacity )
        
    def powerCycle_operation(self
                             , cycle_max_fraction = 1.0499999523162842
                             , cycle_cutoff_frac = 0.20000000298023224
                             , t_sby = 2
                             , q_sby_frac = 0.20000000298023224
                             , fossil_mode = 1
                             , startup_time = 0.34999999403953552
                             , startup_frac = 0.34999999403953552
                             ):
        """
        Assigns default or user-specified values to the fields under Tab : Power Cycle; 
            Section : Operation for Linear Fresnel Direct Steam model of SAM.
        
        :param cycle_max_fraction Maximum turbine over design operation fraction: [none]  Type: SSC_NUMBER
        :param cycle_cutoff_frac Minimum turbine operation fraction before shutdown: [none]  Type: SSC_NUMBER
        :param t_sby Low resource standby period: [hr]  Type: SSC_NUMBER
        :param q_sby_frac Fraction of thermal power required for standby: [none]  Type: SSC_NUMBER
        :param fossil_mode Operation mode for the fossil backup {1=Normal,2=supp,3=toppin}: [none]  Type: SSC_NUMBER    Constraint: INTEGER
        :param startup_time Time needed for power block startup: [hr]  Type: SSC_NUMBER
        :param startup_frac Fraction of design thermal power needed for startup: [none]  Type: SSC_NUMBER
        """
        SamBaseClass.logger.debug("Setting values for Tab : Power Cycle; Section : Operation.")
        self.ssc.data_set_number( self.data, b'cycle_max_fraction', cycle_max_fraction )
        self.ssc.data_set_number( self.data, b'cycle_cutoff_frac', cycle_cutoff_frac )
        self.ssc.data_set_number( self.data, b't_sby', t_sby )
        self.ssc.data_set_number( self.data, b'q_sby_frac', q_sby_frac )
        self.ssc.data_set_number( self.data, b'fossil_mode', fossil_mode )
        self.ssc.data_set_number( self.data, b'startup_time', startup_time )
        self.ssc.data_set_number( self.data, b'startup_frac', startup_frac )
        
        
    def powerCycle_dispatchControl(self
                                   , ffrac = [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
                                   , F_wc = [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
                                   , weekday_schedule = [[ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ]]
                                   , weekend_schedule = [[ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ]]
                                   ):
        """
        Assigns default or user-specified values to the fields under Tab : Power Cycle; 
            Section : Dispatch Control for Linear Fresnel Direct Steam model of SAM.
        
        :param ffrac Fossil dispatch logic - TOU periods: [none]  Type: SSC_ARRAY
        :param F_wc Fraction indicating wet cooling use for hybrid system: [none]  Type: SSC_ARRAY
		:param weekday_schedule 12x24 Time of Use Values for week days: []  Type: SSC_MATRIX
		:param weekend_schedule 12x24 Time of Use Values for week end days: []  Type: SSC_MATRIX
        """  
        SamBaseClass.logger.debug("Setting values for Tab : Power Cycle; Section : Dispatch Control.")
        self.ssc.data_set_array( self.data, b'ffrac',  ffrac);
        self.ssc.data_set_array( self.data, b'F_wc',  F_wc);
        self.ssc.data_set_matrix( self.data, b'weekday_schedule', weekday_schedule );
        self.ssc.data_set_matrix( self.data, b'weekend_schedule', weekend_schedule );        
        
        
    def powerCycle_availAndCurtailment(self
                                       , adjust_constant = 4
                                       #, adjust:hourly = 
                                       #, adjust:periods = 
                                       ):
        """
        Assigns default or user-specified values to the fields under Tab : Power Cycle; 
            Section : Availability and curtailment for Linear Fresnel Direct Steam model of SAM.
        
        :param adjust_constant Constant loss adjustment: [%]  Type: SSC_NUMBER    Constraint: MAX=100
        :param adjust_hourly Hourly loss adjustments: [%]  Type: SSC_ARRAY    Constraint: LENGTH=8760
        :param adjust_periods Period-based loss adjustments: [%]  Type: SSC_MATRIX    Constraint: COLS=3
        """               
        SamBaseClass.logger.debug("Setting values for Tab : Power Cycle; Section : Availability and Curtailment.")
        self.ssc.data_set_number( self.data, b'adjust:constant', adjust_constant )
        
        
        
    def collectorReceiver_BoilerGeomOptPerf(self
                                            , A_aperture = [[ 513.5999755859375 ], [ 513.5999755859375 ]]
                                            , L_col = [[ 44.799999237060547 ], [ 44.799999237060547 ]]
                                            , OptCharType = [[ 1 ], [ 1 ]] 
                                            , TrackingError = [[ 1 ], [ 1 ]]
                                            , GeomEffects = [[ 0.72399997711181641 ], [ 0.72399997711181641 ]]
                                            , rho_mirror_clean = [[ 0.93500000238418579 ], [ 0.93500000238418579 ]] 
                                            , dirt_mirror = [[ 0.94999998807907104 ], [ 0.94999998807907104 ]]
                                            , error = [[ 1 ], [ 1 ]]
                                            , b_OpticalTable = [[ -180,   -160,   -140,   -120,   -100,   -80,   -60,   -40,   -20,   0,   20,   40,   60,   80,   100,   120,   140,   160,   180,   -999.9000244140625 ], [ 0,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1 ], [ 10,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633 ], [ 20,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737 ], [ 30,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563 ], [ 40,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949 ], [ 50,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896 ], [ 60,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869 ], [ 70,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842 ], [ 80,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821 ], [ 90,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0 ]]
                                            , sh_OpticalTable = [[ -180,   -160,   -140,   -120,   -100,   -80,   -60,   -40,   -20,   0,   20,   40,   60,   80,   100,   120,   140,   160,   180,   -999.9000244140625 ], [ 0,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   1 ], [ 10,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633,   0.97444498538970947,   0.97197598218917847,   0.97284698486328125,   0.97690999507904053,   0.97690999507904053,   0.97284698486328125,   0.97197598218917847,   0.97444498538970947,   0.98000001907348633 ], [ 20,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737,   0.92297601699829102,   0.92892998456954956,   0.94600498676300049,   0.95401901006698608,   0.95401901006698608,   0.94600498676300049,   0.92892998456954956,   0.92297601699829102,   0.93000000715255737 ], [ 30,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563,   0.83861798048019409,   0.87069100141525269,   0.9130210280418396,   0.94091099500656128,   0.94091099500656128,   0.9130210280418396,   0.87069100141525269,   0.83861798048019409,   0.8399999737739563 ], [ 40,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949,   0.72994697093963623,   0.80368697643280029,   0.86696100234985352,   0.90003901720046997,   0.90003901720046997,   0.86696100234985352,   0.80368697643280029,   0.72994697093963623,   0.72000002861022949 ], [ 50,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896,   0.59125500917434692,   0.70745402574539185,   0.79350900650024414,   0.83955997228622437,   0.83955997228622437,   0.79350900650024414,   0.70745402574539185,   0.59125500917434692,   0.55000001192092896 ], [ 60,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869,   0.43217799067497253,   0.59747797250747681,   0.66400599479675293,   0.69351100921630859,   0.69351100921630859,   0.66400599479675293,   0.59747797250747681,   0.43217799067497253,   0.34000000357627869 ], [ 70,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842,   0.26525399088859558,   0.42558598518371582,   0.46449598670005798,   0.4771060049533844,   0.4771060049533844,   0.46449598670005798,   0.42558598518371582,   0.26525399088859558,   0.12999999523162842 ], [ 80,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821,   0.11369399726390839,   0.20891000330448151,   0.23325499892234802,   0.23882800340652466,   0.23882800340652466,   0.23325499892234802,   0.20891000330448151,   0.11369399726390839,   0.0099999997764825821 ]]
                                            ):
        """
        Assigns default or user-specified values to the fields under Tab : Collector and Receiver; 
            Section : Boler Geometry and Optical Performance for Linear Fresnel Direct Steam model of SAM.
        
        :param A_aperture (boiler, SH) Reflective aperture area of the collector module: [m^2]  Type: SSC_MATRIX
        :param L_col (boiler, SH) Active length of the superheater section collector module: [m]  Type: SSC_MATRIX
        :param OptCharType (boiler, SH) The optical characterization method: [none]  Type: SSC_MATRIX
        :param TrackingError (boiler, SH) User-defined tracking error derate: [none]  Type: SSC_MATRIX
        :param GeomEffects (boiler, SH) User-defined geometry effects derate: [none]  Type: SSC_MATRIX
        :param rho_mirror_clean (boiler, SH) User-defined clean mirror reflectivity: [none]  Type: SSC_MATRIX
        :param dirt_mirror (boiler, SH) User-defined dirt on mirror derate: [none]  Type: SSC_MATRIX
        :param error (boiler, SH) User-defined general optical error derate: [none]  Type: SSC_MATRIX
        :param b_OpticalTable Values of the optical efficiency table: [none]  Type: SSC_MATRIX
        :param sh_OpticalTable Values of the optical efficiency table: [none]  Type: SSC_MATRIX
        """               
        SamBaseClass.logger.debug("Setting values for Tab : Collector and Receiver, Section : Boiler Geometry and Optical Performance.")
        self.ssc.data_set_matrix( self.data, b'A_aperture', A_aperture );                
        self.ssc.data_set_matrix( self.data, b'L_col', L_col );
        self.ssc.data_set_matrix( self.data, b'OptCharType', OptCharType );                
        self.ssc.data_set_matrix( self.data, b'TrackingError', TrackingError );
        self.ssc.data_set_matrix( self.data, b'GeomEffects', GeomEffects );        
        self.ssc.data_set_matrix( self.data, b'rho_mirror_clean', rho_mirror_clean );        
        self.ssc.data_set_matrix( self.data, b'dirt_mirror', dirt_mirror );        
        self.ssc.data_set_matrix( self.data, b'error', error );        
        self.ssc.data_set_matrix( self.data, b'b_OpticalTable', b_OpticalTable );
        self.ssc.data_set_matrix( self.data, b'sh_OpticalTable', sh_OpticalTable );

        
        
        
    def collectorReceiver_IncAngModifiers(self
                                         , IAM_T = [[ 0.98960000276565552,   0.043999999761581421,   -0.072099998593330383,   -0.23270000517368317,   0 ], [ 0.98960000276565552,   0.043999999761581421,   -0.072099998593330383,   -0.23270000517368317,   0 ]]
                                         , IAM_L = [[ 1.0031000375747681,   -0.22589999437332153,   0.53680002689361572,   -1.6433999538421631,   0.72219997644424438 ], [ 1.0031000375747681,   -0.22589999437332153,   0.53680002689361572,   -1.6433999538421631,   0.72219997644424438 ]]
                                         ):
        """
        Assigns default or user-specified values to the fields under Tab : Collector and Receiver; 
            Section : Incidence Angle Modifier for Linear Fresnel Direct Steam model of SAM.
        
        :param IAM_T (boiler, SH) Transverse Incident angle modifiers (0,1,2,3,4 order terms): [none]  Type: SSC_MATRIX
        :param IAM_L (boiler, SH) Longitudinal Incident angle modifiers (0,1,2,3,4 order terms): [none]  Type: SSC_MATRIX
        """               
        SamBaseClass.logger.debug("Setting values for Tab : Collector and Receiver, Section : Incidence Angle Modifiers.")
        self.ssc.data_set_matrix( self.data, b'IAM_T', IAM_T );                
        self.ssc.data_set_matrix( self.data, b'IAM_L', IAM_L );
        
        
    def collectorReceiver_receiverGeomHeatLoss(self
                                               , HLCharType = [[ 1 ], [ 1 ]]
                                               ):
        """
        Assigns default or user-specified values to the fields under Tab : Collector and Receiver; 
            Section : Recever Geometry and Heat Loss for Linear Fresnel Direct Steam model of SAM.
        
        :param HLCharType (boiler, SH) Flag indicating the heat loss model type {1=poly.; 2=Forristall}: [none]  Type: SSC_MATRIX
        """     
        SamBaseClass.logger.debug("Setting values for Tab : Collector and Receiver, Section : Receiver Geometry and Heat Loss.")
        self.ssc.data_set_matrix( self.data, b'HLCharType', HLCharType );
        
        
        
    def collectorReceiver_receiverGeomHeatLoss_evacTubeHeatLoss(self
                                                                , D_2 = [[ 0.065999999642372131 ], [ 0.065999999642372131 ]]
                                                                , D_3 = [[ 0.070000000298023224 ], [ 0.070000000298023224 ]]
                                                                , D_4 = [[ 0.11500000208616257 ], [ 0.11500000208616257 ]]
                                                                , D_5 = [[ 0.11999999731779099 ], [ 0.11999999731779099 ]]
                                                                , D_p = [[ 0 ], [ 0 ]]
                                                                , Rough = [[ 4.5000000682193786e-05 ], [ 4.5000000682193786e-05 ]]
                                                                , Flow_type = [[ 1 ], [ 1 ]]
                                                                , AbsorberMaterial = [[ 1 ], [ 1 ]]
                                                                , HCE_FieldFrac = [[ 0.98500001430511475,   0.0099999997764825821,   0.004999999888241291,   0 ], [ 0.98500001430511475,   0.0099999997764825821,   0.004999999888241291,   0 ]]
                                                                , alpha_abs = [[ 0.95999997854232788,   0.95999997854232788,   0.80000001192092896,   0 ], [ 0.95999997854232788,   0.95999997854232788,   0.80000001192092896,   0 ]]
                                                                , b_eps_HCE1 = [[ 0 ], [ 0.13840000331401825 ]]
                                                                , b_eps_HCE2 = [[ 0 ], [ 0.64999997615814209 ]]
                                                                , b_eps_HCE3 = [[ 0 ], [ 0.64999997615814209 ]]
                                                                , b_eps_HCE4 = [[ 0 ], [ 0.13840000331401825 ]]
                                                                , sh_eps_HCE1 = [[ 0 ], [ 0.13840000331401825 ]]
                                                                , sh_eps_HCE2 = [[ 0 ], [ 0.64999997615814209 ]]
                                                                , sh_eps_HCE3 = [[ 0 ], [ 0.64999997615814209 ]]
                                                                , sh_eps_HCE4 = [[ 0 ], [ 0.13840000331401825 ]]
                                                                , alpha_env = [[ 0.019999999552965164,   0.019999999552965164,   0,   0 ], [ 0.019999999552965164,   0.019999999552965164,   0,   0 ]]
                                                                , EPSILON_4 = [[ 0.86000001430511475,   0.86000001430511475,   1,   0 ], [ 0.86000001430511475,   0.86000001430511475,   1,   0 ]]
                                                                , Tau_envelope = [[ 0.96299999952316284,   0.96299999952316284,   1,   0 ], [ 0.96299999952316284,   0.96299999952316284,   1,   0 ]]
                                                                , GlazingIntactIn = [[ 1,   1,   0,   1 ], [ 1,   1,   0,   1 ]]
                                                                , AnnulusGas = [[ 27,   1,   1,   1 ], [ 27,   1,   1,   1 ]]
                                                                , P_a = [[ 9.9999997473787516e-05,   750,   750,   0 ], [ 9.9999997473787516e-05,   750,   750,   0 ]]
                                                                , Design_loss = [[ 150,   1100,   1500,   0 ], [ 150,   1100,   1500,   0 ]]
                                                                , Shadowing = [[ 0.95999997854232788,   0.95999997854232788,   0.95999997854232788,   0 ], [ 0.95999997854232788,   0.95999997854232788,   0.95999997854232788,   0 ]]
                                                                , Dirt_HCE = [[ 0.98000001907348633,   0.98000001907348633,   1,   0 ], [ 0.98000001907348633,   0.98000001907348633,   1,   0 ]]
                                                                ):   
        """
        Assigns default or user-specified values to the fields under Tab : Collector and Receiver; 
            Section : Recever Geometry and Heat Loss Sub Section: Evacuated Tube Heat Loss model
            for Linear Fresnel Direct Steam model of SAM.
        
        :param D_2 (boiler, SH) The inner absorber tube diameter: [m]  Type: SSC_MATRIX
        :param D_3 (boiler, SH) The outer absorber tube diameter: [m]  Type: SSC_MATRIX
        :param D_4 (boiler, SH) The inner glass envelope diameter: [m]  Type: SSC_MATRIX
        :param D_5 (boiler, SH) The outer glass envelope diameter: [m]  Type: SSC_MATRIX
        :param D_p (boiler, SH) The diameter of the absorber flow plug (optional): [m]  Type: SSC_MATRIX
        :param Rough (boiler, SH) Roughness of the internal surface: [m]  Type: SSC_MATRIX
        :param Flow_type (boiler, SH) The flow type through the absorber: [none]  Type: SSC_MATRIX
        :param AbsorberMaterial (boiler, SH) Absorber material type: [none]  Type: SSC_MATRIX
        :param HCE_FieldFrac (boiler, SH) The fraction of the field occupied by this HCE type (4: # field fracs): [none]  Type: SSC_MATRIX
        :param alpha_abs (boiler, SH) Absorber absorptance (4: # field fracs): [none]  Type: SSC_MATRIX
        :param b_eps_HCE1 (temperature) Absorber emittance (eps): [none]  Type: SSC_MATRIX
        :param b_eps_HCE2 (temperature) Absorber emittance (eps): [none]  Type: SSC_MATRIX
        :param b_eps_HCE3 (temperature) Absorber emittance (eps): [none]  Type: SSC_MATRIX
        :param b_eps_HCE4 (temperature) Absorber emittance (eps): [none]  Type: SSC_MATRIX
        :param sh_eps_HCE1 (temperature) Absorber emittance (eps): [none]  Type: SSC_MATRIX
        :param sh_eps_HCE2 (temperature) Absorber emittance (eps): [none]  Type: SSC_MATRIX
        :param sh_eps_HCE3 (temperature) Absorber emittance (eps): [none]  Type: SSC_MATRIX
        :param sh_eps_HCE4 (temperature) Absorber emittance (eps): [none]  Type: SSC_MATRIX
        :param alpha_env (boiler, SH) Envelope absorptance (4: # field fracs): [none]  Type: SSC_MATRIX
        :param EPSILON_4 (boiler, SH) Inner glass envelope emissivities (Pyrex) (4: # field fracs): [none]  Type: SSC_MATRIX
        :param Tau_envelope (boiler, SH) Envelope transmittance (4: # field fracs): [none]  Type: SSC_MATRIX
        :param GlazingIntactIn (boiler, SH) The glazing intact flag {true=0; false=1} (4: # field fracs): [none]  Type: SSC_MATRIX
        :param AnnulusGas (boiler, SH) Annulus gas type {1=air; 26=Ar; 27=H2} (4: # field fracs): [none]  Type: SSC_MATRIX
        :param P_a (boiler, SH) Annulus gas pressure (4: # field fracs): [torr]  Type: SSC_MATRIX
        :param Design_loss (boiler, SH) Receiver heat loss at design (4: # field fracs): [W/m]  Type: SSC_MATRIX
        :param Shadowing (boiler, SH) Receiver bellows shadowing loss factor (4: # field fracs): [none]  Type: SSC_MATRIX
        :param Dirt_HCE (boiler, SH) Loss due to dirt on the receiver envelope (4: # field fracs): [none]  Type: SSC_MATRIX
        """               
        SamBaseClass.logger.debug("Setting values for Tab : Collector and Receiver, Section : Receiver Geometry and Heat Loss, Sub Section - Evacuated Tube Heat Loss model")
        self.ssc.data_set_matrix( self.data, b'D_2', D_2 );
        self.ssc.data_set_matrix( self.data, b'D_3', D_3 );
        self.ssc.data_set_matrix( self.data, b'D_4', D_4 );
        self.ssc.data_set_matrix( self.data, b'D_5', D_5 );
        self.ssc.data_set_matrix( self.data, b'D_p', D_p );
        self.ssc.data_set_matrix( self.data, b'Rough', Rough );        
        self.ssc.data_set_matrix( self.data, b'Flow_type', Flow_type );        
        self.ssc.data_set_matrix( self.data, b'AbsorberMaterial', AbsorberMaterial );        
        self.ssc.data_set_matrix( self.data, b'HCE_FieldFrac', HCE_FieldFrac );        
        self.ssc.data_set_matrix( self.data, b'alpha_abs', alpha_abs );        
        self.ssc.data_set_matrix( self.data, b'b_eps_HCE1', b_eps_HCE1 );        
        self.ssc.data_set_matrix( self.data, b'b_eps_HCE2', b_eps_HCE2 );        
        self.ssc.data_set_matrix( self.data, b'b_eps_HCE3', b_eps_HCE3 );        
        self.ssc.data_set_matrix( self.data, b'b_eps_HCE4', b_eps_HCE4 );
        self.ssc.data_set_matrix( self.data, b'sh_eps_HCE1', sh_eps_HCE1 );
        self.ssc.data_set_matrix( self.data, b'sh_eps_HCE2', sh_eps_HCE2 );        
        self.ssc.data_set_matrix( self.data, b'sh_eps_HCE3', sh_eps_HCE3 );        
        self.ssc.data_set_matrix( self.data, b'sh_eps_HCE4', sh_eps_HCE4 );        
        self.ssc.data_set_matrix( self.data, b'alpha_env', alpha_env );        
        self.ssc.data_set_matrix( self.data, b'EPSILON_4', EPSILON_4 );        
        self.ssc.data_set_matrix( self.data, b'Tau_envelope', Tau_envelope );        
        self.ssc.data_set_matrix( self.data, b'GlazingIntactIn', GlazingIntactIn );        
        self.ssc.data_set_matrix( self.data, b'AnnulusGas', AnnulusGas );        
        self.ssc.data_set_matrix( self.data, b'P_a', P_a );        
        self.ssc.data_set_matrix( self.data, b'Design_loss', Design_loss );        
        self.ssc.data_set_matrix( self.data, b'Shadowing', Shadowing );        
        self.ssc.data_set_matrix( self.data, b'Dirt_HCE', Dirt_HCE );

        
        
    def collectorReceiver_receiverGeomHeatLoss_PolyFitHeatLossModel(self
                                                                    , HL_dT = [[ 0,   0.67199999094009399,   0.0025559999048709869,   0,   0 ], [ 0,   0.67199999094009399,   0.0025559999048709869,   0,   0 ]]
                                                                    , HL_W = [[ 1,   0,   0,   0,   0 ], [ 1,   0,   0,   0,   0 ]]
                                                                    ):    
        """
        Assigns default or user-specified values to the fields under Tab : Collector and Receiver; 
            Section : Recever Geometry and Heat Loss Sub Section: Polynomial Fit Heat Loss model
            for Linear Fresnel Direct Steam model of SAM.
        
        :param HL_dT (boiler, SH) Heat loss coefficient - HTF temperature (0,1,2,3,4 order terms): [W/m-K^order]  Type: SSC_MATRIX
        :param HL_W (boiler, SH) Heat loss coef adj wind velocity (0,1,2,3,4 order terms): [1/(m/s)^order]  Type: SSC_MATRIX
        """
        SamBaseClass.logger.debug("Setting values for Tab : Collector and Receiver, Section : Receiver Geometry and Heat Loss, Sub section: Polynomial fit heat loss model")
        self.ssc.data_set_matrix( self.data, b'HL_dT', HL_dT );
        self.ssc.data_set_matrix( self.data, b'HL_W', HL_W );

        
    
    def parasitics(self
                   , PB_fixed_par = 0.0054999999701976776
                   , bop_array =[ 0, 1, 0.4830000102519989, 0.57099997997283936, 0 ]
                   , aux_array =[ 0.023000000044703484, 1, 0.4830000102519989, 0.57099997997283936, 0 ]
                   , Pipe_hl_coef = 0.0035000001080334187
                   , SCA_drives_elec = 0.20000000298023224
                   ):
        """
        Assigns default or user-specified values to the fields under Tab : Parasitics; 
            Section : Parasitic Losses for Linear Fresnel Direct Steam model of SAM.
        
        :param PB_fixed_par fraction of rated gross power consumed at all hours of the year: [none]  Type: SSC_NUMBER
        :param bop_array BOP_parVal, BOP_parPF, BOP_par0, BOP_par1, BOP_par2: [-]  Type: SSC_ARRAY
        :param aux_array Aux_parVal, Aux_parPF, Aux_par0, Aux_par1, Aux_par2: [-]  Type: SSC_ARRAY
        :param Pipe_hl_coef Loss coefficient from the header.. runner pipe.. and non-HCE pipin: [W/m2-K]  Type: SSC_NUMBER
        :param SCA_drives_elec Tracking power.. in Watts per SCA drive: [W/m2]  Type: SSC_NUMBER
        """
        SamBaseClass.logger.debug("Setting values for Tab : Parasitics.")
        self.ssc.data_set_number( self.data, b'PB_fixed_par', PB_fixed_par )
        self.ssc.data_set_array( self.data, b'bop_array',  bop_array);
        self.ssc.data_set_array( self.data, b'aux_array',  aux_array);
        self.ssc.data_set_number( self.data, b'Pipe_hl_coef', Pipe_hl_coef )
        self.ssc.data_set_number( self.data, b'SCA_drives_elec', SCA_drives_elec )
        
    def remainingParams(self):    
        SamBaseClass.logger.debug("Setting the values which were not identified initially.")
        #The methods for the following variables yet to be written.
        self.ssc.data_set_number( self.data, b'tes_hours', 0 )
        self.ssc.data_set_number( self.data, b'q_max_aux', 255.63600158691406 )
        self.ssc.data_set_number( self.data, b'PB_pump_coef', 0 )
        self.ssc.data_set_number( self.data, b'is_sh', 1 )
        
        #Parameters from the weather file?
        self.ssc.data_set_number( self.data, b'dnifc', 0 )
        self.ssc.data_set_number( self.data, b'I_bn', 0 )
        self.ssc.data_set_number( self.data, b'T_db', 15 )
        self.ssc.data_set_number( self.data, b'T_dp', 10 )
        self.ssc.data_set_number( self.data, b'P_amb', 930.5 )
        self.ssc.data_set_number( self.data, b'V_wind', 0 )
        
        #Power block parameters?
        self.ssc.data_set_number( self.data, b'm_dot_htf_ref', 0 )
        self.ssc.data_set_number( self.data, b'm_pb_demand', 0 )
        self.ssc.data_set_number( self.data, b'shift', 0 )
        self.ssc.data_set_number( self.data, b'SolarAz_init', 0 )
        self.ssc.data_set_number( self.data, b'SolarZen', 0 )
        self.ssc.data_set_number( self.data, b'T_pb_out_init', 290 )
        #self.ssc.data_set_number( self.data, b'eta_ref', 0.37099999189376831 )
        self.ssc.data_set_number( self.data, b'T_cold_ref', 230 )
        
        
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
        self.ssc.data_set_number( self.data, b'f_recSU', 1 )
        #self.ssc.data_set_number( self.data, b'adjust:constant', 4 )


    def print_impParams(self):
        capacity_factor = self.ssc.data_get_number(self.data, b'capacity_factor');
        print ('\nCapacity factor (year 1) = ', capacity_factor)
#        annual_total_water_use = self.ssc.data_get_number(self.data, b'annual_total_water_use');
#        print ('Annual Water Usage = ', annual_total_water_use)
        annual_energy = self.ssc.data_get_number(self.data, b'annual_energy');
        print ('Annual energy (year 1) = ', annual_energy)
    
      
        
#Unit test cases for the method    
class sscTests(unittest.TestCase):

    def test_capacityFactor(self):
        """
        Tests if the capacity factor for one year is calculated correctly when 
        system capacity is 50000 and all other values are default values.
        """

        samLfDs = samCspLinearFresnelDirectSteam()
        samLfDs.main()
        capacity_factor = samLfDs.test_capacity_factor #ssc.data_get_number(samLfDs.data, b'capacity_factor');
        self.assertEqual(capacity_factor, 25.037185668945312)
"""
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
"""
         
if __name__ == '__main__':
    sam = samCspLinearFresnelDirectSteam()
    sam.main()
    
    #Argument for the unit test makes sure the unit test does not fail if system_capacity 
    #system_capacity is passed as a first argument on command line.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
 
    
