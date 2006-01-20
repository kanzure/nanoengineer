cdef extern from "quux_help.c":
    __glColor3f(float,float,float)

def glColor3f(r, g, b):
    __glColor3f(r, g, b)
