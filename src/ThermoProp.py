# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ThermoProp.py

$Id$
"""

from qt import *
from ThermoPropDialog import *
from widgets import RGBf_to_QColor, QColor_to_RGBf

class ThermoProp(ThermoPropDialog):
    def __init__(self, thermo, glpane):

        ThermoPropDialog.__init__(self)
        self.jig = thermo
        self.glpane = glpane

    def setup(self):
        
        self.jig_attrs = self.jig.copyable_attrs_dict() # Save the jig's attributes in case of Cancel.
        
        # Jig color
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.jig_color_pixmap.setPaletteBackgroundColor(self.jig_QColor)

        # Jig name
        self.nameLineEdit.setText(self.jig.name)
        
        self.molnameLineEdit.setText(self.jig.atoms[0].molecule.name)
        
    def change_jig_color(self):
        '''Slot method to change the jig's color.'''
        color = QColorDialog.getColor(self.jig_QColor, self, "ColorDialog")

        if color.isValid():
            self.jig_color_pixmap.setPaletteBackgroundColor(color)
            self.jig_QColor = color
            self.jig.color = self.jig.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()

    def accept(self):
        '''Slot for the 'OK' button '''
        self.jig.try_rename(str(self.nameLineEdit.text()))
        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        QDialog.accept(self)
        
    def reject(self):
        '''Slot for the 'Cancel' button '''
        self.jig.attr_update(self.jig_attrs) # Restore attributes of the jig.
        self.glpane.gl_update()
        QDialog.reject(self)