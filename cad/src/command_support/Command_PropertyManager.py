# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
This is a superclass for the property managers of various command objects 

@author: Ninad
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-10-01 : Created this to make it a common superclass of all command PMs
Moved common code from EditCommand_PM to here. 

TODO as of 2008-10-01
- get rid of "not KEEP_SIGNALS_CONNECTED"  case
- revise/ remove self.enable_or_disable_gui_actions() completely
- move PM_dialog.update_UI() to here? 
"""
from PM.PM_Dialog import PM_Dialog
from utilities.exception_classes import AbstractMethod
#debug flag to keep signals always connected
from utilities.GlobalPreferences import KEEP_SIGNALS_ALWAYS_CONNECTED

_superclass = PM_Dialog

class Command_PropertyManager(PM_Dialog):
    """
    This is a superclass for the property managers of various command objects 
    @see: B{PlanePropertyManager} as an example
    @see: B{PM_Dialog}
    """
    # The title that appears in the Property Manager header.
    title = "Property Manager"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = ""
    
    def __init__(self, command):   
        """
        Constructor for Command_PropertyManager. 
        """     
        self.command = command
        self.win = self.command.win
        self.w = self.win
        self.pw = self.command.pw
        self.o = self.win.glpane
        
        _superclass.__init__(self, self.pmName, self.iconPath, self.title)  
        
        if KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)
            
    
    def show(self):
        """
        Shows the Property Manager. Extends superclass method.
        """
        _superclass.show(self)
        
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)
            
        self.enable_or_disable_gui_actions(bool_enable = False)
        

    def close(self):
        """
        Closes the Property Manager. Extends superclass method.
        """            
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(False)
            
        self.enable_or_disable_gui_actions(bool_enable = True)
        _superclass.close(self)
        
        
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot
                          method.
        @type  isConnect: boolean
        """
        pass
    
    def enable_or_disable_gui_actions(self, bool_enable = False):
        """
        Enable or disable some gui actions when this property manager is
        opened or closed, depending on the bool_enable.
        Subclasses can override this method.
        """
        pass
    
    
    def _addGroupBoxes(self):
        """
        Add various group boxes to this PM.
        Abstract method.
        """
        raise AbstractMethod()

    def _addWhatsThisText(self):
        """
        Add what's this text.
        Abstract method.
        """
        raise AbstractMethod()
    
        