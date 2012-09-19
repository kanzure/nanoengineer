# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
PM_PAM5_AtomChooser.py

@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  All rights reserved.
"""

from PM.PM_MolecularModelingKit import PM_MolecularModelingKit
from utilities.constants import diBALL
from utilities.GlobalPreferences import pref_MMKit_include_experimental_PAM_atoms

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

PAM5_ATOMS_BUTTON_LIST = [
    #bruce 080412 revised this
##    ( "QToolButton", 200, "Ax5", "", "PAM5-Axis",           None, 0, 0 ),
    ( "QToolButton", 208, "Gv5", "", "PAM5-Major-Groove",   None, 0, 0 ),
    ( "QToolButton", 201, "Ss5", "", "PAM5-Sugar",          None, 1, 0 ),
    ( "QToolButton", 202, "Pl5", "", "PAM5-Phosphate",      None, 2, 0 ),
##    ( "QToolButton", 203, "Sj5", "", "PAM5-Sugar-Junction", None, 1, 1 ),
##    ( "QToolButton", 204, "Ae5", "", "PAM5-Axis-End",       None, 1, 0 ),
##    ( "QToolButton", 205, "Pe5", "", "PAM5-Phosphate-End",  None, 1, 2 ),
##    ( "QToolButton", 206, "Sh5", "", "PAM5-Sugar-Hydroxyl", None, 2, 1 ),
##    ( "QToolButton", 207, "Hp5", "", "PAM5-Hairpin",        None, 2, 2 )
]

PAM5_ATOMS_BUTTON_LIST_EXPERIMENTAL = [
    #bruce 080412 added this
    ( "QToolButton", 210, "Ub5", "", "PAM5-Unpaired-base",   None, 0, 1 ),
    ( "QToolButton", 211, "Ux5", "", "PAM5-Unpaired-base-x", None, 1, 1 ),
    ( "QToolButton", 212, "Uy5", "", "PAM5-Unpaired-base-y", None, 2, 1 ),
]

if pref_MMKit_include_experimental_PAM_atoms():
    PAM5_ATOMS_BUTTON_LIST += PAM5_ATOMS_BUTTON_LIST_EXPERIMENTAL

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
    @see: U{B{PAM5}<http://www.nanoengineer-1.net/mediawiki/index.php?title=PAM5>}
    """
    viewerDisplay = diBALL

    def __init__(self,
                 parentWidget,
                 parentPropMgr   = None,
                 title           = "",
                 element         = "Ss5",
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


