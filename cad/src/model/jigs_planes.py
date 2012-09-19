# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
jigs_planes.py -- Classes for Plane jigs, including RectGadget,
GridPlane, and (in its own module) ESPImage.

@author: Huaicai (I think), Ninad (I think), maybe others
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History: 

050927. Split off Plane jigs from jigs.py into this file. Mark

bruce 071215 split class ESPImage into its own file.

TODO:

Split more. Perhaps merge GridPlane with Plane (reference plane).
"""

import math
from numpy.oldnumeric import size, add

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef
from OpenGL.GL import glPopMatrix

from graphics.drawing.drawers import drawLineLoop

from graphics.drawing.draw_grid_lines import drawGPGrid
from graphics.drawing.draw_grid_lines import drawSiCGrid

from geometry.VQT import V, Q, A, cross
from graphics.rendering.povray.povheader import povpoint

from model.jigs import Jig

from utilities.constants import black
from utilities.constants import gray

from utilities.prefs_constants import SQUARE_GRID
from utilities.prefs_constants import SOLID_LINE

from geometry.BoundingBox import BBox

from commands.GridPlaneProperties.GridPlaneProp import GridPlaneProp

# == RectGadget

class RectGadget(Jig):
    """
    Abstract superclass for GridPlane and ESPImage.
    """
    is_movable = True #mark 060120
    mutable_attrs = ('center', 'quat')
    copyable_attrs = Jig.copyable_attrs + ('width', 'height') + mutable_attrs

    def __init__(self, assy, list, READ_FROM_MMP):
        Jig.__init__(self, assy, list)
        
        self.width = 20
        self.height = 20
        
        self.assy = assy
        self.cancelled = True # We will assume the user will cancel

        self.atomPos = []
        if not READ_FROM_MMP:
            self.__init_quat_center(list)        

    def _um_initargs(self):
        #bruce 051013 [as of 060209 this is probably well-defined and correct 
        # (for most Jig subclasses), but not presently used]
        """
        Return args and kws suitable for __init__.
        [Overrides Jig._um_initargs; see its docstring.]
        """
        return (self.assy, self.atoms, True), {}

    def setAtoms(self, atomlist):
        """
        Override the version from Jig. Removed adding jig to atoms
        """
        if self.atoms:
            print "fyi: bug? setAtoms overwrites existing atoms on %r" % self
        self.atoms = list(atomlist)
        
    def __init_quat_center(self, list):
        
        for a in list:#[:3]:
            self.atomPos += [a.posn()]
    
        planeNorm = self._getPlaneOrientation(self.atomPos)
        self.quat = Q(V(0.0, 0.0, 1.0), planeNorm)
        self.center = add.reduce(self.atomPos)/len(self.atomPos)
    
    def __computeBBox(self):
        """
        Compute current bounding box.
        """
        hw = self.width/2.0; hh = self.height/2.0
        corners_pos = [V(-hw, hh, 0.0), V(-hw, -hh, 0.0), V(hw, -hh, 0.0), V(hw, hh, 0.0)]
        abs_pos = []
        for pos in corners_pos:
            abs_pos += [self.quat.rot(pos) + self.center]
        
        return BBox(abs_pos)
    
    def __getattr__(self, name): # in class RectGadget
        if name == 'bbox':
            return self.__computeBBox()
        elif name == 'planeNorm':
            return self.quat.rot(V(0.0, 0.0, 1.0))
        elif name == 'right':
            return self.quat.rot(V(1.0, 0.0, 0.0))
        elif name == 'up':
            return self.quat.rot(V(0.0, 1.0, 0.0))
        else:
            raise AttributeError, 'RectGadget has no "%s"' % name
                #bruce 060209 revised text
        
    def getaxis(self):
        # todo: merge somehow with getaxis methods on other Nodes
        return self.planeNorm # axis is normal to plane of RectGadget.  Mark 060120
        
    def move(self, offset):
        """
        Move the plane by <offset>, which is a 'V' object.
        """
        ###k NEEDS REVIEW: does this conform to the new Node API method 'move',
        # or should it do more invalidations / change notifications / updates?
        # [bruce 070501 question]
        self.center += offset
    
    def rot(self, q):
        self.quat += q
        
    def needs_atoms_to_survive(self): # [Huaicai 9/30/05]
        """
        Overrided method inherited from Jig. This is used to tell if the jig
        can be copied even if it doesn't have atoms.
        """
        return False
        
    def _getPlaneOrientation(self, atomPos):
        assert len(atomPos) >= 3
        v1 = atomPos[-2] - atomPos[-1]
        v2 = atomPos[-3] - atomPos[-1]
        
        return cross(v1, v2)
    
    def _mmp_record_last_part(self, mapping):
        return ""
    
##    def is_disabled(self):
##        """
##        """
##        return False

    ###[Huaicai 9/29/05: The following two methods are temporarily copied here, this is try to fix jig copy related bugs
    ### not fully analyzed how the copy works yet. It fixed some problems, but not sure if it's completely right.
    def copy_full_in_mapping(self, mapping): #bruce 070430 revised to honor mapping.assy
        clas = self.__class__
        new = clas(mapping.assy, [], True) # don't pass any atoms yet (maybe not all of them are yet copied)
            # [Note: as of about 050526, passing atomlist of [] is permitted for motors, but they assert it's [].
            #  Before that, they didn't even accept the arg.]
        # Now, how to copy all the desired state? We could wait til fixup stage, then use mmp write/read methods!
        # But I'd rather do this cleanly and have the mmp methods use these, instead...
        # by declaring copyable attrs, or so.
        new._orig = self
        new._mapping = mapping
        new.name = "[being copied]" # should never be seen
        mapping.do_at_end( new._copy_fixup_at_end)
        #k any need to call mapping.record_copy??
        # [bruce comment 050704: if we could easily tell here that none of our atoms would get copied,
        #  and if self.needs_atoms_to_survive() is true, then we should return None (to fix bug 743) here;
        #  but since we can't easily tell that, we instead kill the copy
        #  in _copy_fixup_at_end if it has no atoms when that func is done.]
        return new
    
    def _copy_fixup_at_end(self): # warning [bruce 050704]: some of this code is copied in jig_Gamess.py's Gamess.cm_duplicate method.
        """
        [Private method]
        This runs at the end of a copy operation to copy attributes from the old jig
        (which could have been done at the start but might as well be done now for most of them)
        and copy atom refs (which has to be done now in case some atoms were not copied when the jig itself was).
        Self is the copy, self._orig is the original.
        """
        orig = self._orig
        del self._orig
        mapping = self._mapping
        del self._mapping
        copy = self
        orig.copy_copyable_attrs_to(copy) # replaces .name set by __init__
        self.own_mutable_copyable_attrs() # eliminate unwanted sharing of mutable copyable_attrs
        if orig.picked:
            # clean up weird color attribute situation (since copy is not picked)
            # by modifying color attrs as if we unpicked the copy
            self.color = self.normcolor
        #nuats = []
        #for atom in orig.atoms:
            #nuat = mapping.mapper(atom)
            #if nuat is not None:
                #nuats.append(nuat)
        #if len(nuats) < len(orig.atoms) and not self.name.endswith('-frag'): # similar code is in chunk, both need improving
            #self.name += '-frag'
        #if nuats or not self.needs_atoms_to_survive():
            #self.setAtoms(nuats)
        #else:
            ##bruce 050704 to fix bug 743
            #self.kill()
        #e jig classes with atom-specific info would have to do more now... we could call a 2nd method here...
        # or use list of classnames to search for more and more specific methods to call...
        # or just let subclasses extend this method in the usual way (maybe not doing those dels above).
        return
    
    pass # end of class RectGadget        

# == GridPlane
        
class GridPlane(RectGadget):
    """
    """
    #bruce 060212 include superclass mutables (might fix some bugs); see analogous ESPImage comments for more info
    own_mutable_attrs = ('grid_color', )
    mutable_attrs = own_mutable_attrs + RectGadget.mutable_attrs
    copyable_attrs = RectGadget.copyable_attrs + ('line_type', 'grid_type', 'x_spacing', 'y_spacing') + own_mutable_attrs
    
    sym = "GridPlane" #bruce 070604 removed space (per Mark decision)
    icon_names = ["modeltree/Grid_Plane.png", "modeltree/Grid_Plane-hide.png"] # Added gridplane icons.  Mark 050915.
    mmp_record_name = "gridplane"
    featurename = "Grid Plane" #bruce 051203
    
    def __init__(self, assy, list, READ_FROM_MMP = False):
        RectGadget.__init__(self, assy, list, READ_FROM_MMP)
        
        self.color = black # Border color
        self.normcolor = black
        self.grid_color = gray
        self.grid_type = SQUARE_GRID # Grid patterns: "SQUARE_GRID" or "SiC_GRID"
        # Grid line types: "NO_LINE", "SOLID_LINE", "DASHED_LINE" or "DOTTED_LINE"
        self.line_type = SOLID_LINE 
        # Changed the spacing to 2 to 1. Mark 050923.
        self.x_spacing = 5.0 # 5 Angstroms
        self.y_spacing = 5.0 # 5 Angstroms

    def setProps(self, name, border_color, width, height, center, wxyz, grid_type, \
                           line_type, x_space, y_space, grid_color):
        
        self.name = name; self.color = self.normcolor = border_color;
        self.width = width; self.height = height; 
        self.center = center; self.quat = Q(wxyz[0], wxyz[1], wxyz[2], wxyz[3])
        self.grid_type = grid_type; self.line_type = line_type; self.x_spacing = x_space;
        self.y_spacing = y_space;  self.grid_color = grid_color
        
    def _getinfo(self):
        return  "[Object: Grid Plane] [Name: " + str(self.name) + "] "

    def getstatistics(self, stats):
        stats.num_gridplane += 1  

    def set_cntl(self):
        self.cntl = GridPlaneProp(self, self.assy.o)
        
    def make_selobj_cmenu_items(self, menu_spec):
        """
        Add GridPlane specific context menu items to the <menu_spec> list when
        self is the selobj (i.e. the selected object under the cursor when the 
        context menu is displayed).
        
        @param menu_spec: A list of context menu items, where each member is a
                          tuple (menu item string, method).
        @type  menu_spec: list
        
        @note: This only works in "Build Atoms" (depositAtoms) mode.
        """
        item = ('Hide', self.Hide)
        menu_spec.append(item)
        menu_spec.append(None) # Separator
        item = ('Edit Properties...', self.edit)
        menu_spec.append(item)
        
    def _draw_jig(self, glpane, color, highlighted = False):
        """
        Draw a Grid Plane jig as a set of grid lines.
        """
        glPushMatrix()

        glTranslatef( self.center[0], self.center[1], self.center[2])
        q = self.quat
        glRotatef( q.angle*180.0/math.pi, q.x, q.y, q.z)

        hw = self.width/2.0; hh = self.height/2.0
        corners_pos = [V(-hw, hh, 0.0), V(-hw, -hh, 0.0), V(hw, -hh, 0.0), V(hw, hh, 0.0)]
        
        if highlighted:
            grid_color = color
        else:
            grid_color = self.grid_color
        
        if self.picked:
            drawLineLoop(self.color, corners_pos)
        else:
            drawLineLoop(color, corners_pos)
            
        if self.grid_type == SQUARE_GRID:
            drawGPGrid(glpane, grid_color, self.line_type, self.width, self.height, self.x_spacing, self.y_spacing,
                       q.unrot(self.assy.o.up), q.unrot(self.assy.o.right))
        else:
            drawSiCGrid(grid_color, self.line_type, self.width, self.height,
                        q.unrot(self.assy.o.up), q.unrot(self.assy.o.right))
        
        glPopMatrix()
    
    
    def mmp_record_jigspecific_midpart(self):
        """
        format: width height (cx, cy, cz) (w, x, y, z) grid_type line_type x_space y_space (gr, gg, gb)
        """
        color = map(int, A(self.grid_color)*255)
        
        dataline = "%.2f %.2f (%f, %f, %f) (%f, %f, %f, %f) %d %d %.2f %.2f (%d, %d, %d)" % \
           (self.width, self.height, self.center[0], self.center[1], self.center[2], 
            self.quat.w, self.quat.x, self.quat.y, self.quat.z, self.grid_type, self.line_type, 
            self.x_spacing, self.y_spacing, color[0], color[1], color[2])
        return " " + dataline
    
    
    def writepov(self, file, dispdef):
        if self.hidden:
            return
        if self.is_disabled():
            return #bruce 050421
        
        hw = self.width/2.0; hh = self.height/2.0
        corners_pos = [V(-hw, hh, 0.0), V(-hw, -hh, 0.0), V(hw, -hh, 0.0), V(hw, hh, 0.0)]
        povPlaneCorners = []
        for v in corners_pos:
            povPlaneCorners += [self.quat.rot(v) + self.center]
        strPts = ' %s, %s, %s, %s ' % tuple(map(povpoint, povPlaneCorners))
        color = '%s>' % (povStrVec(self.color),)
        file.write('grid_plane(' + strPts + color + ') \n')
        
    pass # end of class GridPlane   
    
# ==

def povStrVec(va): # review: refile in povheader or so? [bruce 071215 comment]
    # used in other modules too
    rstr = '<'
    for ii in range(size(va)):
        rstr += str(va[ii]) + ', '
    
    return rstr

#end
