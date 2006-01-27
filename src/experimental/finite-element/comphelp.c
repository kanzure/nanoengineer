#include "Python.h"

/*
 * Here's how to get stuff for comp.pyx
 * cproto -I/usr/include/python2.3 comphelp.c 2>/dev/null
 */

extern PyObject * setup(int n);
extern PyObject * internalForces(double stiffness, double viscosityOverDt, double dtm);
extern PyObject * verletMomentum(void);
extern PyObject * applyForces(PyObject *forces, double dtm);

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
#define SAY_STR(x)  fprintf(stderr, "%s(%d)  %s == \"%s\"\n",\
                            __FUNCTION__, __LINE__, #x, x)
#define SAY_INT(x)  fprintf(stderr, "%s(%d)  %s == %d\n", __FUNCTION__, __LINE__, #x, x)
#define SAY_DBL(x)  fprintf(stderr, "%s(%d)  %s == %g\n", __FUNCTION__, __LINE__, #x, x)
#define SAY_OBJ(x)  fprintf(stderr, "%s(%d)  %s == <<", __FUNCTION__, __LINE__, #x); \
	    PyObject_Print(x, stderr, 0); fprintf(stderr, ">>\n")
#else
#define SAY_STR(x)
#define SAY_INT(x)
#define SAY_DBL(x)
#define SAY_OBJ(x)
#endif

static double *u, *u_old, *u_new, *x;

PyObject * setup(int n)
{
    int i;
    ASSERT(n > 1);
    N = n;
    u = (double *) malloc(2 * N * N * sizeof(double));
    ASSERT(u != NULL);
    u_old = (double *) malloc(2 * N * N * sizeof(double));
    ASSERT(u_old != NULL);
    u_new = (double *) malloc(2 * N * N * sizeof(double));
    ASSERT(u_new != NULL);
    x = (double *) malloc(2 * N * N * sizeof(double));
    ASSERT(x != NULL);
    for (i = 0; i < N * N; i++) {
	int row, col;
	u[2 * i] = 0.0;
	u[2 * i + 1] = 0.0;
	u_old[2 * i] = 0.0;
	u_old[2 * i + 1] = 0.0;
	u_new[2 * i] = 0.0;
	u_new[2 * i + 1] = 0.0;
	row = i / N;
	col = i % N;
	x[2 * i] = 1.0 * col / N;
	x[2 * i + 1] = 1.0 * row / N;
    }
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

PyObject * _c_applyForces(double *forces, double dtm)
{
    int k;

    if (forces == NULL) return NULL;
    for (k = 0; k < N * N; k++) {
	u_new[2 * k] += dtm * forces[2 * k];
	u_new[2 * k + 1] += dtm * forces[2 * k + 1];
    }
    Py_INCREF(Py_None);
    return Py_None;
}


PyObject * internalForces(double stiffness, double viscosityOverDt, double dtm)
{
    int i, j;

    for (i = 0; i < N; i++) {
	for (j = 0; j < N; j++) {
	    double Dx, Dy, Px, Py, fx, fy;
	    int k2, k = i * N + j;
	    if (i > 0) {
		k2 = (i - 1) * N + j;
		Dx = u[2*k2] - u[2*k];
		Dy = u[2*k2+1] - u[2*k+1];
		Px = u_old[2*k2] - u_old[2*k];
		Py = u_old[2*k2+1] - u_old[2*k+1];
		fx = stiffness * Dx + viscosityOverDt * (Dx - Px);
		fy = stiffness * Dy + viscosityOverDt * (Dy - Py);
		u_new[2*k] += dtm * fx;
		u_new[2*k+1] += dtm * fy;
		u_new[2*k2] -= dtm * fx;
		u_new[2*k2+1] -= dtm * fy;
	    }
	    if (i < N - 1) {
		k2 = (i + 1) * N + j;
		Dx = u[2*k2] - u[2*k];
		Dy = u[2*k2+1] - u[2*k+1];
		Px = u_old[2*k2] - u_old[2*k];
		Py = u_old[2*k2+1] - u_old[2*k+1];
		fx = stiffness * Dx + viscosityOverDt * (Dx - Px);
		fy = stiffness * Dy + viscosityOverDt * (Dy - Py);
		u_new[2*k] += dtm * fx;
		u_new[2*k+1] += dtm * fy;
		u_new[2*k2] -= dtm * fx;
		u_new[2*k2+1] -= dtm * fy;
	    }
	    if (i > 0) {
		k2 = i * N + (j - 1);
		Dx = u[2*k2] - u[2*k];
		Dy = u[2*k2+1] - u[2*k+1];
		Px = u_old[2*k2] - u_old[2*k];
		Py = u_old[2*k2+1] - u_old[2*k+1];
		fx = stiffness * Dx + viscosityOverDt * (Dx - Px);
		fy = stiffness * Dy + viscosityOverDt * (Dy - Py);
		u_new[2*k] += dtm * fx;
		u_new[2*k+1] += dtm * fy;
		u_new[2*k2] -= dtm * fx;
		u_new[2*k2+1] -= dtm * fy;
	    }
	    if (j < N - 1) {
		k2 = i * N + (j + 1);
		Dx = u[2*k2] - u[2*k];
		Dy = u[2*k2+1] - u[2*k+1];
		Px = u_old[2*k2] - u_old[2*k];
		Py = u_old[2*k2+1] - u_old[2*k+1];
		fx = stiffness * Dx + viscosityOverDt * (Dx - Px);
		fy = stiffness * Dy + viscosityOverDt * (Dy - Py);
		u_new[2*k] += dtm * fx;
		u_new[2*k+1] += dtm * fy;
		u_new[2*k2] -= dtm * fx;
		u_new[2*k2+1] -= dtm * fy;
	    }
	}
    }
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *verletMomentum(void)
{
    int k;
    for (k = 0; k < N * N; k++) {
	u_new[2 * k] = 2 * u[2 * k] - u_old[2 * k];
	u_new[2 * k + 1] = 2 * u[2 * k + 1] - u_old[2 * k + 1];
    }
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject * applyForces(PyObject *forces, double dtm)
{
    PyObject *retval;
    double *f;

    f = getArray(forces);
    if (f == NULL) return NULL;
    retval = _c_applyForces(f, dtm);
    free(f);
    return retval;
}

PyObject * draw(PyObject *drawCallback, int w, int h)
{
    int i;
    double a, b;
    a = 0.6;
    b = 0.5 * (1.0 - a);
    ASSERT(drawCallback != NULL);
    ASSERT(PyCallable_Check(drawCallback));
    for (i = 0; i < N * N; i++) {
	PyObject *pValue;
	PyObject *args =
	    Py_BuildValue("(dd)",
			  w * (a * (x[2 * i] + u[2 * i]) + b),
			  h * (a * (x[2 * i + 1] + u[2 * i + 1]) + b));
	pValue = PyObject_CallObject(drawCallback, args);
	ASSERT(!PyErr_Occurred());
	Py_DECREF(args);
	Py_XDECREF(pValue);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *rotate(void)
{
    double *tmp = u_old;
    u_old = u;
    u = u_new;
    u_new = tmp;
    Py_INCREF(Py_None);
    return Py_None;
}
