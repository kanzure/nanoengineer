# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
whatsthis.py

$Id$
"""

from qt import *

def createWhatsThis(self):
        
        ##############################################
        # File Toolbar
        ##############################################
        
        #### Open File ####
        
        fileOpenText = "<u><b>Open File</b></u>    (Ctrl + O)</b></p><br> "\
                        "<p><img source=\"fileopen\"><br> "\
                       "Opens a new file."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "fileopen",
                                                       self.fileOpenAction.iconSet().pixmap() )

        self.fileOpenAction.setWhatsThis( fileOpenText )
        
        #### Save File ####
        
        fileSaveText = "<u><b>Save File</b></u>     (Ctrl + S)</b></p><br> "\
                       "<p><img source=\"filesave\"><br> "\
                       "Saves the current file."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "filesave",
                                                       self.fileSaveAction.iconSet().pixmap() )

        self.fileSaveAction.setWhatsThis( fileSaveText )
        
        ##############################################
        # Edit Toolbar
        ##############################################
        
        #### Undo ####
        
        editUndoText =  "<u><b>Undo</b></u>     (Ctrl + Z)</b></p><br> "\
                       "<p><img source=\"editUndo\"><br> "\
                       "Reverses the last edit or command to the active part. "\
                       "<b>Currently not implemented</b>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editUndo",
                                                       self.editUndoAction.iconSet().pixmap() )

        self.editUndoAction.setWhatsThis( editUndoText )
        
        #### Redo ####
        
        editRedoText =  "<u><b>Redo</b></u>     (Ctrl + Y)</b></p><br> "\
                       "<p><img source=\"editRedo\"> <br>"\
                       "Re-applies the actions or commands on which you have used "\
                       "the Undo command. <b>Currently not implemented</b>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editRedo",
                                                       self.editRedoAction.iconSet().pixmap() )

        self.editRedoAction.setWhatsThis( editRedoText )
        
         #### Cut ####
        
        editCutText =  "<u><b>Cut</b></u>     (Ctrl + X)</b></p><br> "\
                       "<p><img source=\"editCut\"><br> "\
                       "Removes the selected object(s) and stores the cut data on the"\
                       "clipboard."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editCut",
                                                       self.editCutAction.iconSet().pixmap() )

        self.editCutAction.setWhatsThis( editCutText )
        
        #### Copy ####
        
        editCopyText =  "<u><b>Copy</b></u>     (Ctrl + C)</b></p><br> "\
                       "<p><img source=\"editCopy\"><br> "\
                      "Places a copy of the selected chunk(s) on the clipboard "\
                      "while leaving the original chunk(s) unaffected."\
                      "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editCopy",
                                                       self.editCopyAction.iconSet().pixmap() )

        self.editCopyAction.setWhatsThis( editCopyText )
        
         #### Paste ####
        
        editPasteText = "<u><b>Paste</b></u>     (Ctrl + V)</b></p><br> "\
                       "<p><img source=\"editPaste\"><br> "\
                       "When selecting this feature, you are placed in "\
                       "<b>Build Atom</b> mode where you may paste copies "\
                       "of clipboard objects into the model where ever you click."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editPaste",
                                                       self.editPasteAction.iconSet().pixmap() )

        self.editPasteAction.setWhatsThis( editPasteText )
   
        #### Delete ####
                                 
        editDeleteText =  "<u><b>Delete</b></u>     (DEL)</b></p><br> "\
                       "<p><img source=\"editDelete\"><br> "\
                       "Deletes the selected object(s).  "\
                       "For this Alpha release, deleted objects are permanantly lost.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editDelete",
                                                       self.editDeleteAction.iconSet().pixmap() )

        self.editDeleteAction.setWhatsThis( editDeleteText )
        
        ##############################################
        # View Toolbar
        ##############################################
        
        #### Home View ####
        
        setViewHomeActionText = "<u><b>Home</b></u>     (Home)<br>"\
                       "<p><img source=\"setViewHome\"><br> "\
                       "When you create a new model, it appears in a default view orientation (FRONT view). When you open an existing model, it appears in the orientation it was last saved.  You can change the default orientation by selecting <b>Set Home View to Current View</b> from the <b>View</b> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewHome",
                                                       self.setViewHomeAction.iconSet().pixmap() )

        self.setViewHomeAction.setWhatsThis( setViewHomeActionText )

        #### Fit to Window ####
        
        setViewFitToWindowActionText = "<u><b>Fit To Window</b></u><br>"\
                       "<p><img source=\"setViewFitToWindow\"><br> "\
                       "Refits the model to the screen so you can view the entire model."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewFitToWindow",
                                                       self.setViewFitToWindowAction.iconSet().pixmap() )

        self.setViewFitToWindowAction.setWhatsThis( setViewFitToWindowActionText )   

        #### Recenter ####
        
        setViewRecenterActionText = "<u><b>Recenter</b></u><br>"\
                       "<p><img source=\"setViewRecenter\"><br> "\
                       "Changes the view center and zoom factor so that the origin is in the "\
                       "center of the view and you can view the entire model."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewRecenter",
                                                       self.setViewRecenterAction.iconSet().pixmap() )

        self.setViewRecenterAction.setWhatsThis( setViewRecenterActionText )       
        
         #### Zoom Tool ####
        
        setzoomToolActionText = "<u><b>Zoom Tool</b></u><br>"\
                       "<p><img source=\"setzoomTool\"><br> "\
                       "Allows the user to zoom into a specific area of the model by specifying a rectangular area. "\
                       "This is done by holding down the left button and dragging the mouse.</p>"\
                       "<p>A mouse with a mouse wheel can also be used to zoom in and out "\
                       "at any time, without using the Zoom Tool.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setzoomTool",
                                                       self.zoomToolAction.iconSet().pixmap() )

        self.zoomToolAction.setWhatsThis( setzoomToolActionText )      

        
         #### Pan Tool ####
        
        setpanToolActionText = "<u><b>Pan Tool</b></u><br>"\
                       "<p><img source=\"setpanTool\"><br> "\
                       "Allows X-Y panning using the left mouse button.</p>"\
                       "<p>Users with a 3-button mouse can pan the model at any time by pressing "\
                       "the middle mouse button while holding down the Shift key.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setpanTool",
                                                       self.panToolAction.iconSet().pixmap() )

        self.panToolAction.setWhatsThis( setpanToolActionText )

        
         #### Rotate Tool ####
        
        setrotateToolActionText = "<u><b>Rotate Tool</b></u><br>"\
                       "<p><img source=\"setrotateTool\"><br> "\
                       "Allows free rotation using the left mouse button.</p>"\
                       "<p>Users with a 3-button mouse can rotate the model at any time by pressing "\
                       "the middle mouse button and dragging the mouse.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setrotateTool",
                                                       self.rotateToolAction.iconSet().pixmap() )

        self.rotateToolAction.setWhatsThis( setrotateToolActionText )
        
         #### Orthographic Projection ####
        
        setViewOrthoActionText = "<u><b>Orthographic Projection</b></u><br>"\
                       "<p><img source=\"setViewOrtho\"><br> "\
                       "Sets nonperspective (or parallel) projection, with no foreshortening."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewOrtho",
                                                       self.setViewOrthoAction.iconSet().pixmap() )

        self.setViewOrthoAction.setWhatsThis( setViewOrthoActionText )

           #### Perspective Projection ####
        
        setViewPerspecActionText = "<u><b>Perspective Projection</b></u><br>"\
                       "<p><img source=\"setViewPerspec\"><br> "\
                       "Set perspective projection, drawing objects slightly larger "\
                       "that are closer to the viewer."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewPerspec",
                                                       self.setViewPerspecAction.iconSet().pixmap() )

        self.setViewPerspecAction.setWhatsThis( setViewPerspecActionText )        

           #### Front View ####
        
        setViewFrontActionText = "<u><b>Front View</b></u><br>"\
                       "<p><img source=\"setViewFront\"><br> "\
                       "Reorients the model so that it is viewed from the front."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewFront",
                                                       self.setViewFrontAction.iconSet().pixmap() )

        self.setViewFrontAction.setWhatsThis( setViewFrontActionText )  

           #### Back View ####
        
        setViewBackActionText = "<u><b>Back View</b></u><br>"\
                       "<p><img source=\"setViewBack\"><br> "\
                       "Reorients the model so that it is viewed from the back."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewBack",
                                                       self.setViewBackAction.iconSet().pixmap() )

        self.setViewBackAction.setWhatsThis( setViewBackActionText )     
        
                   #### Top View ####
        
        setViewTopActionText = "<u><b>Top View</b></u><br>"\
                       "<p><img source=\"setViewTop\"><br> "\
                       "Reorients the model so that it is viewed from the top."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewTop",
                                                       self.setViewTopAction.iconSet().pixmap() )

        self.setViewTopAction.setWhatsThis( setViewTopActionText )      
        
                           #### Bottom View ####
        
        setViewBottomActionText = "<u><b>Bottom View</b></u><br>"\
                       "<p><img source=\"setViewBottom\"><br> "\
                       "Reorients the model so that it is viewed from the bottom."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewBottom",
                                                       self.setViewBottomAction.iconSet().pixmap() )

        self.setViewBottomAction.setWhatsThis( setViewBottomActionText )  
        
        #### Left View ####
        
        setViewLeftActionText = "<u><b>Left View</b></u><br>"\
                       "<p><img source=\"setViewLeft\"><br> "\
                       "Reorients the model so that it is viewed from the left side."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewLeft",
                                                       self.setViewLeftAction.iconSet().pixmap() )

        self.setViewLeftAction.setWhatsThis( setViewLeftActionText )
        
        #### Right View ####
        
        setViewRightActionText = "<u><b>Right View</b></u><br>"\
                       "<p><img source=\"setViewRight\"><br> "\
                       "Reorients the model so that it is viewed from the right side."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewRight",
                                                       self.setViewRightAction.iconSet().pixmap() )

        self.setViewRightAction.setWhatsThis( setViewRightActionText )
        
        ##############################################
        # Grids Toolbar
        ##############################################
        
        #### Surface 100 ####
        
        orient100ActionText = "<u><b>Surface 100</b></u><br>"\
                       "<p><img source=\"orient100Action\"><br> "\
                       "Reorients the view to the nearest angle that would "\
                       "look straight into a (1,0,0) surface of a diamond lattice."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient100Action",
                                                       self.orient100Action.iconSet().pixmap() )

        self.orient100Action.setWhatsThis(orient100ActionText )
        
        #### Surface 110 ####
        
        orient110ActionText = "<u><b>Surface 110</b></u><br>"\
                       "<p><img source=\"orient110Action\"><br> "\
                       "Reorients the view to the nearest angle that would "\
                       "look straight into a (1,1,0) surface of a diamond lattice."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient110Action",
                                                       self.orient110Action.iconSet().pixmap() )

        self.orient110Action.setWhatsThis(orient110ActionText )
        
        #### Surface 111 ####

        orient111ActionText = "<u><b>Surface 111</b></u><br>"\
                       "<p><img source=\"orient111Action\"><br> "\
                       "Reorients the view to the nearest angle that would "\
                       "look straight into a (1,1,1) surface of a diamond lattice."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient111Action",
                                                       self.orient111Action.iconSet().pixmap() )

        self.orient111Action.setWhatsThis(orient111ActionText )
        
        ##############################################
        # Molecular Display toolbar
        ##############################################
        
        #### Display Default  ####

        dispDefaultActionText = "<u><b>Display Default</b></u><br>"\
                       "<p><img source=\"dispDefaultAction\"><br> "\
                       "This resets the display setting of the selected atoms or chunks to the "\
                       "<b>Default Display Mode</b>.</p>"\
                       "The active Default Display Mode is displayed in the lower right corner "\
                       "of the main window.  The Default Display Mode can be easily changed "\
                       "by unselecting everything (i.e. Select None) and selecting a "\
                       "different Display Mode.</p>"\
                       "<p><b>Display Default</b> mimics <b>Display VwD</b> when the "\
                       "Default Display Mode is set to <b>Display Default</b>.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispDefaultAction",
                                                       self.dispDefaultAction.iconSet().pixmap() )

        self.dispDefaultAction.setWhatsThis(dispDefaultActionText )
 
         #### Display Invisible ####

        dispInvisActionText = "<u><b>Display Invisible</b></u><br>"\
                       "<p><img source=\"dispInvisAction\"><br> "\
                       "Changes the display setting of the selected atoms or chunks to "\
                       "<b>Invisible</b>.</p>"\
                       "<p>This can also be used to change the active <b>Default Display "\
                       "Mode</b> to <b>Display Invisible</b> by unselecting everything "\
                       "(i.e. Select None) and selecting this action. Doing this will make "\
                       "all atoms and chunks invisible that have their display setting set to "\
                       "<b>Display Default</b>.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispInvisAction",
                                                       self.dispInvisAction.iconSet().pixmap() )

        self.dispInvisAction.setWhatsThis(dispInvisActionText )       

           #### Display Lines ####

        dispLinesActionText = "<u><b>Display Lines</b></u><br>"\
                       "<p><img source=\"dispLinesAction\"><br> "\
                       "Changes the display of the selected atoms or chunks to <b>Lines</b>.  "\
                       "Only bonds are rendered as colored lines.</p>"\
                       "<p>This can also be used to change the active <b>Default Display "\
                       "Mode</b> to <b>Display Lines</b> by unselecting everything "\
                       "(i.e. Select None) and selecting this action. Doing this will render "\
                       "all atoms and chunks Lines mode that have their display setting set to "\
                       "<b>Display Default</b> .</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispLinesAction",
                                                       self.dispLinesAction.iconSet().pixmap() )

        self.dispLinesAction.setWhatsThis(dispLinesActionText )  
        
        #### Display Tubes ####

        dispTubesActionText = "<u><b>Display Tubes</b></u><br>"\
                       "<p><img source=\"dispTubesAction\"><br> "\
                       "Changes the display setting of the selected atoms or chunks to "\
                       "<b>Tubes</b>.  Atoms and bonds are rendered as colored tubes.</p>"\
                       "<p>This can also be used to change the active <b>Default Display "\
                       "Mode</b> to <b>Display Tubes</b> by unselecting everything "\
                       "(i.e. Select None) and selecting this action. Doing this will render "\
                       "all atoms and chunks in Tubes mode that have their display setting set to "\
                       "<b>Display Default</b> .</p>"


        QMimeSourceFactory.defaultFactory().setPixmap( "dispTubesAction",
                                                       self.dispTubesAction.iconSet().pixmap() )

        self.dispTubesAction.setWhatsThis(dispTubesActionText )  
        
        #### Display CPK ####

        dispCPKActionText = "<u><b>Display CPK</b></u><br>"\
                       "<p><img source=\"dispCPKAction\"><br> "\
                       "Changes the display of the selected atoms to <b>CPK</b> mode, "\
                       "also known as <b>\"Ball and Sticks\"</b> mode.  Atoms are rendered "\
                       "as spheres and bonds are rendered as grey cylinders.</p>"\
                       "<p>This can also be used to change the active <b>Default Display "\
                       "Mode</b> to <b>Display CPK</b> by unselecting everything "\
                       "(i.e. Select None) and selecting this action. Doing this will render "\
                       "all atoms and chunks in CPK mode that have their display setting set to "\
                       "<b>Display Default</b> .</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispCPKAction",
                                                       self.dispCPKAction.iconSet().pixmap() )

        self.dispCPKAction.setWhatsThis(dispCPKActionText ) 
        
         #### Display VdW ####

        dispVdWActionText = "<u><b>Display VdW</b></u><br>"\
                       "<p><img source=\"dispVdWAction\"><br> "\
                       "Changes the display of the selected atoms to <b>Van der Waals</b> "\
                       "mode.  Atoms are rendered as spheres with a size equal to the VdW "\
                       "radius.  Bonds are not rendered.</p>"\
                       "<p>This can also be used to change the active <b>Default Display "\
                       "Mode</b> to <b>Display VdW</b> by unselecting everything "\
                       "(i.e. Select None) and selecting this action. Doing this will render "\
                       "all atoms and chunks in VdW mode that have their display setting set to "\
                       "<b>Display Default</b> .</p>"
                      
        QMimeSourceFactory.defaultFactory().setPixmap( "dispVdWAction",
                                                       self.dispVdWAction.iconSet().pixmap() )

        self.dispVdWAction.setWhatsThis(dispVdWActionText )         
        
        ##############################################
        # Select toolbar
        ##############################################
        
        #### Select All ####

        selectAllActionText = "<u><b>Select All</b></u>     (Ctrl + A)</b></p><br>"\
                       "<p><img source=\"selectAllAction\"><br> "\
                       "During <b>Select Atoms</b> mode, this will select all the atoms in "\
                       "the model.  Otherwise, this will select all the chunks in the model."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectAllAction",
                                                       self.selectAllAction.iconSet().pixmap() )

        self.selectAllAction.setWhatsThis(selectAllActionText )
        
        #### Select None ####

        selectNoneActionText = "<u><b>Select None</b></u>     (Ctrl + D)</b></p><br>"\
                       "<p><img source=\"selectNoneAction\"><br> "\
                       "Unselects anything currently selected.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectNoneAction",
                                                       self.selectNoneAction.iconSet().pixmap() )

        self.selectNoneAction.setWhatsThis(selectNoneActionText )
 
        #### Invert Selection ####

        selectInvertActionText = "<u><b>Invert Selection</b></u> <br>    (Ctrl + Shift + I)</b></p><br>"\
                       "<p><img source=\"selectInvertAction\"><br> "\
                       "Inverts the current selection.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectInvertAction",
                                                       self.selectInvertAction.iconSet().pixmap() )

        self.selectInvertAction.setWhatsThis(selectInvertActionText )
        
        #### Select Connected ####

        selectConnectedActionText = "<u><b>Select Connected</b></u>     (Ctrl + Shift+C)</b></p><br>"\
            "<p><img source=\"selectConnectedAction\"><br> "\
            "Selects all the atoms that can be reached by the currently selected atom "\
            "via an unbroken chain of bonds. </p>"\
            "<p>To use this feature, you must first be in "\
            "<b>Select Atoms</b> mode and select at least one atom.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectConnectedAction",
                                                       self.selectConnectedAction.iconSet().pixmap() )

        self.selectConnectedAction.setWhatsThis(selectConnectedActionText )
        
        #### Select Doubly ####

        selectDoublyActionText = "<u><b>Select Doubly</b></u>    (Ctrl + Shift + D)</b></p><br>"\
                       "<p><img source=\"selectDoublyAction\"><br> "\
                       "Selects all the atoms that can be reached from a currently selected "\
                       "atom through two disjoint unbroken chains of bonds.  Atoms singly "\
                       "connected to this group and unconnected to anything else are also "\
                       "included in the selection.</p>"\
                       "<p>To use this feature, you must first be in "\
                       "<b>Select Atoms</b> mode and select at least one atom.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectDoublyAction",
                                                       self.selectDoublyAction.iconSet().pixmap() )

        self.selectDoublyAction.setWhatsThis(selectDoublyActionText )
        
        ##############################################
        # Modify Toolbar
        ##############################################
        
        #### Minimize ####

        modifyMinimizeActionText = "<u><b>Minimize</b></u>    (Ctrl + M)</b></p><br>"\
                       "<p><img source=\"modifyMinimizeAction\"><br> "\
                       "Arranges the atoms of the model to their chemically stable point of "\
                       "equilibrium in reference to the other atoms in the structure."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyMinimizeAction",
                                                       self.modifyMinimizeAction.iconSet().pixmap() )

        self.modifyMinimizeAction.setWhatsThis(modifyMinimizeActionText )
        
        #### Hydrogenate ####

        modifyHydrogenateActionText = "<u><b>Hydrogenate</b></u>    (Ctrl + H)</b></p><br>"\
                       "<p><img source=\"modifyHydrogenateAction\"><br> "\
                       "Adds hydrogen atoms to all the open bonds in the selection.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyHydrogenateAction",
                                                       self.modifyHydrogenateAction.iconSet().pixmap() )

        self.modifyHydrogenateAction.setWhatsThis(modifyHydrogenateActionText )

          #### Dehydrogenate ####

        modifyDehydrogenateActionText = "<u><b>Dehydrogenate</b></u><br>"\
                       "<p><img source=\"modifyDehydrogenateAction\"><br> "\
                       "Removes all hydrogen atoms from the selection.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyDehydrogenateAction",
                                                       self.modifyDehydrogenateAction.iconSet().pixmap() )

        self.modifyDehydrogenateAction.setWhatsThis(modifyDehydrogenateActionText )     
        
        #### Passivate ####

        modifyPassivateActionText = "<u><b>Passivate</b></u>    (Ctrl + P)</b></p><br>"\
                       "<p><img source=\"modifyPassivateAction\"><br> "\
                       "Changes the types of incompletely bonded atoms to atoms with the "\
                       "right number of bonds, using atoms with the best atomic radius."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyPassivateAction",
                                                       self.modifyPassivateAction.iconSet().pixmap() )

        self.modifyPassivateAction.setWhatsThis(modifyPassivateActionText )   
        
        #### Change Element ####

        modifySetElementActionText = "<u><b>Change Element</b></u>    (Ctrl + E)</b></p><br>"\
                       "<p><img source=\"modifySetElementAction\"><br> "\
                       "Allows you to change the element type of selected atoms.  "\
                       "You can also use <b>Change Element</b> while in "\
                       "<b>Build Atom</b> mode to change atom types.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifySetElementAction",
                                                       self.modifySetElementAction.iconSet().pixmap() )

        self.modifySetElementAction.setWhatsThis(modifySetElementActionText )  
        
        #### Stretch ####

        modifyStretchActionText = "<u><b>Stretch</b></u><br>"\
                       "<p><img source=\"modifyStretchAction\"><br> "\
                       "Stretches the bonds of the selected chunk(s).</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyStretchAction",
                                                       self.modifyStretchAction.iconSet().pixmap() )

        self.modifyStretchAction.setWhatsThis(modifyStretchActionText )

        #### Split ####

        modifySplitActionText = "<u><b>Split</b></u><br>"\
                       "<p><img source=\"modifySplitAction\"><br> "\
                       "Creates a new chunk from the currently selected atoms.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifySplitAction",
                                                       self.modifySplitAction.iconSet().pixmap() )

        self.modifySplitAction.setWhatsThis(modifySplitActionText )  
        
        #### Weld Chunks ####

        modifyWeldActionText = "<u><b>Weld Chunks</b></u><br>"\
                       "<p><img source=\"modifyWeldAction\"><br> "\
                       "Merges two or more chunks into one chunk when in "\
                       "<b>Select Chunks</b> mode. Creates one or more new chunks "\
                       "when in <b>Select Atoms</b> mode. </p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyWeldAction",
                                                       self.modifyWeldAction.iconSet().pixmap() )
       
        self.modifyWeldAction.setWhatsThis(modifyWeldActionText )  

        #### Align to Common Axis ####

        modifyAlignCommonAxisActionText = "<u><b>Align To Common Axis</b></u><br>"\
                       "<p><img source=\"modifyAlignCommonAxis\"><br> "\
                       "Automatically aligns two or more chunks to a common axis. You must first "\
                       "select two or more chunks before using this feature."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyAlignCommonAxis",
                                                       self. modifyAlignCommonAxisAction.iconSet().pixmap() )
       
        self. modifyAlignCommonAxisAction.setWhatsThis( modifyAlignCommonAxisActionText )
                
        ##############################################
        # Tools Toolbar
        ##############################################
        
        #### Select Chunks ####

        toolsSelectMoleculesActionText = "<u><b>Select Chunks</b></u><br>"\
                       "<p><img source=\" toolsSelectMoleculesAction\"><br> "\
                       "Activates <b>Select Chunks</b> mode, allowing you to select chunks with the mouse.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSelectMoleculesAction",
                                                       self. toolsSelectMoleculesAction.iconSet().pixmap() )
       
        self. toolsSelectMoleculesAction.setWhatsThis( toolsSelectMoleculesActionText )  

        #### Select Atoms ####

        toolsSelectAtomsActionText = "<u><b>Select Atoms</b></u><br>"\
                       "<p><img source=\" toolsSelectAtomsAction\"><br> "\
                       "Activates <b>Select Atoms</b> mode, allowing you to select atoms with the mouse.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSelectAtomsAction",
                                                       self. toolsSelectAtomsAction.iconSet().pixmap() )
       
        self. toolsSelectAtomsAction.setWhatsThis( toolsSelectAtomsActionText ) 
        
         #### Move Chunks ####

        toolsMoveMoleculeActionText = "<u><b>Move Chunks</b></u><br>"\
                       "<p><img source=\" toolsMoveMoleculeAction\"><br> "\
                       "Activates <b>Move Chunks</b> mode, allowing you to select, move and rotate individual chunks with the mouse.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsMoveMoleculeAction",
                                                       self. toolsMoveMoleculeAction.iconSet().pixmap() )
       
        self. toolsMoveMoleculeAction.setWhatsThis( toolsMoveMoleculeActionText ) 
        
        #### Build Atoms Tool ####

        toolsDepositAtomActionText = "<u><b>Build Tool</b></u><br>"\
                       "<p><img source=\" toolsDepositAtomAction\"><br> "\
                       "Activates <b>Build Atom</b> mode, allowing you to build chunks with the mouse.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsDepositAtomAction",
                                                       self. toolsDepositAtomAction.iconSet().pixmap() )
       
        self. toolsDepositAtomAction.setWhatsThis( toolsDepositAtomActionText ) 
        
        #### Cookie Cutter ####
                                        
        toolsCookieCutActionText = "<u><b>Cookie Cutter Tool</b></u><br>"\
                       "<p><><img source=\" toolsCookieCutAction\"><br> "\
                       "Activates <b>Cookie Cutter</b> mode, allowing you to cut out 3-D shapes from a slab of diamond lattice.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsCookieCutAction",
                                                       self. toolsCookieCutAction.iconSet().pixmap() )
       
        self. toolsCookieCutAction.setWhatsThis( toolsCookieCutActionText )
        
         #### Extrude Tool ####

        toolsExtrudeActionText = "<u><b>Extrude Tool</b></u><br>"\
                       "<p><img source=\" toolsExtrudeAction\"><br> "\
                       "Activates <b>Extrude</b> mode, allowing you to create a rod or ring using a chunk as a repeating unit.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsExtrudeAction",
                                                       self. toolsExtrudeAction.iconSet().pixmap() )
       
        self. toolsExtrudeAction.setWhatsThis( toolsExtrudeActionText )  

        #### Movie Player ####

        toolsMoviePlayerActionText = "<u><b>Movie Player</b></u><br>"\
                       "<p><img source=\" toolsMoviePlayerAction\"><br> "\
                       "Plays the most recent trajectory (movie) file created by the <b>Simulator</b>.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsMoviePlayerAction",
                                                       self. toolsMoviePlayerAction.iconSet().pixmap() )
       
        self. toolsMoviePlayerAction.setWhatsThis( toolsMoviePlayerActionText )  
        
        #### Simulator ####

        toolsSimulatorActionText = "<u><b>Simulator</b></u><br>"\
                       "<p><img source=\" toolsSimulatorAction\"><br> "\
                       "Creates a trajectory (movie) file by calculating the inter-atomic potentials and bonding of the entire model.  The user determines the number of frames in the movie, the time step, and the temperature for the simulation.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSimulatorAction",
                                                       self. toolsSimulatorAction.iconSet().pixmap() )
       
        self. toolsSimulatorAction.setWhatsThis( toolsSimulatorActionText )
        
        ##############################################
        # Dashboard Buttons
        ##############################################
        
        #### Done ####

        toolsDoneActionText = "<u><b>Done</b></u><br>"\
                       "<p><img source=\" toolsDoneAction\"><br> "\
                       "Completes the current operation and enters Select Chunks mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsDoneAction",
                                                       self. toolsDoneAction.iconSet().pixmap() )
       
        self. toolsDoneAction.setWhatsThis( toolsDoneActionText )  

        #### Cancel ####

        toolsCancelActionText = "<u><b>Cancel</b></u><br>"\
                       "<p><img source=\" toolsCancelAction\"><br> "\
                       "Cancels the current operation and enters Select Chunks mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsCancelAction",
                                                       self.toolsCancelAction.iconSet().pixmap() )
       
        self. toolsCancelAction.setWhatsThis( toolsCancelActionText ) 
        
        #### Back up ####

        toolsBackUpActionText = "<u><b>Back Up</b></u><br>"\
                       "<p><img source=\" toolsBackUpAction\"><br> "\
                       "Undoes the previous operation."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsBackUpAction",
                                                       self.toolsBackUpAction.iconSet().pixmap() )
       
        self. toolsBackUpAction.setWhatsThis( toolsBackUpActionText ) 
   
        #### Start Over ####
                        
        toolsStartOverActionText = "<u><b>Start Over</b></u><br>"\
                       "<p><img source=\"toolsStartOverAction\"><br> "\
                       "Cancels the current operation, leaving the user in the current mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "toolsStartOverAction",
                                                       self.toolsStartOverAction.iconSet().pixmap() )
       
        self.toolsStartOverAction.setWhatsThis(toolsStartOverActionText ) 
        
        #### Add Layers ####
                        
        ccAddLayerActionText = "<u><b>Add Layer</b></u><br>"\
                       "<p><img source=\"ccAddLayerAction\"><br> "\
                       "Adds a new layer of diamond lattice to the existing layer.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "ccAddLayerAction",
                                                       self.ccAddLayerAction.iconSet().pixmap() )
       
        self.ccAddLayerAction.setWhatsThis(ccAddLayerActionText ) 
        
        ##############################################
        # Jigs
        ##############################################
        
        #### Ground ####

        jigsGroundActionText = "<u><b>Ground</b></u><br>"\
                       "<p><img source=\"jigsGroundAction\"><br> "\
                       "Attaches a <b>Ground</b> (anchor) to the selected atom(s), which "\
                       "constrains its motion during a simulation.</p>"\
                       "<p>To create a Ground, enter <b>Select Atoms</b> mode, "\
                       "select the atom(s) you want to anchor and then select this action. "\
                       "Grounds are drawn as a black wireframe box around each selected atom.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsGroundAction",
                                                       self.jigsGroundAction.iconSet().pixmap() )
       
        self.jigsGroundAction.setWhatsThis(jigsGroundActionText )  
        
         #### Rotary Motor ####

        jigsMotorActionText = "<u><b>Rotary Motor</b></u><br>"\
                       "<p><img source=\"jigsMotorAction\"><br> "\
                       "Attaches a <b>Rotary Motor</b> to the selected atoms.  The Rotary Motor is used by "\
                       "the simulator to apply rotary motion to a set of atoms during a simulation run.  You may "\
                       "specify the <b>torque (in nN*nm)</b> and <b>speed (in Ghz)</b> of the motor.</p>"\
                       "<p>To create a Rotary Motor, enter <b>Select Atoms</b> mode, "\
                       "select the atoms you want to attach the motor to and then select this action.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsMotorAction",
                                                       self.jigsMotorAction.iconSet().pixmap() )
       
        self.jigsMotorAction.setWhatsThis(jigsMotorActionText )  
        
         #### Linear Motor ####

        jigsLinearMotorActionText = "<u><b>Linear Motor</b></u><br>"\
                       "<p><img source=\"jigsLinearMotorAction\"><br> "\
                       "Attaches a <b>Linear Motor</b> to the selected atoms.  The Linear Motor is used by "\
                       "the simulator to apply linear motion to a set of atoms during a simulation run.  You may "\
                       "specify the <b>force (in nN*nm)</b> and <b>stiffness (in N/m)</b> of the motor.</p>"\
                       "<p>To create a Linear Motor, enter <b>Select Atoms</b> mode, "\
                       "select the atoms you want to attach the motor to and then select this action.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsLinearMotorAction",
                                                       self.jigsLinearMotorAction.iconSet().pixmap() )
       
        self.jigsLinearMotorAction.setWhatsThis(jigsLinearMotorActionText )  
        
        #### Thermostat ####

        jigsStatActionText = "<u><b>Thermostat</b></u><br>"\
                       "<p><img source=\"jigsStatAction\"><br> "\
                       "Attaches a <b>Langevin Thermostat</b> to a single selected atom, thereby associating "\
                       "the themostat to the entire molecule of which the selected atom is a member. The user "\
                       "specifies the temperature (in Kelvin).</p>"\
                       "<p>The Langevin Thermostat is used to set and hold the temperature "\
                       "of a molecule during a simulation run.</p>"\
                       "<p>To create a Langevin Thermostat, enter <b>Select Atoms</b> mode, "\
                       "select a single atom and then select this action. The thermostat is drawn as a "\
                       "blue wireframe box around the selected atom.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsStatAction",
                                                       self.jigsStatAction.iconSet().pixmap() )
       
        self.jigsStatAction.setWhatsThis(jigsStatActionText ) 

        #### Thermometer ####

        jigsThermoActionText = "<u><b>Thermometer</b></u><br>"\
                       "<p><img source=\"jigsThermoAction\"><br> "\
                        "Attaches a <b>Thermometer</b> to a single selected atom, thereby associating "\
                       "the themometer to the entire molecule of which the selected atom is a member. "\
                       "<p>The temperature of the molecule will be recorded and written to a trace file "\
                       "during a simulation run.</p>"\
                       "<p>To create a Thermometer, enter <b>Select Atoms</b> mode, "\
                       "select a single atom and then select this action. The thermometer is drawn as a "\
                       "dark red wireframe box around the selected atom.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsThermoAction",
                                                       self.jigsThermoAction.iconSet().pixmap() )
       
        self.jigsThermoAction.setWhatsThis(jigsThermoActionText ) 
        
        ##############################################
        # Display
        ##############################################
        
        #### Display Object Color ####

        dispObjectColorActionText = "<u><b>Object Color</b></u><br>"\
                       "<p><img source=\"dispObjectColorAction\"><br> "\
                       "Allows you to change the color of the selected object(s).</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispObjectColorAction",
                                                       self.dispObjectColorAction.iconSet().pixmap() )
       
        self.dispObjectColorAction.setWhatsThis(dispObjectColorActionText ) 
        
         #### Display Background Color ####

        dispBGColorActionText = "<u><b>Background Color</b></u><br>"\
                       "<p><img source=\"dispBGColorAction\"><br> "\
                       "Allows you to change the background color of the main window.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispBGColorAction",
                                                       self.dispBGColorAction.iconSet().pixmap() )
       
        self.dispBGColorAction.setWhatsThis(dispBGColorActionText ) 
       
        ##############################################
        # Help Toolbar
        ##############################################
        
        #### NE-1 Assistant ####
        
        helpAssistantText = "<u><b>nanoENGINEER-1 Assistant</b></u><br>"\
                        "<p><img source=\"helpAssistant\"><br> "\
                       "Opens  <b>nanoENGINEER-1 Assistant</b>, "\
                       "the nanoENGINEER-1 Reference Documentation.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "helpAssistant",
                                                       self.helpAssistantAction.iconSet().pixmap() )

        self.helpAssistantAction.setWhatsThis( helpAssistantText )
        

        ##############################################
        # Datum Display Toolbar
        ##############################################
        
        #### Display Trihedron ####

        dispTrihedronText = "<u><b>Display Trihedron</b></u><br>"\
                       "<p><img source=\"dispTrihedron\"><br> "\
                       "Toggles the trihedron on and off.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispTrihedron",
                                                       self.dispTrihedronAction.iconSet().pixmap() )
       
        self.dispTrihedronAction.setWhatsThis(dispTrihedronText ) 

        #### Display Csys ####

        dispCsysText = "<u><b>Display Csys Axis</b></u><br>"\
                       "<p><img source=\"dispCsys\"><br> "\
                       "Toggles the coordinate system axis on and off."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispCsys",
                                                       self.dispCsysAction.iconSet().pixmap() )
       
        self.dispCsysAction.setWhatsThis(dispCsysText ) 
        
        #### Display Datum Lines ####

        dispDatumLinesText = "<u><b>Display Datum Lines</b></u><br>"\
                       "<p><img source=\"dispDatumLines\"><br> "\
                       "Toggles Datum Lines on and off.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispDatumLines",
                                                       self.dispDatumLinesAction.iconSet().pixmap() )
       
        self.dispDatumLinesAction.setWhatsThis(dispDatumLinesText )    

        #### Display Datum Planes ####

        dispDatumPlanesText = "<u><b>Display Datum Planes</b></u><br>"\
                       "<p><img source=\"dispDatumPlanes\"><br> "\
                       "Toggles Datum Planes on and off.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispDatumPlanes",
                                                       self.dispDatumPlanesAction.iconSet().pixmap() )
       
        self.dispDatumPlanesAction.setWhatsThis(dispDatumPlanesText )    
        
        #### Display Grid ####

        dispGridText = "<u><b>Display 3-D Grid</b></u><br>"\
                       "<p><img source=\"dispGrid\"><br> "\
                       "Toggles the 3-D grid on and off."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispGrid",
                                                       self.dispGridAction.iconSet().pixmap() )
       
        self.dispGridAction.setWhatsThis(dispGridText )           

        #### Display Open Bonds ####

        dispOpenBondsText = "<u><b>Display Singlets</b></u><br>"\
                       "<p><img source=\"dispOpenBonds\"><br> "\
                       "Toggles Singlets on and off."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispOpenBonds",
                                                       self.dispOpenBondsAction.iconSet().pixmap() )
       
        self.dispOpenBondsAction.setWhatsThis(dispOpenBondsText )