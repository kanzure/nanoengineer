# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
NE1ToolBar.py - Variant of QToolBar in which the toolbar border is not rendered

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  All rights reserved.

History:

File created on 20070507. There could be more than one NE1Toolbar classes
(subclasses of QToolBar) in future depending upon the need.

"""

from PyQt4.Qt import QToolBar
from PyQt4.Qt import QPainter
from PyQt4.Qt import QStyleOptionToolBar
from PyQt4.Qt import QPalette
from PyQt4.Qt import QStyle


class NE1ToolBar(QToolBar):
    """
    Variant of QToolBar in which the toolbar border is not rendered.
    """
    def paintEvent(self, event):
        """
        reimplements the paintEvent of QToolBar
        """
        #ninad20070507 : NE1ToolBar is used in Movie Prop mgr.
        # reimplementing paint event makes sure that the
        # unwanted toolbar border for the Movie control buttons
        # is not rendered. No other use at the moment.
        # [bruce 071214 guessed class docstring based on this comment.
        #  I think the class should be renamed to be more descriptive.]
        painter = QPainter(self)
        option = QStyleOptionToolBar()
        option.initFrom(self)
        option.backgroundColor = self.palette().color(QPalette.Background)
        option.positionWithinLine = QStyleOptionToolBar.Middle
        option.positionOfLine = QStyleOptionToolBar.Middle
        self.style().drawPrimitive(QStyle.PE_PanelToolBar, option, painter, self)

    pass
