from qt import *

def createWhatsThis(self):
        
        ##############################################
        # File Toolbar
        ##############################################
        
        #### fileOpenAction ####
        
        fileOpenText = "<u><b>Open File</b></u>    (Ctrl + O)</b></p><br> "\
                        "<p><img source=\"fileopen\"><br> "\
                       "Click this button to open a <em>new file</em>."\
                       "You can also select the <b>Open</b> command "\
                       "from the <em>File</em> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "fileopen",
                                                       self.fileOpenAction.iconSet().pixmap() )

        self.fileOpenAction.setWhatsThis( fileOpenText )
        
        #### fileSaveAction ####
        
        fileSaveText = "<u><b>Save File</b></u>     (Ctrl + S)</b></p><br> "\
                       "<p><img source=\"filesave\"><br> "\
                       "Click this button to save the <em>current part</em>."\
                       "You can also select the <b>Save</b> command "\
                       "from the <em>File</em> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "filesave",
                                                       self.fileSaveAction.iconSet().pixmap() )

        self.fileSaveAction.setWhatsThis( fileSaveText )
        
        
        ##############################################
        # Edit Toolbar
        ##############################################
        
        #### editUndoAction ####
        
        editUndoText =  "<u><b>Undo</b></u>     (Ctrl + Z)</b></p><br> "\
                       "<p><img source=\"editUndo\"><br> "\
                       "Click this button to <b>Undo</b> the last operation."\
                       "        You can also select the <b>Undo</b> command "\
                       "from the <em>Edit   </em> menu.  This feature is not implemented yet.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editUndo",
                                                       self.editUndoAction.iconSet().pixmap() )

        self.editUndoAction.setWhatsThis( editUndoText )
        
        #### editRedoAction ####
        
        editRedoText =  "<u><b>Redo</b></u>     (Ctrl + Y)</b></p><br> "\
                       "<p><img source=\"editRedo\"> <br>"\
                       "Click this button to <b>Redo</b> the last operation."\
                       "        You can also select the <b>Redo</b> command "\
                       "from the <em> Edit  </em> menu.  This feature is not implemented yet.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editRedo",
                                                       self.editRedoAction.iconSet().pixmap() )

        self.editRedoAction.setWhatsThis( editRedoText )
        
         #### editCutAction ####
        
        editCutText =  "<u><b>Cut</b></u>     (Ctrl + X)</b></p><br> "\
                       "<p><img source=\"editCut\"><br> "\
                       "Click this button to <b>Cut</b> the selected object from the model."\
                       " A <b>Cut</b> object is removed from the model, and added to the clipboard.  You can also select the <b>Cut</b> "\
                       "command from the <em> Edit </em> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editCut",
                                                       self.editCutAction.iconSet().pixmap() )

        self.editCutAction.setWhatsThis( editCutText )
        
                 #### editCopyAction ####
        
        editCopyText =  "<u><b>Copy</b></u>     (Ctrl + C)</b></p><br> "\
                       "<p><img source=\"editCopy\"><br> "\
                       "Click this button to <b>copy</b> the selected part or atoms."\
                        " A copied object is added to the clipboard for future use.  You can also select the <b>Copy</b> command "\
                       "from the <em>Edit</em> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editCopy",
                                                       self.editCopyAction.iconSet().pixmap() )

        self.editCopyAction.setWhatsThis( editCopyText )
        
                         #### editPasteAction ####
        
        editPasteText = "<u><b>Paste</b></u>     (Ctrl + V)</b></p><br> "\
                       "<p><img source=\"editPaste\"><br> "\
                       "Click this button to <b>Paste</b> the last <em> Copied  </em> or <em>Cut    </em> operation."\
                       " The Paste function outputs what is currently on the clipboard.      You can also select the <b>Paste</b> command "\
                       "from the <em>Edit</em> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editPaste",
                                                       self.editPasteAction.iconSet().pixmap() )

        self.editPasteAction.setWhatsThis( editPasteText )
   
                            #### editDeleteAction ####
                                 
        editDeleteText =  "<u><b>Delete</b></u>     (DEL)</b></p><br> "\
                       "<p><img source=\"editDelete\"><br> "\
                       "Click this button to <b>Delete</b> the selected <em> chunk </em> or atom."\
                       " Deleting an object does not add the object to the clipboard.       You can also select the <b>Delete</b> command "\
                       "from the <em>Edit</em> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editDelete",
                                                       self.editDeleteAction.iconSet().pixmap() )

        self.editDeleteAction.setWhatsThis( editDeleteText )
        
        ##############################################
        # View Toolbar
        ##############################################
        
        #### set Home View####
        
        setViewHomeActionText = "<u><b>Home</b></u>     (Home)<br>"\
                       "<p><img source=\"setViewHome\"><br> "\
                       "This tool sets the parts view to the <b>Home</b> setting."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewHome",
                                                       self. setViewHomeAction.iconSet().pixmap() )

        self.setViewHomeAction.setWhatsThis(  setViewHomeActionText )

        #### Refit to window View####
        
        setViewFitToWindowActionText = "<u><b>Fit To Window</b></u><br>"\
                       "<p><img source=\"setViewFitToWindow\"><br> "\
                       "This tool will fit the part to the size of the screen."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewFitToWindow",
                                                       self. setViewFitToWindowAction.iconSet().pixmap() )

        self.setViewFitToWindowAction.setWhatsThis(  setViewFitToWindowActionText )       
        
         #### set Ortho View####
        
        setViewOrthoActionText = "<u><b>Ortho</b></u><br>"\
                       "<p><img source=\"setViewOrtho\"><br> "\
                       "This tool gives the user a view of an object that is orthogonal to the view of the user.  With the <b>Ortho</b> tool the object is independant of size or distance as in a blueprint."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewOrtho",
                                                       self. setViewOrthoAction.iconSet().pixmap() )

        self.setViewOrthoAction.setWhatsThis(  setViewOrthoActionText )

           #### set Perspective View####
        
        setViewPerspecActionText = "<u><b>Perspective</b></u><br>"\
                       "<p><img source=\"setViewPerspec\"><br> "\
                       "When using the <b>Perspective</b> viewing tool a lattice will not line up to be viewed as a two dimensional structure.  With a <b>Perspective</b> projection:  objects are smaller with distance, as in a photograph."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewPerspec",
                                                       self. setViewPerspecAction.iconSet().pixmap() )

        self.setViewPerspecAction.setWhatsThis(  setViewPerspecActionText )        

           #### set Front View ####
        
        setViewFrontActionText = "<u><b>Front</b></u><br>"\
                       "<p><img source=\"setViewFront\"><br> "\
                       "The <b>Front</b> view tool will show the <em> chunk </em> as seen from the <b>Front</b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewFront",
                                                       self. setViewFrontAction.iconSet().pixmap() )

        self.setViewFrontAction.setWhatsThis(  setViewFrontActionText )  

           #### set Back View ####
        
        setViewBackActionText = "<u><b>Back</b></u><br>"\
                       "<p><img source=\"setViewBack\"><br> "\
                       "The <b>Back</b> view tool will show the <em> chunk </em> as seen from the <b>Back</b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewBack",
                                                       self. setViewBackAction.iconSet().pixmap() )

        self.setViewBackAction.setWhatsThis(  setViewBackActionText )     
        
                   #### set Top View ####
        
        setViewTopActionText = "<u><b>Top</b></u><br>"\
                       "<p><img source=\"setViewTop\"><br> "\
                       "The <b>Top</b> view tool will show the <em> chunk </em> as seen from the <b>Top</b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewTop",
                                                       self. setViewTopAction.iconSet().pixmap() )

        self.setViewTopAction.setWhatsThis(  setViewTopActionText )      
        
                           #### set Bottom View ####
        
        setViewBottomActionText = "<u><b>Bottom</b></u><br>"\
                       "<p><img source=\"setViewBottom\"><br> "\
                       "The <b>Bottom</b>  view tool will show the <em> chunk </em> as seen from the <b>Bottom</b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewBottom",
                                                       self. setViewBottomAction.iconSet().pixmap() )

        self.setViewBottomAction.setWhatsThis(  setViewBottomActionText )  
        
                                   #### set Left View ####
        
        setViewLeftActionText = "<u><b>Left</b></u><br>"\
                       "<p><img source=\"setViewLeft\"><br> "\
                       "The <b>Left</b>  view tool will show the <em> chunk </em>  as seen from the <b>Left</b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewLeft",
                                                       self. setViewLeftAction.iconSet().pixmap() )

        self.setViewLeftAction.setWhatsThis(  setViewLeftActionText )
        
                                           #### set Right View ####
        
        setViewRightActionText = "<u><b>Right</b></u><br>"\
                       "<p><img source=\"setViewRight\"><br> "\
                       "The <b>Right</b>  view tool will show the <em> chunk </em> as seen from the <b>Right </b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewRight",
                                                       self. setViewRightAction.iconSet().pixmap() )

        self.setViewRightAction.setWhatsThis(  setViewRightActionText )
        
        ##############################################
        # Grids Toolbar
        ##############################################
        
        #### Surface 100####


        
        orient100ActionText = "<u><b>Surface100</b></u><br>"\
                       "<p><img source=\"orient100Action\"><br> "\
                       "Selecting <b>Surface (1,0,0)</b> shifts the view to the nearest angle that would look straight into a (1,0,0) surface of a diamond lattice in standard orientation."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient100Action",
                                                       self.orient100Action.iconSet().pixmap() )

        self.orient100Action.setWhatsThis(orient100ActionText )
        
                #### Surface 110####


        
        orient110ActionText = "<u><b>Surface110</b></u><br>"\
                       "<p><img source=\"orient110Action\"><br> "\
                       "Selecting <b>Surface (1,1,0)</b> shifts the view to the nearest angle that would look straight into a (1,1,0) surface of a diamond lattice in standard orientation."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient110Action",
                                                       self.orient110Action.iconSet().pixmap() )

        self.orient110Action.setWhatsThis(orient110ActionText )
        
                        #### Surface 111####


        
        orient111ActionText = "<u><b>Surface111</b></u><br>"\
                       "<p><img source=\"orient111Action\"><br> "\
                       "Selecting <b>Surface (1,1,1)</b> shifts the view to the nearest angle that would look straight into a (1,1,1) surface of a diamond lattice in standard orientation."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient111Action",
                                                       self.orient111Action.iconSet().pixmap() )

        self.orient111Action.setWhatsThis(orient111ActionText )
        
        ##############################################
        # Molecular Display toolbar
        ##############################################
        
        ####Default####


        
        dispDefaultActionText = "<u><b>Default</b></u><br>"\
                       "<p><img source=\"dispDefaultAction\"><br> "\
                       "The <b>Default</b> display mode will set the atoms or <em> chunks </em>displayed view back to its originally displayed <b>Default</b> settings.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispDefaultAction",
                                                       self.dispDefaultAction.iconSet().pixmap() )

        self.dispDefaultAction.setWhatsThis(dispDefaultActionText )
 
         ####Invisible####


        
        dispInvisActionText = "<u><b>Invisible</b></u><br>"\
                       "<p><img source=\"dispInvisAction\"><br> "\
                       "<b>Invisible</b>  allows a selection of <em> chunks </em> or atoms to be displayed as <b>Invisible</b>.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispInvisAction",
                                                       self.dispInvisAction.iconSet().pixmap() )

        self.dispInvisAction.setWhatsThis(dispInvisActionText )       

           ####Lines####



        dispLinesActionText = "<u><b>Lines</b></u><br>"\
                       "<p><img source=\"dispLinesAction\"><br> "\
                       "The <b>Lines</b> display mode is a view setting that displays <em> chunks </em> and atoms as <b>Lines</b>.  In this display mode the user sees only the bonds of a <em> chunk </em>. "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispLinesAction",
                                                       self.dispLinesAction.iconSet().pixmap() )

        self.dispLinesAction.setWhatsThis(dispLinesActionText )  
        
                   ####Tubes####



        dispTubesActionText = "<u><b>Tubes</b></u><br>"\
                       "<p><img source=\"dispTubesAction\"><br> "\
                       "<b>Tubes</b> display mode is a display setting that shows the atoms and bonds as <b>Tubes</b>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispTubesAction",
                                                       self.dispTubesAction.iconSet().pixmap() )

        self.dispTubesAction.setWhatsThis(dispTubesActionText )  
        
        ####CPK####

        dispCPKActionText = "<u><b>CPK</b></u><br>"\
                       "<p><img source=\"dispCPKAction\"><br> "\
                       "Changes the display of the selected atoms to spheres and bonds to grey cylinders."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispCPKAction",
                                                       self.dispCPKAction.iconSet().pixmap() )

        self.dispCPKAction.setWhatsThis(dispCPKActionText ) 
        
                           ####VDW####



        dispVdWActionText = "<u><b>VdW</b></u><br>"\
                       "<p><img source=\"dispVdWAction\"><br> "\
                       "In Van der Waals (<b>VdW</b>) mode the atoms are viewed as spheres that are connected to one another."\
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
                       "Selects all the atoms while in <em>Select Atoms</em> mode, and selects all the chunks while in <em>Select Chunks</em> mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectAllAction",
                                                       self.selectAllAction.iconSet().pixmap() )

        self.selectAllAction.setWhatsThis(selectAllActionText )
        
                ####selectNone####


        
        selectNoneActionText = "<u><b>Select None</b></u>     (Ctrl + D)</b></p><br>"\
                       "<p><img source=\"selectNoneAction\"><br> "\
                       "The <b>Select None</b> tool will deselect all the atoms while in select atom mode.  When operating in <em>Select Chunks</em> mode the <b>Select None</b> tool will deselect all the <em>chunks</em>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectNoneAction",
                                                       self.selectNoneAction.iconSet().pixmap() )

        self.selectNoneAction.setWhatsThis(selectNoneActionText )
 
                 ####select Invert####


        
        selectInvertActionText = "<u><b>Select Invert</b></u>     (Ctrl + Shift + I)</b></p><br>"\
                       "<p><img source=\"selectInvertAction\"><br> "\
                       "In <em>Select chunks</em> mode, the <b>Select invert</b> tool will select all the <em>chunks</em> that are not selected, and deselect the <em>chunks</em> that are selected.  In <em>Select Atoms</em> mode, the unselected atoms are selected while the currently selected atoms are deselected."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectInvertAction",
                                                       self.selectInvertAction.iconSet().pixmap() )

        self.selectInvertAction.setWhatsThis(selectInvertActionText )
        
                         ####Select Connected####


        
        selectConnectedActionText = "<u><b>Select Connected</b></u>     (Ctrl + Shift+C)</b></p><br>"\
                       "<p><img source=\"selectConnectedAction\"><br> "\
                       "The <b>Select Connected</b> tool in <em> Select Atoms</em> mode selects all the atoms that can reach a currently selected atom by an unbroken chain of bonds.  This tool selects all the atoms that are bonded to the atom selected."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectConnectedAction",
                                                       self.selectConnectedAction.iconSet().pixmap() )

        self.selectConnectedAction.setWhatsThis(selectConnectedActionText )
        
                                 ####Select Doubly####


        
        selectDoublyActionText = "<u><b>Select Doubly</b></u>    (Ctrl + Shift + D)</b></p><br>"\
                       "<p><img source=\"selectDoublyAction\"><br> "\
                       "In select atoms mode, <b>Select Doubly</b> selects all the atoms that can be reached from a currently selected atom through two disjoint unbroken chains of bonds. Atoms singly connected to this group and unconnected to anything else are also included in the selection."\
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
                       "The <b>Minimize</b> feature will arrange the atoms to their chemically stable point of equilibrium in reference to the other atoms in the structure."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyMinimizeAction",
                                                       self.modifyMinimizeAction.iconSet().pixmap() )

        self.modifyMinimizeAction.setWhatsThis(modifyMinimizeActionText )
        
        ####Hydrogenate####


        
        modifyHydrogenateActionText = "<u><b>Hydrogenate</b></u>    (Ctrl + H)</b></p><br>"\
                       "<p><img source=\"modifyHydrogenateAction\"><br> "\
                       "The <b>Hydrogenate</b> feature adds hydrogens to all the open bonds in the <em>chunk</em>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyHydrogenateAction",
                                                       self.modifyHydrogenateAction.iconSet().pixmap() )

        self.modifyHydrogenateAction.setWhatsThis(modifyHydrogenateActionText )

          ####Dehydrogenate####


        
        modifyDehydrogenateActionText = "<u><b>Dehydrogenate</b></u><br>"\
                       "<p><img source=\"modifyDehydrogenateAction\"><br> "\
                       "<b>Dehydrogenate</b> removes the hydrogens from the <em>chunk</em>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyDehydrogenateAction",
                                                       self.modifyDehydrogenateAction.iconSet().pixmap() )

        self.modifyDehydrogenateAction.setWhatsThis(modifyDehydrogenateActionText )     
        
                  ####Passivate####


        
        modifyPassivateActionText = "<u><b>Passivate</b></u>    (Ctrl + P)</b></p><br>"\
                       "<p><img source=\"modifyPassivateAction\"><br> "\
                       "<b>Passivate</b> changes the types of incompletely bonded atoms to atoms with <br>the right number of bonds."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyPassivateAction",
                                                       self.modifyPassivateAction.iconSet().pixmap() )

        self.modifyPassivateAction.setWhatsThis(modifyPassivateActionText )   
        
                          ####Change Element####



        modifySetElementActionText = "<u><b>Change Element</b></u>    (Ctrl + E)</b></p><br>"\
                       "<p><img source=\"modifySetElementAction\"><br> "\
                       "The <b>Change Element</b> feature enables the user to choose the type of elements they wish to add by providing a graphical window with different elements to choose from.   If atoms are selected the <b>Change Element</b> tool will change their type; otherwise, the change element tool's primary use is intended for the <em>Build Tool</em>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifySetElementAction",
                                                       self.modifySetElementAction.iconSet().pixmap() )

        self.modifySetElementAction.setWhatsThis(modifySetElementActionText )  
        
                            ####Stretch####



        modifyStretchMoleculeActionText = "<u><b>Stretch</b></u><br>"\
                       "<p><img source=\"modifyStretchMoleculeAction\"><br> "\
                       "The <b>Stretch</b> feature stretches a <em>chunk</em> to a larger size by stretching the bonds of the <em> chunk </em>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyStretchMoleculeAction",
                                                       self.modifyStretchMoleculeAction.iconSet().pixmap() )

        self.modifyStretchMoleculeAction.setWhatsThis(modifyStretchMoleculeActionText )

                                    ####Separate####



        modifySeparateActionText = "<u><b>Separate</b></u><br>"\
                       "<p><img source=\"modifySeparateAction\"><br> "\
                       "The <b>Separate</b> feature creates a second <em> chunk </em>  from a larger <em> chunk </em>.   In effect pulling one <em> chunk </em> apart and having two separate <em> chunks </em>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifySeparateAction",
                                                       self.modifySeparateAction.iconSet().pixmap() )

        self.modifySeparateAction.setWhatsThis(modifySeparateActionText )  
        
                                            ####Weld Chunks####



        modifyWeldMoleculeActionText = "<u><b>Weld Chunks</b></u><br>"\
                       "<p><img source=\"modifyWeldMoleculeAction\"><br> "\
                       "The <b>Weld Chunks</b> tool merges two chunks into one chunk. "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyWeldMoleculeAction",
                                                       self.modifyWeldMoleculeAction.iconSet().pixmap() )
       
        self.modifyWeldMoleculeAction.setWhatsThis(modifyWeldMoleculeActionText )  
        
        ##############################################
        # Tools Toolbar
        ##############################################
        
        ####Select Chunks####


        toolsSelectMoleculesActionText = "<u><b>Select Chunks</b></u><br>"\
                       "<p><img source=\" toolsSelectMoleculesAction\"><br> "\
                       "The <b>Select Chunks</b> tool changes the behaviour of the cursor allowing the user to interact with and select <em>Chunks</em>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSelectMoleculesAction",
                                                       self. toolsSelectMoleculesAction.iconSet().pixmap() )
       
        self. toolsSelectMoleculesAction.setWhatsThis( toolsSelectMoleculesActionText )  

        ####Select Atoms####


        toolsSelectAtomsActionText = "<u><b>Select Atoms</b></u><br>"\
                       "<p><img source=\" toolsSelectAtomsAction\"><br> "\
                       "The <b>Select Atoms</b> tool changes the behaviour of the cursor allowing the user to interact with and select atoms."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSelectAtomsAction",
                                                       self. toolsSelectAtomsAction.iconSet().pixmap() )
       
        self. toolsSelectAtomsAction.setWhatsThis( toolsSelectAtomsActionText ) 
        

        
                        ####Move Chunks####


        toolsMoveMoleculeActionText = "<u><b>Move Chunks</b></u><br>"\
                       "<p><img source=\" toolsMoveMoleculeAction\"><br> "\
                       "The <b>Move Chunks</b> tool enables a selected <em>Chunk</em> to be moved around with respect to the unselected <em>Chunks<em>."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsMoveMoleculeAction",
                                                       self. toolsMoveMoleculeAction.iconSet().pixmap() )
       
        self. toolsMoveMoleculeAction.setWhatsThis( toolsMoveMoleculeActionText ) 
        
                                ####Build Tool####


        toolsDepositAtomActionText = "<u><b>Build Tool</b></u><br>"\
                       "<p><img source=\" toolsDepositAtomAction\"><br> "\
                       "The <b>Build Tool</b> gives the user a way to add atoms to open bonds.  The  <b>Build Tool</b> tool is one of ATOM's many ways to design and build new molecular machine parts."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsDepositAtomAction",
                                                       self. toolsDepositAtomAction.iconSet().pixmap() )
       
        self. toolsDepositAtomAction.setWhatsThis( toolsDepositAtomActionText ) 
        
                                        ####Cookie Cutter####


        toolsCookieCutActionText = "<u><b>Cookie Cutter</b></u><br>"\
                       "<p><img source=\" toolsCookieCutAction\"><br> "\
                       "The <b>Cookie Cutter</b> tool can cut three dimensional shapes called cookies out of a specifically oriented diamond lattice. "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsCookieCutAction",
                                                       self. toolsCookieCutAction.iconSet().pixmap() )
       
        self. toolsCookieCutAction.setWhatsThis( toolsCookieCutActionText )
        
                                    ####Extrude####


        toolsExtrudeActionText = "<u><b>Extrude</b></u><br>"\
                       "<p><img source=\" toolsExtrudeAction\"><br> "\
                       "The <b> Extrude   </b>  tool enables the user to apply a third dimension to a two dimensional surface.  An object must be selected to enter Extrude mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsExtrudeAction",
                                                       self. toolsExtrudeAction.iconSet().pixmap() )
       
        self. toolsExtrudeAction.setWhatsThis( toolsExtrudeActionText )  
        
                                    ####Allign to common Axis####


        toolsAlignToCommonAxisActionText = "<u><b>AlignToCommonAxis</b></u><br>"\
                       "<p><img source=\"toolsAlignToCommonAxis\"><br> "\
                       "The <b>Align To Common Axis</b> tool enables the user place two seperate parts on a common axis."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "toolsAlignToCommonAxis",
                                                       self. toolsAlignToCommonAxisAction.iconSet().pixmap() )
       
        self. toolsAlignToCommonAxisAction.setWhatsThis( toolsAlignToCommonAxisActionText )

                                    ####Movie####


        toolsMovieActionText = "<u><b>Movie</b></u><br>"\
                       "<p><img source=\" toolsMovieAction\"><br> "\
                       "The <b>Movie</b> tool will view & play the trajectory file that was created by the simulator.  This tool will show the simulation created by the designated parameters of the <em> Simulator</em>  tool."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsMovieAction",
                                                       self. toolsMovieAction.iconSet().pixmap() )
       
        self. toolsMovieAction.setWhatsThis( toolsMovieActionText )  
        
                                    ####Simulator####


        toolsSimulator_ActionText = "<u><b>Simulator</b></u><br>"\
                       "<p><img source=\" toolsSimulator_Action\"><br> "\
                       "The <b>Simulator</b> tool simulates the positions of the atoms based on their inter-atomic potentials and bonding between the atoms of the structure.  The <b> Simulator </b>  tool takes temperature, time step, and the number of frames as the input parameters."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSimulator_Action",
                                                       self. toolsSimulator_Action.iconSet().pixmap() )
       
        self. toolsSimulator_Action.setWhatsThis( toolsSimulator_ActionText )
        
        ##############################################
        # Dashboard Buttons
        ##############################################
        
        ####done checkmark####


        toolsDoneActionText = "<u><b>Done</b></u><br>"\
                       "<p><img source=\" toolsDoneAction\"><br> "\
                       "The <b>Done</b> icon completes the current operation and re-enters the user into Selection mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsDoneAction",
                                                       self. toolsDoneAction.iconSet().pixmap() )
       
        self. toolsDoneAction.setWhatsThis( toolsDoneActionText )  

        ####Cancel####


        toolsCancelActionText = "<u><b>Cancel</b></u><br>"\
                       "<p><img source=\" toolsCancelAction\"><br> "\
                       "The <b>Cancel</b> icon cancels the current operation and re-enters the user into Selection mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsCancelAction",
                                                       self.toolsCancelAction.iconSet().pixmap() )
       
        self. toolsCancelAction.setWhatsThis( toolsCancelActionText ) 
        
        ####Back up####

        toolsBackUpActionText = "<u><b>Back Up</b></u><br>"\
                       "<p><img source=\" toolsBackUpAction\"><br> "\
                       "<b>Back Up</b> undoes the previous operation."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsBackUpAction",
                                                       self.toolsBackUpAction.iconSet().pixmap() )
       
        self. toolsBackUpAction.setWhatsThis( toolsBackUpActionText ) 
   
                   ####Start Over####
                        
        toolsStartOverActionText = "<u><b>Start Over</b></u><br>"\
                       "<p><img source=\"toolsStartOverAction\"><br> "\
                       "The <b>Start Over</b> icon cancels the current operation and leaves the user in the current mode."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "toolsStartOverAction",
                                                       self.toolsStartOverAction.iconSet().pixmap() )
       
        self.toolsStartOverAction.setWhatsThis(toolsStartOverActionText ) 
        
                      ####Add Layersr####
                        
        ccAddLayerActionText = "<u><b>Add Layer</b></u><br>"\
                       "<p><img source=\"ccAddLayerAction\"><br> "\
                       "The <b>Add Layer</b> form box provides the user a way to specify the thickness of layers in Angstroms.  The spin box provides a way for the user to specify the number of lattice layers of the cookie that will be cut."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "ccAddLayerAction",
                                                       self.ccAddLayerAction.iconSet().pixmap() )
       
        self.ccAddLayerAction.setWhatsThis(ccAddLayerActionText ) 
        
        ##############################################
        # Jigs
        ##############################################
        
        ####Ground####


        jigsGroundActionText = "<u><b>Ground</b></u><br>"\
                       "<p><img source=\"jigsGroundAction\"><br> "\
                       "The <b>Ground</b> jig makes the selected atoms fixed, and constrains their motion.  The selected atoms will be used as a stand still atom (or grounded atom) in the simulator."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsGroundAction",
                                                       self.jigsGroundAction.iconSet().pixmap() )
       
        self.jigsGroundAction.setWhatsThis(jigsGroundActionText )  
        
                ####Rotary Motor####


        jigsMotorActionText = "<u><b>Motor</b></u><br>"\
                       "<p><img source=\"jigsMotorAction\"><br> "\
                       "The <b>Rotary Motor</b> allows the user to apply a torque to the selected atoms in the simulator."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsMotorAction",
                                                       self.jigsMotorAction.iconSet().pixmap() )
       
        self.jigsMotorAction.setWhatsThis(jigsMotorActionText )  
        
                        ####Linear Motor####


        jigsLinearMotorActionText = "<u><b>Linear Motor</b></u><br>"\
                       "<p><img source=\"jigsLinearMotorAction\"><br> "\
                       "The <b>Linear Motor</b> applies force to the selected section atoms, that section is allowed to moved on a fixed axis with one degree of freedom in the simulator."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsLinearMotorAction",
                                                       self.jigsLinearMotorAction.iconSet().pixmap() )
       
        self.jigsLinearMotorAction.setWhatsThis(jigsLinearMotorActionText )  
        
                                ####Thermostat####


        jigsStatActionText = "<u><b>Thermostat</b></u><br>"\
                       "<p><img source=\"jigsStatAction\"><br> "\
                       " <b>Thermostat</b> sets the temperature of the selected atom(s) for the simulator."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "jigsStatAction",
                                                       self.jigsStatAction.iconSet().pixmap() )
       
        self.jigsStatAction.setWhatsThis(jigsStatActionText ) 
        
        ##############################################
        # Display
        ##############################################
        
        ####Display ObjectColor####


        dispObjectColorActionText = "<u><b>Molecule Color</b></u><br>"\
                       "<p><img source=\"dispObjectColorAction\"><br> "\
                       "The <b>Molecule Color</b> menu icon gives the ability to change the molecule color to any desired color."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispObjectColorAction",
                                                       self.dispObjectColorAction.iconSet().pixmap() )
       
        self.dispObjectColorAction.setWhatsThis(dispObjectColorActionText ) 
        
                ####Display Background Color####


        dispBGColorActionText = "<u><b>Background Color</b></u><br>"\
                       "<p><img source=\"dispBGColorAction\"><br> "\
                       " <b>Background Color</b> allows the user to change the background color of the main window."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispBGColorAction",
                                                       self.dispBGColorAction.iconSet().pixmap() )
       
        self.dispBGColorAction.setWhatsThis(dispBGColorActionText ) 
        ##############################################
        # Display
        ##############################################
        
        ####Display ObjectColor####


        dispTrihedronText = "<u><b>Molecule Color</b></u><br>"\
                       "<p><img source=\"dispTrihedron\"><br> "\
                       "<b>Object Color</b> allows the user to change the color of the selected object(s)."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispTrihedron",
                                                       self.dispTrihedronAction.iconSet().pixmap() )
       
        self.dispTrihedronAction.setWhatsThis(dispTrihedronText ) 
        
                ####Display Background Color####


        dispBGColorActionText = "<u><b>Background Color</b></u><br>"\
                       "<p><img source=\"dispBGColorAction\"><br> "\
                       "<b>Background Color</b> allows the user to change the color of the background color of the main window."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispBGColorAction",
                                                       self.dispBGColorAction.iconSet().pixmap() )
       
        self.dispBGColorAction.setWhatsThis(dispBGColorActionText ) 
              