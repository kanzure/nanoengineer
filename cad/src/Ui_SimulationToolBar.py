# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from wiki_help import QToolBar_WikiHelp
from icon_utilities import geticon

def setupUi(win):
    """
    Creates and populates the "Simulation" toolbar.
    """
    MainWindow = win
    
    win.simulationToolBar = QToolBar_WikiHelp(MainWindow)
    win.simulationToolBar.setEnabled(True)
    win.simulationToolBar.setGeometry(QtCore.QRect(703,47,69,20))
    win.simulationToolBar.setObjectName("simulationToolBar")
    
    MainWindow.addToolBar(Qt.RightToolBarArea, win.simulationToolBar)
    
    win.simulationJigsMenu = QtGui.QMenu()
    win.simulationJigsMenu.setObjectName("simulationJigsMenu")
    
    win.simulationJigsMenu.addAction(win.jigsMotorAction)
    win.simulationJigsMenu.addAction(win.jigsLinearMotorAction)
    win.simulationJigsMenu.addAction(win.jigsAnchorAction)
    win.simulationJigsMenu.addAction(win.jigsStatAction)
    
    win.simulationJigsAction = QtGui.QAction(MainWindow)
    win.simulationJigsAction.setIcon(geticon("ui/actions/Simulation/Simulation_Jigs.png"))
    win.simulationJigsAction.setObjectName("simulationJigsAction")
    win.simulationJigsAction.setToolTip("Simulation Jigs")
    
    win.simulationJigsAction.setMenu(win.simulationJigsMenu)
    
    win.simulationToolBar.addAction(win.simSetupAction)
    win.simulationToolBar.addAction(win.simulationJigsAction)
    win.simulationToolBar.addAction(MainWindow.simMoviePlayerAction)
    win.simulationToolBar.addAction(win.simPlotToolAction)
    
def retranslateUi(win):
    """
    Assigns the I{window title} property of the "Simulation" toolbar.
    
    The window title of the "Simulation" toolbar will be displayed in the popup 
    menu under "View > Toolbars".
    """
    win.simulationToolBar.setWindowTitle(
        QtGui.QApplication.translate("MainWindow", "Simulation", 
                                     None, QtGui.QApplication.UnicodeUTF8))
