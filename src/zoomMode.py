# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
zoomMode.py -- zoom mode.

$Id$
"""
__author__ = "Mark"

from modes import *
#import preferences

class zoomMode(basicMode):

    # class constants
    #
    #  We need to mimic the previous mode, including the background color, dashboard
    # and default_mode_status_text.
    # 
    backgroundColor = 0.5, 0.5, 0.5
    modename = 'ZOOM'
    default_mode_status_text = "Mode: Zoom"  # This should be set to the previous mode's text
    
    # flag indicating when to draw the rubber band window.
    rbw = False
    selSense = 1 # Color of rubber band window.

    # no __init__ method needed
    
    # methods related to entering this mode
    
    def Enter(self):
        # Set background color to the previous mode's bg color
        self.backgroundColor = self.o.prevModeColor
        basicMode.Enter(self)

    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        self.OldCursor = QCursor(self.o.cursor())
        self.o.setCursor(self.w.ZoomCursor)
        
        # Get the previous mode's dashboard widget and show it.
        self.getDashboard() 
        self.dashboard.show()
        
        if self.o.prevMode == "DEPOSIT":
            self.w.setDisplay(diTUBES)
            
# methods related to exiting this mode

    def haveNontrivialState(self):
        return False

    def StateDone(self):
        return None
    
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.o.setCursor(self.OldCursor) # restore cursor
        self.dashboard.hide()

    # Dashboard methods for zoomMode

    def getDashboard(self):
        """Return the dashboard widget for the previous mode.
        """
        prevMode = self.o.prevMode
        if prevMode == 'SELECTMOLS':
            self.dashboard = self.w.selectMolDashboard
        elif prevMode == 'SELECTATOMS':
            self.dashboard = self.w.selectAtomsDashboard
        elif prevMode == 'MODIFY':
            self.dashboard = self.w.moveMolDashboard
        elif prevMode == 'DEPOSIT':
            self.dashboard = self.w.depositAtomDashboard
        elif prevMode == 'MOVIE':
            self.dashboard = self.w.moviePlayerDashboard
        elif prevMode == 'COOKIE':
            self.dashboard = self.w.cookieCutterDashboard
            
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
        self.o.mode.Done()
        self.rbw = False
        self.o.setMode(self.o.prevMode)


    def Draw(self):
        basicMode.Draw(self)   
        if self.rbw: self.pickdraw() # Draw rubber band window.
        if self.o.prevMode == 'COOKIE':
                cookieObj = self.o._find_mode(self.o.prevMode)
                cookieObj.griddraw()
                if cookieObj.sellist: cookieObj.pickdraw()
                if cookieObj.o.shape: 
                       cookieObj.o.shape.draw(cookieObj.o)
        else:        
                self.o.assy.draw(self.o)
        
        if self.o.prevMode == "DEPOSIT":
                self.o._find_mode(self.o.prevMode).surface()
          


    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Done', self.Done),
         ]

    pass # end of class zoomMode