# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
sim.pyx

$Id$

Note: this file is processed by Pyrex to produce sim.c in this directory
(not in the build subdirectory). [bruce 060101]

Example usage script:
  make clean; make pyx && python -c "import sim; sim.test()"
"""
__author__ = "Will"

## import threading #bruce 060101 removed this since I think it's not used now

try:
    import Numeric
except ImportError:
    import numpy as Numeric
import unittest

cdef extern from "simhelp.c": 
    # note: this produces '#include "simhelp.c"' in generated sim.c file,
    # but distutils fails to realize there's a dependency on simhelp.c,
    # so Will added a setup.py dependency to fix that. [bruce 060101]

    # stuff from globals.c
    int debug_flags
    int Iteration
    int ToMinimize
    int IterPerFrame
    int NumFrames
    int DumpAsText
    int DumpIntermediateText
    int PrintFrameNums
    int OutputFormat
    int KeyRecordInterval
    int DirectEvaluate
    int PrintPotentialEnergy
    int Interrupted
    double MinimizeThresholdCutoverRMS
    double MinimizeThresholdCutoverMax
    double MinimizeThresholdEndRMS
    double MinimizeThresholdEndMax
    double VanDerWaalsCutoffRadius
    double VanDerWaalsCutoffFactor
    int EnableElectrostatic
    int NeighborSearching
    double ThermostatGamma
    int UseAMBER
    int TypeFeedback
    char *IDKey
    char *BaseFileName
    char *InputFileName
    char *OutputFileName
    char *TraceFileName
    char *GromacsOutputBaseName
    char *PathToCpp
    char *SystemParametersFileName
    char *AmberBondedParametersFileName
    char *AmberNonbondedParametersFileName
    char *AmberChargesFileName

    double Dt
    double Dx
    double Dmass
    double Temperature
    # end of globals.c stuff

    setWriteTraceCallbackFunc(PyObject)
    setFrameCallbackFunc(PyObject)
    getFrame_c()
    pyrexInitBondTable()
    void dumpPart()
    void reinit_globals()
    everythingElse()
    everythingDone()
    cdef char *structCompareHelp()

    void strcpy(char *, char *) #bruce 051230 guess

    void reinitSimGlobals(PyObject)
    specialExceptionIs(PyObject)

    #void dynamicsMovie_start()
    #void dynamicsMovie_step()
    #void dynamicsMovie_finish()
    void initializeBondTable()
    double getBondEquilibriumDistance(int element1, int element2, char bondOrder)

cdef extern from "string.h":
    int strcmp(char *s1, char *s2)

cdef extern from "stdlib.h":
    void srand(unsigned int)

# wware 060111  a special exception for simulator interruptions
class SimulatorInterrupted(Exception):
    pass

specialExceptionIs(SimulatorInterrupted)

cdef class _Simulator:
    """Pyrex permits access to doc strings"""

    # cdef double *data

    # bruce 060103 comments: BaseSimulator needs an __init__ method which resets all globals 
    # to their desired initial values, in order to make this correct for successive 
    # uses of one of these objects in one session. ###@@@
    # Current code does not support more than one of these objects being active
    # at one time (trying this will crash); but it's ok to use several in succession 
    # except for the issue of the globals not being reset to their initial values.
    
    def __getattr__(self, char *key):
        if key.startswith('_'):
            # important optimization (when Python asks for __xxx__) [bruce 060102]
            raise AttributeError, key
        if strcmp(key, "debug_flags") == 0:
            return debug_flags
        elif strcmp(key, "Iteration") == 0:
            return Iteration
        elif strcmp(key, "ToMinimize") == 0:
            return ToMinimize
        elif strcmp(key, "IterPerFrame") == 0:
            return IterPerFrame
        elif strcmp(key, "NumFrames") == 0:
            return NumFrames
        elif strcmp(key, "DumpAsText") == 0:
            return DumpAsText
        elif strcmp(key, "DumpIntermediateText") == 0:
            return DumpIntermediateText
        elif strcmp(key, "PrintFrameNums") == 0:
            return PrintFrameNums
        elif strcmp(key, "OutputFormat") == 0:
            return OutputFormat
        elif strcmp(key, "KeyRecordInterval") == 0:
            return KeyRecordInterval
        elif strcmp(key, "DirectEvaluate") == 0:
            return DirectEvaluate
        elif strcmp(key, "PrintPotentialEnergy") == 0:
            return PrintPotentialEnergy
        elif strcmp(key, "Interrupted") == 0:
            return Interrupted
        elif strcmp(key, "MinimizeThresholdCutoverRMS") == 0:
            return MinimizeThresholdCutoverRMS
        elif strcmp(key, "MinimizeThresholdCutoverMax") == 0:
            return MinimizeThresholdCutoverMax
        elif strcmp(key, "MinimizeThresholdEndRMS") == 0:
            return MinimizeThresholdEndRMS
        elif strcmp(key, "MinimizeThresholdEndMax") == 0:
            return MinimizeThresholdEndMax
        elif strcmp(key, "VanDerWaalsCutoffRadius") == 0:
            return VanDerWaalsCutoffRadius
        elif strcmp(key, "VanDerWaalsCutoffFactor") == 0:
            return VanDerWaalsCutoffFactor
        elif strcmp(key, "EnableElectrostatic") == 0:
            return EnableElectrostatic
        elif strcmp(key, "NeighborSearching") == 0:
            return NeighborSearching
        elif strcmp(key, "UseAMBER") == 0:
            return UseAMBER
        elif strcmp(key, "TypeFeedback") == 0:
            return TypeFeedback
        elif strcmp(key, "ThermostatGamma") == 0:
            return ThermostatGamma
        elif strcmp(key, "IDKey") == 0:
            return IDKey
        elif strcmp(key, "baseFilename") == 0:
            #bruce 051230 prevent exception when this is NULL (its default value)
            if BaseFileName == NULL:
                # not sure if None would be permitted here
                # probably it would, but this is better anyway
                return ""
            return BaseFileName
        elif strcmp(key, "InputFileName") == 0:
            if InputFileName == NULL:
                # should we raise an AttributeError here?
                return ""
            return InputFileName
        elif strcmp(key, "OutputFileName") == 0:
            if OutputFileName == NULL:
                # should we raise an AttributeError here?
                return ""
            return OutputFileName
        elif strcmp(key, "TraceFileName") == 0:
            if TraceFileName == NULL:
                # should we raise an AttributeError here?
                return ""
            return TraceFileName
        elif strcmp(key, "GromacsOutputBaseName") == 0:
            if GromacsOutputBaseName == NULL:
                # should we raise an AttributeError here?
                return ""
            return GromacsOutputBaseName
        elif strcmp(key, "PathToCpp") == 0:
            if PathToCpp == NULL:
                # should we raise an AttributeError here?
                return ""
            return PathToCpp
        elif strcmp(key, "SystemParametersFileName") == 0:
            if SystemParametersFileName == NULL:
                # should we raise an AttributeError here?
                return ""
            return SystemParametersFileName
        elif strcmp(key, "AmberBondedParametersFileName") == 0:
            if AmberBondedParametersFileName == NULL:
                # should we raise an AttributeError here?
                return ""
            return AmberBondedParametersFileName
        elif strcmp(key, "AmberNonbondedParametersFileName") == 0:
            if AmberNonbondedParametersFileName == NULL:
                # should we raise an AttributeError here?
                return ""
            return AmberNonbondedParametersFileName
        elif strcmp(key, "AmberChargesFileName") == 0:
            if AmberChargesFileName == NULL:
                # should we raise an AttributeError here?
                return ""
            return AmberChargesFileName
        elif strcmp(key, "Dt") == 0:
            return Dt
        elif strcmp(key, "Dx") == 0:
            return Dx
        elif strcmp(key, "Dmass") == 0:
            return Dmass
        elif strcmp(key, "Temperature") == 0:
            return Temperature
        else:
            raise AttributeError, key

    def __setattr__(self, char *key, value):
        if strcmp(key, "debug_flags") == 0:
            global debug_flags
            debug_flags = value
        elif strcmp(key, "Iteration") == 0:
            global Iteration
            Iteration = value
        elif strcmp(key, "ToMinimize") == 0:
            global ToMinimize
            ToMinimize = value
        elif strcmp(key, "IterPerFrame") == 0:
            global IterPerFrame
            IterPerFrame = value
        elif strcmp(key, "NumFrames") == 0:
            global NumFrames
            NumFrames = value
        elif strcmp(key, "DumpAsText") == 0:
            global DumpAsText
            DumpAsText = value
        elif strcmp(key, "DumpIntermediateText") == 0:
            global DumpIntermediateText
            DumpIntermediateText = value
        elif strcmp(key, "PrintFrameNums") == 0:
            global PrintFrameNums
            PrintFrameNums = value
        elif strcmp(key, "OutputFormat") == 0:
            global OutputFormat
            OutputFormat = value
        elif strcmp(key, "KeyRecordInterval") == 0:
            global KeyRecordInterval
            KeyRecordInterval = value
        elif strcmp(key, "DirectEvaluate") == 0:
            global DirectEvaluate
            DirectEvaluate = value
        elif strcmp(key, "PrintPotentialEnergy") == 0:
            global PrintPotentialEnergy
            PrintPotentialEnergy = value
        elif strcmp(key, "Interrupted") == 0:
            global Interrupted
            Interrupted = value
        elif strcmp(key, "MinimizeThresholdCutoverRMS") == 0:
            global MinimizeThresholdCutoverRMS
            MinimizeThresholdCutoverRMS = value
        elif strcmp(key, "MinimizeThresholdCutoverMax") == 0:
            global MinimizeThresholdCutoverMax
            MinimizeThresholdCutoverMax = value
        elif strcmp(key, "MinimizeThresholdEndRMS") == 0:
            global MinimizeThresholdEndRMS
            MinimizeThresholdEndRMS = value
        elif strcmp(key, "MinimizeThresholdEndMax") == 0:
            global MinimizeThresholdEndMax
            MinimizeThresholdEndMax = value
        elif strcmp(key, "VanDerWaalsCutoffRadius") == 0:
            global VanDerWaalsCutoffRadius
            VanDerWaalsCutoffRadius = value
        elif strcmp(key, "VanDerWaalsCutoffFactor") == 0:
            global VanDerWaalsCutoffFactor
            VanDerWaalsCutoffFactor = value
        elif strcmp(key, "EnableElectrostatic") == 0:
            global EnableElectrostatic
            EnableElectrostatic = value
        elif strcmp(key, "NeighborSearching") == 0:
            global NeighborSearching
            NeighborSearching = value
        elif strcmp(key, "UseAMBER") == 0:
            global UseAMBER
            UseAMBER = value
        elif strcmp(key, "TypeFeedback") == 0:
            global TypeFeedback
            TypeFeedback = value
        elif strcmp(key, "ThermostatGamma") == 0:
            global ThermostatGamma
            ThermostatGamma = value
        elif strcmp(key, "IDKey") == 0:
            global IDKey
            IDKey = value
        elif strcmp(key, "baseFilename") == 0:
            global BaseFileName
            BaseFileName = value
        elif strcmp(key, "InputFileName") == 0:
            global InputFileName
            InputFileName = value
        elif strcmp(key, "OutputFileName") == 0:
            global OutputFileName
            OutputFileName = value
        elif strcmp(key, "TraceFileName") == 0:
            global TraceFileName
            TraceFileName = value
        elif strcmp(key, "GromacsOutputBaseName") == 0:
            global GromacsOutputBaseName
            GromacsOutputBaseName = value
        elif strcmp(key, "PathToCpp") == 0:
            global PathToCpp
            PathToCpp = value
        elif strcmp(key, "SystemParametersFileName") == 0:
            global SystemParametersFileName
            SystemParametersFileName = value
        elif strcmp(key, "AmberBondedParametersFileName") == 0:
            global AmberBondedParametersFileName
            AmberBondedParametersFileName = value
        elif strcmp(key, "AmberNonbondedParametersFileName") == 0:
            global AmberNonbondedParametersFileName
            AmberNonbondedParametersFileName = value
        elif strcmp(key, "AmberChargesFileName") == 0:
            global AmberChargesFileName
            AmberChargesFileName = value
        elif strcmp(key, "Dt") == 0:
            global Dt
            Dt = value
        elif strcmp(key, "Dx") == 0:
            global Dx
            Dx = value
        elif strcmp(key, "Dmass") == 0:
            global Dmass
            Dmass = value
        elif strcmp(key, "Temperature") == 0:
            global Temperature
            Temperature = value
        else:
            raise AttributeError, key

    def go(self, frame_callback=None, trace_callback=None):
        "run the simulator loop; optional frame_callback should be None or a callable object"
        
        #e if there's an exception in the callback, maybe that should abort the sim run
        # (requiring change to callback-call-helper in simhelp.c, I think)
        # and reraise that exception or some other one from this method
        #bruce 060103

        setFrameCallbackFunc(frame_callback)
        setWriteTraceCallbackFunc(trace_callback)
        srand(0)
        everythingElse()
        # I don't want to bother saving/restoring an old frame_callback, 
        # since I think having a permanent one should be deprecated [bruce 060102]
        # framebacks are cleared in everythingDone
        everythingDone()
        return

    def structCompare(self):
        r = structCompare()
        if r:
            raise Exception, r

    def reinitGlobals(self):
        reinit_globals()

    def getEquilibriumDistanceForBond(self, element1, element2, order):
        # element1 and element2 are python ints
        # order is a python string
        cdef int int_el1, int_el2
        cdef char *c_order
        int_el1 = element1
        int_el2 = element2
        c_order = order
        # initializeBondTable should not require a tracefile, so can be called
        # at any time.  It must have been called before either parsing an mmp
        # file, or calling getBondEquilibriumDistance().  It checks to see if
        # it's been called already, so it's cheap if that's the case.  It
        # shouldn't affect the saved warning flags in any way.  Warnings are
        # only printed when bond information is retrieved, and
        # getBondEquilibriumDistance() avoids the warning code.
        pyrexInitBondTable()
        return getBondEquilibriumDistance(int_el1, int_el2, c_order[0])

    def getFrame(self):
        frm = getFrame_c()
        num_atoms = len(frm) / (3 * 8)
        array = Numeric.fromstring(frm, Numeric.Float64)
        return Numeric.resize(array, [num_atoms, 3])

_theSimulator = None

def theSimulator():
    global _theSimulator
    if (_theSimulator is None):
        _theSimulator = _Simulator()
    return _theSimulator

#####################################################################################
# Test code below this point

# conventional globals for callback -- they don't have to be used
_frameNumber = 0
_frameFreq = 1

_callbackCounter = 0

def _myCallback(last_frame):
    global _frameNumber
    _frameNumber = _frameNumber + 1
    if (_frameNumber % _frameFreq) == 0:
        #print "frame %d:" % _frameNumber, getFrame()
        global _callbackCounter
        _callbackCounter = _callbackCounter + 1

#bruce 060101 made testsetup a function so it only happens when asked for,
# not on every import and sim run (for example, runSim.py doesn't want it)

def _testsetup(freq=1): 
    "conventional setup for test functions; returns frame_callback argument for .go method"
    global _frameNumber, _frameFreq, _callbackCounter
    _callbackCounter = 0
    _frameNumber = 0
    _frameFreq = max(1, freq)
    return _myCallback

_tracefile = [ ]

def _tracecallback(str):
    global _tracefile
    _tracefile.append(str)
def _badcallback(str):
    raise RuntimeError, "This is a bad callback"
def _badcallback2():
    "This callback should really take an argument"
    pass

#####################################################

def isFileAscii(filename):
    from string import printable
    inf = open(filename)
    R = inf.read(1000)
    inf.close()
    nonascii = 0
    for x in R:
        if x not in printable:
            nonascii = nonascii + 1
    return nonascii < 20

class Tests(unittest.TestCase):

    def setUp(self):
        global _tracefile
        _tracefile = [ ]

    def test_getEquilibriumDistance(self):
        # try C-C single bond; prints 154.88
        assert (theSimulator().getEquilibriumDistanceForBond(6, 6, '1') - 154.88) ** 2 < 0.1

    def test_framecallback(self):
        func = _testsetup(2)
        m = theSimulator()

        m.reinitGlobals()
        m.InputFileName = "tests/minimize/test_h2.mmp"
        m.OutputFileName = "tests/minimize/test_h2.xyz"
        m.ToMinimize = 1
        m.DumpAsText = 1
        m.OutputFormat = 0

        m.go(frame_callback=func)
        assert _callbackCounter == 3, "Callback counter is %d, not 3" %(_callbackCounter)

    def test_frameAndTraceCallback(self):
        func = _testsetup(10)
        d = theSimulator()

        d.reinitGlobals()
        d.InputFileName = "tests/rigid_organics/test_C6H10.mmp"
        d.OutputFileName = "tests/rigid_organics/test_C6H10.dpb"
        d.ToMinimize = 0
        d.DumpAsText = 0
        d.OutputFormat = 1

        d.go(frame_callback=func, trace_callback=_tracecallback)
        assert _callbackCounter == 10

    def test_traceCallbackWithMotor(self):
        d = theSimulator()

        d.reinitGlobals()
        d.InputFileName = "tests/dynamics/test_0001.mmp"
        d.OutputFileName = "tests/dynamics/test_0001.dpb"
        d.ToMinimize = 0
        d.DumpAsText = 0
        d.OutputFormat = 1

        d.go(trace_callback=_tracecallback)
        # Make sure there is motor information being printed
        assert len(_tracefile[-5].split()) == 3, \
               "Motor info not appearing in trace file:" + _tracefile[18]

    def test_dpbFileShouldBeBinary(self):
        d = theSimulator()

        d.reinitGlobals()
        d.InputFileName = "tests/dynamics/test_0001.mmp"
        d.OutputFileName = "tests/dynamics/test_0001.dpb"
        d.ToMinimize = 0
        d.DumpAsText = 0
        d.OutputFormat = 1

        d.go()
        # Make sure that the DPB file is really binary
        assert not isFileAscii("tests/dynamics/test_0001.dpb")

##     def test_dynamicsStepStuff(self):
##         Dynamics("tests/rigid_organics/test_C6H10.mmp")
##         dynamicsMovie_start()
##         j = 0
##         for i in range(10000):
##             dynamicsMovie_step()
##             if (i % 500) == 0:
##                 #print "Here is frame", i
##                 #print getFrame()
##                 j = j + 1
##         dynamicsMovie_finish()
##         assert j == 20

    ######### Tests that should be expected to fail

    def test_badCallback1(self):
        try:
            d = theSimulator()

            d.reinitGlobals()
            d.InputFileName = "tests/dynamics/test_0001.mmp"
            d.OutputFileName = "tests/dynamics/test_0001.dpb"
            d.ToMinimize = 0
            d.DumpAsText = 0
            d.OutputFormat = 1

            d.go(trace_callback=_badcallback)
            assert False, "This test should have failed"
        except RuntimeError, e:
            assert e.args[0] == "This is a bad callback"

    def test_badCallback2(self):
        try:
            d = theSimulator()

            d.reinitGlobals()
            d.InputFileName = "tests/dynamics/test_0001.mmp"
            d.OutputFileName = "tests/dynamics/test_0001.dpb"
            d.ToMinimize = 0
            d.DumpAsText = 0
            d.OutputFormat = 1

            d.go(trace_callback=_badcallback2)
            assert False, "This test should have failed"
        except TypeError:
            pass

    def test_badCallback3(self):
        try:
            d = theSimulator()

            d.reinitGlobals()
            d.InputFileName = "tests/dynamics/test_0001.mmp"
            d.OutputFileName = "tests/dynamics/test_0001.dpb"
            d.ToMinimize = 0
            d.DumpAsText = 0
            d.OutputFormat = 1

            d.go(trace_callback=42)
            assert False, "This test should have failed"
        except RuntimeError, e:
            assert e.args[0] == "callback is not callable"

#
# make pyx && python -c "import sim; sim.test()"
#

def test():
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
