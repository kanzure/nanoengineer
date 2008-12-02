// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/* C extension for speeding up same_vals function
 * Type "make shared" to build.
 */

static char const svnId[] = "$Id$";

#ifndef WIN32
#include <alloca.h>
#endif
#include "Python.h"
#include "Numeric/arrayobject.h"

// remove this when everyone is using a python which defines Py_ssize_t.
typedef int XXX_Py_ssize_t;

// remove this when everyone is using a python which defines these
#ifndef Py_RETURN_TRUE
#define Py_RETURN_TRUE return Py_INCREF(Py_True), Py_True
#define Py_RETURN_FALSE return Py_INCREF(Py_False), Py_False
#define Py_RETURN_NONE return Py_INCREF(Py_None), Py_None
#endif

#define XX(z)    z
//#define XX(z)

static PyTypeObject *arrayType = NULL;
static PyObject *instanceCopier = NULL;
static PyObject *arrayCopier = NULL;
static PyObject *instanceLikeClasses = NULL;

static int
_same_vals_helper(PyObject *v1, PyObject *v2)
{
    PyTypeObject *typ1, *typ2;
    if (v1 == v2) return 0;   // 0 -> items are equal
    typ1 = v1->ob_type;
    typ2 = v2->ob_type;
    if (typ1 != typ2) return 1;
    if (typ1 == &PyDict_Type) {
        PyObject *key;
        PyObject *value;
        XXX_Py_ssize_t pos = 0;
        
        if (PyDict_Size(v1) != PyDict_Size(v2)) {
            return 1;
        }
        while (PyDict_Next(v1, &pos, &key, &value)) {
            PyObject *value2 = PyDict_GetItem(v2, key);
            if (value2 == NULL) {
                return 1;
            }
            if (_same_vals_helper(value, value2)) {
                return 1;
            }
        }
        return 0;
    } else if (typ1 == &PyList_Type) {
        int i, n;

        n = PyList_Size(v1);
        if (n != PyList_Size(v2)) {
            return 1;
        }
        for (i = 0; i < n; i++)
            if (_same_vals_helper(PyList_GetItem(v1, i),
                                 PyList_GetItem(v2, i)))
                return 1;
        return 0;
    } else if (typ1 == &PyTuple_Type) {
        int i, n;

        n = PyTuple_Size(v1);
        if (n != PyTuple_Size(v2)) {
            return 1;
        }
        for (i = 0; i < n; i++)
            if (_same_vals_helper(PyTuple_GetItem(v1, i),
                                 PyTuple_GetItem(v2, i)))
                return 1;
        return 0;
    } else if (arrayType != NULL && typ1 == arrayType) {
        PyArrayObject *x = (PyArrayObject *) v1;
        PyArrayObject *y = (PyArrayObject *) v2;
        int i;
        int elementSize;
        int *indices;
        int topDimension;
        char *xdata;
        char *ydata;
        int objectCompare = 0;

        // do all quick rejects first (no loops)
        if (x->nd != y->nd) {
            // number of dimensions doesn't match
            return 1;
            // note that a (1 x X) array can never equal a single
            // dimensional array of length X.
        }
        if (x->descr->type_num != y->descr->type_num) {
            // type of elements doesn't match
            return 1;
        }
        if (x->descr->type_num == PyArray_OBJECT) {
            objectCompare = 1;
        }
        elementSize = x->descr->elsize;
        if (elementSize != y->descr->elsize) {
            // size of elements doesn't match (shouldn't happen if
            // types match!)
            return 1;
        }
        for (i = x->nd - 1; i >= 0; i--) {
            if (x->dimensions[i] != y->dimensions[i])
                // shapes don't match
                return 1;
        }
        // we do a lot of these, so handle them early
        if (x->nd == 1 && !objectCompare && x->strides[0]==elementSize && y->strides[0]==elementSize) {
            // contiguous one dimensional array of non-objects
            return memcmp(x->data, y->data, elementSize * x->dimensions[0]) ? 1 : 0;
        }
        if (x->nd == 0) {
            // scalar, just compare one element
            if (objectCompare) {
                return _same_vals_helper(*(PyObject **)x->data, *(PyObject **)y->data);
            } else {
                return memcmp(x->data, y->data, elementSize) ? 1 : 0;
            }
        }
        // If we decide we can't do alloca() for some reason, we can
        // either have a fixed maximum dimensionality, or use alloc
        // and free.
        indices = (int *)alloca(sizeof(int) * x->nd);
        for (i = x->nd - 1; i >= 0; i--) {
            indices[i] = 0;
        }
        topDimension = x->dimensions[0];
        while (indices[0] < topDimension) {
            xdata = x->data;
            ydata = y->data;
            for (i = 0; i < x->nd; i++) {
                xdata += indices[i] * x->strides[i];
                ydata += indices[i] * y->strides[i];
            }
            if (objectCompare) {
                if (_same_vals_helper(*(PyObject **)xdata, *(PyObject **)ydata)) {
                    return 1;
                }
            } else if (memcmp(xdata, ydata, elementSize) != 0) {
                // element mismatch
                return 1;
            }
            // step to next element
            for (i = x->nd - 1; i>=0; i--) {
                indices[i]++;
                if (i == 0 || indices[i] < x->dimensions[i]) {
                    break;
                }
                indices[i] = 0;
            }
        }
        // all elements match
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
    if (typ1->tp_compare != NULL) {
      int i;

      i = typ1->tp_compare(v1, v2);
      if (i != 2) {
        // tp_compare() appears to return 2 if __cmp__() is not defined on an instance.
        return i != 0;
      }
    }
#endif
    // BUG: we fail to properly handle an exception in the following call of
    // PyObject_RichCompareBool (for example, a ValueError when it's used
    // on objects of type numpy.ndarray). Until that's fixed in this C code
    // (not just for ndarray, but by making it reraise any potential exception
    // from that call), we work around that bug via a KLUGE in our Pyrex caller,
    // samevals.pyx. 
    // TODO: also extend this function to correctly compare numpy.ndarray,
    // like the Python version (in utilities/Comparison.py) now does.
    // [bruce 081202]
    if (PyObject_RichCompareBool(v1, v2, Py_EQ) == 1)
        return 0;
    return 1;
}

static PyObject *
c_same_vals(PyObject *o1, PyObject *o2)
{
    if (arrayType == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "please set arrayType first");
        return NULL;
    }
    if (_same_vals_helper(o1, o2) != 0) {
        return PyInt_FromLong(0);  // false
    }
    return PyInt_FromLong(1);  // true
}

static PyObject *
internal_copy_val(PyObject *v)
{
    PyTypeObject *typ;
    PyObject *copy;
    
    typ = v->ob_type;
    if (typ == &PyInt_Type ||
        typ == &PyLong_Type ||
        typ == &PyFloat_Type ||
        typ == &PyComplex_Type ||
        typ == &PyString_Type ||
        typ == &PyUnicode_Type) {
        Py_INCREF(v);
        return v;
    } else if (v == Py_False) {
        Py_RETURN_FALSE;
    } else if (v == Py_True) {
        Py_RETURN_TRUE;
    } else if (v == Py_None) {
        Py_RETURN_NONE;
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
        PyObject *args = PyTuple_New(1);
        Py_INCREF(v);
        PyTuple_SetItem(args, 0, v);
        copy = PyObject_CallObject(instanceCopier, args);
        Py_DECREF(args);
        return copy;
    } else if (typ == arrayType) {
        PyObject *args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, v);
        Py_INCREF(v);
        copy = PyObject_CallObject(arrayCopier, args);
        Py_DECREF(args);
        return copy;
    } else {
        if (instanceLikeClasses != NULL) {
          int listSize = PyList_Size(instanceLikeClasses);
          int i;
          for (i=0; i<listSize; i++) {
            PyObject *cls = PyList_GetItem(instanceLikeClasses, i);
            if (typ == (PyTypeObject *)cls) {
              PyObject *args = PyTuple_New(1);
              Py_INCREF(v);
              PyTuple_SetItem(args, 0, v);
              copy = PyObject_CallObject(instanceCopier, args);
              Py_DECREF(args);
              return copy;
            }
          }
        }
      
        // no good ideas here...
        fprintf(stderr, "copy_val(0x%x): not copying, type == %s\n", (int)v, typ->tp_name);
        Py_INCREF(v);
        return v;
    }
}

static PyObject *
c_copy_val(PyObject *obj)
{
    if (arrayType == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "please set arrayType first");
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
    return internal_copy_val(obj);
}

static void
c_setArrayType(PyObject *atype)
{
  Py_XDECREF(arrayType);
  arrayType = (PyTypeObject *)atype ;
  Py_INCREF(arrayType);
}

static void
c_setInstanceCopier(PyObject *copier)
{
  Py_XDECREF(instanceCopier);
  instanceCopier = copier ;
  Py_INCREF(instanceCopier);
}

static void
c_setArrayCopier(PyObject *copier)
{
  Py_XDECREF(arrayCopier);
  arrayCopier = copier ;
  Py_INCREF(arrayCopier);
}

static void
c_setInstanceLikeClasses(PyObject *classList)
{
  Py_XDECREF(instanceLikeClasses);
  instanceLikeClasses = classList ;
  Py_INCREF(instanceLikeClasses);
}
