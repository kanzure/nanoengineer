# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
THIS FILE IS PRESENTLY OWNED BY BRUCE -- please don't change it in any way,
however small, unless this is necessary to make Atom work properly for other developers.
[bruce 040921]

$Id$

Stub file for Extrude mode. For now, this works, but it's almost identical to cookieMode,
except for a different background color.
-- bruce 040924
"""

# bruce 040920: until MainWindow.ui does the following, I'll do it manually:
# (FYI: I will remove this, and the call to this, after MainWindowUI does the same stuff.
#  But first I will be editing this function a lot to get the dashboard contents that I need.)
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

        self.textLabel_extrude_toolbar = QLabel(self.extrudeToolbar,"textLabel_extrude_toolbar") # text set below

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
        self.textLabel_extrude_toolbar.setText(self._MainWindow__tr("Extrude Mode (stub)")) ###

        # fyi: caller hides the toolbar, we don't need to
        
        return

# ==

from modes import *

class extrudeMode(basicMode):

    # class constants
    backgroundColor = 200/256.0, 100/256.0, 100/256.0 # different than in cookieMode
    ##gridColor = 223/256.0, 149/256.0, 0/256.0
    modename = 'EXTRUDE'

    # default initial values
    savedOrtho = 0

    # no __init__ method needed
    
    # methods related to entering this mode
    
    def Enter(self): # bruce 040922 split setMode into Enter and show_toolbars (fyi)
        basicMode.Enter(self)
        self.o.pov -= 3.5*self.o.out
        self.savedOrtho = self.o.ortho

        self.o.ortho = 1

        self.extrudeQuat = None

        self.Rubber = None
        self.o.snap2trackball()

    def show_toolbars(self):
        self.w.extrudeToolbar.show()

    # methods related to exiting this mode [bruce 040922 made these from old Done and Flush methods]

    def haveNontrivialState(self):
        return self.o.shape != None # note that this is stored in the glpane, but not in its assembly.

    def StateDone(self):
        if self.o.shape:
            self.o.assy.molmake(self.o.shape)
        self.o.shape = None
        return None

    def StateCancel(self):
        self.o.shape = None
        # it's mostly a matter of taste whether to put this statement into StateCancel, restore_patches, or clear()...
        # it probably doesn't matter in effect, in this case. To be safe (e.g. in case of Abandon), I put it in more than one place.
        return None
    
    def hide_toolbars(self):
        self.w.extrudeToolbar.hide()

    def restore_patches(self):
        self.o.ortho = self.savedOrtho
        self.o.shape = None
        
    # other dashboard methods (not yet revised by bruce 040922 ###e)
    
    def Backup(self):
        if self.o.shape:
            self.o.shape.undo()
        self.o.paintGL()

##    not needed:
##    def StartOver(self):
##        if self.o.shape:
##            self.o.shape.clear()
##        self.o.paintGL()
        
    # mouse events
    
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
        basicMode.Draw(self)    
        ##self.griddraw()
        if self.sellist: self.pickdraw()
        if self.o.shape: self.o.shape.draw(self.o)
   
    def makeMenus(self):
        self.Menu1 = self.makemenu([('Cancel', self.Cancel),
                                    ('Start Over', self.StartOver),
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

    pass # end of class extrudeMode


