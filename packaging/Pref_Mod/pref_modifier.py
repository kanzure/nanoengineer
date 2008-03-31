import os
from preferences import prefs_context
import sys
import getopt
  
prefs = prefs_context()

if os.name=="nt":  #Windows machines spawn and remove the shell, so no info is normally captured
    try: #The next lines until the sys.stdout were taken and modified from PlatformDependent.py
        capture_con=True
        tmpFilePath = os.path.normpath(os.path.expanduser("~/Nanorex/")) #Find the default user path
        if not os.path.exists(tmpFilePath): #If it doesn't exist
            try:
                os.mkdir(tmpFilePath) #Try making one
            except:
                capture_con=False # we tried, but there's no easy way to capture the console
        if capture_con:
            sys.stdout = open(os.path.normpath(tmpFilePath+"/prefs-run.log"), 'w')
            sys.stderr = open(os.path.normpath(tmpFilePath+"/prefs-err.log"), 'w')
    except:
        pass

from prefs_constants import qutemol_enabled_prefs_key
from prefs_constants import qutemol_path_prefs_key
from prefs_constants import nanohive_enabled_prefs_key
from prefs_constants import nanohive_path_prefs_key
from prefs_constants import povray_enabled_prefs_key
from prefs_constants import povray_path_prefs_key
from prefs_constants import megapov_enabled_prefs_key
from prefs_constants import megapov_path_prefs_key
from prefs_constants import povdir_enabled_prefs_key
from prefs_constants import gamess_enabled_prefs_key
from prefs_constants import gmspath_prefs_key
from prefs_constants import gromacs_enabled_prefs_key
from prefs_constants import gromacs_path_prefs_key
from prefs_constants import cpp_enabled_prefs_key
from prefs_constants import cpp_path_prefs_key
from prefs_constants import nv1_enabled_prefs_key
from prefs_constants import nv1_path_prefs_key

def parseopts(optslist):
    global keyset,valueset,exitset
    #use of globals is generally bad.  If this program gets bigger, this 
    #should be rewritten
    for oneopt in optslist:
        if oneopt[0]=="-K" or oneopt[0]=="-k":
            keyset=oneopt[1]
        if oneopt[0]=="-V" or oneopt[0]=="-v":
            valueset=oneopt[1]
            if valueset.upper()=="TRUE":
                valueset=True
            elif valueset.upper()=="FALSE":
                valueset=False
    if keyset=="" or valueset=="":
        exitset=True 

#re-define the variables needed into a dictionary to make calling them
#easier from the command line input
prefkeys={}
prefkeys["qutemol_enabled"]=qutemol_enabled_prefs_key
prefkeys["qutemol_path"]=qutemol_path_prefs_key
prefkeys["nanohive_enabled"]=nanohive_enabled_prefs_key
prefkeys["nanohive_path"]=nanohive_path_prefs_key
prefkeys["povray_enabled"]=povray_enabled_prefs_key
prefkeys["povray_path"]=povray_path_prefs_key
prefkeys["megapov_enabled"]=megapov_enabled_prefs_key
prefkeys["megapov_path"]=megapov_path_prefs_key
prefkeys["povdir_enabled"]=povdir_enabled_prefs_key
prefkeys["gamess_enabled"]=gamess_enabled_prefs_key
prefkeys["gamess_path"]=gmspath_prefs_key
prefkeys["gromacs_enabled"]=gromacs_enabled_prefs_key
prefkeys["gromacs_path"]=gromacs_path_prefs_key
prefkeys["cpp_enabled"]=cpp_enabled_prefs_key
prefkeys["cpp_path"]=cpp_path_prefs_key
prefkeys["nv1_enabled"]=nv1_enabled_prefs_key
prefkeys["nv1_path"]=nv1_path_prefs_key

#determining if everything needed from the command line is there.
keyset=valueset=""
exitset=False
#progopts stores the arguments passed to it from the command line
try: 
    progopts=getopt.getopt(sys.argv[1:],"k:K:v:V:")
except:
    exitset=True
    
#start of actual main program
progopts=progopts[0]
parseopts(progopts)
if exitset:
    print "Usage: pref_modifier -K <key value> -V <value to store>"
    sys.exit(0)

key=prefkeys[keyset]    #set the key value to that used by the database
print keyset
print valueset
print key

prefstmp={}
prefstmp[key]=valueset  #set up the dict for the database update funtion
prefs.update(prefstmp)
