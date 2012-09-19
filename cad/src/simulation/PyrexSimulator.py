# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
PyrexSimulator.py - Wrapper around the pyrex/C ND-1 simulator code.
Responsible for maintaining references to strings which are passed
to the C code, and which end up referenced by variables defined in
src/sim/globals.c.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""

import os
import foundation.env as env
from platform_dependent.PlatformDependent import find_plugin_dir

_thePyrexSimulator = None

class _PyrexSimulator(object):
    def __init__(self):
        global _thePyrexSimulator
        assert (_thePyrexSimulator is None)
        _thePyrexSimulator = self
        import sim # this import must not be done at toplevel
        self.sim = sim.theSimulator()

        ok, nd1_plugin_path = find_plugin_dir("NanoDynamics-1")
        if (not ok):
            env.history.redmsg("Error: can't find " + nd1_plugin_path)
            nd1_plugin_path = "."
        self.system_parameters_file = os.path.join(nd1_plugin_path, "sim-params.txt")
        self.amber_bonded_parameters_file = os.path.join(nd1_plugin_path, "ffamber03bon.itp")
        self.amber_nonbonded_parameters_file = os.path.join(nd1_plugin_path, "ffamber03nb.itp")
        self.amber_charges_file = os.path.join(nd1_plugin_path, "ffamber03charge.itp")

    def reInitialize(self):
        self.sim.reinitGlobals()
        self.sim.SystemParametersFileName = self.system_parameters_file
        self.sim.AmberBondedParametersFileName = self.amber_bonded_parameters_file
        self.sim.AmberNonbondedParametersFileName = self.amber_nonbonded_parameters_file
        self.sim.AmberChargesFileName = self.amber_charges_file

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

    def run(self, frame_callback = None, trace_callback = None):
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
