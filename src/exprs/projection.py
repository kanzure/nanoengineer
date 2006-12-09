"""
projection.py - utilities loosely related to setting up the projection matrix

$Id$
"""

from basic import *

from prefs_constants import UPPER_RIGHT, UPPER_LEFT, LOWER_LEFT, LOWER_RIGHT

from OpenGL.GL import *
from OpenGL.GLU import gluPickMatrix

class DelegatingInstanceOrExpr(InstanceOrExpr, DelegatingMixin): pass #e refile if I like it

class DrawInCorner(DelegatingInstanceOrExpr):
    delegate = Arg(Widget2D)
    corner = Arg(int, LOWER_RIGHT) # WARNING: only the default corner works properly yet
    def draw(self):
        # this code is modified from GLPane.drawcompass

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        try:
            glpane = self.env.glpane
            aspect = 1.0 ###WRONG but the cases that use it don't work right anyway; BTW does glpane.aspect exist?
            corner = self.corner
            delegate = self.delegate

            ###e should get glpane to do this for us (ie call a method in it to do this if necessary)
            # (this code is copied from it)
            glselect = glpane.current_glselect
            if glselect:
                print "%r setting up gluPickMatrix" % self
                x,y,w,h = glselect
                gluPickMatrix(
                        x,y,
                        w,h,
                        glGetIntegerv( GL_VIEWPORT ) #k is this arg needed? it might be the default...
                )
            
            if corner == UPPER_RIGHT:
                glOrtho(-50*aspect, 5.5*aspect, -50, 5.5,  -5, 500) # Upper Right
            elif corner == UPPER_LEFT:
                glOrtho(-5*aspect, 50.5*aspect, -50, 5.5,  -5, 500) # Upper Left
            elif corner == LOWER_LEFT:
                glOrtho(-5*aspect, 50.5*aspect, -5, 50.5,  -5, 500) # Lower Left
            else:
                ## glOrtho(-50*aspect, 5.5*aspect, -5, 50.5,  -5, 500) # Lower Right
                ## glOrtho(-50*aspect, 0, 0, 50,  -5, 500) # Lower Right [used now] -- x from -50*aspect to 0, y (bot to top) from 0 to 50
                glOrtho(-glpane.width * PIXELS, 0, 0, glpane.height * PIXELS,  -5, 500)
                    # approximately right for the checkbox, but I ought to count pixels to be sure (note, PIXELS is a pretty inexact number)
            
            offset = (-delegate.bright, delegate.bbottom) # only correct for LOWER_RIGHT
            glTranslatef(offset[0], offset[1], 0)
            delegate.draw()
            
        finally:
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()

        return
    pass

# Will this really work with highlighting? (I mean if delegate contains a Highlightable?)
# NO, because that doesn't save both matrices!
# is it inefficient to make every highlightable save both? YES, so let them ask whether they need to,
# and set a flag here that says they need to (but when we have displists we'll need to say how they should treat that flag,
# unless we're saving the ipath instead, as I presume we will be by then).

# BUT FOR NOW, just always save it, since easier.
