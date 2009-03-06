# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
icon_utilities.py - helper functions for finding icon and pixmap files
in standard places, and caching them, and handling errors when they're
not found.

$Id$

History: developed by several authors; moved out of Utility.py
by bruce 070831.

WARNING: most code still imports these functions from Utility.py.
This should be cleaned up when practical.

TODO:

Most of the code in these functions could probably be merged
into fewer functions.

Module classification: these are used for both widgets and 3d graphics,
so they need to be classified lower than either. The file might be
considered a utility, but it does a lot of io, so we can classify it
as io for now. (Another possibility would be platform.) [bruce 071214]
"""

import os, sys
from utilities import debug_flags
from PyQt4 import QtGui
import utilities.Initialize as Initialize
import utilities.EndUser as EndUser
from utilities.debug import print_compact_stack

# This is the subdirectory component "ui" at the end of "cad/src/ui",
# in which we store most icons and similar image files.
#
# (WARNING: it is also hardcoded into longer string literals in
#  many places throughout the source code. In most of them it occurs
#  as "ui/", but probably not in all.)

UI_SUBDIRECTORY_COMPONENT = "ui"

# these private global dictionaries are used to cache
# pixmaps and icons returned by some of the functions herein
_pixmaps = {}
_icons = {}

_INITIAL_ICONPREFIX = "."
_iconprefix = _INITIAL_ICONPREFIX
    # This will be set by initialize() to the pathname of the directory that
    # contains ui/... icon files, for private use. Note that if the
    # ALTERNATE_CAD_SRC_PATH feature is being used, this will be set to
    # a different value than otherwise (new feature, bruce 070831).

def initialize_icon_utilities():
    """
    [must be called during startup, before image_directory() is ever called]
    """
    if (Initialize.startInitialization(__name__)):
        return
    
    # initialization code
    global _iconprefix
    _iconprefix = os.path.dirname(os.path.abspath(sys.argv[0]))
    _iconprefix = os.sep.join(_iconprefix.split(os.sep)[:-1] + ["src"])
        # Note: for developers, this is .../cad/src and also contains the
        # toplevel python modules or packages (as of 080111 anyway);
        # within built releases, it may not be the same directory as that
        # even though it ends with "src". [bruce comment 080111]

    if EndUser.getAlternateSourcePath() != None:
        new_iconprefix = EndUser.getAlternateSourcePath()
        print "ALTERNATE_CAD_SRC_PATH: setting _iconprefix to %r rather than %r" % \
              ( new_iconprefix, _iconprefix )
        _iconprefix = new_iconprefix

    Initialize.endInitialization(__name__)
    return

def image_directory(): #bruce 070604
    """
    Return the full pathname of the directory in which the image files
    (mostly icons) with names like ui/<subdir>/<file> exist.

    @note: As of 070604, for developers this path ends with cad/src
    and is also the main source directory, but in built releases it
    might be something different and might be platform-dependent or even
    build-system-dependent.
    """
    global _iconprefix
    assert _iconprefix != _INITIAL_ICONPREFIX, \
           "too early to call image_directory()" #bruce 080805
    return _iconprefix

def get_image_path(name, print_errors = True):
    """
    Return the full path given an image/icon path name.
    
    @param name: The image path name provided by the user. The path should start 
           with 'ui/' directory inside the src directory.
    @type  name: str

    @param print_errors: whether to report errors for missing icon files
                         when atom_debug is set. True by default.
    @type print_errors: boolean
    
    @return: full path of the image.
    @rtype:  str
    """
    
    root, ext = os.path.splitext(name)
    
    if not ext:
        if name: # 'name' can be an empty string. See docstring for details.
            msg = "Warning: No '.png' extension passed to get_image_path for [%s]. " \
                "\nPlease add the .png suffix in the source code to remove this warning.\n" % name
            print_compact_stack(msg)
        name = name + '.png'
    
    iconPath = os.path.join(image_directory(), name)
    iconPath = os.path.normpath(iconPath)      
    
    if not os.path.exists(iconPath):
        if debug_flags.atom_debug and print_errors:
            print "icon path %s doesn't exist." % (iconPath,)
    
    return iconPath

def geticon(name, print_errors = True):
    """
    Return the icon given an image path name.
    
    @param name: The image path name provided by the user. The path should start 
           with 'ui/' directory inside the src directory. If name is an 
           empty string, a null icon is returned.
    @type  name: str

    @param print_errors: whether to report errors for missing icon files
                         when atom_debug is set. True by default.
    @type print_errors: boolean
    
    @return: QIcon object for the given image path.
    @rtype:  QIcon object.
    """
    
    iconPath = get_image_path(name, print_errors)
    
    # Always set the icon with the 'iconPath'. Don't set it as an empty string 
    # like done in getPixmap. This is done on purpose. Right now there is an 
    # apparent bug in Qt in the text alignment for a push button with style sheet. 
    # @see L{PM_GroupBox._getTitleButton} which sets a non-existant 
    # 'Ghost Icon' for this button using 'geticon method'
    # By setting such an icon, the button text left-aligns! If you create an icon 
    # with iconPath = empty string (when the user supplied path doesn't exist) 
    # the text in that title button center-aligns. So lets just always use the 
    # 'iconPath' even when the path doesn't exist. -- ninad 2007-08-22
    
    icon = QtGui.QIcon(iconPath)
            
    return icon

def getCursorPixmap(png_filename):
    """
    Return the QPixmap for the given cursor PNG image file name.
    
    @param png_filename: The cursor image (PNG) file name provided by the user. 
                 The cursor file must live in the 'ui/cursors' directory
                 inside the src directory.
    @type  png_filename: str
    
    @return: QPixmap object for the given cursor image file name. 
             (could return a Null icon)
    @rtype:  QPixmap object.
    """
    return getpixmap(os.path.join("ui/cursors/", png_filename))
    
def getpixmap(name, print_errors = True):
    """
    Return the QPixmap for the given image path name.
    
    @param name: The image path name provided by the user. The path should start 
           with 'ui/' directory inside the src directory.
    @type  name: str

    @param print_errors: whether to report errors for missing pixmap files
                         when atom_debug is set. True by default.
    @type print_errors: boolean
    
    @return: QPixmap object for the given image path. (could return a Null icon)
    @rtype:  QPixmap object.
    """
    root, ext = os.path.splitext(name)
    if not ext:
        name = name + '.png'
        
    pixmapPath = os.path.join(image_directory(), name)
    pixmapPath = os.path.normpath(pixmapPath)
    
    if os.path.exists(pixmapPath):
        pixmap = QtGui.QPixmap(pixmapPath)        
    else:
        # return a null pixmap. Client code should do the necessary check 
        # before setting the icon. 
        # @see: L{PM_GroupBox.addPmWidget} for an example on how this is done
        pixmap = QtGui.QPixmap('')
        if debug_flags.atom_debug and print_errors:
            # This could be a common case. As the client uses getpixmap function 
            # to see if a pixmap exists. So if its obscuring other debug messages,
            # the following print statement can be removed
            print "pixmap path %s doesn't exist." % pixmapPath
        pass
    return pixmap

def imagename_to_pixmap(imagename): #bruce 050108
    """
    Given the basename of a file in our cad/src/ui directory,
    return a QPixmap created from that file. Cache these
    (in our own Python directory, not Qt's QPixmapCache)
    so that at most one QPixmap is made from each file.
    If the imagename does not exist, a Null pixmap is returned.
    """
    try:
        return _pixmaps[imagename]
    except KeyError:
        if imagename[:3] == "ui/":
            #If the imagename includes  "ui/" at the beginning, 
            #remove it because we will prepend imagename with 
            #UI_SUBDIRECTORY_COMPONENT
            imagename = imagename[3:]          
        
        pixmappath = os.path.join( image_directory(), 
                                   UI_SUBDIRECTORY_COMPONENT,
                                   imagename)
        if not os.path.exists(pixmappath):
            print 'pixmap does not exist; using null pixmap: ' + pixmappath
            import traceback
            traceback.print_stack(file = sys.stdout)
        pixmap = QtGui.QPixmap(pixmappath)
            # missing file prints a warning but doesn't cause an exception,
            # just makes a null pixmap [confirmed by mark 060202]
        _pixmaps[imagename] = pixmap
        return pixmap
    pass

def imagename_to_icon(imagename):
    """
    Given the basename of a file in our cad/src/ui directory,
    return a QIcon created from that file. Cache these
    (in our own Python directory)
    so that at most one QIcon is made from each file.
    If the imagename does not exist, a Null QIcon is returned.
    """
    try:
        return _icons[imagename]
    except KeyError:
        iconpath = os.path.join( image_directory(), UI_SUBDIRECTORY_COMPONENT,
                                 imagename)
        if not os.path.exists(iconpath):
            print 'icon does not exist: ' + iconpath
        icon = QtGui.QIcon(iconpath)
        _icons[imagename] = icon
        return icon
    pass

# end
