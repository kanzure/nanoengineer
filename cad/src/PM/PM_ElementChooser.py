# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_ElementChooser.py

@author: Mark Sims
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-08-03: Created.
"""

from PM.PM_MolecularModelingKit import PM_MolecularModelingKit

from PyQt4.Qt import SIGNAL, QSpacerItem, QSizePolicy
from PM.PM_ToolButtonGrid import PM_ToolButtonGrid

# Elements button list to create elements tool button group.
# Format: 
# - button type
# - buttonId (element number), 
# - buttonText (element symbol), 
# - iconPath
# - tooltip (element name)
# - shortcut
# - column
# - row

ELEMENTS_BUTTON_LIST = [ \
    ( "QToolButton", 1,  "H", "", "Hydrogen (H)",  "H", 4, 0   ),
    ( "QToolButton", 2, "He", "", "Helium",  None,  5, 0   ),
    ( "QToolButton", 5,  "B", "", "Boron (B)",   "B",   0, 1   ),
    ( "QToolButton", 6,  "C", "", "Carbon (C)",  "C",   1, 1   ),
    ( "QToolButton", 7,  "N", "", "Nitrogen (N)", "N",  2, 1   ),
    ( "QToolButton", 8,  "O", "", "Oxygen (O)",  "O",   3, 1   ),
    ( "QToolButton", 9,  "F", "", "Fluorine (F)",  "F", 4, 1   ),
    ( "QToolButton", 10, "Ne", "", "Neon",  None,   5, 1   ),
    ( "QToolButton", 13, "Al", "", "Aluminum (A)", "A", 0, 2   ),
    ( "QToolButton", 14, "Si", "", "Silicon (Q)",  "Q",  1, 2   ),
    ( "QToolButton", 15,  "P", "", "Phosphorus (P)", "P", 2, 2   ),
    ( "QToolButton", 16,  "S", "", "Sulfur (S)",  "S",   3, 2   ),
    ( "QToolButton", 17, "Cl", "", "Chlorine (L)", "L",  4, 2   ),
    ( "QToolButton", 18, "Ar", "", "Argon",   None,  5, 2   ),
    ( "QToolButton", 32, "Ge", "", "Germanium", "G",  1, 3   ),
    ( "QToolButton", 33, "As", "", "Arsenic",  None,   2, 3   ),
    ( "QToolButton", 34, "Se", "", "Selenium", None,  3, 3   ),
    ( "QToolButton", 35, "Br", "", "Bromine" , None,   4, 3   ),
    ( "QToolButton", 36, "Kr", "", "Krypton",  None,  5, 3   )
]

ELEMENT_ATOM_TYPES = { \
    6: ("sp3", "sp2", "sp"                  ), 
    7: ("sp3", "sp2", "sp", "sp2(graphitic)"),
    8: ("sp3", "sp2", "sp2(-)", "sp2(-.5)"  ),
   15: ("sp3", "sp3(p)"             ),
   16: ("sp3", "sp2"                        )
}

ATOM_TYPES = ("sp3", "sp2", "sp", "sp2(graphitic)", "sp3(p)", "sp2(-)", "sp2(-.5)")
            
# Atom types (hybrids) button list to create atom types tool button group.
# Format: 
# - buttonId (hybrid number)
# - buttonText (hybrid symbol)
# - iconPath
# - tooltip (full hybrid name)
# - shortcut
# - column
# - row

ATOM_TYPES_BUTTON_LIST = [ \
    ( "QToolButton", 0, "sp3", "", "sp3", None, 0, 0 ),
    ( "QToolButton", 1, "sp2", "", "sp2", None, 1, 0 ),
    ( "QToolButton", 2, "sp",  "", "sp",  None, 2, 0 ),
    ( "QToolButton", 3, "sp2(graphitic)", "ui/modeltree/N_graphitic.png", 
      "Graphitic", None, 3, 0 ), #@ Icon lives in a poorly chosen location.
    ( "QToolButton", 4, "sp3(p)",  "", "sp3(phosphate)",  None, 4, 0 ),
    ( "QToolButton", 5, "sp2(-)",  "", "sp2(-)",  None, 5, 0 ),
    ( "QToolButton", 6, "sp2(-.5)",  "", "sp2(-.5)",  None, 6, 0 ),
]

# How to add a new hybridization of an element to the UI:

# First, create the hybridization in model/elements_data.py.  See the
# comments there for how to do this.

# Next, add the hybridization to ELEMENT_ATOM_TYPES above.  The
# indices are the element numbers in the ELEMENTS_BUTTON_LIST.

# Next, make sure the hybridization appears in the ATOM_TYPES list and
# the ATOM_TYPES_BUTTON_LIST.  There are two indices that should
# increment by one for each line.  You may wish to add an icon graphic
# if the string does not fit entirely within the button.

class PM_ElementChooser( PM_MolecularModelingKit ):
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
    
    def __init__(self, 
                 parentWidget, 
                 parentPropMgr   = None,
                 title           = "",
                 element         = "Carbon",
                 elementViewer   =  None
                 ):
        """
        Appends a PM_ElementChooser widget to the bottom of I{parentWidget}, 
        a Property Manager dialog. (or as a sub groupbox for Atom Chooser 
        GroupBox.)
        
        @param parentWidget: The parent PM_Dialog or PM_groupBox containing this
                             widget.
        @type  parentWidget: PM_Dialog or PM_GroupBox
        
        @param parentPropMgr: The parent Property Manager 
        @type  parentPropMgr: PM_Dialog or None
        
        @param title: The button title on the group box containing the
                      Element Chooser.
        @type  title: str
        
        @param element: The initially selected element. It can be either an
                        element symbol or name.
        @type  element: str
        """
        
        PM_MolecularModelingKit.__init__( self, 
                                          parentWidget, 
                                          parentPropMgr,
                                          title,
                                          element,
                                          elementViewer)
        
           
    def _addGroupBoxes(self):
        """
        Add various groupboxes present inside the ElementChooser groupbox
        """
        self._addElementsGroupBox(self)
        self._addAtomTypesGroupBox(self)

    def _addAtomTypesGroupBox(self, inPmGroupBox):
        """
        Creates a row of atom type buttons (i.e. sp3, sp2, sp and graphitic).
        
        @param inPmGroupBox: The parent group box to contain the atom type 
                             buttons.
        @type  inPmGroupBox: PM_GroupBox
        """
        self._atomTypesButtonGroup = \
            PM_ToolButtonGrid( inPmGroupBox, 
                               buttonList = self.getAtomTypesButtonList(),
                               label      = "Atomic hybrids:",
                               checkedId  = 0,
                               setAsDefault = True )
        #Increase the button width for atom hybrids so that 
        # button texts such as sp3(p), sp2(-), sp2(-.5) fit. 
        # This change can be removed once we have icons 
        # for the buttons with long text -- Ninad 2008-09-04
        self._atomTypesButtonGroup.setButtonSize(width = 44)
        
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
        self.updateElementViewer()
    
    def getElementsButtonList(self):
        """
        Return the list of buttons in the Element chooser.
        @return: List containing information about the element tool buttons
        @rtype:  list
        """
        return ELEMENTS_BUTTON_LIST
    
    def getAtomTypesButtonList(self):
        """
        Return the list of buttons for the various atom types (hybrids) of the 
        selected atom in the    Element  chooser.
        @return: List containing information about the toolbuttons for 
                 the atom types (hybrids) of the selected atom  in the element
                 chooser.
        @rtype:  list 
        
        """
        return ATOM_TYPES_BUTTON_LIST        
