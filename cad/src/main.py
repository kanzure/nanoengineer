#! /usr/bin/python
# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
main.py -- the initial startup file for NanoEngineer-1, treated specially
by the release-building process.

$Id$

This file should not be imported as the "main" module -- doing so
prints a warning [as of 050902] and doesn't run the contained code.
If necessary, it can be imported as the __main__ module
from within the NE1 process it starts, by "import __main__".
Such an import doesn't rerun the contained code -- only reload(__main__)
would do that, and that should not be done.

Depending on the details of the package building process,
this file might be renamed and/or moved to a different directory
from the other modules under cad/src. As of 050902, it's always
moved to a different directory (by package building on any platform),
and this is detected at runtime (using __main__.__file__) as a way
of distinguishing end-user runs from developer runs [by code now
located somewhere inside the startup package, as of 071008].

When an end-user runs the NE1 application, OS-dependent code somehow
starts the right python interpreter and has it execute this file
(possibly passing command-line arguments, but that might not be implemented
yet).

Developers running NE1 from svn can run this script using a command line
like "python main.py" or "pythonw main.py", depending on the Python
installation. Some Python or Qt installations require that the absolute
pathname of main.py be used, but the current directory should always be
the one containing this file, when it's run manually in this way.

This file then imports and starts everything else, via
the function startup_script defined in main_startup.py.

As of 041217 everything runs in one OS process,
except for occasional temporary subprocesses it might start.

History:

mostly unrecorded, except in cvs/svn; originally by Josh; lots of
changes by various developers at various times.

renamed from atom.py to main.py before release of A9, mid-2007.

bruce 070704 moved most of this file into main_startup.py.

bruce 071008 moved a long comment into a new file
ne1_startup/ALTERNATE_CAD_SRC_PATH-doc.txt,
and enclosed our own startup code into def _start_NE1().
"""

# NOTE: DON'T ADD ANY IMPORTS TO THIS FILE besides those already present
# (as of 071002), since doing so would cause errors in the semantics of
# the ALTERNATE_CAD_SRC_PATH feature and (possibly) in the function
# before_most_imports called inside the startup script. New imports needed
# by startup code, or needed (for side effects) early during startup, should
# be added to the appropriate place in one of the modules in the startup
# package.

import sys, os, time

from mock import Mock

mocked_pyqt = Mock()
mocked_pyqt_qt = Mock()
mocked_opengl = Mock()
sys.modules["PyQt4"] = mocked_pyqt
sys.modules["PyQt4.Qt"] = mocked_pyqt_qt
sys.modules["PyQt4.QtOpenGL"] = Mock()
sys.modules["PyQt4.QtGui"] = Mock()
sys.modules["OpenGL"] = mocked_opengl
sys.modules["OpenGL.GL"] = Mock()
sys.modules["OpenGL._GLE"] = Mock()
sys.modules["OpenGL.GLU"] = Mock()
sys.modules["OpenGL.GL.ARB"] = Mock()
sys.modules["OpenGL.GL.ARB.vertex_buffer_object"] = Mock()
sys.modules["OpenGL.raw.GL.ARB.vertex_buffer_object"] = Mock()
sys.modules["idlelib"] = Mock()
sys.modules["idlelib.Delegator"] = Mock()
sys.modules["LinearAlgebra"] = Mock()

# import numpy; Numeric is numpy.oldnumeric..
import numpy
import numpy.oldnumeric
sys.modules["Numeric"] = numpy.oldnumeric

print
print "starting NanoEngineer-1 in [%s]," % os.getcwd(), time.asctime()
print "using Python: " + sys.version
try:
    print "on path: " + sys.executable
except:
    pass

if __name__ != '__main__':
    print
    print "Warning: main.py should not be imported except as the __main__ module."
    print " (It is now being imported under the name %r.\n" \
          "  This is a bug, but should cause no direct harm.)" % (__name__,)
    print

# ALTERNATE_CAD_SRC_PATH feature:
#
# (WARNING: this MUST BE entirely implemented in main.py)
#
# for documentation and implementation notes, see
#    ne1_startup/ALTERNATE_CAD_SRC_PATH-doc.txt
# and
#    http://www.nanoengineer-1.net/mediawiki/index.php?title=Using_the_Libraries_from_an_NE1_Installation_for_Mac_Development
#
# [bruce 070704 new feature; intended for A9.2 release; UNTESTED except on Mac]

_alternateSourcePath = None

try:
    _main_path = __file__ # REVIEW: this might fail in Windows release build
    _main_dir = os.path.dirname( _main_path)
    _path_of_alt_path_file = os.path.join( _main_dir, "ALTERNATE_CAD_SRC_PATH" )
    if os.path.isfile( _path_of_alt_path_file):
        print "found", _path_of_alt_path_file
        _fp = open( _path_of_alt_path_file, "rU")
        _content = _fp.read().strip()
        _fp.close()
        _content = os.path.normpath( os.path.abspath( _content))
        print "containing pathname %r" % (_content,)
        if os.path.isdir(_content):
            _alternateSourcePath = _content
        else:
            print "which is not a directory, so will be ignored"
            print
        pass
except:
    print "exception (discarded) in code for supporting ALTERNATE_CAD_SRC_PATH feature"
    ## raise # useful for debugging
        ### REVIEW: remove print or fix implementation, if an exception here
        # happens routinely on other platforms' release builds

def _start_NE1():

    if _alternateSourcePath is not None:
        print
        print "WILL USE ALTERNATE_CAD_SRC_PATH = %r" % ( _alternateSourcePath,)
        sys.path.insert(0, _alternateSourcePath)
        # see ne1_startup/ALTERNATE_CAD_SRC_PATH-doc.txt for info about other
        # effects of this (implemented by setAlternateSourcePath below)
        print

    # NOTE: imports of NE1 source modules MUST NOT BE DONE until after the
    # optional sys.path change done for _alternateSourcePath, just above.

    import utilities.EndUser as EndUser

    EndUser.setAlternateSourcePath(_alternateSourcePath)

    _main_globals = globals() # needed by startup_script

    from ne1_startup.main_startup import startup_script

    startup_script( _main_globals )

    return

if __name__ == '__main__':
    _start_NE1()

# end
