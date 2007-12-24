# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui
from icon_utilities import geticon
from debug_prefs  import debug_pref, Choice_boolean_False

def setupUi(win):
    """
    Creates and populates the "View" menu (incuding its "Display" and "Modify"
    submenus) in the main menu bar.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    
    # Create the "Simulation" menu
    win.simulationMenu = QtGui.QMenu(win.MenuBar)
    win.simulationMenu.setObjectName("simulationMenu")

    # Populate the "Simulation" menu.
    win.simulationMenu.addAction(win.simSetupAction) # "Run Dynamics"
    win.simulationMenu.addAction(win.simMoviePlayerAction) # "Play Movie"  
    win.simulationMenu.addSeparator()
    win.simulationMenu.addAction(win.jigsMotorAction)
    win.simulationMenu.addAction(win.jigsLinearMotorAction)
    win.simulationMenu.addAction(win.jigsAnchorAction)
    win.simulationMenu.addAction(win.jigsStatAction)
    win.simulationMenu.addSeparator()

    # Create, populate and add the "Measurements" menu as a submenu of the 
    # "Simulation" menu.
    win.simulationMeasurementsMenu = win.simulationMenu.addMenu("Measurements")  
    win.simulationMeasurementsMenu.setIcon(geticon(
        "ui/actions/Toolbars/Smart/Dimension"))  
    win.simulationMeasurementsMenu.addAction(win.jigsThermoAction)
    #@@@ Following menu items (dimensions) are also provided in Tools > Dimensions. 
    #Need reconsideration. OK for now -- ninad061107
    win.simulationMeasurementsMenu.addAction(win.jigsDistanceAction)
    win.simulationMeasurementsMenu.addAction(win.jigsAngleAction)
    win.simulationMeasurementsMenu.addAction(win.jigsDihedralAction)
    
    win.simulationMenu.addSeparator()
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