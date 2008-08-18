# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
MakeCrossovers_PropertyManager.py

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
See MakeCrossovers_Command for details. 
"""
import foundation.env as env

from widgets.DebugMenuMixin import DebugMenuMixin
from PM.PM_Dialog import PM_Dialog
from PM.PM_SelectionListWidget import PM_SelectionListWidget
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_PushButton import PM_PushButton
from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_CheckBox      import PM_CheckBox


from PyQt4.Qt import SIGNAL, Qt

from utilities.prefs_constants import assignColorToBrokenDnaStrands_prefs_key
from utilities.prefs_constants import makeCrossoversCommand_crossoverSearch_bet_given_segments_only_prefs_key
from dna.commands.MakeCrossovers.ListWidgetItems_PM_Mixin import ListWidgetItems_PM_Mixin
from utilities import debug_flags
from utilities.debug import print_compact_stack
from utilities.Comparison import same_vals
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref
from ne1_ui.WhatsThisText_for_PropertyManagers import whatsThis_MakeCrossoversPropertyManager
from utilities.Log import orangemsg

from utilities.GlobalPreferences import KEEP_SIGNALS_ALWAYS_CONNECTED

_superclass = PM_Dialog
class MakeCrossovers_PropertyManager( PM_Dialog, 
                                      ListWidgetItems_PM_Mixin,
                                      DebugMenuMixin ):
    """
    The MakeCrossovers_PropertyManager class provides a Property Manager 
    for the B{Make Crossovers} command on the flyout toolbar in the 
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

    title         =  "Make Crossovers"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/Crossover.png"


    def __init__( self, command):
        """
        Constructor for the property manager.
        """

        self.command = command
        #We will use self.command hereonwards. self.command is still declared
        #for safety -- 2008-05-29
        self.command = self.command

        self.w = self.command.w
        self.win = self.command.w
        self.pw = self.command.pw        
        self.o = self.win.glpane        

        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False

        self._previous_model_changed_params = None

        _superclass.__init__(self, self.pmName, self.iconPath, self.title)

        DebugMenuMixin._init1( self )

        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_WHATS_THIS_BUTTON)
        
        self.defaultLogMessage = """Pairs of white cylinders (if any) in the 
        3D workspace indicate potential crossover sites. Clicking on such a 
         cylinder pair will make that crossover."""

        self.updateMessage(self.defaultLogMessage)
        
        if KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)


    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        #TODO: This is a temporary fix for a bug. When you invoke a 
        #temporary mode  entering such a temporary mode keeps the signals of 
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

        self.segmentListWidget.connect_or_disconnect_signals(isConnect) 
        change_connect(self.addSegmentsToolButton, 
                       SIGNAL("toggled(bool)"), 
                       self.activateAddSegmentsTool)
        change_connect(self.removeSegmentsToolButton, 
                       SIGNAL("toggled(bool)"), 
                       self.activateRemoveSegmentsTool)

        change_connect(self.makeCrossoverPushButton,
                       SIGNAL("clicked()"),
                       self._makeAllCrossovers)
        
        connect_checkbox_with_boolean_pref(
             self.crossoversBetGivenSegmentsOnly_checkBox,
            makeCrossoversCommand_crossoverSearch_bet_given_segments_only_prefs_key)
        
                                                          
    def show(self):
        """
        Overrides the superclass method
        @see: self._deactivateAddRemoveSegmentsTool
        """
        _superclass.show(self)
        
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(True)
            
        ##self.updateListWidgets()       
        self._deactivateAddRemoveSegmentsTool()
        self._previous_model_changed_params = None

    def close(self):
        _superclass.close(self)
        
        if not KEEP_SIGNALS_ALWAYS_CONNECTED:
            self.connect_or_disconnect_signals(False)

    def _makeAllCrossovers(self):
        self.command.makeAllCrossovers()


    def _addGroupBoxes( self ):
        """
        Add the Property Manager group boxes.
        """        
        self._pmGroupBox1 = PM_GroupBox( self, title = "Segments for crossover search" )
        self._loadGroupBox1( self._pmGroupBox1 )


    def _loadGroupBox1(self, pmGroupBox):
        """
        load widgets in groupbox1
        """

        self._loadSegmentListWidget(pmGroupBox)  
        self.crossoversBetGivenSegmentsOnly_checkBox = PM_CheckBox( 
            pmGroupBox,
            text         = "Between above segments only",
            widgetColumn  = 0,
            setAsDefault = True,
            spanWidth = True,
            )
        
        #If this preferece value is True, the search algotithm will search for
        #the potential crossover sites only *between* the segments in the 
        #segment list widget (thus ignoring other segments not in that list)
        if env.prefs[makeCrossoversCommand_crossoverSearch_bet_given_segments_only_prefs_key]:
            self.crossoversBetGivenSegmentsOnly_checkBox.setCheckState(Qt.Checked) 
        else:
            self.crossoversBetGivenSegmentsOnly_checkBox.setCheckState(Qt.Unchecked)
        
        self.makeCrossoverPushButton = PM_PushButton( 
            pmGroupBox,
            label     = "",
            text      = "Make All Crossovers",
            spanWidth = True )
        

    def model_changed(self): 
        """
        @see: DnaSegment_EditCommand.model_changed()
        @see: DnaSegment_EditCommand.hasResizableStructure()
        @see: self._current_model_changed_params()
        """

        currentParams = self._current_model_changed_params()
        
        #Optimization. Return from the model_changed method if the 
        #params are the same. 
        if same_vals(currentParams, self._previous_model_changed_params):
            return 

        number_of_segments, \
                          crossover_search_pref_junk,\
                          bool_valid_segmentList_junk = currentParams
                
        #update the self._previous_model_changed_params with this new param set.
        self._previous_model_changed_params = currentParams       
        #Ensures that there are only PAM3 DNA segments in the commad's tructure 
        #list (command._structList. Call this before updating the list widgets!
        self.command.ensureValidSegmentList()
        self.updateListWidgets()   
        self.command.updateCrossoverSites()

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
            #update the list first. 
            self.command.updateSegmentList()
            bool_valid_segmentList = self.command.ensureValidSegmentList()
            number_of_segments = len(self.command.getSegmentList()) 
            crossover_search_pref = \
                                  env.prefs[makeCrossoversCommand_crossoverSearch_bet_given_segments_only_prefs_key]
            params = (number_of_segments, 
                      crossover_search_pref, 
                      bool_valid_segmentList
                  )

        return params

    def _addWhatsThisText( self ):
        """
        What's This text for widgets in the DNA Property Manager.  
        """
        whatsThis_MakeCrossoversPropertyManager(self)

    def _addToolTipText(self):
        """
        Tool Tip text for widgets in the DNA Property Manager.  
        """
        pass
    
    
    
