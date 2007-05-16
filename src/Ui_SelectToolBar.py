# Copyright 2004-2006 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from qt4transition import *
from wiki_help import QToolBar_WikiHelp
from Utility import geticon

def setupUi(win):
    
    MainWindow = win
    win.selectToolBar = QToolBar_WikiHelp(MainWindow)
    win.selectToolBar.setEnabled(True)
    win.selectToolBar.setGeometry(QtCore.QRect(458,0,89,20))
    win.selectToolBar.setObjectName("selectToolBar")
    
    MainWindow.addToolBar(Qt.TopToolBarArea, win.selectToolBar)
    
    win.selectToolBar.addAction(win.selectAllAction)
    win.selectToolBar.addAction(win.selectNoneAction)
    win.selectToolBar.addAction(win.selectInvertAction)
    win.selectToolBar.addAction(win.selectConnectedAction)
    win.selectToolBar.addAction(win.selectDoublyAction)
    win.selectToolBar.addAction(win.selectExpandAction)
    win.selectToolBar.addAction(win.selectContractAction)    
    
def retranslateUi(win):
    win.selectToolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Select", None, QtGui.QApplication.UnicodeUTF8))
