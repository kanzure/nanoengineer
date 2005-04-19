# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
cookieMode.py -- cookie cutter mode.

$Id$

"""
from modes import *
from CookieCtrlPanel import CookieCtrlPanel

class cookieMode(basicMode):

    # class constants
    backgroundColor = 103/255.0, 124/255.0, 53/255.0
    gridColor = 222/255.0, 148/255.0, 0/255.0
    modename = 'COOKIE'
    default_mode_status_text = "Mode: Cookie Cutter"
    
    MAX_LATTICE_CELL = 25
    
    layerColors = ((0.0, 85.0/255.0, 127/255.0),
                           (85/255.0, 85/255.0, 0.0),
                           (85/255.0, 85/255.0, 127/255.0),
                            (170.0/255.0, 0.0, 127.0/255.0),
                           (170.0/255.0, 0.0,  1.0),
                           (1.0, 0.0, 127.0/255.0),
                           )
    
    SELECTION_SHAPES = ['TRIANGLE', 'RECTANGLE', 'HEXAGON', 'CIRCLE', 'DEFAULT']
    
    LATTICE_TYPES = ['DIAMOND', 'LONSDALEITE', 'GRAPHITE']
    
    MAX_LAYERS = 6
                           
    # methods related to entering this mode
    def __init__(self, glpane):
        """The initial function is called only once for the whole program """
        basicMode.__init__(self, glpane)
        self.ctrlPanel = CookieCtrlPanel(self.w)
    
    def Enter(self): 
        basicMode.Enter(self)
        self.oldPov = V(self.o.pov[0], self.o.pov[1], self.o.pov[2])
        self.surfset(self.o.snap2trackball())
        
        self.o.pov -= 3.5*self.o.out
        self.savedOrtho = self.o.ortho
        self.o.ortho = 1
        self.cookieQuat = None
        #self.thickness = -1
        
        self.freeView = False
        self.ctrlPanel.freeViewCheckBox.setChecked(self.freeView)
        
        self.gridShow = True
        self.ctrlPanel.gridLineCheckBox.setChecked(self.gridShow)
        
        self.showFullModel = self.ctrlPanel.fullModelCheckBox.isChecked()
        self.cookieDisplayMode = str(self.ctrlPanel.dispModeCBox.currentText())
        self.latticeType = self.LATTICE_TYPES[self.ctrlPanel.latticeCBox.currentItem()]
        
        self.layers = [] ## Stores 'org, color' for each layer
        self.layers += [[V(self.o.pov[0], self.o.pov[1], self.o.pov[2])], [A(gray)]]  
        self.currentLayer = 0
 
        self.picking = None
        self.Rubber = None
       
        self.selectionShape = self.ctrlPanel.getSelectionShape()
        
    
    def init_gui(self):
        """GUI items need initialization every time."""
        self.ctrlPanel.initGui()
        
        #This can't be done in the above call. During this time, 
        # the ctrlPanel can't find the cookieMode, the nullMode
        # is used instead. I don't know if that's good or not, but
        # I think the code readability is not very good. --Huaicai 
        self.setThickness(self.ctrlPanel.layerCellsSpinBox.value())
   
   
    def restore_gui(self):
        """Restore GUI items when exit every time. """
        self.ctrlPanel.restoreGui()
        
        if not self.savedOrtho:
            self.w.setViewPerspecAction.setOn(True) 
    
    
    def setFreeView(self, freeView):
        """When in this mode(freeView is true), cookie-cutting is freezing """
        self.freeView = freeView
        if freeView:
            #Save current pov before free view transformation
            self.cookiePov = V(self.o.pov[0], self.o.pov[1], self.o.pov[2])
            
            self.w.history.message(redmsg("Enter into 'Free View' of cookie cutter mode. No cookie can be cut until exit from it."))
            self.o.setCursor(QCursor(Qt.ArrowCursor))
            self.w.setViewOrthoAction.setEnabled(True)
            self.w.setViewPerspecAction.setEnabled(True)
            
            #Disable controls to change layer, which cause pov change
            self.ctrlPanel.currentLayerCBox.setEnabled(False)
            self.isAddLayerEnabled = self.ctrlPanel.addLayerButton.isEnabled ()
            self.ctrlPanel.addLayerButton.setEnabled(False)
            
            self.ctrlPanel.enableViewChanges(True)
            
            if self.Rubber:
                self._cancelSelection()
                self.w.history.message(redmsg("Changed to free view mode,the unfinished cookie selection will be cancelled."))
            
        else: ## cookie cutting mode
            self.o.setCursor(self.w.CookieAddCursor)
            self.w.setViewOrthoAction.setOn(True)  
            self.w.setViewOrthoAction.setEnabled(False)
            self.w.setViewPerspecAction.setEnabled(False)
            
            #Restore controls to change layer/add layer
            self.ctrlPanel.currentLayerCBox.setEnabled(True)
            self.ctrlPanel.addLayerButton.setEnabled(self.isAddLayerEnabled)
            
            self.ctrlPanel.enableViewChanges(False)
            
            self.o.ortho = True
            if self.o.shape:
                self.o.quat = Q(self.cookieQuat)
                self.o.pov = V(self.cookiePov[0], self.cookiePov[1], self.cookiePov[2]) 
            self.surfset(self.o.snap2trackball())
            
                
      
    def showGridLine(self, show):
        self.gridShow = show
        self.o.gl_update()
        
    def setGridLineColor(self, c):
        """Set the grid Line color to c. c is an object of QColor """
        self.gridColor = c.red()/255.0, c.green()/255.0, c.blue()/255.0
        
    def changeDispMode(self, mode):
        """Change cookie display mode as 'mode'.
        """
        self.cookieDisplayMode = str(mode)
        if self.o.shape:
            self.o.shape.changeDisplayMode(self.cookieDisplayMode)
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
   
        
    def restore_patches(self):
        self.o.ortho = self.savedOrtho
        self.o.shape = None
        self.sellist = []
        self.o.pov = V(self.oldPov[0], self.oldPov[1], self.oldPov[2])
    
    
    def Backup(self):
        if self.o.shape:
            self.o.shape.undo(self.currentLayer)
        self.o.gl_update()

    # mouse and key events
    def keyPress(self,key):
        basicMode.keyPress(self, key)
        if self.freeView: return
        if key == Qt.Key_Shift:
            self.o.setCursor(self.w.CookieCursor)
        if key == Qt.Key_Control:
            self.o.setCursor(self.w.CookieSubtractCursor)
        elif key == Qt.Key_Escape:
            self._cancelSelection()
        if 0:   
            if key in (Qt.Key_C, Qt.Key_H, Qt.Key_R):
                self.sellist = []
                self.o.backlist = []
            if key == Qt.Key_C:
                self.circleSelection = True
            elif key == Qt.Key_H:
                self.hexagonSelection = True
            elif key == Qt.Key_R:
                self.rectangleSelection = True    
            
                                
    def keyRelease(self,key):
        basicMode.keyRelease(self, key)
        if self.freeView: return
        if key == Qt.Key_Shift or key == Qt.Key_Control:
            self.o.setCursor(self.w.CookieAddCursor)
    
    def rightShiftDown(self, event):
        basicMode.rightShiftDown(self, event)
        if self.freeView: return
        self.o.setCursor(self.w.CookieAddCursor)
            
    def rightCntlDown(self, event):          
        basicMode.rightCntlDown(self, event)
        if self.freeView: return
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
        if self.freeView: return
        
        self.selSense = sense
        if self.Rubber: return
        self.picking = 1
        self.cookieQuat = Q(self.o.quat)
        self.pickLineLength = 0.0
        if not self.selectionShape in ['DEFAULT', 'LASSO', 'RECT_CORNER']: return
        
        if self.selectionShape == 'LASSO':
            self.selLassRect = False
        elif self.selectionShape == 'RECT_CORNER':    
            self.selLassRect = True
            
        p1, p2 = self.o.mousepoints(event, 0.01)
        
        self.o.normal = self.o.lineOfSight
        self.sellist = [p1]
        self.o.backlist = [p2]
        self.pickLineStart = self.pickLinePrev = p1
        
    
    def leftDrag(self, event):
        self.ContinDraw(event)
    
    def leftShiftDrag(self, event):
        self.ContinDraw(event)
    
    def leftCntlDrag(self, event):
        self.ContinDraw(event)

    def ContinDraw(self, event):
        """Add another segment to a selection curve
        """
        if self.freeView: return
        
        if not self.picking: return
        if self.Rubber: return
        if not self.selectionShape in ['DEFAULT', 'LASSO', 'RECT_CORNER']: return
        
        p1, p2 = self.o.mousepoints(event, 0.01)

        self.sellist += [p1]
        self.o.backlist += [p2]
        
        netdist = vlen(p1-self.pickLineStart)
        self.pickLineLength += vlen(p1-self.pickLinePrev)
        if self.selectionShape == 'DEFAULT':
            self.selLassRect = self.pickLineLength < 2*netdist
        self.pickLinePrev = p1
        
        self.w.history.transient_msg("Release left button to end selection; Press <Esc> key to cancel selection.")    
        self.o.gl_update()
        
    
    def leftUp(self, event):
        self.EndDraw(event)
    
    def leftShiftUp(self, event):
        self.EndDraw(event)
    
    def leftCntlUp(self, event):
        self.EndDraw(event)

    def leftDouble(self, event):
        """End rubber selection """
        if self.freeView: return
        
        if self.Rubber:
            self.Rubber = 0
            self.picking = 0
             
            self.sellist += [self.sellist[0]]
            self.o.backlist += [self.o.backlist[0]]
        
            if not self.o.shape:
                self.o.shape=CookieShape(self.o.right, self.o.up, self.o.lineOfSight, self.cookieDisplayMode, self.latticeType)
                self.ctrlPanel.latticeCBox.setEnabled(False)
                self.ctrlPanel.enableViewChanges(False)

            self.o.shape.pickline(self.o.backlist, -self.o.pov, self.selSense, self.currentLayer, Slab(-self.o.pov, self.o.out, self.thickness))
            if self.currentLayer < (self.MAX_LAYERS - 1) and self.currentLayer == len(self.layers[0]) - 1:
                self.ctrlPanel.addLayerButton.setEnabled(True)
            self.sellist = []

            self.w.history.transient_msg("")
            self.o.gl_update()        
        
        
    def EndDraw(self, event):
        """Close a selection curve and do the selection
        """
        if self.freeView: return
        if not self.picking: return
        
        p1, p2 = self.o.mousepoints(event, 0.01)

        if not self.pickLineLength > 0: ##Rubber-band/circular selection
            if not self.selectionShape in ['DEFAULT', 'LASSO', 'RECT_CORNER']: 
                if not (self.sellist and self.o.backlist):
                    self.sellist = [p1]; self.sellist += [p1]
                    self.o.backlist = [p2]; self.o.backlist += [p2]
                else:
                    self.o.backlist[-1] = p2
                    self._centerBasedSelect()
                    self.sellist = []
                    self.w.history.transient_msg("   ")
            elif self.picking and self.selectionShape == 'DEFAULT':  ##Rubber-band selection
                self.sellist += [p1]
                self.o.backlist += [p2]
                self.Rubber = True
            else: #This means single click/release without moving  
                self.sellist = []
                self.o.backlist = []
            return
            
        self.picking = 0
        self.Rubber = 0
        self.sellist += [p1]
        self.sellist += [self.sellist[0]]
        self.o.backlist += [p2]
        self.o.backlist += [self.o.backlist[0]]
        # bruce 041213 comment: shape might already exist, from prior drags
        if not self.o.shape:
            self.o.shape=CookieShape(self.o.right, self.o.up, self.o.lineOfSight, self.cookieDisplayMode, self.latticeType)
            self.ctrlPanel.latticeCBox.setEnabled(False)
            self.ctrlPanel.enableViewChanges(False)
            
        # took out kill-all-previous-curves code -- Josh
        if self.selLassRect:
            self.o.shape.pickrect(self.o.backlist[0], p2, -self.o.pov,
                                  self.selSense, self.currentLayer,
                                  Slab(-self.o.pov, self.o.out,
                                            self.thickness))
        else:
            self.o.shape.pickline(self.o.backlist, -self.o.pov, self.selSense,
                                  self.currentLayer, Slab(-self.o.pov, self.o.out, self.thickness))
                                  
        if self.currentLayer < (self.MAX_LAYERS - 1) and self.currentLayer == len(self.layers[0]) - 1:
                self.ctrlPanel.addLayerButton.setEnabled(True)
        self.sellist = []
        
        self.w.history.transient_msg("   ")
        self.o.gl_update()

    def _anyMiddleUp(self):
        if self.freeView: return
       
        if self.cookieQuat:
            self.o.quat = Q(self.cookieQuat)
            self.o.gl_update()
        else:
            self.surfset(self.o.snap2trackball())
            
    def middleUp(self, event):
        """If self.cookieQuat: , which means: a shape 
        object has been created, so if you change the view,
        and thus self.o.quat, then the shape object will be wrong
        ---Huaicai 3/23/05 """
        basicMode.middleUp(self, event)
        self._anyMiddleUp()
            
    def middleShiftDown(self, event):        
         """Disable this action when cutting cookie. """
         if self.freeView: basicMode.middleShiftDown(self, event)   
    def middleCntlDown(self, event):
         """Disable this action when cutting cookie. """   
         if self.freeView: basicMode.middleCntlDown(self, event)

    def middleShiftUp(self, event):        
         """Disable this action when cutting cookie. """   
         if self.freeView: basicMode.middleShiftUp(self, event)
    
    def middleCntlUp(self, event):        
         """Disable this action when cutting cookie. """   
         if self.freeView: basicMode.middleCntlUp(self, event)

        
    def bareMotion(self, event):
        if self.freeView: return
        
        if self.Rubber or not self.selectionShape in ['DEFAULT', 'LASSO', 'RECT_CORNER']: 
            if not self.sellist: return
            p1, p2 = self.o.mousepoints(event, 0.01)
            try: self.sellist[-1]=p1
            except: print self.sellist
            if self.Rubber:
                self.w.history.transient_msg("Double click to end selection; Press <Esc> key to cancel selection.")
            else:
                self.w.history.transient_msg("Left click to end selection; Press <Esc> key to cancel selection.")
            self.o.gl_update()
     
    def _centerBasedSelect(self):
        """End the center based selection"""
        if not self.o.shape:
                self.o.shape=CookieShape(self.o.right, self.o.up, self.o.lineOfSight, self.cookieDisplayMode, self.latticeType)
                self.ctrlPanel.latticeCBox.setEnabled(False)
                self.ctrlPanel.enableViewChanges(False)
                 
        p1 = self.o.backlist[1]
        p0 = self.o.backlist[0]
        pt = p1 - p0
        if self.selectionShape in ['RECTANGLE', 'DIAMOND']:
            hw = dot(self.o.right, pt)*self.o.right
            hh = dot(self.o.up, pt)*self.o.up
            if self.selectionShape == 'RECTANGLE':
                pt1 = p0 - hw + hh
                pt2 = p0 + hw - hh
                self.o.shape.pickrect(pt1, pt2, -self.o.pov,
                                  self.selSense, self.currentLayer,
                                  Slab(-self.o.pov, self.o.out,
                                            self.thickness))
            elif self.selectionShape == 'DIAMOND':
                pp = []
                pp += [p0 + hh]; pp += [p0 - hw]
                pp += [p0 - hh];  pp += [p0 + hw]; pp += [pp[0]]
                self.o.shape.pickline(pp, -self.o.pov, self.selSense,
                                  self.currentLayer, Slab(-self.o.pov, self.o.out, self.thickness))
  
        elif self.selectionShape in ['HEXAGON', 'TRIANGLE', 'SQUARE']:
            if self.selectionShape == 'HEXAGON': sides = 6
            elif self.selectionShape == 'TRIANGLE': sides = 3
            elif self.selectionShape == 'SQUARE': sides = 4
            
            hQ = Q(self.o.out, 2.0*pi/sides)
            pp = []
            pp += [p1]
            for ii in range(1, sides):
                pt = hQ.rot(pt)
                pp += [pt + p0]
            pp += [p1]
            self.o.shape.pickline(pp, -self.o.pov, self.selSense,
                                  self.currentLayer, Slab(-self.o.pov, self.o.out, self.thickness))
                                  
        elif self.selectionShape == 'CIRCLE':
            self.o.shape.pickCircle(self.o.backlist, -self.o.pov, self.selSense, self.currentLayer, Slab(-self.o.pov, self.o.out, self.thickness))
            
        if self.currentLayer < (self.MAX_LAYERS - 1) and self.currentLayer == len(self.layers[0]) - 1:
                self.ctrlPanel.addLayerButton.setEnabled(True)
              
        self.o.gl_update()
    
    
    def _centerRectDiamDraw(self, color, pts, sType):
        """Construct center based Rectange or Diamond to draw
            <Param> pts: (the center and a corner point)"""
        pt = pts[1] - pts[0]
        hw = dot(self.o.right, pt)*self.o.right
        hh = dot(self.o.up, pt)*self.o.up
        pp = []
        
        if sType == 'RECTANGLE':
            pp = [pts[0] - hw + hh]
            pp += [pts[0] - hw - hh]
            pp += [pts[0] + hw - hh]
            pp += [pts[0] + hw + hh]
        elif sType == 'DIAMOND':
            pp += [pts[0] + hh]; pp += [pts[0] - hw]
            pp += [pts[0] - hh];  pp += [pts[0] + hw]
            
        drawer.drawLineLoop(color, pp)    
    
    def _centerEquiPolyDraw(self, color, sides, pts):
        """Construct a center based equilateral polygon to draw. 
        <Param> sides: the number of sides for the polygon
        <Param> pts: (the center and a corner point) """
        hQ = Q(self.o.out, 2.0*pi/sides)
        pt = pts[1] - pts[0]
        pp = []
        pp += [pts[1]]
        for ii in range(1, sides):
            pt = hQ.rot(pt)
            pp += [pt + pts[0]]
        
        drawer.drawLineLoop(color, pp)        
   
    def _centerCircleDraw(self, color, pts):
        """Construct center based hexagon to draw 
        <Param> pts: (the center and a corner point)"""
        pt = pts[1] - pts[0]
        rad = vlen(pt)
        
        drawer.drawCircle(color, pts[0], rad, self.o.out)
        
    def pickdraw(self):
        """selection curve draw"""
        color = logicColor(self.selSense)
        if not self.selectionShape == 'DEFAULT':
            if self.sellist:
                 if self.selectionShape == 'LASSO':
                     for pp in zip(self.sellist[:-1],self.sellist[1:]): 
                            drawer.drawline(color, pp[0], pp[1])
                 elif self.selectionShape == 'RECT_CORNER':
                     drawer.drawrectangle(self.pickLineStart, self.pickLinePrev,
                                 self.o.up, self.o.right, color)
                 else:
                    drawer.drawline(white, self.sellist[0], self.sellist[1], True)
                    if self.selectionShape in ['RECTANGLE', 'DIAMOND']:
                        self._centerRectDiamDraw(color, self.sellist, self.selectionShape)
                    elif self.selectionShape == 'CIRCLE':
                        self._centerCircleDraw(color, self.sellist)
                    elif self.selectionShape == 'HEXAGON':
                        self._centerEquiPolyDraw(color, 6, self.sellist)
                    elif self.selectionShape == 'SQUARE':
                        self._centerEquiPolyDraw(color, 4, self.sellist)
                    elif self.selectionShape == 'TRIANGLE':
                        self._centerEquiPolyDraw(color, 3, self.sellist)   
        else:
            basicMode.pickdraw(self)            


    def Draw(self):
        basicMode.Draw(self)
        if self.gridShow:    
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
        glColor3fv(self.gridColor)
        drawer.drawGrid(1.5*self.o.scale, -self.o.pov, self.latticeType)
        glDisable(GL_CLIP_PLANE0)
        glDisable(GL_CLIP_PLANE1)

   
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

    def addLayer(self):
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
           
            self.change2Layer(size-1)
            
            return size


    def change2Layer(self, layerIndex):
        """Change current layer to layer <layerIndex>"""
        if layerIndex == self.currentLayer: return
        
        assert layerIndex in range(len(self.layers[0]))
        
        pov = self.layers[0][layerIndex]
        self.currentLayer = layerIndex
        self.o.pov = V(pov[0], pov[1], pov[2])
        
        maxCells = self._findMaxNoLattCell(self.currentLayer)
        self.ctrlPanel.layerCellsSpinBox.setMaxValue(maxCells)
       
        ##Cancel any rubber selection if any.
        if self.Rubber:
            self.w.history.message(redmsg("Layer changed during rubber window cookie selection, cancel the selection."))
            self._cancelSelection()
       
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
        self.setThickness(self.ctrlPanel.layerCellsSpinBox.value())
        button = self.ctrlPanel.orientButtonGroup.find(self.whichsurf)
        button.setOn(True)
        self.w.dispbarLabel.setText(QToolTip.textFor(button))
        

    def setThickness(self, num):
        self.thickness = num*DiGridSp*sqrt(self.whichsurf+1)
        s = "%3.4f" % (self.thickness)
        self.ctrlPanel.layerThicknessLineEdit.setText(s)
   
    def toggleFullModel(self, showFullModel):
        """Turn on/off full model """
        self.showFullModel = showFullModel
        self.o.gl_update()
    
    def _cancelSelection(self):
        """Cancel rubber or center based selection before it's finished """
        if self.Rubber:
            self.Rubber = False
        
        #elif self.selectionShape in ['DEFAULT', 'LASSO', 'RECT_CORNER']: return
        
        if self.sellist:
            self.o.backlist = []    
            self.sellist = []
            self.picking = False
            self.w.history.transient_msg("")
            self.o.gl_update()
        
    
    
    def changeLatticeType(self, lType):
        """Change lattice type as 'lType'. """
        self.latticeType = self.LATTICE_TYPES[lType]
        self.o.gl_update()
    
    def changeSelectionShape(self, newShape):
        self.selectionShape = newShape
        
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
    shap.combineLayers()    
    if not shap.curves: return
    mol = molecule(assy, gensym("Cookie."))
    ndx={}
    hashAtomPos #bruce 050222 comment: this line is probably a harmless typo, should be removed
    bbhi, bblo = shap.bbox.data
    # Widen the grid enough to get bonds that cross the box
    allCells = genDiam(bblo-1.6, bbhi+1.6, shap.latticeType)
    for cell in allCells:
        for pp in cell:
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