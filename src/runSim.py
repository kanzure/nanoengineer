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
        self.fileform = 0

    def NumFramesValueChanged(self,a0):
        self.nframes = a0

    def NameFilePressed(self):
        self.filename = ''

    def GoPressed(self):
        QDialog.accept(self)
        tmpFilePath = self.assy.w.tmpFilePath
        if not self.assy.filename: self.assy.filename= tmpFilePath + "simulate.mmp"
        import os, sys
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
       
        args = [filePath + '/../bin/simulator', '-f' + str(self.nframes), '-t' + str(self.temp), '-i' + str(self.stepsper), "simulate.mmp"]
        
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        oldWorkingDir = os.getcwd()
        os.chdir(tmpFilePath)
        try:
            self.assy.w.msgbarLabel.setText("Calculating...")
            if self.assy.modified: writemmp(self.assy, self.assy.filename)
            r = os.spawnv(os.P_WAIT, filePath + '/../bin/simulator', args)
        except:
            print_compact_traceback("exception in simulation; continuing: ")
            s = "internal error (traceback printed elsewhere)"
            r = -1 # simulate failure
        os.chdir(oldWorkingDir)    
        QApplication.restoreOverrideCursor() # Restore the cursor
        if not r:
            self.assy.w.msgbarLabel.setText("Movie written to "+self.assy.filename[:-3]+'dpb')
        else:
            if not s: s = "exit code %r" % r
            self.assy.w.msgbarLabel.setText("Simulation Failed!") ##e include s?
            QMessageBox.warning(self.assy.w, "Simulation Failed:", s)
        return

    def StepsChanged(self,a0):
        self.stepsper = 10

    def TemperatureChanged(self,a0):
        self.temp = 300

    def TimeStepChanged(self,a0):
        self.timestep = 10

    def FileFormat(self,a0):
        self.fileform = a0
       