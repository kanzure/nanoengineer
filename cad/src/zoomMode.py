# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
zoomMode.py -- zoom mode.

$Id$

"""
__author__ = "Mark"

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

from panMode import panlikeMode
_superclass = panlikeMode

class zoomMode(_superclass):
    # class constants
    modename = 'ZOOM'
    default_mode_status_text = "Tool: Zoom" # Changed 'Mode' to 'Tool'. Fixes bug 1298. mark 060323
    
    # methods related to entering this mode
    
    def Enter(self):
        _superclass.Enter(self)
        bg = self.glpane.backgroundColor
                
        # rubber window shows as white color normally, but when the
        # background becomes bright, we'll set it as black.
        brightness = bg[0] + bg[1] + bg[2]
        if brightness > 1.5: self.rbwcolor = bg
        else: self.rbwcolor = A((1.0, 1.0, 1.0)) - A(bg)
        
        self.glStatesChanged = False
        
        
    # init_gui handles all the GUI display when entering this mode [mark 041004]
    def init_gui(self):
        self.win.zoomToolAction.setChecked(1) # toggle on the Zoom Tool icon
        self.glpane.setCursor(self.win.ZoomCursor)
            
    # Huaicai: This method must be called to safely exit this mode    
    def Done(self, new_mode = None):
        
        ## If OpenGL states changed during this mode, we need to restore
        ## them before exit. Currently, only leftDown() will change that.
        if self.glStatesChanged:
            self.glpane.redrawGL = True
            glDisable(GL_COLOR_LOGIC_OP)
            glEnable(GL_LIGHTING)
            glEnable(GL_DEPTH_TEST)
        
        return _superclass.Done(self, new_mode)
    
    # restore_gui handles all the GUI display when leaving this mode [mark 041004]
    def restore_gui(self):
        self.win.zoomToolAction.setChecked(0) # toggle off the Zoom Tool icon
 
    # mouse events
    def leftDown(self, event):
        """Compute the rubber band window starting point, which
             lies on the near clipping plane, projecting into the same 
             point that current cursor points at on the screen plane"""
        self.pWxy = (event.pos().x(), self.glpane.height - event.pos().y())
        p1 = A(gluUnProject(self.pWxy[0], self.pWxy[1], 0.005)) 
        
        self.pStart = p1
        self.pPrev = p1
        self.firstDraw = True
        
        self.glpane.redrawGL = False
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glColor3d(self.rbwcolor[0], self.rbwcolor[1], self.rbwcolor[2])
        
        glEnable(GL_COLOR_LOGIC_OP)
        glLogicOp(GL_XOR)
        
        self.glStatesChanged = True
        return
        
    def leftDrag(self, event):
        """Compute the changing rubber band window ending point. Erase    the previous window, draw the new window """
        # bugs 1190, 1818 wware 060405 - sometimes Qt neglects to call leftDown before this
        if not hasattr(self, "pWxy") or not hasattr(self, "firstDraw"):
            return
        cWxy = (event.pos().x(), self.glpane.height - event.pos().y())
        
        if not self.firstDraw: #Erase the previous rubber window
            drawer.drawrectangle(self.pStart, self.pPrev, self.glpane.up, self.glpane.right, self.rbwcolor)
        self.firstDraw = False

        self.pPrev = A(gluUnProject(cWxy[0], cWxy[1], 0.005))
        ##draw the new rubber band
        drawer.drawrectangle(self.pStart, self.pPrev, self.glpane.up, self.glpane.right, self.rbwcolor)
        glFlush()
        self.glpane.swapBuffers() # Update display
        return
        
    def leftUp(self, event):
        """Erase the final rubber band window and do zoom if user indeed     draws a rubber band window"""
        # bugs 1190, 1818 wware 060405 - sometimes Qt neglects to call leftDown before this
        if not hasattr(self, "pWxy") or not hasattr(self, "firstDraw"):
            return
        cWxy = (event.pos().x(), self.glpane.height - event.pos().y())
        zoomX = (abs(cWxy[0] - self.pWxy[0]) + 0.0) / (self.glpane.width + 0.0)
        zoomY = (abs(cWxy[1] - self.pWxy[1]) + 0.0) / (self.glpane.height + 0.0)

        ##The rubber band window size can be larger than that of glpane.
        ## Limit the zoomFactor to 1.0
        zoomFactor = min(max(zoomX, zoomY), 1.0)
        
        ##Huaicai: when rubber band window is too small,
        ##like a double click, a single line rubber band, skip zoom
        DELTA = 1.0E-5
        if self.pWxy[0] == cWxy[0] or self.pWxy[1] == cWxy[1] or zoomFactor < DELTA: 
                self.glpane.mode.Done(self.glpane.prevMode)
                return
        
        ##Erase the last rubber-band window
        drawer.drawrectangle(self.pStart, self.pPrev, self.glpane.up, self.glpane.right, self.rbwcolor)
        glFlush()
        self.glpane.swapBuffers()
        
        winCenterX = (cWxy[0] + self.pWxy[0]) / 2.0
        winCenterY = (cWxy[1] + self.pWxy[1]) / 2.0
        winCenterZ = glReadPixelsf(int(winCenterX), int(winCenterY), 1, 1, GL_DEPTH_COMPONENT)
        
        assert winCenterZ[0][0] >= 0.0 and winCenterZ[0][0] <= 1.0
        if winCenterZ[0][0] >= GL_FAR_Z:  ### window center touches nothing
                 p1 = A(gluUnProject(winCenterX, winCenterY, 0.005))
                 p2 = A(gluUnProject(winCenterX, winCenterY, 1.0))

                 los = self.glpane.lineOfSight
                 k = dot(los, -self.glpane.pov - p1) / dot(los, p2 - p1)

                 zoomCenter = p1 + k*(p2-p1)
        else:
                zoomCenter = A(gluUnProject(winCenterX, winCenterY, winCenterZ[0][0]))
        self.glpane.pov = V(-zoomCenter[0], -zoomCenter[1], -zoomCenter[2]) 
        
        ## The following are 2 ways to do the zoom, the first one 
        ## changes view angles, the 2nd one change viewing distance
        ## The advantage for the 1st one is model will not be clipped by 
        ##  near or back clipping planes, and the rubber band can be 
        ## always shown. The disadvantage: when the view field is too 
        ## small, a selection window may be actually act as a single pick.
        ## rubber ban window will not look as rectanglular any more.
        #zf = self.glpane.getZoomFactor()
        ##zoomFactor = pow(zoomFactor, 0.25)
        #zoomFactor *= zf
        #self.glpane.setZoomFactor(zoomFactor)
        
        ##Change viewing distance to do zoom. This works better with
        ##mouse wheel, since both are changing viewing distance, and
        ##it's not too bad of model being clipped, since the near/far clip
        ##plane change as scale too.
        self.glpane.scale *= zoomFactor
       
        self.Done()
        return
    
    def Draw(self):
        _superclass.Draw(self)
        ##Make sure this is the last scene draw
        #if self.rbw: 
                #self.RBWdraw() # Draw rubber band window.
        return
       
    def RBWdraw(self):
        """Draw the rubber-band window. 
        """
        drawer.drawrectangle(self.pStart, self.pPrev,
                                 self.glpane.up, self.glpane.right, self.rbwcolor)
         
    def update_cursor_for_no_MB(self): # Fixes bug 1638. mark 060312.
        '''Update the cursor for 'Zoom' mode.
        '''
        self.glpane.setCursor(self.win.ZoomCursor)

    pass # end of class zoomMode

# end
