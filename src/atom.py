#! /usr/bin/python
# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.

"""Atom

142C41+

atom.py is the startup script for nanoENGINEER-1.
OS-dependent code runs before this and somehow starts the
right python interpreter and has it run this script
(possibly with arguments, that might not be implemented yet),
which imports and starts everything else.
As of 041217 everything runs in that one process,
except for occasional temporary subprocesses it might start.

$Id$
"""

__author__ = "Josh"

import sys, os


# user-specific debug code to be run before any other imports [bruce 040903]
if __name__=='__main__':
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
            _debug.legally_execfile_in_globals(rc, globals(), error_exception = False)
                # might fail in non-GPL versions; prints error message but
                # does not raise an exception.
                # (doing it like this is required by our licenses for Qt/PyQt)
    except:
        print """exception in execfile(%r); traceback printed to stderr or console; exiting""" % (rc,)
        raise
    if sys.platform == 'darwin': #bruce 050809 part of improved Mac OS X Tiger QToolButton bug workaround
        try:
            import widget_hacks
            widget_hacks.doit3()
        except:
            print "exception in widget_hacks.doit3() (or in importing it) ignored"
        pass
    pass

from qt import QApplication, SIGNAL, QRect, QDesktopWidget

from constants import *

from MWsemantics import MWsemantics

##############################################################################

if __name__=='__main__':
    
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
            f=open(rc,'r')
            wd = os.path.normpath(f.readline())
            f.close()
            prefs['WorkingDirectory'] = wd # whether or not isdir(wd)!
             # After this, in theory, this ~/.ne1rc is never again needed.
    if wd:
        if os.path.isdir(wd):
            globalParms['WorkingDirectory'] = wd
        else:
            print "Warning: working directory \"%s\" (from %s)" % (wd, where)
            print " no longer exists; using \"%s\" for this session." % globalParms['WorkingDirectory']
            #e Ideally we'd print this into win.history, but that doesn't exist yet.
            #e Someday we should save it up somewhere and print it into the history when that's created.
        pass
    
    QApplication.setColorSpec(QApplication.CustomColor)
    app=QApplication(sys.argv)
    app.connect(app,SIGNAL("lastWindowClosed ()"),app.quit)

    foo = MWsemantics()

    try:
        # do this, if user asked us to by defining it in .atom-debug-rc
        meth = atom_debug_pre_main_show 
    except:
        pass
    else:
        meth()

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
    
    # Set the main window geometry, then show the window 
    foo.setGeometry(QRect(norm_x, norm_y, norm_w, norm_h))
    foo.show()

# This is debugging code used to find out the origin and size of the fullscreen window
#    foo.setGeometry(QRect(600,50,1000,800)) # KEEP FOR DEBUGGING
#    fooge = QRect(foo.geometry())
#    print "Window origin = ",fooge.left(),",",fooge.top()
#    print "Window width =",fooge.width(),", Window height =",fooge.height()

    try:
        # do this, if user asked us to by defining it in .atom-debug-rc
        meth = atom_debug_post_main_show 
    except:
        pass
    else:
        meth()

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

    if atom_debug_profile_filename:
        profile.run('app.exec_loop()', atom_debug_profile_filename )
        print "\nprofile data was presumably saved into %r" % (atom_debug_profile_filename,)
    else:
        # if you change this code, also change the string literal just above
        app.exec_loop() 

    # end
