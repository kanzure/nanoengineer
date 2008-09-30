# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_CheckBox.py

@author: Mark
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrCheckBox out of PropMgrBaseClass.py into this file
and renamed it PM_CheckBox.

"""

from PyQt4.Qt import Qt
from PyQt4.Qt import QCheckBox
from PyQt4.Qt import QLabel
from PyQt4.Qt import QWidget

from PM.PM_Constants import PM_LEFT_COLUMN, PM_RIGHT_COLUMN

from widgets.prefs_widgets import widget_connectWithState
from widgets.prefs_widgets import QCheckBox_ConnectionWithState
from widgets.prefs_widgets import set_metainfo_from_stateref

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
                 state         = None, ##Qt.Unchecked, 
                 setAsDefault  = True,
                 spanWidth = False
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
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left 
                      justified.
        @type  spanWidth: bool
     
        
        @see: U{B{QCheckBox}<http://doc.trolltech.com/4/qcheckbox.html>}
        """
                        
        QCheckBox.__init__(self)
        self.parentWidget = parentWidget        
        self.setText(text)
        self.widgetColumn = widgetColumn
        self.setAsDefault = setAsDefault
        self.spanWidth = spanWidth
   
        #Ideally, this should be simply self.setCheckState(state)  with the 
        #default state = Qt.UnChecked in the ,init argument itself. But, 
        #apparently pylint chokes up when init argument is a Qt enum. 
        #This problem happened while running pylint 0.23 on the SEMBOT server 
        #so comitting this temporary workaround. The pylint on my machine is 
        #0.25 and it runs fine even before this workaround. Similar changes made
        #in PM_Slider. 
        #-- Ninad 2008-06-30
        if state is None:
            state = Qt.Unchecked
        
        if self.setAsDefault:
            self.setDefaultState(state)
            
        self.setCheckState(state)          
        
        parentWidget.addPmWidget(self)
    
    def setDefaultState(self, state):
        self.setAsDefault = True
        self.defaultState = state
        pass
    
    def setCheckState(self, state, setAsDefault = False):
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

    def connectWithState(self,
                         stateref,
                         set_metainfo = True,
                         debug_metainfo = False):
        """
        Connect self to the state referred to by stateref,
        so changes to self's value change that state's value
        and vice versa. By default, also set self's metainfo
        to correspond to what the stateref provides.

        @param stateref: a reference to state of type boolean,
                         which meets the state-reference interface StateRef_API
        @type stateref: StateRef_API

        @param set_metainfo: whether to also set defaultValue,
                             if it's provided by the stateref
        
        @type set_metainfo: bool

        @param debug_metainfo: whether to print debug messages
                               about the actions taken by set_metainfo
        
        @type debug_metainfo: bool
        """
        if set_metainfo:
            set_metainfo_from_stateref( self.setDefaultValue, stateref,
                                        'defaultValue', debug_metainfo)
        widget_connectWithState( self, stateref,
                                 QCheckBox_ConnectionWithState)
            # note: that class uses setChecked, not setCheckState
        return

    def setDefaultValue(self, value): #bruce 070815 guess
        self.setAsDefault = True
        if value:
            self.defaultState = Qt.Checked
        else:
            self.defaultState = Qt.Unchecked  
        return

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
        
    pass
              
# End of PM_CheckBox ############################
