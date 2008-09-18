# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPrimitiveBuffer.py -- Manage VBO space for drawing primitives in large batches.

@author: Russ
@version: $Id
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

class GLPrimitiveBuffer:
    """
    Manage VBO space for drawing primitives in large batches.
    """
    def __init__(self):
        # The number of primitives to put in each VBO hunk.
        self.hunkSize = 10000
        self.hunks = []
        self.freePrimSlotIDs = []
        return
    
    # ...

    pass # End of class GLPrimitiveBuffer.
