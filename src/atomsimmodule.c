/* Atomsim module */

#include "Python.h"

static PyObject *ErrorObject;

/* Accept a string */

static PyObject *
atomsim_roj(PyObject *self, PyObject *args) {
    PyObject *a;
    long b;
    if (!PyArg_ParseTuple(args, "s#", &a, &b))
	return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}


/* List of functions defined in the module */

static PyMethodDef atomsim_methods[] = {
    {"roj",		atomsim_roj,		1},
    {NULL,		NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called initatomsim) */

DL_EXPORT(void)
     initatomsim()
{
    PyObject *m, *d;

    /* Create the module and add the functions */
    m = Py_InitModule("atomsim", atomsim_methods);

    /* Add some symbolic constants to the module */
    d = PyModule_GetDict(m);
    ErrorObject = PyErr_NewException("atomsim.error", NULL, NULL);
    PyDict_SetItemString(d, "error", ErrorObject);
}
