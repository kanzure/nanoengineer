cdef extern from "quux_help.c":
    __glColor3f(float,float,float)

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

def glColor3f(r, g, b):
    __glColor3f(r, g, b)

def hackNumericArray(ArrayType a):
    print "Type:", chr(a.descr.type)
    if chr(a.descr.type) != "f":
        raise TypeError("Float array required")
    if a.nd != 2:
        raise ValueError("2 dimensional array required")
    cdef int nrows, ncols
    cdef float *elems, x
    nrows = a.dimensions[0]
    ncols = a.dimensions[1]
    elems = <float *>a.data
    hyphen = "-"
    divider = ("+" + 10 * hyphen) * ncols + "+"
    print divider
    for row in range(nrows):
        for col in range(ncols):
            x = elems[row * ncols + col]
            print "| %8f" % x,
        print "|"
        print divider

def test():
    import Numeric
    print "Testing the OpenGL interface"
    glColor3f(1,2,3)
    a = (Numeric.array((1, 2), 'f'),
         Numeric.array((3, 4), 'f'))
    a = Numeric.array(a, 'f')
    hackNumericArray(a)
    print "Done testing"
