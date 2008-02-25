# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_MainWindowWidgets.py

Creates all widgets use by the Main Window, including:
- QAction used as menu items for menus in the main menu bar
- QActions, QToolButtons, etc. in main toolbars
- QAction for the Command toolbar

@author: Mark
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

History:

2007-12-23: Moved all QActions from menu and toolbar setupUi() functions here.
"""
import env
from PyQt4 import QtGui
from PyQt4.Qt import QToolButton
from icon_utilities import geticon
from prefs_constants import displayRulers_prefs_key

def setupUi(win):
    """
    Creates and populates the "File" menu in the main menubar.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """

    MainWindow = win
    
    # Create the NE1 main menu bar.
    win.MenuBar = QtGui.QMenuBar(MainWindow)
    win.MenuBar.setEnabled(True)
    win.MenuBar.setObjectName("MenuBar")

    #= File (menu and toolbar) widgets.
    
    # Create the "File" menu.
    win.fileMenu = QtGui.QMenu(win.MenuBar)
    win.fileMenu.setObjectName("fileMenu")
    
    # Create the "Import" menu, a submenu of the "File" menu.
    win.importMenu = QtGui.QMenu(win.fileMenu)
    win.importMenu.setObjectName("importMenu")
    
    # Create the "Export" menu, a submenu of the "File" menu.
    win.exportMenu = QtGui.QMenu(win.fileMenu)
    win.exportMenu.setObjectName("exportMenu")

    win.fileOpenAction = QtGui.QAction(MainWindow)
    win.fileOpenAction.setIcon(geticon("ui/actions/File/Open"))
    win.fileOpenAction.setObjectName("fileOpenAction")

    win.fileCloseAction = QtGui.QAction(MainWindow)
    win.fileCloseAction.setObjectName("fileCloseAction")

    win.fileSaveAction = QtGui.QAction(MainWindow)
    win.fileSaveAction.setIcon(geticon("ui/actions/File/Save"))
    win.fileSaveAction.setObjectName("fileSaveAction")

    win.fileSaveAsAction = QtGui.QAction(MainWindow)
    win.fileSaveAsAction.setObjectName("fileSaveAsAction")

    win.fileImportOpenBabelAction = QtGui.QAction(MainWindow)
    win.fileImportOpenBabelAction.setObjectName("fileImportOpenBabelAction")
    
    win.fileExportPdbAction = QtGui.QAction(MainWindow)
    win.fileExportPdbAction.setObjectName("fileExportPdbAction")
    
    win.fileExportJpgAction = QtGui.QAction(MainWindow)
    win.fileExportJpgAction.setObjectName("fileExportJpgAction")
    
    win.fileExportPngAction = QtGui.QAction(MainWindow)
    win.fileExportPngAction.setObjectName("fileExportPngAction")
    
    win.fileExportPovAction = QtGui.QAction(MainWindow)
    win.fileExportPovAction.setObjectName("fileExportPovAction")
    
    win.fileExportAmdlAction = QtGui.QAction(MainWindow)
    win.fileExportAmdlAction.setObjectName("fileExportAmdlAction")
    
    win.fileExportOpenBabelAction = QtGui.QAction(MainWindow)
    win.fileExportOpenBabelAction.setObjectName("fileExportOpenBabelAction")

    # This action (i.e. the "Set Working Directory" menu item) was removed from 
    # the File menu for Alpha 9 since it was deemed undesireable.
    # If you want a full explanation, ask me. Mark 2007-12-30.
    win.fileSetWorkingDirectoryAction = QtGui.QAction(MainWindow)
    win.fileSetWorkingDirectoryAction.setObjectName("fileSetWorkingDirectoryAction")

    win.fileExitAction = QtGui.QAction(MainWindow)
    win.fileExitAction.setObjectName("fileExitAction")

    # "Save Selection" is not implemented yet (NIY). Mark 2007-12-20.
    win.fileSaveSelectionAction = QtGui.QAction(MainWindow)
    win.fileSaveSelectionAction.setObjectName("fileSaveSelectionAction")

    #= Edit (menu and toolbar) widgets.
    
    # Create the "Edit" menu.
    win.editMenu = QtGui.QMenu(win.MenuBar)
    win.editMenu.setObjectName("editMenu")

    win.editUndoAction = QtGui.QAction(MainWindow)
    win.editUndoAction.setIcon(geticon("ui/actions/Edit/Undo"))
    win.editUndoAction.setVisible(True)
    win.editUndoAction.setObjectName("editUndoAction")

    win.editRedoAction = QtGui.QAction(MainWindow)
    win.editRedoAction.setChecked(False)
    win.editRedoAction.setIcon(geticon("ui/actions/Edit/Redo"))
    win.editRedoAction.setVisible(True)
    win.editRedoAction.setObjectName("editRedoAction")

    win.editMakeCheckpointAction = QtGui.QAction(MainWindow)
    win.editMakeCheckpointAction.setIcon(
        geticon("ui/actions/Edit/Make_Checkpoint"))
    win.editMakeCheckpointAction.setObjectName("editMakeCheckpointAction")
    # Hide the "Make Checkpoint" toolbar button/menu item. mark 060302.
    win.editMakeCheckpointAction.setVisible(False)

    win.editAutoCheckpointingAction = QtGui.QAction(MainWindow)
    win.editAutoCheckpointingAction.setCheckable(True)
    win.editAutoCheckpointingAction.setChecked(True)
    win.editAutoCheckpointingAction.setObjectName("editAutoCheckpointingAction")

    win.editClearUndoStackAction = QtGui.QAction(MainWindow)
    win.editClearUndoStackAction.setObjectName("editClearUndoStackAction")

    win.editCutAction = QtGui.QAction(MainWindow)
    win.editCutAction.setEnabled(True)
    win.editCutAction.setIcon(geticon("ui/actions/Edit/Cut"))
    win.editCutAction.setObjectName("editCutAction")

    win.editCopyAction = QtGui.QAction(MainWindow)
    win.editCopyAction.setEnabled(True)
    win.editCopyAction.setIcon(geticon("ui/actions/Edit/Copy"))
    win.editCopyAction.setObjectName("editCopyAction")

    win.editPasteAction = QtGui.QAction(MainWindow)
    win.editPasteAction.setIcon(geticon("ui/actions/Edit/Paste_Off"))
    win.editPasteAction.setObjectName("editPasteAction")

    win.pasteFromClipboardAction = QtGui.QAction(MainWindow)
    win.pasteFromClipboardAction.setIcon(geticon(
        "ui/actions/Properties Manager/clipboard-full"))

    win.pasteFromClipboardAction.setObjectName("pasteFromClipboardAction")
    win.pasteFromClipboardAction.setText("Paste from clipboard...")

    win.editDeleteAction = QtGui.QAction(MainWindow)
    win.editDeleteAction.setIcon(geticon("ui/actions/Edit/Delete"))
    win.editDeleteAction.setObjectName("editDeleteAction")

    win.dispObjectColorAction = QtGui.QAction(MainWindow)
    win.dispObjectColorAction.setIcon(geticon("ui/actions/Edit/Edit_Color"))
    win.dispObjectColorAction.setObjectName("dispObjectColorAction")
    
    win.resetChunkColorAction = QtGui.QAction(MainWindow)
    win.resetChunkColorAction.setIcon(geticon("ui/actions/Edit/Reset_Chunk_Color"))
    win.resetChunkColorAction.setObjectName("resetChunkColorAction")

    #= View (menu and toolbar) actions.
    
    # Create the "View" menu.
    win.viewMenu = QtGui.QMenu(win.MenuBar)
    win.viewMenu.setObjectName("viewMenu")

    # Create the "Display" menu, a submenu of the "View" menu.
    win.displayMenu = QtGui.QMenu(win.viewMenu)
    win.displayMenu.setObjectName("displayMenu")
    
    # Create the "Modify" menu, a submenu of the "View" menu.
    win.modifyMenu = QtGui.QMenu(win.viewMenu)
    win.modifyMenu.setObjectName("viewMenu")
    
    # Note: The "Toolbars" submenu is created in Ui_ViewMenu.setupIu().

    #== View > Modify (menu and toolbar) actions.
    win.viewOrientationAction = QtGui.QAction(MainWindow)
    win.viewOrientationAction.setCheckable(True)
    win.viewOrientationAction.setIcon(
        geticon("ui/actions/View/Modify/Orientation"))
    win.viewOrientationAction.setObjectName("viewOrientationAction")

    win.setViewFitToWindowAction = QtGui.QAction(MainWindow)
    win.setViewFitToWindowAction.setIcon(
        geticon("ui/actions/View/Modify/Zoom_To_Fit"))
    win.setViewFitToWindowAction.setObjectName("setViewFitToWindowAction")

    win.setViewZoomtoSelectionAction = QtGui.QAction(MainWindow)
    win.setViewZoomtoSelectionAction.setIcon(
        geticon("ui/actions/View/Modify/Zoom_To_Selection"))
    win.setViewZoomtoSelectionAction.setObjectName("setViewZoomtoSelectionAction")

    win.zoomToAreaAction = QtGui.QAction(MainWindow)
    win.zoomToAreaAction.setCheckable(True)
    win.zoomToAreaAction.setIcon(geticon("ui/actions/View/Modify/ZoomToArea"))
    win.zoomToAreaAction.setObjectName("zoomToAreaAction")
    
    win.zoomInOutAction = QtGui.QAction(MainWindow)
    win.zoomInOutAction.setCheckable(True)
    win.zoomInOutAction.setIcon(geticon("ui/actions/View/Modify/Zoom_In_Out"))
    win.zoomInOutAction.setObjectName("zoomInOutAction")

    win.viewZoomAboutScreenCenterAction = QtGui.QAction(MainWindow)
    win.viewZoomAboutScreenCenterAction.setCheckable(True)
    win.viewZoomAboutScreenCenterAction.setObjectName("zoom about screen center")

    win.setViewRecenterAction = QtGui.QAction(MainWindow)
    win.setViewRecenterAction.setEnabled(True)
    win.setViewRecenterAction.setIcon(
        geticon("ui/actions/View/Modify/Recenter"))
    win.setViewRecenterAction.setObjectName("setViewRecenterAction")

    win.panToolAction = QtGui.QAction(MainWindow)
    win.panToolAction.setCheckable(True)
    win.panToolAction.setIcon(geticon("ui/actions/View/Modify/Pan"))
    win.panToolAction.setObjectName("panToolAction")

    win.rotateToolAction = QtGui.QAction(MainWindow)
    win.rotateToolAction.setCheckable(True)
    win.rotateToolAction.setIcon(geticon("ui/actions/View/Modify/Rotate"))
    win.rotateToolAction.setObjectName("rotateToolAction")

    win.setViewHomeAction = QtGui.QAction(MainWindow)
    win.setViewHomeAction.setIcon(geticon("ui/actions/View/Modify/Home"))
    win.setViewHomeAction.setObjectName("setViewHomeAction")

    win.setViewHomeToCurrentAction = QtGui.QAction(MainWindow)
    win.setViewHomeToCurrentAction.setObjectName("setViewHomeToCurrentAction")

    #= View toolbar QActions.
    win.viewNormalToAction = QtGui.QAction(MainWindow)
    win.viewNormalToAction.setIcon(
        geticon("ui/actions/View/Set_View_Normal_To"))
    win.viewNormalToAction.setObjectName("NormalTo")

    win.viewParallelToAction = QtGui.QAction(MainWindow)
    win.viewParallelToAction.setIcon(
        geticon("ui/actions/View/Set_View_Parallel_To"))
    win.viewParallelToAction.setObjectName("ParallelTo")

    win.saveNamedViewAction = QtGui.QAction(MainWindow)
    win.saveNamedViewAction.setIcon(
        geticon("ui/actions/View/Modify/Save_Named_View"))
    win.saveNamedViewAction.setObjectName("saveNamedViewAction")

    win.viewFrontAction = QtGui.QAction(MainWindow)
    win.viewFrontAction.setEnabled(True)
    win.viewFrontAction.setIcon(geticon("ui/actions/View/Front"))
    win.viewFrontAction.setObjectName("Front")

    win.viewBackAction = QtGui.QAction(MainWindow)
    win.viewBackAction.setIcon(geticon("ui/actions/View/Back"))
    win.viewBackAction.setObjectName("Back")

    win.viewRightAction = QtGui.QAction(MainWindow)
    win.viewRightAction.setIcon(geticon("ui/actions/View/Right"))
    win.viewRightAction.setObjectName("Right")

    win.viewLeftAction = QtGui.QAction(MainWindow)
    win.viewLeftAction.setIcon(geticon("ui/actions/View/Left"))
    win.viewLeftAction.setObjectName("Left")

    win.viewTopAction = QtGui.QAction(MainWindow)
    win.viewTopAction.setIcon(geticon("ui/actions/View/Top"))
    win.viewTopAction.setObjectName("Top")

    win.viewBottomAction = QtGui.QAction(MainWindow)
    win.viewBottomAction.setEnabled(True)
    win.viewBottomAction.setIcon(geticon("ui/actions/View/Bottom"))
    win.viewBottomAction.setObjectName("Bottom")

    win.viewIsometricAction = QtGui.QAction(MainWindow)
    win.viewIsometricAction.setIcon(geticon("ui/actions/View/Isometric"))
    win.viewIsometricAction.setObjectName("Isometric")

    win.viewRotate180Action = QtGui.QAction(MainWindow)
    win.viewRotate180Action.setIcon(
        geticon("ui/actions/View/Rotate_View_180"))
    win.viewRotate180Action.setObjectName("Rotate180")

    win.viewRotatePlus90Action = QtGui.QAction(MainWindow)
    win.viewRotatePlus90Action.setIcon(
        geticon("ui/actions/View/Rotate_View_+90"))
    win.viewRotatePlus90Action.setObjectName("RotatePlus90")

    win.viewRotateMinus90Action = QtGui.QAction(MainWindow)
    win.viewRotateMinus90Action.setIcon(
        geticon("ui/actions/View/Rotate_View_-90"))
    win.viewRotateMinus90Action.setObjectName("RotateMinus90")

    win.viewDefviewAction = QtGui.QAction(MainWindow)
    win.viewDefviewAction.setObjectName("viewDefviewAction")

    #== View > Display (menu and toolbar) actions.
    win.dispDefaultAction = QtGui.QAction(MainWindow)
    win.dispDefaultAction.setIcon(geticon("ui/actions/View/Display/Default"))
    win.dispDefaultAction.setObjectName("dispDefaultAction")

    win.dispInvisAction = QtGui.QAction(MainWindow)
    win.dispInvisAction.setIcon(geticon("ui/actions/View/Display/Invisible"))
    win.dispInvisAction.setObjectName("dispInvisAction")

    win.dispLinesAction = QtGui.QAction(MainWindow)
    win.dispLinesAction.setIcon(geticon("ui/actions/View/Display/Lines"))
    win.dispLinesAction.setObjectName("dispLinesAction")

    win.dispTubesAction = QtGui.QAction(MainWindow)
    win.dispTubesAction.setEnabled(True)
    win.dispTubesAction.setIcon(geticon("ui/actions/View/Display/Tubes"))
    win.dispTubesAction.setObjectName("dispTubesAction")

    win.dispCPKAction = QtGui.QAction(MainWindow)
    win.dispCPKAction.setIcon(geticon("ui/actions/View/Display/CPK"))
    win.dispCPKAction.setObjectName("dispCPKAction")

    win.dispBallAction = QtGui.QAction(MainWindow)
    win.dispBallAction.setIcon(geticon("ui/actions/View/Display/Ball_and_Stick"))
    win.dispBallAction.setObjectName("dispBallAction")
    
    #@ Unused. See comments at the top of Ui_ViewMenu.py.
    win.dispHybridAction = QtGui.QAction(MainWindow)
    win.dispHybridAction.setIcon(geticon("ui/actions/View/Display/Hybrid"))
    win.dispHybridAction.setCheckable(True)
    win.dispHybridAction.setObjectName("dispHybridAction")

    win.dispCylinderAction = QtGui.QAction(MainWindow)
    win.dispCylinderAction.setIcon(geticon("ui/actions/View/Display/Cylinder"))
    win.dispCylinderAction.setObjectName("dispCylinderAction")
    
    win.dispDnaCylinderAction = QtGui.QAction(MainWindow)
    win.dispDnaCylinderAction.setIcon(geticon("ui/actions/View/Display/DnaCylinder"))
    win.dispDnaCylinderAction.setObjectName("dispDnaCylinderAction")
    
    win.dispHideAction = QtGui.QAction(MainWindow)
    win.dispHideAction.setIcon(
        geticon("ui/actions/View/Display/Hide"))
    win.dispHideAction.setObjectName("dispHideAction")
    
    win.dispUnhideAction = QtGui.QAction(MainWindow)
    win.dispUnhideAction.setIcon(
        geticon("ui/actions/View/Display/Unhide"))
    win.dispUnhideAction.setObjectName("dispUnhideAction")

    # This is currently NIY. Mark 2007-12-28
    win.dispSurfaceAction = QtGui.QAction(MainWindow)
    win.dispSurfaceAction.setIcon(geticon("ui/actions/View/Display/Surface"))
    win.dispSurfaceAction.setObjectName("dispSurfaceAction")
    
    win.setViewPerspecAction = QtGui.QAction(MainWindow)
    win.setViewPerspecAction.setCheckable(True)

    win.setViewOrthoAction = QtGui.QAction(MainWindow)
    win.setViewOrthoAction.setCheckable(True)

    win.orthoPerpActionGroup = QtGui.QActionGroup(MainWindow)  
    win.orthoPerpActionGroup.setExclusive(True)
    win.orthoPerpActionGroup.addAction(win.setViewPerspecAction)
    win.orthoPerpActionGroup.addAction(win.setViewOrthoAction)

    win.viewQuteMolAction = QtGui.QAction(MainWindow)
    win.viewQuteMolAction.setIcon(geticon("ui/actions/View/Display/QuteMol"))
    win.viewQuteMolAction.setObjectName("viewQuteMolAction")

    win.viewRaytraceSceneAction = QtGui.QAction(MainWindow)
    win.viewRaytraceSceneAction.setIcon(
        geticon("ui/actions/View/Display/Raytrace_Scene"))
    win.viewRaytraceSceneAction.setObjectName("viewRaytraceSceneAction")

    win.dispSetEltable1Action = QtGui.QAction(MainWindow)
    win.dispSetEltable1Action.setObjectName("dispSetEltable1Action")

    win.dispSetEltable2Action = QtGui.QAction(MainWindow)
    win.dispSetEltable2Action.setObjectName("dispSetEltable2Action")

    win.dispResetAtomsDisplayAction = QtGui.QAction(MainWindow)
    win.dispResetAtomsDisplayAction.setObjectName("dispResetAtomsDisplayAction")

    win.dispShowInvisAtomsAction = QtGui.QAction(MainWindow)
    win.dispShowInvisAtomsAction.setObjectName("dispShowInvisAtomsAction")

    win.changeBackgroundColorAction = QtGui.QAction(MainWindow)
    win.changeBackgroundColorAction.setIcon(
        geticon("ui/actions/View/Display/Background_Color"))
    win.changeBackgroundColorAction.setObjectName("changeBackgroundColorAction")

    win.dispElementColorSettingsAction = QtGui.QAction(MainWindow)
    win.dispElementColorSettingsAction.setObjectName("dispElementColorSettingsAction")
    win.dispElementColorSettingsAction.setIcon(
        geticon("ui/actions/View/Display/Element_Color_Settings"))

    win.dispLightingAction = QtGui.QAction(MainWindow)
    win.dispLightingAction.setObjectName("dispLightingAction")

    win.viewSemiFullScreenAction = QtGui.QAction(MainWindow)
    win.viewSemiFullScreenAction.setText('Semi-Full Screen')
    win.viewSemiFullScreenAction.setCheckable(True)
    win.viewSemiFullScreenAction.setChecked(False)
    win.viewSemiFullScreenAction.setShortcut('F11')  

    win.viewFullScreenAction = QtGui.QAction(MainWindow)
    win.viewFullScreenAction.setText('Full Screen')
    win.viewFullScreenAction.setCheckable(True)
    win.viewFullScreenAction.setChecked(False)
    win.viewFullScreenAction.setShortcut('F12')
    
    win.viewReportsAction = QtGui.QAction(MainWindow)
    win.viewReportsAction.setCheckable(True)
    win.viewReportsAction.setChecked(True)
    win.viewReportsAction.setText('Reports')
    
    win.viewRulersAction = QtGui.QAction(MainWindow)
    win.viewRulersAction.setCheckable(True)
    win.viewRulersAction.setChecked(env.prefs[displayRulers_prefs_key])
    win.viewRulersAction.setText('Rulers')

    #= Insert (menu and toolbar) widgets.
    
    # Create the "Insert" menu.
    win.insertMenu = QtGui.QMenu(win.MenuBar)
    win.insertMenu.setObjectName("Insert")
    
    # Create the "Reference Geometry" menu, a submenu of the "Insert" menu.
    win.referenceGeometryMenu = QtGui.QMenu(win.insertMenu)
    win.referenceGeometryMenu.setObjectName("referenceGeometryMenu")

    win.jigsAtomSetAction = QtGui.QWidgetAction(MainWindow)
    win.jigsAtomSetAction.setIcon(geticon("ui/actions/Tools/Atom_Set"))
    win.jigsAtomSetAction.setObjectName("jigsAtomSetAction")

    win.fileInsertMmpAction = QtGui.QAction(MainWindow)
    win.fileInsertMmpAction.setObjectName("fileInsertMmpAction")
    
    win.fileInsertPdbAction = QtGui.QAction(MainWindow)
    win.fileInsertPdbAction.setObjectName("fileInsertPdbAction")

    win.partLibAction = QtGui.QAction(MainWindow)
    win.partLibAction.setObjectName("partLibAction")
    win.partLibAction.setText("Part from partlib...")    
    win.partLibAction.setIcon(geticon('ui/actions/Insert/Partlib'))

    win.insertCommentAction = QtGui.QAction(MainWindow)
    win.insertCommentAction.setIcon(geticon("ui/actions/Insert/Comment"))
    win.insertCommentAction.setObjectName("insertCommentAction")

    win.insertPovraySceneAction = QtGui.QAction(MainWindow)
    win.insertPovraySceneAction.setIcon(geticon("ui/actions/Insert/POV-Ray_Scene"))
    win.insertPovraySceneAction.setObjectName("insertPovraySceneAction")

    win.jigsGridPlaneAction = QtGui.QAction(MainWindow)
    win.jigsGridPlaneAction.setIcon(geticon("ui/actions/Insert/Reference Geometry/Grid_Plane"))
    win.jigsGridPlaneAction.setObjectName("jigsGridPlaneAction")

    win.referencePlaneAction = QtGui.QAction(MainWindow)
    win.referencePlaneAction.setIcon(geticon(
        "ui/actions/Insert/Reference Geometry/Plane"))
    win.referencePlaneAction.setObjectName("referencePlaneAction")

    win.referenceLineAction = QtGui.QAction(MainWindow)
    win.referenceLineAction.setIcon(geticon(
        "ui/actions/Insert/Reference Geometry/Plane"))
    win.referenceLineAction.setObjectName("referenceLineAction")
    win.referenceLineAction.setText("Line...")

    #= Tools (menu and toolbar) widgets.
    
    # Create the "Tools" menu.
    win.toolsMenu = QtGui.QMenu(win.MenuBar)
    win.toolsMenu.setObjectName("Tools")
    
    # Create the "Build Structures" menu, a submenu of the "Tools" menu.
    win.buildStructuresMenu = QtGui.QMenu(win.toolsMenu)
    win.buildStructuresMenu.setObjectName("buildStructuresMenu")
    
    # Create the "Build Tools" menu, a submenu of the "Tools" menu.
    win.buildToolsMenu = QtGui.QMenu(win.toolsMenu)
    win.buildToolsMenu.setObjectName("buildToolsMenu")
    
    # Create the "Dimensions" menu, a submenu of the "Tools" menu.
    win.dimensionsMenu = QtGui.QMenu(win.toolsMenu)
    win.dimensionsMenu.setObjectName("dimensionsMenu")
    
    # Create the "Selection" menu, a submenu of the "Tools" menu.
    win.selectionMenu = QtGui.QMenu(win.toolsMenu)
    win.selectionMenu.setObjectName("selectionMenu")

    win.editPrefsAction = QtGui.QWidgetAction(MainWindow)
    win.editPrefsAction.setIcon(geticon("ui/actions/Tools/Options"))
    win.editPrefsAction.setObjectName("editPrefsAction")    

    win.modifyAdjustSelAction = QtGui.QWidgetAction(MainWindow)
    win.modifyAdjustSelAction.setEnabled(True)
    win.modifyAdjustSelAction.setIcon(geticon("ui/actions/Tools/Adjust_Selection"))
    win.modifyAdjustSelAction.setObjectName("modifyAdjustSelAction")

    win.modifyAdjustAllAction = QtGui.QWidgetAction(MainWindow)
    win.modifyAdjustAllAction.setIcon(geticon("ui/actions/Tools/Adjust_All"))
    win.modifyAdjustAllAction.setObjectName("modifyAdjustAllAction")

    win.simMinimizeEnergyAction = QtGui.QWidgetAction(MainWindow)
    win.simMinimizeEnergyAction.setIcon(geticon("ui/actions/Simulation/Minimize_Energy"))
    win.simMinimizeEnergyAction.setObjectName("simMinimizeEnergyAction")

    win.toolsExtrudeAction = QtGui.QWidgetAction(MainWindow)
    win.toolsExtrudeAction.setCheckable(True)
    win.toolsExtrudeAction.setIcon(geticon("ui/actions/Insert/Features/Extrude"))

    win.toolsFuseChunksAction = QtGui.QWidgetAction(MainWindow)
    win.toolsFuseChunksAction.setCheckable(1) # make the Fuse Mode button checkable
    win.toolsFuseChunksAction.setIcon(geticon("ui/actions/Tools/Build Tools/Fuse_Chunks"))

    win.modifyMirrorAction = QtGui.QWidgetAction(MainWindow)
    win.modifyMirrorAction.setIcon(geticon("ui/actions/Tools/Build Tools/Mirror"))
    win.modifyMirrorAction.setObjectName("modifyMirrorAction")

    win.modifyInvertAction = QtGui.QWidgetAction(MainWindow)
    win.modifyInvertAction.setIcon(geticon("ui/actions/Tools/Build Tools/Invert"))
    win.modifyInvertAction.setObjectName("modifyInvertAction")

    win.modifyStretchAction = QtGui.QWidgetAction(MainWindow)
    win.modifyStretchAction.setIcon(geticon("ui/actions/Tools/Build Tools/Stretch"))
    win.modifyStretchAction.setObjectName("modifyStretchAction")

    #== "Tools > Build Structures" (menu and toolbar) widgets.
    
    win.toolsDepositAtomAction = QtGui.QWidgetAction(MainWindow)
    win.toolsDepositAtomAction.setCheckable(1) # make the build button checkable
    win.toolsDepositAtomAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/Build Atoms"))

    win.toolsCookieCutAction = QtGui.QWidgetAction(MainWindow)
    win.toolsCookieCutAction.setCheckable(1) # make the cookie button checkable
    win.toolsCookieCutAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/Build Crystal"))

    win.insertGrapheneAction = QtGui.QWidgetAction(MainWindow)
    win.insertGrapheneAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/Graphene"))
    win.insertGrapheneAction.setObjectName("insertGrapheneAction")

    win.insertNanotubeAction = QtGui.QWidgetAction(MainWindow)
    win.insertNanotubeAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/Nanotube"))
    win.insertNanotubeAction.setObjectName("insertNanotubeAction")

    win.buildDnaAction = QtGui.QWidgetAction(MainWindow)
    win.buildDnaAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/DNA"))
    win.buildDnaAction.setObjectName("buildDnaAction")

    # Atom Generator (Developer Example). Mark 2007-06-08
    win.insertAtomAction = QtGui.QWidgetAction(MainWindow)
    win.insertAtomAction.setIcon(
        geticon("ui/actions/Toolbars/Smart/Deposit_Atoms.png"))
    win.insertAtomAction.setObjectName("insertAtomAction")

    #== "Tools > Build Tools" (menu and toolbar) widgets.
    
    win.modifyHydrogenateAction = QtGui.QWidgetAction(MainWindow)
    win.modifyHydrogenateAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Hydrogenate"))
    win.modifyHydrogenateAction.setObjectName("modifyHydrogenateAction")

    win.modifyDehydrogenateAction = QtGui.QWidgetAction(MainWindow)
    win.modifyDehydrogenateAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Dehydrogenate"))
    win.modifyDehydrogenateAction.setObjectName("modifyDehydrogenateAction")

    win.modifyPassivateAction = QtGui.QWidgetAction(MainWindow)
    win.modifyPassivateAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Passivate"))
    win.modifyPassivateAction.setObjectName("modifyPassivateAction")

    win.modifyDeleteBondsAction = QtGui.QWidgetAction(MainWindow)
    win.modifyDeleteBondsAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Delete_Bonds"))
    win.modifyDeleteBondsAction.setObjectName("modifyDeleteBondsAction")      

    win.modifySeparateAction = QtGui.QWidgetAction(MainWindow)
    win.modifySeparateAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Separate"))
    win.modifySeparateAction.setObjectName("modifySeparateAction")

    win.modifyMergeAction = QtGui.QWidgetAction(MainWindow)
    win.modifyMergeAction.setIcon(geticon(
        "ui/actions/Tools/Build Tools/Combine_Chunks"))
    win.modifyMergeAction.setObjectName("modifyMergeAction")

    win.makeChunkFromSelectedAtomsAction = QtGui.QWidgetAction(MainWindow)
    win.makeChunkFromSelectedAtomsAction.setIcon(geticon(
        "ui/actions/Tools/Build Tools/New_Chunk"))
    win.makeChunkFromSelectedAtomsAction.setObjectName(
        "makeChunkFromSelectedAtomsAction")

    win.modifyAlignCommonAxisAction = QtGui.QWidgetAction(MainWindow)
    win.modifyAlignCommonAxisAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/AlignToCommonAxis"))
    win.modifyAlignCommonAxisAction.setObjectName("modifyAlignCommonAxisAction")

    win.modifyCenterCommonAxisAction = QtGui.QWidgetAction(MainWindow)
    win.modifyCenterCommonAxisAction.setObjectName(
        "modifyCenterCommonAxisAction")

    #= "Tools > Dimensions" (menu and toolbar) widgets.
    
    win.jigsDistanceAction = QtGui.QWidgetAction(MainWindow)
    win.jigsDistanceAction.setIcon(geticon("ui/actions/Tools/Dimensions/Measure_Distance"))
    win.jigsDistanceAction.setObjectName("jigsDistanceAction")

    win.jigsAngleAction = QtGui.QWidgetAction(MainWindow)
    win.jigsAngleAction.setIcon(geticon("ui/actions/Tools/Dimensions/Measure_Angle"))
    win.jigsAngleAction.setObjectName("jigsAngleAction")

    win.jigsDihedralAction = QtGui.QWidgetAction(MainWindow)
    win.jigsDihedralAction.setIcon(geticon("ui/actions/Tools/Dimensions/Measure_Dihedral"))
    win.jigsDihedralAction.setObjectName("jigsDihedralAction")

    #= "Tools > Select" (menu and toolbar) widgets.
    
    win.selectAllAction = QtGui.QAction(MainWindow)
    win.selectAllAction.setEnabled(True)
    win.selectAllAction.setIcon(
        geticon("ui/actions/Tools/Select/Select_All"))
    win.selectAllAction.setObjectName("selectAllAction")

    win.selectNoneAction = QtGui.QAction(MainWindow)
    win.selectNoneAction.setIcon(
        geticon("ui/actions/Tools/Select/Select_None"))
    win.selectNoneAction.setObjectName("selectNoneAction")

    win.selectInvertAction = QtGui.QAction(MainWindow)
    win.selectInvertAction.setIcon(
        geticon("ui/actions/Tools/Select/Select_Invert"))
    win.selectInvertAction.setObjectName("selectInvertAction")

    win.selectConnectedAction = QtGui.QAction(MainWindow)
    win.selectConnectedAction.setIcon(
        geticon("ui/actions/Tools/Select/Select_Connected"))
    win.selectConnectedAction.setObjectName("selectConnectedAction")

    win.selectDoublyAction = QtGui.QAction(MainWindow)
    win.selectDoublyAction.setIcon(
        geticon("ui/actions/Tools/Select/Select_Doubly"))
    win.selectDoublyAction.setObjectName("selectDoublyAction")

    win.selectExpandAction = QtGui.QAction(MainWindow)
    win.selectExpandAction.setIcon(
        geticon("ui/actions/Tools/Select/Expand"))
    win.selectExpandAction.setObjectName("selectExpandAction")

    win.selectContractAction = QtGui.QAction(MainWindow)
    win.selectContractAction.setIcon(
        geticon("ui/actions/Tools/Select/Contract"))
    win.selectContractAction.setObjectName("selectContractAction")

    #= "Simulation" (menu and toolbar) widgets.
    
    # Create the "Simulation" menu
    win.simulationMenu = QtGui.QMenu(win.MenuBar)
    win.simulationMenu.setObjectName("simulationMenu")
    
    # Create the "Measurements" menu. #@ Not used??? MAS
    win.measurementsMenu = QtGui.QMenu()
    win.measurementsMenu.setObjectName("measurementsMenu")
    win.measurementsMenu.setIcon(geticon(
        "ui/actions/Toolbars/Smart/Dimension"))
    
    win.simSetupAction = QtGui.QWidgetAction(MainWindow)
    win.simSetupAction.setCheckable(True)
    win.simSetupAction.setChecked(False)
    win.simSetupAction.setEnabled(True)
    win.simSetupAction.setIcon(geticon("ui/actions/Simulation/Run_Dynamics"))
    win.simSetupAction.setObjectName("simSetupAction")

    win.simMoviePlayerAction = QtGui.QWidgetAction(MainWindow)
    win.simMoviePlayerAction.setIcon(
        geticon("ui/actions/Simulation/Play_Movie"))

    win.simPlotToolAction = QtGui.QWidgetAction(MainWindow)
    win.simPlotToolAction.setEnabled(True)
    win.simPlotToolAction.setIcon(geticon("ui/actions/Simulation/Make_Graphs"))
    win.simPlotToolAction.setObjectName("simPlotToolAction")

    win.jigsMotorAction = QtGui.QWidgetAction(MainWindow)
    win.jigsMotorAction.setIcon(geticon("ui/actions/Simulation/Rotary_Motor"))
    win.jigsMotorAction.setObjectName("jigsMotorAction")

    win.jigsLinearMotorAction = QtGui.QWidgetAction(MainWindow)
    win.jigsLinearMotorAction.setIcon(
        geticon("ui/actions/Simulation/Linear_Motor"))
    win.jigsLinearMotorAction.setObjectName("jigsLinearMotorAction")

    win.jigsStatAction = QtGui.QWidgetAction(MainWindow)
    win.jigsStatAction.setIcon(geticon("ui/actions/Simulation/Thermostat"))
    win.jigsStatAction.setObjectName("jigsStatAction")

    win.jigsThermoAction = QtGui.QWidgetAction(MainWindow)
    win.jigsThermoAction.setIcon(
        geticon("ui/actions/Simulation/Measurements/Thermometer"))
    win.jigsThermoAction.setObjectName("jigsThermoAction")

    win.jigsAnchorAction = QtGui.QWidgetAction(MainWindow)
    win.jigsAnchorAction.setIcon(geticon("ui/actions/Simulation/Anchor"))
    win.jigsAnchorAction.setObjectName("jigsAnchorAction")
    
    win.simulationJigsAction = QtGui.QAction(win)
    win.simulationJigsAction.setIcon(
        geticon("ui/actions/Simulation/Simulation_Jigs.png"))
    win.simulationJigsAction.setObjectName("simulationJigsAction")

    win.jigsGamessAction = QtGui.QWidgetAction(MainWindow)
    win.jigsGamessAction.setEnabled(True)
    win.jigsGamessAction.setIcon(geticon("ui/actions/Simulation/GAMESS"))
    win.jigsGamessAction.setObjectName("jigsGamessAction")

    win.jigsESPImageAction = QtGui.QWidgetAction(MainWindow)
    win.jigsESPImageAction.setIcon(geticon("ui/actions/Simulation/ESP_Image"))
    win.jigsESPImageAction.setObjectName("jigsESPImageAction")

    # This only shows up if the user enables the NH1 plugin (via Preferences)
    # which is hidden since NH1 doesn't work with NE1.
    # See UserPrefs.enable_nanohive().
    win.simNanoHiveAction = QtGui.QAction(MainWindow)
    win.simNanoHiveAction.setVisible(False)
    win.simNanoHiveAction.setObjectName("simNanoHiveAction")

    #= "Help" (menu and toolbar) widgets.

    win.helpMenu = QtGui.QMenu(win.MenuBar)
    win.helpMenu.setObjectName("helpMenu")
    
    win.helpMouseControlsAction = QtGui.QAction(MainWindow)
    win.helpMouseControlsAction.setObjectName("helpMouseControlsAction")

    win.helpKeyboardShortcutsAction = QtGui.QAction(MainWindow)
    win.helpKeyboardShortcutsAction.setObjectName("helpKeyboardShortcutsAction")

    win.helpGraphicsCardAction = QtGui.QAction(MainWindow)
    win.helpGraphicsCardAction.setObjectName("helpGraphicsCardAction")

    win.helpWhatsThisAction = QtGui.QAction(MainWindow)
    win.helpWhatsThisAction.setIcon(geticon("ui/actions/Help/WhatsThis"))
    win.helpWhatsThisAction.setObjectName("helpWhatsThisAction")

    win.helpAboutAction = QtGui.QAction(MainWindow)
    win.helpAboutAction.setObjectName("helpAboutAction")
    
    #= Widgets for toolbars
    
    # "Standard" toolbar widgets.
    
    # Action items from the Tools menu  @@@ninad061110
    # Not decided whether select chunks and move chunks options
    # will be a part of Tools Menu
    
    win.toolsSelectMoleculesAction = QtGui.QAction(MainWindow)
    win.toolsSelectMoleculesAction.setCheckable(1) # make the select chunks button checkable
    win.toolsSelectMoleculesAction.setIcon(geticon("ui/actions/Toolbars/Standard/Select_Chunks"))
    
    # Define an action grop for move molecules (translate and rotate components)
    # actions ...to make them mutually exclusive. 
    # -- ninad 070309
    win.toolsMoveRotateActionGroup = QtGui.QActionGroup(MainWindow)
    win.toolsMoveRotateActionGroup.setExclusive(True)
    
    win.toolsMoveMoleculeAction = QtGui.QWidgetAction(win.toolsMoveRotateActionGroup)
    win.toolsMoveMoleculeAction.setCheckable(1) # make the Move mode button checkable
    win.toolsMoveMoleculeAction.setIcon(geticon("ui/actions/Toolbars/Standard/Move_Chunks"))
       
    win.rotateComponentsAction = QtGui.QWidgetAction(win.toolsMoveRotateActionGroup)
    win.rotateComponentsAction.setCheckable(1) # make the Move mode button checkable
    win.rotateComponentsAction.setIcon(geticon("ui/actions/Toolbars/Standard/Rotate_Components"))

    #= "View" toolbars.
    
    # Create "Standard Views" dropdown menu for the "View" toolbar.
    win.standardViewsMenu = QtGui.QMenu("Standard Views")

    # Populate the "Standard Views" menu.
    win.standardViewsMenu.addAction(win.viewFrontAction)
    win.standardViewsMenu.addAction(win.viewBackAction)
    win.standardViewsMenu.addAction(win.viewLeftAction)
    win.standardViewsMenu.addAction(win.viewRightAction)
    win.standardViewsMenu.addAction(win.viewTopAction)
    win.standardViewsMenu.addAction(win.viewBottomAction)
    win.standardViewsMenu.addAction(win.viewIsometricAction)
    
    win.standardViewsAction = QtGui.QWidgetAction(MainWindow)
    win.standardViewsAction.setEnabled(True)
    win.standardViewsAction.setIcon(geticon("ui/actions/View/Standard_Views"))
    win.standardViewsAction.setObjectName("standardViews")
    win.standardViewsAction.setText("Standard Views")
    win.standardViewsAction.setMenu(win.standardViewsMenu)

    win.standardViews_btn = QtGui.QToolButton()            
    win.standardViews_btn.setPopupMode(QToolButton.MenuButtonPopup)
    win.standardViewsAction.setDefaultWidget(win.standardViews_btn)
    win.standardViews_btn.setDefaultAction(win.standardViewsAction)

    # Miscellaneous QActions.
    
    # These QActions are used in Cookie (Crystal) and should be moved
    # to one of those file(s). To do for Mark. mark 2007-12-23
    win.DefaultSelAction = QtGui.QAction(MainWindow)
    win.LassoSelAction = QtGui.QAction(MainWindow)
    win.RectCornerSelAction = QtGui.QAction(MainWindow)
    win.RectCtrSelAction = QtGui.QAction(MainWindow)
    win.SquareSelAction = QtGui.QAction(MainWindow)
    win.TriangleSelAction = QtGui.QAction(MainWindow)
    win.DiamondSelAction = QtGui.QAction(MainWindow)
    win.CircleSelAction = QtGui.QAction(MainWindow)
    win.HexagonSelAction = QtGui.QAction(MainWindow)

    # This needs to stay until I talk with Bruce about UpdateDashboard(),
    # which calls a method of toolsDoneAction in Command.py. Mark 2007-12-20
    win.toolsDoneAction = QtGui.QAction(MainWindow)
    win.toolsDoneAction.setIcon(geticon(
        "ui/actions/Properties Manager/Done"))
    win.toolsDoneAction.setObjectName("toolsDoneAction")
    
    # Dock widgets
    from Ui_ReportsDockWidget import Ui_ReportsDockWidget
    win.reportsDockWidget = Ui_ReportsDockWidget(win)

def retranslateUi(win):
    """
    Sets text related attributes for all main window QAction widgets.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    """
    This function centralizes and sets UI text for main window QAction widgets
    for the purpose of making it easier for the programmer to translate the 
    UI into other languages using Qt Linguist.

    @param MainWindow: The main window
    @type  MainWindow: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}

    @see: U{B{The Qt Linquist Manual}<http://doc.trolltech.com/4/linguist-manual.html>}
    """

    #= File (menu and toolbar) actions.
    win.fileOpenAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Open...", None, QtGui.QApplication.UnicodeUTF8))
    win.fileOpenAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
    win.fileOpenAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
    win.fileCloseAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Close and begin new model", None, QtGui.QApplication.UnicodeUTF8))
    win.fileCloseAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Close", None, QtGui.QApplication.UnicodeUTF8))
    win.fileSaveAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Save", None, QtGui.QApplication.UnicodeUTF8))
    win.fileSaveAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
    win.fileSaveAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
    win.fileSaveAsAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Save &As...", None, QtGui.QApplication.UnicodeUTF8))
    win.fileSaveAsAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Save As", None, QtGui.QApplication.UnicodeUTF8))
    win.fileImportOpenBabelAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Open Babel import...", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fileImportOpenBabelAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Open Babel", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fileImportOpenBabelAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Open Babel import", None, QtGui.QApplication.UnicodeUTF8))
    
    win.fileExportPdbAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Protein Data Bank...", 
            None, QtGui.QApplication.UnicodeUTF8))
    
    win.fileExportJpgAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "JPEG image...", 
            None, QtGui.QApplication.UnicodeUTF8))
    
    win.fileExportPngAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "PNG image...", 
            None, QtGui.QApplication.UnicodeUTF8))
    
    win.fileExportPovAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "POV-Ray...", 
            None, QtGui.QApplication.UnicodeUTF8))
    
    win.fileExportAmdlAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Animation Master Model...", 
            None, QtGui.QApplication.UnicodeUTF8))
    
    win.fileExportOpenBabelAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Open Babel export...", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fileExportOpenBabelAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Open Babel", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fileExportOpenBabelAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Open Babel export", None, QtGui.QApplication.UnicodeUTF8))        
    win.fileExitAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "E&xit", None, QtGui.QApplication.UnicodeUTF8))
    win.fileExitAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))

    #= Edit (menu and toolbar) actions.
    win.editUndoAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Undo",
            None, QtGui.QApplication.UnicodeUTF8))
    win.editUndoAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Undo",
            None, QtGui.QApplication.UnicodeUTF8))
    win.editUndoAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Ctrl+Z", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRedoAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Redo", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRedoAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Redo", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRedoAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Ctrl+Y", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editCutAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Cut", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editCutAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Cut", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editCutAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Ctrl+X", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editCopyAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "C&opy", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editCopyAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Copy", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editCopyAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Ctrl+C", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editPasteAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Paste", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editPasteAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Paste", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editPasteAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Ctrl+V", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editDeleteAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Delete",
            None, QtGui.QApplication.UnicodeUTF8))
    win.editDeleteAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Delete", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editDeleteAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Delete (Del)", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editDeleteAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Del", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editMakeCheckpointAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Make Checkpoint", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editAutoCheckpointingAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Automatic Checkpointing", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editClearUndoStackAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Clear Undo Stack", 
            None, QtGui.QApplication.UnicodeUTF8))    
    win.dispObjectColorAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Change Color...", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.dispObjectColorAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Change Color", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.dispObjectColorAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Change Color", 
            None, QtGui.QApplication.UnicodeUTF8))

    #= View (menu and toolbar) actions.
    win.viewOrientationAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Orientation...", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.viewOrientationAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Space", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.setViewFitToWindowAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Zoom to Fit", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.setViewFitToWindowAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Zoom to Fit", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.setViewFitToWindowAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Zoom to Fit (Ctrl+F)", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.setViewFitToWindowAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Ctrl+F", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.zoomToAreaAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Zoom to Area", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.zoomToAreaAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Zoom to Area", 
            None, QtGui.QApplication.UnicodeUTF8))
    
    win.viewZoomAboutScreenCenterAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Zoom About Screen Center", 
            None, QtGui.QApplication.UnicodeUTF8))

    win.setViewZoomtoSelectionAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Zoom To Selection", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.setViewZoomtoSelectionAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Zoom To Selection", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.setViewZoomtoSelectionAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Zoom to Selection",
            None, QtGui.QApplication.UnicodeUTF8))
    
    win.zoomInOutAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Zoom",
            None, QtGui.QApplication.UnicodeUTF8))
    win.zoomInOutAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Zoom", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.zoomInOutAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Zoom",
            None, QtGui.QApplication.UnicodeUTF8))

    win.panToolAction.setText(QtGui.QApplication.translate("MainWindow", "&Pan", None, QtGui.QApplication.UnicodeUTF8))
    win.panToolAction.setIconText(QtGui.QApplication.translate("MainWindow", "Pan ", None, QtGui.QApplication.UnicodeUTF8))
    win.rotateToolAction.setText(QtGui.QApplication.translate("MainWindow", "Rotate", None, QtGui.QApplication.UnicodeUTF8))
    win.rotateToolAction.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeAction.setText(QtGui.QApplication.translate("MainWindow", "&Home", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeAction.setIconText(QtGui.QApplication.translate("MainWindow", "Home", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Home View (Home)", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Home", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewRecenterAction.setText(QtGui.QApplication.translate("MainWindow", "&Recenter", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewRecenterAction.setIconText(QtGui.QApplication.translate("MainWindow", "Recenter", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewRecenterAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Recenter (Ctrl+R)", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewRecenterAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+R", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeToCurrentAction.setText(QtGui.QApplication.translate("MainWindow", "Set Home View", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeToCurrentAction.setIconText(QtGui.QApplication.translate("MainWindow", "Set Home View", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeToCurrentAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Set Home View (Ctrl+Home)", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeToCurrentAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Home", None, QtGui.QApplication.UnicodeUTF8))
    win.saveNamedViewAction.setText(QtGui.QApplication.translate("MainWindow", "Save Named View", None, QtGui.QApplication.UnicodeUTF8))
    win.saveNamedViewAction.setIconText(QtGui.QApplication.translate("MainWindow", "Save Named View", None, QtGui.QApplication.UnicodeUTF8))

    #VIEW > DISPLAY MENU ITEMS
    win.dispBallAction.setText(QtGui.QApplication.translate("MainWindow", "Ball and Stick", None, QtGui.QApplication.UnicodeUTF8))
    win.dispBallAction.setIconText(QtGui.QApplication.translate("MainWindow", "Ball and Stick", None, QtGui.QApplication.UnicodeUTF8))
    win.dispDefaultAction.setText(QtGui.QApplication.translate("MainWindow", "Default", None, QtGui.QApplication.UnicodeUTF8))
    win.dispDefaultAction.setIconText(QtGui.QApplication.translate("MainWindow", "Default", None, QtGui.QApplication.UnicodeUTF8))

    win.dispInvisAction.setText(QtGui.QApplication.translate("MainWindow", "Invisible", None, QtGui.QApplication.UnicodeUTF8))
    win.dispInvisAction.setIconText(QtGui.QApplication.translate("MainWindow", "Invisible", None, QtGui.QApplication.UnicodeUTF8))
    win.dispLinesAction.setText(QtGui.QApplication.translate("MainWindow", "Lines", None, QtGui.QApplication.UnicodeUTF8))
    win.dispLinesAction.setIconText(QtGui.QApplication.translate("MainWindow", "Lines", None, QtGui.QApplication.UnicodeUTF8))
    win.dispTubesAction.setText(QtGui.QApplication.translate("MainWindow", "Tubes", None, QtGui.QApplication.UnicodeUTF8))
    win.dispTubesAction.setIconText(QtGui.QApplication.translate("MainWindow", "Tubes", None, QtGui.QApplication.UnicodeUTF8))
    win.dispCPKAction.setText(QtGui.QApplication.translate("MainWindow", "CPK", None, QtGui.QApplication.UnicodeUTF8))
    win.dispCPKAction.setIconText(QtGui.QApplication.translate("MainWindow", "CPK", None, QtGui.QApplication.UnicodeUTF8))
    win.dispHybridAction.setText(QtGui.QApplication.translate("MainWindow", "Hybrid Display", None, QtGui.QApplication.UnicodeUTF8))
    win.dispHybridAction.setIconText(QtGui.QApplication.translate("MainWindow", "Hybrid", None, QtGui.QApplication.UnicodeUTF8))
    win.dispSurfaceAction.setIconText(QtGui.QApplication.translate("MainWindow", "Surface", None, QtGui.QApplication.UnicodeUTF8))
    win.dispCylinderAction.setIconText(QtGui.QApplication.translate("MainWindow", "Cylinder", None, QtGui.QApplication.UnicodeUTF8))
    win.dispDnaCylinderAction.setIconText(QtGui.QApplication.translate("MainWindow", "DNA Cylinder", None, QtGui.QApplication.UnicodeUTF8))
    win.dispHideAction.setIconText(QtGui.QApplication.translate("MainWindow", "Hide", None, QtGui.QApplication.UnicodeUTF8))
    win.dispHideAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Hide (Ctrl+H)", None, QtGui.QApplication.UnicodeUTF8))
    win.dispHideAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+H", None, QtGui.QApplication.UnicodeUTF8))
    win.dispUnhideAction.setIconText(QtGui.QApplication.translate("MainWindow", "Unhide", None, QtGui.QApplication.UnicodeUTF8))
    win.dispUnhideAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Unhide (Ctrl+Shift+H)", None, QtGui.QApplication.UnicodeUTF8))
    win.dispUnhideAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+H", None, QtGui.QApplication.UnicodeUTF8))

    # FOLLOWING VIEW MENU ITEMS NEED SORTING
    win.viewFrontAction.setText(QtGui.QApplication.translate("MainWindow", "&Front", None, QtGui.QApplication.UnicodeUTF8))
    win.viewFrontAction.setIconText(QtGui.QApplication.translate("MainWindow", "Front", None, QtGui.QApplication.UnicodeUTF8))
    win.viewFrontAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Front View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBackAction.setText(QtGui.QApplication.translate("MainWindow", "&Back", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBackAction.setIconText(QtGui.QApplication.translate("MainWindow", "Back", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBackAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Back View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewTopAction.setText(QtGui.QApplication.translate("MainWindow", "&Top", None, QtGui.QApplication.UnicodeUTF8))
    win.viewTopAction.setIconText(QtGui.QApplication.translate("MainWindow", "Top", None, QtGui.QApplication.UnicodeUTF8))
    win.viewTopAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Top View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBottomAction.setText(QtGui.QApplication.translate("MainWindow", "Botto&m", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBottomAction.setIconText(QtGui.QApplication.translate("MainWindow", "Bottom", None, QtGui.QApplication.UnicodeUTF8))
    win.viewBottomAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Bottom View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRightAction.setText(QtGui.QApplication.translate("MainWindow", "&Right", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRightAction.setIconText(QtGui.QApplication.translate("MainWindow", "Right", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRightAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Right View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRightAction.setStatusTip(QtGui.QApplication.translate("MainWindow", "Right View", None, QtGui.QApplication.UnicodeUTF8))
    win.viewLeftAction.setText(QtGui.QApplication.translate("MainWindow", "&Left", None, QtGui.QApplication.UnicodeUTF8))
    win.viewLeftAction.setIconText(QtGui.QApplication.translate("MainWindow", "Left", None, QtGui.QApplication.UnicodeUTF8))
    win.viewLeftAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Left View", None, QtGui.QApplication.UnicodeUTF8))

    win.viewRotate180Action.setText(QtGui.QApplication.translate("MainWindow", "Rotate View 180", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRotate180Action.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate View 180", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRotate180Action.setToolTip(QtGui.QApplication.translate("MainWindow", "Rotate View 180", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRotate180Action.setStatusTip(QtGui.QApplication.translate("MainWindow", "Rotate View 180", None, QtGui.QApplication.UnicodeUTF8))
    win.viewIsometricAction.setText(QtGui.QApplication.translate("MainWindow", "&Isometric", None, QtGui.QApplication.UnicodeUTF8))
    win.viewIsometricAction.setIconText(QtGui.QApplication.translate("MainWindow", "Isometric", None, QtGui.QApplication.UnicodeUTF8))
    win.resetChunkColorAction.setText(QtGui.QApplication.translate("MainWindow", "&Reset Chunk Color", None, QtGui.QApplication.UnicodeUTF8))
    win.resetChunkColorAction.setIconText(QtGui.QApplication.translate("MainWindow", "Reset Chunk Color", None, QtGui.QApplication.UnicodeUTF8))

    #= Insert (menu and toolbar) actions.
    win.jigsAtomSetAction.setIconText(QtGui.QApplication.translate(
        "MainWindow",  "Atom Set",  None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertMmpAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Molecular Machine Part file...", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertMmpAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Insert MMP", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertMmpAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Insert MMP file", 
        None, QtGui.QApplication.UnicodeUTF8))
    
    win.fileInsertPdbAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Protein Data Bank file...", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertPdbAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Insert PDB", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertPdbAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Insert PDB file", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.insertCommentAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Comment", 
        None,  QtGui.QApplication.UnicodeUTF8))

    win.insertPovraySceneAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "POV-Ray Scene", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.insertPovraySceneAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Insert POV-Ray Scene file", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.jigsGridPlaneAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Grid Plane...", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.referencePlaneAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Plane...", 
        None, QtGui.QApplication.UnicodeUTF8))

    #= Tools (menu and toolbar) actions.
    win.modifyAdjustSelAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Adjust Selection",
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.modifyAdjustSelAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Adjust Selection",
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.modifyAdjustSelAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Adjust Selection",
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.modifyAdjustAllAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Adjust All",
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.modifyAdjustAllAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Adjust All", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.simMinimizeEnergyAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Minimize Energy", 
        None, 
        QtGui.QApplication.UnicodeUTF8))    

    win.toolsExtrudeAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Extrude",
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.toolsFuseChunksAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Fuse",
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.toolsFuseChunksAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Fuse Chunks", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.toolsExtrudeAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Extrude", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.editPrefsAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Preferences...", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.modifyMirrorAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Mirror", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.modifyMirrorAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Mirror Chunks",
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.modifyInvertAction.setText(QtGui.QApplication.translate(
        "MainWindow", "&Invert", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.modifyInvertAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Invert",
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.editPrefsAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Preferences...", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    win.editPrefsAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Preferences", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    #= Tools > Build Structures (menu and toolbar) actions.
    win.toolsDepositAtomAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Atoms", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.toolsDepositAtomAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Build Atoms", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.toolsCookieCutAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Crystal",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.toolsCookieCutAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Build Crystal",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.insertNanotubeAction.setIconText(QtGui.QApplication.translate(
        "MainWindow",
        "Nanotube",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.insertNanotubeAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Build Nanotube", 
        None,
        QtGui.QApplication.UnicodeUTF8))
    win.insertGrapheneAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Graphene", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.insertGrapheneAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Build Graphene Sheet", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.buildDnaAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "DNA", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.buildDnaAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "DNA",
        None,
        QtGui.QApplication.UnicodeUTF8))
    win.buildDnaAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow",
        "Build DNA", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    # Atom Generator example for developers. Mark and Jeff. 2007-06-13
    #@ Jeff - add a link to the public wiki page when ready. Mark 2007-06-13.
    win.insertAtomAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Atom", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.insertAtomAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Atom Generator (Developer Example)", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    #= "Tools > Build Tools" (menu and toolbar) actions.

    win.modifyHydrogenateAction.setText(QtGui.QApplication.translate("MainWindow", "&Hydrogenate", 
                                                                     None, QtGui.QApplication.UnicodeUTF8))
    win.modifyHydrogenateAction.setIconText(QtGui.QApplication.translate("MainWindow", "Hydrogenate", 
                                                                         None, QtGui.QApplication.UnicodeUTF8))
    win.modifyHydrogenateAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Hydrogenate", 
                                                                        None, QtGui.QApplication.UnicodeUTF8))
    win.modifyDehydrogenateAction.setText(QtGui.QApplication.translate("MainWindow", "&Dehydrogenate", 
                                                                       None, QtGui.QApplication.UnicodeUTF8))
    win.modifyDehydrogenateAction.setIconText(QtGui.QApplication.translate("MainWindow", "Dehydrogenate", 
                                                                           None, QtGui.QApplication.UnicodeUTF8))
    win.modifyPassivateAction.setText(QtGui.QApplication.translate("MainWindow", "&Passivate", 
                                                                   None, QtGui.QApplication.UnicodeUTF8))
    win.modifyPassivateAction.setIconText(QtGui.QApplication.translate("MainWindow", "Passivate", 
                                                                       None, QtGui.QApplication.UnicodeUTF8))
    win.modifyPassivateAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Passivate (Ctrl+P)",
                                                                      None, QtGui.QApplication.UnicodeUTF8))
    win.modifyPassivateAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+P", 
                                                                       None, QtGui.QApplication.UnicodeUTF8))
    win.modifyDeleteBondsAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Cut &Bonds",None, QtGui.QApplication.UnicodeUTF8))
    win.modifyDeleteBondsAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Cut Bonds",None, QtGui.QApplication.UnicodeUTF8))
    win.modifyMergeAction.setText(QtGui.QApplication.translate(
        "MainWindow","Combine",None,QtGui.QApplication.UnicodeUTF8))

    win.modifyMergeAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow","Combine Selected Chunks",None, 
        QtGui.QApplication.UnicodeUTF8))

    win.makeChunkFromSelectedAtomsAction.setText(QtGui.QApplication.translate(
        "MainWindow","New Chunk",None,QtGui.QApplication.UnicodeUTF8))

    win.makeChunkFromSelectedAtomsAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow","Create a new chunk for selected atoms",None, 
        QtGui.QApplication.UnicodeUTF8))

    win.modifySeparateAction.setText(QtGui.QApplication.translate(
        "MainWindow",  "&Separate", None,QtGui.QApplication.UnicodeUTF8))
    win.modifySeparateAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Separate", None, QtGui.QApplication.UnicodeUTF8))
    win.modifyAlignCommonAxisAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Align to &Common Axis",None, 
        QtGui.QApplication.UnicodeUTF8))
    win.modifyAlignCommonAxisAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Align to Common Axis",None, 
        QtGui.QApplication.UnicodeUTF8))
    win.modifyCenterCommonAxisAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Center on Common Axis",None,
        QtGui.QApplication.UnicodeUTF8))

    #TOOLS > DIMENSIONS MENU
    win.jigsDistanceAction.setText(QtGui.QApplication.translate("MainWindow", "Measure Distance", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsDistanceAction.setIconText(QtGui.QApplication.translate("MainWindow", "Measure Distance", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsAngleAction.setText(QtGui.QApplication.translate("MainWindow", "Measure Angle", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsAngleAction.setIconText(QtGui.QApplication.translate("MainWindow", "Measure Angle", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsDihedralAction.setText(QtGui.QApplication.translate("MainWindow", "Measure Dihedral", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsDihedralAction.setIconText(QtGui.QApplication.translate("MainWindow", "Measure Dihedral", None, QtGui.QApplication.UnicodeUTF8))

    #TOOLS > SELECT  MENU ITEMS
    win.selectAllAction.setText(QtGui.QApplication.translate("MainWindow", "&All", None, QtGui.QApplication.UnicodeUTF8))
    win.selectAllAction.setIconText(QtGui.QApplication.translate("MainWindow", "All", None, QtGui.QApplication.UnicodeUTF8))
    win.selectAllAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select All", None, QtGui.QApplication.UnicodeUTF8))
    win.selectAllAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+A", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setText(QtGui.QApplication.translate("MainWindow", "&None", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setIconText(QtGui.QApplication.translate("MainWindow", "None", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select None", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setText(QtGui.QApplication.translate("MainWindow", "&Invert", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setIconText(QtGui.QApplication.translate("MainWindow", "Invert", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select Invert", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+I", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setText(QtGui.QApplication.translate("MainWindow", "&Connected", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setIconText(QtGui.QApplication.translate("MainWindow", "Connected", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select Connected", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+C", None, QtGui.QApplication.UnicodeUTF8))
    win.selectDoublyAction.setText(QtGui.QApplication.translate("MainWindow", "&Doubly", None, QtGui.QApplication.UnicodeUTF8))
    win.selectDoublyAction.setIconText(QtGui.QApplication.translate("MainWindow", "Doubly", None, QtGui.QApplication.UnicodeUTF8))
    win.selectDoublyAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select Doubly", None, QtGui.QApplication.UnicodeUTF8))
    win.selectExpandAction.setIconText(QtGui.QApplication.translate("MainWindow", "Expand", None, QtGui.QApplication.UnicodeUTF8))
    win.selectExpandAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Expand Selection (Ctrl+D)", None, QtGui.QApplication.UnicodeUTF8))
    win.selectExpandAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+D", None, QtGui.QApplication.UnicodeUTF8))
    win.selectContractAction.setIconText(QtGui.QApplication.translate("MainWindow", "Contract", None, QtGui.QApplication.UnicodeUTF8))
    win.selectContractAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Contract Selection (Ctrl+Shift+D)", None, QtGui.QApplication.UnicodeUTF8))
    win.selectContractAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+D", None, QtGui.QApplication.UnicodeUTF8))
    
    #= "Simulation" (menu and toolbar) actions.
    win.simSetupAction.setText(QtGui.QApplication.translate(
        "MainWindow", " Run Dynamics...", None, QtGui.QApplication.UnicodeUTF8))
    win.simSetupAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Run Dynamics", None, QtGui.QApplication.UnicodeUTF8))
    win.simSetupAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Run Dynamics", None, QtGui.QApplication.UnicodeUTF8))
    win.simMoviePlayerAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Play Movie",None, QtGui.QApplication.UnicodeUTF8))
    win.simMoviePlayerAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Play Movie",None, QtGui.QApplication.UnicodeUTF8))    
    win.simPlotToolAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Graphs...", None, QtGui.QApplication.UnicodeUTF8))
    win.simPlotToolAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Graphs", None, QtGui.QApplication.UnicodeUTF8))    
    win.jigsESPImageAction.setText(QtGui.QApplication.translate(
        "MainWindow", "ESP Image", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsESPImageAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "ESP Image", None, QtGui.QApplication.UnicodeUTF8))
    win.simulationJigsAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Simulation Jigs", None, QtGui.QApplication.UnicodeUTF8))

    import sys
    if sys.platform == "win32":
        gms_str = "PC GAMESS"
    else:
        gms_str = "GAMESS"

    win.jigsGamessAction.setText(QtGui.QApplication.translate(
        "MainWindow", gms_str, None, QtGui.QApplication.UnicodeUTF8))
    win.jigsGamessAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", gms_str, None, QtGui.QApplication.UnicodeUTF8))

    # Simulation Jigs 
    win.jigsLinearMotorAction.setText(QtGui.QApplication.translate(
        "MainWindow", "&Linear Motor", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsLinearMotorAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Linear Motor", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsStatAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Thermo&stat", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsStatAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Thermostat", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsAnchorAction.setText(QtGui.QApplication.translate(
        "MainWindow", "&Anchor", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsAnchorAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Anchor", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsMotorAction.setText(QtGui.QApplication.translate(
        "MainWindow", "&Rotary Motor", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsMotorAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Rotary Motor", None, QtGui.QApplication.UnicodeUTF8))

    #= "Simuation > Measurements" (menu and toolbar) actions.
    win.jigsThermoAction.setText(QtGui.QApplication.translate(
        "MainWindow", "&Thermometer", None, QtGui.QApplication.UnicodeUTF8))
    win.jigsThermoAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Thermometer", None, QtGui.QApplication.UnicodeUTF8))

    #= "Help" (menu and toolbar) actions.
    win.helpAboutAction.setText(QtGui.QApplication.translate("MainWindow", "&About NanoEngineer-1", None, QtGui.QApplication.UnicodeUTF8))
    win.helpAboutAction.setIconText(QtGui.QApplication.translate("MainWindow", "About NanoEngineer-1", None, QtGui.QApplication.UnicodeUTF8))

    win.helpWhatsThisAction.setText(QtGui.QApplication.translate("MainWindow", "What\'s This", None, QtGui.QApplication.UnicodeUTF8))
    win.helpWhatsThisAction.setIconText(QtGui.QApplication.translate("MainWindow", "What\'s This", None, QtGui.QApplication.UnicodeUTF8))
    win.helpGraphicsCardAction.setText(QtGui.QApplication.translate("MainWindow", "Graphics Card Info...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpGraphicsCardAction.setIconText(QtGui.QApplication.translate("MainWindow", "Graphics Card Info", None, QtGui.QApplication.UnicodeUTF8))

    win.helpMouseControlsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Mouse Controls...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpMouseControlsAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Mouse Controls", None, QtGui.QApplication.UnicodeUTF8))
    win.helpKeyboardShortcutsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Keyboard Shortcuts...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpKeyboardShortcutsAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Keyboard Shortcuts", None, QtGui.QApplication.UnicodeUTF8))

    # Other QActions not used in menus. These QActions are used in toolbars,
    # context menus, etc.
    win.viewDefviewAction.setText(QtGui.QApplication.translate("MainWindow", "Orientations", None, QtGui.QApplication.UnicodeUTF8))
    win.viewDefviewAction.setIconText(QtGui.QApplication.translate("MainWindow", "Orientations", None, QtGui.QApplication.UnicodeUTF8))
    win.viewDefviewAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Default Views", None, QtGui.QApplication.UnicodeUTF8))
    win.changeBackgroundColorAction.setText(QtGui.QApplication.translate("MainWindow", "&Background Color...", None, QtGui.QApplication.UnicodeUTF8))
    win.changeBackgroundColorAction.setIconText(QtGui.QApplication.translate("MainWindow", "Background Color...", None, QtGui.QApplication.UnicodeUTF8))

    win.toolsDoneAction.setText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))
    win.toolsDoneAction.setIconText(QtGui.QApplication.translate("MainWindow", "Done", None, QtGui.QApplication.UnicodeUTF8))

    win.modifyStretchAction.setText(QtGui.QApplication.translate("MainWindow", "S&tretch", None, QtGui.QApplication.UnicodeUTF8))
    win.modifyStretchAction.setIconText(QtGui.QApplication.translate("MainWindow", "Stretch", None, QtGui.QApplication.UnicodeUTF8))      

    win.dispSetEltable1Action.setText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Default", None, QtGui.QApplication.UnicodeUTF8))
    win.dispSetEltable1Action.setIconText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Default", None, QtGui.QApplication.UnicodeUTF8))
    win.dispSetEltable2Action.setText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Alternate", None, QtGui.QApplication.UnicodeUTF8))
    win.dispSetEltable2Action.setIconText(QtGui.QApplication.translate("MainWindow", "Set Atom Colors to Alternate", None, QtGui.QApplication.UnicodeUTF8))

    win.dispElementColorSettingsAction.setText(QtGui.QApplication.translate("MainWindow", "Element Color Settings...", None, QtGui.QApplication.UnicodeUTF8))
    win.dispElementColorSettingsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Element Color Settings...", None, QtGui.QApplication.UnicodeUTF8))

    win.dispLightingAction.setText(QtGui.QApplication.translate("MainWindow", "Lighting...", None, QtGui.QApplication.UnicodeUTF8))
    win.dispLightingAction.setIconText(QtGui.QApplication.translate("MainWindow", "Lighting", None, QtGui.QApplication.UnicodeUTF8))
    win.dispResetAtomsDisplayAction.setText(QtGui.QApplication.translate("MainWindow", "Reset Atoms Display", None, QtGui.QApplication.UnicodeUTF8))
    win.dispResetAtomsDisplayAction.setIconText(QtGui.QApplication.translate("MainWindow", "Reset Atoms Display", None, QtGui.QApplication.UnicodeUTF8))
    win.dispShowInvisAtomsAction.setText(QtGui.QApplication.translate("MainWindow", "Show Invisible Atoms", None, QtGui.QApplication.UnicodeUTF8))
    win.dispShowInvisAtomsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Show Invisible Atoms", None, QtGui.QApplication.UnicodeUTF8))

    win.simNanoHiveAction.setText(QtGui.QApplication.translate("MainWindow", "Nano-Hive...", None, QtGui.QApplication.UnicodeUTF8))
    win.simNanoHiveAction.setIconText(QtGui.QApplication.translate("MainWindow", "Nano-Hive", None, QtGui.QApplication.UnicodeUTF8))

    win.fileSaveSelectionAction.setIconText(QtGui.QApplication.translate("MainWindow", "Save Selection...", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRotatePlus90Action.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate View +90", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRotateMinus90Action.setIconText(QtGui.QApplication.translate("MainWindow", "Rotate View -90", None, QtGui.QApplication.UnicodeUTF8))

    win.viewNormalToAction.setIconText(QtGui.QApplication.translate("MainWindow", "Set View Normal To", None, QtGui.QApplication.UnicodeUTF8))
    win.viewNormalToAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Set View Normal To", None, QtGui.QApplication.UnicodeUTF8))
    win.viewParallelToAction.setIconText(QtGui.QApplication.translate("MainWindow", "Set View Parallel To", None, QtGui.QApplication.UnicodeUTF8))
    win.viewParallelToAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Set View Parallel To", None, QtGui.QApplication.UnicodeUTF8))

    win.viewQuteMolAction.setIconText(QtGui.QApplication.translate("MainWindow", "QuteMolX", None, QtGui.QApplication.UnicodeUTF8))
    win.viewRaytraceSceneAction.setIconText(QtGui.QApplication.translate("MainWindow", "POV-Ray", None, QtGui.QApplication.UnicodeUTF8))
    
    win.setViewPerspecAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Perspective",
            None, QtGui.QApplication.UnicodeUTF8))
    win.setViewOrthoAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Orthographic",
            None, QtGui.QApplication.UnicodeUTF8))
    
    #= Toolbar stuff
    
    #= "Standard" toolbar widgets
    win.toolsSelectMoleculesAction.setText(
        QtGui.QApplication.translate("MainWindow", "Select Chunks",
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.toolsSelectMoleculesAction.setToolTip(
        QtGui.QApplication.translate("MainWindow", "Select Chunks", 
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.toolsMoveMoleculeAction.setText(
        QtGui.QApplication.translate("MainWindow", "Translate",
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.toolsMoveMoleculeAction.setToolTip(
        QtGui.QApplication.translate("MainWindow", "Translate",
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.rotateComponentsAction.setText(
        QtGui.QApplication.translate("MainWindow", "Rotate",
                                     None, QtGui.QApplication.UnicodeUTF8))
    win.rotateComponentsAction.setToolTip(
        QtGui.QApplication.translate("MainWindow", "Rotate",
                                    None, QtGui.QApplication.UnicodeUTF8))
