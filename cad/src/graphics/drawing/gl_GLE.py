# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
gl_GLE.py - Details of loading the GLE functions.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

russ 080523: Factored out duplicate code from CS_draw_primitives.py,
    CS_workers.py, and drawers.py .
"""

try:
    from OpenGL.GLE import glePolyCone, gleGetNumSides, gleSetNumSides
except:
    print "GLE module can't be imported. Now trying _GLE"
    from OpenGL._GLE import glePolyCone, gleGetNumSides, gleSetNumSides

# Check if the gleGet/SetNumSides function is working on this install, and if
# not, patch it to call gleGet/SetNumSlices. Checking method is as recommended
# in an OpenGL exception reported by Brian [070622]:
#   OpenGL.error.NullFunctionError: Attempt to call an
#   undefined function gleGetNumSides, check for
#   bool(gleGetNumSides) before calling
# The underlying cause of this (described by Brian) is that the computer's
# OpenGL has the older gleGetNumSlices (so it supports the functionality), but
# PyOpenGL binds (only) to the newer gleGetNumSides.  I [bruce 070629] think
# Brian said this is only an issue on Macs.
if not bool(gleGetNumSides):
    # russ 080522: Replaced no-op functions with a patch.
    print "fyi: Patching gleGetNumSides to call gleGetNumSlices instead."
    from graphics.drawing.gleNumSides_patch import gleGetNumSides
    from graphics.drawing.gleNumSides_patch import gleSetNumSides

    # russ 081227: The no-ops may still be needed, e.g. on Fedora 10 Linux.
    try:
        gleGetNumSides()
    except:
        print "fyi: Neither gleGetNumSides nor gleGetNumSlices is supported."
        print "fyi: No-ops will be used for gleGetNumSides and gleSetNumSides."
        gleGetNumSides = int
        gleSetNumSides = int
        pass
    pass
