# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ImageUtils.py

Image utilities.

$Id$

History: 

050930. Split off image utilities from drawer.py into this file. Mark

"""

__author__ = "Huaicai"

def getPowerOfTwo(num):
    '''Returns the nearest number for <num> that's a power of 2.'''
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
    

def getTextureData(fileName):
    '''Given a image filename, this returns the RGB values (required by OpenGL) of the image 
    to be texture mapped on a polygon.
    '''
    
    try:
        import Image  # #This is from the PIL library
        ideal_wd = 256; ideal_ht = 256
        
        img = Image.open(fileName)
        width = img.size[0]
        height = img.size[1]
        
        if not (width, height) == (ideal_wd, ideal_ht):
           import os
           from platform import find_or_make_Nanorex_subdir
           nhdir = find_or_make_Nanorex_subdir("Nano-Hive")
         
           nImg = img.resize((ideal_wd, ideal_ht), Image.BICUBIC)        

           #Without saving/openning, 'tostring()' is not working right.
           newName = os.path.join(nhdir, 'new_'+os.path.basename(fileName))
           nImg.save(newName)
           nImg = Image.open(newName)
           
           width = nImg.size[0]
           height = nImg.size[1]
           rst = nImg.tostring("raw", "RGBX", 0, -1)
           print "image size: ", width, height
           return width, height, rst, nImg
        else:
           rst = img.tostring("raw", "RGBX", 0, -1)
           return width, height, rst, img

    except ImportError:
        print "The Python Image Libary doesn't exsit, we'll try to use QImage, which has more limited quality and capacity."
        
        from qt import QImage, QColor
    
        img = QImage(fileName)
        
        width = img.width()
        height = img.height()
        
        ideal_wd = getPowerOfTwo(width); ideal_ht = getPowerOfTwo(height)
        print "image size: ", width, height
        print "ideal size: ", ideal_wd, ideal_ht
        
        if width != ideal_wd or height != ideal_ht:
            img = img.smoothScale(ideal_wd, ideal_ht)
            width = img.width()
            height = img.height()
        
            print "new image size: ", width, height
        
        from array import array
        tData = array('B')
        #for ii in range(ideal_ht):
            #for jj in range(ideal_wd):
                
        # This rotates 90 degree anti-clockwise compared to the above.
        for ii in range(ideal_wd-1, 0, -1): 
            for jj in range(ideal_ht):
                c = img.pixel(jj, ii)
                color = QColor(c)
                tData.extend(array('B', [color.red(), color.green(), color.blue(), 255]))
        
        return height, width, tData.tostring()    
        