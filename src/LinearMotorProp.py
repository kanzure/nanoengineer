# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from LinearMotorPropDialog import *
from VQT import V

class LinearMotorProp(LinearMotorPropDialog):
    def __init__(self, linearMotor, glpane):

        LinearMotorPropDialog.__init__(self)
        self.motor = linearMotor
        self.glpane = glpane
        self.setup()

    def setup(self):
        linearMotor = self.motor
        
        self.nameLineEdit.setText(linearMotor.name)

        self.colorPixmapLabel.setPaletteBackgroundColor(
            QColor(int(linearMotor.color[0]*255), 
                         int(linearMotor.color[1]*255), 
                         int(linearMotor.color[2]*255)))
                         
        self.stiffnessLineEdit.setText(str(linearMotor.stiffness))
        self.forceLineEdit.setText(str(linearMotor.force))
        self.axLineEdit.setText(str(linearMotor.axis[0]))
        self.ayLineEdit.setText(str(linearMotor.axis[1]))
        self.azLineEdit.setText(str(linearMotor.axis[2]))

        self.cxLineEdit.setText(str(linearMotor.center[0]))
        self.cyLineEdit.setText(str(linearMotor.center[1]))
        self.czLineEdit.setText(str(linearMotor.center[2]))
        
        strList = map(lambda i: linearMotor.atoms[i].element.symbol + str(i),
                                                range(0, len(linearMotor.atoms)))
        self.atomsComboBox.insertStrList(strList, 0)

        self.applyPushButton.setEnabled(False)
        

    #########################
    # Change linear motor color
    #########################
    def changeLinearMotorColor(self):

        color = QColorDialog.getColor(
            QColor(int(self.motor.color[0]*255), 
                         int(self.motor.color[1]*255), 
                         int(self.motor.color[2]*255)),
                         self, "ColorDialog")
                        
        if color.isValid():
            self.colorPixmapLabel.setPaletteBackgroundColor(color)
            self.motor.color = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
            self.glpane.paintGL()


    #################
    # OK Button
    #################
    def accept(self):
        self.applyButtonPressed()
        QDialog.accept(self)

    #################
    # Cancel Button
    #################
    def reject(self):
	    QDialog.reject(self)

    #################
    # Apply Button
    #################	
    def applyButtonPressed(self):
        
        self.motor.name = self.nameLineEdit.text()
        self.motor.force = float(str(self.forceLineEdit.text()))
        self.motor.stiffness = float(str(self.stiffnessLineEdit.text()))
        self.motor.axis[0] = float(str(self.axLineEdit.text()))
        self.motor.axis[1] = float(str(self.ayLineEdit.text()))
        self.motor.axis[2] = float(str(self.azLineEdit.text()))

        self.motor.center[0] = float(str(self.cxLineEdit.text()))
        self.motor.center[1] = float(str(self.cyLineEdit.text()))
        self.motor.center[2] = float(str(self.czLineEdit.text()))
        
        self.applyPushButton.setEnabled(False)
	
    def propertyChanged(self):
        self.applyPushButton.setEnabled(True)	