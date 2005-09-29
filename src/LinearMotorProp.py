# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
LinearMotorProp.py

$Id$
"""

from qt import *
from LinearMotorPropDialog import *
from widgets import RGBf_to_QColor, QColor_to_RGBf
import copy

class LinearMotorProp(LinearMotorPropDialog):
    def __init__(self, motor, glpane):

        LinearMotorPropDialog.__init__(self)
        self.jig = motor
        self.glpane = glpane
        self.setup()

    def setup(self):
        
        # Need to ask Bruce about the pros/cons of copying the jig here.  
        # It sure would be nice to use the copy of the jig in self.reject() like this:
        #     self.jig = self.original_jig
        # so I didn't have to copy each attr back when the user hit the Cancel button.  Mark 050929.
        self.original_jig = copy.copy(self.jig) 
        
        # Jig color
        # self.original_normcolor = self.jig.normcolor
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.jig_color_pixmap.setPaletteBackgroundColor(self.jig_QColor)

        self.nameLineEdit.setText(self.jig.name)
        self.stiffnessLineEdit.setText(str(self.jig.stiffness))
        self.forceLineEdit.setText(str(self.jig.force))
        self.lengthLineEdit.setText(str(self.jig.length))
        self.widthLineEdit.setText(str(self.jig.width))
        self.sradiusLineEdit.setText(str(self.jig.sradius)) # spoke radius

    def change_jig_color(self):
        '''Slot method to change the jig's color.'''
        color = QColorDialog.getColor(self.jig_QColor, self, "ColorDialog")

        if color.isValid():
            self.jig_color_pixmap.setPaletteBackgroundColor(color)
            self.jig_QColor = color
            self.jig.color = self.jig.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()
            
    def change_motor_size(self, gl_update=True):
        '''Slot method to change the jig's length, width and/or spoke radius.'''
        self.jig.length = float(str(self.lengthLineEdit.text())) # motor length
        self.jig.width = float(str(self.widthLineEdit.text())) # motor width
        self.jig.sradius = float(str(self.sradiusLineEdit.text())) # spoke radius
        if gl_update:
            self.glpane.gl_update()
        
    def accept(self):
        '''Slot for the 'OK' button '''
        
        self.jig.cancelled = False
        
        text =  QString(self.nameLineEdit.text())
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.jig.name = str(text)
        
        self.jig.force = float(str(self.forceLineEdit.text()))
        self.jig.stiffness = float(str(self.stiffnessLineEdit.text()))
        
        self.change_motor_size(gl_update=False)
        
        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        QDialog.accept(self)
        
    def reject(self):
        '''Slot for the 'Cancel' button '''
        #self.jig.color = self.jig.normcolor = self.original_normcolor
        self.jig.color = self.jig.normcolor = self.original_jig.normcolor
        self.jig.length = self.original_jig.force
        self.jig.length = self.original_jig.stiffness
        self.jig.length = self.original_jig.length
        self.jig.width = self.original_jig.width
        self.jig.sradius = self.original_jig.sradius

        self.glpane.gl_update()
        QDialog.reject(self)