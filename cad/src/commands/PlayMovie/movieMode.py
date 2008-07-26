# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""
movieMode.py -- movie player mode.

@author: Mark
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

History:

By Mark.

bruce 050426 revising it, for Alpha5, mostly to fix bugs and perhaps to generalize it.
Adding various comments and revising docstrings; perhaps not signing every such change.
(Most movie code revisions will be in other files, and most revisions here will
 probably just be to adapt this file to the external changes.)

ninad20070507: moved Movie Player dashboard to Movie Property Manager.
"""

import os

from PyQt4.Qt import Qt
from PyQt4.Qt import QDialog, QGridLayout, QPushButton, QTextBrowser, SIGNAL, QCursor
from PyQt4.Qt import QMessageBox, QString, QWidgetAction, QAction

import foundation.env as env
import foundation.changes as changes

from simulation.movie import find_saved_movie
from command_support.modes import basicMode
from utilities.Log import greenmsg
from utilities.Log import redmsg, orangemsg
from commands.PlayMovie.MoviePropertyManager import MoviePropertyManager
from utilities.icon_utilities import geticon

from utilities.prefs_constants import workingDirectory_prefs_key
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction

class MovieRewindDialog(QDialog):

    def __init__(self, movie):
        self.movie = movie
        QDialog.__init__(self, None)
        self.setObjectName("movie_warning")
        self.text_browser = QTextBrowser(self)
        self.text_browser.setObjectName("movie_warning_textbrowser")
        self.text_browser.setMinimumSize(400, 40)
        self.setWindowTitle('Rewind your movie?')
        self.text_browser.setPlainText(
            "You may want to rewind the movie now. If you save the part without " +
            "rewinding the movie, the movie file will become invalid because it " +
            "depends upon the initial atom positions. The atoms move as the movie " +
            "progresses, and saving the part now will save the final positions, " +
            "which are incorrect for the movie you just watched.")
        self.ok_button = QPushButton(self)
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setText("Rewind movie")
        self.cancel_button = QPushButton(self)
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setText("No thanks")
        layout = QGridLayout(self)
        layout.addWidget(self.text_browser,0,0,0,1)
        layout.addWidget(self.ok_button,1,0)
        layout.addWidget(self.cancel_button,1,1)
        self.connect(self.ok_button,SIGNAL("clicked()"),self.rewindMovie)
        self.connect(self.cancel_button,SIGNAL("clicked()"),self.noThanks)
    def rewindMovie(self):
        self.movie._reset()
        self.accept()
    def noThanks(self):
        self.accept()

####@@@@ It might need removing from other places in the code, as well, like entering the mode.

###doc

class movieMode(basicMode):
    """
    This class is used to play movie files.
    Users know it as "Movie mode".
    When entered, it might start playing a recently-made movie,
    or continue playing the last movie it was playing,
    or do nothing and wait for the user to open a new movie.
    The movie it is working with (if any) is always stored in assy.current_movie.
    In general, if assy.current_movie is playable when the mode is entered,
    it will start playing it. [I don't know the extent to which it will start
    from where it left off, in not only frame number but direction, etc. - bruce 050426]
    """

    # class constants
    commandName = 'MOVIE'
    featurename = "Movie Player Mode"
    from utilities.constants import CL_MISC_TOPLEVEL
    command_level = CL_MISC_TOPLEVEL

    # methods related to entering this mode

    def Enter(self):
        basicMode.Enter(self)
        # [bruce 050427 comment: I'm skeptical of this effect on selection,
        #  since I can't think of any good reason for it [maybe rendering speed optimization??],
        #  and once we have movies as nodes in the MT it will be a problem [why? #k],
        #  but for now I'll leave it in.]
        self.o.assy.unpickall_in_GLPane() # was: unpickparts, unpickatoms [bruce 060721]
        self.o.assy.permit_pick_atoms()

    def _exitMode(self, *args, **kws):
        # note: this definition generates the debug print
        ## fyi (for developers): subclass movieMode overrides basicMode._exitMode; this is deprecated after mode changes of 040924.
        # because it's an API violation to override this method; what should be done instead is to do this in one of the other cleanup
        # functions documented in modes.py. Sometime that doc should be clarified and this method should be redone properly.
        # [bruce 070613 comment]
        movie = self.o.assy.current_movie
        if movie and movie.currentFrame is not 0:
            mrd = MovieRewindDialog(movie)
            mrd.exec_()
        basicMode._exitMode(self, *args, **kws)

    def init_gui(self):

        if not self.propMgr:
            self.propMgr = MoviePropertyManager(self)
            #@bug BUG: following is a workaround for bug 2494
            changes.keep_forever(self.propMgr)

        #@NOTE: self.propMgr.show() is called later in this (init_gui) method.

        self.updateCommandToolbar(bool_entering = True)

        self.w.simMoviePlayerAction.setChecked(1) # toggle on the Movie Player icon+

        # Disable some action items in the main window.
        # [bruce 050426 comment: I'm skeptical of disabling the ones marked #k
        #  and suggest for some others (especially "simulator") that they
        #  auto-exit the mode rather than be disabled,
        #  but I won't revise these for now.]
        self.w.disable_QActions_for_movieMode(True)
            #  Actions marked #k are now in disable_QActions_for_movieMode(). mark 060314)

        # MP dashboard initialization.
        self.enableMovieControls(False)
            #bruce 050428 precaution (has no noticable effect but seems safer in theory)
        #bruce 050428, working on bug 395: I think some undesirable state is left in the dashboard, so let's reinit it
        # (and down below we might like to init it from the movie if possible, but it's not always possible).
        self.propMgr._moviePropMgr_reinit() ###e could pass frameno? is max frames avail yet in all playable movies? not sure.
        # [bruce 050426 comment: probably this should just be a call of an update method, also used during the mode ###e]
        movie = self.o.assy.current_movie # might be None, but might_be_playable() true implies it's not
        if self.might_be_playable(): #bruce 050426 added condition
            frameno = movie.currentFrame
        else:
            frameno = 0 #bruce 050426 guessed value

        self.propMgr.frameNumberSpinBox.setValue(frameno) # bruce 050428 question: does this call our slot method?? ###k
        self.propMgr.moviePlayActiveAction.setVisible(0)
        self.propMgr.moviePlayRevActiveAction.setVisible(0)

        if self.might_be_playable(): # We have a movie file ready.  It's showtime! [bruce 050426 changed .filename -> .might_be_playable()]
            movie.cueMovie(propMgr = self.propMgr) # Cue movie.
            self.enableMovieControls(True)
            self.propMgr.updateFrameInformation()
            if movie.filename: #k not sure this cond is needed or what to do if not true [bruce 050510]
                env.history.message( "Movie file ready to play: %s" % movie.filename) #bruce 050510 added this message
        else:
            self.enableMovieControls(False)

        #Need to do this after calling movie._setUp (propMgr displays movie
        #information in its msg groupbox.  All this will be cleaned up when we
        #do moviemode code cleanup.

        self.propMgr.show()

        # Disable Undo/Redo actions, and undo checkpoints, during this mode (they *must* be reenabled in restore_gui).
        # We do this last, so as not to do it if there are exceptions in the rest of the method,
        # since if it's done and never undone, Undo/Redo won't work for the rest of the session.
        # [bruce 060414; same thing done in some other modes]
        import foundation.undo_manager as undo_manager
        undo_manager.disable_undo_checkpoints('Movie Player')
        undo_manager.disable_UndoRedo('Movie Player', "in Movie Player") # optimizing this for shortness in menu text
            # this makes Undo menu commands and tooltips look like "Undo (not permitted in Movie Player)" (and similarly for Redo)
        self.connect_or_disconnect_signals(True)

    def connect_or_disconnect_signals(self, connect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot
                          method.
        @type  isConnect: boolean
        """
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect

        change_connect(self.exitMovieAction,
                       SIGNAL("triggered()"),
                       self.w.toolsDone)

        self.propMgr.connect_or_disconnect_signals(connect)

    def getFlyoutActionList(self): #Ninad 20070618
        """
        Returns custom actionlist that will be used in a specific mode
        or editing a feature etc Example: while in movie mode,
        the _createFlyoutToolBar method calls
        this.
        """

        #'allActionsList' returns all actions in the flyout toolbar
        #including the subcontrolArea actions
        allActionsList = []

        #Action List for  subcontrol Area buttons.
        #In this mode there is really no subcontrol area.
        #We will treat subcontrol area same as 'command area'
        #(subcontrol area buttons will have an empty list as their command area
        #list). We will set  the Comamnd Area palette background color to the
        #subcontrol area.

        subControlAreaActionList =[]

        self.exitMovieAction = NE1_QWidgetAction(self.w, win = self.w)
        self.exitMovieAction.setText("Exit Movie")
        self.exitMovieAction.setWhatsThis("Exits Movie Mode")
        self.exitMovieAction.setCheckable(True)
        self.exitMovieAction.setChecked(True)
        self.exitMovieAction.setIcon(
            geticon("ui/actions/Toolbars/Smart/Exit.png"))
        subControlAreaActionList.append(self.exitMovieAction)

        separator = QAction(self.w)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator)

        subControlAreaActionList.append(self.w.simPlotToolAction)

        allActionsList.extend(subControlAreaActionList)

        #Empty actionlist for the 'Command Area'
        commandActionLists = []

        #Append empty 'lists' in 'commandActionLists equal to the
        #number of actions in subControlArea
        for i in range(len(subControlAreaActionList)):
            lst = []
            commandActionLists.append(lst)

        params = (subControlAreaActionList, commandActionLists, allActionsList)

        return params

    def updateCommandToolbar(self, bool_entering = True):#Ninad 20070618
        """
        Update the command toolbar.
        """
        # object that needs its own flyout toolbar. In this case it is just
        #the mode itself.

        action = self.w.simMoviePlayerAction
        obj = self
        self.w.commandToolbar.updateCommandToolbar(action,
                                                   obj,
                                                   entering = bool_entering)
        return

    def enableMovieControls(self, enabled = True):
        self.propMgr.enableMovieControls(enabled)

    def might_be_playable(self):
        """
        Do we have a current movie which is worth trying to play?
        """
        movie = self.o.assy.current_movie
        return movie and movie.might_be_playable()

    def update_dashboard_OBS(self): #bruce 050426 pieced this together from other code ####@@@@ call it
        """
        Update our dashboard to reflect the state of assy.current_movie.
        """
        self.enableMovieControls( self.might_be_playable() )
        ###e need to do more here, like the stuff in init_gui and maybe elsewhere
        return

    def restore_patches_by_Command(self):
        """
        This is run when we exit the mode for any reason.
        """
        #bruce 050426 added this, to hold the side effect formerly
        # done illegally by haveNontrivialState.
        # ... but why do we need to do this at all?
        # the only point of what we'd do here would be to stop
        # having that movie optimize itself for rapid playing....
        movie = self.o.assy.current_movie
        if movie:
            movie._close()
            # note: this assumes this is the only movie which might be "open",
            # and that redundant _close is ok.
        return

    def haveNontrivialState(self):
        ##bruce 050426: This used to call self.o.assy.current_movie._close()
        # but that's wrong (this method shouldn't have side effects),
        # so I moved that to our custom restore_patches_by_Command() method.
        # Also, this used to always return False; that's still ok as long as we continually modify
        # the model and tell it so (assy.changed) -- but I'm not sure we do; this needs review. ###k ####@@@@
        # (Current strategy, 050426 eve: ignore this and assy.changed issues, until done.)
        return False

    ##bruce 050426: maybe Done should store the movie changes and Cancel should revert to prior state?? If so, revise this. ####@@@@
##    def StateDone(self):
##        self.o.assy.current_movie._close()
##        return None

    def restore_gui(self):

        self.propMgr.close()

        # Reenable Undo/Redo actions, and undo checkpoints (disabled in init_gui);
        # do it first to protect it from exceptions in the rest of this method
        # (since if it never happens, Undo/Redo won't work for the rest of the session)
        # [bruce 060414; same thing done in some other modes]
        import foundation.undo_manager as undo_manager

        undo_manager.reenable_undo_checkpoints('Movie Player')
        undo_manager.reenable_UndoRedo('Movie Player')

        self.w.simMoviePlayerAction.setChecked(0) # toggle on the Movie Player icon
        self.set_cmdname('Movie Player') # this covers all changes while we were in the mode
            # (somewhat of a kluge, and whether this is the best place to do it is unknown;
            #  without this the cmdname is "Done")

        self.updateCommandToolbar(bool_entering = False)
        self.w.disable_QActions_for_movieMode(False)

        self.connect_or_disconnect_signals(False)

        return

    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Reset Movie', self.ResetMovie),
            ('Done', self.Done),
            None,
            ('Edit Color Scheme...', self.w.colorSchemeCommand),
        ]

    def ResetMovie(self):
        #bruce 050325 revised or made this, since .current_movie can change
        if self.o.assy.current_movie:
            self.o.assy.current_movie._reset()

    def Draw(self):
        basicMode.Draw(self)
        self.o.assy.draw(self.o)

    # mouse and key events

    def keyPress(self, key):

        # Disable delete key
        if key == Qt.Key_Delete:
            return

        movie = self.o.assy.current_movie
        if not movie:
            return

        # Left or Down arrow keys - advance back one frame
        if key == Qt.Key_Left or key == Qt.Key_Down:
            movie._playToFrame(movie.currentFrame - 1)

        # Right or Up arrow keys - advance forward one frame
        if key == Qt.Key_Right or key == Qt.Key_Up:
            movie._playToFrame(movie.currentFrame + 1)

        basicMode.keyPress(self,key) # So F1 Help key works. mark 060321

        return

    def update_cursor_for_no_MB(self): # Fixes bug 1693. mark 060321
        """
        Update the cursor for 'Movie Player' mode.
        """
        self.o.setCursor(QCursor(Qt.ArrowCursor))

# ==

def simMoviePlayer(assy):
    """
    Plays a DPB movie file created by the simulator,
    either the current movie if any, or a previously saved
    dpb file with the same name as the current part, if one can be found.
    """
    from simulation.movie import find_saved_movie, Movie #bruce 050329 precaution (in case of similar bug to bug 499)
    win = assy.w
    if not assy.molecules: # No model, so no movie could be valid for current part.
        # bruce 050327 comment: even so, a movie file might be valid for some other Part...
        # not yet considered here. [050427 addendum: note that user can't yet autoload a new Part
        # just by opening a movie file, so there's no point in going into the mode -- it's only meant
        # for playing a movie for the *current contents of the current part*, for now.]
        env.history.message(redmsg("Movie Player: Need a model."))
        win.simMoviePlayerAction.setChecked(0) # toggle on the Movie Player icon ninad 061113
        return

    if assy.current_movie and assy.current_movie.might_be_playable():
        win.commandSequencer.userEnterCommand('MOVIE')
        return

    # no valid current movie, look for saved one with same name as assy
    ## env.history.message("Plot Tool: No simulation has been run yet.")
    if assy.filename:
        if assy.part is not assy.tree.part:
            msg = "Movie Player: Warning: Looking for saved movie for main part, not for displayed clipboard item."
            env.history.message(orangemsg(msg))
        errorcode, partdir = assy.find_or_make_part_files_directory()
        if not errorcode: # filename could be an MMP or PDB file.
            dir, fil = os.path.split(assy.filename)
            fil, ext = os.path.splitext(fil)
            mfile = os.path.join(partdir, fil + '.dpb')
        else:
            mfile = os.path.splitext(assy.filename)[0] + ".dpb"
        movie = find_saved_movie( assy, mfile)
            # checks existence -- should also check validity for current part or main part, but doesn't yet ###e
            # (neither did the pre-030527 code for this function, unless that's done in moviePlay, which it might be)
        if movie:
            # play this movie, and make it the current movie.
            assy.current_movie = movie
            #e should we switch to the part for which this movie was made? [might be done in moviePlay; if not:]
            # No current way to tell how to do that, and this might be done even if it's not valid
            # for any loaded Part. So let's not... tho we might presume (from filename choice we used)
            # it was valid for Main Part. Maybe print warning for clip item, and for not valid? #e
            env.history.message("Movie Player: %s previously saved movie for this part." % ("playing" or "loading"))
            win.commandSequencer.userEnterCommand('MOVIE')
            return
    # else if no assy.filename or no movie found from that:
    # bruce 050327 comment -- do what the old code did, except for the moviePlay
    # which seems wrong and tracebacks now.
    assy.current_movie = Movie(assy)
        # temporary kluge until bugs in movieMode for no assy.current_movie are fixed
    win.commandSequencer.userEnterCommand('MOVIE')
    return

# end
