# -*- coding: utf-8 -*-
"""
Calculates the financial parameters for the financial model Power Purchase Agreemnt
    with Partnership flip with debt. The following are the important parameters which
    are being calculated for the project. 
    - PPA price (year 1)
    - Levelized PPA price (nominal)
    - Levelized PPA price (real)
    - Levelized COE (nominal)
    - Levelized COE (real)
    - Investor IRR
    - Year investor IRR acheived
    - Investor IRR at end of project
    - Investor NPV over project life
    - Developer IRR at end of project
    - Developer NPV over project life
    - Net capital cost
    - Equity
	- Debt

For a full list of available output variables please refer the documentation for
    Linear Fresnel direct steam model (levpartflip) of NREL's System 
    Advisor Model software development kit.
    
Created by: Vikas Vicraman
Create date: 04/01/2019

V1: - Wrapper from SAM v11.11
    Modified by: Vikas Vicraman
    Modified date: 04/01/2019
    - Added modular functions and constructors
   
"""

from SAM.PySSC import PySSC
from SAM.SamBaseClass import SamBaseClass
import os, sys
import argparse
import logging
import unittest


# TODO: implement logging (gyetman)
     
class samFinPpaPartnershipFlipWithDebt(SamBaseClass):
    
    def __init__(self, SamBaseClass):
        """
        Methods for setting up logger, unit testing and creating the ssc module 
        go here.
        """

        #Change to get the base class data - investigate whether this remains the same throughout the execution
        #self.ssc = SamBaseClass
        #self.data = inputData
        self.data = SamBaseClass.create_ssc_module(SamBaseClass)
        print ('SSC Version = ', self.ssc.version())
        print ('SSC Build Information = ', self.ssc.build_info().decode("utf - 8"))
        
        #Initializes all the variables to default values if the class is called 
        #    from other classes
        if __name__ != '__main__':
            self.main()

    
    def main(self):
             
        """
        Main method gets initialized when the file is run on its own with default
            value for system_capacity = 50000 MWe. This method can also be 
            called from command line with the system_capacity parameter as inline 
            system argument. This argument takes numeric values.
        
        :param system_capacity Nameplate capacity: [kW]  Type: SSC_NUMBER
        """

        print('File name = ', sys.argv[0])
        if len(sys.argv) == 2:     
            annual_energy = float(sys.argv[1])
        else:           
            # Setting default value as 50000
            annual_energy = 109662880
        print("Annual Energy = " , annual_energy)

        #Creating SAM data and ssc modules. 
        #self.create_ssc_module()
        
        #Parsing different default or UI input values for all the different parameters.
        self.systemCosts()
        self.systemCosts_OperAndMaint()

        self.lifetime()

        self.finParams_analysisParams()
        self.finParams_ConstrFinancing()
        self.finParams_CostOfAcqFinancing()
        self.finParams_equityFlipStruct()
        self.finParams_projTaxAndInsurance()
        self.finParams_projTermDebt()
        self.finParams_SolnMode()
        
        self.todFactors()

        self.incentives_CBI()
        self.incentives_IBI()
        self.incentives_ITC()
        self.incentives_PTC()

        self.depreciation()

        self.remainingParams()
        
        #Executes the module and creates annual hourly simulations
        self.module_create_execute('levpartflip', self.ssc, self.data)
        self.print_impParams()



    def systemCosts_OperAndMaint(self
                                 , om_fixed =[ 0 ]
                                 , om_fixed_escal = 0
                                 , om_production =[ 4 ]
                                 , om_production_escal = 0
                                 , om_capacity =[ 55 ]
                                 , om_capacity_escal = 0
                                 , om_fuel_cost =[ 0 ]
                                 , om_fuel_cost_escal = 0
                                 ):
        """
        Assigns default or user-specified values to the fields under Tab : System Costs; 
            Section : Operation and Maintenance of SAM.

        :param om_fixed Fixed O&M annual amount:  [$/year]   Type: SSC_ARRAY   Require: ?=0.0
        :param om_fixed_escal Fixed O&M escalation:  [%/year]   Type: SSC_NUMBER   Require: ?=0.0
        :param om_production Production-based O&M amount:  [$/MWh]   Type: SSC_ARRAY   Require: ?=0.0
        :param om_production_escal Production-based O&M escalation:  [%/year]   Type: SSC_NUMBER   Require: ?=0.0
        :param om_capacity Capacity-based O&M amount:  [$/kWcap]   Type: SSC_ARRAY   Require: ?=0.0
        :param om_capacity_escal Capacity-based O&M escalation:  [%/year]   Type: SSC_NUMBER   Require: ?=0.0
        :param om_fuel_cost Fuel cost:  [$/MMBtu]   Type: SSC_ARRAY   Require: ?=0.0
        :param om_fuel_cost_escal Fuel cost escalation:  [%/year]   Type: SSC_NUMBER   Require: ?=0.0
        """

        self.ssc.data_set_array( self.data, b'om_fixed',  om_fixed)
        self.ssc.data_set_number( self.data, b'om_fixed_escal', om_fixed_escal )    
        self.ssc.data_set_array( self.data, b'om_production',  om_production);
        self.ssc.data_set_number( self.data, b'om_production_escal', om_production_escal )     
        self.ssc.data_set_array( self.data, b'om_capacity',  om_capacity);
        self.ssc.data_set_number( self.data, b'om_capacity_escal', om_capacity_escal )
        self.ssc.data_set_array( self.data, b'om_fuel_cost',  om_fuel_cost);
        self.ssc.data_set_number( self.data, b'om_fuel_cost_escal', om_fuel_cost_escal )


    def systemCosts(self
                    , system_capacity = 50000
                    , total_installed_cost = 185785712
                    ):
        """
        Assigns default or user-specified values to the fields under Tab : System Costs of SAM
        These costs are in various sub-sections of the tab. 
        The variable system_capacity is from the inputs to the CSP system.

        :param system_capacity System nameplate capacity:  [kW]   Type: SSC_NUMBER    Constraint: POSITIVE   Require: *
        :param total_installed_cost Installed cost:  [$]   Type: SSC_NUMBER   Require: *
        """

        self.ssc.data_set_number( self.data, b'total_installed_cost', total_installed_cost )
        #Verify if required
        self.ssc.data_set_number( self.data, b'system_capacity', system_capacity )


    def lifetime(self
                 , degradation =[ 0 ]
                 ):

        """
        Assigns default or user-specified values to the fields under Tab : Lifetime;
        Section: System Performance Degradation of SAM

        :param degradation Annual energy degradation:   Type: SSC_ARRAY   Require: *
        """        
        self.ssc.data_set_array( self.data, b'degradation',  degradation);


    def finParams_SolnMode(self
                            , flip_target_percent = 11
                            , flip_target_year = 9
                            , ppa_soln_mode = 0
                            , ppa_price_input = 0.12999999523162842
                            ):
        """
        Assigns default or user-specified values to the fields under Tab : Financial Parameters;
        Section: Solution Mode of SAM

        :param flip_target_percent After-tax flip/return target:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=11
        :param flip_target_year Return target year:   Type: SSC_NUMBER    Constraint: MIN=1   Require: ?=11
        :param ppa_soln_mode PPA solution mode:  [0/1]   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0,MAX=1   Require: ?=0
        :param ppa_price_input Initial year PPA price:  [$/kWh]   Type: SSC_NUMBER   Require: ?=10

        """        

        self.ssc.data_set_number( self.data, b'flip_target_percent', flip_target_percent )
        self.ssc.data_set_number( self.data, b'flip_target_year', flip_target_year )
        self.ssc.data_set_number( self.data, b'ppa_soln_mode', ppa_soln_mode )
        self.ssc.data_set_number( self.data, b'ppa_price_input', ppa_price_input )
        
        
    def finParams_equityFlipStruct(self
                                   , tax_investor_equity_percent = 98
                                   , tax_investor_preflip_cash_percent = 98
                                   , tax_investor_postflip_cash_percent = 10
                                   , tax_investor_preflip_tax_percent = 98
                                   , tax_investor_postflip_tax_percent = 10
                                   ):
        """
        Assigns default or user-specified values to the fields under Tab : Financial Parameters;
        Section: Equity Flip Structure of SAM
        
        :param tax_investor_equity_percent Tax investor equity:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=98
        :param tax_investor_preflip_cash_percent Tax investor pre-flip cash:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=98
        :param tax_investor_postflip_cash_percent Tax investor post-flip cash:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=15
        :param tax_investor_preflip_tax_percent Tax investor pre-flip tax benefit:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=98
        :param tax_investor_postflip_tax_percent Tax investor post-flip tax benefit:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=15
        """   

        self.ssc.data_set_number( self.data, b'tax_investor_equity_percent', tax_investor_equity_percent )
        self.ssc.data_set_number( self.data, b'tax_investor_preflip_cash_percent', tax_investor_preflip_cash_percent )
        self.ssc.data_set_number( self.data, b'tax_investor_postflip_cash_percent', tax_investor_postflip_cash_percent )
        self.ssc.data_set_number( self.data, b'tax_investor_preflip_tax_percent', tax_investor_preflip_tax_percent )
        self.ssc.data_set_number( self.data, b'tax_investor_postflip_tax_percent', tax_investor_postflip_tax_percent )

    def finParams_analysisParams(self
                                 , analysis_period = 25
                                 , real_discount_rate = 6.4000000953674316
                                 , inflation_rate = 2.5
                                 ):
        """
        Assigns default or user-specified values to the fields under Tab : Financial Parameters;
        Section: Analysis Parameters of SAM
        
        :param analysis_period Analyis period:  [years]   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0,MAX=50   Require: ?=30
        :param real_discount_rate Real discount rate:  [%]   Type: SSC_NUMBER    Constraint: MIN=-99   Require: *
        :param inflation_rate Inflation rate:  [%]   Type: SSC_NUMBER    Constraint: MIN=-99   Require: *
        """   

        self.ssc.data_set_number( self.data, b'analysis_period', analysis_period )
        self.ssc.data_set_number( self.data, b'real_discount_rate', real_discount_rate )
        self.ssc.data_set_number( self.data, b'inflation_rate', inflation_rate )


    def finParams_projTaxAndInsurance(self
                                      , federal_tax_rate =[ 21 ]
                                      , state_tax_rate =[ 7 ]
                                      , property_tax_rate = 0
                                      , prop_tax_cost_assessed_percent = 100
                                      , prop_tax_assessed_decline = 0
                                      , insurance_rate = 0.5
                                      ):
        """
        Assigns default or user-specified values to the fields under Tab : Financial Parameters;
        Section: Project Tax and Insurance Rates of SAM.
        This section also contains variables from the Property Tax sub-section of SAM.

        :param federal_tax_rate Federal income tax rate:  [%]   Type: SSC_ARRAY   Require: *
        :param state_tax_rate State income tax rate:  [%]   Type: SSC_ARRAY   Require: *
        :param property_tax_rate Property tax rate:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=0.0
        :param prop_tax_cost_assessed_percent Percent of pre-financing costs assessed:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=95
        :param prop_tax_assessed_decline Assessed value annual decline:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=5
        :param insurance_rate Insurance rate:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=0.0
        """
        self.ssc.data_set_array( self.data, b'federal_tax_rate',  federal_tax_rate);
        self.ssc.data_set_array( self.data, b'state_tax_rate',  state_tax_rate);
        self.ssc.data_set_number( self.data, b'property_tax_rate', property_tax_rate )
        self.ssc.data_set_number( self.data, b'prop_tax_cost_assessed_percent', prop_tax_cost_assessed_percent )
        self.ssc.data_set_number( self.data, b'prop_tax_assessed_decline', prop_tax_assessed_decline )
        self.ssc.data_set_number( self.data, b'insurance_rate', insurance_rate )


    def finParams_salvage(self
                          , salvage_percentage = 0
                          ):
        """
        Assigns default or user-specified values to the fields under Tab : Financial Parameters;
        Section: Project Tax and Insurance Rates of SAM.
        This section also contains variables from the Property Tax sub-section of SAM.

        :param salvage_percentage Net pre-tax cash salvage value:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=10
        """

        self.ssc.data_set_number( data, b'salvage_percentage', salvage_percentage )

    def finParams_projTermDebt(self
                               , loan_moratorium = 0
                               , term_tenor = 18
                               , term_int_rate = 7
                               , dscr = 1.2999999523162842
                               , debt_percent = 50
                               , debt_option = 1
                               , payment_option = 0
                               , cost_debt_closing = 450000
                               , cost_debt_fee = 2.75
                               ):
        """
        Assigns default or user-specified values to the fields under Tab : Financial Parameters;
        Section: Project Term Debt of SAM.

        :param loan_moratorium Loan moratorium period:  [years]   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0   Require: ?=0
        :param term_tenor Term financing tenor:  [years]   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0   Require: ?=10
        :param term_int_rate Term financing interest rate:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=8.5
        :param dscr Debt service coverage ratio:   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=1.5
        :param debt_percent Debt percent:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=50
        :param debt_option Debt option:  [0/1]   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0,MAX=1   Require: ?=1
        :param payment_option Debt repayment option:  [0/1]   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0,MAX=1   Require: ?=0
        :param cost_debt_closing Debt closing cost:  [$]   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=250000
        :param cost_debt_fee Debt closing fee (% of total debt amount):  [%]   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=1.5

        """

        self.ssc.data_set_number( self.data, b'loan_moratorium', loan_moratorium )
        self.ssc.data_set_number( self.data, b'term_tenor', term_tenor )
        self.ssc.data_set_number( self.data, b'term_int_rate', term_int_rate )                              
        self.ssc.data_set_number( self.data, b'dscr', dscr )
        self.ssc.data_set_number( self.data, b'debt_percent', debt_percent )
        self.ssc.data_set_number( self.data, b'debt_option', debt_option )
        self.ssc.data_set_number( self.data, b'payment_option', payment_option )
        self.ssc.data_set_number( self.data, b'cost_debt_closing', cost_debt_closing )
        self.ssc.data_set_number( self.data, b'cost_debt_fee', cost_debt_fee )

    def finParams_CostOfAcqFinancing(self
                                     , cost_dev_fee_percent = 3
                                     , cost_equity_closing = 300000
                                     , cost_other_financing = 0
                                     ):
        """
        Assigns default or user-specified values to the fields under Tab : Financial Parameters;
        Section: Project Term Debt of SAM.
        
        :param cost_dev_fee_percent Development fee (% pre-financing cost):  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=3
        :param cost_equity_closing Equity closing cost:  [$]   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=100000
        :param cost_other_financing :  [$]   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=150000
        
        """

        self.ssc.data_set_number( self.data, b'cost_dev_fee_percent', cost_dev_fee_percent )
        self.ssc.data_set_number( self.data, b'cost_equity_closing', cost_equity_closing )
        self.ssc.data_set_number( self.data, b'cost_other_financing', cost_other_financing )

    def finParams_ConstrFinancing(self
                                  , construction_financing_cost = 9289286
                                  ):
        """
        Assigns default or user-specified values to the fields under Tab : Financial Parameters;
        Section: Construction Financing of SAM.
        The construction financing cost is being calculated on the UI.
        
        :param construction_financing_cost Construction financing total:  [$]   Type: SSC_NUMBER   Require: *
        
        """

        self.ssc.data_set_number( self.data, b'construction_financing_cost', construction_financing_cost )

    def finParams_reserveAccnts(self
                                , dscr_reserve_months = 6
                                , months_working_reserve = 6
                                , months_receivables_reserve = 0
                                , reserves_interest = 1.75 
                                , equip1_reserve_cost = 0 
                                , equip1_reserve_freq = 12 
                                , equip2_reserve_cost = 0 
                                , equip2_reserve_freq = 15 
                                , equip3_reserve_cost = 0 
                                , equip3_reserve_freq = 3 
                                , equip_reserve_depr_sta = 0 
                                , equip_reserve_depr_fed = 0 
                                ):
        """
        Assigns default or user-specified values to the fields under Tab : Financial Parameters;
        Section: Reserve accounts of SAM
        
        :param dscr_reserve_months Debt service reserve account:  [months P&I]   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=6
        :param months_working_reserve Working capital reserve months of operating costs:  [months]   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=6
        :param months_receivables_reserve Receivables reserve months of PPA revenue:  [months]   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=0
        :param reserves_interest Interest on reserves:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=1.75
        :param equip1_reserve_cost Major equipment reserve 1 cost:  [$/W]   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=0.25
        :param equip1_reserve_freq Major equipment reserve 1 frequency:  [years]   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0   Require: ?=12
        :param equip2_reserve_cost Major equipment reserve 2 cost:  [$/W]   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=0
        :param equip2_reserve_freq Major equipment reserve 2 frequency:  [years]   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0   Require: ?=15
        :param equip3_reserve_cost Major equipment reserve 3 cost:  [$/W]   Type: SSC_NUMBER    Constraint: MIN=0   Require: ?=0
        :param equip3_reserve_freq Major equipment reserve 3 frequency:  [years]   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0   Require: ?=20
        :param equip_reserve_depr_sta Major equipment reserve state depreciation:   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0,MAX=6   Require: ?=0
        :param equip_reserve_depr_fed Major equipment reserve federal depreciation:   Type: SSC_NUMBER    Constraint: INTEGER,MIN=0,MAX=6   Require: ?=0
        
        """
        self.ssc.data_set_number( self.data, b'dscr_reserve_months', dscr_reserve_months )
        self.ssc.data_set_number( self.data, b'months_working_reserve', months_working_reserve )
        self.ssc.data_set_number( self.data, b'months_receivables_reserve', months_receivables_reserve )
        self.ssc.data_set_number( self.data, b'reserves_interest', reserves_interest )
        self.ssc.data_set_number( self.data, b'equip1_reserve_cost', equip1_reserve_cost )
        self.ssc.data_set_number( self.data, b'equip1_reserve_freq', equip1_reserve_freq )
        self.ssc.data_set_number( self.data, b'equip2_reserve_cost', equip2_reserve_cost )
        self.ssc.data_set_number( self.data, b'equip2_reserve_freq', equip2_reserve_freq )
        self.ssc.data_set_number( self.data, b'equip3_reserve_cost', equip3_reserve_cost )
        self.ssc.data_set_number( self.data, b'equip3_reserve_freq', equip3_reserve_freq )
        self.ssc.data_set_number( self.data, b'equip_reserve_depr_sta', equip_reserve_depr_sta )
        self.ssc.data_set_number( self.data, b'equip_reserve_depr_fed', equip_reserve_depr_fed )

    def todFactors(self
                   , dispatch_factor1 = 2.0639998912811279
                   , dispatch_factor2 = 1.2000000476837158
                   , dispatch_factor3 = 1
                   , dispatch_factor4 = 1.1000000238418579
                   , dispatch_factor5 = 0.80000001192092896
                   , dispatch_factor6 = 0.69999998807907104
                   , dispatch_factor7 = 1
                   , dispatch_factor8 = 1
                   , dispatch_factor9 = 1
                   , dispatch_sched_weekday = [[ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   2,   2,   2,   2,   1,   1,   1,   1,   1,   1,   2,   2,   2,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   4,   5,   5,   5 ]]
                   , dispatch_sched_weekend = [[ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3,   3 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ], [ 6,   6,   6,   6,   6,   6,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5,   5 ]]
                   , system_use_lifetime_output = 0
                   , ppa_multiplier_model = 0
                   ):
        """
        Assigns default or user-specified values to the fields under Tab : Time of Delivery Factors;
        Section: Time of Delivery (TOD) Factors of SAM
        
        :param dispatch_factor1 TOD factor for period 1:   Type: SSC_NUMBER   Require: ppa_multiplier_model=0
        :param dispatch_factor2 TOD factor for period 2:   Type: SSC_NUMBER   Require: ppa_multiplier_model=0
        :param dispatch_factor3 TOD factor for period 3:   Type: SSC_NUMBER   Require: ppa_multiplier_model=0
        :param dispatch_factor4 TOD factor for period 4:   Type: SSC_NUMBER   Require: ppa_multiplier_model=0
        :param dispatch_factor5 TOD factor for period 5:   Type: SSC_NUMBER   Require: ppa_multiplier_model=0
        :param dispatch_factor6 TOD factor for period 6:   Type: SSC_NUMBER   Require: ppa_multiplier_model=0
        :param dispatch_factor7 TOD factor for period 7:   Type: SSC_NUMBER   Require: ppa_multiplier_model=0
        :param dispatch_factor8 TOD factor for period 8:   Type: SSC_NUMBER   Require: ppa_multiplier_model=0
        :param dispatch_factor9 TOD factor for period 9:   Type: SSC_NUMBER   Require: ppa_multiplier_model=0
        :param dispatch_sched_weekday Diurnal weekday TOD periods:  [1..9]   Type: SSC_MATRIX   Require: ppa_multiplier_model=0
        :param dispatch_sched_weekend Diurnal weekend TOD periods:  [1..9]   Type: SSC_MATRIX   Require: ppa_multiplier_model=0
        
        """

        self.ssc.data_set_number( self.data, b'dispatch_factor1', dispatch_factor1 )
        self.ssc.data_set_number( self.data, b'dispatch_factor2', dispatch_factor2 )
        self.ssc.data_set_number( self.data, b'dispatch_factor3', dispatch_factor3 )
        self.ssc.data_set_number( self.data, b'dispatch_factor4', dispatch_factor4 )
        self.ssc.data_set_number( self.data, b'dispatch_factor5', dispatch_factor5 )
        self.ssc.data_set_number( self.data, b'dispatch_factor6', dispatch_factor6 )
        self.ssc.data_set_number( self.data, b'dispatch_factor7', dispatch_factor7 )
        self.ssc.data_set_number( self.data, b'dispatch_factor8', dispatch_factor8 )
        self.ssc.data_set_number( self.data, b'dispatch_factor9', dispatch_factor9 )
        self.ssc.data_set_matrix( self.data, b'dispatch_sched_weekday', dispatch_sched_weekday );
        self.ssc.data_set_matrix( self.data, b'dispatch_sched_weekend', dispatch_sched_weekend );

        # TODO: Verify the application of these inputs
        self.ssc.data_set_number( self.data, b'system_use_lifetime_output', system_use_lifetime_output )
        self.ssc.data_set_number( self.data, b'ppa_multiplier_model', ppa_multiplier_model )
        #self.ssc.data_set_array_from_csv( self.data, b'dispatch_factors_ts', b'SAM/AssociatedFiles/dispatch_factors_ts.csv');


    def incentives_ITC(self
                       , itc_fed_amount = 0
                       , itc_fed_amount_deprbas_fed = 1
                       , itc_fed_amount_deprbas_sta = 1
                       , itc_sta_amount = 0
                       , itc_sta_amount_deprbas_fed = 0
                       , itc_sta_amount_deprbas_sta = 0
                       , itc_fed_percent = 30
                       , itc_fed_percent_maxvalue = 9.9999996802856925e37
                       , itc_fed_percent_deprbas_fed = 1
                       , itc_fed_percent_deprbas_sta = 1
                       , itc_sta_percent = 0
                       , itc_sta_percent_maxvalue = 9.9999996802856925e+37
                       , itc_sta_percent_deprbas_fed = 0
                       , itc_sta_percent_deprbas_sta = 0
                       ):
        """
        Assigns default or user-specified values to the fields under Tab : Incentives;
        Section: Investment Tax Credit (ITC) of SAM
        
        :param itc_fed_amount Federal amount-based ITC amount:  [$]   Type: SSC_NUMBER   Require: ?=0
        :param itc_fed_amount_deprbas_fed Federal amount-based ITC reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param itc_fed_amount_deprbas_sta Federal amount-based ITC reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param itc_sta_amount State amount-based ITC amount:  [$]   Type: SSC_NUMBER   Require: ?=0
        :param itc_sta_amount_deprbas_fed State amount-based ITC reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param itc_sta_amount_deprbas_sta State amount-based ITC reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param itc_fed_percent Federal percentage-based ITC percent:  [%]   Type: SSC_NUMBER   Require: ?=0
        :param itc_fed_percent_maxvalue Federal percentage-based ITC maximum value:  [$]   Type: SSC_NUMBER   Require: ?=1e99
        :param itc_fed_percent_deprbas_fed Federal percentage-based ITC reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param itc_fed_percent_deprbas_sta Federal percentage-based ITC reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param itc_sta_percent State percentage-based ITC percent:  [%]   Type: SSC_NUMBER   Require: ?=0
        :param itc_sta_percent_maxvalue State percentage-based ITC maximum Value:  [$]   Type: SSC_NUMBER   Require: ?=1e99
        :param itc_sta_percent_deprbas_fed State percentage-based ITC reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param itc_sta_percent_deprbas_sta State percentage-based ITC reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0

        """

        self.ssc.data_set_number( self.data, b'itc_fed_amount', itc_fed_amount )
        self.ssc.data_set_number( self.data, b'itc_fed_amount_deprbas_fed', itc_fed_amount_deprbas_fed )
        self.ssc.data_set_number( self.data, b'itc_fed_amount_deprbas_sta', itc_fed_amount_deprbas_sta )
        self.ssc.data_set_number( self.data, b'itc_sta_amount', itc_sta_amount )
        self.ssc.data_set_number( self.data, b'itc_sta_amount_deprbas_fed', itc_sta_amount_deprbas_fed )
        self.ssc.data_set_number( self.data, b'itc_sta_amount_deprbas_sta', itc_sta_amount_deprbas_sta )
        self.ssc.data_set_number( self.data, b'itc_fed_percent', itc_fed_percent )
        self.ssc.data_set_number( self.data, b'itc_fed_percent_maxvalue', itc_fed_percent_maxvalue )
        self.ssc.data_set_number( self.data, b'itc_fed_percent_deprbas_fed', itc_fed_percent_deprbas_fed )
        self.ssc.data_set_number( self.data, b'itc_fed_percent_deprbas_sta', itc_fed_percent_deprbas_sta )
        self.ssc.data_set_number( self.data, b'itc_sta_percent', itc_sta_percent )
        self.ssc.data_set_number( self.data, b'itc_sta_percent_maxvalue', itc_sta_percent_maxvalue )
        self.ssc.data_set_number( self.data, b'itc_sta_percent_deprbas_fed', itc_sta_percent_deprbas_fed )
        self.ssc.data_set_number( self.data, b'itc_sta_percent_deprbas_sta', itc_sta_percent_deprbas_sta )


    def incentives_PTC(self
                       , ptc_fed_amount =[ 0 ]
                       , ptc_fed_term = 10
                       , ptc_fed_escal = 0
                       , ptc_sta_amount =[ 0 ]
                       , ptc_sta_term = 10
                       , ptc_sta_escal = 0
                       ):
        """
        Assigns default or user-specified values to the fields under Tab : Incentives;
        Section: Production Tax Credit (PTC) of SAM
        
        :param ptc_fed_amount Federal PTC amount:  [$/kWh]   Type: SSC_ARRAY   Require: ?=0
        :param ptc_fed_term Federal PTC term:  [years]   Type: SSC_NUMBER   Require: ?=10
        :param ptc_fed_escal Federal PTC escalation:  [%/year]   Type: SSC_NUMBER   Require: ?=0
        :param ptc_sta_amount State PTC amount:  [$/kWh]   Type: SSC_ARRAY   Require: ?=0
        :param ptc_sta_term State PTC term:  [years]   Type: SSC_NUMBER   Require: ?=10
        :param ptc_sta_escal State PTC escalation:  [%/year]   Type: SSC_NUMBER   Require: ?=0

        """
        
        self.ssc.data_set_array( self.data, b'ptc_fed_amount',  ptc_fed_amount);
        self.ssc.data_set_number( self.data, b'ptc_fed_term', ptc_fed_term )
        self.ssc.data_set_number( self.data, b'ptc_fed_escal', ptc_fed_escal )
        self.ssc.data_set_array( self.data, b'ptc_sta_amount',  ptc_sta_amount);
        self.ssc.data_set_number( self.data, b'ptc_sta_term', ptc_sta_term )
        self.ssc.data_set_number( self.data, b'ptc_sta_escal', ptc_sta_escal )



    def incentives_IBI(self
                       , ibi_fed_amount = 0 
                       , ibi_fed_amount_tax_fed = 1 
                       , ibi_fed_amount_tax_sta = 1 
                       , ibi_fed_amount_deprbas_fed = 0 
                       , ibi_fed_amount_deprbas_sta = 0 
                       , ibi_sta_amount = 0 
                       , ibi_sta_amount_tax_fed = 1 
                       , ibi_sta_amount_tax_sta = 1 
                       , ibi_sta_amount_deprbas_fed = 0 
                       , ibi_sta_amount_deprbas_sta = 0 
                       , ibi_uti_amount = 0 
                       , ibi_uti_amount_tax_fed = 1 
                       , ibi_uti_amount_tax_sta = 1 
                       , ibi_uti_amount_deprbas_fed = 0 
                       , ibi_uti_amount_deprbas_sta = 0 
                       , ibi_oth_amount = 0 
                       , ibi_oth_amount_tax_fed = 1 
                       , ibi_oth_amount_tax_sta = 1 
                       , ibi_oth_amount_deprbas_fed = 0 
                       , ibi_oth_amount_deprbas_sta = 0 
                       , ibi_fed_percent = 0 
                       , ibi_fed_percent_maxvalue = 9.9999996802856925e+37 
                       , ibi_fed_percent_tax_fed = 1 
                       , ibi_fed_percent_tax_sta = 1 
                       , ibi_fed_percent_deprbas_fed = 0 
                       , ibi_fed_percent_deprbas_sta = 0 
                       , ibi_sta_percent = 0 
                       , ibi_sta_percent_maxvalue = 9.9999996802856925e+37 
                       , ibi_sta_percent_tax_fed = 1 
                       , ibi_sta_percent_tax_sta = 1 
                       , ibi_sta_percent_deprbas_fed = 0 
                       , ibi_sta_percent_deprbas_sta = 0 
                       , ibi_uti_percent = 0 
                       , ibi_uti_percent_maxvalue = 9.9999996802856925e+37 
                       , ibi_uti_percent_tax_fed = 1 
                       , ibi_uti_percent_tax_sta = 1 
                       , ibi_uti_percent_deprbas_fed = 0 
                       , ibi_uti_percent_deprbas_sta = 0 
                       , ibi_oth_percent = 0 
                       , ibi_oth_percent_maxvalue = 9.9999996802856925e+37 
                       , ibi_oth_percent_tax_fed = 1 
                       , ibi_oth_percent_tax_sta = 1 
                       , ibi_oth_percent_deprbas_fed = 0 
                       , ibi_oth_percent_deprbas_sta = 0                        
                       ):

        """
        Assigns default or user-specified values to the fields under Tab : Incentives;
        Section: Production Tax Credit (PTC) of SAM
        
        :param ibi_fed_amount Federal amount-based IBI amount:  [$]   Type: SSC_NUMBER   Require: ?=0
        :param ibi_fed_amount_tax_fed Federal amount-based IBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_fed_amount_tax_sta Federal amount-based IBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_fed_amount_deprbas_fed Federal amount-based IBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_fed_amount_deprbas_sta Federal amount-based IBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_sta_amount State amount-based IBI amount:  [$]   Type: SSC_NUMBER   Require: ?=0
        :param ibi_sta_amount_tax_fed State amount-based IBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_sta_amount_tax_sta State amount-based IBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_sta_amount_deprbas_fed State amount-based IBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_sta_amount_deprbas_sta State amount-based IBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_uti_amount Utility amount-based IBI amount:  [$]   Type: SSC_NUMBER   Require: ?=0
        :param ibi_uti_amount_tax_fed Utility amount-based IBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_uti_amount_tax_sta Utility amount-based IBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_uti_amount_deprbas_fed Utility amount-based IBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_uti_amount_deprbas_sta Utility amount-based IBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_oth_amount Other amount-based IBI amount:  [$]   Type: SSC_NUMBER   Require: ?=0
        :param ibi_oth_amount_tax_fed Other amount-based IBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_oth_amount_tax_sta Other amount-based IBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_oth_amount_deprbas_fed Other amount-based IBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_oth_amount_deprbas_sta Other amount-based IBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_fed_percent Federal percentage-based IBI percent:  [%]   Type: SSC_NUMBER   Require: ?=0.0
        :param ibi_fed_percent_maxvalue Federal percentage-based IBI maximum value:  [$]   Type: SSC_NUMBER   Require: ?=1e99
        :param ibi_fed_percent_tax_fed Federal percentage-based IBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_fed_percent_tax_sta Federal percentage-based IBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_fed_percent_deprbas_fed Federal percentage-based IBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_fed_percent_deprbas_sta Federal percentage-based IBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_sta_percent State percentage-based IBI percent:  [%]   Type: SSC_NUMBER   Require: ?=0.0
        :param ibi_sta_percent_maxvalue State percentage-based IBI maximum value:  [$]   Type: SSC_NUMBER   Require: ?=1e99
        :param ibi_sta_percent_tax_fed State percentage-based IBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_sta_percent_tax_sta State percentage-based IBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_sta_percent_deprbas_fed State percentage-based IBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_sta_percent_deprbas_sta State percentage-based IBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_uti_percent Utility percentage-based IBI percent:  [%]   Type: SSC_NUMBER   Require: ?=0.0
        :param ibi_uti_percent_maxvalue Utility percentage-based IBI maximum value:  [$]   Type: SSC_NUMBER   Require: ?=1e99
        :param ibi_uti_percent_tax_fed Utility percentage-based IBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_uti_percent_tax_sta Utility percentage-based IBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_uti_percent_deprbas_fed Utility percentage-based IBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_uti_percent_deprbas_sta Utility percentage-based IBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_oth_percent Other percentage-based IBI percent:  [%]   Type: SSC_NUMBER   Require: ?=0.0
        :param ibi_oth_percent_maxvalue Other percentage-based IBI maximum value:  [$]   Type: SSC_NUMBER   Require: ?=1e99
        :param ibi_oth_percent_tax_fed Other percentage-based IBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_oth_percent_tax_sta Other percentage-based IBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param ibi_oth_percent_deprbas_fed Other percentage-based IBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param ibi_oth_percent_deprbas_sta Other percentage-based IBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0        

        """

        self.ssc.data_set_number( self.data, b'ibi_fed_amount', ibi_fed_amount )
        self.ssc.data_set_number( self.data, b'ibi_fed_amount_tax_fed', ibi_fed_amount_tax_fed )
        self.ssc.data_set_number( self.data, b'ibi_fed_amount_tax_sta', ibi_fed_amount_tax_sta )
        self.ssc.data_set_number( self.data, b'ibi_fed_amount_deprbas_fed', ibi_fed_amount_deprbas_fed )
        self.ssc.data_set_number( self.data, b'ibi_fed_amount_deprbas_sta', ibi_fed_amount_deprbas_sta )
        self.ssc.data_set_number( self.data, b'ibi_sta_amount', ibi_sta_amount )
        self.ssc.data_set_number( self.data, b'ibi_sta_amount_tax_fed', ibi_sta_amount_tax_fed )
        self.ssc.data_set_number( self.data, b'ibi_sta_amount_tax_sta', ibi_sta_amount_tax_sta )
        self.ssc.data_set_number( self.data, b'ibi_sta_amount_deprbas_fed', ibi_sta_amount_deprbas_fed )
        self.ssc.data_set_number( self.data, b'ibi_sta_amount_deprbas_sta', ibi_sta_amount_deprbas_sta )
        self.ssc.data_set_number( self.data, b'ibi_uti_amount', ibi_uti_amount )
        self.ssc.data_set_number( self.data, b'ibi_uti_amount_tax_fed', ibi_uti_amount_tax_fed )
        self.ssc.data_set_number( self.data, b'ibi_uti_amount_tax_sta', ibi_uti_amount_tax_sta )
        self.ssc.data_set_number( self.data, b'ibi_uti_amount_deprbas_fed', ibi_uti_amount_deprbas_fed )
        self.ssc.data_set_number( self.data, b'ibi_uti_amount_deprbas_sta', ibi_uti_amount_deprbas_sta )
        self.ssc.data_set_number( self.data, b'ibi_oth_amount', ibi_oth_amount )
        self.ssc.data_set_number( self.data, b'ibi_oth_amount_tax_fed', ibi_oth_amount_tax_fed )
        self.ssc.data_set_number( self.data, b'ibi_oth_amount_tax_sta', ibi_oth_amount_tax_sta )
        self.ssc.data_set_number( self.data, b'ibi_oth_amount_deprbas_fed', ibi_oth_amount_deprbas_fed )
        self.ssc.data_set_number( self.data, b'ibi_oth_amount_deprbas_sta', ibi_oth_amount_deprbas_sta )
        self.ssc.data_set_number( self.data, b'ibi_fed_percent', ibi_fed_percent )
        self.ssc.data_set_number( self.data, b'ibi_fed_percent_maxvalue', ibi_fed_percent_maxvalue )
        self.ssc.data_set_number( self.data, b'ibi_fed_percent_tax_fed', ibi_fed_percent_tax_fed )
        self.ssc.data_set_number( self.data, b'ibi_fed_percent_tax_sta', ibi_fed_percent_tax_sta )
        self.ssc.data_set_number( self.data, b'ibi_fed_percent_deprbas_fed', ibi_fed_percent_deprbas_fed )
        self.ssc.data_set_number( self.data, b'ibi_fed_percent_deprbas_sta', ibi_fed_percent_deprbas_sta )
        self.ssc.data_set_number( self.data, b'ibi_sta_percent', ibi_sta_percent )
        self.ssc.data_set_number( self.data, b'ibi_sta_percent_maxvalue', ibi_sta_percent_maxvalue )
        self.ssc.data_set_number( self.data, b'ibi_sta_percent_tax_fed', ibi_sta_percent_tax_fed )
        self.ssc.data_set_number( self.data, b'ibi_sta_percent_tax_sta', ibi_sta_percent_tax_sta )
        self.ssc.data_set_number( self.data, b'ibi_sta_percent_deprbas_fed', ibi_sta_percent_deprbas_fed )
        self.ssc.data_set_number( self.data, b'ibi_sta_percent_deprbas_sta', ibi_sta_percent_deprbas_sta )
        self.ssc.data_set_number( self.data, b'ibi_uti_percent', ibi_uti_percent )
        self.ssc.data_set_number( self.data, b'ibi_uti_percent_maxvalue', ibi_uti_percent_maxvalue )
        self.ssc.data_set_number( self.data, b'ibi_uti_percent_tax_fed', ibi_uti_percent_tax_fed )
        self.ssc.data_set_number( self.data, b'ibi_uti_percent_tax_sta', ibi_uti_percent_tax_sta )
        self.ssc.data_set_number( self.data, b'ibi_uti_percent_deprbas_fed', ibi_uti_percent_deprbas_fed )
        self.ssc.data_set_number( self.data, b'ibi_uti_percent_deprbas_sta', ibi_uti_percent_deprbas_sta )
        self.ssc.data_set_number( self.data, b'ibi_oth_percent', ibi_oth_percent )
        self.ssc.data_set_number( self.data, b'ibi_oth_percent_maxvalue', ibi_oth_percent_maxvalue )
        self.ssc.data_set_number( self.data, b'ibi_oth_percent_tax_fed', ibi_oth_percent_tax_fed )
        self.ssc.data_set_number( self.data, b'ibi_oth_percent_tax_sta', ibi_oth_percent_tax_sta )
        self.ssc.data_set_number( self.data, b'ibi_oth_percent_deprbas_fed', ibi_oth_percent_deprbas_fed )
        self.ssc.data_set_number( self.data, b'ibi_oth_percent_deprbas_sta', ibi_oth_percent_deprbas_sta )


    def incentives_CBI(self
                       , cbi_fed_amount =  0 
                       , cbi_fed_maxvalue =  9.9999996802856925e+37 
                       , cbi_fed_tax_fed =  1 
                       , cbi_fed_tax_sta =  1 
                       , cbi_fed_deprbas_fed =  0 
                       , cbi_fed_deprbas_sta =  0 
                       , cbi_sta_amount =  0 
                       , cbi_sta_maxvalue =  9.9999996802856925e+37 
                       , cbi_sta_tax_fed =  1 
                       , cbi_sta_tax_sta =  1 
                       , cbi_sta_deprbas_fed =  0 
                       , cbi_sta_deprbas_sta =  0 
                       , cbi_uti_amount =  0 
                       , cbi_uti_maxvalue =  9.9999996802856925e+37 
                       , cbi_uti_tax_fed =  1 
                       , cbi_uti_tax_sta =  1 
                       , cbi_uti_deprbas_fed =  0 
                       , cbi_uti_deprbas_sta =  0 
                       , cbi_oth_amount =  0 
                       , cbi_oth_maxvalue =  9.9999996802856925e+37 
                       , cbi_oth_tax_fed =  1 
                       , cbi_oth_tax_sta =  1 
                       , cbi_oth_deprbas_fed =  0 
                       , cbi_oth_deprbas_sta =  0 
                       ):

        """
        Assigns default or user-specified values to the fields under Tab : Incentives;
        Section: Capacity Based Incentives (CBI) of SAM
        
        :param cbi_fed_amount Federal CBI amount:  [$/Watt]   Type: SSC_NUMBER   Require: ?=0.0
        :param cbi_fed_maxvalue Federal CBI maximum:  [$]   Type: SSC_NUMBER   Require: ?=1e99
        :param cbi_fed_tax_fed Federal CBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param cbi_fed_tax_sta Federal CBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param cbi_fed_deprbas_fed Federal CBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param cbi_fed_deprbas_sta Federal CBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param cbi_sta_amount State CBI amount:  [$/Watt]   Type: SSC_NUMBER   Require: ?=0.0
        :param cbi_sta_maxvalue State CBI maximum:  [$]   Type: SSC_NUMBER   Require: ?=1e99
        :param cbi_sta_tax_fed State CBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param cbi_sta_tax_sta State CBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param cbi_sta_deprbas_fed State CBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param cbi_sta_deprbas_sta State CBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param cbi_uti_amount Utility CBI amount:  [$/Watt]   Type: SSC_NUMBER   Require: ?=0.0
        :param cbi_uti_maxvalue Utility CBI maximum:  [$]   Type: SSC_NUMBER   Require: ?=1e99
        :param cbi_uti_tax_fed Utility CBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param cbi_uti_tax_sta Utility CBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param cbi_uti_deprbas_fed Utility CBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param cbi_uti_deprbas_sta Utility CBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param cbi_oth_amount Other CBI amount:  [$/Watt]   Type: SSC_NUMBER   Require: ?=0.0
        :param cbi_oth_maxvalue Other CBI maximum:  [$]   Type: SSC_NUMBER   Require: ?=1e99
        :param cbi_oth_tax_fed Other CBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param cbi_oth_tax_sta Other CBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param cbi_oth_deprbas_fed Other CBI reduces federal depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param cbi_oth_deprbas_sta Other CBI reduces state depreciation basis:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0

        """
        self.ssc.data_set_number( self.data, b'cbi_fed_amount', cbi_fed_amount )
        self.ssc.data_set_number( self.data, b'cbi_fed_maxvalue', cbi_fed_maxvalue )
        self.ssc.data_set_number( self.data, b'cbi_fed_tax_fed', cbi_fed_tax_fed )
        self.ssc.data_set_number( self.data, b'cbi_fed_tax_sta', cbi_fed_tax_sta )
        self.ssc.data_set_number( self.data, b'cbi_fed_deprbas_fed', cbi_fed_deprbas_fed )
        self.ssc.data_set_number( self.data, b'cbi_fed_deprbas_sta', cbi_fed_deprbas_sta )
        self.ssc.data_set_number( self.data, b'cbi_sta_amount', cbi_sta_amount )
        self.ssc.data_set_number( self.data, b'cbi_sta_maxvalue', cbi_sta_maxvalue )
        self.ssc.data_set_number( self.data, b'cbi_sta_tax_fed', cbi_sta_tax_fed )
        self.ssc.data_set_number( self.data, b'cbi_sta_tax_sta', cbi_sta_tax_sta )
        self.ssc.data_set_number( self.data, b'cbi_sta_deprbas_fed', cbi_sta_deprbas_fed )
        self.ssc.data_set_number( self.data, b'cbi_sta_deprbas_sta', cbi_sta_deprbas_sta )
        self.ssc.data_set_number( self.data, b'cbi_uti_amount', cbi_uti_amount )
        self.ssc.data_set_number( self.data, b'cbi_uti_maxvalue', cbi_uti_maxvalue )
        self.ssc.data_set_number( self.data, b'cbi_uti_tax_fed', cbi_uti_tax_fed )
        self.ssc.data_set_number( self.data, b'cbi_uti_tax_sta', cbi_uti_tax_sta )
        self.ssc.data_set_number( self.data, b'cbi_uti_deprbas_fed', cbi_uti_deprbas_fed )
        self.ssc.data_set_number( self.data, b'cbi_uti_deprbas_sta', cbi_uti_deprbas_sta )
        self.ssc.data_set_number( self.data, b'cbi_oth_amount', cbi_oth_amount )
        self.ssc.data_set_number( self.data, b'cbi_oth_maxvalue', cbi_oth_maxvalue )
        self.ssc.data_set_number( self.data, b'cbi_oth_tax_fed', cbi_oth_tax_fed )
        self.ssc.data_set_number( self.data, b'cbi_oth_tax_sta', cbi_oth_tax_sta )
        self.ssc.data_set_number( self.data, b'cbi_oth_deprbas_fed', cbi_oth_deprbas_fed )
        self.ssc.data_set_number( self.data, b'cbi_oth_deprbas_sta', cbi_oth_deprbas_sta )




    def incentives_PBI(self
					   , pbi_fed_amount =[ 0 ]
                       , pbi_fed_term = 0 
                       , pbi_fed_escal = 0 
                       , pbi_fed_tax_fed = 1 
                       , pbi_fed_tax_sta = 1 
					   , pbi_sta_amount =[ 0 ]
                       , pbi_sta_term = 0 
                       , pbi_sta_escal = 0 
                       , pbi_sta_tax_fed = 1 
                       , pbi_sta_tax_sta = 1 
					   , pbi_uti_amount =[ 0 ]
                       , pbi_uti_term = 0 
                       , pbi_uti_escal = 0 
                       , pbi_uti_tax_fed = 1 
                       , pbi_uti_tax_sta = 1 
					   , pbi_oth_amount =[ 0 ]
                       , pbi_oth_term = 0 
                       , pbi_oth_escal = 0 
                       , pbi_oth_tax_fed = 1 
                       , pbi_oth_tax_sta = 1 
                       , pbi_fed_for_ds = 0 
                       , pbi_sta_for_ds = 0 
                       , pbi_uti_for_ds = 0 
                       , pbi_oth_for_ds = 0 
                       ):
        """
        Assigns default or user-specified values to the fields under Tab : Incentives;
        Section: Production Based Incentives (CBI) of SAM
 

        :param pbi_fed_amount Federal PBI amount:  [$/kWh]   Type: SSC_ARRAY   Require: ?=0
        :param pbi_fed_term Federal PBI term:  [years]   Type: SSC_NUMBER   Require: ?=0
        :param pbi_fed_escal Federal PBI escalation:  [%]   Type: SSC_NUMBER   Require: ?=0
        :param pbi_fed_tax_fed Federal PBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param pbi_fed_tax_sta Federal PBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param pbi_sta_amount State PBI amount:  [$/kWh]   Type: SSC_ARRAY   Require: ?=0
        :param pbi_sta_term State PBI term:  [years]   Type: SSC_NUMBER   Require: ?=0
        :param pbi_sta_escal State PBI escalation:  [%]   Type: SSC_NUMBER   Require: ?=0
        :param pbi_sta_tax_fed State PBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param pbi_sta_tax_sta State PBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param pbi_uti_amount Utility PBI amount:  [$/kWh]   Type: SSC_ARRAY   Require: ?=0
        :param pbi_uti_term Utility PBI term:  [years]   Type: SSC_NUMBER   Require: ?=0
        :param pbi_uti_escal Utility PBI escalation:  [%]   Type: SSC_NUMBER   Require: ?=0
        :param pbi_uti_tax_fed Utility PBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param pbi_uti_tax_sta Utility PBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param pbi_oth_amount Other PBI amount:  [$/kWh]   Type: SSC_ARRAY   Require: ?=0
        :param pbi_oth_term Other PBI term:  [years]   Type: SSC_NUMBER   Require: ?=0
        :param pbi_oth_escal Other PBI escalation:  [%]   Type: SSC_NUMBER   Require: ?=0
        :param pbi_oth_tax_fed Other PBI federal taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param pbi_oth_tax_sta Other PBI state taxable:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param pbi_fed_for_ds Federal PBI available for debt service:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param pbi_sta_for_ds State PBI available for debt service:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param pbi_uti_for_ds Utility PBI available for debt service:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param pbi_oth_for_ds Other PBI available for debt service:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0

        """
        self.ssc.data_set_array( self.data, b'pbi_fed_amount',  pbi_fed_amount);
        self.ssc.data_set_number( self.data, b'pbi_fed_term', pbi_fed_term )
        self.ssc.data_set_number( self.data, b'pbi_fed_escal', pbi_fed_escal )
        self.ssc.data_set_number( self.data, b'pbi_fed_tax_fed', pbi_fed_tax_fed )
        self.ssc.data_set_number( self.data, b'pbi_fed_tax_sta', pbi_fed_tax_sta )
        
        self.ssc.data_set_array( self.data, b'pbi_sta_amount',  pbi_sta_amount);
        self.ssc.data_set_number( self.data, b'pbi_sta_term', pbi_sta_term )
        self.ssc.data_set_number( self.data, b'pbi_sta_escal', pbi_sta_escal )
        self.ssc.data_set_number( self.data, b'pbi_sta_tax_fed', pbi_sta_tax_fed )
        self.ssc.data_set_number( self.data, b'pbi_sta_tax_sta', pbi_sta_tax_sta )
        
        self.ssc.data_set_array( self.data, b'pbi_uti_amount',  pbi_uti_amount);
        self.ssc.data_set_number( self.data, b'pbi_uti_term', pbi_uti_term )
        self.ssc.data_set_number( self.data, b'pbi_uti_escal', pbi_uti_escal )
        self.ssc.data_set_number( self.data, b'pbi_uti_tax_fed', pbi_uti_tax_fed )
        self.ssc.data_set_number( self.data, b'pbi_uti_tax_sta', pbi_uti_tax_sta )
        
        self.ssc.data_set_array( self.data, b'pbi_oth_amount',  pbi_oth_amount);
        self.ssc.data_set_number( self.data, b'pbi_oth_term', pbi_oth_term )
        self.ssc.data_set_number( self.data, b'pbi_oth_escal', pbi_oth_escal )
        self.ssc.data_set_number( self.data, b'pbi_oth_tax_fed', pbi_oth_tax_fed )
        self.ssc.data_set_number( self.data, b'pbi_oth_tax_sta', pbi_oth_tax_sta )

        self.ssc.data_set_number( self.data, b'pbi_fed_for_ds', pbi_fed_for_ds )
        self.ssc.data_set_number( self.data, b'pbi_sta_for_ds', pbi_sta_for_ds )
        self.ssc.data_set_number( self.data, b'pbi_uti_for_ds', pbi_uti_for_ds )
        self.ssc.data_set_number( self.data, b'pbi_oth_for_ds', pbi_oth_for_ds )

    def depreciation(self
                     , depr_alloc_macrs_5_percent =  89 
                     , depr_alloc_macrs_15_percent =  1.5 
                     , depr_alloc_sl_5_percent =  0 
                     , depr_alloc_sl_15_percent =  3 
                     , depr_alloc_sl_20_percent =  3.5 
                     , depr_alloc_sl_39_percent =  0 
                     , depr_alloc_custom_percent =  0 
                     , depr_custom_schedule =[ 0 ]        
                     , depr_bonus_sta =  0 
                     , depr_bonus_sta_macrs_5 =  1 
                     , depr_bonus_sta_macrs_15 =  1 
                     , depr_bonus_sta_sl_5 =  0 
                     , depr_bonus_sta_sl_15 =  0 
                     , depr_bonus_sta_sl_20 =  0 
                     , depr_bonus_sta_sl_39 =  0 
                     , depr_bonus_sta_custom =  0 
                     , depr_bonus_fed =  0 
                     , depr_bonus_fed_macrs_5 =  1 
                     , depr_bonus_fed_macrs_15 =  1 
                     , depr_bonus_fed_sl_5 =  0 
                     , depr_bonus_fed_sl_15 =  0 
                     , depr_bonus_fed_sl_20 =  0 
                     , depr_bonus_fed_sl_39 =  0 
                     , depr_bonus_fed_custom =  0 
                     , depr_itc_sta_macrs_5 =  1 
                     , depr_itc_sta_macrs_15 =  0 
                     , depr_itc_sta_sl_5 =  0 
                     , depr_itc_sta_sl_15 =  0 
                     , depr_itc_sta_sl_20 =  0 
                     , depr_itc_sta_sl_39 =  0 
                     , depr_itc_sta_custom =  0 
                     , depr_itc_fed_macrs_5 =  1 
                     , depr_itc_fed_macrs_15 =  0 
                     , depr_itc_fed_sl_5 =  0 
                     , depr_itc_fed_sl_15 =  0 
                     , depr_itc_fed_sl_20 =  0 
                     , depr_itc_fed_sl_39 =  0 
                     , depr_itc_fed_custom =  0 
                     ):

        """
        Assigns default or user-specified values to the fields under Tab : Depreciation of SAM
 
        :param depr_alloc_macrs_5_percent 5-yr MACRS depreciation federal and state allocation:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=89
        :param depr_alloc_macrs_15_percent 15-yr MACRS depreciation federal and state allocation:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=1.5
        :param depr_alloc_sl_5_percent 5-yr straight line depreciation federal and state allocation:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=0
        :param depr_alloc_sl_15_percent 15-yr straight line depreciation federal and state allocation:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=3
        :param depr_alloc_sl_20_percent 20-yr straight line depreciation federal and state allocation:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=3
        :param depr_alloc_sl_39_percent 39-yr straight line depreciation federal and state allocation:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=0.5
        :param depr_alloc_custom_percent Custom depreciation federal and state allocation:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=0
        :param depr_custom_schedule Custom depreciation schedule:  [%]   Type: SSC_ARRAY   Require: *
        :param depr_bonus_sta State bonus depreciation:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=0
        :param depr_bonus_sta_macrs_5 State bonus depreciation 5-yr MACRS:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param depr_bonus_sta_macrs_15 State bonus depreciation 15-yr MACRS:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_sta_sl_5 State bonus depreciation 5-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_sta_sl_15 State bonus depreciation 15-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_sta_sl_20 State bonus depreciation 20-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_sta_sl_39 State bonus depreciation 39-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_sta_custom State bonus depreciation custom:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_fed Federal bonus depreciation:  [%]   Type: SSC_NUMBER    Constraint: MIN=0,MAX=100   Require: ?=0
        :param depr_bonus_fed_macrs_5 Federal bonus depreciation 5-yr MACRS:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param depr_bonus_fed_macrs_15 Federal bonus depreciation 15-yr MACRS:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_fed_sl_5 Federal bonus depreciation 5-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_fed_sl_15 Federal bonus depreciation 15-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_fed_sl_20 Federal bonus depreciation 20-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_fed_sl_39 Federal bonus depreciation 39-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_bonus_fed_custom Federal bonus depreciation custom:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_sta_macrs_5 State itc depreciation 5-yr MACRS:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param depr_itc_sta_macrs_15 State itc depreciation 15-yr MACRS:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_sta_sl_5 State itc depreciation 5-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_sta_sl_15 State itc depreciation 15-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_sta_sl_20 State itc depreciation 20-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_sta_sl_39 State itc depreciation 39-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_sta_custom State itc depreciation custom:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_fed_macrs_5 Federal itc depreciation 5-yr MACRS:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=1
        :param depr_itc_fed_macrs_15 Federal itc depreciation 15-yr MACRS:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_fed_sl_5 Federal itc depreciation 5-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_fed_sl_15 Federal itc depreciation 15-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_fed_sl_20 Federal itc depreciation 20-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_fed_sl_39 Federal itc depreciation 39-yr straight line:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0
        :param depr_itc_fed_custom Federal itc depreciation custom:  [0/1]   Type: SSC_NUMBER    Constraint: BOOLEAN   Require: ?=0

        """

        self.ssc.data_set_number( self.data, b'depr_alloc_macrs_5_percent', depr_alloc_macrs_5_percent )
        self.ssc.data_set_number( self.data, b'depr_alloc_macrs_15_percent', depr_alloc_macrs_15_percent )
        self.ssc.data_set_number( self.data, b'depr_alloc_sl_5_percent', depr_alloc_sl_5_percent )
        self.ssc.data_set_number( self.data, b'depr_alloc_sl_15_percent', depr_alloc_sl_15_percent )
        self.ssc.data_set_number( self.data, b'depr_alloc_sl_20_percent', depr_alloc_sl_20_percent )
        self.ssc.data_set_number( self.data, b'depr_alloc_sl_39_percent', depr_alloc_sl_39_percent )
        self.ssc.data_set_number( self.data, b'depr_alloc_custom_percent', depr_alloc_custom_percent )
        self.ssc.data_set_array( self.data, b'depr_custom_schedule', depr_custom_schedule );
        self.ssc.data_set_number( self.data, b'depr_bonus_sta', depr_bonus_sta )
        self.ssc.data_set_number( self.data, b'depr_bonus_sta_macrs_5', depr_bonus_sta_macrs_5 )
        self.ssc.data_set_number( self.data, b'depr_bonus_sta_macrs_15', depr_bonus_sta_macrs_15 )
        self.ssc.data_set_number( self.data, b'depr_bonus_sta_sl_5', depr_bonus_sta_sl_5 )
        self.ssc.data_set_number( self.data, b'depr_bonus_sta_sl_15', depr_bonus_sta_sl_15 )
        self.ssc.data_set_number( self.data, b'depr_bonus_sta_sl_20', depr_bonus_sta_sl_20 )
        self.ssc.data_set_number( self.data, b'depr_bonus_sta_sl_39', depr_bonus_sta_sl_39 )
        self.ssc.data_set_number( self.data, b'depr_bonus_sta_custom', depr_bonus_sta_custom )
        self.ssc.data_set_number( self.data, b'depr_bonus_fed', depr_bonus_fed )
        self.ssc.data_set_number( self.data, b'depr_bonus_fed_macrs_5', depr_bonus_fed_macrs_5 )
        self.ssc.data_set_number( self.data, b'depr_bonus_fed_macrs_15', depr_bonus_fed_macrs_15 )
        self.ssc.data_set_number( self.data, b'depr_bonus_fed_sl_5', depr_bonus_fed_sl_5 )
        self.ssc.data_set_number( self.data, b'depr_bonus_fed_sl_15', depr_bonus_fed_sl_15 )
        self.ssc.data_set_number( self.data, b'depr_bonus_fed_sl_20', depr_bonus_fed_sl_20 )
        self.ssc.data_set_number( self.data, b'depr_bonus_fed_sl_39', depr_bonus_fed_sl_39 )
        self.ssc.data_set_number( self.data, b'depr_bonus_fed_custom', depr_bonus_fed_custom )
        self.ssc.data_set_number( self.data, b'depr_itc_sta_macrs_5', depr_itc_sta_macrs_5 )
        self.ssc.data_set_number( self.data, b'depr_itc_sta_macrs_15', depr_itc_sta_macrs_15 )
        self.ssc.data_set_number( self.data, b'depr_itc_sta_sl_5', depr_itc_sta_sl_5 )
        self.ssc.data_set_number( self.data, b'depr_itc_sta_sl_15', depr_itc_sta_sl_15 )
        self.ssc.data_set_number( self.data, b'depr_itc_sta_sl_20', depr_itc_sta_sl_20 )
        self.ssc.data_set_number( self.data, b'depr_itc_sta_sl_39', depr_itc_sta_sl_39 )
        self.ssc.data_set_number( self.data, b'depr_itc_sta_custom', depr_itc_sta_custom )
        self.ssc.data_set_number( self.data, b'depr_itc_fed_macrs_5', depr_itc_fed_macrs_5 )
        self.ssc.data_set_number( self.data, b'depr_itc_fed_macrs_15', depr_itc_fed_macrs_15 )
        self.ssc.data_set_number( self.data, b'depr_itc_fed_sl_5', depr_itc_fed_sl_5 )
        self.ssc.data_set_number( self.data, b'depr_itc_fed_sl_15', depr_itc_fed_sl_15 )
        self.ssc.data_set_number( self.data, b'depr_itc_fed_sl_20', depr_itc_fed_sl_20 )
        self.ssc.data_set_number( self.data, b'depr_itc_fed_sl_39', depr_itc_fed_sl_39 )
        self.ssc.data_set_number( self.data, b'depr_itc_fed_custom', depr_itc_fed_custom )




    def remainingParams(self):
        self.ssc.data_set_number( self.data, b'system_use_recapitalization', 0 )
        self.ssc.data_set_number( self.data, b'ppa_escalation', 1 )
        self.ssc.data_set_number( self.data, b'depr_stabas_method', 1 )
        self.ssc.data_set_number( self.data, b'depr_fedbas_method', 1 )
    


    def print_impParams(self):
        annual_energy = self.ssc.data_get_number(self.data, b'annual_energy');
        print ('Annual energy (year 1) = ', annual_energy)
        capacity_factor = self.ssc.data_get_number(self.data, b'capacity_factor');
        print ('Capacity factor (year 1) = ', capacity_factor)
        annual_total_water_use = self.ssc.data_get_number(self.data, b'annual_total_water_use');
        print ('Annual Water Usage = ', annual_total_water_use)
        ppa = self.ssc.data_get_number(self.data, b'ppa');
        print ('PPA price (year 1) = ', ppa)

        """
        lppa_nom = self.ssc.data_get_number(self.data, b'lppa_nom');
        print ('Levelized PPA price (nominal) = ', lppa_nom)
        lppa_real = self.ssc.data_get_number(self.data, b'lppa_real');
        print ('Levelized PPA price (real) = ', lppa_real)
        lcoe_nom = self.ssc.data_get_number(self.data, b'lcoe_nom');
        print ('Levelized COE (nominal) = ', lcoe_nom)
        lcoe_real = self.ssc.data_get_number(self.data, b'lcoe_real');
        print ('Levelized COE (real) = ', lcoe_real)
        flip_actual_irr = self.ssc.data_get_number(self.data, b'flip_actual_irr');
        print ('Investor IRR = ', flip_actual_irr)
        flip_actual_year = self.ssc.data_get_number(self.data, b'flip_actual_year');
        print ('Year investor IRR acheived = ', flip_actual_year)
        tax_investor_aftertax_irr = self.ssc.data_get_number(self.data, b'tax_investor_aftertax_irr');
        print ('Investor IRR at end of project = ', tax_investor_aftertax_irr)
        tax_investor_aftertax_npv = self.ssc.data_get_number(self.data, b'tax_investor_aftertax_npv');
        print ('Investor NPV over project life = ', tax_investor_aftertax_npv)
        sponsor_aftertax_irr = self.ssc.data_get_number(self.data, b'sponsor_aftertax_irr');
        print ('Developer IRR at end of project = ', sponsor_aftertax_irr)
        sponsor_aftertax_npv = self.ssc.data_get_number(self.data, b'sponsor_aftertax_npv');
        print ('Developer NPV over project life = ', sponsor_aftertax_npv)
        cost_installed = self.ssc.data_get_number(self.data, b'cost_installed');
        print ('Net capital cost = ', cost_installed)
        size_of_equity = self.ssc.data_get_number(self.data, b'size_of_equity');
        print ('Equity = ', size_of_equity)
        size_of_debt = self.ssc.data_get_number(self.data, b'size_of_debt');
        print ('Debt = ', size_of_debt)
        """
        



class sscTests(unittest.TestCase):

    def ppa_priceTest(self):
        """
        Tests if the capacity factor for one year is calculated correctly when 
        system capacity is 50000 and all other values are default values.
        """

        # TODO : implement unit tests (vvicraman)
         
if __name__ == '__main__':
    samFin = samFinPpaPartnershipFlipWithDebt()
    samFin.main()
    
    #Argument for the unit test makes sure the unit test does not fail if system_capacity 
    #system_capacity is passed as a first argument on command line.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)