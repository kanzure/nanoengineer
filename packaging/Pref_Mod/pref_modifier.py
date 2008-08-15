import os
from preferences import prefs_context
import sys
import getopt
import NE1_Build_Constants

prefs = prefs_context()

if os.name=="nt":
    capture_console = False
    capture_file = ""
    # if it's not reporting as python is the executable
    if not sys.executable.upper().endswith("PYTHON.EXE") and \
       not sys.executable.upper().endswith("PYTHON"):
        try:
            capture_file = u"".join((sys.executable[:-4], "_console.log"))
            sys.stdout = open(capture_file, 'w')
            capture_console = True # already trapped, don't try more.
        except:
            pass
    if not capture_console:
        # Haven't captured the console log yet.  Find the default user
        # path and try to capture there this happens if we can't write to
        # the normal log location, or if python.exe is the executable.
        tmpFilePath = os.path.normpath(os.path.expanduser("~/Nanorex/"))
        if not os.path.exists(tmpFilePath): #If it doesn't exist
            try:
                os.mkdir(tmpFilePath) #Try making one
                capture_console = True 
            except:
                pass
                # we tried, but there's no easy way to capture the console
        if capture_console or os.path.isdir(tmpFilePath):
            try: # We made the directory or it already existed, try
                    # creating the log file.
                capture_file = os.path.normpath(u"".join((tmpFilePath,\
                                                          "/NE1_console.log")))
                sys.stdout = open(capture_file, 'w')
                capture_console = True
            except:
                print >> sys.__stderr__, \
                      "Failed to create any console log file."
                capture_console = False


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
prefstmp[key]=valueset  #set up the dict for the database update function
    # valueset will be a string or a boolean

prefs.update(prefstmp) # modifies bsddb-shelf

# also write the key/value pair to a text file next to the prefs db
# for later use by NE1 [bruce 080505 for v1.0.1]

_tmpary = NE1_Build_Constants.NE1_RELEASE_VERSION.split(".")
if len(_tmpary) >= 3:
    DEFAULT_PREFS_BASENAME = "default_prefs_v%s-%s-%s.txt" % \
                           (_tmpary[0], _tmpary[1], _tmpary[2])
else:
    DEFAULT_PREFS_BASENAME = "default_prefs_v%s-%s.txt" % \
                           (_tmpary[0], _tmpary[1])

try:
    from preferences import find_or_make_Nanorex_directory
    nanorex = find_or_make_Nanorex_directory()
    filename = os.path.join( nanorex, "Preferences", DEFAULT_PREFS_BASENAME )
    # assume this file's directory exists, since the prefs db (in the same
    # directory) has been created and written to by the code above
    file = open(filename, "a")
    def encode(string1):
        string1 = string1.replace('\\', r'\\')
        string1 = string1.replace('=', r'\=')
        string1 = string1.replace('\n', r'\n')
        string1 = string1.replace('\r', r'\r')
        return string1
    file.write("%s = %s\n" % (encode(key), encode(str(valueset))))
    print "appended to", filename
except:
    print "ignoring exception while appending to", DEFAULT_PREFS_BASENAME
    pass

# end
