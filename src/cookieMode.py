# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
cookieMode.py -- cookie cutter mode.

$Id$
"""

from modes import *

class cookieMode(basicMode):

    # class constants
    backgroundColor = 103/255.0, 124/255.0, 53/255.0
    gridColor = 222/255.0, 148/255.0, 0/255.0
    modename = 'COOKIE'
    default_mode_status_text = "Mode: Cookie Cutter"
    
    # default initial values
    savedOrtho = 0

    # no __init__ method needed
    
    # methods related to entering this mode
    
    def Enter(self): # bruce 040922 split setMode into Enter and init_gui (fyi)
        basicMode.Enter(self)
        self.o.pov -= 3.5*self.o.out
        self.savedOrtho = self.o.ortho

        self.o.ortho = 1

        self.cookieQuat = None

        self.thickness = -1
        self.whichsurf=0

        self.Rubber = None
        self.o.snap2trackball()

    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        self.o.setCursor(self.w.CookieAddCursor)
        self.w.toolsCookieCutAction.setOn(1) # toggle on the Cookie Cutter icon
        self.w.ccLayerThicknessSpinBox.setValue(2)
        self.setthick(2)
        self.w.cookieCutterDashboard.show()
        self.w.connect(self.w.ccLayerThicknessSpinBox,SIGNAL("valueChanged(int)"),
                       self.setthick)
        
        self.w.connect(self.w.ccLayerThicknessLineEdit,SIGNAL("textChanged( const QString &)"),
                       self.setthicktext)
                       
        # Disable some action items in the main window.
        self.w.zoomWindowAction.setEnabled(0) # Disable "Zoom Window"
        
# methods related to exiting this mode [bruce 040922 made these
# from old Done and Flush methods]

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
    
    # restore_gui handles all the GUI display when leavinging this mode [mark 041004]
    def restore_gui(self):
        self.w.cookieCutterDashboard.hide()
        self.w.disconnect(self.w.ccLayerThicknessSpinBox,SIGNAL("valueChanged(int)"),
                       self.setthick)
        
        self.w.disconnect(self.w.ccLayerThicknessLineEdit,SIGNAL("textChanged( const QString &)"),
                       self.setthicktext)
                       
        self.w.zoomWindowAction.setEnabled(1) # Enable "Zoom Window"
        
    def restore_patches(self):
        self.o.ortho = self.savedOrtho
        self.o.shape = None
        
    # other dashboard methods (not yet revised by bruce 040922 ###e)
    
    def Backup(self):
        if self.o.shape:
            self.o.shape.undo()
        self.o.paintGL()

    # StartOver (formerly Restart) is no longer needed here, since the basicMode generic method works now. [bruce 040924]
##    def StartOver(self):
##        if self.o.shape:
##            self.o.shape.clear()
##        self.o.paintGL()
        
    # mouse and key events
    
    def keyPress(self,key):
        basicMode.keyPress(self, key)
        if key == Qt.Key_Shift:
            self.o.setCursor(self.w.CookieCursor)
        if key == Qt.Key_Control:
            self.o.setCursor(self.w.CookieSubtractCursor)
                                
    def keyRelease(self,key):
        basicMode.keyRelease(self, key)
        if key == Qt.Key_Shift or key == Qt.Key_Control:
            self.o.setCursor(self.w.CookieAddCursor)
    
    def rightShiftDown(self, event):
        basicMode.rightShiftDown(self, event)
        self.o.setCursor(self.w.CookieAddCursor)
            
    def rightCntlDown(self, event):          
        basicMode.rightCntlDown(self, event)
        self.o.setCursor(self.w.CookieAddCursor)
    
    def leftDown(self, event):
#        self.shape.curves
        self.StartDraw(event, 1) # add to selection
    
    def leftShiftDown(self, event):
        self.StartDraw(event, 2) # new selection (replace)

    def leftCntlDown(self, event):
        self.StartDraw(event, 0) # subtract from selection

    def StartDraw(self, event, sense):
        """Start a selection curve
        """
        self.selSense = sense
        if self.Rubber: return
        self.picking = 1
        self.o.SaveMouse(event)
        self.o.prevvec = None
        self.cookieQuat = Q(self.o.quat)

        p1, p2 = self.o.mousepoints(event, 0.01)
        
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
        p1, p2 = self.o.mousepoints(event, 0.01)

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
        p1, p2 = self.o.mousepoints(event, 0.01)

        if self.pickLineLength/self.o.scale < 0.03:
            # didn't move much, call it a click
            if not (len(self.sellist)>1 and vlen(p1-self.sellist[0])<1):
                self.sellist += [p1]
                self.o.backlist += [p2]

                self.selLassRect = 0

                self.Rubber = True
        
                return
            else:
                # Check if Rubber selection area is too small, like
                # just a double click, don't do anything. Huaicai
                # 10/16/04
                totalLen = reduce(lambda x, y: x+y, map(lambda m: vlen(m[0]-m[1]),
                                                        zip(self.sellist[:-1],
                                                            self.sellist[1:])))
                if totalLen/self.o.scale < 0.03: #No really selected, do nothing
                       self.Rubber = False
                       self.sellist = []
                       return
      
        self.Rubber = 0
        self.sellist += [p1]
        self.sellist += [self.sellist[0]]
        self.o.backlist += [p2]
        self.o.backlist += [self.o.backlist[0]]
        # bruce 041213 comment: shape might already exist, from prior drags
        if not self.o.shape:
            self.o.shape=shape(self.o.right, self.o.up, self.o.lineOfSight)

        # took out kill-all-previous-curves code -- Josh

        # bruce 041213 comment: eyeball computed here is not presently used
        eyeball = (-self.o.quat).rot(V(0,0,6*self.o.scale)) - self.o.pov
        
        if self.selLassRect:
            self.o.shape.pickrect(self.o.backlist[0], p2, -self.o.pov,
                                  self.selSense,
                                  slab=Slab(-self.o.pov, self.o.out,
                                            self.thickness))
        else:
            self.o.shape.pickline(self.o.backlist, -self.o.pov, self.selSense,
                                  slab = Slab(-self.o.pov, self.o.out, self.thickness))
        self.sellist = []

        self.o.paintGL()

    def middleUp(self,event):
        basicMode.middleUp(self, event)    
        
        if self.cookieQuat:
            self.o.quat = Q(self.cookieQuat)
            self.o.paintGL()
        else:
            self.surfset(self.o.snap2trackball())
            
    def bareMotion(self, event):
        if self.Rubber:
            p1, p2 = self.o.mousepoints(event, 0.01)
            try: self.sellist[-1]=p1
            except: print self.sellist
            self.o.paintGL()

    def Draw(self):
        basicMode.Draw(self)    
        self.griddraw()
        if self.sellist: self.pickdraw()
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
        #drawer.drawaxes(5,-self.o.pov)

   
    def makeMenus(self):
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Start Over', self.StartOver),
            ('Backup', self.Backup),
            ('Done', self.Done), # bruce 041217
            None,
            ('Add New Layer', self.Layer),
            # bruce 041103 removed Copy, per Ninad email;
            # Josh says he might implement it for Alpha;
            # if/when he does, he can uncomment the following two lines.
            ## None,
            ## ('Copy', self.copy),
         ]

    def copy(self):
        print 'NYI'

    def Layer(self):
        if self.o.shape:
            self.o.pov -= self.o.shape.pushdown()

    def surfset(self, num):
        self.whichsurf = num
        self.setthick(self.w.ccLayerThicknessSpinBox.value())

    def setthick(self, num):
        self.thickness = num*DiGridSp*sqrt(self.whichsurf+1)
        s = "%3.4f" % (self.thickness)
        self.w.ccLayerThicknessLineEdit.setText(s)

    def setthicktext(self, text):
        try:
#            if self.w.vd.validate( text, 0 )[0] != 2: self.w.ccLayerThicknessLineEdit.setText(s[:-1])
            self.thickness = float(str(text))
        except: pass
        
    pass # end of class cookieMode