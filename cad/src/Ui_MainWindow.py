# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt, QWidget, QVBoxLayout

from icon_utilities import geticon

import Ui_MainWindowWidgets
import Ui_MainWindowWidgetConnections

import Ui_FileMenu
import Ui_EditMenu
import Ui_ViewMenu
import Ui_InsertMenu
import Ui_ToolsMenu
import Ui_SimulationMenu
import Ui_RenderingMenu
import Ui_HelpMenu

import Ui_StandardToolBar
import Ui_ViewToolBar
import Ui_StandardViewsToolBar
import Ui_DisplayStylesToolBar
import Ui_SelectToolBar
import Ui_SimulationToolBar
import Ui_BuildToolsToolBar
import Ui_BuildStructuresToolBar
import Ui_RenderingToolBar

from StatusBar import StatusBar

import env

class Ui_MainWindow(object):
    """
    The Ui_MainWindow class creates the main window and all its widgets.
    """
    def setupUi(self):
        """
        Sets up the main window UI in the following order:
        - Create all main window widgets used by menus and/or toolbars.
        - Create main menu bar and its menus
        - Create main toolbars
        - Create the statusbar
        """
        self.setObjectName("MainWindow")
        self.setEnabled(True)
        self.setWindowIcon(geticon("ui/border/MainWindow"))
        self.setWindowTitle("NanoEngineer-1")
        
        # Set minimum width and height of the main window.
        # To do: Check that the current screen size is at least 800 x 600.
        MINIMUM_MAIN_WINDOW_SIZE = (800, 600) # Mark 2008-02-08
        self.setMinimumWidth(MINIMUM_MAIN_WINDOW_SIZE[0])
        self.setMinimumHeight(MINIMUM_MAIN_WINDOW_SIZE[1])

        # Create all widgets for all main window menus and toolbars.
        Ui_MainWindowWidgets.setupUi(self)
        
        # Set up all main window widget connections to their slots.
        Ui_MainWindowWidgetConnections.setupUi(self)
        
        # Toolbars should come before menus. The only reason this is necessary
        # is that the "View > Toolbars" submenu needs the main window toolbars
        # to be created before it is created (in 
        self._setupToolbars() 
        self._setupMenus()
        
        # Now set all UI text for main window widgets.
        # Note: I intend to compile all retranslateUi() functions into a single
        # function/method soon. mark 2007-12-31.
        self._retranslateUi()
        
        # The central widget of the NE1 main window contains a VBoxLayout
        # containing the Command Toolbar at top. Below that will be either:
        # 1. a Part Window widget (the default), or 
        # 2. a QWorkspace widget (for MDI support) which will contain only
        #    a single Part Window (experimental)
        # The QWorkspace can be enabled by setting the following debug pref
        # to True: "Enable QWorkspace for MDI support? (next session)"
        # Mark 2007-12-31
        _centralWidget = QWidget()
        self.setCentralWidget(_centralWidget)
        self.centralAreaVBoxLayout = QVBoxLayout(_centralWidget)
        self.centralAreaVBoxLayout.setMargin(0)
        self.centralAreaVBoxLayout.setSpacing(0)
        
        # Add the Command Toolbar to the top of the central widget.
        # Note: Main window widgets must have their text set 
        # via retranslateUi() before instantiating CommandToolbar.
        from CommandToolbar import CommandToolbar
        self.commandToolbar = CommandToolbar(self)
        self.centralAreaVBoxLayout.addWidget(self.commandToolbar)
        
        # Create the statusbar for the main window.
        self.setStatusBar(StatusBar(self))
        
        # =
    
        # Create the "What's This?" text for all main window widgets.
        from gui.WhatsThisText_for_MainWindow import createWhatsThisTextForMainWindowWidgets
        createWhatsThisTextForMainWindowWidgets(self)
        
        # IMPORTANT: All main window widgets and their "What's This" text should 
        # be created before this line. [If this is not possible, we'll need to 
        # split out some functions within this one which can be called
        # later on individual QActions and/or QWidgets. bruce 060319]
        from whatsthis_utilities import fix_whatsthis_text_and_links
        fix_whatsthis_text_and_links(self, refix_later = (self.editMenu,)) 
            # (main call) Fixes bug 1136.  Mark 051126.
            # [bruce 060319 added refix_later as part of fixing bug 1421]
        fix_whatsthis_text_and_links(self.toolsMoveRotateActionGroup)
            # This is needed to add links to the "Translate" and "Rotate"
            # QAction widgets on the standard toolbar, since those two
            # widgets are not direct children of the main window. 
            # Fixes one of the many bugs listed in bug 2412. Mark 2007-12-19
    
    def _setupToolbars(self):
        """
        Populates all Main Window toolbars. 
        Also restores the state of toolbars from the NE1 last session.
        """
        
        # Add toolbars to the Top area of the main window (first row)
        toolbarArea = Qt.TopToolBarArea
        Ui_StandardToolBar.setupUi(self, toolbarArea)
        Ui_BuildToolsToolBar.setupUi(self, toolbarArea)
        self.addToolBarBreak (toolbarArea) # Starts second row.
        Ui_ViewToolBar.setupUi(self, toolbarArea)
        Ui_StandardViewsToolBar.setupUi(self, toolbarArea)
        Ui_SimulationToolBar.setupUi(self, toolbarArea)
        
        # Add toolbars to the Right area of the main window.
        toolbarArea = Qt.RightToolBarArea
        Ui_SelectToolBar.setupUi(self, toolbarArea)
        Ui_DisplayStylesToolBar.setupUi(self, toolbarArea)
        Ui_RenderingToolBar.setupUi(self, toolbarArea)
        
        # This is hidden the first time NE1 starts (below).
        # BTW, I don't think the "Build Structures" toolbar is necessary since
        # all its options are available prominentaly on the Command Toolbar.
        # I intend to completely remove it soon. Mark 2008-02-29.
        Ui_BuildStructuresToolBar.setupUi(self, toolbarArea)
        
        from prefs_constants import toolbar_state_prefs_key
        # This fixes bug 2482.
        if not env.prefs[toolbar_state_prefs_key] == 'defaultToolbarState':
            # Restore the state of the toolbars from the last session.
            toolBarState = QtCore.QByteArray(env.prefs[toolbar_state_prefs_key])
            self.restoreState(toolBarState)
        else:
            # No previous session. Hide only these toolbars by default.
            self.buildStructuresToolBar.hide()
        
        return
    
    def _setupMenus(self):
        """
        Populates all main window menus and adds them to the main menu bar.
        """

        # Populate the menus that appear in the main window menu bar.
        Ui_FileMenu.setupUi(self)
        Ui_EditMenu.setupUi(self)
        Ui_ViewMenu.setupUi(self)
        Ui_InsertMenu.setupUi(self)
        Ui_ToolsMenu.setupUi(self)
        Ui_SimulationMenu.setupUi(self)
        Ui_RenderingMenu.setupUi(self)
        Ui_HelpMenu.setupUi(self)

        # Add menus to the main window menu bar.
        self.MenuBar.addAction(self.fileMenu.menuAction())
        self.MenuBar.addAction(self.editMenu.menuAction())
        self.MenuBar.addAction(self.viewMenu.menuAction())
        self.MenuBar.addAction(self.insertMenu.menuAction())
        self.MenuBar.addAction(self.toolsMenu.menuAction())
        self.MenuBar.addAction(self.simulationMenu.menuAction())
        self.MenuBar.addAction(self.renderingMenu.menuAction())
        self.MenuBar.addAction(self.helpMenu.menuAction())

        # Add the MenuBar to the main window.
        self.setMenuBar(self.MenuBar)
        
        return

    def _retranslateUi(self):
        """
        This method centralizes all calls that set UI text for the purpose of 
        making it easier for the programmer to translate the UI into other 
        languages.

        @see: U{B{The Qt Linquist Manual}<http://doc.trolltech.com/4/linguist-manual.html>}
        """
        self.setWindowTitle(QtGui.QApplication.translate(
            "MainWindow", "NanoEngineer-1", 
            None, QtGui.QApplication.UnicodeUTF8))

        # QActions
        Ui_MainWindowWidgets.retranslateUi(self)
        
        # Toolbars
        Ui_StandardToolBar.retranslateUi(self)
        Ui_ViewToolBar.retranslateUi(self)
        Ui_StandardViewsToolBar.retranslateUi(self)
        Ui_DisplayStylesToolBar.retranslateUi(self)
        Ui_BuildStructuresToolBar.retranslateUi(self)
        Ui_BuildToolsToolBar.retranslateUi(self)
        Ui_SelectToolBar.retranslateUi(self)
        Ui_SimulationToolBar.retranslateUi(self)
        Ui_RenderingToolBar.retranslateUi(self)

        # Menus and submenus
        Ui_FileMenu.retranslateUi(self)
        Ui_EditMenu.retranslateUi(self)
        Ui_ViewMenu.retranslateUi(self)     
        Ui_InsertMenu.retranslateUi(self)
        Ui_ToolsMenu.retranslateUi(self)
        Ui_SimulationMenu.retranslateUi(self)
        Ui_RenderingMenu.retranslateUi(self)
        Ui_HelpMenu.retranslateUi(self)
