# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from MoleculePropDialog import *
from RotaryMotorProp import RotaryMotorProp
from LinearMotorProp import LinearMotorProp

from gadgets import *


class MoleculeProp(MoleculePropDialog):
    def __init__(self, mol):
        MoleculePropDialog.__init__(self)
        self.mol = mol
        self.flag = 0 # First time, the next line will cause nameChanged() signal
        
        self.nameLineEdit.setText(mol.name)
        
        self.atomsTextBrowser.setReadOnly(True)
        totalAtomsStr = "Total Atoms: " + str(len(mol.atoms)) + "\n\n"
        ele2Num = {}
        
        for a in self.mol.atoms.itervalues():
             if ele2Num.has_key(a.element.symbol):
                value = ele2Num[a.element.symbol]
                ele2Num[a.element.symbol] = value + 1
             else:
                ele2Num[a.element.symbol] = 1
                
        for item in ele2Num.iteritems():
            eleStr = item[0] + ": " + str(item[1]) + "\n"
            totalAtomsStr += eleStr
              
        
        self.atomsTextBrowser.setText(totalAtomsStr)
        
        gIndex = 1
        for g in mol.gadgets:
                self.jigsComboBox.insertItem(g.__class__.__name__ + str(gIndex))
                gIndex += 1
        
        if gIndex > 1: 
                self.propPushButton.setEnabled(True)        
    
    def nameChanged(self):
        if self.flag:    
                self.applyPushButton.setEnabled(True)
        else:  self.flag = 1                
                
    def applyButtonClicked(self):    
        self.mol.name = str(self.nameLineEdit.text())
        self.applyPushButton.setEnabled(False)            

    def propClickedButton(self):
        index = self.jigsComboBox.currentItem()
        g = self.mol.gadgets[index]
        if isinstance(g, motor):
              rMotorDialog = RotaryMotorProp(g)
              rMotorDialog.exec_loop()
        elif isinstance(g, LinearMotor):
              lMotorDialog = LinearMotorProp(g)
              lMotorDialog.exec_loop()
        elif isinstance(g, ground):
              pass
            
    def accept(self):
        self.applyButtonClicked()    
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

         