/* C extension for speeding up same_vals function
 * Type "python setup2.py build_ext --inplace" to build.
 */

#include "Python.h"
#include "Numeric/arrayobject.h"

//#define XX(z)    z
#define XX(z)

static PyTypeObject *arraytype = NULL;

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
	XX(printf("dict\n"));
	return _same_vals_helper(PyDict_Items(v1),
				PyDict_Items(v2));
    } else if (typ1 == &PyList_Type) {
	int i, n;
	XX(printf("list\n"));
	n = PyList_Size(v1);
	if (n != PyList_Size(v2)) return 1;
	for (i = 0; i < n; i++)
	    if (_same_vals_helper(PyList_GetItem(v1, i),
				 PyList_GetItem(v2, i)))
		return 1;
	return 0;
    } else if (typ1 == &PyTuple_Type) {
	int i, n;
	XX(printf("tuple\n"));
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
	XX(printf("array\n"));
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
    Py_INCREF(Py_None);
    return Py_None;
}

#if 0
/****
    def _find_attr_decls(self, class1):
        hmm = dir(class1)
        for name in hmm:
            # The _s_attr_ things are always class variables
            # they are never instance variables
            if name.startswith('_s_attr_'):
                attr_its_about = name[len('_s_attr_'):]
                declval = getattr(class1, name)
                self.policies[attr_its_about] = declval
                self.warn = False
                if declval in STATE_ATTR_DECLS:
                    self.dict_of_all_state_attrs[attr_its_about] = None
                    try:
                        dflt = getattr(class1, attr_its_about)
                    except AttributeError:

                        self.attrs_with_no_dflt.append(attr_its_about)
                    else:
                        self.attr_dflt_pairs.append( (attr_its_about, dflt) )
                        self.defaultvals[attr_its_about] = dflt
                    pass
                pass
            # _s_deepcopy is always a class method
            elif name == '_s_deepcopy':
                self.warn = False
            # _s_categorize is also always a class variable
            elif name.startswith('_s_categorize_'):
                attr_its_about = name[len('_s_categorize_'):]
                declval = getattr(class1, name)
                assert type(declval) == type('category')
                self.categories[attr_its_about] = declval
***/

static PyObject *
Find_attr_decls(PyObject *ignore, PyObject *args)
{
    PyInstanceObject *self;
    PyClassObject *class1;
    PyObject *dict, *keys, *declval;
    int i, n;
    if (!PyArg_ParseTuple(args, "OO", &self, &class1))
	return NULL;
    /* step thru the class variables for class1 */
    dict = class1->cl_dict;
    n = PyDict_Size(dict);
    keys = PyDict_Keys(dict);
    for (i = 0; i < n; i++) {
	/* get the name of this variable or method */
	char *name = PyString_AsString(PyList_GetItem(keys, i));
	char *attr_its_about;
	if (strncmp(name, "_s_attr_", 8) == 0) {
	    attr_its_about = name + 8;
	    printf("%d %s\n", __LINE__, name);
	    declval = PyObject_GetAttrString(class1, name);
	    PyObject *policies = PyObject_GetAttrString(self, "policies");
	    PyDict_SetItemString(attr_its_about) = declval;
	    char *declvalname = PyString_AsString(declval);
	    if (strcmp(declvalname, "S_DATA") == 0 ||
		strcmp(declvalname, "S_CHILD") == 0 ||
		strcmp(declvalname, "S_CHILDREN") == 0 ||
		strcmp(declvalname, "S_REF") == 0 ||
		strcmp(declvalname, "S_REFS") == 0 ||
		strcmp(declvalname, "S_PARENT") == 0 ||
		strcmp(declvalname, "S_PARENTS") == 0) {
		/*
		 * self.dict_of_all_state_attrs[attr_its_about] = None
		 * try:
                 *     dflt = getattr(class1, attr_its_about)
		 * except AttributeError:
                 *     self.attrs_with_no_dflt.append(attr_its_about)
		 * else:
                 *     self.attr_dflt_pairs.append( (attr_its_about, dflt) )
                 *     self.defaultvals[attr_its_about] = dflt
		 */
	    }


	} else if (strcmp(name, "_s_deepcopy") == 0) {
	    PyObject_SetAttrString((PyObject*) self, "warn", PyInt_FromLong(0));
	    printf("%d %s\n", __LINE__, name);
	} else if (strncmp(name, "_s_categorize", 13) == 0) {
	    attr_its_about = name + 13;
	    printf("%d %s\n", __LINE__, name);
	}
    }
    Py_INCREF(Py_None);
    return Py_None;
}
#endif


static struct PyMethodDef
samevals_methods[] = {
    {"same_vals", (PyCFunction) same_vals, 1, same_vals_doc},
    {"setArrayType", (PyCFunction) setArrayType, 1, NULL},
#if 0
    {"Find_attr_decls", (PyCFunction) Find_attr_decls, 1, NULL},
#endif
    {NULL, NULL}
};

static char samevals_doc[] = "\
Read the source code. No clues for you here!";

void
initsamevals()
{
    Py_InitModule3("samevals", samevals_methods, samevals_doc);
}
