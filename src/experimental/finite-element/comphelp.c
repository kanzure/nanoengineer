#include "Python.h"

/*
 * Here's how to get stuff for comp.pyx
 * cproto -I/usr/include/python2.3 comphelp.c 2>/dev/null
 */

extern PyObject * setup(PyObject *computronium, int n);
extern PyObject * internalForces(double stiffness, double viscosityOverDt, double dtm);
extern PyObject * verletMomentum(void);
extern PyObject * applyForces(PyObject *forces, double dtm);

static PyObject *comp;
static int N;

#define _ASSERT(cond) \
  if (!(cond)) { char error[200]; sprintf(error, "%s(%d)  Expected: %s", \
           __FUNCTION__, __LINE__, #cond); \
           PyErr_SetString(PyExc_AssertionError, error); return NULL; }
#define CHECKTYPE(type,var)   _ASSERT(var != NULL); \
          _ASSERT(var != Py_None); _ASSERT(Py##type##_Check(var))
#define CHECK_2_TUPLE(var)  CHECKTYPE(Tuple,var); _ASSERT(PyTuple_Size(var) == 2)
#define CHECK_NSQ_LIST(var)  CHECKTYPE(List,var); _ASSERT(PyList_Size(var) == N*N)
#define ASSERT(cond)           _ASSERT(!PyErr_Occurred()); _ASSERT(cond)
#define EXPECTZERO(expr)   { int retval = (expr); ASSERT(retval==0); }

#if 0
#define SAY_INT(x)  fprintf(stderr, "%s(%d)  %s == %d\n", __FUNCTION__, __LINE__, #x, x)
#define SAY_OBJ(x)  fprintf(stderr, "%s(%d)  %s == <<", __FUNCTION__, __LINE__, #x); \
	    PyObject_Print(x, stderr, 0); fprintf(stderr, ">>\n")
#else
#define SAY_INT(x)
#define SAY_OBJ(x)
#endif

PyObject * setup(PyObject *computronium, int n)
{
    CHECKTYPE(Instance, computronium);
    comp = computronium;
    ASSERT(n > 1);
    N = n;
    Py_INCREF(Py_None);
    return Py_None;
}

static double *getArray(PyObject *parray)
{
    int i, j;
    double *v;

    CHECK_NSQ_LIST(parray);
    v = (double *) malloc(2 * N * N * sizeof(double));
    ASSERT(v != NULL);
    for (i = 0; i < N; i++) {
	for (j = 0; j < N; j++) {
	    int k = i * N + j;
	    PyObject *tmp;
	    PyObject *tpl = PyList_GetItem(parray, k);
	    ASSERT(PyTuple_Check(tpl));
	    ASSERT(PyTuple_Size(tpl) == 2);
	    tmp = PyTuple_GetItem(tpl, 0);
	    ASSERT(PyFloat_Check(tmp));
	    v[2*k] = PyFloat_AsDouble(tmp);
	    tmp = PyTuple_GetItem(tpl, 1);
	    ASSERT(PyFloat_Check(tmp));
	    v[2*k+1] = PyFloat_AsDouble(tmp);
	}
    }
    return v;
}


PyObject * internalForces(double stiffness, double viscosityOverDt, double dtm)
{
    int i, j, k, i2, j2, arraysize;
    double *v, *vold, *f;
    PyObject *forces, *u, *u_old;

    CHECKTYPE(Instance, comp);
    arraysize = 2 * N * N * sizeof(double);

    u = PyObject_GetAttr(comp, PyString_FromString("u"));
    v = getArray(u);
    if (v == NULL) return NULL;
    u_old = PyObject_GetAttr(comp, PyString_FromString("u_old"));
    vold = getArray(u_old);
    if (vold == NULL) return NULL;

    f = (double *) malloc(2 * N * N * sizeof(double));
    ASSERT(f != NULL);
    for (k = 0; k < 2*N*N; k++) {
	f[k] = 0.0;
    }

    for (i = 0; i < N; i++) {
	for (j = 0; j < N; j++) {
	    int k = i * N + j;
	    for (i2 = i - 1; i2 <= i + 1; i2 += 2) {
		for (j2 = j - 1; j2 <= j + 1; j2 += 2) {
		    if (0 <= i2 && i2 < N && 0 <= j2 && j2 < N) {
			double Dx, Dy, Px, Py, fx, fy;
			int k2 = i2 * N + j2;
			Dx = v[2*k2] - v[2*k];
			Dy = v[2*k2+1] - v[2*k+1];
			Px = vold[2*k2] - vold[2*k];
			Py = vold[2*k2+1] - vold[2*k+1];
			fx = stiffness * Dx + viscosityOverDt * (Px - Dx);
			fy = stiffness * Dy + viscosityOverDt * (Py - Dy);
			f[2*k] += fx;
			f[2*k+1] += fy;
			f[2*k2] -= fx;
			f[2*k2+1] -= fy;
		    }
		}
	    }
	}
    }
    free(v);
    free(vold);

    forces = PyList_New(N * N);
    ASSERT(forces != NULL);
    for (i = 0; i < N; i++) {
	for (j = 0; j < N; j++) {
	    int k = i * N + j;
	    PyObject *ftpl = PyTuple_New(2);
	    ASSERT(ftpl != NULL);
	    EXPECTZERO(PyTuple_SetItem(ftpl, 0, PyFloat_FromDouble(f[2*k])));
	    EXPECTZERO(PyTuple_SetItem(ftpl, 1, PyFloat_FromDouble(f[2*k+1])));
	    EXPECTZERO(PyList_SetItem(forces, k, ftpl));
	}
    }
    free(f);
    applyForces(forces, dtm);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *verletMomentum(void)
{
    int k;
    PyObject *u_new, *u, *u_old;
    double *v, *vold;

    u = PyObject_GetAttr(comp, PyString_FromString("u"));
    v = getArray(u);
    if (v == NULL) return NULL;
    u_old = PyObject_GetAttr(comp, PyString_FromString("u_old"));
    vold = getArray(u_old);
    if (vold == NULL) return NULL;
    u_new = PyList_New(N * N);
    ASSERT(u_new != NULL);

    for (k = 0; k < N * N; k++) {
	PyObject *vnew;
	vnew = Py_BuildValue("(dd)",
			     2 * v[2*k] - vold[2*k],
			     2 * v[2*k+1] - vold[2*k+1]);
	CHECK_2_TUPLE(vnew);
	EXPECTZERO(PyList_SetItem(u_new, k, vnew));
    }
    free(v);
    free(vold);
    EXPECTZERO(PyObject_SetAttr(comp, PyString_FromString("u_new"), u_new));
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject * applyForces(PyObject *forces, double dtm)
{
    int k;
    PyObject *u_new;
    double *vnew, *f;

    u_new = PyObject_GetAttr(comp, PyString_FromString("u_new"));
    vnew = getArray(u_new);
    if (vnew == NULL) return NULL;
    f = getArray(forces);
    if (f == NULL) return NULL;
    u_new = PyList_New(N * N);
    ASSERT(u_new != NULL);

    for (k = 0; k < N * N; k++) {
	PyObject *vn;
	vn = Py_BuildValue("(dd)",
			   vnew[2*k] + dtm * f[2*k],
			   vnew[2*k+1] + dtm * f[2*k+1]);
	CHECK_2_TUPLE(vn);
	EXPECTZERO(PyList_SetItem(u_new, k, vn));
    }
    free(f);
    free(vnew);
    EXPECTZERO(PyObject_SetAttr(comp, PyString_FromString("u_new"), u_new));
    Py_INCREF(Py_None);
    return Py_None;
}
