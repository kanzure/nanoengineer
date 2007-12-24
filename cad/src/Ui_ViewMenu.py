# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui

# Hybrid display is an experimental work. Its action and others need to be 
# removed. For now, I am just removing it using the following flag as I have 
# unrelated modifications in other files that need to be changed in order to
# remove this option completely. I will do it after commiting those changes. 
# For now this flag is good enough -- ninad 20070612
SHOW_HYBRID_DISPLAY_MENU = 0

def setupUi(win):    
    """
    Creates and populates the "View" menu (incuding its "Display" and "Modify"
    submenus) in the main menu bar.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """  

    # Create the "View" menu.
    win.viewMenu = QtGui.QMenu(win.MenuBar)
    win.viewMenu.setObjectName("viewMenu")

    # Create and add the "Display" and "Modify" submenus to the View menu.
    win.displayMenu = win.viewMenu.addMenu("Display")      
    win.ModifyMenu = win.viewMenu.addMenu("Modify")

    # Populate the rest of the View menu.
    win.viewMenu.addSeparator()
    win.viewMenu.addAction(win.viewSemiFullScreenAction)
    win.viewMenu.addAction(win.viewFullScreenAction)

    # Populate the "Display" submenu.
    win.displayMenu.addAction(win.dispDefaultAction)
    win.displayMenu.addAction(win.dispInvisAction)
    win.displayMenu.addAction(win.dispLinesAction)
    win.displayMenu.addAction(win.dispTubesAction)
    win.displayMenu.addAction(win.dispBallAction)
    win.displayMenu.addAction(win.dispCPKAction)
    win.displayMenu.addAction(win.dispCylinderAction)
    win.displayMenu.addAction(win.dispSurfaceAction)
    win.displayMenu.addSeparator()
    win.displayMenu.addAction(win.setViewPerspecAction)
    win.displayMenu.addAction(win.setViewOrthoAction)
    win.displayMenu.addSeparator()
    win.displayMenu.addAction(win.viewQuteMolAction)
    win.displayMenu.addAction(win.viewRaytraceSceneAction)
    
    # Populate the "Modify" submenu.
    win.ModifyMenu.addAction(win.viewOrientationAction)
    win.ModifyMenu.addAction(win.setViewFitToWindowAction)
    win.ModifyMenu.addAction(win.setViewZoomtoSelectionAction)
    win.ModifyMenu.addAction(win.viewZoomAboutScreenCenterAction)
    win.ModifyMenu.addAction(win.zoomToolAction)        
    win.ModifyMenu.addAction(win.setViewRecenterAction)
    win.ModifyMenu.addSeparator()
    win.ModifyMenu.addAction(win.rotateToolAction)    
    win.ModifyMenu.addAction(win.panToolAction) 
    win.ModifyMenu.addSeparator()
    win.ModifyMenu.addAction(win.setViewHomeAction)
    win.ModifyMenu.addAction(win.setViewHomeToCurrentAction)
    win.ModifyMenu.addAction(win.saveNamedViewAction)

    # Temporary. See comments at top of this file.
    if SHOW_HYBRID_DISPLAY_MENU:
        win.displayMenu.addAction(win.dispHybridAction)

def retranslateUi(win):
    """
    Sets text related attributes for the "View", "Display" and "Modify" menus.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.viewMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&View", None, QtGui.QApplication.UnicodeUTF8))
    win.displayMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&Display", None, QtGui.QApplication.UnicodeUTF8))
    win.ModifyMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "M&odify", None, QtGui.QApplication.UnicodeUTF8))