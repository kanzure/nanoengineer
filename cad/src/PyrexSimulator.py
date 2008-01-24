# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

"""
Wrapper around the pyrex/C simulator code.  Responsible for
maintaining references to strings which are passed to the C code, and
end up referenced by variables defined in src/sim/globals.c.
"""

import os
from PlatformDependent import find_plugin_dir

_thePyrexSimulator = None

class _PyrexSimulator(object):
    def __init__(self):
        global _thePyrexSimulator
        assert(_thePyrexSimulator is None)
        _thePyrexSimulator = self
        import sim
        self.sim = sim.theSimulator()

        ok, nd1_plugin_path = find_plugin_dir("NanoDynamics-1")
        if (not ok):
            env.history.message(redmsg(nd1_plugin_path))
            nd1_plugin_path = "."
        self.system_parameters_file = os.path.join(nd1_plugin_path, "sim-params.txt")

    def reInitialize(self):
        self.sim.reinitGlobals()
        self.sim.SystemParametersFileName = self.system_parameters_file

    def setup(self, mflag, filename):
        self.inputFileName = filename
        self.outputFileName = None

        self.reInitialize()
        if (mflag):
            self.sim.ToMinimize = 1
            self.sim.DumpAsText = 1
        else:
            self.sim.ToMinimize = 0
            self.sim.DumpAsText = 0
        self.sim.PrintFrameNums = 0
        self.sim.InputFileName = self.inputFileName

    def setOutputFileName(self, filename):
        self.outputFileName = filename

    def run(self, frame_callback=None, trace_callback=None):
        if (self.outputFileName is None):
            if (self.sim.DumpAsText):
                outputExtension = "xyz"
            else:
                outputExtension = "dpb"
            if (self.inputFileName.endswith(".mmp")):
                self.outputFileName = self.inputFileName[:-3] + outputExtension
            else:
                self.outputFileName = self.inputFileName + "." + outputExtension
        self.sim.OutputFileName = self.outputFileName
        if (self.sim.DumpAsText):
            self.sim.OutputFormat = 0
        else:
            self.sim.OutputFormat = 1
        self.sim.go(frame_callback, trace_callback)

    def getEquilibriumDistanceForBond(self, element1, element2, order):
        self.reInitialize()
        return self.sim.getEquilibriumDistanceForBond(element1, element2, order)

def thePyrexSimulator():
    global _thePyrexSimulator
    if (_thePyrexSimulator is None):
        _thePyrexSimulator = _PyrexSimulator()
    return _thePyrexSimulator
