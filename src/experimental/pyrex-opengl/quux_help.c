#ifdef MACOSX
#include <gl.h>
#include <glu.h>
#else
#ifdef _WIN32
#include <windows.h> /* Even MinGW includes this */
#endif
#include <GL/gl.h>
#include <GL/glu.h>
#endif
#include "Python.h"
#include "bradg.h"

// extern PyObject *_getTestResult(void);
// PyObject *_getTestResult(void) { return NULL; }
PyObject *_getTestResult(void) { Py_INCREF(Py_None); return Py_None; }

static PyObject *
_glColor3f(float r, float g, float b)
{
    /* Don't call glGetError() in this function! */
    glColor3f(r, g, b);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_checkArray(PyArrayObject *a)
{
    PyObject *retval;
    float *data = (float *) a->data;
    if (a->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions");
	return NULL;
    }
    if (a->dimensions[0] != 2 || a->dimensions[0] != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong dimensions");
	return NULL;
    }
    retval = PyTuple_New(4);
    PyTuple_SetItem(retval, 0, PyFloat_FromDouble((double) data[0]));
    PyTuple_SetItem(retval, 1, PyFloat_FromDouble((double) data[1]));
    PyTuple_SetItem(retval, 2, PyFloat_FromDouble((double) data[2]));
    PyTuple_SetItem(retval, 3, PyFloat_FromDouble((double) data[3]));
    return retval;
}

/*
 * Wrappers for Brad's stuff
 */

static PyObject *_shapeRendererInit(void)
{
    return shapeRendererInit();
}

static PyObject *_shapeRendererStartDrawing(void)
{
    shapeRendererStartDrawing();
    return _getTestResult();
}

static PyObject *_shapeRendererFinishDrawing(void)
{
    shapeRendererFinishDrawing();
    return _getTestResult();
}

static PyObject *_shapeRendererSetFrustum(float frustum[6])
{
    shapeRendererSetFrustum(frustum);
    return _getTestResult();
}

static PyObject *_shapeRendererSetOrtho(float ortho[6])
{
    shapeRendererSetOrtho(ortho);
    return _getTestResult();
}

static PyObject *_shapeRendererSetViewport(int viewport[4])
{
    shapeRendererSetViewport(viewport);
    return _getTestResult();
}

static PyObject *_shapeRendererSetModelView(float modelview[6])
{
    shapeRendererSetModelView(modelview);
    return _getTestResult();
}

static PyObject *_shapeRendererUpdateLODEval(void)
{
    shapeRendererUpdateLODEval();
    return _getTestResult();
}

static PyObject *_shapeRendererSetLODScale(float s)
{
    shapeRendererSetLODScale(s);
    return _getTestResult();
}

static PyObject *_shapeRendererSetMaterialParameters(float whiteness, float brightness, float shininess)
{
    shapeRendererSetMaterialParameters(whiteness, brightness, shininess);
    return _getTestResult();
}

static PyObject *_shapeRendererSetUseDynamicLOD(int useBool)
{
    shapeRendererSetUseDynamicLOD(useBool);
    return _getTestResult();
}

static PyObject *_shapeRendererSetStaticLODLevels(int sphere, int cylinder)
{
    shapeRendererSetStaticLODLevels(sphere, cylinder);
    return _getTestResult();
}

static int _shapeRendererGetInteger(int what)
{
    return shapeRendererGetInteger(what);
}

static PyObject *_shapeRendererDrawSpheres(int count,
					   PyArrayObject *center,
					   PyArrayObject *radius,
					   PyArrayObject *color,
                                           PyArrayObject *names)
{
    unsigned int *namesp;

    if (center->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: center");
	return NULL;
    }
    if (center->dimensions[0] < count) {
	PyErr_SetString(PyExc_ValueError, "too few for count: center");
	return NULL;
    }
    if (center->dimensions[1] != 3) {
	PyErr_SetString(PyExc_ValueError, "wrong number of columns: center");
	return NULL;
    }

    if (radius->nd != 1) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: radius");
	return NULL;
    }
    if (radius->dimensions[0] < count) {
	PyErr_SetString(PyExc_ValueError, "too few for count: radius");
	return NULL;
    }

    if (color->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions");
	return NULL;
    }
    if (color->dimensions[0] < count) {
	PyErr_SetString(PyExc_ValueError, "too few for count: color");
	return NULL;
    }
    if (color->dimensions[1] != 4) {
	PyErr_SetString(PyExc_ValueError, "wrong number of columns: color");
	return NULL;
    }

    if (names == Py_None) {
        namesp = NULL;
    } else {
        if (names->nd != 1) {
            PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: names");
            return NULL;
        }
        if (names->dimensions[0] < count) {
            PyErr_SetString(PyExc_ValueError, "too few for count: names");
            return NULL;
        }
        namesp = (unsigned int *)names->data;
    }

    return shapeRendererDrawSpheres(count,
				    (float(*)[3])center->data,
				    (float*)radius->data,
				    (float(*)[4])color->data,
                                    namesp);
}

static PyObject *_shapeRendererDrawCylinders(int count,
					     PyArrayObject *pos1,
					     PyArrayObject *pos2,
					     PyArrayObject *radius,
					     PyArrayObject *capped,
					     PyArrayObject *color,
                                             PyArrayObject *names)
{
    unsigned int *namesp;

    if (pos1->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: pos1");
	return NULL;
    }
    if (pos1->dimensions[0] < count) {
	PyErr_SetString(PyExc_ValueError, "too few for count: pos1");
	return NULL;
    }
    if (pos1->dimensions[1] != 3) {
	PyErr_SetString(PyExc_ValueError, "wrong number of columns: pos1");
	return NULL;
    }

    if (pos2->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: pos2");
	return NULL;
    }
    if (pos2->dimensions[0] < count) {
	PyErr_SetString(PyExc_ValueError, "too few for count: pos2");
	return NULL;
    }
    if (pos2->dimensions[1] != 3) {
	PyErr_SetString(PyExc_ValueError, "wrong number of columns: pos2");
	return NULL;
    }

    if (radius->nd != 1) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: radius");
	return NULL;
    }
    if (radius->dimensions[0] < count) {
	PyErr_SetString(PyExc_ValueError, "too few for count: radius");
	return NULL;
    }

    if (capped->nd != 1) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: capped");
	return NULL;
    }
    if (capped->dimensions[0] < count) {
	PyErr_SetString(PyExc_ValueError, "too few for count: capped");
	return NULL;
    }

    if (color->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions");
	return NULL;
    }
    if (color->dimensions[0] < count) {
	PyErr_SetString(PyExc_ValueError, "too few for count: color");
	return NULL;
    }
    if (color->dimensions[1] != 4) {
	PyErr_SetString(PyExc_ValueError, "wrong number of columns: color");
	return NULL;
    }

    if (names == Py_None) {
        namesp = NULL;
    } else {
        if (names->nd != 1) {
            PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: names");
            return NULL;
        }
        if (names->dimensions[0] < count) {
            PyErr_SetString(PyExc_ValueError, "too few for count: names");
            return NULL;
        }
        namesp = (unsigned int *)names->data;
    }

    return shapeRendererDrawCylinders(count,
				      (float (*)[3])pos1->data,
                                      (float (*)[3])pos2->data,
				      (float *)radius->data,
                                      (int *)capped->data,
                                      (float (*)[4])color->data,
                                      namesp);
}
