// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.
#include <getopt.h>
#include "simulator.h"

#if 0

// steepest descent terminates when rms_force is below this value (in picoNewtons)
#define RMS_CUTOVER (50.0)
/* additionally, sqrt(max_forceSquared) must be less than this: */
#define MAX_CUTOVER (RMS_CUTOVER * 3.0)
#define MAX_CUTOVER_SQUARED (MAX_CUTOVER * MAX_CUTOVER)

// conjugate gradient terminates when rms_force is below this value (in picoNewtons)
#define RMS_FINAL (1.0)

/* we save the rms value from the initialization iterations in originalMinimize() here: */
static float initial_rms;
/* and terminate minimization if rms ever gets above this: */
#define MAX_RMS (1000.0 * initial_rms)


static int groundExists = 1;

static void
groundAtoms(struct xyz *oldPosition, struct xyz *newPosition) 
{
    int j, k;
    int foundAGround = 0;

    if (groundExists) {
	for (j=0;j<Nexcon;j++) {	/* for each constraint */
	    if (Constraint[j].type == CODEground) { /* welded to space */
                foundAGround = 1;
		for (k=0; k<Constraint[j].natoms; k++) {
		    newPosition[Constraint[j].atoms[k]] = oldPosition[Constraint[j].atoms[k]];
		}
	    }
        }
        groundExists = foundAGround ;
    }
}
#endif // if 0 at top

static void
SIGTERMhandler(int sig) 
{
    Interrupted = 1;
}

#if 0
static void installSIGTERMhandler() 
{
    struct sigaction act;

    act.sa_handler = &SIGTERMhandler;
    sigemptyset(&act.sa_mask);
    act.sa_flags = 0;
    if (sigaction(SIGTERM, &act, NULL) < 0) {
        perror("sigaction()");
        exit(1);
    }
}
#endif

static void
usage()
{
                
    fprintf(stderr, "command line parameters:\n\
   --dump-atoms\n\
                    dump atoms\n\
   --dump-bonds\n\
                    dump bonds\n\
   --dump-constraints\n\
                    dump constraints\n\
   --dump-van-der-walls\n\
                    dump van der Waals\n\
   -n<int>, --num-atoms=<int>\n\
                    expect this many atoms (ignored)\n\
   -m, --minimize\n\
                    minimize the structure\n\
   -E, --print-energy\n\
                    print structure potential energy\n\
   -i<int>, --iters-per-frame=<num>\n\
                    number of iterations per frame\n\
   -f<int>, --num-frames=<int>\n\
                    number of frames\n\
   -s<float>, --time-step=<float>\n\
                    time step\n\
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
   -r, --repress-frame-numbers\n\
                    repress the printing of frame numbers\n\
   -o<string>, --output-file=<string>\n\
                    output file name (otherwise same as input)\n\
   -q<string>, --trace-file=<string>\n\
                    trace file name (default=\"trace\")\n\
   -D<int>, --debug-flag=<int>\n\
                    turn on a debugging flag (see simulator.h)\n\
   -B<filename>, --base-file=<filename>\n\
                    base XYZ file for position comparison (compared to following file)\n\
   filename         if no file extension, add .mmp to read, .dpb to write\n");
    exit(1);
}

#define LONG_OPT(n)  ((n) + 128)  /* This is used to mark options with no short value.  */
#define OPT_HELP     LONG_OPT (0)
#define OPT_DA       LONG_OPT (1)
#define OPT_DB       LONG_OPT (2)
#define OPT_DC       LONG_OPT (3)
#define OPT_DW       LONG_OPT (4)

static const struct option option_vec[] = {
    { "help", no_argument, NULL, 'h' },
    { "dump-atoms", no_argument, NULL, OPT_DA },
    { "dump-bonds", no_argument, NULL, OPT_DB },
    { "dump-constraints", no_argument, NULL, OPT_DC },
    { "dump-van-der-waals", no_argument, NULL, OPT_DW },
    { "num-atoms", required_argument, NULL, 'n' },
    { "minimize", no_argument, NULL, 'm' },
    { "print-energy", no_argument, NULL, 'E' },
    { "iters-per-frame", required_argument, NULL, 'i' },
    { "num-frames", required_argument, NULL, 'f' },
    { "time-step", required_argument, NULL, 's' },
    { "temperature", required_argument, NULL, 't' },
    { "dump-as-text", no_argument, NULL, 'x' },
    { "dump-intermediate-text", no_argument, NULL, 'X' },
    { "output-format-1", no_argument, NULL, 'O' },
    { "output-format-2", no_argument, NULL, 'N' },
    { "id-key", required_argument, NULL, 'I' },
    { "key-record-interval", required_argument, NULL, 'K' },
    { "repress-frame-numbers", no_argument, NULL, 'r' },
    { "debug-flag", required_argument, NULL, 'D' },
    { "output-file", required_argument, NULL, 'o' },
    { "trace-file", required_argument, NULL, 'q' },
    { "base-file", required_argument, NULL, 'B' },
    { NULL, no_argument, NULL, 0 }
};

int
main(int argc,char **argv)
{
    struct part *part;
    int opt, i, n;
    int printPotentialEnergy = 0;
    double potentialEnergy;
    int da=0, db=0, dc=0, dw=0;
	
    char buf[1024], *filename, *ofilename, *tfilename, *c;
	
    if (signal(SIGTERM, &SIGTERMhandler) == SIG_ERR) {
        perror("signal(SIGTERM)");
        exit(1);
    }

    //setupPositionsArrays();
	
    //vsetc(Cog,0.0);
    //vsetc(P,0.0);
    //vsetc(Omega,0.0);
	
    filename = (char *)0;
    ofilename = (char *)0;
    tfilename = (char *)0;

    while ((opt = getopt_long(argc, argv,
			    "hnmEi:f:s:t:xXONI:K:rd:o:q:B:",
			    option_vec, NULL)) != -1) {
	switch(opt) {
	case 'h':
	    usage();
	case OPT_DA:
	    da = 1;
	    break;
	case OPT_DB:
	    db = 1;
	    break;
	case OPT_DC:
	    dc = 1;
	    break;
	case OPT_DW:
	    dw = 1;
	    break;
	case 'n':
	    // ignored
	    break;
	case 'm':
	    ToMinimize=1;
	    break;
	case 'E':
	    printPotentialEnergy=1;
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
	case 'I':
	    IDKey = optarg;
	    break;
	case 'K':
	    KeyRecordInterval = atoi(optarg);
	    break;
	case 'r':
	    PrintFrameNums = 0;
	    break;
	case 'D':
	    n = atoi(optarg);
	    if (n < 32 && n >= 0) {
		debug_flags |= 1 << n;
	    }
	    break;
	case 'o':
	    ofilename = optarg;
	    break;
	case 'q':
	    tfilename = optarg;
	    break;
	case 'B':
	    baseFilename = optarg;
	    break;
	default:
	    fprintf(stderr, "unknown switch %s\n",argv[i]+1);
	    usage();
	    exit(1);
	}
    }
    if (optind + 1 == argc)    // (optind < argc) if not paranoid
	filename = argv[optind];

    if (DumpAsText) {
        OutputFormat = 0;
    }

    if (!filename) {
        usage();
    }

    if (baseFilename != NULL) {
        int i1;
        int i2;
        struct xyz *basePositions;
        struct xyz *initialPositions;
        
        basePositions = readXYZ(baseFilename, &i1);
        if (basePositions == NULL) {
            fprintf(stderr, "could not read base positions file from -B<filename>\n");
            exit(1);
        }
        initialPositions = readXYZ(filename, &i2);
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

    //if (ToMinimize) printf("Minimize\n");

    if (strchr(filename, '.')) {
        sprintf(buf, "%s", filename);
    } else if (baseFilename != NULL) {
        sprintf(buf, "%s.xyz", filename);
    } else {
        sprintf(buf, "%s.mmp", filename);
    }

    if (! ofilename) {
	strcpy(OutFileName,buf);
	c=strchr(OutFileName, '.');
	if (c) {
            *c='\0';
        }
    } else {
        strcpy(OutFileName,ofilename);
    }
    
    if (! strchr(OutFileName, '.')) {
	if (DumpAsText || baseFilename != NULL) {
            strcat(OutFileName,".xyz");
        } else {
            strcat(OutFileName,".dpb");
        }
    }

    if (! tfilename) {
	strcpy(TraceFileName,buf);
	c=strchr(TraceFileName, '.');
	if (c) {
            *c='\0';
        }
    } else {
        strcpy(TraceFileName,tfilename);
    }
    
    if (! strchr(TraceFileName, '.')) {
        strcat(TraceFileName,".trc");
    }
    if (!printPotentialEnergy) {
        tracef = fopen(TraceFileName, "w");
        if (!tracef) {
            perror(TraceFileName);
            exit(1);
        }
    }

    if (IterPerFrame <= 0) IterPerFrame = 1;

    initializeBondTable();
    //vdWsetup(); used to initialize orion space grid, now done in part
    //testInterpolateBondStretch(1, 6, 6);
    //testNewBondStretchTable();

    //filred(buf);
    part = readMMP(buf);
    updateVanDerWaals(part, NULL, part->positions);
    generateStretches(part);
    generateBends(part);

    if (printPotentialEnergy) {
        struct xyz *force = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
        potentialEnergy = calculatePotential(part, part->positions);
        calculateGradient(part, part->positions, force);
        printf("%e %e %e %e (Potential energy in aJ, gradient of atom 1)\n", potentialEnergy, force[1].x, force[1].y, force[1].z);
        exit(0);
    }

    //printPart(stdout, part);
    //exit(0);
    
    // this doesn't seem to make any difference... -emm
    //orion();
#if 0
    if (da) {
	fprintf(stderr, "%d atoms:\n",Nexatom);
	for (i=0; i<Nexatom; i++) pa(stderr, i);
    }
    if (db) {
	fprintf(stderr, "%d bonds:\n",Nexbon);
	for (i=0; i<Nexbon; i++) pb(stderr, i);
	fprintf(stderr, "%d torques:\n",Nextorq);
	for (i=0; i<Nextorq; i++) pq(stderr, i);
    }
    if (dw) {
	fprintf(stderr, "%d Waals:\n",vanderRoot);
	for (i=0; i<vanderRoot.fill; i++) pvdw(stderr, &vanderRoot,i);
    }
    if (dc) {
	fprintf(stderr, "%d constraints:\n",Nexcon);
	for (i=0; i<Nexcon; i++) pcon(stderr, i);
    }
#endif

    /*
    fprintf(stderr, " center of mass velocity: %f\n", vlen(vdif(CoM(Positions),CoM(OldPositions))));
    fprintf(stderr, " center of mass: %f -- %f\n", vlen(CoM(Positions)), vlen(Cog));
    fprintf(stderr, " total momentum: %f\n",P);
    */
    traceHeader(tracef, filename, OutFileName, TraceFileName, 
                part, NumFrames, IterPerFrame, Temperature);

    if  (ToMinimize) {
	NumFrames = max(NumFrames,(int)sqrt((double)part->num_atoms));
	Temperature = 0.0;
    } else {
        traceJigHeader(tracef, part);
    }

    printf("iters per frame = %d\n",IterPerFrame);
    printf("number of frames = %d\n",NumFrames);
    printf("timestep = %e\n",Dt);
    printf("temp = %f\n",Temperature);
    if (DumpAsText) printf("dump as text\n");

    printf("< %s  > %s\n", buf, OutFileName);

    // XXX put me back
    //printf("\nTotal Ke = %e\n",TotalKE);

    outf = fopen(OutFileName, DumpAsText ? "w" : "wb");
    if (outf == NULL) {
        perror(OutFileName);
        exit(1);
    }
    writeOutputHeader(outf, part);

    if  (ToMinimize) {
	minimizeStructure(part);
    }
    else {
        dynamicsMovie(part);
    }

    doneExit(0, tracef, "");
    return 1; // not reached
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
