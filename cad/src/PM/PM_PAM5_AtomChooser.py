# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_PAM5_AtomChooser.py

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  All rights reserved.

"""


from PM.PM_MolecularModelingKit import PM_MolecularModelingKit
from constants import diBALL

# Elements button list to create PAM5 atoms toolbutton group.
# Format: 
# - button type
# - buttonId (element number), 
# - buttonText (element symbol), 
# - iconPath
# - tooltip (element name)
# - shortcut
# - column
# - row

PAM5_ATOMS_BUTTON_LIST = [ \
    ( "QToolButton", 200, "Ax5", "", "PAM5-Axis",           None, 0, 0 ),
    ( "QToolButton", 201, "Ss5", "", "PAM5-Sugar",          None, 0, 1 ),
    ( "QToolButton", 202, "Pl5", "", "PAM5-Phosphate",      None, 0, 2 ),
    ( "QToolButton", 203, "Sj5", "", "PAM5-Sugar-Junction", None, 1, 1 ),
    ( "QToolButton", 204, "Ae5", "", "PAM5-Axis-End",       None, 1, 0 ),
    ( "QToolButton", 205, "Pe5", "", "PAM5-Phosphate-End",  None, 1, 2 ),
    ( "QToolButton", 206, "Sh5", "", "PAM5-Sugar-Hydroxyl", None, 2, 1 ),
    ( "QToolButton", 207, "Hp5", "", "PAM5-Hairpin",        None, 2, 2 )  
]

class PM_PAM5_AtomChooser( PM_MolecularModelingKit ):
    """
    The PM_PAM5_AtomChooser widget provides a PAM5 Atom Chooser,
    PAM5 stands for "Five Pseudo Atom Model "
    contained in its own group box, for a Property Manager dialog (or 
    as a sub groupbox for Atom Chooser GroupBox.)
    
    A PM_PAM5_AtomChooser is a selection widget that displays all PAM5 atoms 
    supported in NE1
        
    @see: B{elements.py}
    @see: B{L{PM_MolecularModelingKit}}
    @see: U{B{PAM-5}<http://www.nanoengineer-1.net/mediawiki/index.php?title=PAM-5>}
    """
    viewerDisplay = diBALL
        
    def __init__(self, 
                 parentWidget,
                 parentPropMgr   = None,
                 title           = "",
                 element         = "Ax5",
                 elementViewer   =  None
                 ):
        """
        Appends a PM_PAM5_AtomChooser widget to the bottom of I{parentWidget}, 
        a Property Manager dialog. (or as a sub groupbox for Atom Chooser 
        GroupBox.)
        
        @param parentWidget: The parent PM_Dialog or PM_groupBox containing this
                             widget.
        @type  parentWidget: PM_Dialog or PM_GroupBox
        
        @param parentPropMgr: The parent Property Manager 
        @type  parentPropMgr: PM_Dialog or None
        
        @param title: The button title on the group box containing the
                      Atom Chooser.
        @type  title: str
        
        @param element: The initially selected PAM5 atom. It can be either an
                        PAM5 atom symbol or name.
        @type  element: str
        """
        
        PM_MolecularModelingKit.__init__( self, 
                                          parentWidget,
                                          parentPropMgr,
                                          title,
                                          element,
                                          elementViewer)
        
        self._elementsButtonGroup.setButtonSize(width = 38, height = 38)

    def _addGroupBoxes(self):
        """
        various groupboxes present inside the PAM5 Atom chooser groupbox.
        """
        self._addElementsGroupBox(self)
        
    def getElementsButtonList(self):
        """
        Return the list of buttons in the PAM5 Atom chooser.
        @return: List containing information about the PAM5 atom toolbuttons
        @rtype:  list
        """
        return PAM5_ATOMS_BUTTON_LIST
 
        