from qt import *
from LinearMotorPropDialog import *


class LinearMotorProp(LinearMotorPropDialog):
    def __init__(self, linearMotor):
        LinearMotorPropDialog.__init__(self)
        self.motor = linearMotor

        self.stiffness.setText(str(linearMotor.stiffness))
        self.force.setText(str(linearMotor.force))
        self.aX.setText(str(linearMotor.axis[0]))
        self.aY.setText(str(linearMotor.axis[1]))
        self.aZ.setText(str(linearMotor.axis[2]))

        self.cX.setText(str(linearMotor.center[0]))	
        self.cY.setText(str(linearMotor.center[1]))
        self.cZ.setText(str(linearMotor.center[2]))
        
        
        strList = map(lambda i: linearMotor.atoms[i].element.symbol + str(i), 
                                                 range(0, len(linearMotor.atoms)))
        self.atomsList.insertStrList(strList, 0)
        

    def accept(self):
        self.motor.stiffness = float(str(self.stiffness.text()))
        self.motor.force = float(str(self.force.text()))
    	self.motor.axis[0] = float(str(self.aX.text()))
	self.motor.axis[1] = float(str(self.aY.text()))
	self.motor.axis[2] = float(str(self.aZ.text()))

        self.motor.center[0] = float(str(self.cX.text()))
	self.motor.center[1] = float(str(self.cY.text()))
	self.motor.center[2] = float(str(self.cZ.text()))

   
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

         

