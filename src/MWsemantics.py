# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
MWsemantics.py provides the main window class, MWsemantics.

$Id$
'''

## bruce 050408 removed: import qt
from qt import QWidget, QFrame, SIGNAL, QFileDialog
    ## bruce 050408 removed: QPushButton, QMainWindow, QPixmap, QGroupBox,
    ## QComboBox, QAction, QMenuBar, QPopupMenu, SLOT, QListView, QListViewItem
from qt import QCursor, QBitmap, QWMatrix, QLabel, QSplitter, QMessageBox, QString, QColorDialog, QColor
from GLPane import GLPane ## bruce 050408 removed: import *
from assembly import assembly ## bruce 050408 added this, was coming from GLPane
import os, sys
import help
from math import ceil
from modelTree import modelTree ## bruce 050408 removed: import *
import platform

from constants import *
from elementColors import elementColors ## bruce 050408 removed: import *
from elementSelector import elementSelector ## bruce 050408 removed: import *
from MMKit import MMKit
from fileIO import * # this might be needed for some of the many other modules it imports; who knows? [bruce 050418 comment]
from files_pdb import readpdb, insertpdb, writepdb
from files_gms import readgms, insertgms
from files_mmp import readmmp, insertmmp, fix_assy_and_glpane_views_after_readmmp
from debug import print_compact_traceback

from MainWindowUI import MainWindow
from assistant import AssistantWindow
from HistoryWidget import greenmsg, redmsg

from movieMode import movieDashboardSlotsMixin
from changes import register_postinit_object
import preferences

helpwindow = None
elementSelectorWin = None
elementColorsWin = None
MMKitWin = None
windowList = []

eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]

eCCBtab2 = {}
for i,elno in zip(range(len(eCCBtab1)), eCCBtab1):
    eCCBtab2[elno] = i
    
def fileparse(name): #bruce 050413 comment: see also filesplit and its comments.
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))

class pre_init_fake_history_widget:
    too_early = 1
        # defined so insiders can detect that it's too early (using hasattr)
        # and not call us at all (as they could have using hasattr on win.history
        #  before this "safety net" for early messages was added)
    def message(self, msg, **options):
        """This exists to handle messages sent to win.history during
        win.__init__, before the history widget has been created!"""
        if platform.atom_debug:
            print "fyi: too early for this status msg:", msg
        pass # too early
    pass

class MWsemantics( movieDashboardSlotsMixin, MainWindow):
    "The single Main Window object."

    #bruce 050413 split out movieDashboardSlotsMixin, which needs to come before MainWindow
    # in the list of superclasses, since MainWindow overrides its methods with "NIM stubs".
    
    initialised = 0 #bruce 041222
    history = pre_init_fake_history_widget() #bruce 050107
    
    def __init__(self, parent = None, name = None):
    
        global windowList

        MainWindow.__init__(self, parent, name, Qt.WDestructiveClose)

        # bruce 050104 moved this here so it can be used earlier
        # (it might need to be moved into atom.py at some point)
        self.tmpFilePath = platform.find_or_make_Nanorex_directory()

        # bruce 040920: until MainWindow.ui does the following, I'll do it manually:
        import extrudeMode as _extrudeMode
        _extrudeMode.do_what_MainWindowUI_should_do(self)
        # (the above function will set up both Extrude and Revolve)
        
        import depositMode as _depositMode
        _depositMode.do_what_MainWindowUI_should_do(self)
        
        # mark 050711: Added Select Atoms dashboard.
        import selectMode as _selectMode
        _selectMode.do_what_MainWindowUI_should_do(self)
        
        # mark 050411: Added Move Mode dashboard.
        import modifyMode as _modifyMode
        _modifyMode.do_what_MainWindowUI_should_do(self)
        
        # mark 050428: Added Fuse Chunk dashboard.
        import fusechunksMode as _fusechunksMode
        _fusechunksMode.do_what_MainWindowUI_should_do(self)
        
        # Load all the custom cursors
        self.loadCursors()
        
        # Hide all dashboards
        self.hideDashboards()
        
        # Create our 2 status bar widgets - msgbarLabel and modebarLabel
        # (see also self.history.message())
        self.createStatusBars()
        
        # Create Assistant - Mark 11-23-2004
        self.assistant = AssistantWindow(self, "Assistant")

        windowList += [self]
        if name == None:
            self.setName("nanoENGINEER-1") # Mark 11-05-2004
#            self.setName("Atom") 

        # start with empty window 
        self.assy = assembly(self, "Untitled")
        #bruce 050429: as part of fixing bug 413, it's now required to call
        # self.assy.reset_changed() sometime in this method; it's called below.
        
        # Set the caption to the name of the current (default) part - Mark [2004-10-11]
#        self.setCaption(self.trUtf8( self.name() +  " - " + "[" + self.assy.name + "]"))
        self.update_mainwindow_caption()

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

        import env
        env.history = self.history #bruce 050727

        # ... and some final vsplitter setup [bruce 041223]
        vsplitter.setResizeMode(self.history.widget, QSplitter.KeepSize)
        vsplitter.setOpaqueResize(False)
        self.setCentralWidget(vsplitter) # this was required (what exactly does it do?)

        # Create a progress bar widget for use during time consuming operations,
        # such as minimize, simulator and select doubly.  Mark 050101
        from ProgressBar import ProgressBar
        self.progressbar = ProgressBar()
        
        # Create the Preferences dialog widget.
        # Mark 050628
        from UserPrefs import UserPrefs
        self.uprefs = UserPrefs(self.assy)

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
        from whatsthis import createWhatsThis
        createWhatsThis(self)

        # Start with Carbon as the default element (for Deposit Mode
        # and the Element Selector)
        self.Element = 6
        self.setElement(6)
        # and paste the atom rather than the clipboard by default
        self.pasteP = False
        
        self.assy.reset_changed() #bruce 050429, part of fixing bug 413

        ###### User Preference initialization ##############################
        
        # Get MainWindowUI related settings from prefs db.
        # If they are not found, set default values here.
        # The keys are located in constants.py 
        # Mark 050716
        
        prefs = preferences.prefs_context()
        
        self.caption_prefix = prefs.get(captionPrefix_prefs_key, '')
        self.caption_suffix = prefs.get(captionSuffix_prefs_key, '*')
        self.caption_fullpath = prefs.get(captionFullPath_prefs_key, False)
        
        ###### End of User Preference initialization ########################## 


        self.initialised = 1

        # be told to add new Jigs menu items, now or as they become available [bruce 050504]
        register_postinit_object( "Jigs menu items", self )

        self.win_update() # bruce 041222
        
        return # from MWsemantics.__init__

    def postinit_item(self, item): #bruce 050504
        try:
            item(self)
        except:
            # blame item
            print_compact_traceback( "exception (ignored) in postinit_item(%r): " % item )
        return
        
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
        self.glpane.gl_update() ###e should inval instead -- soon, this method will!
        self.mt.mt_update()
        self.history.h_update() #bruce 050104
        

    ###################################
    # File Toolbar Slots
    ###################################

    def fileNew(self):
        """If this window is empty (has no assembly), do nothing.
        Else create a new empty one.
        """
        #bruce 050418 comment: this has never worked correctly to my knowledge,
        # and therefore it was made unavailable from the UI some time ago.
        foo = MWsemantics()
        foo.show()

    def fileInsert(self):
        
        self.history.message(greenmsg("Insert File:"))
         
        wd = globalParms['WorkingDirectory']
        fn = QFileDialog.getOpenFileName(wd,
                "Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb);;GAMESS (*.out);;All of the above (*.pdb *.mmp *.out)",
                self )
                
        if not fn:
             self.history.message("Cancelled")
             return
        
        if fn:
            fn = str(fn)
            if not os.path.exists(fn):
                #bruce 050415: I think this should never happen;
                # in case it does, I added a history message (to existing if/return code).
                self.history.message( redmsg( "File not found: " + fn) )
                return

            if fn[-3:] == "mmp":
                try:
                    insertmmp(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting MMP file [%s]: " % fn )
                    self.history.message( redmsg( "Internal error while inserting MMP file: " + fn) )
                else:
                    self.assy.changed() # The file and the part are not the same.
                    self.history.message( "MMP file inserted: " + fn )
            
            if fn[-3:] in ["pdb","PDB"]:
                try:
                    insertpdb(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting PDB file [%s]: " % fn )
                    self.history.message( redmsg( "Internal error while inserting PDB file: " + fn) )
                else:
                    self.assy.changed() # The file and the part are not the same.
                    self.history.message( "PDB file inserted: " + fn )
            
            if fn[-3:] in ["out","OUT"]:
                try:
                    r = insertgms(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting GAMESS OUT file [%s]: " % fn )
                    self.history.message( redmsg( "Internal error while inserting GAMESS OUT file: " + fn) )
                else:
                    if r:
                        self.history.message( redmsg("File not inserted."))
                    else:
                        self.assy.changed() # The file and the part are not the same.
                        self.history.message( "GAMESS file inserted: " + fn )
                    
                    
            self.glpane.scale = self.assy.bbox.scale()
            self.glpane.gl_update()
            self.mt.mt_update()


    def fileOpen(self):
        
        self.history.message(greenmsg("Open File:"))
        
        if self.assy.has_changed():
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
            
            elif ret==2: 
                self.history.message("Cancelled.")
                return # Cancel clicked or Alt+C pressed or Escape pressed

        # Determine what directory to open.
        if self.assy.filename: odir, fil, ext = fileparse(self.assy.filename)
        else: odir = globalParms['WorkingDirectory']

        fn = QFileDialog.getOpenFileName(odir,
                "All Files (*.mmp *.pdb);;Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb)",
                self )
                
        if not fn:
            self.history.message("Cancelled.")
            return

        if fn:
            self.__clear()
                
            fn = str(fn)
            if not os.path.exists(fn): return

            isMMPFile = False
            if fn[-3:] == "mmp":
                readmmp(self.assy,fn)
                    #bruce 050418 comment: we need to check for an error return
                    # and in that case don't clear or have other side effects on assy;
                    # this is not yet perfectly possible in readmmmp.
                self.history.message("MMP file opened: [" + fn + "]")
                isMMPFile = True
                
            if fn[-3:] in ["pdb","PDB"]:
                readpdb(self.assy,fn)
                self.history.message("PDB file opened: [" + fn + "]")

            dir, fil, ext = fileparse(fn)
            self.assy.name = fil
            self.assy.filename = fn
            self.assy.reset_changed() # The file and the part are now the same

#            self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
            self.update_mainwindow_caption()

            if isMMPFile:
                #bruce 050418 moved this code into a new function in files_mmp.py
                # (but my guess is it should mostly be done by readmmp itself)
                fix_assy_and_glpane_views_after_readmmp( self.assy, self.glpane)
            else: ###PDB or other file format        
                self.setViewFitToWindow()

            self.glpane.gl_update() #bruce 050418
            self.mt.mt_update()

    def fileSave(self):
        
        self.history.message(greenmsg("Save File:"))
        
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
            self.history.message( "Save Ignored: Part is currently empty." )
            return False

        if ext == ".pdb": sfilter = QString("Protein Data Bank (*.pdb)")
        else: sfilter = QString("Molecular machine parts (*.mmp)")
        
        fn = QFileDialog.getSaveFileName(sdir,
                    "Molecular Machine Part (*.mmp);;"\
                    "Protein Data Bank (*.pdb);;"\
                    "POV-Ray (*.pov);;"\
                    "Model MDL (*.mdl);;"\
                    "JPEG (*.jpg);;"\
                    "Portable Network Graphics (*.png)",
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
                        self.history.message( "Cancelled.  Part not saved." )
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
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                self.history.message(redmsg( "Problem saving PDB file: " + safile ))
            else:
                self.assy.filename = safile
                self.assy.name = fil
                self.assy.reset_changed() # The file and the part are now the same.
#                self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
                self.update_mainwindow_caption()
                self.history.message( "PDB file saved: " + self.assy.filename )
                self.mt.mt_update()
            
        elif ext == ".pov": # Write POV-Ray file
            try:
                writepovfile(self.assy, safile)
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                self.history.message(redmsg( "Problem saving POV-Ray file: " + safile ))
            else:
                self.history.message( "POV-Ray file saved: " + safile )
            
        elif ext == ".mdl": # Write MDL file
            try:
                writemdlfile(self.assy, safile)
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                self.history.message(redmsg( "Problem saving MDL file: " + safile ))
            else:
                self.history.message( "MDL file saved: " + safile )
            
        elif ext == ".jpg": # Write JPEG file
            try:
                image = self.glpane.grabFrameBuffer()
                image.save(safile, "JPEG", 85)
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                self.history.message(redmsg( "Problem saving JPEG file: " + safile ))
            else:
                self.history.message( "JPEG file saved: " + safile )
            
        elif ext == ".png": # Write PNG file
            try:
                image = self.glpane.grabFrameBuffer()
                image.save(safile, "PNG")
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                self.history.message(redmsg( "Problem saving PNG file: " + safile ))
            else:
                self.history.message( "PNG file saved: " + safile )
                    
        elif ext == ".mmp" : # Write MMP file
            try:
                tmpname = os.path.join(dir, '~' + fil + '.m~')
                self.assy.writemmpfile(tmpname)
            except:
                #bruce 050419 revised printed error message
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file [%s]: " % safile )
                self.history.message(redmsg( "Problem saving file: " + safile ))
                
                # If you want to see what was wrong with the MMP file, you
                # can comment this out so you can see what's in
                # the temp MMP file.  Mark 050128.
                if os.path.exists(tmpname):
                    os.remove (tmpname) # Delete tmp MMP file
            else:
                if os.path.exists(safile):
                    os.remove (safile) # Delete original MMP file

                os.rename( tmpname, safile) # Move tmp file to saved filename. 
                
                self.assy.filename = safile
                self.assy.name = fil
                self.assy.reset_changed() # The file and the part are now the same.
#                self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
                self.update_mainwindow_caption()
                self.history.message( "MMP file saved: " + self.assy.filename )
                self.mt.mt_update()
            
        else: # This should never happen.
            self.history.message(redmsg( "MWSemantics.py: fileSaveAs() - File Not Saved. Unknown extension:" + ext))

    def closeEvent(self,ce): 
        """  via File > Exit or clicking X titlebar button """
        isEventAccepted = True
        if not self.assy.has_changed():
            ce.accept()
        else:
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
                    isEventAccepted = False
            elif rc == 1:
                ce.accept()
            else:
                ce.ignore()
                isEventAccepted = False
        
        #if isEventAccepted: self.periodicTable.close()
            

    def fileClose(self):
        
        self.history.message(greenmsg("Close File:"))
        
        isFileSaved = True
        if self.assy.has_changed():
            ret = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before closing this part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: isFileSaved = self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
            elif ret==1:
                self.history.message("Changes discarded.")
            elif ret==2: 
                self.history.message("Cancelled.")
                return # Cancel clicked or Alt+C pressed or Escape pressed
        
        if isFileSaved: 
                self.__clear()
                self.assy.reset_changed() #bruce 050429, part of fixing bug 413
                self.win_update()


    def fileSetWorkDir(self):
        """Sets working directory"""

        self.history.message(greenmsg("Set Working Directory:"))
        
        wd = globalParms['WorkingDirectory']
        wdstr = "Current Working Directory - [" + wd  + "]"
        wd = QFileDialog.getExistingDirectory( wd, self, "get existing directory", wdstr, 1 )
        
        if not wd:
            self.history.message("Cancelled.")
            return
            
        if wd:
            wd = str(wd)
            wd = os.path.normpath(wd)
            globalParms['WorkingDirectory'] = wd
            
            self.history.message( "Working Directory set to " + wd )

            # bruce 050119: store this in prefs database so no need for ~/.ne1rc
            from preferences import prefs_context
            prefs = prefs_context()
            prefs['WorkingDirectory'] = wd
                
    def __clear(self):
        # assyList refs deleted by josh 10/4
        self.assy = assembly(self, "Untitled")
#        self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.name + "]"))
        self.update_mainwindow_caption()
        self.glpane.setAssy(self.assy)
        self.assy.mt = self.mt
        
        ### Hack by Huaicai 2/1 to fix bug 369
        self.mt.resetAssy_and_clear() 


    ###################################
    # Edit Toolbar Slots
    ###################################

    def editUndo(self):
        self.history.message(redmsg("Undo: Not implemented yet."))

    def editRedo(self):
        self.history.message(redmsg("Redo: Not implemented yet."))

    # bruce 050131 moved some history messages from the following methods
    # into the assy methods they call, so the menu command versions also have them
    
    def editCut(self):
        self.assy.cut_sel()
        self.win_update()

    def editCopy(self):
        self.assy.copy_sel()
        self.win_update()

    def editPaste(self):
        if self.assy.shelf.members:
            self.history.message(greenmsg("Paste:"))
            self.pasteP = True
            self.glpane.setMode('DEPOSIT')
            
    # editDelete
    def killDo(self):
        """ Deletes selected atoms, chunks, jigs and groups.
        """
        self.assy.delete_sel()
        ##bruce 050427 moved win_update into delete_sel as part of fixing bug 566
        ##self.win_update()

    def editPrefs(self):
        """ Edit Preferences """
        self.uprefs.showDialog()

    ###################################
    # View Toolbar Slots
    ###################################

    def setViewHome(self):
        """Reset view to Home view"""
        cmd = greenmsg("Current View: ")
        info = 'Home'
        self.history.message(cmd + info)
        self.glpane.setViewHome()

    def setViewFitToWindow(self):
        """ Fit to Window """
        cmd = greenmsg("Fit to Window: ")
        info = ''
        self.history.message(cmd + info)
        self.glpane.setViewFitToWindow()
            
    def setViewHomeToCurrent(self): #bruce 050418 revised docstring, and moved bodies of View methods into GLPane
        """Changes Home view of the model to the current view in the glpane."""
        cmd = greenmsg("Set Home View to Current View: ")
        info = 'Home'
        self.history.message(cmd + info)
        self.glpane.setViewHomeToCurrent()
            
    def setViewRecenter(self):
        """Recenter the view around the origin of modeling space.
        """
        cmd = greenmsg("Recenter View: ")
        info = 'View Recentered'
        self.history.message(cmd + info)
        self.glpane.setViewRecenter()
                
    def zoomTool(self):
        """Zoom Tool, allowing the user to specify a rectangular area 
        by holding down the left button and dragging the mouse to zoom 
        into a specific area of the model.
        """
        # we never want these modes (ZOOM, PAN, ROTATE) to be assigned to "prevMode". 
        if self.glpane.mode.modename not in ['ZOOM', 'PAN', 'ROTATE']:
            self.glpane.prevMode = self.glpane.mode.modename
            self.glpane.prevModeColor = self.glpane.mode.backgroundColor

        self.glpane.setMode('ZOOM')
        
        # This should be placed in zoomMode.Enter or init_gui, but it always appears 
        # before the green "Entering Mode: Zoom" msg.  So I put it here.  Mark 050130
        self.history.message("You may hit the Esc key to exit Zoom Tool.")

    def panTool(self):
        """Pan Tool allows X-Y panning using the left mouse button.
        """
        # we never want these modes (ZOOM, PAN, ROTATE) to be assigned to "prevMode". 
        if self.glpane.mode.modename not in ['ZOOM', 'PAN', 'ROTATE']:
            self.glpane.prevMode = self.glpane.mode.modename
            self.glpane.prevModeColor = self.glpane.mode.backgroundColor

        self.glpane.setMode('PAN')
        self.history.message("You may hit the Esc key to exit Pan Tool.")

    def rotateTool(self):
        """Rotate Tool allows free rotation using the left mouse button.
        """
        # we never want these modes (ZOOM, PAN, ROTATE) to be assigned to "prevMode". 
        if self.glpane.mode.modename not in ['ZOOM', 'PAN', 'ROTATE']:
            self.glpane.prevMode = self.glpane.mode.modename
            self.glpane.prevModeColor = self.glpane.mode.backgroundColor

        self.glpane.setMode('ROTATE')
        self.history.message("You may hit the Esc key to exit Rotate Tool.")
                
    # GLPane.ortho is checked in GLPane.paintGL
    def setViewOrtho(self):
        self.glpane.ortho = 1
        self.glpane.gl_update()

    def setViewPerspec(self):
        self.glpane.ortho = 0
        self.glpane.gl_update()

    def setViewOpposite(self):
        '''Set view to the opposite of current view. '''
        cmd = greenmsg("Opposite View: ")
        info = 'Current view opposite to the previous view'
        self.history.message(cmd + info)
        self.glpane.quat += Q(V(0,1,0), pi)
        self.glpane.gl_update()

    def setViewBack(self):
        cmd = greenmsg("Back View: ")
        info = 'Current view is Back View'
        self.history.message(cmd + info)
        self.glpane.quat = Q(V(0,1,0),pi)
        self.glpane.gl_update()

    def setViewBottom(self):
        cmd = greenmsg("Bottom View: ")
        info = 'Current view is Bottom View'
        self.history.message(cmd + info)
        self.glpane.quat = Q(V(1,0,0),-pi/2)
        self.glpane.gl_update()

    def setViewFront(self):
        cmd = greenmsg("Front View: ")
        info = 'Current view is Front View'
        self.history.message(cmd + info)
        self.glpane.quat = Q(1,0,0,0)
        self.glpane.gl_update()

    def setViewLeft(self):
        cmd = greenmsg("Left View: ")
        info = 'Current view is Left View'
        self.history.message(cmd + info)
        self.glpane.quat = Q(V(0,1,0),pi/2)
        self.glpane.gl_update()

    def setViewRight(self):
        cmd = greenmsg("Right View: ")
        info = 'Current view is Right View'
        self.history.message(cmd + info)
        self.glpane.quat = Q(V(0,1,0),-pi/2)
        self.glpane.gl_update()

    def setViewTop(self):
        cmd = greenmsg("Top View: ")
        info = 'Current view is Top View'
        self.history.message(cmd + info)
        self.glpane.quat = Q(V(1,0,0),pi/2)
        self.glpane.gl_update()

    ###################################
    # Display Toolbar Slots
    ###################################
    
    # set display formats in whatever is selected,
    # or the GLPane global default if nothing is
    def dispDefault(self):
        self.setDisplay(diDEFAULT, True)

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

    def setDisplay(self, form, default_display=False):
        '''Set the display of the selection to 'form'.  If nothing is selected, then change
        the GLPane's current display to 'form'.
        '''
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
            self.glpane.setDisplay(form, default_display) # See docstring for info about default_display
        self.win_update() # bruce 041206, needed for model tree display mode icons
        ## was self.glpane.paintGL() [but now would be self.glpane.gl_update]

    # set the color of the selected molecule
    # atom colors cannot be changed singly
    def dispObjectColor(self):
        if not self.assy.selmols: 
            self.history.message(redmsg("Set Chunk Color: No chunks selected.")) #bruce 050505 added this message
            return
        c = QColorDialog.getColor(self.paletteBackgroundColor(), self, "Choose color")
        if c.isValid():
            molcolor = c.red()/255.0, c.green()/255.0, c.blue()/255.0
            for ob in self.assy.selmols:
                ob.setcolor(molcolor)
            self.glpane.gl_update()

    def dispResetChunkColor(self):
        "Resets the selected chunk's atom colors to the current element colors"
        if not self.assy.selmols: 
            self.history.message(redmsg("Reset Chunk Color: No chunks selected."))
            return
        
        for chunk in self.assy.selmols:
            chunk.setcolor(None)
        self.glpane.gl_update()
        
    def dispResetAtomsDisplay(self):
        "Resets the display setting for each atom in the selected chunks to Default display mode"
        if not self.assy.selmols: 
            self.history.message(redmsg("Reset Atoms Display: No chunks selected."))
            return
            
        self.assy.resetAtomsDisplay()
        self.history.message(greenmsg("Reset Atoms Display:"))
        msg = "Display setting for all atoms in selected chunk(s) reset to Default."
        self.history.message(msg)

        
    def dispShowInvisAtoms(self):
        "Resets the display setting for each invisible atom in the selected chunks to Default display mode"
        if not self.assy.selmols: 
            self.history.message(redmsg("Show Invisible Atoms: No chunks selected."))
            return
            
        nia = self.assy.showInvisibleAtoms() # nia = Number of Invisible Atoms
        self.history.message(greenmsg("Show Invisible Atoms:"))
        msg = str(nia) + " invisible atoms found."
        self.history.message(msg)
                    
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
            self.glpane.gl_update()


    # pop up Element Color Selector dialog
    def dispElementColorSettings(self):
        """Allows user to change default colors of elements and save them to a file.
        """
        global elementColorsWin
        #Huaicai 2/24/05: Create a new element selector window each time,  
        #so it will be easier to always start from the same states.
        # Make sure only a single element window is shown
        if elementColorsWin and elementColorsWin.isShown(): 
                    return 
        
        elementColorsWin = elementColors(self)
        elementColorsWin.setDisplay(self.Element)
        elementColorsWin.show()

    def dispLighting(self):
        """Allows user to change lighting brightness.
        """
        self.history.message(greenmsg("Lighting:"))

        from LightingTool import LightingTool
        self.lightcntl = LightingTool(self.glpane) # Open Lighting Tool dialog
        
    ###############################################################
    # Select Toolbar Slots
    ###############################################################

    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        """
        self.history.message(greenmsg("Select All:"))
        self.assy.selectAll()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectNone(self):
        self.history.message(greenmsg("Select None:"))
        self.assy.selectNone()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectInvert(self):
        """If some parts are selected, select the other parts instead.
        If some atoms are selected, select the other atoms instead
        (even in chunks with no atoms selected, which end up with
        all atoms selected). (And unselect all currently selected
        parts or atoms.)
        """
        self.history.message(greenmsg("Invert Selection:"))
        # assy method revised by bruce 041217 after discussion with Josh
        self.assy.selectInvert()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        Huaicai 1/19/05: This is called when user clicks the tool button,
        but when the user choose from pop up menu, only assy.selectConnected() called.
        I don't think this is good by any means, so I'll try to make them almost the same,
        but still keep this function. 
        """
        self.assy.selectConnected()
        
        ###Huaicai 1/19/05, commented the following line out
        ##self.update_mode_status() # bruce 040927... not sure if this is ever needed


    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds. 
        Huaicai 1/19/05, see commets for the above method
        """
        self.assy.selectDoubly()
        ##Huaicai 1/19/05 comment out, 
        #self.update_mode_status() # bruce 040927... not sure if this is ever needed

    ###################################
    # Jig Toolbar Slots
    ###################################

    def makeGamess(self):
        self.assy.makegamess()
        
    def makeGround(self):
        self.assy.makeground()
        
    def makeStat(self):
        self.assy.makestat()

    def makeThermo(self):
        self.assy.makethermo()
        
    def makeMotor(self):
        self.assy.makeRotaryMotor(self.glpane.lineOfSight)

    def makeLinearMotor(self):
        self.assy.makeLinearMotor(self.glpane.lineOfSight)

    ###################################
    # Modify Toolbar Slots
    ###################################
        
    def modifyMinimizeSel(self):
        """Minimize the current selection"""
        if platform.atom_debug: ###@@@ remove this when devel is done
            print "atom_debug: reloading runSim on each use, for development"
            import runSim
            reload(runSim)
        from runSim import Minimize_CommandRun
        cmdrun = Minimize_CommandRun( self, 'Sel')
        cmdrun.run()
        return

    def modifyMinimizeAll(self):
        """Minimize the entire (current) Part"""
        if platform.atom_debug: ###@@@ remove this when devel is done
            print "atom_debug: reloading runSim on each use, for development"
            import runSim
            reload(runSim)
        from runSim import Minimize_CommandRun
        cmdrun = Minimize_CommandRun( self, 'All')
        cmdrun.run()
        return
  
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
    
    def modifyDeleteBonds(self):
        """ Delete all bonds between selected and unselected atoms or chunks"""
        self.assy.modifyDeleteBonds()
            
    def modifyStretch(self):
        """ Stretch/expand the selected chunk(s) """
        self.assy.Stretch()
        
    def modifySeparate(self):
        """ Form a new chunk from the selected atoms """
        self.assy.modifySeparate()

    def modifyMerge(self):
        """ Create a single chunk from two of more selected chunks """
        self.assy.merge()
        self.win_update()

    def modifyInvert(self):
        """ Invert the atoms of the selected chunk(s) """
        self.assy.Invert()

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
        ## from somewhere import QAssistantClient ##bruce 050408
        #assistant  = QAssistantClient('', self)
        #assistant.showPage('/home/huaicai/atom/cad/doc/html/index.html')

    def helpAssistant(self):
        # bruce 041118 moved this into assistant.py so I could merge
        # common code about where to find the docfiles
        self.assistant.openNE1Assistant()
             
    def helpAbout(self):
        """Displays information about this version of nanoENGINEER-1
        """
        product = "nanoENGINEER-1 "
        version = "v0.0.6 Special (Alpha)" # This should come from __version__
        date = "Release Date: August 5, 2005" # This should come from __vdate__ or something similar
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        installdir = "Running from: " + filePath
        copyright = "Copyright (C) 2005, Nanorex, Inc."
        techsupport = "For technical support, send email to support@nanorex.com"
        website = "Website: www.nanoengineer-1.com"
        aboutstr = product + version \
                       + "\n\n" \
                       + date \
                       + "\n\n" \
                       + installdir \
                       + "\n\n" \
                       + copyright \
                       + "\n\n" \
                       + techsupport \
                       + "\n" \
                       + website
                      
        QMessageBox.about ( self, "About nanoENGINEER-1", aboutstr)
             
    def helpWhatsThis(self):
        from qt import QWhatsThis ##bruce 050408
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

   
    def toolsBuildAtoms(self):
        self.pasteP = False
        self.glpane.setMode('DEPOSIT')
        
    # get into cookiecutter mode
    def toolsCookieCut(self):
        self.glpane.setMode('COOKIE')

    # get into Extrude mode
    def toolsExtrude(self):
        self.glpane.setMode('EXTRUDE')

    # get into Fuse Chunks mode
    def toolsFuseChunks(self):
        self.glpane.setMode('FUSECHUNKS')
            
    def simSetup(self):
        """Creates a movie of a molecular dynamics simulation.
        """
        from runSim import simSetup_CommandRun
        cmdrun = simSetup_CommandRun( self)
        cmdrun.run()
        return

    def simPlot(self):
        """Opens the Plot Tool dialog... for details see subroutine's docstring.
        """
        from PlotTool import simPlot
        dialog = simPlot(self.assy)
        if dialog:
            self.plotcntl = dialog #probably useless, but done since old code did it;
                # conceivably, keeping it matters due to its refcount. [bruce 050327]
        return
    
    def simMoviePlayer(self):
        """Plays a DPB movie file created by the simulator.
        """
        from movieMode import simMoviePlayer
        simMoviePlayer(self.assy)
        return

    def JobManager(self):
        """Opens the Job Manager dialog... for details see subroutine's docstring.
        """
        from JobManager import JobManager
        dialog = JobManager(self)
        if dialog:
            self.jobmgrcntl = dialog #probably useless, but done since old code did it;
                # conceivably, keeping it matters due to its refcount. [bruce 050327]
        return
    
    def serverManager(self):
        """Opens the server manager dialog. """
        from ServerManager import ServerManager
        ServerManager().showDialog()
        
    #### Movie Player Dashboard Slots ############

    #bruce 050413 moved code for movie player dashboard slots into movieMode.py
    

    ###################################
    # Slots for future tools
    ###################################
    
    # get into Revolve mode [bruce 041015]
    def toolsRevolve(self):
        self.glpane.setMode('REVOLVE')
        
    # Mirror Tool
    def toolsMirror(self):
        self.history.message(redmsg("Mirror Tool: Not implemented yet."))
             
    # Mirror Circular Boundary Tool
    def toolsMirrorCircularBoundary(self):
        self.history.message(redmsg("Mirror Circular Boundary Tool: Not implemented yet."))

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
    # Element Selector Slots
    #######################################
    def modifySetElement(self):
        global elementSelectorWin
        #Huaicai 2/24/05: Create a new element selector window each time,  
        #so it will be easier to always start from the same states.
        # Make sure only a single element window is shown
        if elementSelectorWin and elementSelectorWin.isShown():
            return 
        
        elementSelectorWin = elementSelector(self)
        elementSelectorWin.update_dialog(self.Element)
        elementSelectorWin.show()

    def _findGoodLocation(self):
        '''Find ideal location for the MMKit. Should only be called after history, and MMKit
           has been created.'''
        global MMKitWin
        
        hist_geometry = self.history.widget.frameGeometry()
        hist_height = hist_geometry.height()
        
        ### Qt Notes: On X11 system, before show() call, widget doesn't have a frameGeometry()
        #mmk_geometry = MMKitWin.frameGeometry()
        mmk_height = 470#mmk_geometry.height()
        
        ## 26 is an estimate of the bottom toolbar height
        toolbar_height = self.depositAtomDashboard.frameGeometry().height()
        
        status_bar_height = self.statusBar().frameGeometry().height()
        
        y = self.y() + self.geometry().height() - hist_height - mmk_height - toolbar_height - status_bar_height
        if y < 0: y = 0
        x = self.x()
        
        return x, y
        
    
    def modifyMMKit(self):
        '''Open The Molecular Modeling Kit for Build (DEPOSIT) mode.
        '''
        # This should probably be moved elsewhere
        global MMKitWin
        if MMKitWin and MMKitWin.isShown():
            return 
        
        MMKitWin = MMKit(self)
        MMKitWin.update_dialog(self.Element)
        pos = self._findGoodLocation()
        
        ## On Linux, X11 has some problem for window location before it's shown. So a comprise way to do it, 
        ## which will have the flash problem.
        if sys.platform == 'linux2': 
            MMKitWin.show()
            MMKitWin.move(pos[0], pos[1])
        else:
            MMKitWin.move(pos[0], pos[1])
            MMKitWin.show()
            
    
    def closeMMKit(self):
        global MMKitWin
        if MMKitWin and MMKitWin.isShown():
            MMKitWin.hide()
      
        
    def elemChange(self, a0):
        self.Element = eCCBtab1[a0]
        
        try: #bruce 050606
            from depositMode import update_hybridComboBox
            update_hybridComboBox(self)
        except:
            if platform.atom_debug:
                print_compact_traceback( "atom_debug: ignoring exception from update_hybridComboBox: ")
            pass # might never fail, not sure...
        global elementSelectorWin
        if elementSelectorWin and not elementSelectorWin.isHidden():
           elementSelectorWin.update_dialog(self.Element)     
           elementSelectorWin.show()
        # Update the MMKit dialog   
        global MMKitWin
        if MMKitWin and not MMKitWin.isHidden():
           MMKitWin.update_dialog(self.Element)     
           MMKitWin.show()
           
          
    # this routine sets the displays to reflect elt
    # [bruce 041215: most of this should be made a method in elementSelector.py #e]
    def setElement(self, elt):
        # element specified as element number
        global elementSelectorWin
        global MMKitWin
        
        self.Element = elt
        if elementSelectorWin: elementSelectorWin.update_dialog(elt)
        if MMKitWin: MMKitWin.update_dialog(elt)
        line = eCCBtab2[elt]
        self.elemChangeComboBox.setCurrentItem(line) ###k does this send the signal, or not (if not that might cause bug 690)?
        #bruce 050706 fix bug 690 by calling the same slot that elemChangeComboBox.setCurrentItem should have called
        # (not sure in principle that this is always safe or always a complete fix, but it seems to work)
        self.elemFilterComboBox.setCurrentItem(line)
        self.elemChange(line) #k arg is a guess, but seems to work
            # (btw if you use keypress to change to the same element you're in, it *doesn't* reset that element
            #  to its default atomtype (hybridization combobox in build dashboard);
            #  this is due to a special case in update_hybridComboBox;
            #  I'm not sure whether this is good or bad. #k [bruce 050706])
        return

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
        self.glpane.gl_update()

    def dispCsys(self):
        """ Toggle on/off center coordinate axes """
        self.glpane.cSysToggleButton = not self.glpane.cSysToggleButton
        self.glpane.gl_update()

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
        self.history.message(redmsg("Display Datum Lines: Not implemented yet."))

    def dispDatumPlanes(self):
        """ Toggle on/off datum planes """
        self.history.message(redmsg("Display Datum Planes: Not implemented yet."))

    def dispOpenBonds(self):
        """ Toggle on/off open bonds """
        self.history.message(redmsg("Display Open Bonds: Not implemented yet."))
             
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

        return # from loadCursors
    
    def createStatusBars(self):
        """Create some widgets inside the Qt-supplied statusbar, self.statusBar()."""
        # (see also self.history.message())

        # Mark - Set up display mode bar (right) in status bar area.        
        self.dispbarLabel = QLabel(self.statusBar(), "dispbarLabel")
        self.dispbarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        self.statusBar().addWidget(self.dispbarLabel, 0, True)
        
        # Mark - Set up mode bar (right) in status bar area.        
        self.modebarLabel = QLabel(self.statusBar(), "modebarLabel")
        self.modebarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        self.statusBar().addWidget(self.modebarLabel, 0, True)
        return
    
    def hideDashboards(self):
        # [bruce 050408 comment: this list should be recoded somehow so that it
        #  lists what to show, not what to hide. ##e]
        self.cookieCutterDashboard.hide()
        self.extrudeDashboard.hide()
        self.revolveDashboard.hide()
        self.depositAtomDashboard.hide()
        self.datumDispDashboard.hide()  # (mark note: this is the datum display toolbar)
        self.selectMolDashboard.hide()
        self.selectAtomsDashboard.hide()
        self.moveChunksDashboard.hide()
        self.moviePlayerDashboard.hide()
        self.zoomDashboard.hide()
        self.panDashboard.hide()
        self.rotateDashboard.hide()
        self.fuseChunksDashboard.hide()
        self.cookieSelectDashboard.hide()

        # This section used by Mark and David to hide toolbars, etc when creating
        # tutorial videos.        
#        self.helpToolbar.hide()
        
        ##Huaicai 12/08/04, remove unnecessary toolbars from context menu
        objList = self.queryList("QToolBar")
        for obj in objList:
            # [bruce 050408 comment: this is bad style; the default should be setAppropriate False
            #  (to keep most dashboard names out of the context menu in the toolbar area),
            #  and we should list here the few we want to include in that menu (setAppropriate True),
            #  not the many we want to exclude (which is also a list that changes more often). ##e]
            if obj in [self.datumDispDashboard, self.moviePlayerDashboard, self.moveChunksDashboard,
                self.cookieCutterDashboard, self.depositAtomDashboard, self.extrudeDashboard,
                self.selectAtomsDashboard, self.selectMolDashboard, self.zoomDashboard,
                self.panDashboard, self.rotateDashboard, self.fuseChunksDashboard,
                self.cookieSelectDashboard]:
                    self.setAppropriate(obj, False)

    def update_mainwindow_caption(self, Changed=False):
        '''Update the caption at the top of the of the main window. 
        Example:  "nanoENGINEER-1 - [partname.mmp]"
        Changed=True will add the prefix and suffix to the caption denoting the part has been changed.
        '''
        
        if Changed:
            prefix = self.caption_prefix
            suffix = self.caption_suffix + '*'
        else:
            prefix = ''
            suffix = ''
        try:
            junk, basename = os.path.split(self.assy.filename)
            assert basename # it's normal for this to fail, when there is no file yet
            
            if self.caption_fullpath:
                partname = self.assy.filename
            else:
                partname = basename
        
        except:
            partname = 'Untitled'
        
        self.setCaption(self.trUtf8(self.name() + " - " + prefix + "[" + partname + "]" + suffix))
            
    # end of class MWsemantics