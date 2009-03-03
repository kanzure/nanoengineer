# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPrimitiveSet.py -- Cached data structure for rapidly drawing a set of batched
primitives collected from the CSDLs in a DrawingSet.

@author: Russ
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

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
from graphics.drawing.ColorSortedDisplayList import ColorSortedDisplayList
from graphics.drawing.GLPrimitiveBuffer import GLPrimitiveBuffer
from graphics.drawing.TransformControl import TransformControl

from OpenGL.GL import glPushMatrix, glPopMatrix

class GLPrimitiveSet:
    """
    Cached data structure for rapidly drawing a list of batched primitives
    collected from the CSDLs in a DrawingSet.

    @note: this needs to be remade from scratch if its set of CSDLs,
           or any of its CSDLs' contents or properties, changes.
    """
    def __init__(self, csdl_list):
        self.CSDLs = csdl_list
        
        # Collect lists of primitives to draw in batches, and those CSDLs with
        # display lists to draw as well.  (A given CSDL may have both.)
        self.spheres = []            # Generalize to a dict of lists?
        self.cylinders = []
        self.CSDLs_with_DLs = []
        for csdl in self.CSDLs:
            self.spheres += csdl.spheres
            self.cylinders += csdl.cylinders
            if csdl.has_nonempty_DLs():
                self.CSDLs_with_DLs += [csdl]
                pass
            continue

        self.drawIndices = {}           # Generated on demand.

        # Support for lazily updating drawing caches, namely a
        # timestamp showing when this GLPrimitiveSet was created.
        self.created = drawing_globals.eventStamp()

        # optimization: sort CSDLs_with_DLs by their transformControl.
        # [bruce 090225]
        items = [(id(csdl.transformControl), csdl)
                 for csdl in self.CSDLs_with_DLs]
        items.sort()
        self.CSDLs_with_DLs = [csdl for (junk, csdl) in items]

        return

    def draw(self, highlighted = False, selected = False,
             patterning = True, highlight_color = None, opacity = 1.0):
        """
        Draw the cached display.

        @note: all arguments are sometimes passed positionally.
        """
        # Draw primitives from CSDLs through shaders (via GLPrimitiveBuffers),
        # if that's turned on.
        primlist_buffer_pairs = []
        if drawing_globals.sphereShader_desired():
            primlist_buffer_pairs += [(self.spheres,
                             drawing_globals.spherePrimitives)]
            pass
        if drawing_globals.cylinderShader_desired():
            primlist_buffer_pairs += [(self.cylinders,
                             drawing_globals.cylinderPrimitives)]
            pass
        for primitives, primbuffer in primlist_buffer_pairs:
            if len(primitives) > 0:
                if True: # False ## True: indexed drawing, False: unindexed.
                    # Generate and cache index lists for selective drawing
                    # of primitives through glMultiDrawElements().
                    if primbuffer not in self.drawIndices:
                        self.drawIndices[primbuffer] = primbuffer.makeDrawIndex(primitives)
                        pass
                    # With a drawIndex, draw calls glMultiDrawElements().
                    primbuffer.draw(self.drawIndices[primbuffer], highlighted, selected,
                              patterning, highlight_color, opacity)
                else:
                    # (For initial testing.)  Here GLPrimitiveBuffer draws the
                    # entire set of sphere primitives using glDrawElements().
                    primbuffer.draw()
                    pass
                pass
            continue

        # Draw just the Display Lists, in all CSDLs which have any.
        # Put TransformControl matrices onto the GL matrix stack when present.
        # (Pushing/popping could be minimized by sorting the cached CSDL's.
        #  As of 090025 this is done in __init__.)
        # [algorithm revised by bruce 090203]
        lastTC = None
        for csdl in self.CSDLs_with_DLs:
            tc = csdl.transformControl
            if tc is not lastTC:
                if lastTC is not None:
                    glPopMatrix()
                    pass
                if tc is not None:
                    glPushMatrix()
                    tc.applyTransform()
                    pass
                lastTC = tc
                pass
            csdl.draw(highlighted, selected, patterning, highlight_color,
                      draw_primitives = False, transform_DLs = False)
                # Just draw the DL's, ignoring csdl.transformControl.
            continue
        if lastTC is not None:
            glPopMatrix()
        
        return

    pass # End of class GLPrimitiveSet.
