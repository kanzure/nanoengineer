# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
CommandToolbar.py - controls the main hierarchical toolbar for giving commands

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.


Module classification: [bruce 071228]

This mainly contains control logic (especially regarding flyout
toolbar behavior and appearance) for any hierarchical
command toolbar which operates like NE1's main Command Toolbar.

Accordingly, after future refactoring, it could be part of a
general-purpose "command toolbar widget" package. But at the
moment, it inherits a hardcoding of NE1's specific Command Toolbar
layout and contents, via its superclass Ui_CommandToolbar,
which is what actually needs to be refactored.

So we have two imperfect choices for classifying it:

(1) put it in ne1_ui just because of its superclass; or

(2) classify it as a widget independent of ne1_ui,
but tolerate an import in it from ne1_ui for now,
until the superclass gets refactored (which might
not happen soon).

I think it's best to classify it "optimisitically"
using scheme (2), and let the wrong-direction import
remind us that the superclass needs refactoring.

I am assuming that will cause no inter-package import cycle,
since no cycle has been reported involving this module.

So for now, the superclass is in "ne1_ui", but this module
can go into its own toplevel "CommandToolbar" package.
(Not just into "widgets" or a subpackage, since it is a major
component of an app, and might still assume it's a singleton
or have client code which assumes that. In future, we can
consider making the general part non-singleton and putting
it into its own subpackage of "widgets".)

After future refactoring of the superclass Ui_CommandToolbar
(described in its module classification comment), its general
part would join this module as part of the same package
for a "general command toolbar widget".

BTW, I think it should be the case, and might already
be the case, that whatever state this class needs to help
maintain (even given its not-yet-refactored superclass)
will actually reside in the Command Sequencer and/or
in running commands, along with the logic for how
to modify that state. This class's object is just the
UI that makes the Command Sequencer state visible
and user-controllable.

BTW2, another needed refactoring (perhaps more related
to Ui_CommandToolbar than to this module) is to make
sure commands don't need to update their own UI elements
in various ways; for more on this see

http://www.nanoengineer-1.net/mediawiki/index.php?title=NE1_module/package_organization#Command_Toolbar


History:

ninad 20070109: created this in QT4 branch and subsequently modified it.
ninad 20070125: moved ui generation code to a new file Ui_CommandManager
ninad 20070403: implemented 'Subcontrol Area'  in the command toolbar, related 
             changes (mainly revised _updateFlyoutToolBar,_setFlyoutDictionary) 
             and added/modified several docstrings  
ninad 20070623: Moved _createFlyoutToolbar from modes to here and related changes
mark 20071226: Renamed CommandManager to CommandToolbar.

ninad 20080715: a) Workaround for Qt4.3 bug 2916 (disabled 'extension indicator'
 button ">>" in the flyout toolbar.  b) some refactoring to  move common code 
 in classes FlyoutToolbar and NE1_QWidgetAction.
"""

from PyQt4 import QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QMenu
from PyQt4.Qt import QWidgetAction
from foundation.wiki_help import QToolBar_WikiHelp


from ne1_ui.toolbars.Ui_CommandToolbar import Ui_CommandToolbar
from utilities.debug import print_compact_traceback, print_compact_stack

class CommandToolbar(Ui_CommandToolbar):
    """
    Command Toolbar is the big toolbar above the 3D graphics area and
    the model tree. It is divided into the B{Control Area} and the 
    B{Flyout Toolbar Area}.

    The  B{Control Area} is a fixed toolbar on the left hand side with a
    purple background color and contains buttons with drop down menus. 
    When you click on a button in the Control Area, the Flyout Toolbar Area
    is updated and displays the menu of that button (in most cases). 

    The B{Flyout Toolbar Area} is divided into two areas, the 
    B{Subcontrol Area} (light olive background color) and the 
    B{Command Area} (light gray background color). 
    The Command Area shows commands based on the checked 
    SubControl Area button.  Thus it could be empty in some situations.
    """

    def __init__(self, win):
        """
        Constructor for class CommandToolbar.

        @param win: Mainwindow object
        @type  win: L{MWsemantics}
        """        
        self.flyoutDictionary = None
        
        Ui_CommandToolbar.__init__(self, win)       

        self.setupUi()          

        self._makeConnections() 

        if not self.cmdButtonGroup.checkedButton():
            self.cmdButtonGroup.button(0).setChecked(True)

        self.in_a_mode = None
        self.currentAction = None
        self._updateFlyoutToolBar(self.cmdButtonGroup.checkedId())      

    def _makeConnections(self):
        """
        Connect signals to slots.
        """
        self.win.connect(self.cmdButtonGroup, SIGNAL("buttonClicked(int)"), 
                         self.controlButtonChecked)  

        

    def controlButtonChecked(self, btnId):
        """
        Updates the flyout toolbar based on the button checked in the 
        control area.
        """ 
        self._updateFlyoutToolBar(btnId, self.in_a_mode)

    def resetToDefaultState(self):
        """
        Reset the Command Toolbar to the default state. i.e. the state which
        the user sees when NE1 is started -- Build button in the control area
        of the toolbar checked and the flyout toolbar on the right hand side
        shows the sub-menu items of the build control area.
        @see: SelectChunks_Command.init_gui() which calls this while entering 
        the NE1 default select chunks mode. (fixes bugs like 2682)

        """
        self.cmdButtonGroup.button(0).setChecked(True)
        #Now update the command toolbar (flyout area) such that it shows 
        #the sub-menu items of the control  button
        self._setControlButtonMenu_in_flyoutToolbar(self.cmdButtonGroup.checkedId())

        ##FYI Same effect can be acheived by using the following commented out 
        ##code. But its not obvious so not using it. 
        ###self.updateCommandToolbar(None, None, entering = False)

    def _updateFlyoutToolBar(self, btnId =0, in_a_mode = False):
        """
        Update the Flyout toolbar commands based on the checked button 
        in the control area and the checked action in the 'subcontrol' area 
        of the flyout toolbar.
        """
        ##in_a_mode : inside a mode or while editing a feature etc. 

        if self.currentAction:      
            action = self.currentAction
        else:
            action = None

        if in_a_mode:
            self._showFlyoutToolBar(True)  
            self.flyoutToolBar.clear()  
            #Menu of the checked button in the Control Area of the 
            #command toolbar
            menu = self.cmdButtonGroup.checkedButton().menu()

            if menu:
                for a in menu.actions():
                    # 'action' is self.currentAction which is obtained 
                    #when the 'updateCommandToolbar method is called
                    #while entering a mode , for instance.
                    if a is action :
                        flyoutActionList = []                   
                        flyoutDictionary = self._getFlyoutDictonary()

                        if not flyoutDictionary:
                            print_compact_traceback(
                                "bug: Flyout toolbar not" \
                                "created as flyoutDictionary doesn't exist")
                            return
                        #Dictonary object randomly orders key:value pairs. 
                        #The following ensures that the keys 
                        #(i.e. subcontrol area actions) are properly ordered
                        #This key order while adding these actions to the 
                        # the flyout toolbar subcontrol area. 
                        keyList = self.getOrderedKeyList(flyoutDictionary)

                        flyoutActionList.extend(keyList)                        
                        #Now append commands corresponding to 
                        #the checked action in sub-control area
                        for k in keyList:
                            if k.isChecked():
                                #ordered_key is a list that contains a tuple
                                #i.e. ordered_key = [(counter, key)]
                                #so order_key[0] = (counter, key)
                                #This is required because our flyoutDictinary 
                                #has keys of type:[ (counter1, key1), 
                                #                          (counter2, key2), ..]
                                ordered_key = [(counter, key) 
                                               for (counter, key) 
                                               in flyoutDictionary.keys()
                                               if key is k]
                                #Values corresponding to the ordered_key
                                commands = flyoutDictionary[ordered_key[0]]
                                #Add these commands after the subcontrol area. 
                                flyoutActionList.extend(commands)       
                        #Now add all actions collected in 'flyoutActionList 
                        #to the flyout toolbar.
                        
                        self.flyoutToolBar.addActions(flyoutActionList)

                        return      
                self._setControlButtonMenu_in_flyoutToolbar(
                    self.cmdButtonGroup.checkedId())
        else:       
            self._showFlyoutToolBar(True)
            try:            
                if self.cmdButtonGroup.button(btnId).isChecked():
                    self._setControlButtonMenu_in_flyoutToolbar(
                        self.cmdButtonGroup.checkedId())
            except:
                print_compact_traceback(
                    "command button doesn't have a menu' No actions added \
                to the flyout toolbar")
                return


    def _setControlButtonMenu_in_flyoutToolbar(self, btnId):
        """
        Sets the menu of a control area button in the flyout toolbar 
        on the right.
        @param btnId: The index of the toolbutton in the control area, 
                      that user clicked on. 
        @type  btnId: int
        """
        self.flyoutToolBar.clear()
        menu = self.cmdButtonGroup.button(btnId).menu()
        self.flyoutToolBar.addActions(menu.actions())

    def check_controlAreaButton_containing_action(self, action = None):
        """
        This method is called once while entering a command. It makes 
        sure to check the control area button which lists <action> as its
        menu item. (not true for BuildAtoms subclasses such as partlib mode)

        This ensures that when you enter a command, the flyout toolbar is set
        to show the Exit command etc buttons specific to that command. (The user
        can then always click on some other control button to display some 
        different flyout toolbar. But by default, we ensure to show the flyout 
        toolbar that the user will obviously expect to see after entering a 
        command

        @see: bug 2600, 2801 (this method fixes these bugs)
        @TODO: Ater more testing, deprecate code in 
               Ui_DnaFlyout.activateFlyoutToolbar and some other files that fixes 
               bug 2600. 
        """
        buttonToCheck = None

        if action:
            for controlAreaButton in self.cmdButtonGroup.buttons():
                if buttonToCheck:
                    break

                menu = controlAreaButton.menu()            
                if menu:
                    for a in menu.actions():
                        if a is action:
                            buttonToCheck = controlAreaButton
                            break

        if buttonToCheck:
            buttonToCheck.setChecked(True)       

    def updateCommandToolbar(self, action, obj, entering = True): #Ninad 070125
        """
        Update the command toolbar (i.e. show the appropriate toolbar) 
        depending upon, the command button pressed . 
        It calls a private method that updates the SubcontrolArea and flyout 
        toolbar based on the ControlArea button checked and also based on the 
        SubcontrolArea button checked. 

        @param obj: Object that requests its own Command Manager flyout toolbar
                    This can be a B{mode} or a B{generator}. 
        """     
        if entering:    
            self._createFlyoutToolBar(obj)          
            self.in_a_mode = entering
            #This fixes bugs like 2600, 2801
            self.check_controlAreaButton_containing_action(action)
            self.currentAction = action
            self._updateFlyoutToolBar(in_a_mode = self.in_a_mode)
        else:
            self.in_a_mode = False
            self._updateFlyoutToolBar(self.cmdButtonGroup.checkedId(), 
                                      in_a_mode = self.in_a_mode )

    def _createFlyoutDictionary(self, params):
        """
        Create the dictonary objet with subcontrol area actions as its 
        'keys' and corresponding command actions as the key 'values'. 

        @param params: A tuple that contains 3 lists: 
        (subControlAreaActionList, commandActionLists, allActionsList)

        @return: flyoutDictionary (dictionary object)
        """

        subControlAreaActionList, commandActionLists, allActionsList = params
        #The subcontrol area button and its command list form a 'key:value pair
        #in a python dictionary object
        flyoutDictionary = {}

        counter = 0
        for k in subControlAreaActionList:
            # counter is used to sort the keys in the order in which they 
            #were added
            key = (counter, k) 
            flyoutDictionary[key] = commandActionLists[counter]
            #Also add command actions to the 'allActionsList'
            allActionsList.extend(commandActionLists[counter]) 
            counter += 1

        return flyoutDictionary

   

    def _createFlyoutToolBar(self, obj):
        """
        Creates the flyout tool bar in the Command Manager.
        @see: NE1_QWidgetAction.setToolButtonPalette()
        """
        #This was earlier defined in each mode needing a flyout toolbar
        params = obj.getFlyoutActionList()
        # XXXXXXXXXXXXXXXX The semantics of these lists need to be clearly defined!
        subControlAreaActionList, commandActionLists, allActionsList = params

        flyoutDictionary = self._createFlyoutDictionary(params) 

        #Following counts the total number of actions in the 'command area'
        # if this is zero, that means our subcontrol area itself is a command 
        #area, In this case, no special rendering is needed for this subcontrol
        #area, and so its buttons are rendered as if they were command area 
        #buttons (but internally its still the 'subcontrol area'.--ninad20070622
        cmdActionCount = 0
        for l in commandActionLists:
            cmdActionCount += len(l)    

        widgetActions = filter(lambda act: 
                               isinstance(act, QtGui.QWidgetAction), 
                               allActionsList)
        
                
        self.flyoutToolBar.clear()  
        #========
        #Do this customization BEFORE adding actions to the toolbar. 
        #Reason: custom properties for the button that appears 
        #can not be set AFTER the actions are added to the QToolBar given that
        #the NE1_QWidgetAction.createWidget() method is implemented. (This 
        #method gets called when we do toolbar.addAction()
        
        #Example: The commented out code below won't change the toolbutton 
        #properties -- a leaset in Qt4.3
        ##for widget in action.createdWidgets():
                    ##if isinstance(widget, QToolButton):
                        ##btn = widget
                        ##break
                    ##btn.setPalette(somePalette)
                    ##btn.setText('someText')
        # [Ninad 2008-07-15 comment]
        #=========
        
                
        for action in widgetActions:
            #Set a different color palette for the 'SubControl' buttons in 
            #the command toolbar. 
            if [key for (counter, key) in flyoutDictionary.keys() 
                if key is action]:
                    
    
                if cmdActionCount > 0:
                    subControlPalette = self.getCmdMgrSubCtrlAreaPalette()
                    action.setToolButtonPalette(subControlPalette)
                    
                else:
                    cmdPalette = self.getCmdMgrCommandAreaPalette()  
                    action.setToolButtonPalette(cmdPalette)
                    
        
        
        self.flyoutToolBar.addActions(allActionsList)
        
        ##for action in allActionsList:       
            ##if isinstance(action, QtGui.QWidgetAction):                
                ##btn = None                
                ####for widget in action.associatedWidgets():
                ##for widget in action.createdWidgets():
                    ##if isinstance(widget, QToolButton):
                        ##btn = widget
                        ##break
                    
                ##if btn is None:
                    ##print_compact_stack("bug: Action to be added to the flyout toolbar has no"\
                          ##"ToolButton associated with it")
                    ##continue
  
                    
        self._setFlyoutDictionary(flyoutDictionary)

    
    def _showFlyoutToolBar(self, bool_show):
        """
        Hide or show flyout toolbar depending upon what is requested. 
        At the same time toggle the display of the spacer item 
        (show it when the toolbar is hidden).
        """
        if bool_show:
            self.flyoutToolBar.show()
            self.layout().removeItem(self.spacerItem)
        else:
            self.flyoutToolBar.hide()
            self.layout().addItem(self.spacerItem)

    def _setFlyoutDictionary(self, dictionary):
        """
        Set the flyout dictionary that stores subcontrol area buttons in the
        flyout toolbar as the keys and their corresponding command buttons 
        as values
        @param dictionary: dictionary object. 
        Its key is of the type (counter, subcontrolAreaAction). The counter is 
        used to sort the keys in the order in which they were created. 
        and value is the 'list of commands'  corresponding to the 
        sub control button.
        """           
        if isinstance(dictionary, dict):
            self.flyoutDictionary = dictionary
        else:
            assert isinstance(dictionary, dict) 
            self.flyoutDictionary = None

    def _getFlyoutDictonary(self):
        """
        Returns the flyout dictonary object. 
        @return: self.flyoutDictionary whose
        key : is of the type (counter, subcontrolAreaAction). The counter is 
        used to sort the keys in the order in which they were created. 
        and value is the 'list of commands'  corresponding to the 
        sub control button.
        """
        if self.flyoutDictionary:
            return self.flyoutDictionary
        else:
            print "fyi: flyoutDictionary doesn't exist. Returning None" 
            return self.flyoutDictionary

    def getOrderedKeyList(self, dictionary):
        """
        Orders the keys of a dictionary and returns it as a list. 
        Effective only when the dictonary key is a tuple of format 
        (counter, key)
        @param: dictinary object 
        @return: a list object which contains ordered keys of the dictionary 
        object.
        """
        keyList = dictionary.keys()
        keyList.sort()
        return [keys for (counter, keys) in keyList]

    def _getNumberOfVisibleToolButtons(self):
        """
          """
        numOfVisibletoolbuttons = 0
        rect = self.flyoutToolBar.visibleRegion().boundingRect()
        visibleWidth = rect.width()
        numOfVisibletoolbuttons = int(visibleWidth)/ 75
        return numOfVisibletoolbuttons     


