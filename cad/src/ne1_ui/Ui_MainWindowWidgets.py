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
import foundation.env as env
from PyQt4 import QtGui
from PyQt4.Qt import QToolButton
from utilities.icon_utilities import geticon
from utilities.prefs_constants import displayRulers_prefs_key
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction

def setupUi(win):
    """
    Creates all the QActions used in the main menubar and toolbars.

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
    
    #Create the "Fetch" menu, a submenu of file menu
    win.fetchMenu = QtGui.QMenu(win.fileMenu)
    win.fetchMenu.setObjectName("fetchMenu")

    win.fileOpenAction = QtGui.QAction(MainWindow)
    win.fileOpenAction.setIcon(geticon("ui/actions/File/Open.png"))
    win.fileOpenAction.setObjectName("fileOpenAction")

    win.fileCloseAction = QtGui.QAction(MainWindow)
    win.fileCloseAction.setObjectName("fileCloseAction")

    win.fileSaveAction = QtGui.QAction(MainWindow)
    win.fileSaveAction.setIcon(geticon("ui/actions/File/Save.png"))
    win.fileSaveAction.setObjectName("fileSaveAction")

    win.fileSaveAsAction = QtGui.QAction(MainWindow)
    win.fileSaveAsAction.setObjectName("fileSaveAsAction")

    win.fileImportOpenBabelAction = QtGui.QAction(MainWindow)
    win.fileImportOpenBabelAction.setObjectName("fileImportOpenBabelAction")

    win.fileImportIOSAction = QtGui.QAction(MainWindow)
    win.fileImportIOSAction.setObjectName("fileImportIOSAction")
    
    win.fileFetchPdbAction = QtGui.QAction(MainWindow)
    win.fileFetchPdbAction.setObjectName("fileFetchPdbAction")
    
    win.fileExportPdbAction = QtGui.QAction(MainWindow)
    win.fileExportPdbAction.setObjectName("fileExportPdbAction")

    win.fileExportQuteMolXPdbAction = QtGui.QAction(MainWindow)
    win.fileExportQuteMolXPdbAction.setObjectName("fileExportQuteMolXPdbAction")

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

    win.fileExportIOSAction = QtGui.QAction(MainWindow)
    win.fileExportIOSAction.setObjectName("fileExportIOSAction")
    
    
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
    win.editUndoAction.setIcon(geticon("ui/actions/Edit/Undo.png"))
    win.editUndoAction.setVisible(True)
    win.editUndoAction.setObjectName("editUndoAction")

    win.editRedoAction = QtGui.QAction(MainWindow)
    win.editRedoAction.setChecked(False)
    win.editRedoAction.setIcon(geticon("ui/actions/Edit/Redo.png"))
    win.editRedoAction.setVisible(True)
    win.editRedoAction.setObjectName("editRedoAction")

    win.editMakeCheckpointAction = QtGui.QAction(MainWindow)
    win.editMakeCheckpointAction.setIcon(
        geticon("ui/actions/Edit/Make_Checkpoint.png"))
    win.editMakeCheckpointAction.setObjectName("editMakeCheckpointAction")

    win.editAutoCheckpointingAction = QtGui.QAction(MainWindow)
    win.editAutoCheckpointingAction.setCheckable(True)
    win.editAutoCheckpointingAction.setChecked(True)
    win.editAutoCheckpointingAction.setObjectName("editAutoCheckpointingAction")

    win.editClearUndoStackAction = QtGui.QAction(MainWindow)
    win.editClearUndoStackAction.setObjectName("editClearUndoStackAction")

    win.editCutAction = QtGui.QAction(MainWindow)
    win.editCutAction.setEnabled(True)
    win.editCutAction.setIcon(geticon("ui/actions/Edit/Cut.png"))
    win.editCutAction.setObjectName("editCutAction")

    win.editCopyAction = QtGui.QAction(MainWindow)
    win.editCopyAction.setEnabled(True)
    win.editCopyAction.setIcon(geticon("ui/actions/Edit/Copy.png"))
    win.editCopyAction.setObjectName("editCopyAction")

    win.editPasteAction = QtGui.QAction(MainWindow)
    win.editPasteAction.setIcon(geticon("ui/actions/Edit/Paste_Off.png"))
    win.editPasteAction.setObjectName("editPasteAction")

    win.pasteFromClipboardAction = QtGui.QAction(MainWindow)
    win.pasteFromClipboardAction.setIcon(geticon(
        "ui/actions/Properties Manager/clipboard-full.png"))

    win.pasteFromClipboardAction.setObjectName("pasteFromClipboardAction")
    win.pasteFromClipboardAction.setText("Paste from clipboard...")

    win.editDeleteAction = QtGui.QAction(MainWindow)
    win.editDeleteAction.setIcon(geticon("ui/actions/Edit/Delete.png"))
    win.editDeleteAction.setObjectName("editDeleteAction")

    win.editRenameAction = QtGui.QAction(MainWindow)
    win.editRenameAction.setIcon(geticon("ui/actions/Edit/Rename.png"))
    win.editRenameAction.setObjectName("editRenameAction")

    win.editRenameObjectsAction = QtGui.QAction(MainWindow)
    win.editRenameObjectsAction.setIcon(
        geticon("ui/actions/Edit/Rename_Objects.png"))
    win.editRenameObjectsAction.setObjectName("editRenameObjectsAction")

    win.editAddSuffixAction = QtGui.QAction(MainWindow)
    win.editAddSuffixAction.setIcon(geticon("ui/actions/Edit/Add_Suffixes.png"))
    win.editAddSuffixAction.setObjectName("editAddSuffixAction")

    win.dispObjectColorAction = QtGui.QAction(MainWindow)
    win.dispObjectColorAction.setIcon(geticon("ui/actions/Edit/Edit_Color.png"))
    win.dispObjectColorAction.setObjectName("dispObjectColorAction")
    
    win.editDnaDisplayStyleAction = QtGui.QAction(MainWindow)
    win.editDnaDisplayStyleAction.setText("DNA Display Style")       
    win.editDnaDisplayStyleAction.setIcon(
        geticon("ui/actions/Edit/EditDnaDisplayStyle.png"))
    
    win.editProteinDisplayStyleAction = QtGui.QAction(MainWindow)
    win.editProteinDisplayStyleAction.setText("Protein Display Style")       
    win.editProteinDisplayStyleAction.setIcon(
        geticon("ui/actions/Edit/EditProteinDisplayStyle.png"))
        
    win.resetChunkColorAction = QtGui.QAction(MainWindow)
    win.resetChunkColorAction.setIcon(
        geticon("ui/actions/Edit/Reset_Chunk_Color.png"))
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
        geticon("ui/actions/View/Modify/Orientation.png"))
    win.viewOrientationAction.setObjectName("viewOrientationAction")

    win.setViewFitToWindowAction = QtGui.QAction(MainWindow)
    win.setViewFitToWindowAction.setIcon(
        geticon("ui/actions/View/Modify/Zoom_To_Fit.png"))
    win.setViewFitToWindowAction.setObjectName("setViewFitToWindowAction")

    win.setViewZoomtoSelectionAction = QtGui.QAction(MainWindow)
    win.setViewZoomtoSelectionAction.setIcon(
        geticon("ui/actions/View/Modify/Zoom_To_Selection.png"))
    win.setViewZoomtoSelectionAction.setObjectName("setViewZoomtoSelectionAction")

    win.zoomToAreaAction = QtGui.QAction(MainWindow)
    win.zoomToAreaAction.setCheckable(True)
    win.zoomToAreaAction.setIcon(
        geticon("ui/actions/View/Modify/ZoomToArea.png"))
    win.zoomToAreaAction.setObjectName("zoomToAreaAction")

    win.zoomInOutAction = QtGui.QAction(MainWindow)
    win.zoomInOutAction.setCheckable(True)
    win.zoomInOutAction.setIcon(
        geticon("ui/actions/View/Modify/Zoom_In_Out.png"))
    win.zoomInOutAction.setObjectName("zoomInOutAction")

    win.setViewRecenterAction = QtGui.QAction(MainWindow)
    win.setViewRecenterAction.setEnabled(True)
    win.setViewRecenterAction.setIcon(
        geticon("ui/actions/View/Modify/Recenter.png"))
    win.setViewRecenterAction.setObjectName("setViewRecenterAction")

    win.panToolAction = QtGui.QAction(MainWindow)
    win.panToolAction.setCheckable(True)
    win.panToolAction.setIcon(geticon("ui/actions/View/Modify/Pan.png"))
    win.panToolAction.setObjectName("panToolAction")

    win.rotateToolAction = QtGui.QAction(MainWindow)
    win.rotateToolAction.setCheckable(True)
    win.rotateToolAction.setIcon(geticon("ui/actions/View/Modify/Rotate.png"))
    win.rotateToolAction.setObjectName("rotateToolAction")

    win.setViewHomeAction = QtGui.QAction(MainWindow)
    win.setViewHomeAction.setIcon(geticon("ui/actions/View/Modify/Home.png"))
    win.setViewHomeAction.setObjectName("setViewHomeAction")

    win.setViewHomeToCurrentAction = QtGui.QAction(MainWindow)
    win.setViewHomeToCurrentAction.setObjectName("setViewHomeToCurrentAction")

    #= View toolbar QActions.
    win.viewNormalToAction = QtGui.QAction(MainWindow)
    win.viewNormalToAction.setIcon(
        geticon("ui/actions/View/Set_View_Normal_To.png"))
    win.viewNormalToAction.setObjectName("NormalTo")

    win.viewParallelToAction = QtGui.QAction(MainWindow)
    win.viewParallelToAction.setIcon(
        geticon("ui/actions/View/Set_View_Parallel_To.png"))
    win.viewParallelToAction.setObjectName("ParallelTo")

    win.saveNamedViewAction = QtGui.QAction(MainWindow)
    win.saveNamedViewAction.setIcon(
        geticon("ui/actions/View/Modify/Save_Named_View.png"))
    win.saveNamedViewAction.setObjectName("saveNamedViewAction")

    win.viewFrontAction = QtGui.QAction(MainWindow)
    win.viewFrontAction.setEnabled(True)
    win.viewFrontAction.setIcon(geticon("ui/actions/View/Front.png"))
    win.viewFrontAction.setObjectName("Front")

    win.viewBackAction = QtGui.QAction(MainWindow)
    win.viewBackAction.setIcon(geticon("ui/actions/View/Back.png"))
    win.viewBackAction.setObjectName("Back")

    win.viewRightAction = QtGui.QAction(MainWindow)
    win.viewRightAction.setIcon(geticon("ui/actions/View/Right.png"))
    win.viewRightAction.setObjectName("Right")

    win.viewLeftAction = QtGui.QAction(MainWindow)
    win.viewLeftAction.setIcon(geticon("ui/actions/View/Left.png"))
    win.viewLeftAction.setObjectName("Left")

    win.viewTopAction = QtGui.QAction(MainWindow)
    win.viewTopAction.setIcon(geticon("ui/actions/View/Top.png"))
    win.viewTopAction.setObjectName("Top")

    win.viewBottomAction = QtGui.QAction(MainWindow)
    win.viewBottomAction.setEnabled(True)
    win.viewBottomAction.setIcon(geticon("ui/actions/View/Bottom.png"))
    win.viewBottomAction.setObjectName("Bottom")

    win.viewIsometricAction = QtGui.QAction(MainWindow)
    win.viewIsometricAction.setIcon(geticon("ui/actions/View/Isometric.png"))
    win.viewIsometricAction.setObjectName("Isometric")

    win.viewRotate180Action = QtGui.QAction(MainWindow)
    win.viewRotate180Action.setIcon(
        geticon("ui/actions/View/Rotate_View_180.png"))
    win.viewRotate180Action.setObjectName("Rotate180")

    win.viewRotatePlus90Action = QtGui.QAction(MainWindow)
    win.viewRotatePlus90Action.setIcon(
        geticon("ui/actions/View/Rotate_View_+90.png"))
    win.viewRotatePlus90Action.setObjectName("RotatePlus90")

    win.viewRotateMinus90Action = QtGui.QAction(MainWindow)
    win.viewRotateMinus90Action.setIcon(
        geticon("ui/actions/View/Rotate_View_-90.png"))
    win.viewRotateMinus90Action.setObjectName("RotateMinus90")

    win.viewDefviewAction = QtGui.QAction(MainWindow)
    win.viewDefviewAction.setObjectName("viewDefviewAction")

    #== View > Display (menu and toolbar) actions.
    win.dispDefaultAction = QtGui.QAction(MainWindow)
    win.dispDefaultAction.setIcon(
        geticon("ui/actions/View/Display/Default.png"))
    win.dispDefaultAction.setObjectName("dispDefaultAction")

    win.dispInvisAction = QtGui.QAction(MainWindow)
    win.dispInvisAction.setIcon(
        geticon("ui/actions/View/Display/Invisible.png"))
    win.dispInvisAction.setObjectName("dispInvisAction")

    win.dispLinesAction = QtGui.QAction(MainWindow)
    win.dispLinesAction.setIcon(
        geticon("ui/actions/View/Display/Lines.png"))
    win.dispLinesAction.setObjectName("dispLinesAction")

    win.dispTubesAction = QtGui.QAction(MainWindow)
    win.dispTubesAction.setEnabled(True)
    win.dispTubesAction.setIcon(
        geticon("ui/actions/View/Display/Tubes.png"))
    win.dispTubesAction.setObjectName("dispTubesAction")

    win.dispCPKAction = QtGui.QAction(MainWindow)
    win.dispCPKAction.setIcon(geticon("ui/actions/View/Display/CPK.png"))
    win.dispCPKAction.setObjectName("dispCPKAction")

    win.dispBallAction = QtGui.QAction(MainWindow)
    win.dispBallAction.setIcon(
        geticon("ui/actions/View/Display/Ball_and_Stick.png"))
    win.dispBallAction.setObjectName("dispBallAction")

    #@ This QAction is unused. See comments at the top of Ui_ViewMenu.py.
    win.dispHybridAction = QtGui.QAction(MainWindow)
    win.dispHybridAction.setIcon(
        geticon("ui/actions/View/Display/Hybrid.png"))
    win.dispHybridAction.setCheckable(True)
    win.dispHybridAction.setObjectName("dispHybridAction")

    win.dispCylinderAction = QtGui.QAction(MainWindow)
    win.dispCylinderAction.setIcon(
        geticon("ui/actions/View/Display/Cylinder.png"))
    win.dispCylinderAction.setObjectName("dispCylinderAction")

    win.dispDnaCylinderAction = QtGui.QAction(MainWindow)
    win.dispDnaCylinderAction.setIcon(
        geticon("ui/actions/View/Display/DnaCylinder.png"))
    win.dispDnaCylinderAction.setObjectName("dispDnaCylinderAction")

    win.dispHideAction = QtGui.QAction(MainWindow)
    win.dispHideAction.setIcon(
        geticon("ui/actions/View/Display/Hide.png"))
    win.dispHideAction.setObjectName("dispHideAction")

    win.dispUnhideAction = QtGui.QAction(MainWindow)
    win.dispUnhideAction.setIcon(
        geticon("ui/actions/View/Display/Unhide.png"))
    win.dispUnhideAction.setObjectName("dispUnhideAction")

    # This is currently NIY. Mark 2007-12-28
    win.dispSurfaceAction = QtGui.QAction(MainWindow)
    win.dispSurfaceAction.setIcon(
        geticon("ui/actions/View/Display/Surface.png"))
    win.dispSurfaceAction.setObjectName("dispSurfaceAction")

    win.setViewPerspecAction = QtGui.QAction(MainWindow)
    win.setViewPerspecAction.setCheckable(True)

    win.setViewOrthoAction = QtGui.QAction(MainWindow)
    win.setViewOrthoAction.setCheckable(True)

    win.orthoPerpActionGroup = QtGui.QActionGroup(MainWindow)  
    win.orthoPerpActionGroup.setExclusive(True)
    win.orthoPerpActionGroup.addAction(win.setViewPerspecAction)
    win.orthoPerpActionGroup.addAction(win.setViewOrthoAction)

    # piotr 080516 added stereo view action
    win.setStereoViewAction = QtGui.QAction(MainWindow)
    win.setStereoViewAction.setIcon(
        geticon("ui/actions/View/Stereo_View.png"))
    win.setStereoViewAction.setObjectName("setStereoViewAction")

    win.viewQuteMolAction = QtGui.QAction(MainWindow)
    win.viewQuteMolAction.setIcon(
        geticon("ui/actions/View/Display/QuteMol.png"))
    win.viewQuteMolAction.setObjectName("viewQuteMolAction")

    win.viewRaytraceSceneAction = QtGui.QAction(MainWindow)
    win.viewRaytraceSceneAction.setIcon(
        geticon("ui/actions/View/Display/Raytrace_Scene.png"))
    win.viewRaytraceSceneAction.setObjectName("viewRaytraceSceneAction")

    win.dispSetEltable1Action = QtGui.QAction(MainWindow)
    win.dispSetEltable1Action.setObjectName("dispSetEltable1Action")

    win.dispSetEltable2Action = QtGui.QAction(MainWindow)
    win.dispSetEltable2Action.setObjectName("dispSetEltable2Action")

    win.dispResetAtomsDisplayAction = QtGui.QAction(MainWindow)
    win.dispResetAtomsDisplayAction.setObjectName("dispResetAtomsDisplayAction")

    win.dispShowInvisAtomsAction = QtGui.QAction(MainWindow)
    win.dispShowInvisAtomsAction.setObjectName("dispShowInvisAtomsAction")

    win.dispElementColorSettingsAction = QtGui.QAction(MainWindow)
    win.dispElementColorSettingsAction.setObjectName("dispElementColorSettingsAction")
    win.dispElementColorSettingsAction.setIcon(
        geticon("ui/actions/View/Display/Element_Color_Settings.png"))

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
    #win.referenceGeometryMenu = QtGui.QMenu(win.insertMenu)
    #win.referenceGeometryMenu.setObjectName("referenceGeometryMenu")

    win.jigsAtomSetAction = NE1_QWidgetAction(MainWindow, 
                                                win = MainWindow)
    win.jigsAtomSetAction.setIcon(geticon("ui/actions/Tools/Atom_Set.png"))
    win.jigsAtomSetAction.setObjectName("jigsAtomSetAction")

    win.fileInsertMmpAction = NE1_QWidgetAction(MainWindow, 
                                                  win = MainWindow)
    win.fileInsertMmpAction.setObjectName("fileInsertMmpAction")
    win.fileInsertMmpAction.setIcon(
        geticon('ui/actions/Insert/MMP.png'))

    win.fileInsertPdbAction = NE1_QWidgetAction(MainWindow, 
                                                  win = MainWindow)
    win.fileInsertPdbAction.setObjectName("fileInsertPdbAction")
    win.fileInsertPdbAction.setIcon(geticon('ui/actions/Insert/PDB.png'))

    win.partLibAction = NE1_QWidgetAction(MainWindow, 
                                            win = MainWindow)
    win.partLibAction.setObjectName("partLibAction")
    win.partLibAction.setIcon(geticon('ui/actions/Insert/Part_Library.png'))

    win.insertCommentAction = NE1_QWidgetAction(MainWindow,
                                                  win = MainWindow)
    win.insertCommentAction.setIcon(
        geticon("ui/actions/Insert/Comment.png"))
    win.insertCommentAction.setObjectName("insertCommentAction")

    win.insertPovraySceneAction = NE1_QWidgetAction(MainWindow, 
                                                      win = MainWindow)
    win.insertPovraySceneAction.setIcon(
        geticon("ui/actions/Insert/POV-Ray_Scene.png"))
    win.insertPovraySceneAction.setObjectName("insertPovraySceneAction")

    win.jigsGridPlaneAction = NE1_QWidgetAction(MainWindow, 
                                                  win = MainWindow)
    win.jigsGridPlaneAction.setIcon(
        geticon("ui/actions/Insert/Reference Geometry/Grid_Plane.png"))
    win.jigsGridPlaneAction.setObjectName("jigsGridPlaneAction")

    win.referencePlaneAction = NE1_QWidgetAction(MainWindow, 
                                                   win = MainWindow)
    win.referencePlaneAction.setIcon(
        geticon("ui/actions/Insert/Reference Geometry/Plane.png"))
    win.referencePlaneAction.setObjectName("referencePlaneAction")

    win.referenceLineAction = NE1_QWidgetAction(MainWindow, 
                                                  win = MainWindow)
    win.referenceLineAction.setIcon(
        geticon("ui/actions/Insert/Reference Geometry/Plane.png"))
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

    win.editPrefsAction = NE1_QWidgetAction(MainWindow, 
                                              win = MainWindow)
    win.editPrefsAction.setIcon(geticon("ui/actions/Tools/Options.png"))
    win.editPrefsAction.setObjectName("editPrefsAction")    

     #Urmi background color scheme option 080522
    win.colorSchemeAction =  QtGui.QAction(MainWindow)
    win.colorSchemeAction.setIcon(geticon("ui/actions/View/ColorScheme.png"))
    win.colorSchemeAction.setObjectName("colorSchemeAction")
    
    win.lightingSchemeAction = QtGui.QAction(MainWindow)
    win.lightingSchemeAction.setIcon(geticon("ui/actions/View/LightingScheme.png"))
    win.lightingSchemeAction.setObjectName("lightingSchemeAction")
    
    win.modifyAdjustSelAction = NE1_QWidgetAction(MainWindow, 
                                                    win = MainWindow)
    win.modifyAdjustSelAction.setEnabled(True)
    win.modifyAdjustSelAction.setIcon(
        geticon("ui/actions/Tools/Adjust_Selection.png"))
    win.modifyAdjustSelAction.setObjectName("modifyAdjustSelAction")

    win.modifyAdjustAllAction = NE1_QWidgetAction(MainWindow, 
                                                    win = MainWindow)
    win.modifyAdjustAllAction.setIcon(
        geticon("ui/actions/Tools/Adjust_All.png"))
    win.modifyAdjustAllAction.setObjectName("modifyAdjustAllAction")

    win.simMinimizeEnergyAction = NE1_QWidgetAction(MainWindow, 
                                                      win = MainWindow)
    win.simMinimizeEnergyAction.setIcon(
        geticon("ui/actions/Simulation/Minimize_Energy.png"))
    win.simMinimizeEnergyAction.setObjectName("simMinimizeEnergyAction")

    win.toolsExtrudeAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.toolsExtrudeAction.setCheckable(True)
    win.toolsExtrudeAction.setIcon(
        geticon("ui/actions/Insert/Features/Extrude.png"))

    win.toolsFuseChunksAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.toolsFuseChunksAction.setCheckable(1) # make the Fuse Mode button checkable
    win.toolsFuseChunksAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Fuse_Chunks.png"))

    win.modifyMirrorAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.modifyMirrorAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Mirror.png"))
    win.modifyMirrorAction.setObjectName("modifyMirrorAction")

    win.modifyInvertAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.modifyInvertAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Invert.png"))
    win.modifyInvertAction.setObjectName("modifyInvertAction")

    win.modifyStretchAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.modifyStretchAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Stretch.png"))
    win.modifyStretchAction.setObjectName("modifyStretchAction")

    #== "Tools > Build Structures" (menu and toolbar) widgets.

    win.toolsDepositAtomAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.toolsDepositAtomAction.setCheckable(1) # make the build button checkable
    win.toolsDepositAtomAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/Build Chunks.png"))

    win.toolsCookieCutAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.toolsCookieCutAction.setCheckable(1) # make the cookie button checkable
    win.toolsCookieCutAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/Build Crystal.png"))

    win.insertGrapheneAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.insertGrapheneAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/Graphene.png"))
    win.insertGrapheneAction.setObjectName("insertGrapheneAction")

    win.nanotubeGeneratorAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.nanotubeGeneratorAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/Nanotube.png"))
    win.nanotubeGeneratorAction.setObjectName("nanotubeGeneratorAction")

    win.buildNanotubeAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.buildNanotubeAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/Nanotube.png"))
    win.buildNanotubeAction.setObjectName("buildNanotubeAction")

    win.buildDnaAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.buildDnaAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/DNA.png"))
    win.buildDnaAction.setObjectName("buildDnaAction")

    # Atom Generator (Developer Example). Mark 2007-06-08
    win.insertAtomAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.insertAtomAction.setIcon(
        geticon("ui/actions/Toolbars/Smart/Deposit_Atoms.png"))
    win.insertAtomAction.setObjectName("insertAtomAction")

    # Peptide Generator, piotr 080304
    win.insertPeptideAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.insertPeptideAction.setIcon(
        geticon("ui/actions/Tools/Build Structures/Peptide.png"))
    win.insertPeptideAction.setObjectName("insertPeptideAction")

    #== "Tools > Build Tools" (menu and toolbar) widgets.

    win.modifyHydrogenateAction = NE1_QWidgetAction(MainWindow, 
                                                    win = MainWindow)
    win.modifyHydrogenateAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Hydrogenate.png"))
    win.modifyHydrogenateAction.setObjectName("modifyHydrogenateAction")

    win.modifyDehydrogenateAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.modifyDehydrogenateAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Dehydrogenate.png"))
    win.modifyDehydrogenateAction.setObjectName("modifyDehydrogenateAction")

    win.modifyPassivateAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.modifyPassivateAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Passivate.png"))
    win.modifyPassivateAction.setObjectName("modifyPassivateAction")

    win.modifyDeleteBondsAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.modifyDeleteBondsAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Delete_Bonds.png"))
    win.modifyDeleteBondsAction.setObjectName("modifyDeleteBondsAction")      

    win.modifySeparateAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.modifySeparateAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/Separate.png"))
    win.modifySeparateAction.setObjectName("modifySeparateAction")

    win.modifyMergeAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.modifyMergeAction.setIcon(geticon(
        "ui/actions/Tools/Build Tools/Combine_Chunks.png"))
    win.modifyMergeAction.setObjectName("modifyMergeAction")

    win.makeChunkFromSelectedAtomsAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.makeChunkFromSelectedAtomsAction.setIcon(geticon(
        "ui/actions/Tools/Build Tools/New_Chunk.png"))
    win.makeChunkFromSelectedAtomsAction.setObjectName(
        "makeChunkFromSelectedAtomsAction")

    win.modifyAlignCommonAxisAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.modifyAlignCommonAxisAction.setIcon(
        geticon("ui/actions/Tools/Build Tools/AlignToCommonAxis.png"))
    win.modifyAlignCommonAxisAction.setObjectName("modifyAlignCommonAxisAction")

    win.modifyCenterCommonAxisAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.modifyCenterCommonAxisAction.setObjectName(
        "modifyCenterCommonAxisAction")

    #= "Tools > Dimensions" (menu and toolbar) widgets.

    win.jigsDistanceAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.jigsDistanceAction.setIcon(
        geticon("ui/actions/Tools/Dimensions/Measure_Distance.png"))
    win.jigsDistanceAction.setObjectName("jigsDistanceAction")

    win.jigsAngleAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.jigsAngleAction.setIcon(
        geticon("ui/actions/Tools/Dimensions/Measure_Angle.png"))
    win.jigsAngleAction.setObjectName("jigsAngleAction")

    win.jigsDihedralAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.jigsDihedralAction.setIcon(
        geticon("ui/actions/Tools/Dimensions/Measure_Dihedral.png"))
    win.jigsDihedralAction.setObjectName("jigsDihedralAction")

    #= "Tools > Select" (menu and toolbar) widgets.

    win.selectAllAction = QtGui.QAction(MainWindow)
    win.selectAllAction.setEnabled(True)
    win.selectAllAction.setIcon(
        geticon("ui/actions/Tools/Select/Select_All.png"))
    win.selectAllAction.setObjectName("selectAllAction")

    win.selectNoneAction = QtGui.QAction(MainWindow)
    win.selectNoneAction.setIcon(
        geticon("ui/actions/Tools/Select/Select_None.png"))
    win.selectNoneAction.setObjectName("selectNoneAction")

    win.selectInvertAction = QtGui.QAction(MainWindow)
    win.selectInvertAction.setIcon(
        geticon("ui/actions/Tools/Select/Select_Invert.png"))
    win.selectInvertAction.setObjectName("selectInvertAction")

    win.selectConnectedAction = QtGui.QAction(MainWindow)
    win.selectConnectedAction.setIcon(
        geticon("ui/actions/Tools/Select/Select_Connected.png"))
    win.selectConnectedAction.setObjectName("selectConnectedAction")

    win.selectDoublyAction = QtGui.QAction(MainWindow)
    win.selectDoublyAction.setIcon(
        geticon("ui/actions/Tools/Select/Select_Doubly.png"))
    win.selectDoublyAction.setObjectName("selectDoublyAction")

    win.selectExpandAction = QtGui.QAction(MainWindow)
    win.selectExpandAction.setIcon(
        geticon("ui/actions/Tools/Select/Expand.png"))
    win.selectExpandAction.setObjectName("selectExpandAction")

    win.selectContractAction = QtGui.QAction(MainWindow)
    win.selectContractAction.setIcon(
        geticon("ui/actions/Tools/Select/Contract.png"))
    win.selectContractAction.setObjectName("selectContractAction")

    win.selectLockAction = QtGui.QAction(MainWindow)
    win.selectLockAction.setIcon(
        geticon("ui/actions/Tools/Select/Selection_Unlocked.png"))
    win.selectLockAction.setObjectName("selectLockAction")
    win.selectLockAction.setCheckable(True)

    #= "Simulation" (menu and toolbar) widgets.

    # Create the "Simulation" menu
    win.simulationMenu = QtGui.QMenu(win.MenuBar)
    win.simulationMenu.setObjectName("simulationMenu")

    # Create the "Measurements" menu. #@ Not used??? MAS
    win.measurementsMenu = QtGui.QMenu()
    win.measurementsMenu.setObjectName("measurementsMenu")
    win.measurementsMenu.setIcon(
        geticon("ui/actions/Toolbars/Smart/Dimension.png"))

    win.simSetupAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.simSetupAction.setCheckable(True)
    win.simSetupAction.setChecked(False)
    win.simSetupAction.setEnabled(True)
    win.simSetupAction.setIcon(
        geticon("ui/actions/Simulation/Run_Dynamics.png"))
    win.simSetupAction.setObjectName("simSetupAction")

    win.simMoviePlayerAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.simMoviePlayerAction.setIcon(
        geticon("ui/actions/Simulation/Play_Movie.png"))

    win.rosettaSetupAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.rosettaSetupAction.setCheckable(True)
    win.rosettaSetupAction.setChecked(False)
    win.rosettaSetupAction.setEnabled(True)
    win.rosettaSetupAction.setIcon(
        geticon("ui/actions/Simulation/Rosetta.png"))
    win.rosettaSetupAction.setObjectName("rosettaSetupAction")
    
    win.simPlotToolAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.simPlotToolAction.setIcon(
        geticon("ui/actions/Simulation/Make_Graphs.png"))
    win.simPlotToolAction.setObjectName("simPlotToolAction")

    win.jigsMotorAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.jigsMotorAction.setIcon(
        geticon("ui/actions/Simulation/Rotary_Motor.png"))
    win.jigsMotorAction.setObjectName("jigsMotorAction")

    win.jigsLinearMotorAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.jigsLinearMotorAction.setIcon(
        geticon("ui/actions/Simulation/Linear_Motor.png"))
    win.jigsLinearMotorAction.setObjectName("jigsLinearMotorAction")

    win.jigsStatAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.jigsStatAction.setIcon(
        geticon("ui/actions/Simulation/Thermostat.png"))
    win.jigsStatAction.setObjectName("jigsStatAction")

    win.jigsThermoAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.jigsThermoAction.setIcon(
        geticon("ui/actions/Simulation/Measurements/Thermometer.png"))
    win.jigsThermoAction.setObjectName("jigsThermoAction")

    win.jigsAnchorAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.jigsAnchorAction.setIcon(
        geticon("ui/actions/Simulation/Anchor.png"))
    win.jigsAnchorAction.setObjectName("jigsAnchorAction")

    win.simulationJigsAction = QtGui.QAction(win)
    win.simulationJigsAction.setIcon(
        geticon("ui/actions/Simulation/Simulation_Jigs.png"))
    win.simulationJigsAction.setObjectName("simulationJigsAction")

    win.jigsGamessAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.jigsGamessAction.setEnabled(True)
    win.jigsGamessAction.setIcon(
        geticon("ui/actions/Simulation/GAMESS.png"))
    win.jigsGamessAction.setObjectName("jigsGamessAction")

    win.jigsESPImageAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.jigsESPImageAction.setIcon(
        geticon("ui/actions/Simulation/ESP_Image.png"))
    win.jigsESPImageAction.setObjectName("jigsESPImageAction")

    # This only shows up if the user enables the NH1 plugin (via Preferences)
    # which is hidden since NH1 doesn't work with NE1.
    # See UserPrefs.enable_nanohive().
    win.simNanoHiveAction = QtGui.QAction(MainWindow)
    win.simNanoHiveAction.setVisible(False)
    win.simNanoHiveAction.setObjectName("simNanoHiveAction")

    #= Rendering menu.

    # Create the "Tools" menu.
    win.renderingMenu = QtGui.QMenu(win.MenuBar)
    win.renderingMenu.setObjectName("Rendering")

    #= "Help" (menu and toolbar) widgets.

    win.helpMenu = QtGui.QMenu(win.MenuBar)
    win.helpMenu.setObjectName("helpMenu")
    
    win.helpTutorialsAction = QtGui.QAction(MainWindow)
    win.helpTutorialsAction.setObjectName("helpAboutAction")

    win.helpMouseControlsAction = QtGui.QAction(MainWindow)
    win.helpMouseControlsAction.setObjectName("helpMouseControlsAction")

    win.helpKeyboardShortcutsAction = QtGui.QAction(MainWindow)
    win.helpKeyboardShortcutsAction.setObjectName("helpKeyboardShortcutsAction")

    win.helpSelectionShortcutsAction = QtGui.QAction(MainWindow)
    win.helpSelectionShortcutsAction.setObjectName("helpSelectionShortcutsAction")

    win.helpGraphicsCardAction = QtGui.QAction(MainWindow)
    win.helpGraphicsCardAction.setObjectName("helpGraphicsCardAction")

    win.helpWhatsThisAction = QtGui.QAction(MainWindow)
    win.helpWhatsThisAction.setIcon(geticon("ui/actions/Help/WhatsThis.png"))
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
    win.toolsSelectMoleculesAction.setIcon(
        geticon("ui/actions/Toolbars/Standard/Select_Chunks.png"))

    # Define an action grop for move molecules (translate and rotate components)
    # actions ...to make them mutually exclusive. 
    # -- ninad 070309
    win.toolsMoveRotateActionGroup = QtGui.QActionGroup(MainWindow)
    win.toolsMoveRotateActionGroup.setExclusive(True)

    win.toolsMoveMoleculeAction = NE1_QWidgetAction(win.toolsMoveRotateActionGroup, 
                                                      win = MainWindow)
    win.toolsMoveMoleculeAction.setCheckable(1) # make the Move mode button checkable
    win.toolsMoveMoleculeAction.setIcon(
        geticon("ui/actions/Toolbars/Standard/Move_Chunks.png"))

    win.rotateComponentsAction = NE1_QWidgetAction(win.toolsMoveRotateActionGroup, 
                                                     win = MainWindow)
    win.rotateComponentsAction.setCheckable(1) # make the Move mode button checkable
    win.rotateComponentsAction.setIcon(
        geticon("ui/actions/Toolbars/Standard/Rotate_Components.png"))

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

    win.standardViewsAction = NE1_QWidgetAction(MainWindow, win = MainWindow)
    win.standardViewsAction.setEnabled(True)
    win.standardViewsAction.setIcon(
        geticon("ui/actions/View/Standard_Views.png"))
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
    win.toolsDoneAction.setIcon(
        geticon("ui/actions/Properties Manager/Done.png"))
    win.toolsDoneAction.setObjectName("toolsDoneAction")

    # Dock widgets
    from ne1_ui.Ui_ReportsDockWidget import Ui_ReportsDockWidget
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

    @attention: It is never OK to set the shortcut "Ctrl+H or Cmd+H on Mac)"  
    via setShortcut() since this shortcut is reserved on Mac OS X for hiding a 
    window.
    """

    #= File (menu and toolbar) actions.
    win.fileOpenAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Open...", None, QtGui.QApplication.UnicodeUTF8))
    win.fileOpenAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
    win.fileOpenAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Open(Ctrl+O)", None, QtGui.QApplication.UnicodeUTF8))      
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
    win.fileSaveAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Save (Ctrl+S)", None, QtGui.QApplication.UnicodeUTF8))    
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

    win.fileImportIOSAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "IOS import...", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fileImportIOSAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "IOS", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fileImportIOSAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "IOS import", None, QtGui.QApplication.UnicodeUTF8))
    
    win.fileExportPdbAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Protein Data Bank...", 
            None, QtGui.QApplication.UnicodeUTF8))

    win.fileExportQuteMolXPdbAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Protein Data Bank for QuteMolX...", 
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
    
    #ios export
    win.fileExportIOSAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "IOS export...", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fileExportIOSAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "IOS", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fileExportIOSAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "IOS export", None, QtGui.QApplication.UnicodeUTF8))   
    
    #fetch pdb
    win.fileFetchPdbAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "PDB file from RCSB...", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fileFetchPdbAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Fetch PDB", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.fileFetchPdbAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Fetch a PDB file from RCSB", None, QtGui.QApplication.UnicodeUTF8))  
    
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
    win.editUndoAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Undo (Ctrl+Z)", None, QtGui.QApplication.UnicodeUTF8))  
    win.editRedoAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "&Redo", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRedoAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Redo", 
            None, QtGui.QApplication.UnicodeUTF8))

    # Redo is a special case between Mac OS X and the other platforms:
    # - Cmd+Shift+Z on Mac
    # - Ctrl+Y on Windows and Linux
    # We take care of tooltips and keyboard shortcut settings here.
    # -Mark 2008-05-05.
    from platform_dependent.PlatformDependent import is_macintosh
    if is_macintosh():
        redo_accel = "Cmd+Shift+Z"
    else:
        redo_accel = "Ctrl+Y"
    win.editRedoAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", redo_accel, 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRedoAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Redo (" + redo_accel + ")", 
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
    win.editCutAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Cut (Ctrl+X)", None, QtGui.QApplication.UnicodeUTF8))
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
    win.editCopyAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Copy (Ctrl+V)", None, QtGui.QApplication.UnicodeUTF8))    
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
    win.editRenameAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Rename",
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRenameAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Rename", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRenameAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Rename (Shift+R)", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRenameAction.setShortcut(
        QtGui.QApplication.translate(
            "MainWindow", "Shift+R", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRenameObjectsAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Rename Objects",
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRenameObjectsAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Rename Objects", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editRenameObjectsAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Rename Objects", 
            None, QtGui.QApplication.UnicodeUTF8))

    win.editAddSuffixAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Add Suffixes",
            None, QtGui.QApplication.UnicodeUTF8))
    win.editAddSuffixAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Add Suffixes", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.editAddSuffixAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Add Suffixes", 
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
            "MainWindow", "Change Color of Selection...", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.dispObjectColorAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Change Color of Selected Objects", 
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
            "MainWindow", "Zoom In . (dot) | Zoom Out , (comma)",
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
    win.setViewHomeToCurrentAction.setText(QtGui.QApplication.translate("MainWindow", "Replace 'Home View' with the current view", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeToCurrentAction.setIconText(QtGui.QApplication.translate("MainWindow", "Replace 'Home View' with the current view", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeToCurrentAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Replace 'Home View' with the current view (Ctrl+Home)", None, QtGui.QApplication.UnicodeUTF8))
    win.setViewHomeToCurrentAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Home", None, QtGui.QApplication.UnicodeUTF8))
    win.saveNamedViewAction.setText(QtGui.QApplication.translate("MainWindow", "Save Named View", None, QtGui.QApplication.UnicodeUTF8))
    win.saveNamedViewAction.setIconText(QtGui.QApplication.translate("MainWindow", "Save Named View", None, QtGui.QApplication.UnicodeUTF8))

    #VIEW > DISPLAY MENU ITEMS
    win.dispBallAction.setText(QtGui.QApplication.translate("MainWindow", "Ball and Stick", None, QtGui.QApplication.UnicodeUTF8))
    win.dispBallAction.setIconText(QtGui.QApplication.translate("MainWindow", "Ball and Stick", None, QtGui.QApplication.UnicodeUTF8))
    win.dispBallAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", 
            "Apply <b>Ball and Stick</b> display style to the selection", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
    win.dispDefaultAction.setText(QtGui.QApplication.translate("MainWindow", "Default", None, QtGui.QApplication.UnicodeUTF8))
    win.dispDefaultAction.setIconText(QtGui.QApplication.translate("MainWindow", "Default", None, QtGui.QApplication.UnicodeUTF8))
    win.dispDefaultAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", 
            "Apply <b>Default</b> display setting to the selection", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
    win.dispInvisAction.setText(QtGui.QApplication.translate("MainWindow", "Invisible", None, QtGui.QApplication.UnicodeUTF8))
    win.dispInvisAction.setIconText(QtGui.QApplication.translate("MainWindow", "Invisible", None, QtGui.QApplication.UnicodeUTF8))
    win.dispLinesAction.setText(QtGui.QApplication.translate("MainWindow", "Lines", None, QtGui.QApplication.UnicodeUTF8))
    win.dispLinesAction.setIconText(QtGui.QApplication.translate("MainWindow", "Lines", None, QtGui.QApplication.UnicodeUTF8))
    win.dispLinesAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", 
            "Apply <b>Lines</b> display style to the selection", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
    win.dispTubesAction.setText(QtGui.QApplication.translate("MainWindow", "Tubes", None, QtGui.QApplication.UnicodeUTF8))
    win.dispTubesAction.setIconText(QtGui.QApplication.translate("MainWindow", "Tubes", None, QtGui.QApplication.UnicodeUTF8))
    win.dispTubesAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", 
            "Apply <b>Tubes</b> display style to the selection", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
    win.dispCPKAction.setText(QtGui.QApplication.translate("MainWindow", "CPK", None, QtGui.QApplication.UnicodeUTF8))
    win.dispCPKAction.setIconText(QtGui.QApplication.translate("MainWindow", "CPK", None, QtGui.QApplication.UnicodeUTF8))
    win.dispCPKAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", 
            "Apply <b>CPK</b> display style to the selection", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
    win.dispHybridAction.setText(QtGui.QApplication.translate("MainWindow", "Hybrid Display", None, QtGui.QApplication.UnicodeUTF8))
    win.dispHybridAction.setIconText(QtGui.QApplication.translate("MainWindow", "Hybrid", None, QtGui.QApplication.UnicodeUTF8))
    win.dispSurfaceAction.setIconText(QtGui.QApplication.translate("MainWindow", "Surface", None, QtGui.QApplication.UnicodeUTF8))
    win.dispSurfaceAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", 
            "Apply <b>Surface</b> display style to the selection", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
    win.dispCylinderAction.setIconText(QtGui.QApplication.translate("MainWindow", "Cylinder", None, QtGui.QApplication.UnicodeUTF8))
    win.dispCylinderAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", 
            "Apply <b>Cylinder</b> display style to the selection", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
    win.dispDnaCylinderAction.setIconText(QtGui.QApplication.translate("MainWindow", "DNA Cylinder", None, QtGui.QApplication.UnicodeUTF8))
    win.dispDnaCylinderAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", 
            "Apply <b>DNA Cylinder</b> display style to the selection", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
    win.dispHideAction.setIconText(QtGui.QApplication.translate("MainWindow", "Hide", None, QtGui.QApplication.UnicodeUTF8))
    win.dispHideAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Hide", None, QtGui.QApplication.UnicodeUTF8))
    win.dispUnhideAction.setIconText(QtGui.QApplication.translate("MainWindow", "Unhide", None, QtGui.QApplication.UnicodeUTF8))
    win.dispUnhideAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Unhide", None, QtGui.QApplication.UnicodeUTF8))

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
    win.resetChunkColorAction.setText(QtGui.QApplication.translate("MainWindow", "&Reset Color of Selected Chunks", None, QtGui.QApplication.UnicodeUTF8))
    win.resetChunkColorAction.setIconText(QtGui.QApplication.translate("MainWindow", "Reset Color of Selected Chunks", None, QtGui.QApplication.UnicodeUTF8))

    #= Insert (menu and toolbar) actions.
    win.jigsAtomSetAction.setIconText(QtGui.QApplication.translate(
        "MainWindow",  "Atom Set",  None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertMmpAction.setText(QtGui.QApplication.translate(
        "MainWindow", "MMP file", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertMmpAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "MMP file", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertMmpAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Insert Molecular Machine Part (MMP) file", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertPdbAction.setText(QtGui.QApplication.translate(
        "MainWindow", "PDB file", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertPdbAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "PDB file", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.fileInsertPdbAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Insert Protein Data Bank (PDB) file", 
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
        "MainWindow", "Grid Plane", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.referencePlaneAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Plane",
        None, QtGui.QApplication.UnicodeUTF8))

    # Part Lib
    win.partLibAction.setText(QtGui.QApplication.translate(
        "MainWindow", "Part Library", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.partLibAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Part from Part Library", 
        None, QtGui.QApplication.UnicodeUTF8))

    win.partLibAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Insert Part from Part Library", 
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

    win.colorSchemeAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Color Scheme", 
            None, QtGui.QApplication.UnicodeUTF8))
    
    win.lightingSchemeAction.setText(QtGui.QApplication.translate(
        "MainWindow",
        "Lighting Scheme",
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
    
    #Urmi background color chooser option 080522
    
    win.colorSchemeAction.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Color Scheme", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.colorSchemeAction.setIconText(
        QtGui.QApplication.translate(
            "MainWindow", "Color Scheme", 
            None, QtGui.QApplication.UnicodeUTF8))
    
    win.lightingSchemeAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Lighting Scheme", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.lightingSchemeAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Lighting Scheme", 
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
    win.nanotubeGeneratorAction.setIconText(QtGui.QApplication.translate(
        "MainWindow",
        "Nanotube",
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.nanotubeGeneratorAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Generate Nanotube (old)", 
        None,
        QtGui.QApplication.UnicodeUTF8))
    win.insertGrapheneAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Graphene", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.insertGrapheneAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Generate Graphene", 
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
    win.buildNanotubeAction.setText(QtGui.QApplication.translate(
        "MainWindow", 
        "Nanotube", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.buildNanotubeAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Nanotube",
        None,
        QtGui.QApplication.UnicodeUTF8))
    win.buildNanotubeAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow",
        "Build Nanotube", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    # Atom Generator example for developers.
    win.insertAtomAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", 
        "Atom", 
        None, 
        QtGui.QApplication.UnicodeUTF8))
    win.insertAtomAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", 
        "Generate Atom (Developer Example)", 
        None, 
        QtGui.QApplication.UnicodeUTF8))

    # Peptide Generator. piotr 080304
    # piotr 080710 : Use "Peptide" label instead of "Protein"
    # if the "Enable Proteins" debug pref is set to False.
    # This should be moved to "interactive builders" sections
    # on the Build Structures toolbar.
    from protein.model.Protein import enableProteins
    if enableProteins:    
        win.insertPeptideAction.setIconText(QtGui.QApplication.translate(
            "MainWindow", 
            "Protein", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
        win.insertPeptideAction.setToolTip(QtGui.QApplication.translate(
            "MainWindow", 
            "Build Protein", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
    else:
        win.insertPeptideAction.setIconText(QtGui.QApplication.translate(
            "MainWindow", 
            "Peptide", 
            None, 
            QtGui.QApplication.UnicodeUTF8))
        win.insertPeptideAction.setToolTip(QtGui.QApplication.translate(
            "MainWindow", 
            "Generate Peptide", 
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
    win.modifyPassivateAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Passivate",
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
    win.selectAllAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select All (Ctrl+A)", None, QtGui.QApplication.UnicodeUTF8))
    win.selectAllAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+A", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setText(QtGui.QApplication.translate("MainWindow", "&None", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setIconText(QtGui.QApplication.translate("MainWindow", "None", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select None (Ctrl+N)", None, QtGui.QApplication.UnicodeUTF8))
    win.selectNoneAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setText(QtGui.QApplication.translate("MainWindow", "&Invert", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setIconText(QtGui.QApplication.translate("MainWindow", "Invert", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Invert Selection (Ctrl+Shift+I)", None, QtGui.QApplication.UnicodeUTF8))
    win.selectInvertAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Shift+I", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setText(QtGui.QApplication.translate("MainWindow", "&Connected", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setIconText(QtGui.QApplication.translate("MainWindow", "Connected", None, QtGui.QApplication.UnicodeUTF8))
    win.selectConnectedAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Select Connected (Ctrl+Shift+C)", None, QtGui.QApplication.UnicodeUTF8))
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
    win.selectLockAction.setIconText(QtGui.QApplication.translate("MainWindow", "Lock", None, QtGui.QApplication.UnicodeUTF8))
    win.selectLockAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Selection Lock (Ctrl+L)", None, QtGui.QApplication.UnicodeUTF8))
    win.selectLockAction.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+L", None, QtGui.QApplication.UnicodeUTF8))

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
    
    win.rosettaSetupAction.setText(QtGui.QApplication.translate(
        "MainWindow", " Rosetta", None, QtGui.QApplication.UnicodeUTF8))
    win.rosettaSetupAction.setIconText(QtGui.QApplication.translate(
        "MainWindow", "Rosetta", None, QtGui.QApplication.UnicodeUTF8))
    win.rosettaSetupAction.setToolTip(QtGui.QApplication.translate(
        "MainWindow", "Rosetta", None, QtGui.QApplication.UnicodeUTF8))
    
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

    win.helpWhatsThisAction.setText(QtGui.QApplication.translate("MainWindow", "Enter \"What\'s This\" help mode", None, QtGui.QApplication.UnicodeUTF8))
    win.helpWhatsThisAction.setIconText(QtGui.QApplication.translate("MainWindow", "What\'s This", None, QtGui.QApplication.UnicodeUTF8))
    win.helpGraphicsCardAction.setText(QtGui.QApplication.translate("MainWindow", "Graphics Card Info...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpGraphicsCardAction.setIconText(QtGui.QApplication.translate("MainWindow", "Graphics Card Info", None, QtGui.QApplication.UnicodeUTF8))

    win.helpMouseControlsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Mouse Controls...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpMouseControlsAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Mouse Controls", None, QtGui.QApplication.UnicodeUTF8))
    win.helpKeyboardShortcutsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Keyboard Shortcuts...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpKeyboardShortcutsAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Keyboard Shortcuts", None, QtGui.QApplication.UnicodeUTF8))
    win.helpSelectionShortcutsAction.setIconText(QtGui.QApplication.translate("MainWindow", "Selection Shortcuts...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpSelectionShortcutsAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Selection Shortcuts", None, QtGui.QApplication.UnicodeUTF8))

    win.helpTutorialsAction.setText(QtGui.QApplication.translate("MainWindow", "NanoEngineer-1 Tutorials...", None, QtGui.QApplication.UnicodeUTF8))
    win.helpTutorialsAction.setIconText(QtGui.QApplication.translate("MainWindow", "NanoEngineer-1 Tutorials...", None, QtGui.QApplication.UnicodeUTF8))

    # Other QActions not used in menus. These QActions are used in toolbars,
    # context menus, etc.
    win.viewDefviewAction.setText(QtGui.QApplication.translate("MainWindow", "Orientations", None, QtGui.QApplication.UnicodeUTF8))
    win.viewDefviewAction.setIconText(QtGui.QApplication.translate("MainWindow", "Orientations", None, QtGui.QApplication.UnicodeUTF8))
    win.viewDefviewAction.setToolTip(QtGui.QApplication.translate("MainWindow", "Default Views", None, QtGui.QApplication.UnicodeUTF8))

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

    win.setStereoViewAction.setText(
        QtGui.QApplication.translate(
            "MainWindow", "Stereo View",
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
