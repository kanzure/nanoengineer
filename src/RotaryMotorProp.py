# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from RotaryMotorPropDialog import *
from VQT import V

class RotaryMotorProp(RotaryMotorPropDialog):
    def __init__(self, rotMotor, glpane):

        RotaryMotorPropDialog.__init__(self)
        self.motor = rotMotor
        self.glpane = glpane
        self.setup()

    def setup(self):
        rotMotor = self.motor
        
        self.motor.originalColor = self.motor.normcolor
        
        self.nameLineEdit.setText(rotMotor.name)
        self.colorPixmapLabel.setPaletteBackgroundColor(
            QColor(int(rotMotor.normcolor[0]*255), 
                         int(rotMotor.normcolor[1]*255), 
                         int(rotMotor.normcolor[2]*255)))

        self.torqueLineEdit.setText(str(rotMotor.torque))
        self.speedLineEdit.setText(str(rotMotor.speed))

        self.lengthLineEdit.setText(str(rotMotor.length)) # motor length
        self.radiusLineEdit.setText(str(rotMotor.radius)) # motor radius
        self.sradiusLineEdit.setText(str(rotMotor.sradius)) # spoke radius
        
        self.applyPushButton.setEnabled(False)
        

    #########################
    # Change rotary motor color
    #########################
    def changeRotaryMotorColor(self):
        color = QColorDialog.getColor(
            QColor(int(self.motor.normcolor[0]*255), 
                         int(self.motor.normcolor[1]*255), 
                         int(self.motor.normcolor[2]*255)),
                         self, "ColorDialog")

        if color.isValid():
            self.colorPixmapLabel.setPaletteBackgroundColor(color)
            self.motor.color = self.motor.normcolor = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
            self.glpane.paintGL()

    #################
    # OK Button
    #################
    def accept(self):
        self.applyButtonPressed()
        self.motor.cancelled = False
        QDialog.accept(self)

    #################
    # Cancel Button
    #################
    def reject(self):
	    QDialog.reject(self)
	    self.motor.normcolor = self.motor.originalColor

    #################
    # Apply Button
    #################	
    def applyButtonPressed(self):
        
        self.motor.torque = float(str(self.torqueLineEdit.text()))
        self.motor.speed = float(str(self.speedLineEdit.text()))

        self.motor.length = float(str(self.lengthLineEdit.text())) # motor length
        self.motor.radius = float(str(self.radiusLineEdit.text())) # motor radius
        self.motor.sradius = float(str(self.sradiusLineEdit.text())) # spoke radius

        text =  QString(self.nameLineEdit.text())        
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.motor.name = str(text)
        self.nameLineEdit.setText(self.motor.name)
        self.motor.assy.w.update() # Update model tree
        self.motor.assy.modified = 1
               
        self.applyPushButton.setEnabled(False)

    def propertyChanged(self):
        self.applyPushButton.setEnabled(True)