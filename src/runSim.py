# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
runSim.py

$Id$
'''
__author__ = "Mark"

from SimSetupDialog import *
from fileIO import writemmp, writemovie
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
        self.setup()
        
    def setup(self):
        self.nframes = self.assy.nframes
        self.temp = self.assy.temp
        self.stepsper = self.assy.stepsper
        self.timestep = self.assy.timestep
        
        self.nframesSB.setValue = self.nframes
        self.tempSB.setValue = self.assy.temp
        self.stepsperSB.setValue = self.assy.stepsper
        self.timestepSB.setValue = self.assy.timestep

    def saveFilePressed(self):
        """Prompts user to save a movie file.
        """
        if self.assy.filename: sdir = self.assy.filename
        else: sdir = globalParms['WorkingDirectory']

        sfilter = QString("Binary Trajectory File (*.dpb)")
        
        fn = QFileDialog.getSaveFileName(sdir,
                    "Binary Trajectory File (*.dpb);;XYZ Format (*.xyz)",
                    self, "IDONTKNOWWHATTHISIS",
                    "Save As",
                    sfilter)
        
        if fn:
            fn = str(fn)
            dir, fil, ext2 = fileparse(fn)
            ext =str(sfilter[-5:-1]) # Get "ext" from the sfilter. It *can* be different from "ext2"!!! - Mark
            safile = dir + fil + ext # full path of "Save As" filename
            
            if os.path.exists(safile): # ...and if the "Save As" file exists...

                # ... confirm overwrite of the existing file.
                ret = QMessageBox.warning( self, self.name(),
                        "The file \"" + fil + ext + "\" already exists.\n"\
                        "Do you want to overwrite the existing file or cancel?",
                        "&Overwrite", "&Cancel", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                if ret==1: # The user cancelled
                    self.assy.w.statusBar.message( "Cancelled.  File not saved." )
                    return # Cancel clicked or Alt+C pressed or Escape pressed
            
            if ext == '.dpb': ftype = 'DPB'
            else: ftype = 'XYZ'

            self.hide() # Hide simulator dialog window.
            
            r = writemovie(self.assy, safile) # Save moviefile
            
            if not r: # Movie file saved successfully.
                self.assy.w.statusBar.message( ftype + " file saved: " + safile)


    def createMoviePressed(self):
        """Creates a DPB (movie) file of the current part.  
        The part does not have to be saved
        as an MMP file first, as it used to.
        """
        QDialog.accept(self)
        if self.assy.filename: # Could be an MMP or PDB file.
            moviefile = self.assy.filename[:-4] + '.dpb'
        else: 
            moviefile = os.path.join(self.assy.w.tmpFilePath, "Untitled.dpb")

        print "createMoviePressed: calling writemovie: moviefile =",moviefile
        r = writemovie(self.assy, moviefile)
        
        if not r: # Movie file saved successfully.
            msg = "Total time to create movie file: %d seconds" % self.assy.w.progressbar.duration
            self.assy.w.statusBar.message(msg) 
            msg = "Movie written to [" + moviefile + "]."\
                        "To play movie, click on the <b>Movie Player</b> <img source=\"movieicon\"> icon."
            # This makes a copy of the movie tool icon to put in the HistoryWidget.
            QMimeSourceFactory.defaultFactory().setPixmap( "movieicon", 
                        self.assy.w.toolsMoviePlayerAction.iconSet().pixmap() )
            self.assy.w.statusBar.message(msg)
            
            self.assy.moviename = moviefile

        return

    def NumFramesValueChanged(self,a0):
        """Slot for spinbox that changes the number of frames for the simulator.
        """
        self.assy.nframes = a0

    def StepsChanged(self,a0):
        """Slot for spinbox that changes the number of steps for the simulator.
        """
        self.assy.stepsper = a0

    def TemperatureChanged(self,a0):
        """Slot for spinbox that changes the temperature for the simulator.
        """
        self.assy.temp = a0

    def TimeStepChanged(self,a0):
        """Slot for spinbox that changes time step for the simulator.
        """
        # THIS PARAMETER IS CURRENTLY NOT USED BY THE SIMULATOR
        # - Mark 050106
        self.assy.timestep = a0
