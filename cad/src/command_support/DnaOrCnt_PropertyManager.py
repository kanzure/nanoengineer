# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaOrCnt_PropertyManager.py

DnaOrCnt_PropertyManager class provides common functionality (e.g. groupboxes 
etc) to the subclasses that define various Dna and Cnt (Carbon nanotube) 
Property Managers. 

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created on 2008-05-20

TODO:
- Need a better name for this class? 
"""
from PyQt4.Qt              import Qt
from PM.PM_CheckBox        import PM_CheckBox
from PM.PM_PrefsCheckBoxes import PM_PrefsCheckBoxes

from command_support.EditCommand_PM import EditCommand_PM
from widgets.DebugMenuMixin         import DebugMenuMixin

_superclass = EditCommand_PM
class DnaOrCnt_PropertyManager(EditCommand_PM, DebugMenuMixin):
    """
    DnaOrCnt_PropertyManager class provides common functionality 
    (e.g. groupboxes etc) to the subclasses that define various Dna and Cnt
    (Carbon nanotube) Property Managers. 
    @see: DnaSegment_PropertyManager (subclass)
    @see: DnaDuplexPropertyManager (subclass)
    """

    def __init__( self, win, editCommand ):
        """
        Constructor for the DNA Duplex property manager.
        """
        
        self._cursorTextGroupBox = None
        self.showCursorTextCheckBox = None
        

        _superclass.__init__( self, 
                              win,
                              editCommand)

        DebugMenuMixin._init1( self )
        
        
    def show(self):
        """
        Show this PM
	"""
        _superclass.show(self)
        
        if isinstance(self.showCursorTextCheckBox, PM_CheckBox):
            self._update_state_of_cursorTextGroupBox(
                    self.showCursorTextCheckBox.isChecked())


    def _loadDisplayOptionsGroupBox(self, pmGroupBox):
        """
        Load widgets in the Display Options GroupBox
        """
        self._loadCursorTextGroupBox(pmGroupBox)

    def _loadCursorTextGroupBox(self, pmGroupBox):
        """
        Load various checkboxes within the cursor text groupbox. 
        @see: self. _loadDisplayOptionsGroupBox()
        @see: self._connect_showCursorTextCheckBox()
        @see: self._params_for_creating_cursorTextCheckBoxes()
        """
        self.showCursorTextCheckBox = \
            PM_CheckBox( 
                pmGroupBox,
                text  = "Show cursor text",
                widgetColumn = 0,
                state        = Qt.Checked)

        self._connect_showCursorTextCheckBox()

        paramsForCheckBoxes = self._params_for_creating_cursorTextCheckBoxes()

        self._cursorTextGroupBox = PM_PrefsCheckBoxes(
            pmGroupBox, 
            paramsForCheckBoxes = paramsForCheckBoxes,            
            title = 'Cursor text options:')

    def _connect_showCursorTextCheckBox(self):
        """
        Connect the show cursor text checkbox with user prefs_key.
        Subclasses should override this method. The default implementation 
        does nothing. 
        """
        pass

    def _params_for_creating_cursorTextCheckBoxes(self):
        """
        Subclasses should override this method. The default implementation 
        returns an empty list.
        Returns params needed to create various cursor text checkboxes connected
        to prefs_keys  that allow custom cursor texts. 
        @return: A list containing tuples in the following format:
                ('checkBoxTextString' , preference_key). PM_PrefsCheckBoxes 
                uses this data to create checkboxes with the the given names and
                connects them to the provided preference keys. (Note that 
                PM_PrefsCheckBoxes puts thes within a GroupBox)
        @rtype: list
        @see: PM_PrefsCheckBoxes
        @see: self._loadDisplayOptionsGroupBox where this list is used. 
        #see: self._loadCursorTextGroupBox()
        @see: subclass method: 
        DnaSegment_PropertyManager._params_for_creating_cursorTextCheckBoxes()
        """
        params = [] #Format: (" checkbox text", prefs_key)

        return params
    
    
    def _update_state_of_cursorTextGroupBox(self, enable):
        """
        """
        if not isinstance(self._cursorTextGroupBox, PM_PrefsCheckBoxes):
            return
        
        if enable:
            self._cursorTextGroupBox.setEnabled(True)
        else:
            self._cursorTextGroupBox.setEnabled(False)

