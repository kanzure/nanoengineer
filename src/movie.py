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
from qt import qApp

FWD = 1
REV = -1

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
        # a flag that indicated the movie is paused
        self.isPaused = True
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
        if not os.path.exists(self.filename): 
            self.assy.w.history.message("Cannot play movie file [" + self.filename + "]. It does not exist.")
            return
        self.assy.movsetup()
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

        self.assy.w.movieProgressBar.setTotalSteps(self.totalFrames) # Progress bar
        self.assy.w.movieProgressBar.setProgress(self.currentFrame)

        self.assy.w.frameNumberSB.setValue(self.currentFrame) # Spinbox
        self.assy.w.frameNumberSB.setMaxValue(self.totalFrames)

#        self.assy.w.frameNumberLCD.display(self.currentFrame) # LCD        
#        self.assy.w.frameNumberSL.setValue(self.currentFrame) # SL = Slider
#        self.assy.w.frameNumberSL.setMaxValue(self.totalFrames)

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
        self.fileobj.close()
        self.assy.movend()
        
    def _play(self, direction = FWD):
        """Start playing movie from the current frame.
        """
        self.assy.w.history.message("Playing movie file [" + self.assy.m.filename + "]  Total Frames: " + str(self.totalFrames))
        self.playDirection = direction
        self._continue(0)
        
    def _continue(self, hflag = True):
        """Continue playing movie
        hflag - if True, print history message
        """
        
        # In case the movie is playing
        # This is temporary.  I intend to 
        self._pause(0) 
        
        
        
        if hflag: self.assy.w.history.message("Movie continued.")
        
        self.showEachFrame = True

        # Continue playing movie.
        if self.playDirection == FWD: self._playFrame(self.totalFrames)
        else: self._playFrame(0)

    def _pause(self, hflag = True):
        """Pause movie.
        hflag - if True, print history message
        """
        self.isPaused = True
        self.showEachFrame = False
        self.assy.w.moviePlayActiveAction.setVisible(0)
        self.assy.w.moviePlayAction.setVisible(1)
        self.assy.w.moviePlayRevActiveAction.setVisible(0)
        self.assy.w.moviePlayRevAction.setVisible(1)
        if hflag: self.assy.w.history.message("Movie paused.")

    def _playFrame(self, fnum):
        """Show a specific frame of the movie. If "isPlaying" is true, 
        it will show each frame between "fnum" and "currentFrame".
        fnum - frame number to display in the movie.
        """
        
        self.isPaused = False
        
        # Don't let movie run out of bounds.
        if fnum < 0 or fnum > self.totalFrames or fnum == self.currentFrame:
            self.isPaused = True # May not be needed.  Doing it anyway.
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
        
#        print "BEGIN: fnum = ", fnum, ", currentFrame =", self.currentFrame, ", inc =",inc
        
        # This is the main loop to compute atom positions from the current frame to "fnum"
        # After this loop completes, we paint the model.
        while self.currentFrame != fnum:

            self.currentFrame += inc
            self.assy.w.movieProgressBar.setProgress(self.currentFrame) # Progress bar

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
            
            # update the GLPane and frame number each frame
            if self.showEachFrame:
                qApp.processEvents() # Process queued events (i.e. clicking Abort button).
                self.assy.w.frameNumberSB.setValue(self.currentFrame) # Spinbox
                self.assy.o.paintGL()
            
            # Pause was pressed while playing movie.    
            if self.isPaused: break
                
        # End of loop
        
        # if we just played in reverse, reset the file position in case we play forward next time.
        if inc == REV: self.fileobj.seek( filepos )
        
        # Update dashboard and show frame.        
        self.assy.w.frameNumberSB.setValue(self.currentFrame) # Spinbox
        self.assy.w.moviePlayActiveAction.setVisible(0)
        self.assy.w.moviePlayAction.setVisible(1)
        self.assy.w.moviePlayRevActiveAction.setVisible(0)
        self.assy.w.moviePlayRevAction.setVisible(1)
        self.assy.o.paintGL()

        # This is a temporary workaround for an unusual bug I can't figure out.
        # When the REV play button is pressed during FWD play, the movie
        # will play forward again after REV play gets to frame 0.  Very strange.
        # Mark 050110
        self._pause(0) # Force pause.
