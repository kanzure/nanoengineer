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

FWD = 1
REV = -1

playDirection = { FWD : "Forward", REV : "Reverse" }

class Movie:
    """
    Movie object.
    """
    
    name = "" # for use before __init__ runs (used in __str__ of subclasses)
    
    def __init__(self, assembly, name=None):
        self.assy = assembly
        # for future use: name of the movie that appears in the modelTree. 
        self.name = name or "" # assumed to be a string by some code
        # the name of the movie file
        self.filename = ""
#        pid = os.getpid()
#        self.filename = os.path.join(self.assy.w.tmpFilePath, "sim-%d.dpb" % pid)
        # movie "file object"
        self.fileobj = None
        # the total number of frames in this movie
        self.totalFrames = 0
        # the most recent frame number of this movie that was played
        self.currentFrame = 0
        # a flag that indicates whether this moviefile is open or closed 
        self.isOpen = False
#        print "movie.__init__(). self.isOpen =", self.isOpen
        # a flag that indicates whether this movie is running via the timer
        self.playDirection = FWD
        # a flag that indicates if the movie and the part are synchronized
        self.isValid = False
        # the number of atoms in each frame of the movie.
#        self.natoms = len(self.assy.alist)
        self.natoms = 0
        # show each frame when in _playFrame
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

    def _setup(self):
        """Setup this movie for playing
        """
#        print "movie._setup() called"
        if not os.path.exists(self.filename): 
            self.assy.w.history.message("Cannot play movie file [" + self.filename + "]. It does not exist.")
            return
            
        self.assy.movsetup()
        
        # Save current atom positions.  This allows _reset() to quickly reload frame 0.
        if self.currentFrame == 0: self.assy.savebasepos() 
        
        # Open movie file.
        self.fileobj=open(self.filename,'rb')
        self.isOpen = True
#        print "movie._setup(). self.isOpen =", self.isOpen
        
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

        # Debugging Code
#        msg = "Movie Ready: Number of Frames: " + str(self.totalFrames) + \
#                ", Current Frame:" +  str(self.currentFrame) +\
#                ", Number of Atoms:" + str(self.natoms)
#        self.assy.w.history.message(msg)
        
        # Debugging Code
#        filepos = self.fileobj.tell() # Current file position
#        msg = "Frame:" + str(self.currentFrame) + ", filepos =" + str(filepos)
#        self.assy.w.history.message(msg)

    def _close(self):
        """Close movie file and adjust atom positions.
        """
#        print "movie._close() called"
        self.fileobj.close()
        self.assy.movend()
        
    def _play(self, direction = FWD):
        """Start playing movie from the current frame.
        """
#        print "movie._play() called"
        self.playDirection = direction
        
        if self.currentFrame == 0: 
            self.assy.w.history.message("Playing movie file [" + self.assy.m.filename + "]")
            self._continue(0)
        else:
            self._continue()
        
    def _continue(self, hflag = True):
        """Continue playing movie from current position.
        hflag - if True, print history message
        """
#        print "movie._continue() called"
        # In case the movie is playing
        # This is temporary.  I intend to 
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
#        print "movie._pause() called"
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

#        print "movie._playFrame() called: fnum = ", fnum, ", currentFrame =", self.currentFrame

        self.isPaused = False
        
        # Don't let movie run out of bounds.
        if fnum < 0 or fnum > self.totalFrames or fnum == self.currentFrame:
            self.isPaused = True # May not be needed.  Doing it anyway.
            return
           
        # Reset to movie to beginning (frame 0).  Executed when user types 0 in spinbox.
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

        if not self.showEachFrame:
            fadv = fnum - self.currentFrame
            if fadv != 1:
                if abs(fadv) > 1000:
                    self.waitCursor = True
                    QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
                    self.assy.w.history.message(playDirection[ inc ] + "ing to frame " + str(fnum) + ".  You make select Pause at any time.")
                else:
                    self.assy.w.history.message(playDirection[ inc ] + " to frame " + str(fnum))
            
#        print "BEGIN LOOP: fnum = ", fnum, ", currentFrame =", self.currentFrame, ", inc =",inc
    
        # This is the main loop to compute atom positions from the current frame to "fnum"
        # After this loop completes, we paint the model.
        while self.currentFrame != fnum:

            self.currentFrame += inc

#            print "IN LOOP1: fnum = ", fnum, ", currentFrame =", self.currentFrame, ", inc =",inc

            # Forward one frame
            if inc == FWD:
                
                # Debugging code - Mark 050109
#                filepos = self.fileobj.tell()
#                msg = "FWD Frame:" + str(self.currentFrame) + ", filepos =" + str(filepos) + ", inc =" + str(inc)
#                msg += ", natoms =" + str(self.natoms)
#                self.assy.w.history.message(msg)
#                print msg

                self.assy.movatoms(self.fileobj)
             
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

                self.assy.movatoms(self.fileobj, 0)
            
            # update the GLPane and dashboard widgets each frame
            if self.showEachFrame:
                self.assy.w.frameNumberSL.setValue(self.currentFrame) # SL = Slider
                self.assy.w.frameNumberSB.setValue(self.currentFrame) # Spinbox
                self.assy.o.paintGL()
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
            if self.isPaused: 
#                print "movie._playFrame(): INSIDE LOOP. Movie is paused.  Exiting loop."
                break
            
            # Process queued events
            qApp.processEvents() 
                
        # End of loop
        
        # if we just played in reverse, reset the file position in case we play forward next time.
        if inc == REV: self.fileobj.seek( filepos )
        
        # Update cursor, slider and show frame.
        if self.waitCursor: 
            QApplication.restoreOverrideCursor() # Restore the cursor
            self.waitCursor = False
        self.assy.w.frameNumberSL.setValue(self.currentFrame) # SL = Slider
        self.assy.o.paintGL()

#        print "movie._playFrame(): Calling _pause"
        self._pause(0) # Force pause. Takes care of variable and dashboard maintenance.

    def _playSlider(self, fnum):
        """Slot for movie slider control.
        It will advance the movie to "fnum" from "currentFrame".
        fnum - frame number to advance to.
        """

#        print "movie._playSlider() called: fnum = ", fnum, ", currentFrame =", self.currentFrame

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
        self.assy.o.paintGL()

                
    def _reset(self):
        """Resets the movie to the beginning (frame 0).
        """
#        print "movie._reset() called"
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
        self.assy.o.paintGL()
        
    def _moveToEnd(self):
        """
        """
#        print "movie._moveToEnd() called"
        if self.currentFrame == self.totalFrames: return
        self._pause(0)
        self.moveToEnd = True
        self._playFrame(self.totalFrames)