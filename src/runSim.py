# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
runSim.py

$Id$
'''
__author__ = "Mark"

from SimSetupDialog import *
from commands import *
from debug import *
import os, sys, re, signal
from constants import *
from math import sqrt

def fileparse(name):
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))
    
class runSim(SimSetupDialog):
    def __init__(self, assy):
        SimSetupDialog.__init__(self)
        self.assy = assy
        self.movie = assy.m
        self.setup()
        self.exec_loop()
        
    def setup(self):
        self.movie.cancelled = True # We will assume the user will cancel
        self.nframesSB.setValue = self.movie.totalFrames
        self.tempSB.setValue = self.movie.temp
        self.stepsperSB.setValue = self.movie.stepsper
#        self.timestepSB.setValue = self.movie.timestep # Not supported in Alpha
        

    def createMoviePressed(self):
        """Creates a DPB (movie) file of the current part.  
        The part does not have to be saved
        as an MMP file first, as it used to.
        """
        QDialog.accept(self)
        self.movie.cancelled = False
        self.movie.totalFrames = self.nframesSB.value()
        self.movie.temp = self.tempSB.value()
        self.movie.stepsper = self.stepsperSB.value()
#        self.movie.timestep = self.timestepSB.value()
        
        if self.assy.filename: # Could be an MMP or PDB file.
            self.movie.filename = self.assy.filename[:-4] + '.dpb'
        else: 
            self.movie.filename = os.path.join(self.assy.w.tmpFilePath, "Untitled.dpb")
        return