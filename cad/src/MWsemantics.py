# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
MWsemantics.py provides the main window class, MWsemantics.


$Id$

History: too much to mention, except for breakups of the file.

[maybe some of those are not listed here?]
bruce 050413 split out movieDashboardSlotsMixin
bruce 050907 split out fileSlotsMixin
mark 060120 split out viewSlotsMixin

[Much more splitup of this file is needed. Ideally we would
split up the class MWsemantics (as for cookieMode), not just the file.]

[some of that splitup has been done, now, by Ninad in the Qt4 branch]
"""

from qt4transition import qt4todo
from qt4transition import qt4warning

from PyQt4 import QtGui

from PyQt4.Qt import Qt
from PyQt4.Qt import QFont
from PyQt4.Qt import QAction
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import QGridLayout
from PyQt4.Qt import QMenu
from PyQt4.Qt import QIcon

from PyQt4.Qt import QMainWindow, QFrame, SIGNAL, QWidget
from PyQt4.Qt import QSplitter, QMessageBox
from PyQt4.Qt import QColorDialog
from PyQt4 import QtCore
from PyQt4.Qt import QToolBar
from PyQt4.Qt import QStatusBar
from GLPane import GLPane 
from elements import PeriodicTable
from model.assembly import assembly 
from drawer import get_gl_info_string ## grantham 20051201
from Ui_PartWindow import PartWindow, GridPosition
import os, sys
from modelTree import modelTree 
import platform
from icon_utilities import geticon

from PlatformDependent import find_or_make_Nanorex_directory
from PlatformDependent import make_history_filename

from StatusBar import StatusBar

from elementColors import elementColors 

from ViewOrientationWindow import ViewOrientationWindow # Ninad 061121

from debug import print_compact_traceback
from debug_prefs import debug_pref, Choice_boolean_False

from MainWindowUI import Ui_MainWindow
from utilities.Log import greenmsg, redmsg, orangemsg

import Ui_DnaFlyout

from gui.whatsthis import createWhatsThisTextForMainWindowWidgets, fix_whatsthis_text_and_links

from movieMode import movieDashboardSlotsMixin
from ops_files import fileSlotsMixin
from ops_files import recentfiles_use_QSettings
from ops_view import viewSlotsMixin 
from changes import register_postinit_object
import preferences
import env 
import undo_internals

from prefs_constants import nanohive_enabled_prefs_key
from prefs_constants import gamess_enabled_prefs_key
from prefs_constants import gromacs_enabled_prefs_key
from prefs_constants import cpp_enabled_prefs_key
from prefs_constants import zoomAboutScreenCenter_prefs_key
from prefs_constants import workingDirectory_prefs_key
from prefs_constants import getDefaultWorkingDirectory
from prefs_constants import rememberWinPosSize_prefs_key
from prefs_constants import captionPrefix_prefs_key
from prefs_constants import captionSuffix_prefs_key
from prefs_constants import captionFullPath_prefs_key

from constants import diTrueCPK
from constants import diTUBES
from constants import diBALL
from constants import diLINES
from constants import diCYLINDER
from constants import diSURFACE
from constants import diINVISIBLE
from constants import diDEFAULT
from constants import MULTIPANE_GUI

elementSelectorWin = None
elementColorsWin = None

eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]

eCCBtab2 = {}
for i,elno in zip(range(len(eCCBtab1)), eCCBtab1):
    eCCBtab2[elno] = i


########################################################################

class MWsemantics(QMainWindow, fileSlotsMixin, viewSlotsMixin, movieDashboardSlotsMixin, Ui_MainWindow, object):
    "The single Main Window object."
    #bruce 071008 added object superclass

    #bruce 050413 split out movieDashboardSlotsMixin, which needs to come before MainWindow
    # in the list of superclasses, since MainWindow overrides its methods with "NIM stubs".
    #bruce 050906: same for fileSlotsMixin.
    #mark 060120: same for viewSlotsMixin.

    initialised = 0 #bruce 041222
    _ok_to_autosave_geometry_changes = False #bruce 051218

    # This determines the location of "Open Recent Files" menu item in the File Menu. Mark 060807.
    RECENT_FILES_MENU_ITEM = None

    # The default font for the main window. If I try to set defaultFont using QApplition.font() here,
    # it returns Helvetica pt12 (?), so setting it below in the constructor is a workaround.
    # Mark 2007-05-27.
    defaultFont = None

    def __init__(self, parent = None, name = None):

        assert isinstance(self, object) #bruce 071008

        self._init_part_two_done = False
        self._activepw = None

        self.orientationWindow = None     
       
        self.sequenceEditor = None  #see self.createSequenceEditrIfNeeded 
                                    #for details
        
        self.rotaryMotorPropMgr = None
        self.linearMotorPropMgr = None
        self.dnaDuplexPropMgr   = None
        self.planePropMgr = None
        
        # These boolean flags, if True, stop the execution of slot 
        # methods that are called because the state of 'self.viewFullScreenAction
        # or self.viewSemiFullScreenAction is changed. May be there is a way to 
        # do this using QActionGroup (which make the actions mutually exclusive)
        #.. tried that but it didn't work. After doing this when I tried to 
        #  toggle the checked action in the action group, it didn't work
        #..will try it again sometime in future. The following flags are good 
        # enough for now. See methods self.showFullScreen and 
        # self.showSemiFullScreen where they are used. -- Ninad 2007-12-06
        self._block_viewFullScreenAction_event = False
        self._block_viewSemiFullScreenAction_event = False
        #The following maintains a list of all widgets that are hidden during
        #the FullScreen or semiFullScreen mode. Thislist is then used in 
        #self.showNormal to show the hidden widgets if any. The list is cleared 
        #at the end of self.showNormal
        self._widgetToHideDuringFullScreenMode = []

        undo_internals.just_before_mainwindow_super_init()

        qt4warning('MainWindow.__init__(self, parent, name, Qt.WDestructiveClose) - what is destructive close?')
        QMainWindow.__init__(self, parent)

        self.defaultFont = QFont(self.font()) # Makes copy of app's default font.

        self.DefaultSelAction = QAction(self)
        self.LassoSelAction = QAction(self)
        self.RectCornerSelAction = QAction(self)
        self.RectCtrSelAction = QAction(self)
        self.SquareSelAction = QAction(self)
        self.TriangleSelAction = QAction(self)
        self.DiamondSelAction = QAction(self)
        self.CircleSelAction = QAction(self)
        self.HexagonSelAction = QAction(self)

        self.orthoPerpActionGroup = QtGui.QActionGroup(self)  
        self.orthoPerpActionGroup.setExclusive(True)

        self.setViewPerspecAction = QAction(self)
        self.setViewPerspecAction.setText(QtGui.QApplication.translate("MainWindow", "Perspective",
                                                                       None, QtGui.QApplication.UnicodeUTF8))
        self.setViewPerspecAction.setCheckable(True)

        self.setViewOrthoAction = QAction(self)
        self.setViewOrthoAction.setText(QtGui.QApplication.translate("MainWindow", "Orthographic",
                                                                     None, QtGui.QApplication.UnicodeUTF8))
        self.setViewOrthoAction.setCheckable(True)

        self.orthoPerpActionGroup.addAction(self.setViewPerspecAction)
        self.orthoPerpActionGroup.addAction(self.setViewOrthoAction)


        self.toolsSelectAtomsAction = QAction(self)
        self.simMoviePlayerAction = QAction(self)
        self.setupUi(self)	         

        self.connect(self.changeBackgroundColorAction,SIGNAL("triggered()"),self.changeBackgroundColor)
        self.connect(self.dispBallAction,SIGNAL("triggered()"),self.dispBall)
        self.connect(self.dispDefaultAction,SIGNAL("triggered()"),self.dispDefault)
        self.connect(self.dispElementColorSettingsAction,SIGNAL("triggered()"),self.dispElementColorSettings)
        self.connect(self.dispInvisAction,SIGNAL("triggered()"),self.dispInvis)
        self.connect(self.dispLightingAction,SIGNAL("triggered()"),self.dispLighting)
        self.connect(self.dispLinesAction,SIGNAL("triggered()"),self.dispLines)
        self.connect(self.dispObjectColorAction,SIGNAL("triggered()"),self.dispObjectColor)
        self.connect(self.dispResetAtomsDisplayAction,SIGNAL("triggered()"),self.dispResetAtomsDisplay)
        self.connect(self.dispResetChunkColorAction,SIGNAL("triggered()"),self.dispResetChunkColor)
        self.connect(self.dispShowInvisAtomsAction,SIGNAL("triggered()"),self.dispShowInvisAtoms)
        self.connect(self.dispTubesAction,SIGNAL("triggered()"),self.dispTubes)
        self.connect(self.dispCPKAction,SIGNAL("triggered()"),self.dispCPK)
        self.connect(self.dispHybridAction,SIGNAL("triggered()"),self.dispHybrid)

        self.connect(self.editAutoCheckpointingAction,SIGNAL("toggled(bool)"),self.editAutoCheckpointing)
        self.connect(self.editClearUndoStackAction,SIGNAL("triggered()"),self.editClearUndoStack)
        self.connect(self.editCopyAction,SIGNAL("triggered()"),self.editCopy)
        self.connect(self.editCutAction,SIGNAL("triggered()"),self.editCut)
        self.connect(self.editDeleteAction,SIGNAL("triggered()"),self.killDo)
        #self.connect(self.editFindAction,SIGNAL("triggered()"),self.editFind)
        self.connect(self.editMakeCheckpointAction,SIGNAL("triggered()"),self.editMakeCheckpoint)
        self.connect(self.editPasteAction,SIGNAL("triggered()"),self.editPaste)
        self.connect(self.pasteFromClipboardAction, 
                     SIGNAL("triggered()"),
                     self.editPasteFromClipboard )

        self.connect(self.partLibAction, 
                     SIGNAL("triggered()"),
                     self.insertPartFromPartLib)
        
        self.connect(self.viewFullScreenAction, 
                     SIGNAL("toggled(bool)"), 
                     self.setViewFullScreen)
        self.connect(self.viewSemiFullScreenAction, 
                     SIGNAL("toggled(bool)"), 
                     self.setViewSemiFullScreen)
                     

        self.connect(self.editPrefsAction,SIGNAL("triggered()"),self.editPrefs)
        self.connect(self.editRedoAction,SIGNAL("triggered()"),self.editRedo)
        self.connect(self.editUndoAction,SIGNAL("triggered()"),self.editUndo)
        #self.connect(self.fileClearAction,SIGNAL("triggered()"),self.fileClear)
        self.connect(self.fileCloseAction,SIGNAL("triggered()"),self.fileClose)
        self.connect(self.fileExitAction,SIGNAL("triggered()"), self.close)
        #self.connect(self.fileImageAction,SIGNAL("triggered()"),self.fileImage)
        self.connect(self.fileInsertAction,SIGNAL("triggered()"),self.fileInsert)
        self.connect(self.fileOpenAction,SIGNAL("triggered()"),self.fileOpen)
        self.connect(self.fileOpenMovieAction,SIGNAL("triggered()"),self.fileOpenMovie)
        self.connect(self.fileSaveAction,SIGNAL("triggered()"),self.fileSave)
        self.connect(self.fileSaveAsAction,SIGNAL("triggered()"),self.fileSaveAs)
        self.connect(self.fileSaveMovieAction,SIGNAL("triggered()"),self.fileSaveMovie)
        self.connect(self.fileSaveSelectionAction,SIGNAL("triggered()"),self.fileSaveSelection)
        self.connect(self.fileSetWorkDirAction,SIGNAL("triggered()"),self.fileSetWorkDir)
        #self.connect(self.frameNumberSB,SIGNAL("valueChanged(int)"),self.moviePlayFrame)
        #self.connect(self.frameNumberSL,SIGNAL("valueChanged(int)"),self.movieSlider)
        self.connect(self.helpAboutAction,SIGNAL("triggered()"),self.helpAbout)
        #self.connect(self.helpContentsAction,SIGNAL("triggered()"),self.helpContents)
        self.connect(self.helpGraphicsCardAction,SIGNAL("triggered()"),self.helpGraphicsCard)
        self.connect(self.helpKeyboardShortcutsAction,SIGNAL("triggered()"),self.helpKeyboardShortcuts)
        self.connect(self.helpMouseControlsAction,SIGNAL("triggered()"),self.helpMouseControls)
        self.connect(self.helpWhatsThisAction,SIGNAL("triggered()"),self.helpWhatsThis)
        #self.connect(self.buildDnaAction,SIGNAL("triggered()"),self.insertDna)
        self.connect(self.buildDnaAction,SIGNAL("triggered()"),self.activateDnaTool)
        self.connect(self.insertCommentAction,SIGNAL("triggered()"),self.insertComment)
        self.connect(self.insertNanotubeAction,SIGNAL("triggered()"),self.insertNanotube)
        self.connect(self.insertGrapheneAction,SIGNAL("triggered()"),self.insertGraphene)

        self.connect(self.jigsAnchorAction,SIGNAL("triggered()"),self.makeAnchor)
        self.connect(self.jigsAngleAction,SIGNAL("triggered()"),self.makeMeasureAngle)
        self.connect(self.jigsAtomSetAction,SIGNAL("triggered()"),self.makeAtomSet)
        #self.connect(self.jigsBearingAction,SIGNAL("triggered()"),self.makeBearing)
        self.connect(self.jigsDihedralAction,SIGNAL("triggered()"),self.makeMeasureDihedral)
        self.connect(self.jigsDistanceAction,SIGNAL("triggered()"),self.makeMeasureDistance)
        #self.connect(self.jigsDynoAction,SIGNAL("triggered()"),self.makeDyno)
        self.connect(self.jigsESPImageAction,SIGNAL("triggered()"),self.makeESPImage)
        self.connect(self.jigsGamessAction,SIGNAL("triggered()"),self.makeGamess)
        self.connect(self.jigsGridPlaneAction,SIGNAL("triggered()"),self.makeGridPlane)

        self.connect(self.referencePlaneAction,SIGNAL("triggered()"),
                     self.createPlane)
        self.connect(self.referenceLineAction,SIGNAL("triggered()"),
                     self.createPolyLine)

        #self.connect(self.jigsHandleAction,SIGNAL("triggered()"),self.makeHandle)
        #self.connect(self.jigsHeatsinkAction,SIGNAL("triggered()"),self.makeHeatsink)

        self.connect(self.jigsLinearMotorAction,
                     SIGNAL("triggered()"),
                     self.makeLinearMotor)

        self.connect(self.jigsMotorAction,
                     SIGNAL("triggered()"),
                     self.makeRotaryMotor)

        #self.connect(self.jigsSpringAction,SIGNAL("triggered()"),self.makeSpring)
        self.connect(self.jigsStatAction,SIGNAL("triggered()"),self.makeStat)
        self.connect(self.jigsThermoAction,SIGNAL("triggered()"),self.makeThermo)
        self.connect(self.modifyAlignCommonAxisAction,SIGNAL("triggered()"),self.modifyAlignCommonAxis)
        self.connect(self.modifyCenterCommonAxisAction,SIGNAL("triggered()"),self.modifyCenterCommonAxis)
        self.connect(self.modifyDehydrogenateAction,SIGNAL("triggered()"),self.modifyDehydrogenate)
        self.connect(self.modifyDeleteBondsAction,SIGNAL("triggered()"),self.modifyDeleteBonds)
        self.connect(self.modifyHydrogenateAction,SIGNAL("triggered()"),self.modifyHydrogenate)
        self.connect(self.modifyInvertAction,SIGNAL("triggered()"),self.modifyInvert)
        self.connect(self.modifyMergeAction,SIGNAL("triggered()"),self.modifyMerge)
        self.connect(self.makeChunkFromSelectedAtomsAction,
                     SIGNAL("triggered()"),self.makeChunkFromAtom)


        self.connect(self.modifyAdjustAllAction,SIGNAL("triggered()"),self.modifyAdjustAll)
        self.connect(self.modifyAdjustSelAction,SIGNAL("triggered()"),self.modifyAdjustSel)
        self.connect(self.modifyPassivateAction,SIGNAL("triggered()"),self.modifyPassivate)
        self.connect(self.modifySeparateAction,SIGNAL("triggered()"),self.modifySeparate)
        self.connect(self.modifyStretchAction,SIGNAL("triggered()"),self.modifyStretch)
        #self.connect(self.movieDoneAction,SIGNAL("triggered()"),self.movieDone)
        self.connect(self.movieInfoAction,SIGNAL("triggered()"),self.movieInfo)
        self.connect(self.movieMoveToEndAction,SIGNAL("triggered()"),self.movieMoveToEnd)
        self.connect(self.moviePauseAction,SIGNAL("triggered()"),self.moviePause)
        self.connect(self.moviePlayAction,SIGNAL("triggered()"),self.moviePlay)
        self.connect(self.moviePlayRevAction,SIGNAL("triggered()"),self.moviePlayRev)
        self.connect(self.movieResetAction,SIGNAL("triggered()"),self.movieReset)
        #self.connect(self.panDoneAction,SIGNAL("triggered()"),self.panDone)
        self.connect(self.panToolAction,SIGNAL("toggled(bool)"),self.panTool)
        self.connect(self.rotateToolAction,SIGNAL("toggled(bool)"),self.rotateTool)
        self.connect(self.saveNamedViewAction,SIGNAL("triggered()"),self.saveNamedView)
        self.connect(self.selectAllAction,SIGNAL("triggered()"),self.selectAll)
        self.connect(self.selectConnectedAction,SIGNAL("triggered()"),self.selectConnected)
        self.connect(self.selectContractAction,SIGNAL("triggered()"),self.selectContract)
        self.connect(self.selectDoublyAction,SIGNAL("triggered()"),self.selectDoubly)
        self.connect(self.selectExpandAction,SIGNAL("triggered()"),self.selectExpand)
        self.connect(self.selectInvertAction,SIGNAL("triggered()"),self.selectInvert)
        self.connect(self.selectNoneAction,SIGNAL("triggered()"),self.selectNone)
        self.connect(self.serverManagerAction,SIGNAL("triggered()"),self.serverManager)

        self.connect(self.viewOrientationAction,SIGNAL("triggered()"),self.showOrientationWindow) #ninad061114



        ##When Standard Views button is clicked, show its QMenu.-- By default, nothing happens if you click on the 
        ##toolbutton with submenus. The menus are displayed only when you click on the small downward arrow 
        ## of the tool button. Therefore the following slot is added. Also QWidgetAction is used 
        ## for it to add this feature (see Ui_ViewToolBar for details) ninad 070109 
        self.connect(self.standardViews_btn,SIGNAL("pressed()"),self.showStandardViewsMenu)

        self.connect(self.viewBackAction,SIGNAL("triggered()"),self.viewBack)
        self.connect(self.viewBottomAction,SIGNAL("triggered()"),self.viewBottom)
        self.connect(self.setViewFitToWindowAction,SIGNAL("triggered()"),self.setViewFitToWindow)
        self.connect(self.viewFrontAction,SIGNAL("triggered()"),self.viewFront)
        self.connect(self.setViewHomeAction,SIGNAL("triggered()"),self.setViewHome)
        self.connect(self.setViewHomeToCurrentAction,SIGNAL("triggered()"),self.setViewHomeToCurrent)
        self.connect(self.viewLeftAction,SIGNAL("triggered()"),self.viewLeft)
        self.connect(self.viewRotateMinus90Action,SIGNAL("triggered()"),self.viewRotateMinus90)
        self.connect(self.viewNormalToAction,SIGNAL("triggered()"),self.viewNormalTo)
        self.connect(self.viewRotate180Action,SIGNAL("triggered()"),self.viewRotate180)
        self.connect(self.setViewOrthoAction,SIGNAL("triggered()"),self.setViewOrtho)
        self.connect(self.viewParallelToAction,SIGNAL("triggered()"),self.viewParallelTo)
        self.connect(self.setViewPerspecAction,SIGNAL("triggered()"),self.setViewPerspec)
        self.connect(self.viewRotatePlus90Action,SIGNAL("triggered()"),self.viewRotatePlus90)
        self.connect(self.setViewRecenterAction,SIGNAL("triggered()"),self.setViewRecenter)
        self.connect(self.viewRightAction,SIGNAL("triggered()"),self.viewRight)
        self.connect(self.viewTopAction,SIGNAL("triggered()"),self.viewTop)
        self.connect(self.simJobManagerAction,SIGNAL("triggered()"),self.JobManager)
        self.connect(self.simMoviePlayerAction,SIGNAL("triggered()"),self.simMoviePlayer)
        self.connect(self.simNanoHiveAction,SIGNAL("triggered()"),self.simNanoHive)
        self.connect(self.simPlotToolAction,SIGNAL("triggered()"),self.simPlot)
        self.connect(self.simSetupAction,SIGNAL("triggered()"),self.simSetup)
        #self.connect(self.toggleDatumDispTbarAction,SIGNAL("triggered()"),self.toggleDatumDispTbar)
        #self.connect(self.toggleEditTbarAction,SIGNAL("triggered()"),self.toggleEditTbar)
        #self.connect(self.toggleFileTbarAction,SIGNAL("triggered()"),self.toggleFileTbar)
        #self.connect(self.toggleModelDispTbarAction,SIGNAL("triggered()"),self.toggleModelDispTbar)
        #self.connect(self.toggleModifyTbarAction,SIGNAL("triggered()"),self.toggleModifyTbar)
        #self.connect(self.toggleSelectTbarAction,SIGNAL("triggered()"),self.toggleSelectTbar)
        #self.connect(self.toggleToolsTbarAction,SIGNAL("triggered()"),self.toggleToolsTbar)
        #self.connect(self.toggleViewTbarAction,SIGNAL("triggered()"),self.toggleViewTbar)
        self.connect(self.toolsBackUpAction,SIGNAL("triggered()"),self.toolsBackUp)
        self.connect(self.toolsCancelAction,SIGNAL("triggered()"),self.toolsCancel)
        self.connect(self.toolsCookieCutAction,SIGNAL("triggered()"),self.toolsCookieCut)

        self.connect(self.toolsDepositAtomAction,
                     SIGNAL("triggered()"),
                     self.toolsBuildAtoms)

        self.connect(self.toolsDoneAction,SIGNAL("triggered()"),self.toolsDone)
        self.connect(self.toolsExtrudeAction,SIGNAL("triggered()"),self.toolsExtrude)
        ###self.connect(self.toolsFuseAtomsAction,SIGNAL("triggered()"),self.toolsFuseAtoms)
        self.connect(self.toolsFuseChunksAction,SIGNAL("triggered()"),self.toolsFuseChunks)
        ###self.connect(self.toolsMirrorAction,SIGNAL("triggered()"),self.toolsMirror)
        ###self.connect(self.toolsMirrorCircularBoundaryAction,SIGNAL("triggered()"),self.toolsMirrorCircularBoundary)
        #Move and Rotate Components mode
        self.connect(self.toolsMoveMoleculeAction,SIGNAL("triggered()"),self.toolsMoveMolecule)
        self.connect(self.rotateComponentsAction,SIGNAL("triggered()"),self.toolsRotateComponents)

        self.connect(self.toolsSelectAtomsAction,SIGNAL("triggered()"),self.toolsSelectAtoms)
        self.connect(self.toolsSelectMoleculesAction,SIGNAL("triggered()"),self.toolsSelectMolecules)
        self.connect(self.toolsStartOverAction,SIGNAL("triggered()"),self.toolsStartOver)
        self.connect(self.zoomToolAction,SIGNAL("toggled(bool)"),self.zoomTool)
        self.connect(self.viewZoomAboutScreenCenterAction,SIGNAL("toggled(bool)"),
                     self.changeZoomBehavior)
        self.connect(self.viewQuteMolAction,SIGNAL("triggered()"),self.viewQuteMol)
        self.connect(self.viewRaytraceSceneAction,SIGNAL("triggered()"),self.viewRaytraceScene)
        self.connect(self.insertPovraySceneAction,SIGNAL("triggered()"),self.insertPovrayScene)
        self.connect(self.dispSurfaceAction,SIGNAL("triggered()"),self.dispSurface)
        self.connect(self.dispCylinderAction,SIGNAL("triggered()"),self.dispCylinder)
        self.connect(self.simMinimizeEnergyAction,SIGNAL("triggered()"),self.simMinimizeEnergy)
        self.connect(self.fileImportAction,SIGNAL("triggered()"),self.fileImport)
        self.connect(self.fileExportAction,SIGNAL("triggered()"),self.fileExport)
        self.connect(self.viewIsometricAction,SIGNAL("triggered()"),self.viewIsometric)
        self.connect(self.modifyMirrorAction,SIGNAL("triggered()"),self.modifyMirror)
        self.connect(self.setViewZoomtoSelectionAction,SIGNAL("triggered()"),self.setViewZoomToSelection)

        # Atom Generator example for developers. Mark and Jeff. 2007-06-13
        #@ Jeff - add a link to the public wiki page when ready. Mark 2007-06-13.
        self.connect(self.insertAtomAction,SIGNAL("triggered()"),self.insertAtom)


        from prefs_constants import toolbar_state_prefs_key
        #This fixes bug 2482 
        if not env.prefs[toolbar_state_prefs_key] == 'defaultToolbarState':
            toolBarState = QtCore.QByteArray(env.prefs[toolbar_state_prefs_key])
            self.restoreState(toolBarState)
        else:
            #hide these toolbars by default 
            self.buildStructuresToolBar.hide()
            self.buildToolsToolBar.hide()
            self.selectToolBar.hide()
            self.simulationToolBar.hide()

        #Add Toolbar menu item to the View Menu. 
        #Adding menuitems to View menu is done in Ui_ViewMenu but adding the 
        #toolbar menu is done here as it uses 'createPopupMenu' to retrieve 
        #toolbar information. Note: Toolbars are declared after declaring menus as
        #some of them use menu items (action list) . 
        toolbarMenu = self.createPopupMenu()
        toolbarMenu.setTitle('Toolbars')
        self.viewMenu.addMenu(toolbarMenu)

        # mark 060105 commented out self.make_buttons_not_in_UI_file()
        #self.make_buttons_not_in_UI_file()

        undo_internals.just_after_mainwindow_super_init()

        # bruce 050104 moved this here so it can be used earlier
        # (it might need to be moved into main.py at some point)
        self.tmpFilePath = find_or_make_Nanorex_directory()


        # Load additional icons to QAction iconsets.
        # self.load_icons_to_iconsets() # Uncomment this line to test if Redo button has custom icon when disabled. mark 060427

        # Load all the custom cursors
        from cursors import loadCursors
        loadCursors(self)

        # Create our 2 status bar widgets - msgbarLabel and modebarLabel
        # (see also env.history.message())
        self.setStatusBar(StatusBar(self))

        env.setMainWindow(self)

        if name == None:
            self.setWindowTitle("NanoEngineer-1") # Mark 11-05-2004

        # start with empty window 
        self.assy = assembly(self, "Untitled", own_window_UI = True) # own_window_UI is required for this assy to support Undo
            #bruce 060127 added own_window_UI flag to help fix bug 1403
        #bruce 050429: as part of fixing bug 413, it's now required to call
        # self.assy.reset_changed() sometime in this method; it's called below.

        # Set the caption to the name of the current (default) part - Mark [2004-10-11]
        self.update_mainwindow_caption()	    

        # hsplitter and vsplitter reimplemented. mark 060222.
        # Create the horizontal-splitter between the model tree (left) and the glpane 
        # and history widget (right)
        hsplitter = QSplitter(Qt.Horizontal, self)

        from debug_prefs import this_session_permit_property_pane
        mtree_in_a_vsplitter = this_session_permit_property_pane() or False
            #bruce 060402 experiment; works (except for initial width), but DO NOT COMMIT WITH True
        # only bug known so far is mtree (vsplitter2) width
        if mtree_in_a_vsplitter:
            vsplitter2 = QSplitter(Qt.Vertical, hsplitter)
            self.vsplitter2 = vsplitter2 # use this for property pane parent? doesn't work, don't know why. [060623]
            ## vsplitter2.setBaseSize(QSize(225,150)) #k experiment, guess, height is wrong; has no effect
            mtree_parent = vsplitter2

        else:
            mtree_parent = hsplitter

        if not MULTIPANE_GUI:
            # Create the model tree widget. Width of 225 matches width of MMKit.  Mark 060222.
            self.mt = modelTree(mtree_parent, self)
            self.mt.setMinimumSize(0, 0)
            #self.mt.setColumnWidth(0,225)

            if mtree_in_a_vsplitter:
                mtree_view_in_hsplitter = vsplitter2
            else:
                mtree_view_in_hsplitter = self.mt.modelTreeGui  # @@ninad 061205 replaced self.mt with self.mt.modelTreeGui 
                #to get   hsplitter.setStretchFactor working (without errors)

        # Create the vertical-splitter between the glpane (top) and the
        # history widget (bottom) [history is new as of 041223]
        vsplitter = QSplitter(Qt.Vertical, hsplitter)

        if not MULTIPANE_GUI:
            if 0: 
                #& This creates a gplane with a black 1 pixel border around it.  Leave it in in case we want to use this.
                #& mark 060222. [bruce 060612 committed with 'if 0', in an updated/tested form]
                glframe = QFrame(vsplitter)
                glframe.setFrameShape ( QFrame.Box ) 
                flayout = QVBoxLayout(glframe,1,1,'flayout')
                self.glpane = GLPane(self.assy, glframe, "glpane", self)
                flayout.addWidget(self.glpane,1)
            else:
                # Create the glpane - where all the action is!
                self.glpane = GLPane(self.assy, vsplitter, "glpane", self)
                    #bruce 050911 revised GLPane.__init__ -- now it leaves glpane's mode as nullmode;
                    # we change it below, since doing so now would be too early for some modes permitted as startup mode
                    # (e.g. Build mode, which when Entered needs self.Element to exist, as of 050911)

        if not MULTIPANE_GUI:
            # Create the history area at the bottom
            from HistoryWidget import HistoryWidget
            histfile = make_history_filename()
            #bruce 050913 renamed self.history to self.history_object, and deprecated direct access
            # to self.history; code should use env.history to emit messages, self.history_widget
            # to see the history widget, or self.history_object to see its owning object per se
            # rather than as a place to emit messages (this is rarely needed).
            self.history_object = HistoryWidget(vsplitter, filename = histfile, mkdirs = 1)
                # this is not a Qt widget, but its owner;
                # use self.history_widget for Qt calls that need the widget itself.
            self.history_widget = self.history_object.widget

                #bruce 050913, in case future code splits history widget (as main window subwidget)
                # from history message recipient (the global object env.history).

            env.history = self.history_object #bruce 050727, revised 050913

        # Some final hsplitter setup...
        hsplitter.setHandleWidth(3) # Default is 5 pixels (too wide).  mark 060222.
        qt4todo('hsplitter.setResizeMode(mtree_view_in_hsplitter, QSplitter.KeepSize)')
        qt4todo('hsplitter.setStretchFactor(hsplitter.indexOf(mtree_view_in_hsplitter), 0)')
        #hsplitter.setStretchFactor(0, 0)
        hsplitter.setOpaqueResize(False)	


        # ... and some final vsplitter setup [bruce 041223]
        vsplitter.setHandleWidth(3) # Default is 5 pixels (too wide).  mark 060222.
        qt4todo('vsplitter.setResizeMode(self.history_widget, QSplitter.KeepSize)')
        qt4todo('vsplitter.setStretchFactor(vsplitter.indexOf(self.history_widget), 0)')
        vsplitter.setOpaqueResize(False)

        if not MULTIPANE_GUI:
            self.setCentralWidget(hsplitter) # This is required.
            # This makes the hsplitter the central widget, spanning the height of the mainwindow.
            # mark 060222.


        if mtree_in_a_vsplitter:
            hsplitter.setSizes([225,]) #e this works, but 225 is evidently not always the MMKit width (e.g. on bruce's iMac g4)
            vsplitter2.setHandleWidth(3)
            vsplitter2.setOpaqueResize(False)
            # client code adding things to vsplitter2 may want to call something like:
            ## vsplitter2.setResizeMode(newthing-in-vsplitter2, QSplitter.KeepSize)


        if MULTIPANE_GUI:
            # Create the "What's This?" online help system.
            createWhatsThisTextForMainWindowWidgets(self)

            # This is only used by the Atom Color preference dialog, not the
            # molecular modeling kit in Build Atom (deposit mode), etc.
            start_element = 6 # Carbon
            self.Element = start_element

            # Attr/list for Atom Selection Filter. mark 060401
            self.filtered_elements = [] # Holds list of elements to be selected when the Atom Selection Filter is enabled.
            self.filtered_elements.append(PeriodicTable.getElement(start_element)) # Carbon
            self.selection_filter_enabled = False # Set to True to enable the Atom Selection Filter.

            self.currentWorkingDirectory = ''
            self.setWindowTitle("My Main Window")
            MAIN_WINDOW_SIZE = (800, 600)
            self.setMinimumWidth(MAIN_WINDOW_SIZE[0])
            self.setMinimumHeight(MAIN_WINDOW_SIZE[1])

            ##############################################

            centralwidget = QWidget()
            self.setCentralWidget(centralwidget)
            layout = QVBoxLayout(centralwidget)
            layout.setMargin(0)
            layout.setSpacing(0)
            middlewidget = QWidget()


            from CommandManager import CommandManager

            self.commandManager = CommandManager(self)
            self.cmdManager = self.commandManager.cmdManager  
            layout.addWidget(self.cmdManager)	    


            layout.addWidget(middlewidget)
            self.layout = QGridLayout(middlewidget)
            self.layout.setMargin(0)
            self.layout.setSpacing(0)
            self.gridPosition = GridPosition()
            self.numParts = 0

            self.addPartWindow(self.assy)
        else:
            self._init_part_two()

        env.register_post_event_ui_updater( self.post_event_ui_updater) #bruce 070925

        return # from MWsemantics.__init__

    def _get_commandSequencer(self):
        # WARNING: if this causes infinite recursion, we just get an AttributeError
        # from the inner call (saying self has no attr 'commandSequencer')
        # rather than an understandable exception.
        return self.glpane #bruce 071008; will revise when we have a separate one

    commandSequencer = property(_get_commandSequencer)

    def _get_currentCommand(self):
        return self.commandSequencer.currentCommand

    currentCommand = property(_get_currentCommand)

    def post_event_ui_updater(self): #bruce 070925
        self.currentCommand.state_may_have_changed()
        return

    def createPopupMenu(self): #Ninad 070328
        """
	Reimplemented createPopPupMenu method that allows 
	display of custom context menu (toolbars and dockwidgets) 
	when you rightclick on QMainWindow widget.
	"""
        menu = QMenu(self)
        contextMenuToolBars = \
                        [self.standardToolBar, self.viewToolBar,
                         self.standardViewsToolBar, self.displayStylesToolBar,
                         self.simulationToolBar, self.buildToolsToolBar,
                         self.selectToolBar, self.buildStructuresToolBar]
        for toolbar in contextMenuToolBars:
            menu.addAction(toolbar.toggleViewAction())
        return menu

    def removePartWindow(self, pw):
        self.layout.removeWidget(pw)
        self.gridPosition.removeWidget(pw)
        self.numParts -= 1
        if self.numParts == 0:
            self.cmdManagerControlArea.hide()
        # [bruce 070503 question: why do we not worry about whether pw == self._activepw?]
    
    def showFullScreen(self):
        """
        Full screen mode. (maximize the glpane real estate by hiding/ collapsing
        other widgets. (only Menu bar and the glpane are shown)
        The widgets hidden or collapsed include: 
         - MainWindow Title bar
         - Command Manager, 
         - All toolbars, 
         - ModelTree/PM area,
         - History Widget,
         - Statusbar         
        
        @param val: The state of the QAction (checked or uncheced) If True, it 
                    will show the main window full screen , otherwise show it 
                    with its regular size
        @type val: boolean
        @see: self.showSemiFullScreen, self.showNormal
        @see: ops_view.viewSlotsMixin.setViewFullScreen
        """
        
        if self._block_viewFullScreenAction_event:
            #see self.__init__ for a detailed comment about this instance 
            #variable
            return
        
        self._block_viewFullScreenAction_event = False
        
        if self.viewSemiFullScreenAction.isChecked():
            self._block_viewSemiFullScreenAction_event = True
            self.viewSemiFullScreenAction.setChecked(False)
            self._block_viewSemiFullScreenAction_event = False            
            
        self._showFullScreenCommonCode()
        for  widget in self.children():
            if isinstance(widget, QToolBar):
                if widget.isVisible():
                    widget.hide()
                    self._widgetToHideDuringFullScreenMode.append(widget)
        
        self.commandManager.cmdManager.hide()
        
    def _showFullScreenCommonCode(self):
        """
        The common code for making the Mainwindow full screen (maximimzing the
        3D workspace area) This is used by both, View > Full Screen and 
        View > Semi-Full Screen
        @see: self.showFullScreen 
        @see: self._showSemiFullScreen
        """
        #see self.__init__ for a detailed comment about this list
        self._widgetToHideDuringFullScreenMode = []
        QMainWindow.showFullScreen(self)
        for  widget in self.children():
            if isinstance(widget, QStatusBar):
                if widget.isVisible():
                    widget.hide()
                    self._widgetToHideDuringFullScreenMode.append(widget)      
        
        self.activePartWindow().collapseModelTreeArea()        
        self.activePartWindow().collapseHistoryWidget()

    def showSemiFullScreen(self):
        """
        Semi-Full Screen mode. (maximize the glpane real estate by hiding/ collapsing
        other widgets. This is different than the 'Full Screen mode' as it hides
        or collapses only the following widgets -- 
         - MainWindow Title bar
         - ModelTree/PM area,
         - History Widget,
         - Statusbar         
        
        @param val: The state of the QAction (checked or uncheced) If True, it 
                    will show the main window full screen , otherwise show it 
                    with its regular size
        @type val: boolean
        @see: self.showFullScreen, self.showNormal
        @see: ops_view.viewSlotsMixin.setViewSemiFullScreen
        """
        if self._block_viewSemiFullScreenAction_event:
            #see self.__init__ for a detailed comment about this instance 
            #variable
            return
        
        self._block_viewSemiFullScreenAction_event = False
        
        if self.viewFullScreenAction.isChecked():
            self._block_viewFullScreenAction_event = True
            self.viewFullScreenAction.setChecked(False)
            self._block_viewFullScreenAction_event = False
        
        self._showFullScreenCommonCode()
        
            
    
    def showNormal(self):
        QMainWindow.showNormal(self)
        self.activePartWindow().expandModelTreeArea()
        self.activePartWindow().expandHistoryWidget()
        
        for  widget in self._widgetToHideDuringFullScreenMode:           
            widget.show()
        
        self.commandManager.cmdManager.show()
        #Clear the list of hidden widgets (those are no more hidden)
        self._widgetToHideDuringFullScreenMode = [] 
               
    def addPartWindow(self, assy):
        # This should be associated with fileOpen (ops_files.py) or with creating a new structure
        # from scratch.
        # [bruce 070503 question: why do we get passed an assy, and use it for some things and self.assy for others?]
        if self.numParts == 0:
            #self.cmdManagerControlArea.show()
            self.cmdManager.show()
        self.numParts += 1
        pw = PartWindow(assy, self)
        row, col = self.gridPosition.next(pw)
        self.layout.addWidget(pw, row, col)
        self.assy.o = pw.glpane
        self.assy.mt = pw.modelTree #bruce 070509 revised this, was pw.modelTree.modelTreeGui
        self._activepw = pw
            # Note: nothing in this class can set self._activepw (except to None),
            # which one might guess means that no code yet switches between partwindows,
            # but GLPane.makeCurrent *does* set self._activepw to its .partWindow
            # (initialized to its parent arg when it's created), so that conclusion is not clear.
            # [bruce 070503 comment]
        if not self._init_part_two_done:
            # I bet there are pieces of _init_part_two that should be done EVERY time we bring up a
            # new partwindow.
            # [I guess that comment is by Will... for now, this code doesn't do those things
            #  more than once, it appears. [bruce 070503 comment]]
            MWsemantics._init_part_two(self)

        ## pw.glpane.start_using_mode('$STARTUP_MODE')
            ### TODO: this should be the commandSequencer --
            # decide whether to just get it from win (self) here
            # (e.g. if we abandon separate PartWindow class)
            # or make pw.commandSequencer work.
            # For now just get it from self. [bruce 071012]
        self.commandSequencer.start_using_mode('$STARTUP_MODE')
        return

    def _init_part_two(self):
        # Create the Preferences dialog widget.
        # Mark 050628
        if not MULTIPANE_GUI:
            self.assy.o = self.glpane
        from UserPrefs import UserPrefs
        self.userPrefs = UserPrefs(self.assy)

        # Enable/disable plugins.  These should be moved to a central method
        # where all plug-ins get added and enabled during invocation.  Mark 050921.
        self.userPrefs.enable_nanohive(env.prefs[nanohive_enabled_prefs_key])
        self.userPrefs.enable_gamess(env.prefs[gamess_enabled_prefs_key])
        self.userPrefs.enable_gromacs(env.prefs[gromacs_enabled_prefs_key])
        self.userPrefs.enable_cpp(env.prefs[cpp_enabled_prefs_key])

        #Zoom behavior setting  (View > Zoom About Screen Center)
        self.viewZoomAboutScreenCenterAction.setChecked(
            env.prefs[zoomAboutScreenCenter_prefs_key])

        #Huaicai 9/14/05: Initialization for the 'Recently opened files' feature
        from PyQt4.Qt import QSettings, QWhatsThis
        menuItem = self.RECENT_FILES_MENU_ITEM
        if recentfiles_use_QSettings:
            prefsSetting = QSettings("Nanorex", "NanoEngineer-1")
        else:
            prefsSetting = preferences.prefs_context()

        if recentfiles_use_QSettings:
            # Qt3: fileList = prefsSetting.readListEntry('/Nanorex/nE-1/recentFiles')[0]
            fileList = prefsSetting.value('/Nanorex/nE-1/recentFiles').toStringList()
        else:
            fileList = prefsSetting.get('/Nanorex/nE-1/recentFiles', [])
        if len(fileList):  
            qt4warning('self.fileMenu.setItemEnabled(menuItem, True)')
            if menuItem is not None: menuItem.setEnabled(True)
            self._createRecentFilesList()
        else:
            qt4warning('self.fileMenu.setItemEnabled(menuItem, False)')
            if menuItem is not None: menuItem.setEnabled(False)

        # Create the Help dialog. Mark 050812
        from help import Ne1HelpDialog
        self.help = Ne1HelpDialog()
        
        # Create the NE1 Progress Dialog. mark 2007-12-06
        self.createProgressDialog()

        from GrapheneGenerator import GrapheneGenerator
        self.graphenecntl = GrapheneGenerator(self)
        from NanotubeGenerator import NanotubeGenerator
        self.nanotubecntl = NanotubeGenerator(self)

        # Use old DNA generator or new DNA Duplex generator?
        if debug_pref("Use old 'Build > DNA' generator? (next session)", 
                      Choice_boolean_False, 
                      non_debug = True,
                      prefs_key = "A9 devel/DNA Duplex"):

            print "Using original DNA generator (supports PAM-5)."
            from DnaGenerator import DnaGenerator
            self.dnacntl = DnaGenerator(self)
        else:
            # This might soon become the usual case, with the debug_pref 
            # removed. - Mark

            print "Using new DNA Duplex command (supports PAM-3 only)."
            from DnaDuplexEditController import DnaDuplexEditController
            self.dnaEditController = DnaDuplexEditController(self)	
            self.dnacntl = self.dnaEditController

        from PovraySceneProp import PovraySceneProp
        self.povrayscenecntl = PovraySceneProp(self)
        from CommentProp import CommentProp
        self.commentcntl = CommentProp(self)
        # Minimize Energy dialog. Mark 060705.
        from MinimizeEnergyProp import MinimizeEnergyProp
        self.minimize_energy = MinimizeEnergyProp(self)

        # Atom Generator example for developers. Mark and Jeff. 2007-06-13
        #@ Jeff - add a link to the public wiki page when ready. Mark 2007-06-13.
        from AtomGenerator import AtomGenerator
        self.atomcntl = AtomGenerator(self)
        
        # QuteMol Property Manager. Mark 2007-12-02.
        from QuteMolPropertyManager import QuteMolPropertyManager
        self.qutemolPM = QuteMolPropertyManager(self)

        if not MULTIPANE_GUI:
            # do here to avoid a circular dependency
            # note: as of long before now, this doesn't normally run [bruce 070503 comment]
            self.assy.o = self.glpane
            self.assy.mt = self.mt

        # We must enable keyboard focus for a widget if it processes
        # keyboard events. [Note added by bruce 041223: I don't know if this is
        # needed for this window; it's needed for some subwidgets, incl. glpane,
        # and done in their own code. This window forwards its own key events to
        # the glpane. This doesn't prevent other subwidgets from having focus.]
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Hide the "Make Checkpoint" toolbar button/menu item. mark 060302.
        self.editMakeCheckpointAction.setVisible(False)

        # Create the "What's This?" online help system.
        if not MULTIPANE_GUI:
            createWhatsThisTextForMainWindowWidgets(self)

        # IMPORTANT: All widget creation (i.e. dashboards, dialogs, etc.) and their 
        # whatthis text should be created before this line. [If this is not possible,
        # we'll need to split out some functions within this one which can be called
        # later on individual QActions and/or QWidgets. bruce 060319]
        fix_whatsthis_text_and_links(self, refix_later = (self.editMenu,)) 
            # (main call) Fixes bug 1136.  Mark 051126.
            # [bruce 060319 added refix_later as part of fixing bug 1421]
        fix_whatsthis_text_and_links(self.toolsMoveRotateActionGroup)
            # This is needed to add links to the "Translate" and "Rotate"
            # QAction widgets on the standard toolbar, since those two
            # widgets are not direct children of the main window. 
            # Fixes one of the many bugs listed in bug 2412. Mark 2007-12-19

        if not MULTIPANE_GUI:

            # This is only used by the Atom Color preference dialog, not the
            # molecular modeling kit in Build Atom (deposit mode), etc.
            start_element = 6 # Carbon
            self.Element = start_element

            # Attr/list for Atom Selection Filter. mark 060401
            self.filtered_elements = [] # Holds list of elements to be selected when the Atom Selection Filter is enabled.
            self.filtered_elements.append(PeriodicTable.getElement(start_element)) # Carbon
            self.selection_filter_enabled = False # Set to True to enable the Atom Selection Filter.

        # 'depositState' is used by depositMode and MMKit to synchonize the 
        # depositMode dashboard (Deposit and Paste toggle buttons) and the MMKit pages (tabs).
        # It is also used to determine what type of object (atom, clipboard chunk or library part)
        # to deposit when pressing the left mouse button in Build mode.
        #
        # depositState can be either:
        #   'Atoms' - deposit an atom based on the current atom type selected in the MMKit 'Atoms'
        #           page or dashboard atom type combobox(es).
        #   'Clipboard' - deposit a chunk from the clipboard based on what is currently selected in
        #           the MMKit 'Clipboard' page or dashboard clipboard/paste combobox.
        #   'Library' - deposit a part from the library based on what is currently selected in the
        #           MMKit 'Library' page.  There is no dashboard option for this.
        self.depositState = 'Atoms'

        self.assy.reset_changed() #bruce 050429, part of fixing bug 413

        # Movie Player Flag.  Mark 051209.
        # 'movie_is_playing' is a flag that indicates a movie is playing. It is used by other code to
        # speed up rendering times by disabling the (re)building of display lists for each frame
        # of the movie.
        self.movie_is_playing = False

        # Current Working Directory (CWD).
        # When NE1 starts, the CWD is set to the Working Directory (WD) pref from the prefs db. 
        # Every time the user opens or inserts a file during a session, the CWD changes to the directory containing
        # that file. When the user closes the current file and then attempts to open a new file, the CWD will still
        # be the directory of the last file opened or inserted. 
        # If the user changes the WD via 'File > Set Working Directory' when a file is open, 
        # the CWD will not be changed to the new WD. (This rule may change. Need to discuss with Ninad).
        # On the other hand, if there is no part open, the CWD will be changed to the new WD.  Mark 060729.
        self.currentWorkingDirectory = ''

        # Before setting the CWD, make sure the WD from the prefs db exists (it might have been deleted). 
        # If not, set the CWD to the default WD.
        if os.path.isdir(env.prefs[workingDirectory_prefs_key]): 
            self.currentWorkingDirectory = env.prefs[workingDirectory_prefs_key]
        else:
            self.currentWorkingDirectory = getDefaultWorkingDirectory()

        #bruce 050810 replaced user preference initialization with this, and revised update_mainwindow_caption to match
        from changes import Formula
        self._caption_formula = Formula(
            # this should depend on whatever update_mainwindow_caption_properly depends on;
            # but it can't yet depend on assy.has_changed(),
            # so that calls update_mainwindow_caption_properly (or the equiv) directly.
            lambda: (env.prefs[captionPrefix_prefs_key],
                     env.prefs[captionSuffix_prefs_key],
                     env.prefs[captionFullPath_prefs_key]),
            self.update_mainwindow_caption_properly
        )

        self.initialised = 1 # enables win_update [should this be moved into _init_after_geometry_is_set?? bruce 060104 question]

        # be told to add new Jigs menu items, now or as they become available [bruce 050504]
        register_postinit_object( "Jigs menu items", self )

        # Anything which depends on this window's geometry (which is not yet set at this point)
        # should be done in the _init_after_geometry_is_set method below, not here. [bruce guess 060104]

        self._init_part_two_done = True
        return # from _init_part_two

    def activePartWindow(self): # WARNING: this is inlined in a few methods of self
        return self._activepw

    def get_glpane(self): #bruce 071008; inlines self.activePartWindow
        return self._activepw.glpane

    def get_mt(self): #bruce 071008; inlines self.activePartWindow # TODO: rename .mt to .modelTree
        return self._activepw.modelTree

    if MULTIPANE_GUI:
        #bruce 071008 to replace __getattr__
        glpane = property(get_glpane)
        mt = property(get_mt)

    def closeEvent(self, ce):
        fileSlotsMixin.closeEvent(self, ce)

    def sponsoredList(self):
        return (self.graphenecntl,
                self.nanotubecntl,
                self.dnacntl,
                self.povrayscenecntl,
                self.minimize_energy)

    def _init_after_geometry_is_set(self): #bruce 060104 renamed this from startRun and replaced its docstring.
        """
        Do whatever initialization of self needs to wait until its geometry has been set.
        [Should be called only once, after geometry is set; can be called before self is shown.
         As of 070531, this is called directly from main.py, after our __init__ but before we're first shown.]
        """
        # older docstring:
        # After the main window(its size and location) has been setup, begin to run the program from this method. 
        # [Huaicai 11/1/05: try to fix the initial MMKitWin off screen problem by splitting from the __init__() method]

        if not MULTIPANE_GUI:
            self.commandSequencer.start_using_mode( '$STARTUP_MODE')
            # Note: this might depend on self's geometry in choosing dialog placement, so it shouldn't be done in __init__.

        self.win_update() # bruce 041222
        undo_internals.just_before_mainwindow_init_returns() # (this is now misnamed, now that it's not part of __init__)
        return

    __did_cleanUpBeforeExiting = False #bruce 070618

    def cleanUpBeforeExiting(self): #bruce 060127 added this re bug 1412 (Python crashes on exit, newly common)
        """
        NE1 is going to exit. (The user has already been given the chance to save current files
        if they are modified, and (whether or not they were saved) has approved the exit.)
           Perform whatever internal side effects are desirable to make the exit safe and efficient,
        and/or to implement features which save other info (e.g. preferences) upon exiting.
           This should be safe to call more than once, even though doing so is a bug.
        """

        # We do most things in their own try/except clauses, so if they fail,
        # we'll still do the other actions [bruce 070618 change].
        # But we always print something if they fail.

        if self.__did_cleanUpBeforeExiting:
            # This makes sure it's safe to call this method more than once.
            # (By itself, this fixes the exception in bug 2444 but not the double dialogs from it.
            #  The real fix for bug 2444 is elsewhere, and means this is no longer called more than once,
            #  but I'll leave this in for robustness.) [bruce 070618]
            return

        self.__did_cleanUpBeforeExiting = True

        msg = "exception (ignored) in cleanUpBeforeExiting: "

        try:
            # wware 060406 bug 1263 - signal the simulator that we are exiting
            # (bruce 070618 moved this here from 3 places in prepareToCloseAndExit.)
            from runSim import SimRunner
            SimRunner.PREPARE_TO_CLOSE = True
        except:
            print_compact_traceback( msg )

        try:
            env.history.message(greenmsg("Exiting program."))
        except:
            print_compact_traceback( msg )

        try:
            if env.prefs[rememberWinPosSize_prefs_key]: # Fixes bug 1249-2. Mark 060518.
                self.userPrefs.save_current_win_pos_and_size()
        except:
            print_compact_traceback( msg )

        ## self.__clear() # (this seems to take too long, and is probably not needed)

        try:
            self.deleteOrientationWindow() # ninad 061121- perhaps it's unnecessary
        except:
            print_compact_traceback( msg )

        try:
            self.assy.deinit()
                # in particular, stop trying to update Undo/Redo actions all the time
                # (which might cause crashes once their associated widgets are deallocated)
        except:
            print_compact_traceback( msg )

        return

    def postinit_item(self, item): #bruce 050504
        try:
            item(self)
        except:
            # blame item
            print_compact_traceback( "exception (ignored) in postinit_item(%r): " % item )
        return

    def update_mode_status(self, mode_obj = None):
        """
        [by bruce 040927]

        Update the text shown in self.modebarLabel (if that widget
        exists yet).  Get the text to use from mode_obj if supplied,
        otherwise from the current mode object
        (self.currentCommand). (The mode object has to be supplied when
        the currently stored one is incorrect, during a mode
        transition.)

        This method needs to be called whenever the mode status text
        might need to change.  See a comment in the method to find out
        what code should call it.

        """
        # There are at least 3 general ways we could be sure to call
        # this method often enough; the initial implementation of
        # 040927 uses (approximately) way #1:
        # 
        # (1) Call it after any user-event-handler that might change
        # what the mode status text should be.  This is reasonable,
        # but has the danger that we might forget about some kind of
        # user-event that ought to change it. (As of 040927, we call
        # this method from this file (after tool button actions
        # related to selection), and from the mode code (after mode
        # changes).)
        # 
        # (2) Call it after any user-event at all (except for
        # mouse-move or mouse-drag).  This would probably be best (##e
        # so do it!), since it's simple, won't miss anything, and is
        # probably efficient enough.  (But if we ever support
        # text-editing, we might have to exclude keypress/keyrelease
        # from this, for efficiency.)
        # 
        # (3) Call it after any internal change which might affect the
        # mode-status text. This would have to include, at least, any
        # change to (the id of) self.glpane, self.currentCommand,
        # self.glpane.assy, or (the value of)
        # self.glpane.assy.selwhat, regardless of the initial cause of
        # that change. The problems with this method are: it's
        # complicated; we might miss a necessary update call; we'd
        # have to be careful for efficiency to avoid too many calls
        # after a single user event (e.g. one for which we iterate
        # over all atoms and "select parts" redundantly for each one);
        # or we'd have to make many calls permissible, by separating
        # this method into an "update-needed" notice (just setting a
        # flag), and a "do-update" function, which does the update
        # only when the flag is set. But if we did the latter, it
        # would be simpler and probably faster to just dispense with
        # the flag and always update, i.e. to use method (2).

        try:
            widget = self.statusBar().modebarLabel
        except AttributeError:
            print "Caught <AttributeError: self.statusBar().modebarLabel>, normal behavior, not a bug"
            pass # this is normal, before the widget exists
        else:
            mode_obj = mode_obj or self.currentCommand
            text = mode_obj.get_mode_status_text()
            #widget.setText( text )


    ##################################################
    # The beginnings of an invalidate/update mechanism
    # at the moment it just does update whether needed or not
    ##################################################

    def win_update(self): # bruce 050107 renamed this from 'update'
        """
        Update most state which directly affects the GUI display,
        in some cases repainting it directly.
        (Someday this should update all of it, but only what's needed,
        and perhaps also call QWidget.update. #e)
        [no longer named update, since that conflicts with QWidget.update]
        """
        if not self.initialised:
            return #bruce 041222
        if MULTIPANE_GUI:
            pw = self.activePartWindow()
            pw.glpane.gl_update()
            pw.modelTree.mt_update()
            pw.history_object.h_update()
        else:
            self.glpane.gl_update()
            self.mt.mt_update()	
            self.history_object.h_update() #bruce 050104
                # this is self.history_object, not env.history,
                # since it's really about this window's widget-owner,
                # not about the place to print history messages [bruce 050913]

    ###################################
    # File Toolbar Slots 
    ###################################

    # file toolbar slots are inherited from fileSlotsMixin (in ops_files.py) as of bruce 050907.
    # Notes:
    #   #e closeEvent method (moved to fileSlotsMixin) should be split in two
    # and the outer part moved back into this file.
    #   __clear method was moved to fileSlotsMixin (as it should be), even though
    # its name-mangled name thereby changed, and some comments in other code
    # still refer to it as MWsemantics.__clear. It should be given an ordinary name.


    ###################################
    # Edit Toolbar Slots
    ###################################

    def editMakeCheckpoint(self):
        """
        Slot for making a checkpoint (only available when Automatic 
        Checkpointing is disabled).
        """
        import undo_UI
        undo_UI.editMakeCheckpoint(self)
        return

    def editUndo(self):
        self.assy.editUndo()

    def editRedo(self):
        self.assy.editRedo()

    def editAutoCheckpointing(self, enabled):
        """
        Slot for enabling/disabling automatic checkpointing.
        """
        import undo_manager
        undo_manager.editAutoCheckpointing(self, enabled)
            # note: see code comment there, for why that's not in undo_UI.
            # note: that will probably do this (among other things):
            #   self.editMakeCheckpointAction.setVisible(not enabled)
        return

    def editClearUndoStack(self):
        """
        Slot for clearing the Undo Stack. Requires the user to confirm.
        """
        import undo_UI
        undo_UI.editClearUndoStack(self)
        return

    # bruce 050131 moved some history messages from the following methods
    # into the assy methods they call, so the menu command versions also
    # have them

    def editCut(self):
        self.assy.cut_sel()
        self.win_update()

    def editCopy(self):
        self.assy.copy_sel()
        self.win_update()

    def editPaste(self):
        """
	Single shot paste operation accessible using 'Ctrl + V' or Edit > Paste.
	Implementation notes for the single shot paste operation:
	  - The object (chunk or group) is pasted with a slight offset. 
	    Example:
            Create a graphene sheet, select it , do Ctrl + C and then Ctrl + V 
	    ... the pasted object is offset to original one. 
          - It deselects others, selects the pasted item and then does a zoom to
	    selection so that the selected item is in the center of the screen.
	  - Bugs/ Unsupported feature: If you paste multiple copies of an object
	    they are pasted at the same location. (i.e. the offset is constant)

	@see: L{ops_copy_Mixin.paste} 
	"""
        if self.assy.shelf.members:
            pastables = self.assy.shelf.getPastables()
            if not pastables:
                msg = orangemsg("Nothing to paste.")
                env.history.message(msg)
                return

            recentPastable = pastables[-1]
            self.assy.paste(recentPastable)
        else:
            msg = orangemsg("Nothing to paste.")
            env.history.message(msg)
        return

    def editPasteFromClipboard(self):
        """
        Invokes the L{PasteMode}, a temporary command to paste items in the 
        clipboard, into the 3D workspace. It also stores the command NE1 should 
        return to after exiting this temporary command. 
        """
        if self.assy.shelf.members:	    
            pastables = self.assy.shelf.getPastables()
            if not pastables:
                msg = orangemsg("Nothing to paste. Paste Command cancelled.")
                env.history.message(msg)
                return

            commandSequencer = self.commandSequencer
            currentCommand = commandSequencer.currentCommand

            if currentCommand.modename != "PASTE":
##		#Make sure that previous command (commandSequencer.prevMode) never
##		#stores a 'temporary command' i.e. after exiting Paste Command, the 
##		#command NE1 enters is not one of the following -- 
##		# ('PASTE', 'PARTLIB', 'ZOOM', 'PAN', 'ROTATE')
##		
##		if currentCommand.modename not in ['PASTE', 'PARTLIB',
##					           'ZOOM', 'PAN', 'ROTATE']:		    
##		    commandSequencer.prevMode = currentCommand
##		    
##		commandSequencer.userEnterCommand('PASTE', suspend_old_mode = False)
                commandSequencer.userEnterTemporaryCommand('PASTE') #bruce 071011 guess ### REVIEW
                return
        else:
            msg = orangemsg("Clipboard is empty. Paste Command cancelled.")
            env.history.message(msg)
        return

    def insertPartFromPartLib(self):
        """
        Sets the current command to L{PartLibraryMode}, for inserting (pasting) 
        a part from the partlib into the 3D workspace. It also stores the command 
        NE1 should return to after exiting this temporary command. 
        """
        commandSequencer = self.commandSequencer
        currentCommand = commandSequencer.currentCommand
        if currentCommand.modename != "PARTLIB":
##	    #Make sure that previous command (commandSequencer.prevMode) never
##	    #stores a 'temporary command' i.e. after exiting Paste Command, the 
##	    #command NE1 enters is not one of the following -- 
##	    # ('PASTE', 'PARTLIB', 'ZOOM', 'PAN', 'ROTATE')
##	    if currentCommand.modename not in ['PASTE', 'PARTLIB',
##					       'ZOOM', 'PAN', 'ROTATE']:
##		commandSequencer.prevMode = currentCommand
##		
##	    commandSequencer.userEnterCommand('PARTLIB', suspend_old_mode = False)
            commandSequencer.userEnterTemporaryCommand('PARTLIB') #bruce 071011 guess ### REVIEW
        return

    # TODO: rename killDo to editDelete
    def killDo(self):
        """
        Deletes selected atoms, chunks, jigs and groups.
        """
        self.assy.delete_sel()
        ##bruce 050427 moved win_update into delete_sel as part of fixing bug 566
        ##self.win_update()

    def editPrefs(self):
        """
        Edit Preferences
        """
        self.userPrefs.showDialog()

    ###################################
    # View Toolbar Slots 
    ###################################

    # view toolbar slots are inherited from viewSlotsMixin (in ops_view.py) as of mark 060120.

    ###################################
    # Display Toolbar Slots
    ###################################

    # set display formats in whatever is selected,
    # or the GLPane global default if nothing is
    def dispDefault(self):
        self.setDisplay(diDEFAULT, True)

    def dispInvis(self):
        self.setDisplay(diINVISIBLE)

    def dispCPK(self): #e this slot method (here and in .ui file) renamed from dispVdW to dispCPK [bruce 060607]
        self.setDisplay(diTrueCPK)

    def dispHybrid(self): #@@ Ninad 070308
        print "Hybrid display is  Implemented yet"
        pass

    def dispTubes(self):
        self.setDisplay(diTUBES)

    def dispBall(self): #e this slot method (here and in .ui file) renamed from dispCPK to dispBall [bruce 060607]
        self.setDisplay(diBALL)

    def dispLines(self):
        self.setDisplay(diLINES)

    def dispCylinder(self):
        cmd = greenmsg("Set Display Cylinder: ")
        if self.assy and self.assy.selatoms:
            # Fixes bug 2005. Mark 060702.
            env.history.message(cmd + "Selected atoms cannot have their display mode set to Cylinder.")
            return #ninad 061003  fixed bug 2286... Note: Once atoms and chunks are allowed to be sel at the same 
            #time , this fix might need further mods. 
        self.setDisplay(diCYLINDER)

    def dispSurface(self):
        cmd = greenmsg("Set Display Surface: ")
        if self.assy and self.assy.selatoms:
            # Fixes bug 2005. Mark 060702.
            env.history.message(cmd + "Selected atoms cannot have their display mode set to Surface.")
            return #ninad 061003 fixed bug 2286
        self.setDisplay(diSURFACE)

    def setDisplay(self, form, default_display=False):
        """
        Set the display of the selection to 'form'.  If nothing is selected, then change
        the GLPane's current display to 'form'.
        """
        if self.assy and self.assy.selatoms:
            for ob in self.assy.selatoms.itervalues():
                ob.setDisplay(form)
        elif self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.setDisplay(form)
        else:
            if self.glpane.displayMode == form:
                pass ## was 'return' # no change needed
                # bruce 041129 removing this optim, tho correct in theory,
                # since it's not expensive to changeapp and repaint if user
                # hits a button, so it's more important to fix any bugs that
                # might be in other code failing to call changeapp when needed.
            self.glpane.setDisplay(form, default_display) # See docstring for info about default_display
        self.win_update() # bruce 041206, needed for model tree display mode icons
        ## was self.glpane.paintGL() [but now would be self.glpane.gl_update]

    def dispObjectColor(self, initialColor = Qt.white):
        """
        Sets the color of the selected chunks and/or jigs to a color the user 
        chooses.
        
        @param initialColor: the initial color to display in the color chooser
                             dialog. The default initial color is white.
        @type  initialColor: QColor
        
        @note: Need better method name (i.e. setObjectColor()).
        """
        
        _cmd = greenmsg("Change Color: ")
        
        from ops_select import objectSelected, ATOMS, CHUNKS, JIGS
        if not objectSelected(self.assy, objectFlags = CHUNKS | JIGS):
            if objectSelected(self.assy, objectFlags = ATOMS):
                _msg = redmsg("Cannot change color of individual atoms.")
            else:
                _msg = redmsg("Nothing selected.")
            env.history.message(_cmd + _msg)
            return
        
        _numSelectedObjects = self.assy.getNumberOfSelectedChunks() \
                            + self.assy.getNumberOfSelectedJigs()
        
        if _numSelectedObjects == 1 and self.assy.getNumberOfSelectedChunks() == 1:
            # If only one object is selected, and its a chunk, 
            # assign initialColor its color.
            _selectedChunkColor = self.assy.selmols[0].color
            if _selectedChunkColor:
                from widgets import RGBf_to_QColor
                initialColor = RGBf_to_QColor(_selectedChunkColor)
        
        elif _numSelectedObjects == 1 and self.assy.getNumberOfSelectedJigs() == 1:
            # If only one object is selected, and its a jig, 
            # assign initialColor its color.
            _selectedJig = self.assy.getSelectedJigs()
            _selectedJigColor = _selectedJig[0].normcolor
            if _selectedJigColor:
                from widgets import RGBf_to_QColor
                initialColor = RGBf_to_QColor(_selectedJigColor)
                
        _c = QColorDialog.getColor(initialColor, self)
        if _c.isValid():
            from widgets import QColor_to_RGBf
            _newColor = QColor_to_RGBf(_c)
            list = []
            for ob in self.assy.selmols:
                ob.setcolor(_newColor)
                list.append(ob)
                
            for ob in self.assy.getSelectedJigs():
                ob.color = _newColor # Need jig.setColor() method! --mark
                ob.normcolor =  _newColor
                list.append(ob)

            # Ninad 070321: Since the chunk is selected as a colored selection, 
            # it should be unpicked after changing its color. 
            # The user has most likely selected the chunk to change its color 
            # and won't like it still shown 'green'(the selection color) 
            # even after changing the color. so deselect it. 	
            # The chunk is NOT unpicked IF the color is changed via chunk 
            # property dialog. see ChunkProp.change_chunk_color for details.
            # This is intentional.

            for ob in list: 		
                ob.unpick()

            self.win_update()

    def dispResetChunkColor(self):
        """
        Resets the selected chunk's atom colors to the current element colors.
        """
        if not self.assy.selmols: 
            env.history.message(redmsg("Reset Chunk Color: No chunks selected."))
            return

        for chunk in self.assy.selmols:
            chunk.setcolor(None)
        self.glpane.gl_update()

    def dispResetAtomsDisplay(self):
        """
        Resets the display setting for each atom in the selected chunks or
        atoms to Default display mode.
        """

        cmd = greenmsg("Reset Atoms Display: ")
        msg = "No atoms or chunks selected."

        if self.assy.selmols: 
            self.assy.resetAtomsDisplay()
            msg = "Display setting for all atoms in selected chunk(s) reset" \
                " to Default (i.e. their parent chunk's display mode)."

        if self.assy.selectionContainsAtomsWithOverriddenDisplay():
            for a in self.assy.selatoms.itervalues(): #bruce 060707 itervalues
                if a.display != diDEFAULT:
                    a.setDisplay(diDEFAULT)

            msg = "Display setting for all selected atom(s) reset to Default" \
                " (i.e. their parent chunk's display mode)."

        env.history.message(cmd + msg)

    def dispShowInvisAtoms(self):
        """
        Resets the display setting for each invisible atom in the selected
        chunks or atoms to Default display mode.
        """

        cmd = greenmsg("Show Invisible Atoms: ")

        if not self.assy.selmols and not self.assy.selatoms:
            msg = "No atoms or chunks selected."
            env.history.message(cmd + msg)
            return

        nia = 0 # nia = Number of Invisible Atoms

        if self.assy.selmols:
            nia = self.assy.showInvisibleAtoms()

        if self.assy.selectionContainsInvisibleAtoms():
            for a in self.assy.selatoms.itervalues(): #bruce 060707 itervalues
                if a.display == diINVISIBLE: 
                    a.setDisplay(diDEFAULT)
                    nia += 1

        msg = cmd + str(nia) + " invisible atoms found."
        env.history.message(msg)

    def changeBackgroundColor(self):
        """
        Let user change the background color of the 3D Graphics Area,
        aka "the glpane" to the developers.
        """
        self.userPrefs.showDialog(pagename='General')

    # pop up Element Color Selector dialog
    def dispElementColorSettings(self):
        """
        Slot for 'Display > Element Color Settings...' menu item.
        """
        self.showElementColorSettings()

    def showElementColorSettings(self, parent=None):
        """
        Opens the Element Color Setting dialog, allowing the user to change 
        default colors of elements and bondpoints, and save them to a file.

        @param parent: The parent of the Element Color Setting dialog.
                       This allows the caller (i.e. Preferences dialog) to 
                       make it modal.
        @type  parent: U{B{QDialog}<http://doc.trolltech.com/4/qdialog.html>}
        """
        global elementColorsWin
        # Huaicai 2/24/05: Create a new element selector window each time,  
        # so it will be easier to always start from the same states.
        # Make sure only a single element window is shown
        if elementColorsWin and elementColorsWin.isVisible(): 
            return 

        if not parent:
            parent = self

        elementColorsWin = elementColors(parent)
        elementColorsWin.setDisplay(self.Element)
        # Sync the thumbview bg color with the current mode's bg color.  Mark 051216.
        elementColorsWin.elemGLPane.setBackgroundColor(
            self.glpane.backgroundColor, 
            self.glpane.backgroundGradient
        )
        elementColorsWin.show()

    def dispLighting(self):
        """
        Allows user to change lighting brightness.
        """
        self.userPrefs.showDialog('Lighting') # Show Prefences | Lighting.

    ###############################################################
    # Select Toolbar Slots
    ###############################################################

    def selectAll(self):
        """
        Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        """
        env.history.message(greenmsg("Select All:"))
        self.assy.selectAll()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectNone(self):
        env.history.message(greenmsg("Select None:"))
        self.assy.selectNone()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectInvert(self):
        """
        If some parts are selected, select the other parts instead.
        If some atoms are selected, select the other atoms instead
        (even in chunks with no atoms selected, which end up with
        all atoms selected). (And unselect all currently selected
        parts or atoms.)
        """
        #env.history.message(greenmsg("Invert Selection:"))
        # assy method revised by bruce 041217 after discussion with Josh
        self.assy.selectInvert()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectConnected(self):
        """
        Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """
        self.assy.selectConnected()

    def selectDoubly(self):
        """
        Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds. 
        """
        self.assy.selectDoubly()

    def selectExpand(self):
        """
        Slot for Expand Selection, which selects any atom that is bonded 
        to any currently selected atom.
        """
        self.assy.selectExpand()

    def selectContract(self):
        """
        Slot for Contract Selection, which unselects any atom which has
        a bond to an unselected atom, or which has any open bonds.
        """
        self.assy.selectContract()

    ###################################
    # Jig Toolbar Slots
    ###################################

    def makeGamess(self):
        self.assy.makegamess()

    def makeAnchor(self): # Changed name from makeGround. Mark 051104.
        self.assy.makeAnchor()

    def makeStat(self):
        self.assy.makestat()

    def makeThermo(self):
        self.assy.makethermo()

    def makeRotaryMotor(self):
        self.assy.makeRotaryMotor()

    def makeLinearMotor(self):
        self.assy.makeLinearMotor()

    def createPlane(self):
        self.assy.createPlane()	

    def makeGridPlane(self):
        self.assy.makeGridPlane()

    def createPolyLine(self):
        pass
        if 0: #NIY
            self.assy.createPolyLine()

    def makeESPImage(self):
        self.assy.makeESPImage()

    def makeAtomSet(self):
        self.assy.makeAtomSet()

    def makeMeasureDistance(self):
        self.assy.makeMeasureDistance()

    def makeMeasureAngle(self):
        self.assy.makeMeasureAngle()

    def makeMeasureDihedral(self):
        self.assy.makeMeasureDihedral()


    ###################################
    # Modify Toolbar Slots
    ###################################

    def modifyAdjustSel(self):
        """
        Adjust the current selection.
        """
        if platform.atom_debug:
            print "debug: reloading runSim on each use, for development"
            import runSim, debug
            debug.reload_once_per_event(runSim)
        from runSim import Minimize_CommandRun
        cmdrun = Minimize_CommandRun( self, 'Sel', type = 'Adjust')
        cmdrun.run()
        return

    def modifyAdjustAll(self):
        """
        Adjust all atoms.
        """
        if platform.atom_debug:
            print "debug: reloading runSim on each use, for development"
            import runSim, debug
            debug.reload_once_per_event(runSim)
        from runSim import Minimize_CommandRun
        cmdrun = Minimize_CommandRun( self, 'All', type = 'Adjust')
        cmdrun.run()
        return

    def modifyHydrogenate(self):
        """
        Add hydrogen atoms to each singlet in the selection.
        """
        self.assy.modifyHydrogenate()

    # remove hydrogen atoms from selected atoms/molecules
    def modifyDehydrogenate(self):
        """
        Remove all hydrogen atoms from the selection.
        """
        self.assy.modifyDehydrogenate()

    def modifyPassivate(self):
        """
        Passivate the selection by changing surface atoms to eliminate singlets.
        """
        self.assy.modifyPassivate()

    def modifyDeleteBonds(self):
        """
        Delete all bonds between selected and unselected atoms or chunks.
        """
        self.assy.modifyDeleteBonds()

    def modifyStretch(self):
        """
        Stretch/expand the selected chunk(s).
        """
        self.assy.Stretch()

    def modifySeparate(self):
        """
        Form a new chunk from the selected atoms.
        """
        self.assy.modifySeparate()

    def modifyMerge(self):
        """
        Create a single chunk from two of more selected chunks.
        """
        self.assy.merge()
        self.win_update()

    def makeChunkFromAtom(self):
        """
        Create a new chunk from the selected atoms.
        """
        self.assy.makeChunkFromSelectedAtoms()
        self.win_update()

    def modifyInvert(self):
        """
        Invert the atoms of the selected chunk(s).
        """
        self.assy.Invert()

    def modifyMirror(self):
        """
        Mirrors the selected chunks through a Plane (or Grid Plane).
        """
        self.assy.Mirror()

    def modifyAlignCommonAxis(self):
        """
        Align selected chunks to the computed axis of the first chunk.
        """
        self.assy.align()
        self.win_update()

    def modifyCenterCommonAxis(self):
        """
        Same as "Align to Common Axis", except that it moves all the selected
        chunks to the center of the first selected chunk after 
        aligning/rotating the other chunks.
        """

        # This is still not fully implemented as intended.  Instead of moving all the selected 
        # chunks to the center of the first selected chunk, I want to have them moved to the closest 
        # (perpendicular) point of the first chunk's axis.  I've studied and understand the math involved; 
        # I just need to implement the code.  I plan to ask Bruce for help since the two of us will get it 
        # done much more quickly together than me doing it alone.
        # Mark 050829.

        self.assy.alignmove()
        self.win_update()

    ###################################
    # Help Toolbar Slots
    ###################################

    def helpMouseControls(self):
        self.help.showDialog(0)

    def helpKeyboardShortcuts(self):
        self.help.showDialog(1)

    def helpGraphicsCard(self):
        """
        Display details about the system\'s graphics card in a dialog.
        """
        ginfo = get_gl_info_string( self.glpane) #bruce 070308 added glpane arg

        from widgets import TextMessageBox
        msgbox = TextMessageBox(self)
        msgbox.setWindowTitle("Graphics Card Info")
        msgbox.setText(ginfo)
        msgbox.show()

# I modified a copy of cpuinfo.py from 
# http://cvs.sourceforge.net/viewcvs.py/numpy/Numeric3/scipy/distutils/
# thinking it might help us support users better if we had a built-in utility
# for interrogating the CPU.  I do not plan to commit cpuinfo.py until I speak
# to Bruce about this. Mark 051209.
# 
#    def helpCpuInfo(self):
#        """
#        Displays this system's CPU information.
#        """
#        from cpuinfo import get_cpuinfo
#        cpuinfo = get_cpuinfo()
#        
#        from widgets import TextMessageBox
#        msgbox = TextMessageBox(self)
#        msgbox.setCaption("CPU Info")
#        msgbox.setText(cpuinfo)
#        msgbox.show()

    def helpAbout(self):
        """
        Displays information about this version of NanoEngineer-1.
        """
        from version import Version
        v = Version()
        product = v.product
        versionString = repr(v) + (" (%s)" % v.releaseType)
        date = "Release Date: " + v.releaseDate
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        if filePath.endswith('/Contents/Resources'):
            filePath = filePath[:-19]
        installdir = "Running from: " + filePath
        techsupport = "For technical support, send email to support@nanorex.com"
        website = "Website: www.nanoengineer-1.com"
        wiki = "Wiki: www.nanoengineer-1.net"
        aboutstr = product + " " + versionString \
                 + "\n\n" \
                 + date \
                 + "\n\n" \
                 + installdir \
                 + "\n\n" \
                 + v.copyright \
                 + "\n\n" \
                 + techsupport \
                 + "\n" \
                 + website \
                 + "\n" \
                 + wiki

        QMessageBox.about ( self, "About NanoEngineer-1", aboutstr)

    def helpWhatsThis(self):
        from PyQt4.Qt import QWhatsThis ##bruce 050408
        QWhatsThis.enterWhatsThisMode ()


    ###################################
    # Modes Toolbar Slots
    ###################################

    # get into Select Atoms mode
    def toolsSelectAtoms(self): # note: this can NO LONGER be called from update_select_mode [as of bruce 060403]
        self.commandSequencer.userEnterCommand('SELECTATOMS')

    # get into Select Chunks mode
    def toolsSelectMolecules(self):# note: this can also be called from update_select_mode [bruce 060403 comment]
        self.commandSequencer.userEnterCommand('SELECTMOLS')

    # get into Move Chunks (or Translate Components) command        
    def toolsMoveMolecule(self):
        self.ensureInCommand('MODIFY')
        self.currentCommand.propMgr.activate_translateGroupBox()
        return

    # Rotate Components command
    def toolsRotateComponents(self):
        self.ensureInCommand('MODIFY')
        self.currentCommand.propMgr.activate_rotateGroupBox()
        return

    # get into Build mode        
    def toolsBuildAtoms(self): # note: this can now be called from update_select_mode [as of bruce 060403]
        self.depositState = 'Atoms'
        self.commandSequencer.userEnterCommand('DEPOSIT')

    # get into cookiecutter mode
    def toolsCookieCut(self):
        self.commandSequencer.userEnterCommand('COOKIE')

    # get into Extrude mode
    def toolsExtrude(self):
        self.commandSequencer.userEnterCommand('EXTRUDE')

    # get into Fuse Chunks mode
    def toolsFuseChunks(self):
        self.commandSequencer.userEnterCommand('FUSECHUNKS')

    ###################################
    # Simulator Toolbar Slots
    ###################################

    def simMinimizeEnergy(self):
        """
        Opens the Minimize Energy dialog.
        """
        self.minimize_energy.setup()

    def simSetup(self):
        """
        Creates a movie of a molecular dynamics simulation.
        """
        if platform.atom_debug: #bruce 060106 added this (fixing trivial bug 1260)
            print "atom_debug: reloading runSim on each use, for development"
            import runSim
            reload(runSim)
        from runSim import simSetup_CommandRun
        cmdrun = simSetup_CommandRun( self)
        cmdrun.run()
        return

    def simNanoHive(self):
        """
        Opens the Nano-Hive dialog... for details see subroutine's docstring.
        """
        # This should be probably be modeled after the simSetup_CommandRun class
        # I'll do this if Bruce agrees.  For now, I want to get this working ASAP.
        # Mark 050915.
        self.nanohive.showDialog(self.assy)

    def simPlot(self):
        """
        Opens the "Make Graphs" dialog if there is a movie file
	(i.e. a movie file has been opened in the Movie Player).
	For details see subroutine's docstring.
        """
        from PlotTool import simPlot
        dialog = simPlot(self.assy) # Returns "None" if there is no current movie file. [mark 2007-05-03]
        if dialog:
            self.plotcntl = dialog #probably useless, but done since old code did it;
                # conceivably, keeping it matters due to its refcount. [bruce 050327]
                # matters now, since dialog can be None. [mark 2007-05-03]
        return

    def simMoviePlayer(self):
        """
        Plays a DPB movie file created by the simulator.
        """
        from movieMode import simMoviePlayer
        simMoviePlayer(self.assy)
        return

    def JobManager(self):
        """
        Opens the Job Manager dialog... for details see subroutine's docstring.

        @note: This is not implemented.
        """
        from JobManager import JobManager
        dialog = JobManager(self)
        if dialog:
            self.jobmgrcntl = dialog
                # probably useless, but done since old code did it;
                # conceivably, keeping it matters due to its refcount. 
                # See Bruce's note in simPlot().
        return

    def serverManager(self):
        """
        Opens the server manager dialog.

        @note: This is not implemented.
        """
        from ServerManager import ServerManager
        ServerManager().showDialog()

    ###################################
    # Insert Menu/Toolbar Slots
    ###################################

    def ensureInCommand(self, modename): #bruce 071009
        """
        If the current command's .modename differs from the one given, change
        to that command.

        @note: it's likely that this method is not needed since
        userEnterCommand has the same special case of doing nothing
        if we're already in the named command. If so, the special case
        could be removed with no effect, and this method could be
        inlined to just userEnterCommand.

        @note: all uses of this method are causes for suspicion, about
        whether some sort of refactoring or generalization is called for,
        unless they are called from a user command whose purpose is solely
        to switch to the named command. (In other words, switching to it
        for some reason other than the user asking for that is suspicious.)
        (That happens in current code [071011], and ought to be cleared up somehow,
         but maybe not using this method in particular.)
        """
        commandSequencer = self.commandSequencer
        if commandSequencer.currentCommand.modename != modename:
            commandSequencer.userEnterCommand(modename)
            # note: this changes the value of .currentCommand
        return

    def insertAtom(self):
        self.ensureInCommand('SELECTMOLS')
        self.atomcntl.show()

    def insertGraphene(self):
        self.ensureInCommand('SELECTMOLS')
        self.graphenecntl.show()

    def insertNanotube(self):
        self.ensureInCommand('SELECTMOLS')
        self.nanotubecntl.show()

    def activateDnaTool(self):
        Ui_DnaFlyout.activateDnaFlyout(self)

    def insertDna(self):
        self.ensureInCommand('SELECTMOLS')
        if debug_pref("Use old 'Build > DNA' generator? (next session)", 
                      Choice_boolean_False, 
                      non_debug = True,
                      prefs_key = "A9 devel/DNA Duplex"):

            self.dnacntl.show()
        else:
            self.dnaEditController = self._createDnaDuplexEditController()
            self.dnaEditController.runController()

    def _createDnaDuplexEditController(self, dnaDuplex = None):
        """
	Returns a new L{DnaDuplexEditController} object.	
	@param dnaDuplex: This parameter is passed as an init argument for 
			    the LinearMotorEditController that this method 
			    creates and returns.
	@type dnaDuplex:  B{Group} or None  (instead of a Group it will be a 
	                  separate DNA object in future. 
	@see: L{Group.__init__} , L{Group.edit}, 
	      L{DnaDuplexEditController.__init__}
	TODO: Need to use the same property manager object for all dna edit 
	      controllers. Right now it creates different ones. 
        """
        from DnaDuplexEditController import DnaDuplexEditController
        return DnaDuplexEditController(self, dnaDuplex)
    
    def createSequenceEditorIfNeeded(self):
        """
        Returns a Sequence editor object (a dockwidget).
        If one doesn't already exists, it creates one .
        (created only once and only when its first requested and then the 
        object is reused)
        @return: The sequence editor object (self.sequenceEditor
        @rtype: B{SequenceEditor}
        @see: DnaDuplexPropertyManager._loadSequenceEditor
        @WARNING: QMainwindow.restoreState prints a warning message because its 
        unable to find this object in the next session. (as this object is 
        created only when requested) This warning message is harmless, but
        if we want to get rid of it, easiest way is to always  create this 
        object when MainWindow is created. (This is a small object so may 
        be thats the best way)
        """
        if not self.sequenceEditor:
            from SequenceEditor import SequenceEditor
            self.sequenceEditor = SequenceEditor(self)
            self.sequenceEditor.setObjectName("sequence_editor")
            #Should changes.keep_forevenr be called here? 
            #doesn't look necessary at the moment -- ninad 2007-11-21
        
        return self.sequenceEditor   
    
    def createRotaryMotorPropMgr_if_needed(self, editController):
        """
        Create the Rotary motor PM object (if one doesn't exist) 
        If this object is already present, then set its editcontroller to this
        parameter
        @parameter editController: The edit controller object for this PM 
        @type editController: B{RotaryMotorEditController}
        @see: B{RotaryMotorEditController._createPropMgrObject}
        """
        from RotaryMotorPropertyManager import RotaryMotorPropertyManager
        if self.rotaryMotorPropMgr is None:
            self.rotaryMotorPropMgr = \
                RotaryMotorPropertyManager(self, editController)  
        else:
            self.rotaryMotorPropMgr.setEditController(editController)        
        
        return self.rotaryMotorPropMgr   
    
    
    def createLinearMotorPropMgr_if_needed(self, editController):
        """
        Create the Linear motor PM object (if one doesn't exist) 
        If this object is already present, then set its editcontroller to this
        parameter
        @parameter editController: The edit controller object for this PM 
        @type editController: B{LinearMotorEditController}
        @see: B{LinearMotorEditController._createPropMgrObject}
        """
        from LinearMotorPropertyManager import LinearMotorPropertyManager
        if self.linearMotorPropMgr is None:
            self.linearMotorPropMgr = \
                LinearMotorPropertyManager( self, editController)  
        else:
            self.linearMotorPropMgr.setEditController(editController)        
        
        return self.linearMotorPropMgr
    
    def createPlanePropMgr_if_needed(self, editController):
        """
        Create the Plane PM object (if one doesn't exist) 
        If this object is already present, then set its editcontroller to this
        parameter
        @parameter editController: The edit controller object for this PM 
        @type editController: B{RotaryMotorEditController}
        @see: B{PlaneEditController._createPropMgrObject}
        """
        from PlanePropertyManager import PlanePropertyManager
        if self.planePropMgr is None:
            self.planePropMgr = \
                PlanePropertyManager(self, editController)  
        else:
            self.planePropMgr.setEditController(editController)        
        
        return self.planePropMgr
    
    def createDnaDuplexPropMgr_if_needed(self, editController):
        """
        THIS METHOD IS NOT USED AS OF 2007-12-04
        - This is because the endPoint1 and endPoint2 passed to the 
        Dna duplex PM are unique for each generated Dna group. So having a 
        unique PM for editing such a dna group. The 'endPoints' are not stored
        in the dna group. The new dna data model will store the axis end points
        Once thats done this method will be used to create only a single 
        PM object and reusing it as needed. 
        
        Create the DNA Duplex PM object (if one doesn't exist) 
        If this object is already present, then set its editcontroller to this
        parameter
        @parameter editController: The edit controller object for this PM 
        @type editController: B{DnaDuplexEditController}
        """
        from DnaDuplexPropertyManager import DnaDuplexPropertyManager
        if self.dnaDuplexPropMgr is None:
            self.dnaDuplexPropMgr = \
                DnaDuplexPropertyManager(self, editController)
        else:
            self.dnaDuplexPropMgr.setEditController(editController)
            
        return self.dnaDuplexPropMgr

    def insertPovrayScene(self):
        self.povrayscenecntl.setup()

    def insertComment(self):
        """
        Insert a new comment into the model tree.
        """
        self.commentcntl.setup()

    ###################################
    # Slots for future tools
    ###################################

    # Mirror Tool
    def toolsMirror(self):
        env.history.message(redmsg("Mirror Tool: Not implemented yet."))

    # Mirror Circular Boundary Tool
    def toolsMirrorCircularBoundary(self):
        env.history.message(redmsg("Mirror Circular Boundary Tool: Not implemented yet."))

    ###################################
    # Slots for Dashboard widgets
    ###################################

    # fill the shape created in the cookiecutter with actual
    # carbon atoms in a diamond lattice (including bonds)
    # this works for all modes, not just add atom
    def toolsDone(self):
        self.currentCommand.Done()

    def toolsStartOver(self):
        self.currentCommand.Restart()

    def toolsBackUp(self):
        self.currentCommand.Backup()

    def toolsCancel(self):
        self.currentCommand.Flush()

    ######################################
    # Show View > Orientation Window     
    #######################################

    def showOrientationWindow(self): #Ninad 061121

        if not self.orientationWindow:
            self.orientationWindow  = ViewOrientationWindow(self)
            #self.orientationWindow.createOrientationViewList(namedViewList)
            self.orientationWindow.createOrientationViewList()
            self.viewOrientationAction.setChecked(True)
            self.orientationWindow.setVisible(True)    	
        else:
            if not self.orientationWindow.isVisible():
                self.orientationWindow.setVisible(True)
                self.viewOrientationAction.setChecked(True)

        return self.orientationWindow

    def deleteOrientationWindow(self):
        """
        Delete the orientation window when the main window closes.
        """
        #ninad 061121 - this is probably unnecessary  
        if self.orientationWindow:
            self.orientationWindow.close()
            self.orientationWindow = None

        return self.orientationWindow

    # key event handling revised by bruce 041220 to fix some bugs;
    # see comments in the GLPane methods.

    def keyPressEvent(self, e):
        self.glpane.keyPressEvent(e)

    def keyReleaseEvent(self, e):
        self.glpane.keyReleaseEvent(e)

    def wheelEvent(self, event): #bruce 070607 fix bug xxx [just reported, has no bug number yet]
        ## print "mwsem ignoring wheelEvent",event
        # Note: this gets called by wheel events with mouse inside history widget,
        # whenever it has reached its scrolling limit. Defining it here prevents the bug
        # of Qt passing it on to GLPane (maybe only happens if GLPane was last-clicked widget),
        # causing unintended mousewheel zoom. Apparently just catching this and returning is
        # enough -- it's not necessary to also call event.ignore(). Guess: this method's default
        # implem passes it either to "central widget" (just guessing that's the GLPane) or to
        # the last widget we clicked on (or more likely, the one with the keyfocus).
        return

    # Load IconSets #########################################
    def load_icons_to_iconsets(self): ### REVIEW (Mark): is this still needed? [bruce 070820]
        """
        Load additional icons to QAction icon sets that are used in MainWindow
        toolbars and menus. This is experimental. mark 060427.
        """
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        small_disabled_on_icon_fname = filePath + "/../images/redoAction_small_disabled_off.png"

        # Add the small "disabled/off" icon for the Redo QAction, displayed when editRedoAction.setDisabled(1).
        editRedoIconSet = self.editRedoAction.iconSet()
        editRedoIconSet.setPixmap ( small_disabled_on_icon_fname, QIcon.Small, QIcon.Disabled, QIcon.Off )
        self.editRedoAction.setIcon ( editRedoIconSet )
        return

    def enableViews(self, enableFlag = True):
        """
        Disables/enables view actions on toolbar and menu.
        """
        self.viewNormalToAction.setEnabled(enableFlag)
        self.viewParallelToAction.setEnabled(enableFlag)

        self.viewFrontAction.setEnabled(enableFlag)
        self.viewBackAction.setEnabled(enableFlag)
        self.viewTopAction.setEnabled(enableFlag)
        self.viewBottomAction.setEnabled(enableFlag)
        self.viewLeftAction.setEnabled(enableFlag)
        self.viewRightAction.setEnabled(enableFlag)
        self.viewIsometricAction.setEnabled(enableFlag)

        self.setViewHomeAction.setEnabled(enableFlag)
        self.setViewFitToWindowAction.setEnabled(enableFlag)
        self.setViewRecenterAction.setEnabled(enableFlag)

        self.viewRotate180Action.setEnabled(enableFlag)
        self.viewRotatePlus90Action.setEnabled(enableFlag)
        self.viewRotateMinus90Action.setEnabled(enableFlag)
        return

    def disable_QActions_for_extrudeMode(self, disableFlag = True):
        """
        Disables action items in the main window for extrudeMode.
        """
        self.disable_QActions_for_movieMode(disableFlag)
        self.modifyHydrogenateAction.setEnabled(not disableFlag)
        self.modifyDehydrogenateAction.setEnabled(not disableFlag)
        self.modifyPassivateAction.setEnabled(not disableFlag)
        self.modifyDeleteBondsAction.setEnabled(not disableFlag)
        self.modifyStretchAction.setEnabled(not disableFlag)
        self.modifySeparateAction.setEnabled(not disableFlag)
        self.modifyMergeAction.setEnabled(not disableFlag)
        self.modifyInvertAction.setEnabled(not disableFlag)
        self.modifyMirrorAction.setEnabled(not disableFlag)
        self.modifyAlignCommonAxisAction.setEnabled(not disableFlag)
        # All QActions in the Modify menu/toolbar should be disabled, 
        # too. mark 060323
        return

    def disable_QActions_for_sim(self, disableFlag = True):
        """
        Disables actions items in the main window during simulations
        (and minimize).
        """
        self.disable_QActions_for_movieMode(disableFlag)
        self.simMoviePlayerAction.setEnabled(not disableFlag)
        return

    def disable_QActions_for_movieMode(self, disableFlag = True):
        """
        Disables action items in the main window for movieMode;
        also called by disable_QActions_for_extrudeMode
        and by disable_QActions_for_sim.
        """
        enable = not disableFlag
        self.modifyAdjustSelAction.setEnabled(enable) # "Adjust Selection"
        self.modifyAdjustAllAction.setEnabled(enable) # "Adjust All"
        self.simMinimizeEnergyAction.setEnabled(enable) # Minimize Energy 
        self.simSetupAction.setEnabled(enable) # "Simulator"
        self.fileSaveAction.setEnabled(enable) # "File Save"
        self.fileSaveAsAction.setEnabled(enable) # "File Save As"
        self.fileOpenAction.setEnabled(enable) # "File Open"
        self.fileCloseAction.setEnabled(enable) # "File Close"
        self.fileInsertAction.setEnabled(enable) # "File Insert"
        self.editDeleteAction.setEnabled(enable) # "Delete"

        # [bruce 050426 comment: I'm skeptical of disabling zoom/pan/rotate,
        #  and suggest for some others (especially "simulator") that they
        #  auto-exit the mode rather than be disabled,
        #  but I won't revise these for now.]
        #
        # [update, bruce 070813/070820]
        # Zoom/pan/rotate are now rewritten to suspend rather than exit
        # the current mode, so they no longer need disabling in Extrude or
        # Movie modes. (There is one known minor bug (2517) -- Movie mode
        # asks whether to rewind (via popup dialog), which is only appropriate
        # to ask if it's being exited. Fixing this is relevant to the
        # upcoming "command sequencer".)
        # This is also called by disable_QActions_for_sim, and whether this
        # change is safe in that case is not carefully reviewed or tested,
        # but it seems likely to be ok.

##        self.zoomToolAction.setEnabled(enable) # "Zoom Tool"
##        self.panToolAction.setEnabled(enable) # "Pan Tool"
##        self.rotateToolAction.setEnabled(enable) # "Rotate Tool"

        return

# == Caption methods

    def update_mainwindow_caption_properly(self, junk = None): #bruce 050810 added this
        self.update_mainwindow_caption(self.assy.has_changed())

    def update_mainwindow_caption(self, changed = False): #by mark; bruce 050810 revised this in several ways, fixed bug 785
        """
        Update the caption at the top of the of the main window. 
        Example:  "NanoEngineer-1 - [partname.mmp]"
        changed = True will add the prefix and suffix to the caption denoting the part has been changed.
        """
        caption_prefix = env.prefs[captionPrefix_prefs_key]
        caption_suffix = env.prefs[captionSuffix_prefs_key]
        caption_fullpath = env.prefs[captionFullPath_prefs_key]

        if changed:
            prefix = caption_prefix
            suffix = caption_suffix
        else:
            prefix = ''
            suffix = ''

        # this is not needed here since it's already done in the prefs values themselves when we set them:
        # if prefix and not prefix.endswith(" "):
        #     prefix = prefix + " "
        # if suffix and not suffix.startswith(" "):
        #     suffix = " " + suffix

        try:
            junk, basename = os.path.split(self.assy.filename)
            assert basename # it's normal for this to fail, when there is no file yet

            if caption_fullpath:
                partname = os.path.normpath(self.assy.filename)#fixed bug 453-1 ninad060721
            else:
                partname = basename

        except:
            partname = 'Untitled'

        ##e [bruce 050811 comment:] perhaps we should move prefix to the beginning, rather than just before "[";
        # and in any case the other stuff here, self.name() + " - " + "[" + "]", should also be user-changeable, IMHO.
        #print "****self.accessibleName *****=" , self.accessibleName()
        self.setWindowTitle(self.trUtf8("NanoEngineer-1" + " - " +prefix + "[" + partname + "]" + suffix))
        self.setWindowIcon(geticon("ui/border/MainWindow"))
        return
    
    def createProgressDialog(self):
        """
        Creates the main window's Progress Dialog, which can be used to 
        display a progress dialog at any time. It is modal by default.
        
        @see: _readmmp() for an example of use.
        @see: U{B{QProgressDialog}<http://doc.trolltech.com/4/qprogressdialog.html>}
        
        """
        from PyQt4.Qt import QProgressDialog
        self.progressDialog = QProgressDialog(self)
        self.progressDialog.setWindowModality(Qt.WindowModal)
        self.progressDialog.setWindowTitle("NanoEngineer-1")
        
        # setMinimumDuration() doesn't work. Qt bug?
        self.progressDialog.setMinimumDuration(500) # 500 ms = 0.5 seconds
    
    pass # end of class MWsemantics

# end

