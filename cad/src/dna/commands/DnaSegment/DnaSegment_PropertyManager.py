# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

TODO: as of 2008-01-18
See DnaSegment_EditCommand for details. 
"""
from PyQt4.Qt import SIGNAL
from PM.PM_GroupBox      import PM_GroupBox

from command_support.DnaOrCnt_PropertyManager   import DnaOrCnt_PropertyManager

from PM.PM_Constants     import PM_DONE_BUTTON
from PM.PM_Constants     import PM_WHATS_THIS_BUTTON
from PM.PM_Constants     import PM_CANCEL_BUTTON
from PM.PM_Constants     import PM_PREVIEW_BUTTON

from PM.PM_SpinBox import PM_SpinBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_LineEdit import PM_LineEdit
from dna.model.Dna_Constants import getNumberOfBasePairsFromDuplexLength 
from dna.model.Dna_Constants import getDuplexLength
from geometry.VQT import V, vlen
from utilities.Log import redmsg
from utilities.Comparison import same_vals

from utilities.prefs_constants import dnaSegmentEditCommand_cursorTextCheckBox_length_prefs_key
from utilities.prefs_constants import dnaSegmentEditCommand_cursorTextCheckBox_numberOfBasePairs_prefs_key
from utilities.prefs_constants import dnaSegmentEditCommand_cursorTextCheckBox_changedBasePairs_prefs_key
from utilities.prefs_constants import dnaSegmentEditCommand_showCursorTextCheckBox_prefs_key
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

_superclass = DnaOrCnt_PropertyManager

class DnaSegment_PropertyManager( DnaOrCnt_PropertyManager):
    """
    The DnaSegmenta_PropertyManager class provides a Property Manager 
    for the DnaSegment_EditCommand. 

    @ivar title: The title that appears in the property manager header.
    @type title: str

    @ivar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str

    @ivar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """

    title         =  "DnaSegment Properties"
    pmName        =  title
    iconPath      =  "ui/actions/Tools/Build Structures/DNA.png"

    def __init__( self, win, editCommand ):
        """
        Constructor for the Build DNA property manager.
        """

        #For model changed signal
        #@see: self.model_changed() and self._current_model_changed_params 
        #for example use
        self._previous_model_changed_params = None


        #see self.connect_or_disconnect_signals for comment about this flag
        self.isAlreadyConnected = False
        self.isAlreadyDisconnected = False

        self.endPoint1 = V(0, 0, 0)
        self.endPoint2 = V(0, 0, 0)

        self._numberOfBases = 0 
        self._conformation = 'B-DNA'
        self.duplexRise = 3.18
        self.basesPerTurn = 10
        self.dnaModel = 'PAM3'

        _superclass.__init__( self,  win, editCommand)


        self.showTopRowButtons( PM_DONE_BUTTON | \
                                PM_CANCEL_BUTTON | \
                                PM_PREVIEW_BUTTON | \
                                PM_WHATS_THIS_BUTTON)

        msg = "Use resize handles to resize the segment. Drag any axis or sugar"\
            " atom for translation or rotation about axis respectively. Dragging"\
            " any bond will freely move the whole segment."
        self.updateMessage(msg)   

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
            
        
        _superclass.connect_or_disconnect_signals(self, isConnect)


        change_connect( self.numberOfBasePairsSpinBox,
                        SIGNAL("valueChanged(int)"),
                        self.numberOfBasesChanged )

        change_connect( self.basesPerTurnDoubleSpinBox,
                        SIGNAL("valueChanged(double)"),
                        self.basesPerTurnChanged )

        change_connect( self.duplexRiseDoubleSpinBox,
                        SIGNAL("valueChanged(double)"),
                        self.duplexRiseChanged )

        change_connect(self.showCursorTextCheckBox, 
                       SIGNAL('stateChanged(int)'), 
                       self._update_state_of_cursorTextGroupBox)


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

        isStructResizable, why_not = currentParams
        #update the self._previous_model_changed_params with this new param set.
        self._previous_model_changed_params = currentParams

        if not isStructResizable:
            #disable all widgets
            if self._pmGroupBox1.isEnabled():
                self._pmGroupBox1.setEnabled(False)
                msg = redmsg("DnaSegment is not resizable. Reason: %s"%(why_not))
                self.updateMessage(msg)
        else:
            if not self._pmGroupBox1.isEnabled():
                self._pmGroupBox1.setEnabled(True)
                msg = "Use resize handles to resize the segment. Drag any axis or sugar"\
                    " atom for translation or rotation about axis respectively. Dragging"\
                    " any bond will freely move the whole segment."
                self.updateMessage(msg)


    def _current_model_changed_params(self):
        """
        Returns a tuple containing the parameters that will be compared
        against the previously stored parameters. This provides a quick test
        to determine whether to do more things in self.model_changed()
        @see: self.model_changed() which calls this
        @see: self._previous_model_changed_params attr. 
        """
        params = None

        if self.editCommand:   
            isStructResizable, why_not = self.editCommand.hasResizableStructure()
            params = (isStructResizable, why_not)

        return params 


    def show(self):
        """
        Show this property manager. Overrides EditCommand_PM.show()
        This method also retrives the name information from the 
        editCommand's structure for its name line edit field. 
        @see: DnaSegment_EditCommand.getStructureName()
        @see: self.close()
        """
        _superclass.show(self)
        if self.editCommand is not None:
            name = self.editCommand.getStructureName()
            if name is not None:
                self.nameLineEdit.setText(name)

    def close(self):
        """
        Close this property manager. 
        Also sets the name of the self.editCommand's structure to the one 
        displayed in the line edit field.
        @see self.show()
        @see: DnaSegment_EditCommand.setStructureName
        """
        if self.editCommand is not None:
            name = str(self.nameLineEdit.text())
            self.editCommand.setStructureName(name)
        _superclass.close(self)

    def setParameters(self, params):
        """
        This is usually called when you are editing an existing structure. 
        Some property manager ui elements then display the information 
        obtained from the object being edited. 
        TODO:
        - Make this a EditCommand_PM API method? 
        - See also the routines GraphicsMode.setParams or object.setProps
        ..better to name them all in one style?  
        """
        numberOfBasePairs, \
                         dnaForm, \
                         dnaModel,\
                         basesPerTurn, \
                         duplexRise, \
                         endPoint1, \
                         endPoint2 , \
                         color = params 

        if numberOfBasePairs is not None:
            self.numberOfBasePairsSpinBox.setValue(numberOfBasePairs)
        if dnaForm is not None:
            self._conformation = dnaForm
        if dnaModel is not None:
            self.dnaModel = dnaModel
        if duplexRise is not None:
            self.duplexRiseDoubleSpinBox.setValue(duplexRise)
        if basesPerTurn is not None:
            self.basesPerTurnDoubleSpinBox.setValue(basesPerTurn)
        if endPoint1 is not None:
            self.endPoint1 = endPoint1
        if endPoint2 is not None:
            self.endPoint2 = endPoint2
        if color is not None:
            self._colorChooser.setColor(color)



    def getParameters(self):
        """
        """
        #See bug 2802 for details about the parameter 
        #'number_of_basePairs_from_struct'. Basically it is used to check
        #if the structure got modified (e.g. because of undo) 
        #The numberOfBases parameter obtained from the propMgr is given as a 
        #separate parameter for the reasons mentioned in bug 2802
        #-- Ninad 2008-04-12
        number_of_basePairs_from_struct = None
        if self.editCommand.hasValidStructure():
            number_of_basePairs_from_struct = self.editCommand.struct.getNumberOfBasePairs()
        numberOfBases = self.numberOfBasePairsSpinBox.value()
        dnaForm  = self._conformation
        dnaModel = self.dnaModel
        basesPerTurn = self.basesPerTurn
        duplexRise = self.duplexRise
        color = self._colorChooser.getColor()

        return (
            number_of_basePairs_from_struct,
            numberOfBases, 
            dnaForm,
            dnaModel,
            basesPerTurn,
            duplexRise,
            self.endPoint1, 
            self.endPoint2, 
            color
        )

    def numberOfBasesChanged( self, numberOfBases ):
        """
        Slot for the B{Number of Bases" spinbox.
        """
        duplexRise = self.duplexRiseDoubleSpinBox.value()
        # Update the Duplex Length lineEdit widget.
        text = str(getDuplexLength(self._conformation, 
                                   numberOfBases, 
                                   duplexRise = duplexRise)) \
             + " Angstroms"
        self.duplexLengthLineEdit.setText(text)
        return

    def basesPerTurnChanged( self, basesPerTurn ):
        """
        Slot for the B{Bases per turn} spinbox.
        """
        self.basesPerTurn = basesPerTurn


    def duplexRiseChanged( self, rise ):
        """
        Slot for the B{Rise} spinbox.
        """
        self.duplexRise = rise


    def _addGroupBoxes( self ):
        """
        Add the DNA Property Manager group boxes.
        """        

        self._pmGroupBox1 = PM_GroupBox( self, title = "Parameters" )
        self._loadGroupBox1( self._pmGroupBox1 )

        self._displayOptionsGroupBox = PM_GroupBox( self, 
                                                    title = "Display Options" )
        self._loadDisplayOptionsGroupBox( self._displayOptionsGroupBox )


    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in group box 4.
        """

        self.nameLineEdit = PM_LineEdit( pmGroupBox,
                                         label         =  "Segment name:",
                                         text          =  "",
                                         setAsDefault  =  False)

        # Strand Length (i.e. the number of bases)
        self.numberOfBasePairsSpinBox = \
            PM_SpinBox( pmGroupBox, 
                        label         =  "Base pairs:", 
                        value         =  self._numberOfBases,
                        setAsDefault  =  False,
                        minimum       =  2,
                        maximum       =  10000 )

        self.basesPerTurnDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Bases per turn:",
                              value         =  self.basesPerTurn,
                              setAsDefault  =  True,
                              minimum       =  8.0,
                              maximum       =  20.0,
                              decimals      =  2,
                              singleStep    =  0.1 )

        self.duplexRiseDoubleSpinBox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "Rise:",
                              value         =  self.duplexRise,
                              setAsDefault  =  True,
                              minimum       =  2.0,
                              maximum       =  4.0,
                              decimals      =  3,
                              singleStep    =  0.01 )


        # Duplex Length
        self.duplexLengthLineEdit  =  \
            PM_LineEdit( pmGroupBox,
                         label         =  "Duplex length: ",
                         text          =  "0.0 Angstroms",
                         setAsDefault  =  False)

        self.duplexLengthLineEdit.setDisabled(True)  
        
        
    def _loadDisplayOptionsGroupBox(self, pmGroupBox):
        """
        Overrides superclass method. 
        Also loads the color chooser widget. 
        """
        self._loadColorChooser(pmGroupBox)
        _superclass._loadDisplayOptionsGroupBox(self, pmGroupBox)
        


    def _connect_showCursorTextCheckBox(self):
        """
        Connect the show cursor text checkbox with user prefs_key.
        Overrides 
        DnaOrCnt_PropertyManager._connect_showCursorTextCheckBox
        """
        connect_checkbox_with_boolean_pref(
            self.showCursorTextCheckBox , 
            dnaSegmentEditCommand_showCursorTextCheckBox_prefs_key)


    def _params_for_creating_cursorTextCheckBoxes(self):
        """
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
        @see: Superclass method which is overridden here --
        DnaOrCnt_PropertyManager._params_for_creating_cursorTextCheckBoxes()
        """
        params = \
               [  #Format: (" checkbox text", prefs_key)
                  ("Number of base pairs", 
                   dnaSegmentEditCommand_cursorTextCheckBox_numberOfBasePairs_prefs_key),

                   ("Duplex length",
                    dnaSegmentEditCommand_cursorTextCheckBox_length_prefs_key),

                    ("Number of basepairs to be changed",
                     dnaSegmentEditCommand_cursorTextCheckBox_changedBasePairs_prefs_key) 
                 ]

        return params


    def _addWhatsThisText(self):
        """
        Add what's this text. 
        """
        pass

    def _addToolTipText(self):
        """
        Add Tooltip text
        """
        pass


