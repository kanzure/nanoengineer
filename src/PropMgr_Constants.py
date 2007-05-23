# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PropMgr_Constants.py -- Property Manager constants.

$Id$

"""

__author__ = "Mark"

# Hide button flags for top row buttons.
pmShowAllButtons = 0
pmHideDoneButton = 1
pmHideCancelButton = 2
pmHideRestoreDefaultsButton = 4
pmHidePreviewButton = 8
pmHideWhatsThisButton = 16
pmHideAllButtons = pmHideDoneButton | pmHideCancelButton | pmHideRestoreDefaultsButton | \
          pmHidePreviewButton | pmHideWhatsThisButton

# PropMgr Layout constants.
pmGrpBoxLeftColumn = 0
pmGroupBoxSpacing = 5 # 5 pixels between groupboxes.
pmMainVboxLayoutMargin = 0 # PropMgr's master VboxLayout margin
pmMainVboxLayoutSpacing = 0 # PropMgr's master VboxLayout spacing
pmHeaderFrameMargin = 2 # margin around icon and title.
pmHeaderFrameSpacing = 5 # space between icon and title.
pmSponsorFrameMargin = 0 # margin around sponsor button.
pmSponsorFrameSpacing = 0 # has no effect.
pmTopRowBtnsMargin = 2 # margin around buttons.
pmTopRowBtnsSpacing = 2 # space between buttons.

# GroupBox Layout constants.
pmMsgGrpBoxMargin = 0 # margin around yellow text window.
pmMsgGrpBoxSpacing = 0 # has no effect.
pmGrpBoxVboxLayoutMargin = 0 # Groupbox VboxLayout margin
pmGrpBoxVboxLayoutSpacing = 2 # Groupbox VboxLayout spacing
pmGrpBoxGridLayoutMargin = 2 # Grid contains all widgets in a grpbox
pmGrpBoxGridLayoutSpacing = 4 # Grid contains all widgets in a grpbox

# These need to be deleted by me. Mark 2007-05-20
pmGridLayoutMargin = 2 # Grid contains all widgets in a grpbox (obsolete)
pmGridLayoutSpacing = 4 # Grid contains all widgets in a grpbox (obsolete)

# Directory containing icons/images for the property manager.
pmImagePath = "ui/actions/Properties Manager/"