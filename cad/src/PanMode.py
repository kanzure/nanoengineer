# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Pan mode functionality.

@author:    Mark Sims
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id: $
@license:   GPL
"""

from ArrangementMode import ArrangementMode


class PanMode(ArrangementMode):
    """
    Encapsulates the Pan tool functionality.
    """
    
    # class constants
    modename = 'PAN'
    # Changed 'Mode' to 'Tool'. Fixes bug 1298. Mark 3/23/2006
    default_mode_status_text = "Tool: Pan"

    
    def init_gui(self):
        self.win.panToolAction.setChecked(1) # toggle on the Pan Tool icon
        self.glpane.setCursor(self.win.MoveCursor)
    
        
    def restore_gui(self):
        self.win.panToolAction.setChecked(0) # toggle off the Pan Tool icon
    
        
    def leftDown(self, event):
        """
        Event handler for LMB press event.
        """
        # Setup pan operation
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
        
        # Bruce 3/16/2006 replaced equivalent old code with this new method            
        # Used in leftDrag() to compute move offset during drag op.
        self.startpt = self.movingPoint
        
        
    def leftDrag(self, event):
        """
        Event handler for LMB drag event.
        """
        # Bruce 3/16/2006 replaced old code with dragto (equivalent)
        point = self.dragto( self.movingPoint, event)
        self.glpane.pov += point - self.movingPoint
        self.glpane.gl_update()
    
        
    def update_cursor_for_no_MB(self): # Fixes bug 1638. Mark 3/12/2006.
        """
        Update the cursor for 'Pan' mode.
        """
        self.glpane.setCursor(self.win.MoveCursor)

