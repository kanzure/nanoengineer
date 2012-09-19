# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
JigProp.py

$Id$

History: Original code from GroundProps.py and cleaned up by Mark.

"""

__author__ = "Mark"

from PyQt4.Qt import QDialog
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QColorDialog
from utilities.icon_utilities import geticon

from command_support.JigPropDialog import Ui_JigPropDialog

from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf
from widgets.widget_helpers import get_widget_with_color_palette

# This Jig Property dialog and its slot methods can be used for any simple jig
# that has only a name and a color attribute changable by the user.
# It is currently used by both the Anchor and AtomSet jig.  Mark 050928.

class JigProp(QDialog, Ui_JigPropDialog):
    """
    This Jig Property dialog and its slot methods can be used for any simple jig
    that has only a name and a color attribute changable by the user.
    It is currently used by both the Anchor and AtomSet jig.
    """
    def __init__(self, jig, glpane):
        """
        Constructor for the class JigProp.
        @param jig: the jig whose property dialog will be shown
        @type  jig: L{Jig}
        @param glpane: GLPane object
        @type  glpane: L{GLPane}
        """

        QDialog.__init__(self)
        self.setupUi(self)
        self.connect(self.cancel_btn, SIGNAL("clicked()"), self.reject)
        self.connect(self.ok_btn, SIGNAL("clicked()"), self.accept)
        self.connect(self.choose_color_btn,
                     SIGNAL("clicked()"),
                     self.change_jig_color)

        # Set the dialog's border icon and caption based on the jig type.
        jigtype_name = jig.__class__.__name__

        # Fixes bug 1208. mark 060112.
        self.setWindowIcon(geticon("ui/border/"+ jigtype_name))

        self.setWindowTitle(jigtype_name + " Properties")

        self.jig = jig
        self.glpane = glpane

    def setup(self):
        """
        Initializes the dialog and it's widgets
        """

        # Save the jig's attributes in case of Cancel.
        self.jig_attrs = self.jig.copyable_attrs_dict()

        # Jig color
        # Used as default color by Color Chooser
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor)
        self.jig_color_pixmap = get_widget_with_color_palette(
            self.jig_color_pixmap, self.jig_QColor)

        # Jig name
        self.nameLineEdit.setText(self.jig.name)

    def change_jig_color(self):
        """
        Slot method to change the jig's color.
        """
        color = QColorDialog.getColor(self.jig_QColor, self)

        if color.isValid():
            self.jig_QColor = color
            self.jig_color_pixmap = get_widget_with_color_palette(
                self.jig_color_pixmap, self.jig_QColor)
            self.jig.color = self.jig.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()

    def accept(self):
        """
        Slot for the 'OK' button
        """
        self.jig.try_rename(self.nameLineEdit.text())
        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        QDialog.accept(self)

    def reject(self):
        """
        Slot for the 'Cancel' button
        """
        self.jig.attr_update(self.jig_attrs) # Restore attributes of the jig.
        self.glpane.gl_update()
        QDialog.reject(self)
