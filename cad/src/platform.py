# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

import os

# atom_debug variable:

# When we start, figure out whether user wants to enable general debugging code
# which turns on extra internal error checking (perhaps slowing down the code).
# There is no need to document this, since it is intended for developers familiar
# with the python code.
# I put this into platform.py in case the way of initializing it is platform-specific.
# If we think of a more sensible place to put this, we can move it. [bruce 041103]

try:
    atom_debug # don't disturb it if already set (e.g. by .atom-debug-rc)
except:
    try:
        atom_debug = os.environ['ATOM_DEBUG'] # as a string; suggest "1" or "0"
    except:
        atom_debug = 0
    try:
        atom_debug = int(atom_debug)
    except:
        pass
    atom_debug = not not atom_debug

if atom_debug:
    print "fyi: user has requested ATOM_DEBUG feature; extra debugging code enabled; might be slower"
