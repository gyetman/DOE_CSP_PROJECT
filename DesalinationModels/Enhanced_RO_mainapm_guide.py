# Need to pip install APMonitor and add dependency in beta version
# Saving this as a guide for Zhuoran to implement into the GUI. 
# Adding on printouts of key outputs so that Zhuoran can easily navigate
# Adam A. Atia
from APMonitor.apm import *
import os
# Select server
s = 'http://byu.apmonitor.com'

# Application name
a = 'DesalinationModels'

# Clear previous application
apm(s,a,'clear all')

#APM Model Files
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).replace("\\","/") + "/EnhancedRO_APM_Models"
print(ROOT_DIR)


#LSRRO Cases: 70 g/l Feed, 75% recovery; 35 g/l Feed, 85% recovery; 20 g/l Feed, 92% recovery

LSRRO_70g_L_75rec=ROOT_DIR+'/LSRRO_8stage_cin_70_r_75.apm'
LSRRO_35g_L_85rec=ROOT_DIR+'/LSRRO_6stage_cin_35_r_85.apm'
LSRRO_20g_L_92rec=ROOT_DIR+'/LSRRO_6stage_cin_20_r_92.apm'

#COMRO 
COMRO_125g_L_50rec=ROOT_DIR+'/COMRO_3stage_cin_125_r_50.apm' 
COMRO_125g_L_25rec=ROOT_DIR+'/COMRO_1stage_cin_125_r_25.apm'
COMRO_70g_L_75rec=ROOT_DIR+'/COMRO_4stage_cin_70_r_75.apm' # relatively long to find solution
COMRO_35g_L_85rec=ROOT_DIR+'/COMRO_3stage_cin_35_r_85.apm'
COMRO_20g_L_92rec=ROOT_DIR+'/COMRO_4stage_cin_20_r_92.apm'

#OARO 
OARO_125g_L_50rec=ROOT_DIR+'/OARO_5stage_cin_125_r_50.apm'
OARO_125g_L_25rec=ROOT_DIR+'/OARO_3stage_cin_125_r_25.apm'

OARO_70g_L_75rec=ROOT_DIR+'/OARO_4stage_cin_70_r_75.apm' # Doesn't converge to same solution as MATLAB (LCOW= ~6.5 vs matlab result of 5.14); issue resolved by increasing objective function tolerance, otol, from 1e-6 to 1e-4
OARO_70g_L_50rec=ROOT_DIR+'/OARO_2stage_cin_70_r_50.apm' 

OARO_35g_L_85rec=ROOT_DIR+'/OARO_2stage_cin_35_r_85.apm' # LCOW result is a little bit higher than result in MATLAB (1.5 vs 1.4). SEC is also a little bit higher (5.3 vs 5.2)
OARO_20g_L_92rec=ROOT_DIR+'/OARO_2stage_cin_20_r_92.apm' # not converging to same sol as MATLAB; closer when changing otol from default of 1e-6 to 1e-3



# Load model file
tech=input("Choose 'OARO','COMRO', or 'LSRRO'\n")
feedsal=input("Enter feed concentration of 20,35,70, or 125 g/L (enter number only, e.g., 20)\n")


if feedsal=='20':
    recrate='92'
elif feedsal=='35':
    recrate='85'
elif feedsal=='70':
    if tech=='OARO':
        recrate=input('Enter 50 or 75 for recovery rate\n') 
    else:
        recrate='75'
elif feedsal=='125':
    recrate=input('Enter 25 or 50 for recovery rate\n') 



#testing_file= "C:/Users/adama/Google Drive/PhD Work/Plots_Figures_Images/RO_ZLD/Script_test/OARO/" + "OARO_finalized_v3_newAB_add_salt_balance_recycle_conc_change_sens_cin_rt.apm"

model_file= eval(tech + "_" + feedsal + "g_L_"+ recrate + "rec") #testing_file#

csvfilename=ROOT_DIR+'/inputdata.csv' # Naming the csv file with user inputs (works without csv filename matching model filename)

# print(csvfilename)
# print(model_file)

apm_load(s,a,model_file)
enter_data=input("Press 1 to enter input data or any other key to keep defaults\n")
if enter_data=='1':
    csv_load(s,a,csvfilename)     # Loads the input data (Parameters in the APM file)
#apm_option(s,a,'apm.csv_read',1)

#apm_option(s,a,'nlc.diaglevel',10)
apm_option(s,a,'apm.imode',3) # chooses operation mode; 3= steady-state optimization
apm_option(s,a,'apm.max_iter',1000)  # max number of iterations
apm_option(s,a,'apm.scaling',1) # activate scaling
apm_option(s,a,'apm.reduce',5) # activates reduction


if (tech=='OARO'): 
    if feedsal=='70': 
        apm_option(s,a,'apm.otol',1e-4) # default tolerance is 1e-6
    elif feedsal=='20':
        apm_option(s,a,'apm.otol',1e-3) # default tolerance is 1e-6
    elif (feedsal=='125') & (recrate=='50'):
        apm_option(s,a,'apm.otol',1e-7) # default tolerance is 1e-6

elif (tech=='COMRO'):
    if (feedsal=='125') & (recrate=='50'):
        apm_option(s,a,'apm.otol',1e-6) # default tolerance is 1e-6   

else:
    apm_option(s,a,'apm.otol',1e-6) # default tolerance is 1e-6
output = apm(s,a,'solve');

if (apm_tag(s,a,'apm.appstatus')==1):
    # retrieve solution if successful
    sol = apm_sol(s,a)
    #z = sol.x 

    rtq=sol['rtq']
    LCOW=sol['lcow']
    
    print(tech)
    print("Cin=",sol['cin'])
    print("Water Recovery Rate=",sol['rt'])
    print("Solution recovery rate=",rtq)
    print("LCOW=",LCOW,"$/m3")
    
    #print(sol['mpj[0]'])

   
    if sol['nstage']==2:
        if tech=='OARO':
            SEC=sol['secsum'] # OARO 2stage
            Cb=sol['cb']      # OARO 2stage
            Amj=sol['amjsum']
            Amk=sol['amksum']
            
        elif tech=='LSRRO':
            SEC= sol['sec']
            Cb = sol['cfjout']
            
   
        print("Brine concentration=",Cb,"g/L")

  
    elif sol['nstage']>2:
        SEC= sol['sec']
       #print("SEC=",SEC,"kWh/m3")

        if tech=='LSRRO':
            Cbstring=""""sol['cfjout[{}]']".format(int(sol['ncc']))"""
            Cb=eval(eval(Cbstring))
            Amj=eval(eval(""""sol['amjsum[{}]']".format(int(sol['ncc']))""")) 
            Amk=sol['amksum']           
      
        elif tech=='COMRO':
            Cbstring=""""sol['cfoutj[{}]']".format(int(sol['nstage']))"""   ########## may want to change variable name for final brine concentration to match in all technologies (right now, cfoutj vs cfjout)
            Cb=eval(eval(Cbstring))
            Amj=eval(eval(""""sol['amjsum[{}]']".format(int(sol['nstage']))""")) 
            Amk=eval(eval(""""sol['amksum[{}]']".format(int(sol['nstage']))""")) 
            
        elif tech=='OARO':
            Cb=sol['cfout']
            Amj=eval(eval(""""sol['amjsum[{}]']".format(int(sol['ncc']))""")) 
            Amk=sol['amksum']
    elif (tech=='COMRO') & (sol['nstage']==1):
        Amj=sol['amj1']
        Amk=sol['amk1']       
        SEC=sol['sec']
        Cb=sol['cfoutj']
        
    print("SEC=",SEC,"kWh/m3")
    print("Brine concentration=",Cb,"g/L")       
    print("Cost of electricity=",sol['ecost'],"$/kWh")     
    
   
        
    print("Number of stages=",sol['nstage'])
    
    print("Total specialized membrane area=",Amj)
    print("Total conventional RO membrane area=",Amk)
    print("pump efficiency=",sol['eff_pump'])
    print("ERD efficiency=",sol['eff_erd'])
else:
    # % not successful, retrieve infeasiblilities report
    apm_get(s,a,'infeasibilities.txt')
    # disp(output)
# print(csvfilename)
# print(model_file)






# Load time points for future predictions
#csv_load(server,app,'cstr.csv')

# Load replay replay data for local use
#data = csv.reader(open('replay.csv', 'r'))
#data = csv.reader(open('replay1.csv', 'r'))
#data = csv.reader(open('replay2.csv', 'r'))
#data = csv.reader(open('replay3.csv', 'r'))
#replay = []
#for row in data:
#	replay.append(row)
#len_replay = len(replay)

# APM Variable Classification
# class = FV, MV, SV, CV
#   F or FV = Fixed value - parameter may change to a new value every cycle
#   M or MV = Manipulated variable - independent variable over time horizon
#   S or SV = State variable - model variable for viewing
#   C or CV = Controlled variable - model variable for control

#Parameters
# FVs = 'v','rho','cp','mdelh','eoverr','k0','ua'
# MVs = 'tc','q','caf','tf'

# #Variables
# SVs = 'ca','---'
# CVs = 't','---'

# # Set up variable classifications for data flow
# for x in FVs: apm_info(server,app,'FV',x)
# for x in MVs: apm_info(server,app,'MV',x)
# for x in SVs: apm_info(server,app,'SV',x)
# for x in CVs: apm_info(server,app,'CV',x)

# # Options

# # controller mode (1=simulate, 2=predict, 3=control)
# #apm_option(server,app,'nlc.reqctrlmode',3)

# # time units (1=sec,2=min,3=hrs,etc)
# apm_option(server,app,'nlc.ctrl_units',2)
# apm_option(server,app,'nlc.hist_units',2)

# # set controlled variable error model type
# apm_option(server,app,'nlc.cv_type',1)
# apm_option(server,app,'nlc.ev_type',1)
# apm_option(server,app,'nlc.reqctrlmode',2)

# # read discretization from CSV file
# apm_option(server,app,'nlc.csv_read',1)

# # turn on historization to see past results
# apm_option(server,app,'nlc.hist_hor',500)

# # set web plot update frequency
# apm_option(server,app,'nlc.web_plot_freq',10)


# # Objective for Nonlinear Control

# # Controlled variable (c)
# apm_option(server,app,'t.sp',303)
# apm_option(server,app,'t.sphi',305)
# apm_option(server,app,'t.splo',300)
# apm_option(server,app,'t.tau',10.0)
# apm_option(server,app,'t.status',1)
# apm_option(server,app,'t.fstatus',0)

# # Manipulated variables (u)
# apm_option(server,app,'tc.upper',300)
# apm_option(server,app,'tc.dmax',10)
# apm_option(server,app,'tc.lower',0)
# apm_option(server,app,'tc.status',1)
# apm_option(server,app,'tc.fstatus',1)

# # imode (1=ss, 2=mpu, 3=rto, 4=sim, 5=mhe, 6=nlc)
# apm_option(server,app,'nlc.imode',1)
# solver_output = apm(server,app,'solve')
# apm_option(server,app,'nlc.imode',6)

# for isim in range(1, len_replay-1):
	# print('')
	# print('--- Cycle %i of %i ---' %(isim,len_replay-2))

	# # allow server to process other requests
	# time.sleep(0.1)

	# for x in FVs:
		# value = csv_element(x,isim,replay)
		# if (not math.isnan(value)):
			# response = apm_meas(server,app,x,value)
			# print(response)
	# for x in MVs:
		# value = csv_element(x,isim,replay)
		# if (not math.isnan(value)):
			# response = apm_meas(server,app,x,value)
			# print(response)
	# for x in CVs:
		# value = csv_element(x,isim,replay)
		# if (not math.isnan(value)):
			# response = apm_meas(server,app,x,value)
			# print(response)

	# # schedule a set point change at cycle 40
	# #if (isim==4): apm_option(server,app,'volume.sp',50)

	# # Run NLC on APM server
	# solver_output = apm(server,app,'solve')
	# print(solver_output)

	# if (isim==1):
		# # Open Web Viewer and Display Link
		# print("Opening web viewer")
		# url = apm_web(server,app)

	# # Retrieve results (MEAS,MODEL,NEWVAL)
	# # MEAS = FV, MV,or CV measured values
	# # MODEL = SV & CV predicted values
	# NEWVAL = FV & MV optimized values