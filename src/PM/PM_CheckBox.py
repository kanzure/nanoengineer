# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_CheckBox.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrCheckBox out of PropMgrBaseClass.py into this file
                 and renamed it PM_CheckBox.
"""

from PyQt4.Qt import Qt
from PyQt4.Qt import QCheckBox

from PM_WidgetMixin import PM_WidgetMixin

class PM_CheckBox( QCheckBox, PM_WidgetMixin ):
    """
    The PM_CheckBox widget provides a QCheckBox with a 
    QLabel for a Property Manager groupbox.
    """
    
    defaultState = Qt.Unchecked  # Default state of CheckBox. Qt.Checked is checked.
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  isChecked    = False, 
                  setAsDefault = True,
                  spanWidth    = False):
        """
        Appends a QCheckBox widget to <parentWidget>, a property manager groupbox.
        
        Arguments:
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: the label of this widget.
        @type  label: str
        
        @param isChecked: can be True, False, or one of the Qt ToggleStates
                      True  = checked
                      False = unchecked
        @type  isChecked: bool
        
        @param setAsDefault: if True, will restore <val>
                         when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool
        """
        
        if 0: # Debugging code
            print "PropMgrCheckBox.__init__():"
            print "  label=", label
            print "  state =", state
            print "  setAsDefault =", setAsDefaultfix
            print "  spanWidth =", spanWidth
                
        QCheckBox.__init__(self)
        
        self.parentWidget = parentWidget
   
        self.setCheckState(isChecked, setAsDefault)
        # We use this widget's QLabel to display the label, not the QCheckBox label.
        # So we premanently "remove" the checkbox text.
        self.setText("") 
        self.addWidgetAndLabelToParent(parentWidget, label, spanWidth)
        
    def setCheckState( self, state, setAsDefault = True ):
        """
        Sets the check box's check state to state.
        
        @param state: the check box's check state, where:
            True = checked
            False = unchecked
        @type  state: bool, Qt.ToggleStates
        
        @param setAsDefault: if True, will restore <state> as the current state
                         when the "Restore Defaults" button is clicked.
        @type  setAsDefault: bool (default True)
        """
        
        # Set <state> to the appropriate Qt.ToggleState if True or False.
        if state is True:  state = Qt.Checked
        if state is False: state = Qt.Unchecked
            
        if setAsDefault:
            self.setAsDefault=setAsDefault
            self.defaultState=state
        
        QCheckBox.setCheckState(self, state)
        
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setCheckState(self.defaultState)

# End of PropMgrCheckBox ############################