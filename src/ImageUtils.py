# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
ImageUtils.py - Image utilities based on PIL.
(Some doc of PIL can be found at http://www.pythonware.com/library/pil/handbook .)

$Id$

History: 

050930. Split off image utilities from drawer.py into this file. Mark

061127 some new features and docstrings by bruce

"""

__author__ = "Huaicai"

import Image   # This is from the PIL library
import ImageOps
import PngImagePlugin # Don't remove this, it is used by package creator to find right modules to support PNG image -- Huaicai

import platform #bruce 061127

class nEImageOps:
    '''Common image operations like, get rgb data, flip, mirror, rotation, filter, resize, etc. '''
    ## ideal_wd = ideal_ht = 256
    # note: bruce 061127 renamed these to ideal_width, ideal_height, as public self attrs and __init__ options
    
    def __init__(self, imageName, ideal_width = None, ideal_height = None, rescale = True):
        #bruce 061127 added options, self attrs, docstring; some are marked [untested] in docstring [###k need to test them];
        ##e add options for resize filter choice, whether to use im.convert (experimental, nim), img mode to use for data (now RGBX)
        """Create an nEImageOps object that holds a PIL image made from the given image filename, imageName.
        Not all file formats are supported; the file extension is not enough to know if the file is supported,
        since it also depends on the nature of the internal data (which is probably a bug that could be fixed).
           The image will be resized on demand by getTextureData (but in place in this mutable object,
        thus affecting all subsequent queries too, not only queries via getTextureData),
        to ideal_width, ideal_height, specified as options [untested], or if they're not supplied, by a debug_pref "image size",
        or by direct modification by client of self.ideal_width and self.ideal_height before this resizing is first done.
        (Callers which want no resizing to occur currently need to explicitly set self.ideal_width and self.ideal_height
        to the actual image size (before first calling getTextureData), which can be determined as explained below.
        Note that this API is basically a kluge, and ought to be cleaned up sometime. ##e)
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
        self.imageName = imageName
        self.img = Image.open(imageName)
        self.orig_width = self.img.size[0] #bruce 061127
        self.orig_height = self.img.size[1] #bruce 061127
        if platform.atom_debug:
            #bruce 061127; fyi, see also string in this file containing RGB
            print "debug fyi: nEImageOps.__init__: %r.img.size, mode is %r, %r" % (self, self.img.size, self.img.mode) ###
        if 1:
            #bruce 060213 - let debug pref set default values of ideal_width, ideal_height
            from debug_prefs import debug_pref, Choice
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
        return "<%s at %#x for %r>" % (self.__class__.__name__, id(self), self.imageName) #e add size & mode? use basename only?
    
    def getPowerOfTwo(self, num): # [never reviewed by bruce]
        '''Returns the nearest number for <num> that's a power of 2. Currently, it's not used.'''
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
        """Returns (width, height, data), where data contains the RGB values (required by OpenGL) of the image 
        to be texture mapped onto a polygon. If self.rescale is false and if both image dims need to expand,
        the rgb pixels include padding which is outside the original image. Otherwise (including if one dim
        needs to expand and one to shrink), the image is stretched/shrunk to fit in each dim independently.
        """
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
            rst = self.img.tostring("raw", "RGBX", 0, -1)
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
        """Resize image and filter it (or pad it if self.rescale is false and neither dimension needs to shrink)."""
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
                    if platform.atom_debug:
                        print "debug fyi: %r.resize is rescaling, tho asked not to, since a dim must shrink" % self #e more info
                self.img = self.img.resize( (wd, ht), filter)
            else:
                # new feature, bruce 061127, only works when width and height needn't shrink:
                # make new image, then use im.paste(image, box)
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
                    # in fact, it ends up drawn into the upper left... hmm... guess: tostring args 0, -1 are reversing it for OpenGL;
                    # so would I rather correct that here (move it to upper left), or when I get tex coords for drawing it?? ##e decide
                newimg.paste(img, box) ###k does this do some filtering too? visually it looks like it might have.
                self.img = newimg
            self.update()

    def update(self):
        '''Update the image object.'''
        #Without saving/openning, 'tostring()' is not working right.
        # [bruce guess 061127 about the cause: maybe related to ops that don't work before or after image is loaded.
        #  The docs mentioned elsewhere are not very clear about this.] 
        import os
        from platform import find_or_make_Nanorex_subdir
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        newName = os.path.join(nhdir, 'temp_'+os.path.basename(self.imageName))
        oldmode = self.img.mode #bruce 061127
        self.img.save(newName)
        self.img = Image.open(newName)
        newmode = self.img.mode
        if oldmode != newmode and platform.atom_debug: #k does this ever happen??
            print "debug warning: oldmode != newmode (%r != %r) in %r.update" % (oldmode, newmode, self)
        #e could set actual-size attrs here
        
    def flip(self):
        self.img = ImageOps.flip(self.img)
        self.update()
            
    def mirror(self):
        self.img = ImageOps.mirror(self.img)
        self.update()

    def rotate(self, deg):
        '''Rotate CCW <deg> degrees around center of the current image. '''
        self.img = self.img.rotate(deg)
        self.update()
            
    pass # end of class nEImageOps

# end
