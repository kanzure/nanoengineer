# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui

def setupUi(win):
    """
    Populates the "Build Structures" menu, a submenu of the "Tools" menu.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    
    # Create and add the "Build Structures" to the View menu.
    win.buildStructuresMenu = win.toolsMenu.addMenu("Build Structures")
    
    # Populate the "Build Structures" menu.
    win.buildStructuresMenu.addAction(win.toolsDepositAtomAction)
    win.buildStructuresMenu.addAction(win.buildDnaAction)   
    win.buildStructuresMenu.addAction(win.insertNanotubeAction)
    win.buildStructuresMenu.addAction(win.insertGrapheneAction)
    win.buildStructuresMenu.addAction(win.toolsCookieCutAction)
    win.buildStructuresMenu.addAction(win.insertAtomAction)
    
    #Disabling Ui_DnaFlyout -- It is initialized by the DNA_DUPLEX command 
    #instead.  Command Toolbar code to be revised and 
    #integrated with the commandSequencer -- Ninad 2007-12-19.
    ##Ui_DnaFlyout.setupUi(MainWindow)
    
def retranslateUi(win):
    """
    Sets text related attributes for the "Build Structures" submenu, 
    which is a submenu of the "Tools" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.buildStructuresMenu.setTitle(QtGui.QApplication.translate(
         "MainWindow", "Build Structures", 
         None, QtGui.QApplication.UnicodeUTF8))