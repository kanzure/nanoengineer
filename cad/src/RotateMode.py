# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Rotate mode functionality.

@author:    Mark Sims
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
"""

from ArrangementMode import TemporaryCommand_Overdrawing

# == GraphicsMode part

class RotateMode_GM( TemporaryCommand_Overdrawing.GraphicsMode_class ):
    """
    Custom GraphicsMode for use as a component of RotateMode.
    """
    def leftDown(self, event):
        self.glpane.SaveMouse(event)
        self.glpane.trackball.start(self.glpane.MousePos[0],
                                    self.glpane.MousePos[1])
        self.picking = False
        return
        
    def leftDrag(self, event):
        self.glpane.SaveMouse(event)
        q = self.glpane.trackball.update(self.glpane.MousePos[0],
                                         self.glpane.MousePos[1])
        self.glpane.quat += q 
        self.glpane.gl_update()
        self.picking = False
        return
        
    def update_cursor_for_no_MB(self): # Fixes bug 1638. Mark 3/12/2006
        """
        Update the cursor for 'Rotate' mode.
        """
        self.glpane.setCursor(self.win.RotateCursor)
        return

    pass

# == Command part

class RotateMode(TemporaryCommand_Overdrawing): # TODO: rename to RotateTool or RotateCommand or TemporaryCommand_Rotate or ...
    """
    Encapsulates the Rotate Tool functionality.
    """
    
    # class constants
    modename = 'ROTATE'
    default_mode_status_text = "Tool: Rotate"

    GraphicsMode_class = RotateMode_GM

    def init_gui(self):
        # Toggle on the Rotate Tool icon
        self.win.rotateToolAction.setChecked(1)
    
    def restore_gui(self):
        # Toggle off the Rotate Tool icon
        self.win.rotateToolAction.setChecked(0)

    pass

# end
