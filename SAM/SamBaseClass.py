

from SAM.PySSC import PySSC
import logging

class SamBaseClass(object):
    """description of class"""

    def __init__(self):
        #Sets up logging for the SAM Modules
        _setup_logging()

    ssc = PySSC()
    data = ssc.data_create()

    def create_ssc_module(self):
        try:
            self.ssc.module_exec_set_print(0)        
            return self.data
        except Exception:
            self.logger.critical("Exception occurred while creating the SAM module. Please see the detailed error message below", exc_info=True)


    def module_create_execute(self, module, ssc, data):
        try:
            self.logger.debug("Running execute statements for the SAM module '" + module + "'.")
            module = ssc.module_create(b'' + module.encode("ascii", "backslashreplace"))	
            self.ssc.module_exec_set_print( 0 );
            if ssc.module_exec(module, data) == 0:
                print (module + ' simulation error')
                idx = 1
                msg = ssc.module_log(module, 0)
                while (msg != None):
                    print ('	: ' + msg.decode("utf - 8"))
                    msg = ssc.module_log(module, idx)
                    idx = idx + 1
                SystemExit( "Simulation Error" );
            self.ssc.module_free(module)
        except Exception:
            self.logger.critical("Exception occurred while executing the SAM module. Please see the detailed error message below", exc_info=True)

    def data_free(self):
        self.ssc.data_clear(self.data)

    #Setup logging for the SAM modules
    def _setup_logging(self, className, verbose=False, level = logging.INFO):
        # create logger
        logging.basicConfig(level=logging.DEBUG)
        #The below statement works only once. New loggers have to be created for each module.
        self.logger = logging.getLogger(className)
        #logger.setLevel(logging.DEBUG)
    
        # create console handler and set level to debug - echo to the output - on DOS or anything
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
    
        # create file handler and set level to warning - log level for file
        fh = logging.FileHandler('./logs/applog.log')
        fh.setLevel(logging.INFO)
    
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # add formatter to ch    
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
    
        # add ch to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    
        # test statements; note the use of "logger" instead of "logging";
        # using the latter will still work for the default logger but will not
        # write anything to a file. 
        self.logger.info('Logger started.')
        self.logger.debug('detailed statements here...')
        self.logger.warning('Warning message! Be forewarned!')
        self.logger.critical('Critical error, omg!')