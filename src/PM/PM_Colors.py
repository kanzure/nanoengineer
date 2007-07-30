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

from PyQt4.Qt import QColor
from PyQt4.Qt import QPalette

from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice

# Directory containing icons/images for the property manager.
PM_ICON_DIR = "ui/actions/Properties Manager/"

def getIconPath(iconName):
    """
    Returns the relative path to the PM icon/image file <iconName>.
    
    @param iconName: basename of the icon's PNG file
    @type  iconName: str 
    """
    return os.path.join (PM_ICON_DIR + iconName)

def getPalette( palette, colorRole, color ):
    """
    Assigns a color (based on color role) to palette and returns it.
    The color/color role is assigned to all color groups.
            
    @param palette: A palette. If palette is None, we create and return a new palette.
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

_colortheme_Choice = Choice(["Gray", "Blue"], default_value = COLOR_THEME)

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
pmMessageTextEditColor = QColor(255, 255, 100) # Yellow msg box (QTextEdit widget).
PM_COLOR = QColor(230, 231, 230) # Should get this from the main window (parent).
PM_GROUPBOX_COLOR = QColor(201, 203, 223)
PM_MESSAGE_TEXT_EDIT_COLOR = QColor(255, 255, 100) # Yellow msg box (QTextEdit widget).
pmMessageBoxColor = pmMessageTextEditColor # pmMessageTextEditColor to be depreciated.

if COLOR_THEME == "Gray":

    # Dark Gray Color Theme
    
    # Colors for Property Manager widgets.
    pmTitleFrameColor = QColor(120, 120, 120)
    pmHeaderFrameColor = pmTitleFrameColor # pmTitleFrameColor to be depreciated. Mark 2007-07-24
    pmTitleLabelColor = QColor(255, 255, 255)
    pmHeaderTitleColor = pmTitleLabelColor # pmTitleLabelColor to be depreciated. Mark 2007-07-24
    pmGrpBoxButtonColor = QColor(172, 173, 190)
    pmCheckBoxTextColor = QColor(0, 0, 255) # used in MMKit
    pmCheckBoxButtonColor = QColor(172, 173, 190)
    
    
    # Property Manager stylesheet colors (uses HTML Color Codes)
    #@ To do: I intend to add a method for each (like those above) 
    # that returns a palette. Mark 2007-05-17.
    pmGrpBoxBorderColor = "#444F51"
    pmGrpBoxButtonBorderColor = "#939089"
    pmGrpBoxButtonTextColor = "#282821" # Same as pmCheckBoxTextColor

    # Locations of expanded and collapsed title button images.
    pmGrpBoxExpandedIconPath  = getIconPath("GroupBox_Opened_Gray.png")
    pmGrpBoxCollapsedIconPath = getIconPath("GroupBox_Closed_Gray.png")

else: # Blue Color Theme
    
    # Colors for Property Manager widgets.
    pmTitleFrameColor = QColor(50,90, 230) # I like (50,90, 230). mark
    pmHeaderFrameColor = pmTitleFrameColor # pmTitleFrameColor to be depreciated. Mark 2007-07-24
    pmTitleLabelColor = QColor(255, 255, 255)
    pmHeaderTitleColor = pmTitleLabelColor # pmTitleLabelColor to be depreciated. Mark 2007-07-24
    pmGrpBoxButtonColor = QColor(172, 173, 190)
    pmCheckBoxTextColor = QColor(0, 0, 255)
    pmCheckBoxButtonColor = QColor(172, 173, 190)
    pmMessageTextEditColor = QColor(255, 255, 100)

    # Property Manager stylesheet colors (uses HTML Color Codes)
    pmGrpBoxBorderColor = "blue"
    pmGrpBoxButtonBorderColor = "gray"
    pmGrpBoxButtonTextColor = "blue"

    # Locations of groupbox opened and closed images.
    pmGrpBoxExpandedIconPath  = getIconPath("GroupBox_Opened_Blue.png")
    pmGrpBoxCollapsedIconPath = getIconPath("GroupBox_Closed_Blue.png")
