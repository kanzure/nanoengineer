# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 2007-05-21: Created. 
ninad 2007-06-03: Implemented Plane Property Manager

This file also used to contain DirectionArrow and  ResizeHandle classes. 
Those were moved to their own module on Aug 20 and Oct 17, 2007 respt.

TODO:
- Need to implement some grid plane features. 

"""

from math import pi, atan, cos, sin
from Numeric import add, dot

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef

# piotr 080527
# added texture-related imports
from OpenGL.GL import glBindTexture
from OpenGL.GL import glDeleteTextures
from OpenGL.GL import GL_TEXTURE_2D

from graphics.drawing.drawers import drawLineLoop
from graphics.drawing.drawers import drawPlane
from graphics.drawing.draw_grid_lines import drawGPGridForPlane
from graphics.drawing.drawers import drawHeightfield
from utilities.constants import black, orange, yellow, brown

from geometry.VQT import V, Q, cross, planeXline, vlen, norm, ptonline
from geometry.BoundingBox import BBox

from utilities.debug import print_compact_traceback
import foundation.env as env

from utilities.Log     import redmsg
from model.ReferenceGeometry import ReferenceGeometry 
from graphics.drawables.DirectionArrow import DirectionArrow
from graphics.drawables.ResizeHandle import ResizeHandle  
from utilities.constants import LOWER_LEFT, LABELS_ALONG_ORIGIN
from graphics.drawing.texture_helpers import load_image_into_new_texture_name

ONE_RADIAN = 180.0 / pi
# One radian = 57.29577951 degrees
# This is for optimization since this computation occurs repeatedly
# in very tight drawning loops. --Mark 2007-08-14


def checkIfValidImagePath(imagePath):
    from PIL import Image
    try:
        im = Image.open(imagePath)
    except IOError:
        return 0
    return 1

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
    logMessage      = ""

    default_opacity      = 0.1
    preview_opacity      = 0.0    
    default_fill_color   = orange
    preview_fill_color   = yellow
    default_border_color = orange
    preview_border_color = yellow


    def __init__(self, 
                 win, 
                 editCommand = None, 
                 atomList = None, 
                 READ_FROM_MMP = False):
        """
        Constructs a plane.

        @param win: The NE1 main window.
        @type  win: L{MainWindow}

        @param editCommand: The Plane Edit Controller object. 
                          If this is None, it means the Plane is created by 
                          reading the data from the MMP file and it doesn't 
                          have  an EditCommand assigned. 
                          The EditCommand may be created at a later stage 
                          in this case. 
                          See L{self.edit} for an example. 
        @type  editCommand: B{Plane_EditCommand} or None                          

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
        self.directionArrow =  None

        # This is used to notify drawing code if it's just for picking purpose
        # copied from class ESPImage 
        self.pickCheckOnly  = False 

        self.editCommand      =  editCommand
        self.imagePath = ""
        self.imageSize = 0
        self.imagePreviousSize = -1
        self.heightfield = None
        self.heightfield_scale = 1.0
        self.heightfield_use_texture = True
        
        # piotr 080528
        # added tex_image attribute for texture image
        self.tex_image = None
        self.tex_coords       = [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0]] 
        
        self.image = None
        self.display_heightfield = False
        self.heightfield_hq = False
        
        #related to grid
        
        self.showGrid = False
        self.gridColor = yellow
        self.gridLineType = 3
        self.gridXSpacing = 4.0
        self.gridYSpacing = 4.0       
        self.displayLabels = False
        self.originLocation = LOWER_LEFT
        self.displayLabelStyle = LABELS_ALONG_ORIGIN
        
        if not READ_FROM_MMP:
            self.width      =  10.0 # piotr 080605 - change default dimensions to square
            self.height     =  10.0  
            self.normcolor  =  black            
            self.setup_quat_center(atomList)   
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
        Update the Cosmetic properties for the Plane. The properties such as 
        bordercolor and fill color are different when the Plane is being 
        'Previewed'.

        @param previewing: Set to True only when previewing. 
                           Otherwise, should be False.
        @type  previewing: bool
        """
        if not previewing:
            try:
                self.fill_color   =  self.default_fill_color				    
                self.border_color =  self.default_border_color
                self.opacity      =  self.default_opacity
            except:
                print_compact_traceback("Can't set properties for the Plane"\
                                        "object. Ignoring exception.")
        else:
            self.fill_color   =  self.preview_fill_color
            self.opacity      =  self.preview_opacity
            self.border_color =  self.preview_border_color


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
                 (self.width, self.height, 
                  self.center[0], self.center[1], self.center[2], 
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
         
        # Urmi-20080613: display grid lines on the plane
        
        if self.showGrid == True:
            drawGPGridForPlane(self.glpane, self.gridColor, self.gridLineType, 
                               self.width, self.height, self.gridXSpacing, self.gridYSpacing,
                               self.quat.unrot(self.glpane.up), self.quat.unrot(self.glpane.right), 
                               self.displayLabels, self.originLocation, self.displayLabelStyle)
            
            self.glpane.gl_update()
            
        textureReady = False
        if self.tex_image:
            textureReady = True
            glBindTexture(GL_TEXTURE_2D, self.tex_image)

        if self.display_heightfield:
            if self.heightfield and self.image:
                if not self.heightfield_use_texture:
                    textureReady = False
                drawHeightfield(fill_color, 
                          self.width, 
                          self.height, 
                          textureReady,
                          self.opacity, 
                          SOLID=True, 
                          pickCheckOnly=self.pickCheckOnly,
                          hf=self.heightfield)
        else:
            drawPlane(fill_color, 
                      self.width, 
                      self.height, 
                      textureReady,
                      self.opacity, 
                      SOLID=True, 
                      pickCheckOnly=self.pickCheckOnly,
                      tex_coords=self.tex_coords)

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
                #when the plane was created and a brown border for the backside.
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
                assert isinstance(hdl, ResizeHandle)
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
                handle = ResizeHandle(self, self.glpane, hCenter)

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
        @type  movedHandle: L{ResizeHandle}

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
        #make resizing stop early (need a bug report) ..minor bug , workaround 
        #is to 
        #do the mousemotion slowly. -- ninad 20070615 
        if dot(vec_v1, vec_P) < 0:
            return          
        #ninad 20070515: vec_P is the orthogonal projection of vec_v2 over 
        #vec_v1 
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
        if self.editCommand and self.editCommand.propMgr:
            self.editCommand.propMgr.update_spinboxes()


    def edit(self):
        """
        Overrides node.edit and shows the property manager.
        """

        commandSequencer = self.win.commandSequencer
        commandSequencer.userEnterTemporaryCommand('REFERENCE_PLANE')
        currentCommand = commandSequencer.currentCommand
        assert currentCommand.commandName == 'REFERENCE_PLANE'
        #When a Plane object read from an mmp file is edited, we need to assign 
        #it an editCommand. So, when it is resized, the propMgr spinboxes
        #are properly updated. See self.resizeGeometry. 
        if self.editCommand is None:
            self.editCommand = currentCommand

        currentCommand.editStructure(self)

    def setup_quat_center(self, atomList = None):
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
            self.center = V(0.0, 0.0, 0.0)
            # Following makes sure that Plane edges are parallel to
            # the 3D workspace borders. Fixes bug 2448
            x, y ,z = self.glpane.right, self.glpane.up, self.glpane.out
            self.quat  = Q(x, y, z) 
            self.quat += Q(self.glpane.right, pi)

    def placePlaneParallelToScreen(self):
        """
        Orient this plane such that it is placed parallel to the screen
        """
        self.setup_quat_center()
        self.glpane.gl_update()

    def placePlaneThroughAtoms(self):
        """
        Orient this plane such that its center is same as the common center of 
        three or more selected atoms.
        """       
        atmList = self.win.assy.selatoms_list()         
        if not atmList:
            msg = redmsg("Select 3 or more atoms to create a Plane.")
            self.logMessage = msg
            return            
        # Make sure more than three atoms are selected.
        if len(atmList) < 3: 
            msg = redmsg("Select 3 or more atoms to create a Plane.")
            self.logMessage = msg
            return
        self.setup_quat_center(atomList = atmList)
        self.glpane.gl_update()

    def placePlaneOffsetToAnother(self):
        """
        Orient the plane such that it is parallel to a selected plane , with an
        offset.
        """

        cmd = self.editCommand.cmd 

        jigList = self.win.assy.getSelectedJigs()
        if jigList:
            planeList = []
            for j in jigList:
                if isinstance(j, Plane) and (j is not self):
                    planeList.append(j)  

            #First, clear all the direction arrow drawings if any in 
            #the existing Plane objectes in the part 
            if not self.assy.part.topnode.members:
                msg = redmsg("Select a different plane first to place the"
                             " current plane offset to it")
                env.history.message(cmd + msg)
                return                            

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

    def loadImage(self, file_name):
        """
        Loads an image to be displayed on the plane as a texture. Displays 
        a warning message if the image format is not supported or the file 
        cannot be open.

        This method should be extened to support basic image operations
        (resizing, flipping, cropping).

        @param file_name: The name of the image file.
        """

        # piotr 080528
        
        self.deleteImage()
        
        try:
            mipmaps, image = load_image_into_new_texture_name(file_name)
            self.tex_image = image
            # this gl_update may not be enough to show the image immediately
            self.glpane.gl_update()
        except:
            msg = redmsg("Cannot load plane image " + file_name)
            env.history.message(msg)
            self.tex_image = None

    def computeHeightfield(self):
        """
        Computes a pseudo-3D "relief" mesh from image data.
        The result is a tuple including vertex, normal, and texture coordinates.
        These arrays are used by drawers.drawHeighfield method.
        """
        
        # calculate heightfield data        
        from PIL import Image
        from PIL.Image import ANTIALIAS
        
        self.heightfield = None
        
        if self.display_heightfield:
            if self.image:
                
                self.heightfield = []
                
                wi, he = self.image.size                
                new_size = self.image.size
                
                # resize if too large (max. 300 pixels (HQ) or 100 pixels)
                
                if self.heightfield_hq:
                    if wi > 300 or \
                       he > 300:
                        new_size = (300, (300 * wi) / he)
                else:
                    if wi > 100 or \
                       he > 100:
                        new_size = (100, (100 * wi) / he)                        

                im = self.image.resize(new_size, ANTIALIAS) # resize
                im = im.convert("L") # compute luminance == convert to grayscale
                pix = im.load()
                
                wi, he = im.size
                
                scale = -self.heightfield_scale/256.0
                
                nz = -1.0/float(he + 1)

                # generate triangle strips
                for y in range(0, he-1):
                    tstrip_vert = []
                    tstrip_norm = []
                    tstrip_tex = []
                    for x in range(0, wi):                       
                        for t in [0, 1]:
                            x0 = float(x) / float(wi - 1) 
                            y0 = float(y+t) / float(he - 1) 
                            
                            # transform according to current texture coordinates
                            """
                            nx = (self.tex_coords[1][0] * (x0) + self.tex_coords[0][0] * (1.0 - x0)) * (1.0 - y0) + \
                                 (self.tex_coords[2][0] * (x0) + self.tex_coords[3][0] * (1.0 - x0)) * y0
                            ny = (self.tex_coords[0][1] * (x0) + self.tex_coords[1][1] * (1.0 - x0)) * (1.0 - y0) + \
                                 (self.tex_coords[3][1] * (x0) + self.tex_coords[2][1] * (1.0 - x0)) * y0
                              
                            x0 = nx
                            y0 = ny
                            """
                            
                            # get data point (the image is converted to grayscale)
                            r0 = scale * pix[x, y+t]

                            # append a vertex
                            tstrip_vert.append([x0 - 0.5, y0 - 0.5, r0])                            
                            # append a 2D texture coordinate 
                            tstrip_tex.append([x0 , 1.0 - y0])
                            
                            # compute normal for lighting
                            if x > 0 and \
                               y > 0 and \
                               x < wi - 1 and \
                               y < he - 2:
                                r1 = scale * pix[x-1, y+t]
                                r2 = scale * pix[x+1, y+t]                        
                                r3 = scale * pix[x, y-1+t]                            
                                r4 = scale * pix[x, y+1+t] 
                                tstrip_norm.append(norm(V(r2-r1, r4-r3, nz)))
                            else:
                                tstrip_norm.append(V(0.0, 0.0, -1.0))

                    self.heightfield.append((tstrip_vert, tstrip_norm, tstrip_tex))

    def loadImageFromValidPath(self):
        """
        Loads an image to be displayed on a plane.
        
        This code is obsolete, image loading functions are now directly called 
        from PlanePropertyManager. piotr 080603
        """

        validImagePath = 0 
        if self.imagePath:
            validImagePath = checkIfValidImagePath(self.imagePath)
        else:
            self.deleteImage()
            self.imagePreviousSize = 0 
            self.tex_image = None

        if validImagePath:
            im = Image.open(self.imagePath)
            self.imageSize = im.size
            # load texture image from the disk only if the image is changed
            if self.imageSize != self.imagePreviousSize:
                try:
                    self.deleteImage()
                    mipmaps, self.tex_image = load_image_into_new_texture_name(self.imagePath)
                    self.imagePreviousSize = self.imageSize
                except:
                    msg = redmsg("Can't load the image file.") 
                    env.history.message(msg)
                    self.deleteImage()
                    self.tex_image = None
            im = None
        else:
            self.deleteImage()
            self.tex_image = None
            self.imagePreviousSize = 0 

 
    def rotateImage(self, direction):
        """
        Rotates plane image texture coordinates clockwise (direction==0)
        or counterclockwise (direction==1) by 90 degrees.
        """
        
        if direction == 0:
            tmp = self.tex_coords[0]
            self.tex_coords[0] = self.tex_coords[3]
            self.tex_coords[3] = self.tex_coords[2]
            self.tex_coords[2] = self.tex_coords[1]
            self.tex_coords[1] = tmp
        else:
            tmp = self.tex_coords[0]
            self.tex_coords[0] = self.tex_coords[1]
            self.tex_coords[1] = self.tex_coords[2]
            self.tex_coords[2] = self.tex_coords[3]
            self.tex_coords[3] = tmp
        
        if self.display_heightfield:
            self.computeHeightfield()
            
        self.glpane.gl_update()
        pass
    
    def mirrorImage(self, direction):
        """
        Mirrors image texture coordinates horizontally (direction==0)
        or vertically (direction==1).
        """
        if direction == 0:            
            tmp = self.tex_coords[3]
            self.tex_coords[3] = self.tex_coords[0]
            self.tex_coords[0] = tmp
            tmp = self.tex_coords[2]
            self.tex_coords[2] = self.tex_coords[1]
            self.tex_coords[1] = tmp
        else:
            tmp = self.tex_coords[3]
            self.tex_coords[3] = self.tex_coords[2]
            self.tex_coords[2] = tmp
            tmp = self.tex_coords[0]
            self.tex_coords[0] = self.tex_coords[1]
            self.tex_coords[1] = tmp
        
        if self.display_heightfield:
            self.computeHeightfield()
            
        self.glpane.gl_update()
        pass
    
    def deleteImage(self):
        """
        Deletes a texture.
        """
        if self.tex_image:
            glDeleteTextures(self.tex_image)
            self.tex_image = None

