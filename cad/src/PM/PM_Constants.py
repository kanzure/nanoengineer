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

To do:
- search and replace all lowercase constants with uppercase constants.
"""

import sys

from PyQt4.Qt import Qt

__author__ = "Mark"

# PropMgr constants (system specific).
# Same as above, except these names meet our Python coding guildlines.
# To do: search and replace all lowercase constants with uppercase constants.
if sys.platform == "darwin":
    PM_MINIMUM_WIDTH = 300 # The min PropMgr width.
    PM_MAXIMUM_WIDTH = 450 # The max PropMgr width.
    PM_DEFAULT_WIDTH = PM_MINIMUM_WIDTH # Starting PropMgr width
    PM_HEADER_FONT = "Arial" # Font type used in PropMgr header.
    PM_HEADER_FONT_POINT_SIZE = 18
    PM_HEADER_FONT_BOLD = False
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
PM_GROUPBOX_SPACING       = 4 # 4 pixels between groupboxes
PM_MAINVBOXLAYOUT_MARGIN  = 0 # PropMgr's master VboxLayout marging
PM_MAINVBOXLAYOUT_SPACING = 0 # PropMgr's master VboxLayout spacing

# Header constants.
PM_HEADER_FRAME_MARGIN  = 2 # margin around icon and title.
PM_HEADER_FRAME_SPACING = 5 # space between icon and title.

# Sponsor button constants.
PM_SPONSOR_FRAME_MARGIN  = 0 # margin around sponsor button.
PM_SPONSOR_FRAME_SPACING = 0 # has no effect.

# GroupBox Layout constants.
PM_GROUPBOX_VBOXLAYOUT_MARGIN  = 2 # Groupbox VboxLayout margin
PM_GROUPBOX_VBOXLAYOUT_SPACING = 2 # Groupbox VboxLayout spacing
PM_GROUPBOX_GRIDLAYOUT_MARGIN  = 2 # Grid contains all widgets in a grpbox
PM_GROUPBOX_GRIDLAYOUT_SPACING = 2 # Grid contains all widgets in a grpbox

# Top Row Buttons constants
PM_TOPROWBUTTONS_MARGIN  = 2 # margin around buttons.
PM_TOPROWBUTTONS_SPACING = 2 # space between buttons.

# Top Row Button flags.
PM_NO_BUTTONS = 0
PM_DONE_BUTTON = 1
PM_CANCEL_BUTTON = 2
PM_RESTORE_DEFAULTS_BUTTON = 4
PM_PREVIEW_BUTTON = 8
PM_WHATS_THIS_BUTTON = 16

PM_ALL_BUTTONS = \
    PM_DONE_BUTTON | \
    PM_CANCEL_BUTTON | \
    PM_RESTORE_DEFAULTS_BUTTON | \
    PM_PREVIEW_BUTTON | \
    PM_WHATS_THIS_BUTTON

# Grid layout. Grid contains all widgets in a PM_GroupBox.
PM_GRIDLAYOUT_MARGIN  = 1
PM_GRIDLAYOUT_SPACING = 2

# PM Label alignment constants used for layouts.
PM_LABEL_RIGHT_ALIGNMENT = Qt.AlignRight | Qt.AlignVCenter
PM_LABEL_LEFT_ALIGNMENT  = Qt.AlignLeft  | Qt.AlignVCenter

# The side (column) of a PM group box.
PM_LEFT_COLUMN  = 0
PM_RIGHT_COLUMN = 1
