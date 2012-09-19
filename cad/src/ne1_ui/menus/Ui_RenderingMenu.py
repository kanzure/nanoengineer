# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Ui_RenderingMenu.py - Menu for Rendering plug-ins like QuteMolX, POV-Ray
and others to come (i.e. Sunflow)

@author: Mark
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""

from PyQt4 import QtGui

def setupUi(win):
    """
    Populates the "Rendering" menu which appears in the main window menu bar.

    @param win: NE1's main window object.
    @type  win: Ui_MainWindow
    """

    # Populate the "Rendering" menu.
    win.renderingMenu.addAction(win.viewQuteMolAction)
    win.renderingMenu.addAction(win.viewRaytraceSceneAction)
    win.renderingMenu.addSeparator()
    win.renderingMenu.addAction(win.setStereoViewAction) # piotr 080516

def retranslateUi(win):
    """
    Sets text related attributes for the "Rendering" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.renderingMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Rendering",
            None, QtGui.QApplication.UnicodeUTF8))