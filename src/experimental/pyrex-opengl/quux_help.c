#include <GL/gl.h>
#include <GL/glu.h>
#include "Python.h"

extern PyObject *__glColor3f(float r, float g, float b);

PyObject *
__glColor3f(float r, float g, float b)
{
    /* Don't call glGetError() in this function! */
    printf("Hello from inside Will's code\n");
    glColor3f(r, g, b);
    Py_INCREF(Py_None);
    return Py_None;
}
