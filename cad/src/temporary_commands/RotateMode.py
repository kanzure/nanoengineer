# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Rotate mode functionality.

@author:    Mark Sims
@version:   $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL

piotr 080808: added "auto-rotation" feature.
"""

from temporary_commands.TemporaryCommand import TemporaryCommand_Overdrawing
from PyQt4.Qt import Qt, QTimer, SIGNAL

### from utilities.debug import doProfile   ###
### clicked = False                         ###

# == GraphicsMode part
_superclass = TemporaryCommand_Overdrawing.GraphicsMode_class

class RotateMode_GM( TemporaryCommand_Overdrawing.GraphicsMode_class ):
    """
    Custom GraphicsMode for use as a component of RotateMode.
    """
    
    def __init__(self, glpane):
        TemporaryCommand_Overdrawing.GraphicsMode_class.__init__(self, glpane)

        self.auto_rotate = False # set to True when user presses "A" key while
        self.animationTimer = None # time used to animate view
        self.last_quat = None # last quaternion to be used for incremental rotation 
    
    def leftDown(self, event):
        ### global clicked                  ###
        ### clicked = True                  ###
        self.glpane.SaveMouse(event)
        self.glpane.trackball.start(self.glpane.MousePos[0],
                                    self.glpane.MousePos[1])
        
        # piotr 080807: The most recent quaternion to be used for "auto-rotate" 
        # animation, initially set to None, so the animation stops when
        # user pushes down mouse button.
        self.last_quat = None
        
        self.picking = False
        return
        
    def leftDrag(self, event):
        ### global clicked                  ###
        ### if clicked:                     ###
        ###     doProfile(True)             ###
        ###     clicked = False             ###

        self.glpane.SaveMouse(event)
        q = self.glpane.trackball.update(self.glpane.MousePos[0],
                                         self.glpane.MousePos[1])
        self.glpane.quat += q 
        
        # piotr 080807: Remember the most recent quaternion to be used
        # in 'auto_rotate' mode. Do it only if 'auto_rotate' class attribute
        # is True, i.e. when user pressed an "A" key while dragging the mouse.
        if self.auto_rotate:
            self.last_quat = q
                
        self.glpane.gl_update()
        self.picking = False
        return
        
    def leftUp(self, event):
        if self.last_quat:
            # Create and enable animation timer.
            if self.animationTimer is None:
                self.animationTimer  =  QTimer(self.glpane)
                self.win.connect(self.animationTimer, 
                                 SIGNAL('timeout()'), 
                                 self._animationTimerTimeout)
            self.animationTimer.start(20) # use 50 fps for smooth animation
        else:
            # Stop animation if mouse was not dragged.
            if self.animationTimer:
                self.animationTimer.stop()
    
    def _animationTimerTimeout(self):
        if self.last_quat:
            self.glpane.quat += self.last_quat
            self.glpane.gl_update()
    
    def update_cursor_for_no_MB(self): # Fixes bug 1638. Mark 3/12/2006
        """
        Update the cursor for 'Rotate' mode.
        """
        self.glpane.setCursor(self.win.RotateViewCursor)
        return

    def keyPress(self, key):
        if key == Qt.Key_A:
            self.auto_rotate = True
            
        _superclass.keyPress(self, key)
        return
        
    def keyRelease(self, key):
        if key == Qt.Key_A:
            self.auto_rotate = False
            
        _superclass.keyRelease(self, key)
        return
    pass

# == Command part

class RotateMode(TemporaryCommand_Overdrawing): # TODO: rename to RotateTool or RotateCommand or TemporaryCommand_Rotate or ...
    """
    Encapsulates the Rotate Tool functionality.
    """
    
    # class constants
    commandName = 'ROTATE'
    featurename = "Rotate Tool"
    from utilities.constants import CL_VIEW_CHANGE
    command_level = CL_VIEW_CHANGE

    GraphicsMode_class = RotateMode_GM

    def init_gui(self):
        # Toggle on the Rotate Tool icon
        self.win.rotateToolAction.setChecked(1)
    
    def restore_gui(self):
        # Toggle off the Rotate Tool icon
        self.win.rotateToolAction.setChecked(0)
        # Disable auto-rotation.
        self.graphicsMode.last_quat = False
        
    pass

# end
