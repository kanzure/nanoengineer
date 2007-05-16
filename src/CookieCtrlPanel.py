# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
CookieCtrlPanel.py

Class used for the GUI controls for the cookie mode.

$Id$

Note: Till Alpha8, this mode was called Cookie Cutter mode. In Alpha9 
it has been renamed to 'Build Crystal' mode. -- ninad 20070511
"""
from PyQt4.Qt import *
from PyQt4 import QtGui
from Utility import imagename_to_pixmap
from constants import dispLabel
from qt4transition import *
from PropertyManagerMixin import PropertyManagerMixin
from CookiePropertyManager import CookiePropertyManager
from Utility import geticon


class CookieCtrlPanel(CookiePropertyManager):
    """This is class is served to provide GUI controls to the cookie-cutter mode.
    """
       
    def __init__(self, parent):
        """<parent> is the main window  for the program"""
        self.w = parent
	
	#Create the Flyout toolbar in the Command manager 
	self._createFlyoutToolBar()
                               
        self.pw = None # pw is active part window
        	
        CookiePropertyManager.__init__(self)
        self._makeConnections()

        
    def _createFlyoutToolBar(self):
        """Creates the flyout tool bar in the command manager for Cookie mode"""
	   		
	btn_index= 0
	
	#Create an action group and add all the cookie selection shape buttons to it
	self.cookieSelectionGroup = QActionGroup(self.w)
	
	actionlist, flyoutDictionary = self.getFlyoutActionList()
	
	#Control button color palette for the Exit Chunk button in the 
	#flyout toolbar
	controlPalette = QtGui.QPalette() 
	controlPalette.setColor(QtGui.QPalette.Active,
				   QtGui.QPalette.Button,
				   QtGui.QColor(204,204,255)) 
	controlPalette.setColor(QtGui.QPalette.Inactive,
				   QtGui.QPalette.Button,
				   QtGui.QColor(204,204,255)) 
	controlPalette.setColor(QtGui.QPalette.Disabled,
				   QtGui.QPalette.Button,
				   QtGui.QColor(204,204,255)) 
	
	#Set a different color palette for the 'SubControl' buttons in the 
	#command manager. For Cookie cutter , use the 'Command Area' palette
	
	subControlPalette = QtGui.QPalette() 
	subControlPalette.setColor(QtGui.QPalette.Active,
				   QtGui.QPalette.Button,
				   QtGui.QColor(230, 230, 230)) 
	subControlPalette.setColor(QtGui.QPalette.Inactive,
				   QtGui.QPalette.Button,
				   QtGui.QColor(230, 230, 230)) 
	subControlPalette.setColor(QtGui.QPalette.Disabled,
				   QtGui.QPalette.Button,
				   QtGui.QColor(230, 230, 230)) 
	
	for action in actionlist:	    
	    if action.__class__.__name__ is QtGui.QWidgetAction.__name__:
		if action is not self.exitCrystalAction:	
		    action.setCheckable(True)
		    self.cookieSelectionGroup.addAction(action)
		btn = QToolButton()
		btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)	
		btn.setFixedWidth(62)
		btn.setMinimumHeight(55)		
		
		iconpath = "ui/actions/Toolbars/Smart/" + str(action.text())
		action.setIcon(geticon(iconpath))
		#ninad 070125: make sure to a) define *default action* of button to 
		#action and b) *default widget* of *action* to 'button' 
		#(a) ensures button has got action's signals, icon,  text and other properties
		#(b) ensures action has got button's geometry	    
		btn.setDefaultAction(action)
		action.setDefaultWidget(btn)		
		#@@@ ninad070125 The following function 
		#adds a newline character after each word in toolbutton text. 
		#but the changes are reflected only on 'mode' toolbuttons 
		#on the flyout toolbar (i.e. only Checkable buttons... don't know why)
		#Disabling its use for now. 
		debug_wrapText = False
		
		if debug_wrapText:
		    text = self.w.commandManager.wrapToolButtonText(action.text())			
		    if text:	
			action.setText(text)	
		#Set a different color palette for the 'SubControl' buttons in 
		#the command manager. 
		if [key for (counter, key) in flyoutDictionary.keys() 
		    if key is action]:
		    btn.setAutoFillBackground(True)
		    btn.setPalette(subControlPalette)	
		
		#Set control button color palette for the Exit Chunk button in 
		#the flyout toolbar
		if action is self.exitCrystalAction:
		    btn.setAutoFillBackground(True)
		    btn.setPalette(controlPalette)	
		    action.setIcon(geticon('ui/actions/Toolbars/Smart/Exit'))
			
	    if not self.cookieSelectionGroup.checkedAction():
		self.DefaultSelAction.setChecked(True)
		
	    self.flyoutDictionary = flyoutDictionary
	
    def getFlyoutActionList(self):
	""" returns custom actionlist that will be used in a specific mode or editing a feature etc
	Example: while in cookie cutter mode, the _createFlyoutToolBar method calls
	this """	
	
	#'allActionsList' returns all actions in the flyout toolbar 
	#including the subcontrolArea actions
	allActionsList = []
	
	#Action List for  subcontrol Area buttons. 
	#In cookie cutter, there is really no subcontrol area. 
	#We will treat subcontrol area same as 'command area' 
	#(subcontrol area buttons will have an empty list as their command area 
	#list). We will set  the Comamnd Area palette background color to the
	#subcontrol area.
	
	subControlAreaActionList =[] 
		
	self.exitCrystalAction = QtGui.QWidgetAction(self.w)
	self.exitCrystalAction.setText("Exit Crystal")
	self.exitCrystalAction.setCheckable(True)
	self.exitCrystalAction.setChecked(True)
	subControlAreaActionList.append(self.exitCrystalAction)
	
	separator = QtGui.QAction(self.w)
	separator.setSeparator(True)
	subControlAreaActionList.append(separator) 
	
	self.DefaultSelAction = QWidgetAction(self.w)
	self.DefaultSelAction.setObjectName("DEFAULT")
	self.DefaultSelAction.setText("Default")	
	subControlAreaActionList.append(self.DefaultSelAction)
	
	self.CircleSelAction = QWidgetAction(self.w)	
	self.CircleSelAction.setObjectName("CIRCLE")
	self.CircleSelAction.setText("Circle")	
	subControlAreaActionList.append(self.CircleSelAction)
	
	self.RectCtrSelAction = QWidgetAction(self.w)	
	self.RectCtrSelAction.setObjectName("RECTANGLE")
	self.RectCtrSelAction.setText("RectCenter")
	subControlAreaActionList.append(self.RectCtrSelAction)
		
	self.HexagonSelAction = QWidgetAction(self.w)
	self.HexagonSelAction.setObjectName("HEXAGON")
	self.HexagonSelAction.setText("Hexagon")
	subControlAreaActionList.append(self.HexagonSelAction)
	
	self.TriangleSelAction = QWidgetAction(self.w)
	self.TriangleSelAction.setObjectName("TRIANGLE")
	self.TriangleSelAction.setText("Triangle")
	subControlAreaActionList.append(self.TriangleSelAction)
	
	self.RectCornerSelAction = QWidgetAction(self.w)
	self.RectCornerSelAction.setObjectName("RECT_CORNER")
	self.RectCornerSelAction.setText("RectCorners")
	subControlAreaActionList.append(self.RectCornerSelAction)
	
	self.LassoSelAction = QWidgetAction(self.w)	
	self.LassoSelAction.setObjectName("LASSO")
	self.LassoSelAction.setText("Lasso")
	subControlAreaActionList.append(self.LassoSelAction)
	
	self.DiamondSelAction = QWidgetAction(self.w)
	self.DiamondSelAction.setObjectName("DIAMOND")
	self.DiamondSelAction.setText("Diamond")
	subControlAreaActionList.append(self.DiamondSelAction)
	
	self.SquareSelAction = QWidgetAction(self.w)
	self.SquareSelAction.setObjectName("SQUARE")
	self.SquareSelAction.setText("Square")
	subControlAreaActionList.append(self.SquareSelAction)
	
	allActionsList.extend(subControlAreaActionList)
	
	#Empty actionlist for the 'Command Area'
	commandActionLists = [] 
	
	#Append empty 'lists' in 'commandActionLists equal to the 
	#number of actions in subControlArea 
	for i in range(len(subControlAreaActionList)):
	    lst = []
	    commandActionLists.append(lst)
	    
	#The subcontrol area buuton and its command list form a 'key:value pair
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
		
	return allActionsList, flyoutDictionary
    
    def updateCommandManager(self, bool_entering = True):
	''' Update the command manager '''
	
	self.w.commandManager.updateCommandManager(self.w.toolsCookieCutAction,
						   self.flyoutDictionary, 
						   entering =bool_entering)
	                
    def _makeConnections(self):
        """Connect signal to slots """
        self.connect(self.latticeCBox, SIGNAL("activated ( int )"), self.changeLatticeType)  
            
        self.connect(self.orientButtonGroup, SIGNAL("buttonClicked(int)"), self.changeGridOrientation)
            
        self.connect(self.antiRotateButton, SIGNAL("clicked()"), self.antiRotateView)
        self.connect(self.rotateButton, SIGNAL("clicked()"), self.rotateView)
            
        self.connect(self.addLayerButton,SIGNAL("clicked()"), self.addLayer)
        self.connect(self.currentLayerCBox,SIGNAL("activated(int)"), self.changeLayer)
            
        self.connect(self.layerCellsSpinBox,SIGNAL("valueChanged(int)"), self.setThickness)
        #self.connect(self.gridColorButton,SIGNAL("clicked()"),self.changeGridColor)
        
        self.connect(self.gridLineCheckBox,SIGNAL("toggled(bool)"),self.showGridLine)
        
        self.connect(self.freeViewCheckBox,SIGNAL("toggled(bool)"),self.setFreeView)
        self.connect(self.fullModelCheckBox, SIGNAL("toggled(bool)"),self.toggleFullModel)
        self.connect(self.snapGridCheckBox, SIGNAL("toggled(bool)"), self.setGridSnap)
            
        self.connect(self.dispModeCBox, SIGNAL("activated(const QString &)"), self.changeDispMode)
  
        self.connect(self.cookieSelectionGroup, SIGNAL("triggered(QAction *)"),self.changeSelectionShape)
	
	self.connect(self.exitCrystalAction, SIGNAL("triggered()"), self.w.toolsDone)
       
    def _setAutoShapeAcclKeys(self, on):
        """If <on>, then set the acceleration keys for autoshape selection in this mode, otherwise, like when exit. set it to empty. """
        if on:
	    self.DefaultSelAction.setShortcut('D')
	    self.CircleSelAction.setShortcut('C')
	    self.RectCtrSelAction.setShortcut('R')
	    self.HexagonSelAction.setShortcut('H')
	    self.TriangleSelAction.setShortcut('T')
	    self.RectCornerSelAction.setShortcut('SHIFT+R')
	    self.LassoSelAction.setShortcut('L')
	    self.DiamondSelAction.setShortcut('SHIFT+D')
	    self.SquareSelAction.setShortcut('S')
	    
	else:
	    for btn in self.cookieSelectionGroup.actions():
		btn.setShortcut('')
                           
   
    def initGui(self):
        """This is used to initialize GUI items which needs to change every time when the mode is on. """
        
        self.w.dashboardHolder.hide() #@@ ninad 070104  Once all the dashboards become Property Managers,
        #the w.dashBoardHolder (dockwidget) will be removed completely. So this is a temporary code. (see also restoreGui)
        
        self.w.toolsCookieCutAction.setChecked(1) # toggle on the Cookie Cutter icon 
	
	#always show Exit Crystal button checked. (this implementation may change in future --ninad 070131)
	self.exitCrystalAction.setChecked(True) 
        
        self.openPropertyManager(self) # ninad 061227 see PropertymanagerMixin

        self.updateCommandManager(bool_entering = True)
                        
        self.latticeCBox.setEnabled(True)

        #Set projection to ortho, display them
        self.w.setViewOrthoAction.setChecked(True)  
        self.w.setViewOrthoAction.setEnabled(False)
        self.w.setViewPerspecAction.setEnabled(False)
	
        # Other things that have been lost at this point:
        # self.layerThicknessLineEdit
        self.layerCellsSpinBox.setValue(2)
        self.gridRotateAngle.setValue(45)
        
        self.currentLayerCBox.clear()
        self.currentLayerCBox.addItem("1")   #QString(str(len(self.layers[0])))) ? ? ?
        self.addLayerButton.setEnabled(False)

        # Disable some action items in the main window.
        self.w.zoomToolAction.setEnabled(0) # Disable "Zoom Tool"
        self.w.panToolAction.setEnabled(0) # Disable "Pan Tool"
        self.w.rotateToolAction.setEnabled(0) # Disable "Rotate Tool"
        self.w.setViewZoomtoSelectionAction.setEnabled(0) # Disable Zoom to Selection
        self.w.viewOrientationAction.setEnabled(0) #Disable Orientation Window
        

         # Disable  these toolbars
        self.w.buildToolsToolBar.setEnabled(False)
        self.w.simulationToolBar.setEnabled(False)

        #Set acclerating keys for auto-selection shape
        self._setAutoShapeAcclKeys(True)

        self.w.dashboardHolder.setWidget(self.w.cookieCutterDashboard)
      
    
    def restoreGui(self):
        """Restore GUI items when exit from the cookie-cutter mode. """
        	
	self.updateCommandManager(bool_entering = False)
	        
        self.w.toolsCookieCutAction.setChecked(0) #Toggle cookie cutter icon
        
        self.closePropertyManager() 

        self.w.cookieCutterDashboard.hide()
            
        self.w.zoomToolAction.setEnabled(1) # Enable "Zoom Tool"
        self.w.panToolAction.setEnabled(1) # Enable "Pan Tool"
        self.w.rotateToolAction.setEnabled(1) # Enable "Rotate Tool"
        self.w.setViewZoomtoSelectionAction.setEnabled(1) # Enable Zoom to Selection
        self.w.viewOrientationAction.setEnabled(1) #Enable Orientation Window
	# Enable these toolbars
        self.w.buildToolsToolBar.setEnabled(True)
        self.w.simulationToolBar.setEnabled(True)
	# Enable all those view options
        self.enableViewChanges(True)
	
        #Hide the Cookie Selection Dashboard
        self.w.cookieSelectDashboard.hide()
            
        #Restore display mode status message
        self.w.dispbarLabel.setText( "Current Display: " + dispLabel[self.w.glpane.displayMode] )
            
        # Restore view projection, enable them.
        self.w.setViewOrthoAction.setEnabled(True)
        self.w.setViewPerspecAction.setEnabled(True)
            
        # Turn off acclerating keys
        self._setAutoShapeAcclKeys(False)
            
   
    def enableViewChanges(self, enableFlag):
        """Turn on or off view changes depending on <param> 'enableFlag'. 
	Turn off view changes is needed during the cookie-cutting stage. """
            
	for c in self.orientButtonGroup.buttons():
	    c.setEnabled(enableFlag) 
            
        self.gridRotateAngle.setEnabled(enableFlag)
        self.antiRotateButton.setEnabled(enableFlag) 
        self.rotateButton.setEnabled(enableFlag)                
        self.w.enableViews(enableFlag) # Mark 051122.
            
    
    def changeSelectionShape(self, action):
        """Slot method that is called when user changes selection shape by GUI. """
        if self.w.glpane.mode.modename != 'COOKIE': return
            
	sShape = action.objectName()
	self.w.glpane.mode.changeSelectionShape(sShape)

    def getSelectionShape(self):
        """Return the current selection shape that is checked. """
        selectionShape = self.cookieSelectionGroup.checkedAction().objectName()	   
        return selectionShape
   
    def setThickness(self, value):
       self.w.glpane.mode.setThickness(value)
          
    def addLayer(self):
        self.addLayerButton.setEnabled(False)
        layerId = self.w.glpane.mode.addLayer()
            
        self.currentLayerCBox.addItem(QString(str(layerId)))
        self.currentLayerCBox.setCurrentIndex(layerId-1)
            
        self.w.glpane.gl_update()

    def changeLayer(self, value):
        """Change current layer to <value> layer """
        self.w.glpane.mode.change2Layer(value)

    def setFreeView(self, freeView):
        """Slot function to switch between free view/cookie selection states """
        self.w.glpane.mode.setFreeView(freeView)
        
    def toggleFullModel(self, showFullModel):
        """Slot function for the check box of 'Full Model' in cookie-cutter dashboard """
        self.w.glpane.mode.toggleFullModel(showFullModel)
        
    def showGridLine(self, show):
        """Slot function"""
        self.w.glpane.mode.showGridLine(show)
            
    def setGridSnap(self, snap):
        """Turn on/off the grid snap option """
        self.w.glpane.mode.gridSnap = snap
        pass
                
    def changeGridColor(self):
        """Open the stand color chooser dialog to change grid line color """
        c = QColorDialog.getColor(QColor(222,148,0), self)
        if c.isValid():
            self.gridColorLabel.setPaletteBackgroundColor(c)
            self.w.glpane.mode.setGridLineColor(c)

    def changeLatticeType(self, lType):
        self.w.glpane.mode.changeLatticeType(lType)
        if lType != 0: #Changes to other lattice type
            #Disable the snap to grid feature
            self.setGridSnap(False)
            self.snapGridCheckBox.setEnabled(False)
        else:
            self.snapGridCheckBox.setEnabled(True)
                
    def changeDispMode(self, mode):
        self.w.glpane.mode.changeDispMode(mode)
        
    def changeGridOrientation(self, value):
        if value == 0: self._orient100()
        elif value == 1: self._orient110()
        elif value == 2: self._orient111()
	       
    def _rotView(self, direction):
        """Rotate the view anti-clockwise or clockWise. 
        If <direction> == True, anti-clockwise rotate, otherwise, 
        clockwise rotate"""
        from math import pi
        from VQT import Q, V
           
        angle = self.gridRotateAngle.value()
        if not direction: angle = -angle
        angle = pi * angle/180.0
       
        glpane = self.w.glpane
           
        glpane.quat += Q(V(0, 0, 1), angle)
        glpane.gl_update()
       
    def antiRotateView(self):
        """Anti-clockwise rotatation """
        self._rotView(True)
       
    def rotateView(self):
        """clock-wise rotation """
        self._rotView(False)

    def _orient100(self):
        """ Along one axis """
        self.w.glpane.mode.setOrientSurf(0)
        self.w.glpane.snapquat100()
    
    def _orient110(self):
        """halfway between two axes"""           
        self.w.glpane.mode.setOrientSurf(1)
        self.w.glpane.snapquat110()
    
    def _orient111(self):
        """equidistant from three axes """
        self.w.glpane.mode.setOrientSurf(2)
        self.w.glpane.snapquat111()
