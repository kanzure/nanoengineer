from qt import *
from qtgl import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLE import *
import math

import os,sys
from time import time
from VQT import *
import drawer
from shape import *
from assembly import *
import re
from constants import *


class basicMode:
    """subclass this class to provide a new mode of interaction for the GLPane
    """
    def __init__(self, glpane, name = 'BASIC'):
        self.modename=name
        self.o = glpane
        self.w = glpane.win
        self.o.modetab[self.modename] = self
        self.sellist = []
        self.selLassRect = 0

    def setMode(self):
        self.prevmode = self.o.mode
        self.o.mode = self
        pass

    def Restart(self):
        print self.modename,  "Restart not implemented yet"

    def Flush(self):
        print self.modename, "Flush not implemented yet"

    def Backup(self):
        print self.modename, "Backup not implemented yet"

    def Done(self):
        self.o.setMode(self.prevmode.modename)
    
    def Draw(self):
        drawer.drawaxes(5,-self.o.pov)

    def leftDown(self, event):
        pass
    
    def leftDrag(self, event):
        pass
    
    def leftUp(self, event):
        pass
    
    def leftShiftDown(self, event):
        pass
    
    def leftShiftDrag(self, event):
        pass
    
    def leftShiftUp(self, event):
        pass
    
    def leftCntlDown(self, event):
        pass
    
    def leftCntlDrag(self, event):
        pass
    
    def leftCntlUp(self, event):
        pass
    
    def leftDouble(self, event):
        pass

    # these are the same for all modes
    def middleDown(self, event):
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])
        self.picking = 0

    def middleDrag(self, event):
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1])
        self.o.quat += q 
        self.o.paintGL()
        self.picking = 0

    def middleUp(self, event):
        pass
    
    def middleShiftDown(self, event):
        self.o.SaveMouse(event)
        self.picking = 0
    
    def middleShiftDrag(self, event):
        """Move point of view so that objects appear to follow
        the mouse on the screen.
        """
        w=self.o.width+0.0 
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        move = self.o.scale * deltaMouse/(h*0.5)
        move = dot(move, self.o.quat.matrix3)
        self.o.pov += move
        self.o.paintGL()
        self.o.SaveMouse(event)
        self.picking = 0
    
    def middleShiftUp(self, event):
        pass
    
    def middleCntlDown(self, event):
        """ Set up for zooming or rotating
        """
        self.o.SaveMouse(event)
        self.o.Zorg = self.o.MousePos
        self.o.Zq = Q(self.o.quat)
        self.o.Zscale = self.o.scale
        # start in ambivalent mode
        self.o.Zunlocked = 1
        self.o.ZRot = 0
        self.picking = 0
    
    def middleCntlDrag(self, event):
        """push scene away (mouse goes up) or pull (down)
           rotate around vertical axis (left-right)

        """
        self.o.SaveMouse(event)
        dx,dy = (self.o.MousePos - self.o.Zorg) * V(1,-1)
        ax,ay = abs(V(dx,dy))
        if self.o.Zunlocked:
            self.o.Zunlocked = ax<10 and ay<10
            if ax>ay:
                # rotating
                self.o.scale = self.o.Zscale
                self.o.ZRot = 1
            else:
                # zooming
                self.o.quat = Q(self.o.Zq)
                self.o.ZRot = 0
        if self.o.ZRot:
            w=self.o.width+0.0
            self.o.quat = self.o.Zq + Q(V(0,1,0),2*pi*dx/w)
        else:
            h=self.o.height+0.0
            self.o.scale = self.o.Zscale*10.0**(0.5*dy/h)
                
        self.picking = 0
        self.o.paintGL()

    def middleCntlUp(self, event):
        pass
    
    def middleDouble(self, event):
        pass
    
    def rightDown(self, event):
        self.Menu1.popup(event.globalPos(),3)
    
    def rightDrag(self, event):
        pass
    
    def rightUp(self, event):
        pass
    
    def rightShiftDown(self, event):
        self.Menu2.popup(event.globalPos(),3)
    
    def rightShiftDrag(self, event):
        pass
    
    def rightShiftUp(self, event):
        pass
    
    def rightCntlDown(self, event):
        self.Menu3.popup(event.globalPos(),3)
    
    def rightCntlDrag(self, event):
        pass
    
    def rightCntlUp(self, event):
        pass
    
    def rightDouble(self, event):
        pass
    
    def bareMotion(self, event):
        pass

    def Wheel(self, event):
        but = event.state()

        dScale = 1.0/1200.0
        if but & shiftButton: dScale *= 0.5
        if but & cntlButton: dScale *= 2.0
        self.o.scale *= 1.0 + dScale * event.delta()
        self.o.paintGL()
    
    def Done(self):
        pass
    
    def Flush(self):
        pass

    def makemenu(self, lis):

        win = self.o

        menu = QPopupMenu(win)
    
        for m in lis:
            if m:
            
                act = QAction(win,m[0]+'Action')
                act.setText(win.trUtf8(m[0]))
                act.setMenuText(win.trUtf8(m[0]))
                
                act.addTo(menu)
                win.connect(act, SIGNAL("activated()"), m[1])
            else:
                menu.insertSeparator()
        
        return menu


    def pickdraw(self):
        """Draw the (possibly unfinished) freehand selection curve.
        """
        color = logicColor(self.selSense)
        pl = zip(self.sellist[:-1],self.sellist[1:])
        for pp in pl:
            drawer.drawline(color,pp[0],color,pp[1])
        if self.selLassRect:
            drawer.drawrectangle(self.pickLineStart, self.pickLinePrev,
                                 self.o.up, self.o.right, color)


