# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

from SimSetupDialog import *

class runSim(SimSetupDialog):
    def __init__(self, assy):
        SimSetupDialog.__init__(self)
        self.assy = assy
        self.nframes = 900
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
        print ("physeng -f" + str(self.nframes)
               + " -t" + str(self.temp)
               + " -i" + str(self.stepsper)
               + " -s" + str(self.timestep)
               + " " + self.assy.filename)

    def StepsChanged(self,a0):
        self.stepsper = 10

    def TemperatureChanged(self,a0):
        self.temp = 300

    def TimeStepChanged(self,a0):
        self.timestep = 10

    def FileFormat(self,a0):
        self.fileform = a0
       