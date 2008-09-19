# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DrawingSet.py -- Top-level API for drawing with batched primitives (spheres,
cylinders, cones) supported by specialized OpenGL shader programs.

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
* GLPrimitiveSet in GLPrimitiveSet.py

== GL context ==

Currently NE1 uses multiple GL contexts, but they all share large GL server
state objects such as display lists, textures and VBOs.

If this ever changes, we'll need an explicit object to manage each separate
context with independent GL server state.

For now (in both prior NE1 code and in this proposal), we use global variables
for this, including a single global pool of CSDLs, TransformControls, and
DrawingSets. This global pool can be considered an implicit singleton object. It
has no name in this proposal.

== CSDL (ColorSortedDisplayList) changes to support the new graphics design ==

* CSDLs are 'filled' or 'refilled' by streaming a set of drawing primitives into
  them.

* Some drawing primitive types are supported by VBO batching in the graphics
  card RAM and shader programs, on some platforms.

* In that case, the drawing primitive types and parameters are now saved by the
  ColorSorter front-end, as well as allocated primitive IDs once they're drawn.

* Other primitive types go down though the ColorSorter into OpenGL Display
  Lists, as before.

== DrawingSet ==

* A DrawingSet holds a set (dictionary) of CSDLs and has a draw() method with
  arguments like CSDL.draw: (highlighted = False, selected = False, patterning =
  True, highlight_color = None).

* CSDLs can be efficiently added to or removed from a DrawingSet.

* Each DrawingSet is allowed to contain an arbitrary subset of the global pool
  of CSDLs. Specifically, it's ok if one CSDL is in more than one DrawingSet,
  and if some but not all the CSDLs in one TransformControl are in one
  DrawingSet.

* A DrawingSet caches a GLPrimitiveSet that consolidates the VBO-implemented
  primitives from the CSDLs, maintaining indices of primitive IDs to selectively
  draw large batches of primitives out of IBO/VBO hunks.

* Optimization: There are several styles of using glMultiDrawElements with these
  indices of primitives that allow drawing arbitrary subsets efficiently in one
  GL call (per VBO hunk, per primitive type).

* CSDLs now contain a change counter that causes (parts of) the GLPrimitiveSet
  indices to be lazily updated before a DrawingSet.draw .

* When CSDLs are refilled, their batched drawing primitives are first freed, and
  then re-allocated in a stable order.
"""

from graphics.drawing.GLPrimitiveSet import GLPrimitiveSet
from graphics.drawing.ColorSorter import ColorSortedDisplayList

class DrawingSet:
    """
    Manage a set of CSDLs to be repeatedly drawn together.
    """
    def __init__(self, csdl_list = None):   # Optional CSDL list.

        # Use the integer IDs of the CSDLs as keys in a dictionary.
        # (The "set" type is not used here, since it was introduced in Python
        # 2.4, and we still support 2.3 could also use id(csdl), but it's easier
        # to understand if we have small integer IDs when debugging.)
        self.CSDLs = dict([(csdl.csdl_id, csdl) for csdl in csdl_list])

        # Cache a GLPrimitiveSet to speed drawing.
        self.primSet = None

    # ==

    # A subset of the set-type API.
    def addCSDL(self, csdl):
        """
        Add a CSDL to the DrawingSet.
        """
        if csdl.csdl_id not in self.CSDLs:
            # Clear the cache when the set is changing.
            self.primSet = None

            self.CSDLs[csdl.csdl_id] = csdl
            pass

        return

    def removeCSDL(self, csdl):
        """
        Remove a CSDL from the DrawingSet.
        Raises KeyError if not present.
        """
        if csdl.csdl_id in self.CSDLs:
            # Clear the cache when the set is changing.
            self.primSet = None
            pass

        del self.CSDLs[csdl.csdl_id]     # May raise KeyError.

        return

    def discardCSDL(self, csdl):
        """
        Discard a CSDL from the DrawingSet, if present.
        No error if it isn't.
        """

        if csdl.csdl_id in self.CSDLs:
            # Clear the cache when the set is changing.
            self.primSet = None

            del self.CSDLs[csdl.csdl_id]
            pass

        return

    # ==

    def draw(self, highlighted = False, selected = False,
             patterning = True, highlight_color = None):
        """
        Draw the set of CSDLs in the DrawingSet.
        """
        # See if any of the CSDLs has changed more recently than the primSet and
        # clear the primSet cache if so.  (Possible optimization: regenerate
        # only some affected parts of the primSet.)
        if self.primSet is not None:
            for csdl in self.CSDLs.itervalues():
                if csdl.changed > self.primSet.created:
                    self.primSet = None
                    break
                continue

        # Lazily (re)generate the primSet when needed for drawing.
        if self.primSet is None:
            self.primSet = GLPrimitiveSet(self.CSDLs.values())
            pass

        # Draw the primitives.
        self.primSet.draw(highlighted, selected, patterning, highlight_color)
        return

    pass # End of class DrawingSet.
