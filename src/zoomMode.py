# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
zoomMode.py -- zoom mode.

$Id$
"""
__author__ = "Mark"

from modes import *

class zoomMode(basicMode):

    # class constants
    #
    #  We need to mimic the previous mode, including the background color, dashboard
    # and default_mode_status_text.
    # 
    backgroundColor = 189/255.0, 228/255.0, 238/255.0  # This should be prev mode bg color
    modename = 'ZOOM'
    default_mode_status_text = "Mode: Zoom"  # This should be set to the previous mode's text

    # flag indicating when to draw the rubber band window.
    rbw = False
    selSense = 1 # Color of rubber band window.
    
    # no __init__ method needed
    
    # methods related to entering this mode
    
    def Enter(self): # bruce 040922 split setMode into Enter and init_gui (fyi)
        basicMode.Enter(self)

    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        self.OldCursor = QCursor(self.o.cursor())
        self.o.setCursor(self.w.ZoomCursor)
        
        # There is no dashboard for zoomMode.  
        # We want to display the previous mode's dashboard
        # This should really be addressed in modes.py.
#        self.w.previousMode.Dashboard.show()
        
# methods related to exiting this mode

    def haveNontrivialState(self):
        return False

    def StateDone(self):
        return None
    
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.o.setCursor(self.OldCursor) # restore cursor

    # No dashboard methods for zoomMode

    # mouse and key events

    def leftDown(self, event):
        self.rbw = True
        p1, p2 = self.o.mousepoints(event, 0.01)
        print "zoom start: p1 = ", p1, ", p2 = ", p2
        self.o.normal = self.o.lineOfSight
        self.sellist = [p1]
        self.o.backlist = [p2]
        self.pickLineStart = self.pickLinePrev = p1
    
    def leftDrag(self, event):

        p1, p2 = self.o.mousepoints(event, 0.01)
        self.o.backlist += [p2]
        self.pickLinePrev = p1
        self.o.paintGL()

    def leftUp(self, event):
        
        p1, p2 = self.o.mousepoints(event, 0.01)
        print "backlist[0] = ", self.o.backlist[0]
        print "zoom finished: p1 = ", p1, ", p2 = ", p2
        dx = abs(p2[0]-self.o.backlist[0][0]) * .5
        dy = abs(p2[1]-self.o.backlist[0][1]) * .5
        print "dx = ", dx, ", dy = ", dy
        self.o.scale = max(dx,dy)
#            self.glpane.pov = V(0.0, 0.0, 0.0) # Point of view
        print "scale = ",self.o.scale
        print "pov = ",self.o.pov
        self.o.paintGL()
        self.o.mode.Done()
        self.rbw = False
        return


    def Draw(self):
        basicMode.Draw(self)   
        if self.rbw: self.pickdraw() # Draw rubber band window.
        self.o.assy.draw(self.o)

    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Done', self.Done),
         ]

    pass # end of class zoomMode