# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad,
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 2007-06-21: Created.
ninad 2007-06-01: Implemented DragHandler and selobj interface for classes
      Handles and ReferenceGeoemtry.
ninad 2007-06-03: Implemented Plane Property Manager
ninad 2007-08-20: Moved class DirectionArrow in this file to Directionarrow.py

TODO:
- Need to implement some grid plane features. 

"""

__author__ = "Ninad"

from math import pi, atan, cos, sin
from Numeric import add, dot

from OpenGL.GL import glPushName
from OpenGL.GL import glPopName
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef
from OpenGL.GL import glPopMatrix


from drawer import drawLineLoop, drawPlane
from constants import black, orange, yellow, darkgreen, brown
from VQT import V, Q, cross, planeXline, vlen, norm, ptonline

from debug import print_compact_traceback
import env

from utilities.Log import redmsg

from PlanePropertyManager import PlanePropertyManager
from PlaneGenerator       import PlaneGenerator
from ReferenceGeometry    import ReferenceGeometry 
from DirectionArrow       import DirectionArrow


#Required for class Handle --
from DragHandler import DragHandler_API

ONE_RADIAN = 180.0 / pi
# One radian = 57.29577951 degrees
# This is for optimization since this computation occurs repeatedly
# in very tight drawning loops. --Mark 2007-08-14

class Plane(ReferenceGeometry):
    """ 
    The Plane class provides a reference plane on which to construct other
    2D or 3D structures.
    """
    
    sym             = "Plane"    
    is_movable      = True 
    mutable_attrs   = ('center', 'quat')
    icon_names      = ["modeltree/Plane.png", "modeltree/Plane-hide.png"]
    sponsor_keyword = 'Plane'    
    copyable_attrs  = ReferenceGeometry.copyable_attrs + mutable_attrs
    cmdname         = 'Plane'
    mmp_record_name = "plane"
    
    default_opacity      = 0.1
    preview_opacity      = 0.0    
    default_fill_color   = orange
    preview_fill_color   = yellow
    default_border_color = orange
    preview_border_color = yellow
        
    def __init__(self, win, atomList = None, READ_FROM_MMP = False):
        """
        Constructs a plane.
        
        @param win: The NE1 main window.
        @type  win: L{MainWindow}
        
        @param atomList: List of atoms.
        @type  atomList: list
        
        @param READ_FROM_MMP: True if the plane is read from a MMP file.
        @type  READ_FROM_MMP: bool
        """
        
        self.win = win
                      
        ReferenceGeometry.__init__(self, win)                            
       
        self.fill_color     =  self.default_fill_color
        self.border_color   =  self.default_border_color  
        self.opacity        =  self.default_opacity
        self.handles        =  []   
        self.propMgr        =  PlanePropertyManager(self)
        self.generator      =  PlaneGenerator(self.win, self)
        self.directionArrow =  None
        
        # This is used to notify drawing code if it's just for picking purpose
        # copied from jig_planes.ESPImage 
        self.pickCheckOnly = False 
        
        if not READ_FROM_MMP:
            self.width      =  20.0
            self.height     =  10.0
            self.normcolor  =  black
            
            self._setup_quat_center(atomList)         
            self.propMgr.show()
            self.propMgr.preview_btn_clicked()
        
            self.directionArrow = DirectionArrow(self, 
                                                 self.glpane, 
                                                 self.center, 
                                                 self.getaxis())
    
    def __getattr__(self, attr):
        """
        Recomputes attrs.
        
        @param attr: The attribute to recompute.
        @type  attr: str
        """
        if attr == 'bbox':
            return self.__computeBBox()
        if attr == 'planeNorm':
            return self.quat.rot(V(0.0, 0.0, 1.0))
        if attr == 'members':
            return None # Mark 2007-08-15
        else:
            raise AttributeError, 'Plane has no attr "%s"' % attr 
    
    def __computeBBox(self):
        """
        Compute the plane's current bounding box.
        """
        
        # The move absolute method moveAbsolute() in modifyMode relies on a 
        # 'bbox' attribute for the movables. This attribute is really useless 
        # for Planes otherwise. Instead of modifying that method, I added the 
        # attribute bbox here to fix BUG 2473.
        # -- ninad 2007-06-27.
        
        from shape import BBox
        
        hw = self.width  * 0.5
        hh = self.height * 0.5
        
        corners_pos = [V(-hw,  hh, 0.0), 
                       V(-hw, -hh, 0.0),
                       V( hw, -hh, 0.0), 
                       V( hw,  hh, 0.0)]
        abs_pos = []
        
        for pos in corners_pos:
            abs_pos += [self.quat.rot(pos) + self.center]        
        
        return BBox(abs_pos)
              
    def setProps(self, props):
        """
        Set the Plane properties. It is called while reading a MMP file record.
        
        @param props: The plane's properties.
        @type  props: tuple
        """
        name, border_color, width, height, center, wxyz = props
        
        self.name    =  name
        self.color   =  self.normcolor = border_color
        self.width   =  width
        self.height  =  height
        self.center  =  center 
        self.quat    =  Q(wxyz[0], wxyz[1], wxyz[2], wxyz[3])
        
        if not self.directionArrow:
            self.directionArrow = DirectionArrow(self,
                                                 self.glpane, 
                                                 self.center, 
                                                 self.getaxis())   
            
    def updateCosmeticProps(self, previewing = False):
        """ 
        Update the Cosmetic properties for the Plane. The properties such as border
        color and fill color are different when the Plane is being 'Previewed'.
        
        @param previewing: Set to True only when previewing. Otherwise, should be False.
        @type  previewing: bool
        """
        if not previewing:
            try:
                self.fill_color   =  self.default_fill_color				    
                self.border_color =  self.default_border_color
                self.opacity      =  self.default_opacity
            except:
                print_compact_traceback("Can't set properties for the Plane object\
                Ignoring exception.")
        else:
            self.fill_color   =  self.preview_fill_color
            self.opacity      =  self.preview_opacity
            self.border_color =  self.preview_border_color
            pass
        
    
    def getProps(self):
        """
        Return the current properties of the Plane.
        
        @return: The plane's properties.
        @rtype:  tuple
        """
        # Used in preview method. If an existing structure is changed, and
        # the user clicks "Preview" and then clicks "Cancel", then it restores
        # the old properties of the plane returned by this function.
        props = (self.name, 
                 self.color, 
                 self.width, 
                 self.height, 
                 self.center, 
                 self.quat)
        return props
    
    def mmp_record_jigspecific_midpart(self):
        """
        Returns the "midpart" of the Plane's MMP record in the format:
         - width height (cx, cy, cz) (w, x, y, z)
         
        @return: The midpart of the Plane's MMP record
        @rtype:  str
        """
        #This value is used in method mmp_record  of class Jig
        dataline = "%.2f %.2f (%f, %f, %f) (%f, %f, %f, %f) " % \
           (self.width, self.height, self.center[0], self.center[1], self.center[2], 
            self.quat.w, self.quat.x, self.quat.y, self.quat.z)
        return " " + dataline
                       
    def _draw_geometry(self, glpane, color, highlighted = False):
        """
        Draw the Plane.
        
        @param glpane: The 3D graphics area to draw it in.
        @type  glpane: L{GLPane}
        
        @param color: The color of the plane.
        @type  color: tuple
        
        @param highlighted: This argument determines if the plane is 
                            drawn in the highlighted color.
        @type  highlighted: bool
        """
        # Reference planes don't support textures so set this property to False 
        # in the drawer.drawPlane method        
        textureReady = False
        glPushMatrix()

        glTranslatef( self.center[0], self.center[1], self.center[2])
        q = self.quat
            
        glRotatef( q.angle * ONE_RADIAN, 
                   q.x,
                   q.y,
                   q.z)   
      
        hw = self.width  * 0.5
        hh = self.height * 0.5
        
        bottom_left  = V(- hw, - hh, 0.0)                       
        bottom_right = V(+ hw, - hh, 0.0)        
        top_right    = V(+ hw, + hh, 0.0)
        top_left     = V(- hw, + hh, 0.0)
                
        corners_pos = [bottom_left, bottom_right, top_right, top_left]
        
        if dot(self.getaxis(), glpane.lineOfSight) < 0:
            fill_color = brown #backside
        else:
            fill_color = self.fill_color
                                   
        drawPlane(fill_color, 
                  self.width, 
                  self.height, 
                  textureReady,
                  self.opacity, 
                  SOLID=True, 
                  pickCheckOnly=self.pickCheckOnly)
        
        if self.picked:
            drawLineLoop(self.color, corners_pos)  
            if highlighted:
                drawLineLoop(color, corners_pos, width = 2)            
                pass
            self._draw_handles(corners_pos)    
        else:
            if highlighted:
                drawLineLoop(color, corners_pos, width = 2)
            else:  
                #Following draws the border of the plane in orange color 
                #for it's front side (side that was in front 
                #when the plane was created and a brown border for the back side. 
                if dot(self.getaxis(), glpane.lineOfSight) < 0:
                    bordercolor = brown #backside
                else:
                    bordercolor = self.border_color #frontside
                
                drawLineLoop(bordercolor, corners_pos)
                    
        
        if self.directionArrow.isDrawRequested():
            self.directionArrow.draw()
            
        glPopMatrix()
        
        return
         
    def setWidth(self, newWidth):
        """
        Set the height of the plane.
        
        @param newWidth: The new width.
        @type  newWidth: float
        """
        self.width = newWidth
    
    def setHeight(self, newHeight):
        """
        Set the height of the plane.
        
        @param newHeight: The new height.
        @type  newHeight: float
        """
        self.height = newHeight
    
    def getWidth(self):
        """
        Get the plane's width.
        """
        return self.width
    
    def getHeight(self):
        """
        Get the plane's height.
        """
        return self.height
        
    def getaxis(self):
        """
        Get the plane axis, which is its normal.
        """
        return self.planeNorm
        
    def move(self, offset):
        """
        Move the plane by I{offset}.
        
        @param offset: The XYZ offset.
        @type  offset: L{V}
        """
        self.center += offset
        #Following makes sure that handles move as the geometry moves. 
        #@@ do not call Plane.move method during the Plane resizing. 
        #call recomputeCenter method instead. -- ninad 20070522
        if len(self.handles) == 8:
            for hdl in self.handles:
                assert isinstance(hdl, Handle)
                hdl.move(offset)
            
        
    def rot(self, q):
        """
        Rotate plane by quat I{q}.
        
        @param q: The rotation quat.
        @type  q: L{Q}
        """
        self.quat += q
        
    def _getPlaneOrientation(self, atomPos):
        """
        """
        assert len(atomPos) >= 3
        v1 = atomPos[-2] - atomPos[-1]
        v2 = atomPos[-3] - atomPos[-1]
        
        return cross(v1, v2)
    
    def _draw_handles(self, cornerPoints):
        """
        Draw the handles that permit the geometry resizing. 
        
        Example: For a plane, there will be 8 small squares along the border...
                 4 at plane corners and remaining in the middle of each side 
                 of the plane. The handles will be displayed only when the 
                 geometry is selected.
                 
        @param cornerPoints: List of 4 corner points(V). The handles will be
                             drawn at these corners PLUS in the middle of 
                             each side of the Plane.
        @type  cornerPoints: list of 4 L{V}
        """
        
        handleCenters = list(cornerPoints)
       
        cornerHandleCenters = list(cornerPoints) 
        
        midBtm = (handleCenters[0] + handleCenters[1]) * 0.5      
        midRt  = (handleCenters[1] + handleCenters[2]) * 0.5
        midTop = (handleCenters[2] + handleCenters[3]) * 0.5
        midLft = (handleCenters[3] + handleCenters[0]) * 0.5
                
        for midpt in [midBtm, midRt, midTop, midLft]:
            handleCenters.append(midpt)
                
        if len(self.handles) == 8:   
            assert len(self.handles) == len(handleCenters)
            i = 0
            for i in range(len(self.handles)):
                self.handles[i].draw(hCenter = handleCenters[i])
        else:   
            hdlIndex = 0
            for hCenter in handleCenters: 
                handle = Handle(self, self.glpane, hCenter)
                
                handle.draw() 
                if handle not in self.handles:
                    self.handles.append(handle)
                #handleIndex = 0, 1, 2, 3 -->
                #--> bottomLeft, bottomRight, topRight, topLeft corners respt
                #handleIndex = 4, 5, 6, 7 -->
                #-->midBottom, midRight, midTop, midLeft Handles respt.
                if hdlIndex == 5 or hdlIndex == 7: 
                    handle.setType('Width-Handle')
                elif hdlIndex == 4 or hdlIndex == 6:
                    handle.setType('Height-Handle')
                else:
                    handle.setType('Corner')
                
                hdlIndex +=1
                                            
    def recomputeCenter(self, handleOffset):
        """
        Recompute the center of the Plane based on the handleOffset
        This is needed during resizing.
        """
        
        ##self.move(handleOffset / 2.0) 
        self.center += handleOffset / 2.0
    
    def getHandlePoint(self, hdl, event):
                
        #First compute the intersection point of the mouseray with the plane 
        #This will be our first self.handle_MovePt upon left down. 
        #This value is further used in handleLeftDrag. -- Ninad 20070531
        p1, p2     = self.glpane.mousepoints(event)
        linePoint  = p2
        lineVector = norm(p2 - p1)
        planeAxis  = self.getaxis()
        planeNorm  = norm(planeAxis)
        planePoint = self.center
        
        #Find out intersection of the mouseray with the plane. 
        intersection = planeXline(planePoint, planeNorm, linePoint, lineVector)
        if intersection is None:
            intersection =  ptonline(planePoint, linePoint, lineVector)
            
        handlePoint = intersection
        
        return handlePoint
    
    def resizeGeometry(self, movedHandle, event):
        """
        Resizes the plane's width, height or both depending upon 
        the handle type.
        
        @param movedHandle: The handle being moved.
        @type  movedHandle: L{Handle}
        
        @param event: The mouse event.
        @type  event: QEvent
        """ 
        
        #NOTE: mouseray contains all the points 
        #that a 'mouseray' will travel , between points p1 and p2 .  
        # The intersection of mouseray with the Plane (this was suggested 
        #by Bruce in an email) is our new handle point.
        #obtained in left drag. 
        #The first vector (vec_v1) is the vector obtained by using 
        #plane.quat.rot(handle center)        
        #The handle_NewPt is used to find the second vector
        #between the plane center and this point. 
        # -- Ninad 20070531, (updated 20070615)
        
        handle_NewPt = self.getHandlePoint(movedHandle, event)   
        
        #ninad 20070615 : Fixed the resize geometry bug 2438. Thanks to Bruce 
        #for help with the formula that finds the right vector! (vec_v1)
        vec_v1 = self.quat.rot(movedHandle.center) 
    
        vec_v2 = V(handle_NewPt[0] - self.center[0],
                   handle_NewPt[1] - self.center[1],
                   handle_NewPt[2] - self.center[2])                       
        
        #Orthogonal projection of Vector V2 over V1 call it vec_P. 
        #See Plane.resizeGeometry  for further details -- ninad 20070615
        #@@@ need to document this further. 

        vec_P = vec_v1 * (dot(vec_v2, vec_v1) / dot(vec_v1,vec_v1))
        
        #The folllowing puts 'stoppers' so that if the mouse goes beyond the
        #opposite face while dragging, the plane resizing is stopped.
        #This fixes bug 2447. (It still has a bug where fast mouse movements 
        #make resizing stop early (need a bug report) ..minor bug , workaround is to 
        #do the mousemotion slowly. -- ninad 20070615 
        if dot(vec_v1, vec_P) < 0:
            return          
        #ninad 20070515: vec_P is the orthogonal projection of vec_v2 over vec_v1 
        #(see selectMode.handleLeftDrag for definition of vec_v2). 
        #The total handle movement is by the following offset. So, for instance
        #the fragged handle was a 'Width-Handle' , the original width of the 
        #plane is changed by the vlen(totalOffset). Since we want to keep the 
        #opposite side of the plane fixed during resizing, we need to offset the 
        #plane center , along the direction of the following totalOffsetVector
        #(Remember that the totalOffsetVector is along vec_v1. 
        #i.e. the angle is either 0 or 180), and , by a distance equal to 
        #half the length of the totalOffset. Before moving the center 
        #by this amount we need to recompute the new width or height 
        #or both of the plane because those new values will be used in 
        #the Plane drawing code     
        
        totalOffset = vec_P - vec_v1    
          
        if vlen(vec_P) > vlen(vec_v1):
            new_dimension = 2 * vlen(vec_v1) + vlen(totalOffset)
        else:
            new_dimension = 2 * vlen(vec_v1) - vlen(totalOffset)
                        
        if movedHandle.getType() == 'Width-Handle' : 
            new_w = new_dimension  
            self.setWidth(new_w)
        elif movedHandle.getType() == 'Height-Handle' :
            new_h = new_dimension
            self.setHeight(new_h)
        elif movedHandle.getType() == 'Corner':            
            wh    = 0.5 * self.getWidth()
            hh    = 0.5 * self.getHeight()
            theta = atan(hh / wh)
            new_w = (new_dimension) * cos(theta)
            new_h = (new_dimension) * sin(theta)
            
            self.setWidth(new_w)
            self.setHeight(new_h)            
            
        self.recomputeCenter(totalOffset)
        #update the width,height spinboxes(may be more in future)--Ninad20070601
        self.propMgr.update_spinboxes()
        
        pass
        
    def edit(self):
        """
        Overrided node.edit and shows the property manager.
        """
        self.generator.existingStructForEditing = True
        self.generator.old_props = self.getProps()
        self.propMgr.show()    
                
    def changePlanePlacement(self, buttonId):
        """
        Slot to change the placement of the plane depending upon the 
        option checked in the "Placement Options" group box of the PM.
        
        @param buttonId: The button id of the selected radio button (option).
        @type  buttonId: int
        """       
        if buttonId == 0:
            msg = "Create a Plane parallel to the screen. \
            NOTE: With <b>Parallel to Screen</b> plane placement option, the center \
            of the plane is always (0,0,0). This value is set during plane \
            creation or when the <b>Preview</b> button is clicked."
            self.propMgr.MessageGroupBox.insertHtmlMessage(msg,
                                                           setAsDefault = False,
                                                           minLines     = 5)
            self._setup_quat_center()
            self.glpane.gl_update()
        elif buttonId == 1:
            self._createPlaneThroughAtoms()
        elif buttonId == 2:
            self._createOffsetPlane()
        elif buttonId == 3:
            #'Custom' plane placement. Do nothing (only update message box)
            # Fixes bug 2439
            msg = "Create a plane with a <b>Custom</b> plane placement. During \
            its creation, the plane is placed parallel to the screen, with \
            center at (0, 0, 0). User can then modify the plane placement."
            self.propMgr.MessageGroupBox.insertHtmlMessage(msg,
                                                           setAsDefault = False,
                                                           minLines     = 5)
            pass
            
    def _setup_quat_center(self, atomList = None):
        """
        Setup the plane's quat using a list of atoms.
        
        If no atom list is supplied, the plane is centered in the glpane
        and parallel to the screen.
        
        @param atomList: A list of atoms.
        @type  atomList: list
        
        """
        if atomList:    
            self.atomPos = []
            for a in atomList:
                self.atomPos += [a.posn()]    
            planeNorm = self._getPlaneOrientation(self.atomPos)
            if dot(planeNorm, self.glpane.lineOfSight) < 0:
                planeNorm = -planeNorm                
            self.center = add.reduce(self.atomPos) / len(self.atomPos)
            self.quat   = Q(V(0.0, 0.0, 1.0), planeNorm) 
        else:       
            self.center = [0.0, 0.0, 0.0] 
            # Following makes sure that Plane edges are parallel to
            # the 3D workspace borders. Fixes bug 2448
            x, y ,z = self.glpane.right, self.glpane.up, self.glpane.out
            self.quat  = Q(x, y, z) 
            self.quat += Q(self.glpane.right, pi)
                        
    def _createPlaneThroughAtoms(self):
        """
        Create a Plane with center same as the common center of 
        three or more selected atoms.
        """
        
        cmd = self.generator.cmd 
        msg = "Create a Plane with center coinciding with the common center \
        of <b> 3 or more selected atoms </b>. If exactly 3 atoms are selected, \
        the Plane will pass through those atoms. Select atoms and hit \
        <b>Preview</b> to see the new Plane placement"
        
        self.propMgr.MessageGroupBox.insertHtmlMessage(msg, 
                                                       setAsDefault = False,
                                                       minLines     = 5)
        atmList = self.win.assy.selatoms_list()         
        if not atmList:
            msg = redmsg("Select 3 or more atoms to create a Plane.")
            env.history.message(cmd + msg)
            return            
        # Make sure more than three atoms are selected.
        if len(atmList) < 3: 
            msg = redmsg("Select 3 or more atoms to create a Plane.")
            env.history.message(cmd + msg)
            return
        self._setup_quat_center(atomList = atmList)
        self.glpane.gl_update()
    
    def _createOffsetPlane(self):
        """
        Create a plane offset to a selected plane.
        """
        cmd = self.generator.cmd 
        msg = "Create a Plane,at an <b> offset</b> to the selected plane,\
            in the direction indicated by the direction arrow. \
            Select an existing plane and hit <b>Preview</b>.\
            You can click on the direction arrow to reverse its direction."
        self.propMgr.MessageGroupBox.insertHtmlMessage(msg, 
                                                       setAsDefault = False,
                                                       minLines     = 5)
        jigList = self.win.assy.getSelectedJigs()
        if jigList:
            planeList = []
            for j in jigList:
                if isinstance(j, Plane) and (j is not self):
                        planeList.append(j)  
                        
            #First, clear all the direction arrow drawings if any in 
            #the existing Plane objectes in the part 
            for p in self.assy.part.topnode.members:
                if isinstance(p, Plane):
                    if p.directionArrow:
                        p.directionArrow.setDrawRequested(False)
                                    
            if len(planeList) == 1:                
                self.offsetParentGeometry = planeList[0]
                self.offsetParentGeometry.directionArrow.setDrawRequested(True)
                
                if self.offsetParentGeometry.directionArrow.flipDirection:
                    offset =  2 * norm(self.offsetParentGeometry.getaxis())
                else:
                    offset = -2 * norm(self.offsetParentGeometry.getaxis())
                    
                self.center = self.offsetParentGeometry.center + offset   
                self.quat   = Q(self.offsetParentGeometry.quat)
            else:
                msg = redmsg("Select exactly one plane to\
                create a plane offset to it.")
                env.history.message(cmd + msg)
                return            
        else:            
            msg = redmsg("Select an existing plane first to\
            create a plane offset to it.")
            env.history.message(cmd + msg)
            return    
        self.glpane.gl_update()            
    
                      
class Handle(DragHandler_API):
    """
    @@@EXPERIMENTAL -- ninad 2007-05-17 
    - unrelated with things in handles.py
    - soon it will be moved to handles.py (with added docstrings) -ninad20070521
    """
    def __init__(self, parent, glpane, handleCenter):
        self.parent = parent
        #this could be parent.glpane , but pass glpane object explicitely
        #for creating  a handle to avoid any errors
        self.glpane = glpane
        self.center = handleCenter
        # No texture in handles (drawn Handle object). 
        # Ideally the following value in the drawer.drawPlane method 
        #should be False by default.
        self.textureReady  = False
        self.pickCheckOnly = False        
        self.glname = env.alloc_my_glselect_name(self)        
        self.type   = None      
    
    def draw(self, hCenter = None):
        try:
            glPushName(self.glname)
            if hCenter:
                self._draw(hCenter)    
            else:
                self._draw()
        except:
            glPopName()
            print_compact_traceback("ignoring exception when drawing handle %r: " % self)
        else:
            glPopName()
    
    def _draw(self, hCenter = None, highlighted = False):
        """
        Draw the handle object.
        
        @param hCenter: The center of the handle. If None, use the handle's 
                        I{center} property.
        @type  hCenter: V
        
        @param highlighted: This argument determines if the handle is 
                            drawn in the highlighted color.
        @type  highlighted: bool
        """        
        
        if hCenter:
            if self.center != hCenter:
                self.center = hCenter    
                   
        #Use glpane's scale for drawing the handle. This makes sure that
        # the handle is non-zoomable. 
        side = self.glpane.scale * 0.018                
        glPushMatrix() 
        
        
        #Translate to the center of the handle
        glTranslatef(self.center[0], 
                     self.center[1], 
                     self.center[2])  
                        
        #Bruce suggested undoing the glpane.quat rotation and plane quat rotation 
        #before drawing the handle geometry. -- ninad 20070525
        
        parent_q = self.parent.quat 
        
        if parent_q:
            glRotatef(-parent_q.angle * ONE_RADIAN,
                       parent_q.x, 
                       parent_q.y, 
                       parent_q.z)
            
        glpane_q = self.glpane.quat
        glRotatef(-glpane_q.angle * ONE_RADIAN, 
                   glpane_q.x, 
                   glpane_q.y, 
                   glpane_q.z) 
       
        drawPlane(darkgreen, 
                  side, 
                  side, 
                  self.textureReady,
                  0.9, 
                  SOLID         = True, 
                  pickCheckOnly = self.pickCheckOnly)         
        
        handle_hw = side/2.0 #handle's half width
        handle_hh = side/2.0 #handle's half height        
        handle_corner = [V(-handle_hw,  handle_hh, 0.0), 
                         V(-handle_hw, -handle_hh, 0.0), 
                         V( handle_hw, -handle_hh, 0.0), 
                         V( handle_hw,  handle_hh, 0.0)]   
        
        if highlighted:    
            drawLineLoop(orange, handle_corner, width = 6)
        else:
            drawLineLoop( black, handle_corner, width = 2)                
        glPopMatrix()
        
    def draw_in_abs_coords(self, glpane, color):
        """
        Draw the handle as a highlighted object.
        
        @param glpane: The 3D Graphics area.
        @type  gplane: L{GLPane}
        
        @param color: Unused.
        @type  color:
        
        @attention: I{color} is not used.
        """          
        q = self.parent.quat  
        glPushMatrix()
        if self.parent.center:
            glTranslatef( self.parent.center[0],
                          self.parent.center[1], 
                          self.parent.center[2])
        if q:
            glRotatef( q.angle * ONE_RADIAN, 
                       q.x,
                       q.y,
                       q.z)            
        
        self._draw(highlighted = True)
        glPopMatrix()
        
    def move(self, offset):
        """
        Move the handle by I{offset}.
        
        @param offset: The offset of the handle, in Angstroms.
        @type  offset: V
        """
        self.center += offset
    
    def setType(self, handleType):
        """
        Sets the handle type.
        @param handleType: The handle type. Must be one of:
                           'Width-Handle', 'Height-Handle', or 'Corner'.
        @type  handleType: str
        """
        assert handleType in [ 'Width-Handle', 'Height-Handle', 'Corner']
        self.type = handleType
       
    def getType(self):
        """
        Returns the handle type.
        
        @return: The handle type, which is either
                 'Width-Handle', 'Height-Handle', or 'Corner'.
        @rtype:  str
        """
        assert self.type is not None
        return self.type
        
    ###============== selobj interface Starts ===============###
     
    #Methods for selobj interface  . Note that draw_in_abs_coords method is 
    #already defined above.  -- Ninad 20070612
    
    #@TODO Need some documentation. Basically it implements the selobj 
    #interface mentioned in exprs.Highlightable.py
    
    def leftClick(self, point, event, mode):
        mode.handleLeftDown(self, event)
        mode.update_selobj(event)
        return self               

    def mouseover_statusbar_message(self):
        msg1 = "Parent:"
        msg2 = str(self.parent.name)
        msg3 = " Type: "
        msg4 = self.getType()
        return msg1 + msg2 + msg3 + msg4
        
    def highlight_color_for_modkeys(self, modkeys):
        return orange
    
    # Copied Bruce's code from class Highlightable with some mods. 
    # Need to see if selobj_still_ok() is needed. OK for now.
    # --Ninad 2007-05-31
    def selobj_still_ok(self, glpane):
        res = self.__class__ is ReferenceGeometry 
        if res:
            our_selobj = self
            glname     = self.glname
            owner      = env.obj_with_glselect_name.get(glname, None)
            if owner is not our_selobj:
                res = False
                # Owner might be None, in theory, but is probably a replacement
                # of self at same ipath. Do debug prints.
                print "%r no longer owns glname %r, instead %r does" \
                      % (self, glname, owner) # [perhaps never seen as of 061121]
                our_ipath   = self.ipath
                owner_ipath = getattr(owner, 'ipath', '<missing>')
                if our_ipath != owner_ipath:
                    # [perhaps never seen as of 061121]
                    print "WARNING: ipath for that glname also changed, \
                           from %r to %r" % (our_ipath, owner_ipath)
                pass
            pass
            # MORE IS PROBABLY NEEDED HERE: that check above is about whether this selobj got replaced locally;
            # the comments in the calling code are about whether it's no longer being drawn in the current frame;
            # I think both issues are valid and need addressing in this code or it'll probably cause bugs. [061120 comment] ###BUG
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self ###@@@
        return res # I forgot this line, and it took me a couple hours to debug that problem! Ugh.
            # Caller now prints a warning if it's None. 
    ###============== selobj interface Ends ===============###
    
    ###=========== Drag Handler interface Starts =============###
    #@TODO Need some documentation. Basically it implements the drag handler 
    #interface described in DragHandler.py See also exprs.Highlightable.py
    
    def handles_updates(self): 
        return True
            
    def DraggedOn(self, event, mode): 
        mode.handleLeftDrag(self, event)
        mode.update_selobj(event)
        return
    
    def ReleasedOn(self, selobj, event, mode): 
        pass
    ###=========== Drag Handler interface Ends =============###
