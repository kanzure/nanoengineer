# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
images.py - provide some image-displaying utilities and primitives

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.


semi-obs documentation:

Image(filename) # a tile, exact same size as image in file (which loads into a texture, rounded up to twopow sizes)

can be used as a texture, or drawn using pixel ops

Image(filename, width, height) # if only width is given, preserves aspect ratio (or only height, possible when names used)
  (that's tricky to declare using defaults, btw; maybe default = None or Automatic)

it can be rotated, translated, etc

Q. what if we want to do image ops to get another image
and use general tex coords to draw that?

A. we need the image obj lying around, without drawing it.

Q. do we keep one cache of image objs from filenames?
A. yes.

Note name conflict: our class Image, and PIL's Image class.

To avoid even more confusion, I'll name this module images.py rather than Image.py
(but note, there exists an unrelated directory cad/images).
"""

import os

from OpenGL.GL import glGenTextures
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import glBindTexture
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
from OpenGL.GL import GL_REPLACE
from OpenGL.GL import GL_BLEND
from OpenGL.GL import glEnable
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import GL_SRC_ALPHA
from OpenGL.GL import glBlendFunc
from OpenGL.GL import GL_ALPHA_TEST
from OpenGL.GL import GL_GREATER
from OpenGL.GL import glAlphaFunc
from OpenGL.GL import glDisable
from OpenGL.GL import glFlush
##from OpenGL.GL import glFinish
from OpenGL.GL import GL_CULL_FACE

from OpenGL.GLU import gluProject

from exprs.draw_utils import draw_textured_rect, draw_textured_rect_subtriangle

from exprs.Rect import Rect

from exprs.Center import Center

from utilities import debug_flags

from geometry.VQT import V
from foundation.env import seen_before

from exprs.ExprsMeta import ExprsMeta
from exprs.Exprs import call_Expr
from exprs.py_utils import MemoDict
from exprs.widget2d import Widget2D
from exprs.attr_decl_macros import Arg, Option, Instance
from exprs.instance_helpers import DelegatingInstanceOrExpr, InstanceOrExpr, DelegatingMixin
from exprs.ExprsConstants import Vector, ORIGIN, PIXELS, D2X, D2Y, DX, DY
from exprs.__Symbols__ import _self, Anything

# NOTE: the following code contains some hardcoded "ui" which
# should be UI_SUBDIRECTORY_COMPONENT
## from icon_utilities import UI_SUBDIRECTORY_COMPONENT

# ImageUtils.py class nEImageOps -- see following comment

# TODO: find out if the functions we need from texture_helpers could be imported here at toplevel:
import graphics.drawing.texture_helpers as texture_helpers
    # Note: from texture_helpers we use:
    #   function create_PIL_image_obj_from_image_file, a trivial glue function into ImageUtils.py class nEImageOps,
    #   function loadTexture.

from utilities.icon_utilities import image_directory # for finding texture & cursor files

# last-resort image file (same image file is used in other modules, but for different purposes)
courierfile = os.path.join( image_directory(), "ui/exprs/text/courier-128.png") ### TODO: RENAME

# old comment about testdraw.py, not sure if still relevant as of 071017:
    # and we copy & modify other funcs from it into this file, but they also remain in testdraw for now, in some cases still used.
    # At some point we'll need to clean up the proper source file of our helper functions from testdraw...
    # when the time comes, the only reliable way to sort out & merge duplicated code (some in other cad/src files too)
    # is to search for all uses of the GL calls being used here.

debug_glGenTextures = True #070308 #####

class _texture_holder(object):
    """
    [private class for use in a public MemoDict]
    From a filename and other data, create on demand, and cache, a PIL Image object and an optional OpenGL texture object;
    objects of this class are meant to be saved as a memoized dict value with the filename being the dict key
    """
    #e so far, no param choices, keep only one version, no mgmt, no scaling...

    __metaclass__ = ExprsMeta #e or could use ConstantComputeMethodMixin I think

    def __init__(self, tex_key):
        self.filename, self.pil_kws_items = tex_key # have to put sorted items tuple in key, since dict itself is unhashable
        self.pil_kws = dict(self.pil_kws_items)
        if 1: #e could remove when works, but don't really need to
            items = self.pil_kws.items()
            items.sort()
            assert tuple(items) == self.pil_kws_items
        # pil_kws added 061127, doc in nEImageOps;
        #   current defaults are ideal_width = None, ideal_height = None, rescale = True, convert = False
        # everything else can be computed on-demand (image object, texture name, texture, etc)
        #e no provision yet for file contents changing; when there is, update policy or uniqid might need to be part of tex_key
        #e more options? maybe, but by default, get those from queries, store an optimal set of shared versions [nim]

    def _C__image(self):
        """
        define self._image -- create a PIL Image object (enclosed in an neImageOps container) from the file, and return it
        """
        return texture_helpers.create_PIL_image_obj_from_image_file(self.filename, **self.pil_kws)
            # (trivial glue function into ImageUtils.py class nEImageOps -- return nEImageOps(image_file, **kws))

    def _C_tex_name(self):
        """
        define self.tex_name -- allocate a texture name
        """
        # code copied from texture_helpers.loadTexture (even though we call it, below, for its other code):
        tex_name = glGenTextures(1)
        if debug_glGenTextures and seen_before(('debug_glGenTextures', self.filename)):
            #070313 using env.seen_before (rename env module (cad/src) -> global_env? for now, basic imports seen_before via py_utils.)
            #k I'm not sure if, after certain reloads, I should expect to routinely see this message as textures get reloaded. 070313
            print "debug fyi: same filename seen before, in glGenTextures -> %r for %r" % (tex_name, self)
        # note: by experiment (iMac G5 Panther), this returns a single number (1L, 2L, ...), not a list or tuple,
        # but for an argument >1 it returns a list of longs. We depend on this behavior here. [bruce 060207]
        tex_name = int(tex_name) # make sure it worked as expected
        assert tex_name != 0
        return tex_name

    def _C_loaded_texture_data(self):
        """
        define self.loaded_texture_data = (have_mipmaps, tex_name),
        which stands for the side effect of guaranteeing the texture is loaded
        (but not necessarily currently bound)
        """
        image_obj = self._image
        tex_name = self.tex_name
        assert tex_name, "tex_name should have been allocated and should not be 0 or false or None, but is %r" % (tex_name,)#070308
        have_mipmaps, tex_name = texture_helpers.loadTexture(image_obj, tex_name)
            ##testexpr_11n = imagetest("stopsign.png") # fails; guess, our code doesn't support enough in-file image formats;
            ##    # exception is SystemError: unknown raw mode, [images.py:73] [testdraw.py:663] [ImageUtils.py:69] [Image.py:439] [Image.py:323]
            ##    ##e need to improve gracefulness of response to this error
        glBindTexture(GL_TEXTURE_2D, 0)
            # make sure no caller depends on mere accessing of self.loaded_texture_data binding this texture,
            # which without this precaution would happen "by accident" (as side effect of loadTexture)
            # whenever self.loaded_texture_data ran this recompute method, _C_loaded_texture_data
        assert tex_name == self.tex_name
        return have_mipmaps, tex_name

    def bind_texture(self, clamp = False, use_mipmaps = True, decal = False, pixmap = False):
        """
        bind our texture, and set texture-related GL params as specified.

        Anything that calls this should eventually call
        self.kluge_reset_texture_mode_to_work_around_renderText_bug(),
        but only after all drawing using the texture is done.
        """
        # Notes [some of this belongs in docstring]:
        #e - we might want to pass these tex params as one chunk, or a flags word
        #e - we might want to optim for when they don't change
        # - most of them have default values like the old code had implicitly, but not pixmap, which old code had as implicitly true
        # - pixmap is misnamed, it doesn't use the pixmap ops, tho we might like to use those from the same image data someday

        have_mipmaps, tex_name = self.loaded_texture_data
        ## texture_helpers.setup_to_draw_texture_name(have_mipmaps, tex_name)
        # let's inline that instead, including its call of _initTextureEnv, and then modify it [061126]

        glBindTexture(GL_TEXTURE_2D, tex_name)

        # modified from _initTextureEnv(have_mipmaps) in texture_helpers.py
        if clamp:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        else:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        if not pixmap:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            if have_mipmaps and use_mipmaps:
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            else:
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        else:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        if decal:
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        else:
            # see red book p410-411 -- can use GL_DECAL, GL_REPLACE, GL_MODULATE, GL_BLEND, GL_ADD, GL_COMBINE.
            # (Except that I can't import GL_COMBINE (iMac G5) so maybe it's not always available.)
            # GL_DECAL leaves fragment alpha unchanged and uses texture alpha to mix its color with fragment color
            # (fragment data comes from the polygon's alpha & color as if drawn untextured).
            # GL_REPLACE just discards fragment data in favor of texture data incl alpha -- that would be a better default.
            # [later 070404: now it is the default.]
            # Eventually permit all these values -- for now just let decal = False mean GL_REPLACE. [070403]
            #
            ## print "getTextureData", self, self._image.getTextureData() # presence of correct alpha is plausible from this
            # (in testexpr_11pd2). By itself, it does make a difference (alpha 0 places are black in testexpr_11pd2, not blue
            # (probably a leaked color) like in testexpr_11pd1), but self.blend is also needed to make it translucent.
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

        return

    def kluge_reset_texture_mode_to_work_around_renderText_bug(self, glpane): #bruce 081205
        glpane.kluge_reset_texture_mode_to_work_around_renderText_bug()
        return

    def __repr__(self): #070308
        try:
            basename = os.path.basename(self.filename) #070312
        except:
            basename = self.filename
        return "<%s at %#x for %r, %r>" % (self.__class__.__name__, id(self), basename, self.pil_kws)

    pass # end of class _texture_holder

# ==

texture_holder_for_filename = MemoDict(_texture_holder)
    ###e should canonicalize the filename -- as another optional argfunc to MemoDict
    #doc: now texture_holder_for_filename[filename] is our memoized _texture_holder for a given filename.
    # note [added 061215]: no need to use LvalDict2, since _texture_holder never needs recomputing for a given filename
    # (and uses no usage-tracked values).

# ==

DEBUG_IMAGE_SEARCH = False

def canon_image_filename( filename):
    """
    Figure out (or guess) the right absolute pathname for loading the given image file into OpenGL.

    @warning: the answer depends on what files are found on your disk, so it might differ for different users!

    [Note: It's not yet clear whether that's merely a development kluge, or a feature, or some of each;
     someday there might even be user prefs for image search paths, except that plugins can provide their own images.... ##e]
    """
    orig_filename = filename # for debug prints or warnings
##    #stub, might work for now:
##    thisdir = os.path.dirname(__file__) # dir of exprs module
##    CAD_SRC_PATH = os.path.dirname( thisdir)
    from utilities.constants import CAD_SRC_PATH
        # [note: in a built Mac release, this might be Contents/Resources/Python/site-packages.zip, or
        #  a related pathname; see comments near its definition.]
    cad = os.path.dirname( CAD_SRC_PATH) # used below for cad/images

    # image file path extensively revised 070604, mainly so testmode can work in a built release package
    from platform_dependent.PlatformDependent import path_of_Nanorex_subdir

    # main exprs-package image directory
    cad_src_ui_exprs = os.path.join( image_directory(), "ui/exprs") # not necessarily really in cad/src (in a built release)

    # list of dirs in which to search for filename (#e could precompute; doesn't matter much)
    path = [
        # first, search in a user-controlled dir, so they can override UI image files
        # (if those are accessed using the exprs module).
        path_of_Nanorex_subdir("UI"),

        # next, let the code specify the name exactly, relative to cad_src_ui_exprs
        cad_src_ui_exprs,

        # next, to support older code in this exprs package,
        # let it leave out the subdir component if it's one of these:
        os.path.join( cad_src_ui_exprs, "text" ),
        os.path.join( cad_src_ui_exprs, "widgets" ),
        os.path.join( cad_src_ui_exprs, "textures" ),
        os.path.join( cad_src_ui_exprs, "test" ),

        # next, permit access to anything in image_directory()
        # using the same relative path (starting with "ui/")
        # as typical code in cad/src does (e.g. when calling geticon)
        # (this means we could rewrite geticon to call this routine,
        #  if we wanted it to be user-overridable someday #e)
        image_directory(),

        # for experimental things, let developers refer to things in cad/src/experimental --
        # I guess they can do that using the image_directory() entry (which for developers is .../cad/src)
        # by using filenames starting with "experimental", which is not a big restriction
        # given that we're not doing this early enough to override built-in images
        # (so, no path entry needed for that)

        # we no longer support the old experimental/textures directory
##        os.path.join( CAD_SRC_PATH, "experimental/textures"), # [not supported by autoBuild.py, and never will be]

        # but we do still support the obsolete cad/images dir, since some test code uses it
        # and it was still present in cvs (I think -- at least it's in my checkouts) as of 070604.
        os.path.join( cad, "images"),
    ]
    tries = map( lambda dir: os.path.join(dir, filename), path)
    lastresort = courierfile
        #e replace with some error-indicator image, or make one with the missing filename as text (on demand, or too slow)
    ## tries.append(lastresort)
    tries.append(-1)
    for filename in tries:
        if filename == -1:
            filename = lastresort
            if 'too important to not tell all users for now' or debug_flags.atom_debug:
                print "bug: image file %r not found, using last-resort image file %r" % (orig_filename, lastresort) ###
        filename = os.path.abspath(os.path.normpath(filename)) # faster to do this on demand
        if os.path.isfile(filename):
            if DEBUG_IMAGE_SEARCH:
                print "                found:",filename
            return filename
        if DEBUG_IMAGE_SEARCH:
            print "didn't find:", filename
    assert 0, "lastresort file %r should always be present" % os.path.abspath(os.path.normpath(lastresort))
    pass # end of canon_image_filename

class Image(Widget2D):
    """
    Image(filename, size = Rect(2)) draws a rectangular textured image based on the given image file,
    using the same size and position in model space as the lbox of an instance of self.size
    (a Widget2D, usually a Rect, Rect(2) by default, i.e. about 30 pixels square in home view).
       It uses an OpenGL texture size (resolution) given by options ideal_width and ideal_height
    [#e which need renaming, making into one option, and other improvements; see code comments for details].
       [It doesn't yet work in POV-Ray but it ought to someday. #e]
       The other options are not fully documented here, and need improvements in design and sometimes in implem,
    but are summarized here:
       Options that affect how the file gets loaded into a PIL Image include rescale, convert, _tmpmode [#doc these],
    as well as the texture size options mentioned.
    (The PIL Image object is available as self._image even if our OpenGL texture is not used. [#doc more details?]
    [###WRONG or REVIEW -- isn't it the nEImageOps object which has that name??])
       Options that affect how the texture gets made from the loaded image include... none yet, I think. Someday
    we'll want make_mipmaps (with filtering options for its use) and probably others. [###k need to verify none are used for this]

    @warning: variations in the above options (between instances, or over time [if that's implemented -- untested,
              unsure ##k]) cause both a new OpenGL texture to be created, and (even if it would not be necessarily in a smarter
              implem [i think] -- but the lack of image->texture options makes this academic for now) a new PIL Image to be created
              from the image file on disk.

       Options that affect how the texture is drawn (in any instance, at any moment) include:
    clamp, pixmap [#e misnamed], use_mipmaps, decal, tex_origin, nreps [#doc these].
    [#e More options of this kind are needed.]
    All the texture-drawing options can be varied, either in different instances or over time in one instance
    (by passing them as formulae), without causing a new texture or PIL Image to be loaded as they vary.

    @warning: the image is not visible from the back by default,
              which is only ok for some uses, such as 2D widgets
              or solid-object faces or decals. Use two_sided = True
              to make it visible from both sides.
    """
    ##e about options ideal_width and ideal_height:
    #e should be a single option, resolution or tex_size, number or pair, or smth to pick size based on image native size
    #e should let you specify an image subrect too, or more generally an expr to compute the image -- or this can be part of one...
    # note we do have tex_origin and nreps
    #
    #e size option is misnamed since it also controls position -- maybe give it another name
    # like where, place, footprint, lbox, box? none of those good enough.
    # Also we need a way to change the size but preserve the natural aspect ratio.
    # One way: let size and tex_size both be passed easily as formulas of native image size.
    # The main new thing that requires is an abbreviation for _this(Image), e.g. _my. [note: _my is now implemented, 061205]

    # args
    filename = Arg(str)
    use_filename = call_Expr( canon_image_filename, filename)
    # named options -- clamp = False, use_mipmaps = True, decal = False, pixmap = False [redundant with defaults in bind_texture]
    clamp = Option(bool, False) # clamp or (default) repeat
    pixmap = Option(bool, False) #e misnamed -- whether to use GL_NEAREST filtering
    use_mipmaps = Option(bool, True) # whether to use mipmaps, if present in loaded texture object; only matters if pixmap is False
        #e what determines whether mipmaps are present? For now, they always are;
        # later, it might depend on whether we had RAM, or on a more global pref, or ....
    decal = Option(bool, False, doc = "combine texture with color using GL_DECAL? (by default, use GL_REPLACE)")
        # as of 070403, False works and means GL_REPLACE
        # 070404 changing default to False; not sure if this can affect blend = false cases -- maybe yes beyond edges? ###UNTESTED
        #e should probably rename this and change it from a bool to a choice or to more bools
        # (since it has 5 or 6 possible values; see code comments)
    blend = Option(bool, False, doc = "whether to blend translucent images with background") #070403
        # Note: blend doesn't turn off depth buffer writing, but does reject fully transparent fragments (via GL_ALPHA_TEST),
        # so only the translucent (i.e. partly transparent) pixels can obscure things if drawn first,
        # or can be hover-highlighted (affect sbar_text, act as drag-grip-point, etc).
        # This behavior is fine if translucency is used for antialiased edges.
        # (Except for images that have very small nonzero alphas that really ought to be zero instead,
        #  like the one used in testexpr_11pd3 (fyi, see screenshot 'alpha fluctuations.jpg', not in cvs) --
        #  maybe this comes in through the rescaling and/or mipmap filtering?)
        # See also slightly related glStencilFunc, glDepthFunc.
    alpha_test = Option(bool, _self.blend,
                        doc = "whether to use GL_ALPHA_TEST (by default, use it when blend option is true)" ) #070404
        # this is effectively an option to not use GL_ALPHA_TEST when blend is True (as we'd normally do then)

    two_sided = Option(bool, False, doc = "whether to disable GL_CULL_FACE so that both sides get drawn") #080223

    ###e should add option to turn off depth buffer writing -- see warning below

    ###e should add option to turn off color buffer writing -- glColorMask -- see warning below
    # see also disable_color (widget2d.py, maybe move to GLPane.py?)

        # [or find a more modular way to control things like that -- wrappers? std options?]

    ### WARNING: hard to disable those correctly (re restoring state)
    # if we ever get drawn in a larger thing that disables one of them -- as we might,
    #  due to selobj highlighting! ###k CHECK THIS for other new disables too, alpha and blend...

    nreps = Option(float, 1.0) #e rename - repeat count; mostly only useful when clamp is False, but ought to work otherwise too
        ##e generalize to let caller supply tex_dx and tex_dy vectors, for rotating the texture within the drawing region;
        # (Can that be done as a more general value for this option? Unclear whether that's natural, tho passing in a matrix might be...)
    tex_origin = Option(Vector, ORIGIN) # offset option, to shift tex_origin; can be 2d or 3d, though we use only two dims of it
        #e design Qs:
        # - is it really Point rather than Vector?
        # - does it interact with [nim] drawing-region-origin so as to line up if we use the same one for adjacent regions?
    size = Option(Widget2D, Rect(2)) ##e also permit number or pair, ie args to Rect also should be ok # [experiment 061130]
    shape = Option(Anything, None,
                   doc = """shape name ('upper-left-half' or 'lower-right-half'),
                           or sequence of 3 2d points (intrinsic coords, CCW),
                           to draw only a sub-triangle of the textured rect image""" )
    ###e also permit shape option to specify polygon, not just triangle, or, any geometry-drawing expr
    # (see comments in helper function for more on that)
    # (has design issues re tex/model coord correspondence [tho current scheme is well-defined and might be best for many uses],
    #  and possible embedded textured parts)

    bleft = size.bleft
    bright = size.bright
    bbottom = size.bbottom
    btop = size.btop

    # more options, which affect initial image loading from file, thus are part of the texture-cache key [061127]
    rescale = Option(bool, True) # whether to resize by rescaling or padding (default might be changed after testing #e)
    ideal_width = Option(int, 256) ###e let them be a func of image size, as a pair? (eg so they can be next greater 2pow?) someday.
    ideal_height = Option(int, 256)
    convert = Option(bool, False) #061128, whether to convert image to DESIRED_MODE RGBX.
        ### NOTE: type bool is wrong, since later [but long before 070404] it became able to let you specify another mode,
        # and in that case it also affects getTextureData retval mode. This is now routinely used for transparent texture images.
    _tmpmode = Option(str, None) #k None is not str, is that ok? #doc [might be temp kluge]

    #e these are not fully implem -- at best, when rescale = False, you'll see black padding when drawing;
    # what we need to do is pass a reduced tex coord so you don't. I hope the image (not padding) will be at the lower left corner
    # of what's drawn. [as of 061127 1022p] [it's not -- this is commented on elsewhere and explained, probably in ImageUtils.py]

    # formulae
    # THIS SHOULD WORK (I think), but doesn't, don't know why ####BUG: [is my syntax wrong for passing the kws to call_Expr???]
    ## texture_options = call_Expr( dict, clamp = clamp, pixmap = pixmap, use_mipmaps = use_mipmaps, decal = decal )
    ## __get__ is nim in the Expr <type 'dict'>(*(), **{'clamp': <call_Expr#5175: .....

    def _C__texture_holder(self):
        # pil_kws added 061127, doc in nEImageOps;
        # current defaults are ideal_width = None, ideal_height = None, rescale = True, convert = False, _tmpmode = None.
        # Note: don't include texture_options here, since they don't affect the PIL image object itself.
        pil_kws = dict(rescale = self.rescale, ideal_width = self.ideal_width, ideal_height = self.ideal_height,
                       convert = self.convert, _tmpmode = self._tmpmode)
        items = pil_kws.items()
        items.sort()
        pil_kws_items = tuple(items) # make that dict hashable
        tex_key = (self.use_filename, pil_kws_items) # must be compatible with the single arg to _texture_holder.__init__
        return texture_holder_for_filename[tex_key] # this shared global MemoDict is defined above
    _image = _self._texture_holder._image

    def bind_texture(self, **kws):
        """
        bind our texture (and set other GL params needed to draw with it).

        Anything that calls this should eventually call
        self.kluge_reset_texture_mode_to_work_around_renderText_bug(),
        but only after all drawing using the texture is done.
        """
        self._texture_holder.bind_texture(**kws)

    def kluge_reset_texture_mode_to_work_around_renderText_bug(self):
        """
        This needs to be called after calling self.bind_texture,
        but only after drawing using the texture is done.
        """
        self._texture_holder.kluge_reset_texture_mode_to_work_around_renderText_bug( self.env.glpane)

    def draw(self):
        # bind texture for image filename [#e or other image object],
        # doing whatever is needed of allocating texture name, loading image object, loading texture data;
        ###e optim: don't call glBindTexture if it's already bound, and/or have a "raw draw" which assumes it's already bound
        if 'workaround bug in formula for texture_options':
            texture_options = dict(clamp = self.clamp, pixmap = self.pixmap, use_mipmaps = self.use_mipmaps, decal = self.decal)
        else:
            texture_options = self.texture_options # never used, but desired once bug is fixed
        self.bind_texture( **texture_options)

        try:

            # figure out texture coords (from optional args, not yet defined ###e) -- stub for now
            nreps = float(self.nreps) # float won't be needed once we have type coercion; not analyzed whether int vs float matters in subr
            ## tex_origin = ORIGIN2 # see also testdraw's drawtest1, still used in testmode to draw whole font texture rect
            tex_origin = V(self.tex_origin[0], self.tex_origin[1])
            ## tex_dx = D2X ; tex_dx *= nreps # this modifies a shared, mutable Numeric array object, namely D2X! Not what I wanted.
            tex_dx = D2X * nreps
            tex_dy = D2Y * nreps

            # where to draw it -- act like a 2D Rect for now, determined by self's lbox,
            # which presently comes from self.size
            origin = V(-self.bleft, -self.bbottom, 0)
                # see also the code in drawfont2 which tweaks the drawing position to improve the pixel alignment
                # (in a way which won't work right inside a display list if any translation occurred before now in that display list)
                # in case we want to offer that option here someday [070124 comment]
    ##        dx = DX * self.bright
    ##        dy = DY * self.btop
            dx = DX * (self.bleft + self.bright) # bugfix 070304: include bleft, bbottom here
            dy = DY * (self.bbottom + self.btop)

            blend = self.blend
            alpha_test = self.alpha_test
            two_sided = self.two_sided
            shape = self.shape # for now, None or a symbolic string (choices are hardcoded below)

            if blend:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            if alpha_test:
                glEnable(GL_ALPHA_TEST) # (red book p.462-463)
                glAlphaFunc(GL_GREATER, 0.0) # don't draw the fully transparent parts into the depth or stencil buffers
                    ##e maybe let that 0.0 be an option? eg the value of alpha_test itself? Right now, it can be False ~== 0 (not None).
            if two_sided:
                glDisable(GL_CULL_FACE)

            if not shape:
                draw_textured_rect( origin, dx, dy, tex_origin, tex_dx, tex_dy)
            else:
                # support sub-shapes of the image rect, but with unchanged texture coords relative to the whole rect [070404 ###UNTESTED]
                if type(shape) == type(""):
                    ##e use an external shape name->value mapping?
                    # in fact, should such a mapping be part of the dynamic graphics-instance env (self.env)??
                    if shape == 'upper-left-half':
                        shape = ((0,0), (1,1), (0,1))
                    elif shape == 'lower-right-half':
                        shape = ((0,0), (1,0), (1,1))
                    elif shape == 'upper-right-half': #070628
                        shape = ((0,1), (1,0), (1,1))
                    elif shape == 'lower-left-half': #070628; untested
                        shape = ((0,0), (1,0), (0,1))
                    else:
                        assert 0, "in %r, don't know this shape name: %r" % (self, shape)
                # otherwise assume it might be the right form to pass directly
                # (list of 3 2d points in [0,1] x [0,1] relative coords -- might need to be in CCW winding order)
                draw_textured_rect_subtriangle( origin, dx, dy, tex_origin, tex_dx, tex_dy,
                                                shape )
                pass
            if blend:
                glDisable(GL_BLEND)
            if alpha_test:
                glDisable(GL_ALPHA_TEST)
            if two_sided:
                glEnable(GL_CULL_FACE)
        finally:
            self.kluge_reset_texture_mode_to_work_around_renderText_bug()
        return # from Image.draw

    # note the suboptimal error message from this mistake:
    #   bright = DX * 2
    #   ## TypeError: only rank-0 arrays can be converted to Python scalars. ...
    #   ## [test.py:419 inst.draw()] [Column.py:91 glTranslatef(dx,0,0)]
    #e Ideally we'd have a typecheck on _self.bright (etc) in Widget2D
    # which would catch this error whenever self.bright was computed,
    # or even better, when it's a constant for the class (as in this case),
    # right when that constant formula is defined.

    pass # end of class Image

# ==

IconImage = Image(ideal_width = 22, ideal_height = 22, convert = True, _tmpmode = 'TIFF',
                  doc = "be the best way to use Image for an NE1 icon"  # (informal docstring option 070124 -- not used, just there)
            )
    # WARNING: size 22 MIGHT FAIL on some OpenGL drivers (which require texture dims to be powers of 2);
    # when that happens (or in any case, before a serious release), we'll need to ask OpenGL if it has that limitation
    # and implement this differently if it does.
    #
    # Intent of IconImage is just "be the best way to use Image for an NE1 icon",
    # so it might change in transparency behavior once we work that out inside Image,
    # and we'll hopefully not keep needing that _tmpmode kluge, etc.

# ==

class NativeImage(DelegatingInstanceOrExpr): #070304 [works (imperfectly? see comments there) in testexpr_11u6]
    """
    Show an image in its native size and aspect ratio --
    that is, one image pixel == one texture pixel == one screen pixel,
    when the local coordsys is the standard viewing coordsys.
       Note: callers are advised to enclose this inside Highlightable, at least until
    we add local glnames to fix the bug of all bareMotion over non-Highlightable drawing
    causing redraws.
    """
    # args
    filename = Arg(str, "x") #e better type, eg Filename?
    ###BUG: ought to take all options and pass them on to Image [070403 comment]
    # formulae [non-public in spite of the names]
    im1_expr = Image(filename, use_mipmaps = True, ideal_width = -1, ideal_height = -1)
        # customize Image to use native texture size (but without controlling the aspect ratio for display)
        ###e consider also including the options that IconImage does, or options passed by caller
        # (but passing general opts (like python **kws syntax can do) is nim in the exprs language)
    im1 = Instance(im1_expr) # grab an actual image so we can find out its native size
    th = im1._texture_holder # gets its _texture_holder object
    imops = th._image # get its nEImageOps object
    # appearance
    delegate = im1_expr(size = Center(Rect(imops.orig_width * PIXELS, imops.orig_height * PIXELS)))
        # (implem note: this customizes im1_expr options even though its args (filename) are already supplied.
        #  That used to give a warning but apparently doesn't now. If it does again someday,
        #  it's easy to fix here -- just give filename in each instantation rather than in im1_expr.)
    pass

# ===

# for grabbing pixels, e.g. for visual tests of correctness, live vs saved image

#e put in its own file? yes.

#e search for "visual regression test framework" for ideas on that in comment below; refile them into PixelTester.py ##e

class PixelGrabber(InstanceOrExpr, DelegatingMixin):#e draft, API needs revision to provide more control over when to save, button-compatible
    """
    Act like our first argument, but after the first(??) draw call,
    save an image of the rendered pixels into the file named by arg2.
    """
    ### issues:
    # - gluProject implem only works if we're not inside a display list; this is not checked for
    # - image might be cluttered with things like the origin axis. Maybe turn these off when using?
    #   + It turns out this doesn't happen since those haven't been drawn yet! (or so it seems -- not fully confirmed)
    #   - ###e redefine it to clear the color & depth buffers in its footprint, before drawing?
    # - no guarantee our pixel footprint is a pixel rect on screen. Might want to force this, or check for it?
    #   Until then, use in home view.
    #   (Or outside of the model's modelview matrix, once testmode intercepts render loop.)
    #   + so far it's been a perfect rect, even tho i'm in perspective view. This makes sense in theory for a nonrotated view.
    # - only works if everything we draw actually appears on the glpane -- not outside its boundaries, not obscured beforehand
    # - it saves it on *every* draw call. [Maybe even those for glselect -- might cause bugs, not well tested ###k]
    #   Maybe it ought to save when content changes? (Not yet detected.)
    #   Really, better to have a "save button", but does that have to be provided in same class? If not, how is shared state named?#e
    ###e one possibility, sounds good: [see also PixelTester.py]
    # - separate method on the instance to save image;
    #   - draw call just saves some helper info like lbox mousepoints;
    #   - using env has to know how to call that method;
    # - convenience macro adds a button to do it, and a saved-image viewer,
    #   and this becomes part of our desired "visual regression test framework",
    #   which overall lets us select any test, see its code, rerun it, resave it, see saved image (maybe plus older ones),
    #   do a "flicker test" where we switch between saved and current (recaptured?) image in one place as we toggle mousebutton,
    #   maybe even show a computed "difference image",
    #   and (makes it easier for us to) commit these images into cvs or other archive
    delegate = Arg(Widget2D)
    filename = Arg(str, "/tmp/PixelGrabber-test.jpg") # default value is just for debugging convenience, but can stay, it's useful
    def draw(self):
        self.drawkid( self.delegate) ## self.delegate.draw()
        self.save() #e shouldn't call so often -- see big comment above
    def save(self):
        glFlush() ##k needed? don't know; works with it. Or try glFinish? not sure it's legal here. Not needed, never tried.
        glpane = self.env.glpane
        image = glpane.grabFrameBuffer() # not sure this is legal during the draw... but it seems to work
            # This is a QGLWidget method. Does it have args? only withalpha, not size (no way to only grab a subimage directly).
            # It returns a QImage.
            # See also QGLWidget::renderPixmap (sounds easy to mess up, so not tried).
            # Or we could use OpenGL to grab raw data (as we now do from depth buffer), then use PIL (or QImage) to output it...
            # maybe best in long run, but grabFrameBuffer works ok for now. #e
            #
            # Note: Return value is a constants.qt.QImage object; for debug prints including dir(image), see cvs rev 1.8
            #e optim: use GL calls instead -- but that optim won't matter once we stop this from happening on every draw call
        ## print "glpane dims",glpane.width, glpane.height
            # on bruce's g4 now, whole glpane dims 633 573 (plausible; same as image dims); on g5, 690 637, also same in image
        assert glpane.width == image.width()
        assert glpane.height == image.height()
        # figure out where the image of self lies in this image of the entire glpane (in a rect defined by GL window coords x0,x1, y0,y1)
        #### WARNING: this method only works if we're not inside a display list
        thing = self.delegate
        lbox_corners = [(x,y) for x in (-thing.bleft, thing.bright) for y in (-thing.bbottom, thing.btop)]
            # Note, these are in local model coords, with implicit z = 0, NOT pixels.
            #bugfix 061127 133p: those minus signs -- I forgot them, and it took hours to debug this, since in simple examples
            # the affected attrs are 0. Does this indicate a design flaw in the lbox attr meanings? Guess: maybe --
            # it might affect a lot of code, and be worse in some code like Column. Maybe we just need a default lbox_rect formula
            # which includes the proper signs. ###e
        points = [gluProject(x,y,0) for x,y in lbox_corners] # each point is x,y,depth, with x,y in OpenGL GLPane-window coords
        ## print "raw points are",points
            # this shows they are a list of 4 triples, are fractional, and are perfectly rectangular (since view not rotated).

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)

        ###e could warn if the points are not a rectangle, i.e. if self is drawn in a rotated view
        # add pixelmargin, but limit by window size (glpane.width, glpane.height)
        # (the reason is to verify this grabs bgcolor from around the image; not sure it will, if pixel coords are pixel-centers)
        pixelmargin = 2 + 0.5 #e make 2 an option, so more easily usable for display of saved images too
            # note: if original points are pixel centers, then 0.5 of this serves to turn them into pixel boundaries,
            # but then we'd also want to round them, differently for low and high values,
            # so to do that, add 1 to high values before int()

            ### REVIEW: should we use intRound to avoid issue of int() rounding towards zero
            # even for negative coordinates (for which adding 0.5 has the wrong effect)? [bruce 080521 Q]

        x0 -= pixelmargin
        x0 = int(x0)
        if x0 < 0: x0 = 0

        y0 -= pixelmargin
        y0 = int(y0)
        if y0 < 0: y0 = 0

        x1 += pixelmargin + 1 # 1 is for rounding (see comment)
        x1 = int(x1)
        if x1 > glpane.width:
            x1 = glpane.width ###k need -1?? are these pixels or pixel-boundaries?? assume boundaries, see comment above

        y1 += pixelmargin + 1
        y1 = int(y1)
        if y1 > glpane.height:
            y1 = glpane.height

        # convert to Qt window coords [note: the other code that does this doesn't use -1 either]
        y0 = glpane.height - y0
        y1 = glpane.height - y1
        y0, y1 = y1, y0

        w = x1-x0
        h = y1-y0
        ## print "subimage dims",w,h

        assert x0 <= x1, "need x0 <= x1, got x0 = %r, x1 = %r" % (x0,x1)
        assert y0 <= y1, "need y0 <= y1, got y0 = %r, y1 = %r" % (y0,y1)

        # trim image, i.e. replace it with a subimage which only shows self.delegate
        image = image.copy(x0, y0, w, h)
            # QImage::copy ( int x, int y, int w, int h, int conversion_flags = 0 ) -- copy a subarea, return a new image

        filename = self.filename
        try:
            os.remove(filename)
        except OSError: # file doesn't exist
            pass
        image.save(filename, "JPEG", 85) #e 85->100 for testing, or use "quality" option; option for filetype, or split into helper...
            #e also possible: image.save(filename, "PNG")
            ##e probably better: "If format is omitted, the format is determined from the filename extension, if possible."
            # (Note that's about image.img.save -- not sure it also applies yet to image.save itself.
            #  It's in http://www.pythonware.com/library/pil/handbook/image.htm .)
            # But I'd need to read up about how the option should be given for other formats.
        if os.path.isfile(filename):
            print "saved image, %d x %d:" % (w,h), filename
        else:
            print "save image (%d x %d) didn't work:" % (w,h), filename
        return
    pass # end of class PixelGrabber

# end
