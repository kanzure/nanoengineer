#! /usr/bin/python

"""The MERI Atom!  Molecular CAD and simulation system.

Proud progenitor of Nanorex's Diamond Age.

"""

import sys
from qt import QApplication, SIGNAL

from form1 import Form1


##############################################################################

if __name__=='__main__':

    QApplication.setColorSpec(QApplication.CustomColor)
    app=QApplication(sys.argv)
    app.connect(app,SIGNAL("lastWindowClosed ()"),app.quit)

    foo = Form1()
    foo.show()

    app.exec_loop()
