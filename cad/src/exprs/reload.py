# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

"""
reload.py -- handle dynamic reloading of code for developers

$Id$
"""

import platform
import EndUser
from debug import reload_once_per_event

ENABLE_RELOAD = True and platform.atom_debug

# WARNING: the reload feature implemented herein has become broken, probably
# ever since the confirmation corner started importing exprs modules without
# using reload_once. Its calls were then significantly modified when import *
# was removed from exprs, which may have further broken it, but this is
# unknown. It should be considered dead until it can be analyzed and fixed,
# or preferably, replaced with a better feature. The above init of ENABLE_RELOAD
# is safe enough for now, since it only sets it when ATOM_DEBUG is turned on
# before this module is first imported (probably at startup due to confirmation
# corner imports of other exprs modules -- not sure). [bruce 070829 comment]

def reload_once(module):
    """
    This function is used to support automatic runtime reloading of modules
    within this package, for developer convenience. To use it, add this code
    before any import of symbols from a module (or use this code in place of
    any direct import of a module):

      import module
      reload_once(module)

    Warning: not all modules support runtime reload. Those that don't should
    say so in their docstrings.
    
    Warning: this system does not yet properly handle indirect imports, when
    only the inner module has been modified. See code comments for details,
    especially the docstring of debug.reload_once_per_event(). As a workaround,
    if A imports B and you edit B.py, also edit A.py in order to trigger the
    desired runtime reload of B.py.
    """

    # this comment become obsolete when exprs.basic was split into separate files:    
    ##Note: this function's module (exprs.basic itself) is fast and harmless enough to reload that it can be
    ##reloaded on every use, without bothering to use reload_once. Therefore, external callers of anything
    ##in the exprs package can always "import basic;reload(basic)" first, and if they do, all modules within
    ##exprs can just start with "from basic import *". But for clarity, some of them call reload_once on basic too.
    
    if (not EndUser.enableDeveloperFeatures()): #070627 precaution; should improve by making this only affect default value of a debug_pref ###TODO
        return
    
    if not ENABLE_RELOAD:
        def printfyi(msg): # WARNING: dup code, inlining py_utils version since not yet imported
            msg = "fyi (printonce): " + msg
            from env import seen_before
            if not seen_before(msg):
                print msg
        if 1:
            ## printfyi( "exprs modules won't be reloaded during this session" ) # 070627 removed this
            return
    from testdraw import vv
    reload_once_per_event(module, always_print = True, never_again = False, counter = vv.reload_counter, check_modtime = True)

# end
