# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
draw_bond_cyls.py

part of drawing code for higher-order bonds --
represent double bonds with two cylinders, aromatic bonds with banded cylinders, etc.

$Id$

History:

050725 started by bruce, but the plan is to put in just barely enough to make it
obvious how it can be filled out & completed by Huaicai & Mark.
'''
__authors__ = ['bruce',] # and maybe more


#######@@@@@@@ needs cvs add


# many of these imports are not needed
from VQT import V, dot, cross, vlen, norm
from VQT import pi, acos
import platform
from debug import print_compact_traceback, print_compact_stack

from constants import TubeRadius, blue, gray, black, white
CPKRadius = 0.1 # hardcoded in Bond.draw; should be in constants ##e ###@@@ not yet used here
from math import ceil

from OpenGL.GL import *

from bond_constants import *
from drawer import drawcylinder


def draw_bond_cyls(bond, glpane, sigmabond_cyl_radius, col):
    """Given a bond which is not a single bond, draw it as one or more cylinders or banded cylinders.
    """
    print "draw bond cyls nim"
    del glpane
    res = bond.get_pi_info()
    if res is not None:
        ((a1py, a1pz), (a2py, a2pz), ord_pi_y, ord_pi_z) = res # vectors are in bond's coordsys
        # we could use ord_pi_y, ord_pi_z, but it's probably more straightforward to just use bond.v6.
        v6 = bond.v6
        if v6 == V_DOUBLE:
            drawcylinder
        
        rad = sigmabond_cyl_radius
        
    return

def draw_vane( bond, a1p, a2p, ord_pi, rad, prefs = {}):
    """draw a vane (extending on two opposite sides of the bond axis) [#doc more];
    use ord_pi to determine how intense it is (not yet sure how, maybe by mixing in bgcolor??);
    a1p and a2p should be unit vectors perp to bond and no more than 90 degrees apart when seen along it;
    they should be in the bond's coordinate system.
    rad is inner radius of vanes, typically the cylinder radius for the sigma bond graphic.
    """
    from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
    twisted = debug_pref('pi vanes/ribbons', Choice_boolean_False)
    poles = debug_pref('pi vanes/poles', Choice_boolean_True)
    draw_normals = debug_pref('pi vanes/draw normals', Choice_boolean_False)
    if twisted:
        d12 = dot(a1p, a2p)
        ## assert d12 >= 0.0
        if d12 < 0.0:
            d12 = 0.0
        if d12 > 1.0:
            d12 = 1.0
        twist = acos(d12) # in radians
            # this is numerically inaccurate (since d12 is) near d12 == 1.0, but that's ok,
            # since it's only compared to threshholds (by ceil()) which correspond to d12 values not near 1.0.
            # (#e btw, we could optim the common case (ntwists == 1) by inverting this comparison to get
            #  the equivalent threshhold for d12.)
        maxtwist = prefs.get('maxtwist',MAXTWIST)
        ntwists = max(1, int( ceil( twist / maxtwist ) )) # number of segments needed, to limit each segment's twist to MAXTWIST
    from handles import ave_colors
    ord_pi_for_color = 0.5 # was ord_pi
    color = ave_colors(ord_pi_for_color, blue, gray) #stub; args are: weight, color for weight 1.0, color for weight 0.0
    color = ave_colors(0.8, color, black) #e optim: move outside
##    a1pos = bond.atom1.posn()
##    a2pos = bond.atom2.posn()
    a1pos, c1, center, c2, a2pos, toolong = bond.geom
    if not toolong:
        c1 = c2 = center # don't know if needed
    x_axis = a2pos - a1pos
    if 0 and ord_pi == 1.0: # disable this special case optim for now [or forever if we want to put black outlines on vanes] ###@@@
        radius_pairs = [(- 2.5, 2.5)] # units are multiples of rad (e.g. TubeRadius, but passed by caller)
        ###@@@ if this case is ever used, we need to revise the lines code below to draw two lines not one, between corners of quads;
        # and the direction re lighting (as it affects poygon winding order) must also be reviewed.
    else:
        # from 1 to 2.5, with 1 moved out to shrink width according to ord_pi
        width = 1.5 * ord_pi
        inner, outer = 2.5 - width, 2.5
        radius_pairs = [(outer, inner), (-inner, -outer)]
            # the order within each pair matters, since it affects the polys drawn below being CW or CCW!
    # OpenGL code
    #e could optim this to use Numeric calcs and OpenGL vertex array,
    #  with vertex normals and smooth shading, maybe even color ramp of some kind...
    #e want polygon outlines?
    #e want a 1d texture to emphasize the vane's ribbonness & help show ord_pi?
    glDisable(GL_CULL_FACE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color) # gl args partly guessed #e should add specularity, shininess...
    glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
        # For vane lighting to be correct, two-sided polygon lighting is required,
        # and every polygon's vertex winding order (CCW) has to match its normal vector,
        # as both are produced by the following code. This means that any changes to the
        # orders of lists of vertices or vectors in this code have to be considered carefully.
        # But it's ok if a1p and a2p are negated (fortunately, since calling code arbitrarily negates them),
        # since this reverses the poly scan directions in two ways at once (e.g. via pvec and perpvec in the quads case below).
        # (For ribbon option, it's only ok if they're negated together; for quads case, independent negation is ok.
        #  I'm pretty sure calling code only negates them together.)
        # [bruce 050725]
    if draw_normals:
        normals = []
    for outer, inner in radius_pairs:
        if twisted:
            glBegin(GL_TRIANGLE_STRIP)
            for i in range(1+ntwists):
                t = float(i) / ntwists # 0.0 to 1.0
                _1mt = 1.0 - t # one minus t (python syntax doesn't let me name it just 1mt)
                axispos = _1mt * a1pos + t * a2pos #e could optimize, not sure it matters
                pvec = _1mt * a1p + t * a2p # let it get smaller in the middle for large twist (rather than using angles in calc)
                    # (rationale: shows weakness of bond. real reason: programmer is in a hurry.)
                    #e btw, it might be better to show twist by mismatch of larger rectangular vanes, in the middle; and it's faster to draw.
                ## pvec *= (rad * 2.5) # could also "* ord_pi" rather than using color, if we worked out proper min radius
                perpvec = norm(cross(x_axis, pvec))
                glNormal3fv( perpvec) # test shows this is needed not only for smoothness, but to make the lighting work at all
                glVertex3fv( axispos + pvec * rad * outer)
                ## glNormal3fv( perpvec) # not needed, since the same normal as above
                glVertex3fv( axispos + pvec * rad * inner)
                #e color? want to smooth-shade it using atom colors, or the blue/gray for bond order, gray in center?
                if draw_normals:
                    normals.append(( axispos + pvec * rad * outer, perpvec ))
            glEnd()
        else:
            glBegin(GL_QUADS)
            for axispos, axispos_c, pvec, normalfactor in [(a1pos,c1,a1p,-1), (a2pos,c2,a2p,1)]:
                perpvec = norm(cross(x_axis, pvec)) * normalfactor
                glNormal3fv( perpvec)
                glVertex3fv( axispos   + pvec * rad * inner)
                glVertex3fv( axispos   + pvec * rad * outer)
                glVertex3fv( axispos_c + pvec * rad * outer) # this is the corner we connect by a line
                glVertex3fv( axispos_c + pvec * rad * inner)
                if draw_normals:
                    normals.append(( axispos/2.0 + axispos_c/2.0 + pvec * rad * outer, perpvec ))
            glEnd()
            # and connect the halves of each vane, so that twist doesn't make them look like 2 vanes
            glBegin(GL_LINES)
            glColor3fv(color)
            for axispos, axispos_c, pvec in [(a1pos,c1,a1p), (a2pos,c2,a2p)]:
                glVertex3fv( axispos_c + pvec * rad * outer)
            glEnd()
        if poles:
            glBegin(GL_LINES)
            glColor3fv(color)
            for axispos, pvec in [(a1pos,a1p), (a2pos,a2p)]:
                glVertex3fv( axispos + pvec * rad *  outer)
                glVertex3fv( axispos + pvec * rad * -outer)
            glEnd()
        if draw_normals:
            glBegin(GL_LINES)
            glColor3fv(white)
            for base, vec in normals:
                glVertex3fv(base)
                glVertex3fv(base + vec)
            glEnd()
    glEnable(GL_CULL_FACE)
    glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
    return

# end
