import traceback
import sys
import re
import os
from pprint import PrettyPrinter
from time import localtime, strftime
from datetime import datetime

from helpers_config import DLOG, mainswitch

# TODO 
# various log levels
# remove compatibilty (when projects upgraded)
# cleanup


class Flogger:
    """ 
    logging
    configurable in central file to enable logging  
    seperately for each module in codebase
    hierarchical inheritance of log level and enabling if wanted
    """
    # regexp fuer stacktrace line - nur filename
    #expr = re.compile('.+/([^/]+\.py)", (line \d+, in \w+)\n.+')

    #trace_raw = '  File "'+subroot+'(.*\.py)", (line \d+, in \w+)\n.+'
    def __init__(self, mainswitch=True):
        self.prefix = ''
        self.trace_lnr = -3
        self.tr_lnr = -3
        self.mainswitch = mainswitch
        # read config which modules to log
        self.modules_tolog = []
        self.root = os.getcwd()
        self.sub = ''

    def set_globals(self):
        self.subroot = self.root+self.sub
        modules = file(self.subroot+'/flogger/helpers_config_mod.txt','r').readlines()
        for m in modules:
            if m.startswith('#') or m.startswith("\n"):
                continue
            self.modules_tolog.append(m.strip("\n"))
        self.expr = re.compile('  File "'+self.subroot+'/(.*\.py)", (line \d+, in \w+)\n.+')

        self.today = strftime('%Y-%m-%d')
        ldir = os.path.join(DLOG, self.today)
        # prefix can be set from application, ie for per-user log files
        if not self.prefix:
            self.prefix = 'ZZ_main'
        self.fn = self.prefix +'.log'

        self.logfn = os.path.join(ldir, self.fn)
        if not os.path.exists(ldir):
            os.makedirs(ldir)
            f = file(self.logfn, "w")
            f.close()
        self.f = file(self.logfn, "a")


    def dlog(self, var, v):
        """ old logging method, for compatibility to old flolog """
        self.tr_lnr = self.trace_lnr - 1
        return self.nlog(var, v=v)
        #return self.dlog(l+": "+var, v)

    def llog(t, alist):
        """ prepare list for logging  - unused!  """
        f = file( self.logfile, "a" )
        line = '=========== '
        line += t
        line += "\n"
        for i in alist:
            line += i
            line += "\n"
        f.write(line)


    def nlog(self, var, l=None, v=True):
        """ new logging, varname and content separate """
        if (not v or not self.mainswitch):
            return

        ### traceback check relevant line and match
        tracelines = traceback.format_stack()
        self.f.write('trace_lnr '+str(self.tr_lnr)+"\n")
        s = tracelines[self.tr_lnr] 
        self.f.write(str("\n".join(tracelines)))
        self.f.write("s: "+str(s))
        m = self.expr.match( s )
        if not m:
            line = "dlog:err eval strack expr # "
            line += var +  "\n"
            self.f.write(line)
            return

        ### check which module calls and if logging should be done
        fn = m.group(1)
        basef = os.path.splitext(fn)[0]
        if basef not in self.modules_tolog: return

        ### variable check
        out = ''
        try:
            if type(var) == type(u''):
                out += var.encode('utf8')
                out += " - (dlog:to UTF8)"
            elif type(var) == type(''):
                out += var
                out += " - (dlog:string)"
            else:
                try:
                    pp = PrettyPrinter()
                    out += pp.pprint( var )
                except:
                    out += str(var)

        except:
            out += " dlog:exception "

        # prefix with label if given
        if l:
            out = l +': \t'+out

        method = m.group(2)
        mth = method.split(" ")
        lnr = mth[1][:-1]
        mout = mth[3]

        tstamp = strftime("%H:%M:%S",localtime())
        llen1 = 9+len(fn) #  
        ltab1 = (6-int( llen1/8+2 ))
        # build log line
        line1 = "\n%s %s %s %s: %s" %(
            tstamp,
            fn,
            "\t"*ltab1,
            lnr,
            mout,
        ) 
        # tab calculation 
        llen = len(lnr+mout)+2+ llen1+ 8*(ltab1-1)
        ltab =(10-int( llen/8 ))

        # for long texts
        out_len = len(out)
        if out_len < 100:
            line1 += "\t"*ltab
            line = line1+out
        elif out_len <200:
            line = "%s\n%s" %(line1, out)
        else:
            line = "%s\n%s" %(line1, out)
            line += "\n"+"_"*90

        ### WRITE TO FILE
        self.f.write( line )
        #self.f.write( str( (llen1, ltab1, llen, ltab) ) )


### compat, remove in new projects using nlog
def dlog(var, v):
    flogger = Flogger()
    flogger.set_globals()
    """ wrapper for compat """
    flogger.tr_lnr = -3      # one stacklevel deeper from here
    return flogger.dlog(var, v)




