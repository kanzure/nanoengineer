# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

from SimSetupDialog import *
from fileIO import writemmp
from commands import *
from debug import *
import os

class runSim(SimSetupDialog):
    def __init__(self, assy):
        SimSetupDialog.__init__(self)
        self.assy = assy
        self.nframes = 900
        self.temp = 300
        self.stepsper = 10
        self.timestep = 10
        self.filename = ''
        self.fileform = ''
        self.mext = '.dpb'

    def NumFramesValueChanged(self,a0):
        self.nframes = a0

    def NameFilePressed(self):
        self.filename = ''

    def GoPressed(self):
        QDialog.accept(self)
        import os, sys
        
        #If a new model, save first
        if not self.assy.alist:
            QMessageBox.critical(self, "Error", "You must save the current model before simulation.")
            return
        
        #If the current file directory is not writable or file name has space in it, warn user
        fPath, fName = os.path.split(self.assy.filename)
        if not os.access(fPath, os.W_OK):
            QMessageBox.critical(self, "Error", "You need to make sure you have write permission in the opened file directory.")
            return
        
        import re    
        m = re.search(' +',  self.assy.filename)
        if  m:
            QMessageBox.critical(self, "Errors", "You need to make sure you don't have file name/path with space in it.")
            return
                
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
       
        args = [filePath + '/../bin/simulator', '-f' + str(self.nframes), '-t' + str(self.temp), '-i' + str(self.stepsper),  str(self.fileform),  self.assy.filename]
        
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        
        try:
            self.assy.w.statusBar.message("Calculating...")
            if self.assy.modified: writemmp(self.assy, self.assy.filename)
            r = os.spawnv(os.P_WAIT, filePath + '/../bin/simulator', args)
            s = None
        except:
            print_compact_traceback("exception in simulation; continuing: ")
            s = "internal error (traceback printed elsewhere)"
            r = -1 # simulate failure
        QApplication.restoreOverrideCursor() # Restore the cursor
        if not r:
            self.assy.w.statusBar.message("Movie written to "+self.assy.filename[:-3]+'dpb')
        else:
            if not s: s = "exit code %r" % r
            self.assy.w.statusBar.message("Simulation Failed!") ##e include s?
            QMessageBox.warning(self.assy.w, "Simulation Failed:", s)
        return

    def StepsChanged(self,a0):
        self.stepsper = 10

    def TemperatureChanged(self,a0):
        self.temp = 300

    def TimeStepChanged(self,a0):
        self.timestep = 10

    def FileFormat(self,a0):
        if a0 == 0: # DPB file format
            self.fileform = ''
            self.mext = '.dpb'
        else: # XYZ file format
            self.fileform = '-x'
            self.mext = '.xyz'

