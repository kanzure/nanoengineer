# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
zoomMode.py -- zoom mode.

$Id$

"""
__author__ = "Mark"

from modes import *


class zoomMode(basicMode):
    # class constants
    modename = 'ZOOM'
    default_mode_status_text = "Mode: Zoom"
    
    # methods related to entering this mode
    
    def Enter(self):
        basicMode.Enter(self)
        # Set background color to the previous mode's bg color
        bg = self.backgroundColor = self.o.prevModeColor
        
        # rubber window shows as white color normally, but when the
        # background becomes bright, we'll set it as black.
        brightness = bg[0] + bg[1] + bg[2]
        if brightness > 1.5: self.rbwcolor = bg
        else: self.rbwcolor = A((1.0, 1.0, 1.0)) - A(bg)
        
        self.glStatesChanged = False
        
        
    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        self.OldCursor = QCursor(self.o.cursor())
        self.w.zoomToolAction.setOn(1) # toggle on the Zoom Tool icon
        self.o.setCursor(self.w.ZoomCursor)
        self.w.zoomDashboard.show()
            
# methods related to exiting this mode

    def haveNontrivialState(self):
        return False

    def StateDone(self):
        return None
        
    # a safe way for now to override Done:
    ## Huaicai: This method must be called to safely exit this mode    
    def Done(self, new_mode = None):
        """[overrides basicMode.Done; this is deprecated, so doing it here
        is a temporary measure for Alpha, to be reviewed by Bruce ASAP after
        Alpha goes out; see also the removal of Done from weird_to_override
        in modes.py. [bruce and mark 050130]
        """
        self.w.zoomToolAction.setOn(0) # toggle off the Zoom Tool icon
        ## [bruce's symbol to get him to review it soon: ####@@@@]
        if new_mode == None:
            try:
                m = self.o.prevMode # spelling??
                new_mode = m
            except:
                pass
        
        ## If OpenGL states changed during this mode, we need to restore
        ## them before exit. Currently, only the leftDown() will change that.
        if self.glStatesChanged:
            self.o.redrawGL = True
            glDisable(GL_COLOR_LOGIC_OP)
            glEnable(GL_LIGHTING)
            glEnable(GL_DEPTH_TEST)
        
        return basicMode.Done(self, new_mode)
        
            
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.o.setCursor(self.OldCursor) # restore cursor
        self.w.zoomDashboard.hide()

    # mouse and key events
    def leftDown(self, event):
        """Compute the rubber band window starting point, which
             lies on the near clipping plane, projecting into the same 
             point that current cursor points at on the screen plane"""
        self.pWxy = (event.pos().x(), self.o.height - event.pos().y())
        p1 = A(gluUnProject(self.pWxy[0], self.pWxy[1], 0.005)) 
        
        self.pStart = p1
        self.pPrev = p1
        self.point2 = None
        self.point3 = None
        
        self.o.redrawGL = False
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glColor3d(self.rbwcolor[0], self.rbwcolor[1], self.rbwcolor[2])
        
        glEnable(GL_COLOR_LOGIC_OP)
        glLogicOp(GL_XOR)
        
        self.glStatesChanged = True
        
        
    def computePoints(self):
          """Compute the left bottom(point2) and right top (point3) """
          rt = self.o.right
          up = self.o.up  
          self.point2 = self.pStart + up*dot(up, self.pPrev - self.pStart)
          self.point3 = self.pStart + rt*dot(rt, self.pPrev - self.pStart)
    
            
    def leftDrag(self, event):
        """Compute the changing rubber band window ending point. Erase    the previous window, draw the new window """
        cWxy = (event.pos().x(), self.o.height - event.pos().y())
        
        if self.point2 and self.point3: #Erase the previous rubber window
            drawer.drawRubberBand(self.pStart, self.pPrev, self.point2, self.point3, self.rbwcolor)
          
        self.pPrev = A(gluUnProject(cWxy[0], cWxy[1], 0.005))
        ##draw the new rubber band
        self.computePoints()
        drawer.drawRubberBand(self.pStart, self.pPrev, self.point2, self.point3, self.rbwcolor)
        glFlush()
        self.o.swapBuffers() #Update display
        
        
    def leftUp(self, event):
        """"Erase the final rubber band window and do zoom if user indeed     draws a rubber band window"""
        cWxy = (event.pos().x(), self.o.height - event.pos().y())
        zoomX = (abs(cWxy[0] - self.pWxy[0]) + 0.0) / (self.o.width + 0.0)
        zoomY = (abs(cWxy[1] - self.pWxy[1]) + 0.0) / (self.o.height + 0.0)

        ##The rubber band window size can be larger than that of glpane.
        ## Limit the zoomFactor to 1.0
        zoomFactor = min(max(zoomX, zoomY), 1.0)
        
        ##Huaicai: when rubber band window is too small,
        ##like a double click, a single line rubber band, skip zoom
        DELTA = 1.0E-5
        if self.pWxy[0] == cWxy[0] or self.pWxy[1] == cWxy[1] or zoomFactor < DELTA: 
                self.o.mode.Done(self.o.prevMode)
                return
        
        ##Erase the last rubber-band window
        drawer.drawRubberBand(self.pStart, self.pPrev, self.point2, self.point3, self.rbwcolor)
        glFlush()
        self.o.swapBuffers()
        
        winCenterX = (cWxy[0] + self.pWxy[0]) / 2.0
        winCenterY = (cWxy[1] + self.pWxy[1]) / 2.0
        winCenterZ = glReadPixelsf(int(winCenterX), int(winCenterY), 1, 1, GL_DEPTH_COMPONENT)
        
        assert winCenterZ[0][0] >= 0.0 and winCenterZ[0][0] <= 1.0
        if winCenterZ[0][0] >= 1.0:  ### window center touches nothing
                 p1 = A(gluUnProject(winCenterX, winCenterY, 0.005))
                 p2 = A(gluUnProject(winCenterX, winCenterY, 1.0))

                 los = self.o.lineOfSight
                 k = dot(los, -self.o.pov - p1) / dot(los, p2 - p1)

                 zoomCenter = p1 + k*(p2-p1)
        else:
                zoomCenter = A(gluUnProject(winCenterX, winCenterY, winCenterZ[0][0]))
        self.o.pov = V(-zoomCenter[0], -zoomCenter[1], -zoomCenter[2]) 
        
        ## The following are 2 ways to do the zoom, the first one 
        ## changes view angles, the 2nd one change viewing distance
        ## The advantage for the 1st one is model will not be clipped by 
        ##  near or back clipping planes, and the rubber band can be 
        ## always shown. The disadvantage: when the view field is too 
        ## small, a selection window may be actually act as a single pick.
        ## rubber ban window will not look as rectanglular any more.
        #zf = self.o.getZoomFactor()
        ##zoomFactor = pow(zoomFactor, 0.25)
        #zoomFactor *= zf
        #self.o.setZoomFactor(zoomFactor)
        
        ##Change viewing distance to do zoom. This works better with
        ##mouse wheel, since both are changing viewing distance, and
        ##it's not too bad of model being clipped, since the near/far clip
        ##plane change as scale too.
        self.o.scale *= zoomFactor
       
        self.Done()

    def keyPress(self,key):
        # ESC - Exit/cancel zoom mode.
        if key == Qt.Key_Escape: 
            self.Done()
            
    def Draw(self):
        basicMode.Draw(self)
        self.o.assy.draw(self.o)
        ##Make sure this is the last scene draw
        #if self.rbw: 
                #self.RBWdraw() # Draw rubber band window.
     
       
    def RBWdraw(self):
        """Draw the rubber-band window. 
        """
        drawer.drawrectangle(self.pStart, self.pPrev,
                                 self.o.up, self.o.right, self.rbwcolor)

    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Done),
            ('Done', self.Done),
         ]

    pass # end of class zoomMode