# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_Constants.py -- Property Manager constants.

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Created initially for PM_Dialog as part of the code cleanup
                 and review for new coding standards. Renamed all constants
                 to names with uppercase letters.

"""

import sys

from PyQt4.Qt import Qt

from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice

__author__ = "Mark"

# PropMgr constants (system specific).
if sys.platform == "darwin":
    pmMinWidth = 300 # The min PropMgr width.
    pmMaxWidth = 450 # The max PropMgr width.
    pmDefaultWidth = pmMinWidth # Starting PropMgr width
    pmHeaderFont = "Arial" # Font type used in PropMgr header.
    pmHeaderFontPointSize = 20
    pmHeaderFontBold = True
elif sys.platform == "win32":
    pmMinWidth = 240 # The min PropMgr width.
    pmMaxWidth = 400 # The max PropMgr width.
    pmDefaultWidth = pmMinWidth # Starting PropMgr width
    pmHeaderFont = "Arial" # Font type used in PropMgr header.
    pmHeaderFontPointSize = 12
    pmHeaderFontBold = True
else: #Linux
    pmMinWidth = 250 # The min PropMgr width.
    pmMaxWidth = 400 # The max PropMgr width.
    pmDefaultWidth = pmMinWidth # Starting PropMgr width
    pmHeaderFont = "Arial" # Font type used in PropMgr header.
    pmHeaderFontPointSize = 12
    pmHeaderFontBold = True

# PropMgr constants (system specific).
if sys.platform == "darwin":
    PM_MINIMUM_WIDTH = 300 # The min PropMgr width.
    PM_MAXIMUM_WIDTH = 450 # The max PropMgr width.
    PM_DEFAULT_WIDTH = PM_MINIMUM_WIDTH # Starting PropMgr width
    PM_HEADER_FONT = "Arial" # Font type used in PropMgr header.
    PM_HEADER_FONT_POINT_SIZE = 20
    PM_HEADER_FONT_BOLD = True
elif sys.platform == "win32":
    PM_MINIMUM_WIDTH = 240 # The min PropMgr width.
    PM_MAXIMUM_WIDTH = 400 # The max PropMgr width.
    PM_DEFAULT_WIDTH = PM_MINIMUM_WIDTH # Starting PropMgr width
    PM_HEADER_FONT = "Arial" # Font type used in PropMgr header.
    PM_HEADER_FONT_POINT_SIZE = 12
    PM_HEADER_FONT_BOLD = True
else: #Linux
    PM_MINIMUM_WIDTH = 250 # The min PropMgr width.
    PM_MAXIMUM_WIDTH = 400 # The max PropMgr width.
    PM_DEFAULT_WIDTH = PM_MINIMUM_WIDTH # Starting PropMgr width
    PM_HEADER_FONT = "Arial" # Font type used in PropMgr header.
    PM_HEADER_FONT_POINT_SIZE = 12
    PM_HEADER_FONT_BOLD = True

if 0:
    print "PropMgr width = ",     PM_DEFAULT_WIDTH
    print "PropMgr Min width = ", PM_MINIMUM_WIDTH
    print "PropMgr Max width = ", PM_MAXIMUM_WIDTH

# PropMgr constants.
pmGroupBoxSpacing         = 5 # 5 pixels between groupboxes
PM_GROUPBOX_SPACING       = 5 # 5 pixels between groupboxes
pmMainVboxLayoutMargin    = 0 # PropMgr's master VboxLayout margin
PM_MAINVBOXLAYOUT_MARGIN  = 0 # PropMgr's master VboxLayout margin
pmMainVboxLayoutSpacing   = 0 # PropMgr's master VboxLayout spacing
PM_MAINVBOXLAYOUT_SPACING = 0 # PropMgr's master VboxLayout spacing

# Header constants.
pmHeaderFrameMargin     = 2 # margin around icon and title.
PM_HEADER_FRAME_MARGIN  = 2 # margin around icon and title.
pmHeaderFrameSpacing    = 5 # space between icon and title.
PM_HEADER_FRAME_SPACING = 5 # space between icon and title.

# Sponsor button constants.
pmSponsorFrameMargin     = 0 # margin around sponsor button.
PM_SPONSOR_FRAME_MARGIN  = 0 # margin around sponsor button.
pmSponsorFrameSpacing    = 0 # has no effect.
PM_SPONSOR_FRAME_SPACING = 0 # has no effect.

# GroupBox Layout constants.
pmGrpBoxVboxLayoutMargin       = 2 # Groupbox VboxLayout margin
PM_GROUPBOX_VBOXLAYOUT_MARGIN  = 2 # Groupbox VboxLayout margin
pmGrpBoxVboxLayoutSpacing      = 2 # Groupbox VboxLayout spacing
PM_GROUPBOX_VBOXLAYOUT_SPACING = 2 # Groupbox VboxLayout spacing
pmGrpBoxGridLayoutMargin       = 2 # Grid contains all widgets in a grpbox
PM_GROUPBOX_GRIDLAYOUT_MARGIN  = 2 # Grid contains all widgets in a grpbox
pmGrpBoxGridLayoutSpacing      = 4 # Grid contains all widgets in a grpbox
PM_GROUPBOX_GRIDLAYOUT_SPACING = 4 # Grid contains all widgets in a grpbox

# Top Row Buttons constants
pmTopRowBtnsMargin       = 5 # margin around buttons.
PM_TOPROWBUTTONS_MARGIN  = 5 # margin around buttons.
pmTopRowBtnsSpacing      = 5 # space between buttons.
PM_TOPROWBUTTONS_SPACING = 5 # space between buttons.

# Top Row Button flags.
pmNoButtons = 0
PM_NO_BUTTONS = 0
pmDoneButton = 1
PM_DONE_BUTTON = 1
pmCancelButton = 2
PM_CANCEL_BUTTON = 2
pmRestoreDefaultsButton = 4
PM_RESTORE_DEFAULTS_BUTTON = 4
pmPreviewButton = 8
PM_PREVIEW_BUTTON = 8
pmWhatsThisButton = 16
PM_WHATS_THIS_BUTTON = 16
pmAllButtons = \
    pmDoneButton | \
    pmCancelButton | \
    pmRestoreDefaultsButton | \
    pmPreviewButton | \
    pmWhatsThisButton
PM_ALL_BUTTONS = \
    PM_DONE_BUTTON | \
    PM_CANCEL_BUTTON | \
    PM_RESTORE_DEFAULTS_BUTTON | \
    PM_PREVIEW_BUTTON | \
    PM_WHATS_THIS_BUTTON

# Grid layout. Grid contains all widgets in a PM_GroupBox.
pmGridLayoutMargin    = 2
PM_GRIDLAYOUT_MARGIN  = 2
pmGridLayoutSpacing   = 4
PM_GRIDLAYOUT_SPACING = 4

# PM Label alignment constants used for layouts.
pmRightAlignment    = Qt.AlignRight | Qt.AlignVCenter
PM_LABEL_RIGHT_ALIGNMENT = Qt.AlignRight | Qt.AlignVCenter
pmLeftAlignment     = Qt.AlignLeft  | Qt.AlignVCenter
PM_LABEL_LEFT_ALIGNMENT  = Qt.AlignLeft  | Qt.AlignVCenter

# The side (column) of a PM group box.
pmLeftColumn    = 0
PM_LEFT_COLUMN  = 0
pmRightColumn   = 1
PM_RIGHT_COLUMN = 1

# MMKit element button constants

if sys.platform == "darwin":
    pmMMKitButtonHeight = 32
    pmMMKitButtonWidth = int((pmMinWidth - 38)/6) # 43 for A9. Mark 2007-05-21
    pmMMKitButtonFont = "Arial"
    pmMMKitButtonFontPointSize = 18
    pmMMKitButtonFontBold = False
    PM_MMKIT_BUTTON_HEIGHT = 32
    PM_MMKIT_BUTTON_WIDTH = int((pmMinWidth - 38)/6) # 43 for A9. Mark 2007-05-21
    PM_MMKIT_BUTTON_FONT = "Arial"
    PM_MMKIT_BUTTON_FONT_POINT_SIZE = 18
    PM_MMKIT_BUTTON_FONT_BOLD = False
else: # Windows and Linux
    pmMMKitButtonHeight = 32
    pmMMKitButtonWidth = int((pmMinWidth - 38)/6) # 32 for A9. Mark 2007-05-21
    pmMMKitButtonFont = "Arial"
    pmMMKitButtonFontPointSize = 10
    pmMMKitButtonFontBold = True
    PM_MMKIT_BUTTON_HEIGHT = 32
    PM_MMKIT_BUTTON_WIDTH = int((pmMinWidth - 38)/6) # 32 for A9. Mark 2007-05-21
    PM_MMKIT_BUTTON_FONT = "Arial"
    PM_MMKIT_BUTTON_FONT_POINT_SIZE = 10
    PM_MMKIT_BUTTON_FONT_BOLD = False
    
# print "MMKit button width: ", pmMMKitButtonWidth

pmMMKitPageMargin    = 2 # Used by Atoms, Clipboard and (Part) Library.
PM_MMKIT_PAGE_MARGIN = 2 # Used by Atoms, Clipboard and (Part) Library.
