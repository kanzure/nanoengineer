# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from icon_utilities import geticon


def setupUi(win):
    
    MainWindow = win
                               
    win.helpMouseControlsAction = QtGui.QAction(MainWindow)
    win.helpMouseControlsAction.setObjectName("helpMouseControlsAction")
    
    win.helpKeyboardShortcutsAction = QtGui.QAction(MainWindow)
    win.helpKeyboardShortcutsAction.setObjectName("helpKeyboardShortcutsAction")
    
    win.helpGraphicsCardAction = QtGui.QAction(MainWindow)
    win.helpGraphicsCardAction.setObjectName("helpGraphicsCardAction")
    
    win.helpWhatsThisAction = QtGui.QAction(MainWindow)
    win.helpWhatsThisAction.setIcon(geticon("ui/actions/Help/WhatsThis"))
    win.helpWhatsThisAction.setObjectName("helpWhatsThisAction")
    
    win.helpAboutAction = QtGui.QAction(MainWindow)
    win.helpAboutAction.setObjectName("helpAboutAction")
        
    win.helpMenu = QtGui.QMenu(win.MenuBar)
    win.helpMenu.setObjectName("helpMenu")
    
    win.helpMenu.addAction(win.helpKeyboardShortcutsAction)
    win.helpMenu.addAction(win.helpMouseControlsAction)
    win.helpMenu.addAction(win.helpWhatsThisAction)
    win.helpMenu.addSeparator()
    win.helpMenu.addAction(win.helpGraphicsCardAction)
    win.helpMenu.addSeparator()
    win.helpMenu.addAction(win.helpAboutAction)
    
def retranslateUi(win):
    
    win.helpMenu.setTitle(QtGui.QApplication.translate("MainWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
    
    #HELP MENU ITEMS
    win.helpContentsAction.setText(QtGui.QApplication.translate("MainWindow", "&Contents...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpContentsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Contents", None, QtGui.QApplication.UnicodeUTF8))
    win.helpAboutAction.setText(QtGui.QApplication.translate("MainWindow", "&About NanoEngineer-1", None, QtGui.QApplication.UnicodeUTF8))
    win.helpAboutAction.setIconText(QtGui.QApplication.translate("MainWindow", "About NanoEngineer-1", None, QtGui.QApplication.UnicodeUTF8))
    
    win.helpWhatsThisAction.setText(QtGui.QApplication.translate("MainWindow", "What\'s This", None, QtGui.QApplication.UnicodeUTF8))
    win.helpWhatsThisAction.setIconText(QtGui.QApplication.translate("MainWindow", "What\'s This", None, QtGui.QApplication.UnicodeUTF8))
    win.helpGraphicsCardAction.setText(QtGui.QApplication.translate("MainWindow", "Graphics Card Info...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpGraphicsCardAction.setIconText(QtGui.QApplication.translate("MainWindow", "Graphics Card Info", None, QtGui.QApplication.UnicodeUTF8))
    
    win.helpMouseControlsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Mouse Controls...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpMouseControlsAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Mouse Controls", None, QtGui.QApplication.UnicodeUTF8))
    win.helpKeyboardShortcutsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Keyboard Shortcuts...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpKeyboardShortcutsAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Keyboard Shortcuts", None, QtGui.QApplication.UnicodeUTF8))
