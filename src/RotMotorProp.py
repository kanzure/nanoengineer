# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from RotMotorPropDialog import *
from VQT import V

class RotMotorProp(RotMotorPropDialog):
    def __init__(self, rotMotor):
        RotMotorPropDialog.__init__(self)
        self.motor = rotMotor

        self.torque.setText(str(rotMotor.torque))
        self.speed.setText(str(rotMotor.speed))
        self.aX.setText(str(rotMotor.axis[0]))
        self.aY.setText(str(rotMotor.axis[1]))
        self.aZ.setText(str(rotMotor.axis[2]))

        self.cX.setText(str(rotMotor.center[0]))
        self.cY.setText(str(rotMotor.center[1]))
        self.cZ.setText(str(rotMotor.center[2]))
        
        
        strList = map(lambda i: rotMotor.atoms[i].element.symbol + str(i), 
                                                 range(0, len(rotMotor.atoms)))
        self.atomsList.insertStrList(strList, 0)
        

    def accept(self):
        self.motor.torque = float(str(self.torque.text()))
        self.motor.speed = float(str(self.speed.text()))
    	self.motor.axis[0] = float(str(self.aX.text()))
	self.motor.axis[1] = float(str(self.aY.text()))
	self.motor.axis[2] = float(str(self.aZ.text()))

        self.motor.center[0] = float(str(self.cX.text()))
	self.motor.center[1] = float(str(self.cY.text()))
	self.motor.center[2] = float(str(self.cZ.text()))

        QDialog.accept(self)

    def reject(self):
	
        QDialog.reject(self)

         

