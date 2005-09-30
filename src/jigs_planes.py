# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
jigs_planes.py -- Classes for Plane jigs, including RectGadget, GridPlane and ESPWindow.

$Id$

History: 

050927. Split off Plane jigs from jigs.py into this file. Mark

"""

from VQT import *
from shape import *
from chem import *
from Utility import *
from HistoryWidget import redmsg, greenmsg
from debug import print_compact_stack, print_compact_traceback
import env #bruce 050901
from jigs import Jig

# == RectGadget

class RectGadget(Jig):
    mutable_attrs = ('center', 'quat')
    copyable_attrs = Jig.copyable_attrs + ('width', 'height') + mutable_attrs

    def __init__(self, assy, list, READ_FROM_MMP):
        Jig.__init__(self, assy, list)
        
        self.width = 16
        self.height = 16
        
        self.assy = assy
        self.cancelled = True # We will assume the user will cancel

        self.atomPos = []
        if not READ_FROM_MMP:
            self.__init_quat_center(list)        


    def setAtoms(self, atomlist):
        """Override the version from Jig. Removed adding jig to atoms"""
        if self.atoms:
            print "fyi: bug? setAtoms overwrites existing atoms on %r" % self
            #e remove them? would need to prevent recursive kill.
        self.atoms = list(atomlist) # bruce 050316: copy the list
        
        
    def __init_quat_center(self, list):
        
        for a in list:#[:3]:
            self.atomPos += [a.posn()]
    
        planeNorm = self._getPlaneOrientation(self.atomPos)
        self.quat = Q(V(0.0, 0.0, 1.0), planeNorm)
        self.center = add.reduce(self.atomPos)/len(self.atomPos)

    
    def __computeBBox(self):
        '''Compute current bounding box. '''
        from shape import BBox
        
        hw = self.width/2.0; hh = self.height/2.0
        corners_pos = [V(-hw, hh, 0.0), V(-hw, -hh, 0.0), V(hw, -hh, 0.0), V(hw, hh, 0.0)]
        abs_pos = []
        for pos in corners_pos:
            abs_pos += [self.quat.rot(pos) + self.center]
        
        return BBox(abs_pos)

    
    def __getattr__(self, name):
        if name == 'bbox':
            return self.__computeBBox()
        elif name == 'planeNorm':
            return self.quat.rot(V(0.0, 0.0, 1.0))
        elif name == 'right':
            return self.quat.rot(V(1.0, 0.0, 0.0))
        elif name == 'up':
            return self.quat.rot(V(0.0, 1.0, 0.0))
        else:
            raise AttributeError, 'Grid Plane has no "%s"' % name

    def getaxis(self):
        return self.planeNorm # Axis is perpendicular to plane of jig.  Mark 050930
        
    def move(self, offset):
        '''Move the plane by <offset>, which is a 'V' object. '''
        self.center += offset

        
    def rot(self, q):
        self.quat += q

        
    def needs_atoms_to_survive(self): # [Huaicai 9/30/05]
        '''Overrided method inherited from Jig. This is used to tell if the jig can be copied even
           it doesn't have atoms.'''
        return False
    
        
    def _getPlaneOrientation(self, atomPos):
        assert len(atomPos) >= 3
        v1 = atomPos[-2] - atomPos[-1]
        v2 = atomPos[-3] - atomPos[-1]
        
        return cross(v1, v2)
    

    def _draw(self, win, dispdef):
        pass
    
    
    def _mmp_record_last_part(self, mapping):
        return ""

    ###[Huaicai 9/29/05: The following two methods are temporarally copied here, this is try to fix jig copy related bugs
    ### not fully analynized how the copy works yet. It fixed some problems, but not sure if it's completely right.
    def copy_full_in_mapping(self, mapping):
        clas = self.__class__
        new = clas(self.assy, [], True) # don't pass any atoms yet (maybe not all of them are yet copied)
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
        """[Private method]
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
    ''' '''
    mutable_attrs = ('grid_color', )
    copyable_attrs = RectGadget.copyable_attrs + ('line_type', 'grid_type', 'x_spacing', 'y_spacing') + mutable_attrs
    
    sym = "Grid Plane"
    icon_names = ["gridplane.png", "gridplane-hide.png"] # Added gridplane icons.  Mark 050915.
    mmp_record_name = "gridplane"
    
    def __init__(self, assy, list, READ_FROM_MMP=False):
        RectGadget.__init__(self, assy, list, READ_FROM_MMP)
        
        self.color = black # Border color
        self.normcolor = black
        self.grid_color = gray
        self.grid_type = SQUARE_GRID # Grid patterns: "SQUARE_GRID" or "SiC_GRID"
        # Grid line types: "NO_LINE", "SOLID_LINE", "DASHED_LINE" or "DOTTED_LINE"
        self.line_type = SOLID_LINE 
        # Changed the spacing to 2 to 1. Mark 050923.
        self.x_spacing = 1.0 # 1 Angstrom
        self.y_spacing = 1.0 # 1 Angstrom

    def setProps(self, name, border_color, width, height, center, wxyz, grid_type, \
                           line_type, x_space, y_space, grid_color):
        
        self.name = name; self.color = self.normcolor = border_color;
        self.width = width; self.height = height; 
        self.center = center; self.quat = Q(wxyz[0], wxyz[1], wxyz[2], wxyz[3])
        self.grid_type = grid_type; self.line_type = line_type; self.x_spacing = x_space;
        self.y_spacing = y_space;  self.grid_color = grid_color
        
        
    def set_cntl(self):
        from GridPlaneProp import GridPlaneProp
        self.cntl = GridPlaneProp(self, self.assy.o)
        

    def _draw(self, win, dispdef):
        glPushMatrix()

        glTranslatef( self.center[0], self.center[1], self.center[2])
        q = self.quat
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z) 
        
        hw = self.width/2.0; hh = self.height/2.0
        corners_pos = [V(-hw, hh, 0.0), V(-hw, -hh, 0.0), V(hw, -hh, 0.0), V(hw, hh, 0.0)]
        drawLineLoop(self.color, corners_pos)
        if self.grid_type == SQUARE_GRID:
            drawGPGrid(self.grid_color, self.line_type, self.width, self.height, self.x_spacing, self.y_spacing)
        else:
            drawSiCGrid(self.grid_color, self.line_type, self.width, self.height)
        
        glPopMatrix()
    
    
    def mmp_record_jigspecific_midpart(self):
        '''format: width height (cx, cy, cz) (w, x, y, z) grid_type line_type x_space y_space (gr, gg, gb)  '''
        color = map(int,A(self.grid_color)*255)
        
        dataline = "%.2f %.2f (%f, %f, %f) (%f, %f, %f, %f) %d %d %.2f %.2f (%d, %d, %d)" % \
           (self.width, self.height, self.center[0], self.center[1], self.center[2], 
            self.quat.w, self.quat.x, self.quat.y, self.quat.z, self.grid_type, self.line_type, 
            self.x_spacing, self.y_spacing, color[0], color[1], color[2])
        return " " + dataline
    
    pass # end of class GridPlane   
    
    
# == ESPWindow

class ESPWindow(RectGadget):
    ''' '''
    mutable_attrs = ('fill_color', )
    copyable_attrs = RectGadget.copyable_attrs + ('resolution', 'opacity', 'show_esp_bbox', 'window_offset', 'edge_offset') + mutable_attrs
    
    sym = "ESP Window"
    icon_names = ["espwindow.png", "espwindow-hide.png"] # Added espwindow icons.  Mark 050919.
    mmp_record_name = "espwindow"
    
    def __init__(self, assy, list, READ_FROM_MMP=False):
        RectGadget.__init__(self, assy, list, READ_FROM_MMP)
        self.assy = assy
        self.color = black # Border color
        self.normcolor = black
        self.fill_color = 85/255.0, 170/255.0, 255/255.0 # The fill color, a nice blue
        
        # This specifies the resolution of the ESP Window. 
        # The total number of ESP data points in the window will number resolution^2. 
        self.resolution = 128
        # Show/Hide ESP Window Volume (Bbox).  All atoms inside this volume are used by 
        # the MPQC ESP Plane plug-in to calculate the ESP points.
        self.show_esp_bbox = True
        # the perpendicular (front and back) window offset used to create the depth of the bbox
        self.window_offset = 1.0
        # the edge offset used to create the edge boundary of the bbox
        self.edge_offset = 1.0 
        # opacity, a range between 0-1 where: 0=fully transparent, 1= fully opaque
        self.opacity = 0.6
        self.textureReady = False # Flag if texture image is ready or not
        self.highlightChecked = False # Flag if highlight is turned on or off
    
        
    def _initTextureEnv(self):
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)


    def _loadTexture(self, fileName):
        '''Load the texture image '''
        ix, iy, image  = getTextureData(fileName) 
    
        # Create Texture
        glBindTexture(GL_TEXTURE_2D, glGenTextures(1))   # 2d texture (x and y size)
    
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    
        self._initTextureEnv()
    
        self.textureReady = True
    
    
    def setProps(self, name, border_color, width, height, resolution, center, wxyz, trans, fill_color,show_bbox, win_offset, edge_offset):
        '''Set the properties for a ESP Window read from a (MMP) file. '''
        self.name = name; self.color = self.normcolor = border_color;
        self.width = width; self.height = height; self.resolution = resolution; 
        self.center = center;  

        self.quat = Q(wxyz[0], wxyz[1], wxyz[2], wxyz[3])
        
        self.opacity = trans;  self.fill_color = fill_color
        self.show_esp_bbox = show_bbox; self.window_offset = win_offset; self.edge_offset = edge_offset

    def _getinfo(self):
        
        c = self.center * 1e-10
        ctr_pt = (float(c[0]), float(c[1]), float(c[2]))
        centerPoint = '%1.1e %1.1e %1.1e' % ctr_pt
        
        n = c + (self.planeNorm * 1e-10)
        np = (float(n[0]), float(n[1]), float(n[2]))
        normalPoint = '%1.1e %1.1e %1.1e' % np
        
        return  "[Object: ESP Window] [Name: " + str(self.name) + "] " + \
                    "[centerPoint = " + centerPoint + "] " + \
                    "[normalPoint = " + normalPoint + "]"

# Need to add stats for this jig type (and the GridPlane, too.) Mark 050930.        
#    def getstatistics(self, stats):
#        stats.nespwin += 1    
      
    def set_cntl(self):
        from ESPWindowProp import ESPWindowProp
        self.cntl = ESPWindowProp(self, self.assy.o)

    
    def _createShape(self, selSense = 2):
        ''' '''
        hw = self.width/2.0; wo = self.window_offset; eo = self.edge_offset
        
        shape = SelectionShape(self.right, self.up, self.planeNorm)
        slab = Slab(self.center-self.planeNorm*wo, self.planeNorm, 2*wo)
        pos = [V(-hw-eo, hw+eo, 0.0), V(hw+eo, -hw-eo, 0.0)];  p3d = []         
        for p in pos:   
            p3d += [self.quat.rot(p) + self.center]
        
        shape.pickrect(p3d[0], p3d[1], self.center, selSense, slab=slab)

        return shape
    
        
    def pickSelected(self, pick):
        '''Select atoms inside the ESP Window bounding box. Actually this works for chunk too.'''
        if not pick: sense = 0
        else: sense = 2
        
        shape = self._createShape(sense)
        shape.select(self.assy)

        
    def findObjsInside(self):
        '''Find objects inside the shape '''
        shape = self._createShape()
        return shape.findObjInside(self.assy)


    def highlightAtomChunks(self):
        '''hightlight atoms '''
        if not self.highlightChecked: return 
        
        atomChunks = self.findObjsInside()
        for m in atomChunks:
            if isinstance(m, molecule):
                for a in m.atoms.itervalues():
                    a.overdraw_with_special_color(green)
            else:
                m.overdraw_with_special_color(green)
    
    def edit(self):
        '''Force into 'Select Atom' mode before open the dialog '''
        from constants import SELWHAT_ATOMS
        
        self.assy.o.setMode('SELECTATOMS')        
        Jig.edit(self)
        
    
    def _draw(self, win, dispdef):
        glPushMatrix()

        glTranslatef( self.center[0], self.center[1], self.center[2])
        q = self.quat
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z) 
        
        drawPlane(self.fill_color, self.width, self.width, self.textureReady, self.opacity, SOLID=True)
        
        hw = self.width/2.0
        corners_pos = [V(-hw, hw, 0.0), V(-hw, -hw, 0.0), V(hw, -hw, 0.0), V(hw, hw, 0.0)]
        drawLineLoop(self.color, corners_pos)  
        
        # Draw the ESP Window bbox.
        if self.show_esp_bbox:
            wo = self.window_offset
            eo = self.edge_offset
            drawwirecube(self.color, V(0.0, 0.0, 0.0), V(hw+eo, hw+eo, wo), 1.0) #drawwirebox
            
            # This is for debugging purposes.  This draws a green normal vector using
            # local space coords.  Mark 050930
            if 0:
                drawline(green, V(0.0, 0.0, 0.0), V(0.0, 0.0, 1.0), 0, 3)

        glPopMatrix()
        
        # This is for debugging purposes. This draws a yellow normal vector using 
        # model space coords.  Mark 050930
        if 0:
            drawline(yellow, self.center, self.center + self.planeNorm, 0, 3)
 
 
    def mmp_record_jigspecific_midpart(self):
        color = map(int,A(self.fill_color)*255)
        
        dataline = "%.2f %.2f %d (%f, %f, %f) (%f, %f, %f, %f) %.2f (%d, %d, %d) %d %.2f %.2f" % \
           (self.width, self.height, self.resolution, 
            self.center[0], self.center[1], self.center[2], 
            self.quat.w, self.quat.x, self.quat.y, self.quat.z, 
            self.opacity, color[0], color[1], color[2], self.show_esp_bbox, self.window_offset, self.edge_offset)
        return " " + dataline

    def get_sim_parms(self):
        from NanoHive import NH_Sim_Parameters
        sim_parms = NH_Sim_Parameters()
        
        sim_parms.desc = 'ESP Calculation from MT Context Menu for ' + self.name
        sim_parms.iterations = 1
        sim_parms.spf = 1e-17 # Steps per Frame
        sim_parms.temp = 300 # Room temp
        sim_parms.esp_window = self
        
        return sim_parms
        
    def calculate_esp(self):
        
        cmd = greenmsg("Calculate ESP: ")
        
        sim_parms = self.get_sim_parms()
        sims_to_run = ["MPQC_ESP"]
        results_to_save = [] # Results info included in write_nh_mpqc_esp_rec()
        
        from platform import find_or_make_Nanorex_subdir
        results_file = os.path.join(find_or_make_Nanorex_subdir("Nano-Hive"), self.name + ".png")
        
        from NanoHiveUtils import run_nh_simulation
        run_nh_simulation(self.assy, 'CalcESP', sim_parms, sims_to_run, results_to_save)
        
        info = "Running ESP calculation on [%s]. Results will be written to: [%s]" % (self.name, results_file) 
        env.history.message( cmd + info ) 
        self.assy.w.win_update()
        
        return
        
    def __CM_Calculate_ESP(self):
        '''Method for "Calculate ESP" context menu'''
        self.calculate_esp()
    
    def __CM_Load_ESP_Image(self):
        '''Method for "Calculate ESP" context menu'''
        from platform import find_or_make_Nanorex_subdir
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        png_name = os.path.join(nhdir,self.name+".png")
        print png_name
    
        if not self.textureReady:
            if not os.path.exists(png_name):
                QMessageBox.warning( self.assy.w, "Warnings:", \
                    "The image file doesn't exist, please choose another one.", \
                    QMessageBox.Ok, QMessageBox.NoButton)
              
                odir = globalParms['WorkingDirectory']
    
                fn = QFileDialog.getOpenFileName(odir, \
                    "All Files (*.png *.jpg *.gif *.bmp);;", self.assy.w )
                
                png_name = str(fn)        
            
                if not fn:
                    env.history.message("Cancelled.")
                    return
        
            self._loadTexture(png_name)
        
        else: 
            self.textureReady = False
        
        self.assy.o.gl_update()
    
    pass # end of class ESPWindow       