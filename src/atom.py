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

    rc = os.path.expanduser("~/.atomrc")
    if os.path.exists(rc):
        f=open(rc,'r')
        wd = f.readline()
        globalParms['WorkingDirectory'] = wd
        f.close()

    QApplication.setColorSpec(QApplication.CustomColor)
    app=QApplication(sys.argv)
    app.connect(app,SIGNAL("lastWindowClosed ()"),app.quit)

    foo = MWsemantics()
    app.connect(foo.fileExitAction, SIGNAL("activated()"), app.quit)

    try:
        meth = atom_debug_pre_main_show # do this, if user asked us to by defining it in .atom-debug-rc
    except:
        pass
    else:
        meth()
    
    foo.show()

    try:
        meth = atom_debug_post_main_show # do this, if user asked us to by defining it in .atom-debug-rc
    except:
        pass
    else:
        meth()

    app.exec_loop()
