# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ResizeHandle.py - provides Handles for resizing the parent object. The parent 
object in most cases is a reference geometry model object (e.g. Plane, Line etc) 

@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:
Ninad 2007-10-16: Originally created and modified in Plane.py, while working
                  on implemention of resizable  Planes (in May-June 2007). 
                  Moved this class  to its own module and renamed it to 
                  'ResizeHandle' (the old name was 'Handle')
"""

from OpenGL.GL import glPushName
from OpenGL.GL import glPopName
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef

from graphics.drawing.drawers import drawLineLoop
from graphics.drawing.drawers import drawPlane

import foundation.env as env
from utilities.prefs_constants import selectionColor_prefs_key
from utilities.constants import black, orange

from math import pi
from geometry.VQT import V

from utilities.debug import print_compact_traceback

from graphics.drawables.DragHandler import DragHandler_API
from graphics.drawables.Selobj import Selobj_API

ONE_RADIAN = 180.0 / pi
# One radian = 57.29577951 degrees
# This is for optimization since this computation occurs repeatedly
# in very tight drawning loops. --Mark 2007-08-14

class ResizeHandle(DragHandler_API, Selobj_API):
    """
    This class provides Handles for resizing the parent object. The parent 
    object in most cases is a geometry (e.g. Plane, Line etc) 
    @see: L{Plane._draw_handles} 
    @Note: This is  unrelated with the things in handles.py
          
    """
    def __init__(self, parent, glpane, handleCenter):
        """
        Constructor for class ResizeHandle
        @param parent: The parent object that can be resized using this handle.
                       The parent can be a L{ReferenceGeometry}
        @param handleCenter: The center of the handle. If None, use the handle's
                        I{center} property.
        @type  handleCenter: L{V} or None
        
        """
        self.parent = parent
        #this could be parent.glpane , but pass glpane object explicitely
        #for creating  a handle to avoid any errors
        self.glpane = glpane
        self.center = handleCenter
        # No texture in handles (drawn ResizeHandle object). 
        # Ideally the following value in the drawer.drawPlane method 
        # should be False by default.
        self.textureReady  = False
        self.pickCheckOnly = False        
        self.glname = glpane.alloc_my_glselect_name(self) #bruce 080917 revised
        self.type   = None      
    
    def draw(self, hCenter = None):
        """
        Public method to draw the resize handle. 
        @param hCenter: The center of the handle. If None, use the handle's 
                        I{center} property.
        @type  hCenter: L{V} or None
        @see: :{self._draw} which is called inside this method.
        """
        try:
            glPushName(self.glname)
            if hCenter:
                self._draw(hCenter)    
            else:
                self._draw()
        except:
            glPopName()
            print_compact_traceback(
                "ignoring exception when drawing handle %r: " % self)
        else:
            glPopName()
    
    def _draw(self, hCenter = None, highlighted = False):
        """
        Draw the resize handle. It does the actual drawing work. 
        
        @param hCenter: The center of the handle. If None, use the handle's 
                        I{center} property.
        @type  hCenter: L{V} or None
        
        @param highlighted: This argument determines if the handle is 
                            drawn in the highlighted color.
        @type  highlighted: bool
        @see: {self.draw} where this method is called. 
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
                        
        #Bruce suggested undoing the glpane.quat rotation and plane quat 
        #rotation  before drawing the handle geometry. -- ninad 20070525
        
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
       
        drawPlane(env.prefs[selectionColor_prefs_key], 
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
                           'Width-Handle', 'Height-Handle','Corner' or 
                           just '' (type not specified)
        @type  handleType: str
        """
        assert handleType in [ 'Width-Handle', 'Height-Handle', 'Corner', '']
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
        type = self.getType()
        if type:
            msg3 = " Type: "
        else:
            msg3 = ''
        msg4 = type
        
        return msg1 + msg2 + msg3 + msg4
        
    def highlight_color_for_modkeys(self, modkeys):
        return orange
    
    # Copied Bruce's code from class Highlightable with some mods. 
    # Need to see if selobj_still_ok() is needed. OK for now.
    # --Ninad 2007-05-31
    def selobj_still_ok(self, glpane):
        # bugfix: compare to correct class [bruce 070924]
        res = self.__class__ is ResizeHandle 
        if res:
            our_selobj = self
            glname     = self.glname
            owner      = glpane.assy.object_for_glselect_name(glname)
            if owner is not our_selobj:
                res = False
                # Do debug prints.
                print "%r no longer owns glname %r, instead %r does" \
                      % (self, glname, owner) #[perhaps never seen as of 061121]
            pass
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self 
        return res
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
