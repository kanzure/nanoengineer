# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
MWsemantics.py provides the main window class, MWsemantics.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History: too much to mention, except for breakups of the file.

[maybe some of those are not listed here?]
bruce 050413 split out movieDashboardSlotsMixin
bruce 050907 split out fileSlotsMixin
mark 060120 split out viewSlotsMixin
mark 2008-02-02 split out displaySlotsMixin

[Much more splitup of this file is needed. Ideally we would
split up the class MWsemantics (as for BuildCrystal_Command), not just the file.]

[some of that splitup has been done, now, by Ninad in the Qt4 branch]
"""

from utilities.qt4transition import qt4warning

from PyQt4 import QtGui, QtCore

from PyQt4.Qt import Qt
from PyQt4.Qt import QFont
from PyQt4.Qt import QMenu
from PyQt4.Qt import QSettings
from PyQt4.Qt import QVariant

from PyQt4.Qt import QMainWindow, SIGNAL
from PyQt4.Qt import QMessageBox
from PyQt4.Qt import QToolBar
from PyQt4.Qt import QStatusBar

from model.elements import PeriodicTable
from model.assembly import Assembly
from graphics.drawing.gl_lighting import get_gl_info_string ## grantham 20051201
import os, sys
import time

from utilities import debug_flags

from platform_dependent.PlatformDependent import find_or_make_Nanorex_directory
from platform_dependent.PlatformDependent import open_file_in_editor
from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir

from ne1_ui.ViewOrientationWindow import ViewOrientationWindow # Ninad 061121

from utilities.debug import print_compact_traceback
from utilities.debug_prefs import debug_pref, Choice_boolean_False
from utilities.constants import str_or_unicode
from utilities.constants import RECENTFILES_QSETTINGS_KEY

from ne1_ui.Ui_MainWindow import Ui_MainWindow
from ne1_ui.Ui_PartWindow import Ui_PartWindow

from utilities.Log import greenmsg, redmsg, orangemsg

from operations.ops_files import fileSlotsMixin
from operations.ops_view import viewSlotsMixin
from operations.ops_display import displaySlotsMixin
from operations.ops_modify import modifySlotsMixin
from operations.ops_select import renameableLeafNode

from foundation.changes import register_postinit_object
import foundation.preferences as preferences
import foundation.env as env
import foundation.undo_internals as undo_internals

from commandSequencer.CommandSequencer import CommandSequencer

from operations.ops_select import objectSelected
from operations.ops_select import ATOMS

from widgets.widget_helpers import TextMessageBox
from widgets.simple_dialogs import grab_text_line_using_dialog

from utilities.prefs_constants import qutemol_enabled_prefs_key
from utilities.prefs_constants import nanohive_enabled_prefs_key
from utilities.prefs_constants import povray_enabled_prefs_key
from utilities.prefs_constants import megapov_enabled_prefs_key
from utilities.prefs_constants import povdir_enabled_prefs_key
from utilities.prefs_constants import gamess_enabled_prefs_key
from utilities.prefs_constants import gromacs_enabled_prefs_key
from utilities.prefs_constants import cpp_enabled_prefs_key
from utilities.prefs_constants import rosetta_enabled_prefs_key
from utilities.prefs_constants import rosetta_database_enabled_prefs_key
from utilities.prefs_constants import nv1_enabled_prefs_key
from utilities.prefs_constants import workingDirectory_prefs_key
from utilities.prefs_constants import getDefaultWorkingDirectory
from utilities.prefs_constants import rememberWinPosSize_prefs_key
from utilities.prefs_constants import captionPrefix_prefs_key
from utilities.prefs_constants import captionSuffix_prefs_key
from utilities.prefs_constants import captionFullPath_prefs_key
from utilities.prefs_constants import displayRulers_prefs_key
from utilities.prefs_constants import mouseWheelDirection_prefs_key
from utilities.prefs_constants import zoomInAboutScreenCenter_prefs_key
from utilities.prefs_constants import zoomOutAboutScreenCenter_prefs_key

eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]

eCCBtab2 = {}
for i, elno in zip(range(len(eCCBtab1)), eCCBtab1):
    eCCBtab2[elno] = i

# Debugging for "Open Recent Files" menu. Mark 2007-12-28
debug_recent_files = False  # Do not commit with True
recentfiles_use_QSettings = True # bruce 050919 debug flag

if debug_recent_files:
    def debug_fileList(fileList):
        print "BEGIN fileList"
        for x in fileList:
            print x
        print "END fileList"
else:
    def debug_fileList(fileList):
        pass


# #######################################################################

class MWsemantics(QMainWindow,
                  fileSlotsMixin,
                  viewSlotsMixin,
                  displaySlotsMixin,
                  modifySlotsMixin,
                  Ui_MainWindow,
                  object):
    """
    The single Main Window object.
    """
    #bruce 071008 added object superclass

    # bruce 050413 fileSlotsMixin needs to come before MainWindow in the list
    # of superclasses, since MainWindow overrides its methods with "NIM stubs".
    # mark 060120: same for viewSlotsMixin.

    initialised = 0 #bruce 041222
    _ok_to_autosave_geometry_changes = False #bruce 051218

    # The default font for the main window. If I try to set defaultFont using QApplition.font() here,
    # it returns Helvetica pt12 (?), so setting it below in the constructor is a workaround.
    # Mark 2007-05-27.
    defaultFont = None

    def __init__(self, parent = None, name = None):

        assert isinstance(self, object) #bruce 071008

        self._init_part_two_done = False
        self._activepw = None
        
        self.commandToolbar = None

        self.orientationWindow = None


        self._dnaSequenceEditor = None  #see self.createSequenceEditrIfNeeded
                                    #for details
                                    
        self._proteinSequenceEditor = None
       
        # These boolean flags, if True, stop the execution of slot
        # methods that are called because the state of 'self.viewFullScreenAction
        # or self.viewSemiFullScreenAction is changed. Maybe there is a way to
        # do this using QActionGroup (which make the actions mutually exclusive)
        #.. tried that but it didn't work. After doing this when I tried to
        #  toggle the checked action in the action group, it didn't work
        #..will try it again sometime in future. The following flags are good
        # enough for now. See methods self.showFullScreen and
        # self.showSemiFullScreen where they are used. -- Ninad 2007-12-06
        self._block_viewFullScreenAction_event = False
        self._block_viewSemiFullScreenAction_event = False

        # The following maintains a list of all widgets that are hidden during
        # the FullScreen or semiFullScreen mode. This list is then used in
        # self.showNormal to show the hidden widgets if any. The list is cleared
        # at the end of self.showNormal
        self._widgetToHideDuringFullScreenMode = []

        undo_internals.just_before_mainwindow_super_init()

        qt4warning('MainWindow.__init__(self, parent, name, Qt.WDestructiveClose) - what is destructive close?')
        QMainWindow.__init__(self, parent)

        self.defaultFont = QFont(self.font()) # Makes copy of app's default font.

        # Setup the NE1 graphical user interface.
        self.setupUi() # Ui_MainWindow.setupUi()

        undo_internals.just_after_mainwindow_super_init()

        # bruce 050104 moved this here so it can be used earlier
        # (it might need to be moved into main.py at some point)
        self.tmpFilePath = find_or_make_Nanorex_directory()

        
        # Load all NE1 custom cursors.
        from ne1_ui.cursors import loadCursors
        loadCursors(self)

        # Set the main window environment variable. This sets a single
        # global variable to self. All uses of it need review (and revision)
        # to add support for MDI. Mark 2008-01-02.
        env.setMainWindow(self)

        # Start NE1 with an empty document called "Untitled".
        # See also the _make_and_init_assy method in our mixin class in
        # ops_files.py, which creates and inits an assy using the same method.
        #
        # Note: It is very desirable to change this startup behavior so that
        # the user must select "File > New" to open an empty document after
        # NE1 starts. Mark 2007-12-30.
        self.assy = self._make_a_main_assy()
        
        #bruce 050429: as part of fixing bug 413, it's now required to call
        # self.assy.reset_changed() sometime in this method; it's called below.

        pw = Ui_PartWindow(self.assy, self) # note: calls glpane.setAssy inside GLPane.__init__; that calls _reinit_modes
        self.assy.set_glpane(pw.glpane) # sets assy.o and assy.glpane
        self.assy.set_modelTree(pw.modelTree) # sets assy.mt
        self._activepw = pw
        # Note: nothing in this class can set self._activepw (except to None),
        # which one might guess means that no code yet switches between partwindows,
        # but GLPane.makeCurrent *does* set self._activepw to its .partWindow
        # (initialized to its parent arg when it's created), so that conclusion is not clear.
        # [bruce 070503 comment]

        # Set the caption to the name of the current (default) part - Mark [2004-10-11]
        self.update_mainwindow_caption()

        # This is only used by the Atom Color preference dialog, not the
        # molecular modeling kit in Build Atom (deposit mode), etc.
        start_element = 6 # Carbon
        self.Element = start_element

        # Attr/list for Atom Selection Filter. mark 060401
        # These should become attrs of the assy. mark 2008-01-02.
        self.filtered_elements = [] # Holds list of elements to be selected when the Atom Selection Filter is enabled.
        self.filtered_elements.append(PeriodicTable.getElement(start_element)) # Carbon
        self.selection_filter_enabled = False # Set to True to enable the Atom Selection Filter.

        # Enables the QWorkspace widget which provides Multiple Document
        # Interface (MDI) support for NE1 and adds the Part Window to it.
        # If not enabled, just add the Part Window widget to the
        # centralAreaVBoxLayout only (the default).
        if debug_pref("Enable QWorkspace for MDI support? (next session)",
                      Choice_boolean_False,
                      ## non_debug = True,
                      #bruce 080416 hid this, since MDI is not yet implemented
                      # (this change didn't make it into .rc2)
                      prefs_key = "A10/Use QWorkspace"):

            print "QWorkspace for MDI support is enabled (experimental)"

            from PyQt4.Qt import QWorkspace
            self.workspace = QWorkspace()
            # Note: The QWorkspace class is deprecated in Qt 4.3 and instructs
            # developers to use the new QMdiArea class instead.
            # See: http://doc.trolltech.com/4.3/qmdiarea.html
            # Uncomment the two lines below when we've upgraded to Qt 4.3.
            # from PyQt4.Qt import QMdiArea
            # self.workspace = QMdiArea()
            self.centralAreaVBoxLayout.addWidget(self.workspace)
            self.workspace.addWindow(pw)
            pw.showMaximized()
        else:
            self.centralAreaVBoxLayout.addWidget(pw)

        if not self._init_part_two_done:
            # I bet there are pieces of _init_part_two that should be done EVERY time we bring up a
            # new partwindow.
            # [I guess that comment is by Will... for now, this code doesn't do those things
            #  more than once, it appears. [bruce 070503 comment]]
            MWsemantics._init_part_two(self)
        
        self.commandSequencer.start_using_initial_mode('$STARTUP_MODE')

        env.register_post_event_ui_updater( self.post_event_ui_updater) #bruce 070925
        #Urmi 20080716: initiliaze the Rosetta simulation parameters
        self.rosettaArgs = []
        return

    def _make_a_main_assy(self): #bruce 080813 split this out, revised
        """
        [private]
        
        Make a new main assy, meant for caller to store as self.assy.
        
        Called during __init__, and by _make_and_init_assy (in a mixin class)
        for fileClose and fileOpen.
        """
        res = Assembly(self,
                       "Untitled",
                       own_window_UI = True,
                       run_updaters = True,
                       commandSequencerClass = CommandSequencer
                      )
            #bruce 060127 added own_window_UI flag to help fix bug 1403;
            # it's required for this assy to support Undo.
        return res
        
    def _init_part_two(self):
        """
        #@ NEED DOCSTRING
        """
        # Create the NE1 Progress Dialog. mark 2007-12-06
        self.createProgressDialog()

        # Create the Preferences dialog widget.
        from ne1_ui.prefs.Preferences import Preferences
        self.userPrefs = Preferences(self.assy)

        # Enable/disable plugins.  These should be moved to a central method
        # where all plug-ins get added and enabled during invocation.  Mark 050921.
        self.userPrefs.enable_qutemol(env.prefs[qutemol_enabled_prefs_key])
        self.userPrefs.enable_nanohive(env.prefs[nanohive_enabled_prefs_key])
        self.userPrefs.enable_povray(env.prefs[povray_enabled_prefs_key])
        self.userPrefs.enable_megapov(env.prefs[megapov_enabled_prefs_key])
        self.userPrefs.enable_povdir(env.prefs[povdir_enabled_prefs_key])
        self.userPrefs.enable_gamess(env.prefs[gamess_enabled_prefs_key])
        self.userPrefs.enable_gromacs(env.prefs[gromacs_enabled_prefs_key])
        self.userPrefs.enable_cpp(env.prefs[cpp_enabled_prefs_key])
        self.userPrefs.enable_rosetta(env.prefs[rosetta_enabled_prefs_key])
        self.userPrefs.enable_rosetta_db(env.prefs[rosetta_database_enabled_prefs_key])
        self.userPrefs.enable_nv1(env.prefs[nv1_enabled_prefs_key])

        #Mouse wheel behavior settings.
        self.updateMouseWheelSettings()

        # Create the Help dialog. Mark 050812
        from ne1_ui.help.help import Ne1HelpDialog
        self.help = Ne1HelpDialog()

        
        from commands.PovraySceneProperties.PovraySceneProp import PovraySceneProp
        self.povrayscenecntl = PovraySceneProp(self)

        from commands.CommentProperties.CommentProp import CommentProp
        self.commentcntl = CommentProp(self)

        # Minimize Energy dialog. Mark 060705.
        from commands.MinimizeEnergy.MinimizeEnergyProp import MinimizeEnergyProp
        self.minimize_energy = MinimizeEnergyProp(self)

        # Atom Generator example for developers. Mark and Jeff. 2007-06-13
        from commands.BuildAtom.AtomGenerator import AtomGenerator
        self.atomcntl = AtomGenerator(self)

        # We must enable keyboard focus for a widget if it processes
        # keyboard events. [Note added by bruce 041223: I don't know if this is
        # needed for this window; it's needed for some subwidgets, incl. glpane,
        # and done in their own code. This window forwards its own key events to
        # the glpane. This doesn't prevent other subwidgets from having focus.]
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # 'depositState' is used by BuildAtoms_Command 
        #to determine what type of object (atom, clipboard chunk or library part)
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

        # 'movie_is_playing' is a flag that indicates a movie is playing. It is
        # used by other code to speed up rendering times by disabling the
        # (re)building of display lists for each frame of the movie.
        self.movie_is_playing = False

        # Current Working Directory (CWD).
        # When NE1 starts, the CWD is set to the Working Directory (WD)
        # preference from the user prefs db. Every time the user opens or
        # inserts a file during a session, the CWD changes to the directory
        # containing that file. When the user closes the current file and then
        # attempts to open a new file, the CWD will still be the directory of
        # the last file opened or inserted.
        # If the user changes the WD via 'File > Set Working Directory' when
        # a file is open, the CWD will not be changed to the new WD. (This
        # rule may change. Need to discuss with Ninad).
        # On the other hand, if there is no part open, the CWD will be
        # changed to the new WD.  Mark 060729.
        self.currentWorkingDirectory = ''

        # Make sure the working directory from the user prefs db exists since
        # it might have been deleted.
        if os.path.isdir(env.prefs[workingDirectory_prefs_key]):
            self.currentWorkingDirectory = env.prefs[workingDirectory_prefs_key]
        else:
            # The CWD does not exist, so set it to the default working dir.
            self.currentWorkingDirectory = getDefaultWorkingDirectory()

        # bruce 050810 replaced user preference initialization with this,
        # and revised update_mainwindow_caption to match
        from foundation.changes import Formula
        self._caption_formula = Formula(
            # this should depend on whatever update_mainwindow_caption_properly depends on;
            # but it can't yet depend on assy.has_changed(),
            # so that calls update_mainwindow_caption_properly (or the equiv) directly.
            lambda: (env.prefs[captionPrefix_prefs_key],
                     env.prefs[captionSuffix_prefs_key],
                     env.prefs[captionFullPath_prefs_key]),
            self.update_mainwindow_caption_properly
        )

        # Setting 'initialized' to 1 enables win_update().
        # [should this be moved into _init_after_geometry_is_set??
        # bruce 060104 question]
        self.initialised = 1

        # be told to add new Jigs menu items, now or as they become available [bruce 050504]
        register_postinit_object( "Jigs menu items", self )

        # Anything which depends on this window's geometry (which is not yet set at this point)
        # should be done in the _init_after_geometry_is_set method below, not here. [bruce guess 060104]

        self._init_part_two_done = True
        return # from _init_part_two

    def updateMouseWheelSettings(self):
        """
        Updates important mouse wheel attrs kept in self, including:
        - Mouse direction
        - Zoom in point
        - Zoom out point
        @note: These are typically set from the Preferences dialog.
        """
        if env.prefs[mouseWheelDirection_prefs_key] == 0:
            self.mouseWheelDirection = 1
        else:
            self.mouseWheelDirection = -1

        self.mouseWheelZoomInPoint  = env.prefs[zoomInAboutScreenCenter_prefs_key]
        self.mouseWheelZoomOutPoint = env.prefs[zoomOutAboutScreenCenter_prefs_key]

    def _get_commandSequencer(self): #bruce 080813 revised
        res = self.assy.commandSequencer
        assert res
        return res

    commandSequencer = property(_get_commandSequencer)

    def _get_currentCommand(self):
        return self.commandSequencer.currentCommand

    currentCommand = property(_get_currentCommand)

    def post_event_ui_updater(self): #bruce 070925
        self.currentCommand.command_post_event_ui_updater()
        return

    def createPopupMenu(self): # Ninad 070328
        """
        Returns a popup menu containing checkable entries for the toolbars
        and dock widgets present in the main window.

        This function is called by the main window every time the user
        activates a context menu, typically by right-clicking on a toolbar or
        a dock widget.

        This reimplements QMainWindow's createPopupMenu() method.

        @return: The popup menu.
        @rtype: U{B{QMenu}<http://doc.trolltech.com/4/qmenu.html>}

        @note: All main window toolbars must be created before calling
        createPopupMenu().

        @see: U{B{QMainWindow.createPopupMenu}
        <http://doc.trolltech.com/4.3/qmainwindow.html#createPopupMenu>}
        """
        menu = QMenu(self)

        contextMenuToolBars = \
                            [self.standardToolBar, self.viewToolBar,
                             self.standardViewsToolBar, self.displayStylesToolBar,
                             self.simulationToolBar, self.buildToolsToolBar,
                             self.selectToolBar, self.buildStructuresToolBar,
                             self.renderingToolBar]

        for toolbar in contextMenuToolBars:
            menu.addAction(toolbar.toggleViewAction())

        return menu


    def showFullScreen(self):
        """
        Full screen mode. (maximize the glpane real estate by hiding/ collapsing
        other widgets. (only Menu bar and the glpane are shown)
        The widgets hidden or collapsed include:
         - MainWindow Title bar
         - Command Manager,
         - All toolbars,
         - ModelTree/PM area,
         - History Widget,
         - Statusbar

        @param val: The state of the QAction (checked or uncheced) If True, it
                    will show the main window full screen , otherwise show it
                    with its regular size
        @type val: boolean
        @see: self.showSemiFullScreen, self.showNormal
        @see: ops_view.viewSlotsMixin.setViewFullScreen
        """

        if self._block_viewFullScreenAction_event:
            #see self.__init__ for a detailed comment about this instance
            #variable
            return

        self._block_viewFullScreenAction_event = False

        if self.viewSemiFullScreenAction.isChecked():
            self._block_viewSemiFullScreenAction_event = True
            self.viewSemiFullScreenAction.setChecked(False)
            self._block_viewSemiFullScreenAction_event = False

        self._showFullScreenCommonCode()
        for  widget in self.children():
            if isinstance(widget, QToolBar):
                if widget.isVisible():
                    widget.hide()
                    self._widgetToHideDuringFullScreenMode.append(widget)

        self.commandToolbar.hide()

    def _showFullScreenCommonCode(self, hideLeftArea = True):
        """
        The common code for making the Mainwindow full screen (maximimzing the
        3D workspace area) This is used by both, View > Full Screen and
        View > Semi-Full Screen
        @see: self.showFullScreen
        @see: self._showSemiFullScreen
        """
        #see self.__init__ for a detailed comment about this list
        self._widgetToHideDuringFullScreenMode = []
        QMainWindow.showFullScreen(self)
        for  widget in self.children():
            if isinstance(widget, QStatusBar):
                if widget.isVisible():
                    widget.hide()
                    self._widgetToHideDuringFullScreenMode.append(widget)

        self.activePartWindow().collapseLeftArea(hideLeftArea)
        self.reportsDockWidget.hide()

    def showSemiFullScreen(self):
        """
        Semi-Full Screen mode. (maximize the glpane real estate by hiding/ collapsing
        other widgets. This is different than the 'Full Screen mode' as it hides
        or collapses only the following widgets --
         - MainWindow Title bar and border
         - Report Widget
         - Statusbar

        @param val: The state of the QAction (checked or uncheced) If True, it
                    will show the main window full screen , otherwise show it
                    with its regular size
        @type val: boolean
        @see: self.showFullScreen, self.showNormal
        @see: ops_view.viewSlotsMixin.setViewSemiFullScreen
        """
        if self._block_viewSemiFullScreenAction_event:
            #see self.__init__ for a detailed comment about this instance
            #variable
            return

        self._block_viewSemiFullScreenAction_event = False

        if self.viewFullScreenAction.isChecked():
            self._block_viewFullScreenAction_event = True
            self.viewFullScreenAction.setChecked(False)
            self._block_viewFullScreenAction_event = False

        self._showFullScreenCommonCode(hideLeftArea = False)

    def showNormal(self):
        QMainWindow.showNormal(self)
        self.activePartWindow().expandLeftArea()

        # Note: This will show the reports dock widget even if the user
        # dismissed it earlier in his session. This is OK, they can just
        # dismiss it again if they don't want it. If users complain, this
        # will be easy to fix by overriding its hide() and show() methods
        # (I suggest adding a keyword arg to hide() called "breifly", set
        # to False by default, which sets a flag attr that show() can check.
        # Mark 2008-01-05.
        self.reportsDockWidget.show()

        for  widget in self._widgetToHideDuringFullScreenMode:
            widget.show()

        self.commandToolbar.show()
        #Clear the list of hidden widgets (those are no more hidden)
        self._widgetToHideDuringFullScreenMode = []

    def activePartWindow(self): # WARNING: this is inlined in a few methods of self
        return self._activepw

    def get_glpane(self): #bruce 071008; inlines self.activePartWindow
        return self._activepw.glpane

    glpane = property(get_glpane) #bruce 071008 to replace __getattr__

    def get_mt(self): #bruce 071008; inlines self.activePartWindow # TODO: rename .mt to .modelTree
        return self._activepw.modelTree

    mt = property(get_mt) #bruce 071008 to replace __getattr__

    def closeEvent(self, ce):
        fileSlotsMixin.closeEvent(self, ce)

    def sponsoredList(self):
        return (               
                self.povrayscenecntl,
                self.minimize_energy)

    def _init_after_geometry_is_set(self): #bruce 060104 renamed this from startRun and replaced its docstring.
        """
        Do whatever initialization of self needs to wait until its geometry has been set.
        [Should be called only once, after geometry is set; can be called before self is shown.
         As of 070531, this is called directly from main.py, after our __init__ but before we're first shown.]
        """
        # older docstring:
        # After the main window(its size and location) has been setup, begin to run the program from this method.
        # [Huaicai 11/1/05: try to fix the initial MMKitWin off screen problem by splitting from the __init__() method]

        self.win_update() # bruce 041222
        undo_internals.just_before_mainwindow_init_returns() # (this is now misnamed, now that it's not part of __init__)
        return

    __did_cleanUpBeforeExiting = False #bruce 070618

    def cleanUpBeforeExiting(self): #bruce 060127 added this re bug 1412 (Python crashes on exit, newly common)
        """
        NE1 is going to exit. (The user has already been given the chance to save current files
        if they are modified, and (whether or not they were saved) has approved the exit.)

        Perform whatever internal side effects are desirable to make the exit safe and efficient,
        and/or to implement features which save other info (e.g. preferences) upon exiting.

        This should be safe to call more than once, even though doing so is a bug.
        """

        # We do most things in their own try/except clauses, so if they fail,
        # we'll still do the other actions [bruce 070618 change].
        # But we always print something if they fail.

        if self.__did_cleanUpBeforeExiting:
            # This makes sure it's safe to call this method more than once.
            # (By itself, this fixes the exception in bug 2444 but not the double dialogs from it.
            #  The real fix for bug 2444 is elsewhere, and means this is no longer called more than once,
            #  but I'll leave this in for robustness.) [bruce 070618]
            return

        self.__did_cleanUpBeforeExiting = True

        msg = "exception (ignored) in cleanUpBeforeExiting: "

        try:
            # wware 060406 bug 1263 - signal the simulator that we are exiting
            # (bruce 070618 moved this here from 3 places in prepareToCloseAndExit.)
            from simulation.runSim import SimRunner
            SimRunner.PREPARE_TO_CLOSE = True
        except:
            print_compact_traceback( msg )

        try:
            env.history.message(greenmsg("Exiting program."))
        except:
            print_compact_traceback( msg )

        try:
            if env.prefs[rememberWinPosSize_prefs_key]: # Fixes bug 1249-2. Mark 060518.
                self.userPrefs.save_current_win_pos_and_size()
        except:
            print_compact_traceback( msg )

        ## self._make_and_init_assy() # (this seems to take too long, and is probably not needed)

        try:
            self.deleteOrientationWindow() # ninad 061121- perhaps it's unnecessary
        except:
            print_compact_traceback( msg )

        try:
            if self.assy:
                self.assy.close_assy()
                    # note: we won't also call
                    # self.assy.commandSequencer.exit_all_commands
                    # (with or without warn_about_abandoned_changes = False).
                    # Ideally we might sometimes like that warning here,
                    # but it's better to never have it than to risk exit bugs
                    # (in case it's too late to give it),
                    # or to bother users with duplicate warnings (if they
                    # already said to discard ordinary unsaved changes,
                    # different than the ones that warns about) which we
                    # don't presently have enough info to avoid giving.
                    # As for the exits themselves, they are not needed,
                    # and might be too slow and/or risk exit bugs.
                    # [bruce 080909 comment]
                self.assy.deinit()
                    # in particular, stop trying to update Undo/Redo actions
                    # all the time (which might cause crashes once their
                    # associated widgets are deallocated)
        except:
            print_compact_traceback( msg )

        return

    def postinit_item(self, item): #bruce 050504
        try:
            item(self)
        except:
            # blame item
            print_compact_traceback( "exception (ignored) in postinit_item(%r): " % item )
        return
    
    def win_update(self):
        """
        Update most state which directly affects the GUI display,
        in some cases repainting it directly.
        (Someday this should update all of it, but only what's needed,
        and perhaps also call QWidget.update. #e)
        [no longer named update, since that conflicts with QWidget.update]
        """
        if not self.initialised:
            return

        pw = self.activePartWindow()
        pw.glpane.gl_update()
        pw.modelTree.mt_update()
        self.reportsDockWidget.history_object.h_update()
            # this is self.reportsDockWidget.history_object, not env.history,
            # since it's really about this window's widget-owner,
            # not about the place to print history messages [bruce 050913]
        return

    ###################################
    # File Toolbar Slots
    ###################################

    # file toolbar slots are inherited from fileSlotsMixin (in ops_files.py) as of bruce 050907.
    # Notes:
    #   #e closeEvent method (moved to fileSlotsMixin) should be split in two
    # and the outer part moved back into this file.
    #   _make_and_init_assy method was moved to fileSlotsMixin (as it should be)


    ###################################
    # Edit Toolbar Slots
    ###################################

    def editMakeCheckpoint(self):
        """
        Slot for making a checkpoint (only available when Automatic
        Checkpointing is disabled).
        """
        import operations.undo_UI as undo_UI
        undo_UI.editMakeCheckpoint(self)
        return

    def editUndo(self):
        self.assy.editUndo()

    def editRedo(self):
        self.assy.editRedo()

    def editAutoCheckpointing(self, enabled):
        """
        Slot for enabling/disabling automatic checkpointing.
        """
        import foundation.undo_manager as undo_manager
        undo_manager.editAutoCheckpointing(self, enabled)
            # note: see code comment there, for why that's not in undo_UI.
            # note: that will probably do this (among other things):
            #   self.editMakeCheckpointAction.setVisible(not enabled)
        return

    def editClearUndoStack(self):
        """
        Slot for clearing the Undo Stack. Requires the user to confirm.
        """
        import operations.undo_UI as undo_UI
        undo_UI.editClearUndoStack(self)
        return

    # bruce 050131 moved some history messages from the following methods
    # into the assy methods they call, so the menu command versions also
    # have them

    def editCut(self):
        self.assy.cut_sel()
        self.win_update()

    def editCopy(self):
        self.assy.copy_sel()
        self.win_update()

    def editPaste(self):
        """
        Single shot paste operation accessible using 'Ctrl + V' or Edit > Paste.
        Implementation notes for the single shot paste operation:
          - The object (chunk or group) is pasted with a slight offset.
            Example:
            Create a graphene sheet, select it , do Ctrl + C and then Ctrl + V
            ... the pasted object is offset to original one.
          - It deselects others, selects the pasted item and then does a zoom to
            selection so that the selected item is in the center of the screen.
          - Bugs/ Unsupported feature: If you paste multiple copies of an object
            they are pasted at the same location. (i.e. the offset is constant)

        @see: L{ops_copy_Mixin.paste}
        """
        if self.assy.shelf.members:
            pastables = self.assy.shelf.getPastables()
            if not pastables:
                msg = orangemsg("Nothing to paste.")
                env.history.message(msg)
                return

            recentPastable = pastables[-1]
            self.assy.paste(recentPastable)
        else:
            msg = orangemsg("Nothing to paste.")
            env.history.message(msg)
        return

    def editPasteFromClipboard(self):
        """
        Invokes the L{PasteFromClipboard_Command}, a temporary command to paste items in the
        clipboard, into the 3D workspace. It also stores the command NE1 should
        return to after exiting this temporary command.
        """
        if self.assy.shelf.members:
            pastables = self.assy.shelf.getPastables()
            if not pastables:
                msg = orangemsg("Nothing to paste. Paste Command cancelled.")
                env.history.message(msg)
                return
            
            #pre-commandstack refactoring/cleanup comment: 
            #Make 'paste' as a general command to fix this bug: Enter Dna command
            #, invoke paste command, exit paste, enter Dna again -- the flyout
            #toolbar for dna is not visible . This whole thing will get revised 
            #after the command stack cleanup (to be coded soon)
            # -- Ninad 2008-07-29
            self.commandSequencer.userEnterCommand('PASTE')
        else:
            msg = orangemsg("Clipboard is empty. Paste Command cancelled.")
            env.history.message(msg)
        return

    def insertPartFromPartLib(self):
        """
        Sets the current command to L{PartLibrary_Command}, for inserting (pasting)
        a part from the partlib into the 3D workspace. It also stores the command
        NE1 should return to after exiting this temporary command.
        """
        self.commandSequencer.userEnterCommand('PARTLIB') #bruce 071011 guess ### REVIEW
        return

    # TODO: rename killDo to editDelete
    def killDo(self):
        """
        Deletes selected atoms, chunks, jigs and groups.
        """
        self.assy.delete_sel()
        ##bruce 050427 moved win_update into delete_sel as part of fixing bug 566
        ##self.win_update()

    def resizeSelectedDnaSegments(self):
        """
        Invokes the MultipleDnaSegmentResize_EditCommand to resize the
        selected segments.
        @see: chunk.make_glpane_context_menu_items (a context menu that calls
        this method)
        """
        #TODO: need more ui options to invoke this command.
        selectedSegments = self.assy.getSelectedDnaSegments()
        if len(selectedSegments) > 0:
            commandSequencer = self.commandSequencer
            commandSequencer.userEnterCommand('MULTIPLE_DNA_SEGMENT_RESIZE')
            assert commandSequencer.currentCommand.commandName == 'MULTIPLE_DNA_SEGMENT_RESIZE'
            commandSequencer.currentCommand.editStructure(list(selectedSegments))
        return

    def editAddSuffix(self):
        """
        Adds a suffix to the name(s) the selected objects.
        """
        # Don't allow renaming while animating (b/w views).
        if self.glpane.is_animating:
            return

        _cmd = greenmsg("Add Suffix: ")

        if not objectSelected(self.assy):
            if objectSelected(self.assy, objectFlags = ATOMS):
                _msg = redmsg("Cannot rename atoms.")
            else:
                _msg = redmsg("Nothing selected.")
            env.history.message(_cmd + _msg)
            return

        _renameList = self.assy.getSelectedRenameables()

        ok, new_name = grab_text_line_using_dialog(
            title = "Add Suffixes",
            label = "Suffix to add to selected nodes:",
            iconPath = "ui/actions/Edit/Add_Suffixes.png")

        if not ok:
            return

        _number_renamed = 0
        for _object in _renameList:
            if _object.rename_enabled():
                _new_name = _object.name + new_name
                print "new name = ", _new_name
                ok, info = _object.try_rename(_new_name)
                if ok:
                    _number_renamed += 1

        _msg = "%d of %d selected objects renamed." \
             % (_number_renamed, len(_renameList))
        env.history.message(_cmd + _msg)

    def editRenameSelection(self): # probably by Mark
        """
        Renames multiple selected objects (chunks or jigs).
        """
        # Don't allow renaming while animating (b/w views).
        if self.glpane.is_animating:
            return

        _cmd = greenmsg("Rename: ")

        if not objectSelected(self.assy):
            if objectSelected(self.assy, objectFlags = ATOMS):
                _msg = redmsg("Cannot rename atoms.")
            else:
                _msg = redmsg("Nothing selected.")
            env.history.message(_cmd + _msg)
            return

        _renameList = self.assy.getSelectedRenameables()

        ok, new_name = grab_text_line_using_dialog(
            title = "Rename",
            label = "New name:",
            iconPath = "ui/actions/Edit/Rename.png")

        if not ok:
            # No msg. Ok for now. --Mark
            return
        
        # Renumber the selected objects if the last character is "#"
        # i.e. the # character will be replaced by a number, resulting in 
        # uniquely named (numbered) nodes in the model tree. 
        # IIRC, the numbering is not guaranteed to be in any specific order,
        # but testing has shown that leaf nodes are numbered in the order
        # they appear in the model tree. --Mark 2008-11-12
        if new_name[-1] == "#":
            _renumber = True
            new_name = new_name[:-1]
        else:
            _renumber = False

        _number_renamed = 0
        for _object in _renameList:
            if renameableLeafNode(_object):
                # REVIEW: should renameableLeafNode be tested by getSelectedRenameables?
                # [bruce 081124 question]
                if _renumber:
                    ok, info = _object.try_rename(new_name + str(_number_renamed + 1))
                else:
                    ok, info = _object.try_rename(new_name)
                if ok:
                    _number_renamed += 1

        _msg = "%d of %d selected objects renamed." \
             % (_number_renamed, len(_renameList))
        env.history.message(_cmd + _msg)
        return

    def renameObject(self, object):
        """
        Prompts the user to rename I{object}, which can be any renameable node.

        @param object: The object to be renamed.
        @type  object: Node

        @return: A descriptive message about what happened.
        @rtype:  string
        """
        # Don't allow renaming while animating (b/w views).
        if self.glpane.is_animating:
            return

        # Note: see similar code in rename_node_using_dialog in another class.
        oldname = object.name
        ok = object.rename_enabled()
        # Various things below can set ok to False (if it's not already)
        # and set text to the reason renaming is not ok (for use in error messages).
        # Or they can put the new name in text, leave ok True, and do the renaming.
        if not ok:
            text = "Renaming this object is not permitted."
                #e someday we might want to call try_rename on fake text
                # to get a more specific error message... for now it doesn't have one.
        else:
            ok, text = grab_text_line_using_dialog(
                title = "Rename",
                label = "new name for [%s]:" % oldname,
                iconPath = "ui/actions/Edit/Rename.png",
                default = oldname )
        if ok:
            ok, text = object.try_rename(text)
        if ok:
            msg = "Renamed [%s] to [%s]" % (oldname, text)
            self.mt.mt_update()
        else:
            msg = "Can't rename [%s]: %s" % (oldname, text) # text is reason why not
        return msg

    def editRename(self):
        """
        Renames the selected node/object.

        @note: Does not work for DnaStrands or DnaSegments.
        @deprecated: Use editRenameSelection instead.
        """
        _cmd = greenmsg("Rename: ")

        if not objectSelected(self.assy):
            if objectSelected(self.assy, objectFlags = ATOMS):
                _msg = redmsg("Cannot rename atoms.")
            else:
                _msg = redmsg("Nothing selected.")
            env.history.message(_cmd + _msg)
            return

        _renameableList = self.assy.getSelectedRenameables()
        _numSelectedObjects = len(_renameableList)
        # _numSelectedObjects is > 1 if the user selected a single DnaStrand
        # or DnaSegment, since they contain chunk nodes. This is a bug
        # that I will discuss with Bruce. --Mark 2008-03-14

        if _numSelectedObjects == 0:
            _msg = "Renaming this object is not permitted."
        elif _numSelectedObjects == 1:
            _msg = self.renameObject(_renameableList[0])
        else:
            _msg = redmsg("Only one object can be selected.")
        env.history.message(_cmd + _msg)

    def editPrefs(self):
        """
        Edit Preferences
        """
        self.userPrefs.show()

    ###################################
    # View Toolbar Slots
    ###################################

    # View toolbar slots are inherited from viewSlotsMixin
    # (in ops_view.py) as of 2006-01-20. Mark

    ###################################
    # Display Toolbar Slots
    ###################################

    # Display toolbar slots are inherited from displaySlotsMixin
    # (in ops_display.py) as of 2008-020-02. Mark

    ###############################################################
    # Select Toolbar Slots
    ###############################################################

    def selectAll(self):
        """
        Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        """
        env.history.message(greenmsg("Select All:"))
        self.assy.selectAll()

    def selectNone(self):
        env.history.message(greenmsg("Select None:"))
        self.assy.selectNone()

    def selectInvert(self):
        """
        If some parts are selected, select the other parts instead.
        If some atoms are selected, select the other atoms instead
        (even in chunks with no atoms selected, which end up with
        all atoms selected). (And unselect all currently selected
        parts or atoms.)
        """
        #env.history.message(greenmsg("Invert Selection:"))
        # assy method revised by bruce 041217 after discussion with Josh
        self.assy.selectInvert()

    def selectConnected(self):
        """
        Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """
        self.assy.selectConnected()

    def selectDoubly(self):
        """
        Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """
        self.assy.selectDoubly()

    def selectExpand(self):
        """
        Slot for Expand Selection, which selects any atom that is bonded
        to any currently selected atom.
        """
        self.assy.selectExpand()

    def selectContract(self):
        """
        Slot for Contract Selection, which unselects any atom which has
        a bond to an unselected atom, or which has any open bonds.
        """
        self.assy.selectContract()

    def selectLock(self, lockState):
        """
        Slot for Lock Selection, which locks/unlocks selection.
        @param lockState: The new selection lock state, either locked (True)
                          or unlocked (False).
        @type  lockState: boolean
        """
        self.assy.lockSelection(lockState)
        
        

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

    def makeRotaryMotor(self):
        self.assy.makeRotaryMotor()

    def makeLinearMotor(self):
        self.assy.makeLinearMotor()

    def createPlane(self):
        commandSequencer = self.commandSequencer
        commandSequencer.userEnterCommand('REFERENCE_PLANE')
        commandSequencer.currentCommand.runCommand()

    def makeGridPlane(self):
        self.assy.makeGridPlane()

    def createPolyLine(self):
        pass
        if 0: #NIY
            self.assy.createPolyLine()

    def makeESPImage(self):
        self.assy.makeESPImage()

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

    # Modify toolbar slots are inherited from modifySlotsMixin
    # (in ops_display.py) as of 2008-020-02. Mark

    ###################################
    # Help Toolbar Slots
    ###################################
    
    def helpTutorials(self):
        from foundation.wiki_help import open_wiki_help_URL
        url = "http://www.nanoengineer-1.net/mediawiki/index.php?title=Tutorials"
        worked = open_wiki_help_URL(url)
        return

    def helpMouseControls(self):
        self.help.showDialog(0)
        return

    def helpKeyboardShortcuts(self):
        self.help.showDialog(1)
        return

    def helpSelectionShortcuts(self):
        self.help.showDialog(2)
        return

    def helpGraphicsCard(self):
        """
        Display details about the system\'s graphics card in a dialog.
        """
        ginfo = get_gl_info_string( self.glpane) #bruce 070308 added glpane arg

        msgbox = TextMessageBox(self)
        msgbox.setWindowTitle("Graphics Card Info")
        msgbox.setText(ginfo)
        msgbox.show()
        return

# I modified a copy of cpuinfo.py from
# http://cvs.sourceforge.net/viewcvs.py/numpy/Numeric3/scipy/distutils/
# thinking it might help us support users better if we had a built-in utility
# for interrogating the CPU.  I do not plan to commit cpuinfo.py until I speak
# to Bruce about this. Mark 051209.
#
#    def helpCpuInfo(self):
#        """
#        Displays this system's CPU information.
#        """
#        from cpuinfo import get_cpuinfo
#        cpuinfo = get_cpuinfo()
#
#        from widgets import TextMessageBox
#        msgbox = TextMessageBox(self)
#        msgbox.setCaption("CPU Info")
#        msgbox.setText(cpuinfo)
#        msgbox.show()

    def helpAbout(self):
        """
        Displays information about this version of NanoEngineer-1.
        """
        from utilities.version import Version
        v = Version()
        product = v.product
        versionString = "Version " + repr(v)
        if v.releaseCandidate:
            versionString += ("_RC%d" % v.releaseCandidate)
        if v.releaseType:
            versionString += (" (%s)" % v.releaseType)
        date = "Release Date: " + v.releaseDate
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        if filePath.endswith('/Contents/Resources'):
            filePath = filePath[:-19]
        installdir = "Running from: " + filePath
        techsupport = "For technical support, send email to support@nanorex.com"
        website = "Website: www.nanoengineer-1.com"
        wiki = "Wiki and Tutorials: www.nanoengineer-1.net"
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
                 + website \
                 + "\n" \
                 + wiki

        QMessageBox.about ( self, "About NanoEngineer-1", aboutstr)
        return

    def helpWhatsThis(self):
        from PyQt4.Qt import QWhatsThis ##bruce 050408
        QWhatsThis.enterWhatsThisMode()
        return

    ###################################
    # Modes Toolbar Slots
    ###################################

    # get into Select Atoms mode
    def toolsSelectAtoms(self): # note: this can NO LONGER be called from update_select_mode [as of bruce 060403]
        self.commandSequencer.userEnterCommand('SELECTATOMS', always_update = True)

    # get into Select Chunks mode
    def toolsSelectMolecules(self):# note: this can also be called from update_select_mode [bruce 060403 comment]
        self.commandSequencer.userEnterCommand('SELECTMOLS', always_update = True)

    # get into Move Chunks (or Translate Components) command
    def toolsMoveMolecule(self):
        self.ensureInCommand('MODIFY')
        self.commandSequencer.currentCommand.propMgr.activate_translateGroupBox()
        return

    # Rotate Components command
    def toolsRotateComponents(self):
        self.ensureInCommand('MODIFY')
        self.commandSequencer.currentCommand.propMgr.activate_rotateGroupBox()
        return

    # get into Build mode
    def toolsBuildAtoms(self): # note: this can now be called from update_select_mode [as of bruce 060403]
        self.depositState = 'Atoms'
        self.commandSequencer.userEnterCommand('DEPOSIT', always_update = True)

    # get into cookiecutter mode
    def enterBuildCrystalCommand(self):
        self.commandSequencer.userEnterCommand('CRYSTAL', always_update = True)

    # get into Extrude mode
    def toolsExtrude(self):
        self.commandSequencer.userEnterCommand('EXTRUDE', always_update = True)

    # get into Fuse Chunks mode
    def toolsFuseChunks(self):
        self.commandSequencer.userEnterCommand('FUSECHUNKS', always_update = True)

    ###################################
    # Simulator Toolbar Slots
    ###################################

    def simMinimizeEnergy(self):
        """
        Opens the Minimize Energy dialog.
        """
        self.minimize_energy.setup()

    def simSetup(self):
        """
        Creates a movie of a molecular dynamics simulation.
        """
        if debug_flags.atom_debug: #bruce 060106 added this (fixing trivial bug 1260)
            print "atom_debug: reloading sim_commandruns on each use, for development"
            import simulation.sim_commandruns as sim_commandruns
            reload(sim_commandruns)
        from simulation.sim_commandruns import simSetup_CommandRun
        cmdrun = simSetup_CommandRun( self)
        cmdrun.run()
        return
    
    #Urmi 20080725: Methods for running Rosetta Simulation
    def rosettaSetup(self):
        """
        Setup rosetta simulation.
        """
        from simulation.ROSETTA.RosettaSimulationPopUpDialog import RosettaSimulationPopUpDialog
        form = RosettaSimulationPopUpDialog(self)
        self.connect(form, SIGNAL('editingFinished()'), self.runRosetta)
             
        return
    
    def runRosetta(self):
        """
        Run a Rosetta simulation.
        """
        from simulation.ROSETTA.rosetta_commandruns import rosettaSetup_CommandRun
        if self.rosettaArgs[0] > 0:
            cmdrun = rosettaSetup_CommandRun(self, self.rosettaArgs, "ROSETTA_FIXED_BACKBONE_SEQUENCE_DESIGN")
            cmdrun.run() 
        
        return
    
    def setRosettaParameters(self, numRuns, otherOptionsText):
        """
        Set parameters for a Rosetta .
        @param numRuns: number of Rosetta simulations.
        @type numRuns: int
        @param otherOptionsText: string of all the other options, including the 
                                ones in Rosett pop up dialog.
        @type otherOptionsText: str
        """
        protein = ""
        if self.commandSequencer.currentCommand.commandName == 'BUILD_PROTEIN' or self.commandSequencer.currentCommand.commandName == 'EDIT_ROTAMERS' or self.commandSequencer.currentCommand.commandName == 'EDIT_RESIDUES':
            protein = self.commandSequencer.currentCommand.propMgr.current_protein
        
        #run Rosetta for the first selected protein
        if protein == "" and len(self.assy.selmols) >=1:
            for chunk in self.assy.selmols:
                if chunk.isProteinChunk():
                    protein = chunk.name
                    break
                
        argList = [numRuns, otherOptionsText, protein]
        self.rosettaArgs = []
        self.rosettaArgs.extend(argList)
        return
    
    #end of Rosetta simulation methods
    
    def simNanoHive(self):
        """
        Opens the Nano-Hive dialog... for details see subroutine's docstring.
        """
        # This should be probably be modeled after the simSetup_CommandRun class
        # I'll do this if Bruce agrees.  For now, I want to get this working ASAP.
        # Mark 050915.
        self.nanohive.showDialog(self.assy)

    def simPlot(self):
        """
        Opens the "Make Graphs" dialog if there is a movie file
        (i.e. a movie file has been opened in the Movie Player).
        For details see subroutine's docstring.
        """
        from commands.Plot.PlotTool import simPlot
        dialog = simPlot(self.assy) # Returns "None" if there is no current movie file. [mark 2007-05-03]
        if dialog:
            self.plotcntl = dialog #probably useless, but done since old code did it;
                # conceivably, keeping it matters due to its refcount. [bruce 050327]
                # matters now, since dialog can be None. [mark 2007-05-03]
        return

    def simMoviePlayer(self):
        """
        Plays a DPB movie file created by the simulator.
        """
        from commands.PlayMovie.movieMode import simMoviePlayer
        simMoviePlayer(self.assy)
        return

    def JobManager(self):
        """
        Opens the Job Manager dialog... for details see subroutine's docstring.

        @note: This is not implemented.
        """
        from analysis.GAMESS.JobManager import JobManager
        dialog = JobManager(self)
        if dialog:
            self.jobmgrcntl = dialog
                # probably useless, but done since old code did it;
                # conceivably, keeping it matters due to its refcount.
                # See Bruce's note in simPlot().
        return

    def serverManager(self):
        """
        Opens the server manager dialog.

        @note: This is not implemented.
        """
        from processes.ServerManager import ServerManager
        ServerManager().showDialog()

    ###################################
    # Insert Menu/Toolbar Slots
    ###################################

    def ensureInCommand(self, commandName): #bruce 071009
        """
        If the current command's .commandName differs from the one given, change
        to that command.

        @note: As of 080730, userEnterCommand has the same special case
               of doing nothing if we're already in the named command.
               So we just call it. (Even before, it had almost that
               special case; see its docstring for details.)

        @note: all uses of this method are causes for suspicion, about
        whether some sort of refactoring or generalization is called for,
        unless they are called from a user command whose purpose is solely
        to switch to the named command. (In other words, switching to it
        for some reason other than the user asking for that is suspicious.)
        (That happens in current code [071011], and ought to be cleared up somehow,
         but maybe not using this method in particular.)
        """
        self.commandSequencer.userEnterCommand(commandName)
            # note: this changes the value of .currentCommand
        return

    def insertAtom(self):
        self.ensureInCommand('SELECTMOLS')
        self.atomcntl.show()

    def insertGraphene(self):   
        """
        Invokes the graphene command ('BUILD_GRAPHENE')
        """
        self.commandSequencer.userEnterCommand('BUILD_GRAPHENE')
        self.commandSequencer.currentCommand.runCommand()

    # Build > CNT related slots and methods. ######################

    def activateNanotubeTool(self):
        """
        Enter Build Nanotube.
        @see:B{self.insertNanotube}
        @see: B{ops_select_Mixin.getSelectedNanotubeGroups}
        @see: B{cnt_model.NanotubeGroup.edit}
        """
        selectedNanotubeGroupList = self.assy.getSelectedNanotubeGroups()

        #If exactly one NanotubeGroup is selected then when user invokes Build > Nanotube
        #command, edit the selected NanotubeGroup instead of creating a new one
        #For all other cases, invoking Build > Nanotube will create a new NanotubeGroup
        if len(selectedNanotubeGroupList) == 1:
            selNanotubeGroup = selectedNanotubeGroupList[0]
            selNanotubeGroup.edit()
        else:
            commandSequencer = self.commandSequencer
            commandSequencer.userEnterCommand('BUILD_NANOTUBE')

            assert self.commandSequencer.currentCommand.commandName == 'BUILD_NANOTUBE'
            self.commandSequencer.currentCommand.runCommand()

    def insertNanotube(self, isChecked = False):
        """
        @param isChecked: If Nanotube button in the Nanotube Flyout toolbar is
                          checked, enter NanotubeLineMode. (provided you are
                          using the new InsertNanotube_EditCommand command.
        @type  isChecked: boolean
        @see: B{Ui_NanotubeFlyout.activateInsertNanotubeLine_EditCommand}
        """
        
        self.enterOrExitTemporaryCommand('INSERT_NANOTUBE')
        
        currentCommand = self.commandSequencer.currentCommand
        if currentCommand.commandName == "INSERT_NANOTUBE":
            currentCommand.runCommand()
            

        

    def activateDnaTool(self):
        """
        Enter the DnaDuplex_EditCommand command.
        @see:B{self.insertDna}
        @see: B{ops_select_Mixin.getSelectedDnaGroups}
        @see: B{dna_model.DnaGroup.edit}
        """
        selectedDnaGroupList = self.assy.getSelectedDnaGroups()

        #If exactly one DnaGroup is selected then when user invokes Build > Dna
        #command, edit the selected Dnagroup instead of creating a new one
        #For all other cases, invoking Build > Dna  wikk create a new DnaGroup
        if len(selectedDnaGroupList) == 1:
            selDnaGroup = selectedDnaGroupList[0]
            selDnaGroup.edit()
        else:
            commandSequencer = self.commandSequencer
            commandSequencer.userEnterCommand('BUILD_DNA')

            assert self.commandSequencer.currentCommand.commandName == 'BUILD_DNA'
            self.commandSequencer.currentCommand.runCommand()

    def enterOrExitTemporaryCommand(self, commandName): #bruce 080730 split this out of several methods
        commandSequencer = self.commandSequencer
        currentCommand = commandSequencer.currentCommand
        if currentCommand.commandName != commandName:
            # enter command, if not already in it
            commandSequencer.userEnterCommand( commandName)
        else:
            # exit command, if already in it
            currentCommand.command_Done()
        return
        
    def enterBreakStrandCommand(self, isChecked = False):
        """
        """
        #REVIEW- arg isChecked is unused. Need to revise this this in several 
        #methods-- Ninad 2008-07-31
        self.enterOrExitTemporaryCommand( 'BREAK_STRANDS' )
    
    def enterJoinStrandsCommand(self, isChecked = False):
        """
        """
        self.enterOrExitTemporaryCommand( 'JOIN_STRANDS' )       

    def enterMakeCrossoversCommand(self, isChecked = False):
        """
        Enter make crossovers command.
        """
        self.enterOrExitTemporaryCommand( 'MAKE_CROSSOVERS' )        

    def enterOrderDnaCommand(self, isChecked = False):
        """
        """
        self.enterOrExitTemporaryCommand('ORDER_DNA')        

    def enterDnaDisplayStyleCommand(self, isChecked = False):
        """
        """
        self.enterOrExitTemporaryCommand('EDIT_DNA_DISPLAY_STYLE')
        
    #UM 063008: protein flyout toolbar commands    
    def activateProteinTool(self):
        """
        Activates the Protein toolbar.
        """
        commandSequencer = self.commandSequencer
        commandSequencer.userEnterCommand('MODEL_AND_SIMULATE_PROTEIN')
        return
    
    def insertPeptide(self, isChecked = False):  
        """
        Invokes the peptide command (INSERT_PEPTIDE)
        @param isChecked: If insertPeptide button in the 
                          Protein Flyout toolbar is
                          checked, enter insertPeptideMode. 
        @type isChecked: bool
        """
        
        self.enterOrExitTemporaryCommand('INSERT_PEPTIDE')     
        
        currentCommand = self.commandSequencer.currentCommand      
        if currentCommand.commandName == "INSERT_PEPTIDE":
            currentCommand.runCommand()
        
    def enterProteinDisplayStyleCommand(self, isChecked = False):
        """
        Enter protein display style command
        @param isChecked: If enterProteinDisplayStyleCommand button in the 
                          Protein Flyout toolbar is
                          checked, enter ProteinDisplayStyleMode. 
        @type isChecked: bool
        """
        self.enterOrExitTemporaryCommand('EDIT_PROTEIN_DISPLAY_STYLE')
        
    
    def enterEditRotamersCommand(self, isChecked = False):
        """
        Enter edit rotamers command
        @param isChecked: If enterEditRotamersCommand button in the 
                          Protein Flyout toolbar is
                          checked, enter enterEditRotamersMode. 
        @type isChecked: bool
        """
        self.enterOrExitTemporaryCommand('EDIT_ROTAMERS')
            
        
    def enterEditResiduesCommand(self, isChecked = False):
        """
        Enter edit residues command
        @param isChecked: If enterEditResiduesCommand button in the 
                          Protein Flyout toolbar is
                          checked, enter enterEditResiduesMode. 
        @type isChecked: bool
        """
        self.enterOrExitTemporaryCommand('EDIT_RESIDUES')
            
    def enterCompareProteinsCommand(self, isChecked = False):
        """
        Enter compare proteins command
        @param isChecked: If enterCompareProteinsCommand button in the 
                          Protein Flyout toolbar is
                          checked, enter enterCompareProteinsMode. 
        @type isChecked: bool
        """
        self.enterOrExitTemporaryCommand('COMPARE_PROTEINS')
       

    def enterStereoPropertiesCommand(self):
        """
        Enter Stereo Properties Command
        """
        self.enterOrExitTemporaryCommand('STEREO_PROPERTIES')
                        
                
    def enterQuteMolCommand(self):
        """
        Show the QuteMol property manager. 
        """
        commandSequencer = self.commandSequencer
        commandSequencer.userEnterCommand('QUTEMOL')
        # note: if we make the Qutemol action a 'ckeckable action'
        # (so when unchecked by the user, it should exit the QuteMol command),
        # then replace the above by a call to self.enterOrExitTemporaryCommand.
        
    def insertDna(self, isChecked = False):
        """
        @param isChecked: If Dna Duplex button in the Dna Flyout toolbar is
                          checked, enter DnaLineMode. (provided you are
                          using the new DNADuplexEditCommand command.
        @type  isChecked: boolean
        @see: B{Ui_DnaFlyout.activateDnaDuplex_EditCommand}
        """   
        self.enterOrExitTemporaryCommand('DNA_DUPLEX')
        
        currentCommand = self.commandSequencer.currentCommand
        if currentCommand.commandName == 'DNA_DUPLEX':
            currentCommand.runCommand()

    def orderDna(self, dnaGroupList = ()):
        """
        open a text editor and load a temporary text file containing all the
        DNA strand names and their sequences in the current DNA object. It will
        look something like this: (comma separated values. To be revised)

        Strand1,ATCAGCTACGCATCGCT
        Strand2,TAGTCGATGCGTAGCGA

        The user can then save the file to a permanent location.

        @see: Ui_DnaFlyout.orderDnaCommand
        @see: self._writeDnaSequence
        @TODO: This works only for a single DNA group So dnaGroupList always
                contain a single item.
        """

        dnaGroupNameString = ''

        fileBaseName = 'DnaSequence'

        dnaSequence = ''


        if dnaGroupList:
            dnaSequence = ''
            for dnaGroup in dnaGroupList:
                dnaSequence = dnaSequence + dnaGroup.getDnaSequence(format = 'CSV')
        else:
            currentCommand = self.commandSequencer.currentCommand
            if currentCommand.commandName == 'BUILD_DNA':
                if currentCommand.struct is not None:
                    dnaSequence = currentCommand.struct.getDnaSequence()
                    dnaGroupNameString = currentCommand.struct.name
                    fileBaseName = dnaGroupNameString


        if dnaSequence:
            tmpdir = find_or_make_Nanorex_subdir('temp')
            temporaryFile = os.path.join(tmpdir, "%s.csv" % fileBaseName)
            self._writeDnaSequence(temporaryFile,
                                   dnaGroupNameString,
                                   dnaSequence)

            open_file_in_editor(temporaryFile)


    def _writeDnaSequence(self, fileName, dnaGroupNameString, dnaSequence):
        """
        Open a temporary file and write the specified dna sequence to it
        @param fileName: the full path of the temporary file to be opened
        @param  dnaSequence: The dnaSequence string to be written to the file.
        @see: self.orderDna
        """

        #Create Header
        headerString = '#NanoEngineer-1 DNA Order Form created on: '
        timestr = "%s\n" % time.strftime("%Y-%m-%d at %H:%M:%S")

        if self.assy.filename:
            mmpFileName = "[" + os.path.normpath(self.assy.filename) + "]"
        else:
            mmpFileName = "[" + self.assy.name + "]" + \
                        " ( The mmp file was probably not saved when the "\
                        " sequence was written)"

        if dnaGroupNameString:
            fileNameInfo_header = "#This sequence is created for node "\
                                "[%s] of file %s\n\n"%(dnaGroupNameString,
                                                       mmpFileName)
        else:
            fileNameInfo_header = "#This sequence is created for file '%s\n\n'"%(
                mmpFileName)

        headerString = headerString + timestr + fileNameInfo_header

        f = open(fileName,'w')
        # Write header
        f.write(headerString)
        f.write("Name,Sequence,Notes\n") # Per IDT's Excel format.
        f.write(dnaSequence)

    def createDnaSequenceEditorIfNeeded(self):
        """
        Returns a Sequence editor object (a dockwidget).
        If one doesn't already exists, it creates one .
        (created only once and only when its first requested and then the
        object is reused)
        @return: The sequence editor object (self._dnaSequenceEditor
        @rtype: B{DnaSequenceEditor}
        @see: DnaDuplexPropertyManager._loadSequenceEditor
        @WARNING: QMainwindow.restoreState prints a warning message because its
        unable to find this object in the next session. (as this object is
        created only when requested) This warning message is harmless, but
        if we want to get rid of it, easiest way is to always  create this
        object when MainWindow is created. (This is a small object so may
        be thats the best way)
        """
        if self._dnaSequenceEditor is None:
            from dna.DnaSequenceEditor.DnaSequenceEditor import DnaSequenceEditor
            self._dnaSequenceEditor = DnaSequenceEditor(self)
            self._dnaSequenceEditor.setObjectName("dna_sequence_editor")
            #Should changes.keep_forevenr be called here?
            #Answer : No because python references to these objects are kept in 
            #the MainWindow attrs

        return self._dnaSequenceEditor
    
    
    def createProteinSequenceEditorIfNeeded(self):
        """
        Returns a Sequence editor object (a dockwidget).
        If one doesn't already exists, it creates one .
        (created only once and only when its first requested and then the
        object is reused)
        @return: The sequence editor object (self._proteinSequenceEditor
        @rtype: B{ProteinSequenceEditor}
        
        """
        if self._proteinSequenceEditor is None:
            from protein.ProteinSequenceEditor.ProteinSequenceEditor import ProteinSequenceEditor
            self._proteinSequenceEditor = ProteinSequenceEditor(self)
            self._proteinSequenceEditor.setObjectName("protein_sequence_editor")

        return self._proteinSequenceEditor    
    
    def toggle_selectByNameDockWidget(self, bool_toggle):
        pw = self._activepw
        leftChannelDockWidget = pw.getLeftChannelDockWidget()
        if bool_toggle:
            leftChannelDockWidget.show()
        else:
            leftChannelDockWidget.close()
        

    def insertPovrayScene(self):
        self.povrayscenecntl.setup()

    def insertComment(self):
        """
        Insert a new comment into the model tree.
        """
        self.commentcntl.setup()

    ###################################
    # Slots for future tools
    ###################################

    # Mirror Tool
    def toolsMirror(self):
        env.history.message(redmsg("Mirror Tool: Not implemented yet."))

    # Mirror Circular Boundary Tool
    def toolsMirrorCircularBoundary(self):
        env.history.message(redmsg("Mirror Circular Boundary Tool: Not implemented yet."))

    ###################################
    # Slots for Done and Cancel actions for current command
    ###################################

    def toolsDone(self):
        """
        @note: called from several places, including ok_btn_clicked
        (and in some cases, cancel_btn_clicked) of PM_Dialog and its
        subclasses
        
        The calls from ok_btn_clicked and cancel_btn_clicked methods are 
        probablycorrect, but are deprecated, and should be replaced by calls of
        self.command.command_Done (where self is the calling PM).
        """
        #bruce 080815/080827 docstring
        command_to_exit  = self.currentCommand.command_that_supplies_PM()
        command_to_exit.command_Done()
        return

    def toolsCancel(self):
        """
        Cancel the command which is supplying the currently visible
        Property Manager.
        
        @note: called only from cancel_btn_clicked methods in PM_Dialog or its
        subclasses, but some of those call toolsDone instead.
        
        (where self is the calling PM).
        """
        #bruce 080815/080827 docstring
        command_to_exit = self.currentCommand.command_that_supplies_PM()
        command_to_exit.command_Cancel()
        return

    ######################################
    # Show View > Orientation Window
    #######################################

    def showOrientationWindow(self, isChecked = False): #Ninad 061121

        if isChecked:
            if not self.orientationWindow:
                self.orientationWindow  = ViewOrientationWindow(self)
                #self.orientationWindow.createOrientationViewList(namedViewList)
                self.orientationWindow.createOrientationViewList()
                self.orientationWindow.setVisible(True)
            else:
                if not self.orientationWindow.isVisible():
                    self.orientationWindow.setVisible(True)
        else:
            if self.orientationWindow and self.orientationWindow.isVisible():
                self.orientationWindow.setVisible(False)

        return self.orientationWindow

    def deleteOrientationWindow(self):
        """
        Delete the orientation window when the main window closes.
        """
        #ninad 061121 - this is probably unnecessary
        if self.orientationWindow:
            self.orientationWindow.close()
            self.orientationWindow = None

        return self.orientationWindow

    # key event handling revised by bruce 041220 to fix some bugs;
    # see comments in the GLPane methods.

    def keyPressEvent(self, e):
        self.glpane.keyPressEvent(e)

    def keyReleaseEvent(self, e):
        self.glpane.keyReleaseEvent(e)

    def wheelEvent(self, event): #bruce 070607 fix bug xxx [just reported, has no bug number yet]
        ## print "mwsem ignoring wheelEvent",event
        # Note: this gets called by wheel events with mouse inside history widget,
        # whenever it has reached its scrolling limit. Defining it here prevents the bug
        # of Qt passing it on to GLPane (maybe only happens if GLPane was last-clicked widget),
        # causing unintended mousewheel zoom. Apparently just catching this and returning is
        # enough -- it's not necessary to also call event.ignore(). Guess: this method's default
        # implem passes it either to "central widget" (just guessing that's the GLPane) or to
        # the last widget we clicked on (or more likely, the one with the keyfocus).
        return
    
    # Methods for temporarily disabling QActions in toolbars/menus ##########

    def enableViews(self, enableFlag = True):
        """
        Disables/enables view actions on toolbar and menu.

        This is typically used to momentarily disable some
        of the view actions while animating between views.

        @param enableFlag: Flag to enable/disable the View actions in this
                           method.
        @type  enableFlag: boolean
        """
        self.viewNormalToAction.setEnabled(enableFlag)
        self.viewParallelToAction.setEnabled(enableFlag)

        self.viewFrontAction.setEnabled(enableFlag)
        self.viewBackAction.setEnabled(enableFlag)
        self.viewTopAction.setEnabled(enableFlag)
        self.viewBottomAction.setEnabled(enableFlag)
        self.viewLeftAction.setEnabled(enableFlag)
        self.viewRightAction.setEnabled(enableFlag)
        self.viewIsometricAction.setEnabled(enableFlag)

        self.setViewHomeAction.setEnabled(enableFlag)
        self.setViewFitToWindowAction.setEnabled(enableFlag)
        self.setViewRecenterAction.setEnabled(enableFlag)

        self.viewFlipViewVertAction.setEnabled(enableFlag)
        self.viewFlipViewHorzAction.setEnabled(enableFlag)
        self.viewRotatePlus90Action.setEnabled(enableFlag)
        self.viewRotateMinus90Action.setEnabled(enableFlag)
        return

    def disable_QActions_for_extrudeMode(self, disableFlag = True):
        """
        Disables action items in the main window for extrudeMode.
        """
        self.disable_QActions_for_movieMode(disableFlag)
        self.modifyHydrogenateAction.setEnabled(not disableFlag)
        self.modifyDehydrogenateAction.setEnabled(not disableFlag)
        self.modifyPassivateAction.setEnabled(not disableFlag)
        self.modifyDeleteBondsAction.setEnabled(not disableFlag)
        self.modifyStretchAction.setEnabled(not disableFlag)
        self.modifySeparateAction.setEnabled(not disableFlag)
        self.modifyMergeAction.setEnabled(not disableFlag)
        self.modifyInvertAction.setEnabled(not disableFlag)
        self.modifyMirrorAction.setEnabled(not disableFlag)
        self.modifyAlignCommonAxisAction.setEnabled(not disableFlag)
        # All QActions in the Modify menu/toolbar should be disabled,
        # too. mark 060323
        return

    def disable_QActions_for_sim(self, disableFlag = True):
        """
        Disables actions items in the main window during simulations
        (and minimize).
        """
        self.disable_QActions_for_movieMode(disableFlag)
        self.simMoviePlayerAction.setEnabled(not disableFlag)
        return

    def disable_QActions_for_movieMode(self, disableFlag = True):
        """
        Disables action items in the main window for movieMode;
        also called by disable_QActions_for_extrudeMode
        and by disable_QActions_for_sim.
        """
        enable = not disableFlag
        self.modifyAdjustSelAction.setEnabled(enable) # "Adjust Selection"
        self.modifyAdjustAllAction.setEnabled(enable) # "Adjust All"
        self.simMinimizeEnergyAction.setEnabled(enable) # Minimize Energy
        self.checkAtomTypesAction.setEnabled(enable) # Check AMBER AtomTypes
        self.rosettaSetupAction.setEnabled(enable)
        self.simSetupAction.setEnabled(enable) # "Simulator"
        self.fileSaveAction.setEnabled(enable) # "File Save"
        self.fileSaveAsAction.setEnabled(enable) # "File Save As"
        self.fileOpenAction.setEnabled(enable) # "File Open"
        self.fileCloseAction.setEnabled(enable) # "File Close"
        self.fileInsertMmpAction.setEnabled(enable) # "Insert MMP"
        self.fileInsertPdbAction.setEnabled(enable) # "Insert PDB"
        self.fileInsertInAction.setEnabled(enable) # "Insert IN"
        self.editDeleteAction.setEnabled(enable) # "Delete"

        # [bruce 050426 comment: I'm skeptical of disabling zoom/pan/rotate,
        #  and suggest for some others (especially "simulator") that they
        #  auto-exit the mode rather than be disabled,
        #  but I won't revise these for now.]
        #
        # [update, bruce 070813/070820]
        # Zoom/pan/rotate are now rewritten to suspend rather than exit
        # the current mode, so they no longer need disabling in Extrude or
        # Movie modes. (There is one known minor bug (2517) -- Movie mode
        # asks whether to rewind (via popup dialog), which is only appropriate
        # to ask if it's being exited. Fixing this is relevant to the
        # upcoming "command sequencer".)
        # This is also called by disable_QActions_for_sim, and whether this
        # change is safe in that case is not carefully reviewed or tested,
        # but it seems likely to be ok.

##        self.zoomToAreaAction.setEnabled(enable) # "Zoom Tool"
##        self.panToolAction.setEnabled(enable) # "Pan Tool"
##        self.rotateToolAction.setEnabled(enable) # "Rotate Tool"

        return

# == Caption methods

    def update_mainwindow_caption_properly(self, junk = None): #bruce 050810 added this
        self.update_mainwindow_caption(self.assy.has_changed())
        # The call to updateWindowTitle() is harmless, even when MDI support
        # isn't enabled.
        self.activePartWindow().updateWindowTitle(self.assy.has_changed())

    def update_mainwindow_caption(self, changed = False): #by mark; bruce 050810 revised this in several ways, fixed bug 785
        """
        Update the window title (caption) at the top of the of the main window.
        Example:  "partname.mmp"

        @param changed: If True, the caption will include the prefix and
                        suffix (via user prefs settings in the
                        "Preferences | Window" dialog) to denote the part
                        has been modified.
        @type  changed: boolean

        @attention: I intend to remove the prefix and suffix user prefs and
        use the standard way applications indicate that a document has unsaved
        changes. On Mac OS X the close button will have a modified look;
        on other platforms the window title will have an '*' (asterisk).
        BTW, this has already been done in PartWindow.updateWindowTitle().
        Mark 2008-01-02.

        @see: U{B{windowTitle}<http://doc.trolltech.com/4/qwidget.html#windowTitle-prop>},
              U{B{windowModified}<http://doc.trolltech.com/4/qwidget.html#windowModified-prop>}
        """
        caption_prefix = env.prefs[captionPrefix_prefs_key]
        caption_suffix = env.prefs[captionSuffix_prefs_key]
        caption_fullpath = env.prefs[captionFullPath_prefs_key]

        if changed:
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
                partname = os.path.normpath(self.assy.filename)#fixed bug 453-1 ninad060721
            else:
                partname = basename

        except:
            partname = 'Untitled'

        ##e [bruce 050811 comment:] perhaps we should move prefix to the beginning, rather than just before "[";
        # and in any case the other stuff here, self.name() + " - " + "[" + "]", should also be user-changeable, IMHO.
        #print "****self.accessibleName *****=" , self.accessibleName()
        self.setWindowTitle(self.trUtf8("NanoEngineer-1" + " - " + prefix + "[" + partname.encode("utf_8") + "]" + suffix))

        return

    def createProgressDialog(self):
        """
        Creates the main window's Progress Dialog, which can be used to
        display a progress dialog at any time. It is modal by default.

        @see: _readmmp() for an example of use.
        @see: U{B{QProgressDialog}<http://doc.trolltech.com/4/qprogressdialog.html>}

        """
        from PyQt4.Qt import QProgressDialog
        self.progressDialog = QProgressDialog(self)
        self.progressDialog.setWindowModality(Qt.WindowModal)
        self.progressDialog.setWindowTitle("NanoEngineer-1")

        # setMinimumDuration() doesn't work. Qt bug?
        self.progressDialog.setMinimumDuration(500) # 500 ms = 0.5 seconds


    #= Methods for "Open Recent Files" menu, a submenu of the "Files" menu.

    def getRecentFilesListAndPrefsSetting(self):
        """
        Returns the list of recent files that appears in the "Open Recent Files"
        menu and the preference settings object.

        @return: List of recent files, preference settings.
        @rtype:  list, QSettings

        @see: U{B{QSettings}<http://doc.trolltech.com/4/qsettings.html>}
        """
        if recentfiles_use_QSettings:
            prefsSetting = QSettings("Nanorex", "NanoEngineer-1")
            fileList = prefsSetting.value(RECENTFILES_QSETTINGS_KEY).toStringList()
        else:
            prefsSetting = preferences.prefs_context()
            fileList = prefsSetting.get(RECENTFILES_QSETTINGS_KEY, [])

        return fileList, prefsSetting

    def updateRecentFileList(self, fileName):
        """
        Add I{filename} into the recent file list.

        @param filename: The filename to add to the recently opened files list.
        @type  filename: string
        """

        # LIST_CAPACITY could be set by user preference (NIY).
        LIST_CAPACITY = 9
            # Warning: Potential bug if number of recent files >= 10
            # (i.e. LIST_CAPACITY >= 10). See fileSlotsMixin.openRecentFile().

        fileName = os.path.normpath(str_or_unicode(fileName))

        fileList, prefsSetting = self.getRecentFilesListAndPrefsSetting()

        if len(fileList) > 0:
            # If filename is already in fileList, delete it from the list.
            # filename will be added to the top of the list later.
            for ii in range(len(fileList)):
                if str_or_unicode(fileName) == str_or_unicode(fileList[ii]):
                    del fileList[ii]
                    break

        if recentfiles_use_QSettings:
            fileList.prepend(fileName)
        else:
            fileList.insert(0, fileName)

        fileList = fileList[:LIST_CAPACITY]

        if recentfiles_use_QSettings:
            assert isinstance(prefsSetting, QSettings)
            prefsSetting.setValue(RECENTFILES_QSETTINGS_KEY, QVariant(fileList))

            if 0: #debug_recent_files:
                # confirm that the information really made it into the QSetting.
                fileListTest = prefsSetting.value(RECENTFILES_QSETTINGS_KEY).toStringList()
                fileListTest = map(str, list(fileListTest))
                assert len(fileListTest) == len(fileList)
                for i in range(len(fileList)):
                    assert str_or_unicode(fileList[i]) == str_or_unicode(fileListTest[i])
        else:
            prefsSetting[RECENTFILES_QSETTINGS_KEY] = fileList

        del prefsSetting

        self.createOpenRecentFilesMenu()
        return

    def createOpenRecentFilesMenu(self):
        """
        Creates the "Open Recent Files" menu, a submenu of the "File" menu.

        This is called whenever a new file is opened or the current file
        is renamed.
        """
        if hasattr(self, "openRecentFilesMenu"):
            # Remove the current "Open Recent Files" menu.
            # It will be recreated below.
            self.fileMenu.removeAction(self.openRecentFilesMenuAction)

        # Create a new "Open Recent Files" menu from the current list.
        self.openRecentFilesMenu = QMenu("Open Recent Files", self)

        fileList, prefsSetting = self.getRecentFilesListAndPrefsSetting()

        self.openRecentFilesMenu.clear()
        for ii in range(len(fileList)):
            _recent_filename = os.path.normpath(str_or_unicode(fileList[ii]).encode("utf_8")) # Fixes bug 2193. Mark 060808.
            self.openRecentFilesMenu.addAction(
                QtGui.QApplication.translate(
                    "Main Window",
                    "&" + str(ii + 1) + "  " + _recent_filename, None, QtGui.QApplication.UnicodeUTF8))

        # Insert the "Open Recent Files" menu above "File > Close".
        self.openRecentFilesMenuAction = \
            self.fileMenu.insertMenu(self.fileCloseAction,
                                     self.openRecentFilesMenu)

        self.connect(self.openRecentFilesMenu,
                     SIGNAL('triggered(QAction*)'),
                     self.openRecentFile)
        return

    def colorSchemeCommand(self):
        """
        This is a slot method for invoking the B{Color Scheme} command.
        """
        self.enterOrExitTemporaryCommand('COLOR_SCHEME') 
                
    def lightingSchemeCommand(self):
        """
        This is a slot method for invoking the B{Lighting Scheme} command.
        """
        self.enterOrExitTemporaryCommand('LIGHTING_SCHEME')
        
                
    def toggleRulers(self, isChecked):
        """
        Displays/hides the rulers in the 3D graphics area (glpane).

        @param isChecked: Checked state of the B{View > Rulers} menu item
        @type  isChecked: boolean
        """
        if isChecked:
            env.prefs[displayRulers_prefs_key] = True
        else:
            env.prefs[displayRulers_prefs_key] = False

    pass # end of class MWsemantics

# end

