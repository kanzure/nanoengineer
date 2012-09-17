# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
debug_flags.py -- provide the atom_debug developer debugging flag,
and other debugging flags which might be changed at runtime.

TODO: rename atom_debug, and perhaps change some of its uses
into more specific debugging flags.

@author: Bruce
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

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

# ==

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

# ==

# debug flags for dna updater, controlled by debug_prefs
# in dna_updater.dna_updater_prefs.
# The default values set here don't matter, afaik,
# since they are replaced by debug_pref values before use.
# [bruce 080228 moved these here]

DEBUG_DNA_UPDATER_MINIMAL = True

DEBUG_DNA_UPDATER = True

DEBUG_DNA_UPDATER_VERBOSE = False

DNA_UPDATER_SLOW_ASSERTS = True

# end
