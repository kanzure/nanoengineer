# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_ToolButton.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrToolButton out of PropMgrBaseClass.py into this
file and renamed it PM_ToolButton.
"""
import os

from PyQt4.Qt import QLabel
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QWidget
from PyQt4.Qt import QSize

from utilities.icon_utilities import geticon

class PM_ToolButton( QToolButton ):
    """
    The PM_ToolButton widget provides a QToolButton with a
    QLabel for a Property Manager group box.

    @cvar defaultText: The default text of the tool button.
    @type defaultText: str

    @cvar setAsDefault: Determines whether to reset the value of the
                        tool button to I{defaultText} when the user clicks
                        the "Restore Defaults" button.
    @type setAsDefault: bool

    @cvar labelWidget: The Qt label widget of this tool button.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """

    defaultText = ""
    setAsDefault = True
    labelWidget  = None

    def __init__(self,
                 parentWidget,
                 label        = '',
                 labelColumn  = 0,
                 text         = '',
                 iconPath     = '',
                 setAsDefault = True,
                 spanWidth    = False
                 ):
        """
        Appends a QToolButton (Qt) widget to the bottom of I{parentWidget},
        a Property Manager group box.

        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox

        @param label: The label that appears to the left or right of the
                      checkbox.

                      If spanWidth is True, the label will be displayed on
                      its own row directly above the list widget.

                      To suppress the label, set I{label} to an
                      empty string.
        @type  label: str

        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left
                            column) and 1 (right column). The default is 0
                            (left column).
        @type  labelColumn: int

        @param text: The button's text.
        @type  text: str

        @param iconPath: The relative path to the button's icon.
        @type  iconPath: str

        @param setAsDefault: If True, will restore <text> as the button's text
                         when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool

        @param spanWidth: If True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left
                      justified.
        @type  spanWidth: bool

        @see: U{B{QToolButton}<http://doc.trolltech.com/4/qtoolbutton.html>}
        """

        if 0: # Debugging code
            print "PM_ToolButton.__init__():"
            print "  label        = ", label
            print "  labelColumn  = ", labelColumn
            print "  text         = ", text
            print "  iconPath     = ", iconPath
            print "  setAsDefault = ", setAsDefault
            print "  spanWidth    = ", spanWidth

        QToolButton.__init__(self)

        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth

        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)

        # Set text
        self.setText(text)

        # Set icon
        self.setIcon(geticon(iconPath))
        self.setIconSize(QSize(22, 22))

        # Set default text
        self.defaultText  = text
        self.setAsDefault = setAsDefault

        parentWidget.addPmWidget(self)

    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setText(self.defaultText)

    def hide(self):
        """
        Hides the tool button and its label (if it has one).

        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget:
            self.labelWidget.hide()

    def show(self):
        """
        Unhides the tool button and its label (if it has one).

        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()

# End of PM_ToolButton ############################
