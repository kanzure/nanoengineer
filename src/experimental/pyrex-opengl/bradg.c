/*
 * Brad's stuff
 */

#include "Python.h"

extern PyObject * _result;

// #define ZZ()  printf("%s\n", __FUNCTION__)
#define ZZ()

static PyObject *_result = NULL;

PyObject *
_getTestResult(void)
{
    PyObject *retval;
    if (_result == NULL) {
	PyErr_SetString(PyExc_RuntimeError,
			"no corresponding function call");
	return NULL;
    }
    /*
     * Only return each result once, so refcounting works OK.
     */
    retval = _result;
    _result = NULL;
    return retval;
}

/* --------------------------------------- */

void shapeRendererInit(void)
{
    _result = PyString_FromString(__FUNCTION__);
}

void shapeRendererSetFrustum(float frustum[6])
{
    int i;
    _result = PyTuple_New(6);
    for (i = 0; i < 6; i++)
	PyTuple_SetItem(_result, i,
			PyFloat_FromDouble((double)frustum[i]));
}

void shapeRendererSetViewport(int viewport[4])
{
    int i;
    _result = PyTuple_New(4);
    for (i = 0; i < 4; i++)
	PyTuple_SetItem(_result, i,
			PyInt_FromLong((long)viewport[i]));
}

void shapeRendererSetModelView(float modelview[6])
{
    int i;
    _result = PyTuple_New(6);
    for (i = 0; i < 6; i++)
	PyTuple_SetItem(_result, i,
			PyFloat_FromDouble((double)modelview[i]));
}

void shapeRendererUpdateLODEval(void)
{
    _result = PyString_FromString(__FUNCTION__);
}

void shapeRendererSetLODScale(float s)
{
    _result = Py_BuildValue("f", s);
}

void shapeRendererDrawSpheres(int count, float center[][3],
			      float radius[], float color[][4])
{
    PyObject *centerTuple, *radiusTuple, *colorTuple;
    int i;
    _result = PyTuple_New(3);
    centerTuple = PyTuple_New(count);
    radiusTuple = PyTuple_New(count);
    colorTuple = PyTuple_New(count);
    PyTuple_SetItem(_result, 0, centerTuple);
    PyTuple_SetItem(_result, 1, radiusTuple);
    PyTuple_SetItem(_result, 2, colorTuple);
    for (i = 0; i < count; i++) {
	PyTuple_SetItem(centerTuple, i, Py_BuildValue("(fff)",
						      center[i][0],
						      center[i][1],
						      center[i][2]));
	PyTuple_SetItem(radiusTuple, i, Py_BuildValue("f", radius[i]));
	PyTuple_SetItem(colorTuple, i, Py_BuildValue("(ffff)",
						     color[i][0],
						     color[i][1],
						     color[i][2],
						     color[i][3]));
    }
}

void shapeRendererDrawCylinders(int count, float pos1[][3],
				       float pos2[][3], float radius[],
				       float color[][4])
{
    PyObject *pos1Tuple, *pos2Tuple, *radiusTuple, *colorTuple;
    int i;
    _result = PyTuple_New(4);
    pos1Tuple = PyTuple_New(count);
    pos2Tuple = PyTuple_New(count);
    radiusTuple = PyTuple_New(count);
    colorTuple = PyTuple_New(count);
    PyTuple_SetItem(_result, 0, pos1Tuple);
    PyTuple_SetItem(_result, 1, pos2Tuple);
    PyTuple_SetItem(_result, 2, radiusTuple);
    PyTuple_SetItem(_result, 3, colorTuple);
    for (i = 0; i < count; i++) {
	PyTuple_SetItem(pos1Tuple, i, Py_BuildValue("(fff)",
						    pos1[i][0],
						    pos1[i][1],
						    pos1[i][2]));
	PyTuple_SetItem(pos2Tuple, i, Py_BuildValue("(fff)",
						    pos2[i][0],
						    pos2[i][1],
						    pos2[i][2]));
	PyTuple_SetItem(radiusTuple, i, Py_BuildValue("f", radius[i]));
	PyTuple_SetItem(colorTuple, i, Py_BuildValue("(ffff)",
						     color[i][0],
						     color[i][1],
						     color[i][2],
						     color[i][3]));
    }
}
