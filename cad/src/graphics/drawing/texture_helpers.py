# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
texture_helpers.py -- helper functions for using OpenGL textures

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from OpenGL.GL import glGenTextures
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import glBindTexture
from OpenGL.GL import GL_UNPACK_ALIGNMENT
from OpenGL.GL import glPixelStorei
from OpenGL.GL import GL_RGBA
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import glTexImage2D
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

from OpenGL.GLU import gluBuild2DMipmaps

from utilities.debug_prefs import Choice_boolean_False   # in disabled code
from utilities.debug_prefs import debug_pref   # in disabled code

# note this runtime import below -- TODO, find out if it can be toplevel;
# the file it imports is not now [071017] in any import cycles:
## from ImageUtils import nEImageOps

# ==

# higher-level helpers

def load_image_into_new_texture_name(image_file, tex_name = 0):
    """
    Allocate texture object in current GL Context (or use given one)
    (either way, return have_mipmaps, tex_name)
    and load image from file into it.
    [what if wrong size??]
    """
    # took code from ESPImage
    image_obj = create_PIL_image_obj_from_image_file( image_file)
    have_mipmaps, tex_name = loadTexture(image_obj, tex_name)
    return have_mipmaps, tex_name

# TODO: rename, docstring
def setup_to_draw_texture_name(have_mipmaps, tex_name):
    """
    #doc

    Anything that calls this should eventually call
    glpane.kluge_reset_texture_mode_to_work_around_renderText_bug(),
    but only after all drawing using the texture is done.
    """
    # assume it's already set up [what does that mean? bruce 071017]
    #e bind it
    glBindTexture(GL_TEXTURE_2D, tex_name)
    _initTextureEnv(have_mipmaps) # sets texture params the way we want them
    ## now you can: (from ESPImage._draw_jig, which before this did pushmatrix
    ## etc)
    ## drawPlane(self.fill_color, self.width, self.width, textureReady,
    ##           self.opacity, SOLID = True, pickCheckOnly = self.pickCheckOnly)
    ##hw = self.width/2.0
    ##corners_pos = [V(-hw, hw, 0.0), V(-hw, -hw, 0.0),
    ##               V(hw, -hw, 0.0), V(hw, hw, 0.0)]
    ##drawLineLoop(color, corners_pos)  
    return

# ==

# lower-level helpers modified from ESPImage
# [note: some of these are called from exprs/images.py; others are copied &
# modified into it [bruce 061125]]

# misnamed, see docstring; added kws, 061127
def create_PIL_image_obj_from_image_file(image_file, **kws):
    ### TODO: refile this into ImageUtils?
    """
    Creates and returns an nEImageOps object
    (using the given kws, documented in ImageUtils.py),
    which contains (and sometimes modifies in place)
    a PIL image object made from the named image file.
    """
    from graphics.images.ImageUtils import nEImageOps
    return nEImageOps(image_file, **kws)

def loadTexture(image_obj, tex_name = 0): #e arg want_mipmaps
    """
    Load texture data from current image object;
    return have_mipmaps, tex_name
    (also leave that texture bound, BTW)
    """
    # note: some of this code has been copied into exprs/images.py, class
    # texture_holder [bruce 061125]
    ix, iy, image = image_obj.getTextureData() 

    # allocate texture object if necessary
    if not tex_name:
        tex_name = glGenTextures(1)
        # It's deprecated to let this happen much. [070308]
        print "debug fyi: texture_helpers.loadTexture allocated tex_name %r" %\
              (tex_name,)
        # note: by experiment (iMac G5 Panther), this returns a single number
        # (1L, 2L, ...), not a list or tuple, but for an argument >1 it returns
        # a list of longs. We depend on this behavior here. [bruce 060207]
        tex_name = int(tex_name) # make sure it worked as expected
        assert tex_name != 0
    
    # initialize texture data
    glBindTexture(GL_TEXTURE_2D, tex_name)   # 2d texture (x and y size)

    glPixelStorei(GL_UNPACK_ALIGNMENT,1) ###k what's this?
    have_mipmaps = False
    ##want_mipmaps = debug_pref("smoother tiny textures",
    ##                          Choice_boolean_False, prefs_key = True)
    want_mipmaps = True
    if want_mipmaps: 
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, ix, iy, GL_RGBA,
                          GL_UNSIGNED_BYTE, image)
        have_mipmaps = True
    else:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, image)
            # 0 is mipmap level, GL_RGBA is internal format, ix, iy is size, 0
            # is borderwidth, and (GL_RGBA, GL_UNSIGNED_BYTE, image) describe
            # the external image data. [bruce 060212 comment]
    return have_mipmaps, tex_name

# This gets us ready to draw (using coords in) a texture if we have it bound, I
# think. Called during draw method [modified from ESPImage.]
#e need smooth = False/True
def _initTextureEnv(have_mipmaps):
    """
    have_mipmaps is boolean #doc

    Anything that calls this should eventually call
    glpane.kluge_reset_texture_mode_to_work_around_renderText_bug(),
    but only after all drawing using the texture is done.
    """
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        # [looks like a bug that we overwrite clamp with repeat, just below?
        # bruce 060212 comment]
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    if (0 and "kluge" and
        debug_pref("smoother textures", Choice_boolean_False,
                   prefs_key = True)): ###@@@ revise to param
        #bruce 060212 new feature (only visible in debug version so far);
        # ideally it'd be controllable per-jig for side-by-side comparison;
        # also, changing its menu item ought to gl_update but doesn't ##e
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        if have_mipmaps: ###@@@
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                            GL_LINEAR_MIPMAP_LINEAR)
        else:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    else:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    return

# end
