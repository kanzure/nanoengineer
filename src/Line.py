# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad,
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

"""

__author__ = "Ninad"


import env

from OpenGL.GL  import glPushMatrix
from OpenGL.GL  import glPopMatrix
from OpenGL.GLU import gluProject, gluUnProject
from Numeric    import dot
from VQT        import  V, Q, cross,A, planeXline, vlen, norm

from ReferenceGeometry import ReferenceGeometry
from debug   import print_compact_traceback
from drawer    import drawPolyLine
from constants import blue

class Line(ReferenceGeometry):
    
    sym = "Line" 
    is_movable = True 
    icon_names = ["modeltree/plane.png", "modeltree/plane-hide.png"]
    sponsor_keyword = 'Line' 
    copyable_attrs = ReferenceGeometry.copyable_attrs 
    mmp_record_name = "line"
    
    def __init__(self, win, plane = None, lst = None, READ_FROM_MMP = False):
        self.w = self.win = win                      
        ReferenceGeometry.__init__(self, win)  
        self.plane = plane
        self.linePoints = []
        self.color = blue
        if lst:            
            for a in lst:
                self.linePoints.append(a.posn())  
        
        self.win.assy.place_new_geometry(self)
            
    
    def _draw_geometry(self, glpane, color, highlighted=False):   
        glPushMatrix()
        if not highlighted:
            color = self.color
        drawPolyLine(color, self.linePoints)        
        glPopMatrix()
        
          
    
