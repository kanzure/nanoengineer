#! /usr/bin/python
# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

"""Atom

142C41+

"""

__author__ = "Josh"

import sys, os
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
    
    foo.show()

    app.exec_loop()
