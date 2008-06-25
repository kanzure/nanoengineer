# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
StatProp.py - edit properties of Thermostat jig

$Id$
"""

from PyQt4 import QtGui
from PyQt4.Qt import QDialog
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QColorDialog
from commands.ThermostatProperties.StatPropDialog import Ui_StatPropDialog
from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf, get_widget_with_color_palette

class StatProp(QDialog, Ui_StatPropDialog):
    def __init__(self, stat, glpane):

        QDialog.__init__(self)
        self.setupUi(self)
        self.connect(self.cancel_btn, SIGNAL("clicked()"), self.reject)
        self.connect(self.ok_btn, SIGNAL("clicked()"), self.accept)
        self.connect(self.choose_color_btn, SIGNAL("clicked()"), self.change_jig_color)
        self.jig = stat
        self.glpane = glpane

        jigtype_name = self.jig.__class__.__name__
        self.setWindowIcon(QtGui.QIcon("ui/border/"+ jigtype_name))

    def setup(self):

        self.jig_attrs = self.jig.copyable_attrs_dict() # Save the jig's attributes in case of Cancel.

        # Jig color
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.jig_color_pixmap = get_widget_with_color_palette(
                self.jig_color_pixmap, self.jig_QColor)


        # Jig name
        self.nameLineEdit.setText(self.jig.name)

        self.molnameLineEdit.setText(self.jig.atoms[0].molecule.name)
        self.tempSpinBox.setValue(int(self.jig.temp))

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
        self.jig.temp = self.tempSpinBox.value()

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
