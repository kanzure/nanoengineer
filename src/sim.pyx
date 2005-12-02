cdef extern from "simhelp.c":
    ctypedef struct SimArgs:
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
        char *IDKey
        char *baseFilename
        double Dt
        double Dx
        double Dmass
        double Temperature
        char *printPotential
        double printPotentialInitial
        double printPotentialIncrement
        double printPotentialLimit
        int printPotentialEnergy
        char *ofilename
        char *tfilename
        char *filename
    cdef SimArgs myArgs
    int initsimhelp()
    void readPart()
    void dumpPart()
    void everythingElse()
    cdef char *structCompareHelp()

def initsim(debug_flags=0,
            Iteration=0,
            ToMinimize=0,
            IterPerFrame=10,
            NumFrames=100,
            DumpAsText=0,
            DumpIntermediateText=0,
            PrintFrameNums=1,
            OutputFormat=1,
            KeyRecordInterval=32,
            DirectEvaluate=1, # XXX should default to 0 eventually
            IDKey="",
            baseFilename="",
            Dt=1e-16,              # seconds
            Dx=1e-12,              # meters
            Dmass=1e-27,           # units of mass vs. kg
            Temperature=300.0,     # Kelvins
            printPotentialInitial=1, # pm
            printPotentialIncrement=1, # pm
            printPotentialLimit=200, # pm
            printPotentialEnergy=0,
            printPotential="",
            ofilename="",
            tfilename="",
            filename=""):
    """There has GOT to be a better way to do this than what I'm doing
    here. But I don't think Pyrex can write to a C global variable. So
    pack everything into one big horrible struct on the Python side,
    then unpack it on the C side. Ugly.
    """
    if not filename:
        raise Exception("Need a filename (probably MMP)")

    myArgs.debug_flags = debug_flags
    myArgs.Iteration = Iteration
    myArgs.ToMinimize = ToMinimize
    myArgs.IterPerFrame = IterPerFrame
    myArgs.NumFrames = NumFrames
    myArgs.DumpAsText = DumpAsText
    myArgs.DumpIntermediateText = DumpIntermediateText
    myArgs.PrintFrameNums = PrintFrameNums
    myArgs.OutputFormat = OutputFormat
    myArgs.KeyRecordInterval = KeyRecordInterval
    myArgs.DirectEvaluate = DirectEvaluate
    myArgs.IDKey = IDKey
    myArgs.baseFilename = baseFilename
    myArgs.Dt = Dt
    myArgs.Dx = Dx
    myArgs.Dmass = Dmass
    myArgs.Temperature = Temperature
    myArgs.printPotential = printPotential
    myArgs.printPotentialInitial = printPotentialInitial
    myArgs.printPotentialIncrement = printPotentialIncrement
    myArgs.printPotentialLimit = printPotentialLimit
    myArgs.printPotentialEnergy = printPotentialEnergy
    myArgs.printPotential = printPotential
    myArgs.ofilename = ofilename
    myArgs.tfilename = tfilename
    myArgs.filename = filename

    if initsimhelp():
        raise Exception, "please only run initsim() once!"

def structCompare():
    r = structCompareHelp()
    if r:
        raise Exception, r

def test():
    initsim(ToMinimize=1, DumpAsText=1,
            filename="tests/rigid_organics/test_C6H10.mmp")
    readPart()
    #dumpPart()
    everythingElse()
