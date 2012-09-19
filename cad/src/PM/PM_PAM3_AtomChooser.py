# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
PM_PAM3_AtomChooser.py

@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  All rights reserved.
"""

from PM.PM_MolecularModelingKit import PM_MolecularModelingKit
from utilities.constants import diBALL
from utilities.GlobalPreferences import pref_MMKit_include_experimental_PAM_atoms

# Elements button list to create PAM3 atoms toolbutton group.
# Format:
# - button type
# - buttonId (element number),
# - buttonText (element symbol),
# - iconPath
# - tooltip (element name)
# - shortcut
# - column
# - row

PAM3_ATOMS_BUTTON_LIST = [
    #bruce 080412 revised this
    ( "QToolButton", 300, "Ax3", "", "PAM3-Axis",           None, 0, 0 ),
    ( "QToolButton", 301, "Ss3", "", "PAM3-Sugar",          None, 1, 0 ),
##    ( "QToolButton", 303, "Sj3", "", "PAM3-Sugar-Junction", None, 1, 1 ),
##    ( "QToolButton", 304, "Ae3", "", "PAM3-Axis-End",       None, 1, 0 ),
##    ( "QToolButton", 306, "Sh3", "", "PAM3-Sugar-Hydroxyl", None, 2, 1 ),
##    ( "QToolButton", 307, "Hp3", "", "PAM3-Hairpin",        None, 0, 2 )

    #NOTE: Following atoms are not used for now
    #( "QToolButton", 302, "Pl3", "", "PAM3-Phosphate",      None, 0, 2 ),
    #( "QToolButton", 305, "Se3", "", "PAM3-Sugar-End",      None, 1, 2 ),
]

PAM3_ATOMS_BUTTON_LIST_EXPERIMENTAL = [
    #bruce 080412 added this
    ( "QToolButton", 310, "Ub3", "", "PAM3-Unpaired-base",   None, 0, 1 ),
    ( "QToolButton", 311, "Ux3", "", "PAM3-Unpaired-base-x", None, 1, 1 ),
    ( "QToolButton", 312, "Uy3", "", "PAM3-Unpaired-base-y", None, 2, 1 ),
]

if pref_MMKit_include_experimental_PAM_atoms():
    PAM3_ATOMS_BUTTON_LIST += PAM3_ATOMS_BUTTON_LIST_EXPERIMENTAL


class PM_PAM3_AtomChooser( PM_MolecularModelingKit ):
    """
    The PM_PAM3_AtomChooser widget provides a PAM3 Atom Chooser,
    PAM3 stands for "Three Pseudo Atom Model "
    contained in its own group box, for a Property Manager dialog (or
    as a sub groupbox for Atom Chooser GroupBox.)

    A PM_PAM3_AtomChooser is a selection widget that displays all PAM3 atoms
    supported in NE1.

    @see: B{elements.py}
    @see: B{L{PM_MolecularModelingKit}}
    """

    viewerDisplay = diBALL

    def __init__(self,
                 parentWidget,
                 parentPropMgr   = None,
                 title           = "",
                 element         = "Ss3",
                 elementViewer   =  None
                 ):
        """
        Appends a PM_PAM3_AtomChooser widget to the bottom of I{parentWidget},
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

        @param element: The initially selected PAM3 atom. It can be either an
                        (PAM3) atom symbol or name.
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
        various groupboxes present inside the PAM3 Atom chooser groupbox.
        """
        self._addElementsGroupBox(self)


    def getElementsButtonList(self):
        """
        Return the list of buttons in the PAM3 Atom chooser.
        @return: List containing information about the PAM3 atom toolbuttons
        @rtype:  list
        """
        return PAM3_ATOMS_BUTTON_LIST
