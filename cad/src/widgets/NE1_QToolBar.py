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
from utilities.icon_utilities import getpixmap
from utilities.debug import print_compact_stack

DEBUG = False # Do not commit with DEBUG set to True.

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
    _separatorNumber = 0
    
    def __init__(self, parent):
        """
        Constructs an NE1 toolbar for the main window.
        """
        QToolBar.__init__(self, parent)
        self._separatorList = []
        
        # Attention: This signal-slot connection is not working and I'm not
        # sure why. As a workaround, I reimplemented QToolBar.moveEvent()
        # which does the job nicely. I'm leaving the connect() call here,
        # but commenting it out. I bet its a Qt bug and it might be fixed 
        # in Qt 4.3 (or later). Mark 2008-03-01.
        #self.connect(self, 
        #             SIGNAL("orientationChanged()"), 
        #             self.updateSeparatorPixmaps)

    def updateSeparatorPixmaps(self):
        """
        Updates the pixmap for all separators in this toolbar.
        
        @note: This is also supposed to be the slot for the 
               orientationChanged() signal, but it doesn't work.
        """
        for separator in self._separatorList:
            if DEBUG:
                print separator.objectName()
            self.setSeparatorWidgetPixmap(separator, self.orientation())
            
    def moveEvent(self, event):
        """
        Reimplements QWidget.moveEvent(). It is used as a workaround for
        the orientationChanged() signal bug mentioned throughout.
        """
        QToolBar.moveEvent(self, event)
        self.updateSeparatorPixmaps()
        
    def setSeparatorWidgetPixmap(self, widget, orientation):
        """
        Sets either the horizontal or the vertical pixmap to widget, depending
        on orientation.
        
        @param widget: The separator widget.
        @type  widget: U{B{QLabel}<http://doc.trolltech.com/4/qgroupbox.html>}
        
        @param orientation: The orientation of this separator.
        @type  orientation: U{B{Qt.Orientation enum}<http://doc.trolltech.com/4.2/qtoolbar.html#orientation-prop>}
        """
        if orientation == Qt.Horizontal:
            widget.setPixmap(
                getpixmap("ui/toolbars/h_separator.png"))
        else:
            widget.setPixmap(
                getpixmap("ui/toolbars/v_separator.png"))
        
    def addSeparator(self):
        """
        Reimplements the addSeparator() method of QToolBar.
        """
        _toolbarSeparator = QtGui.QLabel(self)
        if DEBUG:
            _name = "%s-Separator%d" % (self.objectName(), self._separatorNumber)
            _toolbarSeparator.setObjectName(_name)
            self._separatorNumber += 1
        self.setSeparatorWidgetPixmap(_toolbarSeparator, self.orientation())
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
            "Use addSeparator() instead or implement insertSeparator()")
        return
    