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
        self.nframes = 300
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
        tmpFilePath = self.assy.w.tmpFilePath
        if not self.assy.filename: 
                self.assy.filename= os.path.join(tmpFilePath, "simulate.mmp")
        
        #By writting the current model into simulate.mmp under ~/nanorex, no matter
        # if it is a *.pdb, a *.mmp with model change or not, we'll make sure the
        #writing of the *.dpb file will only go to the temporary directory, 
        # otherwise user may get write permission problem.  ---Huaicai 12/07/04
        writemmp(self.assy, os.path.join(tmpFilePath, "simulate.mmp"))
        
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
       
        args = [filePath + '/../bin/simulator', '-f' + str(self.nframes), '-t' + str(self.temp), '-i' + str(self.stepsper),  str(self.fileform),  "simulate.mmp"]
        
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        oldWorkingDir = os.getcwd()
        os.chdir(tmpFilePath)

        try:
            self.assy.w.statusBar.message("Calculating...")
            #if self.assy.modified: writemmp(self.assy, self.assy.filename)
            r = os.spawnv(os.P_WAIT, filePath + '/../bin/simulator', args)
        except:
            print_compact_traceback("exception in simulation; continuing: ")
            s = "internal error (traceback printed elsewhere)"
            r = -1 # simulate failure
        os.chdir(oldWorkingDir)    
        QApplication.restoreOverrideCursor() # Restore the cursor
        if not r:
            self.assy.w.statusBar.message("Movie written to "+ os.path.join(tmpFilePath, "simulate" + self.mext))
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