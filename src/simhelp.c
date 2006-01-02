/**
 * C helper file for sim.pyx
 *
 * $Id$
 *
 * CHANGES  (reverse chronological order, use CVS log for details)
 *
 * wware 060102 - Added a callback for Python to pick up trace file info.
 *
 * WARNING: This file is not compiled separately -- it's #included in sim.c
 * due to the "cdef extern" declaration in sim.pyx which names it.
 * For some reason distutils doesn't realize this means there's a dependency,
 * so Will added one in setup.py to fix this.
 * [bruce 060101]
 *
 */

char __author__[] = "Will";

#include "Python.h"
#include "Numeric/arrayobject.h"
#include "simulator.h"

void initsimhelp(void);
void readPart(void);
void dumpPart(void);
PyObject *everythingElse(void);
char * structCompareHelp(void);

static char retval[100];
static struct part *part;
static struct xyz *pos;
static char buf[1024];

char *filename;
int error_occurred = 0;

static PyObject *writeTraceCallbackFunc = NULL;
static PyObject *frameCallbackFunc = NULL;

void setWriteTraceCallbackFunc(PyObject *f)
{
    writeTraceCallbackFunc = f;
}

void setFrameCallbackFunc(PyObject *f)
{
    frameCallbackFunc = f;
}


// wware 060102   callback for getting info from C to python
static void
do_python_callback(PyObject *callbackFunc, PyObject* args)
{
    PyObject *pValue;
    pValue = PyObject_CallObject(callbackFunc, args);
    Py_DECREF(args);
    if (pValue == NULL)
	error_occurred = 1;
    else
	Py_DECREF(pValue);
}

// wware 060102  callback for trace file
void
write_traceline(const char *format, ...)
{
    va_list args;
    char line[1000];

    if (writeTraceCallbackFunc != NULL && writeTraceCallbackFunc != Py_None &&
	PyCallable_Check(writeTraceCallbackFunc)) {
        va_start(args, format);
        sprintf(line, format, args);
        va_end(args);
	do_python_callback(writeTraceCallbackFunc, Py_BuildValue("(s)", line));
    }
}

// wware 060101   callback for getting frame info in pyrex
void
callback_writeFrame(struct part *part1, struct xyz *pos1)
{
    if (part != part1) {
	fprintf(stderr, "Part mismatch\n");
	exit(1);
    }
    pos = pos1;
    if (frameCallbackFunc != NULL && frameCallbackFunc != Py_None &&
	PyCallable_Check(frameCallbackFunc))
	do_python_callback(frameCallbackFunc, PyTuple_New(0));
}

// wware 060101   make frame info available in pyrex
PyObject *
getFrame_c(void)
{
// .xyz files are in angstroms (1e-10 m)
#define XYZ (1.0e-2)
    PyObject *retval;
    double *data;
    int i, n;
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
    retval = PyString_FromStringAndSize((char*) data, n);
    free(data);
    return retval;
}

int printPotentialEnergy = 0; 
// bruce 060101 made this global from localvar


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
    // since it depends on parameters set by the client code after this init method runs,
    // but then had to move initializeBondTable back here to fix a bug (since mmp reading
    // depends on it)
    initializeBondTable();
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

PyObject *
everythingElse(void) // WARNING: this duplicates some code from simulator.c
{
#if 0   /* do not set tracef */
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
#endif
    if (IterPerFrame <= 0) IterPerFrame = 1;
    // initializeBondTable(); // this had to be done in initsimhelp instead [bruce 060101]
    // end of section moved by bruce 060101

    if (tracef != NULL)
	traceHeader(tracef, filename, OutFileName, TraceFileName, 
		    part, NumFrames, IterPerFrame, Temperature);

    if  (ToMinimize) {
	NumFrames = max(NumFrames,(int)sqrt((double)part->num_atoms));
	Temperature = 0.0;
    } else {
        traceJigHeader(tracef, part);
    }

    // printf("iters per frame = %d\n",IterPerFrame);
    // printf("number of frames = %d\n",NumFrames);
    // printf("timestep = %e\n",Dt);
    // printf("temp = %f\n",Temperature);
    // if (DumpAsText) printf("dump as text\n");

    // printf("< %s  > %s\n", buf, OutFileName);

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
    if (outf != NULL) fclose(outf);
    if (tracef != NULL) fclose(tracef);

    if (error_occurred) return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}


/*
 * Decompose dynamicsMovie into steps callable from Python.
 *
 * Later I'd like to decompose dynamicsMovie_step into still-smaller
 * steps, with one subgoal being to move all the jig calculations
 * entirely into Python.
 */

static struct xyz *_averagePositions;
static struct xyz *_oldPositions;
static struct xyz *_newPositions;
static struct xyz *_positions;
static struct xyz *_force;
static int _framenumber;

void
dynamicsMovie_start(void)
{
    int i;

    _averagePositions = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
    _oldPositions = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
    _newPositions = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
    _positions =  (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
    _force = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);

    for (i=0; i<part->num_atoms; i++) {
	vset(_positions[i], part->positions[i]);
	vsub2(_oldPositions[i], _positions[i], part->velocities[i]);
    }
    _framenumber = 0;
    initializeDeltaBuffers(part);
}

void
dynamicsMovie_step(void)
{
    oneDynamicsFrame(part, IterPerFrame,
		     _averagePositions, &_oldPositions, &_newPositions, &_positions, _force);
    writeDynamicsMovieFrame(outf, _framenumber++, part, _averagePositions);
}


void
dynamicsMovie_finish(void)
{
    free(_averagePositions);
    free(_oldPositions);
    free(_newPositions);
    free(_positions);
    free(_force);
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
