# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Pan mode functionality.

@author:    Mark Sims
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
"""

from ArrangementMode import ArrangementMode


class PanMode(ArrangementMode):
    """
    Encapsulates the Pan tool functionality.
    """

    # == Command part
    
    # class constants
    
    modename = 'PAN'
    default_mode_status_text = "Tool: Pan"

    def init_gui(self):
        self.win.panToolAction.setChecked(1) # toggle on the Pan Tool icon
        # bruce 071012 see if i can remove this setCursor, hoping it's redundant with update_cursor_for_no_MB:
##        self.glpane.setCursor(self.win.MoveCursor)
        return    
        
    def restore_gui(self):
        self.win.panToolAction.setChecked(0) # toggle off the Pan Tool icon
    
    # == GraphicsMode part
    
    def leftDown(self, event):
        """
        Event handler for LMB press event.
        """
        # Setup pan operation
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)        
##        self.startpt = self.movingPoint
##            # REVIEW: is startpt needed? if so, document why. [bruce comment 071012]
        return
        
    def leftDrag(self, event):
        """
        Event handler for LMB drag event.
        """
        point = self.dragto( self.movingPoint, event)
        self.glpane.pov += point - self.movingPoint
        self.glpane.gl_update()
        return
        
    def update_cursor_for_no_MB(self): # Fixes bug 1638. Mark 3/12/2006.
        """
        Update the cursor for 'Pan' mode.
        """
        self.glpane.setCursor(self.win.MoveCursor)

    pass

# end
