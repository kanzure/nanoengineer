# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
RotaryMotorProp.py

$Id$
"""

from qt import *
from RotaryMotorPropDialog import *
from widgets import RGBf_to_QColor, QColor_to_RGBf
import copy

class RotaryMotorProp(RotaryMotorPropDialog):
    def __init__(self, motor, glpane):

        RotaryMotorPropDialog.__init__(self)
        self.jig = motor
        self.glpane = glpane

    def setup(self):
        
        self.jig_attrs = self.jig.copyable_attrs_dict() # Save the jig's attributes in case of Cancel.
        
        # Jig color
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.jig_color_pixmap.setPaletteBackgroundColor(self.jig_QColor)

        self.nameLineEdit.setText(self.jig.name)
        self.torqueLineEdit.setText(str(self.jig.torque))
        self.initialSpeedLineEdit.setText(str(self.jig.initial_speed))
        self.speedLineEdit.setText(str(self.jig.speed))
        self.lengthLineEdit.setText(str(self.jig.length))
        self.radiusLineEdit.setText(str(self.jig.radius))
        self.sradiusLineEdit.setText(str(self.jig.sradius)) # spoke radius
        self.enable_minimize_checkbox.setChecked(self.jig.enable_minimize)

    def change_jig_color(self):
        '''Slot method to change the jig's color.'''
        color = QColorDialog.getColor(self.jig_QColor, self, "ColorDialog")

        if color.isValid():
            self.jig_color_pixmap.setPaletteBackgroundColor(color)
            self.jig_QColor = color
            self.jig.color = self.jig.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()
            
    def change_motor_size(self, gl_update=True):
        '''Slot method to change the jig's length, radius and/or spoke radius.'''
        self.jig.length = float(str(self.lengthLineEdit.text())) # motor length
        self.jig.radius = float(str(self.radiusLineEdit.text())) # motor radius
        self.jig.sradius = float(str(self.sradiusLineEdit.text())) # spoke radius
        if gl_update:
            self.glpane.gl_update()
        
    def accept(self):
        '''Slot for the 'OK' button '''
        self.jig.cancelled = False
        self.jig.try_rename(self.nameLineEdit.text())
        self.jig.torque = float(str(self.torqueLineEdit.text()))
        self.jig.initial_speed = float(str(self.initialSpeedLineEdit.text()))
        self.jig.speed = float(str(self.speedLineEdit.text()))
        
        self.change_motor_size(gl_update=False)
        
        self.jig.enable_minimize = self.enable_minimize_checkbox.isChecked()
        
        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        QDialog.accept(self)
        
    def reject(self):
        '''Slot for the 'Cancel' button '''
        self.jig.attr_update(self.jig_attrs) # Restore attributes of the jig.
        self.glpane.gl_update()
        QDialog.reject(self)