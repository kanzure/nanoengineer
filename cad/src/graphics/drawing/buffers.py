# Vertex/Index Buffer Object support.
#
# Based on a version published without copyright by Nathan Ostgard at
# http://nathanostgard.com/archives/2007/8/31/vertex-buffer-object-pyopengl/
# http://nathanostgard.com/uploaded/vertex-buffer-objects-pyopengl/buffers.py

from OpenGL.GL import GL_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_ELEMENT_ARRAY_BUFFER_ARB
from OpenGL.GL import glGenBuffers
from OpenGL.GL import glBindBuffer
from OpenGL.GL import glBufferData
from OpenGL.GL import glDeleteBuffers
from OpenGL.GL import glColorPointer
from OpenGL.GL import glEdgeFlagPointer
from OpenGL.GL import glIndexPointer
from OpenGL.GL import glNormalPointer
from OpenGL.GL import glTexCoordPointer
from OpenGL.GL import glVertexPointer
from OpenGL.raw import GL
from OpenGL.arrays import ArrayDatatype as ADT

class VertexBuffer(object):

  
  def __init__(self, data, usage):
    self.buffer = GL.GLuint(0)
    glGenBuffers(1, self.buffer)
    self.buffer = self.buffer.value
    self.size = len(data)               # Added.
    glBindBuffer(GL_ARRAY_BUFFER_ARB, self.buffer)
    glBufferData(GL_ARRAY_BUFFER_ARB, ADT.arrayByteCount(data),
                 ADT.voidDataPointer(data), usage)

  def __del__(self):
    if GL:                              # Added.
      glDeleteBuffers(1, GL.GLuint(self.buffer))

  def bind(self):
    glBindBuffer(GL_ARRAY_BUFFER_ARB, self.buffer)

  def bind_colors(self, size, type, stride=0):
    self.bind()
    glColorPointer(size, type, stride, None)

  def bind_edgeflags(self, stride=0):
    self.bind()
    glEdgeFlagPointer(stride, None)

  def bind_indexes(self, type, stride=0):
    self.bind()
    glIndexPointer(type, stride, None)

  def bind_normals(self, type, stride=0):
    self.bind()
    glNormalPointer(type, stride, None)

  def bind_texcoords(self, size, type, stride=0):
    self.bind()
    glTexCoordPointer(size, type, stride, None)

  def bind_vertexes(self, size, type, stride=0):
    self.bind()
    glVertexPointer(size, type, stride, None)


class ElementBuffer(object):            # Added.

  def __init__(self, data, usage):
    self.buffer = GL.GLuint(0)
    glGenBuffers(1, self.buffer)
    self.buffer = self.buffer.value
    self.size = len(data)               # Added.
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER_ARB, self.buffer)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER_ARB, ADT.arrayByteCount(data),
                 ADT.voidDataPointer(data), usage)

  def __del__(self):
    if GL:
      glDeleteBuffers(1, GL.GLuint(self.buffer))

  def bind(self):
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER_ARB, self.buffer)
