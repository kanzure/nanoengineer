# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
import numpy
import types
import unittest
import random
import OpenGL.GL

cdef extern from "Numeric/arrayobject.h":
    struct PyArray_Descr:
        int type_um, elsize
        char type
    ctypedef class Numeric.ArrayType [object PyArrayObject]:
        cdef char *data
        cdef int nd
        cdef int *dimensions, *strides
        cdef object base
        cdef PyArray_Descr *descr
        cdef int flags

# Changes here have to be reflected in bradg.h and vice versa
IS_VBO_ENABLED = 1

cdef extern from "quux_help.c":
    _getTestResult()
    _glColor3f(float,float,float)
    _shapeRendererInit()
    _shapeRendererStartDrawing()
    _shapeRendererFinishDrawing()
    _shapeRendererSetFrustum(float frustum[6])
    _shapeRendererSetOrtho(float ortho[6])
    _shapeRendererSetViewport(int viewport[4])
    _shapeRendererSetModelView(float modelview[6])
    _shapeRendererUpdateLODEval()
    _shapeRendererSetLODScale(float s)
    _shapeRendererSetMaterialParameters(float whiteness, float brightness, float shininess)
    _shapeRendererSetUseDynamicLOD(int useLODBool)
    _shapeRendererSetStaticLODLevels(int sphere, int cylinder)
    _shapeRendererDrawSpheresIlvd(int count, ArrayType spheres)
    _shapeRendererDrawSpheres(int count, ArrayType center,
                              ArrayType radius, ArrayType color,
                              ArrayType names)
    _shapeRendererDrawCylindersIlvd(int count, ArrayType cylinders)
    _shapeRendererDrawCylinders(int count, ArrayType pos1,
                                ArrayType pos2, ArrayType radius,
                                ArrayType capped, ArrayType color,
                                ArrayType names)
    int _shapeRendererGetInteger(int what)
    _checkArray(ArrayType a)

####################################

def glColor3f(r, g, b):
    _glColor3f(r, g, b)

def shapeRendererInit():
    return _shapeRendererInit()

def shapeRendererStartDrawing():
    return _shapeRendererStartDrawing()

def shapeRendererFinishDrawing():
    return _shapeRendererFinishDrawing()

def shapeRendererSetFrustum(ArrayType frustum):
    if chr(frustum.descr.type) != "f":
        raise TypeError("Float array required")
    if frustum.nd != 1:
        raise ValueError("1 dimensional array required")
    cdef int nrows, ncols
    cdef float *elems
    nelems = frustum.dimensions[0]
    assert nelems == 6
    return _shapeRendererSetFrustum(<float *>frustum.data)

def shapeRendererSetOrtho(ArrayType ortho):
    if chr(ortho.descr.type) != "f":
        raise TypeError("Float array required")
    if ortho.nd != 1:
        raise ValueError("1 dimensional array required")
    cdef int nrows, ncols
    cdef float *elems
    nelems = ortho.dimensions[0]
    assert nelems == 6
    return _shapeRendererSetOrtho(<float *>ortho.data)

def shapeRendererSetViewport(ArrayType viewport):
    if chr(viewport.descr.type) != "i":
        raise TypeError("Int array required")
    if viewport.nd != 1:
        raise ValueError("1 dimensional array required")
    cdef int nrows, ncols
    cdef int *elems
    nelems = viewport.dimensions[0]
    assert nelems == 4
    return _shapeRendererSetViewport(<int *>viewport.data)

def shapeRendererSetModelView(ArrayType modelview):
    if chr(modelview.descr.type) != "f":
        raise TypeError("Float array required")
    if modelview.nd != 1:
        raise ValueError("1 dimensional array required")
    cdef int nrows, ncols
    cdef float *elems, x
    nelems = modelview.dimensions[0]
    assert nelems == 6
    return _shapeRendererSetModelView(<float *>modelview.data)

def shapeRendererUpdateLODEval():
    return _shapeRendererUpdateLODEval()

def shapeRendererSetLODScale(s):
    return _shapeRendererSetLODScale(s)

def shapeRendererSetUseDynamicLOD(usebool):
    return _shapeRendererSetUseDynamicLOD(usebool)

def shapeRendererSetStaticLODLevels(sphere, cylinder):
    return _shapeRendererSetStaticLODLevels(sphere, cylinder)

def shapeRendererSetMaterialParameters(whiteness, brightness, shininess):
    return _shapeRendererSetMaterialParameters(whiteness, brightness, shininess)

def shapeRendererDrawSpheresIlvd(count, spheres):
    return _shapeRendererDrawSpheresIlvd(count, spheres)

def shapeRendererDrawSpheres(count, center, radius, color, names = None):
    return _shapeRendererDrawSpheres(count, center, radius, color, names)

def shapeRendererDrawCylindersIlvd(count, cylinders):
    return _shapeRendererDrawCylindersIlvd(count, cylinders)

def shapeRendererDrawCylinders(count, pos1, pos2, radius, capped, color, names = None):
    return _shapeRendererDrawCylinders(count, pos1, pos2, radius, capped, color, names)

def shapeRendererGetInteger(what):
    return _shapeRendererGetInteger(what)

####################################

def diffSquared(x, y):
    if type(x) in (types.FloatType, types.IntType):
        return (x - y) ** 2
    assert len(x) == len(y)
    diff = 0.0
    for u, v in map(None, x, y):
        diff = diff + diffSquared(u, v)
    return diff

# Floats aren't as accurate as doubles
def approximatelyEqual(x, y):
    return diffSquared(x, y) < 1.0e-6

class Tests(unittest.TestCase):

    def testColor(self):
        glColor3f(0.1, 0.2, 0.3)

    def testManyColors(self):
        OpenGL.GL.glClearColor(0.4, 0.4, 0.4, 0.0)  # gray
        OpenGL.GL.glClear(OpenGL.GL.GL_COLOR_BUFFER_BIT)
        OpenGL.GL.glMatrixMode(OpenGL.GL.GL_MODELVIEW)
        OpenGL.GL.glPushMatrix()
        OpenGL.GL.glDisable(OpenGL.GL.GL_LIGHTING)

        glColor3f(1.0, 0.0, 0.0)  # red
        OpenGL.GL.glBegin(OpenGL.GL.GL_POLYGON)
        OpenGL.GL.glVertex2f(0, 0)
        OpenGL.GL.glVertex2f(5, 0)
        OpenGL.GL.glVertex2f(5, 5)
        OpenGL.GL.glEnd()

        glColor3f(1.0, 1.0, 0.0)  # yellow
        OpenGL.GL.glBegin(OpenGL.GL.GL_POLYGON)
        OpenGL.GL.glVertex2f(0, 0)
        OpenGL.GL.glVertex2f(0, 5)
        OpenGL.GL.glVertex2f(-5, 5)
        OpenGL.GL.glEnd()

        glColor3f(0.0, 1.0, 0.0)  # green
        OpenGL.GL.glBegin(OpenGL.GL.GL_POLYGON)
        OpenGL.GL.glVertex2f(0, 0)
        OpenGL.GL.glVertex2f(-5, 0)
        OpenGL.GL.glVertex2f(-5, -5)
        OpenGL.GL.glEnd()

        glColor3f(0.0, 0.0, 1.0)  # blue
        OpenGL.GL.glBegin(OpenGL.GL.GL_POLYGON)
        OpenGL.GL.glVertex2f(0, 0)
        OpenGL.GL.glVertex2f(0, -5)
        OpenGL.GL.glVertex2f(5, -5)
        OpenGL.GL.glEnd()

        OpenGL.GL.glFlush()
        OpenGL.GL.glPopMatrix()

    def testHackNumericArray(self):
        a = Numeric.array((Numeric.array((1, 2), 'f'),
                           Numeric.array((3, 4), 'f')), 'f')
        assert _checkArray(a) == (1.0, 2.0, 3.0, 4.0)

    def testInit(self):
        assert shapeRendererInit() == "shapeRendererInit"

    def testSetFrustum(self):
        frustum = Numeric.array((1, 2, 3, 4, 5, 6), 'f')
        assert shapeRendererSetFrustum(frustum) == (1., 2., 3., 4., 5., 6)

    def testSetViewport(self):
        viewport = Numeric.array((314, 159, 262, 5358), 'i')
        assert shapeRendererSetViewport(viewport) == (314, 159, 262, 5358)

    def testSetModelview(self):
        modelview = Numeric.array((2, 7, 1, 8, 2, 8), 'f')
        #print shapeRendererSetModelView(modelview)
        assert shapeRendererSetModelView(modelview) == (2., 7., 1., 8., 2., 8.)

    def testSetFrustumWrongNumberOfFloats(self):
        try:
            frustum = Numeric.array((1, 2, 3, 4, 5), 'f')
            shapeRendererSetFrustum(frustum)
            assert False, "Failure expected here"
        except AssertionError:
            pass

    def testTooManyCallsToGetTestResult(self):
        try:
            frustum = Numeric.array((1, 2, 3, 4, 5, 6), 'f')
            shapeRendererSetFrustum(frustum)
            _getTestResult()
            assert False, "Failure expected here"
        except RuntimeError:
            pass

    def testSetLODScale(self):
        assert approximatelyEqual(shapeRendererSetLODScale(1.73205), 1.73205)

    def testUpdateLODEval(self):
        assert shapeRendererUpdateLODEval() == "shapeRendererUpdateLODEval"

    def testDrawSpheres(self):
        center = Numeric.array((Numeric.array((0, 0, 0), 'f'),
                                Numeric.array((0, 0, 1), 'f'),
                                Numeric.array((0, 1, 0), 'f'),
                                Numeric.array((0, 1, 1), 'f'),
                                Numeric.array((1, 0, 0), 'f'),
                                Numeric.array((1, 0, 1), 'f'),
                                Numeric.array((1, 1, 0), 'f'),
                                Numeric.array((1, 1, 1), 'f')), 'f')
        radius = Numeric.array((0.2, 0.4, 0.6, 0.8,
                                1.2, 1.4, 1.6, 1.8), 'f')
        color = Numeric.array((Numeric.array((0, 0, 0, 0.5), 'f'),
                               Numeric.array((0, 0, 1, 0.5), 'f'),
                               Numeric.array((0, 1, 0, 0.5), 'f'),
                               Numeric.array((0, 1, 1, 0.5), 'f'),
                               Numeric.array((1, 0, 0, 0.5), 'f'),
                               Numeric.array((1, 0, 1, 0.5), 'f'),
                               Numeric.array((1, 1, 0, 0.5), 'f'),
                               Numeric.array((1, 1, 1, 0.5), 'f')), 'f')
        result = shapeRendererDrawSpheres(8, center, radius, color)
        assert approximatelyEqual(result, (
            ((0., 0., 0.), (0., 0., 1.), (0., 1., 0.), (0., 1., 1.),
             (1., 0., 0.), (1., 0., 1.), (1., 1., 0.), (1., 1., 1.)),
            (0.2, 0.4, 0.6, 0.8, 1.2, 1.4, 1.6, 1.8),
            ((0., 0., 0., 0.5), (0., 0., 1., 0.5),
             (0., 1., 0., 0.5), (0., 1., 1., 0.5),
             (1., 0., 0., 0.5), (1., 0., 1., 0.5),
             (1., 1., 0., 0.5), (1., 1., 1., 0.5))))

    def testDrawCylinders(self):
        pos1 = Numeric.array((Numeric.array((0, 0, 0), 'f'),
                              Numeric.array((0, 0, 1), 'f'),
                              Numeric.array((0, 1, 0), 'f')), 'f')
        pos2 = Numeric.array((Numeric.array((2, 5, 6), 'f'),
                              Numeric.array((2, 5, 7), 'f'),
                              Numeric.array((2, 8, 6), 'f')), 'f')
        radius = Numeric.array((0.2, 0.4, 0.6), 'f')
        capped = Numeric.array((1, 0, 1), 'i')
        color = Numeric.array((Numeric.array((0, 0, 0, 0.5), 'f'),
                               Numeric.array((0, 0, 1, 0.5), 'f'),
                               Numeric.array((0, 1, 0, 0.5), 'f')), 'f')
        result = shapeRendererDrawCylinders(3, pos1, pos2, radius, capped, color)
        assert approximatelyEqual(result, (
            ((0., 0., 0.), (0., 0., 1.), (0., 1., 0.)),
            ((2., 5., 6.), (2., 5., 7.), (2., 8., 6.)),
            (0.2, 0.4, 0.6),
            ((0., 0., 0., 0.5), (0., 0., 1., 0.5), (0., 1., 0., 0.5))))

def test():
    shapeRendererInit()
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
