// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
 * C code for prototyping C with Python
 *
 * gcc -Wall -I/usr/include/python2.4 -shared -o proto.so proto.c
 */

#include "Python.h"
PyObject *ProtoError;

#if 1
#define XX(x)  x
#else
#define XX(x)
#endif

static char pointer2int_doc[] =
    "pointer2int(x) -- convert a PyObject* pointer to an int";

static PyObject *
pointer2int(PyObject * self, PyObject * args)
{
    PyObject *x;
    if (!PyArg_ParseTuple (args, "O", &x)) {
        PyErr_SetString (ProtoError, "Argument must be a Python object");
        return NULL;
    }
    return Py_BuildValue("l", x);
}


static char int2pointer_doc[] =
    "int2pointer(x) -- convert an int to a PyObject* pointer";

static PyObject *
int2pointer(PyObject * self, PyObject * args)
{
    long i;
    PyObject *x;
    if (!PyArg_ParseTuple (args, "l", &i)) {
        PyErr_SetString (ProtoError, "Argument must be an integer");
	return NULL;
    }
    x = (PyObject*) i;
    if (x != NULL)
	Py_INCREF(x);
    else
	PyErr_SetString (ProtoError, "Returning null object");
    return x;
}

static char incref_doc[] =
    "incref(x) -- increment the Python reference count for this object";

static PyObject *
incref(PyObject * self, PyObject * args)
{
    long i;
    PyObject *x;
    if (!PyArg_ParseTuple (args, "l", &i)) {
        PyErr_SetString (ProtoError, "Argument must be an integer");
	return NULL;
    }
    x = (PyObject*) i;
    Py_INCREF(x);
    Py_INCREF(Py_None);
    return Py_None;
}

static char decref_doc[] =
    "decref(x) -- decrement the Python reference count for this object";

static PyObject *
decref(PyObject * self, PyObject * args)
{
    long i;
    PyObject *x;
    if (!PyArg_ParseTuple (args, "l", &i)) {
        PyErr_SetString (ProtoError, "Argument must be an integer");
	return NULL;
    }
    x = (PyObject*) i;
    if (x == NULL) {
        PyErr_SetString (ProtoError, "Argument should be non-zero");
	return NULL;
    }
    Py_DECREF(x);
    Py_INCREF(Py_None);
    return Py_None;
}

static char xdecref_doc[] =
    "xdecref(x) -- decrement the refcount for this object if it's not a null pointer";

static PyObject *
xdecref(PyObject * self, PyObject * args)
{
    long i;
    PyObject *x;
    if (!PyArg_ParseTuple (args, "l", &i)) {
        PyErr_SetString (ProtoError, "Argument must be an integer");
	return NULL;
    }
    x = (PyObject*) i;
    Py_XDECREF(x);
    Py_INCREF(Py_None);
    return Py_None;
}

static struct PyMethodDef proto_methods[] = {
    {"pointer2int", (PyCFunction) pointer2int,
     METH_VARARGS|METH_KEYWORDS, pointer2int_doc},
    {"int2pointer", (PyCFunction) int2pointer,
     METH_VARARGS|METH_KEYWORDS, int2pointer_doc},
    {"incref", (PyCFunction) incref,
     METH_VARARGS|METH_KEYWORDS, incref_doc},
    {"decref", (PyCFunction) decref,
     METH_VARARGS|METH_KEYWORDS, decref_doc},
    {"xdecref", (PyCFunction) xdecref,
     METH_VARARGS|METH_KEYWORDS, xdecref_doc},
    {NULL, NULL}
};

static char proto_doc[] =
    "Docstring not written yet.";

DL_EXPORT(void) initproto(void)
{
    PyObject *m, *d;

    /* Create the module and add the functions */
    m = Py_InitModule3("proto", proto_methods, proto_doc);
    /* Add some symbolic constants to the module */
    d = PyModule_GetDict (m);
    ProtoError = PyString_FromString ("ProtoError");
    PyDict_SetItemString (d, "ProtoError", ProtoError);
}
