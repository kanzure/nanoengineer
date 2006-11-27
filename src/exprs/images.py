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

from basic import * # including ExprsMeta
from basic import _self

from draw_utils import ORIGIN2, D2X, D2Y, ORIGIN, DX, DY, draw_textured_rect

import testdraw #e we'll call some funcs from this, and copy & modify others into this file;
    ##e at some point we'll need to clean up the proper source file of our helper functions from testdraw...
    # when the time comes, the only reliable way to sort out duplicated code is to search for all
    # uses of the GL calls being used here.

from OpenGL.GL import glGenTextures, glBindTexture, GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, \
     GL_CLAMP, GL_REPEAT, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER, GL_LINEAR, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST, \
     GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL, glTexParameterf, glTexEnvf

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
        # code copied from testdraw._loadTexture (even though we call it, below, for its other code):
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
            ##testexpr_11n = imagetest("stopsign.png") # fails; guess, our code doesn't support enough in-file image formats;
            ##    # exception is SystemError: unknown raw mode, [images.py:73] [testdraw.py:663] [ImageUtils.py:69] [Image.py:439] [Image.py:323]
            ##    ##e need to improve gracefulness of response to this error
        glBindTexture(GL_TEXTURE_2D, 0)
            # make sure no caller depends on mere accessing of self.loaded_texture_data binding this texture,
            # which without this precaution would happen "by accident" (as side effect of _loadTexture)
            # whenever self.loaded_texture_data ran this recompute method, _C_loaded_texture_data
        assert tex_name == self.tex_name
        return have_mipmaps, tex_name
    def bind_texture(self, clamp = False, use_mipmaps = True, decal = True, pixmap = False):
        "bind our texture, and set texture-related GL params as specified"
        # Notes [some of this belongs in docstring]:
        #e - we might want to pass these tex params as one chunk, or a flags word
        #e - we might want to optim for when they don't change
        # - most of them have default values like the old code had implicitly, but not pixmap, which old code had as implicitly true
        # - pixmap is misnamed, it doesn't use the pixmap ops, tho we might like to use those from the same image data someday
        # implem: pixmap is for NEAREST

        ###@@@ where i am is here 061126 1140a; caller doesn't pass options
        
        have_mipmaps, tex_name = self.loaded_texture_data
        ## testdraw.setup_to_draw_texture_name(have_mipmaps, tex_name)
        # let's inline that instead, including its call of _initTextureEnv, and then modify it [done, untested] [061126]

        glBindTexture(GL_TEXTURE_2D, tex_name)
        
        # modified from _initTextureEnv(have_mipmaps) in testdraw.py
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
            print "don't know what to set instead of GL_DECAL"###e
        
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
    thisdir = os.path.dirname(__file__) # dir of exprs module
    cad_src = os.path.dirname( thisdir)
    cad = os.path.dirname( cad_src)
    path = [ #e could precompute; doesn't matter much
        thisdir,
        os.path.join( cad_src, "experimental/textures"),
        os.path.join( cad, "images"), #e still correct??
    ]
    tries = map( lambda dir: os.path.join(dir, filename), path)
    lastresort = testdraw.courierfile
        #e replace with some error-indicator image, or make one with the missing filename as text (on demand, or too slow)
    tries.append(lastresort)
    for filename in tries:
        filename = os.path.abspath(os.path.normpath(filename)) # faster to do this on demand
        if os.path.isfile(filename):
            return filename
    assert 0, "lastresort file %r should always be present" % os.path.abspath(os.path.normpath(tries[-1]))
    pass # end of canon_image_filename

class Image(Widget2D):
    "#doc; WARNING: invisible from the back"
    # args
    filename = Arg(str)
    use_filename = call_Expr( canon_image_filename, filename)
    ###e the following argnames get warned about -- not sure if that means they're bad, but avoid issue for now since they're nim
##    width = Arg(Width, 0) # is this in image pixels or screen pixels? hmm... are those in 1-1 corr at cov? ###k
##    height = Arg(Width, 0)
    # named options -- clamp = False, use_mipmaps = True, decal = True, pixmap = False [redundant with defaults in bind_texture]
    clamp = Option(bool, False) # clamp or (default) repeat
    pixmap = Option(bool, False) #e misnamed -- whether to use GL_NEAREST filtering
    use_mipmaps = Option(bool, True) # whether to use mipmaps, if present in loaded texture object; only matters if pixmap is False
        #e what determines whether mipmaps are present? For now, they always are;
        # later, it might depend on whether we had RAM, or on a more global pref, or ....
    decal = Option(bool, True) #e False is nim
    nreps = Option(float, 1.0) #e rename - repeat count; mostly only useful when clamp is False, but ought to work otherwise too
        ##e generalize to let caller supply tex_dx and tex_dy vectors, for rotating the texture within the drawing region;
        # (Can that be done as a more general value for this option? Unclear whether that's natural, tho passing in a matrix might be...)
    tex_origin = Option(Vector, ORIGIN) # offset option, to shift tex_origin; can be 2d or 3d, though we use only two dims of it
        #e design Qs:
        # - is it really Point rather than Vector?
        # - does it interact with [nim] drawing-region-origin so as to line up if we use the same one for adjacent regions?
    
    # formulae
    # THIS SHOULD WORK (I think), but doesn't, don't know why ####BUG: [is my syntax wrong for passing the kws to call_Expr???]
    ## texture_options = call_Expr( dict, clamp = clamp, pixmap = pixmap, use_mipmaps = use_mipmaps, decal = decal )
    ## __get__ is nim in the Expr <type 'dict'>(*(), **{'clamp': <call_Expr#5175: .....
    
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

    def bind_texture(self, **kws):
        "bind our texture (and set other GL params needed to draw with it)"
        self._texture_holder.bind_texture(**kws)
    
    def draw(self):
        # bind texture for image filename [#e or other image object],
        # doing whatever is needed of allocating texture name, loading image object, loading texture data;
        ###e optim: don't call glBindTexture if it's already bound, and/or have a "raw draw" which assumes it's already bound
        if 'workaround bug in formula for texture_options':
            texture_options = dict(clamp = self.clamp, pixmap = self.pixmap, use_mipmaps = self.use_mipmaps, decal = self.decal)
        else:
            texture_options = self.texture_options # never used, but desired once bug is fixed
        self.bind_texture( **texture_options)
        
        # figure out texture coords (from optional args, not yet defined ###e) -- stub for now
        nreps = float(self.nreps) # float won't be needed once we have type coercion; not analyzed whether int vs float matters in subr
        ## tex_origin = ORIGIN2 # see also testdraw's drawtest1, still used in testmode to draw whole font texture rect
        tex_origin = V(self.tex_origin[0], self.tex_origin[1])
        ## tex_dx = D2X ; tex_dx *= nreps # this modifies a shared, mutable Numeric array object, namely D2X! Not what I wanted.
        tex_dx = D2X * nreps
        tex_dy = D2Y * nreps
        
        # where to draw it -- act like a 2D Rect for now; this code is copied from testdraw's drawtest1, not reanalyzed; fixed size 2x2,
        # roughly 30 pixels square in home view i think
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
    pass # end of class Image

# ==

# for grabbing pixels, e.g. for visual tests of correctness, live vs saved image

if 0: # eg code, ops_files.py, comments added here
    # jpg
        image = glpane.grabFrameBuffer()
            # Evidently this is a Qt method, not our own! Does it have args? only withalpha, not size.
            # Presumably it returns a QImage. I suppose I could grab a subimage from that somehow.
            # See also QGLWidget::renderPixmap (sounds easy to mess up).
            # Or we could use OpenGL to grab raw data (as we now do from depth buffer), then use PIL to output it...
            # probably best in long run. #e
        image.save(safile, "JPEG", 85)
    # elif ext == ".png":
        type = "PNG"
        image = glpane.grabFrameBuffer()
        image.save(safile, "PNG")

from OpenGL.GL import glFlush, glFinish

class PixelGrabber(Widget2D, DelegatingMixin): #e draft, API needs revision to provide more control over when to save, button-compatible
    """Act like our first argument, but after the first(??) draw call,
    save an image of the rendered pixels into the file named by arg2.
    """
    ###BUGS:
    # - image might be cluttered with things like the origin axis. Maybe turn these off when using?
    # - no guarantee our pixel footprint is a pixel rect on screen. Might want to force this?
    #   Until then, use in home view, maybe ortho.
    #   (Or outside of the model's modelview matrix, once testmode intercepts render loop.)
    # - it saves it on *every* draw call. Maybe it ought to save when content changes? (Not yet detected.)
    #   really, better to have a "save button", but does that have to be provided in same class? If not, how is shared state named?#e
    ###e one possibility, sounds good:
    # - separate method on the instance to save image;
    #   - draw call just saves some helper info like lbox mousepoints;
    #   - using env has to know how to call that method;
    # - convenience macro adds a button to do it, and a saved-image viewer,
    #   and this becomes part of our desired "visual regression test framework",
    #   which overall lets us select any test, see its code, rerun it, resave it, see saved image (maybe plus older ones),
    #   and (makes it easier for us to) commit these images into cvs or other archive
    delegate = Arg(Widget2D)
    filename = Arg(str) # assume absolute
    def draw(self):
        self.delegate.draw()
        self.save()
    def save(self):
        glFlush() ##k needed? don't know; works with it. Or try glFinish? not sure it's legal here. Not needed, never tried.
        glpane = self.env.glpane
        image = glpane.grabFrameBuffer() # not sure this is legal during the draw... but it seems to work
            #e optim: use GL calls instead -- won't matter once we stop this from happening every time
        ## print "image %r has type %r and dir %r" % (image, type(image), dir(image))
            ## image <constants.qt.QImage object at 0xf1dc690> has type <class 'constants.qt.QImage'>
            ## and dir ['BigEndian', 'IgnoreEndian', 'LittleEndian', 'ScaleFree', 'ScaleMax', 'ScaleMin',
            ##'__class__', '__delattr__', '__doc__', '__getattribute__', '__hash__', '__init__', '__module__',
            ##'__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__str__', '__weakref__',
            ##'allGray', 'bitOrder', 'bits', 'bytesPerLine', 'color', 'colorTable', 'convertBitOrder',
            ##'convertDepth', 'copy', 'create', 'createAlphaMask', 'createHeuristicMask', 'depth', 'detach',
            ##'dotsPerMeterX', 'dotsPerMeterY', 'fill', 'fromMimeSource', 'hasAlphaBuffer', 'height', 'imageFormat',
            ##'inputFormatList', 'inputFormats', 'invertPixels', 'isGrayscale', 'isNull', 'jumpTable', 'load',
            ##'loadFromData', 'mirror', 'numBytes', 'numColors', 'offset', 'outputFormatList', 'outputFormats',
            ##'pixel', 'pixelIndex', 'rect', 'reset', 'save', 'scale', 'scaleHeight', 'scaleWidth', 'scanLine',
            ##'setAlphaBuffer', 'setColor', 'setDotsPerMeterX', 'setDotsPerMeterY', 'setNumColors', 'setOffset',
            ##'setPixel', 'setText', 'size', 'smoothScale', 'swapRGB', 'systemBitOrder', 'systemByteOrder', 'text',
            ##'textKeys', 'textLanguages', 'textList', 'valid', 'width', 'xForm']
        print "image dims",image.width(),image.height() # on bruce's g4 now, 633 573, whole glpane (plausible, same as glpane dims below)
        print "glpane dims",glpane.width, glpane.height
        ###e figure out where self lies in this image -- inverse mousepoints... i have some code for that somewhere; gluProject?
        #e add a 1 or 2 pixel margin to verify this grabs bgcolor, not sure it will if pixel coords are pixel-centers
        ###e trim image
            # e.g. QImage::copy ( int x, int y, int w, int h, int conversion_flags = 0 ) -- copy a subarea, return a new image
        filename = self.filename
        try:
            os.remove(filename)
        except OSError: # file doesn't exist
            pass
        image.save(filename, "JPEG", 85) #e 85->100 for testing, or use "quality" option; option for filetype, or split into helper...
        if os.path.isfile(filename):
            print "saved:",filename # can be false positive i
        else:
            print "save didn't work:",filename
        return
    pass

# end
