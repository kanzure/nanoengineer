# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui

import ne1_ui.menus.Ui_BuildStructuresMenu as Ui_BuildStructuresMenu
import ne1_ui.menus.Ui_BuildToolsMenu as Ui_BuildToolsMenu
import ne1_ui.menus.Ui_SelectMenu as Ui_SelectMenu
import ne1_ui.menus.Ui_DimensionsMenu as Ui_DimensionsMenu

def setupUi(win):
    """
    Populates the "Tools" menu which appears in the main window menu bar.

    @param win: NE1's main window object.
    @type  win: Ui_MainWindow
    """
    
    # Populate all "Tools" submenus.
    Ui_BuildStructuresMenu.setupUi(win)
    Ui_BuildToolsMenu.setupUi(win)
    Ui_DimensionsMenu.setupUi(win)
    Ui_SelectMenu.setupUi(win)

    # Populate the "Tools" menu.
    win.toolsMenu.addAction(win.modifyAdjustSelAction)
    win.toolsMenu.addAction(win.modifyAdjustAllAction)
    win.toolsMenu.addAction(win.simMinimizeEnergyAction)
    win.toolsMenu.addAction(win.checkAtomTypesAction)
    win.toolsMenu.addSeparator()
    win.toolsMenu.addMenu(win.buildStructuresMenu)
    win.toolsMenu.addMenu(win.buildToolsMenu)
    win.toolsMenu.addSeparator()
    win.toolsMenu.addAction(win.toolsExtrudeAction)
    win.toolsMenu.addAction(win.toolsFuseChunksAction)
    win.toolsMenu.addSeparator()
    win.toolsMenu.addAction(win.modifyMirrorAction)
    win.toolsMenu.addAction(win.modifyInvertAction)
    win.toolsMenu.addAction(win.modifyStretchAction)
    win.toolsMenu.addSeparator()
    win.toolsMenu.addMenu(win.dimensionsMenu)
    win.toolsMenu.addMenu(win.selectionMenu)
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

    # Set text for the submenus.
    Ui_BuildStructuresMenu.retranslateUi(win)
    Ui_BuildToolsMenu.retranslateUi(win)
    Ui_SelectMenu.retranslateUi(win)
    Ui_DimensionsMenu.retranslateUi(win)
