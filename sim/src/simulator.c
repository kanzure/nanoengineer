// Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
#include <getopt.h>
#include "simulator.h"
#include "version.h"

static char const rcsid[] = "$Id$";

/* rcsid strings for several *.h files */
static char const rcsid2[] = MULTIPLE_RCSID_STRING;

static char tracePrefix[] = TRACE_PREFIX TRACE_PREFIX_NON_DISTUTILS;

static void
SIGTERMhandler(int sig) 
{
    Interrupted = 1;
}

static void
usage(void)
{
                
    fprintf(stderr, "\ncommand line parameters:\n\
   --dump-part\n\
                    write out internal representation of .mmp file, then exit\n\
   --write-gromacs-topology output_prefix\n\
                    reads .mmp file and writes it as gromacs topology and coordinates\n\
                    files.  Writes output_prefix.top and output_prefix.gro\n\
   --path-to-cpp path\n\
                    path to the c preprocessor executable (for gromacs)\n\
   --neighbor-searching=<int>\n\
                    Enable neighbor searching in gromacs\n\
   --system-parameters path\n\
                    path to the system sim-params.txt file\n\
   --print-potential-function=<bond>\n\
                    print the values of the potential and gradient for the given bond.\n\
                    <bond> should be one of:\n\
                       bond:C-1-H\n\
                       bend:C-1-C-1-H\n\
                       vdw:C-v-H\n\
                       es:Pl-e-Pl\n\
                    you may also want to change the defaults for --initial, --increment, and --limit\n\
   --initial=<r>    lowest r value in the potential function table printed above (in pm)\n\
   --increment=<dr> spacing of r values for above table (in pm)\n\
   --limit=<r>      highest r value in table above (in pm)\n\
   --direct-evaluate\n\
                    call potential and gradient functions directly instead of using\n\
                    any form of interpolation of approximation.  (VERY SLOW!)\n\
   --interpolate\n\
                    use interpolation tables for potential and gradient functions\n\
                    [[current default is --direct-evaluate, should change to --interpolate]]\n\
   --simple-movie-force-scale=<float>\n\
                    used with -D4 and -D5 to scale length of force vectors.\n\
   -n<int>, --num-atoms=<int>\n\
                    expect this many atoms (ignored)\n\
   --thermostat-gamma=<float>\n\
                    control time constant for thermostat coupling, default=0.01\n\
   -m, --minimize\n\
                    minimize the structure\n\
   --min-threshold-cutover-rms=<float>\n\
                    rms force value in pN at which to switch from steepest descent to conjugate gradients.\n\
   --min-threshold-cutover-max=<float>\n\
                    maximum force in pN must be less than this before switching to C-G.\n\
   --min-threshold-end-rms=<float>\n\
                    terminate minimization when rms force falls below this level and...\n\
   --min-threshold-end-max=<float>\n\
                    ...when max force is below this level.\n\
   --vdw-cutoff-radius=<float>\n\
                    maximum range of vdw force for GROMACS, in nm.\n\
   --vdw-cutoff-factor=<float>\n\
                    maximum range of vdw force, as multiple of rvdW.\n\
   --enable-electrostatic=<flag>\n\
                    specify 0 to disable electrostatic interactions, default is non-zero.\n\
   -E, --print-structure-energy\n\
                    print structure potential energy\n\
   --print-energies\n\
                    print potential, kinetic, and total energies for each dynamics frame\n\
   --time-reversal\n\
                    Run dynamics forward, then backwards, to check for conservation of energy\n\
   -i<int>, --iters-per-frame=<num>\n\
                    number of iterations per frame\n\
   -f<int>, --num-frames=<int>\n\
                    number of frames\n\
   -s<float>, --time-step=<float>\n\
                    time step in seconds, default 1e-16\n\
   -t<float>, --temperature=<float>\n\
                    temperature\n\
   -x, --dump-as-text\n\
                    write positions as (text) .xyz file(s)\n\
   -X, --dump-intermediate-text\n\
                    write intermediate minimize positions to .xyz (need -x)\n\
   -O, --output-format-1\n\
                    write old format .dpb files (default)\n\
   -N, --output-format-2\n\
                    write new format .dpb files\n\
   -I<string>, --id-key=<string>\n\
                    specify IDKey\n\
   -K<int>, --key-record-interval=<int>\n\
                    number of delta frames between key frames\n\
   -r               report frame numbers\n\
   -o<string>, --output-file=<string>\n\
                    output file name (otherwise same as input)\n\
   -q<string>, --trace-file=<string>\n\
                    trace file name (default=stdout)\n\
   -D<int>, --debug=<int>\n\
                    turn on a debugging flag (see debug.h)\n\
   -B<filename>, --base-file=<filename>\n\
                    base XYZ file for position comparison (compared to following file)\n\
   filename         if no file extension, add .mmp to read, .dpb to write\n");
    exit(1);
}

// wware 060101  callback for pyrex, no-op in standalone simulator
void
callback_writeFrame(struct part *part, struct xyz *pos, int last_frame)
{
}
// wware 060102  callback for trace file
void
write_traceline(const char *format, ...)
{
    va_list args;

    va_start(args, format);
    vfprintf(TraceFile, format, args);
    va_end(args);
    fflush(stdout);
}

// Python exception stuff, wware 060109
char *py_exc_str = NULL;

void
set_py_exc_str(const char *filename,
	       const int linenum, const char *format, ...)
{
    va_list args;
    fprintf(stderr, "\n%s:%d ", filename, linenum);
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fprintf(stderr, "\n");
    exit(1);
}

#define LONG_OPT(n)  ((n) + 128)  /* This is used to mark options with no short value.  */
#define OPT_HELP              LONG_OPT (0)
#define OPT_DUMP_PART         LONG_OPT (1)
#define OPT_PRINT_POTENTIAL   LONG_OPT (2)
#define OPT_INITIAL           LONG_OPT (3)
#define OPT_INCREMENT         LONG_OPT (4)
#define OPT_LIMIT             LONG_OPT (5)
#define OPT_DIRECT_EVALUATE   LONG_OPT (6)
#define OPT_INTERPOLATE       LONG_OPT (7)
#define OPT_SIMPLE_MOVIE_FORCE_SCALE LONG_OPT (8)
#define OPT_MIN_THRESH_CUT_RMS  LONG_OPT (9)
#define OPT_MIN_THRESH_CUT_MAX  LONG_OPT (10)
#define OPT_MIN_THRESH_END_RMS  LONG_OPT (11)
#define OPT_MIN_THRESH_END_MAX  LONG_OPT (12)
#define OPT_VDW_CUTOFF_FACTOR   LONG_OPT (13)
#define OPT_TIME_REVERSAL     LONG_OPT (14)
#define OPT_THERMOSTAT_GAMMA  LONG_OPT (15)
#define OPT_PRINT_ENERGIES    LONG_OPT (16)
#define OPT_ENABLE_ELECTROSTATIC LONG_OPT (17)
#define OPT_WRITE_GROMACS_TOPOLOGY LONG_OPT (18)
#define OPT_PATH_TO_CPP LONG_OPT (19)
#define OPT_SYSTEM_PARAMETERS LONG_OPT (20)
#define OPT_VDW_CUTOFF_RADIUS LONG_OPT (21)
#define OPT_OUTPUT_FORMAT_3 LONG_OPT (22)
#define OPT_NEIGHBOR_SEARCHING LONG_OPT (23)

static const struct option option_vec[] = {
    { "help", no_argument, NULL, 'h' },
    { "dump-part", no_argument, NULL, OPT_DUMP_PART },
    { "write-gromacs-topology", required_argument, NULL, OPT_WRITE_GROMACS_TOPOLOGY },
    { "path-to-cpp", required_argument, NULL, OPT_PATH_TO_CPP },
    { "system-parameters", required_argument, NULL, OPT_SYSTEM_PARAMETERS },
    { "print-potential-function", required_argument, NULL, OPT_PRINT_POTENTIAL},
    { "initial", required_argument, NULL, OPT_INITIAL},
    { "increment", required_argument, NULL, OPT_INCREMENT},
    { "limit", required_argument, NULL, OPT_LIMIT},
    { "direct-evaluate", no_argument, NULL, OPT_DIRECT_EVALUATE},
    { "interpolate", no_argument, NULL, OPT_INTERPOLATE},
    { "simple-movie-force-scale", required_argument, NULL, OPT_SIMPLE_MOVIE_FORCE_SCALE},
    { "min-threshold-cutover-rms", required_argument, NULL, OPT_MIN_THRESH_CUT_RMS},
    { "min-threshold-cutover-max", required_argument, NULL, OPT_MIN_THRESH_CUT_MAX},
    { "min-threshold-end-rms", required_argument, NULL, OPT_MIN_THRESH_END_RMS},
    { "min-threshold-end-max", required_argument, NULL, OPT_MIN_THRESH_END_MAX},
    { "vdw-cutoff-radius", required_argument, NULL, OPT_VDW_CUTOFF_RADIUS},
    { "vdw-cutoff-factor", required_argument, NULL, OPT_VDW_CUTOFF_FACTOR},
    { "enable-electrostatic", required_argument, NULL, OPT_ENABLE_ELECTROSTATIC},
    { "time-reversal", no_argument, NULL, OPT_TIME_REVERSAL},
    { "thermostat-gamma", required_argument, NULL, OPT_THERMOSTAT_GAMMA},
    { "print-energies", no_argument, NULL, OPT_PRINT_ENERGIES},
    { "num-atoms", required_argument, NULL, 'n' },
    { "minimize", no_argument, NULL, 'm' },
    { "print-structure-energy", no_argument, NULL, 'E' },
    { "iters-per-frame", required_argument, NULL, 'i' },
    { "num-frames", required_argument, NULL, 'f' },
    { "time-step", required_argument, NULL, 's' },
    { "temperature", required_argument, NULL, 't' },
    { "dump-as-text", no_argument, NULL, 'x' },
    { "dump-intermediate-text", no_argument, NULL, 'X' },
    { "output-format-1", no_argument, NULL, 'O' },
    { "output-format-2", no_argument, NULL, 'N' },
    { "output-format-3", no_argument, NULL, OPT_OUTPUT_FORMAT_3},
    { "id-key", required_argument, NULL, 'I' },
    { "key-record-interval", required_argument, NULL, 'K' },
    { "debug", required_argument, NULL, 'D' },
    { "output-file", required_argument, NULL, 'o' },
    { "trace-file", required_argument, NULL, 'q' },
    { "base-file", required_argument, NULL, 'B' },
    { "neighbor-searching", required_argument, NULL, OPT_NEIGHBOR_SEARCHING },
    { NULL, no_argument, NULL, 0 }
};

static char *
assembleCommandLine(int argc, char **argv)
{
    int len = 0;
    int len1;
    char *arg;
    char *s = NULL;

    while (argc-- > 0) {
        arg = *argv++;
        len1 = len + strlen(arg);
        s = (char *)accumulator(s, len1, 0);
        while (len < len1) {
            s[len++] = *arg++;
        }
        s[len++] = ' ';
    }
    s[len] = '\0';
    return s;
}

int
main(int argc, char **argv)
{
    struct part *part;
    int opt, n;
    int dump_part = 0;
    int printStructurePotentialEnergy = 0;
    int needVDW = 1;
    char *printPotential = NULL;
    double printPotentialInitial = -1; // pm
    double printPotentialIncrement = -1; // pm
    double printPotentialLimit = -1; // pm
    char *fileNameTemplate = NULL;
    char *outputFilename = NULL;
	
    reinit_globals();

    if (signal(SIGTERM, &SIGTERMhandler) == SIG_ERR) {
        perror("signal(SIGTERM)");
        exit(1);
    }
    
    CommandLine = assembleCommandLine(argc, argv);
    while ((opt = getopt_long(argc, argv,
			    "hnmEi:f:s:t:xXONI:K:rD:o:q:B:",
			    option_vec, NULL)) != -1) {
	switch(opt) {
	case 'h':
	    usage();
	case OPT_DUMP_PART:
	    dump_part = 1;
	    break;
	case OPT_WRITE_GROMACS_TOPOLOGY:
	    GromacsOutputBaseName = optarg;
	    break;
	case OPT_PATH_TO_CPP:
	    PathToCpp = optarg;
	    break;
	case OPT_SYSTEM_PARAMETERS:
	    SystemParametersFileName = optarg;
	    break;
        case OPT_PRINT_POTENTIAL:
            printPotential = optarg;
	    break;
        case OPT_INITIAL:
	    printPotentialInitial = atof(optarg);
	    break;
        case OPT_INCREMENT:
	    printPotentialIncrement = atof(optarg);
	    break;
        case OPT_LIMIT:
	    printPotentialLimit = atof(optarg);
	    break;
        case OPT_DIRECT_EVALUATE:
            DirectEvaluate = 1;
	    break;
        case OPT_INTERPOLATE:
            DirectEvaluate = 0;
	    break;
        case OPT_SIMPLE_MOVIE_FORCE_SCALE:
            SimpleMovieForceScale = atof(optarg);
            break;
        case OPT_MIN_THRESH_CUT_RMS:
            MinimizeThresholdCutoverRMS = atof(optarg);
            break;
        case OPT_MIN_THRESH_CUT_MAX:
            MinimizeThresholdCutoverMax = atof(optarg);
            break;
        case OPT_MIN_THRESH_END_RMS:
            MinimizeThresholdEndRMS = atof(optarg);
            break;
        case OPT_MIN_THRESH_END_MAX:
            MinimizeThresholdEndMax = atof(optarg);
            break;
        case OPT_VDW_CUTOFF_RADIUS:
            VanDerWaalsCutoffRadius = atof(optarg);
            break;
        case OPT_VDW_CUTOFF_FACTOR:
            VanDerWaalsCutoffFactor = atof(optarg);
            break;
        case OPT_ENABLE_ELECTROSTATIC:
            EnableElectrostatic = atoi(optarg);
            break;
        case OPT_TIME_REVERSAL:
            TimeReversal = 1;
            break;
        case OPT_THERMOSTAT_GAMMA:
            ThermostatGamma = atof(optarg);
            break;
        case OPT_PRINT_ENERGIES:
            PrintPotentialEnergy = 1;
            break;
        case OPT_NEIGHBOR_SEARCHING:
            NeighborSearching = atoi(optarg);
            break;
	case 'n':
	    // ignored
	    break;
	case 'm':
	    ToMinimize=1;
	    break;
	case 'E':
	    printStructurePotentialEnergy=1;
	    break;
	case 'i':
	    IterPerFrame = atoi(optarg);
	    break;
	case 'f':
	    NumFrames = atoi(optarg);
	    break;
	case 's':
	    Dt = atof(optarg);
	    break;
	case 't':
	    Temperature = atof(optarg);
	    break;
	case 'x':
	    DumpAsText = 1;
	    break;
	case 'X':
	    DumpIntermediateText = 1;
	    break;
	case 'O':
	    OutputFormat = 1;
	    break;
	case 'N':
	    OutputFormat = 2;
	    break;
	case OPT_OUTPUT_FORMAT_3:
	    OutputFormat = 3;
	    break;
	case 'I':
	    IDKey = optarg;
	    break;
	case 'K':
	    KeyRecordInterval = atoi(optarg);
	    break;
	case 'r':
	    PrintFrameNums = 1;
	    break;
	case 'D':
	    n = atoi(optarg);
	    if (n < 32 && n >= 0) {
		debug_flags |= 1 << n;
	    }
	    break;
	case 'o':
	    outputFilename = optarg;
	    break;
	case 'q':
	    TraceFileName = optarg;
	    break;
	case 'B':
	    BaseFileName = optarg;
	    break;
        case ':':
        case '?':
	default:
	    usage();
	    exit(1);
	}
    }
    if (optind + 1 == argc) {   // (optind < argc) if not paranoid
	fileNameTemplate = argv[optind];
    }

    if (DEBUG(D_PRINT_BEND_STRETCH)) { // -D8
        initializeBondTable();
        printBendStretch();
        exit(0);
    }

    if (DumpAsText) {
        OutputFormat = 0;
    }

    if (!fileNameTemplate) {
        usage();
    }
    InputFileName = replaceExtension(fileNameTemplate, "mmp");

    if (BaseFileName != NULL) {
        int i1;
        int i2;
        struct xyz *basePositions;
        struct xyz *initialPositions;
        
        basePositions = readXYZ(BaseFileName, &i1);
        if (basePositions == NULL) {
            fprintf(stderr, "could not read base positions file from -B<filename>\n");
            exit(1);
        }
        initialPositions = readXYZ(InputFileName, &i2);
        if (initialPositions == NULL) {
            fprintf(stderr, "could not read comparison positions file\n");
            exit(1);
        }
        if (i1 != i2) {
            fprintf(stderr, "structures to compare must have same number of atoms\n");
            exit(1);
        }
        exit(doStructureCompare(i1, basePositions, initialPositions,
                                NumFrames, 1e-8, 1e-4, 1.0+1e-4));
    }

    if (outputFilename) {
        OutputFileName = copy_string(outputFilename);
    } else {
        char *extension;
        
        switch (OutputFormat) {
        case 0:
            extension = "xyz";
            break;
        case 1:
        case 2:
        default:
            extension = "dpb";
            break;
        case 3:
            extension = "gro";
            break;
        }
        
        OutputFileName = replaceExtension(fileNameTemplate, extension);
    }

    if (TraceFileName) {
        TraceFile = fopen(TraceFileName, "w");
        if (TraceFile == NULL) {
            perror(TraceFileName);
            exit(1);
        }
    } else {
        TraceFile = fdopen(1, "w");
        if (TraceFile == NULL) {
            perror("fdopen stdout as TraceFile");
            exit(1);
        }
    }
    traceFileVersion(); // call this before any other writes to trace file.
    // tell where and how the simulator was built. We never build the
    // standalone simulator with distutils.
    fprintf(TraceFile, "%s", tracePrefix);

    initializeBondTable();

    if (IterPerFrame <= 0) IterPerFrame = 1;

    if (printPotential) {
        printPotentialAndGradientFunctions(printPotential,
                                           printPotentialInitial,
                                           printPotentialIncrement,
                                           printPotentialLimit);
        exit(0);
    }
    
    part = readMMP(InputFileName);
    if (EXCEPTION) {
        exit(1);
    }
    if (GromacsOutputBaseName != NULL) {
        needVDW = 0;
    }
    initializePart(part, needVDW);
    createPatterns();
    matchPartToAllPatterns(part);
    
    if (printStructurePotentialEnergy) {
        struct xyz *force = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
        double potentialEnergy = calculatePotential(part, part->positions);
        calculateGradient(part, part->positions, force);
        printf("%e %e %e %e (Potential energy in aJ, gradient of atom 1)\n", potentialEnergy, force[1].x, force[1].y, force[1].z);
        exit(0);
    }
    
    if (dump_part) {
        //
        // this segment is convenient to run valgrind on to test the
        // part and bond table destructors.  By the time we reach the
        // exit() there should be no malloc'd blocks remaining.
        //
        // valgrind -v --leak-check=full --leak-resolution=high --show-reachable=yes simulator --dump-part part.mmp
        //
        printPart(stdout, part);
        destroyPart(part);
        part = NULL;
        destroyBondTable();
        fclose(TraceFile);
        destroyAccumulator(CommandLine);
        free(InputFileName);
        free(OutputFileName);
        exit(0);
    }

    if (GromacsOutputBaseName != NULL) {
        printGromacsToplogy(GromacsOutputBaseName, part);
        destroyPart(part);
        part = NULL;
        destroyBondTable();
        fclose(TraceFile);
        destroyAccumulator(CommandLine);
        free(InputFileName);
        free(OutputFileName);
        done("");
        exit(0);
    }

    constrainGlobals();
    traceHeader(part);

    if  (ToMinimize) {
	NumFrames = max(NumFrames,(int)sqrt((double)part->num_atoms));
	Temperature = 0.0;
    } else {
        traceJigHeader(part);
    }

    OutputFile = fopen(OutputFileName, DumpAsText ? "w" : "wb");
    if (OutputFile == NULL) {
        perror(OutputFileName);
        exit(1);
    }
    writeOutputHeader(OutputFile, part);

    if  (ToMinimize) {
	minimizeStructure(part);
	exit(0);
    }
    else {
        dynamicsMovie(part);
    }

    done("");
    return 0;
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
