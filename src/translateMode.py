# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
translateMode.py

$Id$

"""

__author__ = "Mark"

from modifyMode import *
from HistoryWidget import redmsg
    
class translateMode(modifyMode):
    "Translates and/or rotates chunks along the 3 cartesian axes"

    # class constants
    modename = 'TRANSLATE'
    default_mode_status_text = "Mode: Translate Chunks"
    moveDelta = 0

    # init_gui handles all the GUI display when entering this mode [mark 041004]
    def init_gui(self):
        self.o.setCursor(self.w.MoveSelectCursor) # load default cursor for MODIFY mode
        
        if self.moveOption == 'TRANSX':
            self.w.transXAction.setOn(1) # toggle on the Translate X icon
        if self.moveOption == 'TRANSY':
            self.w.transYAction.setOn(1) # toggle on the Translate Y icon
        if self.moveOption == 'TRANSZ':
            self.w.transZAction.setOn(1) # toggle on the Translate Z icon
            
        self.w.moveMolDashboard.show() # show the Move Molecules dashboard
        
        self.w.connect(self.w.MoveOptionsGroup, SIGNAL("selected(QAction *)"), self.changeMoveOption)
        
        # This is needed.
        self._getMoveOption()
    
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.w.moveMolDashboard.hide()
        self.w.disconnect(self.w.MoveOptionsGroup, SIGNAL("selected(QAction *)"), self.changeMoveOption)
        
    def keyPress(self,key):
#        print "translateMode: keyPress: key =",key
        pass

    def keyRelease(self,key):
        basicMode.keyRelease(self, key)
        if key == Qt.Key_X or key == Qt.Key_Y or key == Qt.Key_Z: 
#            print "translateMode.keyRelease: returning to Move Chunks mode.  key=",key
            self.w.moveFreeAction.setOn(1) # toggle on the Move Chunks icon
            self.o.setMode('MODIFY')
        
    def leftDown(self, event):
        """ Set up for sliding or rotating the selected chunk(s)
        along an X, Y or Z axis, can have combined motion
        """
        self.o.SaveMouse(event)
        
        self.moveDelta = 0
        
        if self.moveOption == 'TRANSX': 
            ma = V(1,0,0) # X Axis
            self.axis = 'X'
        elif self.moveOption == 'TRANSY': 
            ma = V(0,1,0) # Y Axis
            self.axis = 'Y'
        elif self.moveOption == 'TRANSZ': 
            ma = V(0,0,1) # Z Axis
            self.axis = 'Z'
        else: print "translateMode: Error - unknown moveOption value =", self.moveOption
        
        ma = norm(V(dot(ma,self.o.right),dot(ma,self.o.up)))
        self.Zmat = A([ma,[-ma[1],ma[0]]])
        self.picking = True
        self.dragdist = 0.0
        
    def leftDrag(self, event):
        """move part along its axis (mouse goes up or down)
           rotate around its axis (left-right)
        """
        ##See comments of leftDrag()--Huaicai 3/23/05
        if not self.picking: return

        self.o.setCursor(self.w.MoveRotateMolCursor)
        
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y())
        a =  dot(self.Zmat, deltaMouse)
        dx,dy =  a * V(self.o.scale/(h*0.5), 2*pi/w)
        
        self.moveDelta += dx # Increment move delta
        
        for mol in self.o.assy.selmols:
            if self.moveOption == 'TRANSX': ma = V(1,0,0) # X Axis
            elif self.moveOption == 'TRANSY': ma = V(0,1,0) # Y Axis
            elif self.moveOption == 'TRANSZ': ma = V(0,0,1) # Z Axis
            else: 
                print "translateMode.leftDrag: Error - unknown moveOption value =", self.moveOption
                continue

            mol.move(dx*ma)
            mol.rot(Q(ma,-dy))
        
        # Print status bar msg indicating the current move delta.
        msg = "%s delta: %.2f Angstroms" % (self.axis, self.moveDelta)
        self.w.history.transient_msg(msg)
            
        self.dragdist += vlen(deltaMouse)
        self.o.SaveMouse(event)
        self.o.gl_update()

# end of class translateMode