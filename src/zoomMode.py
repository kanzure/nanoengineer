# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
zoomMode.py -- zoom mode.

$Id$
"""
__author__ = "Mark"

from modes import *

class zoomMode(basicMode):

    # class constants
    backgroundColor = 0.5, 0.5, 0.5
    modename = 'ZOOM'
    default_mode_status_text = "Mode: Zoom"
    
    # flag indicating when to draw the rubber band window.
    rbw = False
    rbwcolor = navy

    # no __init__ method needed
    
    # methods related to entering this mode
    
    def Enter(self):
        # Set background color to the previous mode's bg color
        bg = self.backgroundColor = self.o.prevModeColor
        
        # Set RBW color based on brightness of bg color
        brightness = bg[0] + bg[1] + bg[2]
        if brightness >= 1.5: self.rbwcolor = navy
        else: self.rbwcolor = white
        
        basicMode.Enter(self)

    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        self.OldCursor = QCursor(self.o.cursor())
        self.o.setCursor(self.w.ZoomCursor)
        self.w.zoomDashboard.show()
            
# methods related to exiting this mode

    def haveNontrivialState(self):
        return False

    def StateDone(self):
        return None
    
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.o.setCursor(self.OldCursor) # restore cursor
        self.w.zoomDashboard.hide()

    # mouse and key events
    def leftDown(self, event):
        """Compute the rubber band window starting point, which
             lies on the near clipping plane, projecting into the same 
             point that current cursor points at on the screen plane"""
        self.rbw = True
        self.pWxy = (event.pos().x(), self.o.height - event.pos().y())
        p1 = A(gluUnProject(self.pWxy[0], self.pWxy[1], 0.0)) 
        
        self.pickLineStart = self.pickLinePrev = p1

    
    def leftDrag(self, event):
        """Compute the changing rubber band window ending point """
        cWxy = (event.pos().x(), self.o.height - event.pos().y())
        p1 = A(gluUnProject(cWxy[0], cWxy[1], 0.0)) 
        self.pickLinePrev = p1
        self.o.paintGL()


    def leftUp(self, event):
        """"Compute the final rubber band window ending point, do zoom"""
        cWxy = (event.pos().x(), self.o.height - event.pos().y())
        p1 = A(gluUnProject(cWxy[0], cWxy[1], 0.0)) 
        zoomX = (abs(cWxy[0] - self.pWxy[0]) + 0.0) / (self.o.width + 0.0)
        zoomY = (abs(cWxy[1] - self.pWxy[1]) + 0.0) / (self.o.height + 0.0)
              
        winCenterX = (cWxy[0] + self.pWxy[0]) / 2.0
        winCenterY = (cWxy[1] + self.pWxy[1]) / 2.0
        winCenterZ = glReadPixelsf(int(winCenterX), int(winCenterY), 1, 1, GL_DEPTH_COMPONENT)
        
        zoomFactor = max(zoomX, zoomY)
        
        assert winCenterZ[0][0] >= 0.0 and winCenterZ[0][0] <= 1.0
        if winCenterZ[0][0] >= 1.0:  ### window center touches nothing
                junk, zoomCenter = self.o.mousepoints(event)
                #zoomFactor = 1.0
        else:                 
                zoomCenter = A(gluUnProject(winCenterX, winCenterY, winCenterZ[0][0]))
        self.o.pov = V(-zoomCenter[0], -zoomCenter[1], -zoomCenter[2]) 
        
        ## The following are 2 ways to do the zoom, the first one 
        ## changes view angles, the 2nd one change viewing distance
        ## The advantage for the 1st one is model will not be clipped by 
        ##  near or back clipping planes, and the rubber band can be 
        ## always shown. The disadvantage: TBD
        zoomFactor *= self.o.getZoomFactor()
        self.o.setZoomFactor(zoomFactor)
        
        ###Change viewing distance to do zoom
        ##self.o.scale *= zoomFactor
        
        self.o.paintGL()
        self.rbw = False
        self.o.mode.Done(self.o.prevMode)

    def Draw(self):
        basicMode.Draw(self)   
        if self.rbw: self.RBWdraw() # Draw rubber band window.
        self.o.assy.draw(self.o)
        
    def RBWdraw(self):
        """Draw the rubber-band window.
        """
        drawer.drawrectangle(self.pickLineStart, self.pickLinePrev,
                                 self.o.up, self.o.right, self.rbwcolor)
          
    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Done', self.Done),
         ]

    pass # end of class zoomMode