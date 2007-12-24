# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt

import Ui_MainWindowWidgets
import Ui_MainWindowWidgetConnections

import Ui_FileMenu
import Ui_EditMenu
import Ui_ViewMenu
import Ui_InsertMenu
import Ui_ToolsMenu
import Ui_SimulationMenu
import Ui_HelpMenu

import Ui_StandardToolBar
import Ui_ViewToolBar
import Ui_StandardViewsToolBar
import Ui_DisplayStylesToolBar
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
        Sets up the main window menus and toolbars in the following way:
        - Create all main window widgets used by menus and/or toolbars.
        - Create main menu bar and its menus
        - Create main toolbars
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)

        # Create all widgets for all main menus and toolbars.
        Ui_MainWindowWidgets.setupUi(self)
        
        # Set up all main window widget connections to their slots.
        Ui_MainWindowWidgetConnections.setupUi(self)

        # Create the main menu bar.
        self.MenuBar = QtGui.QMenuBar(MainWindow)
        self.MenuBar.setEnabled(True)
        self.MenuBar.setGeometry(QtCore.QRect(0,0,1014,28))
        self.MenuBar.setObjectName("MenuBar")

        # Create the menus for NE1's main menu bar.
        Ui_FileMenu.setupUi(self)
        Ui_EditMenu.setupUi(self)
        Ui_ViewMenu.setupUi(self)
        Ui_InsertMenu.setupUi(self)
        Ui_ToolsMenu.setupUi(self)
        Ui_SimulationMenu.setupUi(self)
        Ui_HelpMenu.setupUi(self)

        # Add menus to NE1's main menu bar.
        self.MenuBar.addAction(self.fileMenu.menuAction())
        self.MenuBar.addAction(self.editMenu.menuAction())
        self.MenuBar.addAction(self.viewMenu.menuAction())
        self.MenuBar.addAction(self.insertMenu.menuAction())
        self.MenuBar.addAction(self.toolsMenu.menuAction())
        self.MenuBar.addAction(self.simulationMenu.menuAction())
        self.MenuBar.addAction(self.helpMenu.menuAction())

        # Add MenuBar to the main window.
        MainWindow.setMenuBar(self.MenuBar)

        # Set up the toolbars for the main window.
        Ui_StandardToolBar.setupUi(self)       
        Ui_ViewToolBar.setupUi(self)
        Ui_StandardViewsToolBar.setupUi(self)
        Ui_DisplayStylesToolBar.setupUi(self)
        Ui_BuildToolsToolBar.setupUi(self)
        Ui_BuildStructuresToolBar.setupUi(self)
        Ui_SelectToolBar.setupUi(self)
        Ui_SimulationToolBar.setupUi(self)

        # Now set all UI text for main window widgets.
        self.retranslateUi(MainWindow)
        
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

        # QActions
        Ui_MainWindowWidgets.retranslateUi(self)

        # Menus and submenus
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
        Ui_StandardViewsToolBar.retranslateUi(self)
        Ui_DisplayStylesToolBar.retranslateUi(self)
        Ui_BuildStructuresToolBar.retranslateUi(self)
        Ui_BuildToolsToolBar.retranslateUi(self)
        Ui_SelectToolBar.retranslateUi(self)
        Ui_SimulationToolBar.retranslateUi(self)