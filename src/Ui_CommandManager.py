# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_CommandManager.py

$Id$

History:

ninad 070125: created this file, moved and modified relevant code from CommandManager 
to this file. 

"""

__author__ = "Ninad"

from PyQt4.Qt import *
from PyQt4 import QtGui
from Utility import geticon
##from PyQt4.QtGui import QPalette, QWidget, QHBoxLayout, QButtonGroup
from PyQt4.QtGui import *
from wiki_help import QToolBar_WikiHelp
from CmdMgr_Constants import cmdMgrCntrlAreaBtnColor,\
     cmdMgrSubCntrlAreaBtnColor,\
     cmdMgrCmdAreaBtnColor


class Ui_CommandManager:
    """ This provides most of the User Interface for the command manager toolbar. 
    Called in CommandManager class"""
    
    def setupUi(self):	
	self.cmdManager = QWidget()
	#ninad 070123 : Its important to set the Vertical size policy of the cmd manager widget. 
	#otherwise the flyout QToolbar messes up the layout (makes the command manager twice as big) 
	#I have set the vertical policy as fixed. Works fine. There are some MainWindow resizing problems for 
	#but those are not due to this size policy AFAIK	
	self.cmdManager.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
		
	layout_cmd_mgr = QHBoxLayout(self.cmdManager)
	layout_cmd_mgr.setMargin(2)
	layout_cmd_mgr.setSpacing(2)
	 	    	    	    
	self.cmdManagerControlArea = QToolBar_WikiHelp(self.cmdManager)	    	    
	self.cmdManagerControlArea.setAutoFillBackground(True)
		
	self.ctrlAreaPalette = self.getCmdMgrCtrlAreaPalette()	
	self.cmdManagerControlArea.setPalette(self.ctrlAreaPalette)
		
	self.cmdManagerControlArea.setMinimumHeight(55)
	self.cmdManagerControlArea.setMinimumWidth(310)
	self.cmdManagerControlArea.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)	
    
	self.cmdButtonGroup = QButtonGroup()	
	btn_index = 0
	
	for name in ('Build','Tools', 'Move','Simulation'):
	    btn = QToolButton(self.cmdManagerControlArea)	    
	    btn.setObjectName(name)
	    btn.setFixedWidth(65)
	    btn.setMinimumHeight(55)
	    btn.setAutoRaise(True)
	    btn.setCheckable(True)
	    btn.setAutoExclusive(True)
	    iconpath = "ui/actions/Toolbars/Smart/" + name
	    btn.setIcon(geticon(iconpath))
	    btn.setIconSize(QSize(22,22))
	    btn.setText(name)
	    btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
	    btn.setPalette(self.ctrlAreaPalette)
	    self.cmdButtonGroup.addButton(btn, btn_index)
	    btn_index +=1	    
	    self.cmdManagerControlArea.layout().addWidget(btn)
	    
	    #following has issues. so not adding widget directly to the 
	    #toolbar. (instead adding it in its layout)-- ninad 070124 
	    
	    #self.cmdManagerControlArea.addWidget(btn)	    
	
	layout_cmd_mgr.addWidget(self.cmdManagerControlArea) 
	
	#Flyout Toolbar in the command manager 	
	self.flyoutToolBar = QToolBar_WikiHelp(self.cmdManager) 
	self.flyoutToolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
	self.flyoutToolBar.addSeparator()
	self.flyoutToolBar.setAutoFillBackground(True)
	
	self.commandAreaPalette = self.getCmdMgrCommandAreaPalette()
	self.flyoutToolBar.setPalette(self.commandAreaPalette)
	
	layout_cmd_mgr.addWidget(self.flyoutToolBar)   
	
	#ninad 070116: Define a spacer item. It will have the exact geometry as that of the flyout toolbar. 
	#it is added to the command manager layout only when the Flyout Toolbar is hidden. It is required
	# to keep the 'Control Area' widget fixed in its place (otherwise, after hiding the flyout toolbar, the layout 
	#adjusts the position of remaining widget items) 
	
	self.spacerItem =QSpacerItem(0,0,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
	self.spacerItem.setGeometry = self.flyoutToolBar.geometry()
	
	for btn in self.cmdButtonGroup.buttons():
	    if str(btn.objectName()) == 'Build':
		btn.setMenu(self.win.buildStructuresMenu)
		btn.setPopupMode(QToolButton.MenuButtonPopup)
	    if str(btn.objectName()) == 'Tools':
		#fyi: cmt stands for 'command manager toolbar' - ninad070406
		self.win.cmtToolsMenu = QtGui.QMenu(self.win)
		self.win.cmtToolsMenu.addAction(self.win.toolsExtrudeAction)	
		self.win.cmtToolsMenu.addAction(self.win.toolsFuseChunksAction)
		self.win.cmtToolsMenu.addSeparator()
		self.win.cmtToolsMenu.addAction(self.win.modifyMergeAction)
		self.win.cmtToolsMenu.addAction(self.win.modifyMirrorAction)
		self.win.cmtToolsMenu.addAction(self.win.modifyInvertAction)
		self.win.cmtToolsMenu.addAction(self.win.modifyStretchAction)
		btn.setMenu(self.win.cmtToolsMenu)
		btn.setPopupMode(QToolButton.MenuButtonPopup)
	    if str(btn.objectName()) == 'Move':
		self.win.moveMenu = QtGui.QMenu(self.win)
		self.win.moveMenu.addAction(self.win.toolsMoveMoleculeAction)
		self.win.moveMenu.addAction(self.win.rotateComponentsAction)
		self.win.moveMenu.addSeparator()
		self.win.moveMenu.addAction(self.win.modifyAlignCommonAxisAction)
		##self.win.moveMenu.addAction(self.win.modifyCenterCommonAxisAction)
		btn.setMenu(self.win.moveMenu)
		btn.setPopupMode(QToolButton.MenuButtonPopup)
	    if str(btn.objectName()) == 'Dimension':
		btn.setMenu(self.win.dimensionsMenu)
		btn.setPopupMode(QToolButton.MenuButtonPopup)
	    if str(btn.objectName()) == 'Simulation':
		btn.setMenu(self.win.simulationMenu)
		if self.win.simPlotToolAction in btn.menu().actions():
		    btn.menu().removeAction(self.win.simPlotToolAction)
		btn.setPopupMode(QToolButton.MenuButtonPopup)	
		
	#ninad 070125 Following creates Toolbuttons for flyout toolbars and
	#sets proper QWidget actions to them 
	for btn in self.cmdButtonGroup.buttons():
	    menu = btn.menu()
	    if menu:		
		for action in menu.actions():
		    #ninad 070125 must be a QWidgetAction
		    if action.__class__.__name__ is QtGui.QWidgetAction.__name__:
			btn = QToolButton()
			btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)	
			btn.setFixedWidth(65)
			btn.setMinimumHeight(55)					    
			#ninad 070125: make sure to a) define *default action* of button to 
			#action and b) *default widget* of *action* to 'button' 
			#(a) ensures button has got action's signals, icon,  text and other properties
			#(b) ensures action has got button's geometry	    
			btn.setDefaultAction(action)
			action.setDefaultWidget(btn)			
			#ninad 070201 temporary solution -- truncate the toolbutton text if too long. 		
			text = self.truncateText(action.text())
			btn.setText(text)
			
			#@@@ ninad070125 The following function 
			#adds a newline character after each word in toolbutton text. 
			#but the changes are reflected only on 'mode' toolbuttons 
			#on the flyout toolbar (i.e. only Checkable buttons... don't know why)
			#Disabling its use for now. 
			
			debug_wrapText = False
			
			if debug_wrapText:
			    text = self.wrapToolButtonText(action.text())			
			    if text:	
				action.setText(text)	
					   
			
						
    def truncateText(self, text, length=12, truncateSymbol='...'):
	"""Truncates the tooltip text with the given truncation symbol
	    (three dots) in the case """
	    
	#ninad 070201 This is a temporary fix. Ideally it should show the whole text in the 
	#toolbutton. But there are some layout / size policy problems because of which 
	#the toolbar height increases after you print tooltip text on two or more 
	#lines. (undesirable effect) 
	    
	if not text:
	    print "no text to truncate. Returning"
	    return 
	
	truncatedLength  = length - len(truncateSymbol)
	
	if len(text) > length:
	    return text[:truncatedLength] + truncateSymbol
	else:
	    return text
	
		
			
    def wrapToolButtonText(self, text):
	"""Add a newline character at the end of each word in the toolbutton text
	"""
	#ninad 070126 QToolButton lacks this method. This is not really a 'word wrap' 
	#but OK for now. 
	
	#@@@ ninad 070126. Not calling this method as it is creating an annoying resizing problem in 
	#the Command manager layout. Possible solution is to add a spacer item in a vbox layout to the
	#command manager layout
	
	stringlist = text.split(" ", QString.SkipEmptyParts)
	text2 = QString()
	if len(stringlist) > 1:
	    for l in stringlist:
		text2.append(l)
		text2.append("\n")
	    return text2
	        
	return None
    
    ##==================================================================##
    #color palettes (UI stuff) for different command manager areas
   
    def getCmdMgrCtrlAreaPalette(self): 
        """ Return a palette for Command Manager control area 
	(Palette for Tool Buttons in command manager control area)
        """
        return self.getPalette(None,
                               QPalette.Button,
			       cmdMgrCntrlAreaBtnColor
                               )
    
    def getCmdMgrSubCtrlAreaPalette(self):
	""" Return a palette for Command Manager sub control area 
	(Palette for Tool Buttons in command manager sub control area)
        """
	#Define the color role. Make sure to apply color to QPalette.Button 
	#instead of QPalette.Window as it is a QToolBar. - ninad 20070619
	
	return self.getPalette(None,
                               QPalette.Button,
			       cmdMgrSubCntrlAreaBtnColor
                               )
    
    def getCmdMgrCommandAreaPalette(self):
	""" Return a palette for Command Manager 'Commands area'(flyout toolbar)
	(Palette for Tool Buttons in command manager command area)
        """
	return self.getPalette(None,
                               QPalette.Button,
			       cmdMgrCmdAreaBtnColor
                               )
    
    def getPalette(self, palette, obj, color): 
        """ Given a palette, Qt object [actually a ColorRole] and a color, 
	return a new palette.If palette is None, create and return a new palette.
        """
	#Similar function is defined globally in file PropMgrBaseClass.py
	#(better to move that in to a new file that has qt helper methods 
	#like this?) import it for now in this file -- ninad 20070619
	
	import PropMgrBaseClass
	
	return PropMgrBaseClass.getPalette(palette, obj, color)
    ##==================================================================##