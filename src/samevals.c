/* C extension for speeding up same_vals function
 * Type "python setup2.py build_ext --inplace" to build.
 */

#include "Python.h"
#include "Numeric/arrayobject.h"

#define XX(z)    z
//#define XX(z)

static PyTypeObject *arraytype = NULL;
static PyObject *instanceCopier = NULL;
static PyObject *arrayCopier = NULL;

static int
_same_vals_helper(PyObject *v1, PyObject *v2)
{
    PyTypeObject *typ1, *typ2;
    if (v1 == v2) return 0;   // 0 -> items are equal
    typ1 = v1->ob_type;
    typ2 = v2->ob_type;
    if (typ1 != typ2) return 1;
    if (typ1 == &PyDict_Type) {
	/* Dicts have too much complicated internal structure, so
	 * compare lists of 2-tuples instead. This won't be as
	 * efficient as other data types. We can hope to do better
	 * with atom/bond-sets because we know a lot about their
	 * internal structure. Dictionaries are black magic.
	 */
	return _same_vals_helper(PyDict_Items(v1),
				PyDict_Items(v2));
    } else if (typ1 == &PyList_Type) {
	int i, n;
	n = PyList_Size(v1);
	if (n != PyList_Size(v2)) return 1;
	for (i = 0; i < n; i++)
	    if (_same_vals_helper(PyList_GetItem(v1, i),
				 PyList_GetItem(v2, i)))
		return 1;
	return 0;
    } else if (typ1 == &PyTuple_Type) {
	int i, n;
	n = PyTuple_Size(v1);
	if (n != PyTuple_Size(v2)) return 1;
	for (i = 0; i < n; i++)
	    if (_same_vals_helper(PyTuple_GetItem(v1, i),
				 PyTuple_GetItem(v2, i)))
		return 1;
	return 0;
    } else if (arraytype != NULL && typ1 == arraytype) {
	PyArrayObject *x = (PyArrayObject *) v1;
	PyArrayObject *y = (PyArrayObject *) v2;
	int i, elsize, howmany = 1;
	if (x->nd != y->nd) return 1;
	for (i = 0; i < x->nd; i++) {
	    if (x->dimensions[i] != y->dimensions[i])
		return 1;
	    howmany *= x->dimensions[i];
	}
	// if one stride is NULL and the other isn't, it's a problem
	if ((x->strides == NULL) ^ (y->strides == NULL)) return 1;
	if (x->strides != NULL) {
	    // both non-null, compare them
	    for (i = 0; i < x->nd; i++)
		if (x->strides[i] != y->strides[i]) return 1;
	}
	if (x->descr->type_num != y->descr->type_num) return 1;
	elsize = x->descr->elsize;
	if (elsize != y->descr->elsize) return 1;
	if (memcmp(x->data, y->data, elsize * howmany) != 0) return 1;
	return 0;
    }
#if 0
    XX({
	if (typ1 == &PyInstance_Type) {
	    PyInstanceObject *x = (PyInstanceObject *) v1;
	    PyObject_Print(x->in_class->cl_name, stdout, 0);
	} else {
	    PyObject_Print((PyObject*)typ1, stdout, 0);
	}
	if (typ1->tp_compare == NULL)
	    printf(" (rich comparison)");
	printf("\n");
    });
#endif
    if (typ1->tp_compare != NULL) {
	return typ1->tp_compare(v1, v2) != 0;
    }
    if (PyObject_RichCompareBool(v1, v2, Py_EQ) == 1)
	return 0;
    return 1;
}

static char same_vals_doc[] = "\
Try to emulate Bruce's version.";

static PyObject *
same_vals(PyObject *self, PyObject *args)
{
    PyObject *v1, *v2;
    if (arraytype == NULL) {
	PyErr_SetString(PyExc_RuntimeError, "please set arraytype first");
	return NULL;
    }
    if (!PyArg_ParseTuple(args, "OO", &v1, &v2))
	return NULL;
    if (_same_vals_helper(v1, v2) != 0)
	return PyInt_FromLong(0);  // false
    return PyInt_FromLong(1);  // true
}

static PyObject *
setArrayType(PyObject *self, PyObject *args)
{
    PyObject *v;
    if (!PyArg_ParseTuple(args, "O", &v))
	return NULL;
    arraytype = (PyTypeObject *) v;
    if (!PyType_Check(arraytype)) {
	PyErr_SetString(PyExc_TypeError, "argument must be a type");
	return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
internal_copy_val(PyObject *v)
{
    PyTypeObject *typ;
    typ = v->ob_type;
    if (typ == &PyInt_Type ||
	typ == &PyLong_Type ||
	typ == &PyFloat_Type ||
	typ == &PyComplex_Type ||
	typ == &PyString_Type) {
	Py_INCREF(v);
	return v;
    } else if (typ == &PyDict_Type) {
	int i, n = PyDict_Size(v);
	PyObject *newdict = PyDict_New();
	PyObject *keys = PyDict_Keys(v);
	PyObject *values = PyDict_Values(v);
	for (i = 0; i < n; i++)
	    PyDict_SetItem(newdict,
			   PyList_GetItem(keys, i),
			   internal_copy_val(PyList_GetItem(values, i)));
	return newdict;
    } else if (typ == &PyList_Type) {
	int i, n = PyList_Size(v);
	PyObject *newlist = PyList_New(n);
	for (i = 0; i < n; i++)
	    PyList_SetItem(newlist, i,
			   internal_copy_val(PyList_GetItem(v, i)));
	return newlist;
    } else if (typ == &PyTuple_Type) {
	int i, n = PyTuple_Size(v);
	PyObject *newtuple = PyTuple_New(n);
	for (i = 0; i < n; i++)
	    PyTuple_SetItem(newtuple, i,
			   internal_copy_val(PyTuple_GetItem(v, i)));
	return newtuple;
    } else if (typ == &PyInstance_Type) {
	return PyObject_CallObject(instanceCopier, v);
    } else if (typ == arraytype) {
	return PyObject_CallObject(arrayCopier, v);
    }
}

static PyObject *
copy_val(PyObject *self, PyObject *args)
{
    PyObject *v;
    if (arraytype == NULL) {
	PyErr_SetString(PyExc_RuntimeError, "please set arraytype first");
	return NULL;
    }
    if (instanceCopier == NULL) {
	PyErr_SetString(PyExc_RuntimeError, "please set instanceCopier first");
	return NULL;
    }
    if (arrayCopier == NULL) {
	PyErr_SetString(PyExc_RuntimeError, "please set arrayCopier first");
	return NULL;
    }
    if (!PyArg_ParseTuple(args, "O", &v))
	return NULL;
    return internal_copy_val(v);
}

static PyObject *
setInstanceCopier(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "O", &instanceCopier))
	return NULL;
    if (!PyCallable_Check(instanceCopier)) {
	PyErr_SetString(PyExc_TypeError, "argument must be callable");
	return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
setArrayCopier(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "O", &arrayCopier))
	return NULL;
    if (!PyCallable_Check(arrayCopier)) {
	PyErr_SetString(PyExc_TypeError, "argument must be callable");
	return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static struct PyMethodDef
samevals_methods[] = {
    {"same_vals", (PyCFunction) same_vals, 1, same_vals_doc},
    {"setArrayType", (PyCFunction) setArrayType, 1, NULL},
    {"copy_val", (PyCFunction) copy_val, 1, NULL},
    {"setInstanceCopier", (PyCFunction) setInstanceCopier, 1, NULL},
    {"setArrayCopier", (PyCFunction) setArrayCopier, 1, NULL},
    {NULL, NULL}
};

static char samevals_doc[] = "\
copy_val is badly broken at the moment.";

static char *rcsid = "$Id$";

void
initsamevals()
{
    PyObject *m;
    m = Py_InitModule3("samevals", samevals_methods, samevals_doc);
    PyModule_AddStringConstant(m, "__version__", rcsid);
    PyModule_AddStringConstant(m, "__author__", "Will");
}
