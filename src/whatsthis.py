from qt import *

def createWhatsThis(self):
        
        ##############################################
        # File Toolbar
        ##############################################
        
        #### fileOpenAction ####
        
        fileOpenText = "<u><b>Open File</b></u><br> "\
                        "<p><img source=\"fileopen\"> "\
                       "   Click this button to open a <em>new file</em>. <br>"\
                       "You can also select the <b>Open</b> command "\
                       "from the <b>File</b> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "fileopen",
                                                       self.fileOpenAction.iconSet().pixmap() )

        self.fileOpenAction.setWhatsThis( fileOpenText )
        
        #### fileSaveAction ####
        
        fileSaveText = "<p><img source=\"filesave\"> "\
                       "Click this button to save the <em>current part</em>. <br>"\
                       "You can also select the <b>Save</b> command "\
                       "from the <b>File</b> menu.</p>"

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
                       "from the <b>Edit</b>.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editUndo",
                                                       self.editUndoAction.iconSet().pixmap() )

        self.editUndoAction.setWhatsThis( editUndoText )
        
        #### editRedoAction ####
        
        editRedoText =  "<u><b>Redo</b></u>     (Ctrl + Y)</b></p><br> "\
                       "<p><img source=\"editRedo\"> <br>"\
                       "Click this button to <b>Redo</b> the last operation."\
                       "        You can also select the <b>Redo</b> command "\
                       "from the <b>Edit</b> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editRedo",
                                                       self.editRedoAction.iconSet().pixmap() )

        self.editRedoAction.setWhatsThis( editRedoText )
        
         #### editCutAction ####
        
        editCutText =  "<u><b>Cut</b></u>     (Ctrl + X)</b></p><br> "\
                       "<p><img source=\"editCut\"><br> "\
                       "Click this button to <b>Cut</b> the last operation."\
                       "        You can also select the <b>Cut</b> command "\
                       "from the <b>Edit</b> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editCut",
                                                       self.editCutAction.iconSet().pixmap() )

        self.editCutAction.setWhatsThis( editCutText )
        
                 #### editCopyAction ####
        
        editCopyText =  "<u><b>Copy</b></u>     (Ctrl + C)</b></p><br> "\
                       "<p><img source=\"editCopy\"><br> "\
                       "Click this button to <b>copy</b> the selected part or atoms."\
                       "        You can also select the <b>Copy</b> command "\
                       "from the <b>Edit</b> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editCopy",
                                                       self.editCopyAction.iconSet().pixmap() )

        self.editCopyAction.setWhatsThis( editCopyText )
        
                         #### editPasteAction ####
        
        editPasteText = "<u><b>Paste</b></u>     (Ctrl + V)</b></p><br> "\
                       "<p><img source=\"editPaste\"><br> "\
                       "Click this button to <b>Paste</b> the last copied or <b>Cut</b> operation."\
                       "        You can also select the <b>Paste</b> command "\
                       "from the <b>Edit</b> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editPaste",
                                                       self.editPasteAction.iconSet().pixmap() )

        self.editPasteAction.setWhatsThis( editPasteText )
   
                            #### editDeleteAction ####
                                 
        editDeleteText =  "<u><b>Delete</b></u>     (DEL)</b></p><br> "\
                       "<p><img source=\"editDelete\"><br> "\
                       "Click this button to <b>Delete</b> the selected part or atoms."\
                       "        You can also select the <b>Delete</b> command "\
                       "from the <b>Edit</b> menu.</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "editDelete",
                                                       self.editDeleteAction.iconSet().pixmap() )

        self.editDeleteAction.setWhatsThis( editDeleteText )
        
        ##############################################
        # View Toolbar
        ##############################################
        
        #### set Home View####
        
        setViewHomeActionText = "<u><b>Home</b></u>     (Home)<br>"\
                       "<p><img source=\"setViewHome\"><br> "\
                       "This icon sets the parts view to the <b>Home</b> setting."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewHome",
                                                       self. setViewHomeAction.iconSet().pixmap() )

        self.setViewHomeAction.setWhatsThis(  setViewHomeActionText )

        #### Refit to window View####
        
        setViewFitToWindowActionText = "<u><b>Fit To Window</b></u><br>"\
                       "<p><img source=\"setViewFitToWindow\"><br> "\
                       "This icon will fit the part to the size of the screen."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewFitToWindow",
                                                       self. setViewFitToWindowAction.iconSet().pixmap() )

        self.setViewFitToWindowAction.setWhatsThis(  setViewFitToWindowActionText )       
        
         #### set Ortho View####
        
        setViewOrthoActionText = "<u><b>Ortho</b></u><br>"\
                       "<p><img source=\"setViewOrtho\"><br> "\
                       "This icon gives the user a view of an object that is orthogonal to the view of the user."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewOrtho",
                                                       self. setViewOrthoAction.iconSet().pixmap() )

        self.setViewOrthoAction.setWhatsThis(  setViewOrthoActionText )

           #### set Perspective View####
        
        setViewPerspecActionText = "<u><b>Perspective</b></u><br>"\
                       "<p><img source=\"setViewPerspec\"><br> "\
                       "When using the <b>Perspective</b> viewing mode a lattice will not line up to be viewed as a two dimensional structure."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewPerspec",
                                                       self. setViewPerspecAction.iconSet().pixmap() )

        self.setViewPerspecAction.setWhatsThis(  setViewPerspecActionText )        

           #### set Front View ####
        
        setViewFrontActionText = "<u><b>Front</b></u><br>"\
                       "<p><img source=\"setViewFront\"><br> "\
                       "The <b>Front</b> view icon will show the molecule or part as seen from the <b>Front</b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewFront",
                                                       self. setViewFrontAction.iconSet().pixmap() )

        self.setViewFrontAction.setWhatsThis(  setViewFrontActionText )  

           #### set Back View ####
        
        setViewBackActionText = "<u><b>Back</b></u><br>"\
                       "<p><img source=\"setViewBack\"><br> "\
                       "The <b>Back</b> view icon will show the molecule or part as seen from the <b>Back</b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewBack",
                                                       self. setViewBackAction.iconSet().pixmap() )

        self.setViewBackAction.setWhatsThis(  setViewBackActionText )     
        
                   #### set Top View ####
        
        setViewTopActionText = "<u><b>Top</b></u><br>"\
                       "<p><img source=\"setViewTop\"><br> "\
                       "The <b>Top</b> view icon will show the molecule or part as seen from the <b>Top</b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewTop",
                                                       self. setViewTopAction.iconSet().pixmap() )

        self.setViewTopAction.setWhatsThis(  setViewTopActionText )      
        
                           #### set Bottom View ####
        
        setViewBottomActionText = "<u><b>Bottom</b></u><br>"\
                       "<p><img source=\"setViewBottom\"><br> "\
                       "The <b>Bottom</b>  view icon will show the molecule or part as seen from the <b>Bottom</b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewBottom",
                                                       self. setViewBottomAction.iconSet().pixmap() )

        self.setViewBottomAction.setWhatsThis(  setViewBottomActionText )  
        
                                   #### set Left View ####
        
        setViewLeftActionText = "<u><b>Left</b></u><br>"\
                       "<p><img source=\"setViewLeft\"><br> "\
                       "The <b>Left</b>  view icon will show the molecule or part as seen from the <b>Left</b> view of the object.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "setViewLeft",
                                                       self. setViewLeftAction.iconSet().pixmap() )

        self.setViewLeftAction.setWhatsThis(  setViewLeftActionText )
        
                                           #### set Right View ####
        
        setViewRightActionText = "<u><b>Right</b></u><br>"\
                       "<p><img source=\"setViewRight\"><br> "\
                       "The <b>Right</b>  view icon will show the molecule or part as seen from the <b>Right </b> view of the object.  "\
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
                       "The viewpoint orientation of this surface is set at (1, 0, 0) plane in Cartesian coordinates."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient100Action",
                                                       self.orient100Action.iconSet().pixmap() )

        self.orient100Action.setWhatsThis(orient100ActionText )
        
                #### Surface 110####


        
        orient110ActionText = "<u><b>Surface110</b></u><br>"\
                       "<p><img source=\"orient110Action\"><br> "\
                       "The viewpoint orientation of this surface is set at (1, 1, 0) plane in Cartesian coordinates."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "orient110Action",
                                                       self.orient110Action.iconSet().pixmap() )

        self.orient110Action.setWhatsThis(orient110ActionText )
        
                        #### Surface 111####


        
        orient111ActionText = "<u><b>Surface111</b></u><br>"\
                       "<p><img source=\"orient111Action\"><br> "\
                       "The viewpoint orientation of this surface is set at (1, 1, 1) plane in Cartesian coordinates."\
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
                       "The <b>Default</b> icon will set the atoms or molecules back to their originally displayed <b>Default</b> settings.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispDefaultAction",
                                                       self.dispDefaultAction.iconSet().pixmap() )

        self.dispDefaultAction.setWhatsThis(dispDefaultActionText )
 
         ####Invisible####


        
        dispInvisActionText = "<u><b>Invisible</b></u><br>"\
                       "<p><img source=\"dispInvisAction\"><br> "\
                       "<b>Invisible</b>  allows a selection of molecules or atoms to be displayed as <b>Invisible</b>.  "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispInvisAction",
                                                       self.dispInvisAction.iconSet().pixmap() )

        self.dispInvisAction.setWhatsThis(dispInvisActionText )       

           ####Lines####



        dispLinesActionText = "<u><b>Lines</b></u><br>"\
                       "<p><img source=\"dispLinesAction\"><br> "\
                       "The <b>Lines</b> display mode is a view setting that displays the molecules and atoms as <b>Lines</b>.  In this display mode the user sees only the bonds of a molecule."\
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
                       "This setting is known as <b>CPK</b> display mode.   This mode displays the atoms as ball and stick objects."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispCPKAction",
                                                       self.dispCPKAction.iconSet().pixmap() )

        self.dispCPKAction.setWhatsThis(dispCPKActionText ) 
        
                           ####VDW####



        dispVdWActionText = "<u><b>VdW</b></u><br>"\
                       "<p><img source=\"dispVdWAction\"><br> "\
                       "In Van der Waals (<b>VdW</b>) mode the atoms are viewed as balls that are connected to one another."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "dispVdWAction",
                                                       self.dispVdWAction.iconSet().pixmap() )

        self.dispVdWAction.setWhatsThis(dispVdWActionText )         
        
        ##############################################
        # Select toolbar
        ##############################################
        
        ####selectAll####


        
        selectAllActionText = "<u><b>Select All</b></u><br>"\
                       "<p><img source=\"selectAllAction\"><br> "\
                       "The <b>Select All</b> icon will select all the atoms and or parts the screen."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectAllAction",
                                                       self.selectAllAction.iconSet().pixmap() )

        self.selectAllAction.setWhatsThis(selectAllActionText )
        
                ####selectNone####


        
        selectNoneActionText = "<u><b>Select None</b></u><br>"\
                       "<p><img source=\"selectNoneAction\"><br> "\
                       "The <b>Select None</b> icon will deselect all the atoms and parts the screen."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectNoneAction",
                                                       self.selectNoneAction.iconSet().pixmap() )

        self.selectNoneAction.setWhatsThis(selectNoneActionText )
 
                 ####selectInvert####


        
        selectInvertActionText = "<u><b>Select Invert</b></u><br>"\
                       "<p><img source=\"selectInvertAction\"><br> "\
                       "The <b>Select Invert</b> icon will select all the atoms and or parts not currently selected."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectInvertAction",
                                                       self.selectInvertAction.iconSet().pixmap() )

        self.selectInvertAction.setWhatsThis(selectInvertActionText )
        
                         ####Select Connected####


        
        selectConnectedActionText = "<u><b>Select Connected</b></u><br>"\
                       "<p><img source=\"selectConnectedAction\"><br> "\
                       "The <b>Select Connected</b> icon will select all the single bonded atoms to the atom selected."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectConnectedAction",
                                                       self.selectConnectedAction.iconSet().pixmap() )

        self.selectConnectedAction.setWhatsThis(selectConnectedActionText )
        
                                 ####Select Doubly####


        
        selectDoublyActionText = "<u><b>Select Doubly</b></u><br>"\
                       "<p><img source=\"selectDoublyAction\"><br> "\
                       "The <b>Select Doubly</b> icon will select all the double bonded atoms to the atom selected."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "selectDoublyAction",
                                                       self.selectDoublyAction.iconSet().pixmap() )

        self.selectDoublyAction.setWhatsThis(selectDoublyActionText )
        
        ##############################################
        # Modify Toolbar
        ##############################################
        
        ####Minimize####


        
        modifyMinimizeActionText = "<u><b>Minimize</b></u><br>"\
                       "<p><img source=\"modifyMinimizeAction\"><br> "\
                       "The <b>Minimize</b> function will arrange the atoms to their chemically stable point of equilibrium in reference to the other atoms in the structure."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyMinimizeAction",
                                                       self.modifyMinimizeAction.iconSet().pixmap() )

        self.modifyMinimizeAction.setWhatsThis(modifyMinimizeActionText )
        
        ####Hydrogenate####


        
        modifyHydrogenateActionText = "<u><b>Hydrogenate</b></u><br>"\
                       "<p><img source=\"modifyHydrogenateAction\"><br> "\
                       "The <b>Hydrogenate</b> function adds hydrogens to all the open bonds in the molecule."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyHydrogenateAction",
                                                       self.modifyHydrogenateAction.iconSet().pixmap() )

        self.modifyHydrogenateAction.setWhatsThis(modifyHydrogenateActionText )

          ####Dehydrogenate####


        
        modifyDehydrogenateActionText = "<u><b>Dehydrogenate</b></u><br>"\
                       "<p><img source=\"modifyDehydrogenateAction\"><br> "\
                       "<b>Dehydrogenate</b> removes the hydrogens from the molecule."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyDehydrogenateAction",
                                                       self.modifyDehydrogenateAction.iconSet().pixmap() )

        self.modifyDehydrogenateAction.setWhatsThis(modifyDehydrogenateActionText )     
        
                  ####Passivate####


        
        modifyPassivateActionText = "<u><b>Passivate</b></u><br>"\
                       "<p><img source=\"modifyPassivateAction\"><br> "\
                       "<b>Passivate</b> changes the types of incompletely bonded atoms to atoms with <br>the right number of bonds."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyPassivateAction",
                                                       self.modifyPassivateAction.iconSet().pixmap() )

        self.modifyPassivateAction.setWhatsThis(modifyPassivateActionText )   
        
                          ####Change Element####



        modifySetElementActionText = "<u><b>Set Element</b></u><br>"\
                       "<p><img source=\"modifySetElementAction\"><br> "\
                       "The <b>Set Element</b> function enables the user to choose the type of element they wish to add by providing a graphical window with different elements to choose from."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifySetElementAction",
                                                       self.modifySetElementAction.iconSet().pixmap() )

        self.modifySetElementAction.setWhatsThis(modifySetElementActionText )  
        
                            ####Stretch####



        modifyStretchMoleculeActionText = "<u><b>Set Element</b></u><br>"\
                       "<p><img source=\"modifyStretchMoleculeAction\"><br> "\
                       "The <b>Stretch Molecule</b> feature stretches a molecule to a larger size by stretching the bonds of the molecule."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyStretchMoleculeAction",
                                                       self.modifyStretchMoleculeAction.iconSet().pixmap() )

        self.modifyStretchMoleculeAction.setWhatsThis(modifyStretchMoleculeActionText )

                                    ####Stretch####



        modifySeparateActionText = "<u><b>Separate</b></u><br>"\
                       "<p><img source=\"modifySeparateAction\"><br> "\
                       "This <b>Separate</b> function is used to create a second molecule from a piece of a larger molecule.   In effect pulling apart one chunk into two separate chunks."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifySeparateAction",
                                                       self.modifySeparateAction.iconSet().pixmap() )

        self.modifySeparateAction.setWhatsThis(modifySeparateActionText )  
        
                                            ####Stretch####



        modifyWeldMoleculeActionText = "<u><b>Weld Molecule</b></u><br>"\
                       "<p><img source=\"modifyWeldMoleculeAction\"><br> "\
                       "The <b>Weld Molecule</b> feature enables the user to specify the exact locations that two molecules will form bonds when welded together. "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( "modifyWeldMoleculeAction",
                                                       self.modifyWeldMoleculeAction.iconSet().pixmap() )
       
        self.modifyWeldMoleculeAction.setWhatsThis(modifyWeldMoleculeActionText )  
        
        ##############################################
        # Tools Toolbar
        ##############################################
        
        ####Select Molecules####


        toolsSelectMoleculesActionText = "<u><b> toolsSelectMolecules</b></u><br>"\
                       "<p><img source=\" toolsSelectMoleculesAction\"><br> "\
                       "The <b>Select Molecules</b> icon is a selection tool allowing the user to intereact with and select molecules."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSelectMoleculesAction",
                                                       self. toolsSelectMoleculesAction.iconSet().pixmap() )
       
        self. toolsSelectMoleculesAction.setWhatsThis( toolsSelectMoleculesActionText )  

        ####Select Atoms####


        toolsSelectAtomsActionText = "<u><b>Select Atoms</b></u><br>"\
                       "<p><img source=\" toolsSelectAtomsAction\"><br> "\
                       "The <b>Select Atoms</b> icon is a selection tool allowing the user to intereact with and select individual atoms."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSelectAtomsAction",
                                                       self. toolsSelectAtomsAction.iconSet().pixmap() )
       
        self. toolsSelectAtomsAction.setWhatsThis( toolsSelectAtomsActionText ) 
        
                ####Select Atoms####


        toolsSelectAtomsActionText = "<u><b>Select Atoms</b></u><br>"\
                       "<p><img source=\" toolsSelectAtomsAction\"><br> "\
                       "The <b>Select Atoms</b> icon is a selection tool allowing the user to intereact with and select individual atoms."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsSelectAtomsAction",
                                                       self. toolsSelectAtomsAction.iconSet().pixmap() )
       
        self. toolsSelectAtomsAction.setWhatsThis( toolsSelectAtomsActionText ) 
        
                ####Move Molecule####


        toolsMoveMoleculeActionText = "<u><b>Move Molecule</b></u><br>"\
                       "<p><img source=\" toolsMoveMoleculeAction\"><br> "\
                       "The <b>Move Molecule</b> tool enables a selected object to be moved around with respect to the unselected parts at the origin.  ."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsMoveMoleculeAction",
                                                       self. toolsMoveMoleculeAction.iconSet().pixmap() )
       
        self. toolsMoveMoleculeAction.setWhatsThis( toolsMoveMoleculeActionText ) 
        
                        ####Move Molecule####


        toolsMoveMoleculeActionText = "<u><b>Move Molecule</b></u><br>"\
                       "<p><img source=\" toolsMoveMoleculeAction\"><br> "\
                       "The <b>Move Molecule</b> tool enables a selected object to be moved around with respect to the unselected parts at the origin.  ."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsMoveMoleculeAction",
                                                       self. toolsMoveMoleculeAction.iconSet().pixmap() )
       
        self. toolsMoveMoleculeAction.setWhatsThis( toolsMoveMoleculeActionText ) 
        
                                ####Build Atom####


        toolsDepositAtomActionText = "<u><b>Build Atom</b></u><br>"\
                       "<p><img source=\" toolsDepositAtomAction\"><br> "\
                       "The <b>Build Atom</b> tool gives the user a way to add atoms to open bonds.  The  <b>Build Atom</b> tool is one of ATOM's many ways to design and build new molecular machine parts."\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsDepositAtomAction",
                                                       self. toolsDepositAtomAction.iconSet().pixmap() )
       
        self. toolsDepositAtomAction.setWhatsThis( toolsDepositAtomActionText ) 
        
                                        ####Cookie Cutter####


        toolsCookieCutActionText = "<u><b>Build Atom</b></u><br>"\
                       "<p><img source=\" toolsCookieCutAction\"><br> "\
                       "The <b>Cookie Cutter</b> tool delivers the ability to cut three dimensional shapes called cookies out of a specifically oriented diamond lattice. "\
                       "</p>"

        QMimeSourceFactory.defaultFactory().setPixmap( " toolsCookieCutAction",
                                                       self. toolsCookieCutAction.iconSet().pixmap() )
       
        self. toolsCookieCutAction.setWhatsThis( toolsCookieCutActionText )