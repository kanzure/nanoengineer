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
        self.o.modetab[self.modename] = self

    def setMode(self):
        self.o.mode = self
        pass
    
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

    def middleDrag(self, event):
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1])
        self.o.quat += q 
        self.o.paintGL()

    def middleUp(self, event):
        pass
    
    def middleShiftDown(self, event):
        self.o.SaveMouse(event)
    
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
    
    def middleCntlDrag(self, event):
        """push scene away (mouse goes up) or pull (down)
           rotate around vertical axis (left-right)

        """
        self.SaveMouse(event)
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


###########################################################################
    
class selectMode(basicMode):
    def __init__(self, glpane):
        basicMode.__init__(self, glpane, 'SELECT')
        self.backgroundColor = 217/256.0, 214/256.0, 160/256.0
        self.gridColor = (0.0, 0.0, 0.6)
        self.makeMenus()

    def leftDown(self, event):
        self.selSense = 1
        self.StartPick(event)
    
    def leftShiftDown(self, event):
        self.selSense = 0
        self.StartPick(event)

    def leftCntlDown(self, event):
        self.selSense = 2
        self.StartPick(event)


    def StartPick(self, event):
        """Start a selection curve
        """

        self.o.picking = 1
        self.o.SaveMouse(event)
        self.o.prevvec = None

        p1, p2 = self.o.mousepoints(event)
        self.o.normal = self.o.lineOfSight
        self.o.sellist = [p1]
        self.o.backlist = [p2]
        self.o.pickLineStart = self.o.pickLinePrev = p1
        self.o.pickLineLength = 0.0

    
    def leftDrag(self, event):
        self.ContinPick(event)
    
    def leftShiftDrag(self, event):
        self.ContinPick(event)
    
    def leftCntlDrag(self, event):
        self.ContinPick(event)

    def ContinPick(self, event):
        """Add another segment to a selection curve
        """
        if not self.o.picking: return
        p1, p2 = self.o.mousepoints(event)

        self.o.sellist += [p1]
        self.o.backlist += [p2]
        netdist = vlen(p1-self.o.pickLineStart)

        self.o.pickLineLength += vlen(p1-self.o.pickLinePrev)
        self.o.selLassRect = self.o.pickLineLength < 2*netdist

        self.o.pickLinePrev = p1
        self.o.assy.updateDisplays()

    
    def leftUp(self, event):
        self.EndPick(event)
    
    def leftShiftUp(self, event):
        self.EndPick(event)
    
    def leftCntlUp(self, event):
        self.EndPick(event)

    def EndPick(self, event):
        """Close a selection curve and do the selection
        """
        if not self.o.picking: return
        self.o.picking = False

        p1, p2 = self.o.mousepoints(event)

        if self.o.pickLineLength/self.o.scale < 0.03:
            # didn't move much, call it a click
            if self.o.selSense == 0: self.o.assy.unpick(p1,norm(p2-p1))
            if self.o.selSense == 1: self.o.assy.pick(p1,norm(p2-p1))
            if self.o.selSense == 2: self.o.assy.onlypick(p1,norm(p2-p1))
            self.o.assy.updateDisplays()
            return

        self.o.sellist += [p1]
        self.o.sellist += [self.o.sellist[0]]
        self.o.backlist += [p2]
        self.o.backlist += [self.o.backlist[0]]
        self.o.shape=shape(self.o.right, self.o.up, self.o.lineOfSight)
        eyeball = (-self.o.quat).rot(V(0,0,6*self.o.scale)) - self.o.pov
        if self.o.selLassRect:
            self.o.shape.pickrect(self.o.backlist[0], p2, -self.o.pov, self.o.selSense,
                             (not self.o.ortho) and eyeball)
        else:
            self.o.shape.pickline(self.o.backlist, -self.o.pov, self.o.selSense,
                             (not self.o.ortho) and eyeball)
        self.o.shape.select(self.o.assy)

        self.o.sellist = []

        self.o.assy.updateDisplays()

    def leftDouble(self, event):
        """Select the part containing the atom the cursor is on.
        """
        (p1, p2) = self.o.mousepoints(event)

        self.o.assy.pickpart(p1,norm(p2-p1))

        self.o.assy.updateDisplays()

    def Draw(self):
        self.griddraw()
        if self.o.sellist: self.o.pickdraw()
        if self.o.assy: self.o.assy.draw(self.o)

    def griddraw(self):
        """ draws point-of-view axes
        """
        drawer.drawaxes(5,-self.o.pov)

    def makeMenus(self):
        self.Menu1 = self.makemenu([('All', self.o.assy.selectAll),
                                    ('None', self.o.assy.selectNone),
                                    ('Invert', self.o.assy.selectInvert),
                                    ('Connected', self.o.assy.selectConnected),
                                    ('Doubly', self.o.assy.selectDoubly)])
        
        self.Menu2 = self.makemenu([('Kill', self.o.assy.kill),
                                    ('Copy', self.o.assy.copy),
                                    ('Move', self.move),
                                    ('Bond', self.o.assy.Bond),
                                    ('Unbond', self.o.assy.Unbond),
                                    ('Stretch', self.o.assy.Stretch)])
        
        self.Menu3 = self.makemenu([('Default', self.o.dispDefault),
                                    ('Lines', self.o.dispLines),
                                    ('CPK', self.o.dispCPK),
                                    ('VdW', self.o.dispVdW),
                                    None,
                                    ('Invisible', self.o.dispInvis),
                                    None,
                                    ('Color', self.o.dispColor)])

    def move(self):
        # go into move mode
        self.o.setMode('MODIFY')

############################################################################
        

class cookieMode(basicMode):
    def __init__(self, glpane):
        basicMode.__init__(self, glpane, 'COOKIE')
        self.backgroundColor = 103/256.0, 124/256.0, 53/256.0
        self.gridColor = 223/256.0, 149/256.0, 0/256.0
        self.savedOrtho = 0


    def setMode(self):
        basicMode.setMode(self)
        
        self.savedOrtho = self.o.ortho

        self.o.ortho = 1

        self.cookieQuat = None

        self.Rubber = None
        self.o.snap2trackball()

    def Flush(self):
        pass

    def Done(self):
        if self.o.shape:
            self.o.assy.molmake(self.o.shape)
            self.o.shape = None

        self.o.ortho = self.savedOrtho
        self.o.setMode('SELECT')

    def leftDown(self, event):
        self.selSense = 1
        self.StartDraw(event)
    
    def leftShiftDown(self, event):
        self.selSense = 0
        self.StartDraw(event)

    def leftCntlDown(self, event):
        self.selSense = 2
        self.StartDraw(event)

    def StartDraw(self, event):
        """Start a selection curve
        """
        if self.Rubber: return
        self.o.picking = 1
        self.o.SaveMouse(event)
        self.o.prevvec = None
        self.cookieQuat = Q(self.o.quat)

        p1, p2 = self.o.mousepoints(event)
        self.o.normal = self.o.lineOfSight
        self.o.sellist = [p1]
        self.o.backlist = [p2]
        self.o.pickLineStart = self.o.pickLinePrev = p1
        self.o.pickLineLength = 0.0
    
    def leftDrag(self, event):
        self.ContinDraw(event)
    
    def leftShiftDrag(self, event):
        self.ContinDraw(event)
    
    def leftCntlDrag(self, event):
        self.ContinDraw(event)

    def ContinDraw(self, event):
        """Add another segment to a selection curve
        """
        if not self.o.picking: return
        if self.Rubber: return
        p1, p2 = self.o.mousepoints(event)

        self.o.sellist += [p1]
        self.o.backlist += [p2]
        netdist = vlen(p1-self.o.pickLineStart)

        self.o.pickLineLength += vlen(p1-self.o.pickLinePrev)
        self.o.selLassRect = self.o.pickLineLength < 2*netdist

        self.o.pickLinePrev = p1
        self.o.assy.updateDisplays()
    
    def leftUp(self, event):
        self.EndDraw(event)
    
    def leftShiftUp(self, event):
        self.EndDraw(event)
    
    def leftCntlUp(self, event):
        self.EndDraw(event)


    def EndDraw(self, event):
        """Close a selection curve and do the selection
        """
        p1, p2 = self.o.mousepoints(event)

        if self.o.pickLineLength/self.o.scale < 0.03:
            # didn't move much, call it a click
            if not (len(self.o.sellist)>1 and vlen(p1-self.o.sellist[0])<1):
                self.o.sellist += [p1]
                self.o.backlist += [p2]

                self.o.selLassRect = 0

                self.Rubber = True

                return

        self.Rubber = 0
        self.o.sellist += [p1]
        self.o.sellist += [self.o.sellist[0]]
        self.o.backlist += [p2]
        self.o.backlist += [self.o.backlist[0]]
        if not self.o.shape: self.o.shape=shape(self.o.right, self.o.up, self.o.lineOfSight,
                                      Slab(-self.o.pov, self.o.lineOfSight, 7))
        eyeball = (-self.o.quat).rot(V(0,0,6*self.o.scale)) - self.o.pov
        if self.o.selLassRect:
            self.o.shape.pickrect(self.o.backlist[0], p2, -self.o.pov, self.o.selSense)
        else:
            self.o.shape.pickline(self.o.backlist, -self.o.pov, self.o.selSense)
        self.o.sellist = []

        self.o.assy.updateDisplays()

    def middleUp(self,event):
        if self.cookieQuat:
            self.o.quat = Q(self.cookieQuat)
            self.o.paintGL()
        else: self.o.snap2trackball()

    def bareMotion(self, e):
        if self.Rubber:
            p1, p2 = self.o.mousepoints(e)
            try: self.o.sellist[-1]=p1
            except: print self.o.sellist
            self.o.paintGL()

    def Draw(self):
        self.griddraw()
        if self.o.sellist: self.o.pickdraw()
        if self.o.shape: self.o.shape.draw(self.o)

    def griddraw(self):
        """Assigned as griddraw for a diamond lattice grid that is fixed in
        space but cut out into a slab one nanometer thick parallel to the screen
        (and is equivalent to what the cookie-cutter will cut).
        """
        # the grid is in modelspace but the clipping planes are in eyespace
        glPushMatrix()
        glColor3fv(self.gridColor)
        q = self.o.quat
        glTranslatef(-self.o.pov[0], -self.o.pov[1], -self.o.pov[2])
        glRotatef(- q.angle*180.0/pi, q.x, q.y, q.z)
        glClipPlane(GL_CLIP_PLANE0, (0.0, 0.0, 1.0, 6.0))
        glClipPlane(GL_CLIP_PLANE1, (0.0, 0.0, -1.0, 0.1))
        glEnable(GL_CLIP_PLANE0)
        glEnable(GL_CLIP_PLANE1)
        glPopMatrix()
        drawer.drawgrid(1.5*self.o.scale, -self.o.pov)
        glDisable(GL_CLIP_PLANE0)
        glDisable(GL_CLIP_PLANE1)
        drawer.drawaxes(5,-self.o.pov)


###########################################################################
    
class modifyMode(basicMode):
    def __init__(self, glpane):
        basicMode.__init__(self, glpane, 'MODIFY')
        self.backgroundColor = 255/256.0, 174/256.0, 247/256.0
        self.gridColor = 52/256.0, 129/256.0, 26/256.0
        self.makeMenus()

    def Done(self):
        self.o.setMode('SELECT')

    def leftDown(self, event):
        """Move the selected object(s) in the plane of the screen following
        the mouse.
        """
        self.o.SaveMouse(event)

    def leftDrag(self, event):
        """Move the selected object(s) in the plane of the screen following
        the mouse.
        """
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        move = self.o.scale * deltaMouse/(h*0.5)
        move = dot(move, self.o.quat.matrix3)
        self.o.assy.movesel(move)
        self.o.assy.updateDisplays()
        self.o.SaveMouse(event)

     
    def leftShiftDown(self, event):
        """Setup a trackball action on each selected part.
        """
        self.o.SaveMouse(event)
        self.o.trackball.start(self.o.MousePos[0],self.o.MousePos[1])

   
    def leftShiftDrag(self, event):
        """Do an incremental trackball action on each selected part.
        """
        self.o.SaveMouse(event)
        q = self.o.trackball.update(self.o.MousePos[0],self.o.MousePos[1],
                                    self.o.quat)
        self.o.assy.rotsel(q)
        self.o.assy.updateDisplays()
    
    def leftCntlDown(self, event):
        """ Set up for sliding or rotating the selected part
        """
        self.o.SaveMouse(event)
        self.Zorg = self.o.MousePos
        self.Zq = []
        self.Zmov = []
        for mol in self.o.assy.selmols:
            self.Zq += [(mol, Q(mol.quat))]
            self.Zmov += [(mol, mol.center)]
        # start in ambivalent mode
        self.Zunlocked = 1
        self.ZRot = 0
    
    def leftCntlDrag(self, event):
        """move part along its axis (mouse goes up or down)
           rotate around its axis (left-right)

        """
        self.o.SaveMouse(event)
        dx,dy = (self.o.MousePos - self.Zorg) * V(1,-1)
        ax,ay = abs(V(dx,dy))
        if self.Zunlocked:
            self.Zunlocked = ax<10 and ay<10
            if ax>ay:
                # rotating
                for mol, c in self.Zmov:
                    mol.center = c
                self.ZRot = 1
            else:
                # zooming
                for mol, q in self.Zq:
                    mol.quat = Q(q)
                self.ZRot = 0
        if self.ZRot:
            w=self.o.width+0.0
            for mol, q in self.Zq:
                mol.quat = q+Q(mol.getaxis(),2*pi*dx/w)
        else:
            h=self.o.height+0.0
            for mol, c in self.Zmov:
                mol.center = c+mol.getaxis()*self.o.scale * dy/(h*0.5)
        self.o.assy.updateDisplays()

  
    def leftUp(self, event):
        pass
    
    def leftShiftUp(self, event):
        pass

    
    def leftCntlUp(self, event):
        pass


    def leftDouble(self, event):
        self.Done()
        
    def Draw(self):
        self.griddraw()
        if self.o.sellist: self.o.pickdraw()
        if self.o.assy: self.o.assy.draw(self.o)

    def griddraw(self):
        """ draws point-of-view axes
        """
        drawer.drawaxes(5,-self.o.pov)

    def makeMenus(self):
        self.Menu1 = self.makemenu([('All', self.o.assy.selectAll),
                                    ('None', self.o.assy.selectNone),
                                    ('Invert', self.o.assy.selectInvert),
                                    ('Connected', self.o.assy.selectConnected),
                                    ('Doubly', self.o.assy.selectDoubly)])
        
        self.Menu2 = self.makemenu([('Kill', self.o.assy.kill),
                                    ('Copy', self.o.assy.copy),
                                    ('Move', self.move),
                                    ('Bond', self.o.assy.Bond),
                                    ('Unbond', self.o.assy.Unbond),
                                    ('Stretch', self.o.assy.Stretch)])
        
        self.Menu3 = self.makemenu([('Default', self.o.dispDefault),
                                    ('Lines', self.o.dispLines),
                                    ('CPK', self.o.dispCPK),
                                    ('VdW', self.o.dispVdW),
                                    None,
                                    ('Invisible', self.o.dispInvis),
                                    None,
                                    ('Color', self.o.dispColor)])

    def move(self):
        # go into move mode
        pass
