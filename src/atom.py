#! /usr/bin/python
# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

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

from qt import QApplication, SIGNAL, QRect, QDesktopWidget

from constants import *

from MWsemantics import MWsemantics

##############################################################################

if __name__=='__main__':
    
    # the default (1000) bombs with large molecules
    sys.setrecursionlimit(5000)

    # Windows Users: .ne1rc must be placed in C:\Documents and Settings\[username]\.ne1rc
    # .ne1rc contains one line, the Working Directory
    # Example: C:\Documents and Settings\Mark\My Documents\MMP Parts
    
    rc = os.path.expanduser("~/.ne1rc")
    if os.path.exists(rc):
        f=open(rc,'r')
        globalParms['WorkingDirectory'] = os.path.normpath(f.readline())
        f.close()
                        
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
    
    # Create desktop widget to obtain screen resolution
    dtop=QDesktopWidget()
    screensize = QRect (dtop.screenGeometry (0))
#    print "Screen resolution = ",screensize.width(),"x",screensize.height()
    
    # Determine normal window origin and size
    # These dimensions work for WinXP. 
    # Not sure what they should be for Mac and Linux. [mark 041230]
    #
    # [bruce 041230 corrected this for Macintosh, and made sure it never exceeds
    #  screen size even on a very small screen.]
    import platform as _platform
    if _platform.is_macintosh():
        # menubar_height = 44 was measured (approximately) on an iMac G5 20 inch
        # screen; I don't know if it's the same on all Macs (or whether it can
        # vary with OS or user settings). (Is there any way of getting this info
        # from Qt? #e)
        menubar_height = 44
    else:
        menubar_height = 0
    
    screen_w = screensize.width()
    screen_h = screensize.height() # of which menubar_height is in use at the top
    
    # use 85% of screen width and 90% of screen height, or more if that would be
    # less than 780 by 560 pixels, but never more than the available space.
    norm_w = int( min(screen_w - 2, max(780, screen_w * 0.85)))
    norm_h = int( min(screen_h - 2, max(560, (screen_h - menubar_height) * 0.90)))
    
    # determine normal window origin
    # [bruce 041230 changed this to center it, but feel free to change this back
    #  by changing the next line to center_it = 0]
    center_it = 1
    if center_it:
        # centered in available area
        norm_x = (screen_w - norm_w) / 2
        norm_y = (screen_h - menubar_height - norm_h) / 2 + menubar_height
    else:
        # at the given absolute position within the available area
        # (but moved towards (0,0) from that, if necessary to keep it all on-screen)
        want_x = 4 # Left (4 pixels)
        want_y = 36 # Top (36 pixels)
        norm_x = min( want_x, (screen_w - norm_w))
        norm_y = min( want_y, (screen_h - menubar_height - norm_h)) + menubar_height
    
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
