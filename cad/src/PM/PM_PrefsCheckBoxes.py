# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_PrefsCheckBoxes.py

PM_PrefsCheckBoxes class provides a way to insert a groupbox within 
a Property Manager, that contains a bunch of check boxes connected
to the User Preference via  preference keys.

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
"""

from PyQt4.Qt import Qt

from PM.PM_GroupBox import PM_GroupBox
from PM.PM_CheckBox import PM_CheckBox

from widgets.prefs_widgets import connect_checkbox_with_boolean_pref



class PM_PrefsCheckBoxes(PM_GroupBox):
    """
    PM_PrefsCheckBoxes class provides a way to insert a groupbox within 
    a Property Manager, that contains a bunch of check boxes connected
    to the User Preference via  preference keys.
    """
    
    def __init__(self, 
                 parentWidget,
                 paramsForCheckBoxes = (),
                 checkBoxColumn = 1,
                 title = ''):
        """
        @param parentWidget: The parent dialog or group box containing this
                             widget.
        @type  parentWidget: L{PM_Dialog} or L{PM_GroupBox}
        
        @param title: The title (button) text. If empty, no title is added.
        @type  title: str
        
        @param paramsForCheckBoxes: A list object that contains tuples like the
               following : ('checkBoxTextString' , preference_key). The 
               checkboxes will be constucted by looping over this list.
        @type paramsForCheckBoxes:list
        @param checkBoxColumn: The widget column in which all the checkboxes
               will be inserted. 
        @type  checkBoxColumn: int
        
        @see: InsertDna_PropertyManager._loadDisplayOptionsGroupBox for an 
              example use.
        """
        PM_GroupBox.__init__(self, 
                             parentWidget, 
                             title = title)
        
        self._checkBoxColumn = checkBoxColumn
        
        #Also maintain all checkboxes created by this class in this list, 
        #just in case the caller needs them. (need access methods for this)
        self.checkBoxes = []   
        
        #Create checkboxes and also connect them to their preference keys.
        self._addCheckBoxes(paramsForCheckBoxes)        
        
    def _addCheckBoxes(self, paramsForCheckBoxes):
        """
        Creates PM_CheckBoxes within the groupbox and also connects each one
        with its individual prefs key.
        """
        for checkBoxText, prefs_key in paramsForCheckBoxes:            
            checkBox = \
                PM_CheckBox( self,
                             text  = checkBoxText,
                             widgetColumn = self._checkBoxColumn,
                             state        = Qt.Checked)
                                                  
            connect_checkbox_with_boolean_pref(
            checkBox , 
            prefs_key)
            
            self.checkBoxes.append(checkBox) 
