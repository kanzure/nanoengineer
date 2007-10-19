# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

"""
platform.py -- provide the atom_debug developer debugging flag.

TODO: rename this module and the flag. (Hard, since lots of uses.)
And, change some of the uses into more specific debugging flags.

$Id$

Notes:

atom_debug can be set on startup from an environment variable,
or by a developer directly editing this file in their local copy.
(See this module's code for details.)

It can be changed during one session of NE1 using the ATOM_DEBUG
checkmark item in the GLPane debug menu.

It is not persistent between sessions.

TODO: document code usage notes -- how to use it, what to use it for.
"""

import os

# Developers who want atom_debug to start out True on every launch
# can uncomment the following line -- but don't commit that change!

## atom_debug = True

# WARNING: having atom_debug set from startup is currently broken,
# at least when ALTERNATE_CAD_SRC_PATH is being used. It causes code
# to run which doesn't otherwise run, and which fails with fatal tracebacks.
# I don't know why, or for how long this has been true. I used to start
# with it set all the time, but that was a few months back and before I
# routinely used ALTERNATE_CAD_SRC_PATH (in which state I've never before
# started with it set). [bruce 071018]

# ==

try:
    atom_debug # don't disturb it if already set (e.g. by .atom-debug-rc)
except:
    try:
        atom_debug = os.environ['ATOM_DEBUG'] # as a string; should be "1" or "0"
    except:
        atom_debug = 0
    try:
        atom_debug = int(atom_debug)
    except:
        pass
    atom_debug = not not atom_debug

if atom_debug:
    print "fyi: user has requested ATOM_DEBUG feature; extra debugging code enabled; might be slower"

# end
