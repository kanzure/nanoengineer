# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
draw_utils.py

$Id$

Note: this module does not really belong in the exprs package --
that's its main client, but it contains only pure OpenGL utilities.
"""

from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import glTexCoord2fv
from OpenGL.GL import glColor4fv
from OpenGL.GL import GL_QUADS
from OpenGL.GL import glColor3fv
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glDisable
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import glBegin
from OpenGL.GL import glVertex3fv
from OpenGL.GL import glEnd
from OpenGL.GL import glEnable
from OpenGL.GL import GL_QUAD_STRIP

from OpenGL.GLU import gluUnProject

from geometry.VQT import norm, A
from Numeric import dot

from array import array
# ==

def mymousepoints(glpane, x, y): #bruce 071017 moved this here from testdraw.py
    ### TODO: rename, docstring

    # modified from GLPane.mousepoints; x and y are window coords (except y is 0 at bottom, positive as you go up [guess 070124])
    self = glpane
    just_beyond = 0.0
    p1 = A(gluUnProject(x, y, just_beyond))
    p2 = A(gluUnProject(x, y, 1.0))

    los = self.lineOfSight # isn't this just norm(p2 - p1)?? Probably not, if we're in perspective mode! [bruce Q 061206]
        # note: this might be in abs coords (not sure!) even though p1 and p2 would be in local coords.
        # I need to review that in GLPane.__getattr__. ###k
    
    k = dot(los, -self.pov - p1) / dot(los, p2 - p1)

    p2 = p1 + k*(p2-p1)
    return (p1, p2)

# == new LL drawing helpers

def draw_textured_rect(origin, dx, dy, tex_origin, tex_dx, tex_dy):
    """
    Fill a spatial rect defined by the 3d points (origin, dx, dy)
    with the 2d-texture subrect defined by the 2d points (tex_origin, tex_dx, tex_dy)
    in the currently bound texture object.
    """
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
    """
    Like draw_textured_rect, but draw only the sub-triangle of the same rect (textured in the same way),
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
        glTexCoord2fv((tex_origin + px * tex_dx + py * tex_dy).tolist())
        # glVertex3fv(origin + px * dx + py * dy)
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
    """
    draw something that looks like a picture frame of a single filled color.
    """
    tx = thickness * norm(dx)
    ty = thickness * norm(dy)
    ## glColor3fv(color) ### this has an exception (wants 3 elts, gets 4) in Mac A9.1-rc1
    # (i.e. in the Mac "Gold" PyOpenGL for A9.1), so instead, do the following: [bruce 070703]
    glColor3fv(color[:3])
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
