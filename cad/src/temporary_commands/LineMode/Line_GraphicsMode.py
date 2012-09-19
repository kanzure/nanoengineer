# Copyright 2007-2009 Nanorex, Inc.  See LICENSE file for details.
"""
@author:    Ninad
@version:   $Id$
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

History:
Split this out of LineMode.py (and deprecated that class)


TODOs:
- Refactor/ expand snap code. Should all the snapping code be in its own module?
- Need to discuss and derive various snap rules
  Examples: If 'theta_snap' between dragged line and the  two reference enties
            is the same, then the snap should use the entity with shortest
            distance
            Should horizontal/vertical snap checks always be done before
            standard axis  snap checks -- guess-- No. The current implementation
            however skips the standard axis snap check if the
            horizontal/vertical snap checks succeed.

"""

from utilities.constants import black, darkred, blue
from utilities.prefs_constants import DarkBackgroundContrastColor_prefs_key
from utilities.prefs_constants import cursorTextFontSize_prefs_key

from geometry.VQT import vlen, norm, angleBetween, V, ptonline

import foundation.env as env

from graphics.drawing.CS_draw_primitives import drawline
from graphics.drawing.CS_draw_primitives import drawsphere

from commands.Select.Select_GraphicsMode import Select_GraphicsMode

STARTPOINT_SPHERE_RADIUS = 1.0
STARTPOINT_SPHERE_DRAWLEVEL = 2


# == GraphicsMode part

_superclass_for_GM = Select_GraphicsMode

class Line_GraphicsMode( Select_GraphicsMode ):
    """
    Custom GraphicsMode for use as a component of Line_Command.

    It's a temporary mode that draws temporary line with mouse click points
    as endpoints and then returns to the previous mode when the
    mouseClickLimit specified by the user is reached.

    @see: L{DnaLineMode}

    TODO:
    -Need further documentation.
    """

    #Initial values of instance variables --

    #The first end point of the line being drawn.
    #It gets initialized during left down --
    endPoint1 = None
    #The second endpoint of the line. This gets constantly updated as you
    # free drag the mouse (bare motion)
    endPoint2 = None

    rubberband_line_width = 1  #thickness or 'width' for drawer.drawline

    endPoint1_sphereColor = darkred
    endPoint1_sphereOpacity = 0.5

    _snapOn = False
    _snapType = ''
    _standardAxisVectorForDrawingSnapReference = None

    #Flag that determines whether the cursor text should be rendered in
    #self.Draw_other. Example: This class draws cursor text at the end of the draw
    #method. Subclass of this class (say DnaLine_GM) calls this Draw_other method
    #and then do some more drawing and then again want to draw the cursor text.
    #So that subclass can temporarily suppress cursor text.
    #@see: DnaLine_GM.Draw_other()
    _ok_to_render_cursor_text = True

    #cursor text. ##@@ todo: rename it to 'cursorText' -- Ninad
    text = ''

    #the drawing plane on which the line (or the structure in subclasses)
    #will be placed.
    plane = None

    def Enter_GraphicsMode(self):
        _superclass_for_GM.Enter_GraphicsMode(self)
        self._ok_to_render_cursor_text = True

        #Set the drawing plane to the one returned by  self.getDrawingPlane()
        #subclasses override the implementation of self.getDrawingPlane()
        #@see self.setDrawingPlane().
        self.plane = self.getDrawingPlane()


    def getDrawingPlane(self):
        """
        Overridden in subclasses.

        Returns the reference plane on which the line will be drawn.
        The default immplementation returns None.
        @see: InsertDna_GraphicsMode.getDrawingPlane()
        """
        return self.plane


    def setDrawingPlane(self, plane):
        """
        Sets the plane on which the line will be drawn (in subclasses , this
        is the plane on which the structure will be created.)
        @see: InsertDna_GraphicsMode.jigLeftUp()
        @see: InsertDna_EditCommand.updateDrawingPlane()
        """
        if isinstance(plane, self.win.assy.Plane):
            self.plane = plane
        else:
            self.plane = None

    def isSpecifyPlaneToolActive(self):
        """
        Default implementation returns False. Subclasses can override this
        method.
        @see: DnaDuplex_Graphicsmode.isSpecifyPlaneToolActive() which overrides
        this method.
        """
        return False


    def leftDown(self, event):
        """
        Event handler for LMB press event.
        """
        if self.isSpecifyPlaneToolActive():
            #@@@BUGGY: Ideally _superclass.leftDown should take care of this.
            #but Select_GraphicsMode doesn't do that.
            obj = self.get_obj_under_cursor(event)
            if obj is None: # Cursor over empty space.
                self.emptySpaceLeftDown(event)
                return

            self.doObjectSpecificLeftDown(obj, event)
            return

        self._leftDown_determine_endPoint1(event)

        #NIY code that accepts highlighted atom center as the endPoint instead
            ##of always using the glpane depth. To be  implemented
        ##if self.glpane.selobj is not None:
                ##if isinstance(selobj, Atom):
                    ##self.endPoint1 = self.glpane.selobj.posn()

        if self._snapOn and self.endPoint2 is not None:
            # This fixes a bug. Example: Suppose the dna line is snapped to a
            # constraint during the bare motion and the second point is clicked
            # when this happens, the second clicked point is the new
            #'self.endPoint1'  which needs to be snapped like we did for
            # self.endPoint2 in the bareMotion. Setting self._snapOn to False
            # ensures that the cursor is set to the simple Pencil cursor after
            # the click  -- Ninad 2007-12-04
            self.endPoint1 = self.snapLineEndPoint()
            self._snapOn = False

        self.command.mouseClickPoints.append(self.endPoint1)
        return


    def _leftDown_determine_endPoint1(self, event):
        """
        Determine the line endpoint (self.endPoint1) during the leftDown
        event. Subclasses can override this method.
        """
        plane = self.getDrawingPlane()
        if plane:
            self.endPoint1 = self.dragstart_using_plane_depth(
                event, plane )
        else:
            #The endPoint1 and self.endPoint2 are the mouse points at the 'water'
            #surface. Soon, support will be added so that these are actually points
            #on a user specified reference plane. Also, once any temporary mode
            # begins supporting highlighting, we can also add feature to use
            # coordinates of a highlighted object (e.g. atom center) as endpoints
            # of the line
            farQ_junk, self.endPoint1 = self.dragstart_using_GL_DEPTH(
                event,
                always_use_center_of_view = True )


    def bareMotion(self, event):
        """
        Event handler for simple drag event. (i.e. the free drag without holding
        down any mouse button)
        @see: self.isSpecifyPlaneToolActive()
        @see: self.getDrawingPlane()
        @see: DnaDuplex_Graphicsmode.isSpecifyPlaneToolActive()
        """
        if not self.isSpecifyPlaneToolActive():
            if len(self.command.mouseClickPoints) > 0:
                plane = self.getDrawingPlane()
                if plane:
                    self.endPoint2 = self.dragto( self.endPoint1,
                                                  event,
                                                  perp = norm(plane.getaxis()))
                else:
                    self.endPoint2 = self.dragto( self.endPoint1, event)

                self.endPoint2 = self.snapLineEndPoint()
                self.update_cursor_for_no_MB()
                self.glpane.gl_update()

        value = _superclass_for_GM.bareMotion(self,event)

        #Needed to make sure that the cursor is updated properly when
        #the mouse is moved after the 'specify reference plane tool is
        #activated/deactivated
        self.update_cursor()

        return value

    def snapLineEndPoint(self):
        """
        Snap the line to the specified constraints.
        To be refactored and expanded.
        @return: The new endPoint2 i.e. the moving endpoint of the rubberband
                 line . This value may be same as previous or snapped so that it
                 lies on a specified vector (if one exists)
        @rtype: B{A}
        """
        endPoint2 = self._snapEndPointHorizontalOrVertical()

        if not self._snapOn:
            endPoint2 = self._snapEndPointToStandardAxis()
            pass

        return endPoint2

    def _snapEndPointHorizontalOrVertical(self):
        """
        Snap the second endpoint of the line (and thus the whole line) to the
        screen horizontal or vertical vectors.
        @return: The new endPoint2 i.e. the moving endpoint of the rubberband
                 line . This value may be same as previous or snapped so that
                 line is horizontal or vertical depending upon the angle it
                 makes with the horizontal and vertical.
        @rtype: B{A}
        """
        up = self.glpane.up
        down = self.glpane.down
        left = self.glpane.left
        right = self.glpane.right

        endPoint2 = self.endPoint2

        snapVector = V(0, 0, 0)

        currentLineVector = norm(self.endPoint2 - self.endPoint1)

        theta_horizontal = angleBetween(right, currentLineVector)
        theta_vertical = angleBetween(up, currentLineVector)

        theta_horizontal_old = theta_horizontal
        theta_vertical_old = theta_vertical

        if theta_horizontal != 90.0:
            theta_horizontal = min(theta_horizontal,
                                   (180.0 - theta_horizontal))

        if theta_vertical != 90.0:
            theta_vertical = min(theta_vertical,
                                 180.0 - theta_vertical)

        theta = min(theta_horizontal, theta_vertical)

        if theta <= 2.0 and theta != 0.0:
            self._snapOn = True
            if theta == theta_horizontal:
                self._snapType = 'HORIZONTAL'
                if theta_horizontal == theta_horizontal_old:
                    snapVector = right
                else:
                    snapVector = left
            elif theta == theta_vertical:
                self._snapType = 'VERTICAL'
                if theta_vertical == theta_vertical_old:
                    snapVector = up
                else:
                    snapVector = down

            endPoint2 = self.endPoint1 + \
                      vlen(self.endPoint1 - self.endPoint2)*snapVector

        else:
            self._snapOn = False

        return endPoint2

    def _snapEndPointToStandardAxis(self):
        """
        Snap the second endpoint of the line so that it lies on the nearest
        axis vector. (if its close enough) . This functions keeps the uses the
        current rubberband line vector and just extends the second end point
        so that it lies at the intersection of the nearest axis vector and the
        rcurrent rubberband line vector.
        @return: The new endPoint2 i.e. the moving endpoint of the rubberband
                 line . This value may be same as previous or snapped to lie on
                 the nearest axis (if one exists)
        @rtype: B{A}
        """
        x_axis = V(1, 0, 0)
        y_axis = V(0, 1, 0)
        z_axis = V(0, 0, 1)

        endPoint2 = self.endPoint2
        currentLineVector = norm(self.endPoint2 - self.endPoint1)

        theta_x = angleBetween(x_axis, self.endPoint2)
        theta_y = angleBetween(y_axis, self.endPoint2)
        theta_z = angleBetween(z_axis, self.endPoint2)

        theta_x = min(theta_x, (180 - theta_x))
        theta_y = min(theta_y, (180 - theta_y))
        theta_z = min(theta_z, (180 - theta_z))

        theta = min(theta_x, theta_y, theta_z)

        if theta < 2.0:
            if theta == theta_x:
                self._standardAxisVectorForDrawingSnapReference = x_axis
            elif theta == theta_y:
                self._standardAxisVectorForDrawingSnapReference = y_axis
            elif theta == theta_z:
                self._standardAxisVectorForDrawingSnapReference = z_axis

            endPoint2 = ptonline(self.endPoint2,
                                 V(0, 0, 0),
                                 self._standardAxisVectorForDrawingSnapReference)
        else:
            self._standardAxisVectorForDrawingSnapReference = None

        return endPoint2

    def _drawSnapReferenceLines(self):
        """
        Draw the snap reference lines as dotted lines. Example, if the
        moving end of the rubberband line is 'close enough' to a standard axis
        vector, that point is 'snapped' soi that it lies on the axis. When this
        is done, program draws a dotted line from origin to the endPoint2
        indicating that the endpoint is snapped to that axis line.

        This method is called inside the self.Draw_other method.

        @see: self._snapEndPointToStandardAxis
        @see: self.Draw_other
        """
        if self.endPoint2 is None:
            return
        if self._standardAxisVectorForDrawingSnapReference:
            drawline(blue,
                     V(0, 0, 0),
                     self.endPoint2,
                     dashEnabled = True,
                     stipleFactor = 4,
                     width = 2)
        return

    def Draw_other(self):
        """
        """
        _superclass_for_GM.Draw_other(self)

        #This fixes NFR bug  2803
        #Don't draw the Dna rubberband line if the cursor is over the confirmation
        #corner. But make sure to call superclass.Draw_other method before doing this
        #check because we need to draw the rest of the model in the graphics
        #mode!. @see: DnaLineMode_GM.Draw_other() which does similar thing to not
        #draw the rubberband line when the cursor is on the confirmation corner
        handler = self.o.mouse_event_handler
        if handler is not None and handler is self._ccinstance:
            ##### REVIEW:
            #
            # 1. This is probably incorrect in principle, as a way of
            # deciding what to draw. The mouse event handling methods
            # should set an attribute which directly specifies whether
            # the next call of Draw_other (or other Draw methods)
            # should draw the rubberband line or not.
            # (Or which affects the value of an access method, e.g.
            #  something like self.should_draw_rubberband_lines().)
            #
            # 2. Why is update_cursor called here? Any call of update_cursor
            # inside a specific Draw method seems suspicious.
            #
            # 3. This needs refactoring to merge with common code in its
            # subclass DnaLineMode_GM, and to consider doing the same
            # thing in its other 3 subclasses.
            #
            # [bruce 090310 comments]
            self.update_cursor()
            return

        if self.endPoint2 is not None:

            if self.endPoint1:
                drawsphere(self.endPoint1_sphereColor,
                           self.endPoint1,
                           STARTPOINT_SPHERE_RADIUS,
                           STARTPOINT_SPHERE_DRAWLEVEL,
                           opacity = self.endPoint1_sphereOpacity
                           )
            drawline(env.prefs[DarkBackgroundContrastColor_prefs_key],
                     self.endPoint1,
                     self.endPoint2,
                     width = self.rubberband_line_width,
                     dashEnabled = True)

            self._drawSnapReferenceLines()

            if self._ok_to_render_cursor_text:
                self._drawCursorText()

    def _drawCursorText(self):
        """
        """
        if self.endPoint1 is None or self.endPoint2 is None:
            return

        self.text = ''
            #### REVIEW: why do we set an attribute here? That's very
            # suspicious in any drawing method. [bruce 090310 comment]
        textColor = black

        #Draw the text next to the cursor that gives info about
        #number of base pairs etc. So this class and its command class needs
        #cleanup. e.g. callbackMethodForCursorTextString should be simply
        #self.command.getCursorText() and like that. -- Ninad2008-04-17
        if self.command and hasattr(self.command,
                                    'callbackMethodForCursorTextString'):
            self.text, textColor = self.command.callbackMethodForCursorTextString(
                self.endPoint1,
                self.endPoint2)
        else:
            vec = self.endPoint2 - self.endPoint1
            thetaString = self._getCursorText_angle(vec)
            distString = self._getCursorText_length(vec)

            if distString:
                #This could be a user preference. At the moment, subclasses
                #may return an empty string for distance.
                self.text = "%5.2fA, %s" % (dist, thetaString)
            else:
                self.text = "%s" % (thetaString,)

        self.glpane.renderTextNearCursor(self.text,
                                         textColor = textColor,
                                         fontSize = env.prefs[cursorTextFontSize_prefs_key])

    def _getCursorText_length(self, vec):
        """
        Subclasses may override this method.
        @see: self._drawCursorText() for details.
        """
        dist = vlen(vec)
        return "%5.2A"%(dist)

    def _getCursorText_angle(self, vec):
        """
        Subclasses may override this method.
        @see: self._drawCursorText() for details.
        """
        thetaString = ''
        theta = self.glpane.get_angle_made_with_screen_right(vec)
        thetaString = "%5.2f deg"%(theta)
        return thetaString

    def leftUp(self, event):
        """
        Event handler for Left Mouse button left-up event
        @see: Line_Command._f_results_for_caller_and_prepare_for_new_input()
        """
        if self.isSpecifyPlaneToolActive():
            if self.cursor_over_when_LMB_pressed == 'Empty Space':
                self.emptySpaceLeftUp(event)
                return

            obj = self.current_obj
            if obj is None: # Nothing dragged (or clicked); return.
                return

            self.doObjectSpecificLeftUp(obj, event)
            return

        if  self.command.mouseClickLimit is None:
            if len(self.command.mouseClickPoints) == 2:
                self.endPoint2 = None
                self.command._f_results_for_caller_and_prepare_for_new_input()
                self.glpane.gl_update()
            return


        assert len(self.command.mouseClickPoints) <= self.command.mouseClickLimit

        if len(self.command.mouseClickPoints) == self.command.mouseClickLimit:
            self.endPoint2 = None
            self._snapOn = False
            self._standardAxisVectorForDrawingSnapReference = None
            self.glpane.gl_update()
            #Exit this GM's command (i.e. the command 'Line')
            self.command.command_Done()
            return


    def update_cursor_for_no_MB(self):
        """
        Update the cursor for this mode.
        """

        #self.glpane.setCursor(self.win.SelectAtomsCursor)
        if self._snapOn:
            if self._snapType == 'HORIZONTAL':
                self.glpane.setCursor(self.win.pencilHorizontalSnapCursor)
            elif self._snapType == 'VERTICAL':
                self.glpane.setCursor(self.win.pencilVerticalSnapCursor)
        else:
            self.glpane.setCursor(self.win.colorPencilCursor)

    def resetVariables(self):
        """
        Reset instance variables. Typically used by self.command when the
        command is exited without the graphics mode knowing about it before hand
        Example: You entered line mode, started drawing line, and hit Done
        button. This exits the Graphics mode (without the 'leftup' which usually
        terminates the command *from Graphics mode') . In the above case, the
        command.command_will_exit() needs to tell its graphics mode about what just
        happened , so that all the assigned values get cleared and ready to use
        next time this graphicsMode is active.
        """
        self.endPoint1 = None
        self.endPoint2 = None

    pass

# end

