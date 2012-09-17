# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
PM_FontComboBox.py

@author: Derrick
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  All rights reserved.


"""

from PyQt4.Qt import QFontComboBox
from PyQt4.Qt import QLabel
from PyQt4.Qt import QWidget

class PM_FontComboBox( QFontComboBox ):
    """
    Much (practically all) of this code was taken from PM_ComboBox with only
    slight modifications.

    The PM_FontComboBox widget provides a combobox with a text label for a
    Property Manager group box. The text label can be positioned on either
    the left or right side of the combobox.

    For a more complete explanation of a ComboBox, refer to the definition
    provided in PM_ComboBox.  In this case, the list of available fonts is
    not provided by variable, but is read from the system.

    @cvar defaultFont: The default font of the combobox.
    @type defaultFont: QFont

    @cvar setAsDefault: Determines whether to reset the currentFont to
                        the defaultFont when the user clicks the
                        "Restore Defaults" button.
    @type setAsDefault: bool

    @cvar labelWidget: The Qt label widget of this combobox.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}

    @see: U{B{QComboBox}<http://doc.trolltech.com/4/qcombobox.html>}
    """

    defaultFont   = None
    setAsDefault   = True
    labelWidget    = None

    def __init__(self,
                 parentWidget,
                 label        = '',
                 labelColumn  = 0,
                 selectFont  = '',
                 setAsDefault = True,
                 spanWidth    = False
                 ):
        """
        Appends a QFontComboBox widget (with a QLabel widget) to <parentWidget>,
        a property manager group box.

        Arguments:

        @param parentWidget: the group box containing this PM widget.
        @type  parentWidget: PM_GroupBox

        @param label: label that appears to the left of (or above) this PM widget.
        @type  label: str

        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left
                            column) and 1 (right column). The default is 0
                            (left column).
        @type  labelColumn: int

        @param selectFont: initial font of combobox. (''=default)
        @type  selectFont: QFont object (default = '')

        @param setAsDefault: if True, will restore <defaultFont> as the current
                         Font when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool (default True)

        @param spanWidth: If True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left
                      justified.
        @type  spanWidth: bool (default False)

        @see: U{B{QComboBox}<http://doc.trolltech.com/4/qcombobox.html>}
        """

        if 0: # Debugging code
            print "PM_FontComboBox.__init__():"
            print "  label        =", label
            print "  selectFont  =", selectFont
            print "  setAsDefault =", setAsDefault
            print "  spanWidth    =", spanWidth

        QFontComboBox.__init__(self)

        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth

        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)

        # Set initial choice (selectFont).
        if selectFont != '':
            self.setCurrentFont(selectFont)

        self.defaultFont = self.currentFont()

        parentWidget.addPmWidget(self)

    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setCurrentFont(self.defaultFont)

    def hide(self):
        """
        Hides the combobox and its label (if it has one).

        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget:
            self.labelWidget.hide()

    def show(self):
        """
        Unhides the combobox and its label (if it has one).

        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()

# End of PM_FontComboBox ############################
