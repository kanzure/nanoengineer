# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad,
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 20070621: Created.
ninad 20070601: Implemented DragHandler and selobj interface for the 
class Handles. (and for ReferenceGeoemtry which is a superclass of Plane)
ninad 20070603: Implemented Plane Property Manager
ninad 20070606: slightly cleaned up the code-- Plane class now inherits only
ReferenceGeometry and uses PlaneGenerator object for PropertyManager work.

@NOTE:This file is subjected to major changes. 
@TODO: 
-Work needs to be done on resizeGeometry code. 
Many other improvements planned- Ninad 070603
- Needs documentation and code cleanup /organization post Alpha9.--ninad20070604 




"""

from OpenGL.GL import *
from OpenGL.GLU import gluProject, gluUnProject
from math import pi, atan, cos, sin
from Numeric import add

from PyQt4.QtGui import QDialog

from VQT import V,Q, cross, dot, A, planeXline, vlen
from debug import print_compact_traceback
import env
from shape import fill
from drawer import drawLineLoop, drawPlane
from constants import black, gray, orange, yellow, darkgreen
from HistoryWidget import greenmsg, redmsg

from PlanePropertyManager import PlanePropMgr
from ReferenceGeometry import ReferenceGeometry 


#Required for class Handle --
from DragHandler import DragHandler_API

class Plane(ReferenceGeometry):
    
    sym = "Plane"    
    is_movable = True 
    mutable_attrs = ('center', 'quat')
    icon_names = ["modeltree/plane.png", "modeltree/plane-hide.png"]
    sponsor_keyword = 'Plane'    
    copyable_attrs = ReferenceGeometry.copyable_attrs + mutable_attrs
    cmdname = 'Plane'
    mmp_record_name = "plane"
        
    def __init__(self, win, lst = None, READ_FROM_MMP = False):
        ''' 
        @param: win: MainWindow object
        @param: lst: List of atoms or points'''
        
        self.w = self.win = win
                      
        ReferenceGeometry.__init__(self, win)         
        
        if self.win.assy.o.mode.modename in \
           ['DEPOSIT', 'MODIFY', 'FUSE', 'MOVIE']:
            self.modePropertyManager = self.win.assy.o.mode
        
        self.fill_color = gray        
        self.opacity = 0.3
        
        self.handles = []   
                
        #This is used to notify drawing code if it's just for picking purpose
        #copied from jig_planes.ESPImage 
        self.pickCheckOnly=False 
        
        from PlaneGenerator import PlaneGenerator
        self.propMgr = PlaneGenerator(self.win, self)
                   
        
        if not READ_FROM_MMP:
            self.width = 12
            self.height = 12                    
            self.normcolor = black
            self.__init_quat_center(lst)            
            self.propMgr.show_propMgr()
            self.propMgr.preview_btn_clicked()
    
    def __getattr__(self, name):
        if name == 'planeNorm':
            return self.quat.rot(V(0.0, 0.0, 1.0))
        else:
            raise AttributeError, 'Plane has no "%s"' % name 
    
                
    def setProps(self,props):
        ''' Set the Plane properties. It is Called while reading a MMP 
        file record.'''
        name, border_color, width, height, center, wxyz = props
        self.name = name
        self.color = self.normcolor = border_color
        self.width = width
        self.height = height
        self.center = center 
        self.quat = Q(wxyz[0], wxyz[1], wxyz[2], wxyz[3])
        
    
    def getProps(self):
        '''Return the current properties of the Plane'''
        #Used in preview method If an existing structure is changed, 
        #and user hits preview and then hits Cancel then it restores the 
        #old properties of the plane returned by this function. 
        props = (self.name, self.color, self.width, self.height,
             self.center, self.quat)
        return props
    
    def mmp_record_jigspecific_midpart(self):
        '''Return a string of format: width height (cx, cy, cz) (w, x, y, z)'''
        #This value is used in method mmp_record  of class Jig
        dataline = "%.2f %.2f (%f, %f, %f) (%f, %f, %f, %f) " % \
           (self.width, self.height, self.center[0], self.center[1], self.center[2], 
            self.quat.w, self.quat.x, self.quat.y, self.quat.z)
        return " " + dataline
    
    def _mmp_record_last_part(self, mapping):
        ''' Return a fake string 'type-geometry' as the last entry 
        for the mmp record. This part of mmp record is NOT used so far 
        for ReferenceGeometry Objects'''
        #This is needed as ReferenceGeometry is a subclass of Jig 
        #(instead of Node) , Returning string 'geometry' overcomes 
        #the problem faced due to a kludge in method mmp_record 
        #(see file jigs.py)That kludge makes it not write the 
        #proper mmp record. if last part is an empty string (?) --ninad 20070604
        
        return "type-geometry"
    
        
    def draw(self, glpane, dispdef):
        if self.hidden:
            return
        try:
            glPushName(self.glname)
            self._draw(glpane, dispdef)
        except:
            glPopName()
            print_compact_traceback("ignoring exception when drawing Plane %r: " % self)
        else:
            glPopName()
                   
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
        
        bottom_left = V(- hw,- hh, 0.0)                       
        bottom_right = V(+ hw,- hh, 0.0)        
        top_right = V(+ hw, + hh, 0.0)
        top_left = V(- hw, + hh, 0.0)
                
        corners_pos = [bottom_left, bottom_right, 
                       top_right, top_left]          
                                
        drawPlane(self.fill_color, 
                  self.width, 
                  self.height, 
                  textureReady,
                  self.opacity, 
                  SOLID=True, 
                  
                  pickCheckOnly=self.pickCheckOnly)
        
        if self.picked:
            drawLineLoop(self.color, corners_pos)  
            if highlighted:
                drawLineLoop(color, corners_pos, width=2)            
                pass
            self._draw_handles(corners_pos)               
        else:
            if highlighted:
                drawLineLoop(color, corners_pos, width=2)
            else:  
                #Following draws the border of the plane in orange color 
                #for it's front side (side that was in front 
                #when the plane was created and a gray border for the back side. 
                if dot(self.getaxis(), glpane.lineOfSight) < 0:
                    bordercolor = gray #backside
                else:
                    bordercolor = orange #frontside
                drawLineLoop(bordercolor, corners_pos)                  
        glPopMatrix()
        
        return
           
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
        #Following makes sure that handles move as the geometry moves. 
        #@@ do not call Plane.move method during the Plane resizing. 
        #call recomputeCenter method instead. -- ninad 20070522
        if len(self.handles) == 8:
            for hdl in self.handles:
                assert isinstance(hdl, Handle)
                hdl.move(offset)
            
        
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
       
        cornerHandleCenters = list(cornerPoints) 
        
        midBtm = (handleCenters[0] + handleCenters[1])/2      
        midRt = (handleCenters[1] + handleCenters[2])/2
        midTop = (handleCenters[2] + handleCenters[3])/2
        midLft = (handleCenters[3] + handleCenters[0])/2
        
       
        for midpt in [midBtm,midRt,midTop, midLft]:
            handleCenters.append(midpt)
        
        if len(self.handles)==8:   
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
        ''' Recompute the center of the Plane based on the handleOffset
        This is needed during resizing'''
        
        ##self.move(handleOffset/2.0) 
        self.center += handleOffset/2.0
    
    def resizeGeometry(self, movedHandle, vec_P, vec_v1): 
        #@TODO:need to revise this.
        #@BUG: vec_v1 computed in handleLeftDrag needs to be be Handle Center
        #projected on the parent Plane . 
        #At present I'm unable to compute that. handel.center returns , for example
        # (-X, 0, 0) for the mid-west handle even when the handle is created in left view. 
        #In the above case , the real point on the parent plane 
        #(with center at 0, 0,0) should be (0, 0, -8) since you are in left view. 
        #vec_v1 returns a vector between the mouse hitpoint on the handle 
        #and plane center. But since it doesn't have accurate coordinates 
        #as the handle center the resizing is not smooth and plane 
        #'moves' after resize(which shouldn't happen)  -- Ninad 20070601
    
        totalOffset = vec_P - vec_v1
                
        if 0: #For debug
            print "***vec_P = ", vec_P
            print "***length of vec_P = ", vlen(vec_P)
            print "*** vec_v1 = ", vec_v1
            print "***length of vec_v1 = ", vlen(vec_v1)
            print "*** totalOffset vector =", totalOffset
            print "*** length of totalOffset = ", vlen(totalOffset)
            print "*** Original Width = ", self.width
        
        if vlen(vec_P) > vlen(vec_v1):
            new_dimension = 2*vlen(vec_v1) + vlen(totalOffset)
        else:
            new_dimension = 2*vlen(vec_v1) - vlen(totalOffset)
                
        if movedHandle.getType() == 'Width-Handle' :  
            new_w = new_dimension                    
            self.setWidth(new_w)
        elif movedHandle.getType() == 'Height-Handle' :
            new_h = new_dimension
            self.setHeight(new_h)
        elif movedHandle.getType() == 'Corner':            
            wh = 0.5*self.getWidth()
            hh = 0.5*self.getHeight()
            theta = atan(hh/wh)
            new_w = (new_dimension)*cos(theta)
            new_h = (new_dimension)*sin(theta)
            self.setWidth(new_w)
            self.setHeight(new_h)            
        
        self.recomputeCenter(totalOffset)
        #update the width,height spinboxes(may be more in future)--Ninad20070601
        self.propMgr.update_spinboxes()
    
    def edit(self):
        ''' Overrided node.edit and shows the property manager'''
        self.propMgr.existingStructForEditing = True    
        ##self.propMgr.update_spinboxes()
        self.propMgr.old_props = self.getProps()
        self.propMgr.show_propMgr()       
                
    def changePlanePlacement(self, btn_id ):
        ''' Slot to Change the placement of the plane depending upon the 
        action checked in the Placement Groupbox of Plane PM'''
        cmd = self.propMgr.cmd        
        if btn_id == 0:
            msg = "Plane will be created parallel to the screen. \
            NOTE: In Alpha9, the default center of the plane is (0,0,0).\
            This value is set during plane creation or when 'Preview' button \
            is clicked."
            self.propMgr.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
            self._setup_quat_center()
            self.glpane.gl_update()
        elif btn_id == 1:
            msg = "Plane will pass through 3 or more selected atoms.\
            Select atoms and hit 'Preview' to see the new Plane placement"
            self.propMgr.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
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
            self._setup_quat_center(lst = atmList)
            self.glpane.gl_update()
            
    def _setup_quat_center(self, lst = None):
        if lst:    
            self.atomPos =[]
            for a in lst:
                self.atomPos += [a.posn()]    
            planeNorm = self._getPlaneOrientation(self.atomPos)
            if dot(planeNorm, self.glpane.lineOfSight) < 0:
                planeNorm = - planeNorm                
            self.center = add.reduce(self.atomPos)/len(self.atomPos)
        else:            
            planeNorm = self.glpane.lineOfSight
            self.center = [0.0,0.0,0.0]        
        self.quat = Q(V(0.0, 0.0, 1.0), planeNorm)
    
                      
class Handle(DragHandler_API):
    '''@@@EXPERIMENTAL -- ninad 20070517 
    - unrelated with things in handles.py
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
        self.type = None      
    
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
        ''' Draw the handle object '''        
        
        if hCenter:
            if self.center != hCenter:
                self.center = hCenter    
               
        #Use glpane's scale for drawing the handle. This makes sure that
        # the handle is non-zoomable. 
        side = self.glpane.scale*0.018                
        glPushMatrix()           
            
        
        #Translate to the center of the handle
        glTranslatef(self.center[0], 
                     self.center[1], 
                     self.center[2])   
        
        
        #Bruce suggested undoing the glpane.quat rotation and plane quat rotation 
        #before drawing the handle geometry. -- ninad 20070525
        parent_q = self.parent.quat        
        glpane_q = self.glpane.quat 
        glRotatef(-parent_q.angle*180.0/pi, parent_q.x, parent_q.y, parent_q.z)          
        glRotatef(-glpane_q.angle*180.0/pi, glpane_q.x, glpane_q.y, glpane_q.z)        
       
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
            drawLineLoop(orange, handle_corner, width=6)
        else:
            drawLineLoop(black, handle_corner, width=2)                
        glPopMatrix()
        
    def draw_in_abs_coords(self, glpane, color):
        ''' Draw the handle as a highlighted object'''          
        q = self.parent.quat  
        glPushMatrix()
        glTranslatef( self.parent.center[0],
                      self.parent.center[1], 
                      self.parent.center[2])
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)            
        self._draw(highlighted = True)
        glPopMatrix()
        
    def move(self, offset):
        '''Move the handle by <offset>, which is a 'V' object.'''
        self.center += offset
    
    def setType(self, handleType):
        ''' @param: handleType: returns the '''
        assert handleType in [ 'Width-Handle' , 'Height-Handle' , 'Corner']
        self.type = handleType
       
        
    def getType(self):
        '''@return: string self.type that tells whether its a X or Y 
        or a corner handle '''
        assert self.type is not None
        return self.type
        
    ###============== selobj interface ===============###
     
    #Methods for selobj interface  . Note that draw_in_abs_coords method is 
    #already defined above. All of the following is NIY  -- Ninad 20070522
    
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
    # copying Bruce's code from class Highligtable with some mods.Need to see        
    # if sleobj_still_ok method is needed. OK for now --Ninad 20070531
    def selobj_still_ok(self):
        res = self.__class__ is ReferenceGeometry 
        if res:
            our_selobj = self
            glname = self.glname
            owner = env.obj_with_glselect_name.get(glname, None)
            if owner is not our_selobj:
                res = False
                # owner might be None, in theory, but is probably a replacement of self at same ipath
                # do debug prints
                print "%r no longer owns glname %r, instead %r does" % (self, glname, owner) # [perhaps never seen as of 061121]
                our_ipath = self.ipath
                owner_ipath = getattr(owner, 'ipath', '<missing>')
                if our_ipath != owner_ipath:
                    # [perhaps never seen as of 061121]
                    print "WARNING: ipath for that glname also changed, from %r to %r" % (our_ipath, owner_ipath)
                pass
            pass
            # MORE IS PROBABLY NEEDED HERE: that check above is about whether this selobj got replaced locally;
            # the comments in the calling code are about whether it's no longer being drawn in the current frame;
            # I think both issues are valid and need addressing in this code or it'll probably cause bugs. [061120 comment] ###BUG
        import env
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self ###@@@
        return res # I forgot this line, and it took me a couple hours to debug that problem! Ugh.
            # Caller now prints a warning if it's None. 
    
    ###=========== Drag Handler interface =============###
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
    
                
