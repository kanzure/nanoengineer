# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
SimSetup.py

Dialog for setting up to run the simulator.

$Id$

Created by Mark, under the name runSim.py.

Bruce 050324 changed some comments and did some code cleanup.

Bruce 050325 renamed file and class to SimSetup, to fit naming
convention for other Dialog subclasses.

(Bruce 030524 also moved a lot of existing code for actually
"running the simulator" into runSim.py, so that file still exists
but has all different code than before.)
'''
__author__ = "Mark"

from SimSetupDialog import *
import os
from movie import Movie
from debug import print_compact_traceback
import env

class SimSetup(SimSetupDialog): # before 050325 this class was called runSim
    "dialog class for setting up a simulator run"
    def __init__(self, part, previous_movie, suffix = ""):
        "use previous_movie for default values; on success or failure, make a new Movie and store it as self.movie"
        SimSetupDialog.__init__(self)
        ## self.part = part
            # not yet needed, though in future we might display info
            # about this Part in the dialog, to avoid confusion
            # if it's not the main Part.
        self.assy = part.assy # used only for assy.filename
        self.suffix = suffix
        self.previous_movie = previous_movie or Movie(self.assy) # used only for its parameter settings
        self.movie = Movie(self.assy) # public attr used by client code after we return; always a Movie even on failure.
            # (we need it here since no extra method runs on failure, tho that could probably be fixed) 
            # bruce 050325 changes:
            # We make a new Movie here (but only when we return with success).
            # But we use default param settings from prior movie.
            # Caller should pass info about default filename (including uniqueness
            #  when on selection or in clipboard item) -- i.e. the suffix.
            # We should set the params and filename using a Movie method, or warn it we did so,
            # or do them in its init... not yet cleaned up. ###@@@
            # self.movie is now a public attribute.
            #bruce 050329 comment: couldn't we set .movie to None, until we learn we succeeded? ###e ###@@@
        self.setup()
        self.exec_loop()
        
    def setup(self):
        self.movie.cancelled = True # We will assume the user will cancel
        #bruce 050324: fixed KnownBug item 27 by making these call setValue, not assign to it:
        # If the sim parameters change, they need to be updated in all places marked "SIMPARAMS"
        # Movie.__init__ (movie.py), toward the end
        # SimSetup.setup (SimSetup.py)
        # FakeMovie.__init (runSim.py)
        self.nframesSB.setValue( self.previous_movie.totalFramesRequested )
        self.tempSB.setValue( self.previous_movie.temp )
        self.stepsperSB.setValue( self.previous_movie.stepsper )
#        self.timestepSB.setValue( self.previous_movie.timestep ) # Not supported in Alpha
        # new checkboxes for Alpha7, circa 060108
        self.watch_motion_checkbox.setChecked( self.previous_movie.watch_motion ) # whether to move atoms in realtime
        #self.create_movie_file_checkbox.setChecked( self.previous_movie.create_movie_file ) 
            # whether to store movie file (see NFR/bug 1286). [bruce & mark 060108]
            # create_movie_file_checkbox removed for A7 (bug 1729). mark 060321
        if self.previous_movie._update_data:
            update_number, update_units, update_as_fast_as_possible_data = self.previous_movie._update_data
            self.update_btngrp.setButton( update_as_fast_as_possible_data)
            self.update_number_spinbox.setValue( update_number)
            self.update_units_combobox.setCurrentText( update_units)
                #k let's hope this changes the current choice, not the popup menu item text for the current choice!
        return
    
    def createMoviePressed(self):
        """Creates a DPB (movie) file of the current part.
        [Actually only saves the params and filename which should be used
         by the client code (in writemovie?) to create that file.]
        The part does not have to be saved as an MMP file first, as it used to.
        """
        ###@@@ bruce 050324 comment: Not sure if/when user can rename the file.
        QDialog.accept(self)
        self.movie.cancelled = False # This is the only way caller can tell we succeeded.
        self.movie.totalFramesRequested = self.nframesSB.value()
        self.movie.temp = self.tempSB.value()
        self.movie.stepsper = self.stepsperSB.value()
#        self.movie.timestep = self.timestepSB.value() # Not supported in Alpha
        self.movie.watch_motion = self.watch_motion_checkbox.isChecked()
        #self.movie.create_movie_file = self.create_movie_file_checkbox.isChecked() 
            # removed for A7 (bug 1729). mark 060321
        self.movie.create_movie_file = True

        try:
            if self.movie.watch_motion:
                #bruce 060530 use new watch_motion rate parameters
                # first grab them from the UI
                update_as_fast_as_possible_data = self.update_btngrp.selectedId() # 0 means yes, 1 means no (for now)
                    # ( or -1 means neither, but that's prevented by how the button group is set up, at least when it's enabled)
                update_as_fast_as_possible = (update_as_fast_as_possible_data != 1)
                update_number = self.update_number_spinbox.value() # 1, 2, etc (or perhaps 0??)
                update_units = str(self.update_units_combobox.currentText()) # 'frames', 'seconds', 'minutes', 'hours'
                # for sake of propogating them to the next sim run:
                self._update_data = update_number, update_units, update_as_fast_as_possible_data
                if env.debug():
                    print "debug: self.update_btngrp.selectedId() = %r" % (update_as_fast_as_possible_data,)
                    print "debug: self.update_number_spinbox.value() is %r" % self.update_number_spinbox.value() # e.g. 1
                    print "debug: combox text is %r" % str(self.update_units_combobox.currentText()) # e.g. 'frames'
                # Now figure out what they mean, as a function for deciding whether to update the 3D view
                # when a frame is received, given the time since the last update finished, the time that update took,
                # and the number of frames since then (1 or more). Notes: the Qt progress update will be done independently of this,
                # at most once per second (in runSim.py). The last frame we expect to receive will always be updated
                # (this func will be called anyway in case it wants to do something else with the info like store it somewhere,
                #  but its return value will be ignored for the last frame).
                # The details of these functions (and the UI feeding them) are likely to be changed soon.
                if update_as_fast_as_possible:
                    # This radiobutton is misnamed; it really means "use the old code,
                    # i.e. not worse than 20% slowdown, with threshholds".
                    # It's also ambiguous -- does "fast" mean "fast progress"
                    # or "often" (which are opposites)? It sort of means "often".
                    # It also probably ought to be a "faster if possible" checkbox instead.
                    update_cond = ( lambda simtime, pytime, nframes:
                                    simtime >= max(0.05, min(pytime * 4, 2.0)) )
                elif update_units == 'frames':
                    update_cond = ( lambda simtime, pytime, nframes, _nframes = update_number:  nframes >= _nframes )
                elif update_units == 'seconds':
                    update_cond = ( lambda simtime, pytime, nframes, _timelimit = update_number:  simtime + pytime >= _timelimit )
                elif update_units == 'minutes':
                    update_cond = ( lambda simtime, pytime, nframes, _timelimit = update_number * 60:  simtime + pytime >= _timelimit )
                elif update_units == 'hours':
                    update_cond = ( lambda simtime, pytime, nframes, _timelimit = update_number * 3600:  simtime + pytime >= _timelimit )
                else:
                    print "don't know how to set update_cond from (%r, %r)" % (update_number, update_units)
                self.movie.update_cond = update_cond
        except:
            print_compact_traceback("exception trying to set update_cond: ")

        suffix = self.suffix
        if self.assy.filename: # Could be an MMP or PDB file.
            self.movie.filename = self.assy.filename[:-4] + suffix + '.dpb'
        else: 
            self.movie.filename = os.path.join(self.assy.w.tmpFilePath, "Untitled%s.dpb" % suffix)
        return

    pass # end of class SimSetup

# end
