# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui

def setupUi(win):
    """
    Populates the "Build Tools" menu, a submenu of the "Tools" menu.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    
    # Create and add the "Build Tools" to the View menu.
    win.buildToolsMenu = win.toolsMenu.addMenu("Build Tools")

    # Populate the "Build Structures" menu.
    win.buildToolsMenu.addAction(win.modifyHydrogenateAction)
    win.buildToolsMenu.addAction(win.modifyDehydrogenateAction)
    win.buildToolsMenu.addAction(win.modifyPassivateAction)
    win.buildToolsMenu.addSeparator()
    win.buildToolsMenu.addAction(win.modifyDeleteBondsAction)
    win.buildToolsMenu.addAction(win.modifySeparateAction)
    win.buildToolsMenu.addAction(win.modifyMergeAction)
    win.buildToolsMenu.addSeparator()
    win.buildToolsMenu.addAction(win.modifyAlignCommonAxisAction)
    win.buildToolsMenu.addAction(win.modifyCenterCommonAxisAction)
    win.buildToolsMenu.addSeparator() 

def retranslateUi(win):
    """
    Sets text related attributes for the "Build Tools" submenu, 
    which is a submenu of the "Tools" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.buildToolsMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Build Tools", 
            None, QtGui.QApplication.UnicodeUTF8))