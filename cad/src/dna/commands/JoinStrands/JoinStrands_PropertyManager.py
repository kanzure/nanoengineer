# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
JoinStrands_PropertyManager.py

 The JoinStrands_PropertyManager class provides a Property Manager 
    for the B{Join Strands} command on the flyout toolbar in the 
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
"""
import sys
import foundation.env as env
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from widgets.DebugMenuMixin import DebugMenuMixin
from PM.PM_Dialog import PM_Dialog
from PM.PM_Constants     import pmDoneButton
from PM.PM_Constants     import pmWhatsThisButton
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_ColorChooser  import PM_ColorChooser
from utilities.prefs_constants import arrowsOnBackBones_prefs_key
from utilities.prefs_constants import arrowsOnThreePrimeEnds_prefs_key
from utilities.prefs_constants import arrowsOnFivePrimeEnds_prefs_key
from utilities.prefs_constants import useCustomColorForThreePrimeArrowheads_prefs_key
from utilities.prefs_constants import useCustomColorForFivePrimeArrowheads_prefs_key
from utilities.prefs_constants import dnaStrandThreePrimeArrowheadsCustomColor_prefs_key
from utilities.prefs_constants import dnaStrandFivePrimeArrowheadsCustomColor_prefs_key
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

class JoinStrands_PropertyManager( PM_Dialog, DebugMenuMixin ):
    """
    The JoinStrands_PropertyManager class provides a Property Manager 
    for the B{Join Strands} command on the flyout toolbar in the 
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

    title         =  "Join Strands"
    pmName        =  title
    iconPath      =  "ui/actions/Command Toolbar/Join_Strands.png"
    
    
    def __init__( self, parentCommand ):
        """
        Constructor for the property manager.
        """

        self.parentMode = parentCommand
        self.w = self.parentMode.w
        self.win = self.parentMode.w
        self.pw = self.parentMode.pw        
        self.o = self.win.glpane      
        
        #We want all the DNA display options to be turned on when an user 
        # comes into join strand command.
        
        self._setAllDisplayOptionsToTrue()
                    
        PM_Dialog.__init__(self, self.pmName, self.iconPath, self.title)
        
        DebugMenuMixin._init1( self )

        self.showTopRowButtons( pmDoneButton | \
                                pmWhatsThisButton)
        
                
        if sys.platform == 'darwin':
            leftMouseButtonString = 'mouse button'
        else:
            leftMouseButtonString = 'left mouse button'
        
        # Note: 
        msg = ("To join two strands, highlight a 3' arrowhead of one "\
               "strand, hold down the %s and then release it when the cursor "\
               "is over the 5' end of a different strand.") % \
            (leftMouseButtonString)
        
        self.updateMessage(msg)
    
        
    def _setAllDisplayOptionsToTrue(self):
        
        """"
        Set all pref keys to True
        """
        self._local_arrowsOnBackBones_prefs_key = True
        self._local_arrowsOnThreePrimeEnds_prefs_key = True 
        self._local_arrowsOnFivePrimeEnds_prefs_key = True
        self._local_useCustomColorForThreePrimeArrowheads_prefs_key = True
        self._local_useCustomColorForFivePrimeArrowheads_prefs_key = True
        
        env.prefs[arrowsOnBackBones_prefs_key] = self._local_arrowsOnBackBones_prefs_key 
        env.prefs[arrowsOnThreePrimeEnds_prefs_key] = self._local_arrowsOnThreePrimeEnds_prefs_key 
        env.prefs[arrowsOnFivePrimeEnds_prefs_key] = self._local_arrowsOnFivePrimeEnds_prefs_key 
        env.prefs[useCustomColorForThreePrimeArrowheads_prefs_key] = self._local_useCustomColorForThreePrimeArrowheads_prefs_key 
        env.prefs[useCustomColorForFivePrimeArrowheads_prefs_key] =  self._local_useCustomColorForFivePrimeArrowheads_prefs_key 
        

        return
        
    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """      
        self.win.toolsDone()
    
    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """  
        #TODO: Cancel button needs to be removed. See comment at the top
        self.win.toolsDone()
        
        
    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """  
        self._pmGroupBox = PM_GroupBox( self, 
                                         title = "Strand arrowhead display options")
        #load all the options
        self._load3PrimeEndArrowAndCustomColor(self._pmGroupBox)
        self._load5PrimeEndArrowAndCustomColor(self._pmGroupBox)
        self._loadArrowOnBackBone(self._pmGroupBox)
        
        return
    
    def _load3PrimeEndArrowAndCustomColor(self, pmGroupBox):
        """
        Loads 3' end arrow head and custom color checkbox and color chooser dialog
        """
        self.pmGroupBox3 = PM_GroupBox(pmGroupBox, title = "3' end:")
        
        self.arrowsOnThreePrimeEnds_checkBox = PM_CheckBox( self.pmGroupBox3,
                                                            text         = "Show arrow",
                                                            widgetColumn  = 0,
                                                            setAsDefault = True,
                                                            spanWidth = True
                                                            )
        
        if env.prefs[arrowsOnThreePrimeEnds_prefs_key] == True:
            self.arrowsOnThreePrimeEnds_checkBox.setCheckState(Qt.Checked) 
        else:
            self.arrowsOnThreePrimeEnds_checkBox.setCheckState(Qt.Unchecked)
            
        self.strandThreePrimeArrowheadsCustomColorCheckBox = PM_CheckBox( self.pmGroupBox3,
                                                            text         = "Display Custom Color",
                                                            widgetColumn  = 0,
                                                            setAsDefault = True,
                                                            spanWidth = True
                                                            )
        self.threePrimeEndColorChooser = \
            PM_ColorChooser(self.pmGroupBox3,
                            label = "Color"
                            ) 
        self.threePrimeEndColorChooser.setColor(env.prefs[dnaStrandThreePrimeArrowheadsCustomColor_prefs_key])
        
        if env.prefs[useCustomColorForThreePrimeArrowheads_prefs_key] == True:
            self.strandThreePrimeArrowheadsCustomColorCheckBox.setCheckState(Qt.Checked) 
            self.threePrimeEndColorChooser.show()
        else:
            self.strandThreePrimeArrowheadsCustomColorCheckBox.setCheckState(Qt.Unchecked)
            self.threePrimeEndColorChooser.hide()
            
        
        return 
    
    def _load5PrimeEndArrowAndCustomColor(self, pmGroupBox):
        """
        Loads 5' end custom color checkbox and color chooser dialog
        """
        self.pmGroupBox2 = PM_GroupBox(pmGroupBox, title = "5' end:")
        self.arrowsOnFivePrimeEnds_checkBox = PM_CheckBox( self.pmGroupBox2,
                                                            text         = "Show arrow",
                                                            widgetColumn  = 0,
                                                            setAsDefault = True,
                                                            spanWidth = True
                                                            )
        if env.prefs[arrowsOnFivePrimeEnds_prefs_key] == True:
            self.arrowsOnFivePrimeEnds_checkBox.setCheckState(Qt.Checked) 
        else:
            self.arrowsOnFivePrimeEnds_checkBox.setCheckState(Qt.Unchecked)
            
        self.strandFivePrimeArrowheadsCustomColorCheckBox = PM_CheckBox( self.pmGroupBox2,
                                                            text         = "Display Custom Color",
                                                            widgetColumn  = 0,
                                                            setAsDefault = True,
                                                            spanWidth = True
                                                            )
        self.fivePrimeEndColorChooser = \
            PM_ColorChooser(self.pmGroupBox2,
                            label = "Color"
                            ) 
        self.fivePrimeEndColorChooser.setColor(env.prefs[dnaStrandFivePrimeArrowheadsCustomColor_prefs_key])
        
        if env.prefs[useCustomColorForFivePrimeArrowheads_prefs_key] == True:
            self.strandFivePrimeArrowheadsCustomColorCheckBox.setCheckState(Qt.Checked) 
            self.fivePrimeEndColorChooser.show()
        else:
            self.strandFivePrimeArrowheadsCustomColorCheckBox.setCheckState(Qt.Unchecked)
            self.fivePrimeEndColorChooser.hide()
        
        return 
    
        
    def _loadArrowOnBackBone(self, pmGroupBox):
        """
        Loads Arrow on the backbone checkbox
        """
        self.pmGroupBox4 = PM_GroupBox(pmGroupBox, title = "")
        self.arrowsOnBackBones_checkBox = PM_CheckBox( self.pmGroupBox4,
                                                       text         = "Show arrows on back bones",
                                                       widgetColumn  = 0,
                                                       setAsDefault = True,
                                                       spanWidth = True
                                                       )
        if env.prefs[arrowsOnBackBones_prefs_key] == True:
            self.arrowsOnBackBones_checkBox.setCheckState(Qt.Checked) 
        else:
            self.arrowsOnBackBones_checkBox.setCheckState(Qt.Unchecked) 
            
        
    
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
        
        # DNA Strand arrowhead display options signal-slot connections.
        
        
        
        connect_checkbox_with_boolean_pref(self.arrowsOnThreePrimeEnds_checkBox,
                                           arrowsOnThreePrimeEnds_prefs_key)
                                           
        connect_checkbox_with_boolean_pref(self.arrowsOnFivePrimeEnds_checkBox,
                                           arrowsOnFivePrimeEnds_prefs_key)
        
        connect_checkbox_with_boolean_pref(self.strandFivePrimeArrowheadsCustomColorCheckBox,
                                           useCustomColorForFivePrimeArrowheads_prefs_key)
        
        connect_checkbox_with_boolean_pref(self.strandThreePrimeArrowheadsCustomColorCheckBox,
                                           useCustomColorForThreePrimeArrowheads_prefs_key)
        
        connect_checkbox_with_boolean_pref(self.arrowsOnBackBones_checkBox, 
                                           arrowsOnBackBones_prefs_key)
        
        change_connect(self.fivePrimeEndColorChooser,
                       SIGNAL("editingFinished()"), 
                       self.chooseCustomColorOnFivePrimeEnds)
        
        change_connect(self.threePrimeEndColorChooser,
                       SIGNAL("editingFinished()"), 
                       self.chooseCustomColorOnThreePrimeEnds)
        
        change_connect(self.strandFivePrimeArrowheadsCustomColorCheckBox,
                       SIGNAL("toggled(bool)"),
                       self.allowChoosingColorsOnFivePrimeEnd)
        
        change_connect(self.strandThreePrimeArrowheadsCustomColorCheckBox,
                       SIGNAL("toggled(bool)"),
                       self.allowChoosingColorsOnThreePrimeEnd)
    
    def allowChoosingColorsOnFivePrimeEnd(self, state):
        """
        Show or hide color chooser based on the 
        strandFivePrimeArrowheadsCustomColorCheckBox's state
        """
        if self.strandFivePrimeArrowheadsCustomColorCheckBox.isChecked():
            self.fivePrimeEndColorChooser.show()
        else:
            self.fivePrimeEndColorChooser.hide()
        return
    
    def allowChoosingColorsOnThreePrimeEnd(self, state):
        """
        Show or hide color chooser based on the 
        strandThreePrimeArrowheadsCustomColorCheckBox's state
        """
        if self.strandThreePrimeArrowheadsCustomColorCheckBox.isChecked():
            self.threePrimeEndColorChooser.show()
        else:
            self.threePrimeEndColorChooser.hide()
        return
    
    def chooseCustomColorOnThreePrimeEnds(self):
        """
        Choose custom color for 5' prime end
        """
        color = self.threePrimeEndColorChooser.getColor()
        env.prefs[dnaStrandThreePrimeArrowheadsCustomColor_prefs_key] = color
        self.win.glpane.gl_update() 
        return
       
    def chooseCustomColorOnFivePrimeEnds(self):
        """
        Choose custom color for 5' prime end
        """
        color = self.fivePrimeEndColorChooser.getColor()
        env.prefs[dnaStrandFivePrimeArrowheadsCustomColor_prefs_key] = color
        self.win.glpane.gl_update() 
        return
        
    
    def show(self):
        """
        Shows the Property Manager. Overrides PM_Dialog.show.
        """
        PM_Dialog.show(self)
        self._assignLocalPrefKeyValues()
        self.connect_or_disconnect_signals(isConnect = True)
        
    def close(self):
        """
        Closes the Property Manager. Overrides PM_Dialog.close.
        """
        # this is important since these pref keys are used in other command modes 
        # as well and we do not want to see the 5' end arrow in Inset DNA mode
        
        self._reAssignDefaultValuesToPrefKeys()
        self.connect_or_disconnect_signals(False)
        PM_Dialog.close(self)
        
    def _assignLocalPrefKeyValues(self):
        env.prefs[arrowsOnBackBones_prefs_key] = self._local_arrowsOnBackBones_prefs_key 
        env.prefs[arrowsOnThreePrimeEnds_prefs_key] = self._local_arrowsOnThreePrimeEnds_prefs_key 
        env.prefs[arrowsOnFivePrimeEnds_prefs_key] = self._local_arrowsOnFivePrimeEnds_prefs_key 
        env.prefs[useCustomColorForThreePrimeArrowheads_prefs_key] = self._local_useCustomColorForThreePrimeArrowheads_prefs_key 
        env.prefs[useCustomColorForFivePrimeArrowheads_prefs_key] =  self._local_useCustomColorForFivePrimeArrowheads_prefs_key 
        
        
    def _reAssignDefaultValuesToPrefKeys(self):
        """"
        Set all pref keys to their default values
        """
        
        #store old values in local attributes so that when join Strands is 
        # revisited between sesions, the users choices are respected
        self._local_arrowsOnBackBones_prefs_key = env.prefs[arrowsOnBackBones_prefs_key] 
        self._local_arrowsOnThreePrimeEnds_prefs_key = env.prefs[arrowsOnThreePrimeEnds_prefs_key] 
        self._local_arrowsOnFivePrimeEnds_prefs_key = env.prefs[arrowsOnFivePrimeEnds_prefs_key] 
        self._local_useCustomColorForThreePrimeArrowheads_prefs_key = env.prefs[useCustomColorForThreePrimeArrowheads_prefs_key] 
        self._local_useCustomColorForFivePrimeArrowheads_prefs_key = env.prefs[useCustomColorForFivePrimeArrowheads_prefs_key] 
        
        #restore default values of pref keys
        env.prefs[arrowsOnBackBones_prefs_key] = True
        env.prefs[arrowsOnThreePrimeEnds_prefs_key] = True 
        env.prefs[arrowsOnFivePrimeEnds_prefs_key] = False
        env.prefs[useCustomColorForThreePrimeArrowheads_prefs_key] = False
        env.prefs[useCustomColorForFivePrimeArrowheads_prefs_key] = False

        return