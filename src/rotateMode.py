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
        # Set background color to the previous mode's bg color
        bg = self.backgroundColor = self.o.prevModeColor

        basicMode.Enter(self)

    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        self.OldCursor = QCursor(self.o.cursor())
        self.o.setCursor(self.w.RotateCursor)
        self.w.rotateDashboard.show()
            
# methods related to exiting this mode

    def haveNontrivialState(self):
        return False

    def StateDone(self):
        return None
    
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.o.setCursor(self.OldCursor) # restore cursor
        self.w.rotateDashboard.hide()

    # mouse and key events
    
    def leftDown(self, event):
        """
        """
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        self.picking = 0

    def leftDrag(self, event):
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1])
        self.o.quat += q 
        self.o.gl_update()
        self.picking = 0

    def keyPress(self,key):
        # ESC - Exit pan mode.
        if key == Qt.Key_Escape: 
            self.o.mode.Done(self.o.prevMode)

    def Draw(self):
        basicMode.Draw(self)   
        self.o.assy.draw(self.o)
        
    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Done', self.Done),
         ]
         
    pass # end of class panMode