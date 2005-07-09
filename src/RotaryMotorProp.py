# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
RotaryMotorProp.py

$Id$
"""

from qt import *
from RotaryMotorPropDialog import *
from VQT import V

class RotaryMotorProp(RotaryMotorPropDialog):
    def __init__(self, motor, glpane):

        RotaryMotorPropDialog.__init__(self)
        self.motor = motor
        self.glpane = glpane
        self.setup()

    def setup(self):
        motor = self.motor
        
        self.originalColor = self.motor.normcolor
        
        self.nameLineEdit.setText(motor.name)
        self.colorPixmapLabel.setPaletteBackgroundColor(
            QColor(int(motor.normcolor[0]*255), 
                         int(motor.normcolor[1]*255), 
                         int(motor.normcolor[2]*255)))

        self.torqueLineEdit.setText(str(motor.torque))
        self.speedLineEdit.setText(str(motor.speed))

        self.lengthLineEdit.setText(str(motor.length)) # motor length
        self.radiusLineEdit.setText(str(motor.radius)) # motor radius
        self.sradiusLineEdit.setText(str(motor.sradius)) # spoke radius
        

    def choose_color(self):
        color = QColorDialog.getColor(
            QColor(int(self.motor.normcolor[0]*255), 
                         int(self.motor.normcolor[1]*255), 
                         int(self.motor.normcolor[2]*255)),
                         self, "ColorDialog")

        if color.isValid():
            self.colorPixmapLabel.setPaletteBackgroundColor(color)
            self.motor.color = self.motor.normcolor = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
            self.glpane.gl_update()


    #################
    # Cancel Button
    #################
    def reject(self):
        QDialog.reject(self)
        self.motor.color = self.motor.normcolor = self.originalColor
        self.glpane.gl_update()

    #################
    # OK Button
    #################
    def accept(self):
        QDialog.accept(self)
        
        self.motor.cancelled = False
        
        text =  QString(self.nameLineEdit.text())        
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.motor.name = str(text)
        
        self.motor.torque = float(str(self.torqueLineEdit.text()))
        self.motor.speed = float(str(self.speedLineEdit.text()))

        self.motor.length = float(str(self.lengthLineEdit.text())) # motor length
        self.motor.radius = float(str(self.radiusLineEdit.text())) # motor radius
        self.motor.sradius = float(str(self.sradiusLineEdit.text())) # spoke radius
        
        self.motor.assy.w.win_update() # Update model tree
        self.motor.assy.changed()