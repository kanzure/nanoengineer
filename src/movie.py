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
from VQT import A
import platform

ADD = True
SUBTRACT = False
FWD = 1
REV = -1
DEBUG0 = 0
DEBUG1 = 0

playDirection = { FWD : "Forward", REV : "Reverse" }

class Movie:
    """
    Movie object. Holds state of one playable or playing movie,
    and provides methods for playing it,
    and has moviefile name and metainfo;
    also (before its moviefile is made) holds parameters needed
    for setting up a new simulator run
    (even for Minimize, though it might never make a moviefile).
    """
    #bruce 050324 comment: note that this class is misnamed --
    # it's really a SimRunnerAndResultsUser... which might
    # make and then use .xyz or .dpb results; if .dpb, it's able
    # to play the movie; if .xyz, it just makes it and uses it once
    # and presently doesn't even do it in methods, but in external
    # code (nonetheless it's used). Probably should split it into subclasses
    # and have one for .xyz and one for .dpb, and put that ext code
    # into one of them as methods. ###@@@
    #bruce 050329 comment: this file is mostly about the movie-playable DPB file;
    # probably it should turn into a subclass of SimRun, so the objects for other
    # kinds of sim runs (eg minimize) can be different. The superclass would
    # have most of the "writemovie" function (write sim input and run sim)
    # as a method, with subclasses customizing it.
    def __init__(self, assembly, name=None):
        """###doc; note that this Movie might be made to hold params for a sim run,
        and then be told its filename, or to read a previously saved file;
        pre-050326 code always stored filename from outside and didn't tell this object
        how it was becoming valid, etc...
        """
        self.assy = assembly
        self.win = self.assy.w
        self.glpane = self.assy.o ##e if in future there's more than one glpane, recompute this whenever starting to play the movie
        
        ## self.history = self.assy.w.history ###@@@ might not work, might need getattr, until we remake Movies as needed
        # for future use: name of the movie that appears in the modelTree. 
        self.name = name or "" # assumed to be a string by some code
        # the name of the movie file
        self.filename = "" #bruce 050326 comment: so far this is only set by external code; i'll change that
        # movie "file object"
        self.fileobj = None
        # the total number of frames actually in our moviefile [might differ from number requested]
        self.totalFramesActual = 0
            # bruce 050324 split uses of self.totalFrames into totalFramesActual and totalFramesRequested
            # to help fix some bugs, especially when these numbers differ
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
        # simulator parameters to be used when creating this movie,
        # or that were used when it was created;
        # these should be stored in the dpb file header so they
        # can be retrieved later. These will be the default values used by
        # the simsetup dialog, or were the values entered by the user.
        self.totalFramesRequested = 900
            # bruce 050325 added totalFramesRequested, changed some uses of totalFrames to this
        self.temp = 300
        self.stepsper = 10
        self.timestep = 10
            # Note [bruce 050325]: varying the timestep is not yet supported,
            # and this attribute is not presently used in the cad code.
        # bruce 050324 added these:
        self.alist = None # list of atoms for which this movie was made, if this has yet been defined
        
##        # bruce 050324 added this: #### NOT YET, IT WON'T WORK UNTIL WE DELAY CREATION OF THIS OBJECT
##        self.part = self.assy.part # movie is assumed valid only for the current part at its time of creation
        return
    
    def __getattr__(self, attr): # temporary kluge ###@@@
        if attr == 'part':
            if self.alist:
                return self.alist[0].molecule.part # not checked for consistency, but correct if anything is
            assert 0, "part needed before alist" ### can this happen? if it does, return cur part??? main part??? depends on why...
        if attr == 'history': return self.assy.w.history
        raise AttributeError, attr

    def destroy(self): #bruce 050325
        # so far only to be called before file is made; should work either way and _close if necessary.
        # for now, just break cycles.
        self.win = self.assy = self.part = self.alist = self.history = self.fileobj = None

    # == methods for letting this object represent a previously saved movie file

    def represent_this_moviefile( self, mfile, part = None): #bruce 050326
        """Try to start representing the given moviefile;
        return true iff this succeeds; if it fails emit error message.
        if part is supplied, also make sure mfile is valid for current state of that part.
        """
        #e should the checking be done in the caller (a helper function)?
        assert mfile.endswith(".dpb") # for now
        if os.path.exists(mfile):
            self.filename = mfile
            ###e do more... but what is needed? set alist? only if we need to play it, and we might not... (PlotTool doesn't)
            assert not part # this is nim; should call the validity checker
            return True
        else:
            pass #e self.history.message(redmsg(...)) -- is this a good idea? I think caller wants to do this... ###k
            self.destroy()
            return False
        pass

    # == methods for letting this object represent a movie (or xyz) file we're about to make, or just did make
    
    def set_alist(self, alist): #bruce 050325
        """Verify this list of atoms is legal (as an alist to make a movie from),
        and set it as this movie's alist. This only makes sense before making a moviefile,
        or after reading one we didn't make in the same session (or whose alist we lost)
        and figuring out somehow what existing atoms it should apply to.
        But nothing is checked about whether this alist fits the movie file,
        if we have one, and/or the other params we have --
        that's assumed done by the caller.
        """
        alist = list(alist) # make our own copy (in case caller modifies its copy), and ensure type is list
        atm0 = alist[0]
        assert atm0.molecule.part
        for atm in alist:
            assert atm.molecule.part == atm0.molecule.part
        # all atoms have the same Part, which is not None, and there's at least one atom.
        self.alist = alist
        self.natoms = len(alist) #bruce 050404; note, some old code might reset this (perhaps wrongly?) when reading a .dpb file
        return

    def set_alist_from_entire_part(self, part):
        """Set self.alist to a list of all atoms of the given Part,
        in the order in which they would be written to a new mmp file.
        """
        # force recompute of part.alist, since it's not yet invalidated when it needs to be
        part.alist = None
        del part.alist
        ## self.alist = part.alist
        alist = part.alist # this recomputes it
        self.set_alist(alist) #e could optimize (bypass checks in that method)
        return
        
##        ##(In the future we might change that to the order in which they
##        ## were last written to an actual file, if they ever were,
##        ## and if the set of atoms has not changed since then. ###e)
##        ##The right soln is to save alist when we load or save part,
##        ##then when we get this new one, check if atoms in it are same,
##        ##and if so use the saved one instead. [not always legal re jigs, see below]
##        # Check by sorting list of keys.
##        ##Or could we acually use that order in alist? only if we use it to write atoms to sim...
##        ##maybe we can, we'll see. In fact, I'm sure we can, since sim does not care
##        # about chunks, groups, atom order... oh, one exception -- it requires
##        # some jigs to be on contiguous sets of atoms.
##        # even so we could come close... or we might just let those jigs be on too many atoms. ###e
##        res = []
##        for mol in part.molecules: #e check >= 1? with atoms? ###WRONG, order of mols is arb.
##            lis = mol.atoms_in_mmp_file_order(): ###k
##                ###e worry about singlets re bug 254
##                ###e or let new code in minimize selection handle this
##            res.extend(lis)
##        ###e split into a part method to get alist, and our own set_alist method
##        self.set_alist(res) #e could optimize (bypass checks in that method)
##        return None
        
    # == methods for playing the movie file we know about (ie the movie we represent)

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
        self.movsetup()
        
        # Save current atom positions.  This allows _reset() to quickly reload frame 0.
        if self.currentFrame == 0: self.savebasepos() 
        
        # Open movie file.
        self.fileobj=open(self.filename,'rb')
        self.isOpen = True
        if DEBUG1: print "movie._setup(). self.isOpen =", self.isOpen
        
        # Read header (4 bytes) from file containing the number of frames in the moviefile.
        self.totalFramesActual = unpack('i',self.fileobj.read(4))[0]

        # Compute natoms
        filesize = os.path.getsize(self.filename)
        self.natoms = (filesize - 4) / (self.totalFramesActual * 3)
        
        # Set file position at currentFrame.
        filepos = (self.currentFrame * self.natoms * 3) + 4
        self.fileobj.seek( filepos )

        self.win.frameNumberSL.setMaxValue(self.totalFramesActual)      
        self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
        
#        self.win.movieProgressBar.setTotalSteps(self.totalFramesActual) # Progress bar
#        self.win.movieProgressBar.setProgress(self.currentFrame)

        self.win.frameNumberSB.setValue(self.currentFrame) # Spinbox
        self.win.frameNumberSB.setMaxValue(self.totalFramesActual)

        flabel = "Frame (" + str(self.totalFramesActual) + " total):"
        self.win.frameLabel.setText(flabel) # Spinbox label

        if hflag: self._info()
        
        # startframe and currentframe are compared in _close to determine if the assy has changed.
        self.startFrame = self.currentFrame
        
        return 0
        
        # Debugging Code
        if DEBUG1:
            msg = "Movie Ready: Number of Frames: " + str(self.totalFramesActual) + \
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
        self.movend() # Unfreeze atoms.
        if self.startFrame != self.currentFrame: self.assy.changed()
        
        # Delete the array containing the original atom positions for the model.
        # We no longer need them since the movie file is closed.
#        self.deletebasepos() 
        
    def _play(self, direction = FWD):
        """Start playing movie from the current frame.
        """

        if DEBUG0: print "movie._play() called.  Direction = ", playDirection[ direction ]
        
        if direction == FWD and self.currentFrame == self.totalFramesActual: return
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
        if self.playDirection == FWD: self._playFrame(self.totalFramesActual)
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
        if fnum < 0 or fnum > self.totalFramesActual or fnum == self.currentFrame:
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
                self.movatoms(self.fileobj, ADD)
                
                # Skip n frames.
                for n in range(self.win.skipSB.value()):
                    if self.currentFrame != fnum:
                        self.currentFrame += inc
                        self.movatoms(self.fileobj, ADD)
             
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
                self.movatoms(self.fileobj, SUBTRACT)
                self.fileobj.seek( filepos ) # reset the file position in case we play forward next time.
                
                # Skip n frames.
                for n in range(self.win.skipSB.value()):
                    if self.currentFrame != fnum:
                        self.currentFrame += inc
                        filepos = (self.currentFrame * self.natoms * 3) + 4
                        self.fileobj.seek( filepos )
                        self.movatoms(self.fileobj, SUBTRACT)
                        self.fileobj.seek( filepos ) # reset the file position in case we play forward next time.
            
            # update the GLPane and dashboard widgets each frame
            if self.showEachFrame:
                self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
                self.win.frameNumberSB.setValue(self.currentFrame) # Spinbox
                self.glpane.gl_update()
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
        self.glpane.gl_update()

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
        if fnum < 0 or fnum > self.totalFramesActual:
            print "Warning: Slider out of bounds.  Slider value =",fnum,", Number of frames =", self.totalFramesActual
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
            if inc == FWD: self.movatoms(self.fileobj, ADD)
             
            # Backward one frame   
            else: 
                filepos = (self.currentFrame * self.natoms * 3) + 4
                self.fileobj.seek( filepos )
                self.movatoms(self.fileobj, SUBTRACT)
                
        # End of loop
        
        # if we just played in reverse, reset the file position in case we play forward next time.
        if inc == REV: self.fileobj.seek( filepos )
        
        # Update dashboard and show frame.
        if self.waitCursor: 
            QApplication.restoreOverrideCursor() # Restore the cursor
            self.waitCursor = False

        self.win.frameNumberSB.setValue(self.currentFrame) # Update spinbox
        self.glpane.gl_update()

                
    def _reset(self):
        """Resets the movie to the beginning (frame 0).
        """
        if DEBUG0: "movie._reset() called"
        if self.currentFrame == 0: return
        
        # Restore atom positions.
        self.restorebasepos()
            ###@@@ bruce 050325 question: how do we know they were ever saved?
        
        self.currentFrame = 0
            
        # Set file position at currentFrame.
        filepos = (self.currentFrame * self.natoms * 3) + 4
        self.fileobj.seek( filepos )
        
#        self.win.movieProgressBar.setProgress(self.currentFrame) # Progress bar
        self.win.frameNumberSL.setValue(self.currentFrame) # SL = Slider
        self.win.frameNumberSB.setValue(self.currentFrame) # Spinbox
        self._pause(0)
        self.glpane.gl_update()
        
    def _moveToEnd(self):
        """
        """
        if DEBUG0: print "movie._moveToEnd() called"
        if self.currentFrame == self.totalFramesActual: return
        self._pause(0)
        self.moveToEnd = True
        self._playFrame(self.totalFramesActual)

    # ==
    
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

    # ==
    
    def _info(self):
        """Print info about movie
        """
        if DEBUG0: print "movie._info() called."
        if not self.filename:
            self.history.message("No movie file loaded.")
            return
        self.history.message("Filename: [" + self.filename + "]")
        msg = "Number of Frames: " + str(self.totalFramesActual) + ".  Number of Atoms: " + str(self.natoms)
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

    # == low-level movie-playing methods [revised, and moved out of class Part, by bruce 050325]

    ###@@@ need: self.molecules

    # set up to play a movie
    def movsetup(self):
        self.blist = blist = {}
        moldict = {}
        for a in self.alist:
            for b in a.bonds:
                blist[b.key]=b
            m = a.molecule
            moldict[id(m)] = m
        self.molecules = moldict.values()
        self.part = part = self.molecules[0].part
        for m in self.molecules:
            if not m.part == part:
                # check them all before freezing any (does this cover killed atoms too? I think so.)
                self.history.message( redmsg( "Can't play movie, since not all its atoms are still in the same Part" ))
                assert 0 # not sure how well this will be caught... #e should use retval, fix caller ####@@@@
        self.assy.set_current_part(part) ###@@@ ok here?? should also do this whenever movie dashboard is used, i think...
        for m in self.molecules:
            m.freeze()        
        return

    def savebasepos(self):
        """Copy current atom positions into an array.
        """
        # save a copy of each chunk's basepos array 
        # (in the chunk itself, why not -- it's the most convenient place)
        # [only ok if at most one movie can be playing at once, for one chunk ##k]
        for m in self.molecules:
            m._savedbasepos = + m.basepos
            
    def restorebasepos(self):
        """Restore atom positions copied earlier by savebasepos().
        """
        # restore that later (without erasing it, so no need to save it 
        # again right now)
        # (only valid when every molecule is "frozen", i.e. basepos and 
        # curpos are same object):
        for m in self.molecules:
            #bruce 050210 fixing "movie reset" bug reported by Josh for Alpha-2
            assert m.basepos is m.curpos
            m.basepos = m.curpos = m.atpos = + m._savedbasepos
            m.changed_attr('atpos', skip = ('basepos',) )

        for b in self.blist.itervalues():
            b.setup_invalidate()
            
        for m in self.molecules:
            m.changeapp(0)

    def deletebasepos(self):
        """Erase the savedbasepos array.  It takes a lot of room.
        """
        for m in self.molecules:
            del m._savedbasepos
            
    # move the atoms one frame as for movie or minimization
    # .dpb file is in units of 0.01 Angstroms
    # units here are angstroms
    def movatoms(self, file, addpos = ADD):
        "#doc [callers can pass ADD (True) or SUBTRACT (False) for addpos]"
        if not self.alist: return
        ###e bruce 041104 thinks this should first check whether the
        # molecules involved have been updated in an incompatible way
        # (which might change the indices of atoms); otherwise crashes
        # might occur. It might be even worse if a shakedown would run
        # during this replaying! (This is just a guess; I haven't tested
        # it or fully analyzed all related code, or checked whether
        # those dangerous mods are somehow blocked during the replay.)
        for a in self.alist:
            # (assuming mol still frozen, this will change both basepos and
            #  curpos since they are the same object; it won't update or
            #  invalidate other attrs of the mol, however -- ok?? [bruce 041104])
            if addpos: a.molecule.basepos[a.index] += A(unpack('bbb',file.read(3)))*0.01
            else: a.molecule.basepos[a.index] -= A(unpack('bbb',file.read(3)))*0.01
                    
        for b in self.blist.itervalues():
            b.setup_invalidate()
            
        for m in self.molecules:
            m.changeapp(0)

    # regularize the atoms' new positions after the motion
    def movend(self):
        # terrible hack for singlets in simulator, which treats them as H
        for a in self.alist:
            if a.is_singlet(): a.snuggle()
        for m in self.molecules:
            m.unfreeze()
        self.glpane.gl_update()

    def moveAtoms(self, newPositions): # used when reading xyz files
        """Huaicai 1/20/05: Move a list of atoms to newPosition. After 
            all atoms moving, bond updated, update display once.
           <parameter>newPosition is a list of atom absolute position, the list order is the same as self.alist """
           
        if len(newPositions) != len(self.alist): #bruce 050225 added some parameters to this error message
            print "moveAtoms: The number of atoms from XYZ file (%d) is not matching with that of the current model (%d)" % \
                  (len(newPositions), len(self.alist))
            return
        for a, newPos in zip(self.alist, newPositions):
                a.setposn(A(newPos))
        self.glpane.gl_update()

    pass # end of class Movie

# == helper functions

def find_saved_movie( assy, mfile):
    "look for a .dpb file of the given name; if found, return a Movie object for it"
    movie = Movie(assy)
    if movie.represent_this_moviefile( mfile):
        # succeeded
        return movie
    # otherwise it failed and already emitted error messages about that
    return None

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

    #######@@@@@@@ kluge to work around bug in part.natoms not being invalidated enough:
    part.natoms = None
    del part.natoms # force recompute
    
    if natoms == part.natoms: ## bruce 050324 changed this from natoms == len(self.assy.alist)
        return 0
    else:
        if platform.atom_debug:
            print "atom_debug: not natoms == part.natoms, %d %d" % (natoms, part.natoms)
        if print_errors:
            msg = redmsg("Movie file [" + filename + "] not valid for the current part.")
            history.message(msg)
        return 2
    pass

# end
