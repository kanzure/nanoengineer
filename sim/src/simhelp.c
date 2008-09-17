// Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
/**
 * C helper file for sim.pyx
 *
 * $Id$
 *
 * CHANGES  (reverse chronological order, use CVS log for details)
 *
 * wware 060111 - Be more careful with error checking in do_python_callback.
 *
 * wware 060109 - Made several changes to facilitate passing Python
 * exceptions upstream from deep inside C function call stacks.
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

#include <stdlib.h>
#include "Python.h"
#include "Numeric/arrayobject.h"
#include "simulator.h"
#include "version.h"

// #define WWDEBUG

static char const rcsid[] = "$Id$";
/* rcsid strings for several *.h files */
static char const rcsid2[] = MULTIPLE_RCSID_STRING;

#ifdef DISTUTILS
static char tracePrefix[] = TRACE_PREFIX TRACE_PREFIX_DISTUTILS;
#else
static char tracePrefix[] = TRACE_PREFIX TRACE_PREFIX_NON_DISTUTILS;
#endif

static char retval[100];
static struct part *part;
static struct xyz *pos;
static char buf[1024];
static int callback_exception = 0;

// Python exception stuff, wware 010609
char *py_exc_str = NULL;
static char py_exc_strbuf[1024];
PyObject *simulatorInterruptedException;

#ifdef WWDEBUG
#define WHERE_ARE_WE()   DPRINT2(D_PYREX_SIM, "%s: %d\n", __FILE__, __LINE__)
#else
#define WHERE_ARE_WE()   
#endif

// wware 060109  python exception handling
#define PYBAIL() \
    if (py_exc_str != NULL) { \
        raiseExceptionIfNoneEarlier(PyExc_RuntimeError, py_exc_str); \
	WHERE_ARE_WE(); \
        fcloseIfNonNull(&TraceFile); \
        fcloseIfNonNull(&OutputFile); \
        return NULL; \
    }

PyObject *specialExceptionIs(PyObject *specialExcep);
char * structCompareHelp(void);
void set_interrupted_flag(int value);

static void
fcloseIfNonNull(FILE **f)
{
    if (*f != NULL) {
	fclose(*f);
	*f = NULL;
    }
}

/*
 * Raise this exception with this string, UNLESS THIS PYTHON THREAD
 * ALREADY HAD AN EXCEPTION. Never replace an earlier exception,
 * because you'll be overwriting more significant diagnostic
 * information.
 *
 * In the Python source code, see Python/errors.c, the following
 * functions: PyErr_SetString, PyErr_SetObject, PyErr_Restore,
 * PyErr_Occurred
 */
static int raiseExceptionIfNoneEarlier(PyObject *exception, const char *str)
{
    if (PyErr_Occurred()) {
	// the exception already had a string, don't change it
	// let the caller know there was already a string
	WHERE_ARE_WE();
	return 1;
    }
    PyErr_SetString(exception, str);
    WHERE_ARE_WE();
    return 0;
}

PyObject *
specialExceptionIs(PyObject *specialExcep)
{
    if (!(PyType_Check(specialExcep) || PyClass_Check(specialExcep))) {
	raiseExceptionIfNoneEarlier(PyExc_SystemError,
				    "argument must be a PyClass");
	return NULL;
    }
    simulatorInterruptedException = specialExcep;
    Py_INCREF(Py_None);
    return Py_None;
}

static void
start_python_call(void)
{
    py_exc_str = NULL;
    callback_exception = 0;
}

static PyObject *
finish_python_call(PyObject *retval)
{
    if (callback_exception) {
	WHERE_ARE_WE();
	return NULL;
    } else if (py_exc_str != NULL) {
	WHERE_ARE_WE();
	// wware 060109  python exception handling
	raiseExceptionIfNoneEarlier(PyExc_RuntimeError, py_exc_str);
	return NULL;
    } else if (Interrupted) {
	raiseExceptionIfNoneEarlier(simulatorInterruptedException,
				    "simulator was interrupted");
	WHERE_ARE_WE();
	return NULL;
    }
    if (retval == Py_None) {
	WHERE_ARE_WE();
	Py_INCREF(Py_None);
    }
    WHERE_ARE_WE();
    return retval;
}

static PyObject *writeTraceCallbackFunc = NULL;
static PyObject *frameCallbackFunc = NULL;

static PyObject *
setCallbackFunc(PyObject *f, PyObject **cb)
{
    if (*cb != NULL) {
	Py_DECREF(*cb);
    }
    if (f == Py_None) {
	*cb = NULL;
	Py_INCREF(Py_None);
	return Py_None;
    } else if (f == NULL) {
	*cb = NULL;
	raiseExceptionIfNoneEarlier(PyExc_RuntimeError, "null callback");
	return NULL;
    } else if (PyCallable_Check(f)) {
	Py_INCREF(f);
	*cb = f;
	Py_INCREF(Py_None);
	return Py_None;
    } else {
	*cb = NULL;
	raiseExceptionIfNoneEarlier(PyExc_RuntimeError, "callback is not callable");
	return NULL;
    }
}

static PyObject *
setWriteTraceCallbackFunc(PyObject *f)
{
    start_python_call();
    return setCallbackFunc(f, &writeTraceCallbackFunc);
}

static PyObject *
setFrameCallbackFunc(PyObject *f)
{
    start_python_call();
    return setCallbackFunc(f, &frameCallbackFunc);
}


// wware 060102   callback for getting info from C to python
static void
do_python_callback(PyObject *callbackFunc, PyObject* args)
{
    PyObject *pValue = NULL;
    if (PyErr_Occurred()) {
	// there was already a Python error when we got here
	callback_exception = 1;
	goto fini;
    }
    if (callbackFunc == NULL || !PyCallable_Check(callbackFunc)) {
	callback_exception = 1;
	raiseExceptionIfNoneEarlier(PyExc_RuntimeError, "callback not callable");
	goto fini;
    }
    pValue = PyObject_CallObject(callbackFunc, args);
    if (PyErr_Occurred()) {
	callback_exception = 1;
	goto fini;
    }
    if (pValue == NULL) {
	/* If we didn't get PyErr_Occurred(), did we get PyErr_SetString??
	 * Looking at Python/errors.c, I don't think that should happen,
	 * but let's be paranoid.
	 */
	raiseExceptionIfNoneEarlier(PyExc_RuntimeError,
				    "callback returned NULL, PyErr_Occurred() not set");
	callback_exception = 1;
    }
    /*
     * Theoretically we could compare the value of Interrupted at this
     * point with its value before the callback was called, and then
     * raise a SimulatorInterrupted exception if it had been set
     * during the callback. We don't do that, because the
     * SimulatorInterrupted exception is raised in
     * finish_python_call(), and any pathway to get us to this point
     * will return to Python through that routine.
     */
 fini: ;
    Py_XDECREF(args);
    Py_XDECREF(pValue);
}

// wware 060102  callback for trace file
void
write_traceline(const char *format, ...)
{
    va_list args;

    if (writeTraceCallbackFunc != NULL || TraceFile != NULL) {
        va_start(args, format);
        vsnprintf(buf, 1024, format, args);
        va_end(args);
	if (writeTraceCallbackFunc != NULL) {
            do_python_callback(writeTraceCallbackFunc, Py_BuildValue("(s)", buf));
        }
	if (TraceFile != NULL) {
            fprintf(TraceFile, "%s", buf);
        }
    }
}

// wware 060101   callback for getting frame info in pyrex
void
callback_writeFrame(struct part *part1, struct xyz *pos1, int lastFrame)
{
    if (part != part1) {
	// assert part is <previous value for part>
	// we haven't seen this yet, but it would be important to know about
	// wware 060109  python exception handling
	set_py_exc_str(__FILE__, __LINE__, "the part has changed");
	return;
    }
    pos = pos1;
    if (frameCallbackFunc != NULL)
	do_python_callback(frameCallbackFunc, Py_BuildValue("(i)", lastFrame));
}

// wware 060101   make frame info available in pyrex
static PyObject *
getFrame_c(void)
{
    // .xyz files are in angstroms (1e-10 m)
#define XYZ (1.0e-2)
    PyObject *retval;
    double *data;
    int i, n;

    start_python_call();
    if (part == NULL) {
	raiseExceptionIfNoneEarlier(PyExc_MemoryError,
				    "part is null");
	return NULL;
    }
    if (part->num_atoms == 0) {
	return PyString_FromString("");
    }
    n = 3 * part->num_atoms * sizeof(double);
    data = (double *) malloc(n);
    if (data == NULL) {
	raiseExceptionIfNoneEarlier(PyExc_MemoryError,
				    "out of memory");
	return NULL;
    }
    for (i = 0; i < part->num_atoms; i++) {
	data[i * 3 + 0] = pos[i].x * XYZ;
	data[i * 3 + 1] = pos[i].y * XYZ;
	data[i * 3 + 2] = pos[i].z * XYZ;
    }
    retval = PyString_FromStringAndSize((char*) data, n);
    free(data);
    return finish_python_call(retval);
}

static PyObject *
pyrexInitBondTable(void)
{
#ifdef WWDEBUG
    debug_flags |= D_PYREX_SIM;
#endif

    start_python_call();

    initializeBondTable();
    
    return finish_python_call(Py_None);
}

/*
static PyObject *
dumpPart(void)
{
    start_python_call();
    printPart(stdout, part);
    return finish_python_call(Py_None);
}
*/

static PyObject *
everythingElse(void) // WARNING: this duplicates some code from simulator.c
{
    char *problem;
    int needVDW = 1;
    
    // wware 060109  python exception handling
    start_python_call();

    if (TraceFileName != NULL) {
	TraceFile = fopen(TraceFileName, "w");
	if (TraceFile == NULL) {
	    snprintf(buf, 1024, "can't open tracefile for writing: %s", TraceFileName);
	    raiseExceptionIfNoneEarlier(PyExc_IOError, buf);
	    return NULL;
	}
        traceFileVersion(); // call this before any other writes to trace file.
	// tell where and how the pyrex sim was built, whether with or without distutils.
	fprintf(TraceFile, "%s", tracePrefix);
        CommandLine = "run from pyrex interface";
    }

    // this has to happen after opening the trace file and setting up
    // trace callbacks, since we might emit warnings when we do this.
    initializeBondTable();

    part = readMMP(InputFileName);
    PYBAIL();
    if (part == NULL) {
	set_py_exc_str(__FILE__, __LINE__, "part is null");
	PYBAIL();
    }
    if (GromacsOutputBaseName != NULL && GromacsOutputBaseName[0] != '\0') {
        needVDW = 0;
    }
    initializePart(part, needVDW);
    PYBAIL();
    createPatterns();
    matchPartToAllPatterns(part);
    PYBAIL();

    if (TypeFeedback) {
        return finish_python_call(Py_None);
    }

    // ##e should print options set before run, but it's too early to do that in this code

    if (IterPerFrame <= 0) IterPerFrame = 1;

    constrainGlobals();
    traceHeader(part);

    if  (ToMinimize) {
	NumFrames = max(NumFrames,(int)sqrt((double)part->num_atoms));
	Temperature = 0.0;
    } else {
        traceJigHeader(part);
    }

    if (GromacsOutputBaseName != NULL && GromacsOutputBaseName[0] != '\0') {
        problem = printGromacsToplogy(GromacsOutputBaseName, part);
        if (problem != NULL) {
            raiseExceptionIfNoneEarlier(PyExc_IOError, problem);
            free(problem);
        }
    } else {
        OutputFile = fopen(OutputFileName, DumpAsText ? "w" : "wb");
        if (OutputFile == NULL) {
            snprintf(buf, 1024, "bad output filename: %s", OutputFileName);
            raiseExceptionIfNoneEarlier(PyExc_IOError, buf);
            return NULL;
        }
        writeOutputHeader(OutputFile, part);

        if  (ToMinimize) {
            minimizeStructure(part);
        }
        else {
            dynamicsMovie(part);
        }

        fcloseIfNonNull(&OutputFile);
    }
    
    if (py_exc_str != NULL) {
        ERROR(py_exc_str);
    }
    if (callback_exception) {
	WHERE_ARE_WE();  SAY("closing tracefile\n");
	fcloseIfNonNull(&TraceFile);
	return NULL;
    } else if (py_exc_str != NULL) {
	WHERE_ARE_WE();  SAY("closing tracefile\n");
	fcloseIfNonNull(&TraceFile);
	raiseExceptionIfNoneEarlier(PyExc_RuntimeError, py_exc_str);
	return NULL;
    } else if (Interrupted) {
	WHERE_ARE_WE();  SAY("closing tracefile\n");
	fcloseIfNonNull(&TraceFile);
	raiseExceptionIfNoneEarlier(simulatorInterruptedException,
				    "simulator was interrupted");
	return NULL;
    }
    return finish_python_call(Py_None);
}

static PyObject *
everythingDone(void)
{
    start_python_call();
    done("");
    WHERE_ARE_WE();  SAY("closing tracefile\n");
    fcloseIfNonNull(&TraceFile);
    if (writeTraceCallbackFunc != NULL) {
	Py_DECREF(writeTraceCallbackFunc);
    }
    if (frameCallbackFunc != NULL) {
	Py_DECREF(frameCallbackFunc);
    }
    writeTraceCallbackFunc = NULL;
    frameCallbackFunc = NULL;
    destroyPart(part);
    part = NULL;
    return finish_python_call(Py_None);
}


/**
 * If we return a non-empty string, it's an error message.
 */
char * structCompareHelp(void) {
    int i1;
    int i2;
    struct xyz *basePositions;
    struct xyz *initialPositions;

    if (BaseFileName == NULL || strlen(BaseFileName) == 0) {
	sprintf(retval, "No BaseFileName");
	return retval;
    }
    basePositions = readXYZ(BaseFileName, &i1);
    if (basePositions == NULL) {
	sprintf(retval,
		"could not read base positions file from \"%s\"",
		BaseFileName);
	return retval;
    }
    initialPositions = readXYZ(InputFileName, &i2);
    if (initialPositions == NULL) {
	sprintf(retval,
		"could not read comparison positions file \"%s\"",
		InputFileName);
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

void
set_interrupted_flag(int value)
{
    // used in sim.pyx by __setattr__, which has already set Interrupted
    // so our only job here is to set py_exc_str
    if (py_exc_str != NULL) return;
    sprintf(py_exc_strbuf, "simulator has been interrupted");
    py_exc_str = py_exc_strbuf;
}

void
set_py_exc_str(const char *filename,
               const int linenum, const char *format, ...)
{
    va_list args;
    int n;
    if (py_exc_str != NULL) return;
    n = sprintf(py_exc_strbuf, "\n%s:%d ", filename, linenum);
    va_start(args, format);
    vsnprintf(py_exc_strbuf + n, 1024 - n, format, args);
    va_end(args);
    py_exc_str = py_exc_strbuf;
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
