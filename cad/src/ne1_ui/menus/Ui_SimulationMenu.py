# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui
from utilities.icon_utilities import geticon
from utilities.debug_prefs import debug_pref, Choice_boolean_False

def setupUi(win):
    """
    Populates the "Simulation" menu (incuding its "Measurement" submenu) 
    which appears in the main window menu bar.

    @param win: NE1's main window object.
    @type  win: Ui_MainWindow
    """
    
    # Populate the "Measurements" submenu.
    win.measurementsMenu.addAction(win.jigsThermoAction)
    win.measurementsMenu.addAction(win.jigsDistanceAction)
    win.measurementsMenu.addAction(win.jigsAngleAction)
    win.measurementsMenu.addAction(win.jigsDihedralAction)
    
    # Populate the "Simulation" menu.
    win.simulationMenu.addAction(win.simSetupAction) # "Run Dynamics"
    win.simulationMenu.addAction(win.simMoviePlayerAction) # "Play Movie"  
    from utilities.GlobalPreferences import enableProteins
    if enableProteins:
        win.simulationMenu.addSeparator()
        win.simulationMenu.addAction(win.rosettaSetupAction)
    win.simulationMenu.addSeparator()
    win.simulationMenu.addAction(win.jigsMotorAction)
    win.simulationMenu.addAction(win.jigsLinearMotorAction)
    win.simulationMenu.addAction(win.jigsAnchorAction)
    win.simulationMenu.addAction(win.jigsStatAction)
    win.simulationMenu.addAction(win.jigsThermoAction)
    
    win.simulationMenu.addAction(win.simNanoHiveAction)
    
    #NOTE: The GAMESS and ESPImage options are intentionally disabled
    #Disabling these items from the UI was a rattlesnake backlog item. 
    #see this page for details:
    #U{<http://www.nanoengineer-1.net/mediawiki/index.php?title=Rattlesnake_Sprint_Backlog>}
    #See also: UserPrefs.py _hideOrShowTheseWidgetsInUserPreferenceDialog method
    #where the widgets in the UserPrefernces dialog corresponding to these actions
    #are hidden. 
    if debug_pref("Show GAMESS and ESP Image UI options",
                  Choice_boolean_False,
                  prefs_key = True):
        win.simulationMenu.addAction(win.jigsGamessAction) # GAMESS
        win.simulationMenu.addAction(win.jigsESPImageAction) # ESP Image
    
def retranslateUi(win):
    """
    Sets text related attributes for the "Simulations" menu.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    win.simulationMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Simulation", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.measurementsMenu.setTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Measurements", 
            None, QtGui.QApplication.UnicodeUTF8))
