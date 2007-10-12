# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
Zoom mode functionality.

@author:    Mark Sims
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
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

from VQT import V, A
import drawer
from constants import GL_FAR_Z

from ArrangementMode import ArrangementMode
    # TODO: this superclass needs renaming, since it has nothing to do
    # with "arrangements" of anything. What it's about is something like
    # a "view-change temporary command with no PM". We should see which of
    # those qualities it's specific to, when choosing a new name. Note that
    # if we split it into Command and GraphicsMode parts, each part might
    # be specific to different things, i.e. one might be more widely
    # reusable than the other. So they might not have precisely corresponding
    # names, since the name should reflect what it can be used for.
    # [bruce 071010]

_superclass = ArrangementMode

class ZoomMode(_superclass):

    # == Command part
    
    # class constants
    modename = 'ZOOM'
    default_mode_status_text = "Tool: Zoom"
        
    def Enter(self):
        _superclass.Enter(self)
        bg = self.glpane.backgroundColor
                
        # rubber window shows as white color normally, but when the
        # background becomes bright, we'll set it as black.
        brightness = bg[0] + bg[1] + bg[2]
        if brightness > 1.5:
            self.rbwcolor = bg # TODO: make this accessible from our GraphicsMode part, when that's split
        else:
            self.rbwcolor = A((1.0, 1.0, 1.0)) - A(bg)
        
        self.glStatesChanged = False
            # to find uses of this, look for self.command.glStatesChanged in our GraphicsMode part
        return
    
    def init_gui(self):
        self.win.zoomToolAction.setChecked(1) # toggle on the Zoom Tool icon
        self.glpane.setCursor(self.win.ZoomCursor)

    def restore_gui(self):
        self.win.zoomToolAction.setChecked(0) # toggle off the Zoom Tool icon

    # == GraphicsMode part
    
    # TODO:
    # [part of it is already done: change self.Done to self.command.Done below]
    ### bruce 071010: see if I can use this as a test case for having a separate
    ### Command and GraphicsMode, except that I'll first need to do the same
    ### thing inside ArrangementMode I guess... make a split variant of it
    ### for this purpose.
    ##
    ##class ZoomCommand_GraphicsMode(GraphicsMode):

    # mouse events
    
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
        glColor3d(self.rbwcolor[0], self.rbwcolor[1], self.rbwcolor[2])
        
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
        
        if not self.firstDraw: #Erase the previous rubber window
            drawer.drawrectangle(self.pStart, self.pPrev, self.glpane.up,
                                 self.glpane.right, self.rbwcolor)
        self.firstDraw = False

        self.pPrev = A(gluUnProject(cWxy[0], cWxy[1], 0.005))
        # draw the new rubber band
        drawer.drawrectangle(self.pStart, self.pPrev, self.glpane.up,
                             self.glpane.right, self.rbwcolor)
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
        drawer.drawrectangle(self.pStart, self.pPrev, self.glpane.up,
                             self.glpane.right, self.rbwcolor)
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
       
        self.command.Done()
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
        # [bruce 071011/071012 change: do this in restore_patches_by_GraphicsMode, not in Done]
        if self.command.glStatesChanged:
            self.glpane.redrawGL = True
            glDisable(GL_COLOR_LOGIC_OP)
            glEnable(GL_LIGHTING)
            glEnable(GL_DEPTH_TEST)
        return
    
    pass

# end
