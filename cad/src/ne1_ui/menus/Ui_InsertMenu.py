# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui
from utilities.debug_prefs import debug_pref, Choice_boolean_False

def setupUi(win):
    """
    Populates the "Insert" menu (incuding its "Reference Geometry" submenu) 
    which appears in the main window menu bar.

    @param win: NE1's main window object.
    @type  win: Ui_MainWindow
    """
    
    # Populate the "Reference Geometry" submenu.
    win.referenceGeometryMenu.addAction(win.referencePlaneAction)        
    win.referenceGeometryMenu.addAction(win.jigsGridPlaneAction)
    if debug_pref("Show Insert > Line option",
                  Choice_boolean_False,
                  prefs_key=True):
        win.referenceGeometryMenu.addAction(win.referenceLineAction)
        
    # Populate the "Insert" menu.
    win.insertMenu.addMenu(win.referenceGeometryMenu)
    win.insertMenu.addAction(win.jigsAtomSetAction)
    win.insertMenu.addSeparator()
    win.insertMenu.addAction(win.fileInsertMmpAction)
    win.insertMenu.addAction(win.fileInsertPdbAction)
    win.insertMenu.addAction(win.partLibAction)
    win.insertMenu.addSeparator()
    win.insertMenu.addAction(win.insertCommentAction)
    
    #Commenting out the following to 'fix' bug 2455
    #(we decided to remove this from the UI for alpha9.1 Only commenting it out 
    #so that it can be reimplemented in future if we decide to do so. (and 
    #thus it won't be 'forgotton' completely) -- ninad 20070619
    ##win.insertMenu.addSeparator()
    ##win.insertMenu.addAction(win.insertPovraySceneAction) 

def retranslateUi(win):
    """
    Sets text related attributes for the "Insert" and "Reference Geometry"
    menus.

    @param win: NE1's mainwindow object.
    @type  win: Ui_MainWindow
    """
    win.insertMenu.setTitle(QtGui.QApplication.translate(
        "MainWindow", "&Insert", 
        None, QtGui.QApplication.UnicodeUTF8))
    win.referenceGeometryMenu.setTitle(QtGui.QApplication.translate(
        "MainWindow", "Reference Geometry", 
        None, QtGui.QApplication.UnicodeUTF8))
