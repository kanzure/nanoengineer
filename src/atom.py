#! /usr/bin/python
# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.

"""
atom.py is the startup script for NanoEngineer-1.

$Id$

This file should not be imported as the "atom" module -- doing so
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
of distinguishing end-user runs from developer runs.

When an end-user runs the nE-1 application, OS-dependent code somehow
starts the right python interpreter and has it run this script
(possibly passing command-line arguments, but that might not be implemented yet).

Developers running nE-1 from cvs can run this script using a command line
like "python atom.py" or "pythonw atom.py", depending on the Python
installation. Some Python or Qt installations require that the absolute
pathname of atom.py be used, but the current directory should always be
the one containing this file, when it's run manually in this way.

This script then imports and starts everything else.

As of 041217 everything runs in that one process,
except for occasional temporary subprocesses it might start.

History:

[mostly unrecorded except in cvs; originally by Josh; lots of changes by
various developers.]

bruce 050902 revised module docstring, and added comments explaining why
there are two separate tests of __name__ == '__main__'
(which surrounds most code in this module).
The reason this condition is needed at all is to reduce the harm caused
by someone accidentally running "import atom" (which is wrong but causes no harm).
"""

import sys, os, time
if sys.platform == 'darwin':
    # Bug 1724 mitigation, wware 060320 & bruce 060327   [for incomplete parts, search for ####@@@@]
    #
    # setting DYLD_LIBRARY_PATH is needed by the subprocess that runs all_mac_imports, 
    # or the linker will be unable to import qt; I don't know if it's good, bad, or neutral
    # to do it for the main process too, but it seems more likely to be good
    # (making our app more self-contained re qt), and it works for me.
    # This has no effect on developers running from cad/srcs, since RESOURCEPATH won't be set for them.
    # [bruce 060327]
    resources = os.environ.get('RESOURCEPATH')
    if resources:
        os.environ['DYLD_LIBRARY_PATH'] = os.path.abspath( os.path.join( resources, "../Frameworks"))
    if False:
    	# This code can be used to develop a list of import statements for all_mac_imports.py.
    	# This has already been done, and the list has subsequently been hand-edited.
        # Print a list of all the imports to stdout (not including duplications).
        _old_import = __import__
        not_these = [ "swig_runtime_data1", "OpenGL.GL._GL__init__", "bsddb", "_bsddb", "dbhash", "dotblas" ]
        def __import__(*args, **kws):
            global not_these
            arg = args[0]
            if arg not in not_these and not os.path.exists(arg + ".py"):
                not_these.append(arg)
                print "import " + arg
            return _old_import(*args, **kws)
        __builtins__.__import__ = __import__ # this is required, else no effect.
               # if you spell it wrong, the NameError gets into a decently ok dialog.
               # one option for our own alert window, therefore, is an assertion failure
               # (if we don't want to let the user even try to run the app -- but we do).
    else:
    	# Note: this code needs to work for either developers running it from cad/src/atom.py,
    	# or (its main purpose) for end-users running it from either Contents/Resources/NanoEngineer-1.py
    	# or Contents/Resources/Python/NanoEngineer-1.py, since release building can end up putting it
    	# in either of those two locations for reasons we don't yet understand. In the end-user case,
    	# it's execfile'd from __boot__.py. Its purpose is to test whether all required import statements
    	# will work, so if not, we can put up a useful dialog rather than just failing to start for no
    	# apparent reason. We have to do this in a subprocess, since when they fail, it just stops the
    	# process rather than raising an ImportError. The subprocess runs all_mac_imports.py to do the test,
    	# and we assume it succeeded only if it prints a certain string.
    	# For more info see ####@@@@ [ a wiki url about bug 1724].
    	
    	# let developers or end-users see more info about this bug by creating a specially named empty file:
    	try:
    	    debug_1724 = os.path.exists( os.path.join( os.environ['HOME'], 'DEBUG-1724')) # has '-', not '_'
    	except:
    	    debug_1724 = False
	if debug_1724:
	    debug_1724_start = time.time()
	    print "printing debug info relevant to bug 1724"
	    if resources:
	        print "set DYLD_LIBRARY_PATH to %r" % os.environ['DYLD_LIBRARY_PATH']
    	# First, figure out where we're running from and where all_mac_imports is located.
    	# Warning: in the end-user case, all_mac_imports might be in two places -- Contents/Resources
    	# (or Contents/Resources/Python), and site-packages.zip. We only want the Contents/Resources version.
    	# Some variables that might help us tell where we are:
    	if debug_1724:
    	    print __file__ # .../cad/src/atom.py or .../NanoEngineer-1.app/Contents/Resources/__boot__.py 
    	    print sys.argv[0] # .../cad/src/atom.py or .../NanoEngineer-1.app/Contents/Resources/__boot__.py
    	    print sys.executable
 		# For a developer, this depends on how your start the app. A possible value which probably
 		# means you're subject to bug 1724 is (note this is in /Library, not /System/Library):
    		#   /Library/Frameworks/Python.framework/Versions/2.3/Resources/Python.app/Contents/MacOS/Python
    		# For an end-user, whether or not your Mac has the problem in bug 1724, if you have Panther,
    		# the value should be:
    		#   /System/Library/Frameworks/Python.framework/Versions/2.3/bin/python
    	    print os.environ.get('RESOURCEPATH')
    	 	# for a developer, this probably prints None
    	 	# for an end-user, it should print .../NanoEngineer-1.app/Contents/Resources
    	# Since we want to run all_mac_imports.py in any case, let's just look for it in the locations
    	# it might be in:
    	possible_dirs = []
    	possible_dirs.append( os.path.dirname(sys.argv[0]) ) # .../cad/src or .../Contents/Resources
    	if os.path.basename( possible_dirs[-1] ) == 'Resources':
    	    possible_dirs.append( os.path.join( possible_dirs[-1], 'Python' ))
    	elif os.path.basename( possible_dirs[-1] ) == 'Python': # might not be possible
    	    possible_dirs.append( os.path.dirname( possible_dirs[-1] ))
    	allmac_path = None
    	for dir1 in possible_dirs:
    	    file1 = os.path.join( dir1, "all_mac_imports.py" ) 
    	    	# this works even if you run "pythonw atom.py" or "pythonw ./atom.py"
    	    	# (though Qt prints a warning then about using a relative path).
    	    if os.path.exists( file1):
    	        allmac_path = file1
    	        break
    	if allmac_path:
    	    if debug_1724:
    	        print "found all_mac_imports.py at %r" % allmac_path
    	    # run it and warn the user if it doesn't work
            arg = ":".join(sys.path) # pass this to the subprocess so it can use the same sys.path as us
            # try to survive presence of spaces in pathnames (which is common); use single quotes for most likelihood of working
            cmd = "/usr/bin/env '%s' '%s' '%s'" % ( sys.executable , allmac_path , arg )
            if debug_1724:
                os.environ['debug_1724'] = "1"
                # so subprocess can see it (is this wise, or might it cause a heisenbug?)
            try:
                inf = os.popen(cmd) #k does the above cmd work with spaces in paths? maybe, but this is not tested. ####@@@@@
            except:
                print "exception in os.popen(%r) (might be caused by spaces in pathnames); not trying all_mac_imports.py" % (cmd,)
            else:
                lines = map(lambda x: x.rstrip(), inf.readlines())
                if debug_1724:
                    print 'output from all_mac_imports (%d lines, after ">>  ") was:' % len(lines)
                    print
                    print ">>  " + "\n>>  ".join(lines)
                    print
        	inf.close()
        	if "ALL IMPORTS COMPLETED" not in lines:
        	    # This means this machine is almost certainly unable to run nE-1, probably due to bug 1724 or 1882.
        	    # Print some info, including a possible workaround, into the logfile displayable by Console.app,
        	    # and then try to put up a dialog. (The one put up by py2app if we raise an exception
        	    # offers to open the Console, so that's probably best.)
        	    #   This workaround printout is not super easy to notice, even if you think of looking in Console output,
        	    # but that's ok, since we'd really rather you email support@nanorex.com first anyway, so we know whether
        	    # anyone actually encounters this problem.
        	    print "\n * * * * "
            	    print "There were import problems in the test subprocess (bug 1724? 1882?); try to warn the user with a dialog..."
            	    print
            	    print "Note: one workaround might be to remove (or disable by renaming)"
            	    print "/Library/Frameworks/Python.framework and perhaps /Developer/qt,"
            	    print "so that Apple's Python, in /System/Library/Frameworks, can run this app without interference,"
            	    print "and to avoid any chance of this app using a qt dylib other than the one it contains."
            	    print " * * * * \n" 
            	    if "QT IMPORT WORKED" not in lines:
                        # This is not bug 1724, and no specific causes are known except file permission problems in the installer
                        # (probably fixed in autoBuild.py rev 1.51 on 060420), or bug 1882 (Intel Mac problems in qt.so).
                        # Let py2app show the user a dialog, since obviously we can't use Qt for one.
                        # (We do this by raising an exception, and a py2app startup file turns its text into a dialog.)
                        assert 0, \
                               "Internal error linking to self-contained qt dylib; "\
                               "this might be caused by a bug in the NanoEngineer-1 installer, "\
                               "or by this version of nE-1 not working properly on Intel Macs.\n"\
                               "\n"\
                               "Please contact support@nanorex.com for help and more information."
                    else:
                        # This is probably bug 1724.
                        # We could in theory use a Qt dialog -- but actually this is not desirable, since py2app's dialog
                        # is better since it has a button which opens Console.app. (The following commented-out code
                        #  shows how we might try to use a Qt dialog, but it doesn't yet work, as its comment explains.)
##                        try:
##                            import qt
##                            # The following QMessageBox fails with this error:
##                            #   QPaintDevice: Must construct a QApplication before a QPaintDevice
##                            # This could be fixed without too much trouble, but it's not really worth any trouble.
##                            # So forget it for now, assert 0 before running it (so we'll post py2app's error dialog
##                            # from the fallback assertion in our except clause),
##                            # since it fails by exiting rather than by raising an exception we can catch.
##                            assert 0 # explained above
##                            qt.QMessageBox.critical( None, "NanoEngineer-1",
##                                    "Internal error in some imports; "\
##                                    "NanoEngineer-1 may be unable to run on this machine as it's currently configured. "\
##                                    "It will try to start anyway, but will probably fail.\n\n"\
##                                    "Please contact support@nanorex.com for help." ###test
##                                    );
##                        except:
                        # So in this case too, we raise an exception in order to get py2app to show it in a dialog.
                        # The only known cause of this is bug 1724; there may also be unknown causes.
                            assert 0, \
                                "Internal error during startup; "\
                                "NanoEngineer-1 can't run on this machine as it's currently configured.\n"\
                                "\n"\
                                "(The known causes of this problem have a simple solution, "\
                                "but one which the nE-1 installer can't perform automatically.)\n"\
                                "\n"\
                                "Please contact support@nanorex.com for help and more information."
            	    ## sys.exit(1)
                else:
                    if debug_1724:
                        print "all_mac_imports worked"
                        debug_1724_end = time.time()
                        print " (took %0.3f extra seconds for startup)" % (debug_1724_end - debug_1724_start)
                          # This prints 3-4 seconds on bruce's iMac G4 with a small set of imports being tested.
                          # Without debug_1724, it seems faster; maybe this time is less or maybe it reduces
                          # some of the time taken subsequently (e.g. to load python?) so has less than full
                          # impact (just guesses). I think this means I don't need to provide a way to 
                          # disable the test, which is good in case someone might install the problematic
                          # alternative Python *after* installing nE-1. [bruce 060327]
                        print
                    pass
                pass
            pass
        else:
            print "can't find all_mac_imports.py (please inform nanorex support); trying to start anyway"
        pass 
    pass # end of bug 1724 mitigation code

__author__ = "Josh"

if __name__ != '__main__':
    #bruce 050902 added this warning
    print
    print "Warning: atom.py should not be imported except as the __main__ module."
    print " (It is now being imported under the name %r.\n" \
          "  This is a bug, but should cause no direct harm.)" % (__name__,)
    print

import startup_funcs # this has no side effects, it only defines a few functions
    # bruce 050902 moved some code from this file into new module startup_funcs

import sys, os, time # all other imports should be added lower down

if __name__ == '__main__':
    # This condition surrounds most code in this file, but it occurs twice,
    # so that the first occurrence can come before most of the imports,
    # while letting most imports occur at the top level of the file.
    # [bruce 050902 comment about older situation]
    
    main_globals = globals() # needed in case .atom-debug-rc is executed, since it must be executed in that global namespace
    
    startup_funcs.before_most_imports( main_globals )
        # "Do things that should be done before anything that might possibly have side effects."

# most imports in this file should be done here, or inside functions in startup_funcs

from qt import QApplication, QSplashScreen, SIGNAL ## bruce 050902 removed QRect, QDesktopWidget

## from constants import *
    #bruce 050902 removing import of constants since I doubt it's still needed here.
    # This might conceivably cause bugs, but it's unlikely.

from MWsemantics import MWsemantics # (this might have side effects other than defining things)

if __name__ == '__main__':
    # [see comment above about why there are two occurrences of this statement]
    
    startup_funcs.before_creating_app()
        # "Do whatever needs to be done before creating the application object, but after importing MWsemantics."
    
    QApplication.setColorSpec(QApplication.CustomColor)
    app = QApplication(sys.argv)
    app.connect(app, SIGNAL("lastWindowClosed ()"), app.quit)
    
    # If the splash image is found in cad/images, put up a splashscreen. 
    # If you don't want the splashscreen, just rename the splash image.
    # mark 060131.
    from Utility import imagename_to_pixmap
    splash_pixmap = imagename_to_pixmap( "splash.png" ) # rename it if you don't want it.
    if not splash_pixmap.isNull():
        splash = QSplashScreen(splash_pixmap) # create the splashscreen
        splash.show()
        MINIMUM_SPLASH_TIME = 3.0 
            # I intend to add a user pref for MINIMUM_SPLASH_TIME for A7. mark 060131.
        splash_start = time.time()
    
    foo = MWsemantics() # This does a lot of initialization (in MainWindow.__init__)

    try:
        # do this, if user asked us to by defining it in .atom-debug-rc
        meth = atom_debug_pre_main_show
    except:
        pass
    else:
        meth()

    startup_funcs.pre_main_show(foo) # this sets foo's geometry, among other things
    
    foo._init_after_geometry_is_set()
    
    if not splash_pixmap.isNull():
        # If the MINIMUM_SPLASH_TIME duration has not expired, sleep for a moment.
        while time.time() - splash_start < MINIMUM_SPLASH_TIME:
            time.sleep(0.1)
        splash.finish( foo ) # Take away the splashscreen
    
    foo.show() # show the main window
    
    if foo.glpane.mode.modename == 'DEPOSIT':
        # Two problems are addressed here when nE-1 starts in Build (DEPOSIT) mode.
        # 1. The MMKit can cover the splashscreen (bug #1439).
        #   BTW, the other part of bug fix 1439 is in MWsemantics.modifyMMKit()
        # 2. The MMKit appears 1-3 seconds before the main window.
        # Both situations now resolved.  mark 060202
        # Should this be moved to startup_funcs.post_main_show()? I chose to leave
        # it here since the splashscreen code it refers to is in this file.  mark 060202.
        foo.glpane.mode.MMKit.show()
        if sys.platform == 'linux2':
            # During startup on Linux, the MMKit dialog must be "shown" before it can be moved.
            # Fixes bug 1444.  mark 060311.
            x, y = foo.glpane.mode.MMKit.get_location(False)
                # Call MMKit.move_to_best_location(), not get_location(), and move x += 5 there.
                # Then we can remove MMKit.move, too.
            x += 5 # Add 5 pixels. X11 didn't include the border when we called get_location().
            foo.glpane.mode.MMKit.move(x, y)
        
    try:
        # do this, if user asked us to by defining it in .atom-debug-rc
        meth = atom_debug_post_main_show 
    except:
        pass
    else:
        meth()

    startup_funcs.post_main_show(foo) # bruce 050902 added this

    # If the user's .atom-debug-rc specifies PROFILE_WITH_HOTSHOT=True, use hotshot, otherwise
    # fall back to vanilla Python profiler.
    try:
        PROFILE_WITH_HOTSHOT
    except NameError:
        PROFILE_WITH_HOTSHOT = False
    
    # now run the main Qt event loop --
    # perhaps with profiling, if user requested this via .atom-debug-rc.
    try:
        # user can set this to a filename in .atom-debug-rc,
        # to enable profiling into that file
        atom_debug_profile_filename 
        if atom_debug_profile_filename:
            print "user's .atom_debug_rc requests profiling into file %r" % (atom_debug_profile_filename,)
            if not type(atom_debug_profile_filename) in [type("x"), type(u"x")]:
                print "error: atom_debug_profile_filename must be a string; running without profiling"
                assert 0 # caught and ignored, turns off profiling
            if PROFILE_WITH_HOTSHOT:
                try:
                    import hotshot
                except:
                    print "error during 'import hotshot'; running without profiling"
                    raise # caught and ignored, turns off profiling
            else:
                try:
                    import profile
                except:
                    print "error during 'import profile'; running without profiling"
                    raise # caught and ignored, turns off profiling
    except:
        atom_debug_profile_filename = None

    # bruce 041029: create fake exception, to help with debugging
    # (in case it's shown inappropriately in a later traceback)
    try:
        assert 0, "if you see this exception in a traceback, it is from" \
            " the startup script atom.py, not the code that printed the traceback"
    except:
        pass

    if not foo.permdialog.fini:
        foo.permdialog.show()

    from platform import atom_debug
    if atom_debug:
        # Use a ridiculously specific keyword, so this isn't triggered accidentally.
        if len(sys.argv) >= 3 and sys.argv[1] == '--initial-file':
            # fileOpen gracefully handles the case where the file doesn't exist.
            foo.fileOpen(sys.argv[2])
            if len(sys.argv) > 3:
                import env
                from HistoryWidget import orangemsg
                env.history.message(orangemsg("We can only import one file at a time."))
  
    if atom_debug_profile_filename:
        if PROFILE_WITH_HOTSHOT:
            profile = hotshot.Profile(atom_debug_profile_filename)
            profile.run('app.exec_loop()')
        else:
            profile.run('app.exec_loop()', atom_debug_profile_filename)
        print "\nprofile data was presumably saved into %r" % (atom_debug_profile_filename,)
    else:
        # if you change this code, also change the string literal just above
        app.exec_loop() 

    pass

# end
