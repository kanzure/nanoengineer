# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from qt4transition import *
from Utility import geticon


def setupUi(win):
    MainWindow = win
    
    ##### Select Menu Start #####
    win.selectAllAction = QtGui.QAction(MainWindow)
    win.selectAllAction.setEnabled(True)
    win.selectAllAction.setIcon(geticon("ui/actions/Tools/Select/Select_All"))
    win.selectAllAction.setObjectName("selectAllAction")

    win.selectNoneAction = QtGui.QAction(MainWindow)
    win.selectNoneAction.setIcon(geticon("ui/actions/Tools/Select/Select_None"))
    win.selectNoneAction.setObjectName("selectNoneAction")

    win.selectInvertAction = QtGui.QAction(MainWindow)
    win.selectInvertAction.setIcon(geticon("ui/actions/Tools/Select/Select_Invert"))
    win.selectInvertAction.setObjectName("selectInvertAction")
    
    win.selectConnectedAction = QtGui.QAction(MainWindow)
    win.selectConnectedAction.setIcon(geticon("ui/actions/Tools/Select/Select_Connected"))
    win.selectConnectedAction.setObjectName("selectConnectedAction")

    win.selectDoublyAction = QtGui.QAction(MainWindow)
    win.selectDoublyAction.setIcon(geticon("ui/actions/Tools/Select/Select_Doubly"))
    win.selectDoublyAction.setObjectName("selectDoublyAction")
    
    win.selectExpandAction = QtGui.QAction(MainWindow)
    win.selectExpandAction.setIcon(geticon("ui/actions/Tools/Select/Expand"))
    win.selectExpandAction.setObjectName("selectExpandAction")

    win.selectContractAction = QtGui.QAction(MainWindow)
    win.selectContractAction.setIcon(geticon("ui/actions/Tools/Select/Contract"))
    win.selectContractAction.setObjectName("selectContractAction")
    
    win.Select.addAction(win.selectAllAction)
    win.Select.addAction(win.selectNoneAction)
    win.Select.addAction(win.selectInvertAction)
    win.Select.addAction(win.selectConnectedAction)
    win.Select.addAction(win.selectDoublyAction)
    win.Select.addAction(win.selectExpandAction)
    win.Select.addAction(win.selectContractAction)
    
    ##### Select Menu End #####
    
def retranslateUi(win):
    
    win.Select.setTitle(QtGui.QApplication.translate("MainWindow", "&Selection", None, QtGui.QApplication.UnicodeUTF8))
    
    #TOOLS > SELECT  MENU ITEMS
    win.selectAllAction.setText(QtGui.QApplication.translate("MainWindow", "&All", None, QtGui.QApplication.UnicodeUTF8))
    win.selectAllAction.setIconText(QtGui.QApplication.translate("MainWindow", "All", None, QtGui.QApplication.UnicodeUTF8))
    win.selectAllAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select All", None, QtGui.QApplication.UnicodeUTF8))
    win.selectAllAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+A", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setText(QtGui.QApplication.translate("MainWindow", "&None", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setIconText(QtGui.QApplication.translate("MainWindow", "None", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select None", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setText(QtGui.QApplication.translate("MainWindow", "&Invert", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setIconText(QtGui.QApplication.translate("MainWindow", "Invert", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select Invert", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+I", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setText(QtGui.QApplication.translate("MainWindow", "&Connected", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setIconText(QtGui.QApplication.translate("MainWindow", "Connected", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select Connected", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+C", None, QtGui.QApplication.UnicodeUTF8))
    win.selectDoublyAction.setText(QtGui.QApplication.translate("MainWindow", "&Doubly", None, QtGui.QApplication.UnicodeUTF8))
    win.selectDoublyAction.setIconText(QtGui.QApplication.translate("MainWindow", "Doubly", None, QtGui.QApplication.UnicodeUTF8))
    win.selectDoublyAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select Doubly", None, QtGui.QApplication.UnicodeUTF8))
    win.selectExpandAction.setIconText(QtGui.QApplication.translate("MainWindow", "Expand", None, QtGui.QApplication.UnicodeUTF8))
    win.selectExpandAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Expand Selection (Ctrl+D)", None, QtGui.QApplication.UnicodeUTF8))
    win.selectExpandAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+D", None, QtGui.QApplication.UnicodeUTF8))
    win.selectContractAction.setIconText(QtGui.QApplication.translate("MainWindow", "Contract", None, QtGui.QApplication.UnicodeUTF8))
    win.selectContractAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Contract Selection (Ctrl+Shift+D)", None, QtGui.QApplication.UnicodeUTF8))
    win.selectContractAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+D", None, QtGui.QApplication.UnicodeUTF8))
    