# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
Stub file for Extrude mode. For now, this works, but it's almost identical to cookieMode,
except for some textLabel2-related bugs and for a different background color.
-- bruce 040920
"""

# bruce 040920: until MainWindow.ui does the following, I'll do it manually:
# (remove this, and the call to this, when MainWindowUI does the same stuff)
def do_what_MainWindowUI_should_do(self):
        "self should be the main MWSemantics object -- at the moment this is a function, not a method"

        from qt import SIGNAL, QToolBar, QLabel, QLineEdit, QSpinBox

        # 1. connect the mode-entering button to its MWSemantics method 
        self.connect(self.toolsExtrudeAction,SIGNAL("activated()"),self.toolsExtrude)
            # fyi, this is modelled after: 
            # self.connect(self.toolsCookieCutAction,SIGNAL("activated()"),self.toolsCookieCut)

        # 2. make a toolbar to be our dashboard, similar to the cookieCutterToolbar
        # (based on the code for cookieCutterToolbar in MainWindowUI)

        self.extrudeToolbar = QToolBar(QString(""),self,Qt.DockBottom)

        self.extrudeToolbar.setGeometry(QRect(0,0,515,29)) ### will probably be wrong once we modify the contents
        self.extrudeToolbar.setBackgroundOrigin(QToolBar.WidgetOrigin)

        # I'm not sure what's up with textLabel2... it's used in multiple files
        # in ways that look like they'd interfere and/or are partly redundant.
        # So for now, be safe, use a different name.
        # Current behavior -- the label does not show up in the toolbar. (a bug)
        ##self.textLabel2 = QLabel(self.extrudeToolbar,"textLabel2")
        self.textLabel3 = QLabel(self.extrudeToolbar,"textLabel3")

        # these are the wrong actions to add... should cause no harm for now, tho
        self.extrudeToolbar.addSeparator()
        self.ccGraphiteAction.addTo(self.extrudeToolbar)
        self.extrudeToolbar.addSeparator()
        self.orient100Action.addTo(self.extrudeToolbar)
        self.orient110Action.addTo(self.extrudeToolbar)
        self.orient111Action.addTo(self.extrudeToolbar)
        self.extrudeToolbar.addSeparator()
        self.ccAddLayerAction.addTo(self.extrudeToolbar)
        self.extrudeToolbar.addSeparator()

        # ideally these should be known only to the mode, not be members of the main window object... and what we need is different... ok for now
        self.extrudeLineEdit = QLineEdit(self.extrudeToolbar,"extrudeLineEdit")
        self.extrudeSpinBox = QSpinBox(self.extrudeToolbar,"extrudeSpinBox")
        self.extrudeSpinBox.setValue(3) # different than in cookieMode
        
        self.extrudeToolbar.addSeparator()

        # dashboard tools shared with other modes
        self.toolsBackUpAction.addTo(self.extrudeToolbar)
        self.toolsStartOverAction.addTo(self.extrudeToolbar)
        self.toolsDoneAction.addTo(self.extrudeToolbar)
        self.toolsCancelAction.addTo(self.extrudeToolbar)

        # note: python name-mangling would turn __tr, within class MainWindow, into _MainWindow__tr (I think... seems to be right)
        self.extrudeToolbar.setLabel(self._MainWindow__tr("Extrude Mode"))

        # fyi: caller hides the toolbar, we don't need to
        
        return

# ==

from modes import *

class extrudeMode(basicMode):
    def __init__(self, glpane):
        basicMode.__init__(self, glpane, 'EXTRUDE')
        self.backgroundColor = 200/256.0, 100/256.0, 100/256.0 # different than in cookieMode
        self.gridColor = 223/256.0, 149/256.0, 0/256.0
        self.savedOrtho = 0
	self.makeMenus()


    def setMode(self):
        basicMode.setMode(self)
        self.o.pov -= 3.5*self.o.out
        self.savedOrtho = self.o.ortho

        self.o.ortho = 1

        self.extrudeQuat = None

        self.Rubber = None
        self.o.snap2trackball()

        self.w.extrudeToolbar.show()

    def Flush(self):
        self.o.shape = None

        self.w.extrudeToolbar.hide()
        self.o.ortho = self.savedOrtho
        self.o.setMode('SELECT')


    def Done(self):
        if self.o.shape:
            self.o.assy.molmake(self.o.shape)
            self.o.shape = None

        self.w.extrudeToolbar.hide()
        self.o.ortho = self.savedOrtho
        self.o.setMode('SELECT')
         
	basicMode.Done(self)

        

    def Backup(self):
        if self.o.shape:
            self.o.shape.undo()
        self.o.paintGL()
        
    def Restart(self):
        if self.o.shape:
            self.o.shape.clear()
        self.o.paintGL()
        

    def leftDown(self, event):
        self.StartDraw(event, 1)
    
    def leftShiftDown(self, event):
        self.StartDraw(event, 0)

    def leftCntlDown(self, event):
        self.StartDraw(event, 2)

    def StartDraw(self, event, sense):
        """Start a selection curve
        """
        self.selSense = sense
        if self.Rubber: return
        self.picking = 1
        self.o.SaveMouse(event)
        self.o.prevvec = None
        self.extrudeQuat = Q(self.o.quat)

        p1, p2 = self.o.mousepoints(event)
        
        self.o.normal = self.o.lineOfSight
        self.sellist = [p1]
        self.o.backlist = [p2]
        self.pickLineStart = self.pickLinePrev = p1
        self.pickLineLength = 0.0
    
    def leftDrag(self, event):
        self.ContinDraw(event)
    
    def leftShiftDrag(self, event):
        self.ContinDraw(event)
    
    def leftCntlDrag(self, event):
        self.ContinDraw(event)

    def ContinDraw(self, event):
        """Add another segment to a selection curve
        """
        if not self.picking: return
        if self.Rubber: return
        p1, p2 = self.o.mousepoints(event)

        self.sellist += [p1]
        self.o.backlist += [p2]
        netdist = vlen(p1-self.pickLineStart)

        self.pickLineLength += vlen(p1-self.pickLinePrev)
        self.selLassRect = self.pickLineLength < 2*netdist

        self.pickLinePrev = p1
        self.o.paintGL()
    
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

        if self.pickLineLength/self.o.scale < 0.03:
            # didn't move much, call it a click
            if not (len(self.sellist)>1 and vlen(p1-self.sellist[0])<1):
                self.sellist += [p1]
                self.o.backlist += [p2]

                self.selLassRect = 0

                self.Rubber = True

                return

        self.Rubber = 0
        self.sellist += [p1]
        self.sellist += [self.sellist[0]]
        self.o.backlist += [p2]
        self.o.backlist += [self.o.backlist[0]]
        if not self.o.shape:
            self.o.shape=shape(self.o.right, self.o.up, self.o.lineOfSight,
                               Slab(-self.o.pov, self.o.out, 7))
        eyeball = (-self.o.quat).rot(V(0,0,6*self.o.scale)) - self.o.pov
        if self.selLassRect:
            self.o.shape.pickrect(self.o.backlist[0], p2, -self.o.pov, self.selSense)
        else:
            self.o.shape.pickline(self.o.backlist, -self.o.pov, self.selSense)
        self.sellist = []

        self.o.paintGL()

    def middleUp(self,event):
        if self.extrudeQuat:
            self.o.quat = Q(self.extrudeQuat)
            self.o.paintGL()
        else: self.o.snap2trackball()

    def bareMotion(self, e):
        if self.Rubber:
            p1, p2 = self.o.mousepoints(e)
            try: self.sellist[-1]=p1
            except: print self.sellist
            self.o.paintGL()

    def Draw(self):
        self.griddraw()
        if self.sellist: self.pickdraw()
        if self.o.shape: self.o.shape.draw(self.o)

    def griddraw(self):
        """Assigned as griddraw for a diamond lattice grid that is fixed in
        space but cut out into a slab one nanometer thick parallel to the screen
        (and is equivalent to what the extrude-cutter will cut).
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
        #drawer.drawaxes(5,-self.o.pov)

   
    def makeMenus(self):
        self.Menu1 = self.makemenu([('Cancel', self.Flush),
                                    ('Restart', self.Restart),
                                    ('Backup', self.Backup),
                                    None,
                                    ('Layer', self.Layer),
                                    ('Thickness', self.Thickness),
                                    None,
                                    ('Move', self.move),
                                    ('Copy', self.copy)])
        
        self.Menu2 = self.makemenu([('Kill', self.o.assy.kill),
                                    ('Copy', self.o.assy.copy),
                                    ('Separate', self.o.assy.modifySeparate),
                                    ('Bond', self.o.assy.Bond),
                                    ('Unbond', self.o.assy.Unbond),
                                    ('Stretch', self.o.assy.Stretch)])
        
        self.Menu3 = self.makemenu([('Default', self.w.dispDefault),
                                    ('Lines', self.w.dispLines),
                                    ('CPK', self.w.dispCPK),
                                    ('Tubes', self.w.dispTubes),
                                    ('VdW', self.w.dispVdW),
                                    None,
                                    ('Invisible', self.w.dispInvis),
                                    None,
                                    ('Color', self.w.dispObjectColor)])

    def copy(self):
        print 'NYI'

    def move(self):
        print 'NYI'

    def Layer(self):
        if self.o.shape:
            self.o.pov -= self.o.shape.pushdown()
        

    def Thickness(self):
        print 'NYI'