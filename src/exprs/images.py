"""
images.py - provide some image-displaying utilities and primitives

$Id$

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

#e needs cvs add

from basic import * # including ExprsMeta
from basic import _self

from draw_utils import ORIGIN2, D2X, D2Y, ORIGIN, DX, DY, draw_textured_rect

import testdraw #e we'll call some funcs from this, and copy & modify others into this file;
    ##e at some point we'll need to clean up the proper source file of our helper functions from testdraw...
    # when the time comes, the only reliable way to sort out duplicated code is to search for all
    # uses of the GL calls being used here.

from OpenGL.GL import glGenTextures, glBindTexture, GL_TEXTURE_2D

def ensure_courierfile_loaded_EXAMPLE_COPIED_FROM_TESTDRAW(): #e rename to reflect binding too
    "load font-texture if we edited the params for that in this function, or didn't load it yet; bind it for drawing"
    tex_filename = courierfile ## "xxx.png" # the charset
    "courierfile"
    tex_data = (tex_filename,)
    if vv.tex_name == 0 or vv.tex_data != tex_data:
        vv.have_mipmaps, vv.tex_name = load_image_into_new_texture_name( tex_filename, vv.tex_name)
        vv.tex_data = tex_data
    else:
        pass # assume those vars are fine from last time
    setup_to_draw_texture_name(vv.have_mipmaps, vv.tex_name)
    return

class _texture_holder(object): ### WARNING: probably assumes square textures for now, or rescales to create them; maybe even fixed size?
    """From a filename, create on demand, and cache, a PIL Image object and an optional OpenGL texture object;
    objects of this class are meant to be saved as a memoized dict value with the filename being the dict key
    """
    #e so far, no param choices, keep only one version, no mgmt, no scaling...
    __metaclass__ = ExprsMeta #e or could use SimpleComputeMethodMixin(sp?) I think
    def __init__(self, filename):
        #e and some options? maybe, but by default, get those from queries, store an optimal set of shared versions
        self.filename = filename
        # everything else can be computed on-demand (image object, texture name, texture, etc)
        #e no provision yet for file contents changing
    def _C__image(self):
        "define self._image -- create a PIL Image object from the file, and return it"
        return testdraw._create_PIL_image_obj_from_image_file(self.filename) # note: that's a trivial glue function into ImageUtils.py
    def _C_tex_name(self):
        "define self.tex_name -- allocate a texture name"
        # code copied from testdraw._loadTexture
        tex_name = glGenTextures(1)
        # note: by experiment (iMac G5 Panther), this returns a single number (1L, 2L, ...), not a list or tuple,
        # but for an argument >1 it returns a list of longs. We depend on this behavior here. [bruce 060207]
        tex_name = int(tex_name) # make sure it worked as expected
        assert tex_name != 0
        return tex_name
    def _C_loaded_texture_data(self):
        """define self.loaded_texture_data = (have_mipmaps, tex_name),
        which stands for the side effect of guaranteeing the texture is loaded
        (but not necessarily currently bound)
        """
        image_obj = self._image
        tex_name = self.tex_name
        have_mipmaps, tex_name = testdraw._loadTexture(image_obj, tex_name)
        glBindTexture(GL_TEXTURE_2D, 0)
            # make sure no caller depends on mere accessing of self.loaded_texture_data binding this texture,
            # which without this precaution would happen "by accident" (as side effect of _loadTexture)
            # whenever self.loaded_texture_data ran this recompute method, _C_loaded_texture_data
        assert tex_name == self.tex_name
        return have_mipmaps, tex_name
    def bind_texture(self):
        "bind our texture (and set other GL params needed to draw with it)"
        have_mipmaps, tex_name = self.loaded_texture_data
        testdraw.setup_to_draw_texture_name(have_mipmaps, tex_name) ###e we'll need control over the params this sets up
        return
    pass # end of class _texture_holder

# ==

texture_holder_for_filename = MemoDict(_texture_holder) ###e should canonicalize the filename -- as another optional argfunc to MemoDict
    #doc: now texture_holder_for_filename[filename] is our memoized _texture_holder for a given filename

# ==

def canon_image_filename( filename):
    """Figure out (or guess) the right absolute pathname for loading the given image file into OpenGL.
    WARNING: the answer depends on what files are found on your disk, so it might differ for different users!
    [Note: It's not yet clear whether that's merely a development kluge, or a feature, or some of each;
     someday there might even be user prefs for image search paths, except that plugins can provide their own images.... ##e]
    """
    #stub, might work for now:
    return os.path.join( os.path.dirname( os.path.dirname(__file__)), "experimental/textures", filename)

class Image(Widget2D):
    "#doc; WARNING: invisible from the back"
    # args
    filename = Arg(str)
    use_filename = call_Expr( canon_image_filename, filename)
    ###e the following argnames get warned about -- not sure if that means they're bad, but avoid issue for now since they're nim
##    width = Arg(Width, 0) # is this in image pixels or screen pixels? hmm... are those in 1-1 corr at cov? ###k
##    height = Arg(Width, 0)
    ###e named options
    # formulae
    ## _image = PIL_Image(use_filename) ###e should share with other instances of same filename
    def _C__texture_holder(self):
        return texture_holder_for_filename[self.use_filename] # this shared global MemoDict is defined above
    _image = _self._texture_holder._image
##    _width = _image.width
##    _height = _image.height

    # legit but args not yet defined
##    use_width = width or _image.width
##    use_height = height or _image.height ###e should do this differently -- try to preserve aspect ratio
    ##e these are not yet used

    def bind_texture(self):
        "bind our texture (and set other GL params needed to draw with it)"
        self._texture_holder.bind_texture()
    
    def draw(self):
        # bind texture for image filename [#e or other image object],
        # doing whatever is needed of allocating texture name, loading image object, loading texture data;
        ###e optim: don't call glBindTexture if it's already bound, and/or have a "raw draw" which assumes it's already bound
        self.bind_texture()
        
        # figure out texture coords (from optional args, not yet defined ###e) -- stub for now
        tex_origin, tex_dx, tex_dy = ORIGIN2, D2X, D2Y # copied from testdraw's drawtest1, still used in testmode to draw whole font
        ##e set tex coord clamping, mipmap/filter mode, etc, from params (for now, we have no choice about them)

        # where to draw it -- act like a 2D Rect for now; this code is copied from testdraw's drawtest1, not reanalyzed
        origin = ORIGIN
        dx = DX * 2
        dy = DY * 2
        draw_textured_rect(origin, dx, dy, tex_origin, tex_dx, tex_dy)
        return

    ##e need lbox attrs
    # note the suboptimal error message from this mistake:
    #   bright = DX * 2
    #   ## TypeError: only rank-0 arrays can be converted to Python scalars. ...
    #   ## [test.py:419 inst.draw()] [Column.py:91 glTranslatef(dx,0,0)]
    #e Ideally we'd have a typecheck on _self.bright (etc) in Widget2D
    # which would catch this error whenever self.bright was computed,
    # or even better, when it's a constant for the class (as in this case),
    # right when that constant formula is defined.
    bright = 1 * 2 # corresponds to DX * 2 above
    btop = 1 * 2

    ###k???
    pass

# end
