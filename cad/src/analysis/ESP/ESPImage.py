# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
ESPImage.py - display an Electrostatic Potential Image (or any OpenGL texture)

Note: keep this around, even if ESPImage per se becomes obsolete,
since it's also our only working Node for directly displaying an image in
the 3d model space.

@author: Huaicai, Bruce
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History: 

bruce 071215 split class ESPImage into its own file, out of jigs_planes.py.

TODO: refactor into a general texture image jig (and perhaps
some texture helpers, but merge those with the ones in texture_*.py
which were partly derived from these methods),
and a specific ESPImage jig.

Module classification: model, though contains operations/simulation
and perhaps other code. Probably part of an ESP package.
"""

import os
import math
import shutil

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPushName, glPopName

from OpenGL.GL import GL_CLAMP
from OpenGL.GL import GL_TEXTURE_WRAP_S
from OpenGL.GL import glTexParameterf
from OpenGL.GL import GL_TEXTURE_WRAP_T
from OpenGL.GL import GL_REPEAT
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_TEXTURE_MAG_FILTER
from OpenGL.GL import GL_LINEAR_MIPMAP_LINEAR
from OpenGL.GL import GL_TEXTURE_MIN_FILTER
from OpenGL.GL import GL_NEAREST
from OpenGL.GL import GL_DECAL
from OpenGL.GL import GL_TEXTURE_ENV
from OpenGL.GL import GL_TEXTURE_ENV_MODE
from OpenGL.GL import glTexEnvf
from OpenGL.GL import glGenTextures
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import glBindTexture
from OpenGL.GL import GL_UNPACK_ALIGNMENT
from OpenGL.GL import glPixelStorei
from OpenGL.GL import GL_RGBA
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import glTexImage2D
from OpenGL.GLU import gluBuild2DMipmaps

from PyQt4.Qt import QMessageBox
from PyQt4.Qt import QFileDialog

import foundation.env as env
from utilities import debug_flags
from foundation.state_utils import DataMixin

from model.chunk import Chunk
from model.chem import Atom

from graphics.drawing.drawers import drawPlane
from graphics.drawing.drawers import drawwirecube
from graphics.drawing.drawers import drawLineLoop

from geometry.VQT import V, Q, A
from graphics.rendering.povray.povheader import povpoint
from graphics.behaviors.shape import SelectionShape
from geometry.Slab import Slab

from utilities.Log import redmsg, greenmsg 
from utilities.debug_prefs import debug_pref, Choice_boolean_False
from model.jigs import Jig # REVIEW: all uses of this are suspicious!
from graphics.images.ImageUtils import nEImageOps

from utilities.constants import black
from utilities.constants import ave_colors
from utilities.constants import green
from utilities.constants import START_NEW_SELECTION
from utilities.constants import SUBTRACT_FROM_SELECTION

from model.jigs_planes import RectGadget
from model.jigs_planes import povStrVec

from analysis.ESP.ESPImageProp import ESPImageProp
from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir

from analysis.ESP.NanoHiveUtils import get_nh_espimage_filename
from analysis.ESP.NanoHiveUtils import run_nh_simulation
from analysis.ESP.NanoHive_SimParameters import NanoHive_SimParameters
from utilities.debug import print_compact_traceback
# ==

class ESPImage(RectGadget):
    """
    Electrostatic potential image, displayed as a translucent square in 3D.
    """
    #bruce 060212 use separate own_mutable_attrs and mutable_attrs to work around design flaws in attrlist inheritance scheme
    # (also including superclass mutable_attrs center,quat -- might fix some bugs -- and adding image_mods)
    own_mutable_attrs = ('fill_color', 'image_mods', )
    mutable_attrs = RectGadget.mutable_attrs + own_mutable_attrs
    copyable_attrs = RectGadget.copyable_attrs + own_mutable_attrs + \
                   ('resolution', 'opacity', 'show_esp_bbox', 'image_offset', 'edge_offset',
                    'espimage_file', 'highlightChecked', 'xaxis_orient', 'yaxis_orient', 'multiplicity')
        #bruce 060212 added 'espimage_file', 'highlightChecked', 'xaxis_orient', 'yaxis_orient', 'multiplicity'
        # (not sure adding 'multiplicity' is correct)

    sym = "ESPImage" #bruce 070604 removed space (per Mark decision)
    icon_names = ["modeltree/ESP_Image.png", "modeltree/ESP_Image-hide.png"]
    mmp_record_name = "espimage"
    featurename = "ESP Image" #Renamed from ESP Window. mark 060108

    
    def __init__(self, assy, list, READ_FROM_MMP = False):
        RectGadget.__init__(self, assy, list, READ_FROM_MMP)
        self.assy = assy
        self.color = black # Border color
        self.normcolor = black
        self.fill_color = 85/255.0, 170/255.0, 255/255.0 # The fill color, a nice blue

        # This specifies the resolution of the ESP Image. 
        # The total number of ESP data points in the image will number resolution^2. 
        self.resolution = 32 # Keep it small so sim run doesn't take so long. Mark 050930.
        # Show/Hide ESP Image Volume (Bbox).  All atoms inside this volume are used by 
        # the MPQC ESP Plane plug-in to calculate the ESP points.
        self.show_esp_bbox = True
        # the perpendicular (front and back) image offset used to create the depth of the bbox
        self.image_offset = 1.0
        # the edge offset used to create the edge boundary of the bbox
        self.edge_offset = 1.0 
        # opacity, a range between 0-1 where: 0 = fully transparent, 1= fully opaque
        self.opacity = 0.6
        self.image_obj = None # helper object for texture image, or None if no texture is ready [bruce 060207 revised comment]
        self.image_mods = image_mod_record() # accumulated modifications to the file's image [bruce 060210 bugfix]
            ###e need to use self.image_mods in writepov, too, perhaps via a temporary image file
        self.tex_name = None # OpenGL texture name for image_obj, if we have one [bruce 060207 for fixing bug 1059]
        self.espimage_file = '' # ESP Image (png) filename
        self.highlightChecked = False # Flag if highlight is turned on or off
            ###e does this need storing in mmp file? same Q for xaxis_orient, etc. [bruce 060212 comment]
        self.xaxis_orient = 0 # ESP Image X Axis orientation [bruce comment 060212: this is used by external code in files_nh.py]
        self.yaxis_orient = 0 # ESP Image Y Axis orientation
        self.multiplicity = 1 # Multiplicity of atoms within this jig's bbox volume

        self.pickCheckOnly = False #This is used to notify drawing code if it's just for picking purpose
        return

    def _initTextureEnv(self): # called during draw method
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            # [looks like a bug that we overwrite clamp with repeat, just below? bruce 060212 comment]
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        if debug_pref("smoother textures", Choice_boolean_False, prefs_key = True):
            #bruce 060212 new feature (only visible in debug version so far);
            # ideally it'd be controllable per-jig for side-by-side comparison;
            # also, changing its menu item ought to gl_update but doesn't ##e
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            if self.have_mipmaps:
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            else:
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        else:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        return

    def _create_PIL_image_obj_from_espimage_file(self):
        """
        Creates a PIL image object from the jig's ESP image (png) file.
        """
        if self.espimage_file:
            self.image_obj = nEImageOps(self.espimage_file)
            self.image_mods.do_to( self.image_obj) #bruce 060210 bugfix: stored image_mods in mmp file, so we can reuse them here
        return

    def _loadTexture(self):
        """
        Load texture data from current image object
        """
        ix, iy, image = self.image_obj.getTextureData() 

        # allocate texture object if never yet done [bruce 060207 revised all related code, to fix bug 1059]
        if self.tex_name is None:
            self.tex_name = glGenTextures(1)
            # note: by experiment (iMac G5 Panther), this returns a single number (1L, 2L, ...), not a list or tuple,
            # but for an argument >1 it returns a list of longs. We depend on this behavior here. [bruce 060207]

        # initialize texture data
        glBindTexture(GL_TEXTURE_2D, self.tex_name)   # 2d texture (x and y size)

        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        self.have_mipmaps = False
        if debug_pref("smoother tiny textures", Choice_boolean_False, prefs_key = True):
            #bruce 060212 new feature; only takes effect when image is reloaded for some reason (like "load image" button)
            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, ix, iy, GL_RGBA, GL_UNSIGNED_BYTE, image)
            self.have_mipmaps = True
        else:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
                # 0 is mipmap level, GL_RGBA is internal format, ix, iy is size, 0 is borderwidth,
                # and (GL_RGBA, GL_UNSIGNED_BYTE, image) describe the external image data. [bruce 060212 comment]

        ## self._initTextureEnv() #bruce 060207 do this in draw method, not here
        self.assy.o.gl_update()
        return

    def setProps(self, name, border_color, width, height, resolution, center, wxyz, trans, fill_color,show_bbox, win_offset, edge_offset):
        """
        Set the properties for a ESP Image read from a (MMP) file.
        """
        self.name = name; self.color = self.normcolor = border_color;
        self.width = width; self.height = height; self.resolution = resolution; 
        self.center = center;  

        self.quat = Q(wxyz[0], wxyz[1], wxyz[2], wxyz[3])

        self.opacity = trans;  self.fill_color = fill_color
        self.show_esp_bbox = show_bbox; self.image_offset = win_offset; self.edge_offset = edge_offset

    def _getinfo(self):

        c = self.center * 1e-10
        ctr_pt = (float(c[0]), float(c[1]), float(c[2]))
        centerPoint = '%1.2e %1.2e %1.2e' % ctr_pt

        n = c + (self.planeNorm * 1e-10)
        np = (float(n[0]), float(n[1]), float(n[2]))
        normalPoint = '%1.2e %1.2e %1.2e' % np

        return  "[Object: ESP Image] [Name: " + str(self.name) + "] " + \
                "[centerPoint = " + centerPoint + "] " + \
                "[normalPoint = " + normalPoint + "]"

    def getstatistics(self, stats):
        stats.num_espimage += 1  

    def set_cntl(self):
        self.cntl = ESPImageProp(self, self.assy.o)

    def _createShape(self, selSense = START_NEW_SELECTION):
        """
        """
        hw = self.width/2.0; wo = self.image_offset; eo = self.edge_offset

        shape = SelectionShape(self.right, self.up, self.planeNorm)
        slab = Slab(self.center - self.planeNorm * wo, self.planeNorm, 2 * wo)
        pos = [V(-hw - eo, hw + eo, 0.0), V(hw + eo, -hw - eo, 0.0)]
        p3d = []         
        for p in pos:   
            p3d += [self.quat.rot(p) + self.center]

        # selSense used to highlight (not select) atoms inside the jig's volume.
        shape.pickrect(p3d[0], p3d[1], self.center, selSense, slab = slab)

        return shape

    def pickSelected(self, pick):
        """
        Select atoms inside the ESP Image bounding box. Actually this works for chunk too.
        """
        # selSense is used to highlight (not select) atoms inside the jig's volume.
        if not pick:
            selSense = SUBTRACT_FROM_SELECTION
        else:
            selSense = START_NEW_SELECTION

        shape = self._createShape(selSense)
        shape.select(self.assy)
        return

    def findObjsInside(self):
        """
        Find objects [atoms or chunks] inside the shape
        """
        shape = self._createShape()
        return shape.findObjInside(self.assy)

    def highlightAtomChunks(self):
        """
        highlight atoms
        """
        if not self.highlightChecked:
            return 

        atomChunks = self.findObjsInside()
        for m in atomChunks:
            if isinstance(m, Chunk):
                for a in m.atoms.itervalues():
                    a.overdraw_with_special_color(ave_colors( 0.8, green, black))
            else:
                m.overdraw_with_special_color(ave_colors( 0.8, green, black))
        return

    def edit(self): # in class ESPImage
        """
        Force into 'Build' mode before opening the dialog
        """
        #bruce 060403 changes: force Build, not Select Atoms as before; only do this if current mode is not Build.
        # (But why do we need to force it into any particular mode? I don't know. [bruce 070608])
        commandSequencer = self.assy.w.commandSequencer #bruce 071008
        commandSequencer.userEnterCommand('DEPOSIT')
        Jig.edit(self)

    def make_selobj_cmenu_items(self, menu_spec):
        """
        Add ESP Image specific context menu items to <menu_spec> list when self is the selobj.
        Currently not working since ESP Image jigs do not get highlighted. mark 060312.
        """
        item = ('Hide', self.Hide)
        menu_spec.append(item)
        menu_spec.append(None) # Separator
        item = ('Properties...', self.edit)
        menu_spec.append(item)
        item = ('Calculate ESP', self.__CM_Calculate_ESP)
        menu_spec.append(item)
        item = ('Load ESP Image', self.__CM_Load_ESP_Image)
        menu_spec.append(item)
        return

    def writepov(self, file, dispdef):
        if self.hidden:
            return
        if self.is_disabled():
            return #bruce 050421

        hw = self.width/2.0; wo = self.image_offset; eo = self.edge_offset
        corners_pos = [V(-hw, hw, 0.0), V(-hw, -hw, 0.0), V(hw, -hw, 0.0), V(hw, hw, 0.0)]
        povPlaneCorners = []
        for v in corners_pos:
            povPlaneCorners += [self.quat.rot(v) + self.center]
        strPts = ' %s, %s, %s, %s ' % tuple(map(povpoint, povPlaneCorners))
        if self.image_obj:
            imgName = os.path.basename(self.espimage_file)
            imgPath = os.path.dirname(self.espimage_file)
            file.write('\n // Before you render, please set this command option: Library_Path="%s"\n\n' % (imgPath,))
            file.write('esp_plane_texture(' + strPts + ', "'+ imgName + '") \n')
        else:
            color = '%s %f>' % (povStrVec(self.fill_color), self.opacity)
            file.write('esp_plane_color(' + strPts + ', ' + color + ') \n')
        return
    
    def draw(self, glpane, dispdef):
        """
        Does nothing. All the drawing is done after the main drawing code is 
        done. (i.e. in self.draw_after_highlighting(). 
        @see: self.draw_after_highlighting()
        """
        pass
    
    def draw_after_highlighting(self, 
                                glpane, 
                                dispdef, 
                                pickCheckOnly = False):
        """
        For ESPImage class, this does all the drawing. (Does it after main
        drawing code is finished drawing.) This method ensures that the 
        ESP image jig gets selected even when you click inside the 
        rectangular box (i.e. not just along the edges of the box).
        @see: GraphicsMode.Draw_after_highlighting()
        @see: Node.draw_after_highlighting()
        @see: Plane.draw_after_highlighting()
        """
        anythingDrawn = False
        if self.hidden:
            return anythingDrawn
        
        self.pickCheckOnly = pickCheckOnly        
        try:
            anythingDrawn = True
            glPushName(self.glname)
            self._draw(glpane, dispdef) #calls self._draw_jig()
        except:
            anythingDrawn = False
            glPopName()
            print_compact_traceback("ignoring exception when drawing Jig %r: " % self)
        else:
            glPopName()
            
        return anythingDrawn

    def _draw_jig(self, glpane, color, highlighted = False):
        """
        Draw a ESP Image jig as a plane with an edge and a bounding box.
        """
        glPushMatrix()

        glTranslatef( self.center[0], self.center[1], self.center[2])
        q = self.quat
        glRotatef( q.angle*180.0/math.pi, q.x, q.y, q.z) 

        #bruce 060207 extensively revised texture code re fixing bug 1059
        if self.tex_name is not None and self.image_obj: # self.image_obj condition is needed, for clear_esp_image() to work
            textureReady = True
            glBindTexture(GL_TEXTURE_2D, self.tex_name) # maybe this belongs in draw_plane instead? Put it there later. ##e
            self._initTextureEnv() # sets texture params the way we want them
        else:
            textureReady = False
        drawPlane(self.fill_color, self.width, self.width, textureReady, self.opacity,
                  SOLID = True, pickCheckOnly = self.pickCheckOnly)

        hw = self.width/2.0
        corners_pos = [V(-hw, hw, 0.0), V(-hw, -hw, 0.0), V(hw, -hw, 0.0), V(hw, hw, 0.0)]
        drawLineLoop(color, corners_pos)  

        # Draw the ESP Image bbox.
        if self.show_esp_bbox:
            wo = self.image_offset
            eo = self.edge_offset
            drawwirecube(color, V(0.0, 0.0, 0.0), V(hw + eo, hw + eo, wo), 1.0) #drawwirebox

            # This is for debugging purposes.  This draws a green normal vector using
            # local space coords.  Mark 050930
            if 0:
                from graphics.drawing.CS_draw_primitives import drawline
                drawline(green, V(0.0, 0.0, 0.0), V(0.0, 0.0, 1.0), 0, 3)

        glPopMatrix()

        # This is for debugging purposes. This draws a yellow normal vector using 
        # model space coords.  Mark 050930
        if 0:
            from graphics.drawing.CS_draw_primitives import drawline
            from utilities.constants import yellow
            drawline(yellow, self.center, self.center + self.planeNorm, 0, 3)

    def writemmp(self, mapping):
        """
        [extends Jig method]
        """
        super = Jig
        super.writemmp(self, mapping)
        # Write espimage "info" record.
        line = "info espimage espimage_file = " + self.espimage_file + "\n"
        mapping.write(line)
        #bruce 060210 bugfix: write image_mods if we have any
        if self.image_mods:
            line = "info espimage image_mods = %s\n" % (self.image_mods,)
            mapping.write(line)
        return

    def mmp_record_jigspecific_midpart(self):
        color = map(int,A(self.fill_color)*255)

        dataline = "%.2f %.2f %d (%f, %f, %f) (%f, %f, %f, %f) %.2f (%d, %d, %d) %d %.2f %.2f" % \
                 (self.width, self.height, self.resolution, 
                  self.center[0], self.center[1], self.center[2], 
                  self.quat.w, self.quat.x, self.quat.y, self.quat.z, 
                  self.opacity, color[0], color[1], color[2], self.show_esp_bbox, self.image_offset, self.edge_offset)
        return " " + dataline

    def readmmp_info_espimage_setitem( self, key, val, interp ):
        """
        This is called when reading an mmp file, for each "info espimage" record
        which occurs right after this node is read and no other (espimage jig) node has been read.
           Key is a list of words, val a string; the entire record format
        is presently [060108] "info espimage <key> = <val>", and there is exactly
        one word in <key>, "espimage_file". <val> is the espimage filename.
        <interp> is not currently used.
        """
        if len(key) != 1:
            if debug_flags.atom_debug:
                print "atom_debug: fyi: info espimage with unrecognized key %r (not an error)" % (key,)
            return
        if key[0] == 'espimage_file':
            if val:
                if os.path.exists(val):
                    self.espimage_file = val
                    self.image_mods.reset() # also might be done in load_espimage_file, but needed here even if it's not
                    self.load_espimage_file()
                else:
                    msg = redmsg("info espimage espimage_file = " + val + ". File does not exist.  No image loaded.")
                    env.history.message(msg)
            #e I think it's a bug to go on to interpret image_mods if the file doesn't exist. Not sure how to fix that.
            # [bruce 060210]
            pass
        elif key[0] == 'image_mods': #bruce 060210
            try:
                self.image_mods.set_to_str(val)
            except ValueError:
                print "mmp syntax error in esp image modifications:", val
            else:
                if self.image_obj:
                    self.image_mods.do_to( self.image_obj)
                    self._loadTexture()
            pass
        return

    def get_sim_parms(self):
        sim_parms = NanoHive_SimParameters()

        sim_parms.desc = 'ESP Calculation from MT Context Menu for ' + self.name
        sim_parms.iterations = 1
        sim_parms.spf = 1e-17 # Steps per Frame
        sim_parms.temp = 300 # Room temp

        # Get updated multiplicity from this ESP image jig bbox
        atomList = self.findObjsInside()
        self.multiplicity = getMultiplicity(atomList)        

        sim_parms.esp_image = self

        return sim_parms

    def calculate_esp(self):

        cmd = greenmsg("Calculate ESP: ")

        errmsgs = [ "Error: Nano-Hive plug-in not enabled.",
                    "Error: Nano-Hive Plug-in path is empty.",
                    "Error: Nano-Hive plug-in path points to a file that does not exist.",
                    "Error: Nano-Hive plug-in is not Version 1.2b.",
                    "Error: Couldn't connect to Nano-Hive instance.",
                    "Error: Load command failed.",
                    "Error: Run command failed.",
                    "Simulation Aborted"
                ]

        sim_parms = self.get_sim_parms()
        sims_to_run = ["MPQC_ESP"]
        results_to_save = [] # Results info included in write_nh_mpqc_esp_rec()

        # Temporary file name of ESP image file.
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        tmp_espimage_file = os.path.join(nhdir, "%s.png" % (self.name))

        # Destination (permanent) file name of ESP image file.
        espimage_file = get_nh_espimage_filename(self.assy, self.name)

        msg = "Running ESP calculation on [%s]. Results will be written to: [%s]" % (self.name, espimage_file)
        env.history.message( cmd + msg ) 

        r = run_nh_simulation(self.assy, 'CalcESP', sim_parms, sims_to_run, results_to_save)

        if r:
            msg = redmsg(errmsgs[r - 1])
            env.history.message( cmd + msg )
            return

        msg = "ESP calculation on [%s] finished." % (self.name)
        env.history.message( cmd + msg ) 

        # Move tmp file to permanent location.  Make sure the tmp file is there.
        if os.path.exists(tmp_espimage_file):
            shutil.move(tmp_espimage_file, espimage_file)
        else:
            print "Temporary ESP Image file ", tmp_espimage_file," does not exist. Image not loaded."
            return

        self.espimage_file = espimage_file
        self.load_espimage_file()
        self.assy.changed()
        self.assy.w.win_update()

        return


    def __CM_Calculate_ESP(self):
        """
        Method for "Calculate ESP" context menu
        """
        self.calculate_esp()

    def __CM_Load_ESP_Image(self):
        """
        Method for "Load ESP Image" context menu
        """
        self.load_espimage_file()

    def load_espimage_file(self, choose_new_image = False, parent = None):
        """
        Load the ESP (.png) image file pointed to by self.espimage_file.
        If the file does not exist, or if choose_new_image is True, the
        user will be prompted to choose a new image, and if the file chooser dialog is not
        cancelled, the new image will be loaded and its pathname stored in self.espimage_file.
        Return value is None if user cancels the file chooser, but is self.espimage_file
        (which has just been reloaded, and a history message emitted, whether or not
        it was newly chosen) in all other cases.

        If self.espimage_file is changed (to a different value), this marks assy as changed.
        """
        #bruce 060207 revised docstring. I suspect this routine has several distinct
        # purposes which should not be so intimately mixed (i.e. it should be several
        # routines). Nothing presently uses the return value.

        old_espimage_file = self.espimage_file

        if not parent:
            parent = self.assy.w

        cmd = greenmsg("Load ESP Image: ")

        ## print "load_espimage_file(): espimage_file = ", self.espimage_file

        if choose_new_image or not self.espimage_file:
            choose_new_image = True

        elif not os.path.exists(self.espimage_file):
            msg = "The ESP image file:\n" + self.espimage_file + "\ndoes not exist.\n\nWould you like to select one?"
            choose_new_image = True
            QMessageBox.warning( parent, "Choose ESP Image", \
                                 msg, QMessageBox.Ok, QMessageBox.Cancel)
            #bruce 060207 question: shouldn't we check here whether they said ok or cancel?? Looks like a bug. ####@@@@

        if choose_new_image: 
            cwd = self.assy.get_cwd()

            fn = QFileDialog.getOpenFileName(
                parent,
                "Load an ESP Image File",
                cwd,
                "Portable Network Graphics (*.png);;All Files (*.*);;" 
                ) #bruce 060212 added All Files option


            if not fn:
                env.history.message(cmd + "Cancelled.") #bruce 060212 bugfix: included cmd
                return None

            self.espimage_file = str(fn)
            if old_espimage_file != self.espimage_file:
                self.changed() #bruce 060207 fix of perhaps-previously-unreported bug
            pass

        if self.image_mods:
            self.image_mods.reset()
            self.changed()

        self._create_PIL_image_obj_from_espimage_file()
        self._loadTexture()
            #bruce 060212 comment: this does gl_update, but when we're called from dialog's open file button,
            # the glpane doesn't show the new texture until the dialog is closed (which is a bug, IMHO),
            # even if we call env.call_qApp_processEvents() before returning from this method (load_espimage_file).
            # I don't know why.

        # Bug fix 1041-1.  Mark 051003
        msg = "ESP image loaded: [" + self.espimage_file + "]"
        env.history.message(cmd + msg)

        return self.espimage_file


    def clear_esp_image(self):
        """
        Clears the image in the ESP Image.
        """
        self.image_obj = None
        # don't self.image_mods.reset(); but when we load again, that might clear it
        self.assy.o.gl_update()

    def flip_esp_image(self): # slot method
        if self.image_obj:
            self.image_obj.flip()
            self.image_mods.flip() #bruce 060210
            self.changed() #bruce 060210
            self._loadTexture()

    def mirror_esp_image(self):
        if self.image_obj:
            self.image_obj.mirror()
            self.image_mods.mirror() #bruce 060210
            self.changed() #bruce 060210
            self._loadTexture()

    def rotate_esp_image(self, deg):
        if self.image_obj:
            self.image_obj.rotate(deg)
            self.image_mods.rotate(deg) #bruce 060210
            self.changed() #bruce 060210
            self._loadTexture()

    pass # end of class ESPImage       


def getMultiplicity(objList): # only used in this file
    """
    @param objList: A list of Atom/Chunk objects
    @return: If the total number of electron is odd, return 2, otherwise return 1.

    @note: not correct for PAM atoms, but doesn't check for the error of using one.
    """
    #Huaicai 10/04/05 -- see also the test code at EOF
    # [bruce 071120 moved this from chem.py to jigs_planes.py]
    numElectrons = 0
    for m in objList:
        if isinstance(m, Atom):
            numElectrons += m.element.eltnum
        elif isinstance(m, Chunk):
            for a in m.atoms.itervalues():
                numElectrons += a.element.eltnum

    if numElectrons % 2:
        return 2
    else:
        return 1
    pass


class image_mod_record(DataMixin): #bruce 060210; maybe should be refiled in ImageUtils.py, though only used in this file
    """
    record the mirror/flip/rotate history of an image in a short canonical form,
    and be able to write/read/do this
    """
    def __init__(self, mirror = False, ccwdeg = 0):
        """
        whether to mirror it, and (then) how much to rotate it
        counterclockwise, in degrees
        """
            #k haven't verified it's ccw and not cw, in terms of how it's used, but this code should work either way
        self.mirrorQ = not not mirror # boolean
        self.rot = ccwdeg % 360 # float or int (I think)

    def reset(self):
        """reset self to default values"""
        self.mirrorQ = False
        self.rot = 0

    def __str__(self):
        """
        [WARNING (kluge, sorry): this format is required by the code,
         which uses it to print parts of mmp records]
        """
        return "%s %s" % (self.mirrorQ, self.rot)

    def __repr__(self):
        return "<%s at %#x; mirrorQ, rot == %r>" % (self.__class__.__name__, id(self), (self.mirrorQ, self.rot))

    def set_to_str(self, str1):
        """
        set self to the values encoded in the given string, which should
        have been produced by str(self); debug print on syntax error
        """
        try:
            mir, rot = str1.split() # e.g. "False", "180"
            ## mir = bool(mir) # wrong -- bool("False") is True!!!
            # mir should be "True" or "False" (unrecognized mirs are treated as False)
            mir = (mir == 'True')
            rot = float(rot)
        except:
            raise ValueError, "syntax error in %r" % (str1,) # (note: no guarantee str1 is even a string, in principle)
        else:
            self.mirrorQ = mir
            self.rot = rot
        return

    def mirror(self):
        """
        left-right mirroring
        """
        self.mirrorQ = not self.mirrorQ
        self.rot = (- self.rot) % 360

    def flip(self):
        """
        vertical flip (top-bottom mirroring)
        """
        self.rotate(90)
        self.mirror()
        self.rotate(-90)

    def rotate(self, deg):
        self.rot = (self.rot + deg) % 360

    def do_to(self, similar):
        """
        do your mods to another object that also has mirror/flip/rotate methods
        """
        if self.mirrorQ:
            similar.mirror()
        if self.rot:
            similar.rotate(self.rot)
        return

    def __nonzero__(self):
        # Python requires this to return an int; i think a boolean should be ok
        return not not (self.mirrorQ or self.rot) # only correct since we always canonicalize rot by % 360

    # override abstract method of DataMixin
    def _copyOfObject(self, copyfunc): # (in class image_mod_record [bruce circa 060210])
        # ignores copyfunc
        return self.__class__(self.mirrorQ, self.rot)

    # override abstract method of DataMixin
    def __eq__(self, other): #bruce 060222 for Undo; in class image_mod_record
        # note: defining __eq__ is sufficient, but only because we inherit
        # from DataMixin, which defines __ne__ based on __eq__
        return self.__class__ is other.__class__ and \
               (self.mirrorQ, self.rot) == (other.mirrorQ, other.rot)

    pass # end of class image_mod_record

# == test code

if __name__ == '__main__':

    nopos = V(0,0,0) #bruce 060308 replaced 'no' with nopos (w/o knowing if it was correct in the first place)

    alist = [Atom('C', nopos, None),
             Atom('C', nopos, None),
             Atom('H', nopos, None),
             Atom('O', nopos, None),
         ]

    assert getMultiplicity(alist) == 2

    alist += [Atom('N', nopos, None),]
    assert getMultiplicity(alist) == 1

    print "Test succeed, no assertion error."


#end
