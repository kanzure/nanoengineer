# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
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

class SimSetup(SimSetupDialog): # before 050325 this class was called runSim
    "dialog class for setting up a simulator run"
    def __init__(self, assy, previous_movie):
        "use previous_movie for default values; make a new movie and store it as movie ###@@@ not yet, reuse same one for now"
        SimSetupDialog.__init__(self)
        self.assy = assy
        self.previous_movie = previous_movie or Movie() # used only for its parameter settings
        self.movie = self.previous_movie ## assy.current_movie
            #######@@@@@@@ bruce 050324 comments:
            # We should make a new Movie here instead (but only when we return with success).
            # But we might want to use default param settings from prior movie.
            # Caller should pass info about default filename (including uniqueness
            #  when on selection or in clipboard item).
            # We should set the params and filename using a Movie method, or warn it we did so,
            # or do them in its init....
            # self.movie is now a public attribute.
            # I renamed assy.m to assy.current_movie.
        self.setup()
        self.exec_loop()
        
    def setup(self):
        self.movie.cancelled = True # We will assume the user will cancel
        #bruce 050324: shouldn't these be calling setValue, not assigning to it? See if it fixes bug...
        self.nframesSB.setValue( self.previous_movie.totalFramesRequested )
        self.tempSB.setValue( self.previous_movie.temp )
        self.stepsperSB.setValue( self.previous_movie.stepsper )
#        self.timestepSB.setValue( self.previous_movie.timestep ) # Not supported in Alpha
    
    def createMoviePressed(self):
        """Creates a DPB (movie) file of the current part.  
        The part does not have to be saved
        as an MMP file first, as it used to.
        """
        #######@@@@@@@ bruce 050324 comment: docstring says it creates the file
        # but it only sets up self.movie to say how to create it (incl the default filename)
        # and the dialog's caller should then create the file. Not sure if/when user can rename the file.
        QDialog.accept(self)
        self.movie.cancelled = False
        self.movie.totalFramesRequested = self.nframesSB.value()
        self.movie.temp = self.tempSB.value()
        self.movie.stepsper = self.stepsperSB.value()
#        self.movie.timestep = self.timestepSB.value() # Not supported in Alpha
        
        if self.assy.filename: # Could be an MMP or PDB file.
            self.movie.filename = self.assy.filename[:-4] + '.dpb'
        else: 
            self.movie.filename = os.path.join(self.assy.w.tmpFilePath, "Untitled.dpb")
        return

    pass # end of class SimSetup

# end

