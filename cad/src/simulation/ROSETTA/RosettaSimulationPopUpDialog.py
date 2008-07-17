"""
RosettaSimulationPopUpDialog.py 
Qt Dialog for setting the arguments for a rosetta simulation

@author: Urmi
@version: $Id$
@copyright:2008 Nanorex, Inc. See LICENSE file for details.
"""

from PyQt4.Qt import SIGNAL, SLOT
from PyQt4.QtGui import QDialog, QLineEdit, QPushButton, QLabel, QCheckBox
from PyQt4.QtGui import QHBoxLayout, QVBoxLayout, QApplication


class RosettaSimulationPopUpDialog(QDialog):
    def __init__(self, parent = None):
        self.parentWidget = parent
        super(RosettaSimulationPopUpDialog, self).__init__(parent)
        self.text = ''
        self.setWindowTitle("Rosetta Simulation Parameters")
        
        layout = QVBoxLayout()
        
        idLayout = QHBoxLayout()
        self.label = QLabel("Enter number of simulations:")
        self.lineEdit = QLineEdit()
        #self.lineEdit.setMaxLength(8) # Check with Piotr about this.
        idLayout.addWidget(self.label)
        idLayout.addWidget(self.lineEdit)
        
        #rosetta simulation parameters checkboxes
        idLayout1 = QVBoxLayout()
        self.ex1Checkbox = QCheckBox("Expand rotamer library for chi1 angle")
        self.ex1aroCheckbox = QCheckBox("Use large chi1 library for aromatic residues")
        self.ex2Checkbox = QCheckBox("Expand rotamer library for chi2 angle")
        self.ex2aroOnlyCheckbox = QCheckBox("Use large chi2 library only for aromatic residues")
        self.ex3Checkbox = QCheckBox("Expand rotamer library for chi3 angle")
        self.ex4Checkbox = QCheckBox("Expand rotamer library for chi4 angle")
        self.rotOptCheckbox = QCheckBox("Optimize one-body energy")
        self.tryBothHisTautomersCheckbox = QCheckBox("Try both histidine tautomers")
        self.softRepDesignCheckbox = QCheckBox("Use softer Lennard-Jones repulsive term")
        self.useElecRepCheckbox = QCheckBox("Use electrostatic repulsion")
        self.norepackDisulfCheckbox = QCheckBox("Don't re-pack disulphide bonds")
        
        
        #self.lineEdit.setMaxLength(8) # Check with Piotr about this.
        idLayout1.addWidget(self.ex1Checkbox)
        idLayout1.addWidget(self.ex1aroCheckbox)
        idLayout1.addWidget(self.ex2Checkbox)
        idLayout1.addWidget(self.ex2aroOnlyCheckbox)
        idLayout1.addWidget(self.ex3Checkbox)
        idLayout1.addWidget(self.ex4Checkbox)
        idLayout1.addWidget(self.rotOptCheckbox)
        idLayout1.addWidget(self.tryBothHisTautomersCheckbox)
        idLayout1.addWidget(self.softRepDesignCheckbox)
        idLayout1.addWidget(self.useElecRepCheckbox)
        idLayout1.addWidget(self.norepackDisulfCheckbox)
        
        self.otherOptionsLabel = QLabel("Other command line options:")
        self.otherCommandLineOptions = QLineEdit()
        idLayout3 = QHBoxLayout()
        idLayout3.addWidget(self.otherOptionsLabel)
        idLayout3.addWidget(self.otherCommandLineOptions)
        
        
        self.okButton = QPushButton("&OK")
        self.cancelButton = QPushButton("Cancel")
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
        
        layout.addLayout(idLayout)
        layout.addLayout(idLayout1)
        layout.addLayout(idLayout3)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        
        self.connect(self.lineEdit, SIGNAL("returnPressed()"), self.getRosettaParameters)
        self.connect(self.okButton, SIGNAL("clicked()"), self.getRosettaParameters)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        self.show()
        return
        
    def getRosettaParameters(self):
        
        if self.ex1Checkbox.isChecked() == True:
            ex1 = True
        else:
            ex1 = False
        if self.ex1aroCheckbox.isChecked() == True:
            ex1aro = True
        else:
            ex1aro = False 
        if self.ex2Checkbox.isChecked() == True:
            ex2 = True
        else:
            ex2 = False     
        if self.ex2aroOnlyCheckbox.isChecked() == True:
            ex2aro_only = True
        else:
            ex2aro_only = False      
        if self.ex3Checkbox.isChecked() == True:
            ex3 = True
        else:
            ex3 = False    
        if self.ex4Checkbox.isChecked() == True:
            ex4 = True
        else:
            ex4 = False    
        if self.rotOptCheckbox.isChecked() == True:
            rot_opt = True
        else:
            rot_opt = False 
        if self.tryBothHisTautomersCheckbox.isChecked() == True:
            try_both_his_tautomers = True
        else:
            try_both_his_tautomers = False 
        if self.softRepDesignCheckbox.isChecked() == True:
            soft_rep_design = True
        else:
            soft_rep_design = False 
        if self.useElecRepCheckbox.isChecked() == True:
            use_electrostatic_repulsion = True
        else:
            use_electrostatic_repulsion = False    
        if self.norepackDisulfCheckbox.isChecked() == True:
            norepack_disulf = True
        else:
            norepack_disulf = False      
        text = str(self.lineEdit.text())
        otherOptionsText = str(self.otherCommandLineOptions.text())
        self.parentWidget.setRosettaParameters(text, ex1, ex1aro,
                                               ex2, ex2aro_only, ex3, ex4, rot_opt,
                                               try_both_his_tautomers, soft_rep_design,
                                               use_electrostatic_repulsion, norepack_disulf, 
                                               otherOptionsText)                                        
        self.close()
        self.emit(SIGNAL("editingFinished()"))
        return