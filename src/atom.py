#! /usr/bin/python

"""The MERI Atom!  Molecular CAD and simulation system.

Proud progenitor of Nanorex's Diamond Age.

"""

__author__ = "Josh"

import sys
from qt import QApplication, SIGNAL

from form1 import Form1


##############################################################################

if __name__=='__main__':

    # the default (1000) bombs with large molecules
    sys.setrecursionlimit(5000)

    QApplication.setColorSpec(QApplication.CustomColor)
    app=QApplication(sys.argv)
    app.connect(app,SIGNAL("lastWindowClosed ()"),app.quit)

    foo = Form1()
    app.connect(foo.fileExitAction, SIGNAL("activated()"), app.quit)
    
    foo.show()

    app.exec_loop()
