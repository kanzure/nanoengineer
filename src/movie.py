# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
movie.py -- the Movie class.

This file mainly defines class Movie

$Id$
"""

__author__ = "Mark"

import os, sys
from struct import unpack
from runSim import runSim
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
    def __init__(self, assembly, name=None):
        self.assy = assembly
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
        
# movie methods ##########################

    def _setup(self, hflag = True):
        """Setup this movie for playing
        """
        if DEBUG1: print "movie._setup() called. filename = [" + self.filename + "]"
        
        r = self._checkMovieFile()
        
        if r == 1:
            msg = redmsg("Cannot play movie file [" + self.filename + "]. It does not exist.")
            self.assy.w.history.message(msg)
            return r
        
        elif r == 2: 
            msg = redmsg("Movie file [" + self.filename + "] not valid for the current part")
            self.assy.w.history.message(msg)
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

        self.assy.w.frameNumberSL.setMaxValue(self.totalFrames)      
        self.assy.w.frameNumberSL.setValue(self.currentFrame) # SL = Slider
        
#        self.assy.w.movieProgressBar.setTotalSteps(self.totalFrames) # Progress bar
#        self.assy.w.movieProgressBar.setProgress(self.currentFrame)

        self.assy.w.frameNumberSB.setValue(self.currentFrame) # Spinbox
        self.assy.w.frameNumberSB.setMaxValue(self.totalFrames)

        flabel = "Frame (" + str(self.totalFrames) + " total):"
        self.assy.w.frameLabel.setText(flabel) # Spinbox label

        if hflag: self._info()
        
        return 0
        
        # Debugging Code
        if DEBUG1:
            msg = "Movie Ready: Number of Frames: " + str(self.totalFrames) + \
                    ", Current Frame:" +  str(self.currentFrame) +\
                    ", Number of Atoms:" + str(self.natoms)
            self.assy.w.history.message(msg)

            filepos = self.fileobj.tell() # Current file position
            msg = "Current frame:" + str(self.currentFrame) + ", filepos =" + str(filepos)
            self.assy.w.history.message(msg)

    def _close(self):
        """Close movie file and adjust atom positions.
        """
        if DEBUG1: print "movie._close() called. self.isOpen =", self.isOpen
        if not self.isOpen: return
        self._pause(0) 
        self.fileobj.close() # Close the movie file.
        self.assy.movend() # Unfreeze atoms.
        
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
            self.assy.w.history.message("Playing movie file [" + self.filename + "]")
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
        
        if hflag: self.assy.w.history.message("Movie continued: " + playDirection[ self.playDirection ])
        
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
        self.assy.w.moviePlayActiveAction.setVisible(0)
        self.assy.w.moviePlayAction.setVisible(1)
        self.assy.w.moviePlayRevActiveAction.setVisible(0)
        self.assy.w.moviePlayRevAction.setVisible(1)
#        self.assy.w.frameNumberSL.setValue(self.currentFrame) # SL = Slider
#        self.assy.w.frameNumberSB.setValue(self.currentFrame) # Spinbox
        if hflag: self.assy.w.history.message("Movie paused.")

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
            self.assy.w.moviePlayActiveAction.setVisible(1)
            self.assy.w.moviePlayAction.setVisible(0)
        else: 
            inc = REV
            self.assy.w.moviePlayRevActiveAction.setVisible(1)
            self.assy.w.moviePlayRevAction.setVisible(0)

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
                    self.assy.w.history.message(playDirection[ inc ] + "ing to frame " + str(fnum) + ".  You may select Pause at any time.")
                else:
                    self.assy.w.history.message(playDirection[ inc ] + "ing to frame " + str(fnum))
            
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
#                self.assy.w.history.message(msg)
#                print msg

                # adding 1 frame (of XYZ positions from the movie file) to the current atom positions
                self.assy.movatoms(self.fileobj, ADD)
                
                # Skip n frames.
                for n in range(self.assy.w.skipSB.value()):
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
#                self.assy.w.history.message(msg)
#                print msg

                # subtracting 1 frame (of XYZ positions from the movie file) from the current atom positions
                self.assy.movatoms(self.fileobj, SUBTRACT)
                self.fileobj.seek( filepos ) # reset the file position in case we play forward next time.
                
                # Skip n frames.
                for n in range(self.assy.w.skipSB.value()):
                    if self.currentFrame != fnum:
                        self.currentFrame += inc
                        filepos = (self.currentFrame * self.natoms * 3) + 4
                        self.fileobj.seek( filepos )
                        self.assy.movatoms(self.fileobj, SUBTRACT)
                        self.fileobj.seek( filepos ) # reset the file position in case we play forward next time.
            
            # update the GLPane and dashboard widgets each frame
            if self.showEachFrame:
                self.assy.w.frameNumberSL.setValue(self.currentFrame) # SL = Slider
                self.assy.w.frameNumberSB.setValue(self.currentFrame) # Spinbox
                self.assy.o.gl_update()
            else:
                self.assy.w.frameNumberSL.setValue(self.currentFrame) # SL = Slider
                self.assy.w.frameNumberSB.setValue(self.currentFrame) # Spinbox
                
                        
            # Updating MP dashboard widgets will slow down slider control.
            # Only update when "Move To End" button 
            if self.moveToEnd:
#                self.assy.w.movieProgressBar.setProgress(self.currentFrame) # Progress bar
                self.assy.w.frameNumberSL.setValue(self.currentFrame) # SL = Slider
                self.assy.w.frameNumberSB.setValue(self.currentFrame) # Spinbox
            
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
        self.assy.w.frameNumberSL.setValue(self.currentFrame) # SL = Slider
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
            self.assy.w.history.message("Advancing to frame " + str(fnum) + ". Please wait...")
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

        self.assy.w.frameNumberSB.setValue(self.currentFrame) # Update spinbox
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
        
#        self.assy.w.movieProgressBar.setProgress(self.currentFrame) # Progress bar
        self.assy.w.frameNumberSL.setValue(self.currentFrame) # SL = Slider
        self.assy.w.frameNumberSB.setValue(self.currentFrame) # Spinbox
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
        self.assy.w.movieResetAction.setEnabled(On)
        self.assy.w.moviePlayRevAction.setEnabled(On)
        self.assy.w.moviePauseAction.setEnabled(On)
        self.assy.w.moviePlayAction.setEnabled(On)
        self.assy.w.movieMoveToEndAction.setEnabled(On)
        self.assy.w.frameNumberSL.setEnabled(On)
        self.assy.w.frameNumberSB.setEnabled(On)
        self.assy.w.fileSaveMovieAction.setEnabled(On)
        
    def _info(self):
        """Print info about movie
        """
        if DEBUG0: print "movie._info() called."
        if not self.filename:
            self.assy.w.history.message("No movie file loaded.")
            return
        self.assy.w.history.message("Filename: [" + self.filename + "]")
        msg = "Number of Frames: " + str(self.totalFrames) + ".  Number of Atoms: " + str(self.natoms)
        self.assy.w.history.message(msg)
#        self.assy.w.history.message("Temperature:" + str(self.temp) + "K")
#        self.assy.w.history.message("Steps per Frame:" + str(self.stepsper))
#        self.assy.w.history.message("Time Step:" + str(self.stepsper))

    def _checkMovieFile(self, filename=""):
        """Returns 0 if filename is a valid movie file for the current part.
        Returns 1 if filename does not exist.
        Returns 2 if the movie file does not match the part.
        """
        if DEBUG1: print "movie._checkMovieFile() called. filename = ", filename
        
        if filename:
            if not os.path.exists(filename): return 1
        else:
            filename = self.filename
        
        filesize = os.path.getsize(filename) - 4
        
        f=open(filename,'rb')
        
        # Read header (4 bytes) from file containing the number of frames in the movie.
        nframes = unpack('i',f.read(4))[0]
        f.close()
        
        natoms = int(filesize/(nframes*3))
        
        if natoms == len(self.assy.alist): 
            return 0
        else: 
            return 2