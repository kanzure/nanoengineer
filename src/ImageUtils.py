# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
ImageUtils.py

Image utilities.

$Id$

History: 

050930. Split off image utilities from drawer.py into this file. Mark

"""

__author__ = "Huaicai"

import Image   #This is from the PIL library
import ImageOps
import PngImagePlugin #Don't remove this, it is used by package creator to find right modules to support PNG image--Huaicai
           
           
class nEImageOps:
    '''Common image operations like, get rgb data, flip, mirror, rotation, filter, resize, etc. '''
    ideal_wd = ideal_ht = 256
    
    def __init__(self, imageName):
        self.imageName = imageName
        self.img = Image.open(imageName)
        if 1:
            #bruce 060213
            from debug_prefs import debug_pref, Choice
            self.ideal_wd = self.ideal_ht = debug_pref("image size", Choice([256,128,64,32,512,1024]),
                prefs_key = 'A8 devel/image size' ) #bruce 060612 made this persistent
            # these are not used until client code calls getTextureData;
            # it's ok if client modifies them directly before that,
            # anything from just once to before each call of getTextureData.
        return
        
    def getPowerOfTwo(self, num):
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
        
    
    def getTextureData(self):        
        '''Given a image filename, this returns the RGB values (required by OpenGL) of the image 
        to be texture mapped on a polygon.
        '''
        self.resize(self.ideal_wd, self.ideal_ht)
            #k This is often called repeatedly; is it fast when size is already as requested?
            # I guess it is, since it's our own method! (See below.) [bruce 060212 comment]
        
        width = self.img.size[0]
        height = self.img.size[1]
        rst = self.img.tostring("raw", "RGBX", 0, -1)
        #print "image size: ", width, height
        return width, height, rst
     

    def resize(self, wd, ht, filter=Image.BICUBIC):
        '''Resize image and filter it. '''
        width = self.img.size[0]
        height = self.img.size[1]
            
        if not (width, height) == (self.ideal_wd, self.ideal_ht):
           self.img = self.img.resize((self.ideal_wd, self.ideal_ht), filter)
           self.update()


    def update(self):
        '''Update the image object.'''
        #Without saving/openning, 'tostring()' is not working right.
        import os
        from platform import find_or_make_Nanorex_subdir
        nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
        newName = os.path.join(nhdir, 'temp_'+os.path.basename(self.imageName))
        self.img.save(newName)
        self.img = Image.open(newName)
     
        
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
            
