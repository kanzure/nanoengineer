# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
- 2008-07-29 created. Moved related code from BuildAtoms_Command to this new class
NOTE THAT THIS CLASS IS NOT YET USED ANYWHERE. As of 2008-07-29, 
BuildAtoms_Command continues to use its own methods to update the flyout toolbar
Eventually this class will be used to do that part. 


TODO:

- This may be revised heavily during the command toolbar cleanup project. 
The current class refactors the related code from class BuildAtoms_Command

@Note: The class name is BuildAtomsFlyout -- this provides the flyout toolbar
for class BuildAtoms_Command 

"""
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QAction
from PyQt4.Qt import QActionGroup


from utilities.icon_utilities import geticon

from ne1_ui.toolbars.Ui_AbstractFlyout import Ui_AbstractFlyout

_superclass = Ui_AbstractFlyout

class BuildAtomsFlyout(Ui_AbstractFlyout):    
    
    def _action_in_controlArea_to_show_this_flyout(self):
        """
        Required action in the 'Control Area' as a reference for this 
        flyout toolbar. See superclass method for documentation and todo note.
        """
        return self.win.toolsDepositAtomAction
        
    
    def _getExitActionText(self):
        """
        Overrides superclass method. 
        @see: self._createActions()
        """
        return "Exit Atoms"
    
            
    def getFlyoutActionList(self): 
        """
        Returns a tuple that contains mode spcific actionlists in the 
        added in the flyout toolbar of the mode. 
        CommandToolbar._createFlyoutToolBar method calls this 
        @return: params: A tuple that contains 3 lists: 
        (subControlAreaActionList, commandActionLists, allActionsList)
        """
        
        #ninad070330 This implementation may change in future. 
        
        #'allActionsList' returns all actions in the flyout toolbar 
        #including the subcontrolArea actions. 
        allActionsList = []
        #Action List for  subcontrol Area buttons. 
        #For now this list is just used to set a different palette to thisaction
        #buttons in the toolbar
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
        
        subControlAreaActionList.append(self.depositAtomsAction)        
        subControlAreaActionList.append(self.transmuteBondsAction)      
        separator = QAction(self.win)
        separator.setSeparator(True)
        subControlAreaActionList.append(separator) 
        
        #Also add the subcontrol Area actions to the 'allActionsList'
        for a in subControlAreaActionList:
            allActionsList.append(a)    
        ##actionlist.append(self.win.modifyAdjustSelAction)
        ##actionlist.append(self.win.modifyAdjustAllAction)
        
        #Ninad 070330:
        #Command Actions : These are the actual actions that will respond the 
        #a button pressed in the 'subControlArea (if present). 
        #Each Subcontrol area button can have its own 'command list' 
        #The subcontrol area buuton and its command list form a 'key:value pair 
        #in a python dictionary object
        #In Build mode, as of 070330 we have 3 subcontrol area buttons 
        #(or 'actions)'
        commandActionLists = [] 
        
        #Append empty 'lists' in 'commandActionLists equal to the 
        #number of actions in subControlArea 
        for i in range(len(subControlAreaActionList)):
            lst = []
            commandActionLists.append(lst)
        
        #Command list for the subcontrol area button 'Atoms Tool'
        #For others, this list will remain empty for now -- ninad070330 
        depositAtomsCmdLst = []
        depositAtomsCmdLst.append(self.win.modifyHydrogenateAction)
        depositAtomsCmdLst.append(self.win.modifyDehydrogenateAction)
        depositAtomsCmdLst.append(self.win.modifyPassivateAction)
        separatorAfterPassivate = QAction(self.win)
        separatorAfterPassivate.setSeparator(True)
        depositAtomsCmdLst.append(separatorAfterPassivate)
        depositAtomsCmdLst.append(self.transmuteAtomsAction)    
        separatorAfterTransmute = QAction(self.win)
        separatorAfterTransmute.setSeparator(True)
        depositAtomsCmdLst.append(separatorAfterTransmute)
        depositAtomsCmdLst.append(self.win.modifyDeleteBondsAction)
        depositAtomsCmdLst.append(self.win.modifySeparateAction)
        depositAtomsCmdLst.append(self.win.makeChunkFromSelectedAtomsAction)
                        
        commandActionLists[2].extend(depositAtomsCmdLst)
        
        ##for action in self.win.buildToolsMenu.actions():
            ##commandActionLists[2].append(action)
        
        # Command list for the subcontrol area button 'Bonds Tool'
        # For others, this list will remain empty for now -- ninad070405 
        bondsToolCmdLst = []
        bondsToolCmdLst.append(self.bond1Action)
        bondsToolCmdLst.append(self.bond2Action)
        bondsToolCmdLst.append(self.bond3Action)
        bondsToolCmdLst.append(self.bondaAction)
        bondsToolCmdLst.append(self.bondgAction)
        bondsToolCmdLst.append(self.cutBondsAction)
        commandActionLists[3].extend(bondsToolCmdLst)
                            
        params = (subControlAreaActionList, commandActionLists, allActionsList)
        
        return params
    
    
    def _createActions(self, parentWidget):
        """
        Define flyout toolbar actions for this mode.
        """
        #@NOTE: In Build mode, some of the actions defined in this method are also 
        #used in Build Atoms PM. (e.g. bond actions) So probably better to rename 
        #it as _init_modeActions. Not doing that change in mmkit code cleanup 
        #commit(other modes still implement a method by same name)-ninad20070717
                
        _superclass._createActions(self, parentWidget)
        
        #Following Actions are added in the Flyout toolbar. 
        #Defining them outside that method as those are being used
        #by the subclasses of deposit mode (testmode.py as of 070410) -- ninad
                
        self.depositAtomsAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.depositAtomsAction.setText("Atoms Tool")
        self.depositAtomsAction.setIcon(geticon(
            'ui/actions/Toolbars/Smart/Deposit_Atoms.png'))
        self.depositAtomsAction.setCheckable(True)
        self.depositAtomsAction.setChecked(True)
        self.depositAtomsAction.setObjectName('ACTION_ATOMS_TOOL')
        
                
        self.transmuteBondsAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.transmuteBondsAction.setText("Bonds Tool")
        self.transmuteBondsAction.setIcon(geticon(
            'ui/actions/Toolbars/Smart/Transmute_Bonds.png'))
        self.transmuteBondsAction.setCheckable(True)
        self.transmuteBondsAction.setObjectName('ACTION_BOND_TOOL')
        
        self.subControlActionGroup = QActionGroup(parentWidget)
        self.subControlActionGroup.setExclusive(True)   
        self.subControlActionGroup.addAction(self.depositAtomsAction)   
        self.subControlActionGroup.addAction(self.transmuteBondsAction)
        
        self.transmuteAtomsAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.transmuteAtomsAction.setText("Transmute Atoms")
        self.transmuteAtomsAction.setIcon(geticon(
            'ui/actions/Toolbars/Smart/Transmute_Atoms.png'))       
        self.transmuteAtomsAction.setCheckable(False)
        
        
        self._createBondToolActions(parentWidget)
        
    def _createBondToolActions(self, parentWidget): 
        """
        Create the actions to be included in flyout toolbar , when the 'bonds
        tool' is active. Note that the object names of these action will be 
        be used to find the Bond Tool type to which each action corresponds to.
        
        @see: self._createActions() where this is called. 
        """
        self.bondToolsActionGroup = QActionGroup(parentWidget)
        self.bondToolsActionGroup.setExclusive(True)
                
        self.bond1Action = NE1_QWidgetAction(parentWidget, win = self.win)  
        self.bond1Action.setText("Single")
        self.bond1Action.setIcon(geticon("ui/actions/Toolbars/Smart/bond1.png"))
        self.bond1Action.setObjectName('ACTION_SINGLE_BOND_TOOL')
            
        self.bond2Action = NE1_QWidgetAction(parentWidget, win = self.win)  
        self.bond2Action.setText("Double")
        self.bond2Action.setIcon(geticon("ui/actions/Toolbars/Smart/bond2.png"))
        self.bond2Action.setObjectName('ACTION_DOUBLE_BOND_TOOL')
        
        self.bond3Action = NE1_QWidgetAction(parentWidget, win = self.win)  
        self.bond3Action.setText("Triple")
        self.bond3Action.setIcon(geticon("ui/actions/Toolbars/Smart/bond3.png"))
        self.bond3Action.setObjectName('ACTION_TRIPLE_BOND_TOOL')
        
        self.bondaAction = NE1_QWidgetAction(parentWidget, win = self.win)  
        self.bondaAction.setText("Aromatic")
        self.bondaAction.setIcon(geticon("ui/actions/Toolbars/Smart/bonda.png"))
        self.bondaAction.setObjectName('ACTION_AROMATIC_BOND_TOOL')
        
        self.bondgAction = NE1_QWidgetAction(parentWidget, win = self.win)  
        self.bondgAction.setText("Graphitic")
        self.bondgAction.setIcon(geticon("ui/actions/Toolbars/Smart/bondg.png"))
        self.bondgAction.setObjectName('ACTION_GRAPHITIC_BOND_TOOL')
        
        self.cutBondsAction = NE1_QWidgetAction(parentWidget, win = self.win)  
        self.cutBondsAction.setText("Cut Bonds")
        self.cutBondsAction.setIcon(geticon("ui/actions/Tools/Build Tools/Cut_Bonds.png"))
        self.cutBondsAction.setObjectName('ACTION_DELETE_BOND_TOOL')
        
        for action in [self.bond1Action, 
                       self.bond2Action, 
                       self.bond3Action,
                       self.bondaAction,
                       self.bondgAction,
                       self.cutBondsAction  
                       ]:
            self.bondToolsActionGroup.addAction(action)
            action.setCheckable(True)
                    
        
        
    
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
            
        #Atom , Bond Tools Groupbox
        change_connect(self.bondToolsActionGroup,
                       SIGNAL("triggered(QAction *)"), 
                       self.command.changeBondTool)
                
        
        change_connect(self.transmuteAtomsAction,
                        SIGNAL("triggered()"),self.command.transmutePressed)
                       
        change_connect(self.subControlActionGroup, 
                       SIGNAL("triggered(QAction *)"),
                       self.updateCommandToolbar)
        
        change_connect(self.transmuteBondsAction, 
                       SIGNAL("triggered()"), 
                       self._activateBondsTool)
        
        change_connect(self.depositAtomsAction, 
                       SIGNAL("triggered()"), 
                       self._activateAtomsTool)    
        
        
    def get_cursor_id_for_active_tool(self):
        """
        Provides a cursor id (int) for updating cursor in graphics mode, 
        based on the checked action in its flyout toolbar. (i.e. based on the 
        active tool)
        @see: BuildAtoms_GraphicsMode.update_cursor_for_no_MB_selection_filter_disabled
        """
        if self.depositAtomsAction.isChecked(): 
            cursor_id = 0
        elif self.bond1Action.isChecked(): 
            cursor_id = 1
        elif self.bond2Action.isChecked(): 
            cursor_id = 2
        elif self.bond3Action.isChecked(): 
            cursor_id = 3
        elif self.bondaAction.isChecked(): 
            cursor_id = 4
        elif self.bondgAction.isChecked(): 
            cursor_id = 5
        elif self.cutBondsAction.isChecked(): 
            cursor_id = 6
        else: 
            cursor_id = 0 
                    
        return cursor_id
    
    
    def _activateAtomsTool(self):
        """
        Activate the atoms tool of the Build Atoms mode 
        hide only the Atoms Tools groupbox in the Build Atoms Property manager
        and show all others the others.
        """
        self.command.activateAtomsTool()
        self.command.enterToolsCommand('ATOMS_TOOL')
        
    def _activateBondsTool(self):
        """
        Activate the bond tool of the Build Atoms mode 
        Show only the Bond Tools groupbox in the Build Atoms Property manager
        and hide the others.
        @see:self._convert_bonds_bet_selected_atoms()
        """  
        self.command.activateBondsTool()
            
        
    def getBondToolActions(self):
        return self.bondToolsActionGroup.actions()
    
    def getCheckedBondToolAction(self):
        return self.bondToolsActionGroup.checkedAction()
        
    
        