# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
drawcompass.py

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

bruce 080910 factored this out of class GLPane's drawcompass method

bruce 081015 put constant parts into a display list (possible speedup),
and created class Compass to make this easier
"""

from utilities.prefs_constants import UPPER_RIGHT
from utilities.prefs_constants import UPPER_LEFT
from utilities.prefs_constants import LOWER_LEFT

from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import GL_PROJECTION

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glLoadIdentity

from OpenGL.GL import glOrtho

from OpenGL.GL import glRotatef
from OpenGL.GL import GL_COLOR_MATERIAL
from OpenGL.GL import glEnable
from OpenGL.GL import glDisable
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import glPolygonMode
from OpenGL.GL import glColorMaterial
from OpenGL.GL import GL_FRONT_AND_BACK, GL_FILL, GL_AMBIENT_AND_DIFFUSE

from OpenGL.GL import glGenLists
from OpenGL.GL import glNewList
from OpenGL.GL import GL_COMPILE
from OpenGL.GL import glEndList
from OpenGL.GL import glCallList

try:
    from OpenGL.GLE import glePolyCone
except:
    print "GLE module can't be imported. Now trying _GLE"
    from OpenGL._GLE import glePolyCone

from PyQt4.Qt import QFont, QString, QColor

import math

# ==

# drawing parameters

# (note: most of them are hardcoded into specific routines)

_P4 = 3.8 # ??? may be used to specify the slant of the arrow head (conical portion).?

# ==

class Compass(object):
    
    def __init__(self, glpane):
        """
        @param glpane: typically a QGLWidget; used only for its methods
                       glpane.qglColor and glpane.renderText.
        
        @warning: the right OpenGL display list context must be current
                  when this constructor is called.
        """
        self.glpane = glpane
        self._compass_dl = glGenLists(1)
        glNewList(self._compass_dl, GL_COMPILE)
        _draw_compass_geometry()
        glEndList()

        self._font = QFont( QString("Helvetica"), 12)

        return
    
    def draw(self,
             aspect,
             quat,
             compassPosition,
             compass_moved_in_from_corner,
             displayCompassLabels
            ):
        """
        Draw the "compass" (the perpendicular colored arrows showing orientation
        of model coordinates) in the specified corner of the GLPane (self.glpane).

        Doesn't assume a specific glMatrixMode; sets it to GL_MODELVIEW on exit.

        Doesn't trash either matrix, but does require enough GL_PROJECTION stack
        depth to do glPushMatrix on it (though the guaranteed depth for that stack
        is only 2).
        """
        glpane = self.glpane
        
        #bruce 050608 improved behavior re GL state requirements and side effects;
        # 050707 revised docstring accordingly.
        #mark 0510230 switched Y and Z colors.
        # Now X = red, Y = green, Z = blue, standard in all CAD programs.
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity() # needed!

        # Set compass position using glOrtho
        if compassPosition == UPPER_RIGHT:
            # hack for use in testmode [revised bruce 070110 when GLPane_overrider merged into GLPane]:
            if compass_moved_in_from_corner:
                glOrtho(-40 * aspect, 15.5 * aspect, -50, 5.5,  -5, 500)
            else:
                glOrtho(-50 * aspect, 3.5 * aspect, -50, 4.5,  -5, 500) # Upper Right
        elif compassPosition == UPPER_LEFT:
            glOrtho(-3.5 * aspect, 50.5 * aspect, -50, 4.5,  -5, 500) # Upper Left
        elif compassPosition == LOWER_LEFT:
            glOrtho(-3.5 * aspect, 50.5 * aspect, -4.5, 50.5,  -5, 500) # Lower Left
        else:
            glOrtho(-50 * aspect, 3.5 * aspect, -4.5, 50.5,  -5, 500) # Lower Right

        glRotatef(quat.angle * 180.0/math.pi, quat.x, quat.y, quat.z)

        glCallList(self._compass_dl)

        ##Adding "X, Y, Z" text labels for Axis. By test, the following code will get
        # segmentation fault on Mandrake Linux 10.0 with libqt3-3.2.3-17mdk
        # or other 3.2.* versions, but works with libqt3-3.3.3-26mdk. Huaicai 1/15/05

        if displayCompassLabels:
            # maybe todo: optimize by caching QString, QColor objects during __init__
            glDisable(GL_LIGHTING)
            glDisable(GL_DEPTH_TEST)
            ## glPushMatrix()
            font = self._font
            glpane.qglColor(QColor(200, 75, 75)) # Dark Red
            glpane.renderText(_P4, 0.0, 0.0, QString("x"), font)
            glpane.qglColor(QColor(25, 100, 25)) # Dark Green
            glpane.renderText(0.0, _P4, 0.0, QString("y"), font)
            glpane.qglColor(QColor(50, 50, 200)) # Dark Blue
            glpane.renderText(0.0, 0.0, _P4 + 0.2, QString("z"), font)
            ## glPopMatrix()
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)

        # note: this leaves ending matrixmode in standard state, GL_MODELVIEW
        # (though it doesn't matter for present calling code; see discussion in bug 727)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        return # from draw
    
    pass # end of class Compass

# ==

def _draw_compass_geometry():
    """
    Do GL state changes and draw constant geometry for compass.
    Doesn't depend on any outside state, so can be compiled
    into an unchanging display list. 
    """
    glEnable(GL_COLOR_MATERIAL)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glDisable(GL_CULL_FACE)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    #ninad 070122 - parametrized the compass drawing. (also added some doc). 
    #Also reduced the overall size of the compass. 

    p1 = -1 # ? start point of arrow cyl? 
    p2 = 3.25 #end point of the arrow cylindrical portion
    p3 = 2.5 #arrow head start point
    p5 = 4.5 # cone tip

    r1 = 0.2 #cylinder radius 
    r2 =0.2
    r3 = 0.2
    r4 = 0.60 #cone base radius

    glePolyCone([[p1,0,0], [0,0,0], [p2,0,0], [p3,0,0], [_P4,0,0], [p5,0,0]],
                [[0,0,0], [1,0,0], [1,0,0], [.5,0,0], [.5,0,0], [0,0,0]],
                [r1,r2,r3,r4,0,0])

    glePolyCone([[0,p1,0], [0,0,0], [0,p2,0], [0,p3,0], [0,_P4,0], [0,p5,0]],
                [[0,0,0], [0,.9,0], [0,.9,0], [0,.4,0], [0,.4,0], [0,0,0]],
                [r1,r2,r3,r4,0,0])

    glePolyCone([[0,0,p1], [0,0,0], [0,0,p2], [0,0,p3], [0,0,_P4], [0,0,p5]],
                [[0,0,0], [0,0,1], [0,0,1], [0,0,.4], [0,0,.4], [0,0,0]],
                [r1,r2,r3,r4,0,0])

    glEnable(GL_CULL_FACE)
    glDisable(GL_COLOR_MATERIAL)

    return

# end
