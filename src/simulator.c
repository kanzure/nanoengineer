// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.
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
   -d<char>      -- dump, <char>= a: atoms; b: bonds; c: constraints\n\
   -n<int>       -- expect this many atoms (ignored)\n\
   -m            -- minimize the structure\n\
   -i<int>       -- number of iterations per frame\n\
   -f<int>       -- number of frames\n\
   -s<float>     -- timestep\n\
   -t<float>     -- temperature\n\
   -x            -- write positions as (text) .xyz file(s)\n\
   -X            -- write intermediate minimize positions to .xyz (need -x)\n\
   -O            -- write old format .dpb files (default)\n\
   -N            -- write new format .dpb files\n\
   -I<string>    -- specify IDKey\n\
   -K<int>       -- number of delta frames between key frames\n\
   -r            -- repress frame numbers\n\
   -o<string>    -- output file name (otherwise same as input)\n\
   -q<string>    -- trace file name (otherwise trace)\n\
   -D<int>       -- turn on a debugging flag (see simulator.h)\n\
   -B<filename>  -- base XYZ file for position comparison (compared to following file)\n\
   filename      -- if no ., add .mmp to read, .dpb to write\n");
    exit(1);
}

int
main(int argc,char **argv)
{
    struct part *part;
    int i, n;
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

    for (i=1; i<argc; i++) {

	if (argv[i][0] == '-') {
	    switch (argv[i][1]) {
	    case 'h':
                usage();
	    case 'd':
		if (argv[i][2]=='a') da = 1;
		if (argv[i][2]=='b') db = 1;
		if (argv[i][2]=='c') dc = 1;
		if (argv[i][2]=='w') dw = 1;
	    case 'n':
                // ignored
		break;
	    case 'm':
		ToMinimize=1;
		break;
	    case 'i':
		IterPerFrame = atoi(argv[i]+2);
		break;
	    case 'f':
		NumFrames = atoi(argv[i]+2);
		break;
	    case 's':
	        Dt = atof(argv[i]+2);
		break;
	    case 't':
		Temperature = atof(argv[i]+2);
		break;
	    case 'x':
		DumpAsText=1;
		break;
	    case 'X':
		DumpIntermediateText=1;
		break;
	    case 'O':
		OutputFormat=1;
		break;
	    case 'N':
		OutputFormat=2;
		break;
	    case 'I':
                IDKey=argv[i]+2;
		break;
	    case 'K':
                KeyRecordInterval=atoi(argv[i]+2);
		break;
	    case 'r':
		PrintFrameNums=0;
		break;
	    case 'D':
		n = atoi(argv[i]+2);
                if (n < 32 && n >= 0) {
                    debug_flags |= 1 << n;
                }
		break;
            case 'o':
		ofilename=argv[i]+2;
		break;
	    case 'q':
		tfilename=argv[i]+2;
		break;
            case 'B':
                baseFilename=argv[i]+2;
                break;
	    default:
		fprintf(stderr, "unknown switch %s\n",argv[i]+1);
	    }
	}	
	else {
	    filename = argv[i];
	}
    }

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
    tracef = fopen(TraceFileName, "w");
    if (!tracef) {
        perror(TraceFileName);
        exit(1);
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
