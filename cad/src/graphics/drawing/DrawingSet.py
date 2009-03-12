# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
DrawingSet.py -- Top-level API for drawing with batched primitives (spheres,
cylinders, cones) supported by specialized OpenGL shader programs.

@author: Russ
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

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

class DrawingSet:
    """
    Manage a set of CSDLs to be repeatedly drawn together.

    @note: self.CSDLs is a public member, but readonly for public use.
           It's a dict of our current CSDLs (mapping csdl.csdl_id to csdl),
           modified immediately by our methods which change our set of
           CSDLs.
    """
    def __init__(self, csdl_list = ()):
        """
        @param csdl_list: Optional initial CSDL list.
        """
        
        # Use the integer IDs of the CSDLs as keys in a dictionary.
        #
        # The "set" type is not used here, since it was introduced in Python
        # 2.4, and we still support 2.3.
        #
        # Could also use id(csdl) as keys, but it's easier to understand with
        # small integer IDs when debugging, and runs twice as fast too.
        self.CSDLs = dict([(csdl.csdl_id, csdl) for csdl in csdl_list])
            # client can modify this set later, using various methods

        # Cache a GLPrimitiveSet to speed drawing.
        # This must be reset to None whenever we modify self.CSDLs.
        self._primSet = None

    def destroy(self): #bruce 090218
        self._primSet = None
        self.CSDLs = {}
        return
    
    # ==

    # A subset of the set-type API.
    
    def addCSDL(self, csdl):
        """
        Add a CSDL to the DrawingSet.

        No error if it's already present.

        @see: set_CSDLs, to optimize multiple calls.
        """
        if csdl.csdl_id not in self.CSDLs:
            self.CSDLs[csdl.csdl_id] = csdl
            self._primSet = None
            pass
        return

    def removeCSDL(self, csdl):
        """
        Remove a CSDL from the DrawingSet.
        Raises KeyError if not present.

        @see: set_CSDLs, to optimize multiple calls.
        """
        del self.CSDLs[csdl.csdl_id]     # may raise KeyError
        self._primSet = None
        return

    def discardCSDL(self, csdl): # (note: not presently used)
        """
        Discard a CSDL from the DrawingSet, if present.
        No error if it isn't.
        """
        if csdl.csdl_id in self.CSDLs:
            del self.CSDLs[csdl.csdl_id]
            self._primSet = None
            pass
        return

    # ==

    def set_CSDLs(self, csdldict): #bruce 090226
        """
        Change our set of CSDLs (self.CSDLs) to csdldict,
        which we now own and might modify destructively
        (though the present implem doesn't do that),
        doing necessary invalidations or updates,
        in an optimal way.

        (Both self.CSDLs and csdldict are dictionaries which map
        csdl.csdl_id to csdl, to represent a set of CSDLs.)

        This is faster than figuring out and doing separate calls
        of removeCSDL and addCSDL, but is otherwise equivalent.

        It's allowed for csdldict to be empty. Self is not destroyed
        in that case, though all its CSDLs are removed.

        What we should optimize for: old and new csdldicts are either
        identical, or similar (large and mostly overlapping).
        """
        have = self.CSDLs
        remove = dict(have) # modified below, by removing what we want,
            # thus leaving what we don't want
        add = {} # modified below, by adding what we want but don't have
            # question: is it more efficient to start with all we want,
            # then remove what we already have (usually removing fewer)?
            # in that case we'd start with csdldict, which we own.
            # guess: it's not more efficient, since add is usually smaller
            # than half of want (we assume).
        for csdl_id in csdldict.iterkeys():
            # we want csdl_id; do we have it?
            csdl_if_have = remove.pop(csdl_id, None)
            if csdl_if_have is not None:
                # we want it and already have it -- don't remove it
                # (we're done, since we just popped it from remove)
                # (note that a csdl_id might be 0, so don't do a boolean test)
                pass
            else:
                # we want it but don't have it, so add it
                # (we optim for this set being small, so we don't
                #  iterate over items, but look up csdl instead)
                # (we keep 'add' separate partly so we know whether it's
                #  empty or not. review: whether it's more efficient to
                #  set a flag and store csdl directly into self.CSDLs here.
                #  Note that in future we might have to do more work
                #  to each one we add, so that revision is probably
                #  bad then, even if it's ok now.)
                add[csdl_id] = csdldict[csdl_id]
            continue
        # now remove and add are correct
        if remove:
            for csdl_id in remove.iterkeys():
                del have[csdl_id] # modifies self.CSDLs
            self._primSet = None
        if add:
            have.update(add)
            self._primSet = None
        return
    
    # ==

    def draw(self, highlighted = False, selected = False,
             patterning = True, highlight_color = None, opacity = 1.0):
        """
        Draw the set of CSDLs in the DrawingSet.
        """
        # Note: see similar code in CSDL.draw.

        # note: we do nothing about CSDLs whose transformControl has changed
        # since the last draw. This is not needed
        # when the transformControl is a Chunk, and I won't bother to
        # (re)implement it for now when using deprecated class
        # TransformControl. This will make TCs do nothing in their
        # test cases in test_drawing. [bruce 090223 revision]
                        
        # See if any of the CSDLs has changed (in primitive content, not in
        # transformControl value) more recently than the _primSet and
        # clear the _primSet cache if so.  (Possible optimization: regenerate
        # only some affected parts of the _primSet.)
        if self._primSet is not None:
            for csdl in self.CSDLs.itervalues():
                if csdl.changed > self._primSet.created:
                    self._primSet = None
                    break
                continue
            pass

        # Lazily (re)generate the _primSet when needed for drawing.

        ##### REVIEW: does it copy any coordinates? [i don't think so]
        # if so, fix updateTransform somehow. [bruce 090224 comment]
        
        if self._primSet is None:
            self._primSet = GLPrimitiveSet(self.CSDLs.values())
            pass

        # Draw the shader primitives and the OpenGL display lists.
        self._primSet.draw( highlighted, selected,
                            patterning, highlight_color, opacity)

        return

    pass # end of class DrawingSet

# end
