# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Urmi
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
- 2008-08-05 created by Urmi. 
- The motivation was to include all protein modeling and simulation features 
  in one place.
- Based on the original protein flyout toolbar that mostly supported modeling tools 
  and the new flyout toolbar that combines atom and bonds tool for chunks 

"""
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QAction
from PyQt4.Qt import QActionGroup
from utilities.icon_utilities import geticon
from ne1_ui.toolbars.Ui_AbstractFlyout import Ui_AbstractFlyout

from processes.Plugins import checkPluginPreferences
from utilities.prefs_constants import rosetta_enabled_prefs_key, rosetta_path_prefs_key

_superclass = Ui_AbstractFlyout

class ProteinFlyout_v2(Ui_AbstractFlyout):    
 
    def _action_in_controlArea_to_show_this_flyout(self):
        """
        Required action in the 'Control Area' as a reference for this 
        flyout toolbar. See superclass method for documentation and todo note.
        """
        return self.win.insertPeptideAction
        
    
    def _getExitActionText(self):
        """
        Overrides superclass method. 
        @see: self._createActions()
        """
        return "Exit Protein"
    
            
    def getFlyoutActionList(self): 
        """
        Returns a tuple that contains mode spcific actionlists in the 
        added in the flyout toolbar of the mode. 
        CommandToolbar._createFlyoutToolBar method calls this 
        @return: params: A tuple that contains 3 lists: 
        (subControlAreaActionList, commandActionLists, allActionsList)
        """
        
        allActionsList = []
        subControlAreaActionList =[] 
              
        #Append subcontrol area actions to  subControlAreaActionList
        #The 'Exit button' althought in the subcontrol area, would 
        #look as if its in the Control area because of the different color 
        #palette 
        #and the separator after it. This is intentional.
        subControlAreaActionList.append(self.exitModeAction)
        separator1 = QAction(self.win)
        separator1.setSeparator(True)
        subControlAreaActionList.append(separator1) 
        
        subControlAreaActionList.append(self.modelProteinAction)        
        subControlAreaActionList.append(self.simulateProteinAction)      
        separator = QAction(self.win)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator) 
    
        #Also add the subcontrol Area actions to the 'allActionsList'
        for a in subControlAreaActionList:
            allActionsList.append(a)    
        
        commandActionLists = [] 
        
        #Append empty 'lists' in 'commandActionLists equal to the 
        #number of actions in subControlArea 
        for i in range(len(subControlAreaActionList)):
            lst = []
            commandActionLists.append(lst)
        
        #Command list for the subcontrol area button 'Model Proteins Tool'
        modelProteinsCmdLst = []
        modelProteinsCmdLst.append(self.buildPeptideAction)
        modelProteinsCmdLst.append(self.editRotamersAction)
        modelProteinsCmdLst.append(self.compareProteinsAction)
        modelProteinsCmdLst.append(self.displayProteinStyleAction)    
        commandActionLists[2].extend(modelProteinsCmdLst)
        
        # Command list for the subcontrol area button 'Simulate Proteins Tool'
        
        if self.rosetta_enabled:
            simulateProteinsCmdLst = []
            simulateProteinsCmdLst.append(self.rosetta_fixedbb_design_Action)
            simulateProteinsCmdLst.append(self.rosetta_backrub_Action)
            simulateProteinsCmdLst.append(self.editResiduesAction)
            simulateProteinsCmdLst.append(self.rosetta_score_Action)
            commandActionLists[3].extend(simulateProteinsCmdLst)
        else:
            modelProteinsCmdLst = []
            modelProteinsCmdLst.append(self.buildPeptideAction)
            modelProteinsCmdLst.append(self.editRotamersAction)
            modelProteinsCmdLst.append(self.compareProteinsAction)
            modelProteinsCmdLst.append(self.displayProteinStyleAction)    
            commandActionLists[0].extend(modelProteinsCmdLst)
            
        params = (subControlAreaActionList, commandActionLists, allActionsList)
        
        return params
    
    
    def _createActions(self, parentWidget):
        """
        Define flyout toolbar actions for this mode.
        """
              
        _superclass._createActions(self, parentWidget)
        
        #Urmi 20080814: show this flyout toolbar only when rosetta plugin path
        # is there
        #Probably only rosetta_enabled_prefs_key check would have sufficed
        plugin_name = "ROSETTA"
        plugin_prefs_keys = (rosetta_enabled_prefs_key, rosetta_path_prefs_key)    
        errorcode, errortext_or_path = \
                 checkPluginPreferences(plugin_name, plugin_prefs_keys, ask_for_help = False)
        #print "Error code =", errorcode, errortext_or_path
        if errorcode == 0:
            self.rosetta_enabled = True
        else:
            self.rosetta_enabled = False
            
        self.modelProteinAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.modelProteinAction.setText("Model")
        self.modelProteinAction.setIcon(geticon(
            'ui/actions/Command Toolbar/BuildProtein/Peptide.png'))
        self.modelProteinAction.setCheckable(True)
        self.modelProteinAction.setChecked(True)
        self.modelProteinAction.setObjectName('ACTION_MODEL_PROTEINS')
        
        self.simulateProteinAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.simulateProteinAction.setText("Simulate")
        self.simulateProteinAction.setIcon(geticon(
            "ui/actions/Simulation/Rosetta.png"))
        self.simulateProteinAction.setCheckable(True)
        self.simulateProteinAction.setObjectName('ACTION_SIMULATE_PROTEINS')
    
        self.subControlActionGroup = QActionGroup(parentWidget)
        self.subControlActionGroup.setExclusive(True)   
        self.subControlActionGroup.addAction(self.modelProteinAction)   
        self.subControlActionGroup.addAction(self.simulateProteinAction)
    
        self._createModelProteinsActions(parentWidget)
        self._createSimulateProteinsActions(parentWidget)
        
        #else:
        #    self._createModelProteinsActions(parentWidget)
        #return
    
            
    def _createModelProteinsActions(self, parentWidget): 
        """
        Create the actions to be included in flyout toolbar, when the 'Model
        Proteins' is active. 
        
        @see: self._createActions() where this is called. 
        """
        
        self.buildPeptideAction = NE1_QWidgetAction(parentWidget,
                                                      win = self.win)
        self.buildPeptideAction.setText("Peptide")
        self.buildPeptideAction.setCheckable(True)  
        self.buildPeptideAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildProtein/Peptide.png"))

        self.editRotamersAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.editRotamersAction.setText("Rotamers")
        self.editRotamersAction.setCheckable(True)  
        self.editRotamersAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildProtein/Rotamers.png"))
        
        self.compareProteinsAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.compareProteinsAction.setText("Compare")
        self.compareProteinsAction.setCheckable(True)  
        self.compareProteinsAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildProtein/Compare.png"))
        
        self.displayProteinStyleAction = NE1_QWidgetAction(parentWidget, 
                                                           win = self.win)

        self.displayProteinStyleAction.setText("Edit Style")
        self.displayProteinStyleAction.setCheckable(True)        
        self.displayProteinStyleAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildProtein/EditProteinDisplayStyle.png"))
                    
        self.subControlActionGroupForModelProtein = QActionGroup(parentWidget)
        self.subControlActionGroupForModelProtein.setExclusive(True)   
        self.subControlActionGroupForModelProtein.addAction(self.buildPeptideAction)   
        self.subControlActionGroupForModelProtein.addAction(self.displayProteinStyleAction)
        self.subControlActionGroupForModelProtein.addAction(self.compareProteinsAction)
        self.subControlActionGroupForModelProtein.addAction(self.editRotamersAction)
        return
    
    def _createSimulateProteinsActions(self, parentWidget): 
        """
        Create the actions to be included in flyout toolbar, when the 'Simulate
        Proteins' is active. 
        
        @see: self._createActions() where this is called. 
        """
           
        self.rosetta_fixedbb_design_Action = NE1_QWidgetAction(parentWidget,
                                                      win = self.win)
        self.rosetta_fixedbb_design_Action.setText("Fixed BB")
        self.rosetta_fixedbb_design_Action.setCheckable(True)  
        self.rosetta_fixedbb_design_Action.setIcon(
            geticon("ui/actions/Simulation/Rosetta.png"))
        
        self.rosetta_backrub_Action = NE1_QWidgetAction(parentWidget,
                                                      win = self.win)
        self.rosetta_backrub_Action.setText("Backrub")
        self.rosetta_backrub_Action.setCheckable(True)  
        self.rosetta_backrub_Action.setIcon(
            geticon("ui/actions/Simulation/Rosetta.png"))

        self.editResiduesAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.editResiduesAction.setText("Residues")
        self.editResiduesAction.setCheckable(True)  
        self.editResiduesAction.setIcon(
            geticon("ui/actions/Command Toolbar/BuildProtein/Residues.png"))
        
        self.rosetta_score_Action = NE1_QWidgetAction(parentWidget,
                                                      win = self.win)
        self.rosetta_score_Action.setText("Score")
        self.rosetta_score_Action.setCheckable(True)  
        self.rosetta_score_Action.setIcon(
            geticon("ui/actions/Simulation/Rosetta.png"))
        
        self.subControlActionGroupForSimulateProtein = QActionGroup(parentWidget)
        self.subControlActionGroupForSimulateProtein.setExclusive(True)   
        self.subControlActionGroupForSimulateProtein.addAction(self.rosetta_fixedbb_design_Action)   
        self.subControlActionGroupForSimulateProtein.addAction(self.rosetta_backrub_Action)
        self.subControlActionGroupForSimulateProtein.addAction(self.editResiduesAction)
        self.subControlActionGroupForSimulateProtein.addAction(self.rosetta_score_Action)
        return
    
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        
        @see: self.activateFlyoutToolbar, self.deActivateFlyoutToolbar
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
        
        #Ui_AbstractFlyout connects the self.exitmodeAction, so call it first.
        _superclass.connect_or_disconnect_signals(self, isConnect)
        
        change_connect(self.modelProteinAction,
                       SIGNAL("triggered()"),self._activateModelProteins)
        change_connect(self.subControlActionGroup, 
                       SIGNAL("triggered(QAction *)"),
                       self.testRosettaAndUpdateCommandToolbar)
        change_connect(self.simulateProteinAction, 
                       SIGNAL("triggered()"), 
                       self._activateSimulateProteins)
        
        change_connect(self.buildPeptideAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateBuildPeptide_EditCommand)

        change_connect(self.editRotamersAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateEditRotamers_EditCommand)
        change_connect(self.editResiduesAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateEditResidues_EditCommand)

        change_connect(self.compareProteinsAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateCompareProteins_EditCommand)

        change_connect(self.displayProteinStyleAction, 
                       SIGNAL("triggered(bool)"),
                       self.activateProteinDisplayStyle_Command)
        
        change_connect(self.rosetta_fixedbb_design_Action,
                       SIGNAL("triggered(bool)"),
                       self.activateRosettaFixedBBDesign_Command)
    
        change_connect(self.rosetta_score_Action,
                       SIGNAL("triggered(bool)"),
                       self.activateRosettaScore_Command)
    
        change_connect(self.rosetta_backrub_Action,
                       SIGNAL("triggered(bool)"),
                       self.activateRosettaBackrub_Command)
        return
    
    def activateRosettaBackrub_Command(self, isChecked):
        """
        Activate Rosetta sequence design with backrub motion command
        """
        self.win.enterOrExitTemporaryCommand('BACKRUB_PROTEIN_SEQUENCE_DESIGN')
        for action in self.subControlActionGroupForSimulateProtein.actions():
            if action is not self.rosetta_backrub_Action and action.isChecked():
                action.setChecked(False)
        return
    
    def activateRosettaScore_Command(self, isChecked):
        """
        Score the current protein sequence
        """
        otherOptionsText = ""
        numSim = 1
        protein = self.command.propMgr.get_current_protein_chunk_name()
        argList = [numSim, otherOptionsText, protein]
        
        from simulation.ROSETTA.rosetta_commandruns import rosettaSetup_CommandRun
        if argList[0] > 0:
            cmdrun = rosettaSetup_CommandRun(self.win, argList, "ROSETTA_SCORE")
            cmdrun.run() 
            
        for action in self.subControlActionGroupForSimulateProtein.actions():
            if action is not self.rosetta_score_Action and action.isChecked():
                action.setChecked(False)    
        return
    
    def activateRosettaFixedBBDesign_Command(self, isChecked):
        """
        Activate fixed backbone rosetta sequence design mode
        """
        self.win.enterOrExitTemporaryCommand('FIXED_BACKBONE_PROTEIN_SEQUENCE_DESIGN')
        for action in self.subControlActionGroupForSimulateProtein.actions():
            if action is not self.rosetta_fixedbb_design_Action and action.isChecked():
                action.setChecked(False)
        return
    
    def _activateModelProteins(self):
        """
        Activate the model proteins action of the Proteins mode 
        
        """
        self.command.setCurrentCommandMode('MODEL_PROTEIN')
        self.command.enterModelOrSimulateCommand('MODEL_PROTEIN')
        for action in self.subControlActionGroupForModelProtein.actions():
            action.setChecked(False)
        return
        
    def _activateSimulateProteins(self):
        """
        Activate the simulation tool of the Build Protein mode 
        """                
        self.command.setCurrentCommandMode('SIMULATE_PROTEIN')
        self.command.enterModelOrSimulateCommand('SIMULATE_PROTEIN')
        for action in self.subControlActionGroupForSimulateProtein.actions():
            action.setChecked(False)
        return
            
    def activateBuildPeptide_EditCommand(self, isChecked):
        """
        Slot for inserting a peptide action.
        """

        self.win.insertPeptide(isChecked)

        for action in self.subControlActionGroupForModelProtein.actions():
            if action is not self.buildPeptideAction and action.isChecked():
                action.setChecked(False)

    def activateEditRotamers_EditCommand(self, isChecked):
        """
        Slot for B{EditRotamers} action.
        """
        
        self.win.enterEditRotamersCommand(isChecked)

        for action in self.subControlActionGroupForModelProtein.actions():
            if action is not self.editRotamersAction and action.isChecked():
                action.setChecked(False)

    def activateEditResidues_EditCommand(self, isChecked):
        """
        Slot for B{EditResidues} action.
        """

        self.win.enterEditResiduesCommand(isChecked)

        for action in self.subControlActionGroupForSimulateProtein.actions():
            if action is not self.editResiduesAction and action.isChecked():
                action.setChecked(False)

    def activateCompareProteins_EditCommand(self, isChecked):
        """
        Slot for B{CompareProteins} action.
        """

        self.win.enterCompareProteinsCommand(isChecked)

        for action in self.subControlActionGroupForModelProtein.actions():
            if action is not self.compareProteinsAction and action.isChecked():
                action.setChecked(False)

    def activateProteinDisplayStyle_Command(self, isChecked):
        """
        Call the method that enters DisplayStyle_Command. 
        (After entering the command) Also make sure that 
        all the other actions on the DnaFlyout toolbar are unchecked AND 
        the DisplayStyle Action is checked. 
        """

        self.win.enterProteinDisplayStyleCommand(isChecked)

        #Uncheck all the actions except the (DNA) display style action
        #in the flyout toolbar (subcontrol area)
        for action in self.subControlActionGroupForModelProtein.actions():
            if action is not self.displayProteinStyleAction and action.isChecked():
                action.setChecked(False)
                
                
                
    def resetStateOfActions(self):
        """
        Resets the state of actions in the flyout toolbar.
        Uncheck most of the actions. Basically it 
        unchecks all the actions EXCEPT the ExitDnaAction
        @see: self.deActivateFlyoutToolbar()
        
        """
        #Uncheck all the actions in the flyout toolbar (subcontrol area)
        
        for action in self.subControlActionGroup.actions():
            if action.isChecked():
                action.setChecked(False)     
        return
    
    def testRosettaAndUpdateCommandToolbar(self, action):
        if action == self.simulateProteinAction:
            if not self.rosetta_enabled:
                #print "Rosetta is not enabled"
                plugin_name = "ROSETTA"
                plugin_prefs_keys = (rosetta_enabled_prefs_key, rosetta_path_prefs_key)    
                errorcode, errortext_or_path = \
                         checkPluginPreferences(plugin_name, plugin_prefs_keys, ask_for_help = True)
                #print "Error code =", errorcode, errortext_or_path
                if errorcode == 0:
                    self.rosetta_enabled = True
                else:
                    self.rosetta_enabled = False
                    self.modelProteinAction.setChecked(True)
                    self.simulateProteinAction.setChecked(False)
                    return
                
        self.updateCommandToolbar()
        
    