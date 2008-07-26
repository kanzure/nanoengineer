# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
Zoom to Area functionality.

@author:    Mark Sims
@version:   $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

History:
Mark 2008-01-31: Renamed from ZoomMode to ZoomToAreaMode.py
"""

from Numeric import dot

from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import glDisable
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glColor3d
from OpenGL.GL import GL_COLOR_LOGIC_OP
from OpenGL.GL import glEnable
from OpenGL.GL import GL_XOR
from OpenGL.GL import glLogicOp
from OpenGL.GL import glFlush
from OpenGL.GL import GL_DEPTH_COMPONENT
from OpenGL.GL import glReadPixelsf
from OpenGL.GLU import gluUnProject

from geometry.VQT import V, A
from graphics.drawing.drawers import drawrectangle
from utilities.constants import GL_FAR_Z


from temporary_commands.TemporaryCommand import TemporaryCommand_Overdrawing


# == the GraphicsMode part

class ZoomToAreaMode_GM( TemporaryCommand_Overdrawing.GraphicsMode_class ):
    """
    Custom GraphicsMode for use as a component of ZoomToAreaMode.
    """
        
    def leftDown(self, event):
        """
        Compute the rubber band window starting point, which
        lies on the near clipping plane, projecting into the same 
        point that current cursor points at on the screen plane.
        """
        self.pWxy = (event.pos().x(), self.glpane.height - event.pos().y())
        p1 = A(gluUnProject(self.pWxy[0], self.pWxy[1], 0.005)) 
        
        self.pStart = p1
        self.pPrev = p1
        self.firstDraw = True

        self.command.glStatesChanged = True
            # this warns our exit code to undo the following OpenGL state changes:
        
        self.glpane.redrawGL = False
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        rbwcolor = self.command.rbwcolor
        glColor3d(rbwcolor[0], rbwcolor[1], rbwcolor[2])
        
        glEnable(GL_COLOR_LOGIC_OP)
        glLogicOp(GL_XOR)
        
        return
        
    def leftDrag(self, event):
        """
        Compute the changing rubber band window ending point. Erase the
        previous window, draw the new window.
        """
        # bugs 1190, 1818 wware 4/05/2006 - sometimes Qt neglects to call leftDown
        # before this
        if not hasattr(self, "pWxy") or not hasattr(self, "firstDraw"):
            return
        cWxy = (event.pos().x(), self.glpane.height - event.pos().y())

        rbwcolor = self.command.rbwcolor

        if not self.firstDraw: #Erase the previous rubber window
            drawrectangle(self.pStart, self.pPrev, self.glpane.up,
                          self.glpane.right, rbwcolor)
        self.firstDraw = False

        self.pPrev = A(gluUnProject(cWxy[0], cWxy[1], 0.005))
        # draw the new rubber band
        drawrectangle(self.pStart, self.pPrev, self.glpane.up,
                      self.glpane.right, rbwcolor)
        glFlush()
        self.glpane.swapBuffers() # Update display
        return
        
    def leftUp(self, event):
        """
        Erase the final rubber band window and do zoom if user indeed draws a
        rubber band window.
        """
        # bugs 1190, 1818 wware 4/05/2006 - sometimes Qt neglects to call
        # leftDown before this
        if not hasattr(self, "pWxy") or not hasattr(self, "firstDraw"):
            return
        cWxy = (event.pos().x(), self.glpane.height - event.pos().y())
        zoomX = (abs(cWxy[0] - self.pWxy[0]) + 0.0) / (self.glpane.width + 0.0)
        zoomY = (abs(cWxy[1] - self.pWxy[1]) + 0.0) / (self.glpane.height + 0.0)

        # The rubber band window size can be larger than that of glpane.
        # Limit the zoomFactor to 1.0
        zoomFactor = min(max(zoomX, zoomY), 1.0)
        
        # Huaicai: when rubber band window is too small,
        # like a double click, a single line rubber band, skip zoom
        DELTA = 1.0E-5
        if self.pWxy[0] == cWxy[0] or self.pWxy[1] == cWxy[1] \
                or zoomFactor < DELTA: 
            self.command.Done()
            return
        
        # Erase the last rubber-band window
        rbwcolor = self.command.rbwcolor
        drawrectangle(self.pStart, self.pPrev, self.glpane.up,
                      self.glpane.right, rbwcolor)
        glFlush()
        self.glpane.swapBuffers()
        
        winCenterX = (cWxy[0] + self.pWxy[0]) / 2.0
        winCenterY = (cWxy[1] + self.pWxy[1]) / 2.0
        winCenterZ = \
            glReadPixelsf(int(winCenterX), int(winCenterY), 1, 1,
                          GL_DEPTH_COMPONENT)
        
        assert winCenterZ[0][0] >= 0.0 and winCenterZ[0][0] <= 1.0
        if winCenterZ[0][0] >= GL_FAR_Z:  # window center touches nothing
            p1 = A(gluUnProject(winCenterX, winCenterY, 0.005))
            p2 = A(gluUnProject(winCenterX, winCenterY, 1.0))

            los = self.glpane.lineOfSight
            k = dot(los, -self.glpane.pov - p1) / dot(los, p2 - p1)
            
            zoomCenter = p1 + k*(p2-p1)
            
        else:
            zoomCenter = \
                A(gluUnProject(winCenterX, winCenterY, winCenterZ[0][0]))
        self.glpane.pov = V(-zoomCenter[0], -zoomCenter[1], -zoomCenter[2]) 
        
        # The following are 2 ways to do the zoom, the first one 
        # changes view angles, the 2nd one change viewing distance
        # The advantage for the 1st one is model will not be clipped by 
        #  near or back clipping planes, and the rubber band can be 
        # always shown. The disadvantage: when the view field is too 
        # small, a selection window may be actually act as a single pick.
        # rubber ban window will not look as rectanglular any more.
        #zf = self.glpane.getZoomFactor()
        #zoomFactor = pow(zoomFactor, 0.25)
        #zoomFactor *= zf
        #self.glpane.setZoomFactor(zoomFactor)
        
        # Change viewing distance to do zoom. This works better with
        # mouse wheel, since both are changing viewing distance, and
        # it's not too bad of model being clipped, since the near/far clip
        # plane change as scale too.
        self.glpane.scale *= zoomFactor
       
        self.command.Done(exit_using_done_or_cancel_button = False)
        return
        
    def update_cursor_for_no_MB(self): # Fixes bug 1638. Mark 3/12/2006.
        """
        Update the cursor for 'Zoom' mode.
        """
        self.glpane.setCursor(self.win.ZoomCursor)

    def restore_patches_by_GraphicsMode(self):
        """
        This is run when we exit this command for any reason.
        """
        # If OpenGL states changed during this mode, we need to restore
        # them before exit. Currently, only leftDown() will change that.
        # [bruce 071011/071012 change: do this in
        #  restore_patches_by_GraphicsMode, not in Done]
        if self.command.glStatesChanged:
            self.glpane.redrawGL = True
            glDisable(GL_COLOR_LOGIC_OP)
            glEnable(GL_LIGHTING)
            glEnable(GL_DEPTH_TEST)
        return
    
    pass

# == the Command part

class ZoomToAreaMode(TemporaryCommand_Overdrawing):
    """
    Encapsulates the Zoom Tool functionality.
    """
    # TODO: rename to ZoomTool or ZoomCommand or TemporaryCommand_Zoom or ...
    
    # class constants
    commandName = 'ZOOMTOAREA'
    featurename = "Zoom to Area Tool"
    from utilities.constants import CL_VIEW_CHANGE
    command_level = CL_VIEW_CHANGE

    GraphicsMode_class = ZoomToAreaMode_GM
    
    def Enter(self):
        super(ZoomToAreaMode, self).Enter()
        bg = self.glpane.backgroundColor
        
        # rubber window shows as white color normally, but when the
        # background becomes bright, we'll set it as black.
        brightness = bg[0] + bg[1] + bg[2]
        if brightness > 1.5:
            self.rbwcolor = bg
                # note: accessed as self.command.rbwcolor in our GraphicsMode part
        else:
            self.rbwcolor = A((1.0, 1.0, 1.0)) - A(bg)
        
        self.glStatesChanged = False
            # note: accessed as self.command.glStatesChanged in our GraphicsMode part
        return
    
    def init_gui(self):
        self.win.zoomToAreaAction.setChecked(1) # toggle on the Zoom Tool icon

    def restore_gui(self):
        self.win.zoomToAreaAction.setChecked(0) # toggle off the Zoom Tool icon

    pass

# end
