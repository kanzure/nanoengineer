# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
extensions.py

Someday: handle all our custom extension modules.

For now:
Python interface to experimental Pyrex code -- mainly just needs to fail gracefully
if its compiled form (a Python extension) is not there, or doesn't work in a drastic way.
In future, might also make sure it's up-to-date, tell you how to remake it if not,
and handle all extensions instead of just one or just Pyrex extensions.

$Id$

This can't be called pyrex_test.py since then "import pyrex_test" would be ambiguous.
We want that to import the extension module... and this file might as well evolve
to try to handle all the extensions at once, so it gets a different more general name.

This fits the idea that this module contains only rarely-edited glue code,
with the real development action in the Pyrex source code (.pyx file).

For plans and status related to our use of Pyrex, see:

  http://www.nanoengineer-1.net/mediawiki/index.php?title=Integrating_Pyrex_into_the_Build_System

See README-Pyrex for the list of related files and their roles.

'''
__author__ = 'bruce'

have_pyrex_test = False

import platform
import env
from debug import register_debug_menu_command, call_func_with_timing_histmsg, print_compact_traceback

try:
    import pyrex_test
    from pyrex_test import nbonds
    #e verify it's up-to-date? (could ask it for version and compare to a hardcoded version number in this file...)
    #e run a self-test and/or run our own test on it?
    have_pyrex_test = True
except:
    if platform.atom_debug: ### this condition will become "if 1" when developers are required to have Pyrex installed
        print_compact_traceback("atom_debug: exception importing pyrex_test or something inside it: ")
        print "atom_debug: Can't import pyrex_test; we'll define stub functions for its functions,"
        print "but trying to use them will raise an exception; see README-Pyrex for how to fix this."
    
    def nbonds(mols): # stub function; in some cases it might be useful to define a correct but slow stub instead of a NIM stub
        "stub function for nbonds"
        assert 0, "nbonds NIM, since we couldn't import pyrex_test extension module; see README-Pyrex"
        pass
    pass

# whether we now have the real nbonds or a stub function, make it available for testing it in a menu.

def count_bonds_cmd( target):
    win = target.topLevelWidget()
    assy = win.assy
    part = assy.tree.part
    mols = part.molecules
    env.history.message( "count bonds (twice each) in %d mols:" % len(mols) ) 
    def doit():
        return nbonds(mols)
    nb = call_func_with_timing_histmsg( doit)
    env.history.message("count was %d, half that is %d" % (nb, nb/2) )
    return

if have_pyrex_test:
    register_debug_menu_command("count bonds (pyrex_test)", count_bonds_cmd)
else:
    register_debug_menu_command("count bonds (stub)", count_bonds_cmd)

# end
