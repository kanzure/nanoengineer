# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
clipping_planes.py -- support OpenGL clipping planes.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
from OpenGL.GL import glEnable
from OpenGL.GL import glClipPlane
from OpenGL.GL import glDisable
from OpenGL.GL import GL_CLIP_PLANE1
from OpenGL.GL import GL_CLIP_PLANE2
from OpenGL.GL import GL_CLIP_PLANE3
from OpenGL.GL import GL_CLIP_PLANE4

from geometry.VQT import V

from exprs.Exprs import list_Expr
from exprs.widget2d import Widget2D
from exprs.attr_decl_macros import Arg, ArgOrOption
from exprs.instance_helpers import InstanceOrExpr
from exprs.__Symbols__ import Anything

def clip_below_y0(y0): #070322 #e refile #e someday make it return a smarter object (ClippingPlane) than just a 4-tuple or Numeric array
    """
    return a 4-coefficient OpenGL clipping plane (red book p.144)
    which displays the half-space defined by y >= y0.
    """
    # Return V(A,B,C,D) where Ax + By + Cz + D >= 0 defines the visible volume.
    # In this case we want y - y0 >= 0 to be visible.
    y0 = float(y0)
        # mainly to verify the type is ok;
        # also to force it to be a pure number, if someday it could have units or be a time-dependent expr or whatever
    return V(0,1,0,-y0)

def clip_to_right_of_x0(x0):
    """
    return a 4-coefficient OpenGL clipping plane (red book p.144)
    which displays the half-space defined by x <= x0.
    """
    # We want x <= x0 to be visible, i.e. x - x0 <= 0, or -x + x0 >= 0.
    x0 = float(x0)
    return V(-1,0,0,+x0)

ClippingPlane = Anything # stub

# GL_CLIP_PLANE_table lists the OpenGL clipping plane objects we are allowed to use, in the order
# in which we should allocate them for our own use. They're in backwards order in this table,
# since other code (in cad/src) tends to use lower numbered planes first, though only plane 0 is
# excluded completely, since only it appears to be used incompatibly (modes.py sometimes enables it
# while drawing the entire model, in jigGLSelect, for motivations that are not clear to me
# [later, 080917: probably to make GL_SELECT more likely to return only the correct object,
#  which matters since it uses the first one rather than figuring out which one to use]).
# [070322; policy subject to revision]

GL_CLIP_PLANE_table = (
    ## GL_CLIP_PLANE5, # update: now used in stereo mode, so exclude it here. [bruce 080917] UNTESTED
    GL_CLIP_PLANE4,
    GL_CLIP_PLANE3,
    GL_CLIP_PLANE2,
    GL_CLIP_PLANE1, # used in class ThumbView -- see above
    ## GL_CLIP_PLANE0, # excluded, as explained above
 )

class Clipped(InstanceOrExpr):
    """
    #doc
    """
    # note: we're not delegating anything.
    # e.g. the best lbox attrs for this are specified by the caller and relate to the planes passed to us.
    thing = Arg(Widget2D)
    planes = ArgOrOption(list_Expr(ClippingPlane))
    def draw(self):
        planes = self.planes
        assert len(planes) <= len(GL_CLIP_PLANE_table), \
               "no more than %d clipping planes are permitted" % \
               len(GL_CLIP_PLANE_table)
            # even if your OpenGL driver supports more -- no sense writing an expr that not everyone can draw!
            #    WARNING: this ignores the issue of nested Clipped constructs!
            # In fact, it assumes nothing in thing or above self uses any clipping planes.
            # (Not merely "assumes no more than 6 in all", because we hardcode which specific planes to use!)
            #    Worse, we don't even detect the error. Fixing the behavior is just as easy
            # (let graphical dynenv (self.env) know which planes are still available to any drawing-kid), so do that instead. ##e
            # Note that we might need to work inside a display list, and therefore we'd need to get the "next plane to use"
            # from an env which stays fixed (or from an env var which is changedtracked), not just from each draw call's caller
            # (i.e. a glpane attr).
        # enable the planes
        for i, plane in zip(range(len(planes)), planes):
            assert len(plane) == 4
            glEnable( GL_CLIP_PLANE_table[i] )
            glClipPlane( GL_CLIP_PLANE_table[i], plane)
        # draw thing
        self.drawkid( self.thing)
        # disable the planes
        for i in range(len(planes)):
            glDisable( GL_CLIP_PLANE_table[i] )
        return
    pass

#e Maybe add something to easily clip to an lbox or Rect, like we do in DraggablyBoxed.

#e Maybe add options to not cull faces in spheres (and other objects), and to draw both sides of the faces.
# These could be turned on here for what we draw (using graphical dynenv).
#
# Even better, if we wanted spheres to look "filled with a solid color"
# (rather than hollow) when they were clipped, we could probably do it like this:
# - draw the regular model, clipped in the usual way
# - for each face of the clip volume (presumed brick-shaped) exposed to the user, draw some of the model again,
#   only including the spheres that intersect the clipping plane,
#   clipping to include only what's outside that face (and "above it" -- i.e. in another brick-shaped region),
#   but in a squished form so that all drawn surfaces are effectively squished almost totally onto the clipping plane.
#   (I'm not sure this works perfectly for all ways spheres can intersect. In fact, I doubt it. It would be more correct
#   to just draw filled circles, but to make them match up at the edges, they need to depend on the exac polyhedron used
#   for the sphere, so they're complicated to compute.)

# end
