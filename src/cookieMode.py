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
        self.setOrientSurf(self.o.snap2trackball())
        
        self.o.pov -= 3.5*self.o.out
        self.savedOrtho = self.o.ortho
        self.o.ortho = True
        self.cookieQuat = None
        
        ##Every time enters into this mode, we need to set this to False
        self.freeView = False
        self.ctrlPanel.freeViewCheckBox.setChecked(self.freeView)
        
        self.gridShow = True
        self.ctrlPanel.gridLineCheckBox.setChecked(self.gridShow)
        
        self.gridSnap = False
        self.ctrlPanel.snapGridCheckBox.setChecked(self.gridSnap)
        
        self.showFullModel = self.ctrlPanel.fullModelCheckBox.isChecked()
        self.cookieDisplayMode = str(self.ctrlPanel.dispModeCBox.currentText())
        self.latticeType = self.LATTICE_TYPES[self.ctrlPanel.latticeCBox.currentItem()]
        
        self.layers = [] ## Stores 'surface origin' for each layer
        self.layers += [V(self.o.pov[0], self.o.pov[1], self.o.pov[2])]
        self.currentLayer = 0
 
        self.cookieDrawBegins = False
        self.Rubber = None
        self.lastDrawStored = []
       
        self.selectionShape = self.ctrlPanel.getSelectionShape()
        
    
    def init_gui(self):
        """GUI items need initialization every time."""
        self.ctrlPanel.initGui()
        
        #This can't be done in the above call. During this time, 
        # the ctrlPanel can't find the cookieMode, the nullMode
        # is used instead. I don't know if that's good or not, but
        # generally speaking, I think the code structure for mode 
        # operations like enter/init/cancel, etc, are kind of confusing.
        # The code readability is also not very good. --Huaicai
        self.setThickness(self.ctrlPanel.layerCellsSpinBox.value())
   
   
    def restore_gui(self):
        """Restore GUI items when exit every time. """
        self.ctrlPanel.restoreGui()
        
        if not self.savedOrtho:
            self.w.setViewPerspecAction.setOn(True)
            
        #Restore GL states
        self.o.redrawGL = True
        glDisable(GL_COLOR_LOGIC_OP)
        glEnable(GL_DEPTH_TEST)
   
    
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
            
            #Disable controls to change layer.
            self.ctrlPanel.currentLayerCBox.setEnabled(False)
            self.isAddLayerEnabled = self.ctrlPanel.addLayerButton.isEnabled ()
            self.ctrlPanel.addLayerButton.setEnabled(False)
            
            self.ctrlPanel.enableViewChanges(True)
            
            if self.cookieDrawBegins: #Cancel any unfinished cookie drawing
                self._afterCookieSelection()
                self.w.history.message(redmsg("In free view mode,the unfinished cookie selection has be cancelled."))
            
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
            self.setOrientSurf(self.o.snap2trackball())
    
      
    def showGridLine(self, show):
        self.gridShow = show
        self.o.gl_update()
        
    def setGridLineColor(self, c):
        """Set the grid Line color to c. c is an object of QColor """
        self.gridColor = c.red()/255.0, c.green()/255.0, c.blue()/255.0
        
    def changeDispMode(self, mode):
        """Change cookie display mode as <mode>, which can be 'Tubes'
            or 'Spheres'.
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
            #molmake(self.o.assy, self.o.shape) #bruce 050222 revised this call
            self.o.shape.buildChunk(self.o.assy)
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
        
            #If no curves left, let users do what they can just like
            #when they first enter into cookie mode.
            if not self.o.shape.anyCurvesLeft():
                self.StartOver()
            
        self.o.gl_update()

    # mouse and key events
    def keyPress(self,key):
        basicMode.keyPress(self, key)
        if self.freeView: return
        #Don't change cursor during selection
        if key == Qt.Key_Shift and not self.cookieDrawBegins:
            self.o.setCursor(self.w.CookieCursor)
        elif key == Qt.Key_Control and not self.cookieDrawBegins:
            self.o.setCursor(self.w.CookieSubtractCursor)
        elif key == Qt.Key_Escape and self.cookieDrawBegins:
            self._cancelSelection()
        
    def keyRelease(self,key):
        basicMode.keyRelease(self, key)
        if self.freeView: return
        #Don't change cursor during selection
        if (key == Qt.Key_Shift or key == Qt.Key_Control) and not self.cookieDrawBegins:
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
        if self.Rubber: return
        
        self.cookieDrawBegins = True
        self.cookieQuat = Q(self.o.quat)
        self.pickLineLength = 0.0
        
        ## Start color xor operations
        self.o.redrawGL = False
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_LOGIC_OP)
        glLogicOp(GL_XOR)
        
        if not self.selectionShape in ['DEFAULT', 'LASSO']: return
        if self.selectionShape == 'LASSO':
            self.selLassRect = False
        
        self.selSense = sense    
        p1, p2 = self._getPoints(event)
        
        self.sellist = [p1]
        self.o.backlist = [p2]
        
        
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
        
        if not self.cookieDrawBegins: return
        if self.Rubber: return
        if not self.selectionShape in ['DEFAULT', 'LASSO']: return
        
        p1, p2 = self._getPoints(event)

        self.sellist += [p1]
        self.o.backlist += [p2]
        
        netdist = vlen(p1 - self.sellist[0])
        self.pickLineLength += vlen(p1 - self.sellist[-2])
        if self.selectionShape == 'DEFAULT':
            self.selLassRect = self.pickLineLength < 2*netdist
        
        self.w.history.transient_msg("Release left button to end selection; Press <Esc> key to cancel selection.")    
        self.pickdraw()
        
    
    def leftUp(self, event):
        self.EndDraw(event, 1)
    
    def leftShiftUp(self, event):
        self.EndDraw(event, 2)
    
    def leftCntlUp(self, event):
        self.EndDraw(event, 0)

    def leftDouble(self, event):
        """End rubber selection """
        if self.freeView or not self.cookieDrawBegins: return
        
        if self.Rubber and not self.rubberWithoutMoving:
            self._traditionalSelect()
        
        
    def EndDraw(self, event, sense):
        """Close a selection curve and do the selection
        """
        if self.freeView or not self.cookieDrawBegins: return
        
        p1, p2 = self. _getPoints(event)
 
        if not self.pickLineLength > 0: 
            #Rect_corner/circular selection
            if not self.selectionShape in ['DEFAULT', 'LASSO']: 
                if not (self.sellist and self.o.backlist): #The first click release
                    self.selSense = sense
                    self.sellist = [p1]; self.sellist += [p1]; self.sellist += [p1]
                    self.o.backlist = [p2]; self.o.backlist += [p2]
                    if self.selectionShape == 'RECT_CORNER':    
                            self.selLassRect = True
                    #Disable view changes when begin curve drawing 
                    self.ctrlPanel.enableViewChanges(False)
                else: #The end click release
                    self.o.backlist[-1] = p2
                    if self.selLassRect:
                        self._traditionalSelect() 
                    else:
                        self._centerBasedSelect()
            elif self.selectionShape == 'DEFAULT':  ##Rubber-band selection
                self.sellist += [p1]
                self.o.backlist += [p2]
                if not self.Rubber:
                    self.Rubber = True
                    self.rubberWithoutMoving = True
                    #Disable view changes when begin curve drawing        
                    self.ctrlPanel.enableViewChanges(False)
            else: #This means single click/release without dragging for Lasso
                self.sellist = []
                self.o.backlist = []
                self.cookieDrawBegins = False
        else: #Default(excluding rubber band)/Lasso selection
            self.sellist += [p1]
            self.o.backlist += [p2]
            self._traditionalSelect()    
    
    def _anyMiddleUp(self):
        if self.freeView: return
       
        if self.cookieQuat:
            self.o.quat = Q(self.cookieQuat)
            self.o.gl_update()
        else:
            self.setOrientSurf(self.o.snap2trackball())

    def middleDown(self, event):
        """Disable this method when in curve drawing"""
        if not self.cookieDrawBegins:
            basicMode.middleDown(self, event)
     
    def middleUp(self, event):
        """If self.cookieQuat: , which means: a shape 
        object has been created, so if you change the view,
        and thus self.o.quat, then the shape object will be wrong
        ---Huaicai 3/23/05 """
        if not self.cookieDrawBegins:
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
    
    def Wheel(self, event):
        """When in curve drawing stage, disable the zooming. """
        if not self.cookieDrawBegins: 
            basicMode.Wheel(self, event)
        
    def bareMotion(self, event):
        if self.freeView or not self.cookieDrawBegins: return
        
        if self.Rubber or not self.selectionShape in ['DEFAULT', 'LASSO']: 
            if not self.sellist: return
            p1, p2 = self._getPoints(event)
            try: 
                if self.Rubber: self.pickLinePrev = self.sellist[-1]
                else:  self.sellist[-2] = self.sellist[-1]
                self.sellist[-1] = p1
            except:
                print self.sellist
            if self.Rubber:
                self.rubberWithoutMoving = False
                self.w.history.transient_msg("Double click to end selection; Press <Esc> key to cancel selection.")
            else:
                self.w.history.transient_msg("Left click to end selection; Press <Esc> key to cancel selection.")
            self.pickdraw()
   
    def _afterCookieSelection(self):
        """Restore some variable states after the each curve selection """
        if self.sellist:
            self.pickdraw(True)
            
            self.cookieDrawBegins = False
            self.Rubber = False
            self.selLassRect = False
            self.sellist = []
            self.o.backlist = []
            
            self.w.history.transient_msg("   ")
            # Restore the cursor when the selection is done.
            self.o.setCursor(self.w.CookieAddCursor)
            
            #Restore GL states
            self.o.redrawGL = True
            glDisable(GL_COLOR_LOGIC_OP)
            glEnable(GL_DEPTH_TEST)
            self.o.gl_update()
     
     
    def _traditionalSelect(self):
        """The original curve selection"""
        self.sellist += [self.sellist[0]]
        self.o.backlist += [self.o.backlist[0]]
        
        # bruce 041213 comment: shape might already exist, from prior drags
        if not self.o.shape:
            self.o.shape=CookieShape(self.o.right, self.o.up, self.o.lineOfSight, self.cookieDisplayMode, self.latticeType)
            self.ctrlPanel.latticeCBox.setEnabled(False)
            self.ctrlPanel.enableViewChanges(False)
            
        # took out kill-all-previous-curves code -- Josh
        if self.selLassRect:
            self.o.shape.pickrect(self.o.backlist[0], self.o.backlist[-2], 
                    self.o.pov, self.selSense, self.currentLayer,
                                  Slab(-self.o.pov, self.o.out, self.thickness))
        else:
            self.o.shape.pickline(self.o.backlist, -self.o.pov, self.selSense,
                                  self.currentLayer, Slab(-self.o.pov, self.o.out, self.thickness))
        
        if self.currentLayer < (self.MAX_LAYERS - 1) and self.currentLayer == len(self.layers) - 1:
                self.ctrlPanel.addLayerButton.setEnabled(True)
        self._afterCookieSelection()
  
  
    def _centerBasedSelect(self):
        """Construct the right center based selection shape to generate the
         cookie. """
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
        
        if self.currentLayer < (self.MAX_LAYERS - 1) and self.currentLayer == len(self.layers) - 1:
                self.ctrlPanel.addLayerButton.setEnabled(True)
        self._afterCookieSelection()                          
    
        
    def _centerRectDiamDraw(self, color, pts, sType, lastDraw):
        """Construct center based Rectange or Diamond to draw
            <Param> pts: (the center and a corner point)"""
        pt = pts[2] - pts[0]
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
        
        if not self.lastDrawStored:
            self.lastDrawStored += [pp]
            self.lastDrawStored += [pp]
         
        self.lastDrawStored[0] = self.lastDrawStored[1]
        self.lastDrawStored[1] = pp    
        
        if not lastDraw:
            drawer.drawLineLoop(color, self.lastDrawStored[0])
        else: self.lastDrawStored = []     
        drawer.drawLineLoop(color, pp)    
  
    
    def _centerEquiPolyDraw(self, color, sides, pts, lastDraw):
        """Construct a center based equilateral polygon to draw. 
        <Param> sides: the number of sides for the polygon
        <Param> pts: (the center and a corner point) """
        hQ = Q(self.o.out, 2.0*pi/sides)
        pt = pts[2] - pts[0]
        pp = []
        pp += [pts[2]]
        for ii in range(1, sides):
            pt = hQ.rot(pt)
            pp += [pt + pts[0]]
        
        if not self.lastDrawStored:
            self.lastDrawStored += [pp]
            self.lastDrawStored += [pp]
         
        self.lastDrawStored[0] = self.lastDrawStored[1]
        self.lastDrawStored[1] = pp    
        
        if not lastDraw:
            drawer.drawLineLoop(color, self.lastDrawStored[0])        
        else: self.lastDrawStored = []
        drawer.drawLineLoop(color, pp)        
   
   
    def _centerCircleDraw(self, color, pts, lastDraw):
        """Construct center based hexagon to draw 
        <Param> pts: (the center and a corner point)"""
        pt = pts[2] - pts[0]
        rad = vlen(pt)
        
        if not self.lastDrawStored:
            self.lastDrawStored += [rad]
            self.lastDrawStored += [rad]
         
        self.lastDrawStored[0] = self.lastDrawStored[1]
        self.lastDrawStored[1] = rad    
        
        if not lastDraw:
            drawer.drawCircle(color, pts[0], self.lastDrawStored[0], self.o.out)
        else:
            self.lastDrawStored = []
        
        drawer.drawCircle(color, pts[0], rad, self.o.out)
    
    
    def _getXorColor(self, color):
        """Get color for <color>.  When the color is XORed with background color, it will get <color>. If background color is close to <color>
        , we'll use white color. 
        """
        bg = self.backgroundColor
        diff = vlen(A(color)-A(bg))
        if diff < 0.5:
            return (1-bg[0], 1-bg[1], 1-bg[2])
        else:
            rgb = []
            for ii in range(3):
                f = int(color[ii]*255)
                b = int(bg[ii]*255)
                rgb += [(f ^ b)/255.0]
            
            return rgb    
 
    def pickdraw(self, lastDraw = False):
        """Draw the selection curve."""
        color = logicColor(self.selSense)
        color = self._getXorColor(color)
        
        if not self.selectionShape == 'DEFAULT':
            if self.sellist:
                 if self.selectionShape == 'LASSO':
                     if not lastDraw:
                        for pp in zip(self.sellist[:-2],self.sellist[1:-1]): 
                            drawer.drawline(color, pp[0], pp[1])
                     for pp in zip(self.sellist[:-1],self.sellist[1:]):
                            drawer.drawline(color, pp[0], pp[1])
                 elif self.selectionShape == 'RECT_CORNER':
                     if not lastDraw:
                        drawer.drawrectangle(self.sellist[0], self.sellist[-2],
                                 self.o.up, self.o.right, color)
                     drawer.drawrectangle(self.sellist[0], self.sellist[-1],
                                 self.o.up, self.o.right, color)
                 else:
                    xor_white = self._getXorColor(white)
                    if not lastDraw:
                        drawer.drawline(xor_white, self.sellist[0], self.sellist[1], True)
                    drawer.drawline(xor_white, self.sellist[0], self.sellist[2], True)
                    if self.selectionShape in ['RECTANGLE', 'DIAMOND']:
                        self._centerRectDiamDraw(color, self.sellist, self.selectionShape, lastDraw)
                    elif self.selectionShape == 'CIRCLE':
                        self._centerCircleDraw(color, self.sellist, lastDraw)
                    elif self.selectionShape == 'HEXAGON':
                        self._centerEquiPolyDraw(color, 6, self.sellist, lastDraw)
                    elif self.selectionShape == 'SQUARE':
                        self._centerEquiPolyDraw(color, 4, self.sellist, lastDraw)
                    elif self.selectionShape == 'TRIANGLE':
                        self._centerEquiPolyDraw(color, 3, self.sellist, lastDraw)   
        else: #Default selection shape
            if self.Rubber:
                if not lastDraw:
                    drawer.drawline(color, self.sellist[-2], self.pickLinePrev)
                drawer.drawline(color, self.sellist[-2], self.sellist[-1])
            else:
                if not lastDraw:
                    for pp in zip(self.sellist[:-2],self.sellist[1:-1]): 
                        drawer.drawline(color, pp[0], pp[1])
                for pp in zip(self.sellist[:-1],self.sellist[1:]):
                    drawer.drawline(color,pp[0],pp[1])
                
                if self.selLassRect:  # Draw the rectangle window
                    if not lastDraw:
                        drawer.drawrectangle(self.sellist[0], self.sellist[-2],
                                     self.o.up, self.o.right, color)
                    drawer.drawrectangle(self.sellist[0], self.sellist[-1],
                                     self.o.up, self.o.right, color)
        
        glFlush()
        self.o.swapBuffers() #Update display         


    def Draw(self):
        basicMode.Draw(self)
        if self.gridShow:    
            self.griddraw()
        #if self.sellist: ## XOR color operation doesn't request paintGL() call.
        #    self.pickdraw()
        if self.o.shape: self.o.shape.draw(self.o, self.layerColors)
        if self.showFullModel:
            self.o.assy.draw(self.o)

    def griddraw(self):
        """Assigned as griddraw for a diamond lattice grid that is fixed in
        space but cut out into a slab one nanometer thick parallel to the 
        screen (and is equivalent to what the cookie-cutter will cut).
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
            lastLayerId = len(self.layers) - 1
            pov = self.layers[lastLayerId]
            pov = V(pov[0], pov[1], pov[2])
            pov -= self.o.shape.pushdown(lastLayerId)
            
            ## Make sure pushdown() doesn't return V(0,0,0)
            self.layers += [pov]
            size = len(self.layers)
           
            # Change the new layer as the current layer
            self.change2Layer(size-1)
            
            return size


    def change2Layer(self, layerIndex):
        """Change current layer to layer <layerIndex>"""
        if layerIndex == self.currentLayer: return
        
        assert layerIndex in range(len(self.layers))
        
        pov = self.layers[layerIndex]
        self.currentLayer = layerIndex
        self.o.pov = V(pov[0], pov[1], pov[2])
        
        maxCells = self._findMaxNoLattCell(self.currentLayer)
        self.ctrlPanel.layerCellsSpinBox.setMaxValue(maxCells)
       
        ##Cancel any selection if any.
        if self.cookieDrawBegins:
            self.w.history.message(redmsg("Layer changed during cookie selection, cancel this selection."))
            self._cancelSelection()
       
        self.o.gl_update()
      
        
    def _findMaxNoLattCell(self, curLay):
        """Find the possible max no of lattice cells for this layer """
        if curLay == len(self.layers) - 1:
            return self.MAX_LATTICE_CELL
        else:
            depth = vlen(self.layers[curLay+1] - self.layers[curLay])
            num = int(depth/(DiGridSp*sqrt(self.whichsurf+1)) + 0.5)
            return num

    def setOrientSurf(self, num):
        """Set the current view orientation surface to <num>, which
        can be one of values(0, 1, 2) representing 100, 110, 111 surface respectively. """
        
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
        """Cancel selection before it's finished """
        self._afterCookieSelection()
        if not self.o.shape: self.ctrlPanel.enableViewChanges(True)
        
    
    def changeLatticeType(self, lType):
        """Change lattice type as 'lType'. """
        self.latticeType = self.LATTICE_TYPES[lType]
        self.o.gl_update()
    
    def changeSelectionShape(self, newShape):
        if newShape != self.selectionShape:
            #Cancel current selection if any. Otherwise, it may cause
            #bugs like 587
            if self.sellist: ##
                self.w.history.message(redmsg("Current cookie selection was cancelled because of selection shape change. "))
                self._cancelSelection()
            self.selectionShape = newShape
    
    def _project2Plane(self, pt):
        """Project a 3d point <pt> into the plane parallel to screen and through "pov". 
            Return the projected point. """
        op = -self.o.pov
        np = self.o.lineOfSight
        
        v1 = op - pt
        v2 = dot(v1, np)*np
        
        vr = pt + v2
        return vr
 
    def _snap100Grid(self, cellOrig, bLen, p2):
        """Snap point <p2> to its nearest 100 surface grid point"""
        orig3d = self._project2Plane(cellOrig)
        out = self.o.out
        sqrt2 = 1.41421356/2
        if abs(out[2]) > 0.5:
            rt0 = V(1, 0, 0)
            up0 = V(0,1, 0)
            right = V(sqrt2, -sqrt2, 0.0)
            up = V(sqrt2, sqrt2, 0.0)
        elif abs(out[0]) > 0.5:
            rt0 = V(0, 1, 0)
            up0 = V(0, 0, 1)
            right = V(0.0, sqrt2, -sqrt2)
            up = V(0.0, sqrt2, sqrt2)
        elif abs(out[1]) > 0.5:
            rt0 = V(0, 0, 1)
            up0 = V(1, 0, 0)
            right = V(-sqrt2, 0.0, sqrt2)
            up = V(sqrt2, 0.0, sqrt2)    
       
        pt1 = p2 - orig3d
        pt = V(dot(rt0, pt1), dot(up0, pt1))
        pt -= V(2*bLen, 2*bLen)
            
        pt1 = V(sqrt2*pt[0]-sqrt2*pt[1], sqrt2*pt[0]+sqrt2*pt[1])
      
        dx = pt1[0]/(2*sqrt2*bLen)
        dy = pt1[1]/(2*sqrt2*bLen)
        if dx > 0: dx += 0.5
        else: dx -= 0.5
        ii = int(dx)
        if dy > 0: dy += 0.5
        else: dy -= 0.5
        jj = int(dy)
            
        nxy = orig3d + 4*sqrt2*bLen*up + ii*2*sqrt2*bLen*right + jj*2*sqrt2*bLen*up
        
        return nxy
 
 
    def _snap110Grid(self, offset, p2):
        """Snap point <p2> to its nearest 110 surface grid point"""
        uLen = 0.87757241
        DELTA = 0.0005

        if abs(self.o.out[1]) < DELTA: #Looking between X-Z
                if self.o.out[2]*self.o.out[0] < 0:
                    vType = 0  
                    right = V(1, 0, 1)
                    up = V(0, 1, 0)
                    rt = V(1, 0, 0)
                else: 
                    vType = 2  
                    if self.o.out[2] < 0:
                        right = V(-1, 0, 1)
                        up = V(0, 1, 0)
                        rt = V(0, 0, 1)
                    else: 
                        right = V(1, 0, -1)
                        up = V(0, 1, 0)
                        rt = V(1, 0, 0)
        elif abs(self.o.out[0]) < DELTA: # Looking between Y-Z
            if self.o.out[1] * self.o.out[2] < 0:  
                vType = 0
                right = V(0, 1, 1)
                up = V(1, 0, 0)
                rt = V(0, 0, 1)
            else:
                vType = 2
                if self.o.out[2] > 0: 
                    right = V(0, -1, 1)
                    up = V(1, 0, 0)
                    rt = V(0, 0, 1)
                else:
                    right = V(0, 1, -1)
                    up = V(1, 0, 0)
                    rt = V(0, 1, 0)
        elif abs(self.o.out[2]) < DELTA: # Looking between X-Y
            if self.o.out[0] * self.o.out[1] < 0:
                vType = 0
                right = V(1, 1, 0)
                up = V(0, 0, 1)
                rt = (1, 0, 0)
            else:
                vType = 2
                if self.o.out[0] < 0:        
                    right = V(1, -1 , 0)
                    up = V(0, 0, 1)
                    rt = (1, 0, 0)
                else:
                    right = V(-1, 1, 0)
                    up = V(0, 0, 1)
                    rt = V(0, 1, 0)
        else: ##Sth wrong
            raise ValueError, self.out
        
        orig3d = self._project2Plane(offset)
        p2 -= orig3d
        pt = V(dot(rt, p2), dot(up, p2))
        
        if vType == 0:  ## projected orig-point is at the corner
            if pt[1] < uLen:
                uv1 = [[0,0], [1,1], [2, 0], [3, 1], [4, 0]]
                ij = self._findSnap4Corners(uv1, uLen, pt)
            elif pt[1] < 2*uLen:
                if pt[0] < 2*uLen:
                    if pt[1] < 1.5*uLen: ij = [1, 1]
                    else: ij = [1, 2]
                else:
                    if pt[1] < 1.5*uLen: ij = [3, 1]
                    else: ij = [3, 2]
            elif pt[1] < 3*uLen:
                uv1 = [[0,3], [1,2], [2,3], [3, 2], [4, 3]]
                ij = self._findSnap4Corners(uv1, uLen, pt)
            else:
                if pt[1] < 3.5*uLen: j = 3
                else: j = 4
                if pt[0] < uLen: i = 0
                elif pt[0] < 3*uLen: i = 2
                else: i = 4
                ij = [i, j]
        
        elif vType == 2: ## projected orig-point is in the middle
             if pt[1] < uLen:
                 if pt[1] < 0.5*uLen: j = 0
                 else: j = 1
                 if pt[0] < -1*uLen: i = -2
                 elif pt[0] < uLen: i = 0
                 else: i = 2
                 ij = [i, j]
             elif pt[1] < 2*uLen:
                 uv1 = [[-2, 1], [-1, 2], [0, 1], [1, 2], [2, 1]]
                 ij = self._findSnap4Corners(uv1, uLen, pt)
             elif pt[1] < 3*uLen:
                 if pt[1] < 2.5*uLen: j = 2
                 else: j = 3
                 if pt[0] < 0: i = -1
                 else: i = 1
                 ij = [i, j]
             else:
                 uv1 = [[-2, 4], [-1, 3], [0, 4], [1, 3], [2, 4]]
                 ij = self._findSnap4Corners(uv1, uLen, pt)
        
        nxy = orig3d + ij[0]*uLen*right + ij[1]*uLen*up
        return nxy
    
    
    def _getNCartP2d(self, ax1, ay1, pt):
        """Axis <ax> and <ay> is not perpendicular, so we project pt to axis
        <ax> or <ay> by parallel to <ay> or <ax>. The returned 2d coordinates are not cartesian coordinates """
        
        ax = norm(ax1)
        ay = norm(ay1)
        try:
            lx = (ay[1]*pt[0] - ay[0]*pt[1])/(ax[0]*ay[1] - ay[0]*ax[1])
            ly = (ax[1]*pt[0] - ax[0]*pt[1])/(ax[1]*ay[0] - ax[0]*ay[1])
        except ZeroDivisionError:
            print " In _getNCartP2d() of cookieMode.py, divide-by-zero detected."
            return None
        
        return V(lx, ly)
        
    
    def _snap111Grid(self, offset, p2):
        """Snap point <p2> to its nearest 111 surface grid point"""
        DELTA = 0.00005
        uLen = 0.58504827
        
        sqrt6 = sqrt(6)
        orig3d = self._project2Plane(V(0, 0,0))
        p2 -= orig3d
        
        if (self.o.out[0] > 0 and self.o.out[1] > 0 and self.o.out[2] > 0) or \
                (self.o.out[0] < 0 and self.o.out[1] < 0 and self.o.out[2] < 0):
            axy =[V(1, 1, -2), V(-1, 2, -1),  V(-2, 1, 1), V(-1, -1, 2), V(1, -2, 1), V(2, -1, -1), V(1, 1, -2)]
        elif (self.o.out[0] < 0 and self.o.out[1] < 0 and self.o.out[2] > 0) or \
                (self.o.out[0] > 0 and self.o.out[1] > 0 and self.o.out[2] < 0):
            axy =[V(1, -2, -1), V(2, -1, 1),  V(1, 1, 2), V(-1, 2, 1), V(-2, 1, -1), V(-1, -1, -2), V(1, -2, -1)]
        elif (self.o.out[0] < 0 and self.o.out[1] > 0 and self.o.out[2] > 0) or \
                (self.o.out[0] > 0 and self.o.out[1] < 0 and self.o.out[2] < 0):
            axy =[V(2, 1, 1), V(1, 2, -1),  V(-1, 1, -2), V(-2, -1, -1), V(-1, -2, 1), V(1, -1, 2), V(2, 1, 1)]
        elif (self.o.out[0] > 0 and self.o.out[1] < 0 and self.o.out[2] > 0) or \
                (self.o.out[0] < 0 and self.o.out[1] > 0 and self.o.out[2] < 0):
            axy =[V(-1, -2, -1), V(1, -1, -2),  V(2, 1, -1), V(1, 2, 1), V(-1, 1, 2), V(-2, -1, 1), V(-1, -2, -1)]
        
        vlen_p2 = vlen(p2)
        if vlen_p2 < DELTA:
            ax = axy[0]
            ay = axy[1]
        else:
            for ii in range(size(axy) -1):
                cos_theta = dot(axy[ii], p2)/(vlen(axy[ii])*vlen_p2)
                ## the 2 vectors has an angle > 60 degrees 
                if cos_theta < 0.5: continue
                cos_theta = dot(axy[ii+1], p2)/(vlen(axy[ii+1])*vlen_p2)
                if cos_theta > 0.5:  
                    ax = axy[ii]
                    ay = axy[ii+1]
                    break
       
        p2d = self._getNCartP2d(ax, ay, p2)
        
        i = int(p2d[0]/uLen/sqrt6 + 0.5)
        j = int(p2d[1]/uLen/sqrt6 + 0.5)
        
        nxy = orig3d + i*uLen*ax + j*uLen*ay 
        
        return nxy
        
    
    def _findSnap4Corners(self, uv1, uLen, pt, vLen = None):
        """Compute  distance from point <pt> to corners and select the nearest corner."""
        if not vLen: vLen = uLen
        hd = 0.5*sqrt(uLen*uLen + vLen*vLen)
        
        ix = int(floor(pt[0]/uLen)) - uv1[0][0]
        if ix == -1: ix = 0
        elif ix == (len(uv1) - 1): ix = len(uv1) - 2
        elif ix < -1 or ix >= len(uv1): raise ValueError, (uv1, pt, uLen, ix)
        
        dist = vlen(V(uv1[ix][0]*uLen, uv1[ix][1]*vLen) - pt)
        if dist < hd:
            return uv1[ix]
        else: return uv1[ix+1]

    
    def _getPoints(self, event):
        """This method is used to get the points in near clipping plane and pov plane which are in line with the mouse clicking point on the screen plane. Adjust these 2 points if self.snapGrid == True.
        <event> is the mouse event.
        Return a tuple of those 2 points.
        """
        p1, p2 = self.o.mousepoints(event, 0.01)
        # For each curve, the following value is constant, so it could be
        # optimized by saving it to the curve object.
        vlen_p1p2 = vlen(p1 - p2) 
        
        if not self.gridSnap: 
            return p1, p2
        else: # Snap selection point to grid point
             cellOrig, uLen = drawer.findCell(p2, self.latticeType)
             
             if self.whichsurf == 0: p2 = self._snap100Grid(cellOrig, uLen, p2)
             elif self.whichsurf == 1: p2 = self._snap110Grid(cellOrig, p2)
             else: p2 = self._snap111Grid(cellOrig, p2)
             
             return p2 + vlen_p1p2*self.o.out, p2
  
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
        assy.unpickparts()
        mol.pick()
        assy.mt.mt_update()

    return # from molmake

# end