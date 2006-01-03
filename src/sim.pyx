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

import Numeric

cdef extern from "simhelp.c": 
    # note: this produces '#include "simhelp.c"' in generated sim.c file,
    # but distutils fails to realize there's a dependency on simhelp.c,
    # so Will added a setup.py dependency to fix that. [bruce 060101]
    char *filename
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
    char *IDKey
    char *baseFilename
    char *OutFileName
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
    void initsimhelp()
    void readPart()
    void dumpPart()
    everythingElse()
    cdef char *structCompareHelp()

    void strcpy(char *, char *) #bruce 051230 guess

    void dynamicsMovie_start()
    void dynamicsMovie_step()
    void dynamicsMovie_finish()

cdef class BaseSimulator:
    """Pyrex permits access to doc strings"""

    # cdef double *data

    def __getattr__(self, key):
        if key.startswith('_'):
            # important optimization (when Python asks for __xxx__) [bruce 060102]
            raise AttributeError, key
        # the following could probably be optimized by converting key into a C string
        # [bruce guess 060102; comment in two places]
        if key == "debug_flags":
            return debug_flags
        elif key == "Iteration":
            return Iteration
        elif key == "ToMinimize":
            return ToMinimize
        elif key == "IterPerFrame":
            return IterPerFrame
        elif key == "NumFrames":
            return NumFrames
        elif key == "DumpAsText":
            return DumpAsText
        elif key == "DumpIntermediateText":
            return DumpIntermediateText
        elif key == "PrintFrameNums":
            return PrintFrameNums
        elif key == "OutputFormat":
            return OutputFormat
        elif key == "KeyRecordInterval":
            return KeyRecordInterval
        elif key == "DirectEvaluate":
            return DirectEvaluate
        elif key == "Interrupted":
            return Interrupted
        elif key == "IDKey":
            return IDKey
        elif key == "baseFilename":
            #bruce 051230 prevent exception when this is NULL (its default value)
            if baseFilename == NULL:
                # not sure if None would be permitted here
                # probably it would, but this is better anyway
                return ""
            return baseFilename
        elif key == "OutFileName":
            if OutFileName == NULL:
                return ""
            return OutFileName
        elif key == "TraceFileName":
            if TraceFileName == NULL:
                return ""
            return TraceFileName
        elif key == "Dt":
            return Dt
        elif key == "Dx":
            return Dx
        elif key == "Dmass":
            return Dmass
        elif key == "Temperature":
            return Temperature
        else:
            raise AttributeError, key

    def __setattr__(self, key, value):
        # the following could probably be optimized by converting key into a C string
        # [bruce guess 060102; comment in two places]
        if key == "debug_flags":
            global debug_flags
            debug_flags = value
        elif key == "Iteration":
            global Iteration
            Iteration = value
        elif key == "ToMinimize":
            global ToMinimize
            ToMinimize = value
        elif key == "IterPerFrame":
            global IterPerFrame
            IterPerFrame = value
        elif key == "NumFrames":
            global NumFrames
            NumFrames = value
        elif key == "DumpAsText":
            global DumpAsText
            DumpAsText = value
        elif key == "DumpIntermediateText":
            global DumpIntermediateText
            DumpIntermediateText = value
        elif key == "PrintFrameNums":
            global PrintFrameNums
            PrintFrameNums = value
        elif key == "OutputFormat":
            global OutputFormat
            OutputFormat = value
        elif key == "KeyRecordInterval":
            global KeyRecordInterval
            KeyRecordInterval = value
        elif key == "DirectEvaluate":
            global DirectEvaluate
            DirectEvaluate = value
        elif key == "Interrupted":
            global Interrupted
            Interrupted = value
        elif key == "IDKey":
            global IDKey
            IDKey = value
        elif key == "baseFilename":
            global baseFilename
            baseFilename = value
        elif key == "OutFileName":
            global OutFileName
            assert len(value) < 1024
            strcpy( OutFileName, value)
        elif key == "TraceFileName":
            global TraceFileName
            assert len(value) < 1024
            strcpy( TraceFileName, value)
        elif key == "Dt":
            global Dt
            Dt = value
        elif key == "Dx":
            global Dx
            Dx = value
        elif key == "Dmass":
            global Dmass
            Dmass = value
        elif key == "Temperature":
            global Temperature
            Temperature = value
        else:
            raise AttributeError, key

    def go(self, frame_callback=None, trace_callback=None):
        "run the simulator loop; optional frame_callback should be None or a callable object"
        # bruce 060102 adding frame_callback option, and try/finally to reset callback to None.
        ### note, this broke the test methods, need to make them pass their callback to .go().
        if callable(frame_callback):
            setFrameCallbackFunc(frame_callback)
        else:
            setFrameCallbackFunc(None)
        # I don't want to bother saving/restoring an old frame_callback, 
        # since I think having a permanent one should be deprecated [bruce 060102]
        if callable(trace_callback):
            setWriteTraceCallbackFunc(trace_callback)
        else:
            setWriteTraceCallbackFunc(None)
        try:
            everythingElse()
        finally:
            setFrameCallbackFunc(None)
            setWriteTraceCallbackFunc(None)
        return

    def structCompare(self):
        r = structCompare()
        if r:
            raise Exception, r

class Minimize(BaseSimulator):
    def __init__(self, fname):
        global filename
        self.ToMinimize = 1
        self.DumpAsText = 1
        filename = fname
        initsimhelp()
        readPart()

class Dynamics(BaseSimulator): #bruce 060101 changed superclass from Minimize to BaseSimulator
    def __init__(self, fname):
        global filename
        self.ToMinimize = 0
        self.DumpAsText = 0
        filename = fname
        initsimhelp()
        readPart()

def setErrorString(str):
    errString = str

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

def myCallback():
    global frameNumber
    frameNumber = frameNumber + 1
    if (frameNumber % frameFreq) == 0:
        print "frame %d:" % frameNumber, getFrame()

#bruce 060101 made testsetup a function so it only happens when asked for,
# not on every import and sim run (for example, runSim.py doesn't want it)

def testsetup(freq=1): 
    "conventional setup for test functions; returns frame_callback argument for .go method"
    global frameNumber, frameFreq
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

def test():
    func = testsetup(2)
    # m = Minimize("tests/rigid_organics/test_C6H10.mmp")
    m = Minimize("tests/minimize/test_h2.mmp")
    m.go(frame_callback = func)

def test2():
    func = testsetup(10)
    d = Dynamics("tests/rigid_organics/test_C6H10.mmp")
    d.go(frame_callback=func, trace_callback=tracecallback)

def test3():
    # Are we getting trace info correctly?
    # use a test with a motor
    d = Dynamics("tests/dynamics/test_0001.mmp")
    d.go(trace_callback=tracecallback)
    print "".join(tracefile)

def test3a():
    # Test bad callbacks
    d = Dynamics("tests/dynamics/test_0001.mmp")
    d.go(trace_callback=badcallback)

def test3b():
    # Test bad callbacks
    d = Dynamics("tests/dynamics/test_0001.mmp")
    d.go(trace_callback=badcallback2)

def test3c():
    # Test bad callbacks
    d = Dynamics("tests/dynamics/test_0001.mmp")
    d.go(trace_callback=42)

def test4():
    Dynamics("tests/rigid_organics/test_C6H10.mmp")
    dynamicsMovie_start()
    for i in range(10000):
        dynamicsMovie_step()
        if (i % 500) == 0:
            print "Here is frame", i
            print getFrame()
    dynamicsMovie_finish()
