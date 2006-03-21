# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
rotateMode.py -- rotate mode.

$Id$
"""
__author__ = "Mark"

from modes import *

class rotateMode(basicMode):

    # class constants
    backgroundColor = 0.5, 0.5, 0.5
    modename = 'ROTATE'
    default_mode_status_text = "Mode: Rotate"

    # no __init__ method needed
    
    # methods related to entering this mode
    
    def Enter(self):
        basicMode.Enter(self)
        # Set background color to the previous mode's bg color
        self.backgroundColor = self.o.prevModeColor
        self.backgroundGradient = self.o.prevModeGradient
        self.o.setDisplay(self.o.prevModeDisplay)  # Fixes bug 1489. mark 060215.

    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        self.w.rotateToolAction.setOn(1) # toggle on the Rotate Tool icon
        self.o.setCursor(self.w.RotateCursor)
        self.w.rotateDashboard.show()
            
# methods related to exiting this mode

    def haveNontrivialState(self):
        return False

    def StateDone(self):
        return None

    # a safe way for now to override Done:
    def Done(self, new_mode = None):
        """[overrides basicMode.Done; this is deprecated, so doing it here
        is a temporary measure for Alpha, to be reviewed by Bruce ASAP after
        Alpha goes out; see also the removal of Done from weird_to_override
        in modes.py. [bruce and mark 050130]
        """
        ## [bruce's symbol to get him to review it soon: ####@@@@]
        if new_mode is None:
            try:
                m = self.o.prevMode # spelling??
                new_mode = m
            except:
                pass
        return basicMode.Done(self, new_mode)
            
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.w.rotateToolAction.setOn(0) # toggle off the Rotate Tool icon
        self.w.rotateDashboard.hide()

    # mouse and key events
    
    def leftDown(self, event):
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        self.picking = False

    def leftDrag(self, event):
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1])
        self.o.quat += q 
        self.o.gl_update()
        self.picking = False

    def keyPress(self,key):
        # ESC - Exit/cancel rotate mode.
        if key == Qt.Key_Escape:
            self.Done()
            
        basicMode.keyPress(self,key) # Fixes bug 1172. mark 060321

    def Draw(self):
        basicMode.Draw(self)   
        self.o.assy.draw(self.o)
         
    def update_cursor_for_no_MB(self): # Fixes bug 1638. mark 060312.
        '''Update the cursor for 'Rotate' mode.
        '''
        self.o.setCursor(self.w.RotateCursor)
         
    pass # end of class rotateMode