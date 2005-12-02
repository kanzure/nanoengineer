/**
 * C helper file for sim.pyx
 */

#include "simulator.h"

typedef struct {
    int debug_flags;
    int Iteration;
    int ToMinimize;
    int IterPerFrame;
    int NumFrames;
    int DumpAsText;
    int DumpIntermediateText;
    int PrintFrameNums;
    int OutputFormat;
    int KeyRecordInterval;
    int DirectEvaluate; // XXX should default to 0 eventually
    char *IDKey;
    char *baseFilename;
    double Dt;              // seconds
    double Dx;              // meters
    double Dmass;           // units of mass vs. kg
    double Temperature;     /* Kelvins */
    char *printPotential;
    double printPotentialInitial; // pm
    double printPotentialIncrement; // pm
    double printPotentialLimit; // pm
    int printPotentialEnergy;
    char *ofilename;
    char *tfilename;
    char *filename;
} SimArgs;

SimArgs myArgs;

int initsimhelp(void);
void readPart(void);
void dumpPart(void);
void everythingElse(void);
char * structCompareHelp(void);

static char retval[100];
static struct part *part;
static char buf[1024], *filename, *ofilename, *tfilename;
static int initializedAlready = 0;

int initsimhelp(void)
{
    char *printPotential = NULL;
    double printPotentialInitial = 1.0;
    double printPotentialIncrement = 1.0;
    double printPotentialLimit = 200.0;
    int printPotentialEnergy = 0;
    char *ofilename;
    char *tfilename;
    char *filename;
    char *p;
    if (initializedAlready)
	return 1;
    initializedAlready = 1;

    debug_flags = myArgs.debug_flags;
    Iteration = myArgs.Iteration;
    ToMinimize = myArgs.ToMinimize;
    IterPerFrame = myArgs.IterPerFrame;
    NumFrames = myArgs.NumFrames;
    DumpAsText = myArgs.DumpAsText;
    DumpIntermediateText = myArgs.DumpIntermediateText;
    PrintFrameNums = myArgs.PrintFrameNums;
    OutputFormat = myArgs.OutputFormat;
    KeyRecordInterval = myArgs.KeyRecordInterval;
    DirectEvaluate = myArgs.DirectEvaluate;
    IDKey = myArgs.IDKey;
    baseFilename = myArgs.baseFilename;
    Dt = myArgs.Dt;
    Dx = myArgs.Dx;
    Dmass = myArgs.Dmass;
    Temperature = myArgs.Temperature;
    printPotential = myArgs.printPotential;
    printPotentialInitial = myArgs.printPotentialInitial;
    printPotentialIncrement = myArgs.printPotentialIncrement;
    printPotentialLimit = myArgs.printPotentialLimit;
    printPotentialEnergy = myArgs.printPotentialEnergy;
    printPotential = myArgs.printPotential;
    ofilename = myArgs.ofilename;
    tfilename = myArgs.tfilename;
    filename = myArgs.filename;

    if (DumpAsText) {
        OutputFormat = 0;
    }
    if (strchr(filename, '.')) {
        sprintf(buf, "%s", filename);
    } else if (strlen(baseFilename) > 0) {
        sprintf(buf, "%s.xyz", filename);
    } else {
        sprintf(buf, "%s.mmp", filename);
    }
    if (strlen(ofilename) == 0) {
	strcpy(OutFileName,buf);
	p = strchr(OutFileName, '.');
	if (p) {
            *p = '\0';
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
    if (strlen(tfilename) == 0) {
	strcpy(TraceFileName,buf);
	p = strchr(TraceFileName, '.');
	if (p) {
            *p = '\0';
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
    return 0;
}

void readPart(void)
{
    part = readMMP(buf);
    updateVanDerWaals(part, NULL, part->positions);
    generateStretches(part);
    generateBends(part);
}

void dumpPart(void)
{
    printPart(stdout, part);
}

void everythingElse(void)
{
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

    //doneExit(0, tracef, "");
}



#if 0
void printPotential(void)
{
    printPotentialAndGradientFunctions(printPotential,
				       printPotentialInitial,
				       printPotentialIncrement,
				       printPotentialLimit);
}
#endif

char * structCompareHelp(void) {
    if (strlen(baseFilename) > 0) {
        int i1;
        int i2;
        struct xyz *basePositions;
        struct xyz *initialPositions;
        
        basePositions = readXYZ(baseFilename, &i1);
        if (basePositions == NULL) {
	    sprintf(retval, "could not read base positions file from \"%s\"", baseFilename);
            return retval;
        }
        initialPositions = readXYZ(myArgs.filename, &i2);
        if (initialPositions == NULL) {
	    sprintf(retval, "could not read comparison positions file \"%s\"", myArgs.filename);
            return retval;
        }
        if (i1 != i2) {
	    sprintf(retval, "structures to compare must have same number of atoms");
            return retval;
        }
        if (doStructureCompare(i1, basePositions, initialPositions,
			       NumFrames, 1e-8, 1e-4, 1.0+1e-4)) {
	    sprintf(retval, "structure comparison failed");
	    return retval;
	}
    }
    retval[0] = '\0';
    return retval;
}

#if 0
int
main(int argc,char **argv)
{
    struct part *part;
    int opt, n;
    int printPotentialEnergy = 0;
    double potentialEnergy;
    int dump_part = 0;
    char *printPotential = NULL;
    double printPotentialInitial = 1; // pm
    double printPotentialIncrement = 1; // pm
    double printPotentialLimit = 200; // pm
    char buf[1024], *filename, *ofilename, *tfilename, *c;
	
    if (signal(SIGTERM, &SIGTERMhandler) == SIG_ERR) {
        perror("signal(SIGTERM)");
        exit(1);
    }

    //setupPositionsArrays();
	
    //vsetc(Cog,0.0);
    //vsetc(P,0.0);
    //vsetc(Omega,0.0);

    //debug_flags = D_BEND_ONLY;
    
    filename = (char *)0;
    ofilename = (char *)0;
    tfilename = (char *)0;

    while ((opt = getopt_long(argc, argv,
			    "hnmEi:f:s:t:xXONI:K:rD:o:q:B:",
			    option_vec, NULL)) != -1) {
	switch(opt) {
	case 'h':
	    usage();
	case OPT_DUMP_PART:
	    dump_part = 1;
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
            DirectEvaluate = !DirectEvaluate;
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
        case ':':
        case '?':
	default:
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

    if (printPotential) {
        printPotentialAndGradientFunctions(printPotential,
                                           printPotentialInitial,
                                           printPotentialIncrement,
                                           printPotentialLimit);
        exit(0);
    }
    
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

    if (dump_part) {
        printPart(stdout, part);
        exit(0);
    }

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
#endif

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
