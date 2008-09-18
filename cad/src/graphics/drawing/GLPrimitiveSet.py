# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPrimitiveSet.py -- Cached data structure for rapidly drawing a set of batched
primitives collected from the CSDLs in a DrawingSet.

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

== GLPrimitiveSet ==

* GLPrimitiveSets are used for drawing sets of primitives from the VBO array
  hunks, using indexed glMultiDrawElements calls.  They are created and cached
  by DrawingSet.draw() from the possibly-large sequences of primitive types and
  IDs contained in the CSDLs in the DrawingSet.

* Each GLPrimitiveSet caches an "index" for glMultiDrawElements, which gives the
  locations and lengths of blocks of indices in a hunk IBO to draw.

* It is generated from the primitive IDs contained in the CSDL's of a
  DrawingSet, and stored as two host-side C/Numpy arrays for the locations and
  lengths.

* Possible optimization: The drawing index could use a separate run of vertices
  for each primitive, allowing the run lengths (always the same constant) to be
  a constant hunk-sized array, whose values all equal the size of an index
  block.

* Possible optimization: Alternately, it may turn out to be faster to compress
  the primitive index into "runs", each consisting of contiguous primitives
  within the hunk.

* If the primitives in a GLPrimitiveSet are in multiple VBO hunks, there will be
  multiple IBO handles in the GLPrimitiveSet.  While drawing, each one gets a
  glMultiDrawElements call, with the relevant VBO hunk arrays enabled in the GL.
"""

from graphics.drawing.ColorSorter import ColorSortedDisplayList
from graphics.drawing.ColorSorter import eventStamp
from graphics.drawing.GLPrimitiveBuffer import GLPrimitiveBuffer

class GLPrimitiveSet:
    """
    Cached data structure for rapidly drawing a list of batched primitives
    collected from the CSDLs in a DrawingSet.
    """
    def __init__(self, csdlList):
        # XXX Initial dummy version, just holds the CSDL list.
        self.CSDLs = csdlList

        # Support for lazily updating drawing caches, namely a
        # timestamp showing when this GLPrimitiveSet was created.
        self.created = eventStamp()

        return

    def draw(self, highlighted = False, selected = False,
             patterning = True, highlight_color = None):
        for csdl in self.CSDLs:
            csdl.draw(highlighted, selected, patterning, highlight_color)
        return

    pass # End of class GLPrimitiveSet.
