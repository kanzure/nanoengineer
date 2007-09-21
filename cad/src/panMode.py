# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
panMode.py -- pan mode.

$Id$
"""
__author__ = "Mark"

from PyQt4.Qt import Qt

from modes import basicMode

class panlikeMode(basicMode): #bruce 070813 split this out
    """
    Common superclass for Pan, Rotate, and Zoom tools.
    """
    ### TODO: rename to be about how it differs semantically in general; refile

    # a safe way for now to override Done:
    def Done(self, new_mode = None):
        """[overrides basicMode.Done; this is deprecated, so doing it here
        is a temporary measure for Alpha, to be reviewed by Bruce ASAP after
        Alpha goes out; see also the removal of Done from weird_to_override
        in modes.py. [bruce and mark 050130]
        """
        ## [bruce's symbol to get him to review it soon: ####@@@@]
        resuming = False
        if new_mode is None:
            try:
                m = self.glpane.prevMode
                new_mode = m
                resuming = True
            except:
                pass
        return basicMode.Done(self, new_mode, resuming = resuming) #bruce 070813 added resuming arg

    def keyPress(self, key):
        # ESC - Exit mode.
        if key == Qt.Key_Escape: 
            self.Done()
        ### REVIEW: else, here?
        basicMode.keyPress(self, key) # Fixes bug 1172. mark 060321

    def Draw(self): ### verify same as in others
        # bruce 070813 revised this to use prevMode -- clean up and commit, and share w/ others
        glpane = self.glpane
        try:
            prevMode = glpane.prevMode # can be mode object or (deprecated and worse, but common) modename string; or None
        except AttributeError:
            prevMode = None
        if prevMode and isinstance(prevMode, basicMode):
            prevMode.Draw() # fixes bug in which it doesn't show the right things for cookie or extrude modes [partly; untested] ####
        else:
            basicMode.Draw(self)   
            self.glpane.assy.draw(self.glpane)
            if prevMode:
                print "should no longer happen: prevMode is not None or a basicMode, but %r" % (prevMode,)
        return

    pass # end of class xxx
    
class panMode(panlikeMode):
    """
    Pan tool.
    """
    
    # class constants
    modename = 'PAN'
    default_mode_status_text = "Tool: Pan" # Changed 'Mode' to 'Tool'. Fixes bug 1298. mark 060323

    def init_gui(self):
        self.win.panToolAction.setChecked(1) # toggle on the Pan Tool icon
        self.glpane.setCursor(self.win.MoveCursor)
        
    def restore_gui(self):
        self.win.panToolAction.setChecked(0) # toggle off the Pan Tool icon
    
    def leftDown(self, event):
        'Event handler for LMB press event.'
        # Setup pan operation
        farQ_junk, self.movingPoint = self.dragstart_using_GL_DEPTH( event)
            #bruce 060316 replaced equivalent old code with this new method            
        self.startpt = self.movingPoint # Used in leftDrag() to compute move offset during drag op.
        
    def leftDrag(self, event):
        'Event handler for LMB drag event.'
        point = self.dragto( self.movingPoint, event) #bruce 060316 replaced old code with dragto (equivalent)
        self.glpane.pov += point - self.movingPoint
        self.glpane.gl_update()
    
    def update_cursor_for_no_MB(self): # Fixes bug 1638. mark 060312.
        '''Update the cursor for 'Pan' mode.
        '''
        self.glpane.setCursor(self.win.MoveCursor)
         
    pass # end of class panMode

# end
