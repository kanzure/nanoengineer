# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

from SimSetupDialog import *
from fileIO import writemmp
from commands import *
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
        if not self.assy.filename: self.assy.filename="simulate.mmp"
        cmd = ("simulator -f" + str(self.nframes)
               + " -t" + str(self.temp)
               + " -i" + str(self.stepsper)
#               + " -s" + str(self.timestep)
               + " " + self.assy.filename)
        print cmd
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        try:
            self.assy.w.msgbarLabel.setText("Calculating...")
            if self.assy.modified: writemmp(self.assy, self.assy.filename)
            pipe = os.popen(cmd)
            r = pipe.close() # false (0) means success, true means failure
        except:
            print_compact_traceback("exception in minimize; continuing: ")
            s = "internal error (traceback printed elsewhere)"
            r = -1 # simulate failure
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
       