# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from qt4transition import *
from Utility import geticon
from debug import print_compact_traceback

def setupUi(win):
    
    MainWindow = win
    
    win.simulationMenu = QtGui.QMenu(win.MenuBar)
    win.simulationMenu.setObjectName("simulationMenu")
    
    win.simSetupAction = QtGui.QWidgetAction(MainWindow)
    win.simSetupAction.setCheckable(True)
    win.simSetupAction.setChecked(False)
    win.simSetupAction.setEnabled(True)
    win.simSetupAction.setIcon(geticon("ui/actions/Simulation/Run_Dynamics"))
    win.simSetupAction.setObjectName("simSetupAction")
    
    win.simMoviePlayerAction = QtGui.QWidgetAction(MainWindow)
           
            
    win.simMoviePlayerAction.setIcon(geticon("ui/actions/Simulation/Play_Movie"))
    
    win.simPlotToolAction = QtGui.QWidgetAction(MainWindow)
    win.simPlotToolAction.setEnabled(True)
    win.simPlotToolAction.setIcon(geticon("ui/actions/Simulation/Make_Graphs"))
    win.simPlotToolAction.setObjectName("simPlotToolAction")
    
    win.jigsMotorAction = QtGui.QWidgetAction(MainWindow)
    win.jigsMotorAction.setIcon(geticon("ui/actions/Simulation/Rotary_Motor"))
    win.jigsMotorAction.setObjectName("jigsMotorAction")

    win.jigsLinearMotorAction = QtGui.QWidgetAction(MainWindow)
    win.jigsLinearMotorAction.setIcon(geticon("ui/actions/Simulation/Linear_Motor"))
    win.jigsLinearMotorAction.setObjectName("jigsLinearMotorAction")
    
    win.jigsStatAction = QtGui.QWidgetAction(MainWindow)
    win.jigsStatAction.setIcon(geticon("ui/actions/Simulation/Thermostat"))
    win.jigsStatAction.setObjectName("jigsStatAction")
    
    win.jigsThermoAction = QtGui.QWidgetAction(MainWindow)
    win.jigsThermoAction.setIcon(geticon("ui/actions/Simulation/Measurements/Thermometer"))
    win.jigsThermoAction.setObjectName("jigsThermoAction")
    
    win.jigsAnchorAction = QtGui.QWidgetAction(MainWindow)
    win.jigsAnchorAction.setIcon(geticon("ui/actions/Simulation/Anchor"))
    win.jigsAnchorAction.setObjectName("jigsAnchorAction")
       
    win.jigsGamessAction = QtGui.QWidgetAction(MainWindow)
    win.jigsGamessAction.setEnabled(True)
    win.jigsGamessAction.setIcon(geticon("ui/actions/Simulation/GAMESS"))
    win.jigsGamessAction.setObjectName("jigsGamessAction")

    win.jigsESPImageAction = QtGui.QWidgetAction(MainWindow)
    win.jigsESPImageAction.setIcon(geticon("ui/actions/Simulation/ESP_Image"))
    win.jigsESPImageAction.setObjectName("jigsESPImageAction")
    
    win.simulationMenu.addAction(win.simSetupAction) # "Run Dynamics"
    win.simulationMenu.addAction(MainWindow.simMoviePlayerAction) # "Play Movie"
    #Removed from simulation menu and command manager per conversation with Mark. 
    #This option is available in Movie flyout toolbar only. -- ninad 20070627
    ##win.simulationMenu.addAction(win.simPlotToolAction) # "Make Graphs"
    win.simulationMenu.addSeparator()
    win.simulationMenu.addAction(win.jigsMotorAction)
    win.simulationMenu.addAction(win.jigsLinearMotorAction)
    win.simulationMenu.addAction(win.jigsAnchorAction)
    win.simulationMenu.addAction(win.jigsStatAction)
    win.simulationMenu.addSeparator()
    
        
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
    
    win.simulationMenu.addAction(win.jigsGamessAction) # GAMESS
    win.simulationMenu.addAction(win.jigsESPImageAction) # ESP Image
    
def retranslateUi(win):
    win.simulationMenu.setTitle(QtGui.QApplication.translate("MainWindow", "Simulation", None, QtGui.QApplication.UnicodeUTF8))
    win.simSetupAction.setText(QtGui.QApplication.translate("MainWindow", " Run Dynamics...", None, QtGui.QApplication.UnicodeUTF8))
    win.simSetupAction.setIconText(QtGui.QApplication.translate("MainWindow", "Run Dynamics", None, QtGui.QApplication.UnicodeUTF8))
    win.simSetupAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Run Dynamics",
                                                               None, QtGui.QApplication.UnicodeUTF8))
    win.simMoviePlayerAction.setText(QtGui.QApplication.translate("MainWindow", "Play Movie",None, QtGui.QApplication.UnicodeUTF8))
    win.simMoviePlayerAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Play Movie",None, QtGui.QApplication.UnicodeUTF8))    
    win.simPlotToolAction.setText(QtGui.QApplication.translate("MainWindow", "Graphs...", None, QtGui.QApplication.UnicodeUTF8))
    win.simPlotToolAction.setIconText(QtGui.QApplication.translate("MainWindow", "Graphs", None, QtGui.QApplication.UnicodeUTF8))
    
    win.jigsESPImageAction.setText(QtGui.QApplication.translate("MainWindow", "ESP Image", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsESPImageAction.setIconText(QtGui.QApplication.translate("MainWindow", "ESP Image", None, QtGui.QApplication.UnicodeUTF8))
    
    if sys.platform == "win32":
        gms_str = "PC GAMESS"
    else:
        gms_str = "GAMESS"
        
    win.jigsGamessAction.setText(QtGui.QApplication.translate(
        "MainWindow", gms_str, None, QtGui.QApplication.UnicodeUTF8))
    win.jigsGamessAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", gms_str, None, QtGui.QApplication.UnicodeUTF8))
    
    #Simulation Jigs 
    win.jigsLinearMotorAction.setText(QtGui.QApplication.translate("MainWindow", "&Linear Motor", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsLinearMotorAction.setIconText(QtGui.QApplication.translate("MainWindow", "Linear Motor", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsStatAction.setText(QtGui.QApplication.translate("MainWindow", "Thermo&stat", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsStatAction.setIconText(QtGui.QApplication.translate("MainWindow", "Thermostat", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsAnchorAction.setText(QtGui.QApplication.translate("MainWindow", "&Anchor", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsAnchorAction.setIconText(QtGui.QApplication.translate("MainWindow", "Anchor", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsMotorAction.setText(QtGui.QApplication.translate("MainWindow", "&Rotary Motor", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsMotorAction.setIconText(QtGui.QApplication.translate("MainWindow", "Rotary Motor", None, QtGui.QApplication.UnicodeUTF8))

    #Simulation Measurement Jigs
    win.jigsThermoAction.setText(QtGui.QApplication.translate("MainWindow", "&Thermometer", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsThermoAction.setIconText(QtGui.QApplication.translate("MainWindow", "Thermometer", None, QtGui.QApplication.UnicodeUTF8))
    