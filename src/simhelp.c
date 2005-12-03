/**
 * C helper file for sim.pyx
 */

#include "simulator.h"

typedef struct {
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

/* ----- globals.c stuff --------- */
int debug_flags = 0;
int Interrupted = 0; /* set to 1 when a SIGTERM is received */
struct xyz Center, Bbox[2];
int Iteration=0;
// definitions for command line args
int ToMinimize=0;
int IterPerFrame=10;
int NumFrames=100;
int DumpAsText=0;
int DumpIntermediateText=0;
int PrintFrameNums=1;
int OutputFormat=1;
int KeyRecordInterval=32;
int DirectEvaluate=1; // XXX should default to 0 eventually
char *IDKey="";
char OutFileName[1024];
char TraceFileName[1024];
char *baseFilename;
// for writing the differential position and trace files
FILE *outf, *tracef;
int Count = 0;
/** constants: timestep (.1 femtosecond), scale of distance (picometers) */
double Dt = 1e-16;              // seconds
double Dx = 1e-12;              // meters
double Dmass = 1e-27;           // units of mass vs. kg
double Temperature = 300.0;	/* Kelvins */
double Boltz = 1.38e-23;	/* k, in J/K */
double Pi = 3.1415926;
double totClipped=0.0;  // internal thermostat for numerical stability
double Gamma = 0.01; // for Langevin thermostats
//double Gamma = 0.1; // for Langevin thermostats
// double G1=(1.01-0.27*Gamma)*1.4*sqrt(Gamma);
double G1=(1.01-0.27*0.01)*1.4*0.1;
//double G1=(1.01-0.27*0.1)*1.4*0.31623;

/* -------------------------- */

int initsimhelp(void);
void readPart(void);
void dumpPart(void);
void everythingElse(void);
char * structCompareHelp(void);

static char retval[100];
static struct part *part;
static char buf[1024], *filename;
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
    } else if (baseFilename != NULL && strlen(baseFilename) > 0) {
        sprintf(buf, "%s.xyz", filename);
    } else {
        sprintf(buf, "%s.mmp", filename);
    }
    if (ofilename == NULL || strlen(ofilename) == 0) {
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
    if (tfilename == NULL || strlen(tfilename) == 0) {
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

    /* I'd like to remove the "return exitvalue" from doneExit() and
     * do it separately, pending Eric's approval.
     */

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

/**
 * If we return a non-empty string, it's an error message.
 */
char * structCompareHelp(void) {
    int i1;
    int i2;
    struct xyz *basePositions;
    struct xyz *initialPositions;
        
    if (baseFilename == NULL || strlen(baseFilename) == 0) {
	sprintf(retval, "No baseFilename");
	return retval;
    }
    basePositions = readXYZ(baseFilename, &i1);
    if (basePositions == NULL) {
	sprintf(retval,
		"could not read base positions file from \"%s\"",
		baseFilename);
	return retval;
    }
    initialPositions = readXYZ(myArgs.filename, &i2);
    if (initialPositions == NULL) {
	sprintf(retval,
		"could not read comparison positions file \"%s\"",
		myArgs.filename);
	return retval;
    }
    if (i1 != i2) {
	sprintf(retval,
		"structures to compare must have same number of atoms");
	return retval;
    }
    if (doStructureCompare(i1, basePositions, initialPositions,
			   NumFrames, 1e-8, 1e-4, 1.0+1e-4)) {
	sprintf(retval, "structure comparison failed");
	return retval;
    }
    retval[0] = '\0';
    return retval;
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
