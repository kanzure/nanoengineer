# Copyright (c) 2006 Nanorex, Inc. All rights reserved.
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
    int Interrupted
    double MinimizeThresholdCutoverRMS
    double MinimizeThresholdCutoverMax
    double MinimizeThresholdEndRMS
    double MinimizeThresholdEndMax
    char *IDKey
    char *BaseFileName
    char *InputFileName
    char *OutputFileName
    char *TraceFileName
    double Dt
    double Dx
    double Dmass
    double Temperature
    # end of globals.c stuff
    char *errString

    setWriteTraceCallbackFunc(PyObject)
    setFrameCallbackFunc(PyObject)
    getFrame_c()
    initsimhelp()
    void dumpPart()
    everythingElse()
    everythingDone()
    cdef char *structCompareHelp()

    void strcpy(char *, char *) #bruce 051230 guess

    void reinitSimGlobals(PyObject)
    verifySimObject(PyObject)
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

cdef class BaseSimulator:
    """Pyrex permits access to doc strings"""

    # cdef double *data

    # bruce 060103 comments: BaseSimulator needs an __init__ method which resets all globals 
    # to their desired initial values, in order to make this correct for successive 
    # uses of one of these objects in one session. ###@@@
    # Current code does not support more than one of these objects being active
    # at one time (trying this will crash); but it's ok to use several in succession 
    # except for the issue of the globals not being reset to their initial values.
    
    def __getattr__(self, char *key):
        verifySimObject(self)
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
        elif strcmp(key, "IDKey") == 0:
            return IDKey
        elif strcmp(key, "baseFilename") == 0:
            #bruce 051230 prevent exception when this is NULL (its default value)
            if BaseFileName == NULL:
                # not sure if None would be permitted here
                # probably it would, but this is better anyway
                return ""
            return BaseFileName
        elif strcmp(key, "OutFileName") == 0:
            if OutputFileName == NULL:
                # should we raise an AttributeError here?
                return ""
            return OutputFileName
        elif strcmp(key, "TraceFileName") == 0:
            if TraceFileName == NULL:
                # should we raise an AttributeError here?
                return ""
            return TraceFileName
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
        verifySimObject(self)
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
        elif strcmp(key, "IDKey") == 0:
            global IDKey
            IDKey = value
        elif strcmp(key, "baseFilename") == 0:
            global BaseFileName
            BaseFileName = value
        elif strcmp(key, "OutFileName") == 0:
            global OutputFileName
            OutputFileName = value
        elif strcmp(key, "TraceFileName") == 0:
            global TraceFileName
            TraceFileName = value
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

        verifySimObject(self)
        setFrameCallbackFunc(frame_callback)
        setWriteTraceCallbackFunc(trace_callback)
        srand(0)
        try:
            everythingElse()
        finally:
            # I don't want to bother saving/restoring an old frame_callback, 
            # since I think having a permanent one should be deprecated [bruce 060102]
            # framebacks are cleared in everythingDone
            everythingDone()
        return

    def structCompare(self):
        verifySimObject(self)
        r = structCompare()
        if r:
            raise Exception, r

class Minimize(BaseSimulator):
    def __init__(self, fname):
        global InputFileName
        reinitSimGlobals(self)
        self.ToMinimize = 1
        self.DumpAsText = 1
        self.PrintFrameNums = 0
        InputFileName = fname
        initsimhelp()

class Dynamics(BaseSimulator): #bruce 060101 changed superclass from Minimize to BaseSimulator
    def __init__(self, fname):
        global InputFileName
        reinitSimGlobals(self)
        self.ToMinimize = 0
        self.DumpAsText = 0
        self.PrintFrameNums = 0
        InputFileName = fname
        initsimhelp()

def setErrorString(str):
    errString = str

def getEquilibriumDistanceForBond(element1, element2, order):
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
    initializeBondTable()
    return getBondEquilibriumDistance(int_el1, int_el2, c_order[0])

#####################################################
# Per-frame callbacks to Python, wware 060101

def getFrame():
    frm = getFrame_c()
    num_atoms = len(frm) / (3 * 8)
    array = Numeric.fromstring(frm, Numeric.Float64)
    return Numeric.resize(array, [num_atoms, 3])

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# conventional globals for callback -- they don't have to be used
frameNumber = 0
frameFreq = 1

callbackCounter = 0

def myCallback():
    global frameNumber
    frameNumber = frameNumber + 1
    if (frameNumber % frameFreq) == 0:
        #print "frame %d:" % frameNumber, getFrame()
        global callbackCounter
        callbackCounter = callbackCounter + 1

#bruce 060101 made testsetup a function so it only happens when asked for,
# not on every import and sim run (for example, runSim.py doesn't want it)

def testsetup(freq=1): 
    "conventional setup for test functions; returns frame_callback argument for .go method"
    global frameNumber, frameFreq, callbackCounter
    callbackCounter = 0
    frameNumber = 0
    frameFreq = max(1, freq)
    return myCallback

tracefile = [ ]

def tracecallback(str):
    global tracefile
    tracefile.append(str)
def badcallback(str):
    raise RuntimeError, "This is a bad callback"
def badcallback2():
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
        global tracefile
        tracefile = [ ]

    def test_getEquilibriumDistance(self):
        # try C-C single bond; prints 154.88
        assert (getEquilibriumDistanceForBond(6, 6, '1') - 154.88) ** 2 < 0.1

    def test_framecallback(self):
        func = testsetup(2)
        m = Minimize("tests/minimize/test_h2.mmp")
        m.go(frame_callback=func)
        assert callbackCounter == 4, "Callback counter is %d, not 4" %(callbackCounter)

    def test_frameAndTraceCallback(self):
        func = testsetup(10)
        d = Dynamics("tests/rigid_organics/test_C6H10.mmp")
        d.go(frame_callback=func, trace_callback=tracecallback)
        assert callbackCounter == 10

    def test_traceCallbackWithMotor(self):
        d = Dynamics("tests/dynamics/test_0001.mmp")
        d.go(trace_callback=tracecallback)
        # Make sure there is motor information being printed
        assert len(tracefile[-5].split()) == 3, \
               "Motor info not appearing in trace file:" + tracefile[18]

    def test_dpbFileShouldBeBinary(self):
        d = Dynamics("tests/dynamics/test_0001.mmp")
        d.go()
        # Make sure that the DPB file is really binary
        assert not isFileAscii("tests/dynamics/test_0001.dpb")

    def test_dpbFileShouldBeBinaryAfterMinimize(self):
        # bruce 060103 added this; it presently fails, but I hope to fix it in same commit
        m = Minimize("tests/minimize/test_h2.mmp")
        m.go()
        d = Dynamics("tests/dynamics/test_0001.mmp")
        d.go()
        # Make sure that the DPB file is really binary, even after Minimize is run
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
            d = Dynamics("tests/dynamics/test_0001.mmp")
            d.go(trace_callback=badcallback)
            assert False, "This test should have failed"
        except RuntimeError, e:
            assert e.args[0] == "This is a bad callback"

    def test_badCallback2(self):
        try:
            d = Dynamics("tests/dynamics/test_0001.mmp")
            d.go(trace_callback=badcallback2)
            assert False, "This test should have failed"
        except TypeError:
            pass

    def test_badCallback3(self):
        try:
            d = Dynamics("tests/dynamics/test_0001.mmp")
            d.go(trace_callback=42)
            assert False, "This test should have failed"
        except RuntimeError, e:
            assert e.args[0] == "bad callback"

    def test_callWrongSimulatorObject(self):
        try:
            m = Minimize("tests/dynamics/test_0001.mmp")
            d = Dynamics("tests/dynamics/test_0001.mmp")
            m.go(trace_callback=42)
            assert False, "This test should have failed"
        except AssertionError, e:
            assert e.args[0] == "not the most recent simulator object"

#
# make pyx && python -c "import sim; sim.test()"
#

def test():
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
