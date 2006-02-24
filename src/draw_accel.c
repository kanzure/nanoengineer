/*
 * C code to accelerate various drawing operations
 *
 * gcc -Wall -I/usr/include/python2.4 -shared -o draw_accel.so draw_accel.c
 */

#include "Python.h"
PyObject *DrawAccelError;

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
        PyErr_SetString (DrawAccelError, "Argument must be a Python object");
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
        PyErr_SetString (DrawAccelError, "Argument must be an integer");
	return NULL;
    }
    x = (PyObject*) i;
    if (x != NULL)
	Py_INCREF(x);
    else
	PyErr_SetString (DrawAccelError, "Returning null object");
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
        PyErr_SetString (DrawAccelError, "Argument must be an integer");
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
        PyErr_SetString (DrawAccelError, "Argument must be an integer");
	return NULL;
    }
    x = (PyObject*) i;
    if (x == NULL) {
        PyErr_SetString (DrawAccelError, "Argument should be non-zero");
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
        PyErr_SetString (DrawAccelError, "Argument must be an integer");
	return NULL;
    }
    x = (PyObject*) i;
    Py_XDECREF(x);
    Py_INCREF(Py_None);
    return Py_None;
}

static struct PyMethodDef draw_accel_methods[] = {
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

static char draw_accel_doc[] =
    "Docstring not written yet.";

DL_EXPORT(void) initdraw_accel(void)
{
    PyObject *m, *d;

    /* Create the module and add the functions */
    m = Py_InitModule3("draw_accel", draw_accel_methods, draw_accel_doc);
    /* Add some symbolic constants to the module */
    d = PyModule_GetDict (m);
    DrawAccelError = PyString_FromString ("DrawAccelError");
    PyDict_SetItemString (d, "DrawAccelError", DrawAccelError);
}
