"""
### This is a copy of file OpenGL/GL/ARB/vertex_shader.py from
### /Library/Python/2.5/site-packages/PyOpenGL-3.0.0b3-py2.5.egg .
### It replaces the broken version in PyOpenGL-3.0.0a6-py2.5.egg .
###
### The only difference between the two is in the glGetActiveAttribARB function,
### where the max_index and length parameters retrieved from OpenGL by
### glGetObjectParameterivARB are converted to integers.
###
### The only change to the b3 version to make it work in a6 is that the
### glGetObjectParameterivARB function is imported from the b3
### shader_objects_patch.py file in this same directory.

OpenGL extension ARB.vertex_shader

$Id$

This module customises the behaviour of the
OpenGL.raw.GL.ARB.vertex_shader to provide a more
Python-friendly API
"""
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions, wrapper
from OpenGL.GL import glget
import ctypes
from OpenGL.raw.GL.ARB.vertex_shader import *

from graphics.drawing.shader_objects_patch import glGetObjectParameterivARB ### Added _patch.

base_glGetActiveAttribARB = glGetActiveAttribARB
def glGetActiveAttribARB(program, index):
    """
    Retrieve the name, size and type of the uniform of the index in the program
    """
    max_index = int(glGetObjectParameterivARB( program, GL_OBJECT_ACTIVE_ATTRIBUTES_ARB ))
    length = int(glGetObjectParameterivARB( program, GL_OBJECT_ACTIVE_ATTRIBUTE_MAX_LENGTH_ARB))
    if index < max_index and index >= 0 and length > 0:
        name = ctypes.create_string_buffer(length)
        size = arrays.GLintArray.zeros( (1,))
        gl_type = arrays.GLuintArray.zeros( (1,))
        base_glGetActiveAttribARB(program, index, length, None, size, gl_type, name)
        return name.value, size[0], gl_type[0]
    raise IndexError, 'index out of range from zero to %i' % (max_index - 1, )
glGetActiveAttribARB.wrappedOperation = base_glGetActiveAttribARB
