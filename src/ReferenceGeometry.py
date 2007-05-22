# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from Utility import Node
from constants import darkgreen, orange
from Utility import imagename_to_pixmap
import env

##from exprs.Highlightable import DragHandler

Gno = 0
def gensym(string):
    # warning, there are also functions like this in chem.py and jigs.py
    # but with its own global counter!
    """Return string appended with a unique number"""
    global Gno
    Gno += 1
    return string + str(Gno)


class ReferenceGeometry(Node):
    sym = "Geometry" # affects name-making code in __init__
    pickcolor = darkgreen 
    mmp_record_name = "#" # if not redefined, this means it's just a comment in an mmp file
    featurename = "" 
    #color = normcolor = (0.5, 0.5, 0.5)
    color = normcolor = orange

    atoms = None
    points = None
    
    #Handles for resizing the geometry (shown only when the geometry is selected)
    #Subclasses should define this as a List object containing 
    #the center point of each handle (each center point is a vector). 
    #See _draw_handles method in subclasses
    handles = None
    
    
    copyable_attrs = Node.copyable_attrs + ('pickcolor', 'normcolor', 'color')
    
    def __init__(self, win):  
        self.win = win
        Node.__init__(self, win.assy, gensym("%s-" % self.sym))        
        self.glname = env.alloc_my_glselect_name( self) 
        self.glpane = self.assy.o
                        
    def _draw(self, glpane, dispdef):
        self._draw_geometry(glpane, self.color)        
    
    def _draw_geometry(self,glpane, color, highlighted =False):
        ''' The main code that draws the geometry. 
        Subclasses should override this method.'''
        pass
        
    
    def draw(self, glpane):
        try:
            glPushName(self.glname)
            self._draw(glpane, dispdef)
        except:
            glPopName()
            print_compact_traceback("ignoring exception when drawing Plane %r: " % self)
        else:
            glPopName()
            
    def draw_in_abs_coords(self, glpane, color):
        '''Draws the reference geometry with highlighting.'''
        self._draw_geometry(glpane, color, highlighted = True)    
    
    def node_icon(self, display_prefs):
        '''A subclasse should override this if it needs to 
        choose its icons differently'''
        return imagename_to_pixmap( self.icon_names[self.hidden] )
    
    def pick(self): 
        """Select the reference geometry"""
        if not self.picked: 
            Node.pick(self)
            self.normcolor = self.color
            self.color = self.pickcolor
        return

    def unpick(self):
        """Unselect the reference geometry"""
        if self.picked:
            Node.unpick(self) 
            self.color = self.normcolor # see also a copy method which has to use the same statement to compensate for this kluge

    def rot(self, quat):
        pass
    
    """
    #Methods for selobj interface  . Note that dear_in_abs_coords method is 
    #already defined above. All of the following is NIY  -- Ninad 20070522
    
    def leftClick(self, point, event, mode):
        return self
            
    def mouseover_statusbar_message(self):
        pass
    
    def highlight_color_for_modkeys(self):
        return green
            
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
    
    """
    
            
      

    