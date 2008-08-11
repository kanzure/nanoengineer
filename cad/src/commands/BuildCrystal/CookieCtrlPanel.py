# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
CookieCtrlPanel.py

Class used for the GUI controls for the cookie command.

$Id$

Note: Till Alpha8, this command was called Cookie Cutter mode. In Alpha9 
it has been renamed to 'Build Crystal' mode. -- ninad 20070511
"""

from PyQt4 import QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import QActionGroup
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QWidgetAction
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QString
from PyQt4.Qt import QColor
from PyQt4.Qt import QColorDialog

from commands.BuildCrystal.CookiePropertyManager import CookiePropertyManager
from utilities.icon_utilities import geticon
from utilities.constants import dispLabel
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction


class CookieCtrlPanel(CookiePropertyManager):
    """
    This class provides GUI controls to the cookie-cutter command.
    """
       
    def __init__(self, command):
        """
        """
        self.w = command.w
        self.cookieCommand = command
            #bruce 071008, probably redundant with some other attribute
                                       
        self.pw = None # pw is active part window
        
        self._init_flyoutActions()
        CookiePropertyManager.__init__(self, command)
        self._makeConnections()

    def _init_flyoutActions(self):
        """
        Define flyout toolbar actions for this command
        """
        #Create an action group and add all the cookie selection shape buttons to it
        self.cookieSelectionGroup = QActionGroup(self.w)
        
        #Action List for  subcontrol Area buttons. 
        #In cookie cutter, there is really no subcontrol area. 
        #We will treat subcontrol area same as 'command area' 
        #(subcontrol area buttons will have an empty list as their command area 
        #list). We will set  the Comamnd Area palette background color to the
        #subcontrol area. This list will be used in getFlyoutActionList
        
        self.subControlAreaActionList =[] 
                
        self.exitCrystalAction = NE1_QWidgetAction(self.w, 
                                                     win = self.w)
        self.exitCrystalAction.setText("Exit Crystal")
        self.exitCrystalAction.setCheckable(True)
        self.exitCrystalAction.setChecked(True)
        self.exitCrystalAction.setIcon(
            geticon('ui/actions/Toolbars/Smart/Exit.png'))
        self.subControlAreaActionList.append(self.exitCrystalAction)
        
        separator = QtGui.QAction(self.w)
        separator.setSeparator(True)
        self.subControlAreaActionList.append(separator) 
        
        self.DefaultSelAction = NE1_QWidgetAction(self.w, win = self.w)
        self.DefaultSelAction.setObjectName("DEFAULT")
        self.DefaultSelAction.setText("Default")        
        self.subControlAreaActionList.append(self.DefaultSelAction)
        self.DefaultSelAction.setToolTip( "Default Selection (D)")
        self.DefaultSelAction.setWhatsThis(
        """<b>Default </b>
        <p>
       Defines the crystal shape as a polygon with the user specifying the 
       sides
        </p>""")
        
        self.CircleSelAction = NE1_QWidgetAction(self.w, win = self.w)    
        self.CircleSelAction.setObjectName("CIRCLE")
        self.CircleSelAction.setText("Circle")  
        self.subControlAreaActionList.append(self.CircleSelAction)
        self.CircleSelAction.setToolTip( "Circle (C)")
        self.CircleSelAction.setWhatsThis(
        """<b>Circle </b>
        <p>
        Draws the crystal geometry as a circle
        </p>""")
  
        self.RectCtrSelAction = NE1_QWidgetAction(self.w, win = self.w)   
        self.RectCtrSelAction.setObjectName("RECTANGLE")
        self.RectCtrSelAction.setText("RectCenter")
        self.subControlAreaActionList.append(self.RectCtrSelAction)
        self.RectCtrSelAction.setToolTip( "Rectangular Center (R)")
        self.RectCtrSelAction.setWhatsThis(
        """<b>Rectangle - Center Select</b>
        <p>
        Draws the crystal geometry as a rectangle with the cursor defining
        the center of the rectangle
        </p>""")
                
        self.HexagonSelAction = NE1_QWidgetAction(self.w, win = self.w)
        self.HexagonSelAction.setObjectName("HEXAGON")
        self.HexagonSelAction.setText("Hexagon")
        self.subControlAreaActionList.append(self.HexagonSelAction)
        self.HexagonSelAction.setToolTip( "Hexagon (H)")
        self.HexagonSelAction.setWhatsThis(
        """<b>Hexagon </b>
        <p>
        Draws the crystal geometry as a hexagon
        </p>""")
                
        self.TriangleSelAction = NE1_QWidgetAction(self.w, win = self.w)
        self.TriangleSelAction.setObjectName("TRIANGLE")
        self.TriangleSelAction.setText("Triangle")
        self.subControlAreaActionList.append(self.TriangleSelAction)
        self.TriangleSelAction.setToolTip( "Triangle (T)")
        self.TriangleSelAction.setWhatsThis(
        """<b>Triangle </b>
        <p>
        Draws the crystal geometry as a triangle
        </p>""")
                
                
        self.RectCornerSelAction = NE1_QWidgetAction(self.w, win = self.w)
        self.RectCornerSelAction.setObjectName("RECT_CORNER")
        self.RectCornerSelAction.setText("RectCorners")
        self.subControlAreaActionList.append(self.RectCornerSelAction)
        self.RectCornerSelAction.setToolTip( "Rectangular Corner (Shift+R)")
        self.RectCornerSelAction.setWhatsThis(
        """<b>Rectangle - Corner Select</b>
        <p>
        Draws the crystal geometry as a rectangle with the cursor defining 
        the initial corner 
        </p>""")
        
               
        self.LassoSelAction = NE1_QWidgetAction(self.w, win = self.w)     
        self.LassoSelAction.setObjectName("LASSO")
        self.LassoSelAction.setText("Lasso")
        self.subControlAreaActionList.append(self.LassoSelAction)
        self.LassoSelAction.setToolTip( "Lasso (L)")
        self.LassoSelAction.setWhatsThis(
        """<b>Lasso</b>
        <p>
        Can be used to draw irregular crystal geometries 
        </p>""")
        
        self.DiamondSelAction = NE1_QWidgetAction(self.w, win = self.w)
        self.DiamondSelAction.setObjectName("DIAMOND")
        self.DiamondSelAction.setText("Diamond")
        self.subControlAreaActionList.append(self.DiamondSelAction)
        self.DiamondSelAction.setToolTip( "Diamond (D)")
        self.DiamondSelAction.setWhatsThis(
        """<b>Diamond</b>
        <p>
        Draws the crystal geometry as a diamond
        </p>""")
        
        self.SquareSelAction = NE1_QWidgetAction(self.w, win = self.w)
        self.SquareSelAction.setObjectName("SQUARE")
        self.SquareSelAction.setText("Square")
        self.subControlAreaActionList.append(self.SquareSelAction)
        self.SquareSelAction.setToolTip( "Square(S)")
        self.SquareSelAction.setWhatsThis(
        """<b>Square</b>
        <p>
        Draws the crystal geometry as a square
        </p>""")
        
        for action in self.subControlAreaActionList[1:]:
            if isinstance(action, QtGui.QWidgetAction):               
                action.setCheckable(True)
                self.cookieSelectionGroup.addAction(action)
                iconpath = "ui/actions/Toolbars/Smart/" + str(action.text()) + ".png"
                action.setIcon(geticon(iconpath))
        
        if not self.cookieSelectionGroup.checkedAction():
                self.DefaultSelAction.setChecked(True)

                                        
    def getFlyoutActionList(self):
        """
        Returns a tuple that contains mode-specific actionlists in the 
        added in the flyout toolbar of the mode. 
        CommandToolbar._createFlyoutToolBar method calls this 
        @return: params: A tuple that contains 3 lists: 
        (subControlAreaActionList, commandActionLists, allActionsList).
        """       
        
        #'allActionsList' returns all actions in the flyout toolbar 
        #including the subcontrolArea actions
        allActionsList = []
        
        #Action List for  subcontrol Area buttons. 
        #In cookie cutter, there is really no subcontrol area. 
        #We will treat subcontrol area same as 'command area' 
        #(subcontrol area buttons will have an empty list as their command area 
        #list). We will set  the Comamnd Area palette background color to the
        #subcontrol area.
                
        subControlAreaActionList = self.subControlAreaActionList
        
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
                        
        params = (subControlAreaActionList, commandActionLists, allActionsList)
        
        return params
    
    
    def updateCommandToolbar(self, bool_entering = True):
        """
        Update the Command Toolbar.
        """
        if bool_entering:
            action = self.w.toolsCookieCutAction        
        else:
            action = None
        # object that needs its own flyout toolbar. In this case it is just 
        # the mode itself.
        # [later, bruce 071009: self is now a PM -- is that what this should
        #  now say, instead of 'mode'?] 
        obj = self  
                    
        self.w.commandToolbar.updateCommandToolbar(action,
                                                   obj, 
                                                   entering = bool_entering)
    
                        
    def _makeConnections(self):
        """Connect signal to slots """
        
        self.connect(self.latticeCBox, SIGNAL("activated ( int )"), self.changeLatticeType)  
            
        self.connect(self.orientButtonGroup, SIGNAL("buttonClicked(int)"), self.changeGridOrientation)
            
        self.connect(self.rotGridAntiClockwiseButton, SIGNAL("clicked()"), self.antiRotateView)
        self.connect(self.rotGridClockwiseButton, SIGNAL("clicked()"), self.rotateView)
            
        self.connect(self.addLayerButton,SIGNAL("clicked()"), self.addLayer)
        self.connect(self.currentLayerComboBox,SIGNAL("activated(int)"), self.changeLayer)
            
        self.connect(self.layerCellsSpinBox,SIGNAL("valueChanged(int)"), self.setThickness)
        #self.connect(self.gridColorButton,SIGNAL("clicked()"),self.changeGridColor)
        
        self.connect(self.gridLineCheckBox,SIGNAL("toggled(bool)"),self.showGridLine)
        
        self.connect(self.freeViewCheckBox,SIGNAL("toggled(bool)"),self.setFreeView)
        self.connect(self.fullModelCheckBox, SIGNAL("toggled(bool)"),self.toggleFullModel)
        self.connect(self.snapGridCheckBox, SIGNAL("toggled(bool)"), self.setGridSnap)
            
        self.connect(self.dispModeComboBox, SIGNAL("activated(const QString &)"), 
                     self.changeDispMode)
        
        self.connect(self.cookieSelectionGroup, SIGNAL("triggered(QAction *)"),
                     self.changeSelectionShape)
        
        self.connect(self.exitCrystalAction, SIGNAL("triggered()"), 
                     self.w.toolsDone) 
  
       
    def _setAutoShapeAcclKeys(self, on):
        """
        If <on>, then set the acceleration keys for autoshape selection
        in this command; otherwise, like when exit. set it to empty.
        """
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
        """
        This is used to initialize GUI items which need
        to change every time the command becomes active.
        """
        # WARNING: the docstring said "every time when the mode is on"
        # and I am only guessing that it meant "every time the command becomes active".
        # [bruce 071009]
        
        self.w.toolsCookieCutAction.setChecked(1) # toggle on the Cookie Cutter icon 
        
        #always show Exit Crystal button checked. (this implementation may change in future --ninad 070131)
        self.exitCrystalAction.setChecked(True) 
        
        self.show()

        self.updateCommandToolbar(bool_entering = True)
                        
        self.latticeCBox.setEnabled(True)

        #Set projection to ortho, display them
        self.w.setViewOrthoAction.setChecked(True)  
        self.w.setViewOrthoAction.setEnabled(False)
        self.w.setViewPerspecAction.setEnabled(False)
        
        # Other things that have been lost at this point:
        # self.layerThicknessLineEdit
        self.layerCellsSpinBox.setValue(2)
        self.rotateGridByAngleSpinBox.setValue(45)
        
        self.currentLayerComboBox.clear()
        self.currentLayerComboBox.addItem("1")   #QString(str(len(self.layers[0])))) ? ? ?
        self.addLayerButton.setEnabled(False)

        # Disable some action items in the main window.
        self.w.zoomToAreaAction.setEnabled(0) # Disable "Zoom to Area"
        self.w.setViewZoomtoSelectionAction.setEnabled(0) # Disable Zoom to Selection
        self.w.viewOrientationAction.setEnabled(0) #Disable Orientation Window
        
        # Temporarily disable the global display style combobox since this 
        # has its own special "crystal" display styles (i.e. spheres and tubes).
        # I decided to leave them enabled since the user might want to see the
        # entire model and change the global display style. --Mark 2008-03-16
        #self.win.statusBar().dispbarLabel.setEnabled(False)
        #self.win.statusBar().globalDisplayStylesComboBox.setEnabled(False)
        
        # Disable these toolbars
        self.w.buildToolsToolBar.setEnabled(False)
        self.w.simulationToolBar.setEnabled(False)

        # Set acceleration keys for auto-selection shape
        self._setAutoShapeAcclKeys(True)
      
    
    def restoreGui(self):
        """
        Restore GUI items when exiting from the PM (command).
        """
                
        self.updateCommandToolbar(bool_entering = False)
                
        self.w.toolsCookieCutAction.setChecked(0) # Toggle cookie cutter icon
        
        self.close() 
            
        self.w.zoomToAreaAction.setEnabled(1) # Enable "Zoom to Area"
        self.w.setViewZoomtoSelectionAction.setEnabled(1) # Enable Zoom to Selection
        self.w.viewOrientationAction.setEnabled(1) #Enable Orientation Window
        
        # See note above in initGui() about these. Mark 2008-01-30.
        #self.w.panToolAction.setEnabled(1) # Enable "Pan Tool"
        #self.w.rotateToolAction.setEnabled(1) # Enable "Rotate Tool"
        
        # Enable these toolbars
        self.w.buildToolsToolBar.setEnabled(True)
        self.w.simulationToolBar.setEnabled(True)
        # Enable all those view options
        self.enableViewChanges(True)
            
        # Restore global display style label and combobox.
        # (see note above in initGui(). )
        #self.win.statusBar().dispbarLabel.setEnabled(False)
        #self.win.statusBar().globalDisplayStylesComboBox.setEnabled(False)
            
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
            
        self.rotateGridByAngleSpinBox.setEnabled(enableFlag)
        self.rotGridAntiClockwiseButton.setEnabled(enableFlag) 
        self.rotGridClockwiseButton.setEnabled(enableFlag)                
        self.w.enableViews(enableFlag) # Mark 051122.
            
    
    def changeSelectionShape(self, action):
        """Slot method that is called when user changes selection shape by GUI. """
        cookieCommand = self.cookieCommand
        if not cookieCommand.isCurrentCommand(): # [bruce 071008]
            return
        sShape = action.objectName()
        cookieCommand.changeSelectionShape(sShape)
        return

    def getSelectionShape(self):
        """Return the current selection shape that is checked. """
        selectionShape = self.cookieSelectionGroup.checkedAction().objectName()    
        return selectionShape
   
    def setThickness(self, value):
        self.cookieCommand.setThickness(value)
    
    def addLayer(self):
        self.addLayerButton.setEnabled(False)
        layerId = self.cookieCommand.addLayer()
            
        self.currentLayerComboBox.addItem(QString(str(layerId)))
        self.currentLayerComboBox.setCurrentIndex(layerId-1)
            
        self.w.glpane.gl_update()

    def changeLayer(self, value):
        """Change current layer to <value> layer """
        self.cookieCommand.change2Layer(value)

    def setFreeView(self, freeView):
        """Slot function to switch between free view/cookie selection states """
        self.cookieCommand.setFreeView(freeView)
        
    def toggleFullModel(self, showFullModel):
        """Slot function for the check box of 'Full Model' in cookie-cutter dashboard """
        self.cookieCommand.toggleFullModel(showFullModel)
        
    def showGridLine(self, show):
        """Slot function"""
        self.cookieCommand.showGridLine(show)
            
    def setGridSnap(self, snap):
        """Turn on/off the grid snap option """
        self.cookieCommand.gridSnap = snap
        pass
                
    def changeGridColor(self):
        """Open the stand color chooser dialog to change grid line color """
        c = QColorDialog.getColor(QColor(222,148,0), self)
        if c.isValid():
            self.gridColorLabel.setPaletteBackgroundColor(c)
            self.cookieCommand.setGridLineColor(c)

    def changeLatticeType(self, lType):
        self.cookieCommand.changeLatticeType(lType)
        if lType != 0: #Changes to other lattice type
            #Disable the snap to grid feature
            self.setGridSnap(False)
            self.snapGridCheckBox.setEnabled(False)
        else:
            self.snapGridCheckBox.setEnabled(True)
                
    def changeDispMode(self, display_style):
        self.cookieCommand.changeDispMode(display_style)
        
    def changeGridOrientation(self, value):
        if value == 0: self._orient100()
        elif value == 1: self._orient110()
        elif value == 2: self._orient111()
               
    def _rotView(self, direction):
        """Rotate the view anti-clockwise or clockWise. 
        If <direction> == True, anti-clockwise rotate, otherwise, 
        clockwise rotate"""
        from math import pi
        from geometry.VQT import Q, V
           
        angle = self.rotateGridByAngleSpinBox.value()
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
        self.cookieCommand.setOrientSurf(0)
        self.w.glpane.snapquat100()
    
    def _orient110(self):
        """halfway between two axes"""           
        self.cookieCommand.setOrientSurf(1)
        self.w.glpane.snapquat110()
    
    def _orient111(self):
        """equidistant from three axes """
        self.cookieCommand.setOrientSurf(2)
        self.w.glpane.snapquat111()
