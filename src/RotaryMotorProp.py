# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from RotaryMotorPropDialog import *
from VQT import V

class RotaryMotorProp(RotaryMotorPropDialog):
    def __init__(self, rotMotor):
        RotaryMotorPropDialog.__init__(self)
        self.motor = rotMotor

        self.torqueLineEdit.setText(str(rotMotor.torque))
        self.speedLineEdit.setText(str(rotMotor.speed))
        self.axLineEdit.setText(str(rotMotor.axis[0]))
        self.ayLineEdit.setText(str(rotMotor.axis[1]))
        self.azLineEdit.setText(str(rotMotor.axis[2]))

        self.cxLineEdit.setText(str(rotMotor.center[0]))
        self.cyLineEdit.setText(str(rotMotor.center[1]))
        self.czLineEdit.setText(str(rotMotor.center[2]))
        
        strList = map(lambda i: rotMotor.atoms[i].element.symbol + str(i),
                                                range(0, len(rotMotor.atoms)))
        self.atomsComboBox.insertStrList(strList, 0)
        

    #################
    # OK Button
    #################

    def accept(self):
        self.motor.torque = float(str(self.torqueLineEdit.text()))
        self.motor.speed = float(str(self.speedLineEdit.text()))
    	self.motor.axis[0] = float(str(self.axLineEdit.text()))
	self.motor.axis[1] = float(str(self.ayLineEdit.text()))
	self.motor.axis[2] = float(str(self.azLineEdit.text()))

        self.motor.center[0] = float(str(self.cxLineEdit.text()))
	self.motor.center[1] = float(str(self.cyLineEdit.text()))
	self.motor.center[2] = float(str(self.czLineEdit.text()))

        QDialog.accept(self)

    #################
    # Cancel Button
    #################

    def reject(self):
	
        QDialog.reject(self)