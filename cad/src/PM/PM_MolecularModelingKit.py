# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
PM_MolecularModelingKit.py - Atom Chooser widget

@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  All rights reserved.

"""

from model.elements import PeriodicTable

from PyQt4.Qt import SIGNAL
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ToolButtonGrid import PM_ToolButtonGrid
from utilities.constants import diTUBES
from utilities.debug import print_compact_traceback

from utilities.exception_classes import AbstractMethod


class PM_MolecularModelingKit( PM_GroupBox ):
    """
    The PM_MolecularModelingKit widget provides an Atom Chooser widget,
    contained in its own group box, for a Property Manager dialog. (see
    subclasses for details)

    A PM_MolecularModelingKit is a selection widget that displays all elements,
    pseudo-atoms supported in NE1.

    @cvar element: The current element.
    @type element: Elem

    @cvar atomType: The current atom type of the current element.
    @type atomType: str

    @see: B{elements.py}
    @see: B{PM.PM_ElementChooser}
    """

    element        = None
    atomType       = ""
    _periodicTable = PeriodicTable
    viewerDisplay = diTUBES

    def __init__(self,
                 parentWidget,
                 parentPropMgr   = None,
                 title           = "Molecular Modeling Kit",
                 element         = "",
                 elementViewer   =  None,
                 ):
        """
        Appends a AtomChooser widget (see subclasses) to the bottom of
        I{parentWidget}, a Property Manager dialog.
        (or as a sub groupbox for Atom Chooser  GroupBox.)

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

        PM_GroupBox.__init__(self, parentWidget, title)

        self.element = self._periodicTable.getElement(element)
        self.elementViewer = elementViewer
        self.updateElementViewer()

        if parentPropMgr:
            self.parentPropMgr = parentPropMgr
        else:
            self.parentPropMgr = parentWidget

        self._addGroupBoxes()
        self.connect_or_disconnect_signals(True)

    def _addGroupBoxes(self):
        """
        Subclasses should add various groupboxes present inside the Atom chooser
        groupbox.

        AbstractMethod
        """
        raise AbstractMethod()

    def _addElementsGroupBox(self, inPmGroupBox):
        """
        Creates a grid of tool buttons containing all elements supported
        in NE1.

        @param inPmGroupBox: The parent group box to contain the element
                             buttons.
        @type  inPmGroupBox: PM_GroupBox
        """

        self._elementsButtonGroup = \
            PM_ToolButtonGrid( inPmGroupBox,
                               title        = "",
                               buttonList   = self.getElementsButtonList(),
                               checkedId    = self.element.eltnum,
                               setAsDefault = True
                               )

        self.connect( self._elementsButtonGroup.buttonGroup,
                      SIGNAL("buttonClicked(int)"),
                      self.setElement )


    def _updateAtomTypesButtons(self):
        """
        Updates the hybrid buttons based on the currently selected
        element button.
        Subclasses should override this method
        """
        pass


    def restoreDefault(self):
        """
        Restores the default checked (selected) element and atom type buttons.
        """
        PM_GroupBox.restoreDefault(self)
        self._updateAtomTypesButtons()
        return

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
        Set the current element in the MMKit to I{elementNumber}.

        @param elementNumber: Element number. (i.e. 6 = carbon)
        @type  elementNumber: int
        """
        self.element = self._periodicTable.getElement(elementNumber)
        self._updateAtomTypesButtons()
        self.updateElementViewer()
        self._updateParentPropMgr()
        return

    def updateElementViewer(self):
        """
        Update the view in the element viewer (if present)
        """
        if not self.elementViewer:
            return

        from graphics.widgets.ThumbView import MMKitView
        assert isinstance(self.elementViewer, MMKitView)
        self.elementViewer.resetView()
        self.elementViewer.changeHybridType(self.atomType)
        self.elementViewer.refreshDisplay(self.element, self.viewerDisplay)
        return

    def _updateParentPropMgr(self):
        """
        Update things in the parentWidget if necessary.
        (The parentWidget should be a property manager, although not necessary)
        Example: In Build Atoms Mode, the Property manager message groupbox
        needs to be updated if the element is changed in the element chooser.
        Similarly, the selection filter list should be updated in this mode.
        """

        parentPropMgrClass = self.parentPropMgr.__class__

        if hasattr(parentPropMgrClass, 'updateMessage'):
            try:
                self.parentPropMgr.updateMessage()
            except AttributeError:
                print_compact_traceback("Error calling updateMessage()")

        if hasattr(parentPropMgrClass, 'update_selection_filter_list'):
            try:
                self.parentPropMgr.update_selection_filter_list()
            except AttributeError:
                msg = "Error calling update_selection_filter_list()"
                print_compact_traceback(msg)


    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot
                          method.
        @type  isConnect: boolean
        """
        #Not implemented yet
        return

    def getElementsButtonList(self):
        """
        Subclasses should override this and return the list of buttons in the
        Atom chooser.
        """
        raise AbstractMethod()
