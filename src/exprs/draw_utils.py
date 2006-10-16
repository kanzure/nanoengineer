from basic import * # autoreload of basic is done before we're imported

from OpenGL.GL import *

# == geometry

ORIGIN = V(0,0,0)
DX = V(1,0,0)
DY = V(0,1,0)
DZ = V(0,0,1)

ORIGIN2 = V(0.0, 0.0)
D2X = V(1.0, 0.0)
D2Y = V(0.0, 1.0)

# == new LL drawing helpers

def draw_textured_rect(origin, dx, dy, tex_origin, tex_dx, tex_dy):
    """Fill a spatial rect defined by the 3d points (origin, dx, dy)
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

# Ideally we'd modularize the following to separate the fill/color info from the shape-info. (And optimize them.)
# For now they're just demos that might be useful.

def draw_filled_rect(origin, dx, dy, color):
##    print 'draw_filled_rect',(origin, dx, dy, color) #####@@@@@
    glDisable(GL_LIGHTING) # this allows the specified color to work. Otherwise it doesn't work (I always get dark blue). Why???
     # guess: if i want lighting, i have to specify a materialcolor, not just a regular color. (and vertex normals)
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
