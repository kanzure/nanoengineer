# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
panMode.py -- pan mode.

$Id$
"""
__author__ = "Mark"

from modes import *

class panMode(basicMode):

    # class constants
    backgroundColor = 0.5, 0.5, 0.5
    modename = 'PAN'
    default_mode_status_text = "Mode: Pan"

    # no __init__ method needed
    
    # methods related to entering this mode
    
    def Enter(self):
        basicMode.Enter(self)
        # Set background color to the previous mode's bg color
        bg = self.backgroundColor = self.o.prevModeColor

    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        self.OldCursor = QCursor(self.o.cursor())
        self.w.panToolAction.setOn(1) # toggle on the Pan Tool icon
        self.o.setCursor(self.w.MoveCursor)
        self.w.panDashboard.show()
            
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
        self.w.panToolAction.setOn(0) # toggle off the Pan Tool icon
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
        self.o.setCursor(self.OldCursor) # restore cursor
        self.w.panDashboard.hide()

    # mouse and key events
    
    def leftDown(self, event):
        """
        """
        self.o.SaveMouse(event)
        self.picking = 0

    def leftDrag(self, event):
        """Move point of view so that objects appear to follow
        the mouse on the screen.
        """
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        #move = self.o.quat.unrot(self.o.scale * deltaMouse/(h*0.5))
        
        # bruce comment 040908, about josh code: 'move' is mouse
        # motion in model coords. We want center of view, -self.pov,
        # to move in opposite direction as mouse, so that after
        # recentering view on that point, objects have moved with
        # mouse.
        
        ### Huaicai 1/26/05: delta Xe, delta Ye  depend on Ze, here
        ### Ze is just an estimate, so Xe and Ye are estimates too, but
        ### they seems more accurate than before. To accurately 
        ### calculate it, we need to find a depth value for a point on 
        ### the model.
        Ze = 2.0*self.o.near*self.o.far*self.o.scale/(self.o.near+self.o.far)
        tY = (self.o.zoomFactor*Ze)*2.0/h
        
        move = self.o.quat.unrot(deltaMouse*tY)
        self.o.pov += move
        self.o.gl_update()
        self.o.SaveMouse(event)
        self.picking = 0

    def keyPress(self,key):
        # ESC - Exit pan mode.
        if key == Qt.Key_Escape: 
            self.Done()

    def Draw(self):
        basicMode.Draw(self)   
        self.o.assy.draw(self.o)
        
    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Done),
            ('Done', self.Done),
         ]
         
    pass # end of class panMode
