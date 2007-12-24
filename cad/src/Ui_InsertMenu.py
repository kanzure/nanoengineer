# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui
from debug_prefs import debug_pref, Choice_boolean_False

def setupUi(win):
    """
    Creates and populates the "Insert" menu in the main menubar.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """

    # Create the "Insert" menu.
    win.insertMenu = QtGui.QMenu(win.MenuBar)
    win.insertMenu.setObjectName("Insert")

    # Create, populate and add the "Reference Geometry" menu as a submenu
    # to the "Insert" menu.
    win.referenceGeometryMenu = win.insertMenu.addMenu("Reference Geometry")
    win.referenceGeometryMenu.addAction(win.referencePlaneAction)        
    win.referenceGeometryMenu.addAction(win.jigsGridPlaneAction)
    if debug_pref("Show Insert > Line option",
                  Choice_boolean_False,
                  prefs_key=True):
        win.referenceGeometryMenu.addAction(win.referenceLineAction)  

    # Populate the rest of the "Insert" menu.
    win.insertMenu.addAction(win.jigsAtomSetAction)
    win.insertMenu.addSeparator()
    win.insertMenu.addAction(win.fileInsertAction)
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
    Sets text related attributes for the "Insert" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.insertMenu.setTitle(QtGui.QApplication.translate(
        "MainWindow", "&Insert", 
        None, QtGui.QApplication.UnicodeUTF8))
