# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
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
    
    win.buildStructuresToolBar = QToolBar_WikiHelp(MainWindow)
    win.buildStructuresToolBar.setEnabled(True)
    win.buildStructuresToolBar.setGeometry(QtCore.QRect(458,0,89,20))
    win.buildStructuresToolBar.setObjectName("buildStructuresToolBar")
    
    win.buildStructuresToolBar.addAction(MainWindow.toolsDepositAtomAction)
    win.buildStructuresToolBar.addAction(win.buildDnaAction)
    win.buildStructuresToolBar.addAction(win.insertGrapheneAction)
    win.buildStructuresToolBar.addAction(win.insertNanotubeAction)
    win.buildStructuresToolBar.addAction(MainWindow.toolsCookieCutAction)
    
    
    
    MainWindow.addToolBar(Qt.RightToolBarArea, win.buildStructuresToolBar)
    
def retranslateUi(win):
     win.buildStructuresToolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Build Structures", 
                                                                      None, QtGui.QApplication.UnicodeUTF8))
