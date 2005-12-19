# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
MWsemantics.py provides the main window class, MWsemantics.

$Id$

History: too much to mention, except for breakups of the file.

[maybe some of those are not listed here?]
Huaicai ??? split out cookieMode slots (into separate class)
bruce 050413 split out movieDashboardSlotsMixin
bruce 050907 split out fileSlotsMixin

[Much more splitup of this file is needed. Ideally we would
split up the class MWsemantics (as for cookieMode), not just the file.]

bruce 050913 used env.history in some places; also officially
deprecated any remaining uses of win.history, and print a console
warning whenever they occur.
'''

## bruce 050408 removed: import qt
from qt import QWidget, QFrame, SIGNAL, QFileDialog
    ## bruce 050408 removed: QPushButton, QMainWindow, QPixmap, QGroupBox,
    ## QComboBox, QAction, QMenuBar, QPopupMenu, SLOT, QListView, QListViewItem
from qt import QCursor, QBitmap, QWMatrix, QLabel, QSplitter, QMessageBox, QString, QColorDialog, QColor
from GLPane import GLPane ## bruce 050408 removed: import *
from assembly import assembly ## bruce 050408 added this, was coming from GLPane
from drawer import get_gl_info_string ## grantham 20051201
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

# most of the file format imports are probably no longer needed; I'm removing some of them
# (but we need to check for imports of them from here by other modules) [bruce 050907]
from files_pdb import readpdb, insertpdb, writepdb
from files_gms import readgms, insertgms
from files_mmp import readmmp, insertmmp

from debug import print_compact_traceback

from MainWindowUI import MainWindow
from HistoryWidget import greenmsg, redmsg

from movieMode import movieDashboardSlotsMixin
from ops_files import fileSlotsMixin #bruce 050907
from changes import register_postinit_object
import preferences
import env #bruce 050901 (also moved pre_init_fake_history_widget into env.py)
import undo #bruce 050917

elementSelectorWin = None
elementColorsWin = None
MMKitWin = None
windowList = []

eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]

eCCBtab2 = {}
for i,elno in zip(range(len(eCCBtab1)), eCCBtab1):
    eCCBtab2[elno] = i

recentfiles_use_QSettings = True #bruce 050919 debug flag (replacing use of __debug__) #####@@@@@

class MWsemantics( fileSlotsMixin, movieDashboardSlotsMixin, MainWindow):
    "The single Main Window object."

    #bruce 050413 split out movieDashboardSlotsMixin, which needs to come before MainWindow
    # in the list of superclasses, since MainWindow overrides its methods with "NIM stubs".
    #bruce 050906: same for fileSlotsMixin.
    
    initialised = 0 #bruce 041222
    _ok_to_autosave_geometry_changes = False #bruce 051218

    # This is the location of the separator that gets inserted in the File menu above "Recent Files".
    RECENT_FILES_MENU_INDEX = 10 

    def __init__(self, parent = None, name = None):
    
        global windowList
        
        undo.just_before_mainwindow_super_init()
        
        MainWindow.__init__(self, parent, name, Qt.WDestructiveClose)
            # fyi: this connects 138 or more signals to our slot methods [bruce 050917 comment]

        undo.just_after_mainwindow_super_init()

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
        # (see also env.history.message())
        self.createStatusBars()

        windowList += [self]
        if name == None:
            self.setName("nanoENGINEER-1") # Mark 11-05-2004

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
            #bruce 050911 revised GLPane.__init__ -- now it leaves glpane's mode as nullmode;
            # we change it below, since doing so now would be too early for some modes permitted as startup mode
            # (e.g. Build mode, which when Entered needs self.Element to exist, as of 050911)

        # Some final splitter setup
        splitter.setResizeMode(self.modelTreeView, QSplitter.KeepSize)
        splitter.setOpaqueResize(False)

        # Create the history area at the bottom
        from HistoryWidget import HistoryWidget
        histfile = platform.make_history_filename()
        #bruce 050913 renamed self.history to self.history_object, and deprecated direct access
        # to self.history; code should use env.history to emit messages, self.history_widget
        # to see the history widget, or self.history_object to see its owning object per se
        # rather than as a place to emit messages (this is rarely needed).
        self.history_object = HistoryWidget(vsplitter, filename = histfile, mkdirs = 1)
            # this is not a Qt widget, but its owner;
            # use self.history_widget for Qt calls that need the widget itself.
        self.history_widget = self.history_object.widget
            #bruce 050913, in case future code splits history widget (as main window subwidget)
            # from history message recipient (the global object env.history).
        
        env.history = self.history_object #bruce 050727, revised 050913

        # ... and some final vsplitter setup [bruce 041223]
        vsplitter.setResizeMode(self.history_widget, QSplitter.KeepSize)
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

        # Enable/disable plugins.  These should be moved to a central method
        # where all plug-ins get added and enabled during invocation.  Mark 050921.
        self.uprefs.enable_nanohive(env.prefs[nanohive_enabled_prefs_key])
        self.uprefs.enable_gamess(env.prefs[gamess_enabled_prefs_key])
        
        #Huaicai 9/14/05: Initialization for the 'Recently opened files' feature
        from qt import QSettings
        menuIndex = self.RECENT_FILES_MENU_INDEX
        if recentfiles_use_QSettings:
            prefsSetting = QSettings()
        else:
            prefsSetting = preferences.prefs_context()
        popupMenu = QPopupMenu(self)        
        self.fileMenu.insertItem(qApp.translate("Main Window", "Recent Files", None), popupMenu, menuIndex, menuIndex)
        
        if recentfiles_use_QSettings:
            fileList = prefsSetting.readListEntry('/Nanorex/nE-1/recentFiles')[0]
        else:
            fileList = prefsSetting.get('/Nanorex/nE-1/recentFiles', [])
        if len(fileList): 
            self.fileMenu.setItemEnabled(menuIndex, True)
            self._createRecentFilesList()
        else:
            self.fileMenu.setItemEnabled(menuIndex, False)


        # Create the Help dialog.
        # Mark 050812
        from help import Help
        self.help = Help()

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
        from whatsthis import createWhatsThis, fix_whatsthis_text_for_mac
        createWhatsThis(self)
        
        # IMPORTANT: All widget creation (i.e. dashboards, dialogs, etc.) and their 
        # whatthis text should be created before this line.
        fix_whatsthis_text_for_mac(self) # Fixes bug 1136.  Mark 051126.

        # Start with Carbon as the default element (for Deposit Mode
        # and the Element Selector)
        self.Element = 6
        self.setElement(6)
        
        # 'depositState' is used by depositMode and MMKit to synchonize the 
        # depositMode dashboard (Deposit and Paste toggle buttons) and the MMKit pages (tabs).
        # It is also used to determine what type of object (atom, clipboard chunk or library part)
        # to deposit when pressing the left mouse button in Build mode.
        #
        # depositState can be either:
        #   'Atoms' - deposit an atom based on the current atom type selected in the MMKit 'Atoms'
        #           page or dashboard atom type combobox(es).
        #   'Clipboard' - deposit a chunk from the clipboard based on what is currently selected in
        #           the MMKit 'Clipboard' page or dashboard clipboard/paste combobox.
        #   'Library' - deposit a part from the library based on what is currently selected in the
        #           MMKit 'Library' page.  There is no dashboard option for this.
        self.depositState = 'Atoms'
        
        self.assy.reset_changed() #bruce 050429, part of fixing bug 413
        
        # Movie Player Flag.  Mark 051209.
        # 'movie_is_playing' is a flag that indicates a movie is playing. It is used by other code to
        # speed up rendering times by disabling the (re)building of display lists for each frame
        # of the movie.
        self.movie_is_playing = False

        #bruce 050810 replaced user preference initialization with this, and revised update_mainwindow_caption to match
        from changes import Formula
        self._caption_formula = Formula(
            # this should depend on whatever update_mainwindow_caption_properly depends on;
            # but it can't yet depend on assy.has_changed(),
            # so that calls update_mainwindow_caption_properly (or the equiv) directly.
            lambda: (env.prefs[captionPrefix_prefs_key],
                     env.prefs[captionSuffix_prefs_key],
                     env.prefs[captionFullPath_prefs_key]),
            self.update_mainwindow_caption_properly
        )
        
        #bruce 050810 part of QToolButton Tiger bug workaround
        # [intentionally called on all systems,
        #  though it will only do anything on Macs except during debugging]
        if 1:
            from debug import auto_enable_MacOSX_Tiger_workaround_if_desired
            auto_enable_MacOSX_Tiger_workaround_if_desired( self)

        self.initialised = 1 # enables win_update

        # be told to add new Jigs menu items, now or as they become available [bruce 050504]
        register_postinit_object( "Jigs menu items", self )

        return # from MWsemantics.__init__


    def startRun(self):
        '''After the main window(its size and location) has been setup, begin to run the program from this method. 
        [Huaicai 11/1/05: try to fix the initial MMKitWin off screen problem by splitting from the __init__() method'''
        
        self.glpane.start_using_mode( '$STARTUP_MODE') #bruce 050911
            # (no longer done in GLPane.__init__, which used a hardcoded default mode)
        
        self.win_update() # bruce 041222

        undo.just_before_mainwindow_init_returns()
    
    
    def __getattr__(self, attr): #bruce 050913 report deprecated uses of win.history
        if attr == 'history':
            print_compact_traceback("deprecated code warning: win.history should be env.history: ")
            return env.history
        raise AttributeError, attr
    
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
        self.history_object.h_update() #bruce 050104
            # this is self.history_object, not env.history,
            # since it's really about this window's widget-owner,
            # not about the place to print history messages [bruce 050913]
        

    ###################################
    # File Toolbar Slots 
    ###################################

    # file toolbar slots are inherited from fileSlotsMixin (in ops_files.py) as of bruce 050907.
    # Notes:
    #   #e closeEvent method (moved to fileSlotsMixin) should be split in two
    # and the outer part moved back into this file.
    #   __clear method was moved to fileSlotsMixin (as it should be), even though
    # its name-mangled name thereby changed, and some comments in other code
    # still refer to it as MWsemantics.__clear. It should be given an ordinary name.

    
    ###################################
    # Edit Toolbar Slots
    ###################################

    def editUndo(self):
        env.history.message(redmsg("Undo: Not implemented yet."))

    def editRedo(self):
        env.history.message(redmsg("Redo: Not implemented yet."))

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
            env.history.message(greenmsg("Paste:"))
            self.glpane.setMode('DEPOSIT')
            global MMKitWin
            if MMKitWin: MMKitWin.change2ClipboardPage() # Fixed bug 1230.  Mark 051219.
            
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
        env.history.message(cmd + info)
        self.glpane.setViewHome()

    def setViewFitToWindow(self):
        """ Fit to Window """
        cmd = greenmsg("Fit to Window: ")
        info = ''
        env.history.message(cmd + info)
        self.glpane.setViewFitToWindow()
            
    def setViewHomeToCurrent(self): #bruce 050418 revised docstring, and moved bodies of View methods into GLPane
        """Changes Home view of the model to the current view in the glpane."""
        cmd = greenmsg("Set Home View to Current View: ")
        info = 'Home'
        env.history.message(cmd + info)
        self.glpane.setViewHomeToCurrent()
            
    def setViewRecenter(self):
        """Recenter the view around the origin of modeling space.
        """
        cmd = greenmsg("Recenter View: ")
        info = 'View Recentered'
        env.history.message(cmd + info)
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
            self.glpane.prevModeGradient = self.glpane.mode.backgroundGradient

        self.glpane.setMode('ZOOM')
        
        # This should be placed in zoomMode.Enter or init_gui, but it always appears 
        # before the green "Entering Mode: Zoom" msg.  So I put it here.  Mark 050130
        env.history.message("You may hit the Esc key to exit Zoom Tool.")

    def panTool(self):
        """Pan Tool allows X-Y panning using the left mouse button.
        """
        # we never want these modes (ZOOM, PAN, ROTATE) to be assigned to "prevMode". 
        if self.glpane.mode.modename not in ['ZOOM', 'PAN', 'ROTATE']:
            self.glpane.prevMode = self.glpane.mode.modename
            self.glpane.prevModeColor = self.glpane.mode.backgroundColor
            self.glpane.prevModeGradient = self.glpane.mode.backgroundGradient

        self.glpane.setMode('PAN')
        env.history.message("You may hit the Esc key to exit Pan Tool.")

    def rotateTool(self):
        """Rotate Tool allows free rotation using the left mouse button.
        """
        # we never want these modes (ZOOM, PAN, ROTATE) to be assigned to "prevMode". 
        if self.glpane.mode.modename not in ['ZOOM', 'PAN', 'ROTATE']:
            self.glpane.prevMode = self.glpane.mode.modename
            self.glpane.prevModeColor = self.glpane.mode.backgroundColor
            self.glpane.prevModeGradient = self.glpane.mode.backgroundGradient

        self.glpane.setMode('ROTATE')
        env.history.message("You may hit the Esc key to exit Rotate Tool.")
                
    # GLPane.ortho is checked in GLPane.paintGL
    def setViewOrtho(self):
        self.glpane.setViewProjection(ORTHOGRAPHIC)

    def setViewPerspec(self):
        self.glpane.setViewProjection(PERSPECTIVE)

    def setViewOpposite(self):
        '''Set view to the opposite of current view. '''
        cmd = greenmsg("Opposite View: ")
        info = 'Current view opposite to the previous view'
        env.history.message(cmd + info)
        self.glpane.rotateView(self.glpane.quat + Q(V(0,1,0), pi))
  
    def setViewPlus90(self): # Added by Mark. 051013.
        '''Increment the current view by 90 degrees around the vertical axis. '''
        cmd = greenmsg("Rotate View +90 : ")
        info = 'View incremented by 90 degrees'
        env.history.message(cmd + info)
        self.glpane.rotateView(self.glpane.quat + Q(V(0,1,0), pi/2))
        
    def setViewMinus90(self): # Added by Mark. 051013.
        '''Decrement the current view by 90 degrees around the vertical axis. '''
        cmd = greenmsg("Rotate View -90 : ")
        info = 'View decremented by 90 degrees'
        env.history.message(cmd + info)
        self.glpane.rotateView(self.glpane.quat + Q(V(0,1,0), -pi/2))

    def setViewBack(self):
        cmd = greenmsg("Back View: ")
        info = 'Current view is Back View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(0,1,0),pi))

    def setViewBottom(self):
        cmd = greenmsg("Bottom View: ")
        info = 'Current view is Bottom View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(1,0,0),-pi/2))

    def setViewFront(self):
        cmd = greenmsg("Front View: ")
        info = 'Current view is Front View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(1,0,0,0))

    def setViewLeft(self):
        cmd = greenmsg("Left View: ")
        info = 'Current view is Left View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(0,1,0),pi/2))

    def setViewRight(self):
        cmd = greenmsg("Right View: ")
        info = 'Current view is Right View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(0,1,0),-pi/2))

    def setViewTop(self):
        cmd = greenmsg("Top View: ")
        info = 'Current view is Top View'
        env.history.message(cmd + info)

        self.glpane.rotateView(Q(V(1,0,0),pi/2))
        
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
            env.history.message(redmsg("Set Chunk Color: No chunks selected.")) #bruce 050505 added this message
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
            env.history.message(redmsg("Reset Chunk Color: No chunks selected."))
            return
        
        for chunk in self.assy.selmols:
            chunk.setcolor(None)
        self.glpane.gl_update()
        
    def dispResetAtomsDisplay(self):
        "Resets the display setting for each atom in the selected chunks to Default display mode"
        if not self.assy.selmols: 
            env.history.message(redmsg("Reset Atoms Display: No chunks selected."))
            return
            
        self.assy.resetAtomsDisplay()
        env.history.message(greenmsg("Reset Atoms Display:"))
        msg = "Display setting for all atoms in selected chunk(s) reset to Default."
        env.history.message(msg)

        
    def dispShowInvisAtoms(self):
        "Resets the display setting for each invisible atom in the selected chunks to Default display mode"
        if not self.assy.selmols: 
            env.history.message(redmsg("Show Invisible Atoms: No chunks selected."))
            return
            
        nia = self.assy.showInvisibleAtoms() # nia = Number of Invisible Atoms
        env.history.message(greenmsg("Show Invisible Atoms:"))
        msg = str(nia) + " invisible atoms found."
        env.history.message(msg)
                    
    def dispBGColor(self):
        "Let user change the current mode's background color"
        # Fixed bug 894.  Mark
        # Changed "Background" to "Modes". Mark 050911.
        self.uprefs.showDialog(pagename='Modes')
    
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
        # Sync the thumbview bg color with the current mode's bg color.  Mark 051216.
        elementColorsWin.elemGLPane.change_bg_color(
            self.glpane.mode.backgroundColor, 
            self.glpane.mode.backgroundGradient
            )
        elementColorsWin.show()

    def dispLighting(self):
        """Allows user to change lighting brightness.
        """
        self.uprefs.showDialog('Lighting') # Show Prefences | Lighting.

        # env.history.message(greenmsg("Lighting:")) # Not needed IMHO. Mark 051124.
        
        # Original Lighting Tool.  Keeping this here in case we want
        # to play with/test ambient and diffuse parameters.  Mark 051124.
        #from LightingTool import LightingTool
        #self.lightcntl = LightingTool(self.glpane) # Open Lighting Tool dialog
        
    ###############################################################
    # Select Toolbar Slots
    ###############################################################

    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        """
        env.history.message(greenmsg("Select All:"))
        self.assy.selectAll()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectNone(self):
        env.history.message(greenmsg("Select None:"))
        self.assy.selectNone()
        self.update_mode_status() # bruce 040927... not sure if this is ever needed

    def selectInvert(self):
        """If some parts are selected, select the other parts instead.
        If some atoms are selected, select the other atoms instead
        (even in chunks with no atoms selected, which end up with
        all atoms selected). (And unselect all currently selected
        parts or atoms.)
        """
        #env.history.message(greenmsg("Invert Selection:"))
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

    def selectExpand(self):
        """Slot for Expand Selection, which selects any atom that is bonded 
        to any currently selected atom.
        """
        self.assy.selectExpand()
        
    def selectContract(self):
        """Slot for Contract Selection, which unselects any atom which has
        a bond to an unselected atom, or which has any open bonds.
        """
        self.assy.selectContract()
        
    ###################################
    # Jig Toolbar Slots
    ###################################

    def makeGamess(self):
        self.assy.makegamess()
        
    def makeAnchor(self): # Changed name from makeGround. Mark 051104.
        self.assy.makeAnchor()
        
    def makeStat(self):
        self.assy.makestat()

    def makeThermo(self):
        self.assy.makethermo()
        
    def makeMotor(self):
        self.assy.makeRotaryMotor(self.glpane.lineOfSight)

    def makeLinearMotor(self):
        self.assy.makeLinearMotor(self.glpane.lineOfSight)
        
    def makeGridPlane(self):
        self.assy.makeGridPlane()

    def makeESPWindow(self):
        self.assy.makeESPWindow()
        
    def makeAtomSet(self):
        self.assy.makeAtomSet()
        
    def makeMeasureDistance(self):
        self.assy.makeMeasureDistance()
        
    def makeMeasureAngle(self):
        self.assy.makeMeasureAngle()
        
    def makeMeasureDihedral(self):
        self.assy.makeMeasureDihedral()

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
        """ Align selected chunks to the computed axis of the first chunk by rotating them """
        self.assy.align()
        self.win_update()
        
    def modifyCenterCommonAxis(self):
        '''Same as "Align to Common Axis", except that it moves all the selected chunks to the 
        center of the first selected chunk after aligning/rotating the other chunks
        '''

        # This is still not fully implemented as intended.  Instead of moving all the selected 
        # chunks to the center of the first selected chunk, I want to have them moved to the closest 
        # (perpendicular) point of the first chunk's axis.  I've studied and understand the math involved; 
        # I just need to implement the code.  I plan to ask Bruce for help since the two of us will get it 
        # done much more quickly together than me doing it alone.
        # Mark 050829.

        self.assy.alignmove()
        self.win_update()
        
    ###################################
    # Help Toolbar Slots
    ###################################
    
    def helpMouseControls(self):
        self.help.showDialog(0)
        
    def helpKeyboardShortcuts(self):
        self.help.showDialog(1)
    
    def helpGraphicsCard(self):
        '''Displays details about the system's graphics card.
        '''
        # This is for Brad to complete.  Mark 051123.
        ginfo = get_gl_info_string()
        
        from widgets import TextMessageBox
        msgbox = TextMessageBox(self)
        msgbox.setCaption("Graphics Card Info")
        msgbox.setText(ginfo)
        msgbox.show()

# I modified a copy of cpuinfo.py from 
# http://cvs.sourceforge.net/viewcvs.py/numpy/Numeric3/scipy/distutils/
# thinking it might help us support users better if we had a built-in utility
# for interrogating the CPU.  I do not plan to commit cpuinfo.py until I speak
# to Bruce about this. Mark 051209.
# 
#    def helpCpuInfo(self):
#        '''Displays this system's CPU information.
#        '''
#        from cpuinfo import get_cpuinfo
#        cpuinfo = get_cpuinfo()
#        
#        from widgets import TextMessageBox
#        msgbox = TextMessageBox(self)
#        msgbox.setCaption("CPU Info")
#        msgbox.setText(cpuinfo)
#        msgbox.show()
              
    def helpAbout(self):
        """Displays information about this version of nanoENGINEER-1
        """
        from version import Version
        v = Version()
        product = v.product
        versionString = repr(v) + (" (%s)" % v.releaseType)
        date = "Release Date: " + v.releaseDate
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        installdir = "Running from: " + filePath
        techsupport = "For technical support, send email to support@nanorex.com"
        website = "Website: www.nanoengineer-1.com"
        aboutstr = product + " " + versionString \
                       + "\n\n" \
                       + date \
                       + "\n\n" \
                       + installdir \
                       + "\n\n" \
                       + v.copyright \
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
        self.depositState = 'Atoms'
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

    def simNanoHive(self):
        """Opens the Nano-Hive dialog... for details see subroutine's docstring.
        """
        # This should be probably be modeled after the simSetup_CommandRun class
        # I'll do this if Bruce agrees.  For now, I want to get this working ASAP.
        # Mark 050915.
        self.nanohive.showDialog(self.assy)

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
                # conceivably, keeping it matters due to its refcount.  See Bruce's note in simPlot().
        return
    
    def serverManager(self):
        """Opens the server manager dialog. """
        from ServerManager import ServerManager
        ServerManager().showDialog()
        
    def insertNanotube(self):
        from NanotubeGenerator import NanotubeGenerator
        NanotubeGenerator(self).show()

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
        env.history.message(redmsg("Mirror Tool: Not implemented yet."))
             
    # Mirror Circular Boundary Tool
    def toolsMirrorCircularBoundary(self):
        env.history.message(redmsg("Mirror Circular Boundary Tool: Not implemented yet."))

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
        '''Creates the Element Selector for Select Atoms mode.
        '''
        global elementSelectorWin
        #Huaicai 2/24/05: Create a new element selector window each time,  
        #so it will be easier to always start from the same states.
        # Make sure only a single element window is shown
        if elementSelectorWin and elementSelectorWin.isShown():
            return 
        
        elementSelectorWin = elementSelector(self)
        elementSelectorWin.update_dialog(self.Element)
        elementSelectorWin.show()

    def _findGoodLocation(self, firstShow):
        '''Find ideal location for the MMKit. Should only be called after history, and MMKit
           has been created.'''
        global MMKitWin
        
        if sys.platform == 'linux2': 
            hist_height = 70
            mmk_height = 559
            toolbar_height = 25
            status_bar_height = 29
        else:
            hist_geometry = self.history_widget.frameGeometry()
            hist_height = hist_geometry.height()
            
            ### Qt Notes: On X11 system, before show() call, widget doesn't have a frameGeometry()
            
            mmk_geometry = MMKitWin.frameGeometry()
            mmk_height = mmk_geometry.height()
                        
            ## 26 is an estimate of the bottom toolbar height
            toolbar_height = self.depositAtomDashboard.frameGeometry().height()
            
            status_bar_height = self.statusBar().frameGeometry().height()
            
        y = self.geometry().y()-2 + self.geometry().height() - hist_height - mmk_height - toolbar_height - status_bar_height
        if firstShow: y -= 10
        if y < 0: y = 0
        x = self.geometry().x()
        
        return x, y
        
    
    def modifyMMKit(self):
        '''Open The Molecular Modeling Kit for Build (DEPOSIT) mode.
        '''
        # This should probably be moved elsewhere
        global MMKitWin
        if MMKitWin and MMKitWin.isShown():
            return MMKitWin

        # It's very important to add the following condition, so only a single instance
        # of the MMKit has been created and used. This is to fix bug 934, which is kind
        # of hard to find. [Huaicai 9/2/05]
        firstShow = False
        if not MMKitWin:
            firstShow = True
            MMKitWin = MMKit(self)
       
        pos = self._findGoodLocation(firstShow)
        
        ## On Linux, X11 has some problem for window location before it's shown. So a compromised way to do it, 
        ## which will have the flash problem.
        MMKitWin.update_dialog(self.Element)
        
        if sys.platform == 'linux2': 
            MMKitWin.show()
            MMKitWin.move(pos[0], pos[1])
        else:
            MMKitWin.move(pos[0], pos[1])
            MMKitWin.show()
        return MMKitWin
    
    def MMKitShowPage(self, pagename):
        '''Shows page 'pagename' in the MMKit. 
        pagename can be "Atoms", "Clipboard" or "Library".
        '''
        global MMKitWin
        if MMKitWin:
            MMKitWin.setup_current_page(pagename)

    def deleteMMKit(self):
        '''Deletes the MMKit.
        '''
        global MMKitWin
        if MMKitWin:
            MMKitWin = None
            self.depositState = 'Atoms' # reset so next time MMKit is created it will open to Atoms page

    def transmuteElementChanged(self, a0):
        '''Slot method, called when user changes the items in the <Transmute to> comboBox of selectAtom Dashboard.
           I put it here instead of the more relevant selectMode.py is because selectMode is not of 
           QObject, so it doesn't support signal/slots. --Huaicai '''
        self.glpane.mode.update_hybridComboBox(self)
            
        
    def elemChange(self, a0):
        '''Slot for Element selector combobox in Build mode's dashboard.
        '''
        self.Element = eCCBtab1[a0]
        
        try: #bruce 050606
            from depositMode import update_hybridComboBox
            update_hybridComboBox(self)
        except:
            if platform.atom_debug:
                print_compact_traceback( "atom_debug: ignoring exception from update_hybridComboBox: ")
            pass # might never fail, not sure...
        
        #[Huaicai 9/6/05: The element selector feature is obsolete.
        #global elementSelectorWin
        #if elementSelectorWin and not elementSelectorWin.isHidden():
        #   elementSelectorWin.update_dialog(self.Element)     
        #   elementSelectorWin.show()
        
        global MMKitWin
        if MMKitWin and not MMKitWin.isHidden():
           self.depositState = 'Atoms'
           MMKitWin.update_dialog(self.Element)     
           MMKitWin.show()
           
          
    # this routine sets the displays to reflect elt
    # [bruce 041215: most of this should be made a method in elementSelector.py #e]
    def setElement(self, elt):
        # element specified as element number
        global elementSelectorWin
        global MMKitWin
        
        self.Element = elt

        #Huaicai: These are redundant since the elemChange() will do all of them. 8/10/05
        #if elementSelectorWin: elementSelectorWin.update_dialog(elt)
        #if MMKitWin: MMKitWin.update_dialog(elt)
        
        line = eCCBtab2[elt]
        self.elemChangeComboBox.setCurrentItem(line) ###k does this send the signal, or not (if not that might cause bug 690)?
        #bruce 050706 fix bug 690 by calling the same slot that elemChangeComboBox.setCurrentItem should have called
        # (not sure in principle that this is always safe or always a complete fix, but it seems to work)
        
        # Huaicai 8/10/05: remove the synchronization.
        #self.elemFilterComboBox.setCurrentItem(line)
        
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
        env.history.message(redmsg("Display Datum Lines: Not implemented yet."))

    def dispDatumPlanes(self):
        """ Toggle on/off datum planes """
        env.history.message(redmsg("Display Datum Planes: Not implemented yet."))

    def dispOpenBonds(self):
        """ Toggle on/off open bonds """
        env.history.message(redmsg("Display Open Bonds: Not implemented yet."))
             
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
        
        # Create "DeleteCursor" cursor
        self.DeleteCursor = QCursor(
            QBitmap(filePath + "/../images/DeleteCursor.bmp"),
            QBitmap(filePath + "/../images/DeleteCursor-bm.bmp"),
            0, 0)
            
        # Create "ZoomCursor" cursor
        self.ZoomCursor = QCursor(
            QBitmap(filePath + "/../images/ZoomCursor.bmp"),
            QBitmap(filePath + "/../images/ZoomCursor-bm.bmp"),
            10, 10)

        return # from loadCursors
    
    def createStatusBars(self):
        """Create some widgets inside the Qt-supplied statusbar, self.statusBar()."""
        # (see also env.history.message())

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
            
    def enableViews(self, enableFlag=True):
        '''Disables/enables view actions on toolbar and menu.
        '''
        self.setViewFrontAction.setEnabled(enableFlag)
        self.setViewBackAction.setEnabled(enableFlag)
        self.setViewTopAction.setEnabled(enableFlag)
        self.setViewBottomAction.setEnabled(enableFlag)
        self.setViewLeftAction.setEnabled(enableFlag)
        self.setViewRightAction.setEnabled(enableFlag)
        
        self.setViewHomeAction.setEnabled(enableFlag)
        self.setViewFitToWindowAction.setEnabled(enableFlag)
        self.setViewRecenterAction.setEnabled(enableFlag)
        
        self.setViewOppositeAction.setEnabled(enableFlag)
        self.setViewPlus90Action.setEnabled(enableFlag)
        self.setViewMinus90Action.setEnabled(enableFlag)

# == Caption methods

    def update_mainwindow_caption_properly(self, junk = None): #bruce 050810 added this
        self.update_mainwindow_caption(self.assy.has_changed())

    def update_mainwindow_caption(self, Changed=False): #by mark; bruce 050810 revised this in several ways, fixed bug 785
        '''Update the caption at the top of the of the main window. 
        Example:  "nanoENGINEER-1 - [partname.mmp]"
        Changed=True will add the prefix and suffix to the caption denoting the part has been changed.
        '''
        caption_prefix = env.prefs[captionPrefix_prefs_key]
        caption_suffix = env.prefs[captionSuffix_prefs_key]
        caption_fullpath = env.prefs[captionFullPath_prefs_key]
        
        if Changed:
            prefix = caption_prefix
            suffix = caption_suffix
        else:
            prefix = ''
            suffix = ''

        # this is not needed here since it's already done in the prefs values themselves when we set them:
        # if prefix and not prefix.endswith(" "):
        #     prefix = prefix + " "
        # if suffix and not suffix.startswith(" "):
        #     suffix = " " + suffix
        
        try:
            junk, basename = os.path.split(self.assy.filename)
            assert basename # it's normal for this to fail, when there is no file yet
            
            if caption_fullpath:
                partname = self.assy.filename
            else:
                partname = basename
        
        except:
            partname = 'Untitled'

        ##e [bruce 050811 comment:] perhaps we should move prefix to the beginning, rather than just before "[";
        # and in any case the other stuff here, self.name() + " - " + "[" + "]", should also be user-changeable, IMHO.
        self.setCaption(self.trUtf8(self.name() + " - " + prefix + "[" + partname + "]" + suffix))
        return
    
    pass # end of class MWsemantics

# end
