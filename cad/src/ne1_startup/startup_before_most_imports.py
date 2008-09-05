# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
startup_before_most_imports.py - some application startup functions
which need to be run before most imports are done, and which therefore
need to be careful about doing imports themselves.

$Id$

History:

bruce 050902 made startup_funcs.py by moving some code out of main.py,
and adding some stub functions which will be filled in later.

bruce 071005 moved these functions from startup_funcs.py into
this new file startup/startup_before_most_imports.py.
"""

import sys, os

import utilities.EndUser as EndUser

# NOTE: this module (or EndUser) must not do toplevel imports of our other
# source modules, because it contains functions which need to be called
# by main_startup before most imports are done.


def before_most_imports( main_globals ):
    """
    Do things that should be done before most imports occur.
    main_globals should be the value of globals() in the __main__ module.
    """

    # user-specific debug code to be run before any other imports [bruce 040903]

    # gpl_only check at startup [bruce 041217]
    try:
        import platform_dependent.gpl_only as _gpl_only
            # if this module is there, this lets it verify it should be there,
            # and if not, complain (to developers) whenever the program starts
        print "(running a GPL distribution)" #e retain or zap this?
    except ImportError:
        print "(running a non-GPL distribution)" #e retain or zap this? [should never happen for Qt4, as of 070425]
        pass # this is normal for non-GPL distributions
    try:
        rc = "~/.atom-debug-rc"
        rc = os.path.expanduser(rc)
        if os.path.exists(rc):
            ## execfile(rc) -- not allowed!
            import utilities.debug as _debug
            _debug.legally_execfile_in_globals(rc, main_globals, error_exception = False)
                # might fail in non-GPL versions; prints error message but
                # does not raise an exception.
                # (doing it like this is required by our licenses for Qt/PyQt)
    except:
        print """exception in execfile(%r); traceback printed to stderr or console; exiting""" % (rc,)
        raise

    # Figure out whether we're run by a developer from cvs sources
    # (EndUser.enableDeveloperFeatures() returns True), or by an
    # end-user from an installer-created program (it returns False).
    # Use two methods, warn if they disagree, and if either one
    # think's we're an end user, assume we are (so as to turn off
    # certain code it might not be safe for end-users to run).
    # [bruce 050902 new feature; revised 051006 to work in Windows
    # built packages]
    # [Russ 080905: Fixed after this file moved into ne1_startup.]
    ourpackage = "ne1_startup"

    # Method 1. As of 050902, package builders on all platforms reportedly move main.py
    # (the __main__ script) into a higher directory than the compiled python files.
    # But developers running from cvs leave them all in cad/src.
    # So we compare the directories.
    endUser = True # conservative initial assumption (might be changed below)
    import __main__
    ourdir = None # hack for print statement test in except clause
        # this is still being imported, but we only need its __file__ attribute, which should be already defined [but see below]
    try:
        # It turns out that for Windows (at least) package builds, __main__.__file__ is either never defined or not yet
        # defined at this point, so we have no choice but to silently guess endUser = True in that case. I don't know whether
        # this module's __file__ is defined, whether this problem is Windows-specific, etc. What's worse, this problem disables
        # *both* guessing methods, so on an exception we just have to skip the whole thing. Further study might show that there is
        # no problem with ourdir, only with maindir, but I won't force us to test that right now. [bruce 051006]
        # REVIEW: is this still correct now that this code is in a non-toplevel module? [bruce 080111 question]
        ourdir = os.path.split(__file__)[0]
        maindir = os.path.split(__main__.__file__)[0]
    except:
        # unfortunately it's not ok to print the exception or any error message, in case endUser = True is correct...
        # but maybe I can get away with printing something cryptic (since our code is known to print things sometimes anyway)?
        # And I can make it depend on whether ourdir was set, so we have a chance of finding out whether this module defined __file__.
        # [bruce 051006]
        if ourdir is not None:
            print "end-user build"
        else:
            print "end user build" # different text -- no '-'
    else:
        # we set maindir and ourdir; try both guess-methods, etc
        def canon(path):
            #bruce 050908 bugfix in case developer runs python with relative (or other non-canonical) path as argument
            return os.path.normcase(os.path.abspath(path))
        maindir = canon(maindir)
        ourdir = canon(ourdir)
        guess1 = (os.path.join(maindir, ourpackage) != ourdir) # Russ 080905: Loaded from package subdirectory.

        # Method 2. As of 050902, package builders on all platforms remove the .py files, leaving only .pyc files.
        ourfile = os.path.splitext(__name__)[1][1:] # Russ 080905: Remove "ourpackage." prefix.
        guess2 = not os.path.exists(os.path.join(ourdir, ourfile + ".py"))

        endUser = guess1 or guess2
        if EndUser.getAlternateSourcePath() != None:
            # special case when using ALTERNATE_CAD_SRC_PATH feature
            # (which can cause these guesses to differ or be incorrect):
            # assume anyone using it is a developer [bruce 070704]
            endUser = False
        else:
            if guess1 != guess2:
                print "Warning: two methods of guessing whether we're being run by an end-user disagreed (%r and %r)." % (guess1, guess2)
                print "To be safe, assuming we are (disabling some developer-only features)."
                print "If this ever happens, it's a bug, and the methods need to be updated."
                if guess1:
                    print "(debug info: guess1 is true because %r != %r)" % (maindir, ourdir)
                        #bruce 050908 to debug Linux bug in guess1 reported by Ninad (it's True (i.e. wrong) when he runs nE-1 from source)
                print
        pass

    EndUser.setDeveloperFeatures(not endUser)
    if EndUser.enableDeveloperFeatures():
        print "enabling developer features"
        # The actual enabling is done by other code which checks the value of EndUser.enableDeveloperFeatures().
        # Note: most code should NOT behave differently based on that value!
        # (Doing so might cause bugs to exist in the end-user version but not the developer version,
        #  which would make them very hard to notice or debug. This risk is only justified in a few
        #  special cases.)
    
    return # from before_most_imports

    
def before_creating_app():
    """
    Do other things that should be done before creating the application object.
    """
    # the default (1000) bombs with large molecules
    sys.setrecursionlimit(5000)

    # cause subsequent signal->slot connections to be wrapped for undo support
    # (see comment in caller about whether this could be moved later in caller
    #  due to the imports it requires)
    import foundation.undo_internals as undo_internals
    undo_internals.call_asap_after_QWidget_and_platform_imports_are_ok() #bruce 050917
    return


# end
