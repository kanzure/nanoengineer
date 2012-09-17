# Patch to the array size of glBufferDataARB, which should be the size in bytes,
# not the array size (number of elements.)  glBufferSubDataARB has the same bug.
#
# From PyOpenGL-3.0.0a6-py2.5.egg/OpenGL/GL/ARB/vertex_buffer_object.py

from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions, wrapper
from OpenGL.GL import glget
import ctypes
from OpenGL.raw.GL.ARB.vertex_buffer_object import *

def _sizeOfArrayInput( pyArgs, index, wrapper ):
        return (
                # Was arraySize.
                arrays.ArrayDatatype.arrayByteCount( pyArgs[index] )
        )

glBufferDataARB = wrapper.wrapper( glBufferDataARB ).setPyConverter(
        'data', arrays.asVoidArray(),
).setPyConverter( 'size' ).setCResolver(
        'data', arrays.ArrayDatatype.voidDataPointer ,
).setCConverter(
        'size', _sizeOfArrayInput,
).setReturnValues(
        wrapper.returnPyArgument( 'data' )
)

glBufferSubDataARB = wrapper.wrapper( glBufferSubDataARB ).setPyConverter(
        'data', arrays.asVoidArray(),
).setPyConverter( 'size' ).setCResolver(
        'data', arrays.ArrayDatatype.voidDataPointer ,
).setCConverter(
        'size', _sizeOfArrayInput,
).setReturnValues(
        wrapper.returnPyArgument( 'data' )
)

# For VBO drawing, the "indices" argument to glMultiDrawElements is an array of
# byte offsets within the bound Index Buffer Object in graphics card RAM, rather
# than of an array of pointers to parts of client-side index arrays.  See the
# docs for glBindBuffer, glDrawElements, and glMultiDrawElements.
#
# Changed the "indices" argument type from ctypes.POINTER(ctypes.c_void_p) to
# arrays.GLintArray, like the "first" argument of glMultiDrawArrays.
glMultiDrawElementsVBO = platform.createExtensionFunction(
	'glMultiDrawElementsEXT', dll=platform.GL,
	resultType=None,
	argTypes=(constants.GLenum, arrays.GLsizeiArray,
              constants.GLenum, arrays.GLintArray, constants.GLsizei,),
	doc = ('glMultiDrawElementsEXT( GLenum(mode), GLsizeiArray(count), '
           'GLenum(type), GLintArray(indices), GLsizei(primcount) ) -> None'),
	argNames = ('mode', 'count', 'type', 'indices', 'primcount',),
)
