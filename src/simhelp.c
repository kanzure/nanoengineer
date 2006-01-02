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

void initsimhelp(void);
void readPart(void);
void dumpPart(void);
double * everythingElse(void);
char * structCompareHelp(void);

static char retval[100];
static struct part *part;
static char buf[1024];

char *filename;

static double *data = NULL;
static int framesize;
static PyObject *callbackFunc = NULL;

void setCallbackFunc(PyObject *f)
{
    callbackFunc = f;
}

// wware 060101   callback for getting frame info in pyrex
void
callback_writeFrame(struct part *part, struct xyz *pos)
{
// .xyz files are in angstroms (1e-10 m)
#define XYZ (1.0e-2)
    int i, n;
    PyObject *pArgs, *pValue;
    if (data != NULL) free(data);
    framesize = n = 3 * part->num_atoms * sizeof(double);
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

    if (callbackFunc != NULL && PyCallable_Check(callbackFunc)) {
        pArgs = PyTuple_New(0);
        pValue = PyObject_CallObject(callbackFunc, pArgs);
	if (pValue == NULL) {
	    PyErr_Print();
	    fprintf(stderr,"Call failed\n");
	    exit(1);
	}
	Py_DECREF(pArgs);
	Py_DECREF(pValue);
    }
}

// wware 060101   make frame info available in pyrex
PyObject * getMostRecentFrame(void)
{
    return PyString_FromStringAndSize((char*) data, framesize);
}

int printPotentialEnergy = 0; 
// bruce 060101 made this global from localvar; it probably needs to be context-switched ###


/*
 * A good goal would be to eliminate all the filename-twiddling in this
 * function, and only set up the bond tables.
 */
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

double *
everythingElse(void) // WARNING: this duplicates some code from simulator.c
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

    return data;
}


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
