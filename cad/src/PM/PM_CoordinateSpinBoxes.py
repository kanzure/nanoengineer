# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_CoordinateSpinBoxes.py

The PM_CoordinateSpinBoxes class provides a groupbox containing the three 
coordinate spinboxes. 
    
@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

@TODO: Need to implement connectWidgetWithState when that API is formalized.
"""

from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox

class PM_CoordinateSpinBoxes(PM_GroupBox):
    """
    The PM_CoordinateSpinBoxes class provides a groupbox containing the three 
    coordinate spinboxes. 
    @see: L{Ui_BuildAtomsPropertyManager._loadSelectedAtomPosGroupBox} for 
          an example. 
    """
    def __init__(self, 
                 parentWidget,
                 title = "Coordinates:"
                 ):
        """
        Appends a PM_CoordinateSpinBoxes groupbox widget to I{parentWidget},
        a L{PM_Groupbox} or a L{PM_Dialog}
                
        @param parentWidget: The parent groupbox or dialog (Property manager) 
                             containing this  widget.
        @type  parentWidget: L{PM_GroupBox} or L{PM_Dialog} 
        
        @param title: The title (button) text.
        @type  title: str        
        """
        PM_GroupBox.__init__(self, parentWidget)
        self._loadCoordinateSpinBoxes()
    
    def _loadCoordinateSpinBoxes(self):
        """
        Load the coordinateSpinboxes groupbox with the x, y, z spinboxes
        """
         # User input to specify x-coordinate 
        self.xSpinBox  =  \
            PM_DoubleSpinBox( self,
                              label         =  \
                              "ui/actions/Properties Manager/X_Coordinate.png",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  - 9999999,
                              maximum       =  9999999,
                              singleStep    =  1,
                              decimals      =  3,
                              suffix        =  " A")
        

        # User input to specify y-coordinate
        self.ySpinBox  =  \
            PM_DoubleSpinBox( self,
                              label         =  \
                              "ui/actions/Properties Manager/Y_Coordinate.png",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  - 9999999,
                              maximum       =  9999999,
                              singleStep    =  1,
                              decimals      =  3,
                              suffix        =  " A")

        # User input to specify z-coordinate 
        self.zSpinBox  =  \
            PM_DoubleSpinBox( self,
                              label         =  \
                              "ui/actions/Properties Manager/Z_Coordinate.png",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  - 9999999,
                              maximum       =  9999999,
                              singleStep    =  1,
                              decimals      =  3,
                              suffix        =  " A")
    
    def _getStyleSheet(self):
        """
        Return the style sheet for the groupbox. This sets the following 
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)
        For PM_CoordinateSpinBoxes groupbox, we typically don't want the border
        around the groupbox. If client needs a border, it should be explicitly
        defined and set there. 
        @see: L{PM_GroupBox._getStyleSheet} (overrided here)
        """
        
        styleSheet = "QGroupBox {border-style:hidden;\
        border-width: 0px;\
        border-color: "";\
        border-radius: 0px;\
        min-width: 10em; }" 
   
        return styleSheet
         
    
    