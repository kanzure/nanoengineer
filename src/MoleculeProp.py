# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from MoleculePropDialog import *
from RotaryMotorProp import RotaryMotorProp
from LinearMotorProp import LinearMotorProp
from GroundProp import GroundProp

from gadgets import *


class MoleculeProp(MoleculePropDialog):
    def __init__(self, mol):
        MoleculePropDialog.__init__(self)
        self.mol = mol
        
        self.nameLineEdit.setText(mol.name)
        self.applyPushButton.setEnabled(False)
        
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
        
        
        for g in mol.gadgets:
                self.jigsComboBox.insertItem(g.name)
                
        
        if len(mol.gadgets) > 0: 
                self.propPushButton.setEnabled(True)        
    
    def nameChanged(self):
        self.applyPushButton.setEnabled(True)
                
    def applyButtonClicked(self):    
        self.mol.name = str(self.nameLineEdit.text())
        self.applyPushButton.setEnabled(False)            

    def propClickedButton(self):
        index = self.jigsComboBox.currentItem()
        g = self.mol.gadgets[index]
        glpane = self.mol.assy.o
        
        if isinstance(g, RotaryMotor):
              rMotorDialog = RotaryMotorProp(g, glpane)
              if rMotorDialog.exec_loop() ==QDialog.Accepted:
                      self.jigsComboBox.setCurrentText(g.name)
                      glpane.win.modelTreeView.updateTreeItem(g)
                      
        elif isinstance(g, LinearMotor):
              lMotorDialog = LinearMotorProp(g, glpane)
              if lMotorDialog.exec_loop() == QDialog.Accepted:
                      self.jigsComboBox.setCurrentText(g.name)
                      glpane.win.modelTreeView.updateTreeItem(g)
        elif isinstance(g, Ground):
              groundDialog = GroundProp(g,  glpane)
              if groundDialog.exec_loop() == QDialog.Accepted:
                      self.jigsComboBox.setCurrentText(g.name)
                      glpane.win.modelTreeView.updateTreeItem(g)
            
    def accept(self):
        self.applyButtonClicked()    
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

         