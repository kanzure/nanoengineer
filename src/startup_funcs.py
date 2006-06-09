# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
startup_funcs.py

Contains application startup actions, organized into functions called
at specific times by the actual startup script, atom.py (their only caller).

$Id$

History:

bruce 050902 made this by moving some code out of atom.py,
and adding some stub functions which will be filled in later.
'''

import sys, os

def before_most_imports( main_globals ):
    """Do things that should be done before anything that might possibly have side effects.
    main_globals should be the value of globals() in the __main__ module (our caller, atom.py).
    """

    # user-specific debug code to be run before any other imports [bruce 040903]

    # gpl_only check at startup [bruce 041217]
    try:
        import gpl_only as _gpl_only
            # if this module is there, this lets it verify it should be there,
            # and if not, complain (to developers) whenever the program starts
        print "(running a GPL distribution)" #e retain or zap this?
    except ImportError:
        print "(running a non-GPL distribution)" #e retain or zap this?
        pass # this is normal for non-GPL distributions
    try:
        rc = "~/.atom-debug-rc"
        rc = os.path.expanduser(rc)
        if os.path.exists(rc):
            ## execfile(rc) -- not allowed!
            import debug as _debug
            _debug.legally_execfile_in_globals(rc, main_globals, error_exception = False)
                # might fail in non-GPL versions; prints error message but
                # does not raise an exception.
                # (doing it like this is required by our licenses for Qt/PyQt)
    except:
        print """exception in execfile(%r); traceback printed to stderr or console; exiting""" % (rc,)
        raise

    #bruce 050809 part of improved Mac OS X Tiger QToolButton bug workaround
    if sys.platform == 'darwin':
        try:
            import widget_hacks
            widget_hacks.doit3()
        except:
            print "exception in widget_hacks.doit3() (or in importing it) ignored"
        pass

    # Figure out whether we're run by a developer from cvs sources (_end_user = False),
    # or by an end-user from an installer-created program (_end_user = True).
    # Use two methods, warn if they disagree, and if either one think's we're an end user,
    # assume we are (so as to turn off certain code it might not be safe for end-users to run).
    # [bruce 050902 new feature; revised 051006 to work in Windows built packages]

    # Method 1. As of 050902, package builders on all platforms reportedly move atom.py
    # (the __main__ script) into a higher directory than the compiled python files.
    # But developers running from cvs leave them all in cad/src.
    # So we compare the directories.
    import __main__
    ourdir = None # hack for print statement test in except clause
        # this is still being imported, but we only need its __file__ attribute, which should be already defined [but see below]
    try:
        # It turns out that for Windows (at least) package builds, __main__.__file__ is either never defined or not yet
        # defined at this point, so we have no choice but to silently guess _end_user = True in that case. I don't know whether
        # this module's __file__ is defined, whether this problem is Windows-specific, etc. What's worse, this problem disables
        # *both* guessing methods, so on an exception we just have to skip the whole thing. Further study might show that there is
        # no problem with ourdir, only with maindir, but I won't force us to test that right now. [bruce 051006]
        ourdir,  filejunk = os.path.split( __file__ )
        maindir, filejunk = os.path.split( __main__.__file__ )
    except:
        __main__._end_user = _end_user = True
        # unfortunately it's not ok to print the exception or any error message, in case this guess is correct...
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
            return os.path.normcase( os.path.abspath(path) )
        maindir = canon(maindir)
        ourdir = canon(ourdir)
        guess1 = (maindir != ourdir)

        # Method 2. As of 050902, package builders on all platforms remove the .py files, leaving only .pyc files.
        guess2 = not os.path.exists( os.path.join( ourdir, __name__ + ".py" ))

        __main__._end_user = _end_user = guess1 or guess2
        if guess1 != guess2:
            print "Warning: two methods of guessing whether we're being run by an end-user disagreed (%r and %r)." % (guess1, guess2)
            print "To be safe, assuming we are (disabling some developer-only features)."
            print "If this ever happens, it's a bug, and the methods need to be updated."
            if guess1:
                print "(debug info: guess1 is true because %r != %r)" % (maindir, ourdir)
                    #bruce 050908 to debug Linux bug in guess1 reported by Ninad (it's True (i.e. wrong) when he runs nE-1 from source)
            print
        pass

    assert __main__._end_user == _end_user # must be obeyed by except and else clauses of try statement above
    if _end_user:
        pass # normally no message in this case
    else:
        print "enabling developer features"
        # The actual enabling is done by other code which checks the value of __main__._end_user.
        # Note: most code should NOT behave differently based on that value!
        # (Doing so might cause bugs to exist in the end-user version but not the developer version,
        #  which would make them very hard to notice or debug. This risk is only justified in a few
        #  special cases.)
    
    return # from before_most_imports

    
def before_creating_app():
    "Do whatever needs to be done before creating the application object, but after importing MWsemantics."
    # the default (1000) bombs with large molecules
    sys.setrecursionlimit(5000)

    # bruce 050119: get working directory from preferences database.
    # (It used to be stored in ~/.ne1rc; this file is now optional,
    #  used only if preferences doesn't find anything; it's no longer
    #  ever created or written to.)
    from preferences import prefs_context
    prefs = prefs_context()
    where = "preferences database" # only matters when wd is non-null
    wd = prefs.get('WorkingDirectory')
    if not wd:
        # see if it's stored in the old location
        # (this won't be needed in the Alpha release, but is needed for our own
        #  internal users who have these files lying around - but only until the
        #  next time they run the program, since we'll write wd found in .ne1rc
        #  into the prefs db, too.)
        # old code [slightly modified by bruce 050119]:
        # Windows Users: .ne1rc must be placed in C:\Documents and Settings\[username]\.ne1rc
        # .ne1rc contains one line, the Working Directory
        # Example: C:\Documents and Settings\Mark\My Documents\MMP Parts
        rc = os.path.expanduser("~/.ne1rc")
        if os.path.exists(rc):
            where = rc
            f = open(rc,'r')
            wd = os.path.normpath(f.readline())
            f.close()
            prefs['WorkingDirectory'] = wd # whether or not isdir(wd)!
             # After this, in theory, this ~/.ne1rc is never again needed.
    from constants import globalParms
    if wd:
        if os.path.isdir(wd):
            globalParms['WorkingDirectory'] = wd
        else:
            print "Warning: working directory \"%s\" (from %s)" % (wd, where)
            print " no longer exists; using \"%s\" for this session." % globalParms['WorkingDirectory']
            #e Ideally we'd print this into env.history, but as of 050913 it might be too early,
            # and I'm not even 100% sure we can safely import env at this point (#k that should be found out).
            #e Someday we should perhaps save this message somewhere and print it into the history widget
            # when that's created (or make sure env.history can do this, and is importable now).
        pass
    import undo
    undo.call_asap_after_QWidget_and_platform_imports_are_ok() #bruce 050917
    return


# (MWsemantics.__init__ is presumably run after the above functions and before the following ones.)


def pre_main_show( win):
    "Do whatever should be done after the main window is created but before it's first shown."

    # Determine the screen resolution and compute the normal window size for NE-1
    # [bruce 041230 corrected this for Macintosh, and made sure it never exceeds
    #  screen size even on a very small screen.]
    # [bruce 050118 further modified this and removed some older comments
    #  (see cvs for those); also split out some code into platform.py.]
    import platform as _platform
    ((x0, y0), (screen_w, screen_h)) = _platform.screen_pos_size()
    # note: y0 is nonzero on mac, due to menubar at top of screen.
    
    # use 85% of screen width and 90% of screen height, or more if that would be
    # less than 780 by 560 pixels, but never more than the available space.
    norm_w = int( min(screen_w - 2, max(780, screen_w * 0.85)))
    norm_h = int( min(screen_h - 2, max(560, screen_h * 0.90)))
        #bruce 050118 reduced max norm_h to never overlap mac menubar (bugfix?)
    
    # determine normal window origin
    # [bruce 041230 changed this to center it, but feel free to change this back
    #  by changing the next line to center_it = 0]
    center_it = 1
    if center_it:
        # centered in available area
        norm_x = (screen_w - norm_w) / 2 + x0
        norm_y = (screen_h - norm_h) / 2 + y0
    else:
        # at the given absolute position within the available area
        # (but moved towards (0,0) from that, if necessary to keep it all on-screen)
        want_x = 4 # Left (4 pixels)
        want_y = 36 # Top (36 pixels)
        norm_x = min( want_x, (screen_w - norm_w)) + x0
        norm_y = min( want_y, (screen_h - norm_h)) + y0
    
    # Set the main window geometry, hopefully before the caller shows the window
    from qt import QRect
    win.setGeometry(QRect(norm_x, norm_y, norm_w, norm_h))

    ###e it might be good to register this as the default geom. in the prefs system, and use that to implement "restore defaults"

    # After the above (whose side effects on main window geom. are used as defaults by the following code),
    # load any mainwindow geometry present in prefs db. [bruce 051218 new feature; see also new "save" features in UserPrefs.py]
    from debug import print_compact_stack
    try:
        # this code is similar to debug.py's _debug_load_window_layout
        from platform import load_window_pos_size
        from prefs_constants import mainwindow_geometry_prefs_key_prefix
        keyprefix = mainwindow_geometry_prefs_key_prefix
        load_window_pos_size( win, keyprefix)
        win._ok_to_autosave_geometry_changes = True
    except:
        print_compact_stack("exception while loading/setting main window pos/size from prefs db: ")
        win.setGeometry(QRect(norm_x, norm_y, norm_w, norm_h))

    _initialize_custom_display_modes()
    
    return # from pre_main_show

# This is debugging code used to find out the origin and size of the fullscreen window
#    foo = win
#    foo.setGeometry(QRect(600,50,1000,800)) # KEEP FOR DEBUGGING
#    fooge = QRect(foo.geometry())
#    print "Window origin = ",fooge.left(),",",fooge.top()
#    print "Window width =",fooge.width(),", Window height =",fooge.height()

def _initialize_custom_display_modes():
    import CylinderChunks #bruce 060609
    return

def post_main_show( win): # bruce 050902 added this
    "Do whatever should be done after the main window is shown, but before the Qt event loop is started."

    pass ####e rebuild pyx modules if necessary and safe -- but only for developers, not end-users

# end
