# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_Colors.py -- Property Manager color theme functions and constants..

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Created initially for PM_Dialog as part of the code cleanup
                 and review for new coding standards. Renamed all constants
                 to names with uppercase letters.
"""

import os
import sys

from PyQt4.Qt import QColor
from PyQt4.Qt import QPalette

from utilities.debug_prefs import debug_pref, Choice

_iconPrefix = os.path.dirname(os.path.abspath(sys.argv[0]))
_iconPrefix = os.sep.join(_iconPrefix.split(os.sep)[:-1] + ["src"])

# Directory containing icons/images for the property manager.
PM_ICON_DIR = "ui/actions/Properties Manager/"

def getIconPath(iconName, _iconPrefix = _iconPrefix):
    """
    Returns the relative path to the PM icon/image file <iconName>.
    
    @param iconName: basename of the icon's PNG file
    @type  iconName: str 
    
    @param _iconPrefix: The directory path to be prepended to the icon file path
    @param _iconPrefix: str
    """
   
    iconPath = os.path.join ( _iconPrefix, PM_ICON_DIR)   
    iconPath = os.path.join( iconPath, iconName)    
    iconPath = os.path.abspath(iconPath)
       
    if not os.path.exists(iconPath):
        iconPath = ''
    
    forwardSlash = "/"
    
    #The iconPath is used in L{PM_GroupBox._getTitleButtonStyleSheet}
    #the style sheet border-image attribute needs a url with only 
    #forward slashes in the string. This creates problem on windows 
    #because os.path.abspath returns the path with all backword slashes 
    #in the path name(os default). the following replaces all backward 
    #slashes with the forward slashes. Also fixes bug 2509 -- ninad 2007-08-21
    
    if sys.platform == 'win32':
        iconPath = iconPath.replace(os.sep , str(forwardSlash))
           
    return str(iconPath)

def getPalette( palette, colorRole, color ):
    """
    Assigns a color (based on color role) to palette and returns it.
    The color/color role is assigned to all color groups.
            
    @param palette: A palette. If palette is None, we create and return a new 
                   palette.
    @type  palette: QPalette
    
    @param colorRole: the Qt ColorRole
    @type  colorRole: Qt.ColorRole
    
    @param color: color
    @type  color: QColor
    
    @return: Returns the updated palette, or a new palette if none was supplied.
    @rtype : QPalette
    
    @see QPalette.setColor()
    """
    if palette:
        pass # Make sure palette is QPalette.
    else:
        palette = QPalette()
            
    palette.setColor(colorRole, color)
    
    return palette

COLOR_THEME = "Gray"

_colortheme_Choice = Choice(["Gray", "Blue"], defaultValue = COLOR_THEME)

COLOR_THEME_prefs_key = "A9/Color Theme"

def set_Color_Theme_from_pref():
    global COLOR_THEME
    COLOR_THEME = debug_pref("Color Theme (next session)",
                                       _colortheme_Choice,
                                       non_debug = True,
                                       prefs_key = COLOR_THEME_prefs_key)
    return

set_Color_Theme_from_pref()

# Standard colors for all themes.
pmColor = QColor(230, 231, 230) # Should get this from the main window (parent).
pmGrpBoxColor = QColor(201, 203, 223)
# Yellow msg box (QTextEdit widget).
pmMessageTextEditColor = QColor(255, 255, 100) 
# Should get the following from the main window (parent).
PM_COLOR = QColor(230, 231, 230)
PM_GROUPBOX_COLOR = QColor(201, 203, 223)
# Yellow msg box (QTextEdit widget).
PM_MESSAGE_TEXT_EDIT_COLOR = QColor(255, 255, 100)
# pmMessageTextEditColor to be deprecated.
pmMessageBoxColor = pmMessageTextEditColor 

pmReferencesListWidgetColor = QColor(254, 128, 129)

# Special Sequence Editor colors.
sequenceEditorNormalColor = QColor(255, 255, 255) # White
sequenceEditorChangedColor = QColor(255, 220, 200) # Pink
sequenceEditStrandMateBaseColor = QColor(255, 255, 200) # Light yellow

if COLOR_THEME == "Gray":

    # Dark Gray Color Theme
    
    # Colors for Property Manager widgets.
    pmTitleFrameColor = QColor(120, 120, 120)
    # pmTitleFrameColor to be deprecated. Mark 2007-07-24
    pmHeaderFrameColor = pmTitleFrameColor 
    pmTitleLabelColor = QColor(255, 255, 255)
    # pmTitleLabelColor to be deprecated. Mark 2007-07-24
    pmHeaderTitleColor = pmTitleLabelColor 
    pmCheckBoxTextColor = QColor(0, 0, 255) # used in MMKit
    pmCheckBoxButtonColor = QColor(172, 173, 190)
    
    # Property Manager group box colors.
    pmGrpBoxBorderColor = QColor(68, 79, 81)
    pmGrpBoxButtonBorderColor = QColor(147, 144, 137)
    pmGrpBoxButtonTextColor = QColor(40, 40, 33) # Same as pmCheckBoxTextColor
    pmGrpBoxButtonColor = QColor(170, 170, 170)

    # Locations of expanded and collapsed title button images.
    pmGrpBoxExpandedIconPath  = getIconPath("GroupBox_Opened_Gray.png")
    pmGrpBoxCollapsedIconPath = getIconPath("GroupBox_Closed_Gray.png")

else: # Blue Color Theme
    
    # Colors for Property Manager widgets.
    pmTitleFrameColor = QColor(50, 90, 230) # I like (50,90, 230). mark
    # pmTitleFrameColor to be deprecated. Mark 2007-07-24
    pmHeaderFrameColor = pmTitleFrameColor 
    pmTitleLabelColor = QColor(255, 255, 255)
    # pmTitleLabelColor to be deprecated. Mark 2007-07-24
    pmHeaderTitleColor = pmTitleLabelColor 
    pmCheckBoxTextColor = QColor(0, 0, 255)
    pmCheckBoxButtonColor = QColor(172, 173, 190)
    pmMessageTextEditColor = QColor(255, 255, 100)

    # Property Manager group box colors.
    pmGrpBoxBorderColor = QColor(0, 0, 255) # blue
    pmGrpBoxButtonBorderColor = QColor(127, 127, 127) 
    pmGrpBoxButtonTextColor = QColor(0, 0, 255)
    pmGrpBoxButtonColor = QColor(144, 144, 200)

    # Locations of groupbox opened and closed images.
    pmGrpBoxExpandedIconPath  = getIconPath("GroupBox_Opened_Blue.png")
    pmGrpBoxCollapsedIconPath = getIconPath("GroupBox_Closed_Blue.png")
