# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
NE1_QToolBar.py - Main NE1 toolbar class, which subclasses Qt's QToolBar
class. All NE1 main window toolbars should use this class (except for the
Command Toolbar).

@author: Mark Sims
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from PyQt4 import QtGui
from PyQt4.Qt import Qt, QToolBar, SIGNAL
from icon_utilities import getpixmap
from debug import print_compact_stack

class NE1_QToolBar(QToolBar):
    """
    Main NE1 toolbar class.
    
    Its primary use is to reimplement addSeparator() so that we can create
    custom separators.
    
    @limitations: QToolBar's insertSeparator() method has been disabled. 
    See docstring below for more information.
    """
    
    # _separatorList is a list of all the QLabel widgets in this toolbar.
    # Each QLabel has either a horizontal or vertical separator pixmap.
    _separatorList = []
    
    def __init__(self, parent):
        QToolBar.__init__(self, parent)
        self.connect(self, 
                     SIGNAL("orientationChanged()"), 
                     self.updateSeparatorPixmaps)

    def updateSeparatorPixmaps(self):
        """
        Slot for orientationChanged signal.
        """
        print "updateSeparatorPixmaps(): HERE!"
        for separator in self._separatorList:
            setSeparatorWidgetPixmap(separator, self.orientation())
                # REVIEW: should this line start with self.?
                # REVIEW: should the arg be self.orientation() like here, or self.orientation like below?
            
    def setSeparatorWidgetPixmap(self, widget, orientation):
        """
        Sets either the horizontal or the vertical pixmap to widget, depending
        on orientation.
        
        @param widget: The separator widget.
        @type  widget: U{B{QLabel}<http://doc.trolltech.com/4/qgroupbox.html>}
        
        @param orientation: The orientation of this separator.
        @type  orientation: U{B{Qt.Orientation enum}<http://doc.trolltech.com/4.2/qtoolbar.html#orientation-prop>}
        """
        if orientation() == Qt.Horizontal:
            widget.setPixmap(
                getpixmap("ui/actions/Toolbars/Standard/horizontal_toolbar_separator"))
        else:
            widget.setPixmap(
                getpixmap("ui/actions/Toolbars/Standard/vertical_toolbar_separator"))
        
    def addSeparator(self):
        """
        Reimplements the addSeparator() method of QToolBar.
        """
        _toolbarSeparator = QtGui.QLabel()
        self.setSeparatorWidgetPixmap(_toolbarSeparator, self.orientation)
        _toolbarSeparator.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.addWidget(_toolbarSeparator)
        self._separatorList.append(_toolbarSeparator)
        
    def insertSeparator(self):
        """
        This method overrides QToolBar's method. It does nothing since the 
        normal behavior will screw things up.
        
        @note: If you need this method, please code it! Mark 2008-02-29.
        """
        print_compact_stack("insertSeparator() not supported. " \
            "Use addSeparator instead or implement insertSeparator()")
        return
    
    
