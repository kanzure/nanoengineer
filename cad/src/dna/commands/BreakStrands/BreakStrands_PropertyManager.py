# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BreakStrands_PropertyManager.py

 The BreakStrands_PropertyManager class provides a Property Manager 
    for the B{Break Strands} command on the flyout toolbar in the 
    Build > Dna mode. 

@author: Ninad
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.


TODO: as of 2008-02-13:
- Remove 'Cancel' button -- This needs to be supported in transient done-cancel
button code (confirmation_corner)
- methods such as ok_btn_clicked need cleanup in the superclass. This workis 
pending because of some remaining things in GBC cleanup (such as 
NanotubeGenerator etc) 

Ninad 2008-06-05: 
Revised and refactored arrowhead display code and moved part common to both 
Break and JoinStrands PMs into new module BreakOrJoinStrands_PropertyManager
"""

from PyQt4.Qt import SIGNAL
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

from PM.PM_GroupBox import PM_GroupBox
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_SpinBox import PM_SpinBox
from PM.PM_PushButton import PM_PushButton


from utilities.prefs_constants import assignColorToBrokenDnaStrands_prefs_key
from utilities.prefs_constants import breakStrandsCommand_arrowsOnThreePrimeEnds_prefs_key
from utilities.prefs_constants import breakStrandsCommand_arrowsOnFivePrimeEnds_prefs_key 
from utilities.prefs_constants import breakStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key 
from utilities.prefs_constants import breakStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key 
from utilities.prefs_constants import breakStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key 
from utilities.prefs_constants import breakStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key 

from utilities.prefs_constants import breakStrandsCommand_numberOfBasesBeforeNextBreak_prefs_key 


from utilities.Comparison import same_vals
from utilities import debug_flags
from utilities.debug import print_compact_stack
from dna.command_support.BreakOrJoinStrands_PropertyManager import BreakOrJoinStrands_PropertyManager

import foundation.env as env

from widgets.prefs_widgets import connect_spinBox_with_pref


from utilities.GlobalPreferences import DEBUG_BREAK_OPTIONS_FEATURE


from PM.PM_ObjectChooser import PM_ObjectChooser

DEBUG_CHANGE_COUNTERS = False

_superclass = BreakOrJoinStrands_PropertyManager


class BreakStrands_PropertyManager( BreakOrJoinStrands_PropertyManager):
    """
    The BreakStrands_PropertyManager class provides a Property Manager 
    for the B{Break Strands} command on the flyout toolbar in the 
    Build > Dna mode. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "Break Strands"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/Break_Strand.png"
    
    
    def __init__( self, command ):
        """
        Constructor for the property manager.
        """
        self._previous_model_changed_params = None
        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False 
        
        self.command = command
        self.win = self.command.win
        
        _superclass.__init__(self, command)
  
        msg = "Click on a strand's backbone bond to break a strand."
        self.updateMessage(msg)
        
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        #TODO: This is a temporary fix for a bug. When you invoke a temporary mode 
        # entering such a temporary mode keeps the signals of 
        #PM from the previous mode connected (
        #but while exiting that temporary mode and reentering the 
        #previous mode, it atucally reconnects the signal! This gives rise to 
        #lots  of bugs. This needs more general fix in Temporary mode API. 
        # -- Ninad 2008-01-09 (similar comment exists in MovePropertyManager.py
                
        if isConnect and self.isAlreadyConnected:
            if debug_flags.atom_debug:
                print_compact_stack("warning: attempt to connect widgets"\
                                    "in this PM that are already connected." )
            return 
        
        if not isConnect and self.isAlreadyDisconnected:
            if debug_flags.atom_debug:
                print_compact_stack("warning: attempt to disconnect widgets"\
                                    "in this PM that are already disconnected.")
            return
        
        self.isAlreadyConnected = isConnect
        self.isAlreadyDisconnected = not isConnect
        
        if isConnect:
            change_connect = self.win.connect     
        else:
            change_connect = self.win.disconnect 
            
        _superclass.connect_or_disconnect_signals(self, isConnect = isConnect)
        
        
        if DEBUG_BREAK_OPTIONS_FEATURE:
            
            self._dnaStrandChooserGroupBox.connect_or_disconnect_signals(isConnect = isConnect)
            
            change_connect(self.breakAllStrandsButton,
                          SIGNAL("clicked()"),
                          self.command.breakStrandBonds)
            
            change_connect(self.basesBeforeNextBreakSpinBox, 
                           SIGNAL("valueChanged(int)"), 
                           self.valueChanged_basesBeforeNextBreak)
            
            
    def _update_UI_do_updates(self):
        """
        Overrides superclass method. 
        @see: PM_Dialog._update_UI_do_updates()
        @see: DnaSegment_EditCommand.hasResizableStructure()
        @see: self._current_model_changed_params()
        """
        if not DEBUG_BREAK_OPTIONS_FEATURE:
            return 
        
                 
        
        currentParams = self._current_model_changed_params()
        
        #Optimization. Return from the model_changed method if the 
        #params are the same. 
        if same_vals(currentParams, self._previous_model_changed_params):
            return 

        basesBeforeNextBreak = currentParams
                
        #update the self._previous_model_changed_params with this new param set.
        self._previous_model_changed_params = currentParams  
        self.command.updateBreakSites()
               
    def _current_model_changed_params(self):
        """
        Returns a tuple containing the parameters that will be compared
        against the previously stored parameters. This provides a quick test
        to determine whether to do more things in self.model_changed()
        @see: self.model_changed() which calls this
        @see: self._previous_model_changed_params attr. 
        """
        params = None

        if self.command:                        
            params = (env.prefs[breakStrandsCommand_numberOfBasesBeforeNextBreak_prefs_key])

        return params
    
    def valueChanged_basesBeforeNextBreak(self, val):       
        self.win.glpane.gl_update()        
        
    def getNumberOfBasesBeforeNextBreak(self):        
        return self.basesBeforeNextBreakSpinBox.value()
        
    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """        
        self._breakOptionsGroupbox = PM_GroupBox( self, title = "Break Options" )
        self._loadBreakOptionsGroupbox( self._breakOptionsGroupbox )
        
         
        self._displayOptionsGroupBox = PM_GroupBox( self, title = "Display options" )
        self._loadDisplayOptionsGroupBox( self._displayOptionsGroupBox )
        
        self._baseNumberLabelGroupBox = PM_GroupBox( self, title = "Base number labels" )
        self._loadBaseNumberLabelGroupBox(self._baseNumberLabelGroupBox)
        
            
    def _loadBreakOptionsGroupbox(self, pmGroupBox):
        """
        Load widgets in this group box.
        """        
        
        self.assignColorToBrokenDnaStrandsCheckBox = \
            PM_CheckBox(pmGroupBox ,
                        text         = 'Assign new color to broken strands',
                        widgetColumn = 0, 
                        spanWidth = True)
        
        connect_checkbox_with_boolean_pref(
            self.assignColorToBrokenDnaStrandsCheckBox, 
            assignColorToBrokenDnaStrands_prefs_key )
        
           
        
        self.basesBeforeNextBreakSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Break Every:", 
                        value         =  3,
                        setAsDefault  =  False,
                        minimum       =  1,
                        maximum       =  10000,
                        suffix       = " bases"
                        )
        
        connect_spinBox_with_pref(
            self.basesBeforeNextBreakSpinBox, 
            breakStrandsCommand_numberOfBasesBeforeNextBreak_prefs_key)
        
        self.breakAllStrandsButton = PM_PushButton( 
            pmGroupBox,
            label = "",
            text  = "do it" )
    
                
        self._dnaStrandChooserGroupBox = PM_ObjectChooser(            
            pmGroupBox,
            self.command,
            modelObjectType = self.win.assy.DnaStrand,
            title = "Choose strands " )
        
        if not DEBUG_BREAK_OPTIONS_FEATURE:
            self._dnaStrandChooserGroupBox.hide()
            self.breakAllStrandsButton.hide()
            self.basesBeforeNextBreakSpinBox.hide()
            
        

    #Return varius prefs_keys for arrowhead display options ui elements =======     
    def _prefs_key_arrowsOnThreePrimeEnds(self):
        """
        Return the appropriate KEY of the preference for whether to
        draw arrows on 3' strand ends of PAM DNA.
        """
        return breakStrandsCommand_arrowsOnThreePrimeEnds_prefs_key
    
    def _prefs_key_arrowsOnFivePrimeEnds(self):
        """
        Return the appropriate KEY of the preference for whether to
        draw arrows on 5' strand ends of PAM DNA.
        """
        return breakStrandsCommand_arrowsOnFivePrimeEnds_prefs_key
    
    def _prefs_key_useCustomColorForThreePrimeArrowheads(self):
        """
        Return the appropriate KEY of the preference for whether to use a
        custom color for 3' arrowheads (if they are drawn)
        or for 3' strand end atoms (if arrowheads are not drawn)
        """
        return breakStrandsCommand_useCustomColorForThreePrimeArrowheads_prefs_key
    
    def _prefs_key_useCustomColorForFivePrimeArrowheads(self):
        """
        Return the appropriate KEY of the preference for whether to use a
        custom color for 5' arrowheads (if they are drawn)
        or for 5' strand end atoms (if arrowheads are not drawn).        
        """
        return breakStrandsCommand_useCustomColorForFivePrimeArrowheads_prefs_key
    
    def _prefs_key_dnaStrandThreePrimeArrowheadsCustomColor(self):
        """
        Return the appropriate KEY of the preference for what custom color
        to use when drawing 3' arrowheads (if they are drawn)
        or 3' strand end atoms (if arrowheads are not drawn).
        """
        return breakStrandsCommand_dnaStrandThreePrimeArrowheadsCustomColor_prefs_key
    
    def _prefs_key_dnaStrandFivePrimeArrowheadsCustomColor(self):
        """
        Return the appropriate KEY of the preference for what custom color
        to use when drawing 5' arrowheads (if they are drawn)
        or 5' strand end atoms (if arrowheads are not drawn).
        """
        return breakStrandsCommand_dnaStrandFivePrimeArrowheadsCustomColor_prefs_key
    

    def _addWhatsThisText( self ):
        """
        What's This text for widgets in the DNA Property Manager.  
        """
        pass
                
    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the DNA Property Manager.  
        """
        pass
    
    
    
