# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
MWsemantics.py provides the main window class, MWsemantics.

$Id$
'''

import qt
from qt import QMainWindow, QPixmap, QWidget, QFrame, QPushButton
from qt import QGroupBox, QComboBox, QAction, QMenuBar, QPopupMenu
from qt import SIGNAL, SLOT, QListView, QListViewItem, QFileDialog
from GLPane import *
import os
import help
from math import ceil
from runSim import runSim
from modelTree import *
import platform

from constants import *
from elementSelector import *
from fileIO import *
from debug import print_compact_traceback

from MainWindowUI import MainWindow

from assistant import AssistantWindow

from AboutDialog import AboutDialog

helpwindow = None
elementwindow = None
windowList = []

eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]

eCCBtab2 = {}
for i,elno in zip(range(len(eCCBtab1)), eCCBtab1):
    eCCBtab2[elno] = i

def greenmsg(text):
    """Display text in green in the HistoryWidget"""
    return "<span style=\"color:#006600\">" + text + "</span>"
    
def redmsg(text):
    """Display text in red in the HistoryWidget"""
    return "<span style=\"color:#ff0000\">" + text + "</span>"
    
def fileparse(name):
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))

class MWsemantics(MainWindow):
    
    initialised = 0 #bruce 041222
    
    def __init__(self, parent = None, name = None):
    
        global windowList

        MainWindow.__init__(self, parent, name, Qt.WDestructiveClose)
        
        # bruce 050104 moved this here so it can be used earlier
        # (it might need to be moved into atom.py at some point)
        self.tmpFilePath = platform.find_or_make_Nanorex_prefs_directory()

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
        # (see also self.set_status_text())
        self.createStatusBars()
        
        # Create Assistant - Mark 11-23-2004
        self.assistant = AssistantWindow(self, "Assistant")
        
        # Create validator(s)
        maxd = self.ccLayerThicknessSpinBox.maxValue() * 3.5103 # Maximum value allowed
        self.vd = QDoubleValidator( 0.0, maxd , 4, self ) # 4 decimal places
        self.ccLayerThicknessLineEdit.setValidator (self.vd)
        
        windowList += [self]
        if name == None:
            self.setName("nanoENGINEER-1") # Mark 11-05-2004
#            self.setName("Atom") 

        # start with empty window 
        self.assy = assembly(self, "Untitled")
        
        # Set the caption to the name of the current (default) part - Mark [2004-10-11]
        self.setCaption(self.trUtf8( self.name() +  " - " + "[" + self.assy.name + "]"))

        # Create the vertical-splitter between history area (at bottom)
        # and main area (mtree and glpane) [history is new as of 041223]
        vsplitter = QSplitter(Qt.Vertical, self, "vContentsWindow")
        
        # Create the splitter between glpane and the model tree
        splitter = QSplitter(Qt.Horizontal, vsplitter, "ContentsWindow")
        
        # Create the model tree widget
        self.mt = self.modelTreeView = modelTree(splitter, self)
        self.modelTreeView.setMinimumSize(0, 0)
        
        # Create the glpane - where all the action is!
        self.glpane = GLPane(self.assy, splitter, "glpane", self)

        # Some final splitter setup
        splitter.setResizeMode(self.modelTreeView, QSplitter.KeepSize)
        splitter.setOpaqueResize(False)

        # Create the history area at the bottom
        from HistoryWidget import HistoryWidget
        histfile = platform.make_history_filename()
        self.history = HistoryWidget(vsplitter, filename = histfile, mkdirs = 1)
            # this is not a Qt widget, but its owner;
            # use self.history.widget for Qt calls that need the widget itself
        
        # ... and some final vsplitter setup [bruce 041223]
        vsplitter.setResizeMode(self.history.widget, QSplitter.KeepSize)
        vsplitter.setOpaqueResize(False)
        self.setCentralWidget(vsplitter) # this was required (what exactly does it do?)

        # Create a progress bar widget for use during time consuming operations,
        # such as minimize, simulator and select doubly.  Mark 050101
        from ProgressBar import ProgressBar
        self.progressbar = ProgressBar()

        # do here to avoid a circular dependency
        self.assy.o = self.glpane
        self.assy.mt = self.mt

        # We must enable keyboard focus for a widget if it processes
        # keyboard events. [Note added by bruce 041223: I don't know if this is
        # needed for this window; it's needed for some subwidgets, incl. glpane,
        # and done in their own code. This window forwards its own key events to
        # the glpane. This doesn't prevent other subwidgets from having focus.]
        self.setFocusPolicy(QWidget.StrongFocus)
        
        # Create the "What's This?" online help system.
        self.createWhatsThis()

        # Start with Carbon as the default element (for Deposit Mode
        # and the Element Selector)
        self.Element = 6
        self.setElement(6)
        # and paste the atom rather than the clipboard by default
        self.pasteP = False
        
        # Huaicai 12/14/04, the following property should be really a property of Csys, which
        # stores the center view point of the current home view. This needs to change when
        # we update the mmp file format
        self.currentPov = V(0.0, 0.0, 0.0)
        
        # bruce 050104 moved find_or_make_Nanorex_prefs_directory to an earlier time
        
        self.initialised = 1
        self.win_update() # bruce 041222
        
        return # from MWsemantics.__init__

    def set_status_text(self, text, **options):
        try:
            self.history
        except AttributeError:
            if platform.atom_debug:
                print "fyi: too early for this status msg:", text
            pass # too early
        else:
            self.history.set_status_text( text, **options)
        return

    #def resizeEvent(self, event):
     #   print "why I am changing size? ", event
     #   QMainWindow.resizeEvent(self, event)            

    def update_mode_status(self, mode_obj = None):
        """[by bruce 040927]
        
        Update the text shown in self.modebarLabel (if that widget
        exists yet).  Get the text to use from mode_obj if supplied,
        otherwise from the current mode object
        (self.glpane.mode). (The mode object has to be supplied when
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

    def win_update(self): # bruce 050107 renamed this from 'update'
        """ Update most state which directly affects the GUI display,
        in some cases repainting it directly.
        (Someday this should update all of it, but only what's needed,
        and perhaps also call QWidget.update. #e)
        [no longer named update, since that conflicts with QWidget.update]
        """
        if not self.initialised:
            return #bruce 041222
        self.glpane.paintGL() ###e should inval instead
        self.mt.mt_update()
        self.history.h_update() #bruce 050104
        

    ###################################
    # File Toolbar Slots
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
                try:
                    insertmmp(self.assy, fn)
                except:
                    print "MWsemantics.py: fileInsert(): error inserting file" + fn
                    self.statusBar.message( "Problem inserting MMP file: " + fn )
                else:
                    self.assy.modified = 1 # The file and the part are not the same.
                    self.statusBar.message( "MMP file inserted: " + fn )
            
            if fn[-3:] in ["pdb","PDB"]:
                try:
                    insertpdb(self.assy, fn)
                except:
                    print "MWsemantics.py: fileInsert(): error inserting PDB file" + fn
                    self.statusBar.message( "Problem inserting file: " + fn )
                else:
                    self.assy.modified = 1 # The file and the part are not the same.
                    self.statusBar.message( "PDB file inserted: " + fn )
            
            self.glpane.scale=self.assy.bbox.scale()
            self.glpane.paintGL()
            self.mt.mt_update()

    def fileOpen(self):
        if self.assy.modified:
            ret = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before opening a new part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: # Save clicked or Alt+S pressed or Enter pressed.
                ##Huaicai 1/6/05: If user canceled save operation, return 
                ## without letting user open another file
                if not self.fileSave(): return
                
            ## Huaicai 12/06/04. Don't clear it, user may cancel the file open action    
            elif ret==1: pass#self.__clear() 
            
            elif ret==2: return # Cancel clicked or Alt+C pressed or Escape pressed

        # Determine what directory to open.
        if self.assy.filename: odir, fil, ext = fileparse(self.assy.filename)
        else: odir = globalParms['WorkingDirectory']

        fn = QFileDialog.getOpenFileName(odir,
                "All Files (*.mmp *.pdb);;Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb)",
                self )

        if fn:
            # I know we are clearing twice if the file was saved above.
            # This is desidered behavior - Mark [2004-10-11]
            self.__clear()  
                
            fn = str(fn)
            if not os.path.exists(fn): return

            if fn[-3:] == "mmp":
                readmmp(self.assy,fn)
                
            if fn[-3:] in ["pdb","PDB"]:
                readpdb(self.assy,fn)

            dir, fil, ext = fileparse(fn)
            self.assy.name = fil
            self.assy.filename = fn
            self.assy.modified = 0 # The file and the part are now the same

            self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))

            # Huaicai 12/14/04, set the initial orientation to the file's home view orientation 
            # when open a file; set the home view scale = current fit-in-view scale  
            self.glpane.quat = Q( self.assy.csys.quat)
            self.setViewFitToWindow()
            self.currentPov = V(self.glpane.pov[0], self.glpane.pov[1], self.glpane.pov[2])
            self.assy.csys.scale = self.glpane.scale
            self.mt.mt_update()

    def fileSave(self):
        #Huaicai 1/6/05: by returning a boolean value to say if it is really 
        # saved or not, user may choose "Cancel" in the "File Save" dialog          
        if self.assy:
            if self.assy.filename: 
                self.saveFile(self.assy.filename)
                return True
            else: 
                return self.fileSaveAs()


    def fileSaveAs(self):
        if self.assy:
            if self.assy.filename:
                dir, fil, ext = fileparse(self.assy.filename)
                sdir = self.assy.filename
            else: 
                dir, fil = "./", self.assy.name
                ext = ".mmp"
                sdir = globalParms['WorkingDirectory']
        else:
            self.statusBar.message( "Save Ignored: Part is currently empty." )
            return False

        if ext == ".pdb": sfilter = QString("Protein Data Bank (*.pdb)")
        else: sfilter = QString("Molecular machine parts (*.mmp)")
        
        fn = QFileDialog.getSaveFileName(sdir,
                    "Molecular Machine Part (*.mmp);;Protein Data Bank (*.pdb);;POV-Ray (*.pov);;Model MDL (*.mdl);;JPEG (*.jpg)",
                    self, "IDONTKNOWWHATTHISIS",
                    "Save As",
                    sfilter)
        
        if fn:
            fn = str(fn)
            dir, fil, ext2 = fileparse(fn)
            ext =str(sfilter[-5:-1]) # Get "ext" from the sfilter. It *can* be different from "ext2"!!! - Mark
            safile = dir + fil + ext # full path of "Save As" filename
            
            if self.assy.filename != safile: # If the current part name and "Save As" filename are not the same...
                if os.path.exists(safile): # ...and if the "Save As" file exists...

                    # ... confirm overwrite of the existing file.
                    ret = QMessageBox.warning( self, self.name(),
                        "The file \"" + fil + ext + "\" already exists.\n"\
                        "Do you want to overwrite the existing file or cancel?",
                        "&Overwrite", "&Cancel", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                    if ret==1: # The user cancelled
                        self.statusBar.message( "Cancelled.  Part not saved." )
                        return False # Cancel clicked or Alt+C pressed or Escape pressed
            
            self.saveFile(safile)
            return True
            
        else: return False ## User canceled.
            

    def saveFile(self, safile):
        
            dir, fil, ext = fileparse(safile)
#            print "saveFile: ext = [",ext,"]"

            if ext == ".pdb": # Write PDB file.
                try:
                    writepdb(self.assy, safile)
                except:
                    print "MWsemantics.py: saveFile(): error writing file" + safile
                    self.statusBar.message( "Problem saving file: " + safile )
                else:
                    self.assy.filename = safile
                    self.assy.name = fil
                    self.assy.modified = 0 # The file and the part are now the same.
                    self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
                    self.statusBar.message( "PDB file saved: " + self.assy.filename )
                    self.mt.mt_update()
            
            elif ext == ".pov": # Write POV-Ray file
                try:
                    writepov(self.assy, safile)
                except:
                    print "MWsemantics.py: fileSaveAs(): error writing file " + safile
                    self.statusBar.message( "Problem saving file: " + safile )
                else:
                    self.statusBar.message( "POV-Ray file saved: " + safile )
            
            elif ext == ".mdl": # Write MDL file
                try:
                    writemdl(self.assy, safile)
                except:
                    print "MWsemantics.py: fileSaveAs(): error writing file " + safile
                    self.statusBar.message( "Problem saving file: " + safile )
                else:
                    self.statusBar.message( "MDL file saved: " + safile )
            
            elif ext == ".jpg": # Write JPEG file
                try:
                    self.glpane.image(safile)
                except:
                    print "MWsemantics.py: fileSaveAs(): error writing file" + safile
                    self.statusBar.message( "Problem saving file: " + safile )
                else:
                    self.statusBar.message( "JPEG file saved: " + safile )

            elif ext == ".mmp" : # Write MMP file
                try:
                    writemmp(self.assy, safile)
                except:
                    print "MWsemantics.py: fileSaveAs(): error writing file" + safile
                    self.statusBar.message( "Problem saving file: " + safile )
                else:
                    self.assy.filename = safile
                    self.assy.name = fil
                    self.assy.modified = 0 # The file and the part are now the same.
                    self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
                    self.statusBar.message( "MMP file saved: " + self.assy.filename )
                    self.mt.mt_update()
            
            else: # This should never happen.
                self.statusBar.message( "MWSemantics.py: fileSaveAs() - File Not Saved.")

    def closeEvent(self,ce): # via File > Exit or clicking X titlebar button
        
        if not self.assy.modified:
            ce.accept()
            return
            
        rc = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before exiting?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2

        if rc == 0:
            isFileSaved = self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
            ##Huaicai 1/6/05: While in the "Save File" dialog, if user chooses ## "Cancel", the "Exit" action should be ignored. bug 300
            if isFileSaved:
                ce.accept()
            else:
                ce.ignore()
        elif rc == 1:
            ce.accept()
        else:
            ce.ignore()

    def fileClose(self):
        isFileSaved = True
        if self.assy.modified:
            ret = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before closing this part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: isFileSaved = self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
            elif ret==2: return # Cancel clicked or Alt+C pressed or Escape pressed
        
        if isFileSaved: 
                self.__clear()
                self.win_update()


    def fileSetWorkDir(self):
        """ Sets working directory (need dialogue window) """
        # Windows Users: .ne1rc must be placed in C:\Documents and Settings\[username]\.ne1rc
        # .ne1rc contains one line - the "Working Directory"
        # Example: C:\Documents and Settings\Mark\My Documents\MMP Parts
        # Mark [2004-10-13]
        wd = globalParms['WorkingDirectory']
        wdstr = "Current Working Directory - [" + wd  + "]"
        wd = QFileDialog.getExistingDirectory( wd, self, "get existing directory", wdstr, 1 )
        
        if wd:
            wd = str(wd)
            wd = os.path.normpath(wd)
            globalParms['WorkingDirectory'] = wd
            self.statusBar.message( "Working Directory set to " + wd )
            
            # Write ~/.ne1rc file with new Working Directory
            rc = os.path.expanduser("~/.ne1rc")
            try:
                f=open(rc,'w')
            except:
                print "Trouble opening file: [", f, "]"
            else:
                f.write(wd)
                f.close()
                
    def __clear(self):
        # assyList refs deleted by josh 10/4
        self.assy = assembly(self, "Untitled")
        self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.name + "]"))
        self.glpane.setAssy(self.assy)
        self.assy.mt = self.mt


    ###################################
    # Edit Toolbar Slots
    ###################################

    def editUndo(self):
        self.statusBar.message("<span style=\"color:#ff0000\">Undo: Not implemented yet.</span>")

    def editRedo(self):
        self.statusBar.message("<span style=\"color:#ff0000\">Redo: Not implemented yet.</span>")

    def editCut(self):
        self.assy.cut()
        self.win_update()

    def editCopy(self):
        self.assy.copy()
        self.win_update()

    def editPaste(self):
        if self.assy.shelf.members:
            self.pasteP = True
            self.glpane.setMode('DEPOSIT')
            
    # editDelete
    def killDo(self):
        """ Deletes selected atoms, chunks, jigs and groups.
        """
        self.assy.kill()
        self.glpane.paintGL()
        self.mt.mt_update()

    def editFind(self):
        self.statusBar.message("<span style=\"color:#ff0000\">Find: Not implemented yet.</span>")

    ###################################
    # View Toolbar Slots
    ###################################

    def setViewHome(self):
        """Reset view to Home view"""
        self.statusBar.message(greenmsg("Current View: HOME"))
        self.glpane.quat = Q(self.assy.csys.quat) 
        self.glpane.scale = self.assy.csys.scale
        self.glpane.pov = V(self.currentPov[0], self.currentPov[1], self.currentPov[2])
      
        self.glpane.paintGL()


    def setViewFitToWindow(self):
        """ Fit to Window """
        #Recalculate center and bounding box for the assembly    
        self.assy.computeBoundingBox()     

        self.glpane.scale=self.assy.bbox.scale()
        self.glpane.pov = -self.assy.center
        self.glpane.paintGL()
            
    def setViewHomeToCurrent(self):
        """Changes Home view to the current view.  This saves the view info in the Csys"""
        self.assy.csys.quat = Q(self.glpane.quat)
        self.assy.csys.scale = self.glpane.scale
        self.currentPov = V(self.glpane.pov[0], self.glpane.pov[1], self.glpane.pov[2])
        self.assy.modified = 1 # Csys record changed in assy.  Mark [041215]
                
    # GLPane.ortho is checked in GLPane.paintGL
    def setViewOrtho(self):
        self.glpane.ortho = 1
        self.glpane.paintGL()

    def setViewPerspec(self):
        self.glpane.ortho = 0
        self.glpane.paintGL()

    def setViewBack(self):
        self.statusBar.message(greenmsg("Current View: BACK"))
        self.glpane.quat = Q(V(0,1,0),pi)
        self.glpane.paintGL()

    def setViewBottom(self):
        self.statusBar.message(greenmsg("Current View: BOTTOM"))
        self.glpane.quat = Q(V(1,0,0),-pi/2)
        self.glpane.paintGL()

    def setViewFront(self):
        self.statusBar.message(greenmsg("Current View: FRONT"))
        self.glpane.quat = Q(1,0,0,0)
        self.glpane.paintGL()

    def setViewLeft(self):
        self.statusBar.message(greenmsg("Current View: LEFT"))
        self.glpane.quat = Q(V(0,1,0),pi/2)
        self.glpane.paintGL()

    def setViewRight(self):
        self.statusBar.message(greenmsg("Current View: RIGHT"))
        self.glpane.quat = Q(V(0,1,0),-pi/2)
        self.glpane.paintGL()

    def setViewTop(self):
        self.statusBar.message(greenmsg("Current View: TOP"))
        self.glpane.quat = Q(V(1,0,0),pi/2)
        self.glpane.paintGL()

    ###################################
    # Display Toolbar Slots
    ###################################
    
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
            if self.glpane.display == form:
                pass ## was 'return' # no change needed
                # bruce 041129 removing this optim, tho correct in theory,
                # since it's not expensive to changeapp and repaint if user
                # hits a button, so it's more important to fix any bugs that
                # might be in other code failing to call changeapp when needed.
            self.glpane.setDisplay(form)
        self.win_update() # bruce 041206, needed for model tree display mode icons
        ## was self.glpane.paintGL()


    def setdisplay(self, a0):
        #bruce 041129 suspects this is obsolete
        print 'setdisplay', a0


    # set the color of the selected molecule
    # atom colors cannot be changed singly
    def dispObjectColor(self):
        if not self.assy.selmols: return
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
        "let user change the current mode's background color"
        # get r, g, b values of current background color
        r = int (self.glpane.mode.backgroundColor[0] * 255)
        g = int (self.glpane.mode.backgroundColor[1] * 255)
        b = int (self.glpane.mode.backgroundColor[2] * 255) 

        # allow user to select a new background color and set it.
        # bruce 050105: now this new color persists after new files are opened,
        # and into new sessions as well.
        c = QColorDialog.getColor(QColor(r, g, b), self, "choose")
        if c.isValid():
            color = (c.red()/255.0, c.green()/255.0, c.blue()/255.0)
            self.glpane.mode.set_backgroundColor( color ) #bruce 050105
            self.glpane.paintGL()

    def dispSetEltable1(self):
        "set global atom radius/color table to choice 1 (the default)"
        import elements
        elements.set_element_table(1, self.assy)
        self.glpane.paintGL()

    def dispSetEltable2(self):
        "set global atom radius/color table to choice 2"
        import elements
        elements.set_element_table(2, self.assy)
        self.glpane.paintGL()


    ###############################################################
    # Select Toolbar Slots
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
        If some atoms are selected, select the other atoms instead
        (even in chunks with no atoms selected, which end up with
        all atoms selected). (And unselect all currently selected
        parts or atoms.)
        """
        # assy method revised by bruce 041217 after discussion with Josh
        self.assy.selectInvert()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """
        if not self.assy.selatoms:
            self.statusBar.message("<span style=\"color:#ff0000\">Select Connected: No atom(s) selected.</span>")
            return
        self.assy.selectConnected()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed


    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """
        if not self.assy.selatoms:
            self.statusBar.message("<span style=\"color:#ff0000\">Select Doubly: No atom(s) selected.</span>")
            return
        self.assy.selectDoubly()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    ###################################
    # Jig Toolbar Slots
    ###################################

    def makeGround(self):
        self.assy.makeground()
        self.win_update()
        
    def makeStat(self):
        self.assy.makestat()
        self.win_update()

    def makeMotor(self):
        self.assy.makeRotaryMotor(self.glpane.lineOfSight)
        self.win_update()

    def makeLinearMotor(self):
        self.assy.makeLinearMotor(self.glpane.lineOfSight)
        self.win_update()

    ###################################
    # Modify Toolbar Slots
    ###################################
    
    def modifyMinimize(self):
        """ Minimize the current assembly """
        self.glpane.minimize()

    def modifyHydrogenate(self):
        """ Add hydrogen atoms to each singlet in the selection """
        self.assy.modifyHydrogenate()
        
    # remove hydrogen atoms from selected atoms/molecules
    def modifyDehydrogenate(self):
        """ Remove all hydrogen atoms from the selection """
        self.assy.modifyDehydrogenate()
        
    def modifyPassivate(self):
        """ Passivate the selection by changing surface atoms to eliminate singlets """
        self.assy.modifyPassivate()
    
    def modifyStretch(self):
        """ Stretch/expand the selected chunk(s) """
        self.assy.Stretch()
        
    def modifySeparate(self):
        """ Form a new chunk from the selected atoms """
        self.assy.modifySeparate()

    # bring molecules together and bond unbonded sites
    def modifyWeld(self):
        """ Create a single chunk from two of more selected chunks """
        self.assy.weld()
        self.win_update()

    def modifyAlignCommonAxis(self):
        """ Align selected chunks by rotating them """
        self.assy.align()
        self.win_update()
        
    ###################################
    # Help Toolbar Slots
    ###################################

    def helpContents(self):
        global helpwindow
        if not helpwindow: helpwindow = help.Help()
        helpwindow.show()
        #assistant  = QAssistantClient('', self)
        #assistant.showPage('/home/huaicai/atom/cad/doc/html/index.html')

    def helpAssistant(self):
        # bruce 041118 moved this into assistant.py so I could merge
        # common code about where to find the docfiles
        self.assistant.openNE1Assistant()
             
    def helpAbout(self):
        cntl = AboutDialog() # About NE-1 Dialog
        cntl.exec_loop()
             
    def helpWhatsThis(self):
        QWhatsThis.enterWhatsThisMode ()


    ###################################
    # Tools Toolbar Slots
    ###################################

    # get into Select Atoms mode
    def toolsSelectAtoms(self):
        self.glpane.setMode('SELECTATOMS')

    # get into Select Chunks mode
    def toolsSelectMolecules(self):
        self.glpane.setMode('SELECTMOLS')

    # get into Move Chunks mode        
    def toolsMoveMolecule(self):
        self.glpane.setMode('MODIFY')

    # get into Build atoms mode 
    def addAtomStart(self):
        self.pasteP = False
        self.glpane.setMode('DEPOSIT')

    # get into Build atoms mode (duplicate of above).  
    # Should remove one and rename the other to toolsBuildAtoms.  Mark
    def toolsAtomStart(self):
        self.pasteP = False
        self.glpane.setMode('DEPOSIT')
        
    # get into cookiecutter mode
    def toolsCookieCut(self):
        self.glpane.setMode('COOKIE')

    # get into Extrude mode
    def toolsExtrude(self):
        self.glpane.setMode('EXTRUDE')
    
    # Open the Simulator dialog to run a simulation.
    def toolsSimulator(self):
        """Creates a movie of a molecular dynamics simulation.
        """
        if not self.assy.molecules: # Nothing in the part to minimize.
            self.statusBar.message("<span style=\"color:#ff0000\">Simulator: Nothing to simulate.</span>")
            return
        self.simCntl = runSim(self.assy)
        self.simCntl.show()
        
    # Play a movie created by the simulator.
    def toolsMoviePlayer(self):
        """Plays a DPB movie file created by the simulator.
        """
        # If no simulation has been run yet, check to see if there is a "partner" moviefile.
        # If so, go ahead and play it.
        if not self.assy.moviename and self.assy.filename:
            mfile = self.assy.filename[:-4] + ".dpb"
            if os.path.exists(mfile): self.assy.moviename = mfile

        # Make sure there is a moviefile to play.
        if not self.assy.moviename or not os.path.exists(self.assy.moviename):

            msg = "<span style=\"color:#ff0000\">Movie Player: No movie file.</span>"
            self.statusBar.message(msg)

            msg = "To create a movie, click on the <b>Simulator</b> <img source=\"simicon\"> icon."
            QMimeSourceFactory.defaultFactory().setPixmap( "simicon", 
                        self.toolsSimulator_Action.iconSet().pixmap() )
            self.statusBar.message(msg)
            return

        # We have a moviefile ready to go.  It's showtime!!!
        self.hideDashboards()
        self.moviePauseAction.setVisible(1)
        self.moviePlayAction.setVisible(0)
        self.moviePlayerDashboard.show()
        self.glpane.startmovie(self.assy.moviename)

    # Movie Player Dashboard Slots ############
    
    def moviePause(self):
        self.glpane.pausemovie()
        
    def moviePlay(self):
        self.glpane.playmovie()
        
    def movieDone(self):
        self.moviePlayerDashboard.hide()
        self.glpane.pausemovie()
        self.selectMolDashboard.show()
        self.glpane.setMode('SELECTMOLS')


    ###################################
    # Slots for future tools
    ###################################
    
    # get into Revolve mode [bruce 041015]
    def toolsRevolve(self):
        self.glpane.setMode('REVOLVE')
        
    # Mirror Tool
    def toolsMirror(self):
        self.statusBar.message("<span style=\"color:#ff0000\">Mirror Tool: Not implemented yet.</span>")
             
    # Mirror Circular Boundary Tool
    def toolsMirrorCircularBoundary(self):
        self.statusBar.message("<span style=\"color:#ff0000\">Mirror Circular Boundary Tool: Not implemented yet.</span>")

    ###################################
    # Slots for Dashboard widgets
    ###################################

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

    #######################################
    # Cookie Cutter Dashboard Slots
    #######################################
    
    # "push down" one nanometer to cut out the next layer
    def toolsCCAddLayer(self):
        if self.glpane.shape:
            self.glpane.pov -= self.glpane.shape.pushdown()
            self.glpane.paintGL()

    # points of view corresponding to the three crystal
    # surfaces of diamond

    # along one axis
    def orient100(self):
        self.glpane.mode.surfset(0)
        self.glpane.snapquat100()

    # halfway between two axes
    def orient110(self):
        self.glpane.mode.surfset(1)
        self.glpane.snapquat110()

    # equidistant from three axes
    def orient111(self):
        self.glpane.mode.surfset(2)
        self.glpane.snapquat111()

    # lots of things ???
    def orientView(self, a0=None):
        print "MainWindow.orientView(string):", a0
        self.glpane.quat = Q(1,0,0,0)
        self.glpane.pov = V(0,0,0)
        self.glpane.paintGL()

    #######################################
    # Element Selector Slots
    #######################################
    
    # pop up set element box
    def modifySetElement(self):
#        print "modifySetElement: Current Element = ", self.Element    
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
    # [bruce 041215: most of this should be made a method in elementSelector.py #e]
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

    ###################################
    # some unimplemented buttons:
    ###################################
    
    # create bonds where reasonable between selected and unselected
    def modifyEdgeBond(self):
        print "MWsemantics.modifyEdgeBond(): Not implemented yet"
        QMessageBox.information(self, self.name() + " User Notice:",
             "This function is not implemented yet, coming soon...")
        
    # create bonds where reasonable between selected and unselected
    def toolsAddBond(self):
        print "MWsemantics.modifyAddBond(): Not implemented yet"
        QMessageBox.information(self, self.name() + " User Notice:",
             "This function is not implemented yet, coming soon...")

    # Turn on or off the trihedron compass.
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
        QMessageBox.information(self, self.name() + " User Notice:",
             "This function is not implemented yet, coming soon...")

    # 2BDone: make a copy of the selected part, move it, and bondEdge it,
    # having unselected the original and selected the copy.
    # the motion is to be the same relative motion done to a part
    # between copying and bondEdging it.
    def modifyCopyBond(self):
        print "MWsemantics.modifyCopyBond(): Not implemented yet"
        QMessageBox.information(self, self.name() + " User Notice:",
             "This function is not implemented yet, coming soon...")


    # utility functions

    def colorchoose(self, r, g, b): # r, g, b is the default color displayed in the QColorDialog window.
        color = QColorDialog.getColor(QColor(r, g, b), self, "choose")
        if color.isValid():
            return color.red()/255.0, color.green()/255.0, color.blue()/255.0
        else:
            return r/255.0, g/255.0, b/255.0

    # key event handling revised by bruce 041220 to fix some bugs;
    # see comments in the GLPane methods.
    
    def keyPressEvent(self, e):
        self.glpane.keyPressEvent(e)
        
    def keyReleaseEvent(self, e):
        self.glpane.keyReleaseEvent(e)

    ##############################################################
    # Some future slot functions for the UI                      #
    ##############################################################

    def dispDatumLines(self):
        """ Toggle on/off datum lines """
        self.statusBar.message("<span style=\"color:#ff0000\">Display Datum Lines: Not implemented yet.</span>")

    def dispDatumPlanes(self):
        """ Toggle on/off datum planes """
        self.statusBar.message("<span style=\"color:#ff0000\">Display Datum Planes: Not implemented yet.</span>")

    def dispOpenBonds(self):
        """ Toggle on/off open bonds """
        self.statusBar.message("<span style=\"color:#ff0000\">Display Open Bonds: Not implemented yet.</span>")

    def editPrefs(self):
        """ Edit square grid line distances(dx, dy, dz) in nm/angstroms """
        self.statusBar.message("<span style=\"color:#ff0000\">Edit Preferences: Not implemented yet.</span>")
 
    def elemChangePTable(self):
        """ Future: element change via periodic table
        (only elements we support) """
             
    def validateThickness(self, s):
        if self.vd.validate( s, 0 )[0] != 2: self.ccLayerThicknessLineEdit.setText(s[:-1])

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
                        
        # Create "DepositAtomCursor" cursor [differently for Mac or non-Mac]
        if not platform.is_macintosh():
          # use original code
          self.DepositAtomCursor = QCursor(
            QBitmap(filePath + "/../images/DepositAtomCursor.bmp"),
            QBitmap(filePath + "/../images/DepositAtomCursor-bm.bmp"),
            0, 32)
            #bruce 041104 note: 32 is beyond the pixel array; 31 might be better
        else:
          # bruce 041104 bugfix for Mac, whose hotspot can't be (0,31) since
          # that acts like (0,15) or so; in fact, by experiment, hotspot (x,y)
          # acts like ( min(x,15), min(y,15) ) (exact value of upper limit is
          # a guess); so a workaround is to invert the cursor and the desired
          # hotspot in y (though we might decide to just do this on all
          # platforms, for a uniform look):
          self.DepositAtomCursor = QCursor(
            QBitmap(filePath + "/../images/DepositAtomCursor.bmp").xForm(QWMatrix(1,0,0,-1, 0,0)),
            QBitmap(filePath + "/../images/DepositAtomCursor-bm.bmp").xForm(QWMatrix(1,0,0,-1, 0,0)),
            0, 0)
        
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
        self.statusBar = self.statusBar()
        # bruce comment 041223: it's bad to reuse this Qt-defined method name
        # for an attribute! I'll remove this as soon as practical.

        # (see also self.set_status_text())

        # Mark - Set up primary (left) message bar in status bar area.
        #self.msgbarLabel = QLabel(self.statusBar, "msgbarLabel")
        #self.msgbarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        #self.msgbarLabel.setText( " " )
        #self.statusBar.addWidget(self.msgbarLabel, 1, 0)

        # Mark - Set up mode bar (right) in status bar area.        
        self.dispbarLabel = QLabel(self.statusBar, "dispbarLabel")
        self.dispbarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        self.statusBar.addWidget(self.dispbarLabel, 0, True)
        
        # Mark - Set up mode bar (right) in status bar area.        
        self.modebarLabel = QLabel(self.statusBar, "modebarLabel")
        self.modebarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        self.statusBar.addWidget(self.modebarLabel, 0, True)

        # bruce 041223 temporary compatibility kluge:
        # replace self.statusBar with a compatibility object, just until all
        # other files' uses of it (including everyone's local mods which are
        # not yet committed) are changed.
        class nullclass: pass
        self.statusBar = nullclass()
            # that could be anything whose message attribute we can overwrite!
        self.statusBar.message = self.set_status_text
        
        return
    
    def hideDashboards(self):
        self.cookieCutterDashboard.hide()
        self.extrudeDashboard.hide()
        self.revolveDashboard.hide()
        self.depositAtomDashboard.hide()
        self.datumDispDashboard.hide()  # (mark note: this is the datum display toolbar)
        self.selectMolDashboard.hide()
        self.selectAtomsDashboard.hide()
        self.moveMolDashboard.hide()
        self.moviePlayerDashboard.hide()
        
        ##Huaicai 12/08/04, remove unnecessary toolbars from context menu
        objList = self.queryList("QToolBar")
        for obj in objList:
                if obj in [self.datumDispDashboard, self.moviePlayerDashboard, self.moveMolDashboard, self.cookieCutterDashboard, self.depositAtomDashboard, self.extrudeDashboard, self.selectAtomsDashboard, self.selectMolDashboard]:
                         self.setAppropriate(obj, False)

    # Import code for What's This support        
    from whatsthis import createWhatsThis

    # end of class MWsemantics
