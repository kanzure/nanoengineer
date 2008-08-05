# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 20070703 : Created 
Ninad 20070706 : Added support for resizing a poly-line. 
"""

import foundation.env as env

from OpenGL.GL  import glPushMatrix
from OpenGL.GL  import glPopMatrix
from OpenGL.GLU import gluProject, gluUnProject
from graphics.drawing.drawers import drawPolyLine

from Numeric    import dot
from math       import pi, cos
from geometry.VQT import V, Q, cross, A, planeXline, vlen, norm, angleBetween

from utilities.debug import print_compact_traceback
from utilities.constants import blue
from graphics.drawables.ResizeHandle import ResizeHandle
from model.ReferenceGeometry import ReferenceGeometry


class Line(ReferenceGeometry):
    """
    """
    sym = "Line" 
    is_movable = True 
    icon_names = ["modeltree/plane.png", "modeltree/plane-hide.png"]
    copyable_attrs = ReferenceGeometry.copyable_attrs 
    mmp_record_name = "line"
    
    def __init__(self, win, plane = None, lst = None,
                 pointList = None,
                 READ_FROM_MMP = False):
        self.w = self.win = win                      
        ReferenceGeometry.__init__(self, win)  
        self.plane = plane
        self.controlPoints = []
        self.handles = []
        self.quat = None
        self.center = None
        self.color = blue
        if lst:            
            for a in lst:
                self.controlPoints.append(a.posn())  
        elif pointList:
            for a in pointList:
                self.controlPoints.append(a)  
            
        
        self.win.assy.place_new_geometry(self)
            
    
    def _draw_geometry(self, glpane, color, highlighted=False):   
        glPushMatrix()
        if not highlighted:
            color = self.color
        drawPolyLine(color, self.controlPoints)
        if self.picked:
            self._draw_handles(self.controlPoints)
        glPopMatrix()
    
    def _draw_handles(self, controlPoints):
        handleCenters = list(controlPoints)
        if len(self.handles) > 0:
            assert len(self.handles) == len(controlPoints)
            i = 0
            for i in range(len(self.handles)):
                self.handles[i].draw(hCenter = handleCenters[i])
        else:   
            for hCenter in handleCenters: 
                handle = ResizeHandle(self, self.glpane, hCenter)                
                handle.draw() 
                handle.setType('')
                if handle not in self.handles:
                    self.handles.append(handle)
    
    def getHandlePoint(self, hdl, event):
        p1, p2 = self.glpane.mousepoints(event)
        rayPoint = p2
        rayVector = norm(p2-p1)
        ptOnHandle = hdl.center
        handleNorm = hdl.glpane.lineOfSight
        hdl_intersection = planeXline(ptOnHandle, 
                                      handleNorm, 
                                      rayPoint, 
                                      rayVector)
        
        handlePoint = hdl_intersection         
        return handlePoint
         
    def resizeGeometry(self, hdl, evt):
        
        movedHandle = hdl
        event = evt
        
        handle_NewPt = self.getHandlePoint(movedHandle, event)
        ##if movedHandle in self.handles[1:-1]:
        movedHandle.center = handle_NewPt
        self.updateControlPoints(movedHandle, handle_NewPt)
        
    def updateControlPoints(self, hdl, hdl_NewPt):
        """
        Update the control point list of the line.
        """
        #@@TODO No need to clear all the list. Need to make sure that only 
        #the changed point in the list is updated -- Ninad20070706
        movedHandle = hdl
        handle_NewPt = hdl_NewPt
        
        if len(self.handles) > 1:            
            self.controlPoints = []
            for h in self.handles:        
                self.controlPoints.append(h.center)
    
    
    def updateControlPoints_EXPERIMENTAL(self, hdl, hdl_NewPt):
        """
        Experimental stuff in this method. Not used anywhere. Ignore
        """
        movedHandle = hdl
        handle_NewPt = hdl_NewPt
        
        if len(self.handles) > 1:            
            self.controlPoints = []
            if movedHandle in self.handles[1:-1]:
                for h in self.handles:        
                    self.controlPoints.append(h.center)
            else:
                offsetVector = handle_NewPt - movedHandle.center
                movedHandle.center = handle_NewPt
                
                for h in self.handles[1:-1]:
                    vect = movedHandle.center - h.center
                    
                    theta = angleBetween( vect, offsetVector)
                    theta = theta*pi/180.0
             
                    offsetVecForHandle = offsetVector / cos(theta)
                    ##offsetVecForHandle = offsetVector* len(vect)/len(offsetVector)
                    h.center += offsetVecForHandle
                for h in self.handles:
                    self.controlPoints.append(h.center)
                    
                        
                if 0:
                    oldCenter = V(0.0, 0.0, 0.0)
                    for h in self.handles:
                        oldCenter += h.center                    
                    oldCenter /= len(self.handles)
                    movedHandle.center = handle_NewPt
                    
                    newCenter = V(0.0, 0.0, 0.0)
                    for h in self.handles:
                        newCenter += h.center
                    
                    newCenter /= len(self.handles)
                    
                    for h in self.handles:
                        if h in self.handles[1:-1]:
                            h.center += newCenter - oldCenter
                        self.controlPoints.append(h.center)
  
            
