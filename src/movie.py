# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
movie.py -- the Movie class.

This file mainly defines class Movie

$Id$
"""

__author__ = "Mark"

import os, sys
from struct import unpack
from qt import Qt, qApp, QApplication, QCursor, SIGNAL
from HistoryWidget import redmsg

ADD = 1
SUBTRACT = 0
FWD = 1
REV = -1
DEBUG0 = 0
DEBUG1 = 0

playDirection = { FWD : "Forward", REV : "Reverse" }

class Movie:
    """
    Movie object.
    """
    # bruce 050324 comment: note that this class is misnamed --
    # it's really a SimRunnerAndResultsUser... which might
    # make and then use .xyz or .dpb results; if .dpb, it's able
    # to play the movie; if .xyz, it just makes it and uses it once
    # and presently doesn't even do it in methods, but in external
    # code (nonetheless it's used). Probably should split it into subclasses
    # and have one for .xyz and one for .dpb, and put that ext code
    # into one of them as methods. ###@@@
    def __init__(self, assembly, name=None):
        self.assy = assembly
        self.win = self.assy.w
        ## self.history = self.assy.w.history ###@@@ might not work, might need getattr, until we remake Movies as needed
        # for future use: name of the movie that appears in the modelTree. 
        self.name = name or "" # assumed to be a string by some code
        # the name of the movie file
        self.filename = ""
        # movie "file object"
        self.fileobj = None
        # the total number of frames in this movie
        self.totalFrames = 0
        # the most recent frame number of this movie that was played
        self.currentFrame = 0
        # the starting (current) frame number when entering MOVIE mode
        self.startFrame = 0
        # a flag that indicates whether this moviefile is open or closed 
        self.isOpen = False
        # a flag that indicates the current direction the movie is playing
        self.playDirection = FWD
        # for future use: a flag that indicates if the movie and the part are synchronized
        self.isValid = False
        # the number of atoms in each frame of the movie.
        self.natoms = 0
        # show each frame when _playFrame is called
        self.showEachFrame = False
        # a flag that indicates the movie is paused
        self.isPaused = True
        # a flag that indicates the movie is currently fast-forwarding to the end.
        self.moveToEnd = False
        # a flag that indicates if the wait (hourglass) cursor is displayed.
        self.waitCursor = False
        # simulator parameters that were used when creating this movie
        # these should be stored in the dpb file header so they
        # can be retrieved later.  These are the default values used by
        # the simsetup dialog.
        self.temp = 300
        self.stepsper = 10
        self.timestep = 10
##        # bruce 050324 added this: #### NOT YET, IT WON'T WORK UNTIL WE DELAY CREATION OF THIS OBJECT
##        self.part = self.assy.part # movie is assumed valid only for the current part at its time of creation
    def __getattr__(self, attr): # temporary kluge ###@@@
        if attr == 'part': return self.assy.tree.part
        if attr == 'history': return self.assy.w.history
        raise AttributeError, attr
        
# movie methods ##########################

    def _setup(self, hflag = True):
        """Setup this movie for playing
        """
        if DEBUG1: print "movie._setup() called. filename = [" + self.filename + "]"
        
        # Check if this movie's movie file is valid
        # [bruce 050324 made _checkMovieFile a function, made it require filename,
        #  and made it print the history messages which I've commented out below.]
        ## r = self._checkMovieFile()
        part = self.part
        r = _checkMovieFile(part, self.filename, self.history)
        
        if r == 1:
##            msg = redmsg("Cannot play movie file [" + self.filename + "]. It does not exist.")
##            self.history.message(msg)
            return r
        elif r == 2: 
##            msg = redmsg("Movie file [" + self.filename + "] not valid for the current part.")
##            self.history.message(msg)
            self._controls(0) # Disable movie control buttons.
            return r
            
        self._controls(1) # Enable movie control buttons.
            
        # movesetup freezes all the atoms in the model in preparation for playing the movie.
        # when leaving MOVIE mode, we'll need to unfreeze all the atoms by calling movend().
        self.assy.movsetup()
        
        # Save current atom positions.  This allows _reset() to quickly reload frame 0.
        if self.currentFrame == 0: self.assy.savebasepos() 
        
        # Open movie file.
        self.fileobj=open(self.filename,'rb')
        self.isOpen = True
        if DEBUG1: print "movie._setup(). self.isOpen =", self.isOpen
        
        # Read header (4 bytes) from file containing the number of frames in the moviefile.
        self.totalFrames = unpack('i',self.fileobj.read(4))[0]

        # Compute natoms
        filesize = os.path.getsize(self.filename)
        self.natoms = (filesize - 4) / (self.totalFrames * 3)
        
        # Set file position at currentFrame.
        filepos = (self.currentFrame * self.natoms * 3) + 4
        self.fileobj.seek( filepos )

        self.win.frameNumberSL.setMaxValue(self.totalFrames)      
        self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
        
#        self.win.movieProgressBar.setTotalSteps(self.totalFrames) # Progress bar
#        self.win.movieProgressBar.setProgress(self.currentFrame)

        self.win.frameNumberSB.setValue(self.currentFrame) # Spinbox
        self.win.frameNumberSB.setMaxValue(self.totalFrames)

        flabel = "Frame (" + str(self.totalFrames) + " total):"
        self.win.frameLabel.setText(flabel) # Spinbox label

        if hflag: self._info()
        
        # startframe and currentframe are compared in _close to determine if the assy has changed.
        self.startFrame = self.currentFrame
        
        return 0
        
        # Debugging Code
        if DEBUG1:
            msg = "Movie Ready: Number of Frames: " + str(self.totalFrames) + \
                    ", Current Frame:" +  str(self.currentFrame) +\
                    ", Number of Atoms:" + str(self.natoms)
            self.history.message(msg)

            filepos = self.fileobj.tell() # Current file position
            msg = "Current frame:" + str(self.currentFrame) + ", filepos =" + str(filepos)
            self.history.message(msg)

    def _close(self):
        """Close movie file and adjust atom positions.
        """
        if DEBUG1: print "movie._close() called. self.isOpen =", self.isOpen
        if not self.isOpen: return
        self._pause(0) 
        self.fileobj.close() # Close the movie file.
        self.assy.movend() # Unfreeze atoms.
        if self.startFrame != self.currentFrame: self.assy.changed()
        
        # Delete the array containing the original atom positions for the model.
        # We no longer need them since the movie file is closed.
#        self.assy.deletebasepos() 
        
    def _play(self, direction = FWD):
        """Start playing movie from the current frame.
        """

        if DEBUG0: print "movie._play() called.  Direction = ", playDirection[ direction ]
        
        if direction == FWD and self.currentFrame == self.totalFrames: return
        if direction == REV and self.currentFrame == 0: return
        
        self.playDirection = direction
        
        if self.currentFrame == 0: 
            self.history.message("Playing movie file [" + self.filename + "]")
            self._continue(0)
        else:
            self._continue()
        
    def _continue(self, hflag = True):
        """Continue playing movie from current position.
        hflag - if True, print history message
        """
        if DEBUG0: print "movie._continue() called. Direction = ", playDirection[ self.playDirection ]
        
        # In case the movie is already playing (usually the other direction).
        self._pause(0) 
        
        if hflag: self.history.message("Movie continued: " + playDirection[ self.playDirection ])
        
        self.showEachFrame = True

        # Continue playing movie.
        if self.playDirection == FWD: self._playFrame(self.totalFrames)
        else: self._playFrame(0)

    def _pause(self, hflag = True):
        """Pause movie.
        hflag - if True, print history message
        """
        if DEBUG0: print "movie._pause() called"
        self.isPaused = True
        self.showEachFrame = False
        self.moveToEnd = False
        self.win.moviePlayActiveAction.setVisible(0)
        self.win.moviePlayAction.setVisible(1)
        self.win.moviePlayRevActiveAction.setVisible(0)
        self.win.moviePlayRevAction.setVisible(1)
#        self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
#        self.win.frameNumberSB.setValue(self.currentFrame) # Spinbox
        if hflag: self.history.message("Movie paused.")

    def _playFrame(self, fnum):
        """Main method for movie playing (except for slider control).
        If "showEachFrame = True", it will play each frame of the movie between "fnum" and "currentFrame".
        If "showEachFrame = False", it will advance to "fnum" from "currentFrame".
        fnum - frame number to play to in the movie.
        """

        if DEBUG0: print "movie._playFrame() called: fnum = ", fnum, ", currentFrame =", self.currentFrame

        self.isPaused = False
        
        # Don't let movie run out of bounds.
        if fnum < 0 or fnum > self.totalFrames or fnum == self.currentFrame:
            self.isPaused = True # May not be needed.  Doing it anyway.
            return
           
        # Reset movie to beginning (frame 0).  Executed when user types 0 in spinbox.
        if not self.showEachFrame and fnum == 0: 
            self._reset()
            return

        # "inc" is the frame increment (FWD = 1, REV = -1) .
        if fnum > self.currentFrame: 
            inc = FWD
            self.win.moviePlayActiveAction.setVisible(1)
            self.win.moviePlayAction.setVisible(0)
        else: 
            inc = REV
            self.win.moviePlayRevActiveAction.setVisible(1)
            self.win.moviePlayRevAction.setVisible(0)

        # This addresses the situation when the movie file is large (> 1000 frames)
        # and the user drags the slider quickly, creating a large delta between
        # fnum and currentFrame.  Issue: playing this long of a range of the movie 
        # may take some time.  We need to give feedback to the user as to what is happening:
        # 1). turn the cursor into WaitCursor (hourglass).
        # 2). print a history message letting the user know we are advancing the movie, but
        #       also let them know they can pause the movie at any time.
        if not self.showEachFrame:
            delta = abs(fnum - self.currentFrame)
            if delta != 1:
                if delta > 1000:
                    self.waitCursor = True
                    QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
                    self.history.message(playDirection[ inc ] + "ing to frame " + str(fnum) + ".  You may select Pause at any time.")
                else:
                    self.history.message(playDirection[ inc ] + "ing to frame " + str(fnum))
            
        if DEBUG0: print "BEGIN LOOP: fnum = ", fnum, ", currentFrame =", self.currentFrame, ", inc =",inc
    
        # This is the main loop to compute atom positions from the current frame to "fnum"
        # After this loop completes, we paint the model.
        while self.currentFrame != fnum:

            if self.isPaused: break
                
            self.currentFrame += inc

            if DEBUG0: print "IN LOOP1: fnum = ", fnum, ", currentFrame =", self.currentFrame, ", inc =",inc

            # Forward one frame
            if inc == FWD:
                
                # Debugging code - Mark 050109
#                filepos = self.fileobj.tell()
#                msg = "FWD Frame:" + str(self.currentFrame) + ", filepos =" + str(filepos) + ", inc =" + str(inc)
#                msg += ", natoms =" + str(self.natoms)
#                self.history.message(msg)
#                print msg

                # adding 1 frame (of XYZ positions from the movie file) to the current atom positions
                self.assy.movatoms(self.fileobj, ADD)
                
                # Skip n frames.
                for n in range(self.win.skipSB.value()):
                    if self.currentFrame != fnum:
                        self.currentFrame += inc
                        self.assy.movatoms(self.fileobj, ADD)
             
            # Backward one frame   
            else: 
                filepos = (self.currentFrame * self.natoms * 3) + 4
                self.fileobj.seek( filepos )
                
                # Debugging code - Mark 050109
#                filepos = self.fileobj.tell()
#                msg = "REV Frame:" + str(self.currentFrame) + ", filepos =" + str(filepos) + ", inc =" + str(inc)
#                msg += ", natoms =" + str(self.natoms)
#                self.history.message(msg)
#                print msg

                # subtracting 1 frame (of XYZ positions from the movie file) from the current atom positions
                self.assy.movatoms(self.fileobj, SUBTRACT)
                self.fileobj.seek( filepos ) # reset the file position in case we play forward next time.
                
                # Skip n frames.
                for n in range(self.win.skipSB.value()):
                    if self.currentFrame != fnum:
                        self.currentFrame += inc
                        filepos = (self.currentFrame * self.natoms * 3) + 4
                        self.fileobj.seek( filepos )
                        self.assy.movatoms(self.fileobj, SUBTRACT)
                        self.fileobj.seek( filepos ) # reset the file position in case we play forward next time.
            
            # update the GLPane and dashboard widgets each frame
            if self.showEachFrame:
                self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
                self.win.frameNumberSB.setValue(self.currentFrame) # Spinbox
                self.assy.o.gl_update()
            else:
                self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
                self.win.frameNumberSB.setValue(self.currentFrame) # Spinbox
                
                        
            # Updating MP dashboard widgets will slow down slider control.
            # Only update when "Move To End" button 
            if self.moveToEnd:
#                self.win.movieProgressBar.setProgress(self.currentFrame) # Progress bar
                self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
                self.win.frameNumberSB.setValue(self.currentFrame) # Spinbox
            
            # Pause was pressed while playing movie.    
#            if self.isPaused: 
#                if DEBUG0: print "movie._playFrame(): INSIDE LOOP. Movie is paused.  Exiting loop."
#                break
            
            # Process queued events
            qApp.processEvents() 
                
        # End of loop
        
        # if we just played in reverse, reset the file position in case we play forward next time.
        
        # Update cursor, slider and show frame.
        if self.waitCursor: 
            QApplication.restoreOverrideCursor() # Restore the cursor
            self.waitCursor = False
        self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
        self.assy.o.gl_update()

        if DEBUG0: print "movie._playFrame(): Calling _pause"
        self._pause(0) # Force pause. Takes care of variable and dashboard maintenance.
        if DEBUG0: print "movie._playFrame(): BYE!"

    def _playSlider(self, fnum):
        """Slot for movie slider control.
        It will advance the movie to "fnum" from "currentFrame".
        fnum - frame number to advance to.
        """

        if DEBUG0: print "movie._playSlider() called: fnum = ", fnum, ", currentFrame =", self.currentFrame

        if fnum == self.currentFrame: return
        
        # Don't let movie run out of bounds.
        if fnum < 0 or fnum > self.totalFrames:
            print "Warning: Slider out of bounds.  Slider value =",fnum,", Number of frames =", self.totalFrames
            self.isPaused = True # May not be needed.  Doing it anyway.
            return

        # "inc" is the frame increment (FWD = 1, REV = -1) .
        if fnum > self.currentFrame: inc = FWD
        else: inc = REV
        
        if abs(fnum - self.currentFrame) > 1000:
            self.history.message("Advancing to frame " + str(fnum) + ". Please wait...")
            self.waitCursor = True
            QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        
        # This is the main loop to compute atom positions from the current frame to "fnum"
        # After this loop completes, we paint the model in the GLPane.
        while self.currentFrame != fnum:

            self.currentFrame += inc

            # Forward one frame
            if inc == FWD: self.assy.movatoms(self.fileobj)
             
            # Backward one frame   
            else: 
                filepos = (self.currentFrame * self.natoms * 3) + 4
                self.fileobj.seek( filepos )
                self.assy.movatoms(self.fileobj, 0)
                
        # End of loop
        
        # if we just played in reverse, reset the file position in case we play forward next time.
        if inc == REV: self.fileobj.seek( filepos )
        
        # Update dashboard and show frame.
        if self.waitCursor: 
            QApplication.restoreOverrideCursor() # Restore the cursor
            self.waitCursor = False

        self.win.frameNumberSB.setValue(self.currentFrame) # Update spinbox
        self.assy.o.gl_update()

                
    def _reset(self):
        """Resets the movie to the beginning (frame 0).
        """
        if DEBUG0: "movie._reset() called"
        if self.currentFrame == 0: return
        
        # Restore atom positions.
        self.assy.restorebasepos()
        
        self.currentFrame = 0
            
        # Set file position at currentFrame.
        filepos = (self.currentFrame * self.natoms * 3) + 4
        self.fileobj.seek( filepos )
        
#        self.win.movieProgressBar.setProgress(self.currentFrame) # Progress bar
        self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
        self.win.frameNumberSB.setValue(self.currentFrame) # Spinbox
        self._pause(0)
        self.assy.o.gl_update()
        
    def _moveToEnd(self):
        """
        """
        if DEBUG0: print "movie._moveToEnd() called"
        if self.currentFrame == self.totalFrames: return
        self._pause(0)
        self.moveToEnd = True
        self._playFrame(self.totalFrames)

    def _controls(self, On = True):
        """Enable or disable movie controls.
        """
        self.win.movieResetAction.setEnabled(On)
        self.win.moviePlayRevAction.setEnabled(On)
        self.win.moviePauseAction.setEnabled(On)
        self.win.moviePlayAction.setEnabled(On)
        self.win.movieMoveToEndAction.setEnabled(On)
        self.win.frameNumberSL.setEnabled(On)
        self.win.frameNumberSB.setEnabled(On)
        self.win.fileSaveMovieAction.setEnabled(On)
        
    def _info(self):
        """Print info about movie
        """
        if DEBUG0: print "movie._info() called."
        if not self.filename:
            self.history.message("No movie file loaded.")
            return
        self.history.message("Filename: [" + self.filename + "]")
        msg = "Number of Frames: " + str(self.totalFrames) + ".  Number of Atoms: " + str(self.natoms)
        self.history.message(msg)
#        self.history.message("Temperature:" + str(self.temp) + "K")
#        self.history.message("Steps per Frame:" + str(self.stepsper))
#        self.history.message("Time Step:" + str(self.stepsper))

    def get_trace_filename(self):
        """Returns the trace filename for the current movie.
        """
        fullpath, ext = os.path.splitext(self.filename)
        return fullpath + "-trace.txt"
        
    def get_GNUplot_filename(self):
        """Returns the GNUplot filename for the current movie.
        """
        fullpath, ext = os.path.splitext(self.filename)
        return fullpath + "-plot.txt"

    pass # end of class Movie

def _checkMovieFile(part, filename, history = None):
    """Returns 0 if filename is (or might be) a valid movie file for the specified part.
    Returns 1 if filename does not exist.
    Returns 2 if the movie file does not match the part.
    If history arg is provided, prints error messages to it
    (whenever return value is not zero).
    """
    #bruce 050324 made this a separate function, since it's not about a specific
    # Movie instance, just about a Part and a filename. Both args are now required,
    # and a new optional arg "history" is both where and whether to print errors
    # (both existing calls have been changed to pass it).
    # This function only checks number of atoms, and assumes all atoms of the Part
    # must be involved in the movie (in an order known to the Part, not checked,
    # though the order can easily be wrong).
    # It is not yet updated to handle the "new dpb format" (ie it doesn't get help
    # from either file keys or movie ids or atom positions) or movies made from
    # a possible future "simulate selection" operation.
    print_errors = not not history
    
    if DEBUG1: print "movie._checkMovieFile() function called. filename = ", filename
    
    assert filename #bruce 050324
    if not os.path.exists(filename):
        if print_errors:
            msg = redmsg("Cannot play movie file [" + filename + "]. It does not exist.")
            history.message(msg)
        return 1
    
    filesize = os.path.getsize(filename) - 4
    
    fp = open(filename,'rb')
    
    # Read header (4 bytes) from file containing the number of frames in the movie.
    nframes = unpack('i',fp.read(4))[0]
    fp.close()
    
    natoms = int(filesize/(nframes*3))
    
    if natoms == part.natoms: ## bruce 050324 changed this from natoms == len(self.assy.alist)
        return 0
    else:
        if print_errors:
            msg = redmsg("Movie file [" + filename + "] not valid for the current part.")
            history.message(msg)
        return 2
    pass

# end
