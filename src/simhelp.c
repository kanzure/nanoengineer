/**
 * C helper file for sim.pyx
 *
 * WARNING: This file is not compiled separately -- it's #included in sim.c
 * due to the "cdef extern" declaration in sim.pyx which names it.
 * For some reason distutils doesn't realize this means there's a dependency,
 * so I added some dependencies in Makefile to fix this, which as a side effect
 * cause Makefile rather than setup.py to produce sim.c.
 * [bruce 060101]
 *
 * $Id$
 */

char __author__[] = "Will";

#include "Python.h"
#include "Numeric/arrayobject.h"
#include "simulator.h"

typedef struct sim_context {
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
    int DirectEvaluate;
    int Interrupted; /* bruce 051230 */
    char *IDKey;
    char *baseFilename;
#if 0 
 /* these ought to be here, but the globals are char OutFileName[1024];
  * which is too inefficient to copy all the time, so we need to handle them differently,
  * which is not worth it for now since there is never more than one sim object at a time.
  * [bruce 051230]
  */
    char *OutFileName; /* bruce 051230 */
    char *TraceFileName; /* bruce 051230 */
#endif
    /* double Dt; ?? note: it's already accessible in sim.pyx. */
    double Temperature;
    /* other stuff that might belong here? */
    /* finalConfiguration in minstructure.c */
    /* Part in minstructure.c */
} sim_context;

typedef struct two_contexts {
    struct sim_context *first, *second;
} two_contexts;


/* call this guy from Simulator.__init__() */
static struct sim_context *
malloc_context(void)
{
    struct sim_context *ctx = (struct sim_context *)
	malloc(sizeof(struct sim_context));
    if (ctx == NULL) {
	perror("out of memory");
	exit(1);
    }
    return ctx;
}

struct two_contexts *
malloc_two_contexts(void)
{
    static void
	save_context(struct sim_context *ctx);
    struct two_contexts *ctxs = (struct two_contexts *)
	malloc(sizeof(struct two_contexts));
    if (ctxs == NULL) {
	perror("out of memory");
	exit(1);
    }
    ctxs->first = malloc_context();
    save_context(ctxs->first);
    ctxs->second = malloc_context();
    save_context(ctxs->second);
    return ctxs;
}

static void
free_context(sim_context *ctx)
{
    if (ctx == NULL) {
	perror("free_context: ctx null??");
	exit(1);
    }
    free(ctx);
}

void
free_two_contexts(two_contexts *ctxs)
{
    if (ctxs == NULL) {
	perror("free_two_contexts: ctxs null??");
	exit(1);
    }
    free_context(ctxs->first);
    free_context(ctxs->second);
    free(ctxs);
}


static void
save_context(struct sim_context *ctx)
{
    if (ctx == NULL) {
	perror("save_context: ctx null??");
	exit(1);
    }
    ctx->debug_flags = debug_flags;
    ctx->Iteration = Iteration;
    ctx->ToMinimize = ToMinimize;
    ctx->IterPerFrame = IterPerFrame;
    ctx->NumFrames = NumFrames;
    ctx->DumpAsText = DumpAsText;
    ctx->DumpIntermediateText = DumpIntermediateText;
    ctx->PrintFrameNums = PrintFrameNums;
    ctx->OutputFormat = OutputFormat;
    ctx->KeyRecordInterval = KeyRecordInterval;
    ctx->DirectEvaluate = DirectEvaluate;
    ctx->Interrupted = Interrupted;
    ctx->IDKey = IDKey;
    ctx->baseFilename = baseFilename;
#if 0 /* bruce 051230 */
    ctx->OutFileName = OutFileName;
    ctx->TraceFileName = TraceFileName;
#endif
    ctx->Temperature = Temperature;
}

static void
restore_context(struct sim_context *ctx)
{
    if (ctx == NULL) {
	perror("restore_context: ctx null??");
	exit(1);
    }
    debug_flags = ctx->debug_flags;
    Iteration = ctx->Iteration;
    ToMinimize = ctx->ToMinimize;
    IterPerFrame = ctx->IterPerFrame;
    NumFrames = ctx->NumFrames;
    DumpAsText = ctx->DumpAsText;
    DumpIntermediateText = ctx->DumpIntermediateText;
    PrintFrameNums = ctx->PrintFrameNums;
    OutputFormat = ctx->OutputFormat;
    KeyRecordInterval = ctx->KeyRecordInterval;
    DirectEvaluate = ctx->DirectEvaluate;
    Interrupted = ctx->Interrupted;
    IDKey = ctx->IDKey;
    baseFilename = ctx->baseFilename;
#if 0 /* bruce 051230 */
    OutFileName = ctx->OutFileName;
    TraceFileName = ctx->TraceFileName;
#endif
    Temperature = ctx->Temperature;
}

void
swap_contexts(struct two_contexts *ctxs)
{
    struct sim_context *tmp;
    save_context(ctxs->first);
    restore_context(ctxs->second);
    tmp = ctxs->first;
    ctxs->first = ctxs->second;
    ctxs->second = tmp;
}



void initsimhelp(void);
void readPart(void);
void dumpPart(void);
void everythingElse(void);
char * structCompareHelp(void);

static char retval[100];
static struct part *part;
static char buf[1024];

char *filename;

static PyObject *mostRecentFrame = NULL;

// wware 060101   callback for getting frame info in pyrex
void
callback_writeFrame(struct part *part, struct xyz *pos)
{
// .xyz files are in angstroms (1e-10 m)
#define XYZ (1.0e-2)
    double *data;
    int i, n;
    if (mostRecentFrame != NULL)
	Py_DECREF(mostRecentFrame);
    n = 3 * part->num_atoms * sizeof(double);
    data = (double *) malloc(n);
    if (data == NULL) {
	perror("Out of memory");
	exit(1);
    }
    for (i = 0; i < part->num_atoms; i++) {
	data[i * 3 + 0] = pos[i].x * XYZ;
	data[i * 3 + 1] = pos[i].y * XYZ;
	data[i * 3 + 2] = pos[i].z * XYZ;
    }
    mostRecentFrame = PyString_FromStringAndSize((char*) data, n);
}

// wware 060101   make frame info available in pyrex
PyObject * getMostRecentFrame(void)
{
    return mostRecentFrame;
}

int printPotentialEnergy = 0; 
	// bruce 060101 made this global from localvar; it probably needs to be context-switched ###

void initsimhelp(void) // WARNING: this duplicates some code from simulator.c
{
    char *printPotential = NULL;
    double printPotentialInitial = 1.0;
    double printPotentialIncrement = 1.0;
    double printPotentialLimit = 200.0;
    char *ofilename;
    char *tfilename;
    char *p;

    ofilename = "";
    tfilename = "";

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
    // bruce 060101 moved the rest of this function into the start of everythingElse 
    // since it depends on parameters set by the client code after this init method runs
    
    initializeBondTable(); // try doing this here instead ####@@@@@
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

void everythingElse(void) // WARNING: this duplicates some code from simulator.c
{
    // bruce 060101 moved this section here, from the end of initsimhelp,
    // since it depends on parameters set by the client code after that init method runs
    if (!printPotentialEnergy) {
        tracef = fopen(TraceFileName, "w");
        if (!tracef) {
            perror(TraceFileName);
            exit(1);
        }
        fprintf(tracef, "# %s\n", "run from pyrex interface"); // like printing the commandLine
        // ##e should print options set before run, but it's too early to do that in this code
    }
    if (IterPerFrame <= 0) IterPerFrame = 1;
    // initializeBondTable();// try doing this elsewhere instead ####@@@@@
    // end of section moved by bruce 060101
    
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
    initialPositions = readXYZ(filename, &i2);
    if (initialPositions == NULL) {
	sprintf(retval,
		"could not read comparison positions file \"%s\"",
		filename);
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
