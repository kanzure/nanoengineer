"""
sim.pyx

$Id$

Example usage script:

make clean; make pyx && python -c "import sim; sim.test()"
"""
__author__ = "Will"

import threading

cdef extern from "simhelp.c":
    ctypedef struct two_contexts:
        # pyrex doesn't need to know what's inside
        pass
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

    two_contexts *malloc_two_contexts()
    void free_two_contexts(two_contexts *)
    void swap_contexts(two_contexts *)

    void initsimhelp()
    void readPart()
    void dumpPart()
    void everythingElse()
    cdef char *structCompareHelp()

    void strcpy(char *, char *) #bruce 051230 guess


cdef class SimulatorBase:
    """Pyrex permits access to doc strings"""
    cdef two_contexts *mine

    def __init__(self):
        self.mine = malloc_two_contexts()

    def __del__(self):
        free_two_contexts(self.mine)

    def swap(self):
        swap_contexts(self.mine)



class Minimize(SimulatorBase):
    """Pyrex permits access to doc strings"""

    def __init__(self, filename):
        global ToMinimize, DumpAsText
        ToMinimize = 1
        DumpAsText = 1
        self.__init(filename)

    def __init(self, filename):
        if not filename:
            raise Exception("Need a filename (probably MMP)")
        SimulatorBase.__init__(self)
        self.simlock = threading.Lock()
        self.do(self.__read_innards, filename)

    def do(self, f, *args, **kw):
        lock = self.simlock
        retval = None
        exc = None
        lock.acquire()
        self.swap()
            # note: this could be done more efficiently (usually no swaps, not two), with simpler code,
            # as described on the wiki under "context switching" [bruce 051230 comment]
        try:
            retval = f(*args, **kw)
        except Exception, e:
            exc = e
        self.swap()
        lock.release()
        if exc != None:
            raise exc
        return retval

    def __get_innards(self, key):
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
            if baseFilename == NULL: #bruce 051230 prevent exception when this is NULL (its default value)
                return "" # (not sure if None would be permitted here; probably it would, but this is better anyway)
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

    def __set_innards(self, key, value):
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

    def get(self, key):
        """Access to simulator's command line options and globals.c
        goodies
        """
        return self.do(self.__get_innards, key)

    def set(self, key, value):
        """Access to simulator's command line options and globals.c
        goodies
        """ 
        self.do(self.__set_innards, key, value)

    def __everythingElse_innards(self):
        everythingElse()

    def go(self):
        self.do(self.__everythingElse_innards)

    def __read_innards(self, fname):
        global filename
        filename = fname
        initsimhelp()
        readPart()

    def __structCompare_innards(self):
        structCompare()

    def structCompare(self):
        r = self.do(self.__structCompareHelp_innards)
        if r:
            raise Exception, r


class Dynamics(Minimize):
    def __init__(self, filename):
        global ToMinimize, DumpAsText
        ToMinimize = 0
        DumpAsText = 0
        self.__init(filename)

def test():
    m = Minimize("tests/rigid_organics/test_C6H10.mmp")
    m.go()
    print
    d = Dynamics("tests/rigid_organics/test_C6H10.mmp")
    d.go()
