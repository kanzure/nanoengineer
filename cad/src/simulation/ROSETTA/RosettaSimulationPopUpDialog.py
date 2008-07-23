"""
RosettaSimulationPopUpDialog.py 
Qt Dialog for setting the arguments for a rosetta simulation

@author: Urmi
@version: $Id$
@copyright:2008 Nanorex, Inc. See LICENSE file for details.
"""

from PyQt4.Qt import SIGNAL, SLOT
from PyQt4.Qt import QSizePolicy
from PyQt4.QtGui import QDialog, QLineEdit, QPushButton, QLabel, QCheckBox
from PyQt4.QtGui import QHBoxLayout, QVBoxLayout, QApplication, QTextEdit
from PyQt4.QtGui import QSpinBox, QSpacerItem
import string
from utilities.icon_utilities import geticon, getpixmap

class RosettaSimulationPopUpDialog(QDialog):
    
    def __init__(self, parent = None):
        self.parentWidget = parent
        super(RosettaSimulationPopUpDialog, self).__init__(parent)
        self.setWindowIcon(geticon('ui/border/Rosetta.png'))
        self.setWindowTitle("Rosetta Simulation Parameters")
        self._loadWidgets()
        self.connectSignals()
        self.show()
        return
    
    def _loadWidgets(self):
        layout = QVBoxLayout()  
        
        logoLayout = QHBoxLayout()
        self.imageLabel = QLabel()
        self.imageLabel.setPixmap(
                getpixmap("ui/images/Rosetta.png"))
        # Horizontal spacer
        hSpacer = QSpacerItem(1, 1, 
                              QSizePolicy.Expanding, 
                              QSizePolicy.Minimum)
        logoLayout.addItem(hSpacer)
        logoLayout.addWidget(self.imageLabel)
        logoLayout.addItem(hSpacer)
        
        idLayout = QHBoxLayout()
        
        self.label = QLabel("Enter number of simulations:")
        self.numSimSpinBox = QSpinBox()
        self.numSimSpinBox.setMinimum(1)
        self.numSimSpinBox.setMaximum(999)
        
        
        idLayout.addWidget(self.label)
        idLayout.addWidget(self.numSimSpinBox)
        
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
        
        self.otherOptionsLabel = QLabel("Command line options:")
        self.otherCommandLineOptions = QTextEdit()
        self.otherCommandLineOptions.setFixedHeight(80)
        idLayout3 = QVBoxLayout()
        idLayout3.addWidget(self.otherOptionsLabel)
        idLayout3.addWidget(self.otherCommandLineOptions)
        
        
        self.okButton = QPushButton("&OK")
        self.cancelButton = QPushButton("Cancel")
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
        
        layout.addLayout(logoLayout)
        layout.addLayout(idLayout)
        layout.addLayout(idLayout1)
        layout.addLayout(idLayout3)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        
        return
    
    def connectSignals(self):
        
        self.connect(self.ex1Checkbox, SIGNAL("stateChanged(int)"), self.update_ex1)
        self.connect(self.ex1aroCheckbox, SIGNAL("stateChanged(int)"), self.update_ex1aro)
        self.connect(self.ex2Checkbox, SIGNAL("stateChanged(int)"), self.update_ex2)
        self.connect(self.ex2aroOnlyCheckbox, SIGNAL("stateChanged(int)"), self.update_ex2aro_only)
        self.connect(self.ex3Checkbox, SIGNAL("stateChanged(int)"), self.update_ex3)
        self.connect(self.ex4Checkbox, SIGNAL("stateChanged(int)"), self.update_ex4)
        self.connect(self.rotOptCheckbox, SIGNAL("stateChanged(int)"), self.update_rot_opt)
        self.connect(self.tryBothHisTautomersCheckbox, SIGNAL("stateChanged(int)"), self.update_try_both_his_tautomers)
        self.connect(self.softRepDesignCheckbox, SIGNAL("stateChanged(int)"), self.update_soft_rep_design)
        self.connect(self.useElecRepCheckbox, SIGNAL("stateChanged(int)"), self.update_use_elec_rep)
        self.connect(self.norepackDisulfCheckbox, SIGNAL("stateChanged(int)"), self.update_norepack_disulf)
        
        self.connect(self.okButton, SIGNAL("clicked()"), self.getRosettaParameters)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        return
    
    def update_ex1(self, state):
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex1Checkbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex1 '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex1 ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_ex1aro(self, state):
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex1aroCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex1aro '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex1aro ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_ex2(self, state):
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex2Checkbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex2 '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex2 ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_ex2aro_only(self, state):
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex2aroOnlyCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex2aro_only '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex2aro_only ', '')    
            
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_ex3(self, state):
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex3Checkbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex3 '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex3 ', '')
        
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_ex4(self, state):
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex4Checkbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex4 '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex4 ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_rot_opt(self, state):
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.rotOptCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -rot_opt '
        else:
            otherOptionsText = otherOptionsText.replace(' -rot_opt ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_try_both_his_tautomers(self, state):
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.tryBothHisTautomersCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -try_both_his_tautomers '
        else:
            otherOptionsText = otherOptionsText.replace(' -try_both_his_tautomers ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_soft_rep_design(self, state):
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.softRepDesignCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -soft_rep_design '
        else:
            otherOptionsText = otherOptionsText.replace(' -soft_rep_design ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_use_elec_rep(self, state):
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.useElecRepCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -use_electrostatic_repulsion '
        else:
            otherOptionsText = otherOptionsText.replace(' -use_electrostatic_repulsion ', '')    
        self.otherCommandLineOptions.setText(otherOptionsText)        
        return
    
    def update_norepack_disulf(self, state):
        """
        Update the command text edit depending on the state of the update_no_repack
        checkbox
        @param state:state of the update_no_repack checkbox
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.norepackDisulfCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -norepack_disulf '
        else:
            otherOptionsText = otherOptionsText.replace(' -norepack_disulf ', '')      
        self.otherCommandLineOptions.setText(otherOptionsText)        
        return
    
    def getRosettaParameters(self):
        """
        Get all the parameters from the Rosetta pop up dialog
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        numSim = self.numSimSpinBox.value()
        self.parentWidget.setRosettaParameters(numSim, otherOptionsText)                                        
        self.close()
        self.emit(SIGNAL("editingFinished()"))
        return