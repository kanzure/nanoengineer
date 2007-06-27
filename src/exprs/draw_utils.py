# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
draw_utils.py

$Id$

"""

from basic import * # autoreload of basic is done before we're imported

from OpenGL.GL import *

# moved to draw_utils.py, 070130:
##ORIGIN = V(0,0,0)
##DX = V(1,0,0)
##DY = V(0,1,0)
##DZ = V(0,0,1)
##
##ORIGIN2 = V(0.0, 0.0)
##D2X = V(1.0, 0.0)
##D2Y = V(0.0, 1.0)

import platform
# == new LL drawing helpers

def draw_textured_rect(origin, dx, dy, tex_origin, tex_dx, tex_dy):
    """Fill a spatial rect defined by the 3d points (origin, dx, dy)
    with the 2d-texture subrect defined by the 2d points (tex_origin, tex_dx, tex_dy)
    in the currently bound texture object.
    """
    ### WARNING: this function is defined identically in both cad/src/testdraw.py and cad/src/exprs/draw_utils.py. [##e fix]
    glEnable(GL_TEXTURE_2D) 
    glBegin(GL_QUADS)
    glTexCoord2fv(tex_origin) # tex coords have to come before vertices, I think! ###k
    glVertex3fv(origin)
    glTexCoord2fv(tex_origin + tex_dx)
    glVertex3fv(origin + dx)
    glTexCoord2fv(tex_origin + tex_dx + tex_dy)
    glVertex3fv(origin + dx + dy)
    glTexCoord2fv(tex_origin + tex_dy)
    glVertex3fv(origin + dy)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_textured_rect_subtriangle(origin, dx, dy, tex_origin, tex_dx, tex_dy, points): #070404 modified from draw_textured_rect
    """Like draw_textured_rect, but draw only the sub-triangle of the same rect (textured in the same way),
    where the subtriangle has relative 2d vertices as specified inside that rect (treating its own coords as each in [0.0, 1.0]).
       WARNING: depending on the glEnables set up by the caller, the sub-triangle coords might need to be
    in CCW winding order for the triangle to be visible from the front.
    """
    #e could easily generalize API to polygon, and this implem to convex polygon, if desired
    ##e WARNING: this function's name and api are likely to be revised;
    # or we might just replace the whole scheme, using things like Textured(Triangle(...),...) instead,
    # perhaps implemented by telling OpenGL how to compute the texture coords in a wrapper, then just drawing the triangle. 
    assert len(points) == 3
    # and each point should be a V of length 2, or a 2-tuple, with elements convertible to floats -- this is assumed below
    glEnable(GL_TEXTURE_2D) 
    glBegin(GL_TRIANGLES)
    for px, py in points:
        px = float(px)
        py = float(py)        
        glTexCoord2fv(tex_origin + px * tex_dx + py * tex_dy)
        glVertex3fv(origin + px * dx + py * dy)
    glEnd()
    glDisable(GL_TEXTURE_2D)
 
# Ideally we'd modularize the following to separate the fill/color info from the shape-info. (And optimize them.)
# For now they're just demos that might be useful.

def draw_filled_rect(origin, dx, dy, color):
##    print 'draw_filled_rect',(origin, dx, dy, color) #####@@@@@
    glDisable(GL_LIGHTING) # this allows the specified color to work. Otherwise it doesn't work (I always get dark blue). Why???
     # guess: if i want lighting, i have to specify a materialcolor, not just a regular color. (and vertex normals)
    try:
        len(color)
    except:
        print "following exception in len(color) for color = %r" % (color,) # 061212 -- why didn't caller's fix_color catch it? ##k
        raise
    if len(color) == 4:
        glColor4fv(color)
        if 0 and color[3] != 1.0:
            print "color has alpha",color ####@@@@
    else:
        glColor3fv(color)
##    glRectfv(origin, origin + dx + dy) # won't work for most coords! also, ignores Z. color still not working.
    glBegin(GL_QUADS)
    glVertex3fv(origin)
    #glColor3fv(white)#
    glVertex3fv(origin + dx)
    # glColor3fv(white) # hack, see if works - yes!
    #glColor3fv(color)#
    glVertex3fv(origin + dx + dy)
    #glColor3fv(white)#
    glVertex3fv(origin + dy)
    glEnd()
    glEnable(GL_LIGHTING) # should be outside of glEnd! when inside, i got infloop! (not sure that was why; quit/reran after that)

def draw_filled_triangle(origin, dx, dy, color):
    glColor3fv(color)
    glDisable(GL_LIGHTING)
    glBegin(GL_TRIANGLES)
    glVertex3fv(origin)
    glVertex3fv(origin + dx)
    glVertex3fv(origin + dy)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_filled_rect_frame(origin, dx, dy, thickness, color):
    "draw something that looks like a picture frame of a single filled color."
    tx = thickness * norm(dx)
    ty = thickness * norm(dy)
    glColor3fv(color)
    glDisable(GL_LIGHTING)
    glBegin(GL_QUAD_STRIP)
    glVertex3fv(origin)
    glVertex3fv(origin + tx + ty)
    glVertex3fv(origin + dx)
    glVertex3fv(origin + dx - tx + ty)
    glVertex3fv(origin + dx + dy)
    glVertex3fv(origin + dx + dy - tx - ty)
    glVertex3fv(origin + dy)
    glVertex3fv(origin + dy + tx - ty)
    glVertex3fv(origin)
    glVertex3fv(origin + tx + ty)
    glEnd()
    glEnable(GL_LIGHTING)

# end
