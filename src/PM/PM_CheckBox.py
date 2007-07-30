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
from PyQt4.Qt import QLabel
from PyQt4.Qt import QWidget

from PM_Constants import pmLeftColumn, pmRightColumn

class PM_CheckBox( QCheckBox ):
    """
    The PM_CheckBox widget provides a QCheckBox with a 
    QLabel for a Property Manager group box.
    
    @cvar defaultState: The default state of the checkbox.
    @type defaultState: U{B{Qt.CheckState}<http://doc.trolltech.com/4/
                          qt.html#CheckState-enum>}
    
    @cvar setAsDefault: Determines whether to reset the state of the
                        checkbox to I{defaultState} when the user clicks
                        the "Restore Defaults" button.
    @type setAsDefault: bool
    
    @cvar hidden: Hide flag.
    @type hidden: bool
    
    @cvar labelWidget: The Qt label widget of this checkbox.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """
    
    defaultState = Qt.Unchecked  
    setAsDefault = True
    hidden       = False
    labelWidget  = None
    
    def __init__( self, 
                  parentWidget, 
                  label        = '', 
                  labelColumn  = 0,
                  state        = Qt.Unchecked, 
                  setAsDefault = True,
                  spanWidth    = False):
        """
        Appends a QCheckBox (Qt) widget to the bottom of I{parentWidget}, 
        a Property Manager group box.
        
        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: The label that appears to the left or right of the 
                      checkbox. 
                      
                      If spanWidth is True, the label will be displayed on
                      its own row directly above the checkbox.
                      
                      To suppress the label, set I{label} to an 
                      empty string.
        @type  label: str
        
        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left 
                            column) and 1 (right column). The default is 0 
                            (left column).
        @type  labelColumn: int
        
        @param state: Set's the check box's check state. The default is
                      Qt.Unchecked (unchecked).
        @type  state: U{B{Qt.CheckState}<http://doc.trolltech.com/4/
                          qt.html#CheckState-enum>}
        
        @param setAsDefault: If True, will restore I{state} when the 
                             "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        
        @param spanWidth: If True, the checkbox and its label will span the width
                          of the group box. The label will appear directly above
                          the checkbox and is left aligned. 
        @type  spanWidth: bool
        
        @see: U{B{QCheckBox}<http://doc.trolltech.com/4/qcheckbox.html>}
        """
        
        if 0: # Debugging code
            print "PM_CheckBox.__init__():"
            print "  label        = ", label
            print "  labelColumn  = ", labelColumn
            print "  state        = ", state
            print "  setAsDefault = ", setAsDefault
            print "  spanWidth    = ", spanWidth
                
        QCheckBox.__init__(self)
        
        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth    = spanWidth
        
        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)
   
        self.setCheckState(state, setAsDefault)
        # We use this widget's QLabel to display the label, not the QCheckBox label.
        # So we premanently "remove" the checkbox text.
        self.setText("") 
        
        parentWidget.addPmWidget(self)
        
    def setCheckState( self, state, setAsDefault = True ):
        """
        Sets the check box's check state to I{state}.
        
        @param state: Set's the check box's check state.
        @type  state: U{B{Qt.CheckState}<http://doc.trolltech.com/4/
                          qt.html#CheckState-enum>}
                          
        @param setAsDefault: If True, will restore I{state} when the 
                             "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
        """
                  
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
            
    def collapse( self ):
        """
        Hides the checkbox and its label (if it has one) when its group box 
        is collapsed.
        """
        QWidget.hide(self) 
        if self.labelWidget :
            self.labelWidget.hide()
        
    def expand( self ):
        """
        Displays the checkbox and its label (if it has one) when its group 
        box is expanded, unless the checkbox was "permanently" hidden via
        L{hide()}. In that case, the checkbox will remain hidden until 
        L{show()} is called.
        """
        if self.hidden: return
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()
        
    def hide( self ):
        """
        Hides the checkbox and its label (if it has one). If hidden, the 
        checkbox will not be displayed when its group box is expanded.
        Call L{show()} to unhide the checkbox.
        
        @see: L{show}
        """
        self.hidden = True
        QWidget.hide(self)
        if self.labelWidget: 
            self.labelWidget.hide()
            
    def show( self ):
        """
        Unhide the checkbox and its label (if it has one). The checkbox
        will remain (temporarily) hidden if its group box is collapsed, 
        but will be displayed again when the group box is expanded.
        
        @see: L{hide}
        """
        self.hidden = False
        QWidget.show(self)
        if self.labelWidget: 
            self.labelWidget.show()

# End of PM_CheckBox ############################