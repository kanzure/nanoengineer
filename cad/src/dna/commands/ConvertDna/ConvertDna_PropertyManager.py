# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_PushButton import PM_PushButton
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON

from command_support.Command_PropertyManager import Command_PropertyManager

_superclass = Command_PropertyManager
class ConvertDna_PropertyManager(Command_PropertyManager):
    """
    Provides a Property Manager for the B{Convert Dna} command. 
    """
    
    def __init__( self, command ):
        """
        Constructor for the property manager.
        """
        
        _superclass.__init__(self, command)
        
        self.assy = self.win.assy

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        self.updateMessage()        
       
        return
        
        
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect 
        
        change_connect(self._convertButton, 
                             SIGNAL("clicked()"),
                             self._convertDna)
        
        ##change_connect( self.includeStrandsComboBox,
                      ##SIGNAL("activated(int)"),
                      ##self.update_includeStrands )
        return
    
    def _convertDna(self):
        if self._convertChoiceComboBox.currentIndex() == 0:
            self._convertPAM3ToPAM5()
        else:
            self._convertPAM5ToPAM3()
        return
            
    def _convertPAM3ToPAM5(self):
        self.command.assy.convertPAM3to5Command()
        return
    
    def _convertPAM5ToPAM3(self):
        self.command.assy.convertPAM5to3Command()
        return 
       
    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """        
        self._pmGroupBox1 = PM_GroupBox( self, title = "Options" )
        self._loadGroupBox1( self._pmGroupBox1 )
        return
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        convertChoices = ["PAM3 to PAM5",
                        "PAM5 to PAM3"]
        
        self._convertChoiceComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "Convert options:", 
                         choices       =  convertChoices,
                         setAsDefault  =  True)
        
        
                
        self._convertButton = \
            PM_PushButton( pmGroupBox,
                           label     = "",
                           text      = "Convert now",
                           spanWidth = True)
        return
    
    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.
        """
        pass
    
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the DNA Property Manager.  
        """
        pass
    
    def updateMessage(self, msg = ''):
        """
        
        """
        if not msg:
            msg = "To contert DNA, select the DNA you want to convert and "\
                " press the <b>Convert now</b> button."
                
        _superclass.updateMessage(self, msg)
        return
    
