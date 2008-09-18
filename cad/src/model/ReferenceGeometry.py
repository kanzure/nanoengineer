# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ReferenceGeometry.py - Jig subclass used as superclass for Plane, Line, etc

@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:
ninad 20070521 : Created

ninad 20070601: Implemented DragHandler and selobj interface for the 
class Handles. (and for ReferenceGeoemtry which is a superclass of Plane)

ninad 20070604: Changed the superclass from Node to Jig based on a discussion 
with Bruce. This allows us to use code for jig selection deletion in some select
modes. (note that it continues to use drag handler, selobj interfaces.). 
This might CHANGE in future.  After making jig a superclass of ReferenceGeometry
some methods in this file have become overdefined. This needs cleanup
"""

#@NOTE:This file is subjected to major changes.

#@TODO: Ninad20070604 :
#- Needs documentation and code cleanup / organization post Alpha-9.
#-After making jig a superclass of ReferenceGeometry
#some methods in this file have become overdefined. This needs cleanup.

import foundation.env as env
from utilities import debug_flags

from utilities.debug import print_compact_traceback

from utilities.prefs_constants import selectionColor_prefs_key
from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.constants import orange, yellow

from OpenGL.GL import glPushName
from OpenGL.GL import glPopName

from foundation.Utility import Node
from model.jigs import Jig

from graphics.drawables.DragHandler import DragHandler_API
from utilities.Log import greenmsg

class ReferenceGeometry(Jig, DragHandler_API):
    """
    Superclass for various reference geometries. 
    Example or reference geometries: Plane, Point, Line.
    """
    
    sym             =  "Geometry" # affects name-making code in __init__
    # if not redefined, this means it's just a comment in an mmp file
    mmp_record_name = "#" 
    featurename     =  "" 
    color           =  orange
    normcolor       =  color
    atoms           =  []
    points          =  None
    handles         =  None
    
    copyable_attrs = Node.copyable_attrs + ('normcolor', 'color')
        
    def __init__(self, win):  
        self.win = win
        #Node.__init__(self, win.assy, gensym("%s" % self.sym, win.assy))        
        Jig.__init__(self, win.assy, self.atoms) # note: that sets self.glname
        self.glpane = self.assy.o
        #@@Geometry object with a visible direction arrow 
        #(at present used in Plane only) This saves the last geometry object
        #for which the Direction arrow was drawn
        #(that decides the direction of a plane offset to the object)
        #The program needs to skip the arrow drawing (which is done inside the 
        # objects _draw_geometry method) when prop manager is closed or when the
        #Offset option is no more requested.  -- ninad 20070612           
        self.offsetParentGeometry = None
                    
    def needs_atoms_to_survive(self): 
        """
        Overrided method inherited from Jig. This is used to tell 
        if the jig can be copied even it doesn't have atoms.
        """
        return False
    
    def _mmp_record_last_part(self, mapping):
        """
        Return a fake string 'type-geometry' as the last entry 
        for the mmp record. This part of mmp record is NOT used so far 
        for ReferenceGeometry Objects.
        """
        #This is needed as ReferenceGeometry is a subclass of Jig 
        #(instead of Node) , Returning string 'geometry' overcomes 
        #the problem faced due to a kludge in method mmp_record 
        #(see file jigs.py)That kludge makes it not write the 
        #proper mmp record. if last part is an empty string (?)--ninad 20070604
        return "type-geometry"

                        
    def _draw(self, glpane, dispdef):
        self._draw_geometry(glpane, self.color)        
    
    def _draw_geometry(self, glpane, color, highlighted = False):
        """
        The main code that draws the geometry. 
        Subclasses should override this method.
        """
        pass
            
    def draw(self, glpane, dispdef):
        if self.hidden:
            return
        try:
            glPushName(self.glname)
            self._draw(glpane, dispdef)
        except:
            glPopName()
            print_compact_traceback(
                "ignoring exception when drawing Plane %r: " % self)
        else:
            glPopName()

    def draw_in_abs_coords(self, glpane, color):
        """
        Draws the reference geometry with highlighting.
        """       
        self._draw_geometry(glpane,
                            env.prefs[hoverHighlightingColor_prefs_key],
                            highlighted = True)
        return

    def pick(self): 
        """
        Select the reference geometry.
        """
        if not self.picked: 
            Node.pick(self)
            self.normcolor = self.color
            self.color = env.prefs[selectionColor_prefs_key] # russ 080603: pref.
        return

    def unpick(self):
        """
        Unselect the reference geometry.
        """
        if self.picked:
            Node.unpick(self) 
            # see also a copy method which has to use the same statement to 
            #compensate for this kluge
            self.color = self.normcolor 

    def rot(self, quat):
        pass
    
    ##===============copy methods ==================###
    #Reimplementing Jig.copy_full_in_mapping. Keeping an old comment by Bruce
    #-- commented niand 20070613
    def copy_full_in_mapping(self, mapping): 
        #bruce 070430 revised to honor mapping.assy
        clas = self.__class__
        new = clas(mapping.assy.w, [])        
        new._orig = self
        new._mapping = mapping
        return new
    
    ###============== selobj interface ===============###
     
    #Methods for selobj interface  . Note that draw_in_abs_coords method is 
    #already defined above. All of the following is NIY  -- Ninad 20070522
    
    def leftClick(self, point, event, mode): 
        """
        Method that handle Mouse Left click  event
        """
        mode.geometryLeftDown(self, event)
        mode.update_selobj(event)
        return self
                    
    def mouseover_statusbar_message(self):
        """
        Status bar message to display when an object is highlighted. 
        @return: name of the highlighted object
        @rtype:  str
        """
        return str(self.name)
        
    def highlight_color_for_modkeys(self, modkeys):
        """
        Highlight color for the highlighted object
        """
        return env.prefs[hoverHighlightingColor_prefs_key]
    
    # copying Bruce's code from class Highlightable with some mods. Need to see
    # if sleobj_still_ok method is needed. OK for now --Ninad 20070601
    def selobj_still_ok(self, glpane):
        res = self.__class__ is ReferenceGeometry
        if res:
            our_selobj = self
            glname = self.glname
            owner = glpane.assy.object_for_glselect_name(glname)
            if owner is not our_selobj:
                res = False
                # Do debug prints [perhaps never seen as of 061121]
                print "%r no longer owns glname %r, instead %r does" \
                      % (self, glname, owner)
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self
        return res
    
    ###=========== Drag Handler interface =============###
    def handles_updates(self): #k guessing this one might be needed
        return True
            
    def DraggedOn(self, event, mode):
        mode.geometryLeftDrag(self, event)
        mode.update_selobj(event)
        return
    
    def ReleasedOn(self, selobj, event, mode): 
        pass
    
