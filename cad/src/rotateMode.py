# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
rotateMode.py -- rotate mode.

$Id$
"""
__author__ = "Mark"

from panMode import panlikeMode

class rotateMode(panlikeMode):

    # class constants
    modename = 'ROTATE'
    default_mode_status_text = "Tool: Rotate" # Changed 'Mode' to 'Tool'. Fixes bug 1298. mark 060323

    def init_gui(self):
        self.w.rotateToolAction.setChecked(1) # toggle on the Rotate Tool icon
        self.o.setCursor(self.w.RotateCursor)
        self.w.rotateDashboard.show()
    
    def restore_gui(self):
        self.w.rotateToolAction.setChecked(0) # toggle off the Rotate Tool icon
        self.w.rotateDashboard.hide()

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

    def update_cursor_for_no_MB(self): # Fixes bug 1638. mark 060312.
        """
        Update the cursor for 'Rotate' mode.
        """
        self.o.setCursor(self.w.RotateCursor)
         
    pass

# end
