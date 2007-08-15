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
    The PM_CheckBox widget provides a checkbox with a text label for a Property
    Manager group box. The text label can be positioned on the left or 
    right side of the checkbox.
    
    A PM_CheckBox is an option button that can be switched on (checked) or 
    off (unchecked). Checkboxes are typically used to represent features in 
    an application that can be enabled or disabled without affecting others, 
    but different types of behavior can be implemented.
    
    A U{B{QButtonGroup}<http://doc.trolltech.com/4/qbuttongroup.html>} 
    can be used to group check buttons visually.
    
    Whenever a checkbox is checked or cleared it emits the signal 
    stateChanged(). Connect to this signal if you want to trigger an action 
    each time the checkbox changes state. You can use isChecked() to query 
    whether or not a checkbox is checked.
    
    In addition to the usual checked and unchecked states, PM_CheckBox 
    optionally provides a third state to indicate "no change". This is useful 
    whenever you need to give the user the option of neither checking nor 
    unchecking a checkbox. If you need this third state, enable it with 
    setTristate(), and use checkState() to query the current toggle state.
    
    Just like PM_PushButton, a checkbox displays text, and optionally a 
    small icon. The icon is set with setIcon(). The text can be set in the 
    constructor or with setText(). A shortcut key can be specified by preceding
    the preferred character with an ampersand. For example:
    
    checkbox = PM_CheckBox("C&ase sensitive")
 
    In this example the shortcut is B{Alt+A}. See the  
    U{B{QShortcut}<http://doc.trolltech.com/4/qshortcut.html>} documentation 
    for details (to display an actual ampersand, use '&&').
    
    @cvar defaultState: The default state of the checkbox.
    @type defaultState: U{B{Qt.CheckState}<http://doc.trolltech.com/4/
                          qt.html#CheckState-enum>}
    
    @cvar setAsDefault: Determines whether to reset the state of the
                        checkbox to I{defaultState} when the user clicks
                        the "Restore Defaults" button.
    @type setAsDefault: bool
    
    @cvar labelWidget: The Qt label widget of this checkbox. This value is 
                       set to 'None'
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """
    
    defaultState = Qt.Unchecked  
    setAsDefault = True
    labelWidget = None
        
    def __init__(self, 
                 parentWidget, 
                 text          = '', 
                 widgetColumn  = 1,
                 state         = Qt.Unchecked, 
                 setAsDefault  = True
                 ):
        """
        Appends a QCheckBox (Qt) widget to the bottom of I{parentWidget}, 
        a Property Manager group box.
        
        @param parentWidget: The parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param text: This property holds the text shown on the checkbox.                     
        @type  text: str
        
        @param widgetColumn: The column number of the PM_CheckBox widget
                             in the group box grid layout. The only valid values 
                             are 0 (left column) and 1 (right column). 
                             The default is 1 (right column).                             
        @type  widgetColumn: int
        
        @param state: Set's the check box's check state. The default is
                      Qt.Unchecked (unchecked).
        @type  state: U{B{Qt.CheckState}<http://doc.trolltech.com/4/
                          qt.html#CheckState-enum>}
        
        @param setAsDefault: If True, will restore I{state} when the 
                             "Restore Defaults" button is clicked.
        @type  setAsDefault: bool
     
        
        @see: U{B{QCheckBox}<http://doc.trolltech.com/4/qcheckbox.html>}
        """
                        
        QCheckBox.__init__(self)
        self.parentWidget = parentWidget        
        self.setText(text)
        self.widgetColumn = widgetColumn
        self.setAsDefault = setAsDefault
        self.setCheckState(state, setAsDefault)        
                 
        parentWidget.addPmWidget(self)
    
                
    def setCheckState(self, state, setAsDefault = True):
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
            self.setAsDefault = setAsDefault
            self.defaultState = state
        
        QCheckBox.setCheckState(self, state)
        
    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.setCheckState(self.defaultState)
        
    def hide(self):
        """
        Hides the checkbox and its label (if it has one).
        Call L{show()} to unhide the checkbox.
        
        @see: L{show}
        """
        QWidget.hide(self)
        
            
    def show(self):
        """
        Unhides the checkbox and its label (if it has one).
        
        @see: L{hide}
        """
        QWidget.show(self)
        
    
              
# End of PM_CheckBox ############################