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
    Populates the "View" menu (including its "Display", "Modify" and "Toolbars"
    submenus) which appears in the main window menu bar.

    @param win: NE1's main window object.
    @type  win: Ui_MainWindow
    """
    
    # Populate the "Display" submenu.
    win.displayMenu.addAction(win.dispDefaultAction)
    #win.displayMenu.addAction(win.dispInvisAction) # removed by mark 2008-02-25
    win.displayMenu.addAction(win.dispLinesAction)
    win.displayMenu.addAction(win.dispTubesAction)
    win.displayMenu.addAction(win.dispBallAction)
    win.displayMenu.addAction(win.dispCPKAction)
    win.displayMenu.addAction(win.dispDnaCylinderAction)
    win.displayMenu.addAction(win.dispCylinderAction)
    win.displayMenu.addAction(win.dispSurfaceAction)
    win.displayMenu.addSeparator()
    win.displayMenu.addAction(win.dispHideAction)
    win.displayMenu.addAction(win.dispUnhideAction)
    win.displayMenu.addSeparator()
    win.displayMenu.addAction(win.setViewPerspecAction)
    win.displayMenu.addAction(win.setViewOrthoAction)
    win.displayMenu.addSeparator()
    win.displayMenu.addAction(win.viewQuteMolAction)
    win.displayMenu.addAction(win.viewRaytraceSceneAction)
    win.displayMenu.addSeparator()
    win.displayMenu.addAction(win.setStereoViewAction)
    
    # Temporary. See comments at top of this file.
    if SHOW_HYBRID_DISPLAY_MENU:
        win.displayMenu.addAction(win.dispHybridAction)
    
    # Populate the "Modify" submenu.
    win.modifyMenu.addAction(win.viewOrientationAction)
    win.modifyMenu.addAction(win.setViewFitToWindowAction)
    win.modifyMenu.addAction(win.setViewRecenterAction)
    win.modifyMenu.addAction(win.setViewZoomtoSelectionAction)
    win.modifyMenu.addAction(win.zoomToAreaAction)
    win.modifyMenu.addSeparator()
    win.modifyMenu.addAction(win.zoomInOutAction)
    win.modifyMenu.addAction(win.rotateToolAction)    
    win.modifyMenu.addAction(win.panToolAction) 
    win.modifyMenu.addSeparator()
    win.modifyMenu.addAction(win.setViewHomeAction)
    win.modifyMenu.addAction(win.setViewHomeToCurrentAction)
    win.modifyMenu.addAction(win.saveNamedViewAction)
        
    # Create and populate the "Toolbar" submenu. 
    # This is done here since the main window toolbar widgets must be 
    # created first. Mark 2007-12-27
    win.toolbarMenu = win.createPopupMenu()
    
    # Populate the "View" menu.
    win.viewMenu.addMenu(win.displayMenu)
    win.viewMenu.addMenu(win.modifyMenu)
    win.viewMenu.addSeparator()
    win.viewMenu.addAction(win.viewSemiFullScreenAction)
    win.viewMenu.addAction(win.viewFullScreenAction)
    win.viewMenu.addAction(win.viewRulersAction)
    win.viewMenu.addAction(win.viewReportsAction)
    win.viewMenu.addMenu(win.toolbarMenu)
    
def retranslateUi(win):
    """
    Sets text related attributes for the "View", "Display" and "Modify" menus.

    @param win: NE1's mainwindow object.
    @type  win: Ui_MainWindow
    """
    win.viewMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&View", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.displayMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "&Display", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.modifyMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "M&odify", 
            None, QtGui.QApplication.UnicodeUTF8)) 
    win.toolbarMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Toolbars", 
            None, QtGui.QApplication.UnicodeUTF8))