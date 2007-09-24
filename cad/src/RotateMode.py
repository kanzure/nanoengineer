# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Encapsulates rotate mode functionality.

@author:    Mark Sims
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
"""

from panMode import panlikeMode

class rotateMode(panlikeMode):
    """
    Encapsulates rotate mode functionality.
    """
    
    modename = 'ROTATE'

    # Changed 'Mode' to 'Tool'. Fixes bug 1298. Mark 3/23/2006
    default_mode_status_text = "Tool: Rotate"

    def init_gui(self):
        # Toggle on the Rotate Tool icon
        self.win.rotateToolAction.setChecked(1)
        self.glpane.setCursor(self.win.RotateCursor)
    
    def restore_gui(self):
        # Toggle off the Rotate Tool icon
        self.win.rotateToolAction.setChecked(0)

    def leftDown(self, event):
        self.glpane.SaveMouse(event)
        self.glpane.trackball.start(self.glpane.MousePos[0],
                                    self.glpane.MousePos[1])
        self.picking = False

    def leftDrag(self, event):
        self.glpane.SaveMouse(event)
        q = self.glpane.trackball.update(self.glpane.MousePos[0],
                                         self.glpane.MousePos[1])
        self.glpane.quat += q 
        self.glpane.gl_update()
        self.picking = False

    def update_cursor_for_no_MB(self): # Fixes bug 1638. Mark 3/12/2006
        """
        Update the cursor for 'Rotate' mode.
        """
        self.glpane.setCursor(self.win.RotateCursor)

