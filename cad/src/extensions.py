# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
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

How to build:

% make pyx

(see also the wiki page listed above)

How to test:

[updated, bruce 070904; tested now and works on my Mac]

optional: in this source file, change debug_pyrex_test to True below.
But don't commit that change.

In NE1's run py code debug menu item, type "import extensions";
review the console prints for whether this succeeded;
then use debug menu -> other -> count bonds.
If it failed, follow build instructions in README-Pyrex and/or pyrex_text.pyx.
(I don't know how similar your python environment needs to be to NE1's for that to work.)

Possible errors when you run "import extensions":

ImportError: No module named pyrex_test -- you need to build it, e.g. "make pyx" in cad/src.

Fatal Python error: Interpreter not initialized (version mismatch?) -- this is
a Mac-specific problem related to the old bug 1724, caused by an interaction
between an Apple bug, a link error on our part, and having another Python
installed on your Mac -- typically in /Library/Frameworks. When this happens to
me, I can fix it by running the shell commands:

% cd /Library/Frameworks/Python.framework/Versions
% sudo mv 2.3 2.3-DISABLED

and rerunning NE1.

(That problem may occur, and the above fix works for me, whether I run NE1
directly as a developer or use the (Mac-specific) ALTERNATE_CAD_SRC_PATH
feature.)
"""
__author__ = 'bruce'

have_pyrex_test = False

debug_pyrex_test = False ## was platform.atom_debug, changed to 0 for A7 release by bruce 060419

import env
from debug import register_debug_menu_command, call_func_with_timing_histmsg, print_compact_traceback

try:
    from pyrex_test import nbonds
    #e verify it's up-to-date? (could ask it for version and compare to a hardcoded version number in this file...)
    #e run a self-test and/or run our own test on it?
    have_pyrex_test = True
except:
    if debug_pyrex_test: ### this condition will become "if 1" when developers are required to have Pyrex installed
        print_compact_traceback("debug_pyrex_test: exception importing pyrex_test or something inside it: ")
        print "debug_pyrex_test: Can't import pyrex_test; we'll define stub functions for its functions,"
        print "but trying to use them will raise an exception; see README-Pyrex for how to fix this."
    
    def nbonds(mols): # stub function; in some cases it might be useful to define a correct but slow stub instead of a NIM stub
        "stub function for nbonds"
        assert 0, "nbonds NIM, since we couldn't import pyrex_test extension module; see README-Pyrex"
        pass
    pass

# whether we now have the real nbonds or a stub function, make it available for testing in a menu.

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
