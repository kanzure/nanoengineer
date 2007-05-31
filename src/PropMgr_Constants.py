# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PropMgr_Constants.py -- Property Manager constants.

$Id$

"""

from PyQt4.Qt import *
from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice
import os, sys

__author__ = "Mark"

# PropMgr constants (system specific).
if sys.platform == "darwin":
    pmMinWidth = 300 # The min PropMgr width.
    pmMaxWidth = pmMinWidth # The max PropMgr width.
    pmDefaultWidth = pmMinWidth # Starting PropMgr width
    pmHeaderFont = "Arial" # Font type used in PropMgr header.
    pmHeaderFontPointSize = 20
    pmHeaderFontBold = True
elif sys.platform == "win32":
    pmMinWidth = 230 # The min PropMgr width.
    pmMaxWidth = pmMinWidth # The max PropMgr width.
    pmDefaultWidth = pmMinWidth # Starting PropMgr width
    pmHeaderFont = "Arial" # Font type used in PropMgr header.
    pmHeaderFontPointSize = 12
    pmHeaderFontBold = True
else: #Linux
    pmMinWidth = 250 # The min PropMgr width.
    pmMaxWidth = pmMinWidth # The max PropMgr width.
    pmDefaultWidth = pmMinWidth # Starting PropMgr width
    pmHeaderFont = "Arial" # Font type used in PropMgr header.
    pmHeaderFontPointSize = 12
    pmHeaderFontBold = True

if 0:
    print "PropMgr width=", pmDefaultWidth
    print "PropMgr Min width=", pmMinWidth
    print "PropMgr Max width=", pmMaxWidth

# PropMgr constants.
pmGrpBoxLeftColumn = 0
pmGroupBoxSpacing = 5 # 5 pixels between groupboxes
pmMainVboxLayoutMargin = 0 # PropMgr's master VboxLayout margin
pmMainVboxLayoutSpacing = 0 # PropMgr's master VboxLayout spacing

# Header constants.
pmHeaderFrameMargin = 2 # margin around icon and title.
pmHeaderFrameSpacing = 5 # space between icon and title.

# Sponsor button constants.
pmSponsorFrameMargin = 0 # margin around sponsor button.
pmSponsorFrameSpacing = 0 # has no effect.

# GroupBox Layout constants.
pmMsgGrpBoxMargin = 0 # margin around yellow text window.
pmMsgGrpBoxSpacing = 0 # has no effect.
pmGrpBoxVboxLayoutMargin = 0 # Groupbox VboxLayout margin
pmGrpBoxVboxLayoutSpacing = 2 # Groupbox VboxLayout spacing
pmGrpBoxGridLayoutMargin = 2 # Grid contains all widgets in a grpbox
pmGrpBoxGridLayoutSpacing = 4 # Grid contains all widgets in a grpbox

# TopRowButton constants
pmTopRowBtnsMargin = 5 # margin around buttons.
pmTopRowBtnsSpacing = 5 # space between buttons.

# TopRowButton hide button flags for top row buttons.
pmShowAllButtons = 0
pmHideDoneButton = 1
pmHideCancelButton = 2
pmHideRestoreDefaultsButton = 4
pmHidePreviewButton = 8
pmHideWhatsThisButton = 16
pmHideAllButtons = pmHideDoneButton | \
                   pmHideCancelButton | \
                   pmHideRestoreDefaultsButton | \
                   pmHidePreviewButton | \
                   pmHideWhatsThisButton

# These need to be deleted by me. Mark 2007-05-20
pmGridLayoutMargin = 2 # Grid contains all widgets in a grpbox (obsolete)
pmGridLayoutSpacing = 4 # Grid contains all widgets in a grpbox (obsolete)

# Label alignment constants used for layouts.
pmLabelRightAlignment = Qt.AlignRight | Qt.AlignVCenter
pmLabelLeftAlignment = Qt.AlignLeft | Qt.AlignVCenter

# MMKit element button constants

if sys.platform == "darwin":
    pmMMKitButtonHeight = 32
    pmMMKitButtonWidth = int((pmMinWidth - 38)/6) # 43 for A9. Mark 2007-05-21
    pmMMKitButtonFont = "Arial"
    pmMMKitButtonFontPointSize = 18
    pmMMKitButtonFontBold = False
else: # Windows and Linux
    pmMMKitButtonHeight = 32
    pmMMKitButtonWidth = int((pmMinWidth - 38)/6) # 32 for A9. Mark 2007-05-21
    pmMMKitButtonFont = "Arial"
    pmMMKitButtonFontPointSize = 10
    pmMMKitButtonFontBold = True
    
# print "MMKit button width: ", pmMMKitButtonWidth

pmMMKitPageMargin = 2 # Used by Atoms, Clipboard and (Part) Library.

# Directory containing icons/images for the property manager.
pmImagePath = "ui/actions/Properties Manager/"

def getPropMgrImagePath(imageName):
    """Returns the relative path to the icon/image file <imageName>.
    """
    return os.path.join (pmImagePath + imageName)

def getHeaderFont():
    """Returns the QFont used for all PropMgr headers.
    """
    font = QFont()
    font.setFamily(pmHeaderFont)
    font.setPointSize(pmHeaderFontPointSize)
    font.setBold(pmHeaderFontBold)
    return font

# PropMgr color theme functions and constants. #########################

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
pmGrpBoxColor = QColor(201,203,223)
pmMessageTextEditColor = QColor(255,255,100) # Yellow msg box (QTextEdit widget).

if COLOR_THEME == "Gray":

    # Dark Gray Color Theme
    
    # Colors for Property Manager widgets.
    pmTitleFrameColor = QColor(120,120,120)
    pmTitleLabelColor = QColor(255,255,255)
    pmGrpBoxButtonColor = QColor(172,173,190)
    pmCheckBoxTextColor = QColor(0,0,255) # used in MMKit
    pmCheckBoxButtonColor = QColor(172,173,190)
    
    
    # Property Manager stylesheet colors (uses HTML Color Codes)
    #@ To do: I intend to add a method for each (like those above) 
    # that returns a palette. Mark 2007-05-17.
    pmGrpBoxBorderColor = "#444F51"
    pmGrpBoxButtonBorderColor = "#939089"
    pmGrpBoxButtonTextColor = "#282821" # Same as pmCheckBoxTextColor

    # Locations of expanded and collapsed title button images.
    pmGrpBoxExpandedImage = getPropMgrImagePath("GroupBox_Opened_Gray.png")
    pmGrpBoxCollapsedImage = getPropMgrImagePath("GroupBox_Closed_Gray.png")

else: # Blue Color Theme
    
    # Colors for Property Manager widgets.
    pmTitleFrameColor = QColor(120,120,120) # I like (50,90,230). mark
    pmTitleLabelColor = QColor(255,255,255)
    pmGrpBoxButtonColor = QColor(172,173,190)
    pmCheckBoxTextColor = QColor(0,0,255)
    pmCheckBoxButtonColor = QColor(172,173,190)
    pmMessageTextEditColor = QColor(255,255,100)

    # Property Manager stylesheet colors (uses HTML Color Codes)
    pmGrpBoxBorderColor = "blue"
    pmGrpBoxButtonBorderColor = "gray"
    pmGrpBoxButtonTextColor = "blue"

    # Locations of groupbox opened and closed images.
    pmGrpBoxExpandedImage = getPropMgrImagePath("GroupBox_Opened_Blue.png")
    pmGrpBoxCollapsedImage = getPropMgrImagePath("GroupBox_Closed_Blue.png")