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

    MAX_LATTICE_CELL = 25
    # no __init__ method needed
    
    layerColors = ((0.0, 85.0/255.0, 127/255.0),
                           (85/255.0, 85/255.0, 0.0),
                           (85/255.0, 85/255.0, 127/255.0),
                            (170.0/255.0, 0.0, 127.0/255.0),
                           (170.0/255.0, 0.0,  1.0),
                           (1.0, 0.0, 127.0/255.0),
                           )
    # methods related to entering this mode
    
    def Enter(self): # bruce 040922 split setMode into Enter and init_gui (fyi)
        basicMode.Enter(self)
        self.oldPov = V(self.o.pov[0], self.o.pov[1], self.o.pov[2])
        self.o.snap2trackball()
        self.o.pov -= 3.5*self.o.out
        self.savedOrtho = self.o.ortho

        self.o.ortho = 1

        self.cookieQuat = None

        self.thickness = -1
        self.whichsurf=0
        
        self.showFullModel = self.w.isCookieFullModelOn()
        self.tubeDisplayMode = self.w.ccTubeRadioButton.isChecked()
        self.addLayerEnabled = False
        
        self.layers = [] ## Stores 'org, color' for each layer
        self.layers += [[V(self.o.pov[0], self.o.pov[1], self.o.pov[2])], [A(gray)]]  
        self.currentLayer = 0
 
        self.picking = None
        self.Rubber = None
       

    # init_gui handles all the GUI display when entering this mode [mark 041004
    def init_gui(self):
        self.o.setCursor(self.w.CookieAddCursor)
        self.w.toolsCookieCutAction.setOn(1) # toggle on the Cookie Cutter icon
        
        #Huaicai 3/29: Added the condition to fix bug 477
        self.w.dispbarLabel.setText("    ")
        
        ## Set projection to ortho, display them
        self.w.setViewOrthoAction.setOn(True)  
        self.w.setViewOrthoAction.setEnabled(False)
        self.w.setViewPerspecAction.setEnabled(False)
        
        self.w.ccLayerThicknessSpinBox.setValue(2)
        self.setthick(2)
        
        self.w.ccCurrentLayerCB.clear()
        self.w.ccCurrentLayerCB.insertItem(QString(str(len(self.layers[0]))))
        self.w.ccAddLayerAction.setEnabled(False)
         
        self.w.cookieCutterDashboard.show()
        self.w.connect(self.w.ccLayerThicknessSpinBox,SIGNAL("valueChanged(int)"),
                       self.setthick)
        
        self.w.connect(self.w.ccLayerThicknessLineEdit,SIGNAL("textChanged( const QString &)"),
                       self.setthicktext)
                       
        # Disable some action items in the main window.
        self.w.zoomToolAction.setEnabled(0) # Disable "Zoom Tool"
        self.w.panToolAction.setEnabled(0) # Disable "Pan Tool"
        self.w.rotateToolAction.setEnabled(0) # Disable "Rotate Tool"
        
        # Hide the modify toolbar
        self.w.modifyToolbar.hide()
      
      
    def setGridLineColor(self, c):
        """Set the grid Line color to c. c is an object of QColor """
        self.gridColor = c.red()/255.0, c.green()/255.0, c.blue()/255.0
        
    def setCookieDisplayMode(self, displayMode):
        """Set cookie display mode as tube or sphere
           <Param> displayMode: if it is true, display as tube """
        self.tubeDisplayMode = displayMode
        if self.o.shape:
            self.o.shape.changeDisplayMode(self.tubeDisplayMode)
            self.o.gl_update()
            
    # methods related to exiting this mode [bruce 040922 made these
    # from old Done and Flush methods]

    def haveNontrivialState(self):
        return self.o.shape != None # note that this is stored in the glpane, but not in its assembly.

    def StateDone(self):
        if self.o.shape:
            molmake(self.o.assy, self.o.shape) #bruce 050222 revised this call
            #self.o.shape.buildChunk(self.o.assy)
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
                       
        self.w.zoomToolAction.setEnabled(1) # Enable "Zoom Tool"
        self.w.panToolAction.setEnabled(1) # Enable "Pan Tool"
        self.w.rotateToolAction.setEnabled(1) # Enable "Rotate Tool"
        # Show the modify toolbar
        self.w.modifyToolbar.show()
        
        #Restore display mode status message
        self.w.dispbarLabel.setText( "Default Display: " + dispLabel[self.o.display] )
        
        # Restore view projection, enable them.
        self.w.setViewOrthoAction.setEnabled(True)
        self.w.setViewPerspecAction.setEnabled(True)
        if not self.savedOrtho:
            self.w.setViewPerspecAction.setOn(True) 
        
    def restore_patches(self):
        self.o.ortho = self.savedOrtho
        self.o.shape = None
        self.sellist = []
        self.o.pov = V(self.oldPov[0], self.oldPov[1], self.oldPov[2])
    # other dashboard methods (not yet revised by bruce 040922 ###e)
    
    def Backup(self):
        if self.o.shape:
            self.o.shape.undo()
        self.o.gl_update()

    # mouse and key events
    def keyPress(self,key):
        basicMode.keyPress(self, key)
        if key == Qt.Key_Shift:
            self.o.setCursor(self.w.CookieCursor)
        if key == Qt.Key_Control:
            self.o.setCursor(self.w.CookieSubtractCursor)
        elif key == Qt.Key_Escape:
            self._cancelRubberSelection()
                                
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
        self.o.gl_update()
    
    def leftUp(self, event):
        self.EndDraw(event)
    
    def leftShiftUp(self, event):
        self.EndDraw(event)
    
    def leftCntlUp(self, event):
        self.EndDraw(event)

    def leftDouble(self, event):
        """End rubber selection """
        if self.Rubber:
            self.Rubber = 0
            self.picking = 0
             
            self.sellist += [self.sellist[0]]
            self.o.backlist += [self.o.backlist[0]]
        
            if not self.o.shape:
                self.o.shape=CookieShape(self.o.right, self.o.up, self.o.lineOfSight)

            self.o.shape.pickline(self.o.backlist, -self.o.pov, self.selSense, self.currentLayer, Slab(-self.o.pov, self.o.out, self.thickness))
            self.w.enableCCAddLayer()
            self.sellist = []

            self.w.history.transient_msg("")
            self.o.gl_update()        
        
        
    def EndDraw(self, event):
        """Close a selection curve and do the selection
        """
        p1, p2 = self.o.mousepoints(event, 0.01)

        if not self.pickLineLength > 0: #self.pickLineLength/self.o.scale < 0.03:
            # didn't move much, call it a click
            if self.picking:#not(len(self.sellist)> 1 and vlen(p1-self.sellist[0])<1):
                #Normally, the 2nd element in the list is the same as the 1srt.
                #It seems no harm, so didn't remove it.---Huaicai 3/22/05 
                self.sellist += [p1]
                self.o.backlist += [p2]

                self.selLassRect = 0
                self.Rubber = True
            return
            #else:
                # Check if Rubber selection area is too small, like
                # just a double click, don't do anything. Huaicai
                # 10/16/04
             #   totalLen = reduce(lambda x, y: x+y, map(lambda m: vlen(m[0]-m[1]),
              #                                          zip(self.sellist[:-1],
              #                                              self.sellist[1:])))
              #  if totalLen/self.o.scale < 0.03: #No really selected, do nothing
               #        self.Rubber = False
               #        self.sellist = []
               #        return
      
        self.picking = 0
        self.Rubber = 0
        self.sellist += [p1]
        self.sellist += [self.sellist[0]]
        self.o.backlist += [p2]
        self.o.backlist += [self.o.backlist[0]]
        # bruce 041213 comment: shape might already exist, from prior drags
        if not self.o.shape:
            self.o.shape=CookieShape(self.o.right, self.o.up, self.o.lineOfSight)

        # took out kill-all-previous-curves code -- Josh

        if self.selLassRect:
            self.o.shape.pickrect(self.o.backlist[0], p2, -self.o.pov,
                                  self.selSense, self.currentLayer,
                                  Slab(-self.o.pov, self.o.out,
                                            self.thickness))
        else:
            self.o.shape.pickline(self.o.backlist, -self.o.pov, self.selSense,
                                  self.currentLayer, Slab(-self.o.pov, self.o.out, self.thickness))
        self.w.enableCCAddLayer()
        self.sellist = []

        self.o.gl_update()


    def middleUp(self,event):
        """If self.cookieQuat: , which means: a shape 
        object has been created, so if you change the view,
        and thus self.o.quat, then the shape object will be wrong
        ---Huaicai 3/23/05 """
        print "cookie: basicMode.middleUp() called."
        basicMode.middleUp(self, event)
        
        if self.cookieQuat:
            #print "cookie: restore to original view."
            self.o.quat = Q(self.cookieQuat)
            self.o.gl_update()
        else:
            #print "cookie: middle up: snap2trackball() called."
            self.surfset(self.o.snap2trackball())
            
    def bareMotion(self, event):
        if self.Rubber:
            p1, p2 = self.o.mousepoints(event, 0.01)
            try: self.sellist[-1]=p1
            except: print self.sellist
            self.w.history.transient_msg("Double click to close curve; Press <Esc> key to cancel.")
            self.o.gl_update()

    def Draw(self):
        basicMode.Draw(self)    
        self.griddraw()
        if self.sellist:
            self.pickdraw()
        if self.o.shape: self.o.shape.draw(self.o, self.layerColors)#self.layers[1])
        if self.showFullModel:
            self.o.assy.draw(self.o)

    def griddraw(self):
        """Assigned as griddraw for a diamond lattice grid that is fixed in
        space but cut out into a slab one nanometer thick parallel to the screen
        (and is equivalent to what the cookie-cutter will cut).
        """
        # the grid is in modelspace but the clipping planes are in eyespace
        glPushMatrix()
        q = self.o.quat
        glTranslatef(-self.o.pov[0], -self.o.pov[1], -self.o.pov[2])
        glRotatef(- q.angle*180.0/pi, q.x, q.y, q.z)
        glClipPlane(GL_CLIP_PLANE0, (0.0, 0.0, 1.0, 6.0))
        glClipPlane(GL_CLIP_PLANE1, (0.0, 0.0, -1.0, 0.1))
        glEnable(GL_CLIP_PLANE0)
        glEnable(GL_CLIP_PLANE1)
        glPopMatrix()
        #drawer.drawDiamondCubic((0, 0, 0))
        glColor3fv(self.gridColor)
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
            #('Add New Layer', self.Layer),
            # bruce 041103 removed Copy, per Ninad email;
            # Josh says he might implement it for Alpha;
            # if/when he does, he can uncomment the following two lines.
            ## None,
            ## ('Copy', self.copy),
         ]

    def copy(self):
        print 'NYI'

    def addLayer(self, layerCombox):
        """Add a new layer: the new layer will always be at the end"""
        if self.o.shape:
            lastLayerId = len(self.layers[0]) - 1
            pov = self.layers[0][lastLayerId]
            pov = V(pov[0], pov[1], pov[2])
            pov -= self.o.shape.pushdown(lastLayerId)
            
            ## Make sure pushdown() doesn't return V(0,0,0)
            color = self.layers[1][lastLayerId] - 0.05
            if (color[0] < 0): color[0] = 0.0
            if (color[1] < 0): color[1] = 0.0
            if (color[2] < 0): color[2] = 0.0
            
            self.layers[0] += [pov]
            self.layers[1] += [color]
            size = len(self.layers[0])
           
            layerCombox.insertItem(QString(str(size)))
            layerCombox.setCurrentItem(size-1)
            
            self.change2Layer(size-1)
            self.o.gl_update()
            

    def change2Layer(self, layerIndex):
        """Change current layer to layer <layerIndex>"""
        if layerIndex == self.currentLayer: return
        
        assert layerIndex in range(len(self.layers[0]))
        
        pov = self.layers[0][layerIndex]
        self.currentLayer = layerIndex
        self.o.pov = V(pov[0], pov[1], pov[2])
        
        maxCells = self._findMaxNoLattCell(self.currentLayer)
        self.w.ccLayerThicknessSpinBox.setMaxValue(maxCells)
       
        ##Cancel any rubber selection if any.
        if self.Rubber:
            self.w.history.message(redmsg("Layer changed during rubber window cookie selection, cancel the selection."))
            self._cancelRubberSelection()
       
        self.o.gl_update()
      
        
    def _findMaxNoLattCell(self, curLay):
        """Find the possible max no of lattice cells for this layer """
        if curLay == len(self.layers[0]) - 1:
            return self.MAX_LATTICE_CELL
        else:
            depth = vlen(self.layers[0][curLay+1] - self.layers[0][curLay])
            num = int(depth/(DiGridSp*sqrt(self.whichsurf+1)) + 0.5)
            return num

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
    
    def toggleFullModel(self, showFullModel):
        """Turn on/off full model """
        self.showFullModel = showFullModel
        self.o.gl_update()
    
    def _cancelRubberSelection(self):
        """Cancel rubber selection before it's finished """
        if self.Rubber:
            self.sellist = []
            self.Rubber = False
            self.picking = False
            self.w.history.transient_msg("")
            self.o.gl_update()
         
    pass # end of class cookieMode

# == helper functions

def hashAtomPos(pos):
        return int(dot(V(1000000, 1000,1),floor(pos*1.2)))

# make a new molecule using a cookie-cut shape

# [bruce 050222 changed this from an assembly method to a cookieMode function
#  (since it's about cookies made from diamond, like this file),
#  and moved it from assembly.py to cookieMode.py, but changed nothing else
#  except renaming self->assy and adding some comments.]

def molmake(assy,shap):
    assy.changed() # The file and the part are now out of sync.
        #bruce 050222 comment: this is not needed, since it's done by addmol
    mol = molecule(assy, gensym("Cookie."))
    ndx={}
    hashAtomPos #bruce 050222 comment: this line is probably a harmless typo, should be removed
    bbhi, bblo = shap.bbox.data
    # Widen the grid enough to get bonds that cross the box
    griderator = genDiam(bblo-1.6, bbhi+1.6)
    pp=griderator.next()
    while (pp):
        pp0 = pp1 = None
        if shap.isin(pp[0]):
            pp0h = hashAtomPos(pp[0])
            if pp0h not in ndx:
                pp0 = atom("C", pp[0], mol)
                ndx[pp0h] = pp0
            else: pp0 = ndx[pp0h]
        if shap.isin(pp[1]):
            pp1h = hashAtomPos(pp[1])
            if pp1h not in ndx:
                pp1 = atom("C", pp[1], mol)
                ndx[pp1h] = pp1
            else: pp1 = ndx[pp1h]
        if pp0 and pp1: mol.bond(pp0, pp1)
        elif pp0:
            x = atom("X", (pp[0] + pp[1]) / 2.0, mol)
            mol.bond(pp0, x)
        elif pp1:
            x = atom("X", (pp[0] + pp[1]) / 2.0, mol)
            mol.bond(pp1, x)
        pp=griderator.next()

    #Added by huaicai to fixed some bugs for the 0 atoms molecule 09/30/04
    # [bruce 050222 comment: I think Huaicai added the condition, not the body,
    #  i.e. before that it was effectively "if 1".]
    if len(mol.atoms) > 0:
        #bruce 050222 comment: much of this is not needed, since mol.pick() does it.
        assy.addmol(mol)
        assy.unpickatoms()
        assy.unpickparts()
        assy.selwhat = 2
        mol.pick()
        assy.mt.mt_update()

    return # from molmake

# end