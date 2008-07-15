# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
rosetta_commandruns.py -- user-visible commands for running the rosetta simulator,

@author: Urmi
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:
Copied from sim_commandruns.py and then modified to suit rosetta simulation
"""

from utilities.debug import print_compact_traceback
from simulation.ROSETTA.RosettaSetup import RosettaSetup
from utilities.Log import redmsg, greenmsg, orangemsg
import foundation.env as env
# possibly some non-toplevel imports too (of which a few must remain non-toplevel)
from simulation.runSim import FAILURE_ALREADY_DOCUMENTED
from simulation.ROSETTA.runRosetta import RosettaRunner
from model.chunk import Chunk

def checkIfProteinChunkInPart(part):
    chunkList = []     
    def getAllChunks(node):
        if isinstance(node, Chunk):
            chunkList.append(node)
    part.topnode.apply2all(getAllChunks)    
    for chunk in chunkList:
        if chunk.isProteinChunk():
            return True, chunk
    return False, None

def writemovie(part,
               movie,
               mflag = 0,
               simaspect = None,
               print_sim_warnings = False,
               cmdname = "Rosetta Design",
               cmd_type = 'Fixed_Backbone_Sequence_Design',
               useRosetta = False,
               background = False):
        
    """
    Write an input file for the simulator, then run the simulator,
    in order to create a moviefile (.dpb file), or an .xyz file containing all
    frames(??), or an .xyz file containing what would have
    been the moviefile's final frame.  The name of the file it creates is found in
    movie.filename 
    """
    
    simrun = RosettaRunner(part,
                       mflag,
                       simaspect = simaspect,
                       cmdname = cmdname,
                       cmd_type = cmd_type,
                       useRosetta = useRosetta,
                       background = background,
                       )
    movie._simrun = simrun 
    simrun.run_using_old_movie_obj_to_hold_sim_params(movie)
    
    return simrun.errcode


class CommandRun: 
    """
    Class for single runs of commands.
    Commands themselves (as opposed to single runs of them)
    don't yet have objects to represent them in a first-class way,
    but can be coded and invoked as subclasses of CommandRun.
    """
    def __init__(self, win, *args, **kws):
        self.win = win
        self.args = args 
        self.kws = kws 
        self.assy = win.assy
        self.part = win.assy.part
        self.glpane = win.assy.o 
        return
    # end of class CommandRun
    
class rosettaSetup_CommandRun(CommandRun):
    """
    Class for single runs of the rosetta setup command; create it
    when the command is invoked, to prep to run the command once;
    then call self.run() to actually run it.
    """
    
    cmdname = 'Rosetta Design' 
    def run(self):
        
        if not self.part.molecules: # Nothing in the part to simulate.
            msg = redmsg("Nothing to simulate.")
            env.history.message(self.cmdname + ": " + msg)
            self.win.rosettaSetupAction.setChecked(0) 
            return
        #check if at least one protein chunk is present on the NE-1 window,
        #otherwise there's no point calling the simulator
        proteinExists, chunk = checkIfProteinChunkInPart(self.part)
        if not proteinExists:
            msg = redmsg("No protein to simulate.")
            env.history.message(self.cmdname + ": " + msg)
            self.win.rosettaSetupAction.setChecked(0) 
            return
        # iff it's the current mode.
        previous_movie = self.assy.current_movie
           
        self.movie = None
        r = self.makeSimMovie( ) # will store self.movie as the one it made, or leave it as None if cancelled
        self.win.rosettaSetupAction.setChecked(0) 
        
        return
    
    
    def makeSimMovie(self):
        suffix = self.part.movie_suffix()
        if suffix is None: 
            msg = redmsg( "Simulator is not yet implemented for clipboard items.")
            env.history.message(self.cmdname + ": " + msg)
            return -1
        
        self.simcntl = RosettaSetup(self.win, self.part, suffix = suffix)
        movie = self.simcntl.movie 
        r = writemovie(self.part, movie, print_sim_warnings = True, cmdname = self.cmdname, useRosetta = True)
            
        if not r:
            # Movie file created. 
            movie.IsValid = True 
            self.movie = movie 
        return r