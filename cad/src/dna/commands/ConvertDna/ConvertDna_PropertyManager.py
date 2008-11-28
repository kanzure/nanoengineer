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

from dna.model.DnaStrand import DnaStrand

from command_support.Command_PropertyManager import Command_PropertyManager

_superclass = Command_PropertyManager
class ConvertDna_PropertyManager(Command_PropertyManager):
    """
    Provides a Property Manager for the B{Convert Dna} command. 
    """
    
    title         =  "Convert DNA"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/BuildDna/ConvertDna.png"
    
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
    
    # Ask Bruce where this should live (i.e. class Part?) --Mark
    # This method was copied from OrderDna_PropertyManager.py
    def _getAllDnaStrands(self, selectedOnly = False):
        """
        Returns a list of all the DNA strands in the current part, or only
        the selected strands if I{selectedOnly} is True.
        
        @param selectedOnly: If True, return only the selected DNA strands.
        @type  selectedOnly: bool
        """
        
        dnaStrandList = []
         
        def func(node):
            if isinstance(node, DnaStrand):
                if selectedOnly:
                    if node.picked:
                        dnaStrandList.append(node)
                else:
                    dnaStrandList.append(node)
                    
        self.win.assy.part.topnode.apply2all(func)
        
        return dnaStrandList
    
    def _convertDna(self):
        
        _dnaStrandList = []
        _dnaStrandList = self._getAllDnaStrands(selectedOnly = True)
        
        if not _dnaStrandList:
            msg = "<font color=red>" \
                "Nothing converted since no DNA strands are currently selected."
            self.updateMessage(msg)
            return
            
        if self._convertChoiceComboBox.currentIndex() == 0:
            self._convertPAM3ToPAM5()
        else:
            self._convertPAM5ToPAM3()
            
        self.updateMessage()
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
        self._pmGroupBox1 = PM_GroupBox( self, title = "Conversion Options" )
        self._loadGroupBox1( self._pmGroupBox1 )
        return
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box.
        """
        
        convertChoices = ["Convert from PAM3 to PAM5",
                        "Convert from PAM5 to PAM3"]
        
        self._convertChoiceComboBox  = \
            PM_ComboBox( pmGroupBox,
                         label         =  "", 
                         choices       =  convertChoices,
                         index         =  0,
                         setAsDefault  =  True,
                         spanWidth     =  True)
        
        self._convertButton = \
            PM_PushButton( pmGroupBox,
                           label     = "",
                           text      = "Convert Selection Now",
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
    
    def show(self):
        """
        Show this property manager. Overrides EditCommand_PM.show()
        We need this here to force the message update whenever we show the PM
        since an old message might still be there.
        """
        _superclass.show(self)
        self.updateMessage()
    
    def updateMessage(self, msg = ''):
        """
        
        """
        if not msg:
            msg = "Select the DNA you want to convert, then select the appropriate "\
                "conversion option and press the <b>Convert Selection Now</b> button."
            
        _superclass.updateMessage(self, msg)
        return
    
