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

    void setCallbackFunc(PyObject)
    getFrame_c()
    void initsimhelp()
    void readPart()
    void dumpPart()
    void everythingElse()
    cdef char *structCompareHelp()

    void strcpy(char *, char *) #bruce 051230 guess


cdef class BaseSimulator:
    """Pyrex permits access to doc strings"""

    # cdef double *data

    def __getattr__(self, key):
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

    def go(self):
        everythingElse()

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

def testsetup(freq = 1): 
    "conventional setup for test functions; can be done before or after initing sim object"
    global frameNumber, frameFreq
    frameNumber = 0
    frameFreq = max(1, freq)
    setCallbackFunc(myCallback)

def testunsetup(): #bruce 060101
    setCallbackFunc(None)

###e actually we often need to unset the callback at the end of a run, so, 
###  maybe it should be an argument to .go()... we'd just leave in all the
###  existing code, and add to "def go" (above) a setCallbackFunc(func) at start,
###  and a setCallbackFunc(None) at the end, protected from exceptions. [bruce 060101]

#####################################################

def test():
    testsetup(2)
    # m = Minimize("tests/rigid_organics/test_C6H10.mmp")
    m = Minimize("tests/minimize/test_h2.mmp")
    m.go()
    testunsetup()

def test2():
    d = Dynamics("tests/rigid_organics/test_C6H10.mmp")
    testsetup(10)
    d.go()
    testunsetup()

# end
