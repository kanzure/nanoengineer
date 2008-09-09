# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
movieMode.py -- movie player mode.

@author: Mark
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:

By Mark.

bruce 050426 revising it, for Alpha5, mostly to fix bugs and perhaps to generalize it.
Adding various comments and revising docstrings; perhaps not signing every such change.
(Most movie code revisions will be in other files, and most revisions here will
 probably just be to adapt this file to the external changes.)

ninad20070507: moved Movie Player dashboard to Movie Property Manager.
ninad2008-08-21: Cleanup: a) to introduce command_enter/exit_* methods in the 
                  new Command API b) Moved flyouttoolbar related code in its own 
                  module (Ui_PlayMovieFlyout)
"""

import os
from PyQt4.Qt import Qt
from PyQt4.Qt import QDialog, QGridLayout, QPushButton, QTextBrowser, SIGNAL, QCursor
import foundation.env as env
import foundation.changes as changes
from command_support.modes import basicMode
from utilities.Log import redmsg, orangemsg
from commands.PlayMovie.MoviePropertyManager import MoviePropertyManager
from ne1_ui.toolbars.Ui_PlayMovieFlyout import PlayMovieFlyout
import foundation.undo_manager as undo_manager
from utilities.GlobalPreferences import USE_COMMAND_STACK

class _MovieRewindDialog(QDialog):
    """
    Warn the user that a given movie is not rewound,
    explain why that matters, and offer to rewind it
    (by calling its _reset method).
    """
    def __init__(self, movie):
        self.movie = movie
        QDialog.__init__(self, None)
        self.setObjectName("movie_warning")
        self.text_browser = QTextBrowser(self)
        self.text_browser.setObjectName("movie_warning_textbrowser")
        self.text_browser.setMinimumSize(400, 40)
        self.setWindowTitle('Rewind your movie?')
        self.text_browser.setPlainText( #bruce 080827 revised text
            "You may want to rewind the movie now. The atoms move as the movie "
            "progresses, and saving the part without rewinding will save the "
            "current positions, which is sometimes useful, but will make the "
            "movie invalid, because .dpb files only store deltas relative to "
            "the initial atom positions, and don't store the initial positions "
            "themselves." )
        self.ok_button = QPushButton(self)
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setText("Rewind movie")
        self.cancel_button = QPushButton(self)
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setText("Exit command without rewinding") #bruce 080827 revised text
            # Note: this is not, in fact, a cancel button --
            # there is no option in the caller to prevent exiting the command.
            # There is also no option to "forward to final position",
            # though for a minimize movie, that might be most useful.
            # [bruce 080827 comment]
        layout = QGridLayout(self)
        layout.addWidget(self.text_browser, 0, 0, 0, 1)
        layout.addWidget(self.ok_button, 1, 0)
        layout.addWidget(self.cancel_button, 1, 1)
        self.connect(self.ok_button, SIGNAL("clicked()"), self.rewindMovie)
        self.connect(self.cancel_button, SIGNAL("clicked()"), self.noThanks)
    def rewindMovie(self):
        self.movie._reset()
        self.accept()
    def noThanks(self):
        self.accept()
    pass

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

    PM_class = MoviePropertyManager #bruce 080909
    
    flyoutToolbar = None

    # methods related to entering or exiting this mode

    def Enter(self):
        basicMode.Enter(self)
        # [bruce 050427 comment: I'm skeptical of this effect on selection,
        #  since I can't think of any good reason for it [maybe rendering speed optimization??],
        #  and once we have movies as nodes in the MT it will be a problem [why? #k],
        #  but for now I'll leave it in.]
        self.o.assy.unpickall_in_GLPane() # was: unpickparts, unpickatoms [bruce 060721]
        self.o.assy.permit_pick_atoms()

    def _exitMode(self, *args, **kws): # for not-USE_COMMAND_STACK case; happens for Done or Cancel; remove when USE_COMMAND_STACK
        # note: this definition generates the debug print
        ## fyi (for developers): subclass movieMode overrides basicMode._exitMode; this is deprecated after mode changes of 040924.
        # because it's an API violation to override this method; what should be done instead is to do this in one of the other cleanup
        # functions documented in modes.py. Sometime that doc should be clarified and this method should be redone properly.
        # [bruce 070613 comment]

        self._offer_to_rewind_if_necessary()
        
        basicMode._exitMode(self, *args, **kws)
        return

    def command_will_exit(self): # for USE_COMMAND_STACK case; happens for any exit [bruce 080806]
        """
        Extends superclass method, to offer to rewind the movie
        if it's not at the beginning. (Doesn't offer to prevent
        exit, only to rewind or not when exit is done.)
        """
        if USE_COMMAND_STACK:
            ask = not self.commandSequencer.exit_is_forced
                # It's not be safe to rewind if exit is forced,
                # since this might happen *after* the check for whether
                # to offer to save changes in an old file being closed,
                # but it creates such changes.
                #
                # A possible fix is for Open to first exit all current commands
                # (by implicit Done, as when changing to some unrelated command),
                # before even doing the check. There are better, more complex fixes,
                # e.g. checking for changes to ask about saving (or for the need to
                # ask other questions before exit) by asking all commands on the stack.
                #
                # Note: a related necessary change is calling exit_all_commands when
                # closing a file, but I think it doesn't fix the same issue mentioned
                # above.
                #
                # [bruce 080806/080908 comments]
        else:
            ask = True
        if ask:
            self._offer_to_rewind_if_necessary()

        # copied the old self.restore_patches_by_Command():
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
        
        basicMode.command_will_exit(self)
        return

    def _offer_to_rewind_if_necessary(self): #bruce 080806 split this out
        # TODO: add an option to the PM to always say yes or no to this,
        # e.g. a 3-choice combobox for what to do if not rewound on exit
        # (rewind, don't rewind, or ask). [bruce 080806 suggestion]
        movie = self.o.assy.current_movie
        if movie and movie.currentFrame != 0:
            # note: if the movie file stores absolute atom positions,
            # there is no need to call this. Currently, we only support
            # .dpb files, which don't store them.
            # note: if we entered this on a nonzero frame, it might
            # be more useful to compare to and offer to rewind to
            # that frame (perhaps in addition to frame 0).
            # [bruce 080827 comments]
            mrd = _MovieRewindDialog(movie)
                # rewind (by calling movie._reset()), if user desires it
                # (see text and comments in that class)
            mrd.exec_()
        return
    
    def init_gui(self):
        self.command_enter_PM()
        self.command_enter_flyout()
        self.command_enter_misc_actions()

            
    #START new command API methods =============================================
    #currently [2008-08-21 ] also called in by self.init_gui and 
    #self.restore_gui.
    
    # see also command_will_exit, elsewhere in this file
    
    def command_enter_PM(self):
        """
        Extends superclass method.         
        @see: baseCommand.command_enter_PM()  for documentation        
        """
##        #important to check for old propMgr object. Reusing propMgr object 
##        #significantly improves the performance.
##        if not self.propMgr:
##            self.propMgr = self._createPropMgrObject()
##            #@bug BUG: following is a workaround for bug 2494.
##            #This bug is mitigated as propMgr object no longer gets recreated
##            #for modes -- ninad 2007-08-29
##            changes.keep_forever(self.propMgr)
        basicMode.command_enter_PM(self) #bruce 080909 call this instead of inlining it
            
        if not USE_COMMAND_STACK:
            self.propMgr.show()             
            
        #@WARNING: The following code in command_enter_PM was originally in 
        #def init_gui method. Its copied 'as is' from there.-- Ninad 2008-08-21       
        
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

        self.propMgr.frameNumberSpinBox.setValue(frameno, blockSignals = True) 
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
        return
    
    def command_exit_PM(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_PM() for documentation
        """
        if not USE_COMMAND_STACK:
            if self.propMgr:
                self.propMgr.close()
            
    def command_enter_flyout(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_flyout()  for documentation
        """
        if self.flyoutToolbar is None:
            self.flyoutToolbar = self._createFlyoutToolBarObject() 
        self.flyoutToolbar.activateFlyoutToolbar()  
            
    def command_exit_flyout(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_flyout()  for documentation
        """
        if self.flyoutToolbar:
            self.flyoutToolbar.deActivateFlyoutToolbar()
            
    def command_enter_misc_actions(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_enter_misc_actions()  for documentation
        """
        #@WARNING: The following code in  was originally in 
        #def init_gui method. Its copied 'as is' from there.-- Ninad 2008-08-21
        
        self.w.simMoviePlayerAction.setChecked(1) # toggle on the Movie Player icon+

        # Disable some action items in the main window.
        # [bruce 050426 comment: I'm skeptical of disabling the ones marked #k
        #  and suggest for some others (especially "simulator") that they
        #  auto-exit the mode rather than be disabled,
        #  but I won't revise these for now.]
        self.w.disable_QActions_for_movieMode(True)
            #  Actions marked #k are now in disable_QActions_for_movieMode(). mark 060314)

        # Disable Undo/Redo actions, and undo checkpoints, during this mode (they *must* be reenabled in restore_gui).
        # We do this last, so as not to do it if there are exceptions in the rest of the method,
        # since if it's done and never undone, Undo/Redo won't work for the rest of the session.
        # [bruce 060414; same thing done in some other modes]
        
        undo_manager.disable_undo_checkpoints('Movie Player')
        undo_manager.disable_UndoRedo('Movie Player', "in Movie Player") # optimizing this for shortness in menu text
            # this makes Undo menu commands and tooltips look like "Undo (not permitted in Movie Player)" (and similarly for Redo)
 
            
    def command_exit_misc_actions(self):
        """
        Overrides superclass method. 
        
        @see: baseCommand.command_exit_misc_actions()  for documentation
        """
        #@WARNING: The following code in  was originally in 
        #def restore_gui method. Its copied 'as is' from there.-- Ninad 2008-08-21
        
        # Reenable Undo/Redo actions, and undo checkpoints (disabled in init_gui);
        # do it first to protect it from exceptions in the rest of this method
        # (since if it never happens, Undo/Redo won't work for the rest of the session)
        # [bruce 060414; same thing done in some other modes]
        undo_manager.reenable_undo_checkpoints('Movie Player')
        undo_manager.reenable_UndoRedo('Movie Player')

        self.w.simMoviePlayerAction.setChecked(0) # toggle on the Movie Player icon
        self.set_cmdname('Movie Player') # this covers all changes while we were in the mode
            # (somewhat of a kluge, and whether this is the best place to do it is unknown;
            #  without this the cmdname is "Done")
        self.w.disable_QActions_for_movieMode(False)   
    
    def _createFlyoutToolBarObject(self):
        """
        Create a flyout toolbar to be shown when this command is active. 
        Overridden in subclasses. 
        @see: self.command_enter_flyout()
        """
        flyoutToolbar = PlayMovieFlyout(self) 
        return flyoutToolbar 
    
    #END new command API methods =============================================
    
    def enableMovieControls(self, enabled = True):
        self.propMgr.enableMovieControls(enabled)

    def might_be_playable(self):
        """
        Do we have a current movie which is worth trying to play?
        """
        movie = self.o.assy.current_movie
        return movie and movie.might_be_playable()

    def restore_patches_by_Command(self):
        """
        This is run when we exit self for any reason.
        """
        assert not USE_COMMAND_STACK # done in command_will_exit in that case
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

    def restore_gui(self):
        self.command_exit_PM()
        self.command_exit_flyout()
        self.command_exit_misc_actions()
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

        basicMode.keyPress(self, key) # So F1 Help key works. mark 060321

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
        win.commandSequencer.userEnterCommand('MOVIE', always_update = True)
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
            win.commandSequencer.userEnterCommand('MOVIE', always_update = True)
            return
    # else if no assy.filename or no movie found from that:
    # bruce 050327 comment -- do what the old code did, except for the moviePlay
    # which seems wrong and tracebacks now.
    assy.current_movie = Movie(assy)
        # temporary kluge until bugs in movieMode for no assy.current_movie are fixed
    win.commandSequencer.userEnterCommand('MOVIE', always_update = True)
    return

# end
