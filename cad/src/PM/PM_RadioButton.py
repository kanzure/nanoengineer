# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_RadioButton.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrRadioButton out of PropMgrBaseClass.py into this
file and renamed it PM_RadioButton.
"""

from PyQt4.Qt import QRadioButton
from PyQt4.Qt import QWidget

class PM_RadioButton( QRadioButton ):
    """
    The PM_RadioButton widget provides a radio button for a
    Property Manager group box.
    """

    defaultIsChecked = False
    setAsDefault = False

    labelWidget  = None  # Needed for PM_GroupBox.addPmWidget().
    label        = ""    # Needed for PM_GroupBox.addPmWidget().
    labelColumn  = 0     # Needed for PM_GroupBox.addPmWidget().
    spanWidth    = False # Needed for PM_GroupBox.addPmWidget().

    def __init__(self,
                 parentWidget,
                 text         = '',
                 isChecked    = False,
                 setAsDefault = False
                 ):
        """
        Appends a QRadioButton widget to <parentWidget>, a property manager
        group box.

        Appends a QCheckBox (Qt) widget to the bottom of I{parentWidget},
        a Property Manager group box.

        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox

        @param text: The text that appears to the right of the radio button.
        @type  text: str

        @param isChecked: Set's the radio button's check state. The default is
                          True.
        @type  isChecked: bool

        @param setAsDefault: If True, will restore I{isChecked} when the
                             "Restore Defaults" button is clicked.
        @type  setAsDefault: bool

        @see: U{B{QRadioButton}<http://doc.trolltech.com/4/qradiobutton.html>}

        """

        QRadioButton.__init__(self)

        self.parentWidget = parentWidget
        self.setAsDefault = setAsDefault

        self.setText(text)

        self.setCheckable(True)
        self.setChecked(isChecked)

        self.defaultIsChecked = isChecked
        self.setAsDefault     = setAsDefault

        parentWidget.addPmWidget(self)

    def restoreDefault(self):
        """
        Restores the default check state.
        """
        if self.setAsDefault:
            self.setChecked(self.defaultIsChecked)

# End of PM_RadioButton ############################