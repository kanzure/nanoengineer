# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt

import Ui_FileMenu
import Ui_EditMenu
import Ui_ViewMenu
import Ui_InsertMenu
import Ui_ToolsMenu
import Ui_SimulationMenu
import Ui_HelpMenu

import Ui_StandardToolBar
import Ui_ViewToolBar
import Ui_SelectToolBar
import Ui_SimulationToolBar
import Ui_BuildToolsToolBar
import Ui_BuildStructuresToolBar

from icon_utilities import geticon

from constants import MULTIPANE_GUI

class Ui_MainWindow(object):
    """
    The Ui_MainWindow class creates the QAction widgets, including the menus
    and toolbars that use them.
    """
    def setupUi(self, MainWindow):
        """
        Sets up the main window QActions (buttons), menus and toolbar.
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)

        if MULTIPANE_GUI:
            self.widget = self.centralWidget()
        else:
            self.widget = QtGui.QWidget(MainWindow)
            self.widget.setGeometry(QtCore.QRect(0,95,1014,593))
            self.widget.setObjectName("widget")
            MainWindow.setCentralWidget(self.widget)
        
        # Create the main menu bar.
        self.MenuBar = QtGui.QMenuBar(MainWindow)
        self.MenuBar.setEnabled(True)
        self.MenuBar.setGeometry(QtCore.QRect(0,0,1014,28))
        self.MenuBar.setObjectName("MenuBar")
        
        # Set up the menus for the main menu bar.
        Ui_FileMenu.setupUi(self)
        Ui_EditMenu.setupUi(self)
        Ui_ViewMenu.setupUi(self)
        Ui_InsertMenu.setupUi(self)
        Ui_ToolsMenu.setupUi(self)
        Ui_SimulationMenu.setupUi(self)
        Ui_HelpMenu.setupUi(self)
        
        # Add menus to the main menu bar.
        self.MenuBar.addAction(self.fileMenu.menuAction())
        self.MenuBar.addAction(self.editMenu.menuAction())
        self.MenuBar.addAction(self.viewMenu.menuAction())
        self.MenuBar.addAction(self.Insert.menuAction())
        self.MenuBar.addAction(self.toolsMenu.menuAction())
        self.MenuBar.addAction(self.simulationMenu.menuAction())
        self.MenuBar.addAction(self.helpMenu.menuAction())
        
        # Add MenuBar to the main window.
        MainWindow.setMenuBar(self.MenuBar)
        
        # Set up the toolbars for the main window.
        Ui_StandardToolBar.setupUi(self)       
        Ui_ViewToolBar.setupUi(self)       
        Ui_BuildToolsToolBar.setupUi(self)
        Ui_BuildStructuresToolBar.setupUi(self)
        Ui_SelectToolBar.setupUi(self)
        Ui_SimulationToolBar.setupUi(self)
        
        # Miscellaneous stuff.

        # This needs to stay until I talk with Bruce about UpdateDashboard(),
        # which calls a method of toolsDoneAction in Command.py. Mark 2007-12-20
        self.toolsDoneAction = QtGui.QAction(MainWindow)
        self.toolsDoneAction.setIcon(geticon(
            "ui/actions/Properties Manager/Done"))
        self.toolsDoneAction.setObjectName("toolsDoneAction")
        
        # The server manager and sim job manager actions. 
        # They are NIY and probably never will be. 
        # If you have questions about them, you can ask me. Mark 2007-12-20.
        self.serverManagerAction = QtGui.QAction(MainWindow)
        self.serverManagerAction.setIcon(geticon("ui/actions/MainWindowUI_image119"))
        self.serverManagerAction.setObjectName("serverManagerAction")
        
        self.simJobManagerAction = QtGui.QAction(MainWindow)
        self.simJobManagerAction.setIcon(geticon("ui/actions/MainWindowUI_image118"))
        self.simJobManagerAction.setObjectName("simJobManagerAction")

        self.createMoviePlayerActions(MainWindow)
        
        self.retranslateUi(MainWindow)
        
        QtCore.QObject.connect(self.fileExitAction,
                               QtCore.SIGNAL("activated()"),
                               MainWindow.close)

        # bruce 071008 removed this call of connectSlotsByName, since
        # we don't appear to be taking advantage of it
        # (since we have no slots named on_<widgetname>_<signalname>)
##        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        return
    
    def createMoviePlayerActions(self, MainWindow):
        """
        Creates many of the movie player actions for the PM.
        This code should be moved to Ui_MoviePropertyManager.py.
        """
        # These actions appear to be used in the Movie Player PM. These should
        # probably be moved to Ui_MoviePropertyManager.py. Mark 2007-12-20.
        
        self.movieResetAction = QtGui.QAction(MainWindow)
        self.movieResetAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Reset"))
        self.movieResetAction.setObjectName("movieResetAction")

        self.movieMoveToEndAction = QtGui.QAction(MainWindow)
        self.movieMoveToEndAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Move_To_End"))
        self.movieMoveToEndAction.setObjectName("movieMoveToEndAction")

        self.moviePauseAction = QtGui.QAction(MainWindow)
        self.moviePauseAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Pause"))
        self.moviePauseAction.setObjectName("moviePauseAction")

        self.moviePlayAction = QtGui.QAction(MainWindow)
        self.moviePlayAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Play_Forward"))
        self.moviePlayAction.setVisible(True)
        self.moviePlayAction.setObjectName("moviePlayAction")
        
        self.moviePlayActiveAction = QtGui.QAction(MainWindow)
        self.moviePlayActiveAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Play_Forward_Active"))
        self.moviePlayActiveAction.setObjectName("moviePlayActiveAction")

        self.fileSaveMovieAction = QtGui.QAction(MainWindow)
        self.fileSaveMovieAction.setIcon(geticon("ui/actions/Properties Manager/Save"))
        self.fileSaveMovieAction.setObjectName("fileSaveMovieAction")

        self.moviePlayRevAction = QtGui.QAction(MainWindow)
        self.moviePlayRevAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Play_Reverse"))
        self.moviePlayRevAction.setObjectName("moviePlayRevAction")
        
        self.moviePlayRevActiveAction = QtGui.QAction(MainWindow)
        self.moviePlayRevActiveAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Play_Reverse_Active"))
        self.moviePlayRevActiveAction.setObjectName("moviePlayRevActiveAction")

        self.fileOpenMovieAction = QtGui.QAction(MainWindow)
        self.fileOpenMovieAction.setIcon(geticon("ui/actions/Properties Manager/Open"))
        self.fileOpenMovieAction.setObjectName("fileOpenMovieAction")

        self.movieInfoAction = QtGui.QAction(MainWindow)
        self.movieInfoAction.setIcon(geticon("ui/actions/Properties Manager/Movie_Info"))
        self.movieInfoAction.setObjectName("movieInfoAction")
                
        return

    def retranslateUi(self, MainWindow):
        """
        This method centralizes all calls that set UI text for the purpose of 
        making it easier for the programmer to translate the UI into other 
        languages.
        
        @param MainWindow: The main window
        @type  MainWindow: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
        
        @see: U{B{The Qt Linquist Manual}<http://doc.trolltech.com/4/linguist-manual.html>}
        """
        MainWindow.setWindowTitle(QtGui.QApplication.translate(
            "MainWindow", 
            "NanoEngineer-1", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
               
        # Menus and SubMenus
        Ui_FileMenu.retranslateUi(self)
        Ui_EditMenu.retranslateUi(self)
        Ui_ViewMenu.retranslateUi(self)     
        Ui_InsertMenu.retranslateUi(self)
        Ui_ToolsMenu.retranslateUi(self)
        Ui_SimulationMenu.retranslateUi(self)
        Ui_HelpMenu.retranslateUi(self)
        
        # Toolbars
        Ui_StandardToolBar.retranslateUi(self)
        Ui_ViewToolBar.retranslateUi(self)
        Ui_BuildStructuresToolBar.retranslateUi(self)
        Ui_BuildToolsToolBar.retranslateUi(self)
        Ui_SelectToolBar.retranslateUi(self)
        Ui_SimulationToolBar.retranslateUi(self)
                                
        # Menu Item (Action items) text and icons
                       
        # UNUSED MENU ITEMS.
        self.viewDefviewAction.setText(QtGui.QApplication.translate("MainWindow", "Orientations", None, QtGui.QApplication.UnicodeUTF8))
        self.viewDefviewAction.setIconText(QtGui.QApplication.translate("MainWindow", "Orientations", None, QtGui.QApplication.UnicodeUTF8))
        self.viewDefviewAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Default Views", None, QtGui.QApplication.UnicodeUTF8))
        self.changeBackgroundColorAction.setText(QtGui.QApplication.translate("MainWindow", "&Background Color...", None, QtGui.QApplication.UnicodeUTF8))
        self.changeBackgroundColorAction.setIconText(QtGui.QApplication.translate("MainWindow", "Background Color...", None, QtGui.QApplication.UnicodeUTF8))
        
        self.toolsDoneAction.setText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
        self.toolsDoneAction.setIconText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
                
        self.modifyStretchAction.setText(QtGui.QApplication.translate("MainWindow", "S&tretch", None, QtGui.QApplication.UnicodeUTF8))
        self.modifyStretchAction.setIconText(QtGui.QApplication.translate("MainWindow", "Stretch", None, QtGui.QApplication.UnicodeUTF8))      
                
        self.movieResetAction.setText(QtGui.QApplication.translate("MainWindow", "Reset Movie", None, QtGui.QApplication.UnicodeUTF8))
        self.movieResetAction.setIconText(QtGui.QApplication.translate("MainWindow", "Reset Movie", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayRevActiveAction.setText(QtGui.QApplication.translate("MainWindow", "Play Reverse", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayRevActiveAction.setIconText(QtGui.QApplication.translate("MainWindow", "Play Reverse", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayActiveAction.setText(QtGui.QApplication.translate("MainWindow", "Play Forward", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayActiveAction.setIconText(QtGui.QApplication.translate("MainWindow", "Play Forward", None, QtGui.QApplication.UnicodeUTF8))
        self.movieMoveToEndAction.setText(QtGui.QApplication.translate("MainWindow", "Advance To End", None, QtGui.QApplication.UnicodeUTF8))
        self.movieMoveToEndAction.setIconText(QtGui.QApplication.translate("MainWindow", "Advance To End", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePauseAction.setText(QtGui.QApplication.translate("MainWindow", "Pause", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePauseAction.setIconText(QtGui.QApplication.translate("MainWindow", "Pause", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayAction.setText(QtGui.QApplication.translate("MainWindow", "Play Forward", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayAction.setIconText(QtGui.QApplication.translate("MainWindow", "Play Forward", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Play Forward", None, QtGui.QApplication.UnicodeUTF8))
        
        
        self.dispSetEltable1Action.setText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Default", None, QtGui.QApplication.UnicodeUTF8))
        self.dispSetEltable1Action.setIconText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Default", None, QtGui.QApplication.UnicodeUTF8))
        self.dispSetEltable2Action.setText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Alternate", None, QtGui.QApplication.UnicodeUTF8))
        self.dispSetEltable2Action.setIconText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Alternate", None, QtGui.QApplication.UnicodeUTF8))
        self.fileSaveMovieAction.setText(QtGui.QApplication.translate("MainWindow", "Save Movie File...", None, QtGui.QApplication.UnicodeUTF8))
        self.fileSaveMovieAction.setIconText(QtGui.QApplication.translate("MainWindow", "Save Movie File...", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayRevAction.setText(QtGui.QApplication.translate("MainWindow", "Play Reverse", None, QtGui.QApplication.UnicodeUTF8))
        self.moviePlayRevAction.setIconText(QtGui.QApplication.translate("MainWindow", "Play Reverse", None, QtGui.QApplication.UnicodeUTF8))
        self.fileOpenMovieAction.setText(QtGui.QApplication.translate("MainWindow", "Open Movie File...", None, QtGui.QApplication.UnicodeUTF8))
        self.fileOpenMovieAction.setIconText(QtGui.QApplication.translate("MainWindow", "Open Movie File...", None, QtGui.QApplication.UnicodeUTF8))
        self.movieInfoAction.setText(QtGui.QApplication.translate("MainWindow", "Movie Information", None, QtGui.QApplication.UnicodeUTF8))
        self.movieInfoAction.setIconText(QtGui.QApplication.translate("MainWindow", "Movie Information", None, QtGui.QApplication.UnicodeUTF8))
        
        self.dispElementColorSettingsAction.setText(QtGui.QApplication.translate("MainWindow", "Element Color Settings...", None, QtGui.QApplication.UnicodeUTF8))
        self.dispElementColorSettingsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Element Color Settings...", None, QtGui.QApplication.UnicodeUTF8))
        
        self.dispLightingAction.setText(QtGui.QApplication.translate("MainWindow", "Lighting...", None, QtGui.QApplication.UnicodeUTF8))
        self.dispLightingAction.setIconText(QtGui.QApplication.translate("MainWindow", "Lighting", None, QtGui.QApplication.UnicodeUTF8))
        self.dispResetAtomsDisplayAction.setText(QtGui.QApplication.translate("MainWindow", "Reset Atoms Display", None, QtGui.QApplication.UnicodeUTF8))
        self.dispResetAtomsDisplayAction.setIconText(QtGui.QApplication.translate("MainWindow", "Reset Atoms Display", None, QtGui.QApplication.UnicodeUTF8))
        self.dispShowInvisAtomsAction.setText(QtGui.QApplication.translate("MainWindow", "Show Invisible Atoms", None, QtGui.QApplication.UnicodeUTF8))
        self.dispShowInvisAtomsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Show Invisible Atoms", None, QtGui.QApplication.UnicodeUTF8))
        
        self.simJobManagerAction.setText(QtGui.QApplication.translate("MainWindow", "Job Manager...", None, QtGui.QApplication.UnicodeUTF8))
        self.simJobManagerAction.setIconText(QtGui.QApplication.translate("MainWindow", "Job Manager...", None, QtGui.QApplication.UnicodeUTF8))
        self.serverManagerAction.setText(QtGui.QApplication.translate("MainWindow", "Server Manager...", None, QtGui.QApplication.UnicodeUTF8))
        self.serverManagerAction.setIconText(QtGui.QApplication.translate("MainWindow", "Server Manager...", None, QtGui.QApplication.UnicodeUTF8))
   
        self.simNanoHiveAction.setText(QtGui.QApplication.translate("MainWindow", "Nano-Hive...", None, QtGui.QApplication.UnicodeUTF8))
        self.simNanoHiveAction.setIconText(QtGui.QApplication.translate("MainWindow", "Nano-Hive", None, QtGui.QApplication.UnicodeUTF8))
 
        self.fileSaveSelectionAction.setIconText(QtGui.QApplication.translate("MainWindow", "Save Selection...", None, QtGui.QApplication.UnicodeUTF8))
        self.viewRotatePlus90Action.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate View +90", None, QtGui.QApplication.UnicodeUTF8))
        self.viewRotateMinus90Action.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate View -90", None, QtGui.QApplication.UnicodeUTF8))
                
        self.viewNormalToAction.setIconText(QtGui.QApplication.translate("MainWindow", "Set View Normal To", None, QtGui.QApplication.UnicodeUTF8))
        self.viewNormalToAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Set View Normal To", None, QtGui.QApplication.UnicodeUTF8))
        self.viewParallelToAction.setIconText(QtGui.QApplication.translate("MainWindow", "Set View Parallel To", None, QtGui.QApplication.UnicodeUTF8))
        self.viewParallelToAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Set View Parallel To", None, QtGui.QApplication.UnicodeUTF8))
        
        self.viewQuteMolAction.setIconText(QtGui.QApplication.translate("MainWindow", "QuteMol", None, QtGui.QApplication.UnicodeUTF8))
        self.viewRaytraceSceneAction.setIconText(QtGui.QApplication.translate("MainWindow", "POV-Ray", None, QtGui.QApplication.UnicodeUTF8))
