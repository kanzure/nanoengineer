# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ColorCube.py -- a cube of all RGB colors (though only the surface is visible)

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from geometry.VQT import V

from OpenGL.GL import GL_QUADS
from OpenGL.GL import glBegin
from OpenGL.GL import glColor3f
from OpenGL.GL import glColor3fv
from OpenGL.GL import glVertex
from OpenGL.GL import glVertex3f
from OpenGL.GL import glVertex3fv
from OpenGL.GL import glNormal3fv
from OpenGL.GL import glEnd
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import GL_LIGHTING

from exprs.widget2d import Widget2D

# some data for a cube:

# (todo: rename these to show they are mostly constants, and private)

# axes to use
X = V(1,0,0)
Y = V(0,1,0)
Z = V(0,0,1)

# faces are an axis and a sign, and orientation directions 
# (pay attention to positive area in direction of normal)
faces = [(X,  1,  Y, Z), 
         (X, -1, -Y, Z), 
         (Y,  1,  Z, X), 
         (Y, -1, -Z, X), 
         (Z,  1,  X, Y), 
         (Z, -1, -X, Y)
        ]

def facenormal(face):
    return face[0] * face[1]

def faceverts(face):
    perp1, perp2 = face[2], face[3]
    for signs in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        yield signs[0] * perp1 + signs[1] * perp2 + facenormal(face)
    return

def fix(coord):
    """
    turn a sign into a color component; -1 -> 0, 1 -> 1
    """
    return coord * 0.5 + 0.5

class ColorCube(Widget2D):
    def draw(self):
        glDisable(GL_LIGHTING) # note: the colors here don't work without this
        glBegin(GL_QUADS)
        for face in faces:
            face_normal = facenormal(face)
            for vert in faceverts(face):
                color = (fix(vert[0]), fix(vert[1]), fix(vert[2]))
                glColor3fv(color)
                glNormal3fv(face_normal)
                glVertex3fv(vert)
        glEnd()
        glEnable(GL_LIGHTING)
    pass

# end
