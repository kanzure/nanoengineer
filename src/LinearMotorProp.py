# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from LinearMotorPropDialog import *


class LinearMotorProp(LinearMotorPropDialog):
    def __init__(self, linearMotor, glpane):

        LinearMotorPropDialog.__init__(self)
        self.motor = linearMotor
        self.glpane = glpane

        self.nameLineEdit.setText(linearMotor.name)
        self.stiffnessLineEdit.setText(str(linearMotor.stiffness))
        self.forceLineEdit.setText(str(linearMotor.force))
        self.axLineEdit.setText(str(linearMotor.axis[0]))
        self.ayLineEdit.setText(str(linearMotor.axis[1])) 
        self.azLineEdit.setText(str(linearMotor.axis[2]))

        self.cxLineEdit.setText(str(linearMotor.center[0]))	
        self.cyLineEdit.setText(str(linearMotor.center[1]))
        self.czLineEdit.setText(str(linearMotor.center[2]))

        self.colorPixmapLabel.setPaletteBackgroundColor(linearMotor.color)

        self.nameLineEdit.setText(linearMotor.name)
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
    # Change motor color
    #########################
    def changeLinearMotorColor(self):
        color = QColorDialog.getColor(QColor("linen"), self, "ColorDialog")
        self.colorPixmapLabel.setPaletteBackgroundColor(color)
        
        self.motor.molecule.havelist = 0
        self.motor.color = color
        self.glpane.paintGL()

    def accept(self):           # OK Button
        self.applyButtonPressed()  
        QDialog.accept(self)

    def reject(self):   # Cancel Button
        QDialog.reject(self)

    def applyButtonPressed(self):   # Apply Button

        self.motor.name = self.nameLineEdit.text()
        self.motor.stiffness = float(str(self.stiffnessLineEdit.text()))
        self.motor.force = float(str(self.forceLineEdit.text()))
        self.motor.axis[0] = float(str(self.axLineEdit.text()))
        self.motor.axis[1] = float(str(self.ayLineEdit.text()))
        self.motor.axis[2] = float(str(self.azLineEdit.text()))

        self.motor.center[0] = float(str(self.cxLineEdit.text()))
        self.motor.center[1] = float(str(self.cyLineEdit.text()))
        self.motor.center[2] = float(str(self.czLineEdit.text()))

        self.applyPushButton.setEnabled(False)

    def propertyChanged(self):    
        self.applyPushButton.setEnabled(True)