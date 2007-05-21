# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from Utility import Node
from constants import darkgreen, orange
from Utility import imagename_to_pixmap
import env


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
    
    
        
    

    