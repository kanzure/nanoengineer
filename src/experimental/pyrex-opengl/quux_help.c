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

static PyObject *_shapeRendererInit()
{
    return shapeRendererInit();
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

static PyObject *_shapeRendererSetUseLOD(int useBool)
{
    shapeRendererSetUseLOD(useBool);
    return _getTestResult();
}

static PyObject *_shapeRendererDrawSpheres(int count,
					   PyArrayObject *center,
					   PyArrayObject *radius,
					   PyArrayObject *color)
{
    float center_data[count][3];
    float radius_data[count];
    float color_data[count][4];

    if (center->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: center");
	return NULL;
    }
    if (center->dimensions[0] != count) {
	PyErr_SetString(PyExc_ValueError, "wrong number of atoms: center");
	return NULL;
    }
    if (center->dimensions[1] != 3) {
	PyErr_SetString(PyExc_ValueError, "wrong number of columns: center");
	return NULL;
    }
    memmove(center_data, center->data, 3 * count * sizeof(float));

    if (radius->nd != 1) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: radius");
	return NULL;
    }
    if (radius->dimensions[0] != count) {
	PyErr_SetString(PyExc_ValueError, "wrong dimension: radius");
	return NULL;
    }
    memmove(radius_data, radius->data, count * sizeof(float));

    if (color->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions");
	return NULL;
    }
    if (color->dimensions[0] != count) {
	PyErr_SetString(PyExc_ValueError, "wrong number of atoms: color");
	return NULL;
    }
    if (color->dimensions[1] != 4) {
	PyErr_SetString(PyExc_ValueError, "wrong number of columns: color");
	return NULL;
    }
    memmove(color_data, color->data, 4 * count * sizeof(float));

    return shapeRendererDrawSpheres(count,
				    center_data,
				    radius_data,
				    color_data);
}

static PyObject *_shapeRendererDrawCylinders(int count,
					     PyArrayObject *pos1,
					     PyArrayObject *pos2,
					     PyArrayObject *radius,
					     PyArrayObject *capped,
					     PyArrayObject *color)
{
    float pos1_data[count][3];
    float pos2_data[count][3];
    float radius_data[count];
    int capped_data[count];
    float color_data[count][4];

    if (pos1->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: pos1");
	return NULL;
    }
    if (pos1->dimensions[0] != count) {
	PyErr_SetString(PyExc_ValueError, "wrong number of atoms: pos1");
	return NULL;
    }
    if (pos1->dimensions[1] != 3) {
	PyErr_SetString(PyExc_ValueError, "wrong number of columns: pos1");
	return NULL;
    }
    memmove(pos1_data, pos1->data, 3 * count * sizeof(float));

    if (pos2->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: pos2");
	return NULL;
    }
    if (pos2->dimensions[0] != count) {
	PyErr_SetString(PyExc_ValueError, "wrong number of atoms: pos2");
	return NULL;
    }
    if (pos2->dimensions[1] != 3) {
	PyErr_SetString(PyExc_ValueError, "wrong number of columns: pos2");
	return NULL;
    }
    memmove(pos2_data, pos2->data, 3 * count * sizeof(float));

    if (radius->nd != 1) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: radius");
	return NULL;
    }
    if (radius->dimensions[0] != count) {
	PyErr_SetString(PyExc_ValueError, "wrong dimension: radius");
	return NULL;
    }
    memmove(radius_data, radius->data, count * sizeof(float));

    if (capped->nd != 1) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions: capped");
	return NULL;
    }
    if (capped->dimensions[0] != count) {
	PyErr_SetString(PyExc_ValueError, "wrong dimension: capped");
	return NULL;
    }
    memmove(capped_data, capped->data, count * sizeof(int));

    if (color->nd != 2) {
	PyErr_SetString(PyExc_ValueError, "wrong number of dimensions");
	return NULL;
    }
    if (color->dimensions[0] != count) {
	PyErr_SetString(PyExc_ValueError, "wrong number of atoms: color");
	return NULL;
    }
    if (color->dimensions[1] != 4) {
	PyErr_SetString(PyExc_ValueError, "wrong number of columns: color");
	return NULL;
    }
    memmove(color_data, color->data, 4 * count * sizeof(float));

    return shapeRendererDrawCylinders(count,
				      pos1_data, pos2_data,
				      radius_data, capped_data, color_data);
}
