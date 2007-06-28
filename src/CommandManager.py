# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
CommandManager.py
@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History: 
ninad 20070109: created this in QT4 branch and subsequently modified it.
ninad 20070125: moved ui generation code to a new file Ui_CommandManager
ninad 20070403: implemented 'Subcontrol Area'  in the command manager, related 
	     changes (mainly revised _updateFlyoutToolBar,_setFlyoutDictionary) 
	     and added/modified several docstrings  
ninad 20070623:Moved _createFlyoutToolbar from modes to here and related changes
"""

__author__ = "Ninad"

from PyQt4.Qt import SIGNAL
from Ui_CommandManager import Ui_CommandManager
from PyQt4 import QtGui, Qt
from PyQt4.QtGui import *
from debug import print_compact_traceback
import platform



class CommandManager(Ui_CommandManager):
    '''Command Manager is the big toolbar at the top of the 3D graphics area and 
    the model tree. It is divided into three areas:  'Control Area', 
    and Flyout Toolbar Area' (which , in turn, includes  'SubControl Area' 
    and 'Command Area'. )
    The  'Control Area' is a fixed toolbar on the left hand side. It has a 
    default purple background color and contains command buttons with menus
    When you click on a command button, the Flyout toolbar updates and displays
    the Menu of that command button (in most cases). The flyout toolbar can be
    divided into two areas: Subcontrol Area (greenish color)
    and Command Area. The 'Command Area' shows commands based on the 
    checke SubControl Area button.Thus it could be empty in some situations. 
    '''
    
    def __init__(self, win):
	self.win = win
	
	self.setupUi()		
	self._makeConnections()	
	
	if not self.cmdButtonGroup.checkedButton():
	    self.cmdButtonGroup.button(0).setChecked(True)
	
	self.in_a_mode = None
	self.currentAction = None
	self._updateFlyoutToolBar(self.cmdButtonGroup.checkedId())	
		
    def _makeConnections(self):
	"""connect signals to slots"""
	self.win.connect(self.cmdButtonGroup, SIGNAL("buttonClicked(int)"), 
			 self.controlButtonChecked)  
	
    def controlButtonChecked(self, id):
	"""Updates the flyout toolbar based on the button checked in the 
	control area"""	
	self._updateFlyoutToolBar(id, self.in_a_mode)
   
    def _updateFlyoutToolBar(self, id =0, in_a_mode = False):
	""" Update the Flyout toolbar commands based on the checked button 
	in the control area and the checked action in the 'subcontrol' area 
	of the flyout toolbar """
	##in_a_mode : inside a mode or while editing a feature etc. 
	
	if self.currentAction:	    
	    action = self.currentAction
	else:
	    action = None
	    
	if in_a_mode:
	    self._showFlyoutToolBar(True)  
	    self.flyoutToolBar.clear()	
	    #Menu of the checked button in the Control Area of the 
	    #command manager
	    menu = self.cmdButtonGroup.checkedButton().menu()
	    
	    if menu:
		for a in menu.actions():
		    # 'action' is self.currentAction which is obtained 
		    #when the 'updateCommandManager method is called
		    #while entering a mode , for instance. 
		    if a is action :
			flyoutActionList = []			
			flyoutDictionary = self._getFlyoutDictonary()
			
			if not flyoutDictionary:
			    print_compact_traceback("bug: Flyout toolbar not \
			    created as flyoutDictionary doesn't exist")
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
				ordered_key = [(counter,key) 
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
		if self.cmdButtonGroup.button(id).isChecked():
		    self._setControlButtonMenu_in_flyoutToolbar(
			self.cmdButtonGroup.checkedId())
	    except:
		print_compact_traceback(
		    "command button doesn't have a menu' No actions added \
		     to the flyout toolbar")
		return
    
    	    
    def _setControlButtonMenu_in_flyoutToolbar(self, id):
	self.flyoutToolBar.clear()
	menu = self.cmdButtonGroup.button(id).menu()
	for a in menu.actions():
	    if a.__class__.__name__ is QtGui.QWidgetAction.__name__:
		btn = QToolButton()
		btn.setToolButtonStyle(Qt.Qt.ToolButtonTextUnderIcon)	
		btn.setMinimumWidth(75)
		btn.setMaximumWidth(75)
		btn.setMinimumHeight(62)	
		    
		btn.setDefaultAction(a)
		a.setDefaultWidget(btn)
		text = self.truncateText(a.text())	
		a.defaultWidget().setText(text)
		
	self.flyoutToolBar.addActions(menu.actions())
		    
    def updateCommandManager(self, action, obj, entering=True): #Ninad 070125
        """ Update the command manager (i.e. show the appropriate toolbar) 
	depending upon, the command button pressed . 
	It calls a privet method that updates the SubcontrolArea and flyout 
	toolbar based on the ControlAra button checked and also based on the 
	SubcontrolArea button checked. 
	@return:obj: Object that requests its own Command Manager flyout toolbar
        """	
	if entering:    
	    self._createFlyoutToolBar(obj)	    
	    self.in_a_mode = entering
	    self.currentAction = action
	    self._updateFlyoutToolBar(in_a_mode = self.in_a_mode)
	else:
	    self.in_a_mode = False
	    self._updateFlyoutToolBar(self.cmdButtonGroup.checkedId(), 
				      in_a_mode = self.in_a_mode )
    
    def _createFlyoutDictionary(self,params):
	''' Create the dictonary objet with subcontrol area actions as its 'keys'
	and corresponding command actions as the key 'values'. 
	@param: params: A tuple that contains 3 lists: 
	(subControlAreaActionList, commandActionLists, allActionsList)
	@return: flyoutDictionary (dictionary object)'''
	
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
	    counter +=1
	
	return flyoutDictionary
	
	    
    def _createFlyoutToolBar(self, obj):
	'''Creates the flyout tool bar in the Command Manager '''
	
	#This was earlier defined in each mode needing a flyout toolbar

	params = obj.getFlyoutActionList()
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
		    	
	for action in allActionsList:	    
	    if action.__class__.__name__ is QtGui.QWidgetAction.__name__:    
		btn = QToolButton()
		btn.setToolButtonStyle(Qt.Qt.ToolButtonTextUnderIcon)	
		btn.setMinimumWidth(75)
		btn.setMaximumWidth(75)
		btn.setMinimumHeight(62)		
	
		#ninad 070125: make sure to a) define *default action* of button  
		#to action and b) *default widget* of *action* to 'button' 
		#(a) ensures button has got action's signals, icon, text and 
		#other properties
		#(b) ensures action has got button's geometry	    
		btn.setDefaultAction(action)
		action.setDefaultWidget(btn)	
		
		# I forgot to add the following lines (that truncate the text),
		# while transfering this method from
		# mode to here... fixes bug 2471 - ninad 20070625
		
		#ninad 070201 temporary solution -- truncate the toolbutton 	 
		#text if too long. 
		text = self.truncateText(action.text()) 	 
		btn.setText(text)
			 
		#@@@ ninad070125 The following function 
		#adds a newline character after each word in toolbutton text. 
		#but the changes are reflected only on 'mode' toolbuttons 
		#on the flyout toolbar (i.e.only Checkable buttons..don't know why)
		#Disabling its use for now. 
		debug_wrapText = False
		
		if debug_wrapText:
		    text = self.wrapToolButtonText(action.text())		
		    if text:	
			action.setText(text)	
		#Set a different color palette for the 'SubControl' buttons in 
		#the command manager. 
		if [key for (counter, key) in flyoutDictionary.keys() 
		    if key is action]:
		    btn.setAutoFillBackground(True)	
		    
		    if cmdActionCount > 0:
			subControlPalette = self.getCmdMgrSubCtrlAreaPalette()
			btn.setPalette(subControlPalette)	
		    else:
			cmdPalette = self.getCmdMgrCommandAreaPalette()
			btn.setPalette(cmdPalette)		    
		    							
	self._setFlyoutDictionary(flyoutDictionary)
	pass
    
	    	    
    def _showFlyoutToolBar(self, bool):
	""" Hide or show flyout toolbar depending upon what is requested. 
	At the same time toggle the display of the spacer item 
	(show it when the toolbar is hidden)"""
	if bool:
	    self.flyoutToolBar.show()
	    self.cmdManager.layout().removeItem(self.spacerItem)
	else:
	    self.flyoutToolBar.hide()
	    self.cmdManager.layout().addItem(self.spacerItem)
	    
    def _setFlyoutDictionary(self, dictionary):
	''' set the flyout dictionary that stores subcontrol area buttons in the 
	flyout toolbar as the keys and their corresponding command buttons 
	as values
	@param dictionary: dictionary object. 
	Its key is of the type (counter, subcontrolAreaAction). The counter is 
	used to sort the keys in the order in which they were created. 
	and value is the 'list of commands'  corresponding to the 
	sub control button'''		
	if isinstance(dictionary, dict):
	    self.flyoutDictionary = dictionary
	else:
	    assert isinstance(dictionary, dict) 
	    self.flyoutDictionary = None
    
    def _getFlyoutDictonary(self):
	''' Returns the flyout dictonary object. 
	@return: self.flyoutDictionary whose
	key : is of the type (counter, subcontrolAreaAction). The counter is 
	used to sort the keys in the order in which they were created. 
	and value is the 'list of commands'  corresponding to the 
	sub control button'''
	if self.flyoutDictionary:
	    return self.flyoutDictionary
	else:
	    print "fyi: flyoutDictionary doesn't exist. Returning None" 
	    return self.flyoutDictionary
        
    
    def getOrderedKeyList(self, dictionary):
	''' Orders the keys of a dictionary and returns it as a list. 
	Effective only when the dictonary key is a tuple of format 
	(counter, key)
	@param: dictinary object 
	@return: a list object which contains ordered keys of the dictionary 
	object
	'''
	keyList = dictionary.keys()
	keyList.sort()
	return [keys for (counter, keys) in keyList]
    
	
    