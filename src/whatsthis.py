from qt import *

def createWhatsThis(self):
        
        ##############################################
        # File Toolbar
        ##############################################
        
        #### fileOpenAction ####
        
        fileOpenText = "<u><b>Open File</b></u>    (Ctrl + O)</b></p><br> "\
                        "<p><img source=\"fileopen\"><br> "\
                       "Opens a <tt><em>new file</em></tt>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "fileopen",
                                                       self.fileOpenAction.iconSet().pixmap() )

        self.fileOpenAction.setWhatsThis( fileOpenText )
        
        #### fileSaveAction ####
        
        fileSaveText = "<u><b>Save File</b></u>     (Ctrl + S)</b></p><br> "\
                       "<p><img source=\"filesave\"><br> "\
                       "Saves the <tt><em>current file</em></tt>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "filesave",
                                                       self.fileSaveAction.iconSet().pixmap() )

        self.fileSaveAction.setWhatsThis( fileSaveText )
        
        ##############################################
        # Edit Toolbar
        ##############################################
        
        #### editUndoAction ####
        
        editUndoText =  "<u><b>Undo</b></u>     (Ctrl + Z)</b></p><br> "\
                       "<p><img source=\"editUndo\"><br> "\
                       "Reverses the last edit or command to the active part. <b>Currently not implemented</b>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editUndo",
                                                       self.editUndoAction.iconSet().pixmap() )

        self.editUndoAction.setWhatsThis( editUndoText )
        
        #### editRedoAction ####
        
        editRedoText =  "<u><b>Redo</b></u>     (Ctrl + Y)</b></p><br> "\
                       "<p><img source=\"editRedo\"> <br>"\
                       "Re-applies the actions or commands on which you have used the Undo command. <b>Currently not implemented</b>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editRedo",
                                                       self.editRedoAction.iconSet().pixmap() )

        self.editRedoAction.setWhatsThis( editRedoText )
        
         #### editCutAction ####
        
        editCutText =  "<u><b>Cut</b></u>     (Ctrl + X)</b></p><br> "\
                       "<p><img source=\"editCut\"><br> "\
                       "Removes the selected object(s) and stores the cut data on the clipboard.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editCut",
                                                       self.editCutAction.iconSet().pixmap() )

        self.editCutAction.setWhatsThis( editCutText )
        
        #### editCopyAction ####
        
        editCopyText =  "<u><b>Copy</b></u>     (Ctrl + C)</b></p><br> "\
                       "<p><img source=\"editCopy\"><br> "\
                      "Places a copy of the selected object(s) on the clipboard while leaving the original object(s) unaffected.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editCopy",
                                                       self.editCopyAction.iconSet().pixmap() )

        self.editCopyAction.setWhatsThis( editCopyText )
        
         #### editPasteAction ####
        
        editPasteText = "<u><b>Paste</b></u>     (Ctrl + V)</b></p><br> "\
                       "<p><img source=\"editPaste\"><br> "\
                       "When you choose this command, you are placed in <b>Build</b> mode and a copy of the top object on the clipboard is inserted where you click.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editPaste",
                                                       self.editPasteAction.iconSet().pixmap() )

        self.editPasteAction.setWhatsThis( editPasteText )
   
        #### editDeleteAction ####
                                 
        editDeleteText =  "<u><b>Delete</b></u>     (DEL)</b></p><br> "\
                       "<p><img source=\"editDelete\"><br> "\
                       "Deletes the selected object(s).  "\
                       "Deleted objects are not placed on the clipboard.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editDelete",
                                                       self.editDeleteAction.iconSet().pixmap() )

        self.editDeleteAction.setWhatsThis( editDeleteText )
        
        ##############################################
        # View Toolbar
        ##############################################
        
        #### set Home View####
        
        setViewHomeActionText = "<u><b>Home</b></u>     (Home)<br>"\
                       "<p><img source=\"setViewHome\"><br> "\
                       "When you create a new model, it appears in a default view orientation (FRONT view). When you open an existing model, it appears in the orientation it was last saved.  You can change the default orientation by selecting <b>Reorient</b> from the <b>View</b> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewHome",
                                                       self. setViewHomeAction.iconSet().pixmap() )

        self.setViewHomeAction.setWhatsThis(  setViewHomeActionText )

        #### Refit to window Viepw####
        
        setViewFitToWindowActionText = "<u><b>Fit To Window</b></u><br>"\
                       "<p><img source=\"setViewFitToWindow\"><br> "\
                       "Refits the model to the screen so you can view the entire model."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewFitToWindow",
                                                       self. setViewFitToWindowAction.iconSet().pixmap() )

        self.setViewFitToWindowAction.setWhatsThis(  setViewFitToWindowActionText )       
         #### set Ortho View####
        
        setViewOrthoActionText = "<u><b>Orthogonal Projection</b></u><br>"\
                       "<p><img source=\"setViewOrtho\"><br> "\
                       "Orthogonal projection: FINAL TEXT TO BE COMPLETED."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewOrtho",
                                                       self. setViewOrthoAction.iconSet().pixmap() )

        self.setViewOrthoAction.setWhatsThis(  setViewOrthoActionText )

           #### set Perspective View####
        
        setViewPerspecActionText = "<u><b>Perspective Projection</b></u><br>"\
                       "<p><img source=\"setViewPerspec\"><br> "\
                       "Perspective projection: FINAL TEXT TO BE COMPLETED."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewPerspec",
                                                       self. setViewPerspecAction.iconSet().pixmap() )

        self.setViewPerspecAction.setWhatsThis(  setViewPerspecActionText )        

           #### set Front View ####
        
        setViewFrontActionText = "<u><b>Front View</b></u><br>"\
                       "<p><img source=\"setViewFront\"><br> "\
                       "Reorients view to Front orientation. </p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewFront",
                                                       self. setViewFrontAction.iconSet().pixmap() )

        self.setViewFrontAction.setWhatsThis(  setViewFrontActionText )  

           #### set Back View ####
        
        setViewBackActionText = "<u><b>Back View</b></u><br>"\
                       "<p><img source=\"setViewBack\"><br> "\
                       "Reorients view to Back orientation. </p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewBack",
                                                       self. setViewBackAction.iconSet().pixmap() )

        self.setViewBackAction.setWhatsThis(  setViewBackActionText )     
        
                   #### set Top View ####
        
        setViewTopActionText = "<u><b>Top View</b></u><br>"\
                       "<p><img source=\"setViewTop\"><br> "\
                       "Reorients view to Top orientation. </p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewTop",
                                                       self. setViewTopAction.iconSet().pixmap() )

        self.setViewTopAction.setWhatsThis(  setViewTopActionText )      
        
                           #### set Bottom View ####
        
        setViewBottomActionText = "<u><b>Bottom View</b></u><br>"\
                       "<p><img source=\"setViewBottom\"><br> "\
                       "Reorients view to Bottom orientation. </p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewBottom",
                                                       self. setViewBottomAction.iconSet().pixmap() )

        self.setViewBottomAction.setWhatsThis(  setViewBottomActionText )  
        
        #### set Left View ####
        
        setViewLeftActionText = "<u><b>Left View</b></u><br>"\
                       "<p><img source=\"setViewLeft\"><br> "\
                       "Reorients view to Left orientation. </p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewLeft",
                                                       self. setViewLeftAction.iconSet().pixmap() )

        self.setViewLeftAction.setWhatsThis(  setViewLeftActionText )
        
        #### set Right View ####
        
        setViewRightActionText = "<u><b>Right View</b></u><br>"\
                       "<p><img source=\"setViewRight\"><br> "\
                       "Reorients view to Right orientation. </p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewRight",
                                                       self. setViewRightAction.iconSet().pixmap() )

        self.setViewRightAction.setWhatsThis(  setViewRightActionText )
        
        ##############################################
        # Grids Toolbar
        ##############################################
        
        #### Surface 100####
        
        orient100ActionText = "<u><b>Surface 100</b></u><br>"\
                       "<p><img source=\"orient100Action\"><br> "\
                       "Reorients the view to the nearest angle that would look straight into a (1,0,0) surface of a diamond lattice.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient100Action",
                                                       self.orient100Action.iconSet().pixmap() )

        self.orient100Action.setWhatsThis(orient100ActionText )
        
        #### Surface 110####
        
        orient110ActionText = "<u><b>Surface 110</b></u><br>"\
                       "<p><img source=\"orient110Action\"><br> "\
                       "Reorients the view to the nearest angle that would look straight into a (1,1,0) surface of a diamond lattice.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient110Action",
                                                       self.orient110Action.iconSet().pixmap() )

        self.orient110Action.setWhatsThis(orient110ActionText )
        
        #### Surface 111####

        orient111ActionText = "<u><b>Surface 111</b></u><br>"\
                       "<p><img source=\"orient111Action\"><br> "\
                       "Reorients the view to the nearest angle that would look straight into a (1,1,1) surface of a diamond lattice.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient111Action",
                                                       self.orient111Action.iconSet().pixmap() )

        self.orient111Action.setWhatsThis(orient111ActionText )
        
        ##############################################
        # Molecular Display toolbar
        ##############################################
        
        ####Default####

        dispDefaultActionText = "<u><b>Default</b></u><br>"\
                       "<p><img source=\"dispDefaultAction\"><br> "\
                       "Resets the display of the selected atoms or chunks to their default display mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispDefaultAction",
                                                       self.dispDefaultAction.iconSet().pixmap() )

        self.dispDefaultAction.setWhatsThis(dispDefaultActionText )
 
         ####Invisible####

        dispInvisActionText = "<u><b>Invisible</b></u><br>"\
                       "<p><img source=\"dispInvisAction\"><br> "\
                       "Changes the display of the selected atoms or chunks to <b>Invisible</b>, making them invisible, but does not delete them.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispInvisAction",
                                                       self.dispInvisAction.iconSet().pixmap() )

        self.dispInvisAction.setWhatsThis(dispInvisActionText )       

           ####Lines####

        dispLinesActionText = "<u><b>Lines</b></u><br>"\
                       "<p><img source=\"dispLinesAction\"><br> "\
                       "Changes the display of the selected atoms or chunks to <b>Lines</b>.  "\
                       "Only bonds are rendered as colored lines."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispLinesAction",
                                                       self.dispLinesAction.iconSet().pixmap() )

        self.dispLinesAction.setWhatsThis(dispLinesActionText )  
        
        ####Tubes####

        dispTubesActionText = "<u><b>Tubes</b></u><br>"\
                       "<p><img source=\"dispTubesAction\"><br> "\
                       "Changes the display of the selected atoms or chunks to <b>Tubes</b>.  "\
                       "Atoms and bonds are rendered as colored tubes."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispTubesAction",
                                                       self.dispTubesAction.iconSet().pixmap() )

        self.dispTubesAction.setWhatsThis(dispTubesActionText )  
        
        ####CPK####

        dispCPKActionText = "<u><b>CPK</b></u><br>"\
                       "<p><img source=\"dispCPKAction\"><br> "\
                       "Changes the display of the selected atoms to <b>CPK</b> mode, also known as <b>\"Ball and Sticks\"</b> mode.  Atoms are rendered as spheres and bonds are rendered as grey cylinders."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispCPKAction",
                                                       self.dispCPKAction.iconSet().pixmap() )

        self.dispCPKAction.setWhatsThis(dispCPKActionText ) 
        
         ####VDW####

        dispVdWActionText = "<u><b>VdW</b></u><br>"\
                       "<p><img source=\"dispVdWAction\"><br> "\
                       "Changes the display of the selected atoms to <b>Van der Waals</b> mode.  Atoms are rendered as spheres with a size equal to the VdW radius.  Bonds are not rendered."\
                       "</p>"
                      
        QMimeSourceFactory.defaultFactory().setPixmap( "dispVdWAction",
                                                       self.dispVdWAction.iconSet().pixmap() )

        self.dispVdWAction.setWhatsThis(dispVdWActionText )         
        
        ##############################################
        # Select toolbar
        ##############################################
        
        ####selectAll####

        selectAllActionText = "<u><b>Select All</b></u>     (Ctrl + A)</b></p><br>"\
                       "<p><img source=\"selectAllAction\"><br> "\
                       "Selects all the atoms while in <tt><em>Select Atoms</em></tt> mode, and selects all the <tt><em>Chunks</em></tt> while in <em>Select Chunks</em> mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectAllAction",
                                                       self.selectAllAction.iconSet().pixmap() )

        self.selectAllAction.setWhatsThis(selectAllActionText )
        
        ####selectNone####

        selectNoneActionText = "<u><b>Select None</b></u>     (Ctrl + D)</b></p><br>"\
                       "<p><img source=\"selectNoneAction\"><br> "\
                       "Unselects the current selection.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectNoneAction",
                                                       self.selectNoneAction.iconSet().pixmap() )

        self.selectNoneAction.setWhatsThis(selectNoneActionText )
 
        ####select Invert####

        selectInvertActionText = "<u><b>Invert Selection</b></u>     (Ctrl + Shift + I)</b></p><br>"\
                       "<p><img source=\"selectInvertAction\"><br> "\
                       "Inverts the current selection.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectInvertAction",
                                                       self.selectInvertAction.iconSet().pixmap() )

        self.selectInvertAction.setWhatsThis(selectInvertActionText )
        
        ####Select Connected####

        selectConnectedActionText = "<u><b>Select Connected</b></u>     (Ctrl + Shift+C)</b></p><br>"\
            "<p><img source=\"selectConnectedAction\"><br> "\
            "Selects all the atoms that can be reached by the currently selected atom via an unbroken chain of bonds."\
            "You must first be in <b>Select Atoms</b> mode and select at least one atom to use this feature.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectConnectedAction",
                                                       self.selectConnectedAction.iconSet().pixmap() )

        self.selectConnectedAction.setWhatsThis(selectConnectedActionText )
        
        ####Select Doubly####

        selectDoublyActionText = "<u><b>Select Doubly</b></u>    (Ctrl + Shift + D)</b></p><br>"\
                       "<p><img source=\"selectDoublyAction\"><br> "\
                       "Selects all the atoms that can be reached from a currently selected atom through two disjoint unbroken chains of bonds.  Atoms singly connected to this group and unconnected to anything else are also included in the selection.  You must first be in <b>Select Atoms</b> mode and select at least one atom to use this feature."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectDoublyAction",
                                                       self.selectDoublyAction.iconSet().pixmap() )

        self.selectDoublyAction.setWhatsThis(selectDoublyActionText )
        
        ##############################################
        # Modify Toolbar
        ##############################################
        
        ####Minimize####

        modifyMinimizeActionText = "<u><b>Minimize</b></u>    (Ctrl + M)</b></p><br>"\
                       "<p><img source=\"modifyMinimizeAction\"><br> "\
                       "Arranges the atoms of the selected chunk(s) to their chemically stable point of equilibrium in reference to the other atoms in the structure."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyMinimizeAction",
                                                       self.modifyMinimizeAction.iconSet().pixmap() )

        self.modifyMinimizeAction.setWhatsThis(modifyMinimizeActionText )
        
        ####Hydrogenate####

        modifyHydrogenateActionText = "<u><b>Hydrogenate</b></u>    (Ctrl + H)</b></p><br>"\
                       "<p><img source=\"modifyHydrogenateAction\"><br> "\
                       "Adds hydrogen atoms to all the open bonds in the selection.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyHydrogenateAction",
                                                       self.modifyHydrogenateAction.iconSet().pixmap() )

        self.modifyHydrogenateAction.setWhatsThis(modifyHydrogenateActionText )

          ####Dehydrogenate####

        modifyDehydrogenateActionText = "<u><b>Dehydrogenate</b></u><br>"\
                       "<p><img source=\"modifyDehydrogenateAction\"><br> "\
                       "Removes all hydrogen atoms from the selection.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyDehydrogenateAction",
                                                       self.modifyDehydrogenateAction.iconSet().pixmap() )

        self.modifyDehydrogenateAction.setWhatsThis(modifyDehydrogenateActionText )     
        
        ####Passivate####

        modifyPassivateActionText = "<u><b>Passivate</b></u>    (Ctrl + P)</b></p><br>"\
                       "<p><img source=\"modifyPassivateAction\"><br> "\
                       "Changes the types of incompletely bonded atoms to atoms with the right number of bonds, using atoms with the best atomic radius."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyPassivateAction",
                                                       self.modifyPassivateAction.iconSet().pixmap() )

        self.modifyPassivateAction.setWhatsThis(modifyPassivateActionText )   
        
        ####Change Element####

        modifySetElementActionText = "<u><b>Change Element</b></u>    (Ctrl + E)</b></p><br>"\
                       "<p><img source=\"modifySetElementAction\"><br> "\
                       "Allows you to change the element type of selected atoms.  You can also use <b>Change Element</b> while in <tt><em>Build Mode</em></tt> to change atom types."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifySetElementAction",
                                                       self.modifySetElementAction.iconSet().pixmap() )

        self.modifySetElementAction.setWhatsThis(modifySetElementActionText )  
        
        ####Stretch####

        modifyStretchActionText = "<u><b>Stretch</b></u><br>"\
                       "<p><img source=\"modifyStretchAction\"><br> "\
                       "Stretches the bonds of the selected chunk(s).</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyStretchAction",
                                                       self.modifyStretchAction.iconSet().pixmap() )

        self.modifyStretchAction.setWhatsThis(modifyStretchActionText )

        ####Separate####

        modifySeparateActionText = "<u><b>Separate</b></u><br>"\
                       "<p><img source=\"modifySeparateAction\"><br> "\
                       "Creates a new chunk from the currently selected atoms.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifySeparateAction",
                                                       self.modifySeparateAction.iconSet().pixmap() )

        self.modifySeparateAction.setWhatsThis(modifySeparateActionText )  
        
        ####Weld Chunks####

        modifyWeldActionText = "<u><b>Weld Chunks</b></u><br>"\
                       "<p><img source=\"modifyWeldAction\"><br> "\
                       "Merges two or more chunks into one chunk when in <b>Select Chunks</b> mode. "\
                       "Creates one or more new chunks when in <b>Select Atoms</b> mode. "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyWeldAction",
                                                       self.modifyWeldAction.iconSet().pixmap() )
       
        self.modifyWeldAction.setWhatsThis(modifyWeldActionText )  

        ####Align to Common Axis####

        modifyAlignCommonAxisActionText = "<u><b>Align To Common Axis</b></u><br>"\
                       "<p><img source=\"modifyAlignCommonAxis\"><br> "\
                       "Automatically aligns two or more chunks to a common axis. You must first select two or more chunks before using this feature."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyAlignCommonAxis",
                                                       self. modifyAlignCommonAxisAction.iconSet().pixmap() )
       
        self. modifyAlignCommonAxisAction.setWhatsThis( modifyAlignCommonAxisActionText )
                
        ##############################################
        # Tools Toolbar
        ##############################################
        
        ####Select Chunks####

        toolsSelectMoleculesActionText = "<u><b>Select Chunks</b></u><br>"\
                       "<p><img source=\" toolsSelectMoleculesAction\"><br> "\
                       "Puts the program in <b>Select Chunks</b> mode, allowing you to select chunks with the mouse.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSelectMoleculesAction",
                                                       self. toolsSelectMoleculesAction.iconSet().pixmap() )
       
        self. toolsSelectMoleculesAction.setWhatsThis( toolsSelectMoleculesActionText )  

        ####Select Atoms####

        toolsSelectAtomsActionText = "<u><b>Select Atoms</b></u><br>"\
                       "<p><img source=\" toolsSelectAtomsAction\"><br> "\
                       "Puts the program in <b>Select Atoms</b> mode, allowing you to select atoms with the mouse.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSelectAtomsAction",
                                                       self. toolsSelectAtomsAction.iconSet().pixmap() )
       
        self. toolsSelectAtomsAction.setWhatsThis( toolsSelectAtomsActionText ) 
        
         ####Move Chunks####

        toolsMoveMoleculeActionText = "<u><b>Move Chunks</b></u><br>"\
                       "<p><img source=\" toolsMoveMoleculeAction\"><br> "\
                       "Puts the program in <b>Move Chunks</b> mode, allowing you to select, move and rotate individual chunks with the mouse.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsMoveMoleculeAction",
                                                       self. toolsMoveMoleculeAction.iconSet().pixmap() )
       
        self. toolsMoveMoleculeAction.setWhatsThis( toolsMoveMoleculeActionText ) 
        
        ####Build Tool####

        toolsDepositAtomActionText = "<u><b>Build Tool</b></u><br>"\
                       "<p><img source=\" toolsDepositAtomAction\"><br> "\
                       "Puts the program in <b>Build</b> mode, allowing you to build molecules with the mouse.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsDepositAtomAction",
                                                       self. toolsDepositAtomAction.iconSet().pixmap() )
       
        self. toolsDepositAtomAction.setWhatsThis( toolsDepositAtomActionText ) 
        
        ####Cookie Cutter####
                                        
        toolsCookieCutActionText = "<u><b>Cookie Cutter Tool</b></u><br>"\
                       "<p><><img source=\" toolsCookieCutAction\"><br> "\
                       "Puts the program in <b>Cookie Cutter</b> mode, allowing you to cut out 3-D shapes from a slab of diamond lattice.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsCookieCutAction",
                                                       self. toolsCookieCutAction.iconSet().pixmap() )
       
        self. toolsCookieCutAction.setWhatsThis( toolsCookieCutActionText )
        
         ####Extrude####

        toolsExtrudeActionText = "<u><b>Extrude Tool</b></u><br>"\
                       "<p><img source=\" toolsExtrudeAction\"><br> "\
                       "Puts the program in <b>Extrude</b> mode, allowing you to create a rod or ring using a chunk as a repeating unit.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsExtrudeAction",
                                                       self. toolsExtrudeAction.iconSet().pixmap() )
       
        self. toolsExtrudeAction.setWhatsThis( toolsExtrudeActionText )  

        ####Movie####

        toolsMovieActionText = "<u><b>Movie Player</b></u><br>"\
                       "<p><img source=\" toolsMovieAction\"><br> "\
                       "Plays the most recent trajectory (movie) file created by the <b>Simulator</b>.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsMovieAction",
                                                       self. toolsMovieAction.iconSet().pixmap() )
       
        self. toolsMovieAction.setWhatsThis( toolsMovieActionText )  
        
        ####Simulator####

        toolsSimulator_ActionText = "<u><b>Simulator</b></u><br>"\
                       "<p><img source=\" toolsSimulator_Action\"><br> "\
                       "Creates a trajectory (movie) file by calculating the inter-atomic potentials and bonding of the entire model.  The user determines the number of frames in the movie, the time step, and the temperature for the simulation.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSimulator_Action",
                                                       self. toolsSimulator_Action.iconSet().pixmap() )
       
        self. toolsSimulator_Action.setWhatsThis( toolsSimulator_ActionText )
        
        ##############################################
        # Dashboard Buttons
        ##############################################
        
        ####done checkmark####

        toolsDoneActionText = "<u><b>Done</b></u><br>"\
                       "<p><img source=\" toolsDoneAction\"><br> "\
                       "Completes the current operation and enters Select Chunks mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsDoneAction",
                                                       self. toolsDoneAction.iconSet().pixmap() )
       
        self. toolsDoneAction.setWhatsThis( toolsDoneActionText )  

        ####Cancel####

        toolsCancelActionText = "<u><b>Cancel</b></u><br>"\
                       "<p><img source=\" toolsCancelAction\"><br> "\
                       "Cancels the current operation and enters Select Chunks mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsCancelAction",
                                                       self.toolsCancelAction.iconSet().pixmap() )
       
        self. toolsCancelAction.setWhatsThis( toolsCancelActionText ) 
        
        ####Back up####

        toolsBackUpActionText = "<u><b>Back Up</b></u><br>"\
                       "<p><img source=\" toolsBackUpAction\"><br> "\
                       "Undoes the previous operation."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsBackUpAction",
                                                       self.toolsBackUpAction.iconSet().pixmap() )
       
        self. toolsBackUpAction.setWhatsThis( toolsBackUpActionText ) 
   
        ####Start Over####
                        
        toolsStartOverActionText = "<u><b>Start Over</b></u><br>"\
                       "<p><img source=\"toolsStartOverAction\"><br> "\
                       "Cancels the current operation, leaving the user in the current mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "toolsStartOverAction",
                                                       self.toolsStartOverAction.iconSet().pixmap() )
       
        self.toolsStartOverAction.setWhatsThis(toolsStartOverActionText ) 
        
        ####Add Layersr####
                        
        ccAddLayerActionText = "<u><b>Add Layer</b></u><br>"\
                       "<p><img source=\"ccAddLayerAction\"><br> "\
                       "Adds a new layer of diamond lattice to the existing layer.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "ccAddLayerAction",
                                                       self.ccAddLayerAction.iconSet().pixmap() )
       
        self.ccAddLayerAction.setWhatsThis(ccAddLayerActionText ) 
        
        ##############################################
        # Jigs
        ##############################################
        
        ####Ground####

        jigsGroundActionText = "<u><b>Ground</b></u><br>"\
                       "<p><img source=\"jigsGroundAction\"><br> "\
                       "Attaches a <b>Ground</b> (anchor) to the selected atom(s), which constrains its motion during a simulation.  Grounds are drawn as a black wire box around each atom to which it is attached.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsGroundAction",
                                                       self.jigsGroundAction.iconSet().pixmap() )
       
        self.jigsGroundAction.setWhatsThis(jigsGroundActionText )  
        
         ####Rotary Motor####

        jigsMotorActionText = "<u><b>Rotary Motor</b></u><br>"\
                       "<p><img source=\"jigsMotorAction\"><br> "\
                       "Attaches a <b>Rotary Motor</b> to the selected atoms for a simulation.  You may specify the <b>torque (in nN*nm)</b> and <b>speed (in Ghz)</b> of the motor. </p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsMotorAction",
                                                       self.jigsMotorAction.iconSet().pixmap() )
       
        self.jigsMotorAction.setWhatsThis(jigsMotorActionText )  
        
         ####Linear Motor####

        jigsLinearMotorActionText = "<u><b>Linear Motor</b></u><br>"\
                       "<p><img source=\"jigsLinearMotorAction\"><br> "\
                       "Attaches a <b>Linear Motor</b> to the selected atoms for a simulation.  You may specify the <b>force (in nN*nm)</b> and <b>stiffness (in N/m)</b> of the motor. </p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsLinearMotorAction",
                                                       self.jigsLinearMotorAction.iconSet().pixmap() )
       
        self.jigsLinearMotorAction.setWhatsThis(jigsLinearMotorActionText )  
        
        ####Thermostat####

        jigsStatActionText = "<u><b>Stat</b></u><br>"\
                       "<p><img source=\"jigsStatAction\"><br> "\
                       "Allows you to set the temperature (in Kelvin) of the selected atom(s) for the simulator."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsStatAction",
                                                       self.jigsStatAction.iconSet().pixmap() )
       
        self.jigsStatAction.setWhatsThis(jigsStatActionText ) 
        
        ##############################################
        # Display
        ##############################################
        
        ####Display ObjectColor####

        dispObjectColorActionText = "<u><b>Object Color</b></u><br>"\
                       "<p><img source=\"dispObjectColorAction\"><br> "\
                       "Allows you to change the color of the selected object(s).</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispObjectColorAction",
                                                       self.dispObjectColorAction.iconSet().pixmap() )
       
        self.dispObjectColorAction.setWhatsThis(dispObjectColorActionText ) 
        
         ####Display Background Color####

        dispBGColorActionText = "<u><b>Background Color</b></u><br>"\
                       "<p><img source=\"dispBGColorAction\"><br> "\
                       "Allows you to change the background color of the main window.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispBGColorAction",
                                                       self.dispBGColorAction.iconSet().pixmap() )
       
        self.dispBGColorAction.setWhatsThis(dispBGColorActionText ) 
       
        ##############################################
        # Help Toolbar
        ##############################################
        
        #### helpAssistantAction ####
        
        helpAssistantText = "<u><b>nanoENGINEER-1 Assistant</b></u><br>"\
                        "<p><img source=\"helpAssistant\"><br> "\
                       "Opens  <b>nanoENGINEER-1 Assistant</b>, "\
                       "the nanoENGINEER-1 Reference Documentation.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "helpAssistant",
                                                       self.helpAssistantAction.iconSet().pixmap() )

        self.helpAssistantAction.setWhatsThis( helpAssistantText )
        
        #### fileSaveAction ####
       
       
        ##############################################
        # Datum Display Toolbar
        ##############################################
        
        ####Display Trihedron####

        dispTrihedronText = "<u><b>Display Trihedron</b></u><br>"\
                       "<p><img source=\"dispTrihedron\"><br> "\
                       "Toggles the trihedron on and off.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispTrihedron",
                                                       self.dispTrihedronAction.iconSet().pixmap() )
       
        self.dispTrihedronAction.setWhatsThis(dispTrihedronText ) 

        ####Display Csys####

        dispCsysText = "<u><b>Display Csys Axis</b></u><br>"\
                       "<p><img source=\"dispCsys\"><br> "\
                       "Toggles the coordinate system axis on and off."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispCsys",
                                                       self.dispCsysAction.iconSet().pixmap() )
       
        self.dispCsysAction.setWhatsThis(dispCsysText ) 
        
        ####Display Datum Lines####

        dispDatumLinesText = "<u><b>Display Datum Lines</b></u><br>"\
                       "<p><img source=\"dispDatumLines\"><br> "\
                       "Toggles Datum Lines on and off.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispDatumLines",
                                                       self.dispDatumLinesAction.iconSet().pixmap() )
       
        self.dispDatumLinesAction.setWhatsThis(dispDatumLinesText )    

        ####Display Datum Planes####

        dispDatumPlanesText = "<u><b>Display Datum Planes</b></u><br>"\
                       "<p><img source=\"dispDatumPlanes\"><br> "\
                       "Toggles Datum Planes on and off.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispDatumPlanes",
                                                       self.dispDatumPlanesAction.iconSet().pixmap() )
       
        self.dispDatumPlanesAction.setWhatsThis(dispDatumPlanesText )    
        
        ####Display Grid####

        dispGridText = "<u><b>Display 3-D Grid</b></u><br>"\
                       "<p><img source=\"dispGrid\"><br> "\
                       "Toggles the 3-D grid on and off."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispGrid",
                                                       self.dispGridAction.iconSet().pixmap() )
       
        self.dispGridAction.setWhatsThis(dispGridText )           

        ####Display Open Bonds####

        dispOpenBondsText = "<u><b>Display Singlets</b></u><br>"\
                       "<p><img source=\"dispOpenBonds\"><br> "\
                       "Toggles Singlets on and off."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispOpenBonds",
                                                       self.dispOpenBondsAction.iconSet().pixmap() )
       
        self.dispOpenBondsAction.setWhatsThis(dispOpenBondsText )                   