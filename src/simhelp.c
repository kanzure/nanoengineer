/**
 * C helper file for sim.pyx
 */

#include "Python.h"
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

void initsimhelp(void);
void readPart(void);
void dumpPart(void);
struct sim_context *makeContext(void);
PyObject * everythingElse(struct sim_context *);
PyObject * structCompareHelp(struct sim_context *ctx);

static struct part *part;  // make this non-static, move into context
static char buf[1024], *filename;

struct sim_context *
makeContext(void)
{
    struct sim_context *ctx;
	
    ctx = (struct sim_context *) malloc(sizeof(struct sim_context));
    if (ctx == NULL) {
	perror("out of memory");
	exit(1);
    }
}

void
initsimhelp(void)
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
}

void
readPart(void)
{
    part = readMMP(buf);
    updateVanDerWaals(part, NULL, part->positions);
    generateStretches(part);
    generateBends(part);
}

void
dumpPart(void)
{
    printPart(stdout, part);
}

PyObject *
everythingElse(struct sim_context *ctx)
{
    traceHeader(tracef, filename, OutFileName, TraceFileName, 
                part, NumFrames, IterPerFrame, Temperature);

    if  (ctx->ToMinimize) {
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

    if  (ctx->ToMinimize) {
	extern struct configuration *finalConfiguration;
	int i;
	struct atom *a;
	PyObject *retval = PyList_New(0);
	minimizeStructure(ctx, part);
	for (i=0; i < part->num_atoms; i++) {
	    struct xyz *positions = (struct xyz *) finalConfiguration->coordinate;
	    // convert from picometers to angstroms
	    PyObject *tpl = Py_BuildValue("(sfff)",
					  part->atoms[i]->type->symbol,
					  0.01 * positions[i].x,
					  0.01 * positions[i].y,
					  0.01 * positions[i].z);
	    PyList_Append(retval, tpl);
	}
	SetConfiguration(&finalConfiguration, NULL);
	return retval;
    }
    else {
        dynamicsMovie(ctx, part);
	Py_INCREF(Py_None);
        return Py_None;
    }
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
PyObject *
structCompareHelp(struct sim_context *ctx)
{
    int i1;
    int i2;
    struct xyz *basePositions;
    struct xyz *initialPositions;
    
    if (baseFilename == NULL || strlen(baseFilename) == 0) {
	PyErr_SetString(PyExc_IOError, "No baseFilename");
	return NULL;
    }
    basePositions = readXYZ(baseFilename, &i1);
    if (basePositions == NULL) {
	PyErr_SetString(PyExc_IOError, baseFilename);
	return NULL;
    }
    initialPositions = readXYZ(myArgs.filename, &i2);
    if (initialPositions == NULL) {
	PyErr_SetString(PyExc_IOError, myArgs.filename);
	return NULL;
    }
    if (i1 != i2) {
	PyErr_SetString(PyExc_RuntimeError,
			"structures to compare must have same number of atoms");
	return NULL;
    }
    if (doStructureCompare(ctx, i1, basePositions, initialPositions,
			   NumFrames, 1e-8, 1e-4, 1.0+1e-4)) {
	PyErr_SetString(PyExc_ValueError, "structure comparison failed");
	return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
