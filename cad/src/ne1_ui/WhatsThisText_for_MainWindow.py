# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
WhatsThisText_for_MainWindow.py

This file provides functions for setting the "What's This" and tooltip text
for widgets in the NE1 Main Window, except widgets in Property Managers.

Edit WhatsThisText_for_PropertyManagers.py to set "What's This" and tooltip
text for widgets in the NE1 Property Managers.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Note: bruce 080210 split whatsthis_utilities.py out of this file
into their own new file. 

To do:
- Change the heading for all Display Style actions from "Display <ds>" to
"Apply <ds> Display Style to the selection". Change tooltips and wiki help
pages as well.
- Replace current text string name with "_text" (like "Open File" example)
"""

from PyQt4.Qt import QWhatsThis

def createWhatsThisTextForMainWindowWidgets(win):
    """
    Adds the "What's This" help text to items found in the NE1 mainwindow
    toolbars and menus .
    
    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    
    @note: Property Managers specify "What's This" text for their own widgets, 
           usually in a method called add_whats_this_text(), not in this file. 
    """

    #
    # File Toolbar
    #

    # Open File
    _text = \
        "<u><b>Open File</b></u>    (Ctrl + O)"\
        "<p><img source=\"ui/actions/File/Open.png\"><br> "\
        "Opens a new file."\
        "</p>"

    win.fileOpenAction.setWhatsThis( _text )
    # Import File

    fileImportText = \
        "<u><b>Open Babel</b></u>"\
        "<p>"\
        "Imports a file of any chemical file format supported by "\
        "<b>Open Babel</b> into the current Part."\
        "</p>"

    win.fileImportOpenBabelAction.setWhatsThis(fileImportText)
    
    
    # Close File
    fileCloseAction = \
        "<b>Close and begin a new model</b>"\
        "<p>"\
        "Close the .mmp file currently being edited and loads a new one "\
        "</p>"

    win.fileCloseAction.setWhatsThis(fileCloseAction)
    
    
    #Export File 
    fileExportText = \
        "<u><b>Open Babel</b></u>"\
        "<p>"\
        "Exports the current part in any chemical file format "\
        "supported by <b>Open Babel</b>. Note that exclusive "\
        "features of NanoEngineer-1 are not saved to the exported file."\
        "</p>"

    win.fileExportOpenBabelAction.setWhatsThis(fileExportText)

    # Save File

    fileSaveText = \
        "<u><b>Save File</b></u>     (Ctrl + S) "\
        "<p>"\
        "<img source=\"ui/actions/File/Save.png\"><br> "\
        "Saves the current file."\
        "</p>"

    win.fileSaveAction.setWhatsThis( fileSaveText )
    
    # Save File As

    fileSaveAsText = \
        "<b>Save File As</b>"\
        "<p>"\
        "Allows the user to save the current .mmp file with a new name or."\
        "in a different location"\
        "</p>"

    win.fileSaveAsAction.setWhatsThis( fileSaveAsText )
    
    # Import Molcular Machine Part

    fileInsertMmpActionText = \
        "<b> Molecular Machine Part</b>"\
        "<p>"\
        "<img source=\"ui/actions/Insert/Molecular_Machine_Part.png\"><br> "\
        "Inserts an existing .mmp file into the current part."\
        "</p>"

    win.fileInsertMmpAction.setWhatsThis( fileInsertMmpActionText )
    
    # Import Protein Data Bank File

    fileInsertPdbActionText = \
        "<b> Protein Databank File</b>"\
        "<p>"\
        "Inserts an existing .pdb file into the current part."\
        "</p>"

    win.fileInsertPdbAction.setWhatsThis( fileInsertPdbActionText )
    
    # Import AMBER .in file

    fileInsertInActionText = \
        "<b> AMBER .in file fragment</b>"\
        "<p>"\
        "Inserts a fragment of an AMBER .in file into the current part.<p>"\
        "The fragment should just contain the lines defining the actual z-matrix.  "\
        "Loop closure bonds are not created, nor are bond orders inferred."\
        "</p>"

    win.fileInsertInAction.setWhatsThis( fileInsertInActionText )
    
    # Export Protein Data Bank File

    fileExportPdbActionText = \
        "<b> Export Protein Databank File</b>"\
        "<p>"\
        "Saves the current .mmp model as a Protein Databank File"\
        "</p>"

    win.fileExportPdbAction.setWhatsThis( fileExportPdbActionText )

 # Export Jpeg File

    fileExportJpgActionText = \
        "<b> Export JPEG File</b>"\
        "<p>"\
        "Saves the current .mmp model as a JPEG File"\
        "</p>"

    win.fileExportJpgAction.setWhatsThis( fileExportJpgActionText )

    # Export PNG File

    fileExportPngActionText = \
        "<b> Export PNG File</b>"\
        "<p>"\
        "Saves the current .mmp model as a PNG File"\
        "</p>"

    win.fileExportPngAction.setWhatsThis( fileExportPngActionText )

    # Export POV-ray File

    fileExportPovActionText = \
        "<b> Export POV-Ray File</b>"\
        "<p>"\
        "Saves the current .mmp model as a POV-Ray File"\
        "</p>"

    win.fileExportPovAction.setWhatsThis( fileExportPovActionText )
    
    # Export POV-ray File

    fileExportAmdlActionText = \
        "<b> Export Animation Master Model</b>"\
        "<p>"\
        "Saves the current .mmp model as an Animation Master Model File"\
        "</p>"

    win.fileExportAmdlAction.setWhatsThis( fileExportAmdlActionText )
    
    # Exit

    fileExitActionText = \
        "<b> Exit NanoEngineer-1</b>"\
        "<p>"\
        "Closes NanoEngineer-1"\
        "<p>"\
        "You will be prompted to save any current changes to the .mmp file"\
        "</p>"

    win.fileExitAction.setWhatsThis( fileExitActionText )



    #
    # Edit Toolbar
    #

    # Make Checkpoint ###

    editMakeCheckpointText = \
        "<u><b>Make Checkpoint</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Edit/Make_CheckPoint.png\"><br> "\
        "Make Undo checkpoint."\
        "</p>"

    win.editMakeCheckpointAction.setWhatsThis( editMakeCheckpointText )

    # Automatic Checkpointing ### [minor changes, bruce 060319]

    editAutoCheckpointingText = \
        "<u><b>Automatic Checkpointing</b></u>"\
        "<p>"\
        "Enables/Disables <b>Automatic Checkpointing</b>. When enabled, "\
        "the program maintains the Undo stack automatically.  When disabled, "\
        "the user is required to manually create Undo checkpoints using the "\
        "<b>Make Checkpoint</b> button: "\
        "</p>"\
        "<p><img source=\"ui/actions/Edit/Make_CheckPoint.png\">"\
        "</p>"\
        "<p><b>Automatic Checkpointing</b> can impact program performance. "\
        "By disabling Automatic Checkpointing, the program will run faster. "\
        "</p>"\
        "<p><b><i>Remember that you must make your own Undo checkpoints "\
        "manually when Automatic Checkpointing is disabled.</i></b>"\
        "</p>"

    win.editAutoCheckpointingAction.setWhatsThis( editAutoCheckpointingText )

    # Clear Undo Stack ### [minor changes, bruce 060319]

    editClearUndoStackText = \
        "<u><b>Clear Undo Stack</b></u>"\
        "<p>"\
        "Clears all checkpoints on the Undo and Redo "\
        "stacks, freeing up memory."\
        "</p>"

    win.editClearUndoStackAction.setWhatsThis( editClearUndoStackText )

    # Undo

    editUndoText = \
        "<u><b>Undo</b></u>     (Ctrl + Z) "\
        "<p>"\
        "<img source=\"ui/actions/Edit/Undo.png\"><br> "\
        "Reverses the last edit or command which changed structure "\
        "or selection. "\
        "</p>" 
    #bruce 060317 revised this text to reflect 
    #what it does in A7; 060320 added 1421-not-fixed warning

    win.editUndoAction.setWhatsThis( editUndoText )

    win.editUndoText = editUndoText #bruce 060317 to help fix bug 1421 in 
                                    #Undo whatsthis wiki help link

    # Redo

    from platform_dependent.PlatformDependent import is_macintosh
    if is_macintosh():
        redo_accel = "(Ctrl + Shift + Z)" # note: this is further 
                                          #modified (Ctrl -> Cmd) by other code
        # changing this is partly redundant with code in undo*.py, 
        #but as of 060317 it's desirable in editRedoText too
    else:
        redo_accel = "(Ctrl + Y)"

    editRedoText = \
        "<u><b>Redo</b></u>     %s<br> "\
        "<img source=\"ui/actions/Edit/Redo.png\"> <br>"\
        "Restores a change which was undone using the Undo command."\
        "<br><font color=\"#808080\">"\
        "</p>" \
        % redo_accel
    
    # This "known bug" (below) is no longer a bug, at least it works on Windows.
    # I'll ask someone with a MacOSX machine to test. --Mark 2008-05-05.
    
        #"Known bug: the link to wiki help for Redo "\
        #"only works if you got this popup from the Edit menu item "\
        #"for Redo, not from the Redo toolbutton. </font>"\
        #"</p>" \
        #% redo_accel
        #bruce 060317 revised this text to be more accurate, and split 
        #out redo_accel; 060320 added 1421-not-fixed warning

    win.editRedoAction.setWhatsThis( editRedoText )

    win.editRedoText = editRedoText #bruce 060317 to help fix bug 1421 
                                    #in Redo whatsthis wiki help link

    # Cut

    editCutText =  \
        "<u><b>Cut</b></u>     (Ctrl + X) "\
        "<p>"\
        "<img source=\"ui/actions/Edit/Cut.png\"><br> "\
        "Removes the selected object(s) and stores the cut data on the"\
        "clipboard."\
        "</p>"

    win.editCutAction.setWhatsThis( editCutText )

    # Copy

    editCopyText = \
        "<u><b>Copy</b></u>     (Ctrl + C) "\
        "<p>"\
        "<img source=\"ui/actions/Edit/Copy.png\"><br> "\
        "Places a copy of the selected chunk(s) on the clipboard "\
        "while leaving the original chunk(s) unaffected."\
        "</p>"

    win.editCopyAction.setWhatsThis( editCopyText )

    # Paste

    editPasteText = \
        "<u><b>Paste</b></u>     (Ctrl + V) "\
        "<p>"\
        "<img source=\"ui/actions/Edit/Paste_On.png\"><br> "\
        "<b>Paste</b> places the user in <b>Build</b> mode "\
        "where copied chunks on the clipboard can be pasted into "\
        "the model by double clicking in empty space. If the "\
        "current clipboard chunk has a <b><i>hotspot</i></b>, "\
        "it can be bonded to another chunk by single clicking on "\
        "one of the chunk's bondpoints."\
        "</p>"\
        "<p>A <b><i>Hotspot</i></b> is a green bondpoint on a "\
        "clipboard chunk indicating it will be the active "\
        "bondpoint which will connect to another chunk's bondpoint. "\
        "To specify a hotspot on the clipboard chunk, click on one "\
        "of its bondpoints in the <b><i>MMKit's Thumbview</i></b>."\
        "</p>"

    win.editPasteAction.setWhatsThis( editPasteText )

    # Paste From Clipboard
    
    pasteFromClipboardText = \
        "<u><b>Paste From Clipboard</b></u> "\
        "<p>"\
        "<img source=\"ui/actions/properties manager/clipboard-full.png\">"\
        "<br> "\
        "Allows the user to preview the contents of the "\
        "clipboard and past items into the Workspace."\
        "The preview window also allows the user to set "\
        "hot spots on chunks."\
        "</p>"
     
    win.pasteFromClipboardAction.setWhatsThis( pasteFromClipboardText )
    
    win.editDnaDisplayStyleAction.setWhatsThis(
        """<b>Edit DNA Display Style</b>
        <p>
        <img source=\"ui/actions/Edit/EditDnaDisplayStyle.png\">
        <br>
        Edit the DNA Display Style settings used whenever the <b>Global Display
        Style</b> is set to <i>DNA Cylinder</i>. These settings also apply
        to DNA strands and segments that have had their display style set
        to <i>DNA Cylinder</i>.
        </p>""")
    
    win.editProteinDisplayStyleAction.setWhatsThis(
        """<b>Edit Protein Display Style</b>
        <p>
        <img source=\"ui/actions/Edit/EditProteinDisplayStyle.png\">
        <br>
        Edit the Protein Display Style settings used whenever the <b>Global Display
        Style</b> is set to <i>Protein</i>.
        </p>""") 
   
    #Rename (deprecated by Rename Selection)
    EditrenameActionText = \
        "<u><b>Rename</b></u> "\
        "<p>"\
        "<img source=\"ui/actions/Edit/Rename.png\">"\
        "<br> "\
        "Allows the user to rename the selected chunk "\
        "</p>"
     
    win.editRenameAction.setWhatsThis( EditrenameActionText )
    
    #Rename selection
    _text = \
        "<u><b>Rename Selection</b></u> "\
        "<p>"\
        "<img source=\"ui/actions/Edit/Rename.png\">"\
        "<br> "\
        "Rename the selected object(s). Only leaf nodes in the model tree are "\
        "renamed. Specifically, group nodes are not renamed, even if they are "\
        "selected)."\
        "</p>"\
        "To uniquely name multiple objects, include the <b>#</b> character "\
        "at the end of the name. This (re)numbers the selected objects."\
        "</p>"
     
    win.editRenameSelectionAction.setWhatsThis( _text )
    
    #editAddSuffixAction
    EditeditAddSuffixActionActionText = \
        "<u><b>Add Suffix</b></u> "\
        "<p>"\
        "<img source=\"ui/actions/Edit/Add_Suffix.png\">"\
        "<br> "\
        "Add suffix to the name of the selected object(s)."\
        "</p>"
     
    win.editAddSuffixAction.setWhatsThis( EditeditAddSuffixActionActionText )
    
    # Translate

    toolsMoveMoleculeActionText = \
        "<u><b>Translate</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Properties Manager/"\
        "Translate_Components.png\">"\
        "<br> "\
        "Activates <b>Move Chunks</b> mode, allowing "\
        "you to select, move and rotate one or more "\
        "chunks with the mouse. Displays the Translate commands of the Move "\
        "Properties Manager."\
        "</p>"

    win.toolsMoveMoleculeAction.setWhatsThis( toolsMoveMoleculeActionText )

    rotateComponentsActionText = \
        "<u><b>Rotate Chunk</b></u> "\
        "<p>"\
        "<img source=\"ui/actions/properties manager/Rotate_Components.png\">"\
        "<br> " \
        "Activates <b>Move Chunks</b> mode, allowing you to select, move and "\
        "rotate one or more chunks with the mouse. Displays the Rotate "\
        "commands of the Move Properties Manager." \
        "</p>"

    win.rotateComponentsAction.setWhatsThis( rotateComponentsActionText )
    
    # Delete

    editDeleteText =  \
        "<u><b>Delete</b></u>     (DEL) "\
        "<p>"\
        "<img source=\"ui/actions/Edit/Delete.png\"><br> "\
        "Deletes the selected object(s).  "\
        "For this Alpha release, deleted objects may "\
        "be permanently lost, or they might be recoverable "\
        "using Undo."\
        "</p>"
        #bruce 060212 revised above text (and fixed spelling error); 
        #should be revised again before A7 release

    win.editDeleteAction.setWhatsThis( editDeleteText )

    
    # Color Scheme
    
    _text = \
        "<u><b>Color Scheme</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/ColorScheme.png\"><br> "\
        "Edit and save/restore favorite NanoEngineer-1 color schemes "\
        "including background color, selection/highlight color, etc."\
        "</p>"
    win.colorSchemeAction.setWhatsThis( _text )
    
    # Lighting Scheme
    
    _text = \
        "<u><b>Lighting Scheme</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/LightingScheme.png\"><br> "\
        "Edit and save/restore favorite NanoEngineer-1 lighting schemes."\
        "</p>"
    win.lightingSchemeAction.setWhatsThis( _text )
    
    #Preferences Dialog

    editPrefsText = \
        "<u><b>Preferences Dialog</b></u>"\
        "<p>"\
        "Allows you to edit various user preferences "\
        "such as changing atom, bond display properties,"\
        "lighting, background color, window position and"\
        "size, plugins etc. </p>"
    win.editPrefsAction.setWhatsThis( editPrefsText )
    
    #
    # View Toolbar
    #

    # Home View

    setViewHomeActionText = \
        "<u><b>Home</b></u>     (Home)"\
        "<p>"\
        "<img source=\"ui/actions/View/Modify/Home.png\"><br>"\
        "When you create a new model, it appears in a "\
        "default view orientation (FRONT view). When you "\
        "open an existing model, it appears in the "\
        "orientation it was last saved.  You can change the "\
        "default orientation by selecting <b>Set Home View "\
        "to Current View</b> from the <b>View</b> menu."\
        "</p>"

    win.setViewHomeAction.setWhatsThis( setViewHomeActionText )

    # Zoom to fit

    setViewFitToWindowActionText = \
        "<u><b>Zoom to Fit</b></u>"\
        "<p><img source=\"ui/actions/View/Modify/Zoom_To_Fit.png\"><br> "\
        "Refits the model to the screen so you can "\
        "view the entire model."\
        "</p>"

    win.setViewFitToWindowAction.setWhatsThis( setViewFitToWindowActionText )   

    # Recenter

    setViewRecenterActionText = \
        "<u><b>Recenter</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Modify/Recenter.png\"><br> "\
        "Changes the view center and zoom factor so "\
        "that the origin is in the center of the view "\
        "and you can view the entire model."\
        "</p>"

    win.setViewRecenterAction.setWhatsThis( setViewRecenterActionText )       

    # Zoom to Area (used to be Zoom Tool). Mark 2008-01-29.

    setzoomToAreaActionText = \
        "<u><b>Zoom to Area</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Modify/ZoomToArea.png\"><br> "\
        "Allows the user to zoom into a specific area of "\
        "the model by specifying a rectangular area. "\
        "The area is specified by holding down the left button, "\
        "dragging the mouse, and then releasing the mouse button."\
        "</p>"\
        "Pressing the <b>Escape</b> key exits Zoom to Area and returns to the"\
        "previous command."\
        "</p>"\
        "<p>A mouse with a mouse wheel can also be used to "\
        "zoom in/out."\
        "</p>"\
        "<p>The keyboard can also be used to zoom in/out:"\
        "<br>- <b>Zoom in</b> by pressing the 'period' key ( '.' )."\
        "<br>- <b>Zoom out</b> by pressing the 'comma' key ( ',' )."\
        "</p>"

    win.zoomToAreaAction.setWhatsThis( setzoomToAreaActionText )
    
    # Zoom (In/Out)

    setzoomInOutActionText = \
        "<u><b>Zoom In/Out</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Modify/Zoom_In_Out.png\"><br> "\
        "Enters a temporary zoom mode that allows the user to zoom in or out "\
        "using the mouse. Press ESC or click this button again to exit "\
        "temporary zoom mode and return to the previous command."\
        "</p>"\
        "<p>- <b>Zoom in</b> by holding down the mouse button and pulling "\
        "the mouse closer (cursor moves down)."\
        "<br>- <b>Zoom out</b> by holding the mouse button and pushing "\
        "the mouse away (cursor moves up)."\
        "</p>"\
        "<p>A mouse with a mouse wheel can also be used to "\
        "zoom in/out."\
        "</p>"\
        "<p>The keyboard can also be used to zoom in/out:"\
        "<br>- <b>Zoom in</b> by pressing the 'period' key ( '.' )."\
        "<br>- <b>Zoom out</b> by pressing the 'comma' key ( ',' )."\
        "</p>"

    win.zoomInOutAction.setWhatsThis( setzoomInOutActionText )
    
    #Zoom To Selection
    
    setViewZoomtoSelectionActionText = \
        "<u><b>Zoom to Selection</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Modify/Zoom_To_Selection.png\"><br> "\
        " Zooms view to selected atoms or chunks. "\
        "</p>"
    
    win.setViewZoomtoSelectionAction.setWhatsThis\
       ( setViewZoomtoSelectionActionText )

    # Pan Tool

    setpanToolActionText = \
        "<u><b>Pan Tool</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Modify/Pan.png\"><br> "\
        "Allows X-Y panning using the left mouse button."\
        "</p>"\
        "Pressing the <b>Escape</b> key exits Pan Tool and returns to the"\
        "previous command."\
        "</p>"\
        "<p>Users with a 3-button mouse can pan the model at "\
        "any time by pressing the middle mouse button while "\
        "holding down the Shift key."\
        "</p>"

    win.panToolAction.setWhatsThis( setpanToolActionText )

    # Rotate Tool

    setrotateToolActionText = \
        "<u><b>Rotate Tool</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Modify/Rotate.png\"><br> "\
        "Allows free rotation using the left mouse button."\
        "</p>"\
        "<p>Holding down the <b>A</b> key activates auto-rotation, which will "\
        "continue rotation after releasing the mouse button (try it!)."\
        "Pressing the <b>Escape</b> key exits Rotate Tool and returns to the"\
        "previous command."\
        "</p>"\
        "<p>Users with a 3-button mouse can rotate the "\
        "model at any time by pressing "\
        "the middle mouse button and dragging "\
        "the mouse."\
        "</p>"

    win.rotateToolAction.setWhatsThis( setrotateToolActionText )
    
    #Standard Views
    
    standardViews_btnText = \
        "<u><b>Standard Views</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Standard_Views.png\"><br> "\
        "Displays the Standards Views Menu "\
        "</p>"

    win.standardViews_btn.setWhatsThis( standardViews_btnText )
    
    # Orthographic Projection
    
    setViewOrthoActionText = \
        "<u><b>Orthographic Projection</b></u>"\
        "<p>"\
        "Sets nonperspective (or parallel) projection, "\
        "with no foreshortening."\
        "</p>"

    win.setViewOrthoAction.setWhatsThis( setViewOrthoActionText )

    # Perspective Projection

    setViewPerspecActionText = \
        "<u><b>Perspective Projection</b></u>"\
        "<p>"\
        "Set perspective projection, drawing objects "\
        "slightly larger that are closer to the viewer."\
        "</p>"

    win.setViewPerspecAction.setWhatsThis( setViewPerspecActionText )

    # Normal To

    viewNormalToActionText = \
        "<u><b>Set View Normal To</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Set_View_Normal_To/\"><br> "\
        "Orients view to the normal vector of the plane "\
        "defined by 3 or more selected atoms, or a jig's "\
        "axis."\
        "</p>"

    win.viewNormalToAction.setWhatsThis( viewNormalToActionText )

    # Parallel To

    _text = \
        "<u><b>Set View Parallel To</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Set_View_Parallel_To.png\"><br> "\
        "Orients view parallel to the vector defined by "\
        "2 selected atoms."\
        "</p>"

    win.viewParallelToAction.setWhatsThis( _text ) 

    # Save Named View

    _text = \
        "<u><b>Save Named View</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Modify/Save_Named_View.png\"><br> "\
        "Saves the current view as a custom "\
        "<b>named view</b> and places it in "\
        "the Model Tree."\
        "</p>" \
        "<p>The view can be restored by selecting "\
        "<b>Change View</b> from its context "\
        "menu in the Model Tree."\
        "</p>"

    win.saveNamedViewAction.setWhatsThis( _text ) 

    # Front View

    _text = \
        "<u><b>Front View</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Front.png\"><br> "\
        "Orients the view to the Front View."\
        "</p>"

    win.viewFrontAction.setWhatsThis( _text )  

    # Back View

    _text = \
        "<u><b>Back View</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Back.png\"><br> "\
        "Orients the view to the Back View."\
        "</p>"

    win.viewBackAction.setWhatsThis( _text )     

    # Top View

    _text = \
        "<u><b>Top View</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Top.png\"><br> "\
        "Orients the view to the Top View."\
        "</p>"

    win.viewTopAction.setWhatsThis( _text )      

    # Bottom View

    _text = \
        "<u><b>Bottom View</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Bottom.png\"><br> "\
        "Orients the view to the Bottom View."\
        "</p>"

    win.viewBottomAction.setWhatsThis( _text )  

    # Left View

    _text = \
        "<u><b>Left View</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Left.png\"><br> "\
        "Orients the view to the Left View."\
        "</p>"

    win.viewLeftAction.setWhatsThis( _text )

    # Right View

    _text = \
        "<u><b>Right View</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Right.png\"><br> "\
        "Orients the view to the Right View."\
        "</p>"

    win.viewRightAction.setWhatsThis( _text )

    #Isometric View 

    _text = \
        "<u><b>IsometricView</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Isometric.png\"><br> "\
        "Orients the view to the Isometric View."\
        "</p>"

    win.viewIsometricAction.setWhatsThis( _text )

    # Flip View Vertically

    _text = \
        "<u><b>Flip View Vertically</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/FlipViewVert.png\"><br> "\
        "Flip the view vertically."\
        "</p>"

    win.viewFlipViewVertAction.setWhatsThis( _text )
    
    # Flip View Horizontally

    _text = \
        "<u><b>Flip View Horizontally</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/FlipViewHorz.png\"><br> "\
        "Flip the view horizontally."\
        "</p>"

    win.viewFlipViewHorzAction.setWhatsThis( _text )

    # Rotate View +90

    _text = \
        "<u><b>Rotate View +90</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Rotate_View_+90.png\"><br> "\
        "Increment the current view by 90 degrees "\
        "around the vertical axis."\
        "</p>"

    win.viewRotatePlus90Action.setWhatsThis( _text )

    # Rotate View -90

    _text = \
        "<u><b>Rotate View -90</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Rotate_View_-90.png\"><br> "\
        "Decrement the current view by 90 degrees "\
        "around the vertical axis."\
        "</p>"

    win.viewRotateMinus90Action.setWhatsThis( _text )

    # Orientation Window
    
    _text = \
        "<u><b>Orientation Window</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Modify/Orientation.png\"><br> "\
        "Opens the Orientation Menu "\
        "</p>"

    win.viewOrientationAction.setWhatsThis( _text ) 
    
    # Set Current View to Home View
    
    setViewHomeToCurrentActionText = \
        "<b>Set Current View to Home View</b>"\
        "<p>"\
        "Sets the current view displayed in the 3D graphics area to the Home View "\
        "</p>"

    win.setViewHomeToCurrentAction.setWhatsThis( setViewHomeToCurrentActionText )
    
    # Semi-Full Screen view 
    
    viewSemiFullScreenActionText = \
        "<b>Semi-Full Screen</b>"\
        "<p>"\
        "Sets display to Semi-Full Screen "\
        "</p>"

    win.viewSemiFullScreenAction.setWhatsThis( viewSemiFullScreenActionText )
    
    # Display Rulers
    
    viewRulersActionText = \
        "<b>Display Rulers</b>"\
        "<p>"\
        "Toggles the display of 3D graphics area rulers"\
        "</p>"

    win.viewRulersAction.setWhatsThis( viewRulersActionText )
    
    # Display Reports
    
    viewReportsActionText = \
        "<b>Display Reports</b>"\
        "<p>"\
        "Toggles the display of the report window"\
        "</p>"

    win.viewReportsAction.setWhatsThis( viewReportsActionText )
    
    # Full Screen view 
    
    viewFullScreenActionText = \
        "<b>Full Screen</b>"\
        "<p>"\
        "Sets display to Full Screen "\
        "</p>"

    win.viewFullScreenAction.setWhatsThis( viewFullScreenActionText )
    

    # QuteMolX

    viewQuteMolActionText = \
        "<u><b>QuteMolX</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/QuteMol.png\"><br> "\
        "Opens the QuteMolX Properties Manager where the user can "\
        "alter rendering styles and launch QutemolX."\
        "</p>" \
        "QuteMolX must be installed and enabled as a "\
        "plug-in from <b>Preferences > Plug-ins</b> for "\
        "this feature to work." \
        "</p>"

    win.viewQuteMolAction.setWhatsThis( viewQuteMolActionText )

    # POV-Ray (was Raytrace Scene)

    viewRaytraceSceneActionText = \
        "<u><b>POV-Ray</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/Raytrace_Scene.png\"><br> "\
        "Raytrace the current scene using POV-Ray. "\
        "</p>" \
        "POV-Ray must be installed and enabled as "\
        "a plug-in from <b>Preferences > Plug-ins</b> "\
        "for this feature to work." \
        "</p>"

    win.viewRaytraceSceneAction.setWhatsThis( viewRaytraceSceneActionText )
   
    # Stereo View
    
    viewStereoViewActionText = \
        "<u><b>Stereo View</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Stereo_View.png\"><br> "\
        "Displays the Stereo View Property Manager "\
        "</p>"
    
    win.setStereoViewAction.setWhatsThis(viewStereoViewActionText)
   
    #
    # Insert toolbar
    #

    # Graphene

    insertGrapheneActionText = \
        "<u><b>Build Graphene</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Structures/Graphene.png\"><br> "\
        "Inserts a 2D sheet of graphene in the model "\
        "based on the current parameters in the "\
        "Property Manager. To preview the structure "\
        "based on the current parameters, click the "\
        "Preview button located at the top of the "\
        "Property Manager :<br> "\
        "<img source=\"ui/actions/Properties Manager/Preview.png\"> "\
        "</p>"

    win.insertGrapheneAction.setWhatsThis(insertGrapheneActionText )

        
    # Build Nanotube 

    _text = \
        "<u><b>Build Nanotube</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Structures/Nanotube.png\"> <br>"\
        "Inserts a carbon nanotube (CNT) or boron nitride nanotube (BNNT) "\
        "in the 3D graphics area by defining the two endpoints of the "\
        "nanotube."\
        "</p>"

    win.buildNanotubeAction.setWhatsThis( _text )

    # Build DNA

    buildDnaActionText = \
        "<u><b>Build DNA</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Structures/DNA.png\"><br> "\
        "Invokes the interactive DNA Builder."\
        "</p>"

    win.buildDnaAction.setWhatsThis(buildDnaActionText )


   # Build Peptide
   
    buildPeptideActionText = \
        "<u><b>Build Peptide</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Structures/Peptide.png\"><br> "\
        "Displays peptide property manager where peptides can be created from"\
        " a list of amino acids, click the Preview button "\
        "located at the top of the Property Manager :<br> "\
        "<img source=\"ui/actions/Properties Manager/Preview.png\"> "\
        "</p>"

    win.insertPeptideAction.setWhatsThis(buildPeptideActionText )
    
    # POV-Ray Scene

    insertPovraySceneActionText = \
        "<u><b>Insert POV-Ray Scene</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/POV-Ray_Scene.png\"><br> "\
        "Inserts a POV-Ray Scene file based on the "\
        "current model and viewpoint. "\
        "</p>"

    win.insertPovraySceneAction.setWhatsThis(insertPovraySceneActionText )

    # Part Library
    
    _text = \
        "<u><b>Part Library</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Insert/Part_Library.png\"><br> "\
        "Prompts the user to select an .mmp file from the NanoEngineer-1 "\
        "Part Library to be inserted into the current part. "\
        "</p>"
    win.partLibAction.setWhatsThis( _text )
    
    # Comment

    insertCommentActionText = \
        "<u><b>Insert Comment</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Insert/Comment.png\"><br> "\
        "Inserts a comment in the current part. "\
        "</p>"

    win.insertCommentAction.setWhatsThis(insertCommentActionText )
    
    #Insert Plane
    referencePlaneActionText = \
        "<b>Insert Reference Plane</b>"\
        "<p>"\
        "<img source=\"ui/actions/Insert/Reference Geometry/Plane.png\"><br> "\
        "Inserts a reference plane into the 3D graphics area based on the. "\
        "current visual orientation and user specified parameters"\
        "</p>"

    win.referencePlaneAction.setWhatsThis(referencePlaneActionText )
    

    #
    # Display toolbar
    #

    # Display Default 

    dispDefaultActionText = \
        "<u><b>Display Default</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/Default.png\"><br> "\
        "Changes the <i>display setting</i> of the selection (i.e. selected "\
        "atoms, chunks, DNA, etc.) to <b>Default</b>. Objects with their "\
        "display setting set to <b>Default</b> are rendered in the "\
        "<b>Global Display Style</b>. "\
        "</p>"\
        "<p>The current <b>Global Display Style</b> is displayed in the "\
        "status bar in the lower right corner of the main window and can "\
        "be changed from there."\
        "</p>"

    win.dispDefaultAction.setWhatsThis(dispDefaultActionText )

    # Display Invisible

    dispInvisActionText = \
        "<u><b>Display Invisible</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/Invisible.png\"><br> "\
        "Changes the <i>display setting</i> of selected atoms "\
        "or chunks to <b>Invisible</b>, making them invisible."\
        "</p>"\
        "<p>If no atoms or chunks are selected, then this "\
        "action will change the <b>Current Display Mode</b> "\
        "of the 3D workspace to <b>Invisible</b>. All chunks "\
        "with their display setting set to <b>Default</b> will"\
        " inherit this display property."\
        "</p>"

    win.dispInvisAction.setWhatsThis(dispInvisActionText )       

    # Display Lines
    dispLinesActionText = \
        "<u><b>Display Lines</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/Lines.png\"><br> "\
        "Changes the <i>display setting</i> of the selection (i.e. selected "\
        "atoms, chunks, DNA, etc.) to <b>Lines</b> display style. "\
        "Only bonds are rendered as colored lines. "\
        "</p>"\
        "<p>The thickness of bond lines can be changed from the <b>Bonds</b> "\
        "page of the <b>Preferences</b> dialog."\
        "</p>"

    win.dispLinesAction.setWhatsThis(dispLinesActionText )  

    # Display Tubes

    dispTubesActionText = \
        "<u><b>Display Tubes</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/Tubes.png\"><br> "\
        "Changes the <i>display setting</i> of the selection (i.e. selected "\
        "atoms, chunks, DNA, etc.) to <b>Tubes</b> display style. "\
        "Atoms and bonds are rendered as colored tubes."\
        "</p>"
    
    win.dispTubesAction.setWhatsThis(dispTubesActionText )  

    # Display Ball and Stick

    dispBallActionText = \
        "<u><b>Display Ball and Stick</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/Ball_and_Stick.png\"><br> "\
        "Changes the <i>display setting</i> of the selection (i.e. selected "\
        "atoms, chunks, DNA, etc.) to <b>Ball and Stick</b> display style. "\
        "Atoms are rendered as spheres and bonds are rendered as narrow "\
        "cylinders."\
        "</p>"\
        "<p>The scale of the spheres and cylinders can be "\
        "changed from the <b>Atoms</b> and <b>Bonds</b> pages "\
        "of the <b>Preferences</b> dialog."\
        "</p>"

    win.dispBallAction.setWhatsThis(dispBallActionText ) 

    # Display CPK # [bruce extended and slightly corrected text, 060307]

    _text = \
        "<u><b>Display CPK</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/CPK.png\"><br> "\
        "Changes the <i>display setting</i> of the selection (i.e. selected "\
        "atoms, chunks, DNA, etc.) to <b>CPK</b> display style.  Atoms are "\
        "rendered as spheres with a size equal to 0.775 of their VdW radius, "\
        "corresponding to a contact force of approximately 0.1 nN with "\
        "neighboring nonbonded atoms. Bonds are not rendered."\
        "</p>"\
        "<p>The scale of the spheres can be changed from the "\
        "<b>Atoms</b> page of the <b>Preferences</b> dialog."\
        "</p>"

    win.dispCPKAction.setWhatsThis( _text )
    
    # DNA Cylinder
    
    _text = \
        "<u><b>Display DNA Cylinder</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/DNACylinder.png\"><br> "\
        "Changes the <i>display setting</i> of the selection (i.e. selected "\
        "DNA, etc.) to <b>DNA Cylinder</b> display style.  DNA are rendered "\
        "based on the settings found in the <b>DNA Cylinder Display Style "\
        "Options</b> in the <b>DNA</b> page of the <b>Preferences</b> dialog."\
        "</p>"\
        "<p>Atoms and bonds are not rendered. This is considered a bug that "\
        "will be fixed soon."\
        "</p>"

    win.dispDnaCylinderAction.setWhatsThis( _text )
    
    # Hide (Selection)

    _text = \
        "<u><b>Hide</b></u>    "\
        "<p>"\
        "<img source=\"ui/actions/View/Display/Hide.png\"><br> "\
        "Hides the current selection. Works on atoms, chunks and/or any "\
        "other object that can be hidden."\
        "</p>"

    win.dispHideAction.setWhatsThis( _text )
    
    # Unhide (Selection)

    unhideActionText = \
        "<u><b>Unhide</b></u>    "\
        "<p>"\
        "<img source=\"ui/actions/View/Display/Unhide.png\"><br> "\
        "Unhides the current selection. Works on atoms, chunks and/or any "\
        "other object that can be hidden.</p>"\
        "<p>"\
        "If a selected chunk is both hidden <i>and</i> contains invisible "\
        "atoms, then the first unhide operation will unhide the chunk and "\
        "the second unhide operation will unhide the invisible atoms inside "\
        "the chunk."\
        "</p>"

    win.dispUnhideAction.setWhatsThis(unhideActionText)

    # Display Cylinder

    dispCylinderActionText = \
        "<u><b>Display Cylinder</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/Cylinder.png\"><br> "\
        "Changes the <i>display setting</i> of selected "\
        "chunks to <b>Cylinder</b> mode.  Chunks are "\
        "rendered as cylinders. "\
        "</p>"\
        "<p>If no chunks are selected, then this action "\
        "will change the <b>Current Display Mode</b> of "\
        "the 3D workspace to <b>Cylinder</b>. All chunks "\
        "with their display setting set to <b>Default</b> "\
        "will inherit this display property."\
        "</p>"

    win.dispCylinderAction.setWhatsThis(dispCylinderActionText )

    # Display Surface

    dispSurfaceActionText = \
        "<u><b>Display Surface</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/View/Display/Surface.png\"><br> "\
        "Changes the <i>display setting</i> of selected "\
        "chunks to <b>Surface</b> mode.  Chunks are "\
        "rendered  as a smooth surface."\
        "</p>"\
        "<p>If no chunks are selected, then this action "\
        "will change the <b>Current Display Mode</b> of "\
        "the 3D workspace to <b>Surface</b>. All chunks "\
        "with their display setting set to <b>Default</b>"\
        " will inherit this display property."\
        "</p>"

    win.dispSurfaceAction.setWhatsThis(dispSurfaceActionText )

    # Reset Chunk Color
    
    dispResetChunkColorText = \
        "<u><b>Reset Chunk Color</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Edit/Reset_Chunk_Color.png\"><br> "\
        "Resets (removes) the user defined color of all selected chunks. "\
        "All atoms and bonds in the chunk are rendered in their normal "\
        "element colors."\
        "</p>"

    win.resetChunkColorAction.setWhatsThis(dispResetChunkColorText )

    # Reset Atoms Display

    dispResetAtomsDisplayText = \
        "<u><b>Reset Atoms Display</b></u>"\
        "Renders the  selected atoms (or the atoms in the"\
        "selected chunks) with the same display style as "\
        "that of their parent chunk"

    win.dispResetAtomsDisplayAction.setWhatsThis(dispResetAtomsDisplayText)

    # Show Invisible Atoms

    dispShowInvisAtomsText = \
        "<u><b>Show Invisible Atoms</b></u>"\
        "Renders the  selected atoms (or the atoms in the "\
        "selected chunks)  with the same display style as "\
        " their parent chunk. However, if the parent chunk "\
        "is set as invisible, this feature will not work." 

    win.dispShowInvisAtomsAction.setWhatsThis(dispShowInvisAtomsText)

    #Element Color Settings Dialog

    dispElementColorSettingsText = \
        "<u><b>Element Color Settings Dialog</b></u>"\
        "Element colors can be manually changed " \
        "using this dialog. Also, the user can load"\
        "or save the element colors"

    win.dispElementColorSettingsAction.setWhatsThis\
       (dispElementColorSettingsText)

    #
    # Select toolbar
    #

    # Select All

    selectAllActionText = \
        "<u><b>Select All</b></u> (Ctrl + A)"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Select/Select_All.png\"><br> "\
        "When in <b>Build</b> mode, this will select all the "\
        "atoms in the model.  Otherwise, this will select all "\
        "the chunks in the model."\
        "</p>"

    win.selectAllAction.setWhatsThis(selectAllActionText )

    # Select None

    selectNoneActionText = \
        "<u><b>Select None</b></u></p>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Select/Select_None.png\"><br> "\
        "Unselects everything currently selected. "\
        "</p>"

    win.selectNoneAction.setWhatsThis(selectNoneActionText )

    # InvertSelection

    selectInvertActionText = \
        "<u><b>Invert Selection</b></u> (Ctrl + Shift + I)"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Select/Select_Invert.png\"><br> "\
        "Inverts the current selection."\
        "</p>"

    win.selectInvertAction.setWhatsThis(selectInvertActionText )

    # Select Connected

    selectConnectedActionText = \
        "<u><b>Select Connected</b></u> (Ctrl + Shift + C)"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Select/Select_Connected.png\"><br> "\
        "Selects all the atoms that can be reached by "\
        "the currently selected atom via an unbroken "\
        "chain of bonds. </p>"\
        "<p>"\
        "<p>You can also select all connected atoms by "\
        "double clicking on an atom or bond while in "\
        "<b>Build</b> mode.</p>"

    win.selectConnectedAction.setWhatsThis(selectConnectedActionText )

    # Select Doubly

    selectDoublyActionText = \
        "<u><b>Select Doubly</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Select/Select_Doubly.png\"><br> "\
        "Selects all the atoms that can be reached from a "\
        "currently selected atom through two disjoint "\
        "unbroken chains of bonds.  Atoms singly connected "\
        "to this group and unconnected to anything else "\
        "are also included in the selection."\
        "</p>"

    win.selectDoublyAction.setWhatsThis(selectDoublyActionText )

    # Expand Selection

    selectExpandActionText = \
        "<u><b>Expand Selection</b></u>    (Ctrl + D)"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Select/Expand.png\"><br> "\
        "Selects any atom that is a neighbor of a "\
        "currently selected atom."\
        "</p>"

    win.selectExpandAction.setWhatsThis(selectExpandActionText )

    # Contract Selection

    selectContractActionText = \
        "<u><b>Contract Selection</b></u>    "\
        "(Ctrl + Shift + D)"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Select/Contract.png\"><br> "\
        "Deselects any atom that is a neighbor of a "\
        "non-picked atom or has a bondpoint."\
        "</p>"

    win.selectContractAction.setWhatsThis(selectContractActionText )
    
    # Selection Lock

    selectionLockActionText = \
        "<u><b>Selection Lock</b></u>    "\
        "(Ctrl + L)"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Select/Selection_Unlocked.png\">"\
        " (off) "\
        "<img source=\"ui/actions/Tools/Select/Selection_Locked.png\">"\
        " (on)<br> "\
        "Toggles the mouse <i>Selection Lock</i> on and off. </p>"\
        "<p>"\
        "When enabled, selection operations using the mouse (i.e. clicks and "\
        "drags) are disabled in the 3D graphics area. All other selection "\
        "commands available via toolbars, menus, the model tree and keyboard "\
        "shortcuts are not affected when the Selection Lock is turned on."\
        "</p>"

    win.selectLockAction.setWhatsThis(selectionLockActionText)
    
    #
    # Modify Toolbar
    #

    # Adjust Selection

    modifyAdjustSelActionText = \
        "<u><b>Adjust Selection</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Adjust_Selection.png\"><br> "\
        "Adjusts the atom and bond positions (<i>of the "\
        "selection</i>) to make the geometry more "\
        "realistic. The operations used to move the "\
        "atoms and bonds approximate molecular mechanics"\
        " methods."\
        "</p>"

    win.modifyAdjustSelAction.setWhatsThis(modifyAdjustSelActionText )

    # Adjust All

    modifyAdjustAllActionText = \
        "<u><b>Adjust All</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Adjust_All.png\"><br> "\
        "Adjusts the atom and bond positions (<i>of the"\
        " entire part</i>) to make the geometry of the "\
        " part more realistic. The operations used to "\
        "move the atoms and bonds approximate molecular "\
        "mechanics methods."\
        "</p>"

    win.modifyAdjustAllAction.setWhatsThis(modifyAdjustAllActionText )

    # Hydrogenate

    modifyHydrogenateActionText = \
        "<u><b>Hydrogenate</b></u>"\
        "<P>"\
        "<img source=\"ui/actions/Tools/Build Tools/Hydrogenate.png\"><br> "\
        "Adds hydrogen atoms to all the bondpoints in "\
        "the selection.</p>"

    win.modifyHydrogenateAction.setWhatsThis(modifyHydrogenateActionText )

    # Dehydrogenate

    modifyDehydrogenateActionText = \
        "<u><b>Dehydrogenate</b></u>"\
        "<P>"\
        "<img source=\"ui/actions/Tools/Build Tools/Dehydrogenate.png\"><br> "\
        "Removes all hydrogen atoms from the "\
        "selection.</p>"

    win.modifyDehydrogenateAction.setWhatsThis(modifyDehydrogenateActionText )     

    # Passivate

    modifyPassivateActionText = \
        "<u><b>Passivate</b></u>"\
        "<P>"\
        "<img source=\"ui/actions/Tools/Build Tools/Passivate.png\"><br> "\
        "Changes the types of incompletely bonded atoms "\
        "to atoms with the right number of bonds, using"\
        " atoms with the best atomic radius."\
        "</p>"

    win.modifyPassivateAction.setWhatsThis(modifyPassivateActionText )

    # Stretch

    modifyStretchActionText = \
        "<u><b>Stretch</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Tools/Stretch.png\"><br> "\
        "Stretches the bonds of the selected chunk(s).</p>"

    win.modifyStretchAction.setWhatsThis(modifyStretchActionText )

    # Delete Bonds

    modifyDeleteBondsActionText = \
        "<u><b>Cut Bonds</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Tools/Delete_Bonds.png\"><br> "\
        "Delete all bonds between selected and unselected atoms or chunks.</p>"

    win.modifyDeleteBondsAction.setWhatsThis(modifyDeleteBondsActionText )  

    # Separate/New Chunk

    modifySeparateActionText = \
        "<u><b>Separate</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Tools/Separate.png\"><br> "\
        "Creates a new chunk(s) from the currently "\
        "selected atoms. If the selected atoms belong to different "\
        "chunks, multiple new chunks are created.</p>"

    win.modifySeparateAction.setWhatsThis(modifySeparateActionText )  

    # New Chunk

    makeChunkFromSelectedAtomsActionText = \
        "<u><b>New Chunk</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Tools/New_Chunk.png\"><br>  "\
        "Creates a new chunk from the currently selected atoms. "\
        "All atoms end up in a single chunk.</p>"

    win.makeChunkFromSelectedAtomsAction.setWhatsThis\
       (makeChunkFromSelectedAtomsActionText ) 

    # Combine Chunks

    modifyMergeActionText = \
        "<u><b>Combine Chunks</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Tools/Combine_Chunks.png\"><br> "\
        "Combines two or more chunks into a single chunk.</p>"

    win.modifyMergeAction.setWhatsThis(modifyMergeActionText )  

    # Invert Chunks

    modifyInvertActionText = \
        "<u><b>Invert</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Tools/Invert.png\"><br> "\
        "Inverts the atoms of the selected chunks.</p>"

    win.modifyInvertAction.setWhatsThis(modifyInvertActionText )  

    # Mirror Selected Chunks

    #Note that the the feature name is intentionally kept "Mirror" instead of 
    #"Mirror Chunks" because 
    # in future we will support mirrroing atoms as well. -- ninad060814
    modifyMirrorActionText = \
        "<u><b>Mirror</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Tools/Mirror.png\"><br> "\
        "Mirrors the selected <b> chunks </b> about a "\
        "reference Grid or Plane.<br>"

    win.modifyMirrorAction.setWhatsThis(modifyMirrorActionText )  

    # Align to Common Axis

    modifyAlignCommonAxisActionText = \
        "<u><b>Align To Common Axis</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Tools/"\
        "AlignToCommonAxis.png\"><br> "\
        "Aligns one or more chunks to the axis of the first selected chunk. "\
        "You must select two or more chunks before using this feature."\
        "</p>"

    win. modifyAlignCommonAxisAction.setWhatsThis\
       ( modifyAlignCommonAxisActionText )

    #Center on Common Axis 
    modifyCenterCommonAxisActionText = \
        "<u><b>Center On Common Axis</b></u>"\
        "<p>"\
        "<b> Moves</b> all selected chunks to "\
        "the center of  the <b> first </b> "\
        "selected chunk and also <b>aligns</b> "\
        "them to the axis of the first one . You "\
        "must select two or more chunks before "\
        "using this feature. </p>" 

    win.modifyCenterCommonAxisAction.setWhatsThis\
       (modifyCenterCommonAxisActionText)

    #
    # Tools Toolbar
    #

    # Select Chunks

    toolsSelectMoleculesActionText = \
        "<u><b>Select Chunks</b></u><!-- [[Feature:Select Chunks Mode]] -->"\
        "<p>"\
        "<img source=\"ui/cursors/SelectArrowCursor.png\"><br> "\
        "<b>Select Chunks</b> allows you to select/unselect chunks with the "\
        "mouse.</p>"\
        "<p>"\
        "<b><u>Mouse/Key Combinations</u></b></p>"\
        "<p><b>Left Click/Drag</b> - selects a chunk(s).</p>"\
        "<p>"\
        "<b>Ctrl+Left Click/Drag</b> - removes chunk(s) from selection.</p>"\
        "<p>"\
        "<b>Shift+Left Click/Drag</b> - adds chunk(s) to selection."\
        "</p>"

    win.toolsSelectMoleculesAction.setWhatsThis\
       ( toolsSelectMoleculesActionText )

    # Build Atoms

    toolsDepositAtomActionText = \
        "<u><b>Build Atoms</b></u><!-- [[Feature:Build Atoms]] -->"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Structures/Atoms.png\"><br> "\
        "<b>Build Atoms</b> provides an interactive molecular modeler "\
        "that allows the user to easily build molecular structures one "\
        "atom at a time.</p>"

    win.toolsDepositAtomAction.setWhatsThis( toolsDepositAtomActionText )

    # Build Crystal 

    toolsCookieCutActionText = \
        "<u><b>Build Crystal</b></u><!-- [[Feature:Build Crystal Mode]] -->"\
        "<p>"\
        "<><img source=\"ui/actions/Tools/Build Structures/"\
        "Cookie_Cutter.png\"><br"\
        "<b>Build Crystal</b> provides tools for cutting "\
        "out multi-layered shapes from slabs of diamond "\
        "or lonsdaleite lattice.</p>"

    win.buildCrystalAction.setWhatsThis( toolsCookieCutActionText )

    # Tools > Extrude

    toolsExtrudeActionText = \
        "<u><b>Extrude</b></u><!-- [[Feature:Extrude Mode]] --><br>"\
        "<p>"\
        "<img source=\"ui/actions/Insert/Features/Extrude.png\"><br> "\
        "Activates <b>Extrude</b> mode, allowing the user to "\
        "create a rod or ring using one or more chunks as a repeating "\
        "unit.</p>"

    win.toolsExtrudeAction.setWhatsThis( toolsExtrudeActionText )

    # Fuse Chunks Mode

    toolsFuseChunksActionText = \
        "<u><b>Fuse Chunks Mode</b></u>"\
        "<!-- [[Feature:Fuse Chunks Mode]] -->"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Build Tools/Fuse_Chunks.png\"><br> "\
        "<b>Fuse Chunks</b> can be used to "\
        "interactively join two or more chunks by "\
        "dragging chunks around and fusing them "\
        "together. Two fusing options are "\
        "supported:<br><br> <b>Make Bonds</b> creates "\
        "bonds between the existing bondpoints of two "\
        "or more chunks.  Bondpoints are highlighted "\
        "and lines are drawn (and undrawn) as chunks "\
        "are dragged to indicate bonding relationships "\
        "between bondpoints. Bondpoints with "\
        "multiple bonding relationships are highlighted "\
        "in magenta to indicate that they cannot "\
        "make bonds.<br><br> <b>Fuse Atoms</b> fuses "\
        "pairs of overlapping atoms between chunks. "\
        "The set of overlapping atoms in the selected "\
        "chunk(s) are highlighted in green while the "\
        "set of atoms that will be deleted in "\
        "non-selected chunks are highlighted in dark "\
        "red. It is possible that deleted atoms will "\
        "not fuse properly, leaving bondpoints on the "\
        "selected chunk(s) atoms.  This is a bug.  To "\
        " help minimize this problem, try to get the "\
        "bonds of overlapping atoms oriented "\
        "similarly.<br>"\
        "</p>"

    win.toolsFuseChunksAction.setWhatsThis( toolsFuseChunksActionText )

    #
    # Simulator Toolbar
    #

    # Minimize Energy

    simMinimizeEnergyActionText = \
        "<u><b>Minimize Energy</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Minimize_Energy.png\"><br> "\
        "The potential energy of a chemical structure "\
        "is a function of the relative positions of "\
        "its atoms. To obtain this energy with "\
        "complete accuracy involves a lot of computer "\
        "time spent on quantum mechanical "\
        "calculations, which cannot be practically "\
        "done on a desktop computer. To get an "\
        "approximate potential energy without all "\
        "that, we represent the energy as a series "\
        "of terms involving geometric properties of "\
        "the structure: lengths of chemical bonds, "\
        "angles between pairs and triples of chemical "\
        "bonds, etc. </p>" \
        "<p>" \
        "As is generally the case with physical "\
        "systems, the gradient of the potential "\
        "energy represents the forces acting on "\
        "various particles. The atoms want to move in "\
        "the direction that most reduces the "\
        "potential energy. Energy minimization is a "\
        "process of adjusting the atom positions to "\
        "try to find a global minimum of the "\
        "potential energy. Each atom "\
        "contributes three variables (its x, y, and z"\
        " coordinates) so the search space is "\
        "multi-dimensional. The global minimum is the "\
        "configuration that the atoms will settle "\
        "into if lowered to zero Kelvin. </p>"

    win.simMinimizeEnergyAction.setWhatsThis( simMinimizeEnergyActionText )

    checkAtomTypesActionText = \
        "<u><b>Check AMBER AtomTypes</b></u>"\
        "<p>"\
        "Shows which AtomTypes will be assigned to each atom when the AMBER force field is in use."\
        "</p>"

    win.checkAtomTypesAction.setWhatsThis( checkAtomTypesActionText )

    # Change Chunk Color
    
    dispObjectColorActionText = \
        "<u><b>Edit Color</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Edit/Edit_Color.png\"><br> "\
        "Allows the user to change the color of all selected chunks and/or "\
        "jigs (i.e. rotary and linear motors)."\
        "</p>"
    
    win.dispObjectColorAction.setWhatsThis(  dispObjectColorActionText )

    # Run Dynamics (was NanoDynamics-1). Mark 060807.

    simSetupActionText = \
        "<u><b>Run Dynamics</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Run_Dynamics.png\"><br> "\
        "This is the interface to the NanoEngineer-1 molecular "\
        "dynamics simulator. Enter the parameters of the "\
        "simulation and click <b>Run Simulation</b>. The "\
        "simulator creates a trajectory (movie) file by "\
        "calculating the inter-atomic potentials and bonding "\
        "of the entire model.</p>"

    win. simSetupAction.setWhatsThis( simSetupActionText )

    # Simulation Jigs
    
    simulationJigsActionText = \
        "<u><b>Simulation Jigs</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Simulation_Jigs.png\"><br> "\
        "Drop down menu for adding rotary motors, linear motors and "\
        "other jigs used to simulate structures"\
        "</p>"
    win.simulationJigsAction.setWhatsThis( simulationJigsActionText )
    
    # Play Movie (was Movie Player) Mark 060807.

    simMoviePlayerActionText = \
        "<u><b>Play Movie</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Play_Movie.png\"><br> "\
        "Plays the most recent trajectory (movie) file "\
        "created by the NanoEngineer-1 molecular dynamics"\
        " simulator. To create a movie file, select "\
        "<b>Run Dynamics</b>.</p>"

    win. simMoviePlayerAction.setWhatsThis( simMoviePlayerActionText )

    # Make Graphs (was Plot Tool) Mark 060807.

    simPlotToolActionText = \
        "<u><b>Make Graphs</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Make_Graphs.png\"><br> "\
        "Make a graph of a simulator trace file using "\
        "GNUplot.  A simulation must be run to create "\
        "the trace file and the part must have a jig that "\
        "writes output to the trace file. <br><br>"\
        "The following list of jigs write data to the trace "\
        "file:<br><b>Rotary Motors:</b> speed (GHz) and "\
        "torque (nn-nm)<br> <b>Linear Motors:</b> "\
        "displacement (pm)<br><b>Anchors:</b> torque "\
        "(nn-nm)<br><b>Thermostats:</b> energy added "\
        "(zJ)<br><b>Thermometer:</b> temperature (K)<br>"\
        "<b>Measure Distance:</b> distance(angstroms)<br>"\
        "<b>Measure Angle:</b> angle (degrees)<br>"\
        "<b>Measure Dihedral:</b> dihedral(degrees)<br>"\
        "</p>"

    win. simPlotToolAction.setWhatsThis( simPlotToolActionText )
    
    #
    # Jigs
    #

    # Anchor

    jigsAnchorActionText = \
        "<u><b>Anchor</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Anchor.png\"><br> "\
        "Attaches an <b>Anchor</b> to the selected atom(s), "\
        "which constrains its motion during a minimization "\
        "or simulation."\
        "</p>"\
        "<p>To create an Anchor, enter <b>Build</b> mode, "\
        "select the atom(s) you want to anchor and then "\
        "select this action. Anchors are drawn as a black "\
        "wireframe box around each selected atom."\
        "</p>"

    win.jigsAnchorAction.setWhatsThis(jigsAnchorActionText )  

    # Rotary Motor

    jigsMotorActionText = \
        "<u><b>Rotary Motor</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Rotary_Motor.png\"><br> "\
        "Attaches a <b>Rotary Motor</b> to the selected "\
        "atoms. The Rotary Motor is used by the simulator to "\
        "apply rotary motion to a set of atoms during a "\
        "simulation run.  You may specify the <b>torque "\
        "(in nN*nm)</b> and <b>speed (in Ghz)</b> of the "\
        "motor."\
        "</p>"\
        "<p>To create a Rotary Motor, enter <b>Build</b> mode,"\
        " select the atoms you want to attach the motor to "\
        "and then select this action."\
        "</p>"

    win.jigsMotorAction.setWhatsThis(jigsMotorActionText )  

    # Linear Motor

    jigsLinearMotorActionText = \
        "<u><b>Linear Motor</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Linear_Motor.png\"><br> "\
        "Attaches a <b>Linear Motor</b> to the selected "\
        "atoms.  The Linear Motor is used by the "\
        "simulator to apply linear motion to a set of "\
        "atoms during a simulation run.  You may specify"\
        " the <b>force (in nN*nm)</b> and <b>stiffness "\
        "(in N/m)</b> of the motor. "\
        "</p>"\
        "<p>To create a Linear Motor, enter "\
        "<b>Build</b> mode, select the atoms you want "\
        "to attach the motor to and then select "\
        "this action."\
        "</p>"

    win.jigsLinearMotorAction.setWhatsThis(jigsLinearMotorActionText )  

    # Thermostat

    jigsStatActionText = \
        "<u><b>Thermostat</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Thermostat.png\"><br> "\
        "Attaches a <b>Langevin Thermostat</b> to a single "\
        "selected atom, thereby associating the thermostat to "\
        "the entire molecule of which the selected atom is a "\
        "member. The user specifies the temperature "\
        "(in Kelvin)."\
        "</p>"\
        "<p>The Langevin Thermostat is used to set and hold "\
        "the temperature of a molecule during a simulation run."\
        "</p>"\
        "<p>To create a Langevin Thermostat, enter "\
        "<b>Build</b> mode, select a single atom and then "\
        "select this action. The thermostat is drawn as a "\
        "blue wireframe box around the selected atom."\
        "</p>"

    win.jigsStatAction.setWhatsThis(jigsStatActionText ) 

    # Thermometer

    jigsThermoActionText = \
        "<u><b>Thermometer</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Measurements/"\
        "Thermometer.png\"><br> "\
        "Attaches a <b>Thermometer</b> to a single selected "\
        "atom, thereby associating the themometer to the "\
        "entire molecule of which the selected atom is a "\
        "member. "\
        "<p>The temperature of the molecule will be recorded "\
        "and written to a trace file during a simulation run."\
        "</p>"\
        "<p>To create a Thermometer, enter <b>Build</b> mode,"\
        " select a single atom and then select this action. "\
        "The thermometer is drawn as a dark red wireframe "\
        "box around the selected atom."\
        "</p>"

    win.jigsThermoAction.setWhatsThis(jigsThermoActionText )

    # ESP Image

    jigsESPImageActionText = \
        "<u><b>ESP Image</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/ESP_Image.png\"><br> "\
        "An <b>ESP Image</b> allows the user to visualize "\
        "the electrostatic potential of points on the face "\
        "of a square 2D surface. Nano-Hive's MPQC ESP "\
        "Plane plug-in is used to calculate the "\
        "electrostatic potential."\
        "</p>"\
        "<p>To create an ESP Image, enter <b>Build</b> "\
        "mode, select three or more atoms and then select "\
        "this jig. The ESP Image is drawn as a plane with "\
        "a bounding volume."\
        "</p>"

    win.jigsESPImageAction.setWhatsThis(jigsESPImageActionText )

    # Atom Set

    jigsAtomSetActionText = \
        "<u><b>Atom Set</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Tools/Atom_Set.png\"><br> "\
        "An <b>Atom Set</b> jig provides a convienient way "\
        "to save an atom selection which can be reselected "\
        "later."\
        "</p>"\
        "<p>To create an Atom Set, enter <b>Build</b> mode, "\
        "select any number of atoms and then select this "\
        "jig. The Atom Set is drawn as a set of wireframe "\
        "boxes around each atom in the selection."\
        "</p>"\
        "<p>To reselect the atoms in an Atom Set, select "\
        "it's context menu in the Model Tree and click the "\
        "menu item that states "\
        "<b>Select this jig's atoms</b>."\
        "</p>"

    win.jigsAtomSetAction.setWhatsThis(jigsAtomSetActionText )

    # Measure Distance

    jigsDistanceActionText = \
        "<u><b>Measure Distance Jig</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Measurements/"\
        "Measure_Distance.png\">"\
        "<br> "\
        "A <b>Measure Distance Jig</b> functions as a "\
        "dimension to display the distance between two "\
        "atoms."\
        "</p>"\
        "<p>To create the Measure Distance Jig, enter "\
        "<b>Build</b> mode, select two atoms and then "\
        "select this jig. The Measure Distance Jig is "\
        "drawn as a pair of wireframe boxes around each "\
        "atom connected by a line and a pair of numbers. "\
        "The first number is the distance between the "\
        "VdW radii (this can be a negative number for "\
        "atoms that are close together). The second number "\
        "is the distance between the nuclei."\
        "</p>"\
        "<p>The Measure Distance Jig will write the two "\
        "distance values to the trace file for each frame "\
        "of a simulation run and can be plotted using the "\
        "Plot Tool."\
        "</p>"

    win.jigsDistanceAction.setWhatsThis(jigsDistanceActionText )

    # Measure Angle

    jigsAngleActionText = \
        "<u><b>Measure Angle Jig</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Measurements/" \
        "Measure_Angle.png\"><br> "\
        "A <b>Measure Angle Jig</b> functions as a dimension "\
        "to display the angle between three atoms."\
        "</p>"\
        "<p>To create the Measure Angle Jig, enter "\
        "<b>Build</b> mode, select three atoms and then "\
        "select this jig. The Measure Angle Jig is "\
        "drawn as a set of wireframe boxes around each atom "\
        "and a number which is the angle between the three "\
        "atoms."\
        "</p>"\
        "<p>The Measure Angle Jig will write the angle value "\
        "to the trace file "\
        "for each frame of a simulation run and can be "\
        "plotted using the Plot Tool."\
        "</p>"

    win.jigsAngleAction.setWhatsThis(jigsAngleActionText )

    # Measure Dihedral

    jigsDihedralActionText = \
        "<u><b>Measure Dihedral Jig</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Measurements/"\
        "Measure_Dihedral.png\">"\
        "<br> "\
        "A <b>Measure Dihedral Jig</b> functions as a "\
        "dimension to display the dihedral angle of a four"\
        " atom sequence."\
        "</p>"\
        "<p>To create the Measure Dihedral Jig, enter "\
        "<b>Build</b> mode, select four atoms and then "\
        "select this jig. The Measure Dihedral Jig is "\
        "drawn as a set of wireframe boxes around each "\
        "atom and a number which is the dihedral angle "\
        "value."\
        "</p>"\
        "<p>The Measure Dihedral Jig will write the "\
        "dihedral angle value to the trace file "\
        "for each frame of a simulation run and can be "\
        "plotted using the Plot Tool."\
        "</p>"

    win.jigsDihedralAction.setWhatsThis(jigsDihedralActionText )

    # GAMESS Jig

    jigsGamessActionText = \
        "<u><b>GAMESS Jig</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Simulation/Gamess.png\"><br> "\
        "A <b>GAMESS Jig</b> is used to tag a set of atoms "\
        "for running a GAMESS calculation. <b>Energy</b> "\
        "and <b>Geometry Optimization</b> calculations are "\
        "supported."\
        "</p>"\
        "<p>To create the GAMESS Jig, enter <b>Build</b> mode, "\
        "select the atoms to tag and then select this jig. "\
        "The GAMESS Jig is drawn as a set of magenta "\
        "wireframe boxes around each atom."\
        "</p>"

    win.jigsGamessAction.setWhatsThis(jigsGamessActionText )

    # Grid Plane Jig

    jigsGridPlaneActionText = \
        "<u><b>Grid Plane</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Insert/Reference Geometry/"\
        "Grid_Plane.png\"><br> "\
        "A <b>Grid Plane</b> jig is a rectanglar plane "\
        "that can display a square or SiC grid within its "\
        "boundary. It is often used as an aid in "\
        "constructing large lattice structures made of "\
        "silicon carbide (SiC).  It is also used as a "\
        "visual aid in estimating distances between atoms "\
        "and/or other structures."\
        "</p>"\
        "<p>To create the Grid Plane jig, enter"\
        "<b>Build</b> mode, select three or more atoms "\
        "and then select this jig. "\
        "</p>"\
        "<p>The Grid Plane jig is drawn as a rectanglar "\
        "plane with a grid."\
        "</p>"

    win.jigsGridPlaneAction.setWhatsThis(jigsGridPlaneActionText )

    #
    # Help Toolbar
    #

    # What's This

    _text = \
        "<u><b>Enter \"What's This\" mode</b></u>"\
        "<p>"\
        "<img source=\"ui/actions/Help/WhatsThis.png\"><br> "\
        "This invokes \"What's This?\" help mode which is part of NanoEngineer-1's "\
        "online help system, and provides users with information about the "\
        "functionality and usage of a particular command button or widget.</p>"

    win.helpWhatsThisAction.setWhatsThis( _text )
    
    win.helpMouseControlsAction.setWhatsThis("Displays help for mouse controls")
    
    win.helpKeyboardShortcutsAction.setWhatsThis("Displays help for keyboard"\
    "shortcuts")
    
    win.helpSelectionShortcutsAction.setWhatsThis("Displays help for selection"\
    " controls")
    
    win.helpGraphicsCardAction.setWhatsThis("Displays information for the"\
    " computer's graphics card") 
    
    win.helpAboutAction.setWhatsThis("Displays information about this version"\
    " of NanoEngineer-1") 
    
    
    #
    # Status bar
    #
    
    # Global Display Style combobox
    _text = \
        "<u><b>Global Display Style</b></u>"\
        "<p>"\
        "Use this widget to change the <b>Global Display Style</b>."\
        "</p>"\
        "Objects with their display setting set to <b>Default</b> are "\
        "rendered in the <b>Global Display Style</b>."\
        "</p>"
    
    win.statusBar().globalDisplayStylesComboBox.setWhatsThis( _text )

def create_whats_this_descriptions_for_NanoHive_dialog(w):
    "Create What's This descriptions for the Nano-Hive dialog widgets."

    # MPQC Electrostatics Potential Plane

    MPQCESPText = \
                "<u><b>MPQC Electrostatics Potential Plane</b></u>"\
                "Enables the <i>MPQC Electrostatics Potential Plane</i> "\
                "plugin. "\
                "</p>"

    w.MPQC_ESP_checkbox.setWhatsThis(MPQCESPText )

    MPQCESPTipText = "Enables/disables MPQC Electrostatics "\
                     "Potential Plane Plugin"

    w.MPQC_ESP_checkbox.setToolTip(MPQCESPTipText)

def whats_this_text_for_glpane():
    """
    Return a What's This description for a GLPane.
    """
    #bruce 080912 moved this here from part of a method in class GLPane
    import sys
    if sys.platform == "darwin":
        ctrl_or_cmd = "Cmd"
    else:
        ctrl_or_cmd = "Ctrl"

    glpaneText = \
               "<u><b>Graphics Area</b></u><br> "\
               "<br>This is where the action is."\
               "<p><b>Mouse Button Commands :</b><br> "\
               "<br> "\
               "<b>Left Mouse Button (LMB)</b> - Select<br> "\
               "<b>LMB + Shift</b> - add to current selection <br> "\
               "<b>LMB + " + ctrl_or_cmd + "</b> - remove from current selection <br> "\
               "<b>LMB + Shift + " + ctrl_or_cmd + "</b> - delete highlighted object <br> "\
               "<br> "\
               "<b>Middle Mouse Button (MMB)</b> - Rotate view <br> "\
               "<b>MMB + Shift</b> - Pan view <br> "\
               "<b>MMB + " + ctrl_or_cmd + "</b> - Rotate view around the point of view (POV) <br> "\
               "<br> "\
               "<b>Right Mouse Button (RMB)</b> - Display context-sensitive menus <br>"\
               "<br> "\
               "<b>Mouse Wheel</b> - Zoom in/out (configurable from Preference settings)"\
               "</p>"
    return glpaneText

# end
