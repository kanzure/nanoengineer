# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_ElementChooser.py

@author: Mark Sims
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-08-03: Created.
"""

from elements import PeriodicTable

from PyQt4.Qt import SIGNAL, QSpacerItem, QSizePolicy
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ToolButtonGrid import PM_ToolButtonGrid
from constants import diTUBES

# Elements button list to create elements tool button group.
# Format: 
# - buttonId (element number), 
# - buttonText (element symbol), 
# - iconPath
# - tooltip (element name)
# - column
# - row

ELEMENTS_BUTTON_LIST = [ \
    ( "QToolButton", 1,  "H", "", "Hydrogen",   4, 0   ),
    ( "QToolButton", 2, "He", "", "Helium",     5, 0   ),
    ( "QToolButton", 5,  "B", "", "Boron",      0, 1   ),
    ( "QToolButton", 6,  "C", "", "Carbon",     1, 1   ),
    ( "QToolButton", 7,  "N", "", "Nitrogen",   2, 1   ),
    ( "QToolButton", 8,  "O", "", "Oxygen",     3, 1   ),
    ( "QToolButton", 9,  "F", "", "Fluorine",   4, 1   ),
    ( "QToolButton", 10, "Ne", "", "Neon",       5, 1   ),
    ( "QToolButton", 13, "Al", "", "Aluminum",   0, 2   ),
    ( "QToolButton", 14, "Si", "", "Silicon",    1, 2   ),
    ( "QToolButton", 15,  "P", "", "Phosphorus", 2, 2   ),
    ( "QToolButton", 16,  "S", "", "Sulfur",     3, 2   ),
    ( "QToolButton", 17, "Cl", "", "Chlorine",   4, 2   ),
    ( "QToolButton", 18, "Ar", "", "Argon",      5, 2   ),
    ( "QToolButton", 32, "Ge", "", "Germanium",  1, 3   ),
    ( "QToolButton", 33, "As", "", "Arsenic",    2, 3   ),
    ( "QToolButton", 34, "Se", "", "Selenium",   3, 3   ),
    ( "QToolButton", 35, "Br", "", "Bromine" ,   4, 3   ),
    ( "QToolButton", 36, "Kr", "", "Krypton",    5, 3   )
]

ELEMENT_ATOM_TYPES = { \
    6: ("sp3", "sp2", "sp"                  ), 
    7: ("sp3", "sp2", "sp", "sp2(graphitic)"),
    8: ("sp3", "sp2"                        ),
   16: ("sp3", "sp2"                        )
}

ATOM_TYPES = ("sp3", "sp2", "sp", "sp2(graphitic)")
            
# Atom types (hybrids) button list to create atom types tool button group.
# Format: 
# - buttonId (hybrid number)
# - buttonText (hybrid symbol)
# - iconPath
# - tooltip (full hybrid name)
# - column
# - row

ATOM_TYPES_BUTTON_LIST = [ \
    ( "QToolButton", 0, "sp3", "", "sp3", 0, 0 ),
    ( "QToolButton", 1, "sp2", "", "sp2", 1, 0 ),
    ( "QToolButton", 2, "sp",  "", "sp",  2, 0 ),
    ( "QToolButton", 3, "sp2(graphitic)", "ui/modeltree/N_graphitic.png", 
      "Graphitic", 3, 0 ) #@ Icon lives in a poorly chosen location.
]

class PM_ElementChooser( PM_GroupBox ):
    """
    The PM_ElementChooser widget provides an Element Chooser widget,
    contained in its own group box, for a Property Manager dialog.
    
    A PM_ElementChooser is a selection widget that displays all elements, 
    including their atom types (atomic hybrids), supported in NE1. Methods
    are provided to set and get the selected element and atom type
    (e.g., L{setElement()}, L{getElement()}, L{getElementNumber()} and
    L{getElementSymbolAndAtomType()}).
    
    @cvar element: The current element.
    @type element: Elem
    
    @cvar atomType: The current atom type of the current element.
    @type atomType: str
    
    @see: B{elements.py}
    """
    
    element        = None
    atomType       = ""
    _periodicTable = PeriodicTable
    
    def __init__(self, 
                 parentWidget, 
                 title           = "Element Chooser",
                 element         = "Carbon",
                 elementViewer   =  None
                 ):
        """
        Appends a PM_ElementChooser widget to the bottom of I{parentWidget}, 
        a Property Manager dialog.
        
        @param parentWidget: The parent PM dialog containing this widget.
        @type  parentWidget: PM_Dialog
        
        @param title: The button title on the group box containing the
                      Element Chooser.
        @type  title: str
        
        @param element: The initially selected element. It can be either an
                        element symbol or name.
        @type  element: str
        """
        
        PM_GroupBox.__init__(self, parentWidget, title)
        
        self.element = self._periodicTable.getElement(element)
        self.elementViewer = elementViewer
        self._updateElementViewer()
        self._addElementsGroupBox(self)
        self._addAtomTypesGroupBox(self)
        self.connect_disconnect_signals(True)
        
    def _addElementsGroupBox(self, inPmGroupBox):
        """
        Creates a grid of tool buttons containing all elements supported
        in NE1.
        
        @param inPmGroupBox: The parent group box to contain the element buttons.
        @type  inPmGroupBox: PM_GroupBox
        """
        
        self._elementsButtonGroup = \
            PM_ToolButtonGrid( inPmGroupBox, 
                               title        = "",
                               buttonList   = ELEMENTS_BUTTON_LIST,
                               checkedId    = self.element.eltnum,
                               setAsDefault = True
                               )
        
        self.connect( self._elementsButtonGroup.buttonGroup, 
                      SIGNAL("buttonClicked(int)"), 
                      self.setElement )
        
    def _addAtomTypesGroupBox(self, inPmGroupBox):
        """
        Creates a row of atom type buttons (i.e. sp3, sp2, sp and graphitic).
        
        @param inPmGroupBox: The parent group box to contain the atom type buttons.
        @type  inPmGroupBox: PM_GroupBox
        """
        self._atomTypesButtonGroup = \
            PM_ToolButtonGrid( inPmGroupBox, 
                               buttonList = ATOM_TYPES_BUTTON_LIST,
                               label      = "Atomic hybrids:",
                               checkedId  = 0,
                               setAsDefault = True )
        
        # Horizontal spacer to keep buttons grouped close together.
        _hSpacer = QSpacerItem( 1, 32, 
                                QSizePolicy.Expanding, 
                                QSizePolicy.Fixed )
        
        self._atomTypesButtonGroup.gridLayout.addItem( _hSpacer, 0, 4, 1, 1 )
        
        self.connect( self._atomTypesButtonGroup.buttonGroup, 
                      SIGNAL("buttonClicked(int)"), 
                      self._setAtomType )
        
        self._updateAtomTypesButtons()
        
    def _updateAtomTypesButtons(self):
        """
        Updates the hybrid buttons based on the currently selected 
        element button.
        """
        currentElementNumber = self.getElementNumber()
        
        if ELEMENT_ATOM_TYPES.has_key(currentElementNumber):
            elementAtomTypes = ELEMENT_ATOM_TYPES[currentElementNumber]
        else:
            # Selected element has no hybrids.
            elementAtomTypes = []
            self.atomType = ""
            
        for atomType in ATOM_TYPES:
            button = self._atomTypesButtonGroup.getButtonByText(atomType)
            if atomType in elementAtomTypes:
                button.show()
                if atomType == elementAtomTypes[0]:
                    # Select the first atomType button.
                    button.setChecked(True)
                    self.atomType = atomType                    
            else:
                button.hide()
                
        self._updateAtomTypesTitle()
                
    def _updateAtomTypesTitle(self):
        """
        Updates the title for the Atom Types group box.
        """
        title = "Atomic Hybrids for " + self.element.name + ":"
        self._atomTypesButtonGroup.setTitle(title)
                
    def restoreDefault(self):
        """
        Restores the default checked (selected) element and atom type buttons.
        """
        PM_GroupBox.restoreDefault(self)
        self._updateAtomTypesButtons()
        
    def getElementNumber(self):
        """
        Returns the element number of the currently selected element.
        
        @return: Selected element number
        @rtype:  int
        """
        return self._elementsButtonGroup.checkedId()
    
    def getElementSymbolAndAtomType(self):
        """
        Returns the symbol and atom type of the currently selected element.
        
        @return: element symbol, atom type
        @rtype:  str, str
        """
        currentElementNumber = self.getElementNumber()
        element = self._periodicTable.getElement(currentElementNumber)
        return element.symbol, self.atomType
    
    def getElement(self):
        """
        Get the current element.
        
        @return: element
        @rtype:  Elem
        
        @see: B{element.py}
        """
        return self.element
        
    def setElement(self, elementNumber):
        """
        Set the selected element to I{elementNumber}.
        
        @param elementNumber: Element number.
        @type  elementNumber: int
        """
        self.element = self._periodicTable.getElement(elementNumber)
        self._updateAtomTypesButtons()
        self._updateElementViewer()
        
    def _setAtomType(self, atomTypeIndex):
        """
        Set the current atom type.
        
        @param atomTypeIndex: The atom type index, where:
                              0 = sp3,
                              1 = sp2,
                              2 = sp,
                              3 = sp2(graphitic)
        @type  atomTypeIndex: int
        
        @note: Calling this method does not update the atom type buttons.
        """
        self.atomType = ATOM_TYPES[atomTypeIndex]
        self._updateElementViewer()
    
    def _updateElementViewer(self):
        if not self.elementViewer:
            return
        
        from ThumbView import MMKitView
        assert isinstance(self.elementViewer, MMKitView)       
        self.elementViewer.resetView()                
        self.elementViewer.changeHybridType(self.atomType)        
        self.elementViewer.refreshDisplay(self.element, diTUBES)
    
    def connect_disconnect_signals(self, connect):
        """
        """
        if connect:
            change_connect = self.connect
        else:
            change_connect = self.disconnect
        
        
            
        