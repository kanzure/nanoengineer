# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 20070703 : Created 
Ninad 20070706 : Added support for resizing a poly-line. 
"""

import env

from OpenGL.GL import glPushName
from OpenGL.GL import glPopName
from OpenGL.GL  import glPushMatrix
from OpenGL.GL  import glPopMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef

from OpenGL.GLU import gluProject, gluUnProject
from drawer     import drawPolyLine, drawline, drawLineLoop, drawPoint
from drawer     import drawLadder, drawRibbons
from Numeric    import dot
from math       import pi, cos
from VQT        import  V, Q, cross, A, planeXline, vlen, norm, angleBetween

from debug     import print_compact_traceback
from constants import blue, red, orange, darkgreen, black, darkred
from ResizeHandle     import ResizeHandle
from DragHandler import DragHandler_API

from LinePropertyManager import LinePropertyManager

ONE_RADIAN = 180.0 / pi

class Line(DragHandler_API):
    """
    """
    sym = "Line" 
    is_movable = True 
    icon_names = ["modeltree/plane.png", "modeltree/plane-hide.png"]
    sponsor_keyword = 'Line'
    name = "Line"
    def __init__(self, glpane, editCommand = None, lineEndPoints = []):
        """
        """
        self.glpane = glpane
        self.editCommand = editCommand
        self.endPoint1 = lineEndPoints[0]
        self.endPoint2 = lineEndPoints[1]
        
        
        for lineVertex in [self.endPoint1, self.endPoint2]:
            if hasattr(lineVertex, 'lineSegments'):
                lineVertex.lineSegments.append(self)

        #Line vector -- might be needed when another line is moved. 
        self.vector = self.getVector()
        self.length = vlen(self.endPoint1.center - self.endPoint2.center)
        self.color = blue
        self.glname = env.alloc_my_glselect_name(self)
        self.isPicked = False
        side = self.glpane.scale * 0.02
        self.endHandleHalfWidth = side/2.0 #handle's half width
        self.endHandleHalfHeight = side/2.0 #handle's half height
        self.propMgr = LinePropertyManager(self.glpane.assy.w, None)
    
    def getVector(self):
        """
        """
        #Line vector -- might be needed when another line is moved. 
        self.vector = self.endPoint1.center - self.endPoint2.center
        return self.vector
    
    def setLength(self, newLength):
        """
        """
        offset = (newLength - self.length)
        offset = norm(self.vector)* offset
        self.endPoint2.move(offset)
        self.length = newLength
        
                
    def draw(self):
        """
        """
        try:
            glPushName(self.glname)
            glPushMatrix()
            self._draw()    
            glPopMatrix()
        except:
            glPopName()
            print_compact_traceback(
                "ignoring exception when drawing handle %r: " % self)
        else:
            glPopName()

    def _draw(self, highlighted = False):
        if highlighted:
            ##drawline(red, self.endPoint1.center, self.endPoint2.center, width = 2)
            if 1:
                #drawLadder(self.endPoint1.center,
                           #self.endPoint2.center, 
                           #3.18,
                           #self.glpane.scale, 
                           #self.glpane.lineOfSight,
                           #beam1Color = red,
                           #beam2Color = blue,
                           #stepColor = black    
                        #)  
                drawRibbons(self.endPoint1.center,
                       self.endPoint2.center, 
                       3.18,
                       self.glpane.scale,
                       self.glpane.lineOfSight,
                       ribbonThickness = 4.0,
                       ribbon1Color = darkred,
                       ribbon2Color = blue,
                       stepColor = black    
                    )     
        else:
            if self.isPicked:
                color = darkgreen
                self._drawEndsAsHandles()
            else:
                color = blue
                
            stepSize  = 3.18
            #drawLadder(self.endPoint1.center,
                       #self.endPoint2.center, 
                       #stepSize,
                       #self.glpane.scale, 
                       #self.glpane.lineOfSight,
                       #beam1Color = red,
                       #beam2Color = blue,
                       #stepColor = black    
                    #)  
            drawRibbons(self.endPoint1.center,
                       self.endPoint2.center, 
                       3.18,
                       self.glpane.scale,
                       self.glpane.lineOfSight,
                       ribbonThickness = 4.0,
                       ribbon1Color = darkred,
                       ribbon2Color = blue,
                       stepColor = black    
                    )     
    
            ##drawline(color, self.endPoint1.center, self.endPoint2.center, 
                     ##width = 2)
                
    
    def _drawEndsAsHandles(self):
        """
        """
        if not self.isPicked:
            return
        
        side = self.glpane.scale * 0.03
        self.endHandleHalfWidth = side/2.0 #handle's half width
        self.endHandleHalfHeight = side/2.0 #handle's half height
        
        handle_hw = self.endHandleHalfWidth
        handle_hh = self.endHandleHalfHeight
        
        for point in [self.endPoint1.center, self.endPoint2.center]:
            if 1:
                drawPoint(darkgreen, point, pointSize = 10, isRound = False)
                                
                if 1:
                    
                    glPushMatrix()
                    glTranslatef(point[0], point[1], point[2])
                    
                    glpane_q = self.glpane.quat
                    glRotatef(-glpane_q.angle * ONE_RADIAN, 
                               glpane_q.x, 
                               glpane_q.y, 
                               glpane_q.z)
                            
                    handle_corner = [V(-handle_hw,  handle_hh, 0.0), 
                                     V(-handle_hw, -handle_hh, 0.0), 
                                     V( handle_hw, -handle_hh, 0.0), 
                                     V( handle_hw,  handle_hh, 0.0)]   
                        
                    drawLineLoop(blue, handle_corner, width = 2)
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
        glPushMatrix()
        self._draw(highlighted = True)
        glPopMatrix()
    
    def highlight_color_for_modkeys(self, modkeys):
        return orange

    def selobj_still_ok(self, glpane):
        # bugfix: compare to correct class [bruce 070924]
        res = self.__class__ is Line 
        if res:
            our_selobj = self
            glname     = self.glname
            owner      = env.obj_with_glselect_name.get(glname, None)
            if owner is not our_selobj:
                res = False
                # Do debug prints.
                print "%r no longer owns glname %r, instead %r does" \
                      % (self, glname, owner) #[perhaps never seen as of 061121]
            pass
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self 
        return res

        
    def leftClick(self, point, event, mode):
        
        if mode.o.selobj is self:
            self.pick()
        else:
            self.unpick()
        mode.update_selobj(event)
        return self     
    
    def DraggedOn(self, event, mode): 
        ##mode.update_selobj(event)
        return

    def mouseover_statusbar_message(self):
        msg = "line"        
        return msg
    
    
    def pick(self):
        """
        """
        self.glpane.assy.unpickall_in_GLPane()     
        self.glpane.assy.selectedEntities.append(self)
        self.isPicked = True
        ##self.glpane.gl_update()
        self.editCommand.propMgr.show()
    
    def unpick(self):
        """
        """
        self.isPicked = False
        self.color = blue
        if self in self.glpane.assy.selectedEntities[:]:
            self.glpane.assy.selectedEntities.remove(self)
        
        self.editCommand.propMgr.ok_btn_clicked()
        ##self.glpane.gl_update()
    
    def updateCosmeticProps(self):
        pass    
    

