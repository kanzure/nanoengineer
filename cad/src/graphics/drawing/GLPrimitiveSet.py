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

* Each GLPrimitiveSet caches a drawIndex for glMultiDrawElements, which gives the
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

import graphics.drawing.drawing_globals as drawing_globals
from graphics.drawing.ColorSorter import ColorSortedDisplayList
from graphics.drawing.GLPrimitiveBuffer import GLPrimitiveBuffer
from graphics.drawing.TransformControl import TransformControl

from OpenGL.GL import glPushMatrix, glPopMatrix

class GLPrimitiveSet:
    """
    Cached data structure for rapidly drawing a list of batched primitives
    collected from the CSDLs in a DrawingSet.
    """
    def __init__(self, csdl_list):
        self.CSDLs = csdl_list
        
        # Collect lists of primitives to draw in batches, and those CSDLs with
        # display lists to draw as well.  (A given CSDL may have both.)
        self.primitives = []            # Generalize to a dict of lists?
        self.CSDLs_with_DLs = []
        for csdl in self.CSDLs:
            self.primitives += csdl.spheres
            if len(csdl.per_color_dls) > 0:
                self.CSDLs_with_DLs += [csdl]
                pass
            continue

        self.drawIndex = None           # Generated on demand.

        # Support for lazily updating drawing caches, namely a
        # timestamp showing when this GLPrimitiveSet was created.
        self.created = drawing_globals.eventStamp()

        return

    def draw(self, highlighted = False, selected = False,
             patterning = True, highlight_color = None):
        """
        Draw the cached display.
        """
        # Generate and cache index lists for selective drawing of primitives
        # through glMultiDrawElements().
        spheres = drawing_globals.spherePrimitives
        if len(self.primitives) > 0:
            if True: # False  ## True for indexed drawing, False for unindexed.
                if self.drawIndex is None:
                    self.drawIndex = spheres.makeDrawIndex(self.primitives)
                    pass
                spheres.draw(self.drawIndex)
            else:
                # For initial testing, GLPrimitiveBuffer draws the whole set of
                # sphere primitives using glDrawElements().
                spheres.draw()
                pass
            pass

        # Put TransformControl matrices onto the GL matrix stack if present.
        # Does nothing if the TransformControls all have a tranform of None.
        # (Pushing/popping could be minimized by sorting the cached CSDL's.)
        lastTC = None
        pushed = False
        for csdl in self.CSDLs_with_DLs:
            tc = csdl.transformControl
            if tc is not None and tc != lastTC:
                # Restore matrix stack top to push a different transform.
                if pushed:
                    glPopMatrix()
                    pass

                glPushMatrix()
                pushed = True
                tc.applyTransform()
            elif tc is None and pushed:
                # Back to transformless drawing.
                glPopMatrix()
                pushed = False
                pass
            lastTC = tc


            csdl.draw(highlighted, selected, patterning, highlight_color)
            continue

        if pushed:
            glPopMatrix()
        
        return

    pass # End of class GLPrimitiveSet.
