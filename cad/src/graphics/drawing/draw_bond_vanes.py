# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
draw_bond_vanes.py -- part of the drawing code for higher-order bonds --
represent pi orbitals as "vanes".

@author: bruce
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""

import math
from numpy.oldnumeric import dot

from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import glDisable
from OpenGL.GL import GL_LIGHT_MODEL_TWO_SIDE
from OpenGL.GL import GL_TRUE
from OpenGL.GL import glLightModelfv
from OpenGL.GL import GL_TRIANGLE_STRIP
from OpenGL.GL import glBegin
from OpenGL.GL import glNormal3fv
from OpenGL.GL import glVertex3fv
from OpenGL.GL import glEnd
from OpenGL.GL import GL_QUADS
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LINES
from OpenGL.GL import glColor3fv
from OpenGL.GL import GL_LINE_STRIP
from OpenGL.GL import glEnable
from OpenGL.GL import GL_FALSE

from geometry.VQT import cross, vlen, norm

import foundation.env as env
from graphics.drawing.gl_lighting import apply_material
from utilities.constants import white
from utilities.prefs_constants import pibondStyle_prefs_key

# permissible twist of one vane segment (5 degrees -- just a guess)
MAXTWIST = 5 * math.pi / 180

def draw_bond_vanes(bond, glpane, sigmabond_cyl_radius, col):
    """
    Given a bond with some pi orbital occupancy (i.e. not a single bond),
    draw some "vanes" representing the pi orbitals.

    DON'T use glpane for .out and .up when arbitrary choices are needed -- use
    coords derived from model-space out and up.
    """
    del glpane
    pi_info = bond.get_pi_info()
    if pi_info is not None:
        # vectors are in bond's coordsys
        ((a1py, a1pz), (a2py, a2pz), ord_pi_y, ord_pi_z) = pi_info
        rad = sigmabond_cyl_radius
        if ord_pi_y:
            #k does this mean pi_vectors retval order is wrong?
            draw_vane( bond, a1py, a2py, ord_pi_y, rad, col)
            pass
        if ord_pi_z:
            # this only happens for triple or carbomeric bonds
            draw_vane( bond, a1pz, a2pz, ord_pi_z, rad, col) 
    return

def draw_vane( bond, a1p, a2p, ord_pi, rad, col ):
    """
    Draw a vane (extending on two opposite sides of the bond axis) [#doc more];
    use ord_pi to determine how intense it is (not yet sure how, maybe by mixing
    in bgcolor??);

    a1p and a2p should be unit vectors perp to bond and no more than 90 degrees
    apart when seen along it; they should be in the bond's coordinate system.

    rad is inner radius of vanes, typically the cylinder radius for the sigma
    bond graphic.

    If col is not boolean false, use it as the vane color; otherwise, use a
    constant color which might be influenced by the pi orbital occupancy.
    """
    from utilities.debug_prefs import debug_pref
    from utilities.debug_prefs import Choice_boolean_True, Choice_boolean_False
    ## twisted = debug_pref('pi vanes/ribbons', Choice_boolean_False)
    # one of ['multicyl','vane','ribbon']
    pi_bond_style = env.prefs[ pibondStyle_prefs_key]
    twisted = (pi_bond_style == 'ribbon')
    poles = debug_pref('pi vanes/poles', Choice_boolean_True)
    draw_outer_edges = debug_pref('pi vanes/draw edges', Choice_boolean_True)
        #bruce 050730 new feature, so that edge-on vanes are still visible
    draw_normals = debug_pref('pi vanes/draw normals', Choice_boolean_False)
    print_vane_params = debug_pref('pi vanes/print params',
                                   Choice_boolean_False)
    if print_vane_params:
        print "draw vane",a1p,vlen(a1p),a2p,vlen(a2p),ord_pi
    if twisted:
        d12 = dot(a1p, a2p)
        ## assert d12 >= 0.0
        if d12 < 0.0:
            d12 = 0.0
        if d12 > 1.0:
            d12 = 1.0
        twist = math.acos(d12) # in radians
            # this is numerically inaccurate (since d12 is) near d12 == 1.0, but
            # that's ok, since it's only compared to threshholds (by ceil())
            # which correspond to d12 values not near 1.0.
            # (#e btw, we could optim the common case (ntwists == 1) by
            #  inverting this comparison to get the equivalent threshhold for
            #  d12.)
        maxtwist = MAXTWIST # debug_pref doesn't yet have a PrefsType for this
        # number of segments needed, to limit each segment's twist to MAXTWIST
        ntwists = max(1, int( math.ceil( twist / maxtwist ) ))
        pass
    if col:
        color = col
    else:
        #bruce 050804: initial test of bond color prefs; inadequate in several
        #  ways ###@@@
        from foundation.preferences import prefs_context
        prefs = prefs_context()
        from utilities.prefs_constants import bondVaneColor_prefs_key
        #k I hope this color tuple of floats is in the correct prefs format
        color = prefs.get(bondVaneColor_prefs_key)
        # protect following code from color being None (which causes bus error,
        # maybe in PyOpenGL)
        assert len(color) == 3
        
        ###@@@ it would be much faster to update this pref (or almost any
        # graphics color pref) if the OpenGL command to set the color was in its
        # own display list, redefined when the redraw starts, and called from
        # inside every other display list that needs it.  Then when you changed
        # it, gl_update would be enough -- the chunk display lists would not
        # need to be remade.
        
        ###@@@ problems include:
        # - being fast enough
        # + dflt should be specified in just one place, and earlier than in this
        #   place, so it can show up in prefs ui before this runs (in fact, even
        #   earlier than when this module is first imported, which might be only
        #   when needed),
        # - existing prefs don't have all the color vars needed (eg no
        #   toolong-highlighted color)
        # - being able to track them only when finally used, not when pulled
        #   into convenience vars before final use -- this might even be an
        #   issue if we precompute a formula from a color-pref, but only count
        #   it as used if that result is used.  (we could decide to track the
        #   formula res as a separate thing, i suppose)
##    a1pos = bond.atom1.posn()
##    a2pos = bond.atom2.posn()
    a1pos, c1, center, c2, a2pos, toolong = bond.geom
    if not toolong:
        c1 = c2 = center # don't know if needed
    x_axis = a2pos - a1pos
    # from 1 to 2.5, with 1 moved out to shrink width according to ord_pi
    width = 1.5 * ord_pi
    inner, outer = 2.5 - width, 2.5
    radius_pairs = [(outer, inner, outer), (-inner, -outer, -outer)]
        # the order within each pair matters, since it affects the polys drawn
        # below being CW or CCW!  but for purposes of edges, we also have to
        # know which one is *really* outer...  thus the third elt (edge_outer)
        # of the tuple.
    # OpenGL code
    #e could optim this to use Numeric calcs and OpenGL vertex array, with
    #  vertex normals and smooth shading, maybe even color ramp of some kind...
    #e want polygon outlines?
    #e want a 1d texture to emphasize the vane's ribbonness & help show ord_pi?
    glDisable(GL_CULL_FACE)
    #bruce 051215 use apply_material(color) instead of glMaterialfv, partly to
    # prevent bug of passing 3-tuple to glMaterialfv, partly to make the vanes
    # appear specular, partly to thereby fix bug 1216 (which was probably caused
    # by not setting specular color here, thus letting it remain from whatever
    # happened to be drawn just before). If we decide vanes should *not* appear
    # specular, we have to actively turn off specular color here rather than
    # ignoring the issue.  One way would be to create and use some new
    # functionality like apply_material(color, specular=False).
    apply_material(color)
    # gl args partly guessed #e should add specularity, shininess...
    ## glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)
    glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
        # For vane lighting to be correct, two-sided polygon lighting is
        # required, and every polygon's vertex winding order (CCW) has to match
        # its normal vector, as both are produced by the following code. This
        # means that any changes to the orders of lists of vertices or vectors
        # in this code have to be considered carefully.  But it's ok if a1p and
        # a2p are negated (fortunately, since calling code arbitrarily negates
        # them), since this reverses the poly scan directions in two ways at
        # once (e.g. via pvec and perpvec in the quads case below).  (For ribbon
        # option, it's only ok if they're negated together; for quads case,
        # independent negation is ok.  I'm pretty sure calling code only negates
        # them together.)  [bruce 050725]
    for outer, inner, edge_outer in radius_pairs:
        normals = []
        edgeverts = []
        if twisted:
            glBegin(GL_TRIANGLE_STRIP)
            for i in range(1+ntwists):
                t = float(i) / ntwists # 0.0 to 1.0
                # one minus t (python syntax doesn't let me name it just 1mt)
                _1mt = 1.0 - t
                #e could optimize, not sure it matters
                axispos = _1mt * a1pos + t * a2pos
                # let it get smaller in the middle for large twist (rather than
                # using angles in calc)
                pvec = _1mt * a1p + t * a2p
                # (rationale: shows weakness of bond. real reason: programmer is
                # in a hurry.)
                    #e btw, it might be better to show twist by mismatch of
                    #  larger rectangular vanes, in the middle; and it's faster
                    #  to draw.
                # Could also "* ord_pi" rather than using color, if we worked
                # out proper min radius.
                ## pvec *= (rad * 2.5)
                perpvec = norm(cross(x_axis, pvec))
                # test shows this is needed not only for smoothness, but to make
                # the lighting work at all
                glNormal3fv( perpvec)
                outervert = axispos + pvec * rad * outer
                innervert = axispos + pvec * rad * inner
                glVertex3fv( outervert)
                ## not needed, since the same normal as above
                ## glNormal3fv( perpvec)
                glVertex3fv( innervert)
                #e color? want to smooth-shade it using atom colors, or the
                #  blue/gray for bond order, gray in center?
                if draw_normals:
                    normals.append(( axispos + pvec * rad * edge_outer,
                                     perpvec ))
                if draw_outer_edges:
                    edgeverts.append( axispos + pvec * rad * edge_outer )
            glEnd()
        else:
            glBegin(GL_QUADS)
            for axispos, axispos_c, pvec, normalfactor in \
                    [(a1pos,c1,a1p,-1), (a2pos,c2,a2p,1)]:
                perpvec = norm(cross(x_axis, pvec)) * normalfactor
                glNormal3fv( perpvec)
                glVertex3fv( axispos   + pvec * rad * inner)
                glVertex3fv( axispos   + pvec * rad * outer)
                glVertex3fv( axispos_c + pvec * rad * outer)
                    # This (axispos_c + pvec * rad * outer) would be the corner
                    # we connect by a line, even when not draw_outer_edges, if
                    # outer == edge_outer -- but it might or might not be.
                glVertex3fv( axispos_c + pvec * rad * inner)
                if draw_normals:
                    normals.append(( axispos/2.0 +
                                       axispos_c/2.0 + pvec * rad * edge_outer,
                                     perpvec ))
                if draw_outer_edges:
                    # Kluge to reverse order of first loop body but not second.
                    edgeverts.reverse()
                    edgeverts.append( axispos_c + pvec * rad * edge_outer)
                    edgeverts.append( axispos   + pvec * rad * edge_outer)
                else:
                    # At least connect the halves of each vane, so that twist
                    # doesn't make them look like 2 vanes.
                    edgeverts.append( axispos_c + pvec * rad * edge_outer)
            glEnd()
##            glBegin(GL_LINES)
##            glColor3fv(color)
##            for axispos, axispos_c, pvec in [(a1pos,c1,a1p), (a2pos,c2,a2p)]:
##                glVertex3fv( axispos_c + pvec * rad * outer)
##            glEnd()
        glDisable(GL_LIGHTING) # for lines... don't know if this matters
        if poles:
            glBegin(GL_LINES)
            glColor3fv(color)
            for axispos, pvec in [(a1pos,a1p), (a2pos,a2p)]:
                glVertex3fv( axispos + pvec * rad *  outer)
                glVertex3fv( axispos + pvec * rad * -outer)
            glEnd()
        if normals:
            glBegin(GL_LINES)
            glColor3fv(white)
            for base, vec in normals:
                glVertex3fv(base)
                glVertex3fv(base + vec)
            glEnd()
        if edgeverts:
            glBegin(GL_LINE_STRIP)
            glColor3fv(color)
            for vert in edgeverts:
                glVertex3fv(vert)
            glEnd()
        glEnable(GL_LIGHTING)
    glEnable(GL_CULL_FACE)
    glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
    return

# end
