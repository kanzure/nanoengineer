# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
"""
movieMode.py -- movie player mode.

$Id$

History:

By Mark.

bruce 050426 revising it, for Alpha5, mostly to fix bugs and perhaps to generalize it.
Adding various comments and revising docstrings; perhaps not signing every such change.
(Most movie code revisions will be in other files, and most revisions here will
 probably just be to adapt this file to the external changes.)

bruce 050913 used env.history in some places.
"""

__author__ = "Mark"

from modes import *
from HistoryWidget import redmsg, orangemsg

from qt import QFileDialog, QMessageBox, QString, QMimeSourceFactory

import env

auto_play = False # whether to automatically start playing the movie when you enter the mode
    # bruce 050510 disabling automatic play per Mark urgent request (this is also a bug or NFR in bugzilla).
    # Not sure whether this will need to be added back under certain conditions,
    # therefore I'm adding this flag, so it's easy to review all the places that might need changing.


####@@@@ It might need removing from other places in the code, as well, like entering the mode.

###doc

class movieMode(basicMode):
    """ This class is used to play movie files.
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
    backgroundColor = 189/255.0, 228/255.0, 238/255.0
    modename = 'MOVIE'
    default_mode_status_text = "Mode: Movie Player"
    
    # methods related to entering this mode
    
    def Enter(self):
        basicMode.Enter(self)
        # [bruce 050427 comment: I'm skeptical of this effect on selection,
        #  since I can't think of any good reason for it,
        #  and once we have movies as nodes in the MT it will be a problem,
        #  but for now I'll leave it in.]
        self.o.assy.unpickatoms()
        self.o.assy.unpickparts()
        self.o.assy.permit_pick_atoms() #bruce 050517 revised API of this call

    def init_gui(self):

        self.w.simMoviePlayerAction.setOn(1) # toggle on the Movie Player icon

        # Disable some action items in the main window.
        # [bruce 050426 comment: I'm skeptical of disabling the ones marked #k 
        #  and suggest for some others (especially "simulator") that they
        #  auto-exit the mode rather than be disabled,
        #  but I won't revise these for now.]
        self.w.disable_QActions_for_movieMode(True)
            #  Actions marked #k are now in disable_QActions_for_movieMode(). mark 060314)
        
        # MP dashboard initialization.
        self._controls(0) # bruce 050428 precaution (has no noticable effect but seems safer in theory)
        #bruce 050428, working on bug 395: I think some undesirable state is left in the dashboard, so let's reinit it
        # (and down below we might like to init it from the movie if possible, but it's not always possible).
        self.w._movieDashboard_reinit() ###e could pass frameno? is max frames avail yet in all playable movies? not sure.
        # [bruce 050426 comment: probably this should just be a call of an update method, also used during the mode ###e]
        movie = self.o.assy.current_movie # might be None, but might_be_playable() true implies it's not
        if self.might_be_playable(): #bruce 050426 added condition
            frameno = movie.currentFrame
        else:
            frameno = 0 #bruce 050426 guessed value
        self.w.frameNumberSB.setValue(frameno) # SB = Spinbox [bruce 050428 question: does this call our slot method?? ###k]
        self.w.moviePlayActiveAction.setVisible(0)
        self.w.moviePlayRevActiveAction.setVisible(0)
        self.w.moviePlayerDashboard.show()
        
        if self.might_be_playable(): # We have a movie file ready.  It's showtime! [bruce 050426 changed .filename -> .might_be_playable()]
            movie._setup() # Cue movie. [bruce 050501 comment: I don't think this actually starts playing it, and I hope not.]
            if movie.filename: #k not sure this cond is needed or what to do if not true [bruce 050510]
                env.history.message( "Movie file ready to play: %s" % movie.filename) #bruce 050510 added this message
        else:
            self._controls(0) # Movie control buttons are disabled.

        # Disable Undo/Redo actions, and undo checkpoints, during this mode (they *must* be reenabled in restore_gui).
        # We do this last, so as not to do it if there are exceptions in the rest of the method,
        # since if it's done and never undone, Undo/Redo won't work for the rest of the session.
        # [bruce 060414; same thing done in some other modes]
        import undo_manager
        undo_manager.disable_undo_checkpoints('Movie Player')
        undo_manager.disable_UndoRedo('Movie Player', "in Movie Player") # optimizing this for shortness in menu text
            # this makes Undo menu commands and tooltips look like "Undo (not permitted in Movie Player)" (and similarly for Redo)

    def _controls(self, On = True): #bruce 050427
        _controls( self.w, On)

    def might_be_playable(self):
        "Do we have a current movie which is worth trying to play?"
        movie = self.o.assy.current_movie
        return movie and movie.might_be_playable()
    
    def update_dashboard(self): #bruce 050426 pieced this together from other code ####@@@@ call it
        """Update our dashboard to reflect the state of assy.current_movie."""
        self._controls( self.might_be_playable() )
        ###e need to do more here, like the stuff in init_gui and maybe elsewhere
        return

    def restore_patches(self): #bruce 050426 added this, to hold the side effect formerly done illegally by haveNontrivialState.
        "This is run when we exit the mode for any reason."
        #bruce 050426 continues commentary:
        # ... but why do we need to do this at all?
        # the only point of what we'd do here would be to stop
        # having that movie optimize itself for rapid playing....
        movie = self.o.assy.current_movie
        if movie:
            movie._close() # assume this is the only movie which might be "open", and that redundant _close is ok.
        return
        
    def haveNontrivialState(self):
        ##bruce 050426: This used to call self.o.assy.current_movie._close()
        # but that's wrong (this method shouldn't have side effects),
        # so I moved that to our custom restore_patches() method.
        # Also, this used to always return False; that's still ok as long as we continually modify
        # the model and tell it so (assy.changed) -- but I'm not sure we do; this needs review. ###k ####@@@@
        # (Current strategy, 050426 eve: ignore this and assy.changed issues, until done.)
        return False

    ##bruce 050426: maybe Done should store the movie changes and Cancel should revert to prior state?? If so, revise this. ####@@@@
##    def StateDone(self):
##        self.o.assy.current_movie._close()
##        return None

    def restore_gui(self):
        "[#doc]"
        # Reenable Undo/Redo actions, and undo checkpoints (disabled in init_gui);
        # do it first to protect it from exceptions in the rest of this method
        # (since if it never happens, Undo/Redo won't work for the rest of the session)
        # [bruce 060414; same thing done in some other modes]
        import undo_manager
        undo_manager.reenable_undo_checkpoints('Movie Player')
        undo_manager.reenable_UndoRedo('Movie Player')
        self.set_cmdname('Movie Player') # this covers all changes while we were in the mode
            # (somewhat of a kluge, and whether this is the best place to do it is unknown;
            #  without this the cmdname is "Done")

        self.w.moviePlayerDashboard.hide()
        self.w.disable_QActions_for_movieMode(False)
        return

    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Reset Movie', self.ResetMovie),
            ('Done', self.Done)
         ]

    def ResetMovie(self):
        #bruce 050325 revised or made this, since .current_movie can change
        if self.o.assy.current_movie:
            self.o.assy.current_movie._reset()
        
    def Draw(self):
        basicMode.Draw(self)
        self.o.assy.draw(self.o)

    # mouse and key events
            
    def keyPress(self,key):
        
        # Disable delete key
        if key == Qt.Key_Delete: return
        
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
        '''Update the cursor for 'Movie Player' mode.
        '''
        self.o.setCursor(QCursor(Qt.ArrowCursor))

# ==

def _controls(win, On = True):
    """Enable or disable movie controls on movieMode dashboard."""
    #bruce 050427 moved this here -- it was a method on class Movie.
    #e It probably should become a method of the mixin class.
    win.movieResetAction.setEnabled(On)
    win.moviePlayRevAction.setEnabled(On)
    win.moviePauseAction.setEnabled(On)
    win.moviePlayAction.setEnabled(On)
    win.movieMoveToEndAction.setEnabled(On)
    win.frameNumberSL.setEnabled(On)
    win.frameNumberSB.setEnabled(On)
    win.fileSaveMovieAction.setEnabled(On)

def simMoviePlayer(assy):
    """Plays a DPB movie file created by the simulator,
    either the current movie if any, or a previously saved
    dpb file with the same name as the current part, if one can be found.
    """
    # moved here from MWsemantics method, and fixed bugs I recently put into it 
    # (by rewriting it from original and from rewritten simPlot function)
    # [bruce 050327]
    from movie import find_saved_movie, Movie #bruce 050329 precaution (in case of similar bug to bug 499)
    win = assy.w
    if not assy.molecules: # No model, so no movie could be valid for current part.
        # bruce 050327 comment: even so, a movie file might be valid for some other Part...
        # not yet considered here. [050427 addendum: note that user can't yet autoload a new Part
        # just by opening a movie file, so there's no point in going into the mode -- it's only meant
        # for playing a movie for the *current contents of the current part*, for now.]
        env.history.message(redmsg("Movie Player: Need a model."))
        return

    if assy.current_movie and assy.current_movie.might_be_playable():
        win.glpane.setMode('MOVIE')
        if auto_play:
            win.moviePlay() # [bruce 050427 guess: simulate pressing the play button]
        return

    # no valid current movie, look for saved one with same name as assy
    ## env.history.message("Plot Tool: No simulation has been run yet.")
    if assy.filename:
        if assy.part is not assy.tree.part:
            msg = "Movie Player: Warning: Looking for saved movie for main part, not for displayed clipboard item."
            env.history.message(orangemsg(msg))
        mfile = assy.filename[:-4] + ".dpb"
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
            env.history.message("Movie Player: %s previously saved movie for this part." % (auto_play and "playing" or "loading"))
            win.glpane.setMode('MOVIE')
            if auto_play:
                win.moviePlay()
            return
    # else if no assy.filename or no movie found from that:
    # bruce 050327 comment -- do what the old code did, except for the moviePlay
    # which seems wrong and tracebacks now.
    assy.current_movie = Movie(assy)
        # temporary kluge until bugs in movieMode for no assy.current_movie are fixed
    win.glpane.setMode('MOVIE')
    ## win.moviePlay()
        # [bruce 0505010 comment: not sure if this one would need auto_play, if it worked again]
    return

# ==

#bruce 050413 change: copy fileparse from MWsemantics, reimplement it using os.path
# (the old one used re.match, and I don't know if it was correct in all cases),
# which revises the spec (now the returned directory part doesn't end with '/'),
# so renaming it to filesplit to avoid confusion. Sometime soon the one in
# MWsemantics should be replaced with this one, which should be moved into some other file.

##def fileparse(name): # '/' at end of dirname
##    "fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')"
##    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
##    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))

def filesplit(pathname): #bruce 050413 fileparse variant: no '/' at end of dirname
    """Splits pathname into directory part (not ending with '/'),
    basename, and extension (including '.', or can be "")
    and returns them in a 3-tuple.
    For example, filesplit('~/foo/bar/gorp.xam') ==> ('~/foo/bar', 'gorp', '.xam').
    Compare with fileparse (deprecated), whose returned dir ends with '/'.
    """
    import os
    dir, file = os.path.split(pathname)
    base, ext = os.path.splitext(file)
    return dir, base, ext

#bruce 050413: try to move most of movie dashboard slot method code
# out of MWsemantics, without changing the basic fact that the .ui file
# wants to send the button signals into methods of MWsemantics
# (and these methods probably have to exist, unchanging, from the time
#  the MWsemantics object is initialized).
# Besides moving the slot methods, I replaced fileparse (above) with filesplit,
# and revised some calling code to use os.path.join to compensate for their
# difference in returning dirname.

class movieDashboardSlotsMixin:
    "Mixin class for letting MWsemantics have the movieMode dashboard slot methods."
    # bruce 050428: these attrs say when we're processing a valueChanged signal from slider or spinbox
    _movieDashboard_in_valuechanged_SL = False
    _movieDashboard_in_valuechanged_SB = False
    # bruce 050428: this says whether to ignore signals from slider and spinbox, since they're being changed
    # by the program rather than by the user. (#e The Movie method that sets it should be made a method of this class.)
    _movieDashboard_ignore_slider_and_spinbox = False
    def _movieDashboard_reinit(self):
        self._movieDashboard_ignore_slider_and_spinbox = True
        try:
            self.frameNumberSB.setMaxValue(999999) # in UI.py code
            self.frameNumberSL.setMaxValue(999999) # guess
            self.frameNumberSB.setValue(0) # guess
            self.frameNumberSL.setValue(0) # guess
        finally:
            self._movieDashboard_ignore_slider_and_spinbox = False
        return
    def moviePlay(self):
        """Play current movie foward from current position.
        """
        if self.assy.current_movie: #bruce 050427 added this condition in all these slot methods
            self.assy.current_movie._play(1)

    def moviePause(self):
        """Pause movie.
        """
        if self.assy.current_movie:
            self.assy.current_movie._pause()

    def moviePlayRev(self):
        """Play current movie in reverse from current position.
        """
        if self.assy.current_movie:
            self.assy.current_movie._play(-1)

    def movieReset(self):
        """Move current frame position to frame 0 (beginning) of the movie.
        """
        if self.assy.current_movie:
            self.assy.current_movie._reset()
    
    def movieMoveToEnd(self):
        """Move frame position to the last frame (end) of the movie.
        """
        if self.assy.current_movie:
            self.assy.current_movie._moveToEnd()
                            
    def moviePlayFrame(self, fnum):
        """Show frame fnum in the current movie. This slot receives valueChanged(int) signal from self.frameNumberSB.
        """
        if not self.assy.current_movie:
            return
        if self._movieDashboard_ignore_slider_and_spinbox:
            return
        ## next line is redundant, so I removed it [bruce 050428]
        ## if fnum == self.assy.current_movie.currentFrame: return

        self._movieDashboard_in_valuechanged_SB = True
        try:
            self.assy.current_movie._playToFrame(fnum)
        finally:
            self._movieDashboard_in_valuechanged_SB = False
        return
                            
    def movieSlider(self, fnum):
        """Show frame fnum in the current movie. This slot receives valueChanged(int) signal from self.frameNumberSL.
        """
        if not self.assy.current_movie:
            return
        if self._movieDashboard_ignore_slider_and_spinbox:
            return
        ## next line is redundant, so I removed it [bruce 050428]
        ## if fnum == self.assy.current_movie.currentFrame: return

        self._movieDashboard_in_valuechanged_SL = True
        try:
            self.assy.current_movie._playSlider(fnum)
        finally:
            self._movieDashboard_in_valuechanged_SL = False
        return

    def movieInfo(self):
        """Prints information about the current movie to the history widget.
        """
        if not self.assy.current_movie:
            return
        env.history.message(greenmsg("Movie Information"))
        self.assy.current_movie._info()
        
    def fileOpenMovie(self):
        """Open a movie file to play.
        """
        # bruce 050327 comment: this is not yet updated for "multiple movie objects"
        # and bugfixing of bugs introduced by that is in progress (only done in a klugy
        # way so far). ####@@@@
        env.history.message(greenmsg("Open Movie File:"))
        assert self.assy.current_movie
            # (since (as a temporary kluge) we create an empty one, if necessary, before entering
            #  Movie Mode, of which this is a dashboard method [bruce 050328])
        if self.assy.current_movie and self.assy.current_movie.currentFrame != 0:
            ###k bruce 060108 comment: I don't know if this will happen when currentFrame != 0 due to bug 1273 fix... #####@@@@@
            env.history.message(redmsg("Current movie must be reset to frame 0 to load a new movie."))
            return
        
        # Determine what directory to open. [bruce 050427 comment: if no moviefile, we should try assy.filename's dir next ###e]
        if self.assy.current_movie and self.assy.current_movie.filename:
            odir, fil, ext = filesplit(self.assy.current_movie.filename)
            del fil, ext #bruce 050413
        else:
            odir = globalParms['WorkingDirectory']

        fn = QFileDialog.getOpenFileName(odir,
                "Differential Position Bytes Format (*.dpb)",
                self )

        if not fn:
            env.history.message("Cancelled.")
            return
        
        fn = str(fn)

        # Check if file with name fn is a movie file which is valid for the current Part
        # [bruce 050324 made that a function and made it print the history messages
        #  which I've commented out below.]
        from movie import _checkMovieFile
        r = _checkMovieFile(self.assy.part, fn)
        
        if r == 1:
##            msg = redmsg("Cannot play movie file [" + fn + "]. It does not exist.")
##            env.history.message(msg)
            return
        elif r == 2: 
##            msg = redmsg("Movie file [" + fn + "] not valid for the current part.")
##            env.history.message(msg)
            if self.assy.current_movie and self.assy.current_movie.might_be_playable(): #bruce 050427 isOpen -> might_be_playable()
                msg = "(Previous movie file [" + self.assy.current_movie.filename + "] is still open.)"
                env.history.message(msg)
            return


        #bruce 050427 rewrote the following to use a new Movie object
        new_movie = find_saved_movie( self.assy, fn )
        if new_movie:
            new_movie.set_alist_from_entire_part(self.assy.part) # kluge? might need changing...
            if self.assy.current_movie: #bruce 050427 no longer checking isOpen here
                self.assy.current_movie._close()
            self.assy.current_movie = new_movie
            self.assy.current_movie._setup()
        else:
            # should never happen due to _checkMovieFile call, so this msg is ok
            # (but if someday we do _checkMovieFile inside find_saved_movie and not here,
            #  then this will happen as an error return from find_saved_movie)
            env.history.message(redmsg("Internal error in fileOpenMovie"))
        return

    def fileSaveMovie(self):
        """Save a copy of the current movie file loaded in the Movie Player.
        """
        # Make sure there is a moviefile to save.
        if not self.assy.current_movie or not self.assy.current_movie.filename \
          or not os.path.exists(self.assy.current_movie.filename):
            
            msg = redmsg("Save Movie File: No movie file to save.")
            env.history.message(msg)
            msg = "To create a movie, click on the <b>Simulator</b> <img source=\"simicon\"> icon."
            QMimeSourceFactory.defaultFactory().setPixmap( "simicon", 
                        self.simSetupAction.iconSet().pixmap() )
            env.history.message(msg)
            return
        
        env.history.message(greenmsg("Save Movie File:"))
        
        if self.assy.filename: sdir = self.assy.filename
        else: sdir = globalParms['WorkingDirectory']

        sfilter = QString("Differential Position Bytes Format (*.dpb)")
        
        # Removed .xyz as an option in the sfilter since the section of code below 
        # to save XYZ files never worked anyway.  This also fixes bug 492.  Mark 050816.
        fn = QFileDialog.getSaveFileName(sdir,
                    "Differential Position Bytes Format (*.dpb);;POV-Ray Series (*.pov)",
                    self, "IDONTKNOWWHATTHISIS",
                    "Save As",
                    sfilter)
        
        if not fn:
            env.history.message("Cancelled.")
            return
        else:
            fn = str(fn)
            dir, fil, ext2 = filesplit(fn)
            del ext2 #bruce 050413
            ext = str(sfilter[-5:-1]) # Get "ext" from the sfilter. It *can* be different from "ext2"!!! - Mark
                #bruce 050413 comment: the above assumes that len(ext) is always 4 (.xxx).
                # I'm speculating that this is ok for now since it has to be one of the ones
                # provided to the getSaveFileName method above.
            # Changed os.path.join > os.path.normpath to partially fix bug #956.  Mark 050911.
            safile = os.path.normpath(dir+"/"+fil+ext) # full path of "Save As" filename
            
            if os.path.exists(safile): # ...and if the "Save As" file exists...

                # ... confirm overwrite of the existing file.
                ret = QMessageBox.warning( self, self.name(),
                        "The file \"" + fil + ext + "\" already exists.\n"\
                        "Do you want to overwrite the existing file or cancel?",
                        "&Overwrite", "&Cancel", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                if ret==1: # The user cancelled
                    env.history.message( "Cancelled.  File not saved." )
                    return # Cancel clicked or Alt+C pressed or Escape pressed
            
            if ext == '.dpb':
#                print "fileSaveMovie(): Saving movie file", safile
#                print "fileSaveMovie(). self.assy.current_movie.isOpen =", self.assy.current_movie.isOpen
                self.assy.current_movie._close()
                import shutil
                shutil.copy(self.assy.current_movie.filename, safile)
                
                # Get the trace file name.
                tfile1 = self.assy.current_movie.get_trace_filename()
        
                # Copy the tracefile
                if os.path.exists(tfile1): 
                    fullpath, ext = os.path.splitext(safile)
                    tfile2 = fullpath + "-trace.txt"
                    shutil.copy(tfile1, tfile2)

                env.history.message("DPB movie file saved: " + safile)
                # note that we are still playing it from the old file and filename... does it matter? [bruce 050427 question]
                
                # Added "hflag=False" to suppress history msg, fixing bug #956.  Mark 050911.
                self.assy.current_movie._setup(hflag=False) # Do not print info to history widget.

            elif ext == '.pov':
                self.assy.current_movie._write_povray_series( os.path.normpath(dir+"/"+fil))
                
            else: #.xyz (or something unexpected)
                #bruce 051115 added warning and immediate return, to verify that this code is never called
                QMessageBox.warning(self, "ERROR", "internal error: unsupported file extension %r" % (ext,) ) # args are title, content
                return
                ## assert 0, "unsupported extension %r" % (ext,)
                
                # XYZ option removed above from call to QFileDialog.getSaveFileName().  
                # This section of code should not be called now (for A6).  Bruce was correct
                # in his comments below; this section of code never worked anyway.
                # Mark 050816
                #
                # writemovie() in runSim.py creates either an dpb or xyz file based on the 
                # file extension in assy.current_movie.filename.  To make this work for now, we
                # need to temporarily save assy.current_movie.filename of the current movie (dpb) file,
                # change the name, write the xyz file, then restore the dpb filename.
                # [bruce 050325 comment: I doubt this could have ever worked, but I don't know.
                #  For now I'm not revising it much. BTW it should be moved to some other file. ###@@@]
                self.assy.current_movie._pause() # To fix bug 358.  Mark  050201
                tmpname = self.assy.current_movie.filename #save the dpb filename of the current movie file.
                self.assy.current_movie.filename = safile # the name of the XYZ file the user wants to save.
                r = writemovie(self.part, self.assy.current_movie) # Save the XYZ moviefile
                    # [bruce 050325 revised this but it looks wrong anyway, what about mflag??
                    #  Besides, it runs the sim, so it will do a minimize... maybe it never worked, I don't know.]
                if not r: # Movie file saved successfully.
                    env.history.message("XYZ trajectory movie file saved: " + safile)
                self.assy.current_movie.filename = tmpname # restore the dpb filename.
                self.assy.current_movie._setup(0) # To fix bug 358.  Mark  050201
        return # from fileSaveMovie
    
    pass # end of class movieDashboardSlotsMixin

# end
