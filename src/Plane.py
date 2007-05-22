# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from ReferenceGeometry import ReferenceGeometry 
from shape import fill
from drawer import drawLineLoop, drawPlane
from constants import black, gray, orange, yellow, darkgreen
from VQT import V,Q, cross, dot
from OpenGL.GL import *
from math import pi
from debug import print_compact_traceback
import env

class Plane(ReferenceGeometry):    
    sym = "Plane"    
    is_movable = True 
    mutable_attrs = ('center', 'quat')
    icon_names = ["modeltree/plane.png", "modeltree/plane-hide.png"]
    
    copyable_attrs = ReferenceGeometry.copyable_attrs + mutable_attrs
    
    def __init__(self, win, lst = None, READ_FROM_MMP = False):
        ''' 
        @param: win: MainWindow object
        @param: lst: List of atoms or points'''
        ReferenceGeometry.__init__(self, win)        
        self.width = 16
        self.height = 16                    
        self.normcolor = black
        self.fill_color = gray
        
        self.opacity = 0.3
        
        self.handles = []        
        self.cornerHandles = []
        self.middleHandles = []   
        
        #This is used to notify drawing code if it's just for picking purpose
        #copied from jig_planes.ESPImage
        self.pickCheckOnly=False 
        
        if not READ_FROM_MMP:
            self.__init_quat_center(lst)
    
    def __getattr__(self, name): # in class RectGadget
        if name == 'planeNorm':
            return self.quat.rot(V(0.0, 0.0, 1.0))
        else:
            raise AttributeError, 'Plane has no "%s"' % name 
        
    
    def draw(self, glpane, dispdef):
        try:
            glPushName(self.glname)
            self._draw(glpane, dispdef)
        except:
            glPopName()
            print_compact_traceback("ignoring exception when drawing Plane %r: " % self)
        else:
            glPopName()
                    
                    
    def _draw_geometry_ORIG(self, glpane, color, highlighted=False):
        '''Draw a Plane.'''
        
        # Reference planes don't support textures so set this property to False 
        # in the drawer.drawPlane method        
        textureReady = False
        glPushMatrix()

        glTranslatef( self.center[0], self.center[1], self.center[2])
        q = self.quat
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)

        hw = self.width/2.0; hh = self.height/2.0
        
        corners_pos = [V(-hw, hh, 0.0), 
                       V(-hw, -hh, 0.0), 
                       V(hw, -hh, 0.0), 
                       V(hw, hh, 0.0)]
        
                
        drawPlane(self.fill_color, 
                  self.width, 
                  self.height, 
                  textureReady,
                  self.opacity, 
                  SOLID=True, 
                  pickCheckOnly=self.pickCheckOnly)
        
        if self.picked:
            drawLineLoop(self.color, corners_pos)  
        else:
            if highlighted:
                drawLineLoop(yellow, corners_pos, width=2)
            else:  
                #Following draws the border of the plane in orange color 
                #for it's front side (side that was in front 
                #when the plane was created and a gray border for the back side. 
                if dot(self.getaxis(), glpane.lineOfSight) < 0:
                    bordercolor = gray #backside
                else:
                    bordercolor = color #frontside
                drawLineLoop(bordercolor, corners_pos)                  
        glPopMatrix()
        
        #We need to compute the corner positions to draw 
        #the handles. The list 'corners_pos' can't be used for this 
        #purpose as it computes the corners in a translation matrix 
        #whose center is always at the center of the geometry. 
        # Then why not use the above translation matrix for handles?
        #-- we can't do this because then the handles are not drawn parallel
        #to the screen in some orientations (i.e. user doesn't see them as 
        #squares in some orientations) -- ninad 20070518
        corner_handle_pos = []
        bottom_left = V(self.center[0] - hw,
                        self.center[1] - hh,
                        self.center[2])
        bottom_right = V(self.center[0] + hw,
                        self.center[1] - hh,
                        self.center[2])
        
        top_right = V(self.center[0] + hw,
                        self.center[1] + hh,
                        self.center[2])
        top_left = V(self.center[0] - hw,
                        self.center[1] + hh,
                        self.center[2])
        
        
        corner_handle_pos = [ bottom_left,
                              bottom_right,
                              top_right,
                              top_left
                              ]        
        
        # Draw the handles when selected. 
        if self.picked:
            self._draw_handles(corner_handle_pos)
            if highlighted:
                glPushMatrix()
                glTranslatef( self.center[0], self.center[1], self.center[2])
                q = self.quat
                glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)
                drawLineLoop(yellow, corners_pos, width=2)
                glPopMatrix()
           
        return
    
    def _draw_geometry(self, glpane, color, highlighted=False):
        '''Draw a Plane.'''
        
        # Reference planes don't support textures so set this property to False 
        # in the drawer.drawPlane method        
        textureReady = False
        glPushMatrix()

        glTranslatef( self.center[0], self.center[1], self.center[2])
        q = self.quat
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)

        hw = self.width/2.0; hh = self.height/2.0
        
        corners_pos = [V(-hw, hh, 0.0), 
                       V(-hw, -hh, 0.0), 
                       V(hw, -hh, 0.0), 
                       V(hw, hh, 0.0)]
        
                
        drawPlane(self.fill_color, 
                  self.width, 
                  self.height, 
                  textureReady,
                  self.opacity, 
                  SOLID=True, 
                  pickCheckOnly=self.pickCheckOnly)
        
        if self.picked:
            drawLineLoop(self.color, corners_pos)  
        else:
            if highlighted:
                drawLineLoop(yellow, corners_pos, width=2)
            else:  
                #Following draws the border of the plane in orange color 
                #for it's front side (side that was in front 
                #when the plane was created and a gray border for the back side. 
                if dot(self.getaxis(), glpane.lineOfSight) < 0:
                    bordercolor = gray #backside
                else:
                    bordercolor = color #frontside
                drawLineLoop(bordercolor, corners_pos)                  
        glPopMatrix()
        
        #We need to compute the corner positions to draw 
        #the handles. The list 'corners_pos' can't be used for this 
        #purpose as it computes the corners in a translation matrix 
        #whose center is always at the center of the geometry. 
        # Then why not use the above translation matrix for handles?
        #-- we can't do this because then the handles are not drawn parallel
        #to the screen in some orientations (i.e. user doesn't see them as 
        #squares in some orientations) -- ninad 20070518
                
        bottom_left = V(self.center[0] - hw,
                        self.center[1] - hh,
                        self.center[2])
        bottom_right = V(self.center[0] + hw,
                        self.center[1] - hh,
                        self.center[2])
        
        top_right = V(self.center[0] + hw,
                        self.center[1] + hh,
                        self.center[2])
        top_left = V(self.center[0] - hw,
                        self.center[1] + hh,
                        self.center[2])
        
        cornerHandleCenters =  [bottom_left,bottom_right,
                                top_right,top_left]       
                    
    
        # Draw the handles when selected. 
        if self.picked:
            self._draw_handles(cornerHandleCenters)
            if highlighted:
                glPushMatrix()
                glTranslatef( self.center[0], self.center[1], self.center[2])
                q = self.quat
                glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)
                drawLineLoop(yellow, corners_pos, width=2)
                glPopMatrix()
           
        return
    
    
    def _draw_handles_ORIG(self, cornerPoints):
        '''' Draw the handles that permit the geometry resizing. 
        Example: For a plane, there will be 8 small squares along the 
        border...4 at plane corners and remaining in the middle 
        of each side of the plane. The handles will be displayed only when the 
        geometry is selected
        @param: cornerPoints : List of corner points. The handles will be
        drawn at these corners PLUS in the middle of each side of tthe Plane'''
        
        # No texture in handles. 
        # Ideally the following value in the drawer.drawPlane method 
        #should be False by default.
        textureReady = False
        
        #self.handles (a list containing the centerpoints of all the handles)
        self.handles = cornerPoints
                 
        midpoint1 = (self.handles[0] + self.handles[1])/2      
        midpoint2 = (self.handles[1] + self.handles[2])/2
        midpoint3 = (self.handles[2] + self.handles[3])/2
        midpoint4 = (self.handles[3] + self.handles[0])/2
        for midpt in [midpoint1,midpoint2, midpoint3, midpoint4]:
            self.handles.append(midpt)
        
        
        #Always draw the handle geometry facing the line of sight. So that 
        #the handles are visible in any orientation of the plane.   

        handleNorm = self.glpane.lineOfSight        
        handleQuat = Q(V(0.0, 0.0, 1.0), handleNorm)
        
        #Use glpane's scale for drawing the handle. This makes sure that
        # the handle is non-zoomable. 
        side = self.glpane.scale*0.015
        
        for handle in self.handles:  
            glPushMatrix()                
            glTranslatef(handle[0], handle[1], handle[2])
            q = handleQuat
            glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)
            drawPlane(darkgreen, 
                  side, 
                  side, 
                  textureReady,
                  0.9, 
                  SOLID=True, 
                  pickCheckOnly=self.pickCheckOnly) 
            
            
            handle_hw = side/2.0 #handle's half width
            handle_hh = side/2.0 #handle's half height
            
            handle_corner = [V(-handle_hw, handle_hh, 0.0), 
                   V(-handle_hw, -handle_hh, 0.0), 
                   V(handle_hw, -handle_hh, 0.0), 
                   V(handle_hw, handle_hh, 0.0)]                
            drawLineLoop(black, handle_corner)                
            glPopMatrix()
         
    def __init_quat_center(self, lst = None):
        if lst:    
            self.atomPos =[]
            for a in lst:
                self.atomPos += [a.posn()]    
            planeNorm = self._getPlaneOrientation(self.atomPos)
            self.center = add.reduce(self.atomPos)/len(self.atomPos)
        else:            
            planeNorm = self.glpane.lineOfSight
            self.center = [0.0,0.0,0.0]        
        self.quat = Q(V(0.0, 0.0, 1.0), planeNorm)
    
    def setWidth(self, newwidth):
        self.width = newwidth
    
    def setHeight(self, newheight):
        self.height = newheight
    
    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height
        
    def getaxis(self):
        return self.planeNorm
        
    def move(self, offset):
        '''Move the plane by <offset>, which is a 'V' object.'''
        self.center += offset
        
    def rot(self, q):
        self.quat += q
        
    def _getPlaneOrientation(self, atomPos):
        assert len(atomPos) >= 3
        v1 = atomPos[-2] - atomPos[-1]
        v2 = atomPos[-3] - atomPos[-1]
        
        return cross(v1, v2)
    
    def _draw_handles(self, cornerPoints):
        '''' Draw the handles that permit the geometry resizing. 
        Example: For a plane, there will be 8 small squares along the 
        border...4 at plane corners and remaining in the middle 
        of each side of the plane. The handles will be displayed only when the 
        geometry is selected
        @param: cornerPoints : List of corner points. The handles will be
        drawn at these corners PLUS in the middle of each side of tthe Plane'''
        
        handleCenters = list(cornerPoints)
                 
        midpoint1 = (handleCenters[0] + handleCenters[1])/2      
        midpoint2 = (handleCenters[1] + handleCenters[2])/2
        midpoint3 = (handleCenters[2] + handleCenters[3])/2
        midpoint4 = (handleCenters[3] + handleCenters[0])/2
        
        for midpt in [midpoint1,midpoint2, midpoint3, midpoint4]:
            handleCenters.append(midpt)
  
        for hCenter in handleCenters: 
            handle = Handle(self, self.glpane, hCenter)
            handle.draw() 
        
        cornerHandleCenters = list(cornerPoints) 
      
        for hCenter in handleCenters:
            if handle not in self.handles:
                self.handles.append(handle)
            if hCenter in cornerHandleCenters:
                if handle not in self.cornerHandles:
                    self.cornerHandles.append(handle)
      
    def recomputeCenter(self, bottomleftPt):
        ''' Recompute the center of the Plane based on a new corner point
        This is needed during resizing'''
        
        pt = bottomleftPt
        w = self.getWidth()
        h = self.getHeight()
        
        self.center[0] =  pt[0] + w/2
        self.center[1] = pt[1] + h/2
        
    def recomputeHandleCenters(self, movedHandle, offset):
        ''' Recompute the coordinates of all the handle centers
        based on the handle moved.'''
        
        assert movedHandle in self.handles
        
        #@@@EXPERIMENTAL. Still work in progress -- ninad 20070518
        #this is intended only for midpoint handles. Need special cases 
        #for corners. -- NIY
        
        print "***self.handles :", self.handles
        movedHandle.center += offset
        neighbors = []
        neighbors = list(movedHandle.nearestNeighbors())
        ##neighbors = movedHandle.nearestNeighbors()
        for hdl in neighbors:
            if hdl in self.handles:
                hdl.center += offset    
    
    def resizeGeometry(self, movedHandle, offset):
        self.recomputeHandleCenters(movedHandle, offset)
        btmLeftHandle = self.cornerHandles[0]
        btmLeftPoint = btmLeftHandle.center        
        self.recomputeCenter(btmLeftPoint)
                
            
class Handle:
    '''@@@EXPERIMENTAL -- ninad 20070517 
    - unreleated with things in handles.py
    - soon it will be moved to handles.py (with added docstrings)-ninad20070521'''
    def __init__(self, parent, glpane, handleCenter):
        self.parent = parent
        #this could be parent.glpane , but pass glpane object explicitely
        #for creating  a handle to avoid any errors
        self.glpane = glpane
        
        self.center = handleCenter
        # No texture in handles (drawn Handle object). 
        # Ideally the following value in the drawer.drawPlane method 
        #should be False by default.
        self.textureReady = False
        self.pickCheckOnly = False
        
        self.glname = env.alloc_my_glselect_name(self)
               
    
    def draw(self):
        try:
            glPushName(self.glname)
            self._draw()    
        except:
            glPopName()
            print_compact_traceback("ignoring exception when drawing handle %r: " % self)
        else:
            glPopName()
    
    def _draw(self, highlighted = False):
        ''' Draw the handle object '''        
        
        #Always draw the handle geometry facing the line of sight. So that 
        #the handles are visible in any orientation of the plane.   

        handleNorm = self.glpane.lineOfSight        
        handleQuat = Q(V(0.0, 0.0, 1.0), handleNorm)
        
        #Use glpane's scale for drawing the handle. This makes sure that
        # the handle is non-zoomable. 
        side = self.glpane.scale*0.15        
        
        glPushMatrix()                
        glTranslatef(self.center[0], 
                     self.center[1], 
                     self.center[2])
        q = handleQuat
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)
        drawPlane(darkgreen, 
              side, 
              side, 
              self.textureReady,
              0.9, 
              SOLID=True, 
              pickCheckOnly=self.pickCheckOnly) 
        
        
        handle_hw = side/2.0 #handle's half width
        handle_hh = side/2.0 #handle's half height
        
        handle_corner = [V(-handle_hw, handle_hh, 0.0), 
               V(-handle_hw, -handle_hh, 0.0), 
               V(handle_hw, -handle_hh, 0.0), 
               V(handle_hw, handle_hh, 0.0)] 
        
        if highlighted:
                drawLineLoop(orange, handle_corner, width=2)
        else:
            drawLineLoop(black, handle_corner)                
        glPopMatrix()

    def draw_in_abs_coords(self, glpane, color):
        ''' Draw the handle as a highlighted object'''
        self._draw(highlighted = True)
        
    def move(self, offset):
        '''Move the handle by <offset>, which is a 'V' object.'''
        self.center += offset
        
    def nearestNeighbors(self):
        ''' Nearest Handle objects (in the parent)to the current handle object
        @return: List of Handle Objects nearest to the current handle '''
        assert self in self.parent.handles
        
        w = None
        h = None
        
        if isinstance(self.parent, Plane):
            w = self.parent.getWidth()
            h = self.parent.getHeight()
        
        neighbors = []
        
        east_nbr = V(self.center[0] + w/2.0, self.center[1], self.center[2])
        west_nbr = V(self.center[0] - w/2.0 , self.center[1], self.center[2])
        north_nbr = V(self.center[0], self.center[1] + h/2.0, self.center[2])
        south_nbr = V(self.center[0], self.center[1] - h/2.0, self.center[2])
        
        nbrs = [east_nbr,west_nbr, north_nbr, south_nbr] 
        if w and h:
            for hdl in self.parent.handles:
                if hdl.center in nbrs:
                    neighbors.append(hdl)   
                    
        return neighbors
    
      
                 
        
        
    
             
    