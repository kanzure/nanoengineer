# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
icon_utilities.py - helper functions for finding icon and pixmap files
in standard places.

$Id$

History: developed by several authors; moved out of Utility.py
by bruce 070831.

WARNING: most code still imports these functions from Utility.py.
This should be cleaned up when practical.
"""

import os, sys
import platform
from PyQt4 import QtGui

# utility function: global cache for QPixmaps (needed by most Node subclasses)

_pixmap_image_path = None
_pixmaps = {}
_icons = {}

_iconprefix = os.path.dirname(os.path.abspath(sys.argv[0]))
_iconprefix = os.sep.join(_iconprefix.split(os.sep)[:-1] + ["src"])

def image_directory(): #bruce 070604
    """Return the full pathname of the directory in which the image files
    (mostly icons) with names like ui/<subdir>/<file> exist.
       Note: As of 070604, for developers this path ends with cad/src
    and is also the main source directory, but in built releases it
    might be something different and might be platform-dependent or even
    build-system-dependent.
    """
    return _iconprefix

def geticon(name, _iconprefix = _iconprefix):
    """
    Return the QIcon for the given image path name. 
    @param name: The image path name provided by the user. the path should start 
           with 'ui/' directory inside the src directory.
    @type  name: str
    
    @param _iconPrefix: The directory path to be prepended to the pixmap filepath
    @param _iconPrefix: str
    
    @return: QIcon object for the given image path.
    @rtype:  QIcon object. 
    """
  
    root, ext = os.path.splitext(name)
    if not ext:
        name = name + '.png'
    
    iconPath = os.path.join(_iconprefix, name)
    iconPath = os.path.normpath(iconPath)      
    
    if not os.path.exists(iconPath):
        if platform.atom_debug:
            print "icon path %s doesn't exist." %(iconPath)
    
    #Always set the icon with the 'iconPath'. Don't set it as an empty string 
    #like done in getPixmap. This is done on purpose. Right now there is an 
    #apparent bug in Qt in the text alignment for a push button with style sheet. 
    #@see L{PM_GroupBox._getTitleButton} which sets a non-existant 
    #'Ghost Icon' for this button using 'geticon method'
    # By setting such  icon, the button text left aligns! If you create an icon 
    #with iconPath = empty string (when the user supplied path doesn't exist) 
    #the text in that title button center aligns. So lets just always use the 
    #'iconPath' even when the path doesn't exist. -- ninad 2007-08-22
    
    icon = QtGui.QIcon(iconPath)
            
    return icon

def getpixmap(name, _iconprefix = _iconprefix):
    """
    Return the QPixmap for the given image path name. 
    @param name: The image path name provided by the user. the path should start 
           with 'ui/' directory inside the src directory.
    @type  name: str
    
    @param _iconPrefix: The directory path to be prepended to the pixmap filepath
    @param _iconPrefix: str
    
    @return: QPixmap object for the given image path. (could return a Null icon)
    @rtype:  QPixmap object.
    """
    root, ext = os.path.splitext(name)
    if not ext:
        name = name + '.png'
        
    pixmapPath = os.path.join(_iconprefix, name)
    pixmapPath = os.path.normpath(pixmapPath)
    
    if os.path.exists(pixmapPath):
        pixmap = QtGui.QPixmap(pixmapPath)        
    else:
        #return a null pixmap. Client code should do the necessary check 
        #before setting the icon. 
        #@see: L{PM_GroupBox.addPmWidget} for an example on how this is done
        pixmap = QtGui.QPixmap('')
        if platform.atom_debug:
            #This could be a common case. As the client uses getpixmap function 
            #to see if a pixmap exists. So if its obsucring other debug messages
            #,the following print statement can be removed
            print "pixmap path %s doesn't exist." %(pixmapPath)
        
    return pixmap

def imagename_to_pixmap(imagename): #bruce 050108
    """Given the basename of a file in our cad/images directory [now cad/src/ui],
    return a QPixmap created from that file. Cache these
    (in our own Python directory, not Qt's QPixmapCache)
    so that at most one QPixmap is made from each file.
    If the imagename does not exist, a Null pixmap is returned.
    """
    global _pixmap_image_path, _pixmaps
    try:
        return _pixmaps[imagename]
    except KeyError:
        if not _pixmap_image_path:
            # This runs once per Atom session (unless this directory is missing).
            #
            # (We don't run it until needed, in case something modifies
            #  sys.argv[0] during init (we want the modified form in that case).
            #  As of 050108 this is not known to ever happen. Another reason:
            #  if we run it when this module is imported, we get the error message
            #  "QPaintDevice: Must construct a QApplication before a QPaintDevice".)
            #
            # We assume sys.argv[0] looks like .../cad/src/xxx.py
            # and we want .../cad/images. [note: this comment is out of date]
            from os.path import dirname, abspath
            cadpath = dirname(dirname(abspath(sys.argv[0]))) # ../cad
            _pixmap_image_path = os.path.join(cadpath, "src/ui/")
            assert os.path.isdir(_pixmap_image_path), "missing pixmap directory: \"%s\"" % _pixmap_image_path
        pixmappath = os.path.join( _pixmap_image_path, imagename)
        if not os.path.exists(pixmappath):
            print 'pixmap does not exist: ' + pixmappath
            import traceback
            traceback.print_stack(file=sys.stdout)
        pixmap = QtGui.QPixmap(pixmappath)
            # missing file prints a warning but doesn't cause an exception,
            # just makes a null pixmap [confirmed by mark 060202]
        _pixmaps[imagename] = pixmap
        return pixmap
    pass

def imagename_to_icon(imagename): #bruce 050108 
    """Given the basename of a file in our cad/images directory,
    return a QPixmap created from that file. Cache these
    (in our own Python directory, not Qt's QPixmapCache)
    so that at most one QPixmap is made from each file.
    If the imagename does not exist, a Null pixmap is returned.
    """
    global _pixmap_image_path, _icons
    try:
        return _icons[imagename]
    except KeyError:
        if not _pixmap_image_path:
            # This runs once per Atom session (unless this directory is missing).
            #
            # (We don't run it until needed, in case something modifies
            #  sys.argv[0] during init (we want the modified form in that case).
            #  As of 050108 this is not known to ever happen. Another reason:
            #  if we run it when this module is imported, we get the error message
            #  "QPaintDevice: Must construct a QApplication before a QPaintDevice".)
            #
            # We assume sys.argv[0] looks like .../cad/src/xxx.py
            # and we want .../cad/images.
            from os.path import dirname, abspath
            cadpath = dirname(dirname(abspath(sys.argv[0]))) # ../cad
            _pixmap_image_path = os.path.join(cadpath, "src/ui/")
            assert os.path.isdir(_pixmap_image_path), "missing pixmap directory: \"%s\"" % _pixmap_image_path
        iconpath = os.path.join( _pixmap_image_path, imagename)
        if not os.path.exists(iconpath):
            print 'icon does not exist: ' + iconpath
        icon = QtGui.QIcon(iconpath)
            # missing file prints a warning but doesn't cause an exception,
            # just makes a null icon [confirmed by mark 060202]
        _icons[imagename] = icon
        return icon
    pass

# end
