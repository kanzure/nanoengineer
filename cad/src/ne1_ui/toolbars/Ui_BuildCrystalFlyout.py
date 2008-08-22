# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
This class provides the flyout toolbar for BuildCrystals command 

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-08-11: Created during command stack refactoring project

TODO:
"""
from ne1_ui.toolbars.Ui_AbstractFlyout import Ui_AbstractFlyout
from PyQt4.Qt import SIGNAL
from PyQt4 import QtGui
from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction
from utilities.icon_utilities import geticon
_superclass = Ui_AbstractFlyout
class BuildCrystalFlyout(Ui_AbstractFlyout):
    """
    This class provides the flyout toolbar for BuildCrystals command 
    """
    _subControlAreaActionList = []
    
    def _action_in_controlArea_to_show_this_flyout(self):
        """
        Required action in the 'Control Area' as a reference for this 
        flyout toolbar. See superclass method for documentation and todo note.
        """
        return self.win.toolsCookieCutAction
    
    def _getExitActionText(self):
        """
        Overrides superclass method. 
        @see: self._createActions()
        """
        return "Exit Crystal"
    
    def activateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides. 
        @see: Ui_AbstractFlyout.activateFlyoutToolbar()
        """    
        _superclass.activateFlyoutToolbar(self)
        self._setAutoShapeAcclKeys(True)
        
    def deActivateFlyoutToolbar(self):
        """
        Updates the flyout toolbar with the actions this class provides.
        @see: Ui_AbstractFlyout.deActivateFlyoutToolbar()
        """
        self._setAutoShapeAcclKeys(False)
        _superclass.deActivateFlyoutToolbar(self)
    
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
            
        _superclass.connect_or_disconnect_signals(self, 
                                                  isConnect)
        
        change_connect(self.cookieSelectionGroup, 
                       SIGNAL("triggered(QAction *)"),
                       self.parentWidget.changeSelectionShape)
        
    
    def _createActions(self, parentWidget):
        
        _superclass._createActions(self, parentWidget)
        
        self.cookieSelectionGroup = QtGui.QActionGroup(parentWidget)
        
        self._subControlAreaActionList.append(self.exitModeAction)
        separator = QtGui.QAction(parentWidget)
        separator.setSeparator(True)
        self._subControlAreaActionList.append(separator) 
        
        self.DefaultSelAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.DefaultSelAction.setObjectName("DEFAULT")
        self.DefaultSelAction.setText("Default")        
        self._subControlAreaActionList.append(self.DefaultSelAction)
        self.DefaultSelAction.setToolTip( "Default Selection (D)")
        self.DefaultSelAction.setWhatsThis(
        """<b>Default </b>
        <p>
       Defines the crystal shape as a polygon with the user specifying the 
       sides
        </p>""")
        
        self.CircleSelAction = NE1_QWidgetAction(parentWidget, win = self.win)    
        self.CircleSelAction.setObjectName("CIRCLE")
        self.CircleSelAction.setText("Circle")  
        self._subControlAreaActionList.append(self.CircleSelAction)
        self.CircleSelAction.setToolTip( "Circle (C)")
        self.CircleSelAction.setWhatsThis(
        """<b>Circle </b>
        <p>
        Draws the crystal geometry as a circle
        </p>""")
  
        self.RectCtrSelAction = NE1_QWidgetAction(parentWidget, win = self.win)   
        self.RectCtrSelAction.setObjectName("RECTANGLE")
        self.RectCtrSelAction.setText("RectCenter")
        self._subControlAreaActionList.append(self.RectCtrSelAction)
        self.RectCtrSelAction.setToolTip( "Rectangular Center (R)")
        self.RectCtrSelAction.setWhatsThis(
        """<b>Rectangle - Center Select</b>
        <p>
        Draws the crystal geometry as a rectangle with the cursor defining
        the center of the rectangle
        </p>""")
                
        self.HexagonSelAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.HexagonSelAction.setObjectName("HEXAGON")
        self.HexagonSelAction.setText("Hexagon")
        self._subControlAreaActionList.append(self.HexagonSelAction)
        self.HexagonSelAction.setToolTip( "Hexagon (H)")
        self.HexagonSelAction.setWhatsThis(
        """<b>Hexagon </b>
        <p>
        Draws the crystal geometry as a hexagon
        </p>""")
                
        self.TriangleSelAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.TriangleSelAction.setObjectName("TRIANGLE")
        self.TriangleSelAction.setText("Triangle")
        self._subControlAreaActionList.append(self.TriangleSelAction)
        self.TriangleSelAction.setToolTip( "Triangle (T)")
        self.TriangleSelAction.setWhatsThis(
        """<b>Triangle </b>
        <p>
        Draws the crystal geometry as a triangle
        </p>""")
                
                
        self.RectCornerSelAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.RectCornerSelAction.setObjectName("RECT_CORNER")
        self.RectCornerSelAction.setText("RectCorners")
        self._subControlAreaActionList.append(self.RectCornerSelAction)
        self.RectCornerSelAction.setToolTip( "Rectangular Corner (Shift+R)")
        self.RectCornerSelAction.setWhatsThis(
        """<b>Rectangle - Corner Select</b>
        <p>
        Draws the crystal geometry as a rectangle with the cursor defining 
        the initial corner 
        </p>""")
        
               
        self.LassoSelAction = NE1_QWidgetAction(parentWidget, win = self.win)     
        self.LassoSelAction.setObjectName("LASSO")
        self.LassoSelAction.setText("Lasso")
        self._subControlAreaActionList.append(self.LassoSelAction)
        self.LassoSelAction.setToolTip( "Lasso (L)")
        self.LassoSelAction.setWhatsThis(
        """<b>Lasso</b>
        <p>
        Can be used to draw irregular crystal geometries 
        </p>""")
        
        self.DiamondSelAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.DiamondSelAction.setObjectName("DIAMOND")
        self.DiamondSelAction.setText("Diamond")
        self._subControlAreaActionList.append(self.DiamondSelAction)
        self.DiamondSelAction.setToolTip( "Diamond (D)")
        self.DiamondSelAction.setWhatsThis(
        """<b>Diamond</b>
        <p>
        Draws the crystal geometry as a diamond
        </p>""")
        
        self.SquareSelAction = NE1_QWidgetAction(parentWidget, win = self.win)
        self.SquareSelAction.setObjectName("SQUARE")
        self.SquareSelAction.setText("Square")
        self._subControlAreaActionList.append(self.SquareSelAction)
        self.SquareSelAction.setToolTip( "Square(S)")
        self.SquareSelAction.setWhatsThis(
        """<b>Square</b>
        <p>
        Draws the crystal geometry as a square
        </p>""")
        
        for action in self._subControlAreaActionList[1:]:
            if isinstance(action, NE1_QWidgetAction):               
                action.setCheckable(True)
                self.cookieSelectionGroup.addAction(action)
                iconpath = "ui/actions/Toolbars/Smart/" + str(action.text()) + ".png"
                action.setIcon(geticon(iconpath))
        
        if not self.cookieSelectionGroup.checkedAction():
                self.DefaultSelAction.setChecked(True)
                
    
    def getFlyoutActionList(self):
        """
        Returns a tuple that contains mode spcific actionlists in the
        added in the flyout toolbar of the mode.
        CommandToolbar._createFlyoutToolBar method calls this
        @return: params: A tuple that contains 3 lists:
        (subControlAreaActionList, commandActionLists, allActionsList)
        """
        #'allActionsList' returns all actions in the flyout toolbar
        #including the subcontrolArea actions
        allActionsList = []

        #Action List for  subcontrol Area buttons.
        #In this mode, there is really no subcontrol area.
        #We will treat subcontrol area same as 'command area'
        #(subcontrol area buttons will have an empty list as their command area
        #list). We will set  the Comamnd Area palette background color to the
        #subcontrol area.        
       
        subControlAreaActionList =[]
        
        subControlAreaActionList.append(self.exitModeAction)
        subControlAreaActionList.extend(self._subControlAreaActionList)

        allActionsList.extend(subControlAreaActionList)

        #Empty actionlist for the 'Command Area'
        commandActionLists = []

        #Append empty 'lists' in 'commandActionLists equal to the
        #number of actions in subControlArea
        for i in range(len(subControlAreaActionList)):
            lst = []
            commandActionLists.append(lst)

        params = (subControlAreaActionList, commandActionLists, allActionsList)

        return params
    
    
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

    
    def getSelectionShape(self):
        """
        Return the current selection shape that is checked. 
        """
        selectionShape = self.cookieSelectionGroup.checkedAction().objectName()    
        return selectionShape
