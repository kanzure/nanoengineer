# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
GLPrimitiveSet.py -- Cached data structure for rapidly drawing a set of batched
primitives collected from the CSDLs in a DrawingSet, along with any other kind
of drawable content in the CSDLs.

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

import graphics.drawing.drawing_constants as drawing_constants

import graphics.drawing.drawing_globals as drawing_globals

from OpenGL.GL import glPushMatrix, glPopMatrix

class GLPrimitiveSet:
    """
    Cached data structure for rapidly drawing a set of CSDLs.
    It collects their shader primitives (of various kinds),
    color-sorted DLs, and anything else they might have for
    immediate-mode OpenGL drawing (nothing as of 090311), into a
    structure that can be rapidly redrawn multiple times.

    @note: this needs to be remade from scratch if its set of CSDLs,
           or any of its CSDLs' contents or properties, changes.

    @todo: provisions for incremental modification.
    """
    def __init__(self, csdl_list):
        """
        """
        self.CSDLs = csdl_list

        # Collect lists of primitives to draw in batches, and those CSDLs with
        # display lists to draw as well.  (A given CSDL may have both.)
        self.spheres = []            # Generalize to a dict of lists?
        self.cylinders = []
        self._CSDLs_with_nonshader_drawing = []
            #bruce 090312 renamed this from CSDLs_with_DLs,
            # since the logic herein only cares that they have some sort of
            # drawing to do in immediate-mode OpenGL, not how it's done.
            #
            # (todo, in future: split this into whatever can be compiled
            #  into an overall DL of our own (meaning it never changes and
            #  is all legal while compiling a DL -- in particular, it can call
            #  other DLs but it can't recompile them), and whatever really has
            #  to be done in immediate mode and perhaps recomputed on each
            #  draw, as a further optimization. This requires splitting
            #  each of the associated CSDL API methods, has_nonshader_drawing
            #  and .draw(..., draw_shader_primitives = False,
            #                 transform_nonshaders = False ).
            #  If that's done, draw the immediate-mode-parts first here, in case
            #  any of them also want to recompile DLs which are called in the
            #  ok-for-inside-one-big-DL parts.)

        for csdl in self.CSDLs:
            self.spheres += csdl.spheres
            self.cylinders += csdl.cylinders
            if csdl.has_nonshader_drawing():
                self._CSDLs_with_nonshader_drawing += [csdl]
                pass
            continue

        self.drawIndices = {}           # Generated on demand.

        # Support for lazily updating drawing caches, namely a
        # timestamp showing when this GLPrimitiveSet was created.
        self.created = drawing_constants.eventStamp()

        # optimization: sort _CSDLs_with_nonshader_drawing by their transformControl.
        # [bruce 090225]
        items = [(id(csdl.transformControl), csdl)
                 for csdl in self._CSDLs_with_nonshader_drawing]
        items.sort()
        self._CSDLs_with_nonshader_drawing = [csdl for (junk, csdl) in items]

        return

    def draw(self,
             highlighted = False,
             selected = False,
             patterning = True,
             highlight_color = None,
             opacity = 1.0 ):
        """
        Draw the cached display.

        @note: all arguments are sometimes passed positionally.

        @note: opacity other than 1.0 is not yet implemented.
        """
        # Draw shader primitives from CSDLs through shaders
        # (via GLPrimitiveBuffers, one per kind of shader),
        # if that's turned on.
        primlist_buffer_pairs = []
        if self.spheres: # note: similar code exists in CSDL.
            primlist_buffer_pairs += [(self.spheres,
                             drawing_globals.sphereShaderGlobals.primitiveBuffer)]
            pass
        if self.cylinders:
            primlist_buffer_pairs += [(self.cylinders,
                             drawing_globals.cylinderShaderGlobals.primitiveBuffer)]
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

        # Draw just the non-shader drawing (e.g. color-sorted display lists),
        # in all CSDLs which have any.
        # Put TransformControl matrices onto the GL matrix stack when present.
        # (Pushing/popping is minimized by sorting the cached CSDL's earlier.)
        # [algorithm revised by bruce 090203]
        lastTC = None
        for csdl in self._CSDLs_with_nonshader_drawing:
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
            # just draw non-shader stuff, and ignore csdl.transformControl
            csdl.draw( highlighted, selected, patterning, highlight_color,
                       draw_shader_primitives = False,
                       transform_nonshaders = False )
            continue
        if lastTC is not None:
            glPopMatrix()

        return

    pass # end of class GLPrimitiveSet

# end
