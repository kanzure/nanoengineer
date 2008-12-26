# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
FixedBBProteinSim_PropertyManager.py

The FixedBBProteinSim_PropertyManager class provides a Property Manager 
for the B{Fixed Backbone protein sequence design} command on the flyout toolbar in the 
Build > Protein mode. 

@author: Urmi
@version: $Id$ 
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

"""
import string
import foundation.env as env

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4 import QtGui
from PyQt4.Qt import QString
from PM.PM_PushButton   import PM_PushButton
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_TextEdit import PM_TextEdit
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_Constants import PM_DONE_BUTTON
from PM.PM_Constants import PM_WHATS_THIS_BUTTON
from PM.PM_SpinBox import PM_SpinBox

from command_support.Command_PropertyManager import Command_PropertyManager

_superclass = Command_PropertyManager

class FixedBBProteinSim_PropertyManager(Command_PropertyManager):
    """
    The FixedBBProteinSim_PropertyManager class provides a Property Manager 
    for the B{Fixed backbone Protein Sequence Design} command on the flyout toolbar in the 
    Build > Protein > Simulate mode. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Fixed Backbone Design"
    pmName        =  title
    iconPath      = "ui/actions/Command Toolbar/BuildProtein/FixedBackbone.png"

    
    def __init__( self, command ):
        """
        Constructor for the property manager.
        """

        _superclass.__init__(self, command)

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        msg = "Choose from the various options below to design "\
            "an optimized <b>fixed backbone protein sequence</b> with Rosetta."
        self.updateMessage(msg)            
        return
    

    def connect_or_disconnect_signals(self, isConnect = True):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
        
        
        change_connect(self.ex1Checkbox, SIGNAL("stateChanged(int)"), self.update_ex1)
        change_connect(self.ex1aroCheckbox, SIGNAL("stateChanged(int)"), self.update_ex1aro)
        change_connect(self.ex2Checkbox, SIGNAL("stateChanged(int)"), self.update_ex2)
        change_connect(self.ex2aroOnlyCheckbox, SIGNAL("stateChanged(int)"), self.update_ex2aro_only)
        change_connect(self.ex3Checkbox, SIGNAL("stateChanged(int)"), self.update_ex3)
        change_connect(self.ex4Checkbox, SIGNAL("stateChanged(int)"), self.update_ex4)
        change_connect(self.rotOptCheckbox, SIGNAL("stateChanged(int)"), self.update_rot_opt)
        change_connect(self.tryBothHisTautomersCheckbox, SIGNAL("stateChanged(int)"), self.update_try_both_his_tautomers)
        change_connect(self.softRepDesignCheckbox, SIGNAL("stateChanged(int)"), self.update_soft_rep_design)
        change_connect(self.useElecRepCheckbox, SIGNAL("stateChanged(int)"), self.update_use_elec_rep)
        change_connect(self.norepackDisulfCheckbox, SIGNAL("stateChanged(int)"), self.update_norepack_disulf)
        #signal slot connections for the push buttons
        change_connect(self.okButton, SIGNAL("clicked()"), self.runRosettaFixedBBSim)
        return
        
    #Protein Display methods         

    
    def show(self):
        """
        Shows the Property Manager. 
        """
        #@REVIEW: Why does it create sequence editor here? Also, is it
        #required to be done before the superclass.show call? Similar code 
        #found in CompareProteins_PM and some other files --Ninad 2008-10-02
        
        self.sequenceEditor = self.win.createProteinSequenceEditorIfNeeded()
        self.sequenceEditor.hide()
        
        _superclass.show(self)
        return
        
    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """
        self._pmGroupBox1 = PM_GroupBox( self,
                                         title = "Rosetta Fixed backbone sequence design")
        self._loadGroupBox1( self._pmGroupBox1 )
        return
    
        
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        self.numSimSpinBox = PM_SpinBox( pmGroupBox,
                                         labelColumn  = 0,
                                         label = "Number of simulations:",
                                         minimum = 1,
                                         maximum = 999,
                                         setAsDefault  =  False,
                                         spanWidth = False)
        
        self.ex1Checkbox = PM_CheckBox(pmGroupBox,
                                       text = "Expand rotamer library for chi1 angle",
                                       state = Qt.Unchecked,
                                       setAsDefault  =  False,
                                       widgetColumn  = 0,
                                       spanWidth = True)
        
        self.ex1aroCheckbox = PM_CheckBox(pmGroupBox,
                                          text = "Use large chi1 library for aromatic residues",
                                          state = Qt.Unchecked,
                                          setAsDefault  =  False,
                                          widgetColumn  = 0,
                                          spanWidth = True)
        
        self.ex2Checkbox = PM_CheckBox(pmGroupBox,
                                       text = "Expand rotamer library for chi2 angle",
                                       state = Qt.Unchecked,
                                       setAsDefault  =  False,
                                       widgetColumn  = 0,
                                       spanWidth = True)
        
        self.ex2aroOnlyCheckbox = PM_CheckBox(pmGroupBox,
                                              text = "Use large chi2 library only for aromatic residues",
                                              state = Qt.Unchecked,
                                              setAsDefault  =  False,
                                              widgetColumn  = 0,
                                              spanWidth = True)
                                              
        self.ex3Checkbox = PM_CheckBox(pmGroupBox,
                                     text = "Expand rotamer library for chi3 angle",
                                     state = Qt.Unchecked,
                                     setAsDefault  =  False,
                                     widgetColumn  = 0,
                                     spanWidth = True)
        
        self.ex4Checkbox = PM_CheckBox(pmGroupBox,
                                       text ="Expand rotamer library for chi4 angle",
                                       state = Qt.Unchecked,
                                       setAsDefault  =  False,
                                       widgetColumn  = 0,
                                       spanWidth = True)
        
        self.rotOptCheckbox = PM_CheckBox(pmGroupBox,
                                          text ="Optimize one-body energy",
                                          state = Qt.Unchecked,
                                          setAsDefault  =  False,
                                          widgetColumn  = 0,
                                          spanWidth = True)
        
        self.tryBothHisTautomersCheckbox = PM_CheckBox(pmGroupBox,
                                                       text ="Try both histidine tautomers",
                                                       state = Qt.Unchecked,
                                                       setAsDefault  =  False,
                                                       widgetColumn  = 0,
                                                       spanWidth = True)
        
        self.softRepDesignCheckbox = PM_CheckBox(pmGroupBox,
                                                 text ="Use softer Lennard-Jones repulsive term",
                                                 state = Qt.Unchecked,
                                                 setAsDefault  =  False,
                                                 widgetColumn  = 0,
                                                 spanWidth = True)
        
        self.useElecRepCheckbox = PM_CheckBox(pmGroupBox,
                                              text ="Use electrostatic repulsion",
                                              state = Qt.Unchecked,
                                              setAsDefault  =  False,
                                              widgetColumn  = 0,
                                              spanWidth = True)
        
        self.norepackDisulfCheckbox = PM_CheckBox(pmGroupBox,
                                                  text ="Don't re-pack disulphide bonds",
                                                  state = Qt.Unchecked,
                                                  setAsDefault  =  False,
                                                  widgetColumn  = 0,
                                                  spanWidth = True)
        
        
        self.otherCommandLineOptions = PM_TextEdit(pmGroupBox,
                                                   label = "Command line options:",
                                                   spanWidth = True)
        self.otherCommandLineOptions.setFixedHeight(80)
        
        self.okButton = PM_PushButton( pmGroupBox,
                         text         =  "Launch Rosetta",
                         setAsDefault  =  True,
                         spanWidth = True)
        return
    
    def _addWhatsThisText( self ):
        """
        What's This text for widgets in this Property Manager.  
        """
        pass
                
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in this Property Manager.  
        """
        pass
    
    def update_ex1(self, state):
        """
        Update the command text edit depending on the state of the update_ex1
        checkbox
        @param state:state of the update_ex1 checkbox
        @type state: int
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex1Checkbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex1 '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex1 ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_ex1aro(self, state):
        """
        Update the command text edit depending on the state of the update_ex1aro
        checkbox
        @param state:state of the update_ex1aro checkbox
        @type state: int
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex1aroCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex1aro '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex1aro ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_ex2(self, state):
        """
        Update the command text edit depending on the state of the update_ex2
        checkbox
        @param state:state of the update_ex2 checkbox
        @type state: int
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex2Checkbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex2 '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex2 ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_ex2aro_only(self, state):
        """
        Update the command text edit depending on the state of the update_ex2aro_only
        checkbox
        @param state:state of the update_ex2aro_only checkbox
        @type state: int
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex2aroOnlyCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex2aro_only '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex2aro_only ', '')    
            
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_ex3(self, state):
        """
        Update the command text edit depending on the state of the update_ex3
        checkbox
        @param state:state of the update_ex3 checkbox
        @type state: int
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex3Checkbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex3 '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex3 ', '')
        
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_ex4(self, state):
        """
        Update the command text edit depending on the state of the update_ex4
        checkbox
        @param state:state of the update_ex4 checkbox
        @type state: int
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.ex4Checkbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -ex4 '
        else:
            otherOptionsText = otherOptionsText.replace(' -ex4 ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_rot_opt(self, state):
        """
        Update the command text edit depending on the state of the update_rot_opt
        checkbox
        @param state:state of the update_rot_opt checkbox
        @type state: int
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.rotOptCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -rot_opt '
        else:
            otherOptionsText = otherOptionsText.replace(' -rot_opt ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_try_both_his_tautomers(self, state):
        """
        Update the command text edit depending on the state of the update_try_both_his_tautomers
        checkbox
        @param state:state of the update_try_both_his_tautomers checkbox
        @type state: int
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.tryBothHisTautomersCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -try_both_his_tautomers '
        else:
            otherOptionsText = otherOptionsText.replace(' -try_both_his_tautomers ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_soft_rep_design(self, state):
        """
        Update the command text edit depending on the state of the update_soft_rep_design
        checkbox
        @param state:state of the update_soft_rep_design checkbox
        @type state: int
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.softRepDesignCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -soft_rep_design '
        else:
            otherOptionsText = otherOptionsText.replace(' -soft_rep_design ', '')
        self.otherCommandLineOptions.setText(otherOptionsText)    
        return
    
    def update_use_elec_rep(self, state):
        """
        Update the command text edit depending on the state of the update_use_elec_rep
        checkbox
        @param state:state of the update_use_elec_rep checkbox
        @type state: int
        """
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
        @type state: int
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        if self.norepackDisulfCheckbox.isChecked() == True:
            otherOptionsText = otherOptionsText + ' -norepack_disulf '
        else:
            otherOptionsText = otherOptionsText.replace(' -norepack_disulf ', '')      
        self.otherCommandLineOptions.setText(otherOptionsText)        
        return
    
    def runRosettaFixedBBSim(self):
        """
        Get all the parameters from the PM and run a rosetta simulation.
        """
        proteinChunk = self.win.assy.getSelectedProteinChunk()
        if not proteinChunk:
            msg = "You must select a single protein to run a Rosetta <i>Fixed Backbone</i> simulation."
            self.updateMessage(msg)
            return
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        numSim = self.numSimSpinBox.value()
        argList = [numSim, otherOptionsText, proteinChunk.name]
        
        from simulation.ROSETTA.rosetta_commandruns import rosettaSetup_CommandRun
        if argList[0] > 0:
            cmdrun = rosettaSetup_CommandRun(self.win, argList, "ROSETTA_FIXED_BACKBONE_SEQUENCE_DESIGN")
            cmdrun.run() 
        return    