import Numeric
import unittest

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

cdef extern from "quux_help.c":
    __glColor3f(float,float,float)
    _shapeRendererInit()
    _shapeRendererSetFrustum(float frustum[6])
    _shapeRendererSetViewport(int viewport[4])
    _shapeRendererSetModelView(float modelview[6])
    _shapeRendererUpdateLODEval()
    _shapeRendererSetLODScale(float s)
    _shapeRendererDrawSpheres(int count, float center[][3],
                              float radius[], float color[][4])
    _shapeRendererDrawCylinders(int count, float pos1[][3],
                                float pos2[][3], float radius[],
                                float color[][4])
    _checkArray(ArrayType a)

#####################################

def __hackNumericArray(ArrayType a):
    if chr(a.descr.type) != "f":
        raise TypeError("Float array required")
    if a.nd != 2:
        raise ValueError("2 dimensional array required")
    cdef int nrows, ncols
    cdef float *elems, x
    nrows = a.dimensions[0]
    ncols = a.dimensions[1]
    elems = <float *>a.data
    result = [ ]
    for row in range(nrows):
        thisRow = [ ]
        for col in range(ncols):
            thisRow.append(elems[row * ncols + col])
        result.append(thisRow)
    return result

def hackNumericArray(ArrayType a):
    return _checkArray(a)

####################################

def glColor3f(r, g, b):
    __glColor3f(r, g, b)


def shapeRendererInit():
    _shapeRendererInit()

def shapeRendererSetFrustum(ArrayType frustum):
    if chr(frustum.descr.type) != "f":
        raise TypeError("Float array required")
    if frustum.nd != 1:
        raise ValueError("1 dimensional array required")
    cdef int nrows, ncols
    cdef float *elems, x
    nelems = frustum.dimensions[0]
    assert nelems == 6
    _shapeRendererSetFrustum(<float *>frustum.data)

def shapeRendererSetViewport(viewport):
    pass

def shapeRendererSetModelView(modelview):
    pass

def shapeRendererUpdateLODEval():
    pass

def shapeRendererSetLODScale(s):
    pass

def shapeRendererDrawSpheres(count, center,
                             radius, color):
    pass

def shapeRendererDrawCylinders(count, pos1,
                               pos2, radius,
                               color):
    pass

####################################

class Tests(unittest.TestCase):

    def testColor(self):
        glColor3f(1,2,3)

    def testHackNumericArray(self):
        a = Numeric.array((Numeric.array((1, 2), 'f'),
                           Numeric.array((3, 4), 'f')), 'f')
        assert hackNumericArray(a) == (1.0, 2.0, 3.0, 4.0)

    def testSetFrustum(self):
        frustum = Numeric.array((1, 2, 3, 4, 5, 6), 'f')
        shapeRendererSetFrustum(frustum)

    def testSetFrustumWrongNumberOfFloats(self):
        try:
            frustum = Numeric.array((1, 2, 3, 4, 5), 'f')
            shapeRendererSetFrustum(frustum)
        except AssertionError:
            pass

def test():
    suite = unittest.makeSuite(Tests, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)


