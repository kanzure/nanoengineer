# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPrimitiveBuffer.py -- Manage VBO space for drawing primitives in large batches.

@author: Russ
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:
Originally written by Russ Fish; designed together with Bruce Smith.

================================================================

See design comments on:
* GL contexts, CSDLs and DrawingSet in DrawingSet.py
* TransformControl in TransformControl.py
* VBOs, IBOs, and GLPrimitiveBuffer in GLPrimitiveBuffer.py
* GLPrimitiveSet in GLPrimitiveSet in GLPrimitiveSet.py

== VBOs ==

* VBOs (Vertex Buffer Objects) in graphics card RAM store per-vertex data such
  as position and normal coordinates, color values, together with per-vertex
  attributes used by shader programs, such as sphere center point coordinates
  and radii.

* All of these per-vertex VBO arrays for a particular type of primitive are
  activated and used in parallel by a VBO draw command such as glDrawElements or
  glMultiDrawElements.

* Thus, although there will be (for example) the same radius for all parts of a
  sphere, it is replicated in the radius attribute array for all of the block of
  vertices of the polygonal GL object that is drawn to cover the shader sphere
  primitive.

* For dynamic allocation of drawing primitives, it's best to pre-allocate VBO
  arrays in largish fixed-sized hunks for each primitive type and dole them out
  individually.  10,000 primitives may be a good VBO hunk size to use at first,
  minimizing the number of per-hunk draw calls.

== IBOs ==

* IBOs (Index Buffer Objects) in graphics card RAM contain subscripts into the
  blocks of per-vertex data so that a large batch of allocated primitives may be
  drawn in one graphics call.  One call will be needed for each hunk of
  primitives of a given type.

* The indexed vertices make up a pattern of faces for each primitive (likely
  quads, triangles, or triangle-strips.)  This is fast because it gets to
  transform and shade the vertices of a primitive in the graphics pipeline once,
  and re-use them for all of the faces that use the same vertex.

== GlPrimitiveBuffer ==

* GLPrimitiveBuffer (through subtypes such as GLSphereBuffer) manages the data
  for a collection of hunks of objects of a particular primitive type.

* It caches the Python (and possibly C/Numpy) numeric value arrays for each VBO,
  as well as a set of OpenGL handles in GLBufferObjects for accessing the VBO
  arrays (each one divided into hunks) in graphics card RAM.

* Allocating a drawing primitive gives it a fixed vertex block ID that never
  changes.

* The vertex block ID is an integer but not a subscript.  It determines both the
  hunk number, and the offsets within the various VBO hunks to the blocks of
  vertex data for the primitive.

* A vertex block contains data for a small sequence of vertices (e.g. a shader
  bounding box, tetrahedron, or billboard) that is the drawing pattern used to
  draw the primitive.

* All vertex blocks for a given type are in 'unit' coordinates and are
  identical, so there is a common VBO for all hunks of vertices for primitives
  of a particular type.

* Similarly, there is a common IBO for all hunks of indices for primitives of a
  particular type.  Each copy of the vertex subscripting pattern is offset by
  adding the vertex block base subscript to all of the index values in the
  block.

* The data for each primitive goes in a block of per-vertex attributes used by
  the shader programs.  Each attribute memory slot contains four floating-point
  values.  sphere primitives use only one slot: center point X, Y, Z coordinates
  with the radius in the W value.

* Primitive block data values can be updated individually or in batches within a
  hunk-sized VBO array.

* Primitive blocks may be deallocated and re-used quickly in groups, such as by
  a CSDL while regenerating the appearance of an NE1 model object.

* Optimization: It's easy to monitor changes to the Python copy of a VBO hunk by
  keeping the low- and high-change subscripts.  The before-drawing sync can send
  only the modified part of each hunk to a VBO sub-range in the graphics card
  RAM, or do nothing if there have been no changes.

* During drawing, the per-primitive-type vertex shader program combines the unit
  primitive vertex coordinates from the vertex VBO with the primitive location
  (e.g. center point and radius.) The result is transformed into global modeling
  coordinates through the TransformControl matrix referred to by the
  transform_id attribute.

* Any subset of the primitives in a particular VBO hunk can be drawn very
  quickly with a single glMultiDrawElements call, using the IBO indices managed
  by GLPrimitiveSets.

* Any subset of primitives in the whole model can be drawn very quickly with a
  small number of glMultiDrawElements calls, no more than the number of active
  allocation hunks of each primitive type that needs to be drawn.
"""
import graphics.drawing.drawing_globals as drawing_globals
from gl_buffers import GLBufferObject

import numpy

from OpenGL.GL import GL_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import GL_ELEMENT_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_QUADS
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_TEXTURE_2D
#from OpenGL.GL import GL_TEXTURE0
from OpenGL.GL import GL_UNSIGNED_INT
from OpenGL.GL import GL_VERTEX_ARRAY

#from OpenGL.GL import glActiveTexture
from OpenGL.GL import glBindTexture
from OpenGL.GL import glDisable
from OpenGL.GL import glDisableClientState
from OpenGL.GL import glDrawElements
from OpenGL.GL import glEnable
from OpenGL.GL import glEnableClientState
from OpenGL.GL import glVertexPointer

#from OpenGL.GL.ARB.shader_objects import glUniform1iARB

from OpenGL.GL.ARB.vertex_program import glDisableVertexAttribArrayARB
from OpenGL.GL.ARB.vertex_program import glEnableVertexAttribArrayARB
from OpenGL.GL.ARB.vertex_program import glVertexAttrib1fARB
from OpenGL.GL.ARB.vertex_program import glVertexAttrib3fARB
from OpenGL.GL.ARB.vertex_program import glVertexAttribPointerARB

# Constants.
HUNK_SIZE = 5000 # 10000 # 20000   # The number of primitives in each VBO hunk.
BYTES_PER_FLOAT = 4             # All per-vertex attributes are floats in GLSL.

class GLPrimitiveBuffer(object):
    """
    Manage VBO space for drawing primitives in large batches.
    """
    def __init__(self, drawingMode, vertexBlock, indexBlock):
        """
        Fill in the vertex VBO and IBO drawing pattern for this primitive type.

        drawingMode - What kind of primitives to render, e.g. GL_QUADS.

        vertexBlock, indexBlock - Single blocks (lists) of vertices and indices
        making up the drawing pattern for this primitive.
        See description in the file docstring.
        """
        # Shared data for drawing calls to follow.
        self.drawingMode = drawingMode

        # Remember the drawing pattern.  (We may want to make transformed vertex
        # blocks someday, losing the one-hunk-per-type goodness in favor of some
        # other greater goodness like minimizing use of constant registers.)
        # See below for filling the vertex VBO and IBO with these.
        self.nVertices = len(vertexBlock)
        self.vertexBlock = vertexBlock
        self.indexBlock = indexBlock

        # Allocation of primitives within hunks.
        self.nPrims = 0             # Number of primitives allocated.
        self.freePrimSlotIDs = []   # Free list of freed primitives.
        self.nHunks = 0             # Number of hunks allocated.

        # Common per-vertex attribute hunk VBOs for all primitive types.
        # (The hunkVertVBO and hunkIndexIBO are shared by all hunks.)
        self.colorHunks = HunkBuffer("color", self.nVertices, 4)
        self.transform_id_Hunks = HunkBuffer("transform_id", self.nVertices, 1)
        # Subclasses may add their own attributes to the hunkBuffers list.
        self.hunkBuffers = [self.colorHunks, self.transform_id_Hunks]

        # Support for lazily updating drawing caches, namely a timestamp showing
        # when this GLPrimitiveBuffer was last flushed to graphics card RAM.
        self.flushed = drawing_globals.NO_EVENT_YET

        # Fill in shared data in the graphics card RAM.
        self._setupSharedVertexData()

        # Cached info for blocks of transforms.
        # Transforms here are lists (or Numpy arrays) of 16 numbers.
        self.transforms = []
        self.identityTransform = ([1.0] + 4*[0.0]) * 3 + [1.0]

        return

    def color4(self,color):
        """
        Minor helper function for colors.  Converts a given (R, G, B) 3-tuple to
        (R, G, B, A) by adding an opacity of 1.0 .
        """
        if len(color) == 3:
            # Add opacity to color if missing.
            color = (color[0], color[1], color[2], 1.0)
            pass
        return color

    def newPrimitives(self, n):
        """
        Allocate a group of primitives. Returns a list of n IDs.
        """
        primIDs = []
        for i in range(n):
            # Take ones from the free list first.
            if len(self.freePrimSlotIDs):
                primID = self.freePrimSlotIDs.pop()
            else:
                # Allocate a new one.
                primID = self.nPrims     # ID is a zero-origin subscript.
                self.nPrims += 1        # nPrims is a counter.

                # Allocate another set of hunks if the new ID has passed a hunk
                # boundary.
                if (primID + HUNK_SIZE) / HUNK_SIZE > self.nHunks:
                    for buffer in self.hunkBuffers:
                        buffer.addHunk()
                        continue
                    self.nHunks += 1
                pass
            primIDs += [primID]
            continue
        return primIDs

    def releasePrimitives(self, idList):
        """
        Release the given primitive IDs into the free-list.
        """
        self.freePrimSlotIDs += idList
        return

    def _setupSharedVertexData(self):
        """
        Gather data for the drawing pattern Vertex and Index Buffer Objects
        shared by all hunks of the same primitive type.  The drawing pattern is
        replicated HUNK_SIZE times and sent to graphics card RAM for use in
        every draw command for collections of primitives of this type.
        
        In theory, the vertex shader processes each vertex only once, even if
        it is indexed many times in different faces within the same draw.  In
        practice, locality of vertex referencing in the drawing pattern is
        optimal, since there may be a cache of the most recent N transformed
        vertices in that stage of the drawing pipeline on graphics card.
        
        For indexed gl(Multi)DrawElements, the index is a list of faces
        (typically triangles or quads, specified by the drawingMode.)  Each
        face is represented by a list of subscripts into the vertex block.
        """
        self.nIndices = len(self.indexBlock) * len(self.indexBlock[0])
        indexOffset = 0
        # (May cache these someday.  No need now since they don't change.)
        Py_iboIndices = []
        Py_vboVerts = []
        for i in range(HUNK_SIZE):
            # Accumulate a hunk full of blocks of vertices.  Each block is
            # identical, with coordinates relative to its local primitive
            # origin.  Hence, the vertex VBO may be shared among all hunks of
            # primitives of the same type.  A per-vertex attribute gives the
            # spatial location of the primitive origin, and is combined with the
            # local vertex coordinates in the vertex shader program.
            Py_vboVerts += self.vertexBlock

            # Accumulate a hunk full of index blocks, offsetting the indices in
            # each block to point to the vertices for the corresponding
            # primitive block in the vertex hunk.
            for face in self.indexBlock:
                Py_iboIndices += [idx + indexOffset for idx in face]
                continue
            indexOffset += self.nVertices
            continue

        # Push shared vbo/ibo hunk data through C to the graphics card RAM.
        C_vboVerts = numpy.array(Py_vboVerts, dtype=numpy.float32)
        self.hunkVertVBO = GLBufferObject(
            GL_ARRAY_BUFFER_ARB, C_vboVerts, GL_STATIC_DRAW)
        self.hunkVertVBO.unbind()
        
        C_iboIndices = numpy.array(Py_iboIndices, dtype=numpy.uint32)
        self.hunkIndexIBO = GLBufferObject(
            GL_ELEMENT_ARRAY_BUFFER_ARB, C_iboIndices, GL_STATIC_DRAW)
        self.hunkIndexIBO.unbind()

        return

    def draw(self, primIdSet = None):
        """
        Draw the buffered geometry, binding vertex attribute values for the
        shaders.

        If no primIdSet is given, the whole array is drawn.
        """
        shader = drawing_globals.sphereShader
        shader.use(True)             # Turn on the sphere shader.

        glEnableClientState(GL_VERTEX_ARRAY)

        # XXX No transform data until that is more implemented.
        ###shader.setupTransforms(self.transforms)
        if shader.get_texture_xforms():
            # Activate a texture unit for transforms.
            ## XXX Not necessary for custom shader programs.
            ##glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.transform_memory)

            # Set the sampler to the handle for the active texture image (0).
            ## XXX Not needed if only one texture is being used?
            ##glActiveTexture(GL_TEXTURE0)
            ##glUniform1iARB(shader.uniform("transforms"), 0)
            pass        

        glDisable(GL_CULL_FACE)

        # Draw the hunks.
        for hunkNumber in range(self.nHunks):
            # Bind the per-vertex generic attribute arrays for one hunk.
            for buffer in self.hunkBuffers:
                buffer.flush()      # Sync graphics card copies of the VBO data.
                buffer.bindHunk(hunkNumber)
                continue

            # Shared vertex coordinate data VBO: GL_ARRAY_BUFFER_ARB.
            self.hunkVertVBO.bind()
            glVertexPointer(3, GL_FLOAT, 0, None)

            # XXX Temporary code -- For initial tests, draw all primitives.
            # glMultiDrawElements on the GLPrimitiveSet goes here.
            if hunkNumber < self.nHunks-1:
                nToDraw = HUNK_SIZE # Hunks before the last.
            else:
                nToDraw = self.nPrims - (self.nHunks-1) * HUNK_SIZE
            # Shared vertex index data IBO: GL_ELEMENT_ARRAY_BUFFER_ARB
            self.hunkIndexIBO.bind()
            glDrawElements(GL_QUADS, self.nIndices * nToDraw,
                       GL_UNSIGNED_INT, None)

        shader.use(False)            # Turn off the sphere shader.
        glEnable(GL_CULL_FACE)

        self.hunkIndexIBO.unbind()   # Deactivate the ibo.
        self.hunkVertVBO.unbind()    # Deactivate all vbo's.

        glDisableClientState(GL_VERTEX_ARRAY)
        for buffer in self.hunkBuffers:
            buffer.unbindHunk()      # glDisableVertexAttribArrayARB.
            continue
        return

    pass # End of class GLPrimitiveBuffer.

class HunkBuffer:
    """
    Helper class to manage updates to Vertex Buffer Objects for groups of
    fixed-size HUNKS of per-vertex attributes in graphics card RAM.
    """
    def __init__(self, attribName, nVertices, nCoords):
        """
        Allocate a Buffer Object for the hunk, but don't fill it in yet.

        attribName - String name of an attrib variable in the vertex shader.

        nVertices - The number of vertices in the primitive drawing pattern.

        nCoords - The number of coordinates per attribute (e.g. 1 for float, 3
        for vec3, 4 for vec4), so the right size storage can be allocated.
        """
        self.attribName = attribName
        self.nVertices = nVertices
        self.nCoords = nCoords

        self.hunks = []

        # Look up the location of the named generic vertex attribute in the
        # previously linked shader program object.
        shader = drawing_globals.sphereShader
        self.attribLocation = shader.attribute(attribName)

        # Cache the Python data that will be sent to the graphics card RAM.
        # Internally, the data is a list, block-indexed by primitive ID, but
        # replicated in block sublists by a factor of self.nVertices to match
        # the vertex buffer.  What reaches the attribute VBO is automatically
        # flattened into a sequence.
        self.data = []

        return

    def addHunk(self):
        """
        Allocate a new hunk VBO when needed.
        """
        hunkNumber = len(self.hunks)
        self.hunks += [Hunk(hunkNumber, self.nVertices, self.nCoords)]
        return

    def bindHunk(self, hunkNumber):
        glEnableVertexAttribArrayARB(self.attribLocation)
        self.hunks[hunkNumber].VBO.bind()
        glVertexAttribPointerARB(self.attribLocation, self.nCoords,
                                 GL_FLOAT, 0, 0, None)
        return

    def unbindHunk(self):
        glDisableVertexAttribArrayARB(self.attribLocation)
        return

    def setData(self, primID, value):
        """
        Add data for a primitive.  The ID will always be within the array, or
        one past the end when allocating new ones.

        primID - In Python, this is just a subscript.
        value - The new data.
        """

        # Internally, the data is a list, block-indexed by primitive ID, but
        # replicated in block sublists by a factor of self.nVertices to match
        # the vertex buffer size.  What reaches the attribute VBO is
        # automatically flattened into a sequence of floats.
        replicatedValue = self.nVertices * [value]

        if primID >= len(self.data):
            assert primID == len(self.data)
            self.data += [replicatedValue]
        else:
            assert primID >= 0
            self.data[primID] = replicatedValue
            pass
        self.changedRange(primID, primID+1)
        return

    # Maybe a range setter would be useful, too:
    # def setDataRange(self, primLow, primHigh, valueList):

    def changedRange(self, chgLowID, chgHighID):
        """
        Record a range of data changes, for later flushing.

        chgLowID and chgHighID are primitive IDs, possibly spanning many hunks.

        The high end is the index of the one *after* the end of the range, as
        usual in Python.

        Just passes it on to the relevant hunks for the range.
        """
        (lowHunk, highHunk) = (chgLowID / HUNK_SIZE, chgHighID / HUNK_SIZE)
        for hunk in self.hunks[lowHunk:highHunk+1]:
            hunk.changedRange(chgLowID, chgHighID)
            continue
        return

    def flush(self):
        """
        Update a changed range of the data, sending it to the Buffer Objects in
        graphics card RAM.

        This level just passes the flush() on to the Hunks.
        """
        for hunk in self.hunks:
            hunk.flush(self.data)

    pass # End of class HunkBuffer.

class Hunk:
    """
    Helper class to wrap low-level VBO objects with data caches, change ranges,
    and flushing of the changed range to the hunk VBO in graphics card RAM.
    """
    def __init__(self, hunkNumber, nVertices, nCoords):
        """
        hunkNumber - The index of this hunk, e.g. 0 for the first in a group.
        Specifies the range of IDs residing in this hunk.
        
        nVertices - The number of vertices in the primitive drawing pattern.

        nCoords - The number of entries per attribute, e.g. 1 for float, 3 for
        vec3, 4 for vec4, so the right size storage can be allocated.
        """
        self.nVertices = nVertices
        self.hunkNumber = hunkNumber
        self.nCoords = nCoords

        self.VBO = GLBufferObject(
            GL_ARRAY_BUFFER_ARB,
            # Per-vertex attributes are all multiples (1-4) of Float32.
            HUNK_SIZE * self.nVertices * self.nCoords * BYTES_PER_FLOAT,
            GL_STATIC_DRAW)

        # Low- and high-water marks to optimize for sending a range of data.
        self.unchanged()
        return

    def unchanged(self):
        """
        Mark a Hunk as unchanged.  (Empty or flushed.) 
        """
        self.low = self.high = 0
        return

    def changedRange(self, chgLowID, chgHighID):
        """
        Record a range of data changes, for later flushing.

        chgLowID and chgHighID are primitive IDs, possibly spanning many hunks.

        The high end is the index of the one *after* the end of the range, as
        usual in Python.
        """
        (lowHunk, lowIndex) = (chgLowID / HUNK_SIZE, chgLowID % HUNK_SIZE)
        (highHunk, highIndex) = (chgHighID / HUNK_SIZE, chgHighID % HUNK_SIZE)

        if self.hunkNumber < lowHunk or self.hunkNumber > highHunk:
            return              # This hunk is not in the hunk range.

        if lowHunk < self.hunkNumber:
            self.low = 0
        else:
            self.low = min(self.low, lowIndex) # Maybe extend the range.
            pass

        if highHunk > self.hunkNumber:
            self.high = HUNK_SIZE
        else:
            self.high = max(self.high, highIndex) # Maybe extend the range.
            pass

        return

    def flush(self, allData):
        """
        Update a changed range of the data that applies to this hunk, sending it
        to the Buffer Object in graphics card RAM.

        allData - List of data blocks for the whole hunk-list.  We'll extract
        just the part relevant to the changed part of this particular hunk.

        Internally, the data is a list, block-indexed by primitive ID, but
        replicated in block sublists by a factor of self.nVertices to match the
        vertex buffer size.  What reaches the attribute VBO is automatically
        flattened into a sequence.
        """
        rangeSize = self.high - self.low
        assert rangeSize >= 0
        if rangeSize == 0:
            # Nothing to do.
            return
        
        lowID = (self.hunkNumber * HUNK_SIZE) + self.low
        highID = (self.hunkNumber * HUNK_SIZE) + self.high

        # Send all or part of the Python data to C.
        C_data = numpy.array(allData[lowID:highID], dtype=numpy.float32)

        if rangeSize == HUNK_SIZE:
            # Special case to send the whole Hunk's worth of data.
            self.VBO.updateAll(C_data)
        else:
            # Send a portion, with a byte offset within the VBO.
            offset = self.low * self.nVertices * self.nCoords * BYTES_PER_FLOAT
            self.VBO.update(offset, C_data)
            pass

        self.unchanged()             # Now we're in sync.
        return
            
    pass # End of class HunkBuffer.

