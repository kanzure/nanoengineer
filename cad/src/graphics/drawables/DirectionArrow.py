# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
DirectionArrow.py

@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:
ninad 2007-06-12: Created this class (initially) to support the implementation
of 'offset plane' (was created in Plane.py)
ninad 2007-08-20: Split it out of Plane.py into this new file.

TODO:
- Need to implement some grid plane features.
- Plane should be selectable when clicked anywhere inside.
"""

from OpenGL.GL import glPushName
from OpenGL.GL import glPopName
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef
from OpenGL.GL import glPopMatrix

from graphics.drawing.CS_draw_primitives import drawDirectionArrow

from geometry.VQT import V, norm, vlen
from math        import pi
from utilities.constants import gray, orange
from utilities.debug import print_compact_traceback
from graphics.drawables.DragHandler import DragHandler_API
from graphics.drawables.Selobj import Selobj_API

import foundation.env as env


ONE_RADIAN = 180.0 / pi
# One radian = 57.29577951 degrees
# This is for optimization since this computation occurs repeatedly
# in very tight drawning loops. --Mark 2007-08-14


class DirectionArrow(DragHandler_API, Selobj_API):
    """
    The DirectionArrow class provides a 3D direction arrow that can be
    interacted with in the 3D graphics area. The direction arrow object
    is created in its parent class. (class corresponding to self.parent)

    Example: Used to generate a plane offset to the selected plane,
             in the direction indicated by the direction arrow.
             Clicking on the arrow reverses its direction and
             thus the direction of the plane placement.
    """
    def __init__(self, parent, glpane, tailPoint, defaultDirection):
        """
        Creates a direction arrow.

        @param parent: The parent object.
        @type  parent:

        @param glpane: The 3D graphics area object.
        @type  glpane: L{GLPane}

        @param tailPoint: The origin of the arrow.
        @type  tailPoint: V

        @param defaultDirection: The direction of the arrow.
        @type  defaultDirection:
        """
        self.parent = parent
        self.glpane = glpane
        self.tailPoint = tailPoint
        self.direction = defaultDirection
        self.glname = glpane.alloc_my_glselect_name(self) #bruce 080917 revised
        self.flipDirection = False
        self.drawRequested = False

    def setDrawRequested(self, bool_request = False):
        """
        Sets the draw request for drawing the direction arrow.
        This class's draw method is called in the parent class's draw method
        This functions sets the flag that decides whether to draw direction
        arrow (the flag  value is returned using isDrawRequested method.
        @param bool_request: Default is False. (request to draw direction arrow)
        @type  bool_request: bool
        """
        self.drawRequested = bool_request

    def isDrawRequested(self):
        """
        Returns the flag that decides whether to draw the direction arrow.
        @return B{self.drawRequested} (boolean value)
        @rtype  instance variable B{self.drawRequested}
        """
        return self.drawRequested

    def draw(self):
        """
        Draw the direction arrow. (This method is called inside of the
        parent object's drawing code.
        """
        try:
            glPushName(self.glname)
            if self.flipDirection:
                self._draw(flipDirection = self.flipDirection)
            else:
                self._draw()
        except:
            glPopName()
            print_compact_traceback("ignoring exception when drawing handle %r: " % self)
        else:
            glPopName()
        pass

    def _draw(self, flipDirection = False, highlighted = False):
        """ Main drawing code.
        @param flipDirection: This flag decides the direction in which the
               arrow is drawn. This value is set in the leftClick method.
               The default value is 'False'
        @type   flipDirection: bool
        @param highlighted: Decids the color of the arrow based on whether
               it is highlighted. The default value is 'False'
        @type  highlighted: bool

        """

        if highlighted:
            color = orange
        else:
            color = gray

        if flipDirection:
            #@NOTE: Remember we are drawing the arrow inside of the _draw_geometry
            #so its drawing it in the translated coordinate system (translated
            #at the center of the Plane. So we should do the following.
            #(i.e. use V(0,0,1)). This will change if we decide to draw the
            #direction arrow outside of the parent object
            #requesting this drawing.--ninad 20070612
            #Using headPoint = self.tailPoint + V(0,0,1) * 2.0 etc along with
            #the transformation matrix in self.draw_in_abs_coordinate()
            #fixes bug 2702 and 2703 -- Ninad 2008-06-11
            headPoint = self.tailPoint + V(0,0,1) * 2.0
            ##headPoint = self.tailPoint + 2.0 * norm(self.parent.getaxis())
        else:
            headPoint = self.tailPoint - V(0,0,1) * 2.0
            ##headPoint = self.tailPoint - 2.0 * self.parent.getaxis()



        vec = vlen(headPoint - self.tailPoint)
        vec = self.glpane.scale*0.07*vec
        tailRadius = vlen(vec)*0.16

        drawDirectionArrow(color,
                           self.tailPoint,
                           headPoint,
                           tailRadius,
                           self.glpane.scale,
                           flipDirection = flipDirection)

    def draw_in_abs_coords(self, glpane, color):
        """
        Draw the handle as a highlighted object.
        @param glpane: B{GLPane} object
        @type  glpane: L{GLPane}
        @param color: Highlight color
        """
        q = self.parent.quat
        glPushMatrix()
        glTranslatef( self.parent.center[0],
                      self.parent.center[1],
                      self.parent.center[2])
        glRotatef( q.angle * ONE_RADIAN,
                   q.x,
                   q.y,
                   q.z)

        if self.flipDirection:
            self._draw(flipDirection = self.flipDirection,
                       highlighted   = True)
        else:
            self._draw(highlighted   = True)

        glPopMatrix()

    ###=========== Drag Handler interface Starts =============###
    #@TODO Need some documentation. Basically it implements the drag handler
    #interface described in DragHandler.py See also exprs.Highlightable.py
    # -- ninad 20070612
    def handles_updates(self):
        return True

    def DraggedOn(self, event, mode):
        return

    def ReleasedOn(self, selobj, event, mode):
        pass

    # =========== Drag Handler interface Ends =============

    # ============== selobj interface Starts ==============

    #@TODO Need some documentation. Basically it implements the selobj
    # interface mentioned in exprs.Highlightable.py -- ninad 2007-06-12

    def leftClick(self, point, event, mode):
        """
        Left clicking on the DirectionArrow flips its direction.

        @param point: not used for now.
        @type  point: V

        @param event: Left down event.
        @type  event: QEvent

        @param mode: Current mode program is in.
        @type  mode: L{anyMode}
        """
        self.flipDirection = not self.flipDirection
        mode.update_selobj(event)
        mode.o.gl_update()
        return self

    def mouseover_statusbar_message(self):
        """
        Returns the statusbar message to display when the cursor is over the
        direction arrow in the 3D graphics area.

        @return: The statusbar message
        @rtype:  str
        """
        msg1 = "Click on arrow to flip its direction"
        return msg1

    def highlight_color_for_modkeys(self, modkeys):
        return orange

    # Copied Bruce's code from class Highlightable with some mods.
    # Need to see if selobj_still_ok() is needed. OK for now.
    # --Ninad 2007-05-31
    def selobj_still_ok(self, glpane):
        res = self.__class__ is DirectionArrow
        if res:
            our_selobj = self
            glname     = self.glname
            owner      = glpane.assy.object_for_glselect_name(glname)
            if owner is not our_selobj:
                res = False
                # Do debug prints.
                print "%r no longer owns glname %r, instead %r does" \
                      % (self, glname, owner) # [perhaps never seen as of 061121]
                pass
            pass
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self
        return res

        ###============== selobj interface Ends===============###

    pass
