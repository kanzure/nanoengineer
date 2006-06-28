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

# class FakeMovie:
#
# wware 060406 bug 1471 (sticky dialog params) - don't need a real movie, just need to hold the sim parameters
# If the sim parameters change, they might need to be updated everywhere a comment says "SIMPARAMS".
#
#bruce 060601 moving this here, since it's really an aspect of this dialog
# (in terms of what params to store, when to store them, etc);
# also fixing bug 1840 (like 1471 but work even after a sim was not aborted),
# and making the stickyness survive opening of a new file rather than being stored in the assy.

class FakeMovie:
    def __init__(self, realmovie):
        self.totalFramesRequested = realmovie.totalFramesRequested
        self.temp = realmovie.temp
        self.stepsper = realmovie.stepsper
        self.watch_motion = realmovie.watch_motion
        self._update_data = realmovie._update_data
        self.update_cond = realmovie.update_cond # probably not needed
    def fyi_reusing_your_moviefile(self, moviefile):
        pass
    def might_be_playable(self):
        return False
    pass

_stickyParams = None # sometimes this is a FakeMovie object


class SimSetup(SimSetupDialog): # before 050325 this class was called runSim
    "dialog class for setting up a simulator run"
    def __init__(self, part, previous_movie = None, suffix = ""):
        """use previous_movie (if passed) for default values,
        otherwise use the same ones last ok'd by user
        (whether or not that sim got aborted), or default values if that never happened in this session;
        on success or failure, make a new Movie and store it as self.movie
        """
        SimSetupDialog.__init__(self)
        ## self.part = part
            # not yet needed, though in future we might display info
            # about this Part in the dialog, to avoid confusion
            # if it's not the main Part.
        self.assy = part.assy # used only for assy.filename
        self.suffix = suffix
        self.previous_movie = previous_movie or _stickyParams or Movie(self.assy) # used only for its parameter settings
            # note: as of bruce 060601 fixing bug 1840, previous_movie is no longer ever passed by caller.
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
                self.movie._update_data = update_number, update_units, update_as_fast_as_possible_data
##                if env.debug():
##                    print "stored _update_data %r into movie %r" % (self.movie._update_data, self.movie)
##                    print "debug: self.update_btngrp.selectedId() = %r" % (update_as_fast_as_possible_data,)
##                    print "debug: self.update_number_spinbox.value() is %r" % self.update_number_spinbox.value() # e.g. 1
##                    print "debug: combox text is %r" % str(self.update_units_combobox.currentText()) # e.g. 'frames'
                # Now figure out what these user settings mean our realtime updating algorithm should be,
                # as a function to be used for deciding whether to update the 3D view when each new frame is received,
                # which takes as arguments the time since the last update finished (simtime), the time that update took (pytime),
                # and the number of frames since then (nframes, 1 or more), and returns a boolean for whether to draw this new frame.
                # Notes:
                # - The Qt progress update will be done independently of this, at most once per second (in runSim.py).
                # - The last frame we expect to receive will always be drawn. (This func may be called anyway in case it wants
                #   to do something else with the info like store it somewhere, or it may not (check runSim.py for details #k),
                #   but its return value will be ignored if it's called for the last frame.)
                # The details of these functions (and the UI feeding them) might be revised.

                # This code for setting update_cond is duplicated (inexactly) in Minimize_CommandRun.doMinimize() in runSim.py
                if update_as_fast_as_possible:
                    # This radiobutton might be misnamed; it really means "use the old code,
                    # i.e. not worse than 20% slowdown, with threshholds".
                    # It's also ambiguous -- does "fast" mean "fast progress"
                    # or "often" (which are opposites)? It sort of means "often".
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
        #bruce 060601 fix bug 1840, also make params sticky across opening of new files
        global _stickyParams
        _stickyParams = FakeMovie(self.movie) # these will be used as default params next time, whether or not this gets aborted
        return

    pass # end of class SimSetup

# end
