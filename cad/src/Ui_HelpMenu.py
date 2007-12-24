# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui

def setupUi(win):
    """
    Creates and populates the "File" menu in the main menubar.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """

    # Create the "Help" menu.
    win.helpMenu = QtGui.QMenu(win.MenuBar)
    win.helpMenu.setObjectName("helpMenu")
    
    # Populate the "Help" menu.
    win.helpMenu.addAction(win.helpKeyboardShortcutsAction)
    win.helpMenu.addAction(win.helpMouseControlsAction)
    win.helpMenu.addAction(win.helpWhatsThisAction)
    win.helpMenu.addSeparator()
    win.helpMenu.addAction(win.helpGraphicsCardAction)
    win.helpMenu.addSeparator()
    win.helpMenu.addAction(win.helpAboutAction)
    
def retranslateUi(win):
    """
    Sets text related attributes for the "Help" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.helpMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&Help", 
            None, QtGui.QApplication.UnicodeUTF8))