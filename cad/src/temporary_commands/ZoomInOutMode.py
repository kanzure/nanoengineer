# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Zoom in/out mode functionality.

@author:    Mark Sims
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL
"""

from Numeric import exp
from temporary_commands.TemporaryCommand import TemporaryCommand_Overdrawing

# == GraphicsMode part

class ZoomInOutMode_GM( TemporaryCommand_Overdrawing.GraphicsMode_class ):
    """
    Custom GraphicsMode for use as a component of ZoomInOutMode.
    """    
    def leftDown(self, event):
        """
        Event handler for LMB press event.
        
        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        # Setup zoom operation
        self.prevY = event.y()
        return
        
    def leftDrag(self, event):
        """
        Event handler for LMB drag event.
        
        @param event: A Qt mouse event.
        @type  event: U{B{QMouseEvent}<http://doc.trolltech.com/4/qmouseevent.html>}
        """
        dScale = .025 # This works nicely. Mark 2008-01-29.
        delta = self.prevY - event.y()
        self.prevY = event.y()
        factor = exp(dScale * delta)
        #print "y, py =", event.y(), self.prevY, ", delta =", delta, ", factor=", factor
        self.glpane.rescale_around_point(factor)
        self.glpane.gl_update()
        return
        
    def update_cursor_for_no_MB(self): # Fixes bug 1638. Mark 3/12/2006.
        """
        Update the cursor for 'Zoom In/Out' mode.
        """
        self.glpane.setCursor(self.win.ZoomInOutCursor)
    
    pass

# == Command part

class ZoomInOutMode(TemporaryCommand_Overdrawing):
    """
    Encapsulates the Zoom In/Out functionality.
    """
    
    # class constants
    
    commandName = 'ZOOMINOUT'
    featurename = "Zoom In/Out Tool"
    from utilities.constants import CL_VIEW_CHANGE
    command_level = CL_VIEW_CHANGE

    GraphicsMode_class = ZoomInOutMode_GM

    def init_gui(self):
        self.win.zoomInOutAction.setChecked(1) # toggle on the Zoom In/Out icon
        return    
        
    def restore_gui(self):
        self.win.zoomInOutAction.setChecked(0) # toggle off the Zoom In/Out icon

    pass

# end
