# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
movieMode.py -- movie player mode.

$Id$
"""

__author__ = "Mark"

from modes import *

from qt import QFileDialog, QMessageBox, QString, QMimeSourceFactory

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

        self.w.simMoviePlayerAction.setOn(1) # toggle on the Movie Player icon

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
    def moviePlay(self):
        """Play current movie foward from current position.
        """
        self.assy.current_movie._play(1)

    def moviePause(self):
        """Pause movie.
        """
        self.assy.current_movie._pause()

    def moviePlayRev(self):
        """Play current movie in reverse from current position.
        """
        self.assy.current_movie._play(-1)

    def movieReset(self):
        """Move current frame position to frame 0 (beginning) of the movie.
        """
        self.assy.current_movie._reset()
    
    def movieMoveToEnd(self):
        """Move frame position to the last frame (end) of the movie.
        """
        self.assy.current_movie._moveToEnd()
                            
    def moviePlayFrame(self, fnum):
        """Show frame fnum in the current movie.
        """
        if fnum == self.assy.current_movie.currentFrame: return
        self.assy.current_movie._playFrame(fnum)
                            
    def movieSlider(self, fnum):
        """Show frame fnum in the current movie.
        """
        if fnum == self.assy.current_movie.currentFrame: return
        self.assy.current_movie._playSlider(fnum)

    def movieInfo(self):
        """Prints information about the current movie to the history widget.
        """
        self.history.message(greenmsg("Movie Information"))
        self.assy.current_movie._info()
        
    def fileOpenMovie(self):
        """Open a movie file to play.
        """
        # bruce 050327 comment: this is not yet updated for "multiple movie objects"
        # and bugfixing of bugs introduced by that is in progress (only done in a klugy
        # way so far). ####@@@@
        # Also it should be moved into movieMode.py.
        self.history.message(greenmsg("Open Movie File:"))
        assert self.assy.current_movie
            # (since (as a temporary kluge) we create an empty one, if necessary, before entering
            #  Movie Mode, of which this is a dashboard method [bruce 050328])
        if self.assy.current_movie.currentFrame != 0:
            self.history.message(redmsg("Current movie must be reset to frame 0 to load a new movie."))
            return
        
        # Determine what directory to open.
        if self.assy.current_movie.filename:
            odir, fil, ext = filesplit(self.assy.current_movie.filename)
            del fil, ext #bruce 050413
        else:
            odir = globalParms['WorkingDirectory']

        fn = QFileDialog.getOpenFileName(odir,
                "Differential Position Bytes Format (*.dpb)",
                self )

        if not fn:
            self.history.message("Cancelled.")
            return
        
        fn = str(fn)

        # Check if this movie file is valid
        # [bruce 050324 made that a function and made it print the history messages
        #  which I've commented out below.]
        ## r = self.assy.current_movie._checkMovieFile(fn)
        from movie import _checkMovieFile
        r = _checkMovieFile(self.assy.part, fn, self.history)
        
        if r == 1:
##            msg = redmsg("Cannot play movie file [" + fn + "]. It does not exist.")
##            self.history.message(msg)
            return
        elif r == 2: 
##            msg = redmsg("Movie file [" + fn + "] not valid for the current part.")
##            self.history.message(msg)
            if self.assy.current_movie.isOpen:
                msg = "Movie file [" + self.assy.current_movie.filename + "] still open."
                self.history.message(msg)
            return

        if self.assy.current_movie.isOpen: self.assy.current_movie._close()
        self.assy.current_movie.filename = fn
        self.assy.current_movie.set_alist_from_entire_part(self.assy.part)
            # temporary bugfix kluge, might only partly work [bruce 050327]
        self.assy.current_movie._setup()

    def fileSaveMovie(self):
        """Save a copy of the current movie file loaded in the Movie Player.
        """
        # Make sure there is a moviefile to save.
        if not self.assy.current_movie or not self.assy.current_movie.filename \
          or not os.path.exists(self.assy.current_movie.filename):
            
            msg = redmsg("Open Movie File: No movie file to save.")
            self.history.message(msg)
            msg = "To create a movie, click on the <b>Simulator</b> <img source=\"simicon\"> icon."
            QMimeSourceFactory.defaultFactory().setPixmap( "simicon", 
                        self.simSetupAction.iconSet().pixmap() )
            self.history.message(msg)
            return
        
        self.history.message(greenmsg("Save Movie File:"))
        
        if self.assy.filename: sdir = self.assy.filename
        else: sdir = globalParms['WorkingDirectory']

        sfilter = QString("Differential Position Bytes Format (*.dpb)")
        
        fn = QFileDialog.getSaveFileName(sdir,
                    "Differential Position Bytes Format (*.dpb);;XYZ Format (*.xyz)",
                    self, "IDONTKNOWWHATTHISIS",
                    "Save As",
                    sfilter)
        
        if not fn:
            self.history.message("Cancelled.")
            return
        else:
            fn = str(fn)
            dir, fil, ext2 = filesplit(fn)
            del ext2 #bruce 050413
            ext = str(sfilter[-5:-1]) # Get "ext" from the sfilter. It *can* be different from "ext2"!!! - Mark
                #bruce 050413 comment: the above assumes that len(ext) is always 4 (.xxx).
                # I'm speculating that this is ok for now since it has to be one of the ones
                # provided to the getSaveFileName method above.
            safile = os.path.join(dir, fil + ext) # full path of "Save As" filename
            
            if os.path.exists(safile): # ...and if the "Save As" file exists...

                # ... confirm overwrite of the existing file.
                ret = QMessageBox.warning( self, self.name(),
                        "The file \"" + fil + ext + "\" already exists.\n"\
                        "Do you want to overwrite the existing file or cancel?",
                        "&Overwrite", "&Cancel", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                if ret==1: # The user cancelled
                    self.history.message( "Cancelled.  File not saved." )
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

                self.history.message("DPB movie file saved: " + safile)
                self.assy.current_movie._setup()
                
            else: 
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
                    self.history.message("XYZ trajectory movie file saved: " + safile)
                self.assy.current_movie.filename = tmpname # restore the dpb filename.
                self.assy.current_movie._setup(0) # To fix bug 358.  Mark  050201
        return # from fileSaveMovie
    
    pass # end of class movieDashboardSlotsMixin

# end
