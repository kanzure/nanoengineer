/*
 * C code for prototyping C with Python
 *
 * gcc -Wall -I/usr/include/python2.4 -shared -o proto.so proto.c
 */

#include "Python.h"
PyObject *ProtoError;

static char getpointer_doc[] =
    "getpointer (x) -- convert a PyObject* pointer to an int";

static PyObject *
getpointer(PyObject * self, PyObject * args)
{
    PyObject *x;
    if (!PyArg_ParseTuple (args, "O", &x))
	return NULL;
    return Py_BuildValue("i", x);
}


static struct PyMethodDef proto_methods[] = {
    {"getpointer", (PyCFunction) getpointer,
     METH_VARARGS|METH_KEYWORDS, getpointer_doc},
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
