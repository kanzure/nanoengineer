# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
RosettaSetup.py

Dialog for setting up to run the simulator.

@author: Urmi
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.
Copied and then modified from SimSetup.py
"""

from simulation.movie import Movie

_stickyParams = None

class RosettaSetup:
    """
    The "Run Dynamics" dialog class for setting up and launching a simulator run.
    """
    def __init__(self, win, part, previous_movie = None, suffix = ""):
        """
        use previous_movie (if passed) for default values,
        otherwise use the same ones last ok'd by user
        (whether or not that sim got aborted), or default values if that never happened in this session;
        on success or failure, make a new Movie and store it as self.movie
        """

        self.assy = part.assy # used only for assy.filename
        self.suffix = suffix
        self.previous_movie = previous_movie or _stickyParams or Movie(self.assy) # used only for its parameter settings
            # note: as of bruce 060601 fixing bug 1840, previous_movie is no longer ever passed by caller.
        self.movie = Movie(self.assy) # public attr used by client code after we return; always a Movie even on failure.
        #Urmi 20080709: set movie filename to something for existing code to work
        self.movie.filename = "RosettaDesignTest.xyz"


    pass # end of class SimSetup

# end
