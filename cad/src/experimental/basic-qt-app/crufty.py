#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""This is a demonstration of some very simple Qt ideas. Qt is so
complicated that you can't just sit down and write a GUI like you
could in Java or Tkinter. You need to start in Qt Designer.

Use designer-qt3 to tweak cruft.ui. Then run
pyuic cruft.ui > cruft.py    or just    make cruft.py
to produce a class that gets inherited by Crufty.

Qt Designer won't do everything you want. You sometimes need to
manually edit the XML in cruft.ui to accomplish things that it can't
do.


"""

import sys

from cruft import Ui_Cruft
from PyQt4.Qt import *

class Crufty(QWidget, Ui_Cruft):

    def __init__(self):
        QWidget.__init__(self, None)
        self.setupUi(self)
        self.connect(self.pushButton1, SIGNAL('clicked()'), self.pushButton1_clicked)
        self.textBrowser.setPlainText('hello')
        self.show()

    def pushButton1_clicked(self):
        print self.textBrowser.toPlainText()
        self.close()

def main():
    app = QApplication(sys.argv)
    cr = Crufty()
    app.exec_()

if __name__ == "__main__":
    main()
