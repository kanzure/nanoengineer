# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

from PyQt4 import QtGui
from foundation.wiki_help import QToolBar_WikiHelp

def setupUi(win, toolbarArea):
    """
    Creates and populates the "Simulation" toolbar in the main window.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}

    @param toolbarArea: The ToolBarArea of the main window where this toolbar
                        will live (i.e. top, right, left, bottom).
    @type  toolbarArea: U{B{Qt.ToolBarArea enum}<http://doc.trolltech.com/4.2/qt.html#ToolBarArea-enum>}
    """

    # Create the "Simulation" toolbar.
    win.simulationToolBar = QToolBar_WikiHelp(win)
    win.simulationToolBar.setEnabled(True)
    win.simulationToolBar.setObjectName("simulationToolBar")
    win.addToolBar(toolbarArea, win.simulationToolBar)

    # Populate the "Simulation" toolbar.
    win.simulationToolBar.addAction(win.simSetupAction)
    win.simulationToolBar.addAction(win.simMoviePlayerAction)
    win.simulationToolBar.addSeparator()
    win.simulationToolBar.addAction(win.jigsMotorAction)
    win.simulationToolBar.addAction(win.jigsLinearMotorAction)
    win.simulationToolBar.addAction(win.jigsAnchorAction)
    win.simulationToolBar.addAction(win.jigsStatAction)
    win.simulationToolBar.addAction(win.jigsThermoAction)

    # Create the "Simulation Jigs" menu, to be added to the Simuation toolbar.
    #win.simulationJigsMenu = QtGui.QMenu()
    #win.simulationJigsMenu.setObjectName("simulationJigsMenu")
    #win.simulationJigsAction.setMenu(win.simulationJigsMenu)

    # Populate the "Simulation Jigs" menu.
    #win.simulationJigsMenu.addAction(win.jigsMotorAction)
    #win.simulationJigsMenu.addAction(win.jigsLinearMotorAction)
    #win.simulationJigsMenu.addAction(win.jigsAnchorAction)
    #win.simulationJigsMenu.addAction(win.jigsStatAction)

    #win.simulationToolBar.addAction(win.simulationJigsAction)

    # To do: The simulation measurement menu that appears in the
    # "Simulation" menu and command toolbar is missing from the "Simulation"
    # toolbar. This isn't hard to fix, but it isn't important to do now.
    # To fix, search for "measurementsMenu" in
    # Ui_SimulationMenu.py. That code needs work to look more like the
    # code above that creates and populates the "Simulation Jigs" menu,
    # which I've commented out since I don't think it is necessary
    # (i.e. just place all the jig options on the toolbar, not in a menu).
    # Mark 2007-12-24

def retranslateUi(win):
    """
    Assigns the I{window title} property of the "Simulation" toolbar.

    The window title of the "Simulation" toolbar will be displayed in the popup
    menu under "View > Toolbars".
    """
    win.simulationToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Simulation",
            None, QtGui.QApplication.UnicodeUTF8))
    win.simulationToolBar.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Simulation Toolbar",
            None, QtGui.QApplication.UnicodeUTF8))