# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
import qt
from qt import QMainWindow, QPixmap, QWidget, QFrame, QPushButton
from qt import QGroupBox, QComboBox, QAction, QMenuBar, QPopupMenu
from qt import SIGNAL, SLOT, QListView, QListViewItem, QFileDialog
from GLPane import *
import os
import help
from runSim import runSim
from modelTree import *

from constants import *
from elementSelector import *
from fileIO import *
from debug import print_compact_traceback

from MainWindowUI import MainWindow
helpwindow = None
elementwindow = None
windowList = []

eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]

eCCBtab2 = {}
for i,elno in zip(range(len(eCCBtab1)), eCCBtab1):
    eCCBtab2[elno] = i

def fileparse(name):
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))

class MWsemantics(MainWindow):
    def __init__(self,parent = None, name = None, fl = 0):
	
        global windowList

        MainWindow.__init__(self, parent, name, fl)

        # bruce 040920: until MainWindow.ui does the following, I'll do it manually:
        import extrudeMode as _extrudeMode
        _extrudeMode.do_what_MainWindowUI_should_do(self)
        # (the above function will set up both Extrude and Revolve)
        
        import depositMode as _depositMode
        _depositMode.do_what_MainWindowUI_should_do(self)

        # this got lost in MainWindowUI somehow
        self.disconnect(self.editCopyAction,SIGNAL("activated()"),self.copyDo)
        self.connect(self.editCopyAction,SIGNAL("activated()"),self.editCopy)
        
        # Load all the custom cursors
        self.loadCursors()
        
        # Hide all dashboards
        self.hideDashboards()
        
        # Create our 2 status bar widgets - msgbarLabel and modebarLabel
        self.createStatusBars()
        
        windowList += [self]
        if name == None:
            self.setName("Atom")

	    # start with empty window 
        self.assy = assembly(self, "Empty")
        
        # Set the caption to the name of the current (default) part - Mark [2004-10-11]
        self.setCaption(self.trUtf8("Atom - " + "[" + self.assy.name + "]"))

        # Create the splitter between glpane and the model tree
        splitter = QSplitter(Qt.Horizontal, self, "ContentsWindow")
        
        # Create the model tree widget
        self.mt = self.modelTreeView = modelTree(splitter, self)
        self.modelTreeView.setMinimumSize(0, 0)
        
        # Create the glpane - where all the action is!
        self.glpane = GLPane(self.assy, splitter, "glpane", self)

        # Some final splitter setup
        splitter.setResizeMode(self.modelTreeView, QSplitter.KeepSize)       
        splitter.setOpaqueResize(False)
        self.setCentralWidget(splitter)
        
        # do here to avoid a circular dependency
        self.assy.o = self.glpane
        self.assy.mt = self.mt

        # We must enable keyboard focus for a widget if it processes
        # keyboard events.
        self.setFocusPolicy(QWidget.StrongFocus)

        # Start with Carbon as the default element (for Deposit Mode
        # and the Element Selector)
        self.Element = 6
        self.setElement(6)
        # and paste the atom rather than the clipboard by default
        self.pasteP = False
        

    def update_mode_status(self, mode_obj = None):
        """[by bruce 040927]
        
        Update the text shown in self.modebarLabel (if that widget
        exists yet).  Get the text to use from mode_obj if supplied,
        otherwise from the current mode object
        (self.glpane.mode). (The mode object has to be supplied when
        the currently stored one is incorrect, during a mode
        transition.) #####doit

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
        # change to (the id of) self.glpane, self.glpane.mode,
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
            widget = self.modebarLabel
        except AttributeError:
            print "AttributeError: self.modebarLabel"
            pass # this is normal, before the widget exists
        else:
            mode_obj = mode_obj or self.glpane.mode
            text = mode_obj.get_mode_status_text()
            widget.setText( text )


    ##################################################
    # The beginnings of an invalidate/update mechanism
    # at the moment it just does update whether needed or not
    ##################################################

    def update(self):
        self.glpane.paintGL()
        self.mt.update()
        

    ###################################
    # functions from the "File" menu
    ###################################

    def fileNew(self):
        """If this window is empty (has no assembly), do nothing.
        Else create a new empty one.
        """
        foo = MWsemantics()
        foo.show()

    def fileInsert(self):
        wd = globalParms['WorkingDirectory']
        fn = QFileDialog.getOpenFileName(wd,
                "Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb);;All of the above (*.pdb *.mmp)",
                self )
        
        if fn:

            fn = str(fn)
            if not os.path.exists(fn): return

            if fn[-3:] == "mmp":
                #print " MWsemantics.py: fileInsert(): inserting MMP file: ", fn
                insertmmp(self.assy, fn)
            if fn[-3:] == "pdb":
                #print " MWsemantics.py: fileInsert(): inserting PDB file: ", fn
                readpdb(self.assy, fn)

            self.assy.modified = 1 # The file and the part are not the same

            self.glpane.scale=self.assy.bbox.scale()
            self.glpane.paintGL()
            self.mt.update()

    def fileOpen(self):
        if self.assy.modified:
            ret = QMessageBox.information( self, "Atom",
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before opening a new part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: # Save clicked or Alt+S pressed or Enter pressed.
                self.fileSave()
                self.__clear() # Clear the part - we're loading a new file.
            elif ret==1: self.__clear() # Discard the part - we're loading a new file.
            elif ret==2: return # Cancel clicked or Alt+C pressed or Escape pressed

        wd = globalParms['WorkingDirectory']
        fn = QFileDialog.getOpenFileName(wd,
                "Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb);;All of the above (*.pdb *.mmp)",
                self )
        
        if fn:
            # I know we are clearing twice if the file was saved above.
            # This is desidered behavior - Mark [2004-10-11]
            self.__clear()  
                
            fn = str(fn)
            if not os.path.exists(fn): return

            if fn[-3:] == "mmp":
                readmmp(self.assy,fn)
            if fn[-3:] == "pdb":
                readpdb(self.assy,fn)

            dir, fil, ext = fileparse(fn)
            self.assy.name = fil
            self.assy.filename = fn
            self.assy.modified = 0 # The file and the part are now the same

            self.setCaption(self.trUtf8("Atom - " + "[" + self.assy.filename + "]"))

            #self.glpane.scale=self.assy.bbox.scale()
            #self.glpane.paintGL()
            self.setViewFitToWindow()
            self.mt.update()


    def fileSave(self):
        if self.assy:
            if self.assy.filename:
                fn = str(self.assy.filename)
                dir, fil, ext = fileparse(fn)
                writemmp(self.assy, dir + fil + ".mmp")
                self.setCaption(self.trUtf8("Atom - " + "[" + self.assy.filename + "]"))
                self.assy.modified = 0 # The file and the part are now the same.
                self.msgbarLabel.setText( "MMP file saved: " + self.assy.filename )
            else: self.fileSaveAs()

    def fileSaveAs(self):
        if self.assy:
            if self.assy.filename:
                dir, fil, ext = fileparse(self.assy.filename)
            else: dir, fil = "./", self.assy.name
        else:
            print "MWsemantics.py: fileSaveAs(): Part is Empty - nothing to save"
            return

        sfilter = QString("")   
        fn = QFileDialog.getSaveFileName(self.assy.filename,
                    "Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb);;POV-Ray (*.pov);;JPEG (*.jpg)",
                    self, "IDONTKNOWWHATTHISIS",
                    "Save As",
                    sfilter)
        
        if fn:
            fn = str(fn)
            dir, fil, ext = fileparse(fn)
            ext =str(sfilter[-5:-1]) # Get the file extension from the sfilter.

            if ext == ".pdb": # Write PDB file.
                try:
                    writepdb(self.assy, dir + fil + ext)
                except:
                    print "MWsemantics.py: fileSaveAs(): error writing file" + dir + fil + ext
                    self.msgbarLabel.setText( "Problem saving file: " + dir + fil + ext )
                else:
                    self.msgbarLabel.setText( "File saved: " + dir + fil + ext )
            
            elif ext == ".pov": # Write POV-Ray file
                try:
                    writepov(self.assy, dir + fil + ext)
                except:
                    print "MWsemantics.py: fileSaveAs(): error writing file " + dir + fil + ext
                    self.msgbarLabel.setText( "Problem saving file: " + dir + fil + ext )
                else:
                    self.msgbarLabel.setText( "File saved: " + dir + fil + ext )
            
            elif ext == ".jpg": # Write JPEG file
                try:
                    self.glpane.image(dir + fil + ext)
                except:
                    print "MWsemantics.py: fileSaveAs(): error writing file" + dir + fil + ext
                    self.msgbarLabel.setText( "Problem saving file: " + dir + fil + ext )
                else:
                    self.msgbarLabel.setText( "File saved: " + dir + fil + ext )

            elif ext == ".mmp" : # Write MMP file.
                self.assy.filename = dir + fil + ext
                self.assy.name = fil
                try:
                    writemmp(self.assy, dir + fil + ext)
                except:
                    print "MWsemantics.py: fileSaveAs(): error writing file" + dir + fil + ext
                    self.msgbarLabel.setText( "Problem saving file: " + dir + fil + ext )
                else:
                    self.assy.modified = 0 # The file and the part are now the same.
                    self.setCaption(self.trUtf8("Atom - " + "[" + self.assy.filename + "]"))
                    self.msgbarLabel.setText( "MMP file saved: " + self.assy.filename )
                    self.assy.modified = 0 # The file and the part are now the same.
                    self.assy.name = fil
                    self.mt.update()
            
            else: # This should never happen.
                self.msgbarLabel.setText( "MWSemantics.py: fileSaveAs() - File Not Saved.")

    def fileExit(self):
        if self.assy.modified:
            ret = QMessageBox.information( self, "Atom",
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before exiting?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
            elif ret==2: return # Cancel clicked or Alt+C pressed or Escape pressed
#        pass

    def fileClear(self):
        self.__clear()
        self.modelTreeView.update()
        self.update()

    def fileClose(self):
        if self.assy.modified:
            ret = QMessageBox.information( self, "Atom",
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before closing this part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
            elif ret==2: return # Cancel clicked or Alt+C pressed or Escape pressed

        self.__clear()
        self.update()

    def fileSetWorkDir(self):
        """ Sets working directory (need dialogue window) """
        # Windows Users: .atomrc must be placed in C:\Documents and Settings\[username]\.atomrc
        # .atomrc contains one line, the Working Directory
        # Example: C:\Documents and Settings\Mark\My Documents\MMP Parts
        # Mark [2004-10-13]
        wd = globalParms['WorkingDirectory']
        wd = QFileDialog.getExistingDirectory( wd, self, "get existing directory", "Choose Working Directory", 1 )
        
        if wd:
            wd = str(wd) + "/" # the additional slash needed by Windows
            globalParms['WorkingDirectory'] = wd
            self.msgbarLabel.setText( "Working Directory set to " + wd )
            
            # Write ~/.atomrc file with new Working Directory
            rc = os.path.expanduser("~/.atomrc")
            try:
                f=open(rc,'w')
            except:
                print "Trouble opening file: [", f, "]"
            else:
                f.write(wd)
                f.close()
        	    
    def __clear(self):
        # assyList refs deleted by josh 10/4
        self.assy = assembly(self, "Empty")
        self.setCaption(self.trUtf8("Atom - " + "[" + self.assy.name + "]"))
        self.msgbarLabel.setText( " " )
        self.glpane.setAssy(self.assy)
        self.assy.mt = self.mt


    ###################################
    # functions from the "Edit" menu
    ###################################

    def editUndo(self):
        print "MWsemantics.editUndo(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    def editRedo(self):
        print "MWsemantics.editRedo(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    def editCut(self):
        self.assy.cut()
        self.update()

    def editCopy(self):
        print 'got editCopy'
        self.assy.copy()
        self.update()

    def editPaste(self):
        self.pasteP = True
        self.glpane.setMode('DEPOSIT')

    def editFind(self):
        print "MWsemantics.editFind(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    ###################################
    # functions from the "View" menu
    ###################################

    # GLPane.ortho is checked in GLPane.paintGL
    def setViewOrtho(self):
        self.glpane.ortho = 1
        self.glpane.paintGL()

    def setViewPerspec(self):
        self.glpane.ortho = 0
        self.glpane.paintGL()

    def setViewBack(self):
        self.glpane.quat = Q(V(0,1,0),pi)
        self.glpane.paintGL()

    def setViewBottom(self):
        self.glpane.quat = Q(V(1,0,0),-pi/2)
        self.glpane.paintGL()

    def setViewFront(self):
        self.glpane.quat = Q(1,0,0,0)
        self.glpane.paintGL()

    def setViewHome(self):
        self.glpane.quat = self.assy.csys.quat#Q(1,0,0,0)
        self.glpane.paintGL()

    def setViewLeft(self):
        self.glpane.quat = Q(V(0,1,0),pi/2)
        self.glpane.paintGL()

    def setViewRight(self):
        self.glpane.quat = Q(V(0,1,0),-pi/2)
        self.glpane.paintGL()

    def setViewTop(self):
        self.glpane.quat = Q(V(1,0,0),pi/2)
        self.glpane.paintGL()

    # set display formats in whatever is selected,
    # or the GLPane global default if nothing is
    def dispDefault(self):
        self.setDisplay(diDEFAULT)

    def dispInvis(self):
        self.setDisplay(diINVISIBLE)

    def dispVdW(self):
        self.setDisplay(diVDW)

    def dispTubes(self):
        self.setDisplay(diTUBES)

    def dispCPK(self):
        self.setDisplay(diCPK)

    def dispLines(self):
        self.setDisplay(diLINES)

    def setDisplay(self, form):
        if self.assy and self.assy.selatoms:
            for ob in self.assy.selatoms.itervalues():
                ob.setDisplay(form)
        elif self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.setDisplay(form)
        else:
            if self.glpane.display == form: return
            self.glpane.setDisplay(form)
        self.glpane.paintGL()

    def setdisplay(self, a0):
        print 'setdisplay', a0


    # set the color of the selected molecule
    # atom colors cannot be changed singly
    def dispObjectColor(self):
        c = QColorDialog.getColor(QColor(100,100,100), self, "choose")
        if c.isValid():
            molcolor = c.red()/255.0, c.green()/255.0, c.blue()/255.0
            for ob in self.assy.selmols:
                ob.setcolor(molcolor)
            self.glpane.paintGL()

    # Reset the color of the selected molecule back to element colors
    def dispResetMolColor(self):
#        molcolor = c.red()/255.0, c.green()/255.0, c.blue()/255.0
        for ob in self.assy.selmols:
            ob.setcolor(None)
        self.glpane.paintGL()
            
    def dispBGColor(self):
        
        # get r, g, b values of current background color
        r = int (self.glpane.mode.backgroundColor[0] * 255)
        g = int (self.glpane.mode.backgroundColor[1] * 255)
        b = int (self.glpane.mode.backgroundColor[2] * 255) 

        # allow user to select a new background color and set it.
        c = QColorDialog.getColor(QColor(r, g, b), self, "choose")
        if c.isValid():
            self.glpane.mode.backgroundColor = c.red()/255.0, c.green()/255.0, c.blue()/255.0
            self.glpane.paintGL()

    def dispGrid(self):
        print "MWsemantics.dispGrid(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")
        

    def gridGraphite(self):
        print "MWsemantics.gridGraphite(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    #######################################
    # functions from the "Orientation" menu
    #######################################

    # points of view corresponding to the three crystal
    # surfaces of diamond

    # along one axis
    def orient100(self):
        self.glpane.snapquat100()

    # halfway between two axes
    def orient110(self):
        self.glpane.snapquat110()

    # equidistant from three axes
    def orient111(self):
        self.glpane.snapquat111()

    # lots of things ???
    def orientView(self, a0=None):
        print "MainWindow.orientView(string):", a0
        self.glpane.quat = Q(1,0,0,0)
        self.glpane.pov = V(0,0,0)
        self.glpane.paintGL()

    ###############################################################
    # functions from the "Select" menu
    ###############################################################

    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        """
        self.assy.selectAll()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectNone(self):
        self.assy.selectNone()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectInvert(self):
        """If some parts are selected, select the other parts instead.
        If some atoms are selected, select all currently unselected
        atoms in parts in which there are currently some selected atoms.
        (And unselect all currently selected atoms.)
        """
        self.assy.selectInvert()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """
        self.assy.selectConnected()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed


    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """
        self.assy.selectDoubly()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    ###################################
    # Functions from the "Make" menu
    ###################################

    # these functions (do or will) create small structures that
    # describe records to send to the simulator
    # they don't do much in Atom itself
    def makeGround(self):
        self.assy.makeground()
        self.update()
        
    def makeStat(self):
        self.assy.makestat()
        self.update()

    def makeHandle(self):
        print "MWsemantics.makeHandle(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    def makeMotor(self):
        self.assy.makeRotaryMotor(self.glpane.lineOfSight)
        self.update()

    def makeLinearMotor(self):
        self.assy.makeLinearMotor(self.glpane.lineOfSight)
        self.update()

    def makeBearing(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def makeSpring(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
    def makeDyno(self):
        print "MWsemantics.makeDyno(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    def makeHeatsink(self):
        print "MWsemantics.makeHeatsink(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    ###################################
    # functions from the "Modify" menu
    ###################################

    # change surface atom types to eliminate dangling bonds
    # a kludgey hack
    def modifyPassivate(self):
        self.assy.modifyPassivate()

    # add hydrogen atoms to each dangling bond
    def modifyHydrogenate(self):
        self.assy.modifyHydrogenate()
        
    # remove hydrogen atoms from selected atoms/molecules
    def modifyDehydrogenate(self):
        self.assy.modifyDehydrogenate()

    # form a new part (molecule) with whatever atoms are selected
    def modifySeparate(self):
        self.assy.modifySeparate()
    
    # stretch selected molecule(s)    
    def modifyStretchMolecule(self):
        self.assy.Stretch()

    ###################################
    # Functions from the "Help" menu
    ###################################

    def helpContents(self):
        global helpwindow
        if not helpwindow: helpwindow = help.Help()
        helpwindow.show()

    def helpIndex(self):
        print "MWsemantics.helpIndex(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")
    def helpAbout(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")


    ######################################################
    # functions for toggling (hiding/unhiding) toolbars  #
    ######################################################

    def toggleFileTbar(self):
        if self.fileToolbar.isVisible():
            self.fileToolbar.hide()
        else:
            self.fileToolbar.show()

    def toggleEditTbar(self):
        if self.editToolbar.isVisible():
            self.editToolbar.hide()
        else:
            self.editToolbar.show()

    def toggleViewTbar(self):
        if self.viewToolbar.isVisible():
            self.viewToolbar.hide()
        else:
            self.viewToolbar.show()

    def toggleGridTbar(self):
        if self.gridToolbar.isVisible():
            self.gridToolbar.hide()
        else:
            self.gridToolbar.show()

    def toggleModelDispTbar(self):
        if self.modelDispToolbar.isVisible():
            self.modelDispToolbar.hide()
        else:
            self.modelDispToolbar.show()

    def toggleSelectTbar(self):
        if self.selectToolbar.isVisible():
            self.selectToolbar.hide()
        else:
            self.selectToolbar.show()

    def toggleModifyTbar(self):
        if self.modifyToolbar.isVisible():
            self.modifyToolbar.hide()
        else:
            self.modifyToolbar.show()

    def toggleToolsTbar(self):
        if self.toolsToolbar.isVisible():
            self.toolsToolbar.hide()
        else:
            self.toolsToolbar.show()

    def toggleDatumDispTbar(self):
        if self.datumDispToolbar.isVisible():
            self.datumDispToolbar.hide()
        else:
            self.datumDispToolbar.show()

    def toggleSketchAtomTbar(self):
        if self.sketchAtomToolbar.isVisible():
            self.sketchAtomToolbar.hide()
        else:
            self.sketchAtomToolbar.show()

    ###############################################################
    # functions from the buttons down the right side of the display
    ###############################################################

    def toolsSelectAtoms(self):
        self.glpane.setMode('SELECTATOMS')

    def toolsSelectMolecules(self):
        self.glpane.setMode('SELECTMOLS')

    def toolsSelectJigs(self):
        print "MWsemantics.toolsSelectJigs(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:", 
             "This function is not implemented yet, coming soon...")
        
    def toolsMoveMolecule(self):
        self.glpane.setMode('MODIFY')
            
    # get into cookiecutter mode
    def toolsCookieCut(self):
        self.glpane.setMode('COOKIE')

    # get into Extrude mode
    def toolsExtrude(self):
        self.glpane.setMode('EXTRUDE')

    # get into Revolve mode [bruce 041015]
    def toolsRevolve(self):
        self.glpane.setMode('REVOLVE')

    # Mirror Tool
    def toolsMirror(self):
        print "MWsemantics.toolsMirror(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:", 
             "This function is not implemented yet, coming soon...")
             
    # Mirror Circular Boundary Tool
    def toolsMirrorCircularBoundary(self):
        print "MWsemantics.toolsMirrorCircularBoundary(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:", 
             "This function is not implemented yet, coming soon...")

    # "push down" one nanometer to cut out the next layer
    def toolsCCAddLayer(self):
        if self.glpane.shape:
            self.glpane.pov -= self.glpane.shape.pushdown()
            self.glpane.paintGL()

    # fill the shape created in the cookiecutter with actual
    # carbon atoms in a diamond lattice (including bonds)
    # this works for all modes, not just add atom
    def toolsDone(self):
        self.glpane.mode.Done()

    def toolsStartOver(self):
        self.glpane.mode.Restart()

    def toolsBackUp(self):
        self.glpane.mode.Backup()

    def toolsCancel(self):
        self.glpane.mode.Flush()

    # turn on and off an "add atom with a mouse click" mode
    
    # [bruce 040927 wonders why there is code for two separate buttons
    # for this...]
    def addAtomStart(self):
        ##self.modebarLabel.setText( "Mode: Sketch Atoms" )
        # bruce 040927 let mode control this
        self.pasteP = False
        self.glpane.setMode('DEPOSIT')

    def toolsAtomStart(self):
        ##self.modebarLabel.setText( "Mode: Sketch Atoms" )
        self.pasteP = False
        self.glpane.setMode('DEPOSIT')

    # pop up set element box
    def modifySetElement(self):
        print self.Element    
        global elementwindow
        if not elementwindow:
            elementwindow = elementSelector(self)
        elementwindow.setDisplay(self.Element)
        elementwindow.show()

    def elemChange(self, a0):
        self.Element = eCCBtab1[a0]
        global elementwindow
        if elementwindow and not elementwindow.isHidden():
           elementwindow.setDisplay(self.Element)     
           elementwindow.show()
          
         
    # this routine sets the displays to reflect elt
    def setElement(self, elt):
        # element specified as element number
        global elementwindow
        self.Element = elt
        if elementwindow: elementwindow.setDisplay(elt)
        line = eCCBtab2[elt]
        self.elemChangeComboBox.setCurrentItem(line)

    def setCarbon(self):
        self.setElement(6)

    def setHydrogen(self):
        self.setElement(1)
    
    def setOxygen(self):
        self.setElement(8)

    def setNitrogen(self):
        self.setElement(7)

    # Play a movie from the simulator
    def toolsMovie(self):
        dir, fil, ext = fileparse(self.assy.filename)
        self.glpane.startmovie(dir + fil + ".dpb")

    
    ###################################
    # some unimplemented buttons:
    ###################################

    # bring molecules together and bond unbonded sites
    def modifyWeldMolecule(self):
        print "MWsemantics.modifyWeldMolecule(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    def toolsAlignToCommonAxis(self):
        print "MWsemantics.modifyAlignToCommonAxis(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:", 
             "This function is not implemented yet, coming soon...")        
    
    # create bonds where reasonable between selected and unselected
    def modifyEdgeBond(self):
        print "MWsemantics.modifyEdgeBond(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")
        
    # create bonds where reasonable between selected and unselected
    def toolsAddBond(self):
        print "MWsemantics.modifyAddBond(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    # Turn on or off the axis icon
    def dispTrihedron(self):
        self.glpane.drawAxisIcon = not self.glpane.drawAxisIcon
        self.glpane.paintGL()

    def dispCsys(self):
        """ Toggle on/off center coordinate axes """
        self.glpane.cSysToggleButton = not self.glpane.cSysToggleButton
        self.glpane.paintGL()

    # break bonds between selected and unselected atoms
    def toolsDeleteBond(self):
        print "MWsemantics.modifyDeleteBond(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    # 2BDone: make a copy of the selected part, move it, and bondEdge it,
    # having unselected the original and selected the copy.
    # the motion is to be the same relative motion done to a part
    # between copying and bondEdging it.
    def modifyCopyBond(self):
        print "MWsemantics.modifyCopyBond(): Not implemented yet"
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    # delete selected parts or atoms
    def killDo(self):
        self.assy.kill()
        self.glpane.paintGL()
        self.mt.update()

    # utility functions

    def colorchoose(self, r, g, b): # r, g, b is the default color displayed in the QColorDialog window.
        color = QColorDialog.getColor(QColor(r, g, b), self, "choose")
        if color.isValid():
            return color.red()/256.0, color.green()/256.0, color.blue()/256.0
        else:
            return r/256.0, g/256.0, b/256.0


    def keyPressEvent(self, e):
        self.glpane.mode.keyPress(e.key())
        
    def keyReleaseEvent(self, e):
        self.glpane.mode.keyRelease(e.key())

    ##############################################################
    # Some future slot functions for the UI                      #
    ##############################################################

    def dispDatumLines(self):
        """ Toggle on/off datum lines """
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    def dispDatumPlanes(self):
        """ Toggle on/off datum planes """
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    def dispOpenBonds(self):
        """ Toggle on/off open bonds """
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")

    def editPrefs(self):
        """ Edit square grid line distances(dx, dy, dz) in nm/angtroms """
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")
 
    def elemChangePTable(self):
        """ Future: element change via periodic table
        (only elements we support) """

    def modifyMinimize(self):
        """ Minimize the current assembly """
        self.glpane.minimize()

    def toolsSimulator(self):
        self.simCntl = runSim(self.assy)
        self.simCntl.show()

    def setViewFitToWindow(self):
        """ Fit to Window """
        self.glpane.scale=self.assy.bbox.scale()
        #print "scale: ", self.glpane.scale
        #print "pov, center: ", self.glpane.pov, self.assy.center
        self.glpane.pov = -self.assy.center#-planeXline(-self.glpane.pov, self.glpane.out, self.assy.center, self.glpane.out)
        #print "Again: pov, center: ", self.glpane.pov, self.assy.center
        self.glpane.paintGL()
        
    def setViewRecenter(self):
        """ Fit to Window """
        QMessageBox.warning(self, "ATOM User Notice:",
	         "This function is not implemented yet, coming soon...")
	         
#######  Load Cursors #########################################
    def loadCursors(self):

        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))

        # Create "SelectAtomsCursor" cursor
        self.SelectAtomsCursor = QCursor(
            QBitmap(filePath + "/../images/SelectAtomsCursor.bmp"),
            QBitmap(filePath + "/../images/SelectAtomsCursor-bm.bmp"),
            0, 0)

        # Create "SelectAtomsAddCursor" cursor
        self.SelectAtomsAddCursor = QCursor(
            QBitmap(filePath + "/../images/SelectAtomsAddCursor.bmp"),
            QBitmap(filePath + "/../images/SelectAtomsAddCursor-bm.bmp"),
            0, 0)

        # Create "SelectAtomsSubtractCursor" cursor
        self.SelectAtomsSubtractCursor = QCursor(
            QBitmap(filePath + "/../images/SelectAtomsSubtractCursor.bmp"),
            QBitmap(filePath + "/../images/SelectAtomsSubtractCursor-bm.bmp"),
            0, 0)
                                        
        # Create "SelectMolsCursor" cursor
        self.SelectMolsCursor = QCursor(
            QBitmap(filePath + "/../images/SelectMolsCursor.bmp"),
            QBitmap(filePath + "/../images/SelectMolsCursor-bm.bmp"),
            0, 0)

        # Create "SelectMolsAddCursor" cursor
        self.SelectMolsAddCursor = QCursor(
            QBitmap(filePath + "/../images/SelectMolsAddCursor.bmp"),
            QBitmap(filePath + "/../images/SelectMolsAddCursor-bm.bmp"),
            0, 0)
        
        # Create "SelectMolsSubtractCursor" cursor
        self.SelectMolsSubtractCursor = QCursor(
            QBitmap(filePath + "/../images/SelectMolsSubtractCursor.bmp"),
            QBitmap(filePath + "/../images/SelectMolsSubtractCursor-bm.bmp"),
            0, 0)
        
        # Create "CookieCursor" cursor
        self.CookieCursor = QCursor(
            QBitmap(filePath + "/../images/CookieCursor.bmp"),
            QBitmap(filePath + "/../images/CookieCursor-bm.bmp"),
            -1, -1)
                    
        # Create "CookieAddCursor" cursor
        self.CookieAddCursor = QCursor(
            QBitmap(filePath + "/../images/CookieAddCursor.bmp"),
            QBitmap(filePath + "/../images/CookieAddCursor-bm.bmp"),
            -1, -1)

        # Create "CookieSubtractCursor" cursor
        self.CookieSubtractCursor = QCursor(
            QBitmap(filePath + "/../images/CookieSubtractCursor.bmp"),
            QBitmap(filePath + "/../images/CookieSubtractCursor-bm.bmp"),
            -1, -1)
            
        # Create "RotateCursor" cursor
        self.RotateCursor = QCursor(
            QBitmap(filePath + "/../images/RotateCursor.bmp"),
            QBitmap(filePath + "/../images/RotateCursor-bm.bmp"),
            0, 0)
            
        # Create "RotateZCursor" cursor
        self.RotateZCursor = QCursor(
            QBitmap(filePath + "/../images/RotateZCursor.bmp"),
            QBitmap(filePath + "/../images/RotateZCursor-bm.bmp"),
            0, 0)
            
        # Create "MoveCursor" cursor
        self.MoveCursor = QCursor(
            QBitmap(filePath + "/../images/MoveCursor.bmp"),
            QBitmap(filePath + "/../images/MoveCursor-bm.bmp"),
            0, 0)
            
        # Create "MoveSelectCursor" cursor
        self.MoveSelectCursor = QCursor(
            QBitmap(filePath + "/../images/MoveSelectCursor.bmp"),
            QBitmap(filePath + "/../images/MoveSelectCursor-bm.bmp"),
            -1, -1)

        # Create "MoveAddCursor" cursor
        self.MoveAddCursor = QCursor(
            QBitmap(filePath + "/../images/MoveAddCursor.bmp"),
            QBitmap(filePath + "/../images/MoveAddCursor-bm.bmp"),
            -1, -1)
            
        # Create "MoveSubtractCursor" cursor
        self.MoveSubtractCursor = QCursor(
            QBitmap(filePath + "/../images/MoveSubtractCursor.bmp"),
            QBitmap(filePath + "/../images/MoveSubtractCursor-bm.bmp"),
            -1, -1)
                                    
        # Create "MoveRotateMolCursor" cursor
        self.MoveRotateMolCursor = QCursor(
            QBitmap(filePath + "/../images/MoveRotateMolCursor.bmp"),
            QBitmap(filePath + "/../images/MoveRotateMolCursor-bm.bmp"),
            -1, -1)
                                    
        # Create "RotateMolCursor" cursor
        self.RotateMolCursor = QCursor(
            QBitmap(filePath + "/../images/RotateMolCursor.bmp"),
            QBitmap(filePath + "/../images/RotateMolCursor-bm.bmp"),
            -1, -1)
                        
        # Create "DepositAtomCursor" cursor
        self.DepositAtomCursor = QCursor(
            QBitmap(filePath + "/../images/DepositAtomCursor.bmp"),
            QBitmap(filePath + "/../images/DepositAtomCursor-bm.bmp"),
            0, 32)
                        
        # Create "KillCursor" cursor
        self.KillCursor = QCursor(
            QBitmap(filePath + "/../images/KillCursor.bmp"),
            QBitmap(filePath + "/../images/KillCursor-bm.bmp"),
            0, 0)
            
        # Create "ZoomCursor" cursor
        self.ZoomCursor = QCursor(
            QBitmap(filePath + "/../images/ZoomCursor.bmp"),
            QBitmap(filePath + "/../images/ZoomCursor-bm.bmp"),
            10, 10)
                
            
    def createStatusBars(self):
        # Mark - Set up primary (left) message bar in status bar area.
        self.msgbarLabel = QLabel(self, "msgbarLabel")
        self.msgbarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        self.msgbarLabel.setText( " " )
        
        self.statusBar().addWidget(self.msgbarLabel,1,1)

        # Mark - Set up mode bar (right) in status bar area.        
        self.modebarLabel = QLabel(self, "modebarLabel")
        self.modebarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        
        self.statusBar().addWidget(self.modebarLabel,0,1)
        #self.update_mode_status() # bruce 040927            
        
    def hideDashboards(self):
        self.cookieCutterDashboard.hide()
        self.extrudeDashboard.hide()
        self.revolveDashboard.hide()
        self.depositAtomDashboard.hide()
        self.datumDispDashboard.hide()  # (mark note: this is the datum display toolbar)
        self.selectMolDashboard.hide()
        self.selectAtomsDashboard.hide()
        self.moveMolDashboard.hide()        