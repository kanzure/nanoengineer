#include <GL/gl.h>
#include <GL/glu.h>
#include "Python.h"

extern PyObject *__glColor3f(float r, float g, float b);

PyObject *
__glColor3f(float r, float g, float b)
{
    /* Don't call glGetError() in this function! */
    //printf("Hello from inside Will's code\n");
    glColor3f(r, g, b);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *
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
 * Brad's stuff
 */

extern void shapeRendererInit();

extern void shapeRendererSetFrustum(float frustum[6]);
extern void shapeRendererSetViewport(int viewport[4]);
extern void shapeRendererSetModelView(float modelview[6]);
extern void shapeRendererUpdateLODEval();
extern void shapeRendererSetLODScale(float s);

extern void shapeRendererDrawSpheres(int count, float center[][3],
				     float radius[], float color[][4]);
extern void shapeRendererDrawCylinders(int count, float pos1[][3],
				       float pos2[][3], float radius[],
				       float color[][4]);

// #define ZZ()  printf("%s\n", __FUNCTION__)
#define ZZ()

void shapeRendererInit()
{
    ZZ();
}

void shapeRendererSetFrustum(float frustum[6])
{
    ZZ();
}

void shapeRendererSetViewport(int viewport[4])
{
    ZZ();
}

void shapeRendererSetModelView(float modelview[6])
{
    ZZ();
}

void shapeRendererUpdateLODEval()
{
    ZZ();
}

void shapeRendererSetLODScale(float s)
{
    ZZ();
}

void shapeRendererDrawSpheres(int count, float center[][3],
				     float radius[], float color[][4])
{
    ZZ();
}

void shapeRendererDrawCylinders(int count, float pos1[][3],
				       float pos2[][3], float radius[],
				       float color[][4])
{
    ZZ();
}



/*
 * Wrappers for Brad's stuff
 */

extern PyObject *_shapeRendererInit();

extern PyObject *_shapeRendererSetFrustum(float frustum[6]);
extern PyObject *_shapeRendererSetViewport(int viewport[4]);
extern PyObject *_shapeRendererSetModelView(float modelview[6]);
extern PyObject *_shapeRendererUpdateLODEval(void);
extern PyObject *_shapeRendererSetLODScale(float s);

extern PyObject *_shapeRendererDrawSpheres(int count,
					   PyArrayObject *center,
					   PyArrayObject *radius,
					   PyArrayObject *color);
extern PyObject *_shapeRendererDrawCylinders(int count,
					     PyArrayObject *pos1,
					     PyArrayObject *pos2,
					     PyArrayObject *radius,
					     PyArrayObject *color);



PyObject *_shapeRendererInit()
{
    shapeRendererInit();
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *_shapeRendererSetFrustum(float frustum[6])
{
    shapeRendererSetFrustum(frustum);
#if 0
    printf("%g %g %g %g %g %g\n",
	   frustum[0], frustum[1], frustum[2],
	   frustum[3], frustum[4], frustum[5]);
#endif
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *_shapeRendererSetViewport(int viewport[4])
{
    shapeRendererSetViewport(viewport);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *_shapeRendererSetModelView(float modelview[6])
{
    shapeRendererSetModelView(modelview);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *_shapeRendererUpdateLODEval(void)
{
    shapeRendererUpdateLODEval();
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *_shapeRendererSetLODScale(float s)
{
    shapeRendererSetLODScale(s);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *_shapeRendererDrawSpheres(int count,
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

    shapeRendererDrawSpheres(count,
			     center_data,
			     radius_data,
			     color_data);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *_shapeRendererDrawCylinders(int count,
				      PyArrayObject *pos1,
				      PyArrayObject *pos2,
				      PyArrayObject *radius,
				      PyArrayObject *color)
{
    float pos1_data[count][3];
    float pos2_data[count][3];
    float radius_data[count];
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

    shapeRendererDrawCylinders(count, pos1_data, pos2_data, radius_data, color_data);
    Py_INCREF(Py_None);
    return Py_None;
}
