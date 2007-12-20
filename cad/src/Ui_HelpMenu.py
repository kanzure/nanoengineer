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
    """
    This function centralizes all calls that set UI text for the purpose of 
    making it easier for the programmer to translate the UI into other 
    languages.
    
    @param MainWindow: The main window
    @type  MainWindow: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    
    @see: U{B{The Qt Linquist Manual}<http://doc.trolltech.com/4/linguist-manual.html>}
    """
    
    win.helpMenu.setTitle(QtGui.QApplication.translate("MainWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
    
    # "Help" menu items
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
