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