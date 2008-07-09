# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
ImageUtils.py - Image utilities based on PIL.
(Some doc of PIL can be found at http://www.pythonware.com/library/pil/handbook .)

@author: Huaicai
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.


History: 

050930. Split off image utilities from drawer.py into this file. Mark

061127 some new features and docstrings by bruce

"""

import Image   # This is from the PIL library
import ImageOps
import PngImagePlugin # Don't remove this, it is used by package creator to find right modules to support PNG image -- Huaicai

# try to tell pylint we need to import PngImagePlugin [bruce 071023]
PngImagePlugin

from utilities import debug_flags #bruce 061127
from utilities.debug import print_compact_traceback #bruce 061128

class nEImageOps:
    """
    Common image operations, such as get rgb data, flip, mirror,
    rotate, filter, resize, etc.

    Initialized from a filename readable by PIL.
    """
    ## ideal_wd = ideal_ht = 256
    # note: bruce 061127 renamed these to ideal_width, ideal_height, as public self attrs and __init__ options

    DESIRED_MODE = "RGBX" #bruce 061128 split this out
    
    def __init__(self, imageName,
                 ideal_width = None, ideal_height = None,
                 rescale = True, ##e filter = ...
                 convert = False,
                 _tmpmode = None,
                 _debug = False):
        #bruce 061127 added options, self attrs, docstring; some are marked [untested] in docstring [###k need to test them];
        ##e add options for resize filter choice, whether to use im.convert (experimental, nim), img mode to use for data (now RGBX)
        """
        Create an nEImageOps object that holds a PIL image made from the given image filename, imageName.
        Not all file formats are supported; the file extension is not enough to know if the file is supported,
        since it also depends on the nature of the internal data (which is probably a bug that could be fixed).
        [#doc the convert option, which tries to address that [not fully tested], and the _tmpmode option.]
           The image will be resized on demand by getTextureData (but in place in this mutable object,
        thus affecting all subsequent queries too, not only queries via getTextureData),
        to ideal_width, ideal_height, specified as options, or if they're not supplied, by a debug_pref "image size",
        or by direct modification by client of self.ideal_width and self.ideal_height before this resizing is first done.
        (Callers which want no resizing to occur currently need to explicitly set self.ideal_width and self.ideal_height
        to the actual image size (before first calling getTextureData), which can be determined as explained below.
        Or, as of 'kluge070304', they can pass -1 for ideal_width and/or ideal_height to make them equal that dim of the native size.
        Note that this entire API is basically a kluge, and ought to be cleaned up sometime. ##e)
           For many OpenGL drivers, if the image will be used as texture data, these sizes need to be powers of two.
           The resizing will be done by rescaling, by default, or by padding on top and right if rescale = False.
           The original dimensions can be found in self.orig_width and self.orig_height [untested];
        these never change after first reading the file (even when we internally reread the file in self.update,
        to work around bugs).
           The current dimensions can be found by knowing that width = self.img.size[0] and height = self.img.size[1].
        If getTextureData has been called, these presumably equal the ideal dims, but I [bruce] don't know if this is always true.
           The PIL image object is stored in the semi-public attribute self.img, but this object often replaces that image
        with a new one, with altered data and/or size, either due to resizing for getTextureData, or to external calls of
        one of several image-modifying methods.
        """
        self.debug = _debug #bruce 061204
        self.imageName = imageName
        self.convert = convert
        self._tmpmode = _tmpmode #bruce 061128, probably temporary, needs doc if not; JPG illegal, JPEG doesn't work, TIFF works well
        self.img = Image.open(imageName)
        self.unconverted_img = self.img # for debugging, and in case keeping the python reference is needed
        if self.convert: #bruce 061128
            # im.convert(mode) => image
            if type(self.convert) == type(""):
                mode = self.convert # let caller specify mode to convert to
                # Q: should this also affect getTextureData retval? if so, also reset self.DESIRED_MODE here. A: yes.
                #e [or maybe have a separate option, desired_mode or mode or convert_to? Guess: someday have that,
                # and the convert flag will go away since it will always be true, BUT the desired mode will be
                # a function of the original mode! (just as that will be the case with the desired size.)]
                if mode != self.DESIRED_MODE:
                    # as of circa 070403 this happens routinely for convert = 'RGBA', and seems harmless...
                    # if DESIRED_MODE was cleaned up as suggested above it'd probably be a historical relic;
                    # so remove the debug print. [bruce 070404]
                    ## print "%r: warning: convert = mode %r is not yet fully supported" % (self, self.convert)
                    self.DESIRED_MODE = mode
            else:
                assert self.convert == True or self.convert == 1
                mode = self.DESIRED_MODE
            old_data = self.img.size, self.img.mode
            self.img = self.img.convert(mode) #k does it matter whether we do this before or after resizing it?
            new_data = self.img.size, self.img.mode
            if old_data != new_data and debug_flags.atom_debug and self.debug:
                print "debug: %r: fyi: image converted from %r to %r" % (self, old_data, new_data)
                ###e also need self.update() in this case?? if so, better do it later during __init__.
            pass
        self.orig_width = self.img.size[0] #bruce 061127
        self.orig_height = self.img.size[1] #bruce 061127
        if debug_flags.atom_debug and self.debug:
            #bruce 061127; fyi, see also string in this file containing RGB
            print "debug fyi: nEImageOps.__init__: %r.img.size, mode is %r, %r" % (self, self.img.size, self.img.mode) ###
        if 1:
            #bruce 060213 - let debug pref set default values of ideal_width, ideal_height
            from utilities.debug_prefs import debug_pref, Choice
            self.ideal_width = self.ideal_height = debug_pref("image size", Choice([256,128,64,32,512,1024]),
                prefs_key = 'A8 devel/image size' ) #bruce 060612 made this persistent
            # these are not used until client code calls getTextureData;
            # it's ok if client modifies them directly before that,
            # anything from just once to before each call of getTextureData.
        if 1:
            #bruce 061127 - let caller override those values, and other behavior, using options
            if ideal_width is not None:
                self.ideal_width = ideal_width
            if ideal_height is not None:
                self.ideal_height = ideal_height
            self.rescale = rescale
        return

    def __repr__(self): #bruce 061127
        #e add size & mode? if so, make sure it works in __init__ before self.img has been set!
        return "<%s at %#x for %r>" % (self.__class__.__name__, id(self), self.imageName) #e use basename only?
    
    def getPowerOfTwo(self, num): # [never reviewed by bruce]
        """
        Returns the nearest number for <num> that's a power of 2. Currently, it's not used.
        """
        assert(type(num) == type(1))
        a = 0
        
        # This proves that a large image may crash the program. This value works on my machine.   H.
        maxValue = 256
        
        oNum = num
        while num>1:
           num = num>>1
           a += 1
        
        s = min(1<<a, maxValue) ; b = min(1<<(a+1), maxValue)
        
        if (oNum-s) > (b-oNum):
            return b
        else: return s
    
    def getTextureData(self): #bruce 061127 revised API, implem and docstring
        """
        Returns (width, height, data), where data contains the RGB values (required by OpenGL) of the image 
        to be texture mapped onto a polygon. If self.rescale is false and if both image dims need to expand,
        the rgb pixels include padding which is outside the original image. Otherwise (including if one dim
        needs to expand and one to shrink), the image is stretched/shrunk to fit in each dim independently.
        """
        if 'kluge070304':
            #bruce 070304 API kluge [works]:
            # permit -1 in ideal_width to indicate "use native width", and same for ideal_height.
            # (Note: it's difficult for an exprs.images.Image client to do the same without this kluge,
            #  since orig_width is not available when ideal_width must be passed. It could do it by making one image,
            #  examining it, then making another, though -- a bit inefficiently since two textures would be created.)
            if self.ideal_width == -1:
                self.ideal_width = self.orig_width
            if self.ideal_height == -1:
                self.ideal_height = self.orig_height
        ##e try using im.convert here... or as a new resize arg... or maybe in __init__
        self.resize(self.ideal_width, self.ideal_height) # behavior depends on self.rescale
            # Notes:
            # - This is often called repeatedly; good thing it's fast
            #   when size is already as requested (i.e. on all but the first call).
            # - self.resize used to ignore its arguments, but the same values given here were hardcoded internally. Fixed now.
            # [bruce 060212/061127 comments]
        width = self.img.size[0]
        height = self.img.size[1]
        try:
            rst = self.img.tostring("raw", self.DESIRED_MODE, 0, -1)
            # Note: this line can raise the exception "SystemError: unknown raw mode" for certain image files.
            # Maybe this could be fixed by using "im.convert(mode) => image" when loading the image??
            ##e try it, see above for where [bruce 061127 comment]
        except:
            #bruce 061127
            print "fyi: following exception relates to %r with mode %r" % (self.img, self.img.mode)
                #e also self.img.info? not sure if huge.
            raise
        #print "image size: ", width, height
        return width, height, rst

    def resize(self, wd, ht, filter = Image.BICUBIC): #e should self.rescale also come in as an arg?
        """
        Resize image and filter it (or pad it if self.rescale is false and neither dimension needs to shrink).
        """
        #e sometime try Image.ANTIALIAS to see if it's better quality; there are also faster choices.
        # For doc, see http://www.pythonware.com/library/pil/handbook/image.htm .
        # It says "Note that the bilinear and bicubic filters in the current version of PIL are not well-suited
        # for thumbnail generation. You should use ANTIALIAS unless speed is much more important than quality."
        #
        # Note: the arguments wd and ht were not used until bruce 061127 redefined this method to use them.
        # Before that, it acted as if self.ideal_width, self.ideal_height were always passed (as they in fact were).
        width = self.img.size[0]
        height = self.img.size[1]
            
        if (width, height) != (wd, ht): # actual != desired
            if self.rescale or wd < width or ht < height: # have to rescale if either dim needs to shrink
                # we will rescale.
                if not self.rescale:
                    # print debug warning that it can't do as asked
                    if debug_flags.atom_debug and self.debug:
                        print "debug fyi: %r.resize is rescaling, tho asked not to, since a dim must shrink" % self #e more info
                self.img = self.img.resize( (wd, ht), filter)
                    # supported filters, says doc:
                        ##The filter argument can be one of NEAREST (use nearest neighbour), BILINEAR
                        ##(linear interpolation in a 2x2 environment), BICUBIC (cubic spline
                        ##interpolation in a 4x4 environment), or ANTIALIAS (a high-quality
                        ##downsampling filter). If omitted, or if the image has mode "1" or "P", it is
                        ##set to NEAREST.
                    #e see also im.filter(filter) => image, which supports more filters. Maybe add it to our ops like flip & rotate?
            else:
                # new feature, bruce 061127, only works when width and height needn't shrink:
                # make new image, then use im.paste(image, box, [mask])
                # "Image.new(mode, size) => image"
                img = self.img
                mode = img.mode #e or could alter this to convert it at the same time, says the doc
                size = (wd,ht)
                newimg = Image.new(mode, size) # "If the colour argument is omitted, the image is filled with black."
                # From the PIL docs:
                # "im.paste(image, box) pastes another image into this image. The box argument is either a 2-tuple
                #  giving the upper left corner, a 4-tuple defining the left, upper, right, and lower pixel coordinate,
                #  or None (same as (0, 0)). If a 4-tuple is given, the size of the pasted image must match the size of the region.
                #  If the modes don't match, the pasted image is converted to the mode of this image...."
                box = (0,0) # try this, even though I'm not sure upper left for PIL will be lower left for OpenGL, as I hope it will #k
                    # in fact, it ends up drawn into the upper left... hmm... guess: tostring args 0, -1 are reversing it for OpenGL
                    # (apparently confirmed by doc of PIL decoders);
                    # so would I rather correct that here (move it to upper left), or when I get tex coords for drawing it?? ##e decide
                if 'A' in mode: ###k??
                    # experiment, bruce 061128:
                    ##e might need to cause alpha of newimg to start out as 0 -- not sure what's done with it... we want to copy it
                    # from what we paste, let it be 0 elsewhere.
                    newimg.paste(img, box, img) # im.paste(image, box, mask)
                        # motivation: doc says "Note that if you paste an "RGBA" image, the alpha band is ignored.
                        # You can work around this by using the same image as both source image and mask."
                else:
                    newimg.paste(img, box)
                        ###k does this do some filtering too? visually it looks like it might have. Doc doesn't say it does.
                self.img = newimg
            try:
                self.update()
                # Note: an exception in self.update() will abort a current call of e.g. getTextureData,
                # but won't prevent the next call from working, since the modified image was already stored in self before this call.
                # That may mean it would make more sense to catch the exception here or inside update, complain, then discard it.
                # Doing that now. [bruce 061128]
            except:
                print_compact_traceback("bug: exception (ignored) in %r.update(): " % self)
            pass
        return

    def update(self):
        """
        Update the image object.
        """
        # Without saving/opening, 'tostring()' is not working right.
        # [bruce guess 061127 about the cause: maybe related to ops that don't
        #  work before or after image is loaded. The docs mentioned elsewhere
        #  are not very clear about this.] 
        import os
        from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        basename = os.path.basename(self.imageName)
        if self._tmpmode:
            # change file extension of tmp file to correspond with the format we'll store in it
            # [this is not needed (I think) except to not fool people who stumble upon the temporary file]
            basename, extjunk = os.path.splitext(basename)
            basename = "%s.%s" % (basename, self._tmpmode)
        newName = os.path.join(nhdir, 'temp_' + basename)
            ###e change file extension to one that always supports self.DESIRED_MODE? (or specify it in save command)
        oldmode = self.img.mode #bruce 061127
        if self._tmpmode:
            self.img.save(newName, self._tmpmode) #bruce 061128 experimental, hopefully a temporary kluge
        else:
            self.img.save(newName)
            # if we use self.convert to convert PNG RGBA to RGBX, this can raise an exception:
            ## IOError: cannot write mode RGBX as PNG
        self.img = Image.open(newName)
        newmode = self.img.mode
        if oldmode != newmode and debug_flags.atom_debug and self.debug: #k does this ever happen??
            print "debug warning: oldmode != newmode (%r != %r) in %r.update" % (oldmode, newmode, self)
        #e could set actual-size attrs here
        
    def flip(self):
        self.img = ImageOps.flip(self.img)
        self.update()
            
    def mirror(self):
        self.img = ImageOps.mirror(self.img)
        self.update()

    def rotate(self, deg):
        """
        Rotate CCW <deg> degrees around center of the current image.
        """
        self.img = self.img.rotate(deg)
        self.update()
            
    pass # end of class nEImageOps

# end
