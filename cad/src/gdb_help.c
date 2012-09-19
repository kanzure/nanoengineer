// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
/*
 * gcc -I/usr/include/python2.4 -g -Wall -c -o gdb_help.o gdb_help.c
 * gcc -shared -o gdb_help.so gdb_help.o
 */

static char const svnId[] = "$Id$";

#include <stdio.h>
#include <unistd.h>
#include "Python.h"


#define DEBUG 1

#if DEBUG
#define MARK()  \
  fprintf(stderr, __FILE__ ":%d\n", __LINE__); fflush(stderr)
#define DBGPRINTF(fmt)  \
  fprintf(stderr, __FILE__ ":%d " fmt, __LINE__); fflush(stderr)
#define DBGPRINTF1(fmt,a)  \
  fprintf(stderr, __FILE__ ":%d " fmt, __LINE__, a); fflush(stderr)
#define DBGPRINTF2(fmt,a,b)  \
  fprintf(stderr, __FILE__ ":%d " fmt, __LINE__, a, b); fflush(stderr)
#define DBGPRINTF3(fmt,a,b,c)  \
  fprintf(stderr, __FILE__ ":%d " fmt, __LINE__, a, b, c); fflush(stderr)
#else
#define MARK()
#define DBGPRINTF(fmt)
#define DBGPRINTF1(fmt,a)
#define DBGPRINTF2(fmt,a,b)
#define DBGPRINTF3(fmt,a,b,c)
#endif

static PyObject *
stop(PyObject *self, PyObject *args)
{
    int x = 0, y;
    if (!PyArg_ParseTuple(args, ""))
	return NULL;
    y = 1 / x;  // force a divide-by-zero error to make GDB stop
    Py_INCREF(Py_None);
    return Py_None;
}


static struct PyMethodDef gdb_help_methods[] = {
    {"stop",   stop, 1},
    {NULL,       NULL}
};

static char gdb_help_doc [] =
"This module has some handy functions for working with Python in GDB.\n\
\n\
stop()  ==> force a divide-by-zero to make GDB stop";

void
initgdb_help()
{
    /* Create the module and add the functions */
    Py_InitModule3("gdb_help", gdb_help_methods, gdb_help_doc);
}
