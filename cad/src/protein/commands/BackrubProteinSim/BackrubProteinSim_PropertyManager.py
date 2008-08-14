# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
BackrubProteinSim_PropertyManager.py

The BackrubProteinSim_PropertyManager class provides a Property Manager 
for the B{Backrub protein sequence design} command on the flyout toolbar in the 
Build > Protein > Simulate mode. 

@author: Urmi
@version: $Id$ 
@copyright: 2008 Nanorex, Inc. See LICENSE file for details.

"""
import string
import foundation.env as env
from utilities.Log import redmsg
from widgets.DebugMenuMixin import DebugMenuMixin
from utilities.prefs_constants import rosetta_backrub_enabled_prefs_key
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt
from PyQt4 import QtGui
from PyQt4.Qt import QString
from PM.PM_PushButton   import PM_PushButton
from PM.PM_Dialog   import PM_Dialog
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_TextEdit import PM_TextEdit
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_Constants import PM_DONE_BUTTON
from PM.PM_Constants import PM_WHATS_THIS_BUTTON
from PM.PM_SpinBox import PM_SpinBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_ComboBox import PM_ComboBox

#debug flag to keep signals always connected
from utilities.GlobalPreferences import KEEP_SIGNALS_ALWAYS_CONNECTED

class BackrubProteinSim_PropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The BackrubProteinSim_PropertyManager class provides a Property Manager 
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

    title         =  "Protein Sequence Design with Backrub motion"
    pmName        =  title
    iconPath      = "ui/actions/Simulation/Rosetta.png"

    
    def __init__( self, command ):
        """
        Constructor for the property manager.
        """

        self.command = command
        self.win = self.command.w
        self.pw = self.command.pw        
        self.o = self.win.glpane                 
        
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)

        DebugMenuMixin._init1( self )

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        msg = "Choose various parameters from below to design an optimized" \
            " protein sequence with Rosetta with backrub motion allowed."
        self.updateMessage(msg)
        
        if KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)

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
        change_connect(self.okButton, SIGNAL("clicked()"), self.runRosettaBackrubSim)
        return
    
        
    #Protein Display methods         

    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """
        self.win.toolsDone()

    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """
        self.win.toolsDone()

    def show(self):
        """
        Shows the Property Manager. Overrides PM_Dialog.show.
        """
        self.sequenceEditor = self.win.createProteinSequenceEditorIfNeeded()
        self.sequenceEditor.hide()
        #update the min and max residues spinbox max values based on the length
        #of the current protein
        numResidues = self._getNumResiduesForCurrentProtein()
        if numResidues == 0:
            self.minresSpinBox.setMaximum(numResidues + 2)
            self.maxresSpinBox.setMaximum(numResidues + 2)
        else:    
            self.minresSpinBox.setMaximum(numResidues)
            self.maxresSpinBox.setMaximum(numResidues)
        
        PM_Dialog.show(self)
        
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)
        return
    
        
    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(False)
            
        PM_Dialog.close(self)
        return
    

    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """
        self._pmGroupBox2 = PM_GroupBox( self,
                                         title = "Backrub specific parameters")
        self._loadGroupBox2( self._pmGroupBox2 )
        
        self._pmGroupBox1 = PM_GroupBox( self,
                                         title = "Rosetta sequence design parameters")
        self._loadGroupBox1( self._pmGroupBox1 )
        
        return
    
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        self.bondAngleWeightSimSpinBox = PM_DoubleSpinBox( pmGroupBox,
                                         labelColumn  = 0,
                                         label = "Bond angle weight:",
                                         minimum = 0.01,
                                         decimals     = 2, 
                                         maximum = 1.0,
                                         singleStep = 0.01,
                                         value = 1.0,
                                         setAsDefault  =  False,
                                         spanWidth = False)
        
        bond_angle_param_list = ['Amber', 'Charmm']
        
        self.bondAngleParamComboBox = PM_ComboBox( pmGroupBox,
                                                   label         =  "Bond angle parameters:",
                                                   choices       =  bond_angle_param_list,
                                                   setAsDefault  =  False)
        
        self.onlybbSpinBox = PM_DoubleSpinBox( pmGroupBox,
                                         labelColumn  = 0,
                                         label = "Only backbone rotation:",
                                         minimum = 0.01,
                                         maximum = 1.0,
                                         value        = 0.75, 
                                        decimals     = 2, 
                                         singleStep = 0.01,
                                         setAsDefault  =  False,
                                         spanWidth = False)
        
        self.onlyrotSpinBox = PM_DoubleSpinBox( pmGroupBox,
                                         labelColumn  = 0,
                                         label = "Only rotamer rotation:",
                                         minimum = 0.01,
                                         maximum = 1.0,
                                        decimals     = 2, 
                                        value        = 0.25, 
                                         singleStep = 0.01,
                                         setAsDefault  =  False,
                                         spanWidth = False)
        
        self.mctempSpinBox = PM_DoubleSpinBox( pmGroupBox,
                                         labelColumn  = 0,
                                         label = "MC simulation temperature:",
                                         minimum = 0.1,
                                         value        = 0.6, 
                                         maximum = 1.0,
                                        decimals     = 2, 
                                         singleStep = 0.1,
                                         setAsDefault  =  False,
                                         spanWidth = False)
        
        numResidues = self._getNumResiduesForCurrentProtein()
        self.minresSpinBox = PM_SpinBox( pmGroupBox,
                                         labelColumn  = 0,
                                         label = "Minimum number of residues:",
                                         minimum = 2,
                                         maximum = numResidues,
                                         singleStep = 1,
                                         setAsDefault  =  False,
                                         spanWidth = False)
        
        self.maxresSpinBox = PM_SpinBox( pmGroupBox,
                                         labelColumn  = 0,
                                         label = "Maximum number of residues:",
                                         minimum = 2,
                                         maximum = numResidues,
                                         singleStep = 1,
                                         setAsDefault  =  False,
                                         spanWidth = False)
        if numResidues == 0:
            self.minresSpinBox.setMaximum(numResidues + 2)
            self.maxresSpinBox.setMaximum(numResidues + 2)
        return
    
    def _getNumResiduesForCurrentProtein(self):
        """
        Get number of residues for the current protein
        """
        previousCommand = self.command.find_parent_command_named('MODEL_AND_SIMULATE_PROTEIN')
        if  previousCommand:
            #Urmi 20080728: get the protein currently selected in the combo box
            current_protein = previousCommand.propMgr.get_current_protein_chunk_name()
            for mol in self.win.assy.molecules:
                if mol.isProteinChunk() and current_protein == mol.name:
                    return len(mol.protein.get_sequence_string()) 
                
        else:
            return 0
        return 0
    
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        self.numSimSpinBox = PM_SpinBox( pmGroupBox,
                                         labelColumn  = 0,
                                         label = "Number of trials:",
                                         minimum = 1000,
                                         maximum = 1000000,
                                         singleStep = 1000,
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
                         text         =  "Run Rosetta",
                         setAsDefault  =  True,
                         spanWidth = True)
        return
    
    
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
    
    def runRosettaBackrubSim(self):
        """
        Get all the parameters from the PM and run a rosetta simulation
        """
        otherOptionsText = str(self.otherCommandLineOptions.toPlainText())
        numSim = self.numSimSpinBox.value()
        previousCommand = self.command.find_parent_command_named('MODEL_AND_SIMULATE_PROTEIN')
        protein = previousCommand.propMgr.get_current_protein_chunk_name()
        argList = [numSim, otherOptionsText, protein]
        backrubSpecificArgList = self.getBackrubSpecificArgumentList()
        from simulation.ROSETTA.rosetta_commandruns import rosettaSetup_CommandRun
        if argList[0] > 0:
            env.prefs[rosetta_backrub_enabled_prefs_key] = True
            cmdrun = rosettaSetup_CommandRun(self.win, argList, "BACKRUB_PROTEIN_SEQUENCE_DESIGN", backrubSpecificArgList)
            cmdrun.run() 
        return    
    
    def getBackrubSpecificArgumentList(self):
        """
        get list of backrub specific parameters from PM
        """
        listOfArgs = []
        
        bond_angle_weight = str(self.bondAngleWeightSimSpinBox.value())
        listOfArgs.append('-bond_angle_weight')
        listOfArgs.append( bond_angle_weight)
        
        if self.bondAngleParamComboBox.currentIndex() == 0:
            bond_angle_params = 'bond_angle_amber_rosetta'
        else:
            bond_angle_params = 'bond_angle_charmm_rosetta'
            
        listOfArgs.append('-bond_angle_params')            
        listOfArgs.append(bond_angle_params)    
        
        only_bb = str(self.onlybbSpinBox.value())
        listOfArgs.append('-only_bb')
        listOfArgs.append( only_bb)
        
        only_rot = str(self.onlyrotSpinBox.value())
        listOfArgs.append('-only_rot')
        listOfArgs.append( only_rot)
        
        mc_temp = str(self.mctempSpinBox.value())
        listOfArgs.append('-mc_temp')
        listOfArgs.append( mc_temp)
        
        min_res = self.minresSpinBox.value()
        max_res = self.maxresSpinBox.value()
        if max_res < min_res:
            msg = redmsg("Maximum number of residues for rosetta simulation with backrub" \
                " motion cannot be less than minimum number of residues."\
                " Neglecting this parameter for this simulation.")
            
            env.history.message("BACKRUB SIMULATION: " + msg)
        else:
            listOfArgs.append('-min_res')
            listOfArgs.append( str(min_res))
            listOfArgs.append('-max_res')
            listOfArgs.append( str(max_res))
        
        return listOfArgs