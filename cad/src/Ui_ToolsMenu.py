# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui

import Ui_BuildStructuresMenu
import Ui_BuildToolsMenu
import Ui_SelectMenu
import Ui_DimensionsMenu

def setupUi(win):
    """
    Creates and populates the "Tools" menu in the main menubar.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """

    # Create the "Tools" menu.
    win.toolsMenu = QtGui.QMenu(win.MenuBar)
    win.toolsMenu.setObjectName("Tools")

    # Populate the "Tools" menu.
    win.toolsMenu.addAction(win.modifyAdjustSelAction)
    win.toolsMenu.addAction(win.modifyAdjustAllAction)
    win.toolsMenu.addAction(win.simMinimizeEnergyAction)
    win.toolsMenu.addSeparator()

    # Create and add the "Build Structures" menu as a submenu to the Tools menu.
    Ui_BuildStructuresMenu.setupUi(win)
    
    # Create and add the "Build Tools" menu as a submenu to the "Tools" menu.
    Ui_BuildToolsMenu.setupUi(win)
    
    # Continue populating the rest of the Tools menu.
    win.toolsMenu.addSeparator()
    win.toolsMenu.addAction(win.toolsExtrudeAction)
    win.toolsMenu.addAction(win.toolsFuseChunksAction)
    win.toolsMenu.addSeparator()
    win.toolsMenu.addAction(win.modifyMirrorAction)
    win.toolsMenu.addAction(win.modifyInvertAction)
    win.toolsMenu.addAction(win.modifyStretchAction)
    win.toolsMenu.addSeparator()
    
    # Create and add the "Dimensions" menu as a submenu to the "Tools" menu.
    Ui_DimensionsMenu.setupUi(win)
    
    # Create and add the "Select" menu as a submenu to the "Tools" menu.
    Ui_SelectMenu.setupUi(win)

    # Add "Preferences" to the bottom of the View menu.
    win.toolsMenu.addSeparator()
    win.toolsMenu.addAction(win.editPrefsAction) 

def retranslateUi(win):
    """
    Sets text related attributes for the "Tools" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.toolsMenu.setTitle(QtGui.QApplication.translate(
        "MainWindow", "&Tools",
        None, QtGui.QApplication.UnicodeUTF8))

    # Set text for the View submenus.
    Ui_BuildStructuresMenu.retranslateUi(win)
    Ui_BuildToolsMenu.retranslateUi(win)
    Ui_SelectMenu.retranslateUi(win)
    Ui_DimensionsMenu.retranslateUi(win)