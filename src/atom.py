#! /usr/bin/python
# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

"""Atom

142C41+

"""

__author__ = "Josh"

import sys, os

# user-specific debug code to be run before any other imports [bruce 040903]
if __name__=='__main__':
    try:
        rc = "~/.atom-debug-rc"
        rc = os.path.expanduser(rc)
        if os.path.exists(rc):
            execfile(rc)
    except:
        print """exception in execfile(%r); traceback printed to stderr or console; exiting""" % (rc,)
        raise

from qt import QApplication, SIGNAL

from constants import *

from MWsemantics import MWsemantics

##############################################################################

if __name__=='__main__':
    
    # the default (1000) bombs with large molecules
    sys.setrecursionlimit(5000)

    # Windows Users: .atomrc must be placed in C:\Documents and Settings\[username]\.atomrc
    # .atomrc contains one line, the Working Directory
    # Example: C:\Documents and Settings\Mark\My Documents\MMP Parts
    
    rc = os.path.expanduser("~/.atomrc")
    if os.path.exists(rc):
        f=open(rc,'r')
        wd = f.readline()
        # wd has a <cr> at the end which needs to be stripped for Win32 - Mark [2004-10-13]
        globalParms['WorkingDirectory'] = wd[:-1] 
        f.close()
        
    QApplication.setColorSpec(QApplication.CustomColor)
    app=QApplication(sys.argv)
    app.connect(app,SIGNAL("lastWindowClosed ()"),app.quit)

    foo = MWsemantics()
    app.connect(foo.fileExitAction, SIGNAL("activated()"), app.quit)

    try:
        # do this, if user asked us to by defining it in .atom-debug-rc
        meth = atom_debug_pre_main_show 
    except:
        pass
    else:
        meth()

    # show the main window
    foo.show()

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
