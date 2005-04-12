# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
movieMode.py -- movie player mode.

$Id$
"""

__author__ = "Mark"

from modes import *

class movieMode(basicMode):
    """ This class is used to play movie files.
       Users know it as "Movie mode".
    """

    # class constants
    backgroundColor = 189/255.0, 228/255.0, 238/255.0
    modename = 'MOVIE'
    default_mode_status_text = "Mode: Movie Player"
    
    # methods related to entering this mode
    
    def Enter(self):
        basicMode.Enter(self)
        self.o.assy.unpickatoms()
        self.o.assy.unpickparts()
        self.o.assy.selwhat = 0

    def init_gui(self):

        self.w.toolsMoviePlayerAction.setOn(1) # toggle on the Movie Player icon

        # Disable some action items in the main window.
        self.w.modifyMinimizeSelAction.setEnabled(0) # Disable "Minimize Selection"
        self.w.modifyMinimizeAllAction.setEnabled(0) # Disable "Minimize All"
        self.w.simSetupAction.setEnabled(0) # Disable "Simulator"
        self.w.fileSaveAction.setEnabled(0) # Disable "File Save"
        self.w.fileSaveAsAction.setEnabled(0) # Disable "File Save As"
        self.w.fileOpenAction.setEnabled(0) # Disable "File Open"
        self.w.fileCloseAction.setEnabled(0) # Disable "File Close"
        self.w.fileInsertAction.setEnabled(0) # Disable "File Insert"
        self.w.editDeleteAction.setEnabled(0) # Disable "Delete"
        self.w.zoomToolAction.setEnabled(0) # Disable "Zoom Tool"
        self.w.panToolAction.setEnabled(0) # Disable "Pan Tool"
        self.w.rotateToolAction.setEnabled(0) # Disable "Rotate Tool"
        
        # MP dashboard initialization.
        self.w.frameNumberSB.setValue(self.o.assy.current_movie.currentFrame) # SB = Spinbox
        self.w.moviePlayActiveAction.setVisible(0)
        self.w.moviePlayRevActiveAction.setVisible(0)
        self.w.moviePlayerDashboard.show()
        
        if self.o.assy.current_movie.filename: # We have a movie file ready.  It's showtime!
            self.o.assy.current_movie._setup() # Cue movie.
        else:
            self.o.assy.current_movie._controls(0) # Movie control buttons are disabled.

    def haveNontrivialState(self):
        self.o.assy.current_movie._close()
        return False

    def StateDone(self):
        self.o.assy.current_movie._close()
        return None

    def restore_gui(self):
        self.w.moviePlayerDashboard.hide()
        self.w.modifyMinimizeSelAction.setEnabled(1) # Enable "Minimize Selection"
        self.w.modifyMinimizeAllAction.setEnabled(1) # Enable "Minimize All"
        self.w.simSetupAction.setEnabled(1) # Enable "Simulator"
        self.w.fileSaveAction.setEnabled(1) # Enable "File Save"
        self.w.fileSaveAsAction.setEnabled(1) # Enable "File Save"
        self.w.fileOpenAction.setEnabled(1) # Enable "File Open"
        self.w.fileCloseAction.setEnabled(1) # Enable "File Close"
        self.w.fileInsertAction.setEnabled(1) # Enable "File Insert"
        self.w.editDeleteAction.setEnabled(1) # Enable "Delete"
        self.w.zoomToolAction.setEnabled(1) # Enable "Zoom Tool"
        self.w.panToolAction.setEnabled(1) # Enable "Pan Tool"
        self.w.rotateToolAction.setEnabled(1) # Enable "Rotate Tool"

    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Reset Movie', self.ResetMovie),
            
            ('Done', self.Done)
         ]

    def ResetMovie(self): #bruce 050325
        if self.o.assy.current_movie:
            self.o.assy.current_movie._reset() # since .current_movie can change
        
    def Draw(self):
        basicMode.Draw(self)
        self.o.assy.draw(self.o)

    # mouse and key events
            
    def keyPress(self,key):
        
        # Disable delete key
        if key == Qt.Key_Delete: return 
        
        # Left or Down arrow keys - advance back one frame
        if key == Qt.Key_Left or key == Qt.Key_Down:
            self.o.assy.current_movie._playFrame(self.o.assy.current_movie.currentFrame - 1)
        
        # Right or Up arrow keys - advance forward one frame
        if key == Qt.Key_Right or key == Qt.Key_Up:
            self.o.assy.current_movie._playFrame(self.o.assy.current_movie.currentFrame +1)
        
        return

# ==

def simMoviePlayer(assy):
    """Plays a DPB movie file created by the simulator,
    either the current movie if any, or a previously saved
    dpb file with the same name as the current part, if one can be found.
    """
    # moved here from MWsemantics method, and fixed bugs I recently put into it 
    # (by rewriting it from original and from rewritten simPlot function)
    # [bruce 050327]
    from movie import find_saved_movie, Movie #bruce 050329 precaution (in case of similar bug to bug 499)
    history = assy.w.history
    win = assy.w
    if not assy.molecules: # No model, so no movie could be valid for current part.
        # bruce 050327 comment: even so, a movie file might be valid for some other Part...
        # not yet considered here.
        history.message(redmsg("Movie Player: Need a model."))
        return
    ###@@@
    ## history.message(greenmsg("Plot Tool:")) # do before other messages, tho success is not yet known

    if assy.current_movie and assy.current_movie.filename:
        win.glpane.setMode('MOVIE')
        win.moviePlay()
        return

    # no valid current movie, look for saved one with same name as assy
    ## history.message("Plot Tool: No simulation has been run yet.")
    if assy.filename:
        if assy.part != assy.tree.part:
            history.message("Movie Player: Warning: Looking for saved movie for main part, not for displayed clipboard item.")
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
            history.message("Movie Player: playing previously saved movie for this part.")
            win.glpane.setMode('MOVIE')
            win.moviePlay()
            return
    # else if no assy.filename or no movie found from that:
    # bruce 050327 comment -- do what the old code did, except for the moviePlay
    # which seems wrong and tracebacks now.
    assy.current_movie = Movie(assy)
        # temporary kluge until bugs in movieMode for no assy.current_movie are fixed
    win.glpane.setMode('MOVIE')
    ## win.moviePlay()
    return

# end

