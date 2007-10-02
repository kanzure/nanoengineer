#! /usr/bin/python
# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
main.py -- the initial startup file for NanoEngineer-1, treated specially
by the release-building process.

$Id$

This file should not be imported as the "main" module -- doing so
prints a warning [as of 050902] and doesn't run the contained code.
If necessary, it can be imported as the __main__ module
from within the nE-1 process it starts, by "import __main__".
Such an import doesn't rerun the contained code -- only reload(__main__)
would do that, and that should not be done.

Depending on the details of the package building process,
this file might be renamed and/or moved to a different directory
from the other modules under cad/src. As of 050902, it's always
moved to a different directory (by package building on any platform),
and this is detected at runtime (using __main__.__file__) as a way
of distinguishing end-user runs from developer runs [by code now
located in startup_funcs.py, as of sometime before 070704].

When an end-user runs the nE-1 application, OS-dependent code somehow
starts the right python interpreter and has it execute this file
(possibly passing command-line arguments, but that might not be implemented yet).

Developers running nE-1 from cvs can run this script using a command line
like "python main.py" or "pythonw main.py", depending on the Python
installation. Some Python or Qt installations require that the absolute
pathname of main.py be used, but the current directory should always be
the one containing this file, when it's run manually in this way.

This file then imports and starts everything else, mostly using code in
the function startup_script defined in main_startup.py.

As of 041217 everything runs in that one process,
except for occasional temporary subprocesses it might start.

History:

mostly unrecorded, except in cvs; originally by Josh; lots of
changes by various developers at various times.

renamed from atom.py to main.py before release of A9, mid-2007.

bruce 070704 moved most of this file into main_startup.py.
"""

# NOTE: DON'T ADD ANY IMPORTS TO THIS FILE besides those already present
# (as of 071002), since doing so would cause errors in the semantics of
# both the ALTERNATE_CAD_SRC_PATH feature and the function
# startup_funcs.before_most_imports. New imports needed by startup code,
# or needed (for side effects) early during startup, should be added to
# the appropriate place in main_startup.py or startup_funcs.py.

import sys, os, time

print
print "starting NanoEngineer-1 in [%s]," % os.getcwd(), time.asctime()

if __name__ != '__main__':
    print
    print "Warning: main.py should not be imported except as the __main__ module."
    print " (It is now being imported under the name %r.\n" \
          "  This is a bug, but should cause no direct harm.)" % (__name__,)
    print

# ALTERNATE_CAD_SRC_PATH feature:  (note, this MUST BE entirely implemented in main.py)
#
#   If you are a developer who wants an installed release build of NE1 to load
# most of its Python code (the code normally located in cad/src in cvs) from
# a different directory than usual, find this source file (main.py) in the
# place that the release builder copies it to (details below), and add a file
# next to it named ALTERNATE_CAD_SRC_PATH, consisting of a single line giving
# the absolute pathname in which cad/src files should be found. (This feature
# may only work correctly if that pathname also ends with cad/src.)
#
#   If a directory exists at that path, it will be prepended to sys.path,
# so that Python imports will look in it first, and a flag and global
# variable will be set here, so that other code can also behave differently
# when this feature is in use. (This is intended to permit printing of startup
# messages prominently warning the developer-user that this feature is being
# used, and to permit startup or other code to improve the behavior of this
# feature, for example by removing the usual location of files in cad/src
# from sys.path (so that removed files don't still seem to be present),
# by also looking for cad/plugins/* or sim.so in a different place, etc.)
#
#   Finding the correct main.py file to place ALTERNATE_CAD_SRC_PATH next to:
# At least on the Mac, this source file (main.py) is copied to a different place
# than all other cad/src files (which remain as .pyc files in a .zip archive) --
# though it is also left (unused) in the same place as they are. As of 070704,
# the copied main.py is located inside NE1's .app folder, with a pathname like
# NanoEngineer-1-version.app/Contents/Resources/main.py. So the new file should
# have a name like NanoEngineer-1-version.app/Contents/Resources/ALTERNATE_CAD_SRC_PATH
# and contents that look something like <your cvs dir>/cad/src on a single line.
#
#   The motivation of this feature is to permit a developer to run NE1 from cvs
# or other modified sources, but using the same libraries present in an
# installed NE1, whether or not they're installed on that developer's system in
# the usual way. This saves developers from having to install those libraries
# or worry about whether they're the right version, and permits testing code
# with more than one different set of such libraries. It also helps test for
# bugs due to the possible dependence of code on its location in the filesystem.
#
#   This feature is operative (when its special file is found) regardless of
# whether NE1 is being run from a built release or from cvs, so don't check in an
# ALTERNATE_CAD_SRC_PATH file to cvs! 
#
#   This feature might work on Windows and Linux, but has only been tested on Mac
# as of 070704. It's possible those platforms will require alternative ways of
# modifying the installed NE1.
#
# Implementation & design notes:
#
#   This feature needs to be implemented here in main.py, and can't make use of any
# normal "preference setting", since it has to know how to modify sys.path before we
# import any other modules. (It's also good if it affects each installation of NE1
# independently, but that requirement would only complicate the use of a prefs setting
# rather than ruling it out.)
#
#   One reason we implement this using a separate file (rather than just suggesting
# that the developer-user edit the global definitions in this file directly) is to
# make it less likely that a mistaken cvs commit will activate this feature for
# everyone by default. Another reason is to make it more likely to work unchanged
# on all platforms (in case finding and modifying this file is difficult on some
# platforms).
#
# [bruce 070704 new feature; intended for A9.2 release; UNTESTED except on Mac]

_alternateSourcePath = None

try:
    _main_path = __file__ # REVIEW: this line might fail in Windows release build
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

if __name__ == '__main__':
    
    if _alternateSourcePath is not None:
        print
        print "WILL USE ALTERNATE_CAD_SRC_PATH = %r" % ( _alternateSourcePath,)
        sys.path.insert(0, _alternateSourcePath)
        # see block comment above re behavior changes besides this one, by other code
        print

    # NOTE: imports of NE1 source modules MUST NOT BE DONE until after the optional
    # sys.path change done for _alternateSourcePath, just above.

    import EndUser

    EndUser.setAlternateSourcePath(_alternateSourcePath)
    
    _main_globals = globals() # needed by startup_script

    from main_startup import startup_script
    
    startup_script( _main_globals )
    

# The rest of main.py has been moved into a startup function in a new file, main_startup.py,
# as of bruce 070704.

# end
