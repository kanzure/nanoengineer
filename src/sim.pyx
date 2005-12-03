cdef extern from "simhelp.c":
    ctypedef struct SimArgs:
        char *printPotential
        double printPotentialInitial
        double printPotentialIncrement
        double printPotentialLimit
        int printPotentialEnergy
        char *ofilename
        char *tfilename
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
    char *IDKey
    char *baseFilename
    double Dt
    double Dx
    double Dmass
    double Temperature
    # end of globals.c stuff
    SimArgs myArgs
    int initsimhelp()
    void readPart()
    void dumpPart()
    void everythingElse()
    cdef char *structCompareHelp()

def initsim(filename,
            printPotentialInitial=1, # pm
            printPotentialIncrement=1, # pm
            printPotentialLimit=200, # pm
            printPotentialEnergy=0,
            printPotential="",
            ofilename="",
            tfilename=""):

    if not filename:
        raise Exception("Need a filename (probably MMP)")

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
    global ToMinimize, DumpAsText  # don't forget this
    ToMinimize=1
    DumpAsText=1
    initsim(filename="tests/rigid_organics/test_C6H10.mmp")
    readPart()
    #dumpPart()
    everythingElse()
