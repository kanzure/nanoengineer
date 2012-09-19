# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
CommandToolbar_Constants.py

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.


Module classification: [bruce 071228]

This is used only in Ui_CommandToolbar, slated for "ne1_ui" package.
But when we refactor Ui_CommandToolbar as described in its docstring,
this will end up used only by the part that goes into the toplevel
"CommandToolbar" package. So we might as well classify it there now.


History:

ninad 20070622 Created this file that defines various constants (e.g. color)
                    used in the command toolbar.
"""

from PyQt4.Qt import QColor

# Colors for Command Manager Control Areas
cmdTbarCntrlAreaBtnColor = QColor(204, 204, 255)
cmdTbarSubCntrlAreaBtnColor = QColor(190, 210, 190)
cmdTbarCmdAreaBtnColor = QColor(230, 230, 230)
